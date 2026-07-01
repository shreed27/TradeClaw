import os
import sys
import shutil

repo_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, repo_root)
shutil.rmtree(os.path.join(repo_root, "finclaw", "main.py"), ignore_errors=True)

from finclaw.core.bus import MessageBus
from finclaw.core.agent import Agent
from finclaw.core.llm import MockLLM
from finclaw.data.mock_feed import MockMarketFeed
from finclaw.data.scenarios import SCENARIOS
from finclaw.strategy.option_strategy import OptionStrategyLibrary
from finclaw.loop.learning import LearningLoop
from finclaw.core.session import SessionRunner
from finclaw.core.quant import QuantBrain
from finclaw.agents.personas.build import write_personas

PERSONA_DIR = os.path.join(repo_root, "finclaw", "agents", "personas")
MEMORY_DIR = os.path.join(repo_root, "finclaw", "memory")

SCENARIOS_ORDER = [
    "nifty_bullish",
    "nifty_bearish",
    "nifty_range",
    "banknifty_volatile",
    "event_budget",
]


def main() -> None:
    write_personas()
    llm = MockLLM()
    bus = MessageBus()
    feed = MockMarketFeed()
    strategy_lib = OptionStrategyLibrary()
    learning_loop = LearningLoop(MEMORY_DIR)
    quant_brain = QuantBrain(os.path.join(MEMORY_DIR, "model_registry.json"))

    agents_cfg = [
        ("boss", "Harshad Mehta", "Boss", "harshad_mehta.md"),
        ("a02", "Satoshi Nakamoto", "Quant", "satoshi.md"),
        ("a03", "Rakesh Jhunjhunwala", "Contrarian", "rakesh_jhunjhunwala.md"),
        ("a04", "Warren Buffett", "Quality", "warren_buffett.md"),
        ("a05", "Vijay Kedia", "Conviction", "vijay_kedia.md"),
        ("a06", "Jim Simons", "Quant", "jim_simons.md"),
        ("a07", "George Soros", "Macro", "george_soros.md"),
        ("a08", "Paul Tudor Jones", "Trend", "paul_tudor_jones.md"),
        ("a09", "Jesse Livermore", "Tape-Reader", "jesse_livermore.md"),
    ]
    agents = []
    for aid, name, role, fname in agents_cfg:
        pfile = os.path.join(PERSONA_DIR, fname)
        agent = Agent(aid, name, role, bus, llm, pfile, MEMORY_DIR, weight=1.0)
        if aid == "a06":
            agent.quant = quant_brain
        bus.register(agent)
        agents.append(agent)

    runner = SessionRunner(bus, agents, strategy_lib, learning_loop)

    print("\n" + "=" * 72)
    print("  FinClaw // A2A 24/7 LOOP // MASTER BRAIN: Harshad Mehta")
    print("=" * 72)

    for scenario_name in SCENARIOS_ORDER:
        scenario = feed.fetch_scenario(scenario_name)
        print(f"\n>>> SCENARIO: {scenario_name.upper()}")
        print(f">>> market_context: spot={scenario['spot']} vix={scenario['vix']} dte={scenario['days_to_expiry']}")

        jim = next(a for a in agents if a.id == "a06")
        quant_out = jim.digest(scenario)
        if quant_out:
            print(f"\n[Jim Simons QUANT] side={quant_out['side']} strike={quant_out['strike']} lots={quant_out['lots']} "
                  f"delta={quant_out['delta']} z={quant_out['z']} confidence={quant_out['confidence']} "
                  f"expected_return={quant_out['expected_return_per_trade']:.0%} orderbook_imbalance={quant_out['orderbook_imbalance']}")
            print(f"[Jim Simons QUANT] score={quant_out['score']} annualized_target_inr={quant_out['annualized_target_inr']:,}")
            bus.broadcast(
                "a06",
                "quant_signal",
                {"from": "Jim Simons", "text": f"Quant signal: {quant_out['side']} {quant_out['strike']} lots={quant_out['lots']} score={quant_out['score']}"},
            )

        result = runner.run(scenario_name, rounds=1)
        bus.clear()

    print("\n" + "=" * 72)
    print("  FinClaw // 24/7 LOOP COMPLETE")
    print("=" * 72)
    for agent in agents:
        print(f"  {agent.name:<28} weight={learning_loop.get_weight(agent.id):.2f}  ")

    print("\nNote: 1Cr INR/year target tracked in quant brain model registry file under finclaw/memory/model_registry.json")


if __name__ == "__main__":
    main()
