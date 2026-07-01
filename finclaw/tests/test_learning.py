import json
import os
import tempfile
import unittest

from finclaw.loop.learning import LearningLoop


class LearningLoopTests(unittest.TestCase):
    def test_log_trade_and_update_weights(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            loop = LearningLoop(tmp)
            loop.log_trade("a1", {"strategy": "buy_call"}, "WIN", 1000.0)
            loop.log_trade("a1", {"strategy": "buy_put"}, "LOSS", -100.0)
            loop.update_weights()

            self.assertEqual(loop.stats["a1"]["total"], 2)
            self.assertEqual(loop.stats["a1"]["wins"], 1)
            self.assertEqual(loop.stats["a1"]["losses"], 1)
            self.assertGreaterEqual(loop.get_weight("a1"), 0.2)
            self.assertLessEqual(loop.get_weight("a1"), 2.0)
            self.assertTrue(loop.get_leaderboard())

            self.assertTrue(os.path.exists(os.path.join(tmp, "learning.json")))
            self.assertTrue(os.path.exists(os.path.join(tmp, "stats.json")))

    def test_load_reads_persisted_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "learning.json"), "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "trades": [{"agent_id": "a2", "trade": "strangle", "outcome": "WIN", "pnl": 10}],
                        "weights": {"a2": 1.3},
                        "stats": {"a2": {"wins": 1, "losses": 0, "total": 1}},
                    },
                    f,
                )
            with open(os.path.join(tmp, "stats.json"), "w", encoding="utf-8") as f:
                json.dump({"a2": {"wins": 1, "losses": 0, "total": 1}}, f)

            loop = LearningLoop(tmp)
            self.assertEqual(loop.get_weight("a2"), 1.3)
            self.assertEqual(loop.stats["a2"]["total"], 1)


if __name__ == "__main__":
    unittest.main()
