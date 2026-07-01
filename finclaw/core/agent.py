from __future__ import annotations
import os, json, time
from typing import List, Optional

class Agent:
    def __init__(self, id: str, name: str, role: str, bus, llm, persona_file: str, memory_folder: str, weight: float = 1.0):
        self.id = id
        self.name = name
        self.role = role
        self.bus = bus
        self.llm = llm
        self.persona_file = persona_file
        self.memory_folder = memory_folder
        self.weight = weight
        self.persona = ""
        self.memory: List[dict] = []
        self.inbox: List[dict] = []
        self.memory_file = os.path.join(memory_folder, f"{id}_memory.json")
        self._load_memory()
        self._load_persona()

    def _load_persona(self):
        with open(self.persona_file, "r", encoding="utf-8") as f:
            self.persona = f.read().strip()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    self.memory = json.load(f).get("history", [])
            except Exception:
                self.memory = []

    def save_memory(self):
        os.makedirs(self.memory_folder, exist_ok=True)
        data = {"weight": self.weight, "history": self.memory, "last_seen": time.time()}
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def post(self, msg_type: str, payload: dict, to: Optional[str] = None):
        if to:
            self.bus.dm(self.id, to, msg_type, {"from": self.name, "text": payload["text"]})
        else:
            self.bus.broadcast(self.id, msg_type, {"from": self.name, "text": payload["text"]})
        self.save_memory()

    def to_prompt(self) -> str:
        return f"{self.name} | Role: {self.role} | Weight: {self.weight:.2f}\n{self.persona}"

    def react(self, messages: List[dict]) -> dict:
        prompt = self.to_prompt() + "\n"
        if messages:
            prompt += "Context:\n"
            for m in messages[-4:]:
                sender = m.get("from", "unknown")
                text = ""
                if isinstance(m.get("payload"), dict):
                    text = m["payload"].get("text", "")
                prompt += f"- {sender}: {text}\n"
        prompt += "Respond as yourself in 1-3 sentences max."
        response_text = self.llm(prompt)
        return {"agent_id": self.id, "name": self.name, "text": response_text, "timestamp": time.time()}
