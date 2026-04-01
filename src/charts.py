# TASK 5 — CHARTS
# 4 interactive Plotly charts returned as JSON for the browser.

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def _dark_layout(title: str, height: int) -> dict:
    return dict(
        title=dict(text=title, font=dict(size=16, color="#e2e8f0")),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        hovermode="x unified",
        legend=dict(bgcolor="rgba(15,23,42,0.7)", bordercolor="#334155", borderwidth=1),
        xaxis=dict(gridcolor="#1e293b", linecolor="#334155"),
        yaxis=dict(gridcolor="#1e293b", linecolor="#334155"),
    )


def chart_price(df: pd.DataFrame, stock_name: str) -> str:
    """Price + SMA 20/50 + Bollinger Bands / Volume / RSI"""
    price_col = "adj_close" if "adj_close" in df.columns else "close"
    w = df.copy()

    if "rsi" not in w.columns:
        d = w[price_col].diff()
        g = d.clip(lower=0).rolling(14, min_periods=5).mean()
        l = (-d.clip(upper=0)).rolling(14, min_periods=5).mean()
        w["rsi"] = (100 - 100 / (1 + g/l.replace(0, np.nan))).fillna(50)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.6, 0.2, 0.2], vertical_spacing=0.02,
        subplot_titles=("Price + Moving Averages + Bollinger Bands", "Volume", "RSI (14)"))

    dates = w["date"]
    p = w[price_col]

    fig.add_trace(go.Scatter(x=dates, y=p, name="Price",
        line=dict(color="#38bdf8", width=2)), row=1, col=1)
    if "sma_20" in w.columns:
        fig.add_trace(go.Scatter(x=dates, y=w["sma_20"], name="SMA 20",
            line=dict(color="#fb923c", width=1.5)), row=1, col=1)
    if "sma_50" in w.columns:
        fig.add_trace(go.Scatter(x=dates, y=w["sma_50"], name="SMA 50",
            line=dict(color="#a78bfa", width=1.5)), row=1, col=1)
    if "bb_upper" in w.columns:
        fig.add_trace(go.Scatter(x=dates, y=w["bb_upper"], name="BB Upper",
            line=dict(color="#475569", dash="dot", width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=dates, y=w["bb_lower"], name="BB Lower",
            line=dict(color="#475569", dash="dot", width=1),
            fill="tonexty", fillcolor="rgba(71,85,105,0.08)"), row=1, col=1)

    if "volume" in w.columns:
        fig.add_trace(go.Bar(x=dates, y=w["volume"], name="Volume",
            marker_color="rgba(56,189,248,0.25)"), row=2, col=1)

    fig.add_trace(go.Scatter(x=dates, y=w["rsi"], name="RSI",
        line=dict(color="#f472b6", width=1.5)), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#22c55e", row=3, col=1)
    fig.update_yaxes(range=[0, 100], row=3, col=1)

    fig.update_layout(**_dark_layout(f"{stock_name} — Price & Key Indicators", 820))
    for i in range(1, 4):
        fig.update_xaxes(gridcolor="#1e293b", linecolor="#334155", row=i, col=1)
        fig.update_yaxes(gridcolor="#1e293b", linecolor="#334155", row=i, col=1)
    return fig.to_json()


def chart_performance(perf_df: pd.DataFrame) -> str:
    """RMSE / MAE / R² bar chart per model"""
    models = perf_df.index.tolist()
    colors = ["#38bdf8", "#fb923c", "#a78bfa"]

    fig = make_subplots(rows=1, cols=3, horizontal_spacing=0.08,
        subplot_titles=("RMSE ↓ Lower Better", "MAE ↓ Lower Better", "R² ↑ Higher Better"))

    for col, (metric, clr) in enumerate(zip(["RMSE","MAE","R²"], colors), 1):
        vals = perf_df[metric]
        fig.add_trace(go.Bar(x=models, y=vals, name=metric, marker_color=clr,
            text=vals.round(2), textposition="auto",
            marker=dict(line=dict(width=0))), row=1, col=col)

    fig.update_layout(**_dark_layout("Model Performance Comparison", 380), showlegend=False)
    for i in range(1, 4):
        fig.update_xaxes(tickangle=-20, gridcolor="#1e293b", row=1, col=i)
        fig.update_yaxes(gridcolor="#1e293b", row=1, col=i)
    return fig.to_json()


def chart_overlay(df: pd.DataFrame, test_preds: dict, test_start: int, name: str) -> str:
    """Actual price vs model predictions on test window"""
    price_col = "adj_close" if "adj_close" in df.columns else "close"
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df[price_col], name="Actual",
        line=dict(color="#e2e8f0", width=2)))

    colors = ["#38bdf8", "#fb923c", "#a78bfa"]
    for i, (mname, preds) in enumerate(test_preds.items()):
        n = len(preds)
        dates = df["date"].iloc[test_start:test_start+n]
        fig.add_trace(go.Scatter(x=dates, y=preds, name=mname,
            line=dict(color=colors[i % len(colors)], dash="dash", width=1.5)))

    fig.update_layout(**_dark_layout(f"{name} — Predictions vs Actual (Test Window)", 480))
    fig.update_xaxes(title="Date", gridcolor="#1e293b")
    fig.update_yaxes(title="Price (₹)", gridcolor="#1e293b")
    return fig.to_json()


def chart_next(next_pred: dict, current_price: float) -> str:
    """Next-day prediction per model vs current price"""
    models = list(next_pred.keys())
    vals   = [next_pred[m] or 0 for m in models]
    colors = ["#22c55e" if v > current_price else "#ef4444" for v in vals]

    fig = go.Figure(go.Bar(
        y=models, x=vals, orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"₹{v:,.2f}" for v in vals], textposition="auto",
    ))
    fig.add_vline(x=current_price, line_dash="dash", line_color="#f59e0b", line_width=2,
        annotation_text=f"Current ₹{current_price:,.2f}", annotation_font_color="#f59e0b")
    fig.update_layout(**_dark_layout("Next-Day Prediction by Model", 340))
    fig.update_xaxes(title="Predicted Price (₹)", gridcolor="#1e293b")
    fig.update_yaxes(gridcolor="#1e293b")
    return fig.to_json()
