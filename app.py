import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BorsaITA · Inversioni",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (dark, finance-terminal aesthetic) ─────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0d0f14;
    color: #c9d1d9;
  }
  .stApp { background-color: #0d0f14; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background-color: #111520;
    border-right: 1px solid #1e2535;
  }

  /* Metric cards */
  .metric-card {
    background: #111520;
    border: 1px solid #1e2535;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 10px;
  }
  .metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6e7f9a;
    margin-bottom: 4px;
  }
  .metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    font-weight: 600;
    color: #e6edf3;
  }
  .metric-sub {
    font-size: 0.78rem;
    color: #6e7f9a;
    margin-top: 2px;
  }
  .pos { color: #3fb950; }
  .neg { color: #f85149; }
  .neu { color: #d29922; }

  /* Section headers */
  .section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #3fb950;
    border-bottom: 1px solid #1e2535;
    padding-bottom: 8px;
    margin-bottom: 20px;
    margin-top: 28px;
  }

  /* Insight box */
  .insight-box {
    background: #111d2c;
    border-left: 3px solid #1f6feb;
    border-radius: 0 6px 6px 0;
    padding: 12px 16px;
    font-size: 0.88rem;
    line-height: 1.6;
    margin-bottom: 8px;
    color: #c9d1d9;
  }
  .insight-box strong { color: #79c0ff; }

  /* Tables */
  .stDataFrame { border: 1px solid #1e2535 !important; border-radius: 8px; }

  /* Buttons */
  .stButton > button {
    background: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    transition: all 0.2s;
  }
  .stButton > button:hover {
    background: #1f6feb;
    border-color: #1f6feb;
    color: #fff;
  }

  /* Selectbox */
  .stSelectbox label { color: #6e7f9a; font-size: 0.8rem; }

  /* Title banner */
  .title-banner {
    background: linear-gradient(135deg, #0d0f14 0%, #111d2c 100%);
    border: 1px solid #1e2535;
    border-radius: 10px;
    padding: 28px 32px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
  }
  .title-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #1f6feb, #3fb950, #1f6feb);
  }
  .title-main {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.8rem;
    font-weight: 600;
    color: #e6edf3;
    margin: 0;
    letter-spacing: -0.02em;
  }
  .title-sub {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.9rem;
    color: #6e7f9a;
    margin-top: 6px;
  }
  .title-badge {
    display: inline-block;
    background: #1f3a5f;
    border: 1px solid #1f6feb;
    border-radius: 4px;
    padding: 2px 8px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    color: #79c0ff;
    text-transform: uppercase;
    margin-right: 6px;
  }
</style>
""", unsafe_allow_html=True)

# ── Universe of Milan-listed tickers ─────────────────────────────────────────
MILAN_TICKERS = [
    "ENI.MI","ENEL.MI","ISP.MI","UCG.MI","STM.MI","RACE.MI","TIT.MI","PRY.MI",
    "MB.MI","G.MI","AZM.MI","LDO.MI","SRG.MI","A2A.MI","HER.MI","BZU.MI",
    "CNHI.MI","FCA.MI","BPER.MI","BAMI.MI","BMPS.MI","UNI.MI","TEN.MI","CPR.MI",
    "INW.MI","INWIT.MI","SFER.MI","WEBUILD.MI","CIR.MI","CASS.MI","SFL.MI",
    "IGD.MI","IREN.MI","MARR.MI","MONC.MI","OVIND.MI","PIRC.MI","PIA.MI",
    "REC.MI","SAVE.MI","SOL.MI","SOS.MI","TLNT.MI","TOD.MI","TRN.MI",
    "IVG.MI","FILA.MI","BRE.MI","FNM.MI","GVS.MI","ERG.MI","SAES.MI",
    "SIEM.MI","ALERION.MI","TERNA.MI","POSTE.MI","MEDIOBANCA.MI","AZIMUT.MI",
    "ITALGAS.MI","DIASORIN.MI","AMPLIFON.MI","RECORDATI.MI","INTERPUMP.MI",
    "BRUNELLO.MI","MONCLER.MI","PRADA.MI",
]
# Deduplicate & keep clean list
MILAN_TICKERS = list(dict.fromkeys(MILAN_TICKERS))

MONTHS_IT = {1:"Gennaio",2:"Febbraio",3:"Marzo",4:"Aprile",5:"Maggio",
             6:"Giugno",7:"Luglio",8:"Agosto",9:"Settembre",
             10:"Ottobre",11:"Novembre",12:"Dicembre"}

# ── Helpers ───────────────────────────────────────────────────────────────────
def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    hi, lo, cl = df["High"], df["Low"], df["Close"]
    tr = pd.concat([
        hi - lo,
        (hi - cl.shift()).abs(),
        (lo - cl.shift()).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(com=period - 1, min_periods=period).mean()

def mean_reversion_stats(pct: pd.Series) -> dict:
    """Returns avg negative streak length before a positive day, overall."""
    streaks = []
    count = 0
    for v in pct:
        if v < 0:
            count += 1
        elif v > 0 and count > 0:
            streaks.append(count)
            count = 0
        else:
            count = 0
    avg = float(np.mean(streaks)) if streaks else 0.0
    total_events = len(streaks)
    return {"avg_streak": round(avg, 2), "n_events": total_events}

def monthly_reversion(df: pd.DataFrame) -> pd.DataFrame:
    """Per each calendar month, compute mean reversion stats."""
    rows = []
    for month in range(1, 13):
        subset = df[df.index.month == month]["pct"]
        stats = mean_reversion_stats(subset)
        rows.append({
            "Mese": MONTHS_IT[month],
            "Avg Streak Neg.": stats["avg_streak"],
            "N° Inversioni": stats["n_events"],
            "Var % Media": round(subset.mean(), 3),
            "Var % Mediana": round(subset.median(), 3),
            "% Giorni Positivi": round((subset > 0).mean() * 100, 1),
        })
    return pd.DataFrame(rows)

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def load_all(tickers: list) -> dict:
    results = {}
    for ticker in tickers:
        try:
            raw = yf.download(ticker, period="1y", interval="1d",
                              progress=False, auto_adjust=True)
            if raw.empty or len(raw) < 30:
                continue
            # Flatten multi-index if needed
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            raw = raw[["Open","High","Low","Close","Volume"]].dropna()
            avg_vol = raw["Volume"].mean()
            if avg_vol < 500_000:
                continue
            raw["pct"] = raw["Close"].pct_change() * 100
            raw["RSI"] = compute_rsi(raw["Close"])
            raw["ATR"] = compute_atr(raw)
            raw["ATR_pct"] = (raw["ATR"] / raw["Close"]) * 100
            results[ticker] = raw
        except Exception:
            continue
    return results

# ── Build summary table ───────────────────────────────────────────────────────
def build_summary(data: dict) -> pd.DataFrame:
    rows = []
    for ticker, df in data.items():
        if df.empty:
            continue
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else last
        stats = mean_reversion_stats(df["pct"].dropna())
        rows.append({
            "Ticker": ticker.replace(".MI",""),
            "Prezzo (€)": round(float(last["Close"]), 3),
            "Var % (1d)": round(float(last["pct"]), 2),
            "RSI (14)": round(float(last["RSI"]), 1) if not np.isnan(last["RSI"]) else None,
            "ATR % (14)": round(float(last["ATR_pct"]), 2) if not np.isnan(last["ATR_pct"]) else None,
            "Vol. Medio (M)": round(df["Volume"].mean() / 1e6, 2),
            "Avg Streak Neg.": stats["avg_streak"],
            "N° Inversioni": stats["n_events"],
            "_ticker_full": ticker,
        })
    df_out = pd.DataFrame(rows).sort_values("Var % (1d)", ascending=False)
    return df_out.reset_index(drop=True)

# ── Plotly candlestick + RSI ──────────────────────────────────────────────────
def make_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    fig = make_subplots(
        rows=3, cols=1,
        row_heights=[0.55, 0.25, 0.20],
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=("Prezzi & Volume", "RSI (14)", "ATR %")
    )
    colors = ["#3fb950" if v >= 0 else "#f85149" for v in df["pct"].fillna(0)]

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_line_color="#3fb950", decreasing_line_color="#f85149",
        name="OHLC"
    ), row=1, col=1)

    # Volume bars
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"],
        marker_color=[c + "55" for c in colors],
        name="Volume", yaxis="y2"
    ), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        line=dict(color="#79c0ff", width=1.5), name="RSI"
    ), row=2, col=1)
    fig.add_hline(y=70, line=dict(color="#f85149", dash="dot", width=1), row=2, col=1)
    fig.add_hline(y=30, line=dict(color="#3fb950", dash="dot", width=1), row=2, col=1)
    fig.add_hrect(y0=30, y1=70, fillcolor="#ffffff08", line_width=0, row=2, col=1)

    # ATR %
    fig.add_trace(go.Scatter(
        x=df.index, y=df["ATR_pct"],
        line=dict(color="#d29922", width=1.5), fill="tozeroy",
        fillcolor="#d2992222", name="ATR %"
    ), row=3, col=1)

    fig.update_layout(
        height=620,
        paper_bgcolor="#0d0f14",
        plot_bgcolor="#0d0f14",
        font=dict(family="IBM Plex Mono", color="#6e7f9a", size=11),
        xaxis_rangeslider_visible=False,
        showlegend=False,
        margin=dict(l=8, r=8, t=40, b=8),
        title=dict(text=f"<b>{ticker}</b> · Ultimi 365 giorni",
                   font=dict(color="#e6edf3", size=14)),
    )
    for axis in ["xaxis","xaxis2","xaxis3","yaxis","yaxis2","yaxis3","yaxis4"]:
        fig.update_layout(**{axis: dict(
            gridcolor="#1e2535",
            zerolinecolor="#1e2535",
            color="#6e7f9a",
        )})
    return fig

def make_monthly_bar(monthly: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    colors = ["#3fb950" if v >= 0 else "#f85149" for v in monthly["Var % Media"]]
    fig.add_trace(go.Bar(
        x=monthly["Mese"],
        y=monthly["Var % Media"],
        marker_color=colors,
        name="Var % Media",
        text=[f"{v:+.2f}%" for v in monthly["Var % Media"]],
        textposition="outside",
        textfont=dict(size=10, color="#c9d1d9"),
    ))
    fig.update_layout(
        height=300,
        paper_bgcolor="#0d0f14",
        plot_bgcolor="#0d0f14",
        font=dict(family="IBM Plex Mono", color="#6e7f9a", size=11),
        xaxis=dict(gridcolor="#1e2535"),
        yaxis=dict(gridcolor="#1e2535"),
        margin=dict(l=8, r=8, t=30, b=8),
        title=dict(text="Variazione % media mensile",
                   font=dict(color="#e6edf3", size=13)),
    )
    return fig

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

# ── Title banner ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="title-banner">
  <span class="title-badge">Live</span>
  <span class="title-badge">Borsa Milano</span>
  <p class="title-main">📊 BorsaITA · Mean Reversion Scanner</p>
  <p class="title-sub">Analisi inversioni · RSI · ATR · Statistiche mensili storiche · Ultimi 365 giorni</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Controlli")
    st.caption("Dati via yfinance · Vol min 500K · 365 gg")

    if st.button("🔄  Aggiorna Dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    rsi_min, rsi_max = st.slider("Filtro RSI", 0, 100, (0, 100), step=1)
    vol_min = st.slider("Vol. Medio min (M)", 0.5, 10.0, 0.5, step=0.1)
    st.divider()
    st.caption("© 2025 · BorsaITA Analytics")

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("⏳  Download dati Borsa Italiana…"):
    data = load_all(MILAN_TICKERS)

if not data:
    st.error("Nessun dato disponibile. Verifica la connessione o riprova più tardi.")
    st.stop()

summary = build_summary(data)

# Apply sidebar filters
mask = (
    (summary["Vol. Medio (M)"] >= vol_min) &
    (summary["RSI (14)"].fillna(50).between(rsi_min, rsi_max))
)
summary_filtered = summary[mask].copy()

# ── KPI row ───────────────────────────────────────────────────────────────────
n_tickers = len(summary_filtered)
n_pos = (summary_filtered["Var % (1d)"] > 0).sum()
n_neg = (summary_filtered["Var % (1d)"] < 0).sum()
avg_rsi = summary_filtered["RSI (14)"].mean()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card">
      <div class="metric-label">Titoli Attivi</div>
      <div class="metric-value">{n_tickers}</div>
      <div class="metric-sub">Filtro: Vol >{vol_min}M</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
      <div class="metric-label">Titoli in Rialzo</div>
      <div class="metric-value pos">▲ {n_pos}</div>
      <div class="metric-sub">{round(n_pos/max(n_tickers,1)*100,1)}% del totale</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card">
      <div class="metric-label">Titoli in Ribasso</div>
      <div class="metric-value neg">▼ {n_neg}</div>
      <div class="metric-sub">{round(n_neg/max(n_tickers,1)*100,1)}% del totale</div>
    </div>""", unsafe_allow_html=True)
with c4:
    rsi_color = "neg" if avg_rsi > 65 else ("pos" if avg_rsi < 40 else "neu")
    st.markdown(f"""<div class="metric-card">
      <div class="metric-label">RSI Medio Mercato</div>
      <div class="metric-value {rsi_color}">{round(avg_rsi,1)}</div>
      <div class="metric-sub">{"Ipercomprato" if avg_rsi>65 else "Ipervenduto" if avg_rsi<35 else "Neutro"}</div>
    </div>""", unsafe_allow_html=True)

# ── Main table ────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">◼ Tabella Principale · Tutti i Titoli</p>', unsafe_allow_html=True)

display_cols = ["Ticker","Prezzo (€)","Var % (1d)","RSI (14)","ATR % (14)",
                "Vol. Medio (M)","Avg Streak Neg.","N° Inversioni"]
df_show = summary_filtered[display_cols].copy()

def color_pct(val):
    if pd.isna(val): return ""
    return "color: #3fb950" if val > 0 else ("color: #f85149" if val < 0 else "")

def color_rsi(val):
    if pd.isna(val): return ""
    if val > 70: return "color: #f85149"
    if val < 30: return "color: #3fb950"
    return ""

styled = (df_show.style
    .map(color_pct, subset=["Var % (1d)"])
    .map(color_rsi, subset=["RSI (14)"])
    .format({
        "Prezzo (€)": "{:.3f}",
        "Var % (1d)": "{:+.2f}%",
        "RSI (14)": "{:.1f}",
        "ATR % (14)": "{:.2f}%",
        "Vol. Medio (M)": "{:.2f}M",
        "Avg Streak Neg.": "{:.2f}",
    }, na_rep="—")
    .set_properties(**{
        "background-color": "#111520",
        "color": "#c9d1d9",
        "border-color": "#1e2535",
        "font-family": "IBM Plex Mono",
        "font-size": "13px",
    })
    .set_table_styles([
        {"selector":"th","props":[
            ("background-color","#0d0f14"),
            ("color","#6e7f9a"),
            ("font-size","11px"),
            ("letter-spacing","0.08em"),
            ("text-transform","uppercase"),
            ("border-bottom","1px solid #1e2535"),
        ]},
        {"selector":"tr:hover td","props":[("background-color","#1a2030")]},
    ])
)
st.dataframe(styled, use_container_width=True, height=420)

# ── Drill-down ────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">◼ Drill-Down Titolo · Analisi Storica Mensile</p>', unsafe_allow_html=True)

ticker_labels = sorted([t.replace(".MI","") for t in data.keys()])
selected_label = st.selectbox("Seleziona un titolo", ticker_labels, index=0)
selected_full = selected_label + ".MI"

if selected_full in data:
    df_sel = data[selected_full].copy()

    # Top metrics for selected ticker
    last_row = df_sel.iloc[-1]
    mr = mean_reversion_stats(df_sel["pct"].dropna())

    m1, m2, m3, m4, m5 = st.columns(5)
    for col, label, val, fmt in [
        (m1, "Prezzo Attuale", float(last_row["Close"]), "€{:.3f}"),
        (m2, "Var % (1d)", float(last_row["pct"]), "{:+.2f}%"),
        (m3, "RSI (14)", float(last_row["RSI"]), "{:.1f}"),
        (m4, "ATR % (14)", float(last_row["ATR_pct"]), "{:.2f}%"),
        (m5, "Avg Streak Neg.", mr["avg_streak"], "{:.2f} gg"),
    ]:
        with col:
            color = ""
            if "Var" in label:
                color = "pos" if val > 0 else "neg"
            elif "RSI" in label:
                color = "neg" if val > 70 else ("pos" if val < 30 else "neu")
            st.markdown(f"""<div class="metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value {color}">{fmt.format(val)}</div>
            </div>""", unsafe_allow_html=True)

    # Chart
    st.plotly_chart(make_chart(df_sel, selected_label), use_container_width=True)

    # Monthly stats
    monthly_df = monthly_reversion(df_sel)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("**Statistiche Mensili**")
        st.dataframe(
            monthly_df.style
            .format({
                "Avg Streak Neg.": "{:.2f}",
                "Var % Media": "{:+.3f}%",
                "Var % Mediana": "{:+.3f}%",
                "% Giorni Positivi": "{:.1f}%",
            })
            .map(lambda v: "color:#3fb950" if isinstance(v,float) and v>0 else "color:#f85149" if isinstance(v,float) and v<0 else "",
                      subset=["Var % Media","Var % Mediana"])
            .set_properties(**{
                "background-color":"#111520",
                "color":"#c9d1d9",
                "font-family":"IBM Plex Mono",
                "font-size":"12px",
            })
            .set_table_styles([{"selector":"th","props":[
                ("background-color","#0d0f14"),("color","#6e7f9a"),
                ("font-size","10px"),("text-transform","uppercase"),
            ]}]),
            use_container_width=True, height=460,
        )

    with col_right:
        st.plotly_chart(make_monthly_bar(monthly_df), use_container_width=True)

        # Insight bullets
        st.markdown("**📌 Regola Statistica · Insights Mensili**")
        for _, row in monthly_df.iterrows():
            avg_s = row["Avg Streak Neg."]
            n_ev = row["N° Inversioni"]
            pct_pos = row["% Giorni Positivi"]
            mese = row["Mese"]
            if n_ev == 0:
                note = f"Nessuna inversione rilevata a {mese} nell'ultimo anno."
            elif avg_s <= 1.2:
                note = (f"A <strong>{mese}</strong>, mediamente dopo solo "
                        f"<strong>{avg_s}</strong> giorno/i negativi si osserva un rimbalzo "
                        f"(su {n_ev} eventi · {pct_pos}% gg positivi).")
            else:
                note = (f"A <strong>{mese}</strong>, mediamente dopo <strong>{avg_s}</strong> "
                        f"chiusure negative consecutive si verifica un'inversione rialzista "
                        f"(su {n_ev} eventi · {pct_pos}% gg positivi).")
            st.markdown(f'<div class="insight-box">{note}</div>', unsafe_allow_html=True)

else:
    st.warning("Dati non disponibili per il ticker selezionato.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("⚠️ Questo strumento è a scopo puramente informativo/educativo. "
           "Non costituisce consulenza finanziaria. I dati sono forniti da Yahoo Finance via yfinance.")
