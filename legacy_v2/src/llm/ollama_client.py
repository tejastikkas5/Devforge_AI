import os
import time
import subprocess
import json
import requests
from typing import Generator, List, Dict, Any, Optional

class OllamaClient:
    def __init__(self, base_url: str = "http://127.0.0.1:11434"):
        self.base_url = base_url.rstrip("/")

    def ensure_server_running(self) -> bool:
        """Checks if Ollama is running; if not, automatically launches the daemon with E:\\OllamaModels."""
        if self.is_alive():
            return True

        possible_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
            r"C:\Users\ASUS\AppData\Local\Programs\Ollama\ollama.exe",
            r"C:\Program Files\Ollama\ollama.exe",
            "ollama"
        ]
        exe_path = None
        for p in possible_paths:
            if os.path.exists(p) or p == "ollama":
                exe_path = p
                break

        if not exe_path:
            return False

        try:
            env = os.environ.copy()
            env["OLLAMA_MODELS"] = r"E:\OllamaModels"
            creation_flags = 0x08000000 if os.name == "nt" else 0
            subprocess.Popen([exe_path, "serve"], env=env, creationflags=creation_flags)

            for _ in range(10):
                time.sleep(1)
                if self.is_alive():
                    return True
        except Exception as e:
            print(f"[OllamaClient] Auto-start daemon error: {e}")

        return self.is_alive()

    def is_alive(self) -> bool:
        """Check if Ollama server daemon is accessible."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=2.0)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        """Fetch list of locally available model names, auto-starting server if needed."""
        self.ensure_server_running()
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            print(f"[OllamaClient] Error fetching models: {e}")
        return []

    def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2
    ) -> Generator[str, None, None]:
        """
        Stream tokens from Ollama chat endpoint.
        Yields chunk tokens as they arrive.
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            with requests.post(url, json=payload, stream=True, timeout=180.0) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        if "message" in chunk and "content" in chunk["message"]:
                            yield chunk["message"]["content"]
                        if chunk.get("done", False):
                            break
        except Exception as e:
            yield f"\n[Error communicating with Ollama: {e}]"

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2
    ) -> str:
        """Non-streaming chat request returning full content string."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        try:
            resp = requests.post(url, json=payload, timeout=120.0)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")
        except Exception as e:
            return f"[Error: {e}]"
