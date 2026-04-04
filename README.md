# 📈 Indian Stock Price Predictor

A clean ML web app that predicts Indian stock prices using 3 machine learning models.
Built with Flask + Plotly. One-click deploy to Vercel.

---

## 📁 File Structure

```
indian-stock-predictor/
│
├── api/
│   └── index.py            ← 🚀 Main Flask app (Vercel entry point)
│
├── src/
│   ├── data_fetcher.py     ← 📥 TASK 1: Download stock data from Yahoo Finance
│   ├── features.py         ← 🔧 TASK 2: Add technical indicators (SMA, RSI, MACD…)
│   ├── trainer.py          ← 🤖 TASK 3: Train ML models & evaluate
│   ├── predictor.py        ← 🔮 TASK 4: Run full prediction pipeline
│   └── charts.py           ← 📊 TASK 5: Build interactive Plotly charts
│
├── requirements.txt        ← Python dependencies
├── vercel.json             ← Vercel deployment config
└── .vercelignore           ← Files to exclude from deploy
```

---

## 🧠 How it works

```
User clicks "Run Analysis"
    ↓
data_fetcher.py    → Downloads price history from Yahoo Finance (yfinance)
    ↓
features.py        → Calculates 25+ technical indicators (SMA, EMA, MACD, RSI, Bollinger…)
    ↓
trainer.py         → Trains 5 ML models side by side, scores each one
    ↓
predictor.py       → Picks the last feature row → predicts tomorrow's price
    ↓
charts.py          → Builds 4 interactive Plotly charts → JSON
    ↓
api/index.py       → Returns everything to the browser as JSON
    ↓
Browser            → Renders charts with Plotly.js
```

---

## 🤖 ML Models used

| Model              | Type         |
|--------------------|--------------|
| Linear Regression  | Linear       |
| Decision Tree      | Tree-based   |
| Random Forest      | Ensemble     |


---

## 🚀 Deploy to Vercel (3 steps)

1. Push this folder to a GitHub repo
2. Go to [vercel.com](https://vercel.com) → **Add New Project** → import your repo
3. Vercel auto-detects `vercel.json` and deploys — no extra config needed ✅

---

## 💻 Run locally

```bash
pip install -r requirements.txt
python api/index.py
# Open http://localhost:5000
```

---

## 📊 Technical Indicators Calculated

- **SMA** 5, 10, 20, 50 — Simple Moving Averages
- **EMA** 12, 26 — Exponential Moving Averages
- **MACD** + Signal + Histogram
- **RSI** (14-day) — Overbought/oversold
- **Bollinger Bands** (20-day ±2σ) + position within bands
- **Volume Ratio** — current vs 10-day avg volume
- **OBV** — On-Balance Volume
- **Volatility** (20-day rolling std)
- **Momentum** (10-day)
- **Lag Features** — previous 1, 2, 3, 5 day prices
- **Support / Resistance** (20-day rolling min/max)
