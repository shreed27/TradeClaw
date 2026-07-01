import json
import os
import time
from collections import defaultdict
from typing import Any, Dict, List, Tuple


class LearningLoop:
    def __init__(self, memory_folder: str = "finclaw/memory"):
        self.memory_folder = memory_folder
        self.log_file = os.path.join(memory_folder, "learning.json")
        self.stats_file = os.path.join(memory_folder, "stats.json")
        os.makedirs(memory_folder, exist_ok=True)
        self.trades: List[dict] = []
        self.weights: Dict[str, float] = {}
        self.stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"wins": 0, "losses": 0, "total": 0})
        self._load()

    def _load(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.trades = data.get("trades", [])
                    self.weights = data.get("weights", {})
                    raw_stats = data.get("stats", {})
                    self.stats = defaultdict(lambda: {"wins": 0, "losses": 0, "total": 0})
                    for k, v in raw_stats.items():
                        self.stats[k] = v
            except Exception:
                pass
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    stats = json.load(f)
                    for aid, s in stats.items():
                        self.stats[aid] = s
            except Exception:
                pass

    def log_trade(self, agent_id: str, trade: dict, outcome: str, pnl: float):
        record = {
            "agent_id": agent_id,
            "trade": trade.get("strategy"),
            "outcome": outcome,
            "pnl": pnl,
            "ts": time.time(),
        }
        self.trades.append(record)
        self.stats[agent_id]["total"] += 1
        if pnl > 0:
            self.stats[agent_id]["wins"] += 1
        else:
            self.stats[agent_id]["losses"] += 1
        self._persist()

    def update_weights(self):
        for aid, s in self.stats.items():
            wr = s["wins"] / s["total"] if s["total"] else 0.5
            base = 0.2 + 0.8 * wr
            self.weights[aid] = float(max(0.2, min(2.0, base)))
        self._persist()

    def get_weight(self, agent_id: str) -> float:
        return float(self.weights.get(agent_id, 1.0))

    def get_leaderboard(self) -> List[Tuple[str, float]]:
        return sorted(self.weights.items(), key=lambda x: x[1], reverse=True)

    def _persist(self):
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "trades": self.trades,
                    "weights": self.weights,
                    "stats": {k: dict(v) for k, v in self.stats.items()},
                },
                f,
                indent=2,
            )
        with open(self.stats_file, "w", encoding="utf-8") as f:
            json.dump({k: dict(v) for k, v in self.stats.items()}, f, indent=2)
