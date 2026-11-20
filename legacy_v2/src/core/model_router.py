from typing import Dict, List
from config.settings import config
from src.llm.ollama_client import OllamaClient

class ModelRouter:
    """
    Automated backend model router.
    The user NEVER selects models in the UI.
    Instead, this router inspects installed Ollama models and routes each agent
    (Planner, Coder, Tester, Debugger) to the best installed model.
    """

    def __init__(self, client: OllamaClient):
        self.client = client
        self._installed_models: List[str] = []
        self.refresh()

    def refresh(self):
        """Discovers available models from local Ollama daemon."""
        try:
            self._installed_models = self.client.list_models()
        except Exception:
            self._installed_models = []

    def get_model_for_role(self, role: str) -> str:
        """
        Returns the best matching model for a specific agent role.
        Role can be: 'planner', 'coder', 'tester', 'debugger'
        """
        if not self._installed_models:
            # Fallback to configured default
            return getattr(config, f"default_{role}_model", "qwen2.5-coder:1.5b")

        # Check for preferred models in priority order
        role = role.lower()
        if role == "planner":
            candidates = ["deepseek-coder:6.7b", "deepseek-coder-v2", "deepseek-coder", "qwen2.5-coder:7b", "qwen2.5-coder"]
        elif role == "coder":
            candidates = ["qwen2.5-coder:7b", "codestral", "deepseek-coder", "qwen2.5-coder:1.5b", "qwen2.5-coder"]
        elif role == "tester":
            candidates = ["codegemma:2b", "codegemma", "qwen2.5-coder:1.5b", "qwen2.5-coder"]
        elif role == "debugger":
            candidates = ["qwen2.5-coder:1.5b", "devstral", "qwen2.5-coder:7b", "deepseek-coder", "qwen2.5-coder"]
        else:
            candidates = ["qwen2.5-coder"]

        for cand in candidates:
            for installed in self._installed_models:
                if cand in installed:
                    return installed

        # If no specific match, use the first available installed model
        return self._installed_models[0]

    def get_active_routing_summary(self) -> Dict[str, str]:
        """Returns a snapshot of which models are actively handling each task."""
        return {
            "Planner": self.get_model_for_role("planner"),
            "Coder": self.get_model_for_role("coder"),
            "Tester": self.get_model_for_role("tester"),
            "Debugger": self.get_model_for_role("debugger"),
        }
