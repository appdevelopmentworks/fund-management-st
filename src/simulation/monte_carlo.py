"""Monte Carlo simulation utilities."""

from __future__ import annotations

import random
from typing import Dict, List, Optional

from src.models.trade import Trade
from src.risk.metrics import compute_metrics
from src.simulation.engine import SimulationSettings, simulate


def _sample_trades(trades: List[Trade], n_trades: Optional[int]) -> List[Trade]:
    if n_trades is None or n_trades <= 0:
        sampled = trades[:]
        random.shuffle(sampled)
        return sampled
    return random.choices(trades, k=n_trades)


def run_monte_carlo(
    trades: List[Trade],
    settings: SimulationSettings,
    n_sims: int = 100,
    n_trades: Optional[int] = None,
) -> Dict[str, List[float]]:
    """Run multiple randomized simulations and return distribution stats."""
    final_equities: List[float] = []
    cagrs: List[float] = []
    max_dds: List[float] = []

    for _ in range(n_sims):
        sampled_trades = _sample_trades(trades, n_trades)
        results = simulate(sampled_trades, settings)
        metrics = compute_metrics(results, settings.initial_equity)
        final_equities.append(metrics["final_equity"])
        cagrs.append(metrics["cagr"])
        max_dds.append(metrics["max_drawdown"])

    return {
        "final_equities": final_equities,
        "cagrs": cagrs,
        "max_drawdowns": max_dds,
    }
