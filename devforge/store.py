"""Per-folder chat sessions (many chats per project, each either Chat or Code mode)
and the recent-folders list.

Layout:  <folder>/.devforge/chats/<id>.json  =
    {"id", "mode", "title", "title_auto", "created", "updated", "messages": [...]}
"""
import json
import os
import re
import tempfile
import time
from typing import Dict, List, Optional

from devforge import config

_ID_RE = re.compile(r"^[0-9a-f]{6,20}$")


def _atomic_write(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def fallback_title(text: str, max_len: int = 42) -> str:
    """Instant provisional chat title taken from the first prompt."""
    text = re.sub(r"\s+", " ", text).strip().strip("`'\"")
    if not text:
        return "New chat"
    words = text.split(" ")[:7]
    title = " ".join(words)
    if len(title) > max_len:
        title = title[:max_len].rsplit(" ", 1)[0] or title[:max_len]
    return title[0].upper() + title[1:]


class ProjectStore:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self.dir = os.path.join(self.root, config.STATE_DIRNAME)
        self.chats_dir = os.path.join(self.dir, "chats")

    # ---- low level ---------------------------------------------------------
    def _path(self, sid: str) -> str:
        if not _ID_RE.match(sid or ""):
            raise ValueError(f"bad chat id: {sid!r}")
        return os.path.join(self.chats_dir, f"{sid}.json")

    def _read(self, sid: str) -> Optional[Dict]:
        try:
            with open(self._path(sid), "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else None
        except (OSError, ValueError):
            return None

    # ---- sessions ----------------------------------------------------------
    def create(self, mode: str, title: str) -> Dict:
        assert mode in ("chat", "code")
        now = time.time()
        sid = f"{int(now * 1000):x}"
        while os.path.exists(self._path(sid)):
            sid = f"{int(sid, 16) + 1:x}"
        data = {"id": sid, "mode": mode, "title": title or "New chat", "title_auto": True,
                "created": now, "updated": now, "messages": []}
        _atomic_write(self._path(sid), data)
        return self._summary(data)

    @staticmethod
    def _summary(d: Dict) -> Dict:
        return {"id": d["id"], "mode": d.get("mode", "code"), "title": d.get("title", "New chat"),
                "title_auto": d.get("title_auto", True), "updated": d.get("updated", 0),
                "count": len(d.get("messages", []))}

    def list_sessions(self) -> List[Dict]:
        """Newest first."""
        self._migrate_legacy()
        out = []
        try:
            names = os.listdir(self.chats_dir)
        except OSError:
            return []
        for fn in names:
            if fn.endswith(".json") and _ID_RE.match(fn[:-5]):
                d = self._read(fn[:-5])
                if d and d.get("id"):
                    out.append(self._summary(d))
        out.sort(key=lambda s: s["updated"], reverse=True)
        return out

    def meta(self, sid: str) -> Optional[Dict]:
        d = self._read(sid)
        return self._summary(d) if d else None

    def load(self, sid: str) -> List[Dict]:
        d = self._read(sid)
        return d.get("messages", []) if d else []

    def append(self, sid: str, role: str, content: str, meta: Dict = None) -> None:
        d = self._read(sid)
        if d is None:
            raise KeyError(f"chat {sid} does not exist")
        now = time.time()
        d.setdefault("messages", []).append({"role": role, "content": content, "ts": now, "meta": meta or {}})
        d["updated"] = now
        _atomic_write(self._path(sid), d)

    def rename(self, sid: str, title: str, auto: bool = False) -> bool:
        d = self._read(sid)
        title = re.sub(r"\s+", " ", title).strip()
        if d is None or not title:
            return False
        if auto and not d.get("title_auto", True):
            return False             # never overwrite a name the user chose
        d["title"] = title[:80]
        d["title_auto"] = auto
        _atomic_write(self._path(sid), d)
        return True

    def delete(self, sid: str) -> None:
        try:
            os.remove(self._path(sid))
        except OSError:
            pass

    # ---- migration from the single-history format ------------------------------
    def _migrate_legacy(self) -> None:
        for mode in ("chat", "code"):
            old = os.path.join(self.dir, f"{mode}_history.json")
            if not os.path.exists(old):
                continue
            try:
                with open(old, "r", encoding="utf-8") as f:
                    msgs = json.load(f)
            except (OSError, ValueError):
                msgs = []
            if isinstance(msgs, list) and msgs:
                first = next((m.get("content", "") for m in msgs if m.get("role") == "user"), "")
                meta = self.create(mode, fallback_title(first))
                d = self._read(meta["id"])
                d["messages"] = msgs
                d["updated"] = msgs[-1].get("ts", d["updated"]) or d["updated"]
                d["created"] = msgs[0].get("ts", d["created"]) or d["created"]
                _atomic_write(self._path(meta["id"]), d)
            try:
                os.replace(old, old + ".migrated")
            except OSError:
                pass


# ---------------------------------------------------------------- recent folders
def _recent_file() -> str:
    return os.path.join(os.path.expanduser("~"), ".devforge", "recent.json")


def load_recent() -> List[str]:
    try:
        with open(_recent_file(), "r", encoding="utf-8") as f:
            return [p for p in json.load(f) if os.path.isdir(p)]
    except (OSError, ValueError):
        return []


def add_recent(path: str) -> List[str]:
    path = os.path.abspath(path)
    items = [p for p in load_recent() if os.path.normcase(p) != os.path.normcase(path)]
    items.insert(0, path)
    items = items[:20]
    _atomic_write(_recent_file(), items)
    return items


def remove_recent(path: str) -> List[str]:
    items = [p for p in load_recent() if os.path.normcase(p) != os.path.normcase(path)]
    _atomic_write(_recent_file(), items)
    return items


# ---------------------------------------------------------------- app settings (e.g. light/dark theme)
def _settings_file() -> str:
    return os.path.join(os.path.expanduser("~"), ".devforge", "settings.json")


def load_settings() -> dict:
    try:
        with open(_settings_file(), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_setting(key: str, value) -> None:
    data = load_settings()
    data[key] = value
    try:
        _atomic_write(_settings_file(), data)
    except OSError:
        pass
