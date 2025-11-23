"""UI layout helpers."""

from __future__ import annotations

import io
from typing import List, Optional, Tuple

import pandas as pd
import streamlit as st

from src import config
from src.data.loader import load_trades_csv
from src.models.trade import Trade
from src.risk.sizing import PositionSizingMode, PositionSizingParams
from src.simulation.engine import SimulationSettings


def sidebar_settings() -> Tuple[SimulationSettings, Optional[pd.DataFrame]]:
    st.sidebar.header("設定")
    initial_equity = st.sidebar.number_input("初期資金 (円)", value=config.DEFAULT_INITIAL_EQUITY, min_value=0.0)
    max_portfolio_risk = st.sidebar.number_input(
        "同時最大リスク合計(%)", value=config.DEFAULT_MAX_PORTFOLIO_RISK * 100, min_value=0.0, max_value=100.0
    ) / 100

    sizing_mode = st.sidebar.selectbox(
        "資金管理方式",
        [
            ("Fixed Fractional", PositionSizingMode.FIXED_FRACTIONAL),
            ("Fractional Kelly", PositionSizingMode.FRACTIONAL_KELLY),
            ("Fixed Lot / Notional", PositionSizingMode.FIXED_LOT),
        ],
        format_func=lambda x: x[0],
    )[1]

    params = PositionSizingParams()
    if sizing_mode == PositionSizingMode.FRACTIONAL_KELLY:
        params.p = st.sidebar.number_input("勝率 p", value=0.5, min_value=0.0, max_value=1.0)
        params.expected_r = st.sidebar.number_input("期待値 E[R]", value=1.0, min_value=0.0)
        params.safety_coefficient = st.sidebar.number_input(
            "安全係数 c", value=config.DEFAULT_KELLY_SAFETY_COEFFICIENT, min_value=0.0, max_value=1.0
        )
    elif sizing_mode == PositionSizingMode.FIXED_LOT:
        params.fixed_quantity = st.sidebar.number_input("固定数量 (株/ロット)", value=0.0, min_value=0.0)
        params.fixed_notional = st.sidebar.number_input("固定金額 (円)", value=0.0, min_value=0.0)
    else:
        params.f = st.sidebar.number_input(
            "1トレードリスク f (％)",
            value=config.DEFAULT_FRACTIONAL_RISK * 100,
            min_value=0.0,
            max_value=100.0,
        ) / 100

    uploaded = st.sidebar.file_uploader("トレード履歴 CSV", type=["csv"])
    uploaded_df = None
    if uploaded is not None:
        uploaded_df = pd.read_csv(uploaded)

    settings = SimulationSettings(
        initial_equity=initial_equity,
        sizing_mode=sizing_mode,
        sizing_params=params,
        max_portfolio_risk=max_portfolio_risk,
    )
    return settings, uploaded_df


def parse_trades(uploaded_df: Optional[pd.DataFrame]) -> List[Trade]:
    if uploaded_df is None:
        return []
    buffer = io.StringIO()
    uploaded_df.to_csv(buffer, index=False)
    buffer.seek(0)
    return load_trades_csv(buffer)
