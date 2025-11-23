"""Performance metrics for trade simulations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

from src.models.trade import TradeResult


@dataclass
class DrawdownStats:
    max_drawdown: float
    max_duration: int
    drawdown_series: List[float]


def _drawdown(equity_curve: List[float]) -> DrawdownStats:
    peaks = np.maximum.accumulate(equity_curve)
    drawdowns = (equity_curve - peaks) / peaks
    durations = []
    duration = 0
    for equity, peak in zip(equity_curve, peaks):
        if equity < peak:
            duration += 1
        else:
            duration = 0
        durations.append(duration)
    return DrawdownStats(
        max_drawdown=float(drawdowns.min()) if len(drawdowns) else 0.0,
        max_duration=int(max(durations)) if durations else 0,
        drawdown_series=drawdowns.tolist(),
    )


def _cagr(initial_equity: float, final_equity: float, years: float) -> float:
    if initial_equity <= 0 or years <= 0:
        return 0.0
    return (final_equity / initial_equity) ** (1 / years) - 1


def compute_metrics(
    results: List[TradeResult], initial_equity: float, years: float = 1.0
) -> dict:
    """Aggregate performance statistics."""
    trade_count = len(results)
    pnl_values = np.array([r.pnl for r in results], dtype=float)
    r_values = np.array([r.r_multiple for r in results], dtype=float)
    equity_curve = [r.equity_after for r in results]

    wins = (pnl_values > 0).sum()
    total_pnl = float(pnl_values.sum())
    avg_pnl = float(pnl_values.mean()) if trade_count else 0.0
    avg_pnl_pct = avg_pnl / initial_equity if initial_equity > 0 else 0.0
    avg_r = float(r_values.mean()) if trade_count else 0.0

    dd = _drawdown(equity_curve) if equity_curve else DrawdownStats(0.0, 0, [])
    final_equity = equity_curve[-1] if equity_curve else initial_equity

    portfolio_risks = np.array([r.portfolio_risk_sum for r in results], dtype=float)
    max_portfolio_risk = float(portfolio_risks.max()) if portfolio_risks.size else 0.0

    return {
        "trade_count": trade_count,
        "win_rate": wins / trade_count if trade_count else 0.0,
        "total_pnl": total_pnl,
        "avg_pnl": avg_pnl,
        "avg_pnl_pct": avg_pnl_pct,
        "avg_r": avg_r,
        "max_drawdown": dd.max_drawdown,
        "max_dd_duration": dd.max_duration,
        "drawdown_series": dd.drawdown_series,
        "final_equity": final_equity,
        "cagr": _cagr(initial_equity, final_equity, years),
        "max_portfolio_risk": max_portfolio_risk,
        "equity_curve": equity_curve,
    }
