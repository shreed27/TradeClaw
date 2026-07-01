from __future__ import annotations
import math
import random
from typing import Any, Dict, Optional


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _bs_delta(option_type: str, S: float, K: float, T: float, sigma: float, r: float = 0.05) -> float:
    if T <= 0 or sigma <= 0:
        return 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    if option_type == "CE":
        return _norm_cdf(d1)
    return _norm_cdf(d1) - 1.0


class QuantBrain:
    def __init__(self, registry_path: str = "finclaw/memory/model_registry.json"):
        self.registry_path = registry_path
        self.models: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self.models = __import__("json").load(f)
        except Exception:
            self.models = {}

    def _persist(self) -> None:
        with open(self.registry_path, "w", encoding="utf-8") as f:
            __import__("json").dump(self.models, f, indent=2)

    def backtest_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        S = float(scenario.get("spot", 22500))
        K = float(scenario.get("atm") or S + 100)
        T = float(scenario.get("days_to_expiry", 5)) / 365.0
        sigma = float(scenario.get("iv", 0.18) or 0.18)
        regime = scenario.get("regime", "range")
        pcr = float(scenario.get("pcr", 1.0) or 1.0)
        oi = (scenario.get("oi_distribution", "") or "").lower()

        if regime == "bullish":
            side = "CE"
        elif regime == "bearish":
            side = "PE"
        else:
            side = "CE"

        delta = _bs_delta(side, S, K, T, sigma)
        z = delta * 2.3
        confidence = max(0.0, min(1.0, _norm_cdf(z)))
        target_return = 0.15
        expected_pnl_per_lot = target_return * 50 * 180
        lots = max(1, min(5, int(confidence * 5 + 0.5)))
        if "bearish" in oi or "put-heavy" in oi or pcr > 1.2:
            side = "PE"
            delta = _bs_delta(side, S, K, T, sigma)
        elif "call-heavy" in oi or pcr < 0.8:
            side = "CE"
            delta = _bs_delta(side, S, K, T, sigma)

        ob = self._orderbook(K, side)
        orderbook_imbalance = ob.get("imbalance", 0.0)
        score = round((confidence * target_return) / max(0.05, abs(expected_pnl_per_lot / 10000.0)), 4)
        return {
            "regime": regime,
            "side": side,
            "strike": K,
            "lots": lots,
            "delta": round(delta, 3),
            "z": round(z, 2),
            "confidence": round(confidence, 2),
            "expected_return_per_trade": target_return,
            "estimated_pnl_per_lot": round(expected_pnl_per_lot, 2),
            "orderbook_imbalance": orderbook_imbalance,
            "score": score,
            "annualized_target_inr": 10_000_000,
        }

    def _orderbook(self, strike: float, option_type: str) -> Dict[str, Any]:
        base_bid = 185.0
        base_ask = 185.5
        bids = []
        asks = []
        for i in range(8):
            bb = round(base_bid - i * 0.05 + random.uniform(-0.12, 0.12), 2)
            ba = round(base_ask + i * 0.05 + random.uniform(-0.12, 0.12), 2)
            bids.append({"price": bb, "qty": int(random.uniform(20, 80) * 50), "orders": int(random.uniform(5, 40))})
            asks.append({"price": ba, "qty": int(random.uniform(20, 80) * 50), "orders": int(random.uniform(5, 40))})
        bid_qty = sum(b["qty"] for b in bids)
        ask_qty = sum(a["qty"] for a in asks)
        imbalance = (bid_qty - ask_qty) / max(1, bid_qty + ask_qty)
        return {
            "strike": strike,
            "type": option_type,
            "mid": round((base_bid + base_ask) / 2, 2),
            "spread": round(base_ask - base_bid, 2),
            "imbalance": round(imbalance, 3),
            "bids": bids,
            "asks": asks,
        }

    def evolve_params(self) -> Dict[str, float]:
        base = {
            "z_entry": 1.5,
            "z_exit": 0.5,
            "confidence_threshold": 0.65,
            "target_return": 0.15,
            "stop_loss": -0.08,
        }
        mutated = {}
        for k, v in base.items():
            lo, hi = {
                "z_entry": (0.5, 3.5),
                "z_exit": (0.1, 1.5),
                "confidence_threshold": (0.45, 0.95),
                "target_return": (0.08, 0.25),
                "stop_loss": (-0.20, -0.03),
            }[k]
            mutation = random.uniform(-0.2, 0.2) * (hi - lo)
            mutated[k] = round(max(lo, min(hi, v + mutation)), 4)
        return mutated
