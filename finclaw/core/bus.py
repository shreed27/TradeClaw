from __future__ import annotations
import time, threading
from typing import Any

class MessageBus:
    def __init__(self):
        self.agents: dict[str, Any] = {}
        self._history: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def register(self, agent: Any) -> None:
        self.agents[agent.id] = agent

    def broadcast(self, sender_id: str, msg_type: str, payload: dict):
        msg = {"from": sender_id, "to": "ALL", "type": msg_type, "payload": payload, "ts": time.time()}
        with self._lock:
            self._history.append(msg)
        for aid, agent in self.agents.items():
            if aid != sender_id:
                agent.inbox.append(msg)

    def dm(self, sender_id: str, receiver_id: str, msg_type: str, payload: dict):
        msg = {"from": sender_id, "to": receiver_id, "type": msg_type, "payload": payload, "ts": time.time()}
        with self._lock:
            self._history.append(msg)
        if receiver_id in self.agents:
            self.agents[receiver_id].inbox.append(msg)

    def history(self) -> list[dict[str, Any]]:
        return list(self._history)

    def clear(self) -> None:
        with self._lock:
            self._history.clear()
