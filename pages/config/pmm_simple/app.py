import base64
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

import streamlit as st

from frontend.components.backtesting import backtesting_section
from frontend.components.config_loader import get_default_config_loader
from frontend.components.save_config import render_save_config

# Import submodules
from frontend.pages.config.pmm_simple.user_inputs import user_inputs
from frontend.st_utils import get_backend_api_client, initialize_st_page
from frontend.visualization.backtesting import create_backtesting_figure
from frontend.visualization.backtesting_metrics import render_accuracy_metrics, render_backtesting_metrics, render_close_types
from frontend.visualization.executors_distribution import create_executors_distribution_traces

# Initialize the Streamlit page
initialize_st_page(title="PMM Simple", icon="👨‍🏫")
backend_api_client = get_backend_api_client()

# Page content
st.text("This tool will let you create a config for PMM Simple, backtest and upload it to the Backend API.")
get_default_config_loader("pmm_simple")

inputs = user_inputs()

# Backtesting endpoint requires a non-empty controller identifier (`id`).
# Some UI flows may leave it unset (controller_id: null), causing API validation errors.
if not inputs.get("id") and not inputs.get("controller_id"):
    generated_id = "pmm_simple_ui"
    inputs["id"] = generated_id
    inputs["controller_id"] = generated_id

st.session_state["default_config"].update(inputs)
with st.expander("Executor Distribution:", expanded=True):
    fig = create_executors_distribution_traces(inputs["buy_spreads"], inputs["sell_spreads"], inputs["buy_amounts_pct"],
                                               inputs["sell_amounts_pct"], inputs["total_amount_quote"])
    st.plotly_chart(fig, use_container_width=True)

bt_results = backtesting_section(inputs, backend_api_client)


def _run_direct_backtesting_debug(config_inputs: dict):
    """
    Fallback direct API call to expose exact backend response when
    `backtesting_section` returns None.
    """
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=1)
    start_time = int(config_inputs.get("start_time", int(start_dt.timestamp())))
    end_time = int(config_inputs.get("end_time", int(end_dt.timestamp())))
    resolution = config_inputs.get("backtesting_resolution", "1h")
    trade_cost = float(config_inputs.get("trade_cost", 0.0006))

    config_payload = dict(config_inputs)
    config_payload["id"] = config_payload.get("id") or config_payload.get("controller_id") or "pmm_simple_ui"
    config_payload.pop("controller_id", None)

    payload = {
        "start_time": start_time,
        "end_time": end_time,
        "backtesting_resolution": resolution,
        "trade_cost": trade_cost,
        "config": config_payload,
    }

    host = os.getenv("BACKEND_API_HOST", "hummingbot-api")
    port = os.getenv("BACKEND_API_PORT", "8000")
    username = os.getenv("BACKEND_API_USERNAME", "admin")
    password = os.getenv("BACKEND_API_PASSWORD", "admin")
    url = f"http://{host}:{port}/backtesting/run-backtesting"

    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type", "application/json")
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    req.add_header("Authorization", f"Basic {token}")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

if bt_results is None:
    try:
        bt_results = _run_direct_backtesting_debug(inputs)
    except Exception as e:
        st.error(f"Backtesting failed: {e}")

if bt_results:
    if bt_results.get("error"):
        st.error(f"Backtesting API error: {bt_results.get('error')}")

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
