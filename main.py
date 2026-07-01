import os
import sys
import shutil

# Ensure finclaw package is importable
repo_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, repo_root)

# Remove any out-of-band sibling file that may clash
shutil.rmtree(os.path.join(repo_root, "finclaw", "main.py"), ignore_errors=True)

# Local imports only
from finclaw.core.bus import MessageBus
from finclaw.core.agent import Agent
from finclaw.core.llm import MockLLM
from finclaw.data.mock_feed import MockMarketFeed
from finclaw.data.scenarios import SCENARIOS
from finclaw.strategy.option_strategy import OptionStrategyLibrary
from finclaw.loop.learning import LearningLoop
from finclaw.core.session import SessionRunner
from finclaw.agents.personas.build import write_personas

PERSONA_DIR = os.path.join(repo_root, "finclaw", "agents", "personas")
MEMORY_DIR = os.path.join(repo_root, "finclaw", "memory")


def main():
    write_personas()
    llm = MockLLM()
    bus = MessageBus()
    feed = MockMarketFeed()
    strategy_lib = OptionStrategyLibrary()
    learning_loop = LearningLoop(MEMORY_DIR)

    agents_cfg = [
        ("boss",   "Harshad Mehta",       "Boss",        "harshad_mehta.md"),
        ("a02",    "Satoshi Nakamoto",     "Quant",       "satoshi.md"),
        ("a03",    "Rakesh Jhunjhunwala",  "Contrarian",  "rakesh_jhunjhunwala.md"),
        ("a04",    "Warren Buffett",       "Quality",     "warren_buffett.md"),
        ("a05",    "Vijay Kedia",          "Conviction",  "vijay_kedia.md"),
        ("a06",    "Jim Simons",           "Quant",       "jim_simons.md"),
        ("a07",    "George Soros",         "Macro",       "george_soros.md"),
        ("a08",    "Paul Tudor Jones",     "Trend",       "paul_tudor_jones.md"),
        ("a09",    "Jesse Livermore",      "Tape-Reader", "jesse_livermore.md"),
    ]
    agents = []
    for aid, name, role, fname in agents_cfg:
        pfile = os.path.join(PERSONA_DIR, fname)
        agent = Agent(aid, name, role, bus, llm, pfile, MEMORY_DIR, weight=1.0)
        bus.register(agent)
        agents.append(agent)

    runner = SessionRunner(bus, agents, strategy_lib, learning_loop)
    result = runner.run("nifty_bullish", rounds=1)
    bus.clear()
    return result


if __name__ == "__main__":
    main()
