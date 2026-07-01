import unittest

from finclaw.core.orchestrator import Helm


class _StubBus:
    def __init__(self) -> None:
        self._history = []

    def broadcast(self, sender_id: str, msg_type: str, payload: dict) -> None:
        self._history.append({"from": sender_id, "type": msg_type, "payload": payload})

    def history(self):
        return list(self._history)


class _StubLearning:
    def __init__(self) -> None:
        self.logged = []
        self.updated = False

    def log_trade(self, agent_id: str, trade: dict, outcome: str, pnl: float) -> None:
        self.logged.append((agent_id, trade, outcome, pnl))

    def update_weights(self) -> None:
        self.updated = True


class _StubAgent:
    def __init__(self, aid: str, name: str, reply: str) -> None:
        self.id = aid
        self.name = name
        self.reply = reply
        self.inbox = []

    def react(self, _messages):
        return {"text": self.reply}

    def post(self, msg_type: str, payload: dict, to: str = None) -> None:
        _ = (msg_type, payload, to)


class HelmTests(unittest.TestCase):
    def test_extract_vote_defaults_to_hold(self) -> None:
        helm = Helm(_StubBus(), [_StubAgent("harshad", "Boss", "BUY")], {"regime": "bullish", "spot": 1, "vix": 1, "pcr": 1, "max_pain": 1, "days_to_expiry": 1})
        self.assertEqual(helm._extract_vote("Strong BUY now"), "BUY")
        self.assertEqual(helm._extract_vote("unclear"), "HOLD")

    def test_finalize_logs_learning(self) -> None:
        learning = _StubLearning()
        bus = _StubBus()
        boss = _StubAgent("harshad", "Harshad", "Final decision text")
        peer = _StubAgent("a2", "A2", "BUY")
        helm = Helm(
            bus,
            [boss, peer],
            {"template": "nifty_bullish", "regime": "bullish", "spot": 1, "vix": 1, "pcr": 1, "max_pain": 1, "days_to_expiry": 1},
            learning=learning,
        )
        response, trade_log = helm.finalize({"harshad": "BUY", "a2": "SELL"})

        self.assertEqual(response["text"], "Final decision text")
        self.assertEqual(trade_log["scenario"], "nifty_bullish")
        self.assertEqual(len(learning.logged), 1)
        self.assertTrue(learning.updated)


if __name__ == "__main__":
    unittest.main()
