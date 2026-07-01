import os
import tempfile
import unittest

from finclaw.core.agent import Agent
from finclaw.core.bus import MessageBus
from finclaw.core.llm import MockLLM
from finclaw.core.session import SessionRunner
from finclaw.loop.learning import LearningLoop
from finclaw.strategy.option_strategy import OptionStrategyLibrary


class SessionRunnerIntegrationTests(unittest.TestCase):
    def _make_persona(self, folder: str, filename: str, text: str) -> str:
        path = os.path.join(folder, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_run_returns_trade_votes_and_updates_learning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bus = MessageBus()
            llm = MockLLM()
            learning = LearningLoop(tmp)
            strategy = OptionStrategyLibrary()

            boss_persona = self._make_persona(tmp, "boss.md", "Boss persona")
            sub_persona = self._make_persona(tmp, "a2.md", "Sub persona")

            boss = Agent("boss", "Harshad Mehta", "Boss", bus, llm, boss_persona, tmp)
            sub = Agent("a2", "Satoshi Nakamoto", "Quant", bus, llm, sub_persona, tmp)
            bus.register(boss)
            bus.register(sub)

            runner = SessionRunner(bus, [boss, sub], strategy, learning)
            result = runner.run("nifty_bullish", rounds=0)

            for key in ["scenario", "trade", "votes", "pnl", "outcome"]:
                self.assertIn(key, result)
            self.assertIn("Harshad Mehta", result["votes"])
            self.assertIn("Satoshi Nakamoto", result["votes"])
            self.assertEqual(learning.stats["boss"]["total"], 1)
            self.assertEqual(learning.stats["a2"]["total"], 1)


if __name__ == "__main__":
    unittest.main()
