"""Thin Ollama HTTP client (streaming chat + embeddings) and model resolution."""
import json
import os
import shutil
import subprocess
import time
from typing import Callable, Dict, Generator, List, Optional

import requests

from devforge import config


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, base_url: str = config.OLLAMA_URL,
                 num_ctx: int = config.NUM_CTX, keep_alive: str = config.KEEP_ALIVE):
        self.base_url = base_url.rstrip("/")
        self.num_ctx = num_ctx
        self.keep_alive = keep_alive

    # ---- server management -------------------------------------------------
    def is_alive(self) -> bool:
        try:
            return requests.get(f"{self.base_url}/api/tags", timeout=2).status_code == 200
        except requests.RequestException:
            return False

    def ensure_server(self) -> bool:
        if self.is_alive():
            return True
        exe = shutil.which("ollama")
        for p in (os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
                  r"C:\Program Files\Ollama\ollama.exe"):
            if not exe and os.path.exists(p):
                exe = p
        if not exe:
            return False
        env = os.environ.copy()
        if os.path.isdir(config.OLLAMA_MODELS_DIR):
            env.setdefault("OLLAMA_MODELS", config.OLLAMA_MODELS_DIR)
        try:
            subprocess.Popen([exe, "serve"], env=env,
                             creationflags=0x08000000 if os.name == "nt" else 0)
        except OSError:
            return False
        for _ in range(15):
            time.sleep(1)
            if self.is_alive():
                return True
        return False

    def list_models(self) -> List[str]:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]
        except (requests.RequestException, ValueError):
            return []

    # ---- chat --------------------------------------------------------------
    def stream(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.2,
               num_predict: Optional[int] = None,
               cancel: Optional[Callable[[], bool]] = None) -> Generator[str, None, None]:
        options = {"temperature": temperature, "num_ctx": self.num_ctx}
        if num_predict:
            options["num_predict"] = num_predict
        payload = {"model": model, "messages": messages, "stream": True,
                   "keep_alive": self.keep_alive, "options": options}
        try:
            resp = requests.post(f"{self.base_url}/api/chat", json=payload,
                                 stream=True, timeout=(10, 900))
        except requests.RequestException as e:
            raise OllamaError(f"Cannot reach Ollama at {self.base_url}: {e}") from e
        if resp.status_code != 200:
            body = resp.text[:300]
            resp.close()
            raise OllamaError(f"Ollama error {resp.status_code}: {body}")
        try:
            for line in resp.iter_lines():
                if cancel and cancel():
                    break
                if not line:
                    continue
                chunk = json.loads(line.decode("utf-8"))
                if chunk.get("error"):
                    raise OllamaError(chunk["error"])
                piece = chunk.get("message", {}).get("content", "")
                if piece:
                    yield piece
                if chunk.get("done"):
                    break
        except requests.RequestException as e:
            raise OllamaError(f"Connection to Ollama lost: {e}") from e
        finally:
            resp.close()

    def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.2,
             num_predict: Optional[int] = None, cancel=None) -> str:
        return "".join(self.stream(model, messages, temperature, num_predict, cancel))

    # ---- embeddings --------------------------------------------------------
    def embed(self, model: str, texts: List[str]) -> List[List[float]]:
        try:
            r = requests.post(f"{self.base_url}/api/embed",
                              json={"model": model, "input": texts, "keep_alive": self.keep_alive},
                              timeout=120)
            r.raise_for_status()
            return r.json()["embeddings"]
        except (requests.RequestException, KeyError, ValueError) as e:
            raise OllamaError(f"Embedding failed: {e}") from e


def resolve_model(wanted: str, installed: List[str]) -> Optional[str]:
    """Pick the installed model closest to `wanted` (exact > same family > any coder > any)."""
    if not installed:
        return None
    if wanted in installed:
        return wanted
    family = wanted.split(":")[0]
    for m in installed:
        if m.split(":")[0] == family:
            return m
    for m in installed:
        if "coder" in m:
            return m
    chat_capable = [m for m in installed if config.EMBED_MODEL_HINT not in m]
    return (chat_capable or installed)[0]


def pick_embed_model(installed: List[str]) -> Optional[str]:
    for m in installed:
        if config.EMBED_MODEL_HINT in m:
            return m
    return None
