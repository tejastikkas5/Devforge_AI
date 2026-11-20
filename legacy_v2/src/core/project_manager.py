import os
import json
import re
import datetime
from typing import List, Dict, Any, Optional

class ProjectManager:
    """
    Manages individual projects inside the workspace.
    Each project has its own folder containing:
    - Generated source files (frontend, backend, ui)
    - conversation_history.json (persists all user prompts, agent thoughts, code, and test runs)
    """

    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)
        os.makedirs(self.workspace_root, exist_ok=True)

    def slugify(self, text: str) -> str:
        """Generates a clean directory name from prompt or project title."""
        clean = re.sub(r'[^a-zA-Z0-9_\-\s]', '', text.strip().lower())
        words = clean.split()[:4]
        slug = "_".join(words)
        if not slug:
            slug = "project"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{slug}_{timestamp}"

    def list_projects(self) -> List[Dict[str, Any]]:
        """Scans workspace_root for project folders and loads summary metadata."""
        projects = []
        if not os.path.exists(self.workspace_root):
            return projects

        for entry in os.listdir(self.workspace_root):
            full_path = os.path.join(self.workspace_root, entry)
            if os.path.isdir(full_path) and not entry.startswith('.') and entry != '__pycache__':
                history_file = os.path.join(full_path, "conversation_history.json")
                title = entry
                last_updated = os.path.getmtime(full_path)
                message_count = 0
                preview = "Empty project"

                if os.path.exists(history_file):
                    try:
                        with open(history_file, "r", encoding="utf-8") as f:
                            hist_data = json.load(f)
                            title = hist_data.get("title", entry)
                            messages = hist_data.get("messages", [])
                            message_count = len(messages)
                            if messages:
                                preview = messages[-1].get("text", "")[:80]
                    except Exception:
                        pass

                projects.append({
                    "id": entry,
                    "title": title,
                    "path": full_path,
                    "last_updated": last_updated,
                    "message_count": message_count,
                    "preview": preview
                })

        # Sort newest first
        projects.sort(key=lambda p: p["last_updated"], reverse=True)
        return projects

    def create_project(self, title: str) -> Dict[str, Any]:
        """Creates a brand new dedicated project folder with initial history."""
        folder_name = self.slugify(title)
        project_dir = os.path.join(self.workspace_root, folder_name)
        os.makedirs(project_dir, exist_ok=True)

        history_file = os.path.join(project_dir, "conversation_history.json")
        initial_data = {
            "title": title,
            "created_at": datetime.datetime.now().isoformat(),
            "project_dir": project_dir,
            "messages": []
        }
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2)

        return {
            "id": folder_name,
            "title": title,
            "path": project_dir,
            "last_updated": os.path.getmtime(project_dir),
            "message_count": 0,
            "preview": "New project created"
        }

    def load_history(self, project_dir: str) -> List[Dict[str, Any]]:
        """Loads all conversation messages for a project."""
        history_file = os.path.join(project_dir, "conversation_history.json")
        if not os.path.exists(history_file):
            return []
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("messages", [])
        except Exception:
            return []

    def append_message(self, project_dir: str, sender: str, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Appends a new conversation step to the project's history file."""
        history_file = os.path.join(project_dir, "conversation_history.json")
        data = {"title": os.path.basename(project_dir), "messages": []}

        if os.path.exists(history_file):
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass

        new_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "sender": sender,
            "text": text,
            "metadata": metadata or {}
        }
        data.setdefault("messages", []).append(new_entry)

        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
