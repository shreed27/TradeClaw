from typing import Dict, Any


class OptionStrategyLibrary:
    @staticmethod
    def suggest(agent_style: str, scenario: dict) -> dict:
        regime = scenario.get("regime", "range")
        if regime == "bullish":
            side = "CALL"
            strategy = "buy_call"
            rationale = "Spot above max pain, PCR < 1, bullish momentum."
        elif regime == "bearish":
            side = "PUT"
            strategy = "buy_put"
            rationale = "VIX rising, PCR > 1, put-heavy OI distribution."
        elif regime == "range":
            side = "STRANGLE"
            strategy = "strangle"
            rationale = "VIX range-bound, balanced OI, sell premium for theta."
        elif regime == "volatile":
            side = "IRON_CONDOR"
            strategy = "iron_condor"
            rationale = "VIX spike > 25, wide expected move, defined-risk premium."
        else:
            side = "CALL"
            strategy = "buy_call_spread"
            rationale = "Event-driven, defined risk via spread."

        return {"strategy": strategy, "side": side, "rationale": rationale}

    @staticmethod
    def suggest_final(agent_style: str, scenario: dict) -> dict:
        suggestion = OptionStrategyLibrary.suggest(agent_style, scenario)
        strike_info = OptionStrategyLibrary.strike_selector(scenario, suggestion["side"])
        size = OptionStrategyLibrary.position_size(0.8)
        trade = dict(suggestion)
        trade.update(strike_info)
        trade.update(size)
        trade["target"] = round(scenario.get("spot", 22000) * 1.02, 2)
        trade["stop"] = round(scenario.get("spot", 22000) * 0.98, 2)
        trade["entry"] = round(scenario.get("spot", 22000), 2)
        return trade

    @staticmethod
    def strike_selector(scenario: dict, side: str) -> dict:
        spot = scenario.get("spot", 22000)
        if side == "CALL":
            otm = round((spot + spot * 0.01) / 50) * 50
            return {"strike": otm, "type": "CE", "distance_otm": otm - spot}
        elif side == "PUT":
            otm = round((spot - spot * 0.01) / 50) * 50
            return {"strike": otm, "type": "PE", "distance_otm": spot - otm}
        else:
            atm = round(spot / 50) * 50
            return {"strike": atm, "type": "ATM_STRADDLE", "distance_otm": 0}

    @staticmethod
    def position_size(confidence: float, capital: int = 100000) -> dict:
        lots = max(1, min(5, int(confidence * 5)))
        lot_size = 50
        margin_est = lots * lot_size * 180
        return {
            "lot_size": lot_size,
            "lots": lots,
            "margin_est": margin_est,
            "max_risk_pct": 0.02,
        }
