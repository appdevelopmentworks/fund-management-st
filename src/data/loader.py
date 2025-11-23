"""CSV loaders for trades and strategy aggregates."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List

import pandas as pd

from src.models.trade import Trade

REQUIRED_TRADE_COLUMNS = [
    "trade_id",
    "strategy_id",
    "instrument",
    "entry_datetime",
    "exit_datetime",
    "side",
    "entry_price",
    "exit_price",
]

OPTIONAL_TRADE_COLUMNS = ["market", "stop_price", "quantity", "comment"]


def _parse_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value
    try:
        return pd.to_datetime(value)
    except Exception as exc:
        raise ValueError(f"Invalid datetime value: {value}") from exc


def load_trades_csv(file_path: str | Path) -> List[Trade]:
    """Load trades from CSV and validate required columns."""
    df = pd.read_csv(file_path)

    missing = [col for col in REQUIRED_TRADE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    trades: List[Trade] = []
    for _, row in df.iterrows():
        try:
            trade = Trade(
                trade_id=str(row["trade_id"]),
                strategy_id=str(row["strategy_id"]),
                instrument=str(row["instrument"]),
                market=str(row["market"]) if "market" in row and not pd.isna(row["market"]) else None,
                entry_datetime=_parse_datetime(row["entry_datetime"]),
                exit_datetime=_parse_datetime(row["exit_datetime"]),
                side=str(row["side"]).upper(),
                entry_price=float(row["entry_price"]),
                exit_price=float(row["exit_price"]),
                stop_price=float(row["stop_price"])
                if "stop_price" in row and not pd.isna(row["stop_price"])
                else None,
                quantity=float(row["quantity"]) if "quantity" in row and not pd.isna(row["quantity"]) else None,
                comment=str(row["comment"]) if "comment" in row and not pd.isna(row["comment"]) else None,
            )
        except Exception as exc:
            raise ValueError(f"Failed to parse trade row: {row}") from exc
        trades.append(trade)

    return trades


def load_trades_from_records(records: Iterable[dict]) -> List[Trade]:
    """Create trades from iterable of dicts (already validated)."""
    trades: List[Trade] = []
    for row in records:
        trade = Trade(
            trade_id=str(row.get("trade_id")),
            strategy_id=str(row.get("strategy_id")),
            instrument=str(row.get("instrument")),
            market=row.get("market"),
            entry_datetime=_parse_datetime(row.get("entry_datetime")),
            exit_datetime=_parse_datetime(row.get("exit_datetime")),
            side=str(row.get("side", "LONG")).upper(),
            entry_price=float(row.get("entry_price")),
            exit_price=float(row.get("exit_price")),
            stop_price=row.get("stop_price"),
            quantity=row.get("quantity"),
            comment=row.get("comment"),
        )
        trades.append(trade)
    return trades
