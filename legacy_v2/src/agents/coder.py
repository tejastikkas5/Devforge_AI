import re
from typing import Dict, List, Tuple
from src.agents.base_agent import BaseAgent
from src.llm.ollama_client import OllamaClient

CODER_SYSTEM = """You are the Senior Full-Stack Implementation Engineer (Coder Agent) of DevForge AI.
Your role:
1. Implement the requested software end-to-end based on the architectural plan and user goal.
2. If the user asks for a standalone script or algorithm (e.g. Python, C++, Node.js):
   - Generate clean, self-contained, executable script files (e.g. `main.py` or `prime_numbers.py`).
3. If the user asks for a website, dashboard, or web application:
   - Generate complete frontend (`index.html`, `styles.css`, `app.js`) and backend files.
4. ZERO CODE OMISSIONS: Do NOT write "TODO", "code goes here", or truncated logic. Everything must work out-of-the-box when the user clicks 'Run Project'.
5. Format every file in a standard markdown code block with the filename on the very first line comment, e.g.:
```python
# filename: prime_numbers.py
...
```
```html
<!-- filename: index.html -->
...
```
"""

class CoderAgent(BaseAgent):
    def __init__(self, model: str, client: OllamaClient):
        super().__init__(name="Coder", role="Full-Stack Code Implementation", model=model, client=client)

    def generate_code(self, user_request: str, plan: str) -> str:
        prompt = (
            f"User Goal: {user_request}\n\n"
            f"Architectural Plan:\n{plan}\n\n"
            f"Generate all complete, fully-implemented source files. Start each code block with the filename comment."
        )
        return self.run_stream(CODER_SYSTEM, prompt)

    @staticmethod
    def extract_files(llm_output: str) -> List[Tuple[str, str]]:
        """
        Parses code blocks out of LLM output across any programming language.
        Returns a list of (filename, code_content).
        """
        pattern = r"```(?:[a-zA-Z0-9_\-\+\.]+)?\s*\n(?:(?://|#|/\*|<!--)\s*(?:filename:\s*|File:\s*)?([a-zA-Z0-9_\-\./\\]+)(?:\s*\*/|\s*-->)?\s*\n)?(.*?)```"
        matches = re.findall(pattern, llm_output, re.DOTALL)
        
        extracted = []
        default_idx = 1
        for fname, content in matches:
            filename = fname.strip() if fname and fname.strip() else f"generated_code_{default_idx}"
            clean_content = content.strip()
            if clean_content:
                extracted.append((filename, clean_content))
                default_idx += 1
            
        return extracted
