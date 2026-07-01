import unittest

from finclaw.core.quant import QuantBrain, _bs_delta, _norm_cdf


class QuantTests(unittest.TestCase):
    def test_math_helpers(self) -> None:
        self.assertAlmostEqual(_norm_cdf(0), 0.5, places=6)
        self.assertGreater(_bs_delta("CE", 22500, 22500, 7 / 365, 0.2), 0)
        self.assertLess(_bs_delta("PE", 22500, 22500, 7 / 365, 0.2), 0)

    def test_backtest_output_has_expected_shape(self) -> None:
        qb = QuantBrain("finclaw/memory/model_registry.json")
        out = qb.backtest_scenario(
            {
                "spot": 22500,
                "atm": 22500,
                "days_to_expiry": 7,
                "iv": 0.2,
                "regime": "bullish",
                "pcr": 0.9,
                "oi_distribution": "call-heavy",
            }
        )
        for key in [
            "side",
            "strike",
            "lots",
            "delta",
            "confidence",
            "score",
            "annualized_target_inr",
            "orderbook_imbalance",
        ]:
            self.assertIn(key, out)
        self.assertIn(out["side"], {"CE", "PE"})
        self.assertGreaterEqual(out["confidence"], 0.0)
        self.assertLessEqual(out["confidence"], 1.0)

    def test_pcr_override_can_force_put_side(self) -> None:
        qb = QuantBrain("finclaw/memory/model_registry.json")
        out = qb.backtest_scenario(
            {
                "spot": 22000,
                "atm": 22000,
                "days_to_expiry": 7,
                "iv": 0.2,
                "regime": "bullish",
                "pcr": 1.3,
                "oi_distribution": "balanced",
            }
        )
        self.assertEqual(out["side"], "PE")

    def test_evolve_params_stays_within_expected_ranges(self) -> None:
        qb = QuantBrain("finclaw/memory/model_registry.json")
        params = qb.evolve_params()
        self.assertGreaterEqual(params["z_entry"], 0.5)
        self.assertLessEqual(params["z_entry"], 3.5)
        self.assertGreaterEqual(params["z_exit"], 0.1)
        self.assertLessEqual(params["z_exit"], 1.5)
        self.assertGreaterEqual(params["confidence_threshold"], 0.45)
        self.assertLessEqual(params["confidence_threshold"], 0.95)
        self.assertGreaterEqual(params["target_return"], 0.08)
        self.assertLessEqual(params["target_return"], 0.25)
        self.assertGreaterEqual(params["stop_loss"], -0.20)
        self.assertLessEqual(params["stop_loss"], -0.03)


if __name__ == "__main__":
    unittest.main()
