"""Project skills: named instruction notes saved as <project>/skills/<name>.md.

A skill is applied to a prompt in two ways:
  * forced  - the user types /skill-name anywhere in the prompt
  * auto    - DevForge scores the saved skills against the prompt and uses the best 1-2

Files are plain Markdown (with a tiny front-matter header) so they can be edited by hand;
plain .txt files dropped into the folder are read too.
"""
import os
import re
import tempfile
from typing import Dict, List, Optional, Tuple

from devforge.rag import tokenize

SKILLS_DIRNAME = "skills"
MAX_INJECT_CHARS = 1500        # per skill, what the (small, limited-context) model actually receives
MAX_AUTO_SKILLS = 2
MAX_NAME_LEN = 40
_SLASH = re.compile(r"(?<!\S)/([A-Za-z0-9][\w-]*)")


class SkillError(ValueError):
    pass


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")[:MAX_NAME_LEN].strip("-")
    if not slug:
        raise SkillError("Please give the skill a name (letters or numbers).")
    return slug


def _parse(raw: str, fallback_name: str) -> Tuple[str, str, str]:
    """-> (name, description, body). Reads the front-matter header if present."""
    name, desc, body = fallback_name, "", raw
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S)
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            if k.strip().lower() == "name" and v.strip():
                name = v.strip()
            elif k.strip().lower() == "description":
                desc = v.strip()
        body = m.group(2)
    elif fallback_name and raw.strip():
        desc = raw.strip().splitlines()[0][:120]       # plain .txt: first line doubles as the description
    return name, desc, body.strip()


class SkillStore:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self.dir = os.path.join(self.root, SKILLS_DIRNAME)

    def _path(self, slug: str, ext: str = ".md") -> str:
        full = os.path.abspath(os.path.join(self.dir, slug + ext))
        if os.path.commonpath([self.dir, full]) != self.dir:
            raise SkillError("invalid skill name")
        return full

    # ---- reading -----------------------------------------------------------
    def list(self) -> List[Dict]:
        out = []
        try:
            files = sorted(os.listdir(self.dir))
        except OSError:
            return out
        for fn in files:
            stem, ext = os.path.splitext(fn)
            if ext.lower() not in (".md", ".txt") or not re.fullmatch(r"[A-Za-z0-9][\w-]*", stem):
                continue
            try:
                with open(os.path.join(self.dir, fn), "r", encoding="utf-8", errors="replace") as f:
                    raw = f.read(200_000)
            except OSError:
                continue
            name, desc, body = _parse(raw, stem)
            out.append({"slug": stem.lower(), "name": name, "description": desc, "text": body,
                        "file": fn, "ext": ext.lower()})
        return out

    def get(self, slug: str) -> Optional[Dict]:
        return next((s for s in self.list() if s["slug"] == slug.lower()), None)

    # ---- writing -----------------------------------------------------------
    def save(self, name: str, text: str, description: str = "", replace_slug: Optional[str] = None) -> Dict:
        """Create or update a skill. Returns the saved skill. Renaming removes the old file."""
        slug = slugify(name)
        if not text.strip():
            raise SkillError("The skill text is empty.")
        header = f"---\nname: {name.strip()}\ndescription: {description.strip().replace(chr(10), ' ')}\n---\n"
        os.makedirs(self.dir, exist_ok=True)
        path = self._path(slug)
        fd, tmp = tempfile.mkstemp(dir=self.dir, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(header + text.strip() + "\n")
        os.replace(tmp, path)
        if replace_slug and replace_slug != slug:
            self.delete(replace_slug)
        # a same-named .txt would shadow nothing, but keep one file per skill
        txt = self._path(slug, ".txt")
        if os.path.exists(txt):
            os.remove(txt)
        return self.get(slug)

    def delete(self, slug: str) -> bool:
        removed = False
        for ext in (".md", ".txt"):
            try:
                p = self._path(slug.lower(), ext)
            except SkillError:
                continue
            if os.path.exists(p):
                os.remove(p)
                removed = True
        return removed


# ---------------------------------------------------------------- choosing skills for a prompt
def split_forced(text: str, skills: List[Dict]) -> Tuple[str, List[Dict]]:
    """Find /skill-name tokens that match a real skill. Returns (prompt without them, forced skills).
    Unknown /words are left alone (they may be paths)."""
    by_slug = {s["slug"]: s for s in skills}
    forced: List[Dict] = []

    def take(m):
        s = by_slug.get(m.group(1).lower())
        if s is None:
            return m.group(0)
        if s not in forced:
            forced.append(s)
        return ""

    clean = re.sub(r"[ \t]{2,}", " ", _SLASH.sub(take, text)).strip()
    return clean, forced


def score(prompt: str, skill: Dict) -> int:
    q = set(tokenize(prompt))
    head = set(tokenize(skill["name"] + " " + skill["description"] + " " + skill["slug"].replace("-", " ")))
    body = set(tokenize(skill["text"]))
    return 3 * len(q & head) + len(q & (body - head))


def auto_select(prompt: str, skills: List[Dict], exclude: List[Dict], limit: int = MAX_AUTO_SKILLS) -> List[Dict]:
    """Skills whose name/description match the prompt, or whose body shares several words with it."""
    taken = {s["slug"] for s in exclude}
    scored = [(score(prompt, s), s) for s in skills if s["slug"] not in taken]
    scored = [(sc, s) for sc, s in scored if sc >= 3]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:limit]]


def pick(text: str, skills: List[Dict]) -> Tuple[str, List[Tuple[Dict, str]]]:
    """-> (prompt with /tokens removed, [(skill, 'forced'|'auto')])"""
    clean, forced = split_forced(text, skills)
    if forced and not clean:
        clean = "Apply the skill " + ", ".join(f"'{s['name']}'" for s in forced) + " to this project."
    auto = auto_select(clean, skills, forced)
    return clean, [(s, "forced") for s in forced] + [(s, "auto") for s in auto]


def format_block(chosen: List[Tuple[Dict, str]]) -> str:
    """Text appended to the model's prompt. Each skill is capped for the small context window."""
    if not chosen:
        return ""
    parts = []
    for s, _ in chosen:
        body = s["text"]
        if len(body) > MAX_INJECT_CHARS:
            body = body[:MAX_INJECT_CHARS].rsplit("\n", 1)[0] + "\n[...skill text cut to fit]"
        parts.append(f"### Skill: {s['name']}\n{body}")
    return ("USER SKILLS - the user wrote these standing instructions for this project. Follow them "
            "whenever they apply to the request:\n\n" + "\n\n".join(parts))
