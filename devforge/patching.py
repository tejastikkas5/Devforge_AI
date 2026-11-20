"""Targeted edits: change only the part of a file the user asked for.

For an existing file the model does NOT rewrite the file. It answers with SEARCH/REPLACE blocks:

    <<<<<<< SEARCH
    exact lines copied from the current file
    =======
    the new lines
    >>>>>>> REPLACE

and the code below applies them. Every line the model did not mention stays exactly as it was, so
old features cannot be lost by a model that "forgot" them while rewriting.
"""
import re
from typing import List, Optional, Set, Tuple

_BLOCK = re.compile(
    r"<{5,9}\s*SEARCH[^\n]*\n(.*?)\n?={5,9}[ \t]*\n(.*?)\n?>{5,9}\s*REPLACE", re.S)


def parse_edits(text: str) -> List[Tuple[str, str]]:
    """[(search, replace)] from a model reply (code fences around the blocks are allowed)."""
    return [(s, r) for s, r in _BLOCK.findall(text or "")]


def _norm(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def _find(src_lines: List[str], search_lines: List[str]) -> List[int]:
    """Start indexes where `search_lines` match `src_lines` ignoring indentation / inner spacing."""
    want = [_norm(x) for x in search_lines if x.strip()]
    if not want:
        return []
    hits = []
    for i in range(len(src_lines)):
        if not src_lines[i].strip():                    # a match never starts on a blank line
            continue
        j, k = i, 0
        while j < len(src_lines) and k < len(want):
            if not src_lines[j].strip():                # blank lines in the file never break a match
                j += 1
                continue
            if _norm(src_lines[j]) != want[k]:
                break
            j += 1
            k += 1
        if k == len(want):
            hits.append((i, j))
    # keep the first / shortest window per start
    return hits


def _indent(line: str) -> str:
    return re.match(r"[ \t]*", line).group(0)


def _reindent(matched: List[str], search: List[str], replace: List[str]) -> List[str]:
    """Give the replacement lines the file's real indentation when the model's SEARCH/REPLACE lost it:
    a replacement line equal to a matched line takes that line's indentation; a new line takes the
    indentation of the line above it in the file (plus any extra indent the model gave it)."""
    pairs = list(zip([s for s in search if s.strip()], [m for m in matched if m.strip()]))  # (model line, file line)
    if not pairs:
        return replace
    by_text = {_norm(s): (s, m) for s, m in pairs}
    out, k = [], 0
    for r in replace:
        if not r.strip():
            out.append(r)
            continue
        s, m = by_text.get(_norm(r)) or pairs[min(k, len(pairs) - 1)]
        delta = len(_indent(r)) - len(_indent(s))       # extra indent the model gave this line, relative to its anchor
        base = _indent(m)
        if delta > 0:
            base = base + " " * delta
        elif delta < 0:
            base = base[:max(0, len(base) + delta)]
        out.append(base + r.lstrip())
        k += 1
    return out


def apply_edits(src: str, edits: List[Tuple[str, str]]) -> Tuple[str, List[str]]:
    """Apply SEARCH/REPLACE edits in order. Returns (new_source, errors). An edit whose SEARCH text is
    missing or appears more than once is NOT applied and reported in errors (nothing is guessed)."""
    errors: List[str] = []
    out = src
    for n, (search, replace) in enumerate(edits, 1):
        if not search.strip():                          # empty SEARCH = add the new code at the end
            out = out.rstrip("\n") + "\n" + replace.rstrip("\n") + "\n"
            continue
        count = out.count(search)
        if count == 1:
            out = out.replace(search, replace, 1)
            continue
        if count > 1:
            errors.append(f"edit {n}: the SEARCH text appears {count} times - include more surrounding lines so it is unique")
            continue
        lines = out.split("\n")
        hits = _find(lines, search.split("\n"))
        if len(hits) == 1:                              # same lines, different indentation / spacing
            i, j = hits[0]
            lines[i:j] = _reindent(lines[i:j], search.split("\n"), replace.split("\n"))
            out = "\n".join(lines)
            continue
        if len(hits) > 1:
            errors.append(f"edit {n}: the SEARCH text appears {len(hits)} times - include more surrounding lines so it is unique")
        else:
            first = next((x for x in search.split("\n") if x.strip()), "")[:80]
            errors.append(f"edit {n}: the SEARCH text was not found in the file (it starts with: {first!r}) - "
                          "copy the lines exactly from the CURRENT CONTENT")
    return out, errors


# ---------------------------------------------------------------- what a file defines (for the no-loss guard)
_JS_NAMES = re.compile(r"""\bfunction\s+([A-Za-z_$][\w$]*)|\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)""")
_PY_NAMES = re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)|^\s*class\s+([A-Za-z_]\w*)", re.M)
_HTML_IDS = re.compile(r"""\bid\s*=\s*["']([^"']+)["']""")
_CSS_SEL = re.compile(r"""([.#][A-Za-z_][\w-]*)""")


def defined_names(rel: str, src: str) -> Set[str]:
    """Functions (JS/Python), element ids (HTML) or selectors (CSS) a file defines."""
    ext = rel.rsplit(".", 1)[-1].lower() if "." in rel else ""
    if ext == "js":
        return {a or b for a, b in _JS_NAMES.findall(src)}
    if ext == "py":
        return {a or b for a, b in _PY_NAMES.findall(src)}
    if ext in ("html", "htm"):
        return set(_HTML_IDS.findall(src))
    if ext == "css":
        body_free = re.sub(r"\{[^{}]*\}", "{}", src)
        return set(_CSS_SEL.findall(body_free))
    return set()


_REMOVE_WORDS = re.compile(r"\b(remove|delete|drop|get rid of|rename|replace|rewrite|from scratch|start over|"
                           r"clean ?up|refactor|instead of)\b", re.I)


def lost_names(rel: str, old: str, new: str, request: str = "") -> List[str]:
    """Names the old file defined that the new version silently dropped. Empty when the user asked for a
    removal/rewrite (then losing things is intended) or when nothing was lost."""
    if _REMOVE_WORDS.search(request or ""):
        return []
    gone = defined_names(rel, old) - defined_names(rel, new)
    return sorted(gone)
