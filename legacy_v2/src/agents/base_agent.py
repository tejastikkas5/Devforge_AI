from typing import List, Dict, Generator
from src.llm.ollama_client import OllamaClient
from src.core.event_bus import bus

class BaseAgent:
    def __init__(self, name: str, role: str, model: str, client: OllamaClient):
        self.name = name
        self.role = role
        self.model = model
        self.client = client

    def notify_status(self, status: str):
        """Sends an event to update GUI agent state."""
        bus.post("agent_status", {
            "name": self.name,
            "role": self.role,
            "status": status
        })

    def notify_token(self, token: str):
        """Streams a generated token to the UI."""
        bus.post("token_stream", {
            "agent": self.name,
            "token": token
        })

    def run_stream(self, system_prompt: str, user_prompt: str) -> str:
        """Runs the agent with token streaming to both GUI and returning complete output."""
        self.notify_status("active")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        full_text = []
        for token in self.client.stream_chat(self.model, messages):
            self.notify_token(token)
            full_text.append(token)
            
        self.notify_status("idle")
        return "".join(full_text)
