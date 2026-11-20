from src.agents.base_agent import BaseAgent
from src.llm.ollama_client import OllamaClient

TESTER_SYSTEM = """You are the Senior QA & Automation Verification Engineer (Tester Agent) of DevForge AI.
Your role:
1. Write verification tests or smoke tests for the synthesized project code.
2. If Python code or a server was generated, write standard Python `unittest` tests to verify module imports, API endpoints, or core algorithmic functions.
3. If an HTML/JS frontend was generated, write a Python smoke-test script (e.g. `verify_project.py`) that parses `index.html`, checks that referenced CSS/JS files exist on disk, and verifies HTML tag completeness.
4. Output the test suite in a clear code block:
```python
# filename: test_suite.py
import unittest
...
if __name__ == '__main__':
    unittest.main()
```
"""

class TesterAgent(BaseAgent):
    def __init__(self, model: str, client: OllamaClient):
        super().__init__(name="Tester", role="QA & Autonomous Verification", model=model, client=client)

    def generate_tests(self, user_request: str, generated_code: str) -> str:
        prompt = (
            f"User Goal: {user_request}\n\n"
            f"Generated Project Code:\n{generated_code}\n\n"
            f"Write an automated verification test suite (Python unittest format) to verify the generated files."
        )
        return self.run_stream(TESTER_SYSTEM, prompt)
