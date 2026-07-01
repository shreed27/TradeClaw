import unittest

from finclaw.strategy.option_strategy import OptionStrategyLibrary


class OptionStrategyLibraryTests(unittest.TestCase):
    def test_suggest_covers_all_regimes(self) -> None:
        cases = [
            ("bullish", "buy_call", "CALL"),
            ("bearish", "buy_put", "PUT"),
            ("range", "strangle", "STRANGLE"),
            ("volatile", "iron_condor", "IRON_CONDOR"),
            ("event", "buy_call_spread", "CALL"),
        ]
        for regime, strategy, side in cases:
            with self.subTest(regime=regime):
                result = OptionStrategyLibrary.suggest("any", {"regime": regime})
                self.assertEqual(result["strategy"], strategy)
                self.assertEqual(result["side"], side)

    def test_strike_selector_and_position_size_bounds(self) -> None:
        scenario = {"spot": 22500}
        call = OptionStrategyLibrary.strike_selector(scenario, "CALL")
        put = OptionStrategyLibrary.strike_selector(scenario, "PUT")
        atm = OptionStrategyLibrary.strike_selector(scenario, "STRANGLE")

        self.assertEqual(call["type"], "CE")
        self.assertEqual(put["type"], "PE")
        self.assertEqual(atm["type"], "ATM_STRADDLE")

        low = OptionStrategyLibrary.position_size(0.01)
        high = OptionStrategyLibrary.position_size(0.99)
        self.assertEqual(low["lots"], 1)
        self.assertLessEqual(high["lots"], 5)

    def test_suggest_final_builds_complete_trade(self) -> None:
        trade = OptionStrategyLibrary.suggest_final("boss", {"regime": "bullish", "spot": 22500})
        for key in ["strategy", "side", "strike", "lot_size", "target", "stop", "entry"]:
            self.assertIn(key, trade)


if __name__ == "__main__":
    unittest.main()
