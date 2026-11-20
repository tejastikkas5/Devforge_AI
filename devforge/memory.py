"""Project memory shared by EVERY chat in a folder.

Two parts, both stored/read locally:
  1. Notes   - short durable facts ("user wants a dark theme", "built a task manager site"), saved in
               <project>/.devforge/memory.json. Extracted after each reply by the small model, and
               fully editable by the user.
  2. Recall  - the most relevant exchanges from the project's OTHER chats, found with BM25 search.

Both are turned into a short text block that is added to the prompt of every new chat.
"""
import json
import math
import os
import re
import tempfile
import threading
import time
from collections import Counter
from typing import Dict, List, Optional, Tuple

from devforge import config
from devforge.rag import tokenize
from devforge.store import ProjectStore

MAX_NOTES = 40
MAX_NOTE_CHARS = 200
NOTES_BLOCK_CHARS = 1200
EXCERPT_CHARS = 700
MAX_EXCHANGES_SCANNED = 300
_LOCK = threading.Lock()
_RECALL_WORDS = re.compile(r"\b(earlier|before|previous(ly)?|last time|we discussed|we talked|remember|did we|you said|"
                           r"i (told|asked)|yesterday|other chat|first chat|again|what did|decided)\b", re.I)


def _norm(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", t.lower()).strip()


class MemoryStore:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self.path = os.path.join(self.root, config.STATE_DIRNAME, "memory.json")

    def _load(self) -> Dict:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                d = json.load(f)
            if isinstance(d, dict):
                d.setdefault("enabled", True)
                d.setdefault("notes", [])
                return d
        except (OSError, ValueError):
            pass
        return {"enabled": True, "notes": []}

    def _save(self, d: Dict) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(self.path), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        os.replace(tmp, self.path)

    # ---- reading
    def enabled(self) -> bool:
        return bool(self._load()["enabled"])

    def notes(self) -> List[Dict]:
        return self._load()["notes"]

    # ---- writing
    def set_enabled(self, on: bool) -> None:
        with _LOCK:
            d = self._load()
            d["enabled"] = bool(on)
            self._save(d)

    def add(self, texts: List[str], chat: Optional[str] = None) -> int:
        """Add new facts (duplicates ignored, oldest dropped past MAX_NOTES). Returns how many were new."""
        with _LOCK:
            d = self._load()
            seen = {_norm(n["text"]) for n in d["notes"]}
            added = 0
            for t in texts:
                t = re.sub(r"\s+", " ", t).strip(" -•*\t")[:MAX_NOTE_CHARS]
                if len(t) < 6 or _norm(t) in seen:
                    continue
                seen.add(_norm(t))
                d["notes"].append({"text": t, "ts": time.time(), "chat": chat})
                added += 1
            d["notes"] = d["notes"][-MAX_NOTES:]
            if added:
                self._save(d)
            return added

    def replace_all(self, lines: List[str]) -> None:
        """The user edited the notes: keep timestamps of unchanged lines, drop removed ones."""
        with _LOCK:
            d = self._load()
            old = {_norm(n["text"]): n for n in d["notes"]}
            out, seen = [], set()
            for line in lines:
                t = re.sub(r"\s+", " ", line).strip(" -•*\t")[:MAX_NOTE_CHARS]
                if not t or _norm(t) in seen:
                    continue
                seen.add(_norm(t))
                out.append(old.get(_norm(t)) or {"text": t, "ts": time.time(), "chat": None})
            d["notes"] = out[-MAX_NOTES:]
            self._save(d)

    def clear(self) -> None:
        with _LOCK:
            d = self._load()
            d["notes"] = []
            self._save(d)


# ---------------------------------------------------------------- extracting facts from a reply
def parse_facts(raw: str, limit: int = 3) -> List[str]:
    """Turn the small model's answer into clean one-line facts ('NONE' -> [])."""
    if re.search(r"^\W*none\W*$", raw.strip(), re.I):
        return []
    facts = []
    for line in raw.splitlines():
        m = re.match(r"^\s*(?:[-*•]|\d+[.)])\s*(.+)$", line)
        if not m:
            continue
        t = m.group(1).strip().strip('"')
        if 8 <= len(t) <= MAX_NOTE_CHARS and not re.match(r"^(none|n/a|no (new )?facts?)\b", t, re.I):
            facts.append(t)
    return facts[:limit]


# ---------------------------------------------------------------- recalling old chats
def exchanges(store: ProjectStore, exclude_sid: Optional[str]) -> List[Dict]:
    """Every (user message, assistant reply) pair in the project's other chats, newest chat first."""
    out: List[Dict] = []
    for s in store.list_sessions():
        if s["id"] == exclude_sid:
            continue
        msgs = store.load(s["id"])
        for i, m in enumerate(msgs):
            if m.get("role") == "user" and i + 1 < len(msgs) and msgs[i + 1].get("role") == "assistant":
                reply = msgs[i + 1]["content"]
                if reply.startswith(("⚠️", "⏹")):
                    continue
                out.append({"sid": s["id"], "title": s["title"], "user": m["content"][:400],
                            "assistant": reply[:500], "ts": m.get("ts", 0)})
        if len(out) >= MAX_EXCHANGES_SCANNED:
            break
    return out[:MAX_EXCHANGES_SCANNED]


def recall(store: ProjectStore, query: str, exclude_sid: Optional[str] = None, k: int = 3) -> List[Dict]:
    """BM25 over earlier exchanges; 'what did we decide earlier?'-style questions search more widely."""
    ex = exchanges(store, exclude_sid)
    if not ex:
        return []
    broad = bool(_RECALL_WORDS.search(query))
    k = 5 if broad else k
    docs = [Counter(tokenize(e["user"] + " " + e["assistant"] + " " + e["title"])) for e in ex]
    n = len(ex)
    df: Counter = Counter()
    for d in docs:
        df.update(d.keys())
    qtoks = set(tokenize(query))
    scored = []
    for e, d in zip(ex, docs):
        hits = [t for t in qtoks if t in d]
        if not hits:
            continue
        s = sum(math.log(1 + (n + 1) / (df[t] + 0.5)) * (1 + math.log(d[t])) for t in hits)
        scored.append((s, len(hits), e))
    min_score = 1.2 if broad else 2.4
    keep = [x for x in scored if x[0] >= min_score and (x[1] >= 2 or broad or x[0] >= 3.2)]
    keep.sort(key=lambda x: (x[0], x[2]["ts"]), reverse=True)
    picked = [e for _, _, e in keep[:k]]
    if not picked and broad:                                   # "what did we discuss?" -> latest exchanges
        picked = sorted(ex, key=lambda e: e["ts"], reverse=True)[:3]
    return picked


def format_block(notes: List[Dict], recalled: List[Dict], notes_budget: int = NOTES_BLOCK_CHARS) -> str:
    parts = []
    if notes:
        lines, used = [], 0
        for n in reversed(notes):                              # newest first, until the budget is used
            if used + len(n["text"]) + 3 > notes_budget:
                break
            lines.append(f"- {n['text']}")
            used += len(n["text"]) + 3
        parts.append("PROJECT MEMORY - facts saved from earlier chats in this project (rely on them unless the "
                     "user says otherwise):\n" + "\n".join(reversed(lines)))
    if recalled:
        rows = []
        for e in recalled:
            rows.append(f"[Earlier chat: {e['title']}]\nUser: {e['user'][:EXCERPT_CHARS // 2]}\n"
                        f"Assistant: {e['assistant'][:EXCERPT_CHARS // 2]}")
        parts.append("RELATED EARLIER CHATS - excerpts from other conversations in this project:\n" + "\n\n".join(rows))
    return "\n\n".join(parts)
