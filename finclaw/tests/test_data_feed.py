import unittest

from finclaw.data.mock_feed import MockMarketFeed
from finclaw.data.scenarios import SCENARIOS


class DataFeedTests(unittest.TestCase):
    def test_fetch_scenario_returns_known_template(self) -> None:
        feed = MockMarketFeed()
        scenario = feed.fetch_scenario("nifty_bearish")
        self.assertEqual(scenario["regime"], "bearish")
        self.assertIn("spot", scenario)

    def test_fetch_scenario_falls_back_to_bullish(self) -> None:
        feed = MockMarketFeed()
        scenario = feed.fetch_scenario("unknown_template")
        self.assertEqual(scenario["regime"], "bullish")

    def test_scenarios_module_contains_core_templates(self) -> None:
        for name in ["nifty_bullish", "nifty_bearish", "nifty_range", "banknifty_volatile", "event_budget"]:
            with self.subTest(name=name):
                self.assertIn(name, SCENARIOS)
                self.assertIn("spot", SCENARIOS[name])
                self.assertIn("regime", SCENARIOS[name])


if __name__ == "__main__":
    unittest.main()
