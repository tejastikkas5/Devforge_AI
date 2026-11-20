"""Code RAG: AST-aware chunking + BM25 keyword search + optional embedding search,
fused with reciprocal-rank fusion. Pure Python (no vector DB dependency).

Index state lives in memory; embeddings (if an embedding model is installed) are cached
in <project>/.devforge/embeddings.json so they are only computed once per chunk.
"""
import ast
import hashlib
import json
import math
import os
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from devforge import config
from devforge.llm import OllamaClient, OllamaError

SKIP_DIRS = {".git", ".venv", "venv", "env", "node_modules", "__pycache__", ".idea", ".vscode",
             "dist", "build", ".mypy_cache", ".pytest_cache", config.STATE_DIRNAME}
TEXT_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".htm", ".css", ".json", ".md", ".txt",
            ".c", ".h", ".cpp", ".hpp", ".java", ".go", ".rs", ".cs", ".sql", ".yml", ".yaml",
            ".toml", ".sh", ".bat", ".php", ".rb", ".xml", ".ini", ".cfg"}
MAX_FILE_BYTES = 200_000
STOP = {"the", "and", "for", "with", "that", "this", "from", "are", "you", "can", "not", "all",
        "def", "return", "self", "var", "let", "const", "import", "class", "function"}


@dataclass
class Chunk:
    path: str          # relative, forward slashes
    start: int
    end: int
    kind: str          # function | class | method | module | window
    name: str
    text: str

    @property
    def key(self) -> str:
        return hashlib.sha1(f"{self.path}:{self.start}:{self.text}".encode("utf-8", "ignore")).hexdigest()


def tokenize(text: str) -> List[str]:
    toks: List[str] = []
    for w in re.findall(r"[A-Za-z0-9]+", text):
        low = w.lower()
        toks.append(low)
        parts = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", w).split()
        if len(parts) > 1:
            toks.extend(p.lower() for p in parts)
    return [t for t in toks if len(t) > 1 and t not in STOP]


# ---------------------------------------------------------------- chunking
def _window_chunks(rel: str, lines: List[str], size: int = 40, stride: int = 32) -> List[Chunk]:
    out = []
    i = 0
    while i < len(lines):
        seg = lines[i:i + size]
        if "".join(seg).strip():
            out.append(Chunk(rel, i + 1, i + len(seg), "window", os.path.basename(rel), "\n".join(seg)))
        if i + size >= len(lines):
            break
        i += stride
    return out


def _python_chunks(rel: str, source: str) -> List[Chunk]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return _window_chunks(rel, source.splitlines())
    lines = source.splitlines()
    out: List[Chunk] = []

    def seg(node) -> Tuple[int, int, str]:
        s, e = node.lineno, getattr(node, "end_lineno", node.lineno)
        if getattr(node, "decorator_list", None):
            s = min(s, min(d.lineno for d in node.decorator_list))
        body = lines[s - 1:min(e, s + 79)]
        return s, e, "\n".join(body)

    first_def = None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            first_def = first_def or node.lineno
            s, e, t = seg(node)
            out.append(Chunk(rel, s, e, "function", node.name, t))
        elif isinstance(node, ast.ClassDef):
            first_def = first_def or node.lineno
            s, e, t = seg(node)
            out.append(Chunk(rel, s, e, "class", node.name, t))
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    ss, se, st = seg(sub)
                    out.append(Chunk(rel, ss, se, "method", f"{node.name}.{sub.name}", st))
    head_end = (first_def - 1) if first_def else min(len(lines), 40)
    head = "\n".join(lines[:min(head_end, 40)])
    if head.strip():
        out.insert(0, Chunk(rel, 1, min(head_end, 40), "module", os.path.basename(rel), head))
    return out or _window_chunks(rel, lines)


def chunk_file(rel: str, source: str) -> List[Chunk]:
    if rel.endswith(".py"):
        return _python_chunks(rel, source)
    return _window_chunks(rel, source.splitlines())


# ---------------------------------------------------------------- symbols
_JS_SYM = re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)|^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(?:\(|function|\w+\s*=>)")
_CSS_SEL = re.compile(r"^\s*([.#][\w-]+)[^{]*\{")


def file_outline(rel: str, source: str) -> str:
    syms: List[str] = []
    if rel.endswith(".py"):
        try:
            for n in ast.parse(source).body:
                if isinstance(n, ast.ClassDef):
                    methods = [m.name for m in n.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    syms.append(f"class {n.name}({', '.join(methods[:8])})")
                elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    syms.append(f"def {n.name}()")
        except SyntaxError:
            syms.append("(syntax error)")
    elif rel.endswith((".js", ".jsx", ".ts", ".tsx")):
        for line in source.splitlines():
            m = _JS_SYM.match(line)
            if m:
                syms.append(f"{m.group(1) or m.group(2)}()")
    elif rel.endswith(".css"):
        sels = [m.group(1) for line in source.splitlines() if (m := _CSS_SEL.match(line))]
        syms = sels[:10]
    return ", ".join(syms[:14])


# ---------------------------------------------------------------- index
class CodeIndex:
    def __init__(self, root: str, client: Optional[OllamaClient] = None,
                 embed_model: Optional[str] = None):
        self.root = os.path.abspath(root)
        self.client = client
        self.embed_model = embed_model if client else None
        self._sig: Dict[str, Tuple[float, int]] = {}
        self._file_chunks: Dict[str, List[Chunk]] = {}
        self._outlines: Dict[str, Tuple[int, str]] = {}
        self.chunks: List[Chunk] = []
        self._tf: List[Counter] = []
        self._len: List[int] = []
        self._post: Dict[str, List[Tuple[int, int]]] = {}
        self._emb: Dict[str, List[float]] = {}
        self._emb_loaded = False

    # -- scanning
    def _iter_files(self):
        for dp, dns, fns in os.walk(self.root):
            dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")
                      and not (dp == self.root and d == "skills")]      # skills are handled by devforge.skills
            for fn in fns:
                if os.path.splitext(fn)[1].lower() in TEXT_EXT:
                    full = os.path.join(dp, fn)
                    try:
                        st = os.stat(full)
                    except OSError:
                        continue
                    if st.st_size <= MAX_FILE_BYTES:
                        yield os.path.relpath(full, self.root).replace("\\", "/"), full, st

    def refresh(self) -> int:
        """Re-index changed files. Returns number of chunks."""
        seen = set()
        changed = False
        for rel, full, st in self._iter_files():
            seen.add(rel)
            sig = (st.st_mtime, st.st_size)
            if self._sig.get(rel) == sig:
                continue
            try:
                with open(full, "r", encoding="utf-8", errors="replace") as f:
                    src = f.read()
            except OSError:
                continue
            self._sig[rel] = sig
            self._file_chunks[rel] = chunk_file(rel, src)
            self._outlines[rel] = (src.count("\n") + 1, file_outline(rel, src))
            changed = True
        for gone in set(self._sig) - seen:
            self._sig.pop(gone, None)
            self._file_chunks.pop(gone, None)
            self._outlines.pop(gone, None)
            changed = True
        if changed or not self.chunks:
            self._rebuild()
        if self.embed_model and self.chunks:
            self._embed_missing()
        return len(self.chunks)

    def _rebuild(self):
        self.chunks = [c for rel in sorted(self._file_chunks) for c in self._file_chunks[rel]]
        self._tf, self._len, self._post = [], [], {}
        for i, c in enumerate(self.chunks):
            toks = tokenize(c.text) + tokenize(c.path) * 2 + tokenize(c.name) * 3
            tf = Counter(toks)
            self._tf.append(tf)
            self._len.append(len(toks))
            for t, n in tf.items():
                self._post.setdefault(t, []).append((i, n))

    # -- embeddings (optional)
    def _emb_path(self) -> str:
        return os.path.join(self.root, config.STATE_DIRNAME, "embeddings.json")

    def _embed_missing(self):
        if not self._emb_loaded:
            self._emb_loaded = True
            try:
                with open(self._emb_path(), "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("model") == self.embed_model:
                    self._emb = data.get("vectors", {})
            except (OSError, ValueError):
                pass
        todo = [c for c in self.chunks if c.key not in self._emb][:400]
        if not todo:
            return
        try:
            for i in range(0, len(todo), 16):
                batch = todo[i:i + 16]
                vecs = self.client.embed(self.embed_model, [f"{c.path}\n{c.text}"[:1500] for c in batch])
                for c, v in zip(batch, vecs):
                    self._emb[c.key] = v
        except OllamaError:
            self.embed_model = None     # fall back to BM25 only
            return
        try:
            os.makedirs(os.path.dirname(self._emb_path()), exist_ok=True)
            live = {c.key for c in self.chunks}
            with open(self._emb_path(), "w", encoding="utf-8") as f:
                json.dump({"model": self.embed_model,
                           "vectors": {k: v for k, v in self._emb.items() if k in live}}, f)
        except OSError:
            pass

    # -- search
    def _bm25(self, qtoks: List[str]) -> List[Tuple[int, float]]:
        n = len(self.chunks)
        if not n:
            return []
        avg = sum(self._len) / n or 1.0
        scores: Dict[int, float] = {}
        for t in set(qtoks):
            post = self._post.get(t)
            if not post:
                continue
            idf = math.log(1 + (n - len(post) + 0.5) / (len(post) + 0.5))
            for i, tf in post:
                denom = tf + 1.5 * (0.25 + 0.75 * self._len[i] / avg)
                scores[i] = scores.get(i, 0.0) + idf * tf * 2.5 / denom
        return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    def _dense(self, query: str) -> List[Tuple[int, float]]:
        if not (self.embed_model and self._emb):
            return []
        try:
            q = self.client.embed(self.embed_model, [query])[0]
        except OllamaError:
            return []
        qn = math.sqrt(sum(x * x for x in q)) or 1.0
        out = []
        for i, c in enumerate(self.chunks):
            v = self._emb.get(c.key)
            if v:
                vn = math.sqrt(sum(x * x for x in v)) or 1.0
                out.append((i, sum(a * b for a, b in zip(q, v)) / (qn * vn)))
        return sorted(out, key=lambda kv: kv[1], reverse=True)

    def search(self, query: str, k: int = 6) -> List[Tuple[Chunk, float]]:
        qtoks = tokenize(query)
        bm = self._bm25(qtoks)[:30]
        dn = self._dense(query)[:30]
        fused: Dict[int, float] = {}
        for ranking in (bm, dn):
            for rank, (i, _) in enumerate(ranking):
                fused[i] = fused.get(i, 0.0) + 1.0 / (60 + rank)
        top = sorted(fused.items(), key=lambda kv: kv[1], reverse=True)[:k]
        return [(self.chunks[i], s) for i, s in top]

    # -- context building
    def repo_map(self, max_chars: int = 2200) -> str:
        if not self._outlines:
            return "(the folder has no source files yet)"
        rows = []
        for rel in sorted(self._outlines):
            n, outline = self._outlines[rel]
            rows.append(f"- {rel} ({n} lines)" + (f": {outline}" if outline else ""))
        text = "\n".join(rows)
        return text if len(text) <= max_chars else text[:max_chars] + "\n- ..."

    def context(self, query: str, k: int = 6, max_chars: int = 6000) -> str:
        parts = [f"PROJECT FILES:\n{self.repo_map()}"]
        hits = self.search(query, k) if self.chunks else []
        if hits:
            parts.append("RELEVANT CODE:")
            used = 0
            for c, _ in hits:
                block = f"### {c.path} (lines {c.start}-{c.end}, {c.kind} {c.name})\n```\n{c.text}\n```"
                if used + len(block) > max_chars:
                    break
                parts.append(block)
                used += len(block)
        return "\n\n".join(parts)

    def has_files(self) -> bool:
        return bool(self._outlines)
