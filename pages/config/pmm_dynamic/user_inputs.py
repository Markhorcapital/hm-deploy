import streamlit as st

from frontend.components.market_making_general_inputs import get_market_making_general_inputs
from frontend.components.risk_management import get_risk_management_inputs

DEFAULT_POOL_ADDRESS = "0xF260d15e8eBe54D210ef53F5b61Cb46bD9Aa29EE"
DEFAULT_ALI_TOKEN = "0x6B0b3a982b4634aC68dD83a4DBF02311cE324181"
DEFAULT_WETH_TOKEN = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"


def user_inputs():
    default_config = st.session_state.get("default_config", {})

    dex_rpc_url = default_config.get("dex_rpc_url", "")
    dex_pool_address = default_config.get("dex_pool_address", DEFAULT_POOL_ADDRESS)
    dex_base_token_address = default_config.get("dex_base_token_address", DEFAULT_ALI_TOKEN)
    dex_quote_token_address = default_config.get("dex_quote_token_address", DEFAULT_WETH_TOKEN)
    dex_eth_usdt_trading_pair = default_config.get("dex_eth_usdt_trading_pair", "ETH-USDT")
    dex_poll_interval_seconds = default_config.get("dex_poll_interval_seconds", 12)
    dex_twap_seconds = default_config.get("dex_twap_seconds", 180)
    dex_price_max_stale_seconds = default_config.get("dex_price_max_stale_seconds", 30)
    dex_sanity_max_divergence_pct = float(default_config.get("dex_sanity_max_divergence_pct", 0.15))
    regime_hysteresis_bps = default_config.get("regime_hysteresis_bps", 50)
    regime_hysteresis_ticks = default_config.get("regime_hysteresis_ticks", 2)
    dex_cex_log_only = default_config.get("dex_cex_log_only", True)
    dex_cex_debug = default_config.get("dex_cex_debug", True)
    cancel_open_orders_on_refresh = default_config.get("cancel_open_orders_on_refresh", True)

    position_rebalance_threshold_pct = default_config.get("position_rebalance_threshold_pct", 0.05)
    skip_rebalance = default_config.get("skip_rebalance", False)

    connector_name, trading_pair, leverage, total_amount_quote, position_mode, cooldown_time, \
        executor_refresh_time, _, _, _ = get_market_making_general_inputs()
    sl, tp, time_limit, ts_ap, ts_delta, take_profit_order_type = get_risk_management_inputs()

    with st.expander("DEX Price Feed (Uniswap V3)", expanded=True):
        st.caption(
            "dex_fair = Uniswap V3 pool TWAP × CEX ETH/USDT mid. "
            "Leave RPC URL empty to use DEX_RPC_URL or WEB3_PROVIDER on the bot container."
        )
        c1, c2 = st.columns(2)
        with c1:
            dex_rpc_url = st.text_input(
                "Ethereum RPC URL",
                value=dex_rpc_url,
                type="password",
                help="Optional here if DEX_RPC_URL is set on the bot. Required when saving config without env fallback.",
            )
            dex_pool_address = st.text_input("Uniswap V3 Pool Address", value=dex_pool_address)
            dex_base_token_address = st.text_input("Base Token Address", value=dex_base_token_address)
        with c2:
            dex_quote_token_address = st.text_input("Quote Token Address (WETH)", value=dex_quote_token_address)
            dex_eth_usdt_trading_pair = st.text_input(
                "CEX ETH/USDT Pair",
                value=dex_eth_usdt_trading_pair,
                help="ETH-USDT on the same connector used for market making.",
            )
            dex_poll_interval_seconds = st.number_input(
                "Poll Interval (seconds)",
                min_value=1,
                max_value=300,
                value=int(dex_poll_interval_seconds),
            )
        c1, c2, c3 = st.columns(3)
        with c1:
            dex_twap_seconds = st.number_input(
                "TWAP Window (seconds)",
                min_value=10,
                max_value=3600,
                value=int(dex_twap_seconds),
                help="Uniswap observe() window. 60–300s is typical for reactive basis.",
            )
        with c2:
            dex_price_max_stale_seconds = st.number_input(
                "Max Stale Seconds",
                min_value=5,
                max_value=600,
                value=int(dex_price_max_stale_seconds),
            )
        with c3:
            dex_sanity_max_divergence_pct = st.number_input(
                "Sanity Max Divergence",
                min_value=0.01,
                max_value=1.0,
                value=float(dex_sanity_max_divergence_pct),
                step=0.01,
                format="%.2f",
                help="Block quotes when |cex_mid - dex_fair| / dex_fair exceeds this (e.g. 0.15 = 15%).",
            )

    with st.expander("Regime A/B Quoting", expanded=True):
        st.markdown(
            "**Regime A** (`cex_mid > dex_fair`): buy at `dex_fair`, sell at `cex_mid`.  \n"
            "**Regime B** (`dex_fair > cex_mid`): buy at `cex_mid`, sell at `dex_fair`."
        )
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            regime_hysteresis_bps = st.number_input(
                "Hysteresis (bps)",
                min_value=1,
                max_value=500,
                value=int(regime_hysteresis_bps),
                help="Regime switch threshold in basis points (50 = 0.5%).",
            )
        with c2:
            regime_hysteresis_ticks = st.number_input(
                "Confirm Ticks",
                min_value=1,
                max_value=20,
                value=int(regime_hysteresis_ticks),
                help="Consecutive polls beyond threshold before switching regime.",
            )
        with c3:
            dex_cex_log_only = st.checkbox(
                "Log-Only Mode",
                value=bool(dex_cex_log_only),
                help="When enabled, quotes use CEX mid ± spreads while logging dex_fair and regime.",
            )
        with c4:
            dex_cex_debug = st.checkbox("Debug Logging", value=bool(dex_cex_debug))

    with st.expander("Order Refresh", expanded=False):
        cancel_open_orders_on_refresh = st.checkbox(
            "Cancel Open Orders on Refresh",
            value=bool(cancel_open_orders_on_refresh),
        )

    with st.expander("Position Rebalancing", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            position_rebalance_threshold_pct = st.number_input(
                "Position Rebalance Threshold (%)",
                min_value=0.0,
                max_value=100.0,
                value=position_rebalance_threshold_pct * 100,
                step=0.1,
            ) / 100
        with c2:
            skip_rebalance = st.checkbox("Skip Rebalance", value=skip_rebalance)

    config = {
        "controller_name": "pmm_dynamic",
        "controller_type": "market_making",
        "manual_kill_switch": False,
        "candles_config": [],
        "connector_name": connector_name,
        "trading_pair": trading_pair,
        "total_amount_quote": total_amount_quote,
        "executor_refresh_time": executor_refresh_time,
        "cooldown_time": cooldown_time,
        "leverage": leverage,
        "position_mode": position_mode,
        "cancel_open_orders_on_refresh": cancel_open_orders_on_refresh,
        "dex_rpc_url": dex_rpc_url,
        "dex_pool_address": dex_pool_address,
        "dex_base_token_address": dex_base_token_address,
        "dex_quote_token_address": dex_quote_token_address,
        "dex_eth_usdt_trading_pair": dex_eth_usdt_trading_pair,
        "dex_poll_interval_seconds": int(dex_poll_interval_seconds),
        "dex_twap_seconds": int(dex_twap_seconds),
        "dex_price_max_stale_seconds": int(dex_price_max_stale_seconds),
        "dex_sanity_max_divergence_pct": dex_sanity_max_divergence_pct,
        "regime_hysteresis_bps": int(regime_hysteresis_bps),
        "regime_hysteresis_ticks": int(regime_hysteresis_ticks),
        "dex_cex_log_only": dex_cex_log_only,
        "dex_cex_debug": dex_cex_debug,
        "stop_loss": sl,
        "take_profit": tp,
        "time_limit": time_limit,
        "take_profit_order_type": take_profit_order_type.value,
        "trailing_stop": {
            "activation_price": ts_ap,
            "trailing_delta": ts_delta,
        },
        "position_rebalance_threshold_pct": position_rebalance_threshold_pct,
        "skip_rebalance": skip_rebalance,
    }

    return config
