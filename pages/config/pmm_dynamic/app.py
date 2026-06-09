from decimal import Decimal

import streamlit as st

from frontend.components.backtesting import backtesting_section
from frontend.components.config_loader import get_default_config_loader
from frontend.components.executors_distribution import get_executors_distribution_inputs
from frontend.components.save_config import render_save_config
from frontend.pages.config.pmm_dynamic.regime_preview import (
    compute_basis_pct,
    compute_level_prices,
    infer_regime,
)
from frontend.pages.config.pmm_dynamic.user_inputs import user_inputs
from frontend.pages.config.utils import get_candles
from frontend.st_utils import get_backend_api_client, initialize_st_page
from frontend.visualization.backtesting import create_backtesting_figure
from frontend.visualization.backtesting_metrics import (
    render_accuracy_metrics,
    render_backtesting_metrics,
    render_close_types,
)
from frontend.visualization.candles import get_candlestick_trace
from frontend.visualization.executors_distribution import create_executors_distribution_traces
from frontend.visualization.utils import add_traces_to_fig

initialize_st_page(title="PMM Dynamic", icon="👩‍🏫")
backend_api_client = get_backend_api_client()

st.text(
    "Configure PMM Dynamic (DEX/CEX asymmetric market making), preview regime quotes, "
    "backtest CEX-only approximation, and save to the Backend API."
)
get_default_config_loader("pmm_dynamic")

inputs = user_inputs()

st.write("### Regime Quote Preview")
st.caption(
    "Enter hypothetical CEX and DEX fair prices to preview Regime A/B level-0 quotes. "
    "Live dex_fair comes from on-chain Uniswap TWAP when the bot runs."
)
c1, c2 = st.columns(2)
with c1:
    preview_cex_mid = st.number_input(
        "Preview CEX Mid",
        min_value=0.0,
        value=0.01,
        format="%.6f",
        help=f"Mid price for {inputs['trading_pair']} on {inputs['connector_name']}.",
    )
with c2:
    preview_dex_fair = st.number_input(
        "Preview DEX Fair",
        min_value=0.0,
        value=0.0098,
        format="%.6f",
        help="Uniswap TWAP × ETH/USDT fair price for the base token.",
    )

buy_spread_distributions, sell_spread_distributions, buy_order_amounts_pct, \
    sell_order_amounts_pct = get_executors_distribution_inputs()
inputs["buy_spreads"] = buy_spread_distributions
inputs["sell_spreads"] = sell_spread_distributions
inputs["buy_amounts_pct"] = buy_order_amounts_pct
inputs["sell_amounts_pct"] = sell_order_amounts_pct
st.session_state["default_config"].update(inputs)

if preview_cex_mid > 0 and preview_dex_fair > 0:
    cex = Decimal(str(preview_cex_mid))
    dex = Decimal(str(preview_dex_fair))
    basis = compute_basis_pct(cex, dex)
    regime = infer_regime(basis, inputs["regime_hysteresis_bps"])
    basis_str = f"{float(basis) * 100:.4f}%" if basis is not None else "N/A"

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Basis", basis_str)
    with m2:
        st.metric("Inferred Regime", regime or "Unset")
    with m3:
        st.metric("Log-Only Mode", "Yes" if inputs["dex_cex_log_only"] else "No")
    with m4:
        st.metric("TWAP Window", f"{inputs['dex_twap_seconds']}s")

    if regime and not inputs["dex_cex_log_only"]:
        level_prices = compute_level_prices(
            cex, dex, inputs["buy_spreads"], inputs["sell_spreads"], regime
        )
        if level_prices:
            st.write(f"**Active regime {regime} quotes (first levels):**")
            cols = st.columns(min(4, len(level_prices)))
            for idx, (label, price) in enumerate(level_prices.items()):
                if idx >= 4:
                    break
                with cols[idx]:
                    st.metric(label, f"{float(price):.6f}")
    elif inputs["dex_cex_log_only"]:
        st.info(
            "Log-only mode: live orders use CEX mid ± spreads. "
            "Regime anchors are logged but not used for quoting."
        )
    else:
        st.warning(
            f"Regime unset at |basis| ≤ {inputs['regime_hysteresis_bps']} bps. "
            "Live quotes are blocked until basis exceeds the hysteresis threshold."
        )

st.write("### CEX Price History")
st.caption("Historical CEX mid proxy (close) for the market-making pair. DEX fair is not available in backfill.")
days_to_visualize = st.number_input("Days to Visualize", min_value=1, max_value=365, value=7)
candles = get_candles(
    connector_name=inputs["connector_name"],
    trading_pair=inputs["trading_pair"],
    interval="1m",
    days=days_to_visualize,
)

with st.expander("CEX Candlestick Chart", expanded=True):
    if not candles.empty and all(c in candles.columns for c in ["open", "high", "low", "close"]):
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        from frontend.visualization import theme

        fig = make_subplots(rows=1, cols=1, subplot_titles=(f"{inputs['trading_pair']} on {inputs['connector_name']}",))
        add_traces_to_fig(fig, [get_candlestick_trace(candles)], row=1, col=1)
        fig.update_layout(**theme.get_default_layout(height=500))
        st.plotly_chart(fig, use_container_width=True)
        if len(candles) > 0:
            st.metric("Latest Close (CEX proxy)", f"{candles['close'].iloc[-1]:.6f}")
    else:
        st.warning("No candle data available for the selected connector and trading pair.")

st.write("### Executors Distribution")
st.caption(
    "Spreads are decimals (e.g. 0.001 = 0.1%). "
    "In live Regime mode, buy/sell anchors switch between cex_mid and dex_fair per regime."
)
with st.expander("Executor Distribution", expanded=True):
    fig = create_executors_distribution_traces(
        inputs["buy_spreads"],
        inputs["sell_spreads"],
        inputs["buy_amounts_pct"],
        inputs["sell_amounts_pct"],
        inputs["total_amount_quote"],
    )
    st.plotly_chart(fig, use_container_width=True)

st.write("### Backtesting")
st.warning(
    "Backtesting uses CEX candle data only and does not simulate on-chain DEX TWAP or Regime A/B anchors. "
    "Use it as a rough CEX-side reference, not as a DEX/CEX performance estimate."
)
bt_results = backtesting_section(inputs, backend_api_client)
if bt_results:
    fig = create_backtesting_figure(
        df=bt_results["processed_data"],
        executors=bt_results["executors"],
        config=inputs,
    )
    c1, c2 = st.columns([0.9, 0.1])
    with c1:
        render_backtesting_metrics(bt_results["results"])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        render_accuracy_metrics(bt_results["results"])
        st.write("---")
        render_close_types(bt_results["results"])

st.write("---")
render_save_config(st.session_state["default_config"]["id"], st.session_state["default_config"])
