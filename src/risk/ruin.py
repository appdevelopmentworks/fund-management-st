"""Approximate risk of ruin calculations (Balsara-like)."""

from __future__ import annotations

from typing import Iterable, List, Tuple


def risk_of_ruin(p: float, payoff_ratio: float, f: float, ruin_threshold: float = 0.1) -> float:
    """
    Approximate risk of ruin.

    p: win probability (0-1)
    payoff_ratio: average profit / average loss (>0)
    f: risk per trade (as decimal of equity)
    ruin_threshold: equity level considered ruin (fraction of start)
    """
    p = max(min(p, 1.0), 0.0)
    payoff_ratio = max(payoff_ratio, 0.0)
    if f <= 0 or payoff_ratio == 0:
        return 1.0
    edge = p * payoff_ratio - (1 - p)
    if edge <= 0:
        return 1.0
    k = ruin_threshold / f
    base = (1 - edge) / (1 + edge)
    base = max(min(base, 1.0), 0.0)
    return base ** k


def ruin_table(p: float, payoff_ratio: float, f_values: Iterable[float], ruin_threshold: float = 0.1) -> List[Tuple[float, float]]:
    """Return list of (f, risk_of_ruin)."""
    return [(f, risk_of_ruin(p, payoff_ratio, f, ruin_threshold)) for f in f_values]
