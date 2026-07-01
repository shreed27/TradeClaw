import random
import time
from typing import List, Dict, Optional


class Helm:
    def __init__(self, bus, agents, scenario: dict, learning=None):
        self.bus = bus
        self.agents = agents
        self.scenario = scenario
        self.learning = learning
        self.transcript: List[str] = []
        self.boss = next((a for a in agents if "harshad" in a.id.lower()), agents[0])

    def _log(self, fmt, *args):
        line = (fmt % args) if args else fmt
        self.transcript.append(line)
        print(line)

    def _inject_scenario(self):
        text = (
            f"MARKET SCENARIO: Regime={self.scenario['regime']}, Spot={self.scenario['spot']}, "
            f"VIX={self.scenario['vix']}, PCR={self.scenario['pcr']}, MaxPain={self.scenario['max_pain']}. "
            f"Days to expiry: {self.scenario['days_to_expiry']}. Provide your view."
        )
        self.bus.broadcast("SYSTEM", "scenario_injection", {"text": text})

    def deliberate(self, n_rounds: int = 2):
        self._inject_scenario()
        for r in range(1, n_rounds + 1):
            self._log("\n%s", "=" * 60)
            self._log("  ROUND %d", r)
            self._log("%s", "=" * 60)

            if r == 1:
                for agent in self.agents:
                    if agent == self.boss:
                        continue
                    resp = agent.react(agent.inbox)
                    agent.post("analysis", {"text": f"{agent.name}: {resp['text']}"})
                    self._log("[%s] %s", agent.name, resp["text"])
                    agent.inbox = []
            else:
                for agent in self.agents:
                    if agent == self.boss:
                        continue
                    peers = [a for a in self.agents if a != agent and a != self.boss]
                    if not peers:
                        continue
                    peer = random.choice(peers)
                    msgs = [m for m in agent.inbox if m.get("from") == peer.id]
                    fallback = [{"text": f"No new messages from {peer.name}."}]
                    resp = agent.react(msgs if msgs else fallback)
                    agent.post(
                        "rebuttal",
                        {"text": f"{agent.name} -> {peer.name}: {resp['text']}"},
                        to=peer.id,
                    )
                    self._log("  [%s -> %s] %s", agent.name, peer.name, resp["text"])
                    agent.inbox = []

        self._log("\n%s", "=" * 60)
        self._log("  BOSS CONSOLIDATION")
        self._log("%s", "=" * 60)
        all_msgs = self.bus.history()
        resp = self.boss.react(all_msgs)
        self.boss.post("synthesis", {"text": f"BOSS: {resp['text']}"})
        self._log("[%s] %s", self.boss.name, resp["text"])

    def vote(self) -> dict:
        self._log("\n%s", "=" * 60)
        self._log("  VOTING")
        self._log("%s", "=" * 60)
        votes = {}
        for agent in self.agents:
            resp = agent.react(agent.inbox)
            vote = self._extract_vote(resp["text"])
            votes[agent.id] = vote
            self._log("  %s: %s", agent.name, vote)
            agent.inbox = []
        return votes

    def _extract_vote(self, text: str) -> str:
        t = text.upper()
        for v in ["BUY", "SELL", "HOLD", "AVOID"]:
            if v in t:
                return v
        return "HOLD"

    def finalize(self, votes: dict) -> dict:
        self._log("\n%s", "=" * 60)
        self._log("  FINALIZATION")
        self._log("%s", "=" * 60)
        summary = {
            "votes": votes,
            "consensus": max(set(votes.values()), key=list(votes.values()).count),
        }
        all_msgs = self.bus.history()
        resp = self.boss.react(all_msgs + [{"type": "vote_summary", "payload": summary}])
        self._log("FINAL DECISION: %s", resp["text"])

        trade_log = {
            "scenario": self.scenario.get("template", "custom"),
            "votes": votes,
            "final_text": resp["text"],
        }
        if self.learning:
            self.learning.log_trade(self.boss.id, trade_log, "executed", 0.0)
            self.learning.update_weights()
        return resp, trade_log

    def run_session(self, scenario: dict):
        self.deliberate(n_rounds=2)
        votes = self.vote()
        final, trade_log = self.finalize(votes)
        return final, votes, self.transcript, trade_log
