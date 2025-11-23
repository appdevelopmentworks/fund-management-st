"""Reusable Streamlit components."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def equity_and_drawdown_charts(metrics: dict) -> None:
    equity_curve = metrics.get("equity_curve", [])
    dd_series = metrics.get("drawdown_series", [])
    if not equity_curve:
        st.info("資産曲線を表示するにはトレードデータを読み込んでください。")
        return

    df = pd.DataFrame(
        {
            "Trade": list(range(1, len(equity_curve) + 1)),
            "Equity": equity_curve,
            "Drawdown": dd_series if dd_series else [0.0] * len(equity_curve),
        }
    )
    st.line_chart(df, x="Trade", y=["Equity", "Drawdown"])


def metrics_table(metrics: dict) -> None:
    rows = [
        ("トレード数", metrics.get("trade_count", 0)),
        ("勝率", f"{metrics.get('win_rate', 0.0)*100:.1f}%"),
        ("平均損益(円)", f"{metrics.get('avg_pnl', 0.0):,.0f}"),
        ("平均損益(初期資産比)", f"{metrics.get('avg_pnl_pct', 0.0)*100:.2f}%"),
        ("平均R", f"{metrics.get('avg_r', 0.0):.3f}"),
        ("CAGR", f"{metrics.get('cagr', 0.0)*100:.2f}%"),
        ("最大ドローダウン", f"{metrics.get('max_drawdown', 0.0)*100:.2f}%"),
        ("最大DD期間", metrics.get("max_dd_duration", 0)),
        ("同時リスク合計(最大)", f"{metrics.get('max_portfolio_risk', 0.0)*100:.2f}%"),
        ("最終資産", f"{metrics.get('final_equity', 0.0):,.0f}"),
    ]
    df = pd.DataFrame(rows, columns=["指標", "値"])
    st.table(df.astype(str))


def monte_carlo_section(mc_results: dict) -> None:
    if not mc_results:
        st.info("モンテカルロを実行すると分布が表示されます。")
        return
    st.subheader("モンテカルロ分布")
    df = pd.DataFrame(mc_results)
    st.bar_chart(df[["final_equities"]])
    st.bar_chart(df[["cagrs"]])


def ruin_table_component(ruin_rows: list[tuple[float, float]]) -> None:
    if not ruin_rows:
        return
    df = pd.DataFrame(ruin_rows, columns=["f", "Risk of Ruin"])
    df["Risk of Ruin (%)"] = df["Risk of Ruin"] * 100
    st.table(df[["f", "Risk of Ruin (%)"]])
