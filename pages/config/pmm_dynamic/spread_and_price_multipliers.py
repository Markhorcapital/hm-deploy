import pandas as pd
import pandas_ta as ta  # noqa: F401


def get_pmm_dynamic_indicators(df, natr_length, rsi_length, volatility_threshold, natr_upper_limit):
    """
    Get NATR and RSI indicators for PMM Dynamic visualization.
    Returns NATR, RSI, volatility_detected, and natr_exceeded_limit flags.
    """
    required = ["high", "low", "close"]
    if df.empty or not all(c in df.columns for c in required):
        n = len(df) if not df.empty else 0
        return (
            pd.Series([0.01] * n),
            pd.Series([50.0] * n),
            pd.Series([False] * n),
            pd.Series([False] * n),
        )
    # Calculate NATR
    natr_raw = ta.natr(df["high"], df["low"], df["close"], length=natr_length)
    
    if natr_raw is None or len(natr_raw) == 0:
        natr = pd.Series([0.01] * len(df))  # Default 1%
    else:
        # Convert from 0-100 range to 0-1 range (percentage)
        natr = natr_raw / 100
    
    # Calculate RSI
    rsi = ta.rsi(df["close"], length=rsi_length)
    
    if rsi is None or len(rsi) == 0:
        rsi = pd.Series([50.0] * len(df))  # Default neutral RSI
    
    # Calculate volatility detection flags
    natr_percentage = natr * 100  # Convert to percentage for comparison
    
    # Check if NATR exceeds upper limit
    natr_exceeded_limit = natr_percentage >= natr_upper_limit
    
    # Check if volatility is detected (above threshold but below upper limit)
    volatility_detected = (natr_percentage >= volatility_threshold) & (natr_percentage < natr_upper_limit)
    
    return natr, rsi, volatility_detected, natr_exceeded_limit
