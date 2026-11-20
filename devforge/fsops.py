"""File parsing, safe writing, static checks and command execution for generated projects."""
import json
import os
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple

from devforge import config

CODE_EXTS = {".html", ".htm", ".css", ".js", ".jsx", ".ts", ".tsx", ".json", ".py", ".c", ".h",
             ".cpp", ".hpp", ".java", ".go", ".rs", ".cs", ".md", ".txt", ".sql", ".sh", ".bat",
             ".php", ".rb", ".yml", ".yaml", ".svg", ".xml"}
LANG_DEFAULT_NAME = {"html": "index.html", "css": "styles.css", "javascript": "script.js",
                     "js": "script.js", "python": "main.py", "py": "main.py", "c": "main.c",
                     "cpp": "main.cpp", "json": "data.json"}


# ---------------------------------------------------------------- paths
def safe_join(root: str, rel: str) -> str:
    """Resolve `rel` inside `root`; raise ValueError on traversal or reserved dirs."""
    rel = rel.strip().strip("`'\"").replace("\\", "/").lstrip("/")
    if not rel or re.match(r"^[A-Za-z]:", rel):
        raise ValueError(f"invalid path: {rel!r}")
    root_abs = os.path.abspath(root)
    full = os.path.abspath(os.path.join(root_abs, rel))
    if os.path.commonpath([root_abs, full]) != root_abs:
        raise ValueError(f"path escapes the project folder: {rel}")
    if config.STATE_DIRNAME in rel.split("/"):
        raise ValueError("cannot write into the internal state folder")
    return full


def write_file(root: str, rel: str, content: str) -> str:
    full = safe_join(root, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(content if content.endswith("\n") else content + "\n")
    return full


def read_file(root: str, rel: str, limit: int = 12000) -> Optional[str]:
    try:
        with open(safe_join(root, rel), "r", encoding="utf-8", errors="replace") as f:
            return f.read(limit)
    except (OSError, ValueError):
        return None


# ---------------------------------------------------------------- parsing LLM output
_FENCE = re.compile(r"```([\w+.#-]*)[ \t]*\n(.*?)```", re.DOTALL)
_HEADER_PATS = [
    re.compile(r"(?:file(?:name)?|path)\s*[:=]\s*[`*\"']*([\w./\\-]+\.\w{1,6})", re.I),
    re.compile(r"^#{1,6}\s*[`*]*([\w./\\-]+\.\w{1,6})", re.I),
    re.compile(r"^\W*\*\*[`]?([\w./\\-]+\.\w{1,6})[`]?\*\*", re.I),
    re.compile(r"^\W*`([\w./\\-]+\.\w{1,6})`\W*$"),
]
_INLINE_NAME = re.compile(
    r"^\s*(?:#|//|--|/\*|<!--)\s*(?:file(?:name)?|path)\s*[:=]\s*([\w./\\-]+\.\w{1,6})\s*(?:\*/|-->)?\s*$", re.I)


def _valid_name(name: str) -> bool:
    name = name.strip().replace("\\", "/")
    return (0 < len(name) < 100 and " " not in name and ".." not in name
            and os.path.splitext(name)[1].lower() in CODE_EXTS)


def _close_fences(text: str) -> str:
    return text + "\n```" if text.count("```") % 2 == 1 else text


def parse_files(text: str) -> List[Tuple[str, str]]:
    """Extract (relative_path, content) pairs from an LLM reply with fenced code blocks."""
    text = _close_fences(text)
    results: List[Tuple[str, str]] = []
    fallback_idx: Dict[str, int] = {}
    for m in _FENCE.finditer(text):
        lang, body = m.group(1).lower(), m.group(2)
        name = None
        lines = body.split("\n")
        im = _INLINE_NAME.match(lines[0]) if lines else None
        if im and _valid_name(im.group(1)):
            name = im.group(1)
            body = "\n".join(lines[1:])
        if not name:
            before = text[max(0, m.start() - 200):m.start()].rstrip().split("\n")
            for cand in reversed(before[-2:]):
                for pat in _HEADER_PATS:
                    hm = pat.search(cand.strip())
                    if hm and _valid_name(hm.group(1)):
                        name = hm.group(1)
                        break
                if name:
                    break
        if not name:
            base = LANG_DEFAULT_NAME.get(lang)
            if not base:
                continue
            n = fallback_idx.get(base, 0)
            fallback_idx[base] = n + 1
            name = base if n == 0 else f"{os.path.splitext(base)[0]}{n + 1}{os.path.splitext(base)[1]}"
        body = body.strip("\n")
        if body.strip():
            results.append((name.replace("\\", "/").lstrip("./"), body))
    merged: Dict[str, str] = {}
    for n, c in results:           # later blocks win when the model repeats a file
        merged[n] = c
    return list(merged.items())


def extract_single(text: str) -> str:
    """Return the content of the first fenced block (or the whole text if unfenced)."""
    text = _close_fences(text)
    m = _FENCE.search(text)
    body = m.group(2) if m else text
    lines = body.split("\n")
    if lines and _INLINE_NAME.match(lines[0]):
        body = "\n".join(lines[1:])
    return body.strip("\n")


def parse_plan_files(plan: str, limit: int = config.MAX_PLAN_FILES) -> List[Tuple[str, str]]:
    """Pull '- path/to/file.ext: purpose' lines out of the planner's output."""
    found: List[Tuple[str, str]] = []
    in_files = False
    pat = re.compile(r"^\s*(?:[-*]|\d+[.)])\s*[`*]*([\w./\\-]+\.\w{1,6})[`*]*\s*(?:[:\-–—(]\s*(.*))?$")
    for line in plan.splitlines():
        if re.match(r"^\W*FILES\b", line, re.I):
            in_files = True
            continue
        if in_files and re.match(r"^\W*(NOTES|SUMMARY)\b", line, re.I):
            break
        m = pat.match(line)
        if m and (in_files or not found) and _valid_name(m.group(1)):
            name = m.group(1).replace("\\", "/").lstrip("./")
            if name not in [f for f, _ in found]:
                found.append((name, (m.group(2) or "").strip(" )")))
    return found[:limit]


def order_files(files: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Pages first, then styles, then a Python backend, then the scripts - so a script is written after the
    backend it calls and can use its real routes."""
    rank = {".html": 0, ".htm": 0, ".css": 1, ".py": 2, ".js": 3}
    return sorted(files, key=lambda f: rank.get(os.path.splitext(f[0])[1].lower(), 4))


# ---------------------------------------------------------------- static checks
class _TagChecker(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
            "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack: List[str] = []
        self.problems: List[str] = []
        self.refs: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)
        d = dict(attrs)
        for k in ("src", "href"):
            v = d.get(k)
            if v and not re.match(r"^(https?:|//|#|data:|mailto:|tel:|javascript:)", v):
                self.refs.append(v.split("#")[0].split("?")[0])

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.problems.append(f"<{self.stack.pop()}> is not closed")
            self.stack.pop()
        else:
            self.problems.append(f"unexpected </{tag}>")


def static_check(root: str, rels: List[str]) -> List[Dict]:
    """Cheap, dependency-free verification. Returns [{file, ok, message}]."""
    results = []
    for rel in rels:
        ext = os.path.splitext(rel)[1].lower()
        src = read_file(root, rel, limit=400_000)
        if src is None:
            results.append({"file": rel, "ok": False, "message": "file is missing"})
            continue
        ok, msg = True, "ok"
        if ext == ".py":
            try:
                compile(src, rel, "exec")
            except SyntaxError as e:
                ok, msg = False, f"SyntaxError line {e.lineno}: {e.msg}"
        elif ext == ".json":
            try:
                json.loads(src)
            except ValueError as e:
                ok, msg = False, f"invalid JSON: {e}"
        elif ext in (".js",) and shutil.which("node"):
            r = run_command(["node", "--check", rel], root, 20)
            if not r["success"]:
                ok, msg = False, (r["stderr"] or r["stdout"]).strip()[:500]
        elif ext == ".css":
            if src.count("{") != src.count("}"):
                ok, msg = False, "unbalanced { } braces"
        elif ext in (".html", ".htm"):
            chk = _TagChecker()
            try:
                chk.feed(src)
            except Exception as e:      # noqa: BLE001 - parser errors are reported, not raised
                chk.problems.append(str(e))
            chk.problems += [f"<{t}> is not closed" for t in chk.stack if t not in ("html", "body", "head", "p", "li")]
            base = os.path.dirname(rel)
            for ref in chk.refs:
                target = os.path.normpath(os.path.join(base, ref)).replace("\\", "/")
                try:
                    if not os.path.exists(safe_join(root, target)):
                        chk.problems.append(f"references missing file '{ref}'")
                except ValueError:
                    pass
            if chk.problems:
                ok, msg = False, "; ".join(dict.fromkeys(chk.problems))[:500]
        results.append({"file": rel, "ok": ok, "message": msg})
    return results


_IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
_PALETTE = [("#6366f1", "#8b5cf6"), ("#f43f5e", "#fb923c"), ("#10b981", "#06b6d4"), ("#f59e0b", "#ef4444")]


def fix_missing_images(root: str, rel: str) -> int:
    """Local models often reference images that do not exist. Swap each broken <img> for a
    self-contained gradient placeholder (keeps layout, works offline). Returns replacements."""
    src = read_file(root, rel, limit=400_000)
    if src is None:
        return 0
    base = os.path.dirname(rel)
    count = 0

    def repl(m):
        nonlocal count
        tag = m.group(0)
        sm = re.search(r"""src\s*=\s*["']([^"']+)["']""", tag, re.I)
        if not sm or re.match(r"^(https?:|//|data:)", sm.group(1)):
            return tag
        target = os.path.normpath(os.path.join(base, sm.group(1).split("?")[0])).replace("\\", "/")
        try:
            if os.path.exists(safe_join(root, target)):
                return tag
        except ValueError:
            return tag
        am = re.search(r"""alt\s*=\s*["']([^"']*)["']""", tag, re.I)
        label = html_escape(am.group(1)) if am and am.group(1) else "Image"
        a, b = _PALETTE[count % len(_PALETTE)]
        count += 1
        return (f'<div role="img" aria-label="{label}" style="width:100%;aspect-ratio:4/3;display:flex;'
                f'align-items:center;justify-content:center;font-size:2.2rem;color:#fff;border-radius:8px;'
                f'background:linear-gradient(135deg,{a},{b})">{label[:2] if label == "Image" else label[:18]}</div>')

    new = _IMG_TAG.sub(repl, src)
    if count:
        write_file(root, rel, new)
    return count


_SCRIPT_TAG = re.compile(r"""<script\b[^>]*\bsrc\s*=\s*["']([^"']+)["'][^>]*>\s*</script>""", re.I)
_LINK_TAG = re.compile(r"""<link\b[^>]*\bhref\s*=\s*["']([^"']+)["'][^>]*>""", re.I)
_ANCHOR_HREF = re.compile(r"""(<a\b[^>]*\bhref\s*=\s*)(["'])([^"']+)\2""", re.I)


def _is_local_missing(root: str, base: str, ref: str) -> bool:
    if re.match(r"^(https?:|//|#|data:|mailto:|tel:|javascript:)", ref):
        return False
    target = os.path.normpath(os.path.join(base, ref.split("#")[0].split("?")[0])).replace("\\", "/")
    try:
        return not os.path.exists(safe_join(root, target))
    except ValueError:
        return False


def fix_dangling_refs(root: str, rel: str) -> int:
    """Remove <script>/<link> tags that point at files that don't exist and point broken
    page links at '#'. Returns the number of fixes."""
    src = read_file(root, rel, limit=400_000)
    if src is None:
        return 0
    base = os.path.dirname(rel)
    count = 0

    def drop(m):
        nonlocal count
        if _is_local_missing(root, base, m.group(1)):
            count += 1
            return ""
        return m.group(0)

    def anchor(m):
        nonlocal count
        if _is_local_missing(root, base, m.group(3)):
            count += 1
            return f"{m.group(1)}{m.group(2)}#{m.group(2)}"
        return m.group(0)

    new = _SCRIPT_TAG.sub(drop, src)
    new = _LINK_TAG.sub(drop, new)
    new = _ANCHOR_HREF.sub(anchor, new)
    if count:
        write_file(root, rel, new)
    return count


_EXT_SCRIPT = re.compile(r"""<script\b[^>]*\bsrc\s*=\s*["']\s*(?:https?:)?//[^"']+["'][^>]*>\s*</script>""", re.I)
_EXT_STYLE = re.compile(r"""<link\b[^>]*\bhref\s*=\s*["']\s*(?:https?:)?//[^"']+["'][^>]*>""", re.I)


def strip_external_assets(root: str, rel: str) -> int:
    """Generated sites must work offline: drop CDN <script>/<link> tags the model added anyway."""
    src = read_file(root, rel, limit=400_000)
    if src is None:
        return 0
    removed = 0

    def drop_style(m):
        nonlocal removed
        if re.search(r"rel\s*=\s*[\"'](?:icon|canonical|alternate)", m.group(0), re.I):
            return m.group(0)           # favicons etc. are harmless offline
        removed += 1
        return ""

    new, n1 = _EXT_SCRIPT.subn("", src)
    new = _EXT_STYLE.sub(drop_style, new)
    removed += n1
    if removed:
        write_file(root, rel, new)
    return removed


def ensure_theme_link(root: str, rel: str, theme_file: str = "theme.css") -> bool:
    """Guarantee an HTML page links the shared theme stylesheet (and has a viewport meta).
    Returns True if the file was changed."""
    src = read_file(root, rel, limit=400_000)
    if src is None:
        return False
    new = src
    href = os.path.relpath(os.path.join(root, theme_file), os.path.join(root, os.path.dirname(rel))).replace("\\", "/")
    if not re.search(r"""href\s*=\s*["'][^"']*theme\.css["']""", new, re.I):
        tag = f'<link rel="stylesheet" href="{href}">'
        m = re.search(r"<link\b[^>]*rel\s*=\s*[\"']stylesheet[\"'][^>]*>", new, re.I)
        if m:
            new = new[:m.start()] + tag + "\n    " + new[m.start():]
        elif re.search(r"</head>", new, re.I):
            new = re.sub(r"</head>", "    " + tag + "\n</head>", new, count=1, flags=re.I)
        elif re.search(r"<html\b[^>]*>", new, re.I):
            new = re.sub(r"(<html\b[^>]*>)", r"\1\n<head>" + tag + "</head>", new, count=1, flags=re.I)
        else:
            new = tag + "\n" + new
    if re.search(r"</head>", new, re.I) and not re.search(r"""name\s*=\s*["']viewport["']""", new, re.I):
        new = re.sub(r"</head>", '    <meta name="viewport" content="width=device-width, initial-scale=1">\n</head>',
                     new, count=1, flags=re.I)
    if new != src:
        write_file(root, rel, new)
        return True
    return False


def ensure_script_link(root: str, rel: str, script_file: str) -> bool:
    """Make an HTML page load `script_file` (placed in <head> so the saved theme applies before paint)."""
    src = read_file(root, rel, limit=400_000)
    if src is None:
        return False
    href = os.path.relpath(os.path.join(root, script_file), os.path.join(root, os.path.dirname(rel))).replace("\\", "/")
    if re.search(r"""src\s*=\s*["'][^"']*""" + re.escape(os.path.basename(script_file)) + r"""["']""", src, re.I):
        return False
    tag = f'<script src="{href}"></script>'
    if re.search(r"</head>", src, re.I):
        new = re.sub(r"</head>", "    " + tag + "\n</head>", src, count=1, flags=re.I)
    elif re.search(r"</body>", src, re.I):
        new = re.sub(r"</body>", "    " + tag + "\n</body>", src, count=1, flags=re.I)
    else:
        new = src + "\n" + tag + "\n"
    write_file(root, rel, new)
    return True


def list_files(root: str, limit: int = 80) -> str:
    """Plain listing of what is really in the folder (all file types), for 'which files are here?' questions."""
    skip = {".git", ".venv", "venv", "node_modules", "__pycache__", config.STATE_DIRNAME}
    rows = []
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(d for d in dns if d not in skip and not d.startswith("."))
        rel_dir = os.path.relpath(dp, root).replace("\\", "/")
        for fn in sorted(fns):
            if fn.startswith("."):
                continue
            try:
                size = os.path.getsize(os.path.join(dp, fn))
            except OSError:
                size = 0
            rows.append(f"- {fn if rel_dir == '.' else rel_dir + '/' + fn} ({size / 1024:.1f} KB)")
            if len(rows) >= limit:
                return "\n".join(rows) + "\n- ... (more files not shown)"
    return "\n".join(rows) or "(the folder is empty)"


def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ---------------------------------------------------------------- running
def run_command(args: List[str], cwd: str, timeout: int = 30) -> Dict:
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace",
                           creationflags=0x08000000 if os.name == "nt" else 0)
        return {"success": r.returncode == 0, "stdout": r.stdout, "stderr": r.stderr, "exit_code": r.returncode}
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": f"timed out after {timeout}s", "exit_code": -1}
    except OSError as e:
        return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -1}


def run_python(root: str, rel: str, timeout: int = 30) -> Dict:
    return run_command([sys.executable, rel], root, timeout)


def find_run_target(root: str) -> Optional[Tuple[str, str]]:
    """What should the Run button do? -> ('server'|'browser'|'python'|'node', relative path)
    A site with a Python backend is started through the backend ('server'), so its data is really saved."""
    servers = backend_files(root)
    if servers and any(os.path.exists(os.path.join(root, n)) for n in ("index.html", "public/index.html", "static/index.html")):
        return "server", ("app.py" if "app.py" in servers else servers[0])
    for name in ("index.html", "public/index.html", "src/index.html"):
        if os.path.exists(os.path.join(root, name)):
            return "browser", name
    for name in ("main.py", "app.py", "run.py"):
        if os.path.exists(os.path.join(root, name)):
            return "python", name
    for name in ("index.js", "main.js", "app.js", "server.js"):
        if os.path.exists(os.path.join(root, name)) and shutil.which("node"):
            return "node", name
    for fn in sorted(os.listdir(root)):
        if fn.endswith(".py") and not fn.startswith("test_"):
            return "python", fn
    for fn in sorted(os.listdir(root)):
        if fn.endswith(".html"):
            return "browser", fn
    return None


# ---------------------------------------------------------------- HTML / CSS / JS consistency
_JS_ID = re.compile(r"""getElementById\(\s*['"]([\w-]+)['"]\s*\)|querySelector(?:All)?\(\s*['"]#([\w-]+)['"]""")
_JS_CLASS_SEL = re.compile(r"""querySelector(?:All)?\(\s*['"]\.([\w-]+)['"]\s*\)|getElementsByClassName\(\s*['"]([\w-]+)['"]""")
_JS_CLASS_SET = re.compile(r"""classList\.(?:add|toggle)\(\s*['"]([\w-]+)['"]""")
_JS_VAR_CLASS_SET = re.compile(r"""([\w$]+)\.classList\.(?:add|toggle)\(\s*['"]([\w-]+)['"]""")
_JS_TARGET = re.compile(r"""(?:const|let|var)\s+([\w$]+)\s*=\s*document\.(?:querySelector\(\s*['"]([.#][\w-]+)['"]\s*\)|getElementById\(\s*['"]([\w-]+)['"]\s*\))""")
_KIT_FILES = {"site.js", "theme-toggle.js"}
_THEMEISH = re.compile(r"theme|dark|light|night|day-?mode", re.I)          # written by code, always consistent


def consistency_check(root: str, rels: List[str]) -> List[Dict]:
    """Cross-file check a small model often gets wrong: JavaScript that uses an id or class the HTML
    does not have, or that switches on a class no CSS rule styles (e.g. a menu that never opens).
    Only clear-cut cases are reported, so the Debugger is never sent after a false alarm.
    Returns [{file, error}] for the JavaScript files among `rels`."""
    html_files = [r for r in rels if r.endswith((".html", ".htm"))]
    js_files = [r for r in rels if r.endswith(".js") and os.path.basename(r) not in _KIT_FILES]
    if not js_files:
        return []
    # look at every page / stylesheet in the folder, not only the files written in this build
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv")]
        for fn in fns:
            rel = os.path.relpath(os.path.join(dp, fn), root).replace("\\", "/")
            if fn.endswith((".html", ".htm")) and rel not in html_files:
                html_files.append(rel)
    if not html_files:
        return []
    html = "\n".join(read_file(root, r, 400_000) or "" for r in html_files)
    css = ""
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv")]
        css += "\n".join(open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
                         for f in fns if f.endswith(".css"))
    css += "\n" + re.sub(r"(?s)<style[^>]*>(.*?)</style>", lambda m: m.group(1), " ".join(
        re.findall(r"(?is)<style[^>]*>.*?</style>", html)))
    ids = set(re.findall(r"""\bid\s*=\s*["']([^"']+)["']""", html))
    classes = set()
    for c in re.findall(r"""\bclass\s*=\s*["']([^"']+)["']""", html):
        classes.update(c.split())
    css_classes = set(re.findall(r"\.(-?[_a-zA-Z][\w-]*)", css))
    out: List[Dict] = []
    backend, backend_src = [], ""                                     # Python server files in the project root
    for fn in sorted(os.listdir(root)):
        if fn.endswith(".py") and not fn.startswith("test_"):
            code = read_file(root, fn, 400_000) or ""
            if re.search(r"http\.server|BaseHTTPRequestHandler|flask|@app\.route|do_GET|do_POST", code):
                backend.append(fn)
                backend_src += code
    backend_names = ", ".join(backend)
    kit = os.path.exists(os.path.join(root, "site.js"))              # site.js runs the menu, whatever a script does
    switch = os.path.exists(os.path.join(root, "theme-toggle.js"))   # ...and theme-toggle.js the light/dark theme
    for rel in js_files:
        js = read_file(root, rel, 400_000) or ""
        made = js_made_names(js)                  # ids/classes the script creates itself
        problems = []
        for a, b in _JS_ID.findall(js):
            name = a or b
            if name not in ids and name not in made and not (switch and _THEMEISH.search(name)):
                problems.append(f'it looks for id "{name}" but no element in the HTML has id="{name}"')
        for a, b in _JS_CLASS_SEL.findall(js):
            name = a or b
            if name not in classes and name not in made:
                problems.append(f'it looks for class "{name}" but no element in the HTML has that class')
        targets = _js_targets(js)
        for var, name in _JS_VAR_CLASS_SET.findall(js):
            if name in ("hidden", "visible", "selected", "checked", "disabled", "loading"):
                continue
            sel = targets.get(var)
            if kit and sel in (".nav-links", "#menu-btn", ".menu-btn", ".nav-toggle", ".hamburger"):
                continue
            if switch and _THEMEISH.search(name + " " + (sel or "")):     # old theme code, now dead
                continue
            if name not in css_classes:
                problems.append(f'it switches on class "{name}" but no CSS rule styles ".{name}", so nothing visible changes')
            elif sel and not _styled_on(css, sel, name):
                problems.append(f'it switches on class "{name}" on {sel} but no CSS rule styles "{sel}.{name}" '
                                f'(or a plain ".{name}"), so nothing visible changes')
        for target in missing_redirects(root, js, backend_src):           # location.href = a page that is not there
            problems.append(f'it sends the browser to "{target}" but that page does not exist '
                            f'(create it, or use the name of an existing .html file)')
        for path in re.findall(r"""fetch\(\s*['"`](/[\w./-]*)""", js):    # frontend -> backend routes
            if "." in path.rsplit("/", 1)[-1]:
                continue                                          # a static file such as /index.html, not a route
            if not backend and path.rstrip("/"):
                problems.append(f'it sends data to "{path}" but the project has no backend, so nothing is saved')
                continue
            if backend and path.rstrip("/") and path.rstrip("/") not in backend_src:
                problems.append(f'it calls "{path}" but the backend ({backend_names}) has no route "{path}"')
        problems = list(dict.fromkeys(problems))
        if problems:
            out.append({"file": rel, "error": "Mismatch with the HTML/CSS/backend: " + "; ".join(problems[:5]) +
                        ". Use only ids, classes and routes that really exist, or add the missing CSS rule."})
    return out


def _js_targets(js: str) -> Dict[str, str]:
    """variable -> the simple selector it was found with, e.g. {'navLinks': '.nav-links', 'btn': '#menu-btn'}."""
    out = {}
    for var, sel, el_id in _JS_TARGET.findall(js):
        out[var] = sel or f"#{el_id}"
    return out


def _styled_on(css: str, sel: str, cls: str) -> bool:
    """Is there a rule for `sel.cls` (either order), or a plain `.cls` rule not tied to another element?"""
    s, c = re.escape(sel), re.escape("." + cls)
    if re.search(s + r"(?:[.#][\w-]+)*" + c + r"(?![\w-])", css) or re.search(c + r"(?:[.#][\w-]+)*" + s + r"(?![\w-])", css):
        return True
    return bool(re.search(r"(?:^|[\s,{}>+~])" + c + r"(?![\w-])", css))


def js_made_names(js: str) -> set:
    """ids / classes a script creates itself (createElement + id/className, or HTML in strings)."""
    names = set(re.findall(r"""\.id\s*=\s*['"`]([\w-]+)['"`]""", js))
    for c in re.findall(r"""className\s*=\s*['"`]([^'"`]+)['"`]""", js):
        names.update(c.split())
    for c in re.findall(r"""class=\\?["']([^"'\\]+)""", js):
        names.update(c.split())
    names.update(re.findall(r"""id=\\?["']([\w-]+)""", js))
    names.update(re.findall(r"""classList\.add\(\s*['"]([\w-]+)['"]""", js))
    return names


# ---------------------------------------------------------------- in-page links
_A_TAG = re.compile(r"""(<a\b[^>]*?\bhref\s*=\s*)(["'])([^"']*)\2([^>]*>)(.*?)</a>""", re.I | re.S)
_DEAD_HREFS = ("", "#", "#!", "#0", "javascript:void(0)", "javascript:void(0);", "javascript:;")
_SYNONYMS = {
    "home": ("home", "hero", "top", "banner", "main"),
    "contact": ("contact", "contact-us", "get-in-touch", "footer"),
    "services": ("services", "features", "what-we-do"),
    "features": ("features", "services"),
    "products": ("products", "shop", "store", "collection", "menu"),
    "shop": ("shop", "products", "store", "collection"),
    "team": ("team", "speakers", "people", "about"),
    "register": ("register", "registration", "signup", "sign-up", "join"),
    "pricing": ("pricing", "plans", "prices"),
}


def _section_ids(src: str) -> List[str]:
    """ids of page landmarks, in page order (sections, header, footer, main, divs with an id)."""
    return re.findall(r"""<(?:section|header|footer|main|div|article|aside|form)\b[^>]*?\bid\s*=\s*["']([^"']+)["']""", src, re.I)


def _link_target(text: str, href: str, ids: List[str]) -> Optional[str]:
    words = re.sub(r"<[^>]+>|&[#\w]+;", " ", text).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", words).strip("-")
    stem = re.sub(r"[^a-z0-9]+", "-", href.split("/")[-1].split(".")[0].lstrip("#").lower()).strip("-")
    low = {i.lower(): i for i in ids}
    for cand in (slug, stem):
        if not cand:
            continue
        if cand in low:
            return low[cand]
        for key, alts in _SYNONYMS.items():                        # "Home" -> #hero, "Contact" -> #footer ...
            if cand == key or cand.startswith(key + "-"):
                for a in alts:
                    if a in low:
                        return low[a]
        for li, i in low.items():                                  # "register-now" -> #register, "about" -> #about-us
            if len(li) >= 4 and (cand.startswith(li + "-") or li.startswith(cand + "-")):
                return i
    if slug in ("home", "top") or stem in ("index", "home"):
        return ids[0] if ids else None
    return None


def fix_nav_anchors(root: str, rel: str) -> int:
    """Point dead links (href="#", javascript:void(0), or #id with no such id) at the matching section
    on the page, e.g. <a href="#">About</a> -> href="#about". Returns the number of links fixed."""
    src = read_file(root, rel, limit=400_000)
    if src is None:
        return 0
    ids = _section_ids(src)
    all_ids = set(re.findall(r"""\bid\s*=\s*["']([^"']+)["']""", src))
    if not ids:
        return 0
    count = 0

    def fix(m):
        nonlocal count
        href = m.group(3).strip()
        dead = href.lower() in _DEAD_HREFS or (href.startswith("#") and len(href) > 1 and href[1:] not in all_ids)
        if not dead:
            return m.group(0)
        if "theme" in m.group(0).lower() or "menu-btn" in m.group(0):
            return m.group(0)                                      # a button styled as a link, not navigation
        target = _link_target(m.group(5), href, ids)
        if not target:
            return m.group(0)
        count += 1
        return f"{m.group(1)}{m.group(2)}#{target}{m.group(2)}{m.group(4)}{m.group(5)}</a>"

    new = _A_TAG.sub(fix, src)
    if count:
        write_file(root, rel, new)
    return count


def dead_nav_links(src: str) -> List[str]:
    """Links inside the navbar that still go nowhere (after fix_nav_anchors could not match them)."""
    nav = " ".join(re.findall(r"(?is)<nav\b.*?</nav>", src))
    all_ids = set(re.findall(r"""\bid\s*=\s*["']([^"']+)["']""", src))
    out = []
    for m in _A_TAG.finditer(nav):
        href = m.group(3).strip()
        if href.lower() in _DEAD_HREFS or (href.startswith("#") and len(href) > 1 and href[1:] not in all_ids):
            label = re.sub(r"<[^>]+>", "", m.group(5)).strip()[:30]
            out.append(f'nav link "{label}" points to "{href or "nothing"}"')
    return out


# ---------------------------------------------------------------- backend detection
_SERVER_CODE = re.compile(r"http\.server|BaseHTTPRequestHandler|SimpleHTTPRequestHandler|flask|@app\.route|do_GET|do_POST")


def backend_files(root: str) -> List[str]:
    """Python files in the project root that run a web server (the site's backend)."""
    out = []
    try:
        names = sorted(os.listdir(root))
    except OSError:
        return out
    for fn in names:
        if fn.endswith(".py") and not fn.startswith("test_"):
            if _SERVER_CODE.search(read_file(root, fn, 400_000) or ""):
                out.append(fn)
    return out


def server_port(root: str, rel: str) -> int:
    """The port a backend listens on (PORT = 8000 / ("", 8000)), 8000 when not found."""
    src = read_file(root, rel, 400_000) or ""
    m = re.search(r"\bPORT\s*=\s*(\d{2,5})", src) or re.search(r"""\(\s*["'][^"']*["']\s*,\s*(\d{2,5})\s*\)""", src)
    return int(m.group(1)) if m else 8000


_REDIRECT = re.compile(r"""location(?:\.href)?\s*=\s*['"`]([^'"`]+)['"`]|location\.(?:assign|replace)\(\s*['"`]([^'"`]+)""")


def missing_redirects(root: str, js: str, backend_src: str = "") -> List[str]:
    """Pages a script sends the browser to that do not exist (e.g. location.href = '/thank-you' with no
    thank-you.html and no backend route for it)."""
    out = []
    for a, b in _REDIRECT.findall(js):
        target = (a or b).split("?")[0].split("#")[0]
        if not target or target.startswith(("http:", "https:", "mailto:", "tel:", "javascript:")):
            continue
        rel = target.lstrip("/") or "index.html"
        candidates = [rel] if "." in rel.rsplit("/", 1)[-1] else [rel + ".html", rel + "/index.html"]
        if any(os.path.exists(os.path.join(root, c)) for c in candidates):
            continue
        if backend_src and target.rstrip("/") and (f"'{target}'" in backend_src or f'"{target}"' in backend_src):
            continue                                    # a backend route serves it
        out.append(target)
    return out


def fix_redirect_paths(root: str, rel: str) -> int:
    """location.href = '/thank-you' -> 'thank-you.html' when that page exists, so the redirect works both
    through the backend and when the page is opened directly. Returns the number of fixes."""
    src = read_file(root, rel, 400_000)
    if src is None:
        return 0
    count = 0

    def fix(m):
        nonlocal count
        target = m.group(2)
        if target.startswith(("http:", "https:", "#")) or "." in target.rsplit("/", 1)[-1]:
            return m.group(0)
        page = target.strip("/") + ".html"
        if target.strip("/") and os.path.exists(os.path.join(root, page)):
            count += 1
            return m.group(1) + page + m.group(3)
        return m.group(0)

    new = re.sub(r"""(location(?:\.href)?\s*=\s*['"`])([^'"`?#]+)(['"`])""", fix, src)
    new = re.sub(r"""(location\.(?:assign|replace)\(\s*['"`])([^'"`?#]+)(['"`])""", fix, new)
    if count:
        write_file(root, rel, new)
    return count
