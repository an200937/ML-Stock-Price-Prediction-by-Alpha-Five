# TASK 1 — DATA FETCHER
# Downloads stock data from Yahoo Finance for any Nifty 50 symbol

import yfinance as yf
import pandas as pd
from datetime import date, timedelta

# ── All 50 Nifty 50 stocks ──────────────────────────────────────────────────
NIFTY50_STOCKS = {
    "Adani Enterprises":        "ADANIENT.NS",
    "Adani Ports":              "ADANIPORTS.NS",
    "Apollo Hospitals":         "APOLLOHOSP.NS",
    "Asian Paints":             "ASIANPAINT.NS",
    "Axis Bank":                "AXISBANK.NS",
    "Bajaj Auto":               "BAJAJ-AUTO.NS",
    "Bajaj Finance":            "BAJFINANCE.NS",
    "Bajaj Finserv":            "BAJAJFINSV.NS",
    "Bharti Airtel":            "BHARTIARTL.NS",
    "BPCL":                     "BPCL.NS",
    "Britannia Industries":     "BRITANNIA.NS",
    "Cipla":                    "CIPLA.NS",
    "Coal India":               "COALINDIA.NS",
    "Divi's Laboratories":      "DIVISLAB.NS",
    "Dr. Reddy's Laboratories": "DRREDDY.NS",
    "Eicher Motors":            "EICHERMOT.NS",
    "Grasim Industries":        "GRASIM.NS",
    "HCL Technologies":         "HCLTECH.NS",
    "HDFC Bank":                "HDFCBANK.NS",
    "HDFC Life Insurance":      "HDFCLIFE.NS",
    "Hero MotoCorp":            "HEROMOTOCO.NS",
    "Hindalco Industries":      "HINDALCO.NS",
    "Hindustan Unilever":       "HINDUNILVR.NS",
    "ICICI Bank":               "ICICIBANK.NS",
    "IndusInd Bank":            "INDUSINDBK.NS",
    "Infosys":                  "INFY.NS",
    "ITC":                      "ITC.NS",
    "JSW Steel":                "JSWSTEEL.NS",
    "Kotak Mahindra Bank":      "KOTAKBANK.NS",
    "Larsen & Toubro":          "LT.NS",
    "LTIMindtree":              "LTIM.NS",
    "Mahindra & Mahindra":      "M&M.NS",
    "Maruti Suzuki":            "MARUTI.NS",
    "NTPC":                     "NTPC.NS",
    "Nestle India":             "NESTLEIND.NS",
    "Oil & Natural Gas Corp":   "ONGC.NS",
    "Power Grid Corp":          "POWERGRID.NS",
    "Reliance Industries":      "RELIANCE.NS",
    "SBI Life Insurance":       "SBILIFE.NS",
    "Shriram Finance":          "SHRIRAMFIN.NS",
    "State Bank of India":      "SBIN.NS",
    "Sun Pharmaceutical":       "SUNPHARMA.NS",
    "Tata Consultancy Services":"TCS.NS",
    "Tata Consumer Products":   "TATACONSUM.NS",
    "Tata Motors":              "TATAMOTORS.NS",
    "Tata Steel":               "TATASTEEL.NS",
    "Tech Mahindra":            "TECHM.NS",
    "Titan Company":            "TITAN.NS",
    "UltraTech Cement":         "ULTRACEMCO.NS",
    "Wipro":                    "WIPRO.NS",
}


def fetch_stock_data(ticker: str, prediction_date: str, lookback_days: int = 365) -> pd.DataFrame:
    """
    Downloads historical stock data.

    Args:
        ticker         : NSE symbol e.g. "RELIANCE.NS"
        prediction_date: Target date "YYYY-MM-DD"
        lookback_days  : Days of history to fetch

    Returns:
        Clean DataFrame with: date, open, high, low, close, adj_close, volume
    """
    end_date   = pd.to_datetime(prediction_date) - timedelta(days=1)
    start_date = end_date - timedelta(days=lookback_days)

    raw = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if raw.empty:
        raise ValueError(f"No data found for '{ticker}'. Check the symbol.")

    # Flatten MultiIndex columns (yfinance quirk)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.droplevel(1)

    raw = raw.rename(columns={
        "Open": "open", "High": "high", "Low": "low",
        "Close": "close", "Adj Close": "adj_close", "Volume": "volume",
    })

    if "adj_close" not in raw.columns:
        raw["adj_close"] = raw["close"]

    raw = raw.reset_index().rename(columns={"Date": "date"})
    raw = raw.dropna(subset=["close", "adj_close"])
    raw = raw.sort_values("date").reset_index(drop=True)

    if len(raw) < 60:
        raise ValueError(f"Only {len(raw)} rows — need at least 60. Increase lookback days.")

    return raw
