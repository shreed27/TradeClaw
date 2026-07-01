import unittest

from finclaw.core.bus import MessageBus


class _DummyAgent:
    def __init__(self, agent_id: str):
        self.id = agent_id
        self.inbox = []


class MessageBusTests(unittest.TestCase):
    def test_broadcast_sends_to_all_except_sender(self) -> None:
        bus = MessageBus()
        a1 = _DummyAgent("a1")
        a2 = _DummyAgent("a2")
        a3 = _DummyAgent("a3")
        bus.register(a1)
        bus.register(a2)
        bus.register(a3)

        bus.broadcast("a1", "ANALYSIS", {"text": "hello"})

        self.assertEqual(len(a1.inbox), 0)
        self.assertEqual(len(a2.inbox), 1)
        self.assertEqual(len(a3.inbox), 1)
        self.assertEqual(bus.history()[0]["type"], "ANALYSIS")

    def test_dm_sends_only_to_receiver(self) -> None:
        bus = MessageBus()
        a1 = _DummyAgent("a1")
        a2 = _DummyAgent("a2")
        a3 = _DummyAgent("a3")
        bus.register(a1)
        bus.register(a2)
        bus.register(a3)

        bus.dm("a1", "a2", "DIRECT", {"text": "private"})

        self.assertEqual(len(a1.inbox), 0)
        self.assertEqual(len(a2.inbox), 1)
        self.assertEqual(len(a3.inbox), 0)
        self.assertEqual(bus.history()[0]["to"], "a2")

    def test_clear_resets_history(self) -> None:
        bus = MessageBus()
        a1 = _DummyAgent("a1")
        a2 = _DummyAgent("a2")
        bus.register(a1)
        bus.register(a2)
        bus.broadcast("a1", "ANALYSIS", {"text": "x"})
        self.assertEqual(len(bus.history()), 1)

        bus.clear()
        self.assertEqual(bus.history(), [])


if __name__ == "__main__":
    unittest.main()
