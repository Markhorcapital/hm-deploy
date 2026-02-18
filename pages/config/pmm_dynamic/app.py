import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Import submodules
from frontend.components.backtesting import backtesting_section
from frontend.components.config_loader import get_default_config_loader
from frontend.components.executors_distribution import get_executors_distribution_inputs
from frontend.components.save_config import render_save_config
from frontend.pages.config.pmm_dynamic.spread_and_price_multipliers import get_pmm_dynamic_indicators
from frontend.pages.config.pmm_dynamic.user_inputs import user_inputs
from frontend.pages.config.utils import get_candles
from frontend.st_utils import get_backend_api_client, initialize_st_page
from frontend.visualization import theme
from frontend.visualization.backtesting import create_backtesting_figure
from frontend.visualization.backtesting_metrics import render_accuracy_metrics, render_backtesting_metrics, render_close_types
from frontend.visualization.candles import get_candlestick_trace
from frontend.visualization.executors_distribution import create_executors_distribution_traces
from frontend.visualization.utils import add_traces_to_fig

# Initialize the Streamlit page
initialize_st_page(title="PMM Dynamic", icon="👩‍🏫")
backend_api_client = get_backend_api_client()

# Page content
st.text("This tool will let you create a config for PMM Dynamic, backtest and upload it to the Backend API.")
get_default_config_loader("pmm_dynamic")
# Get user inputs
inputs = user_inputs()
st.write("### Visualizing NATR and RSI indicators for PMM Dynamic")
st.text("The NATR is used to detect volatility and adjust spreads dynamically. "
        "The RSI determines buying vs selling pressure for asymmetric spread adjustments. "
        "When volatility is detected, spreads increase asymmetrically based on RSI direction.")
days_to_visualize = st.number_input("Days to Visualize", min_value=1, max_value=365, value=7)

# Load candle data - use volatility_reference_pair for indicators
volatility_pair = inputs.get("volatility_reference_pair", "ETH-USDT")
candles = get_candles(connector_name=inputs["candles_connector"], trading_pair=volatility_pair,
                      interval=inputs["interval"], days=days_to_visualize)

with st.expander("Visualizing PMM Dynamic Indicators", expanded=True):
    # Calculate indicators
    natr, rsi, volatility_detected, natr_exceeded_limit = get_pmm_dynamic_indicators(
        candles, 
        inputs["natr_length"],
        inputs["rsi_length"],
        inputs["volatility_threshold"],
        inputs["natr_upper_limit"]
    )
    
    # Create subplots: Candlestick, NATR, RSI, Volatility Status
    fig = make_subplots(
        rows=4, cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.02, 
        subplot_titles=(
            "Candlestick Chart", 
            "NATR (Normalized Average True Range)", 
            "RSI (Relative Strength Index)",
            "Volatility Detection Status"
        ),
        row_heights=[0.5, 0.2, 0.2, 0.1]
    )
    
    # Row 1: Candlestick
    add_traces_to_fig(fig, [get_candlestick_trace(candles)], row=1, col=1)
    
    # Row 2: NATR with threshold and upper limit lines
    natr_percentage = natr * 100  # Convert to percentage for display
    fig.add_trace(
        go.Scatter(
            x=candles.index, 
            y=natr_percentage, 
            name="NATR (%)", 
            line=dict(color="blue", width=2)
        ), 
        row=2, col=1
    )
    # Add volatility threshold line
    fig.add_hline(
        y=inputs["volatility_threshold"],
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Volatility Threshold ({inputs['volatility_threshold']}%)",
        row=2, col=1
    )
    # Add NATR upper limit line
    fig.add_hline(
        y=inputs["natr_upper_limit"],
        line_dash="dot",
        line_color="red",
        annotation_text=f"NATR Upper Limit ({inputs['natr_upper_limit']}%)",
        row=2, col=1
    )
    
    # Row 3: RSI with buying/selling threshold lines
    fig.add_trace(
        go.Scatter(
            x=candles.index, 
            y=rsi, 
            name="RSI", 
            line=dict(color="purple", width=2)
        ), 
        row=3, col=1
    )
    # Add RSI buying threshold
    fig.add_hline(
        y=inputs["rsi_buying_threshold"],
        line_dash="dash",
        line_color="green",
        annotation_text=f"Buying Threshold ({inputs['rsi_buying_threshold']})",
        row=3, col=1
    )
    # Add RSI selling threshold
    fig.add_hline(
        y=inputs["rsi_selling_threshold"],
        line_dash="dash",
        line_color="red",
        annotation_text=f"Selling Threshold ({inputs['rsi_selling_threshold']})",
        row=3, col=1
    )
    # Add RSI neutral zone (50)
    fig.add_hline(
        y=50.0,
        line_dash="dot",
        line_color="gray",
        opacity=0.5,
        row=3, col=1
    )
    
    # Row 4: Volatility detection status
    # Create a color-coded status indicator
    status_colors = []
    status_text = []
    for i, (vol, exceeded) in enumerate(zip(volatility_detected, natr_exceeded_limit)):
        if exceeded:
            status_colors.append("red")
            status_text.append("STOPPED")
        elif vol:
            status_colors.append("orange")
            status_text.append("HIGH VOLATILITY")
        else:
            status_colors.append("green")
            status_text.append("NORMAL")
    
    fig.add_trace(
        go.Scatter(
            x=candles.index,
            y=[1] * len(candles),
            mode="markers",
            marker=dict(
                size=10,
                color=status_colors,
                symbol="square"
            ),
            name="Volatility Status",
            showlegend=False
        ),
        row=4, col=1
    )
    
    fig.update_layout(**theme.get_default_layout(height=1200))
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="NATR (%)", row=2, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)
    fig.update_yaxes(title_text="Status", range=[0, 2], showticklabels=False, row=4, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display current values and statistics
    current_natr = natr_percentage.iloc[-1] if len(natr_percentage) > 0 else 0
    current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50.0
    is_volatile = volatility_detected.iloc[-1] if len(volatility_detected) > 0 else False
    is_exceeded = natr_exceeded_limit.iloc[-1] if len(natr_exceeded_limit) > 0 else False
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current NATR", f"{current_natr:.2f}%")
    with col2:
        st.metric("Current RSI", f"{current_rsi:.1f}")
    with col3:
        status = "STOPPED" if is_exceeded else ("HIGH VOLATILITY" if is_volatile else "NORMAL")
        st.metric("Volatility Status", status)
    with col4:
        avg_natr = natr_percentage.mean()
        st.metric("Average NATR", f"{avg_natr:.2f}%")

st.write("### Executors Distribution")
st.write("The order distributions use base spreads. When volatility is detected, spreads are adjusted based on NATR and RSI. "
         "The spread increment is applied asymmetrically: wider spreads on the side opposite to the RSI pressure.")
buy_spread_distributions, sell_spread_distributions, buy_order_amounts_pct, \
    sell_order_amounts_pct = get_executors_distribution_inputs(use_custom_spread_units=True)
inputs["buy_spreads"] = [spread * 100 for spread in buy_spread_distributions]
inputs["sell_spreads"] = [spread * 100 for spread in sell_spread_distributions]
inputs["buy_amounts_pct"] = buy_order_amounts_pct
inputs["sell_amounts_pct"] = sell_order_amounts_pct
st.session_state["default_config"].update(inputs)

with st.expander("Executor Distribution:", expanded=True):
    # Calculate average NATR for reference
    natr_percentage = natr * 100
    natr_average = natr_percentage.mean()
    
    st.write(f"**Average NATR: {natr_average:.2f}%**")
    st.write("Note: Base spreads are shown. Actual spreads will be adjusted based on volatility detection and RSI direction.")
    
    # Show base spreads (these will be adjusted dynamically during trading)
    buy_spreads_base = inputs["buy_spreads"]
    sell_spreads_base = inputs["sell_spreads"]
    
    fig = create_executors_distribution_traces(
        buy_spreads_base, 
        sell_spreads_base, 
        inputs["buy_amounts_pct"],
        inputs["sell_amounts_pct"], 
        inputs["total_amount_quote"]
    )
    st.plotly_chart(fig, use_container_width=True)

bt_results = backtesting_section(inputs, backend_api_client)
if bt_results:
    fig = create_backtesting_figure(
        df=bt_results["processed_data"],
        executors=bt_results["executors"],
        config=inputs)
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
