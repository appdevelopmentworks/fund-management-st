"""Trade and TradeResult models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Trade:
    trade_id: str
    strategy_id: str
    instrument: str
    market: Optional[str]
    entry_datetime: datetime
    exit_datetime: datetime
    side: str  # "LONG" or "SHORT"
    entry_price: float
    exit_price: float
    stop_price: Optional[float]
    quantity: Optional[float] = None
    comment: Optional[str] = None

    def direction(self) -> int:
        """Return +1 for long, -1 for short."""
        return 1 if self.side.upper() == "LONG" else -1


@dataclass
class TradeResult:
    trade: Trade
    pnl: float
    risk_amount: float
    equity_before: float
    equity_after: float
    r_multiple: float
    f_risk: float
    portfolio_risk_sum: float
