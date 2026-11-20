"""The brains: Chat engine and the Code pipeline (Planner -> Coder -> Tester -> Debugger),
with RAG context and strict project-only behaviour in Code mode.

All progress is reported through the `emit(kind, **data)` callback so the UI (or a test) can
render it. Kinds: stage, stream, log, file, done.
"""
import os
import re
import threading
from typing import Callable, Dict, List, Optional, Tuple

from devforge import config, fsops, prompts, themes
from devforge import skills as skilllib
from devforge import memory as memlib
from devforge.llm import OllamaClient, OllamaError, pick_embed_model, resolve_model
from devforge.rag import CodeIndex
from devforge.store import ProjectStore, fallback_title

Emit = Callable[..., None]

# One model call at a time across ALL running chats: a 4 GB GPU cannot serve two big models at
# once, so parallel tasks queue here (each agent call) instead of thrashing Ollama.
_GPU_LOCK = threading.Lock()


class Cancelled(Exception):
    pass


_GREETING = re.compile(r"^\s*(hi+|hello+|hey+|yo|sup|hola|good (morning|evening|afternoon)|thanks?|thank you|ok(ay)?|bye)\W*$", re.I)
_BUILD_VERBS = re.compile(r"\b(build|create|generate|make|write|implement|add|fix|refactor|update|change|modify|develop|design|convert|rewrite|improve|remove|delete|rename|debug|test|want|need)\b", re.I)
_TECH_NOUNS = re.compile(r"\b(website|web ?site|web ?page|page|app|application|api|script|function|class|code|file|game|server|html|css|js|javascript|python|program|calculator|landing|dashboard|form|button|navbar|component|module|test|tests|bug|error|feature|project|store|shop|portfolio|todo|backend|frontend|ui|c\+\+|database|login|theme|toggle|switch|colou?rs?|font|layout|menu|dark mode|light mode)\b", re.I)
_WEB_REQ = re.compile(r"\b(web ?site|web ?page|landing|home ?page|portfolio|dashboard|front ?end|html|ui|blog|site|web ?app)\b", re.I)
_DESIGN_REQ = re.compile(r"\b(theme|design|redesign|modern|beautiful|stylish|style|look|ui|dark mode|colou?rs?|layout)\b", re.I)
_MULTI_PAGE = re.compile(r"\b(pages|multi[- ]?page|several pages|separate pages?|about page|contact page|products? page|login page)\b", re.I)
_ASK_START = re.compile(
    r"^\s*(?:(?:hey|hi|hello|please|pls|ok(?:ay)?|so|now|and|also)[,\s]+)*"
    r"(?:(?:could|can|would|will|do|did)\s+(?:you|u)\s+(?:please\s+|pls\s+)?|(?:i\s+(?:want|wanna|need)\s+to\s+(?:know|see)|let me (?:know|see))\s*)?"
    r"(what|why|where|which|who|when|explain|summari[sz]e|describe|does|is there|are there|tell me|show me|list|give me (?:a )?(?:list|summary)|"
    r"how (?:does|is|do i run|to run|can i run|many))\b", re.I)
_PROJECT_REF = re.compile(r"\b(project|code|codebase|files?|fo+lders?|directory|app|application|website|site|page|functions?|class(es)?|script|repo|readme|this|here|\w+\.(py|js|html|css|json|md))\b", re.I)
_FIX_REQ = re.compile(r"\b(fix|bug|bugs|error|errors|broken|not working|doesn'?t work|does not work|isn'?t working|won'?t (work|load|open|change)|crash(es|ed)?|fails?|failing|wrong|problem|issue|not (changing|updating|showing|displaying|responding)|doesn'?t (change|update|show|display|respond))\b", re.I)
_TOGGLE_REQ = re.compile(r"\b(toggle|switch(er)?|switching)\b.{0,40}\b(theme|dark|light)\b|\b(dark|light)\b.{0,40}\b(toggle|switch(er)?)\b|\btheme (toggle|switch)", re.I)
# things the code-written site kit handles instantly (no model): theme colours, the mobile menu
_KIT_REQ = re.compile(r"\b(theme colou?rs?|dark mode colou?rs?|colou?rs? (in|for) dark mode|hamburger|mobile menu|"
                      r"(menu|side ?bar|navbar|nav) (button )?(is )?(not|doesn'?t|does not|won'?t) (open|opening|work|working|show))\b", re.I)
_REDESIGN_REQ = re.compile(r"\b(redesign|re-design|restyle|new (theme|look|design)|change (the )?(theme|design|look|colou?rs?|style)|(make|give) it (look )?(more )?(modern|fancy|beautiful|stylish|professional|pretty)|make (the )?(design|ui|site|website|page|look)( look)? (more )?(modern|fancy|beautiful|stylish|professional|pretty|better)|better (design|ui|look)|improve (the )?(design|ui|look)|modernize|(dark|light|glass|elegant|vibrant|fresh) (theme|design|style))\b", re.I)
_ROUTE_TEXT = {
    "new": "New project - full team: Researcher, Designer, Planner, Coder, Reviewer",
    "redesign": "Redesign - Designer, Planner, Coder, Reviewer (Researcher skipped)",
    "toggle": "Light/dark switch - added directly, no model needed",
    "fix": "Fix - Planner, Coder, Reviewer (Researcher and Designer skipped, your theme stays untouched)",
    "change": "Change - Planner, Coder, Reviewer (Researcher and Designer skipped)",
}
_ASK_HINT = re.compile(r"\b(what|why|how|where|which|explain|show|list|describe|summari[sz]e|does|is there)\b", re.I)


class Engine:
    def __init__(self, root: str, client: Optional[OllamaClient] = None,
                 emit: Optional[Emit] = None, cancel: Optional[Callable[[], bool]] = None):
        self.root = os.path.abspath(root)
        self.client = client or OllamaClient()
        self.emit: Emit = emit or (lambda kind, **kw: None)
        self._cancel = cancel or (lambda: False)
        self.store = ProjectStore(self.root)
        self._models: Optional[Dict[str, str]] = None
        self._index: Optional[CodeIndex] = None

    # ------------------------------------------------------------ plumbing
    def cancelled(self) -> bool:
        return bool(self._cancel())

    def _check(self):
        if self.cancelled():
            raise Cancelled()

    def models(self) -> Dict[str, str]:
        if self._models is None:
            if not self.client.ensure_server():
                raise OllamaError("Ollama is not running and could not be started. Install/start Ollama first.")
            installed = self.client.list_models()
            if not installed:
                raise OllamaError("Ollama has no models installed. Run: ollama pull qwen2.5-coder:7b")
            self._models = {r: resolve_model(m, installed) for r, m in config.ROLE_MODELS.items()}
            self._installed = installed
        return self._models

    def index(self) -> CodeIndex:
        if self._index is None:
            self.models()
            self._index = CodeIndex(self.root, self.client, pick_embed_model(self._installed))
        self._index.refresh()
        return self._index

    def _llm(self, role: str, system: str, user: str, *, history: Optional[List[Dict]] = None,
             temperature: float = 0.2, num_predict: Optional[int] = None,
             stream_to_ui: bool = False, agent: str = "") -> str:
        model = self.models()[role]
        messages = [{"role": "system", "content": system}] + (history or []) + [{"role": "user", "content": user}]
        out: List[str] = []
        size = 0
        self._acquire_gpu()
        try:
            for piece in self.client.stream(model, messages, temperature, num_predict, self.cancelled):
                out.append(piece)
                size += len(piece)
                if stream_to_ui:
                    self.emit("stream", text=piece)
                else:
                    self.emit("progress", agent=agent or role, chars=size)
        finally:
            _GPU_LOCK.release()
        self._check()
        return "".join(out)

    def _acquire_gpu(self):
        if _GPU_LOCK.acquire(blocking=False):
            return
        self.emit("stage", agent="Queue", model="", text="Waiting for another running task to finish with the model...")
        while not _GPU_LOCK.acquire(timeout=0.25):
            self._check()               # stopping a queued task works too

    def _stage(self, agent: str, role: str, text: str):
        self.emit("stage", agent=agent, model=self.models()[role], text=text)

    @staticmethod
    def _history_msgs(msgs: List[Dict], n: int) -> List[Dict]:
        return [{"role": m["role"], "content": m["content"][:3000]}
                for m in msgs[-n:] if m["role"] in ("user", "assistant")]

    # ------------------------------------------------------------ chat tab
    def _open_session(self, mode: str, text: str, sid: Optional[str]) -> Tuple[str, List[Dict]]:
        """Resume chat `sid`, or create a new one (shown instantly with a provisional title)."""
        if sid and self.store.meta(sid):
            history = self.store.load(sid)
        else:
            m = self.store.create(mode, fallback_title(re.sub(r"(?<!\S)/[A-Za-z0-9][\w-]*", "", text).strip() or text))
            sid, history = m["id"], []
            self.emit("session", id=sid, title=m["title"], mode=mode)
        self.store.append(sid, "user", text)
        return sid, history

    def _apply_skills(self, text: str) -> Tuple[str, str]:
        """Resolve /skill-name tokens and auto-matched skills. -> (prompt for the models, skills block)."""
        skills = skilllib.SkillStore(self.root).list()
        if not skills:
            return text, ""
        clean, chosen = skilllib.pick(text, skills)
        if chosen:
            names = ", ".join(f"{s['name']} ({how})" for s, how in chosen)
            self.emit("stage", agent="Skills", model="", text=f"Using: {names}")
        return clean, skilllib.format_block(chosen)

    def _apply_memory(self, text: str, sid: str, light: bool = False) -> str:
        """Saved project notes + relevant excerpts from the OTHER chats of this project."""
        mem = memlib.MemoryStore(self.root)
        if not mem.enabled():
            return ""
        notes = mem.notes()
        recalled = [] if light else memlib.recall(self.store, text, exclude_sid=sid)
        block = memlib.format_block(notes, recalled, notes_budget=700 if light else memlib.NOTES_BLOCK_CHARS)
        if block:
            self.emit("stage", agent="Memory", model="",
                      text=f"Using {len(notes)} saved note(s) and {len(recalled)} earlier chat excerpt(s)")
        return block

    def _remember(self, sid: str, request: str, reply: str, meta: Optional[Dict]) -> None:
        """After a reply: save durable facts so every other chat in this project knows them."""
        mem = memlib.MemoryStore(self.root)
        if not mem.enabled() or reply == prompts.OFFTOPIC_REPLY:
            return
        facts: List[str] = []
        if meta and meta.get("files"):
            facts.append(f'Built for "{request.strip()[:100]}": ' + ", ".join(meta["files"][:6]))
        try:
            if len(request.strip()) >= 12:
                self.emit("stage", agent="Memory", model="", text="Saving what we learned...")
                known = "\n".join("- " + n["text"] for n in mem.notes()[-15:]) or "(none yet)"
                raw = self._llm("router", prompts.MEMORY_SYSTEM.replace("{known}", known),
                                f"USER: {request[:600]}\n\nASSISTANT: {reply[:900]}", temperature=0.0,
                                num_predict=140, agent="Memory")
                facts += memlib.parse_facts(raw)
        except (OllamaError, Cancelled):
            pass                    # memory is a bonus; never fail or "stop" a finished reply because of it
        mem.add(facts, chat=sid)

    def _finish(self, sid: str, text: str, reply: str, meta: Optional[Dict] = None) -> None:
        """Persist the reply; after the first exchange give the chat a proper short name."""
        self.store.append(sid, "assistant", reply, meta)
        info = self.store.meta(sid)
        if info and info["count"] == 2 and info["title_auto"]:
            title = self._make_title(text)
            if title and self.store.rename(sid, title, auto=True):
                self.emit("title", id=sid, title=title)
        self._remember(sid, text, reply, meta)
        self.emit("done", text=reply)

    def _make_title(self, first_prompt: str) -> str:
        """Short chat name from the small router model; '' on any failure (keeps provisional title)."""
        try:
            raw = self._llm("router", prompts.TITLE_SYSTEM, first_prompt[:600], temperature=0.2,
                            num_predict=20, agent="Namer")
        except OllamaError:
            return ""
        line = (raw.strip().splitlines() or [""])[0]
        title = re.sub(r"""^[\s"'`*#-]+|[\s"'`*.:;,!?-]+$""", "", line)
        title = re.sub(r"^(title|chat name)\s*[:\-]\s*", "", title, flags=re.I)
        if not title or len(title.split()) > 8 or len(title) > 50:
            return ""
        return title[0].upper() + title[1:]

    def handle_chat(self, text: str, sid: Optional[str] = None) -> str:
        sid, history = self._open_session("chat", text, sid)
        llm_text, skills_block = self._apply_skills(text)
        memory_block = self._apply_memory(llm_text, sid)
        system = prompts.CHAT_SYSTEM
        files = [f for f in os.listdir(self.root) if not f.startswith(".")][:25] if os.path.isdir(self.root) else []
        if files:
            system += f"\nThe user has the folder '{os.path.basename(self.root)}' open (files: {', '.join(files)})."
        if skills_block:
            system += "\n\n" + skills_block
        if memory_block:
            system += "\n\n" + memory_block
        self._stage("Assistant", "chat", "Thinking...")
        reply = self._llm("chat", system, llm_text, history=self._history_msgs(history, 12),
                          temperature=0.5, stream_to_ui=True)
        self._finish(sid, llm_text, reply)
        return reply

    # ------------------------------------------------------------ code tab
    def classify_intent(self, text: str) -> str:
        """BUILD | ASK | OFFTOPIC. Heuristics first, small LLM for the ambiguous middle."""
        if _GREETING.match(text):
            return "OFFTOPIC"
        if _KIT_REQ.search(text):
            return "BUILD"        # theme colours / mobile menu: handled instantly by the site kit
        if _ASK_START.match(text) and _PROJECT_REF.search(text):
            return "ASK"          # "what does this project do?" never needs the small model's opinion
        has_verb, has_noun = bool(_BUILD_VERBS.search(text)), bool(_TECH_NOUNS.search(text))
        if has_verb and has_noun and not re.match(r"^\s*(what|why|how|where|which|explain|does)\b", text, re.I):
            return "BUILD"
        try:
            raw = self._llm("router", prompts.INTENT_SYSTEM, text, temperature=0.0, num_predict=6,
                            agent="Router").upper()
            for word in ("OFFTOPIC", "BUILD", "ASK"):
                if word in raw:
                    return word
        except OllamaError:
            raise
        if has_noun and _ASK_HINT.search(text):
            return "ASK"
        return "BUILD" if has_verb and has_noun else "OFFTOPIC"

    def handle_code(self, text: str, sid: Optional[str] = None) -> str:
        sid, history = self._open_session("code", text, sid)
        llm_text, skills_block = self._apply_skills(text)
        self._stage("Router", "router", "Understanding your request...")
        intent = self.classify_intent(llm_text)
        self._check()

        if intent == "OFFTOPIC":
            reply = prompts.OFFTOPIC_REPLY
            self._finish(sid, llm_text, reply)
            return reply

        if intent == "ASK":
            self._stage("RAG", "coder", "Searching the project...")
            ctx = self.index().context(llm_text) + "\n\nALL FILES IN THE FOLDER (real listing):\n" + fsops.list_files(self.root)
            extra = "\n\n".join(b for b in (skills_block, self._apply_memory(llm_text, sid)) if b)
            self._stage("Coder", "coder", "Answering from your project...")
            reply = self._llm("coder", prompts.CODE_ASK_SYSTEM + "\n\nPROJECT CONTEXT:\n" + ctx
                              + ("\n\n" + extra if extra else ""), llm_text,
                              history=self._history_msgs(history, 6), temperature=0.2, stream_to_ui=True)
            self._finish(sid, llm_text, reply)
            return reply

        build_extra = "\n\n".join(b for b in (skills_block, self._apply_memory(llm_text, sid, light=True)) if b)
        reply, meta = self._build(llm_text, history, build_extra)
        self._finish(sid, llm_text, reply, meta)
        return reply

    # ------------------------------------------------------------ the pipeline
    def _build(self, request: str, history: List[Dict], skills: str = "") -> Tuple[str, Dict]:
        steps: List[str] = []
        idx = self.index()
        existing = idx.has_files()
        ctx = idx.context(request, k=5, max_chars=4000) if existing else ""
        recent = self._history_msgs(history, 4)
        convo = "\n".join(f"{m['role']}: {m['content'][:500]}" for m in recent)

        # Supervisor: decide which agents this request really needs
        kind = self._classify_build(request, idx)
        self.emit("stage", agent="Supervisor", model="", text=_ROUTE_TEXT[kind])
        if kind == "toggle":
            return self._toggle_theme(request, idx)

        # 0) Researcher (offline: reads the request + project context) -------
        brief = ""
        if config.ENABLE_RESEARCH and kind == "new":
            self._stage("Researcher", "researcher", "Researching the best approach...")
            ruser = f"REQUEST:\n{request}\n\nPROJECT CONTEXT:\n{ctx or '(empty folder - new project)'}"
            if skills:
                ruser += "\n\n" + skills
            brief = self._llm("researcher", prompts.RESEARCHER_SYSTEM, ruser, temperature=0.3,
                              num_predict=450, agent="Researcher").strip()[:2000]
            steps.append(f"Researcher ({self.models()['researcher']}): design brief ready")

        # 0b) Designer: pick a modern theme; theme.css is written by code, not by the model
        design: Optional[Dict[str, str]] = None
        if config.ENABLE_DESIGNER and self._wants_design(request, idx, kind):
            self._stage("Designer", "designer", "Choosing a visual theme...")
            design = self._design(request, brief, skills)
            self._write_site_kit(design["theme"], design["accent"], request)
            steps.append(f"Designer ({self.models()['designer']}): theme '{design['theme']}'")

        # 1) Planner -------------------------------------------------------
        self._stage("Planner", "planner", "Planning the files...")
        user = f"REQUEST:\n{request}\n"
        if brief:
            user += f"\nDESIGN BRIEF:\n{brief}\n"
        if design:
            user += (f"\nVISUAL DESIGN: theme '{design['theme']}' - {design['style']}. Home page sections: "
                     f"{design['sections'] or 'hero, features, call to action'}. The stylesheet theme.css is already "
                     f"provided: do NOT plan it; plan styles.css only for small page-specific extras.\n")
        if convo:
            user += f"\nRECENT CONVERSATION:\n{convo}\n"
        user += f"\nPROJECT CONTEXT:\n{ctx or '(empty folder - new project)'}"
        if skills:
            user += "\n\n" + skills
        plan = self._llm("planner", prompts.PLANNER_SYSTEM, user, temperature=0.2, num_predict=900, agent="Planner")
        planned = fsops.order_files([f for f in fsops.parse_plan_files(plan) if f[0] != "theme.css"])
        if design and not existing and not _MULTI_PAGE.search(request):
            # A new website is ONE page unless the user asked for several: small planners over-engineer this.
            planned = [("index.html", "the whole site on one page: navbar, hero, main sections, contact, footer"),
                       ("styles.css", "small page-specific extras only (theme.css already provides the design)"),
                       ("script.js", "interactivity for this page")]
        summary = re.search(r"SUMMARY:\s*(.+)", plan)
        steps.append(f"Planner ({self.models()['planner']}): {len(planned)} file(s) planned")

        # 2) Coder: one file at a time ---------------------------------------
        written: List[str] = []
        contents: Dict[str, str] = {}
        if planned:
            names = [p for p, _ in planned]
            for i, (rel, purpose) in enumerate(planned, 1):
                self._check()
                self._stage("Coder", "coder", f"Writing {rel} ({i}/{len(planned)})...")
                old = fsops.read_file(self.root, rel, 8000)
                parts = [f"REQUEST:\n{request}", f"PLAN:\n{plan}", f"ALL PLANNED FILES: {', '.join(names)}"]
                if brief:
                    parts.append(f"DESIGN BRIEF:\n{brief}")
                if design:
                    parts.append(themes.design_system_text(design["theme"]) +
                                 f"\nMood: {design['style']}. Home page sections: {design['sections']}")
                if skills:
                    parts.append(skills)
                parts.append(f"FILE TO WRITE NOW: {rel}" + (f" - {purpose}" if purpose else ""))
                if old:
                    parts.append(f"CURRENT CONTENT OF {rel} (modify it as requested, keep what still works):\n```\n{old}\n```")
                sib = ""
                for srel, sc in contents.items():
                    sib += f"\n--- {srel} ---\n{sc[:3500]}\n"
                if sib:
                    parts.append("OTHER FILES ALREADY WRITTEN (stay consistent with them):" + sib[:9000])
                if ctx:
                    parts.append(f"PROJECT CONTEXT:\n{ctx[:3000]}")
                raw = self._llm("coder", prompts.CODER_SYSTEM, "\n\n".join(parts), temperature=0.2,
                                num_predict=4096, agent=f"Coder · {rel}")
                code = fsops.extract_single(raw)
                if not code.strip():
                    steps.append(f"Coder: no content produced for {rel}")
                    continue
                fsops.write_file(self.root, rel, code)
                contents[rel] = code
                written.append(rel)
                self.emit("file", path=rel)
        else:   # planner format failed - let the coder emit several files at once
            self._stage("Coder", "coder", "Writing the project...")
            raw = self._llm("coder", prompts.CODER_SYSTEM.replace("exactly ONE file", "every needed file").replace(
                "a single fenced code block containing only that file's content",
                "one fenced code block per file, each preceded by a line 'FILE: path'"),
                f"REQUEST:\n{request}\n\nPLAN:\n{plan}\n\nPROJECT CONTEXT:\n{ctx}", num_predict=6000, agent="Coder")
            for rel, code in fsops.parse_files(raw):
                try:
                    fsops.write_file(self.root, rel, code)
                except ValueError:
                    continue
                contents[rel] = code
                written.append(rel)
                self.emit("file", path=rel)
        steps.append(f"Coder ({self.models()['coder']}): wrote {len(written)} file(s)")
        if not written:
            return ("I couldn't produce any files for that request. Try rephrasing it with a bit more "
                    "detail, for example *\"Create a shoe store website with a product grid and cart\"*."), {"files": []}

        # 2b) Cheap deterministic repairs, then the Reviewer ---------------------
        html_files = [r for r in written if r.endswith((".html", ".htm"))]
        self._themed = bool(design) or self._has_devforge_theme()
        fixes = self._repair_html(html_files) + self._repair_site(written)
        if fixes:
            steps.append("Auto-fix: " + ", ".join(fixes))
        for r in written:
            if r.endswith((".html", ".htm", ".css")):
                contents[r] = fsops.read_file(self.root, r, 400_000) or contents[r]

        review_rows = ""
        logic = [r for r in written if r.endswith((".js", ".py")) and not os.path.basename(r).startswith("test_")]
        if config.ENABLE_REVIEW and logic:          # HTML/CSS consistency is checked by code, not by the model
            self._stage("Reviewer", "reviewer", "Reviewing the logic...")
            issues = self._review(request, logic, contents)
            if not issues:
                review_rows = "- ✅ review: no proven defects - nothing rewritten"
            else:
                fixed = self._apply_review(request, issues, plan, contents)
                review_rows = "\n".join(f"- 🔎 `{f}` - {msg}" for f, msg in issues) + \
                    f"\n- {fixed} of {len(issues)} finding(s) fixed (each fix re-checked; a fix that broke the file was undone)"
            dropped = getattr(self, "_review_dropped", 0)
            if dropped:
                review_rows += f"\n- {dropped} unproven finding(s) ignored (they did not quote real code)"
            steps.append(f"Reviewer ({self.models()['reviewer']}): {len(issues)} proven finding(s)")

        # 3) Tester (Python logic only) ------------------------------------
        test_rel = None
        py_src = [r for r in written if r.endswith(".py") and not os.path.basename(r).startswith("test_")]
        if py_src:
            self._stage("Tester", "tester", "Writing unit tests...")
            code_blob = "\n\n".join(f"# {r}\n{contents[r][:5000]}" for r in py_src)
            raw = self._llm("tester", prompts.TESTER_SYSTEM,
                            f"USER GOAL: {request}\n\nCODE UNDER TEST:\n{code_blob}", temperature=0.1,
                            num_predict=1500, agent="Tester")
            tcode = fsops.extract_single(raw)
            if tcode.strip():
                test_rel = f"test_{os.path.splitext(os.path.basename(py_src[0]))[0]}.py"
                fsops.write_file(self.root, test_rel, tcode)
                self.emit("file", path=test_rel)
                steps.append(f"Tester ({self.models()['tester']}): wrote {test_rel}")

        # 4) Verify + Debugger self-healing loop ---------------------------
        verdict, problems = self._verify(written, test_rel)
        rounds = 0
        while problems and rounds < config.MAX_DEBUG_ROUNDS:
            self._check()
            rounds += 1
            self._stage("Debugger", "debugger", f"Fixing problems (attempt {rounds}/{config.MAX_DEBUG_ROUNDS})...")
            if not self._debug(problems, written, test_rel):
                break
            verdict, problems = self._verify(written, test_rel)
        if rounds:
            steps.append(f"Debugger ({self.models()['debugger']}): {rounds} attempt(s)")

        # 5) Summary ---------------------------------------------------------
        self.index()    # refresh RAG so follow-up prompts see the new files
        target = fsops.find_run_target(self.root)
        lines = []
        if summary:
            lines.append(summary.group(1).strip() + "\n")
        kit = [f for f in ("theme.css", "theme-toggle.js", "site.js") if design and os.path.exists(os.path.join(self.root, f))]
        all_files = kit + written + ([test_rel] if test_rel else [])
        lines.append("**Files**\n" + "\n".join(f"- `{r}`" + (" - written by DevForge's code (always works)" if r in kit else "")
                                               for r in all_files))
        if design:
            lines.append(f"**Design**\nTheme **{design['theme']}**" + (f", accent `{design['accent']}`" if design["accent"] else "")
                         + (f" - {design['style']}" if design["style"] else "")
                         + ("\n\nBuilt in: light/dark switch, mobile menu and active nav link." if "site.js" in kit else ""))
        lines.append("**Checks**\n" + verdict)
        if review_rows:
            lines.append("**Review**\n" + review_rows)
        if problems:
            lines.append("Some problems remain (see above). You can ask me to fix them, e.g. *\"fix the error in " + problems[0]["file"] + "\"*.")
        if target:
            lines.append(f"Press **Run** to {'open `' + target[1] + '` in your browser' if target[0] == 'browser' else 'run `' + target[1] + '`'}.")
        lines.append("<sub>" + " → ".join(steps) + "</sub>")
        return "\n\n".join(lines), {"files": written, "tests": test_rel, "ok": not problems}

    # ------------------------------------------------------------ site kit (written by code, not by a model)
    def _has_devforge_theme(self) -> bool:
        return themes.is_devforge_theme(fsops.read_file(self.root, "theme.css", 300) or "")

    def _write_site_kit(self, theme: str, accent: Optional[str], request: str = "") -> None:
        """theme.css (+ both palettes and the switch when enabled) and site.js for a new website."""
        if config.ENABLE_THEME_SWITCH:
            pair = themes.dual_pair(theme)
            low = request.lower()
            if re.search(r"(default|start|begin)\w*\s+(in\s+|with\s+)?(a\s+)?dark|dark (by default|first)", low):
                default = "dark"
            elif re.search(r"(default|start|begin)\w*\s+(in\s+|with\s+)?(a\s+)?light|light (by default|first)", low):
                default = "light"
            else:
                default = "dark" if themes.is_dark(theme) else "light"
            fsops.write_file(self.root, "theme.css", themes.render_dual_css(pair["dark"], pair["light"], accent, default))
            fsops.write_file(self.root, "theme-toggle.js", themes.toggle_js(default))
            self.emit("file", path="theme-toggle.js")
        else:
            fsops.write_file(self.root, "theme.css", themes.render_css(theme, accent))
        fsops.write_file(self.root, "site.js", themes.site_js())
        self.emit("file", path="theme.css")
        self.emit("file", path="site.js")

    def _repair_site(self, written: List[str]) -> List[str]:
        """Deterministic, idempotent: link the kit files into every page and turn fixed colours in the
        page stylesheets into theme colours, so the light/dark switch recolours everything."""
        if not self._has_devforge_theme():
            return []
        out: List[str] = []
        pages = sorted(set(r for r in self.index()._outlines if r.endswith((".html", ".htm")))
                       | {r for r in written if r.endswith((".html", ".htm"))})
        for r in pages:
            fsops.ensure_theme_link(self.root, r)
            for js in ("theme-toggle.js", "site.js"):
                if os.path.exists(os.path.join(self.root, js)):
                    fsops.ensure_script_link(self.root, r, js)
        css_files = sorted({r for r in self.index()._outlines if r.endswith(".css") and r != "theme.css"}
                           | {r for r in written if r.endswith(".css") and r != "theme.css"})
        n = 0
        for r in css_files:
            src = fsops.read_file(self.root, r, 300_000)
            if not src:
                continue
            new, k = themes.theme_colours(src)
            if k:
                fsops.write_file(self.root, r, new)
                n += k
        if n:
            out.append(f"turned {n} fixed colour(s) into theme colours")
        return out

    def _repair_html(self, html_files: List[str]) -> List[str]:
        """Deterministic, idempotent repairs. Runs before the Reviewer and again before every
        verification, because a model rewrite can bring the same problems back."""
        out: List[str] = []
        if getattr(self, "_themed", False):
            for r in html_files:
                fsops.ensure_theme_link(self.root, r)
            n = sum(fsops.strip_external_assets(self.root, r) for r in html_files)
            if n:
                out.append(f"removed {n} online (CDN) asset(s) so the site works offline")
        n = sum(fsops.fix_missing_images(self.root, r) for r in html_files)
        if n:
            out.append(f"replaced {n} missing image(s) with offline placeholders")
        n = sum(fsops.fix_dangling_refs(self.root, r) for r in html_files)
        if n:
            out.append(f"repaired {n} dangling link(s)")
        return out

    # ------------------------------------------------------------ design
    def _classify_build(self, request: str, idx: CodeIndex) -> str:
        """new | redesign | toggle | fix | change  - decides which agents run."""
        has_html = any(r.endswith((".html", ".htm")) for r in idx._outlines)
        if not idx.has_files() or (not has_html and _WEB_REQ.search(request)):
            return "new"
        if has_html and (_TOGGLE_REQ.search(request) or _KIT_REQ.search(request)):
            return "toggle"
        if _FIX_REQ.search(request):
            return "fix"
        if has_html and _REDESIGN_REQ.search(request):
            return "redesign"
        return "change"

    def _wants_design(self, request: str, idx: CodeIndex, kind: Optional[str] = None) -> bool:
        """The Designer picks a look only for a NEW website or an explicit redesign - never for fixes or features."""
        kind = kind or self._classify_build(request, idx)
        if kind == "new":
            return bool(_WEB_REQ.search(request))
        return kind == "redesign"

    def _toggle_theme(self, request: str, idx: CodeIndex) -> Tuple[str, Dict]:
        """Add a real light/dark switch without any model: both palettes in theme.css + theme-toggle.js."""
        html_files = sorted(r for r in idx._outlines if r.endswith((".html", ".htm")))
        cur = themes.read_current(fsops.read_file(self.root, "theme.css", 300_000) or "")
        pair = themes.dual_pair(cur["theme"])
        low = request.lower()
        if re.search(r"(default|start|begin)\w*\s+(in\s+|with\s+)?(a\s+)?light|light (by default|first)", low):
            default = "light"
        elif re.search(r"(default|start|begin)\w*\s+(in\s+|with\s+)?(a\s+)?dark|dark (by default|first)", low):
            default = "dark"
        else:
            default = "light" if (cur["theme"] and not themes.is_dark(cur["theme"])) else "dark"
        fsops.write_file(self.root, "theme.css",
                         themes.render_dual_css(pair["dark"], pair["light"], cur["accent"], default))
        fsops.write_file(self.root, "theme-toggle.js", themes.toggle_js(default))
        fsops.write_file(self.root, "site.js", themes.site_js())
        for f in ("theme.css", "theme-toggle.js", "site.js"):
            self.emit("file", path=f)
        self._themed = True
        fixes = self._repair_site(html_files)               # links + fixed colours -> theme colours
        js = sorted(r for r in idx._outlines if r.endswith(".js"))
        verdict, problems = self._verify(html_files + [r for r in js if r not in ("theme-toggle.js", "site.js")]
                                         + ["theme-toggle.js", "site.js"], None)
        self.index()
        lines = ["Added a light / dark theme switch to your site, and the built-in mobile menu.\n",
                 "**Files**\n- `theme.css` - now holds both palettes "
                 f"(dark: {pair['dark']}, light: {pair['light']}) and the mobile menu styles\n- `theme-toggle.js` - the "
                 "switch; it remembers your choice in the browser\n- `site.js` - hamburger menu and the active nav link "
                 "while scrolling\n" + "\n".join(f"- `{r}` - linked to all of them" for r in html_files),
                 f"**Design**\nThe site starts in **{default}** mode. Use the round button at the bottom-right "
                 "(or your own theme button, which now works) to switch."
                 + (f"\n\n{fixes[0][0].upper() + fixes[0][1:]} in your stylesheets, so every part follows the theme." if fixes else ""),
                 "**Checks**\n" + verdict]
        if problems:
            lines.append("Some problems remain (see above). You can ask me to fix them, e.g. *\"fix the error in "
                         + problems[0]["file"] + "\"*.")
        lines.append("<sub>Supervisor: theme switch, menu and colours handled directly by code - no Planner or Coder needed</sub>")
        return "\n\n".join(lines), {"files": ["theme.css", "theme-toggle.js", "site.js"] + html_files, "ok": not problems}

    def _design(self, request: str, brief: str, skills: str = "") -> Dict[str, str]:
        hint = themes.suggest(request)
        user = f"REQUEST:\n{request}\n\nKEYWORD SUGGESTION: {hint}"
        if skills:
            user += "\n\n" + skills
        if brief:
            user += f"\n\nBRIEF:\n{brief[:600]}"
        raw = self._llm("designer", prompts.DESIGNER_SYSTEM.replace("{themes}", themes.describe()), user,
                        temperature=0.3, num_predict=160, agent="Designer")
        spec = themes.parse_design(raw, fallback=hint)
        forced = themes.explicit_theme(request)       # the user's own words beat the model's guess
        if forced:
            spec["theme"] = forced
        return spec

    # ------------------------------------------------------------ review
    def _review(self, request: str, written: List[str], contents: Dict[str, str]) -> List[Tuple[str, str]]:
        """Reviewer agent: returns [(file, defect)] (max MAX_REVIEW_ISSUES), [] when LGTM."""
        blob = "\n\n".join(f"--- {r} ---\n{contents.get(r, '')[:4000]}" for r in written)[:12000]
        raw = self._llm("reviewer", prompts.REVIEWER_SYSTEM, f"REQUEST:\n{request}\n\nFILES:\n{blob}",
                        temperature=0.1, num_predict=400, agent="Reviewer")
        issues: List[Tuple[str, str]] = []
        self._review_dropped = 0
        for line in raw.splitlines():
            m = re.match(r"^\s*[-*\d.)]+\s*[`*]*([\w./\\-]+\.\w{1,6})[`*]*\s*[:\-]\s*(.+)$", line)
            if m:
                path = m.group(1).replace("\\", "/")
                if path in written and m.group(2).strip():
                    if self._proven(m.group(2), contents.get(path, "")):
                        issues.append((path, m.group(2).strip()[:300]))
                    else:
                        self._review_dropped += 1
        return issues[:config.MAX_REVIEW_ISSUES]

    @staticmethod
    def _proven(finding: str, source: str) -> bool:
        """A finding counts only if it quotes real code from the file (small models invent defects such
        as 'the section is not completed'; those would cost a full rewrite for nothing)."""
        norm = lambda t: re.sub(r"\s+", "", t)
        src = norm(source)
        for quote in re.findall(r"`([^`]{6,})`", finding):
            q = norm(quote)
            if len(q) >= 6 and q in src:
                return True
        return False

    def _apply_review(self, request: str, issues: List[Tuple[str, str]], plan: str,
                      contents: Dict[str, str]) -> int:
        """Have the Coder fix each review finding. Rejects truncated or broken rewrites."""
        fixed = 0
        by_file: Dict[str, List[str]] = {}
        for f, msg in issues:
            by_file.setdefault(f, []).append(msg)
        for rel, msgs in by_file.items():
            self._check()
            self._stage("Coder", "coder", f"Applying review fixes to {rel}...")
            old = contents.get(rel, "")
            others = "".join(f"\n--- {r} ---\n{c[:2500]}\n" for r, c in contents.items() if r != rel)[:6000]
            user = (f"REQUEST:\n{request}\n\nFILE TO WRITE NOW: {rel}\n\n"
                    f"CURRENT CONTENT (keep everything that works):\n```\n{old[:9000]}\n```\n\n"
                    f"REVIEW FINDINGS TO FIX (change only what is needed for these):\n- " + "\n- ".join(msgs) +
                    (f"\n\nOTHER FILES (for consistency):{others}" if others else ""))
            raw = self._llm("coder", prompts.CODER_SYSTEM, user, temperature=0.1, num_predict=4096,
                            agent=f"Coder · {rel}")
            new = fsops.extract_single(raw)
            if not new.strip() or len(new) < len(old) * 0.6:
                continue
            if rel.endswith(".py"):
                try:
                    compile(new, rel, "exec")
                except SyntaxError:
                    continue
            before_ok = all(r["ok"] for r in fsops.static_check(self.root, [rel]))
            fsops.write_file(self.root, rel, new)
            if before_ok and not all(r["ok"] for r in fsops.static_check(self.root, [rel])):
                fsops.write_file(self.root, rel, old)        # the "fix" broke a working file: undo it
                continue
            contents[rel] = new
            self.emit("file", path=rel)
            fixed += len(msgs)
        return fixed

    # ------------------------------------------------------------ verification
    def _verify(self, written: List[str], test_rel: Optional[str]) -> Tuple[str, List[Dict]]:
        self.emit("stage", agent="Verifier", model="", text="Checking the result...")
        self._repair_html([r for r in written if r.endswith((".html", ".htm"))])
        self._repair_site(written)
        problems: List[Dict] = []
        rows = []
        for r in fsops.static_check(self.root, written):
            rows.append(f"- {'✅' if r['ok'] else '❌'} `{r['file']}` - {r['message']}")
            if not r["ok"]:
                problems.append({"file": r["file"], "error": r["message"]})
        # cross-file check: ids / classes the JavaScript uses must exist in the HTML / CSS
        bad = {p["file"] for p in problems}
        scope = list(written)
        if any(r.endswith((".html", ".htm")) for r in written):      # a rewritten page can break any script
            scope += [r for r in self.index()._outlines if r.endswith(".js") and r not in scope]
        for c in fsops.consistency_check(self.root, scope):
            if c["file"] in bad:
                continue
            rows.append(f"- ❌ `{c['file']}` - {c['error'][:300]}")
            problems.append(c)
        if test_rel and not any(p["file"].endswith(".py") for p in problems):
            res = fsops.run_python(self.root, test_rel, 30)
            tail = ((res["stderr"] or res["stdout"]).strip().splitlines() or [""])[-1]
            rows.append(f"- {'✅' if res['success'] else '❌'} unit tests (`{test_rel}`) - {'passed' if res['success'] else tail[:160]}")
            if not res["success"]:
                problems.append({"file": test_rel, "error": (res["stderr"] or res["stdout"]).strip()[-1800:], "is_test": True})
        return "\n".join(rows), problems

    def _debug(self, problems: List[Dict], written: List[str], test_rel: Optional[str]) -> bool:
        """One Debugger round. Returns True if any file was changed."""
        changed = False
        targets: List[Tuple[str, str]] = []
        for p in problems:
            if p.get("is_test"):
                trace = p["error"]
                srcs = [f for f in written if f.endswith(".py") and not os.path.basename(f).startswith("test_")]
                hit = [f for f in srcs if os.path.basename(f) in trace]
                pick = (hit or srcs or [test_rel])[0]
                targets.append((pick, trace))
            else:
                targets.append((p["file"], p["error"]))
        seen = set()
        for rel, error in targets:
            if rel in seen:
                continue
            seen.add(rel)
            src = fsops.read_file(self.root, rel, 12000)
            if not src:
                continue
            extra = ""
            if test_rel and rel != test_rel and error and test_rel in error:
                t = fsops.read_file(self.root, test_rel, 4000)
                extra = f"\n\nTHE TEST THAT FAILS ({test_rel}):\n```\n{t}\n```" if t else ""
            raw = self._llm("debugger", prompts.DEBUGGER_SYSTEM,
                            f"FILE: {rel}\n```\n{src}\n```\n\nERROR:\n{error}{extra}", temperature=0.1,
                            num_predict=4096, agent="Debugger")
            fixed = fsops.extract_single(raw)
            if not fixed.strip() or len(fixed) < len(src) * 0.4:
                continue     # reject truncated / empty rewrites from the small model
            if rel.endswith(".py"):
                try:
                    compile(fixed, rel, "exec")
                except SyntaxError:
                    continue
            fsops.write_file(self.root, rel, fixed)
            self.emit("file", path=rel)
            changed = True
        return changed
