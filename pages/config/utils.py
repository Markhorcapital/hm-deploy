import datetime

import pandas as pd
import streamlit as st

from frontend.st_utils import get_backend_api_client


def get_max_records(days_to_download: int, interval: str) -> int:
    conversion = {"s": 1 / 60, "m": 1, "h": 60, "d": 1440}
    unit = interval[-1]
    quantity = int(interval[:-1])
    return int(days_to_download * 24 * 60 / (quantity * conversion[unit]))


@st.cache_data
def get_candles(connector_name="binance", trading_pair="BTC-USDT", interval="1m", days=7):
    backend_client = get_backend_api_client()
    
    # Use the market_data.get_candles_last_days method
    candles = backend_client.market_data.get_candles_last_days(
        connector_name=connector_name,
        trading_pair=trading_pair,
        days=days,
        interval=interval
    )
    
    # Normalize response: API may return a list of candle dicts, a single dict (error or one row), or empty
    if isinstance(candles, dict):
        if "error" in candles:
            return pd.DataFrame()
        # Single row (all scalar values) — wrap in list so DataFrame gets one row
        candles = [candles]
    if not candles:
        return pd.DataFrame()
    
    df = pd.DataFrame(candles)
    if df.empty:
        return df
    # Normalize column names to lowercase (API may return e.g. High, Low, Close)
    df.columns = df.columns.str.lower().str.strip()
    # Map common alternate OHLC names to standard (open, high, low, close)
    ohlc_rename = {"o": "open", "h": "high", "l": "low", "c": "close"}
    for alt, standard in ohlc_rename.items():
        if alt in df.columns and standard not in df.columns:
            df = df.rename(columns={alt: standard})
    if "timestamp" in df.columns:
        df.index = pd.to_datetime(df.timestamp, unit="s")
    return df
