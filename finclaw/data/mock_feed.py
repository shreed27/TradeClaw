import random
from typing import Dict


class MockMarketFeed:
    def __init__(self):
        self.templates = {
            "nifty_bullish": {
                "spot": 22500,
                "vix": 12.5,
                "regime": "bullish",
                "oi_distribution": "call_heavy",
                "max_pain": 22400,
                "pcr": 0.85,
                "days_to_expiry": 7,
            },
            "nifty_bearish": {
                "spot": 22000,
                "vix": 22.0,
                "regime": "bearish",
                "oi_distribution": "put_heavy",
                "max_pain": 22100,
                "pcr": 1.25,
                "days_to_expiry": 7,
            },
            "nifty_range": {
                "spot": 22200,
                "vix": 14.0,
                "regime": "range",
                "oi_distribution": "balanced",
                "max_pain": 22200,
                "pcr": 1.0,
                "days_to_expiry": 14,
            },
            "banknifty_volatile": {
                "spot": 48000,
                "vix": 28.0,
                "regime": "volatile",
                "oi_distribution": "skewed_put",
                "max_pain": 47800,
                "pcr": 1.15,
                "days_to_expiry": 7,
            },
            "event_budget": {
                "spot": 22450,
                "vix": 18.5,
                "regime": "event",
                "oi_distribution": "call_skewed",
                "max_pain": 22350,
                "pcr": 0.92,
                "days_to_expiry": 5,
            },
        }
        random.seed(42)

    def fetch_option_chain(self, symbol: str) -> dict:
        base = self.templates["nifty_bullish"]
        return {
            "symbol": symbol,
            "atm_strike": round(base["spot"] / 50) * 50,
            "ce_iv": 14.2,
            "pe_iv": 15.1,
            "oi_total": 45_000_000,
            "volume": 12_500_000,
            "pcr": base["pcr"],
            "max_pain": base["max_pain"],
        }

    def fetch_regime(self) -> dict:
        return {
            "vix_sentiment": "complacent",
            "fii_dii": "fii_buy",
            "policy_event": "none",
        }

    def fetch_scenario(self, template_name: str) -> dict:
        return dict(self.templates.get(template_name, self.templates["nifty_bullish"]))
