"""Core simulation engine for sequential trades."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from src.models.trade import Trade, TradeResult
from src.risk.sizing import PositionSizingMode, PositionSizingParams, compute_position_size


@dataclass
class SimulationSettings:
    initial_equity: float
    sizing_mode: str
    sizing_params: PositionSizingParams
    max_portfolio_risk: float


def simulate(trades: List[Trade], settings: SimulationSettings) -> List[TradeResult]:
    """Run a simple sequential simulation over trades ordered by entry date."""
    sorted_trades = sorted(trades, key=lambda t: t.entry_datetime)
    equity = settings.initial_equity
    results: List[TradeResult] = []

    for trade in sorted_trades:
        equity_before = equity
        qty, risk_amount = compute_position_size(
            settings.sizing_mode,
            equity_before,
            trade.entry_price,
            trade.stop_price,
            settings.sizing_params,
        )

        # If trade already has explicit quantity, prefer it for sizing output.
        if trade.quantity is not None:
            qty = trade.quantity
            # Re-evaluate risk if stop present.
            if trade.stop_price is not None:
                risk_amount = abs(trade.entry_price - trade.stop_price) * qty

        risk_pct = (risk_amount / equity_before) if equity_before > 0 else 0.0
        if settings.max_portfolio_risk and risk_pct > settings.max_portfolio_risk > 0:
            scale = settings.max_portfolio_risk / risk_pct
            qty *= scale
            risk_amount *= scale
            risk_pct = settings.max_portfolio_risk

        direction = trade.direction()
        pnl = (trade.exit_price - trade.entry_price) * qty * direction
        equity_after = equity_before + pnl
        r_multiple = (pnl / risk_amount) if risk_amount else 0.0

        results.append(
            TradeResult(
                trade=trade,
                pnl=pnl,
                risk_amount=risk_amount,
                equity_before=equity_before,
                equity_after=equity_after,
                r_multiple=r_multiple,
                f_risk=risk_pct,
                portfolio_risk_sum=risk_pct,
            )
        )
        equity = equity_after

    return results
