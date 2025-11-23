"""Position sizing utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


class PositionSizingMode:
    FIXED_FRACTIONAL = "fixed_fractional"
    FRACTIONAL_KELLY = "fractional_kelly"
    FIXED_LOT = "fixed_lot"


@dataclass
class PositionSizingParams:
    f: Optional[float] = None
    p: Optional[float] = None
    expected_r: Optional[float] = None
    safety_coefficient: Optional[float] = None
    fixed_quantity: Optional[float] = None
    fixed_notional: Optional[float] = None


def _per_unit_risk(entry_price: float, stop_price: Optional[float]) -> float:
    if stop_price is None:
        return 0.0
    return abs(entry_price - stop_price)


def fixed_fractional(
    equity: float,
    entry_price: float,
    stop_price: Optional[float],
    params: PositionSizingParams,
) -> Tuple[float, float]:
    """Return quantity and risk_amount for fixed fractional sizing."""
    f = params.f or 0.0
    risk_amount = equity * f
    per_unit = _per_unit_risk(entry_price, stop_price)
    if per_unit <= 0:
        quantity = risk_amount / entry_price if entry_price > 0 else 0.0
        risk_amount = quantity * per_unit
    else:
        quantity = max(risk_amount / per_unit, 0.0)
    return quantity, risk_amount


def fractional_kelly(
    equity: float,
    entry_price: float,
    stop_price: Optional[float],
    params: PositionSizingParams,
) -> Tuple[float, float]:
    """Use Kelly formula (fractional) then delegate to fixed fractional logic."""
    p = params.p or 0.0
    expected_r = params.expected_r or 0.0
    safety = params.safety_coefficient or 0.0
    denominator = expected_r - p + 1
    if denominator == 0:
        f_star = 0
    else:
        f_star = (expected_r * p) / denominator
    f_safe = max(f_star * safety, 0.0)
    return fixed_fractional(
        equity,
        entry_price,
        stop_price,
        PositionSizingParams(f=f_safe),
    )


def fixed_lot(
    equity: float,
    entry_price: float,
    stop_price: Optional[float],
    params: PositionSizingParams,
) -> Tuple[float, float]:
    """Fixed quantity or notional sizing."""
    quantity = params.fixed_quantity
    if quantity is None and params.fixed_notional is not None and entry_price > 0:
        quantity = params.fixed_notional / entry_price
    quantity = quantity or 0.0
    per_unit = _per_unit_risk(entry_price, stop_price)
    risk_amount = per_unit * quantity
    return quantity, risk_amount


def compute_position_size(
    mode: str,
    equity: float,
    entry_price: float,
    stop_price: Optional[float],
    params: PositionSizingParams,
) -> Tuple[float, float]:
    """Dispatch to the selected sizing mode."""
    if mode == PositionSizingMode.FRACTIONAL_KELLY:
        return fractional_kelly(equity, entry_price, stop_price, params)
    if mode == PositionSizingMode.FIXED_LOT:
        return fixed_lot(equity, entry_price, stop_price, params)
    return fixed_fractional(equity, entry_price, stop_price, params)
