from src.agents.base_agent import BaseAgent
from src.llm.ollama_client import OllamaClient

DEBUGGER_SYSTEM = """You are the Lead Systems Debugger & Diagnostic Engineer of DevForge AI.
Your role:
1. Examine failing test outputs, compiler traces, syntax errors, or runtime exceptions.
2. Pinpoint the root cause accurately (e.g. missing import, unclosed tag, type error, broken file path).
3. Generate the fully corrected, working file.
Format your fix in a standard code block:
```python
# filename: <filename>
... corrected full file contents ...
```
"""

class DebuggerAgent(BaseAgent):
    def __init__(self, model: str, client: OllamaClient):
        super().__init__(name="Debugger", role="Automated Diagnosis & Bug Healing", model=model, client=client)

    def diagnose_and_fix(self, code: str, error_trace: str) -> str:
        prompt = (
            f"Failing Code / Files:\n{code}\n\n"
            f"Error / Test Traceback:\n{error_trace}\n\n"
            f"Diagnose this error and output the fully corrected, complete file with no omissions."
        )
        return self.run_stream(DEBUGGER_SYSTEM, prompt)
