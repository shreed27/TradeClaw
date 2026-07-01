from __future__ import annotations
import math
import random
from typing import Callable, Dict, List


def _extract_name(prompt: str) -> str:
    first = prompt.split("\n")[0].strip()
    for sep in ["You are ", "Respond as "]:
        if sep in first:
            first = first.split(sep, 1)[1]
            break
    name = first.split("|")[0].strip()
    return name


class MockLLM:
    def __init__(self) -> None:
        self.pools: Dict[str, List[str]] = {
            "Satoshi Nakamoto": [
                "The on-chain data is screaming. Delta is collapsing ATM while IV is still bid. I'm leaning short gamma here.",
                "Volume profile shows nodes at support/resistance. The chain distribution is asymmetric.",
                "Order flow suggests smart money selling the rip. Regime shifted risk-off.",
            ],
            "Rakesh Jhunjhunwala": [
                "The market gives you lemons? I buy calls when others buy puts. Temptation window.",
                "India's story hasn't ended. Deep OTM puts in panic = my bread and butter. Recovery to 24,800.",
                "When the street panics about expiry, I step in. Contrarian bias active.",
            ],
            "Warren Buffett": [
                "Moats don't vanish in one session. I wait for margin of safety.",
                "Speculative option plays are not my style. Better to sit on cash and watch.",
                "Price is what you pay. At this expiry, risk/reward is not compelling.",
            ],
            "Vijay Kedia": [
                "Hidden gems in index components show strong deliveries. Possibility of gap-up tomorrow.",
                "Microstructure shows institutions building positions in select names.",
                "Conviction play: lot-traded counters suggest a 24,200+ week close possible.",
            ],
            "Jim Simons": [
                "Signal-to-noise below threshold. Model says fade-gamma setup; size accordingly.",
                "Z-score deviation at 2.3 sigma; statistically significant reversion leg expected.",
                "Rising entropy in the chain; suppress size, hedge with wings.",
            ],
            "George Soros": [
                "Reflexivity loop building. As shorts cover, spot rallies and FOMO ignites boom leg.",
                "FII flows negative for 3 days. Reflexivity says larger reversal setup; huge notional.",
                "Markets are biased downside. Once false bias peaks, reflex will be violent upside.",
            ],
            "Paul Tudor Jones": [
                "Don't fight the Fed, don't fight the expiry trend. Technicals: positive momentum.",
                "Risk overlay: VIX above 14 means trim exposure. Trend rules say hold until price turns.",
                "Military risk discipline: 1% max loss per trade. If trend confirms, scale in.",
            ],
            "Jesse Livermore": [
                "The tape says the crowd is wrong. Panic climax near — I short the blowoff after final wick.",
                "Oldest rule: never argue with the tape. Distribution near 24,500; wait for top.",
                "Markets repeat nature. Euphoria peaking. This is where most blow their accounts.",
            ],
            "Harshad Mehta": [
                "Synthesizing all voices: risk/reward shifts bullish near expiry. Final word: BUY 24,200 CE with defined risk.",
                "The street thinks range-bound. I see breakout. Decision: CALL side with wings protection.",
                "Opportunity is where others see risk. DECISION: directional long bias into expiry.",
            ],
        }
        self.fallback = [
            "I'm monitoring the situation. Awaiting clearer setup before committing.",
            "Neutral stance. Data is mixed; no sharp edge detected right now.",
        ]

    def register(self, name: str, lines: List[str]) -> None:
        self.pools[name] = lines

    def __call__(self, prompt: str) -> str:
        name = _extract_name(prompt).strip()
        pool = self.pools.get(name, self.fallback)
        idx = sum(ord(c) for c in prompt) % len(pool)
        return pool[idx]
