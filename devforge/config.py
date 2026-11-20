"""Central configuration: which Ollama model does which job."""
import os

OLLAMA_URL = os.environ.get("OLLAMA_HOST_URL", "http://127.0.0.1:11434")

# One model per role (all installed locally through Ollama).
ROLE_MODELS = {
    "planner": "deepseek-coder:6.7b",   # breaks a request into a file plan
    "coder": "qwen2.5-coder:7b",        # writes every file, answers project questions
    "tester": "codegemma:2b",           # writes unit tests
    "debugger": "qwen2.5-coder:1.5b",   # fixes failing code; also classifies prompt intent
    "chat": "qwen2.5-coder:7b",         # free-form Chat tab
    "researcher": "qwen2.5:7b",         # reads project docs/context, writes a short design brief
    "reviewer": "qwen2.5-coder:7b",     # reviews the finished code for real defects
    "designer": "qwen2.5:7b",           # picks the UI theme/accent for websites (shares the Researcher's model)
}

ENABLE_DESIGNER = True              # set False to skip the Designer step
ENABLE_RESEARCH = True              # set False to skip the Research step (faster)
ENABLE_REVIEW = True                # set False to skip the Review step (faster)
MAX_REVIEW_ISSUES = 3

# Optional embedding model. If one is installed, RAG becomes hybrid (BM25 + vectors).
EMBED_MODEL_HINT = "embed"          # any installed model whose name contains this

NUM_CTX = 8192                      # context window requested from Ollama
KEEP_ALIVE = "10m"                  # keep a model in memory between agent hand-offs
MAX_DEBUG_ROUNDS = 2
MAX_PLAN_FILES = 5
OLLAMA_MODELS_DIR = r"E:\OllamaModels"   # used only when starting the daemon ourselves

STATE_DIRNAME = ".devforge"         # per-project folder holding history + RAG cache
