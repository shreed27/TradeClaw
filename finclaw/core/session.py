from __future__ import annotations
import time
import random as _r_mod
from typing import Any, List

from .bus import MessageBus
from .agent import Agent
from ..data.mock_feed import MockMarketFeed
from ..data.scenarios import SCENARIOS
from ..strategy.option_strategy import OptionStrategyLibrary
from ..loop.learning import LearningLoop


class SessionRunner:
    def __init__(self, bus: MessageBus, agents: List[Agent], strategy_lib: OptionStrategyLibrary,
                 learning_loop: "LearningLoop"):
        self.bus = bus
        self.agents = agents
        self.strategy_lib = strategy_lib
        self.learning_loop = learning_loop

    def run(self, scenario_name: str = "nifty_bullish", rounds: int = 1) -> dict[str, Any]:
        feed = MockMarketFeed()
        scenario = feed.fetch_scenario(scenario_name)

        print(f"\n{'='*72}")
        print(f"  FinClaw // A2A SESSION | {scenario_name.upper()}")
        print(f"  Spot: {scenario['spot']}  |  VIX: {scenario['vix']}  |  DTE: {scenario['days_to_expiry']}")
        print(f"  PCR: {scenario.get('pcr','-')}  |  Max Pain: {scenario.get('max_pain','-')}")
        print(f"{'='*72}")

        rounds_total = int(rounds) + 1
        for round_num in range(rounds_total):
            print(f"\n--- Round {round_num + 1} ---")
            for agent in self.agents:
                msgs = self.bus.history()
                reply = agent.react(msgs)
                text = reply["text"]
                print(f"[{agent.name}]  {text}")
                if agent.id == "boss":
                    continue
                agent.post("ANALYSIS", {"text": text, "from": agent.name, "round": round_num}, to="boss")
            time.sleep(0.01)

        # Votes
        votes: dict[str, str] = {}
        for agent in self.agents:
            msgs = self.bus.history()
            prompt = (
                agent.to_prompt()
                + "\nRecent: "
                + str([m["payload"] for m in msgs[-6:]])[:700]
                + "\nVote exactly one: BUY, SELL, HOLD, or AVOID. One word only."
            )
            vote_text = agent.llm(prompt).strip().upper().split()[0]
            if vote_text not in {"BUY", "SELL", "HOLD", "AVOID"}:
                vote_text = _r_mod.choice(["BUY", "SELL", "HOLD", "AVOID"])
            votes[agent.name] = vote_text

        print("\n--- Votes ---")
        for nm, v in votes.items():
            print(f"  {nm:<28} {v}")

        trade = self.strategy_lib.suggest_final("boss", scenario)

        print("\n--- Final Trade ---")
        for k in ["side", "strategy", "strike", "lot_size", "target", "stop", "rationale"]:
            print(f"  {k+' '*(12-len(k))}: {trade.get(k)}")
        print(f"{'='*72}")

        for agent in self.agents:
            agent.save_memory()

        pnl = _r_mod.uniform(-5000, 18000)
        outcome = "WIN" if pnl > 0 else "LOSS"
        for agent in self.agents:
            self.learning_loop.log_trade(agent.id, trade, outcome, round(pnl, 2))
        self.learning_loop.update_weights()

        print("\n--- Learning Loop Status ---")
        leaderboard = self.learning_loop.get_leaderboard()[:5]
        if not leaderboard:
            print("  no data yet")
        else:
            for aid, _weight in leaderboard:
                s = self.learning_loop.stats.get(aid, {"wins": 0, "total": 0})
                w = self.learning_loop.get_weight(aid)
                wr = s["wins"] / s["total"] if s["total"] else 0.0
                print(
                    f"  {aid:<16} weight={w:.2f}  win_rate={float(wr):.0%}  trades={s['total']}"
                )
        return {
            "scenario": scenario_name,
            "trade": trade,
            "votes": votes,
            "pnl": round(pnl, 2),
            "outcome": outcome,
        }
