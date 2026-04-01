# TASK 2 — FEATURE ENGINEERING
# Only the most important, easy-to-understand indicators.
# Designed to AVOID overfitting — no exotic or redundant features.

import pandas as pd
import numpy as np


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds the 8 most important technical indicators.
    Kept simple to prevent overfitting.

    Indicators:
      SMA 20, SMA 50   → Trend direction
      RSI 14           → Momentum (overbought/oversold)
      MACD             → Trend momentum
      Bollinger %B     → Where price sits in volatility band
      Volume Ratio     → Unusual buying/selling activity
      Daily Return     → % change today
      Lag 1, 5         → Yesterday and last week's price
    """
    df = df.copy()
    price = df["adj_close"] if "adj_close" in df.columns else df["close"]

    # ── Trend: Moving Averages ─────────────────────────────────
    df["sma_20"] = price.rolling(20, min_periods=10).mean()
    df["sma_50"] = price.rolling(50, min_periods=25).mean()

    # ── MACD (trend momentum) ──────────────────────────────────
    ema_12 = price.ewm(span=12, adjust=False).mean()
    ema_26 = price.ewm(span=26, adjust=False).mean()
    df["macd"] = ema_12 - ema_26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    # ── RSI 14 (momentum) ──────────────────────────────────────
    delta = price.diff()
    gain  = delta.clip(lower=0).rolling(14, min_periods=5).mean()
    loss  = (-delta.clip(upper=0)).rolling(14, min_periods=5).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["rsi"] = (100 - 100 / (1 + rs)).fillna(50)

    # ── Bollinger %B (volatility position) ────────────────────
    bb_mid = price.rolling(20, min_periods=10).mean()
    bb_std = price.rolling(20, min_periods=10).std()
    bb_upper = bb_mid + 2 * bb_std
    bb_lower = bb_mid - 2 * bb_std
    df["bb_upper"] = bb_upper     # keep for charts
    df["bb_lower"] = bb_lower     # keep for charts
    denom = (bb_upper - bb_lower).replace(0, np.nan)
    df["bb_pct"] = ((price - bb_lower) / denom).fillna(0.5)

    # ── Volume Ratio (unusual activity) ───────────────────────
    if "volume" in df.columns:
        vol_avg = df["volume"].rolling(10, min_periods=5).mean()
        df["volume_ratio"] = (df["volume"] / vol_avg.replace(0, np.nan)).fillna(1)

    # ── Daily Return & Lags ────────────────────────────────────
    df["daily_return"] = price.pct_change()
    df["lag_1"]  = price.shift(1)   # yesterday's price
    df["lag_5"]  = price.shift(5)   # last week's price
    df["lag_10"] = price.shift(10)  # 2 weeks ago

    return df


def build_xy(df: pd.DataFrame, target_col: str = "adj_close", prediction_days: int = 1):
    """
    Builds feature matrix X and target y.
    Target = price N days in the future.
    """
    df = df.copy()
    df["target"] = df[target_col].shift(-prediction_days)
    df = df.dropna(subset=["target"])

    # Features: exclude date, raw OHLCV (too easy to memorise = overfitting)
    drop = {"target", "date", target_col, "open", "high", "low",
            "close", "volume", "bb_upper", "bb_lower"}
    feature_cols = [c for c in df.columns if c not in drop]

    X = df[feature_cols].copy()
    y = df["target"].copy()

    # Drop rows with NaN features
    valid = ~X.isna().any(axis=1)
    return X[valid], y[valid]


def time_split(df: pd.DataFrame, test_frac: float = 0.2):
    """Chronological split — never shuffle time series data."""
    n = int(len(df) * (1 - test_frac))
    return df.iloc[:n].reset_index(drop=True), df.iloc[n:].reset_index(drop=True)
