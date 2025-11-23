import streamlit as st

from src import config
from src.data.loader import load_trades_from_records
from src.presets import manager as preset_manager
from src.risk.metrics import compute_metrics
from src.risk.ruin import ruin_table
from src.simulation.engine import SimulationSettings, simulate
from src.simulation.monte_carlo import run_monte_carlo
from src.ui import components, layout


def sample_trades():
    records = [
        {
            "trade_id": "T1",
            "strategy_id": "EVT",
            "instrument": "7203.T",
            "market": "JP",
            "entry_datetime": "2024-01-01 09:00:00",
            "exit_datetime": "2024-01-05 15:00:00",
            "side": "LONG",
            "entry_price": 2000,
            "exit_price": 2100,
            "stop_price": 1900,
        },
        {
            "trade_id": "T2",
            "strategy_id": "EVT",
            "instrument": "9984.T",
            "market": "JP",
            "entry_datetime": "2024-02-01 09:00:00",
            "exit_datetime": "2024-02-03 15:00:00",
            "side": "LONG",
            "entry_price": 6000,
            "exit_price": 5700,
            "stop_price": 5700,
        },
        {
            "trade_id": "T3",
            "strategy_id": "ML",
            "instrument": "USDJPY=X",
            "market": "FX",
            "entry_datetime": "2024-03-01 10:00:00",
            "exit_datetime": "2024-03-02 10:00:00",
            "side": "SHORT",
            "entry_price": 150.0,
            "exit_price": 148.5,
            "stop_price": 151.5,
        },
    ]
    return load_trades_from_records(records)


def main():
    st.set_page_config(page_title="資金管理シミュレーション", layout="wide")
    st.title("資金管理シミュレーション & 戦略評価")

    settings, uploaded_df = layout.sidebar_settings()
    trades = layout.parse_trades(uploaded_df)

    use_sample = st.sidebar.checkbox("サンプルトレードを使う", value=not trades)
    if use_sample and not trades:
        trades = sample_trades()

    st.sidebar.markdown("---")
    preset_action = st.sidebar.selectbox("プリセット操作", ["なし", "保存", "読み込み", "削除"])
    preset_name = st.sidebar.text_input("プリセット名")

    if preset_action == "保存" and preset_name:
        preset_manager.save_preset(
            preset_name,
            {
                "initial_equity": settings.initial_equity,
                "max_portfolio_risk": settings.max_portfolio_risk,
                "sizing_mode": settings.sizing_mode,
                "params": settings.sizing_params.__dict__,
            },
        )
        st.sidebar.success(f"プリセットを保存しました: {preset_name}")
    elif preset_action == "読み込み" and preset_name:
        try:
            data = preset_manager.load_preset(preset_name)
            settings = SimulationSettings(
                initial_equity=data.get("initial_equity", config.DEFAULT_INITIAL_EQUITY),
                sizing_mode=data.get("sizing_mode", settings.sizing_mode),
                sizing_params=settings.sizing_params.__class__(**data.get("params", {})),
                max_portfolio_risk=data.get("max_portfolio_risk", config.DEFAULT_MAX_PORTFOLIO_RISK),
            )
            st.sidebar.success(f"プリセットを読み込みました: {preset_name}")
        except FileNotFoundError:
            st.sidebar.error("プリセットが見つかりませんでした。")
    elif preset_action == "削除" and preset_name:
        preset_manager.delete_preset(preset_name)
        st.sidebar.info(f"プリセットを削除しました: {preset_name}")

    tabs = st.tabs(["結果", "モンテカルロ", "破産確率", "プリセット一覧"])

    with tabs[0]:
        st.header("シミュレーション結果")
        if not trades:
            st.info("CSV をアップロードするかサンプルデータを有効にしてください。")
        else:
            results = simulate(trades, settings)
            metrics = compute_metrics(results, settings.initial_equity)
            components.metrics_table(metrics)
            components.equity_and_drawdown_charts(metrics)

    with tabs[1]:
        st.header("モンテカルロシミュレーション")
        if not trades:
            st.info("トレードデータを読み込んでください。")
        else:
            n_sims = st.number_input("試行回数", value=config.DEFAULT_MONTE_CARLO_SIMS, min_value=10, max_value=2000)
            mc_runs = st.number_input("各試行のトレード数 (省略可)", value=0, min_value=0)
            if st.button("モンテカルロ実行"):
                mc_results = run_monte_carlo(trades, settings, int(n_sims), int(mc_runs) or None)
                components.monte_carlo_section(mc_results)

    with tabs[2]:
        st.header("破産確率（簡易）")
        p = st.number_input("勝率 p", value=0.5, min_value=0.0, max_value=1.0)
        payoff_ratio = st.number_input("損益比 (平均利益/平均損失)", value=1.0, min_value=0.0)
        ruin_threshold = st.number_input("破産とみなす残高比", value=0.1, min_value=0.0, max_value=1.0)
        f_values = [i / 100 for i in range(1, 11)]
        rows = ruin_table(p, payoff_ratio, f_values, ruin_threshold)
        components.ruin_table_component(rows)

    with tabs[3]:
        st.header("プリセット一覧")
        presets = preset_manager.list_presets()
        if presets:
            st.write(presets)
        else:
            st.info("保存されたプリセットはありません。")


if __name__ == "__main__":
    main()
