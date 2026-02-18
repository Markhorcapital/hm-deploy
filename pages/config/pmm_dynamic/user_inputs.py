import streamlit as st

from frontend.components.market_making_general_inputs import get_market_making_general_inputs
from frontend.components.risk_management import get_risk_management_inputs


def user_inputs():
    default_config = st.session_state.get("default_config", {})
    
    # NATR parameters
    natr_length = default_config.get("natr_length", 14)
    volatility_threshold = default_config.get("volatility_threshold", 1.0)
    natr_upper_limit = default_config.get("natr_upper_limit", 10.0)
    
    # RSI parameters
    rsi_length = default_config.get("rsi_length", 14)
    rsi_buying_threshold = default_config.get("rsi_buying_threshold", 60.0)
    rsi_selling_threshold = default_config.get("rsi_selling_threshold", 40.0)
    rsi_asymmetric_multiplier = default_config.get("rsi_asymmetric_multiplier", 1.5)
    
    # Volatility parameters
    volatility_reference_pair = default_config.get("volatility_reference_pair", "ETH-USDT")
    volatility_spread_increment_pct = default_config.get("volatility_spread_increment_pct", 1.0)
    
    position_rebalance_threshold_pct = default_config.get("position_rebalance_threshold_pct", 0.05)
    skip_rebalance = default_config.get("skip_rebalance", False)
    
    connector_name, trading_pair, leverage, total_amount_quote, position_mode, cooldown_time, executor_refresh_time, \
        candles_connector, candles_trading_pair, interval = get_market_making_general_inputs(custom_candles=True)
    sl, tp, time_limit, ts_ap, ts_delta, take_profit_order_type = get_risk_management_inputs()
    
    with st.expander("PMM Dynamic Configuration", expanded=True):
        st.write("**Volatility Detection (NATR)**")
        c1, c2, c3 = st.columns(3)
        with c1:
            natr_length = st.number_input("NATR Length", min_value=1, max_value=200, value=natr_length, 
                                         help="Period for NATR calculation")
        with c2:
            volatility_threshold = st.number_input(
                "Volatility Threshold (%)", 
                min_value=0.1, 
                max_value=50.0, 
                value=volatility_threshold,
                step=0.1,
                help="NATR percentage to trigger spread increase (e.g., 1.0 for 1%)"
            )
        with c3:
            natr_upper_limit = st.number_input(
                "NATR Upper Limit (%)", 
                min_value=1.0, 
                max_value=100.0, 
                value=natr_upper_limit,
                step=0.5,
                help="Maximum NATR percentage - orders stop if exceeded (e.g., 10.0 for 10%)"
            )
        
        st.write("**Directional Bias (RSI)**")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            rsi_length = st.number_input("RSI Length", min_value=1, max_value=200, value=rsi_length,
                                       help="Period for RSI calculation")
        with c2:
            rsi_buying_threshold = st.number_input(
                "RSI Buying Threshold", 
                min_value=50.0, 
                max_value=100.0, 
                value=rsi_buying_threshold,
                step=1.0,
                help="RSI threshold for buying pressure (e.g., 60.0)"
            )
        with c3:
            rsi_selling_threshold = st.number_input(
                "RSI Selling Threshold", 
                min_value=0.0, 
                max_value=50.0, 
                value=rsi_selling_threshold,
                step=1.0,
                help="RSI threshold for selling pressure (e.g., 40.0)"
            )
        with c4:
            rsi_asymmetric_multiplier = st.number_input(
                "RSI Asymmetric Multiplier", 
                min_value=1.0, 
                max_value=5.0, 
                value=rsi_asymmetric_multiplier,
                step=0.1,
                help="Multiplier for asymmetric spread adjustments (e.g., 1.5 for 50% wider spreads)"
            )
        
        st.write("**Spread Adjustment**")
        c1, c2 = st.columns(2)
        with c1:
            volatility_reference_pair = st.text_input(
                "Volatility Reference Pair",
                value=volatility_reference_pair,
                help="Trading pair to use for NATR/RSI calculation (e.g., ETH-USDT). Use a stable pair for consistent volatility detection."
            )
        with c2:
            volatility_spread_increment_pct = st.number_input(
                "Volatility Spread Increment (%)", 
                min_value=0.1, 
                max_value=10.0, 
                value=volatility_spread_increment_pct,
                step=0.1,
                help="Additional spread percentage when volatility is detected (e.g., 1.0 for 1%)"
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
                help="Threshold percentage for position rebalancing"
            ) / 100
        with c2:
            skip_rebalance = st.checkbox(
                "Skip Rebalance", 
                value=skip_rebalance,
                help="Skip position rebalancing"
            )

    # Create the config
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
        "candles_connector": candles_connector,
        "candles_trading_pair": candles_trading_pair,
        "interval": interval,
        "volatility_reference_pair": volatility_reference_pair,
        "volatility_spread_increment_pct": volatility_spread_increment_pct,
        "natr_length": natr_length,
        "rsi_length": rsi_length,
        "rsi_buying_threshold": rsi_buying_threshold,
        "rsi_selling_threshold": rsi_selling_threshold,
        "rsi_asymmetric_multiplier": rsi_asymmetric_multiplier,
        "volatility_threshold": volatility_threshold,
        "natr_upper_limit": natr_upper_limit,
        "stop_loss": sl,
        "take_profit": tp,
        "time_limit": time_limit,
        "take_profit_order_type": take_profit_order_type.value,
        "trailing_stop": {
            "activation_price": ts_ap,
            "trailing_delta": ts_delta
        },
        "position_rebalance_threshold_pct": position_rebalance_threshold_pct,
        "skip_rebalance": skip_rebalance
    }

    return config
