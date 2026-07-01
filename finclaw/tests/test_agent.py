import json
import os
import tempfile
import unittest

from finclaw.core.agent import Agent


class _StubBus:
    def __init__(self) -> None:
        self.broadcast_calls = []
        self.dm_calls = []

    def broadcast(self, sender_id: str, msg_type: str, payload: dict) -> None:
        self.broadcast_calls.append((sender_id, msg_type, payload))

    def dm(self, sender_id: str, receiver_id: str, msg_type: str, payload: dict) -> None:
        self.dm_calls.append((sender_id, receiver_id, msg_type, payload))


class _StubLLM:
    def __call__(self, _prompt: str) -> str:
        return "mock-response"


class AgentTests(unittest.TestCase):
    def test_agent_loads_persona_and_saves_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            persona = os.path.join(tmp, "persona.md")
            with open(persona, "w", encoding="utf-8") as f:
                f.write("persona content")

            bus = _StubBus()
            agent = Agent("a1", "Agent 1", "Role", bus, _StubLLM(), persona, tmp, weight=1.2)
            self.assertEqual(agent.persona, "persona content")
            self.assertEqual(agent.to_prompt().split("\n")[0], "Agent 1 | Role: Role | Weight: 1.20")

            agent.memory.append({"msg": "x"})
            agent.save_memory()
            mem_file = os.path.join(tmp, "a1_memory.json")
            self.assertTrue(os.path.exists(mem_file))
            with open(mem_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["history"][0]["msg"], "x")

    def test_post_uses_bus_broadcast_and_dm(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            persona = os.path.join(tmp, "persona.md")
            with open(persona, "w", encoding="utf-8") as f:
                f.write("persona content")
            bus = _StubBus()
            agent = Agent("a1", "Agent 1", "Role", bus, _StubLLM(), persona, tmp)

            agent.post("ANALYSIS", {"text": "hello"})
            self.assertEqual(len(bus.broadcast_calls), 1)

            agent.post("ANALYSIS", {"text": "private"}, to="boss")
            self.assertEqual(len(bus.dm_calls), 1)

    def test_digest_returns_none_without_quant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            persona = os.path.join(tmp, "persona.md")
            with open(persona, "w", encoding="utf-8") as f:
                f.write("persona content")
            agent = Agent("a1", "Agent 1", "Role", _StubBus(), _StubLLM(), persona, tmp)
            self.assertIsNone(agent.digest({"spot": 1}))


if __name__ == "__main__":
    unittest.main()
