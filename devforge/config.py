"""Central configuration: which Ollama model does which job."""
import os

OLLAMA_URL = os.environ.get("OLLAMA_HOST_URL", "http://127.0.0.1:11434")

# One model per role (all installed locally through Ollama). Every role can use a different model,
# but on a 4 GB GPU each switch between two 4-5 GB models reloads one from disk. So all roles share the
# strongest local coder: no swaps (faster), and the Debugger / Tester no longer run on 1.5B-2B models
# that were too weak to fix code or write tests. Change any line to use another installed model.
CODER_MODEL = "qwen2.5-coder:7b"
ROLE_MODELS = {
    "planner": CODER_MODEL,             # breaks a request into a file plan
    "coder": CODER_MODEL,               # writes every file, answers project questions
    "tester": CODER_MODEL,              # writes unit tests
    "debugger": CODER_MODEL,            # fixes failing code; also routes prompts, names chats, saves memory
    "chat": CODER_MODEL,                # free-form Chat tab
    "researcher": CODER_MODEL,          # writes a short design brief for new websites
    "reviewer": CODER_MODEL,            # reviews the finished logic for proven bugs only
    "designer": CODER_MODEL,            # picks the UI theme/accent for websites
}

ENABLE_DESIGNER = True              # set False to skip the Designer step
ENABLE_RESEARCH = True              # set False to skip the Research step (faster)
ENABLE_REVIEW = True                # set False to skip the Review step (faster)
ENABLE_THEME_SWITCH = True          # every new website gets the light/dark switch + mobile menu built in
MAX_REVIEW_ISSUES = 2

# Optional embedding model. If one is installed, RAG becomes hybrid (BM25 + vectors).
EMBED_MODEL_HINT = "embed"          # any installed model whose name contains this

NUM_CTX = 8192                      # context window requested from Ollama
KEEP_ALIVE = "30m"                  # keep the model loaded between agent hand-offs and prompts
MAX_DEBUG_ROUNDS = 2
MAX_PLAN_FILES = 5
OLLAMA_MODELS_DIR = r"E:\OllamaModels"   # used only when starting the daemon ourselves

STATE_DIRNAME = ".devforge"         # per-project folder holding history + RAG cache
