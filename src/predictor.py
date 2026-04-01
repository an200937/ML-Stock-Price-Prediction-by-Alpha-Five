# TASK 4 — PREDICTOR
# Runs the full pipeline in one call.

import numpy as np
import pandas as pd
from datetime import date

from src.data_fetcher import fetch_stock_data
from src.features     import add_indicators, build_xy, time_split
from src.trainer      import preprocess, train_all


def run(ticker: str, prediction_date: str = None,
        lookback_days: int = 365, test_frac: float = 0.2,
        prediction_days: int = 1) -> dict:
    """
    Full pipeline:
      1. Download data
      2. Add indicators
      3. Split train/test
      4. Scale
      5. Train 3 models
      6. Predict next price

    Returns dict with everything the frontend needs.
    """
    if prediction_date is None:
        prediction_date = str(date.today())

    # Step 1 – Fetch
    df_raw = fetch_stock_data(ticker, prediction_date, lookback_days)

    # Step 2 – Features
    df = add_indicators(df_raw)

    # Step 3 – Split
    train_df, test_df = time_split(df, test_frac)

    target = "adj_close" if "adj_close" in df.columns else "close"
    current_price = float(df[target].iloc[-1])

    X_tr_df, y_tr = build_xy(train_df, target, prediction_days)
    X_te_df, y_te = build_xy(test_df,  target, prediction_days)

    # Align columns
    cols = sorted(set(X_tr_df.columns) & set(X_te_df.columns))
    X_tr_df, X_te_df = X_tr_df[cols], X_te_df[cols]

    # Step 4 – Scale
    X_tr, X_te, imputer, scaler = preprocess(X_tr_df, X_te_df)

    # Step 5 – Train
    perf, models, test_preds = train_all(X_tr, y_tr.values, X_te, y_te.values)

    # Step 6 – Predict next price
    last_row = scaler.transform(imputer.transform(X_te_df.iloc[[-1]]))
    next_pred = {}
    for name, m in models.items():
        try:
            next_pred[name] = round(float(m.predict(last_row)[0]), 2)
        except Exception:
            next_pred[name] = None

    valid = [v for v in next_pred.values() if v]
    ensemble = round(float(np.mean(valid)), 2) if valid else None

    return {
        "df":             df,
        "performance":    perf,
        "test_preds":     test_preds,
        "y_test":         y_te.tolist(),
        "next_pred":      next_pred,
        "ensemble":       ensemble,
        "current_price":  current_price,
        "train_size":     len(X_tr),
        "test_size":      len(X_te),
        "feature_names":  cols,
        "test_start_idx": len(train_df),
        "target":         target,
    }
