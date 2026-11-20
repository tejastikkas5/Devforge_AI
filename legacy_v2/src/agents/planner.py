from src.agents.base_agent import BaseAgent
from src.llm.ollama_client import OllamaClient

PLANNER_SYSTEM = """You are the Principal Systems Architect and Planner Agent of DevForge AI.
Your role:
1. Deconstruct the user's software requirement accurately and directly match the requested stack.
2. If the user asks for a simple script or Python program (e.g. "prime number python program", "binary search", "calculator script"):
   - DO NOT invent unnecessary web frontends, HTML, or CSS.
   - Plan ONLY the requested Python script (e.g. `prime_checker.py`) and a corresponding unit test file (e.g. `test_prime_checker.py`).
3. If the user asks for a website, dashboard, or full-stack app (e.g. "portfolio website", "counter web app"):
   - Architect the full solution: Frontend (HTML, CSS, JS) and Backend.
4. Output a concise blueprint with exact filenames and descriptions so the Coder agent can generate 100% complete, runnable code.
"""

class PlannerAgent(BaseAgent):
    def __init__(self, model: str, client: OllamaClient):
        super().__init__(name="Planner", role="Architecture & End-to-End Decomposition", model=model, client=client)

    def plan(self, user_request: str) -> str:
        prompt = (
            f"User Goal: {user_request}\n\n"
            f"Generate a concise, targeted architectural plan. Specifically tailor the architecture to the exact language, framework, or simplicity requested by the user."
        )
        return self.run_stream(PLANNER_SYSTEM, prompt)
