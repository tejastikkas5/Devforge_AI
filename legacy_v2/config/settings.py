import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent

class AppConfig(BaseModel):
    app_name: str = "DevForge AI"
    version: str = "2.0.0"
    ollama_url: str = "http://127.0.0.1:11434"
    
    # Workspace root where projects live
    workspace_dir: str = str(BASE_DIR / "workspace")

    # Backend specialized model routing policy
    # Exactly mapped to our downloaded heterogeneous multi-agent suite:
    default_planner_model: str = "deepseek-coder:6.7b"
    default_coder_model: str = "qwen2.5-coder:7b"
    default_tester_model: str = "codegemma:2b"
    default_debugger_model: str = "qwen2.5-coder:1.5b"
    
    # Preferred models for high-tier hardware when available
    preferred_planner_model: str = "deepseek-coder:6.7b"
    preferred_coder_model: str = "qwen2.5-coder:7b"
    preferred_tester_model: str = "codegemma:2b"
    preferred_debugger_model: str = "qwen2.5-coder:1.5b"

    # UI Theme
    theme: str = "dark"
    color_theme: str = "blue"

config = AppConfig()

# Ensure workspace directory exists
os.makedirs(config.workspace_dir, exist_ok=True)
