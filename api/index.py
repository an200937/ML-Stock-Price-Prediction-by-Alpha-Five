"""
api/index.py — Flask entry point for Vercel
Indian Stock Predictor by Alpha Five Team
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, jsonify, request, Response
import traceback

from src.data_fetcher import NIFTY50_STOCKS
from src.predictor    import run
from src.charts       import chart_price, chart_performance, chart_overlay, chart_next

app = Flask(__name__)

# ══════════════════════════════════════════════════════════════════════════════
#  HTML PAGE
# ══════════════════════════════════════════════════════════════════════════════
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Indian Stock Predictor · Alpha Five</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
/* ── CSS Variables ──────────────────────────────────────── */
:root {
  --bg:       #020817;
  --surface:  #0f172a;
  --card:     #111827;
  --border:   #1e293b;
  --border2:  #243044;
  --text:     #e2e8f0;
  --muted:    #64748b;
  --accent:   #38bdf8;
  --accent2:  #818cf8;
  --green:    #22c55e;
  --red:      #ef4444;
  --gold:     #f59e0b;
  --orange:   #fb923c;
  --glow:     rgba(56,189,248,0.18);
  --font:     'Space Grotesk', sans-serif;
  --mono:     'JetBrains Mono', monospace;
  --display:  'Syne', sans-serif;
}

/* ── Reset ──────────────────────────────────────────────── */
*,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }
html { scroll-behavior:smooth; }
body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  overflow-x: hidden;
}

/* ── Animated background grid ───────────────────────────── */
body::before {
  content:'';
  position:fixed; inset:0; z-index:0;
  background-image:
    linear-gradient(rgba(56,189,248,.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(56,189,248,.03) 1px, transparent 1px);
  background-size: 48px 48px;
  pointer-events:none;
}

/* ── Header ─────────────────────────────────────────────── */
header {
  position: relative; z-index:10;
  border-bottom: 1px solid var(--border);
  background: rgba(2,8,23,0.92);
  backdrop-filter: blur(20px);
  padding: 0 32px;
  display: flex; align-items: center; justify-content: space-between;
  height: 72px;
}
.logo {
  display: flex; align-items: center; gap: 14px;
}
.logo-icon {
  width: 42px; height: 42px;
  background: linear-gradient(135deg, #38bdf8, #818cf8);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  box-shadow: 0 0 20px rgba(56,189,248,0.3);
}
.logo-text h1 {
  font-family: var(--display);
  font-size: 1.2rem;
  font-weight: 800;
  background: linear-gradient(90deg, #38bdf8, #818cf8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.02em;
}
.logo-text p {
  font-size: 0.7rem;
  color: var(--muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-top: 1px;
}
.header-badge {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--accent);
  border: 1px solid rgba(56,189,248,0.3);
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(56,189,248,0.06);
}

/* ── Layout ─────────────────────────────────────────────── */
.layout {
  display: flex;
  min-height: calc(100vh - 72px);
  position: relative; z-index:1;
}

/* ── Sidebar ─────────────────────────────────────────────── */
aside {
  width: 290px;
  flex-shrink: 0;
  background: rgba(15,23,42,0.7);
  border-right: 1px solid var(--border);
  padding: 28px 20px;
  overflow-y: auto;
  backdrop-filter: blur(10px);
}
.sidebar-section { margin-bottom: 8px; }
.sidebar-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  font-weight: 600;
  margin-bottom: 10px;
  margin-top: 20px;
  display: flex; align-items: center; gap: 6px;
}
.sidebar-label:first-child { margin-top: 0; }

/* Stock search */
.stock-search-wrap {
  position: relative;
  margin-bottom: 6px;
}
.stock-search-wrap input {
  width: 100%;
  padding: 10px 36px 10px 12px;
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 8px;
  color: var(--text);
  font-family: var(--font);
  font-size: 0.85rem;
  outline: none;
  transition: border-color .2s, box-shadow .2s;
}
.stock-search-wrap input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(56,189,248,0.12);
}
.search-icon {
  position:absolute; right:10px; top:50%;
  transform:translateY(-50%);
  color:var(--muted); font-size:14px; pointer-events:none;
}

/* Stock list */
.stock-list {
  max-height: 220px;
  overflow-y: auto;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
}
.stock-list::-webkit-scrollbar { width: 4px; }
.stock-list::-webkit-scrollbar-track { background: transparent; }
.stock-list::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }
.stock-item {
  padding: 9px 12px;
  cursor: pointer;
  border-bottom: 1px solid rgba(30,41,59,0.5);
  transition: background .15s;
  display: flex; align-items: center; justify-content: space-between;
}
.stock-item:last-child { border-bottom: none; }
.stock-item:hover { background: rgba(56,189,248,0.08); }
.stock-item.selected {
  background: rgba(56,189,248,0.14);
  color: var(--accent);
}
.stock-item-name { font-size: 0.82rem; font-weight: 500; }
.stock-item-sym  { font-size: 0.68rem; font-family: var(--mono); color: var(--muted); }

/* Form controls */
.ctrl-group { margin-top: 16px; }
.ctrl-label {
  font-size: 0.75rem;
  color: var(--muted);
  font-weight: 500;
  margin-bottom: 6px;
  display: flex; justify-content: space-between;
}
.ctrl-label span { color: var(--accent); font-family: var(--mono); }

input[type=date], input[type=number] {
  width: 100%;
  padding: 9px 12px;
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 8px;
  color: var(--text);
  font-family: var(--mono);
  font-size: 0.85rem;
  outline: none;
  transition: border-color .2s;
}
input[type=date]:focus, input[type=number]:focus {
  border-color: var(--accent);
}
input[type=date]::-webkit-calendar-picker-indicator { filter: invert(0.5); }

/* Range slider */
input[type=range] {
  width: 100%;
  -webkit-appearance: none;
  height: 4px;
  background: var(--border2);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}
input[type=range]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px; height: 16px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 8px var(--glow);
  cursor: pointer;
}

/* Run button */
#run-btn {
  margin-top: 24px;
  width: 100%;
  padding: 13px;
  background: linear-gradient(135deg, #0ea5e9, #6366f1);
  color: white;
  border: none;
  border-radius: 10px;
  font-family: var(--font);
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  letter-spacing: 0.02em;
  position: relative;
  overflow: hidden;
  transition: opacity .2s, transform .15s, box-shadow .2s;
  box-shadow: 0 4px 20px rgba(14,165,233,0.3);
}
#run-btn::before {
  content:'';
  position:absolute; inset:0;
  background: linear-gradient(135deg, rgba(255,255,255,0.12), transparent);
}
#run-btn:hover  { opacity:.92; transform:translateY(-1px); box-shadow: 0 6px 28px rgba(14,165,233,0.4); }
#run-btn:active { transform:translateY(0); }
#run-btn:disabled { opacity:.45; cursor:not-allowed; transform:none; }

/* Selected stock display */
.selected-display {
  background: rgba(56,189,248,0.06);
  border: 1px solid rgba(56,189,248,0.2);
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 6px;
  display: none;
}
.selected-display.show { display: block; }
.selected-display .name { font-size: 0.82rem; font-weight: 600; color: var(--accent); }
.selected-display .sym  { font-size: 0.7rem; font-family: var(--mono); color: var(--muted); margin-top: 2px; }

/* ── Main content ────────────────────────────────────────── */
main {
  flex: 1;
  padding: 28px 32px;
  overflow-y: auto;
}

/* ── Welcome screen ──────────────────────────────────────── */
#welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  text-align: center;
}
.welcome-orb {
  width: 120px; height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(56,189,248,0.25), rgba(99,102,241,0.1));
  border: 1px solid rgba(56,189,248,0.3);
  display: flex; align-items: center; justify-content: center;
  font-size: 52px;
  margin-bottom: 28px;
  box-shadow: 0 0 60px rgba(56,189,248,0.15);
  animation: pulse-orb 3s ease-in-out infinite;
}
@keyframes pulse-orb {
  0%,100% { box-shadow: 0 0 60px rgba(56,189,248,0.15); }
  50%      { box-shadow: 0 0 90px rgba(56,189,248,0.28); }
}
#welcome h2 {
  font-family: var(--display);
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(90deg, #e2e8f0, #94a3b8);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin-bottom: 12px;
}
#welcome p { color: var(--muted); font-size: 0.9rem; line-height: 1.7; max-width: 480px; }
.model-pills { display: flex; gap: 8px; margin-top: 20px; flex-wrap: wrap; justify-content: center; }
.pill {
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid;
}
.pill-blue   { border-color: rgba(56,189,248,0.4);  color: #38bdf8;  background: rgba(56,189,248,0.07); }
.pill-purple { border-color: rgba(129,140,248,0.4); color: #818cf8; background: rgba(129,140,248,0.07); }
.pill-orange { border-color: rgba(251,146,60,0.4);  color: #fb923c;  background: rgba(251,146,60,0.07); }

/* ── Status bar ──────────────────────────────────────────── */
#status {
  display: none;
  padding: 12px 18px;
  border-radius: 10px;
  margin-bottom: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  align-items: center;
  gap: 10px;
  border: 1px solid;
}
#status.show { display: flex; }
#status.info    { background: rgba(56,189,248,0.08);  border-color: rgba(56,189,248,0.25);  color: #7dd3fc; }
#status.success { background: rgba(34,197,94,0.08);   border-color: rgba(34,197,94,0.25);   color: #86efac; }
#status.error   { background: rgba(239,68,68,0.08);   border-color: rgba(239,68,68,0.25);   color: #fca5a5; }

/* ── Metric cards ─────────────────────────────────────────── */
.metric-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}
.metric-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px 20px;
  position: relative;
  overflow: hidden;
  transition: border-color .2s, transform .2s;
}
.metric-card:hover { border-color: var(--border2); transform: translateY(-2px); }
.metric-card::before {
  content:'';
  position:absolute;
  top:0; left:0; right:0;
  height:2px;
}
.metric-card.blue::before   { background: linear-gradient(90deg, #38bdf8, transparent); }
.metric-card.purple::before { background: linear-gradient(90deg, #818cf8, transparent); }
.metric-card.green::before  { background: linear-gradient(90deg, #22c55e, transparent); }
.metric-card.red::before    { background: linear-gradient(90deg, #ef4444, transparent); }
.metric-card.gold::before   { background: linear-gradient(90deg, #f59e0b, transparent); }

.m-label { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); font-weight: 600; }
.m-value { font-family: var(--mono); font-size: 1.5rem; font-weight: 600; color: var(--text); margin: 6px 0 4px; }
.m-sub   { font-size: 0.75rem; color: var(--muted); }
.m-up    { color: var(--green); }
.m-dn    { color: var(--red); }

/* ── Tabs ────────────────────────────────────────────────── */
.tab-bar {
  display: flex; gap: 4px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
}
.tab-btn {
  padding: 10px 20px;
  border: none; background: transparent;
  color: var(--muted);
  font-family: var(--font); font-size: 0.85rem; font-weight: 600;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color .2s, border-color .2s;
  display: flex; align-items: center; gap: 7px;
}
.tab-btn:hover { color: var(--text); }
.tab-btn.active { color: var(--accent); border-bottom-color: var(--accent); }

.tab-panel { display: none; }
.tab-panel.active { display: block; }

/* ── Chart card ──────────────────────────────────────────── */
.chart-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 18px;
}
.chart-card h3 {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted);
  font-weight: 700;
  margin-bottom: 14px;
  display: flex; align-items: center; gap: 8px;
}
.chart-card h3 span { color: var(--accent); }

/* ── Tables ──────────────────────────────────────────────── */
.tbl-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.84rem; }
thead th {
  background: rgba(30,41,59,0.6);
  padding: 11px 16px;
  text-align: left;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  font-weight: 700;
  border-bottom: 1px solid var(--border);
}
tbody td {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(30,41,59,0.5);
  color: var(--text);
  font-family: var(--mono);
  font-size: 0.83rem;
}
tbody tr:hover td { background: rgba(56,189,248,0.04); }
tbody tr:last-child td { border-bottom: none; }
.td-model { font-family: var(--font); font-weight: 600; color: var(--text); }

.badge {
  display: inline-block;
  padding: 3px 9px;
  border-radius: 20px;
  font-size: 0.74rem;
  font-weight: 700;
}
.badge-up { background: rgba(34,197,94,0.15); color: var(--green); border: 1px solid rgba(34,197,94,0.3); }
.badge-dn { background: rgba(239,68,68,0.15);  color: var(--red);   border: 1px solid rgba(239,68,68,0.3); }

/* ── Loading spinner ─────────────────────────────────────── */
.spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(56,189,248,0.2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin .6s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Reveal animation ────────────────────────────────────── */
.reveal { animation: reveal .4s ease both; }
@keyframes reveal {
  from { opacity:0; transform:translateY(12px); }
  to   { opacity:1; transform:translateY(0); }
}

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

@media (max-width:768px) {
  .layout { flex-direction: column; }
  aside   { width:100%; border-right:none; border-bottom:1px solid var(--border); max-height:420px; }
  main    { padding: 18px; }
}
</style>
</head>
<body>

<!-- ══ HEADER ═══════════════════════════════════════════════════ -->
<header>
  <div class="logo">
    <div class="logo-icon">📈</div>
    <div class="logo-text">
      <h1>Indian Stock Predictor</h1>
      <p>by Alpha Five Team</p>
    </div>
  </div>
  <div class="header-badge">Nifty 50 · 3 ML Models · Live NSE Data</div>
</header>

<div class="layout">

<!-- ══ SIDEBAR ══════════════════════════════════════════════════ -->
<aside>

  <div class="sidebar-label">🏢 Select Stock</div>

  <div class="stock-search-wrap">
    <input type="text" id="stock-search" placeholder="Search Nifty 50 stocks…" autocomplete="off" oninput="filterStocks()"/>
    <span class="search-icon">⌕</span>
  </div>

  <div class="selected-display" id="sel-display">
    <div class="name" id="sel-name">—</div>
    <div class="sym"  id="sel-sym">—</div>
  </div>

  <div class="stock-list" id="stock-list"></div>

  <div class="ctrl-group">
    <div class="sidebar-label">📅 Prediction Date</div>
    <input type="date" id="pred-date"/>
  </div>

  <div class="ctrl-group">
    <div class="sidebar-label">📆 History Days
      <span style="margin-left:auto;font-family:var(--mono);color:var(--accent)" id="lb-val">365</span>
    </div>
    <input type="range" id="lookback" min="90" max="730" value="365" step="30"
           oninput="document.getElementById('lb-val').textContent=this.value"/>
  </div>

  <div class="ctrl-group">
    <div class="sidebar-label">🧪 Test Split
      <span style="margin-left:auto;font-family:var(--mono);color:var(--accent)" id="ts-val">20%</span>
    </div>
    <input type="range" id="test-frac" min="0.1" max="0.35" value="0.2" step="0.05"
           oninput="document.getElementById('ts-val').textContent=Math.round(this.value*100)+'%'"/>
  </div>

  <div class="ctrl-group">
    <div class="sidebar-label">⏩ Days Ahead</div>
    <input type="number" id="pred-days" min="1" max="5" value="1"/>
  </div>

  <button id="run-btn" onclick="runAnalysis()" disabled>
    🚀 &nbsp;Run Analysis
  </button>

</aside>

<!-- ══ MAIN ═════════════════════════════════════════════════════ -->
<main>

  <div id="status"></div>

  <!-- Welcome -->
  <div id="welcome">
    <div class="welcome-orb">📊</div>
    <h2>Start Predicting</h2>
    <p>Choose a Nifty 50 stock from the sidebar, set your parameters, and click <strong style="color:var(--accent)">Run Analysis</strong> to see ML-powered price predictions.</p>
    <div class="model-pills">
      <span class="pill pill-blue">Linear Regression</span>
      <span class="pill pill-orange">Decision Tree</span>
      <span class="pill pill-purple">Random Forest</span>
    </div>
  </div>

  <!-- Results (hidden until analysis runs) -->
  <div id="results" style="display:none">

    <!-- Metric cards -->
    <div class="metric-row reveal" id="metric-row"></div>

    <!-- Tabs -->
    <div class="tab-bar">
      <button class="tab-btn active" onclick="switchTab('tech',this)">📊 Technical Chart</button>
      <button class="tab-btn"        onclick="switchTab('ml',this)">🤖 Model Results</button>
      <button class="tab-btn"        onclick="switchTab('pred',this)">🔮 Predictions</button>
    </div>

    <!-- Tab: Technical -->
    <div id="tab-tech" class="tab-panel active">
      <div class="chart-card reveal">
        <h3><span>◈</span> Price · SMA 20/50 · Bollinger Bands · Volume · RSI</h3>
        <div id="ch-price" style="min-height:820px"></div>
      </div>
    </div>

    <!-- Tab: ML Results -->
    <div id="tab-ml" class="tab-panel">
      <div class="chart-card reveal">
        <h3><span>◈</span> Model Performance — RMSE · MAE · R²</h3>
        <div id="ch-perf" style="min-height:380px"></div>
      </div>
      <div class="chart-card reveal" style="animation-delay:.1s">
        <h3><span>◈</span> Predictions vs Actual Price (Test Window)</h3>
        <div id="ch-overlay" style="min-height:480px"></div>
      </div>
      <div class="chart-card reveal" style="animation-delay:.2s">
        <h3><span>◈</span> Performance Summary</h3>
        <div class="tbl-wrap" id="perf-tbl"></div>
      </div>
    </div>

    <!-- Tab: Predictions -->
    <div id="tab-pred" class="tab-panel">
      <div class="chart-card reveal">
        <h3><span>◈</span> Next-Day Prediction by Model</h3>
        <div id="ch-next" style="min-height:340px"></div>
      </div>
      <div class="chart-card reveal" style="animation-delay:.1s">
        <h3><span>◈</span> Prediction Summary</h3>
        <div class="tbl-wrap" id="pred-tbl"></div>
      </div>
    </div>

  </div><!-- #results -->

</main>
</div>

<script>
/* ── Stock list state ──────────────────────────────────────── */
let ALL_STOCKS = {};   // { name: symbol }
let selectedSym  = null;
let selectedName = null;

/* ── Load stock list from API ──────────────────────────────── */
fetch("/api/stocks").then(r=>r.json()).then(d=>{
  ALL_STOCKS = d.stocks;
  renderList(ALL_STOCKS);
});

function renderList(stocks) {
  const el = document.getElementById("stock-list");
  el.innerHTML = Object.entries(stocks).map(([n,s])=>
    `<div class="stock-item${s===selectedSym?' selected':''}"
          onclick="selectStock('${n}','${s}')"
          data-name="${n}" data-sym="${s}">
       <span class="stock-item-name">${n}</span>
       <span class="stock-item-sym">${s.replace('.NS','')}</span>
     </div>`
  ).join("");
}

function filterStocks() {
  const q = document.getElementById("stock-search").value.toLowerCase();
  const filtered = Object.fromEntries(
    Object.entries(ALL_STOCKS).filter(([n,s])=>
      n.toLowerCase().includes(q) || s.toLowerCase().includes(q)
    )
  );
  renderList(filtered);
}

function selectStock(name, sym) {
  selectedSym  = sym;
  selectedName = name;
  document.getElementById("sel-display").classList.add("show");
  document.getElementById("sel-name").textContent = name;
  document.getElementById("sel-sym").textContent  = sym;
  document.getElementById("run-btn").disabled = false;
  renderList(
    document.getElementById("stock-search").value
      ? Object.fromEntries(Object.entries(ALL_STOCKS).filter(([n])=>
          n.toLowerCase().includes(document.getElementById("stock-search").value.toLowerCase())))
      : ALL_STOCKS
  );
}

/* ── Default date = tomorrow ───────────────────────────────── */
const tmr = new Date(); tmr.setDate(tmr.getDate()+1);
document.getElementById("pred-date").value = tmr.toISOString().split("T")[0];

/* ── Tab switcher ──────────────────────────────────────────── */
function switchTab(name, btn){
  document.querySelectorAll(".tab-btn").forEach(b=>b.classList.remove("active"));
  document.querySelectorAll(".tab-panel").forEach(p=>p.classList.remove("active"));
  document.getElementById("tab-"+name).classList.add("active");
  btn.classList.add("active");
}

/* ── Status helper ─────────────────────────────────────────── */
function setStatus(msg, type, spinner=false){
  const el = document.getElementById("status");
  el.innerHTML = (spinner?'<div class="spinner"></div>':'')+`<span>${msg}</span>`;
  el.className = "show "+type;
}
function hideStatus(){ document.getElementById("status").className=""; }

/* ── Main: run analysis ────────────────────────────────────── */
async function runAnalysis(){
  if(!selectedSym){ setStatus("Pick a stock first.","error"); return; }
  const btn = document.getElementById("run-btn");
  btn.disabled = true;
  btn.innerHTML = "⏳ &nbsp;Analysing…";

  setStatus(`Fetching ${selectedName} data and training models…`, "info", true);
  document.getElementById("welcome").style.display  = "none";
  document.getElementById("results").style.display  = "none";

  const payload = {
    ticker:          selectedSym,
    prediction_date: document.getElementById("pred-date").value,
    lookback_days:   +document.getElementById("lookback").value,
    test_frac:       +document.getElementById("test-frac").value,
    prediction_days: +document.getElementById("pred-days").value,
  };

  try {
    const res  = await fetch("/api/analyze", {method:"POST",
      headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)});
    const data = await res.json();
    if(!res.ok){ setStatus("❌ "+( data.error||"Unknown error"), "error"); return; }

    renderMetrics(data);
    renderChart("ch-price",   data.chart_price);
    renderChart("ch-perf",    data.chart_perf);
    renderChart("ch-overlay", data.chart_overlay);
    renderChart("ch-next",    data.chart_next);
    renderPerfTable(data.performance);
    renderPredTable(data.next_pred, data.current_price);

    document.getElementById("results").style.display = "block";
    setStatus(
      `✅ Done! Ensemble: ₹${fmt(data.ensemble)} · Current: ₹${fmt(data.current_price)}`,
      "success"
    );
  } catch(e){
    setStatus("❌ Network error: "+e.message, "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = "🚀 &nbsp;Run Analysis";
  }
}

const fmt = v => v!=null ? Number(v).toLocaleString('en-IN',{maximumFractionDigits:2}) : "—";

function renderChart(id, json){
  const fig = JSON.parse(json);
  Plotly.react(id, fig.data, fig.layout, {responsive:true, displayModeBar:false});
}

function renderMetrics(d){
  const cur = d.current_price;
  const ens = d.ensemble;
  const diff = ens&&cur ? ens-cur : null;
  const diffP= diff&&cur ? diff/cur*100 : null;
  const up   = diff > 0;

  document.getElementById("metric-row").innerHTML = `
    <div class="metric-card blue">
      <div class="m-label">Stock</div>
      <div class="m-value" style="font-size:1.1rem;font-family:var(--font)">${selectedName}</div>
      <div class="m-sub">${selectedSym}</div>
    </div>
    <div class="metric-card gold">
      <div class="m-label">Current Price</div>
      <div class="m-value">₹${fmt(cur)}</div>
      <div class="m-sub">Latest closing</div>
    </div>
    <div class="metric-card ${up?'green':'red'}">
      <div class="m-label">Ensemble Prediction</div>
      <div class="m-value ${up?'m-up':'m-dn'}">₹${fmt(ens)}</div>
      <div class="m-sub ${up?'m-up':'m-dn'}">${diff!=null?(up?'▲':'▼')+' ₹'+fmt(Math.abs(diff))+' ('+Math.abs(diffP).toFixed(2)+'%)':''}</div>
    </div>
    <div class="metric-card purple">
      <div class="m-label">Training Rows</div>
      <div class="m-value">${d.train_size}</div>
      <div class="m-sub">data points</div>
    </div>
    <div class="metric-card blue">
      <div class="m-label">Test Rows</div>
      <div class="m-value">${d.test_size}</div>
      <div class="m-sub">data points</div>
    </div>`;
}

function renderPerfTable(rows){
  if(!rows||!rows.length){document.getElementById("perf-tbl").innerHTML="<p style='color:var(--muted);padding:12px'>No data</p>";return;}
  const cols = Object.keys(rows[0]);
  const tbody = rows.map(r=>"<tr>"+cols.map((c,i)=>
    `<td class="${i===0?'td-model':''}">${typeof r[c]==='number'?r[c].toFixed(4):r[c]}</td>`
  ).join("")+"</tr>").join("");
  document.getElementById("perf-tbl").innerHTML=
    `<table><thead><tr>${cols.map(c=>`<th>${c}</th>`).join("")}</tr></thead><tbody>${tbody}</tbody></table>`;
}

function renderPredTable(preds, cur){
  if(!preds){document.getElementById("pred-tbl").innerHTML="<p style='color:var(--muted);padding:12px'>No data</p>";return;}
  const rows = Object.entries(preds).map(([m,v])=>{
    const d=v&&cur?v-cur:null, p=d&&cur?d/cur*100:null, up=d>0;
    return `<tr>
      <td class="td-model">${m}</td>
      <td>₹${fmt(v)}</td>
      <td>${d!=null?`<span class="badge ${up?'badge-up':'badge-dn'}">${up?'+':''}₹${fmt(Math.abs(d))}</span>`:'—'}</td>
      <td>${p!=null?`<span class="badge ${up?'badge-up':'badge-dn'}">${up?'+':''}${Math.abs(p).toFixed(2)}%</span>`:'—'}</td>
    </tr>`;
  }).join("");
  document.getElementById("pred-tbl").innerHTML=
    `<table><thead><tr><th>Model</th><th>Predicted</th><th>Δ Price</th><th>Δ %</th></tr></thead><tbody>${rows}</tbody></table>`;
}
</script>
</body>
</html>"""


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return Response(HTML, mimetype="text/html")


@app.route("/api/stocks")
def list_stocks():
    return jsonify({"stocks": NIFTY50_STOCKS})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    body = request.get_json(force=True)
    try:
        result = run(
            ticker=          body.get("ticker", "TCS.NS"),
            prediction_date= body.get("prediction_date"),
            lookback_days=   int(body.get("lookback_days", 365)),
            test_frac=       float(body.get("test_frac", 0.2)),
            prediction_days= int(body.get("prediction_days", 1)),
        )
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

    df   = result["df"]
    perf = result["performance"]
    name = body.get("ticker", "Stock")

    perf_rows = [{"Model": idx, **{k: round(v, 4) for k, v in row.items()}}
                 for idx, row in perf.iterrows()]

    return jsonify({
        "chart_price":   chart_price(df, name),
        "chart_perf":    chart_performance(perf),
        "chart_overlay": chart_overlay(df, result["test_preds"], result["test_start_idx"], name),
        "chart_next":    chart_next(result["next_pred"], result["current_price"]),
        "performance":   perf_rows,
        "next_pred":     result["next_pred"],
        "ensemble":      result["ensemble"],
        "current_price": result["current_price"],
        "train_size":    result["train_size"],
        "test_size":     result["test_size"],
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
