import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="RevertMI · Scanner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');

  /* ── Base ── */
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #080a0f; color: #e2e8f0; }
  .stApp { background-color: #080a0f; }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background-color: #0d1117 !important;
    border-right: 1px solid #21262d !important;
  }
  section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
  section[data-testid="stSidebar"] .stSlider label,
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] small { color: #c9d1d9 !important; }
  /* Slider track + thumb contrast */
  section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] [role="slider"] {
    background: #3fb950 !important;
    border-color: #3fb950 !important;
  }

  /* ── Global text legibility ── */
  p, span, div, li { color: #e2e8f0; }
  .stMarkdown p { color: #d0d7de; font-size: 0.92rem; line-height: 1.6; }
  /* captions */
  small, .stCaption, [data-testid="stCaptionContainer"] { color: #8b949e !important; font-size: 0.82rem !important; }
  /* selectbox label */
  .stSelectbox label { color: #c9d1d9 !important; font-size: 0.85rem !important; font-weight: 500; }
  /* selectbox value text */
  .stSelectbox [data-baseweb="select"] { background: #161b22 !important; border-color: #30363d !important; }
  .stSelectbox [data-baseweb="select"] * { color: #e2e8f0 !important; }

  /* ── Metric cards ── */
  .metric-card {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
  }
  .metric-card:hover { border-color: #30363d; }
  .metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #8b949e;
    margin-bottom: 6px;
    font-weight: 500;
  }
  .metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    font-weight: 600;
    color: #f0f6fc;
    line-height: 1.2;
  }
  .metric-sub { font-size: 0.76rem; color: #8b949e; margin-top: 4px; }
  .pos { color: #3fb950 !important; }
  .neg { color: #f85149 !important; }
  .neu { color: #e3b341 !important; }

  /* ── Section headers ── */
  .section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #3fb950;
    border-bottom: 1px solid #21262d;
    padding-bottom: 10px;
    margin-bottom: 20px;
    margin-top: 30px;
    font-weight: 600;
  }

  /* ── Title banner ── */
  .title-banner {
    background: linear-gradient(135deg, #0d1117 0%, #111d2c 60%, #0d1117 100%);
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
  }
  .title-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #1f6feb 0%, #3fb950 50%, #1f6feb 100%);
  }
  .title-main {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem; font-weight: 600;
    color: #f0f6fc; margin: 0;
    letter-spacing: -0.02em;
  }
  .title-sub { font-size: 0.88rem; color: #8b949e; margin-top: 8px; font-weight: 400; }
  .title-badge {
    display: inline-block;
    background: #1f3a5f; border: 1px solid #1f6feb;
    border-radius: 4px; padding: 3px 9px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem; letter-spacing: 0.12em;
    color: #79c0ff; text-transform: uppercase; margin-right: 6px;
    font-weight: 600;
  }

  /* ── Drill-down heading ── */
  h3 { color: #f0f6fc !important; font-size: 1.05rem !important; font-weight: 600 !important; }

  /* ── Streamlit dataframe text ── */
  [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── FTSE MIB completo + extra liquid mid-caps ────────────────────────────────
# FTSE MIB 40 completo con simboli Yahoo Finance verificati + mid-cap liquidi
MILAN_TICKERS = [
    # FTSE MIB 40
    "A2A.MI",   # A2A
    "AMP.MI",   # Amplifon
    "AZM.MI",   # Azimut
    "BAMI.MI",  # Banco BPM
    "BC.MI",    # Brunello Cucinelli
    "BMED.MI",  # Banca Mediolanum
    "BMPS.MI",  # Monte dei Paschi
    "BPER.MI",  # BPER Banca
    "BZU.MI",   # Buzzi
    "CNHI.MI",  # CNH Industrial
    "CPR.MI",   # Azimut (ex-CPR)
    "DIA.MI",   # DiaSorin
    "ENEL.MI",  # Enel
    "ENI.MI",   # Eni
    "ERG.MI",   # ERG
    "FBK.MI",   # FinecoBank
    "G.MI",     # Generali
    "HER.MI",   # Hera
    "IG.MI",    # Italgas
    "IP.MI",    # Interpump
    "IREN.MI",  # Iren
    "ISP.MI",   # Intesa Sanpaolo
    "LDO.MI",   # Leonardo
    "MB.MI",    # Mediobanca
    "MONC.MI",  # Moncler
    "NEXI.MI",  # Nexi
    "PIRC.MI",  # Pirelli
    "PRY.MI",   # Prysmian
    "PST.MI",   # Poste Italiane
    "RACE.MI",  # Ferrari
    "REC.MI",   # Recordati
    "SRG.MI",   # Snam
    "STLAM.MI", # Stellantis
    "STM.MI",   # STMicroelectronics
    "TEN.MI",   # Tenaris
    "TIT.MI",   # Telecom Italia
    "TRN.MI",   # Terna
    "UCG.MI",   # UniCredit
    "UNI.MI",   # Unipol
    "WBD.MI",   # Webuild
    # Mid-cap liquidi
    "INW.MI",   # Inwit
    "GVS.MI",   # GVS
    "SOL.MI",   # Sol
    "MARR.MI",  # Marr
    "FNM.MI",   # FNM
    "SAVE.MI",  # Save
    "IGD.MI",   # IGD
    "CIR.MI",   # CIR
    "TOD.MI",   # Tod's
    "ALERION.MI",# Alerion
    "SFL.MI",   # Salvatore Ferragamo
]
MILAN_TICKERS = list(dict.fromkeys(MILAN_TICKERS))

MONTHS_IT = {1:"Gen",2:"Feb",3:"Mar",4:"Apr",5:"Mag",6:"Giu",
             7:"Lug",8:"Ago",9:"Set",10:"Ott",11:"Nov",12:"Dic"}
MONTHS_FULL = {1:"Gennaio",2:"Febbraio",3:"Marzo",4:"Aprile",5:"Maggio",
               6:"Giugno",7:"Luglio",8:"Agosto",9:"Settembre",
               10:"Ottobre",11:"Novembre",12:"Dicembre"}

# ── Helpers ───────────────────────────────────────────────────────────────────
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(com=period-1, min_periods=period).mean()
    loss = (-delta.clip(upper=0)).ewm(com=period-1, min_periods=period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def compute_atr_pct(df, period=14):
    hi, lo, cl = df["High"], df["Low"], df["Close"]
    tr = pd.concat([(hi-lo), (hi-cl.shift()).abs(), (lo-cl.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(com=period-1, min_periods=period).mean()
    return (atr / cl) * 100

def mean_rev_stats(pct):
    streaks, count = [], 0
    for v in pct:
        if v < 0: count += 1
        elif v > 0 and count > 0: streaks.append(count); count = 0
        else: count = 0
    return {"avg": round(float(np.mean(streaks)), 2) if streaks else 0.0, "n": len(streaks)}

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def load_all(tickers):
    results = {}
    for ticker in tickers:
        try:
            raw = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
            if raw.empty or len(raw) < 30: continue
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            raw = raw[["Open","High","Low","Close","Volume"]].dropna()
            if raw["Volume"].mean() < 500_000: continue
            raw["pct"] = raw["Close"].pct_change() * 100
            raw["RSI"] = compute_rsi(raw["Close"])
            raw["ATR_pct"] = compute_atr_pct(raw)
            results[ticker] = raw
        except Exception:
            continue
    return results

def build_summary(data):
    rows = []
    for ticker, df in data.items():
        if df.empty: continue
        last = df.iloc[-1]
        stats = mean_rev_stats(df["pct"].dropna())
        rsi_val = float(last["RSI"]) if not np.isnan(last["RSI"]) else None
        atr_val = float(last["ATR_pct"]) if not np.isnan(last["ATR_pct"]) else None
        rows.append({
            "Ticker": ticker.replace(".MI",""),
            "Prezzo (€)": round(float(last["Close"]), 3),
            "Var % (1d)": round(float(last["pct"]), 2),
            "RSI (14)": round(rsi_val, 1) if rsi_val else None,
            "ATR % (14)": round(atr_val, 2) if atr_val else None,
            "Vol. Medio (M)": round(df["Volume"].mean()/1e6, 2),
            "Avg Streak Neg.": stats["avg"],
            "N° Inversioni": stats["n"],
            "_ticker_full": ticker,
        })
    return pd.DataFrame(rows).sort_values("Var % (1d)", ascending=False).reset_index(drop=True)

# ── Calendar HTML builder ─────────────────────────────────────────────────────
def build_calendar_html(df: pd.DataFrame) -> str:
    """
    Per ogni mese: una riga con colonne = giorni 1..31.
    Celle: freccia + % se giorno presente, vuoto altrimenti.
    """
    pct = df["pct"].dropna()
    pct.index = pd.to_datetime(pct.index)

    # Collect all days present — keyed by (year, month, day)
    day_data = {}  # (year, month, day) -> pct value
    for dt, val in pct.items():
        day_data[(dt.year, dt.month, dt.day)] = val

    # sorted unique (year, month) pairs
    ym_pairs = sorted(set((dt.year, dt.month) for dt in pct.index))
    last_date = pct.index.max()

    # Header
    days_header = "".join(f"<th>{d}</th>" for d in range(1, 32))
    html = f"""
    <div class="cal-wrap">
    <table class="cal-table">
      <thead>
        <tr>
          <th style="text-align:left;padding-left:8px;">Mese</th>
          {days_header}
          <th>↑ Pos</th><th>↓ Neg</th><th>Avg%</th><th>Rend. Mese</th>
        </tr>
      </thead>
      <tbody>
    """

    # Pre-compute monthly close returns from Close prices
    close_series = df["Close"].copy()
    close_series.index = pd.to_datetime(close_series.index)

    for (year, month) in ym_pairs:
        month_pcts = [v for (y, m, d), v in day_data.items() if y == year and m == month]
        n_pos = sum(1 for v in month_pcts if v > 0)
        n_neg = sum(1 for v in month_pcts if v < 0)
        avg_m = float(np.mean(month_pcts)) if month_pcts else 0.0
        avg_cls = "stat-pos" if avg_m > 0 else "stat-neg"

        # True monthly return: (last close / first close of month - 1) * 100
        month_closes = close_series[(close_series.index.year == year) & (close_series.index.month == month)]
        if len(month_closes) >= 2:
            month_ret = (float(month_closes.iloc[-1]) / float(month_closes.iloc[0]) - 1) * 100
        elif len(month_closes) == 1:
            month_ret = 0.0
        else:
            month_ret = None
        ret_cls = "stat-pos" if (month_ret is not None and month_ret > 0) else "stat-neg"
        ret_str = f"{month_ret:+.2f}%" if month_ret is not None else "—"
        ret_arrow = "▲" if (month_ret is not None and month_ret > 0) else ("▼" if (month_ret is not None and month_ret < 0) else "")

        cells = ""
        for day in range(1, 32):
            val = day_data.get((year, month, day))
            if val is None:
                cells += '<td class="day-na">·</td>'
            elif val >= 0:
                cells += f'<td class="day-up">↑<br>{val:+.1f}%</td>'
            else:
                cells += f'<td class="day-dn">↓<br>{val:.1f}%</td>'

        html += f"""
        <tr>
          <td class="month-label">{MONTHS_FULL[month]} {year}</td>
          {cells}
          <td class="stat-cell stat-pos">{n_pos}</td>
          <td class="stat-cell stat-neg">{n_neg}</td>
          <td class="stat-cell {avg_cls}">{avg_m:+.2f}%</td>
          <td class="stat-cell {ret_cls}" style="font-weight:600;font-size:0.78rem;white-space:nowrap">{ret_arrow} {ret_str}</td>
        </tr>
        """

    html += "</tbody></table></div>"

    # ── MOBILE cards (same data, vertical layout) ──────────────────────────
    mobile = ""
    for (year, month) in ym_pairs:
        month_pcts = [v for (y, m, d), v in day_data.items() if y == year and m == month]
        n_pos = sum(1 for v in month_pcts if v > 0)
        n_neg = sum(1 for v in month_pcts if v < 0)
        month_closes = close_series[(close_series.index.year == year) & (close_series.index.month == month)]
        if len(month_closes) >= 2:
            month_ret = (float(month_closes.iloc[-1]) / float(month_closes.iloc[0]) - 1) * 100
        else:
            month_ret = 0.0
        ret_cls  = "stat-pos" if month_ret > 0 else "stat-neg"
        ret_arrow = "▲" if month_ret > 0 else "▼"
        ret_str  = f"{month_ret:+.2f}%"

        # days grid: all 31 slots
        day_cells = ""
        for day in range(1, 32):
            val = day_data.get((year, month, day))
            if val is None:
                day_cells += f'<div class="dc na"><span class="dn-num">{day}</span>·</div>'
            elif val >= 0:
                day_cells += f'<div class="dc up"><span class="dn-num">{day}</span>↑<br>{val:+.1f}%</div>'
            else:
                day_cells += f'<div class="dc dn"><span class="dn-num">{day}</span>↓<br>{val:.1f}%</div>'

        mobile += f"""
        <div class='month-card'>
          <div class='mch'>
            <span class='mch-title'>{MONTHS_FULL[month]} {year}</span>
            <span class='mch-ret {ret_cls}'>{ret_arrow} {ret_str}</span>
          </div>
          <div class='mcs'>
            <span>↑ Positivi: <b style='color:#3fb950'>{n_pos}</b></span>
            <span>↓ Negativi: <b style='color:#f85149'>{n_neg}</b></span>
          </div>
          <div class='dgrid'>{day_cells}</div>
        </div>"""

    return html, mobile

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="title-banner">
  <span class="title-badge">Live</span><span class="title-badge">FTSE MIB</span>
  <p class="title-main">📊 RevertMI · Mean Reversion Scanner</p>
  <p class="title-sub">Analisi inversioni giornaliere · RSI · ATR · Calendario storico · Ultimi 365 giorni</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Controlli")
    st.caption("Dati via yfinance · Vol min 500K · 365 gg")
    if st.button("🔄  Aggiorna Dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    rsi_min, rsi_max = st.slider("Filtro RSI", 0, 100, (0, 100))
    vol_min = st.slider("Vol. Medio min (M)", 0.5, 10.0, 0.5, step=0.1)
    st.divider()
    st.caption("© 2025 · RevertMI Analytics")

# Load
with st.spinner("⏳  Download dati FTSE MIB…"):
    data = load_all(MILAN_TICKERS)

if not data:
    st.error("Nessun dato disponibile.")
    st.stop()

summary = build_summary(data)
mask = (
    (summary["Vol. Medio (M)"] >= vol_min) &
    (summary["RSI (14)"].fillna(50).between(rsi_min, rsi_max))
)
sf = summary[mask].copy()

# KPI row
n_t = len(sf)
n_pos = (sf["Var % (1d)"] > 0).sum()
n_neg = (sf["Var % (1d)"] < 0).sum()
avg_rsi = sf["RSI (14)"].mean()

c1,c2,c3,c4 = st.columns(4)
for col, label, val, sub, cls in [
    (c1, "Titoli Attivi", str(n_t), f"Filtro: Vol >{vol_min}M", ""),
    (c2, "Titoli in Rialzo", f"▲ {n_pos}", f"{round(n_pos/max(n_t,1)*100,1)}% del totale", "pos"),
    (c3, "Titoli in Ribasso", f"▼ {n_neg}", f"{round(n_neg/max(n_t,1)*100,1)}% del totale", "neg"),
    (c4, "RSI Medio", f"{round(avg_rsi,1)}", "Ipercomprato" if avg_rsi>65 else "Ipervenduto" if avg_rsi<35 else "Neutro",
     "neg" if avg_rsi>65 else "pos" if avg_rsi<35 else "neu"),
]:
    with col:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value {cls}">{val}</div>
          <div style="font-size:0.75rem;color:#6e7f9a;margin-top:2px">{sub}</div>
        </div>""", unsafe_allow_html=True)

# Main table
st.markdown('<p class="section-header">◼ Tabella Principale · Tutti i Titoli</p>', unsafe_allow_html=True)

display_cols = ["Ticker","Prezzo (€)","Var % (1d)","RSI (14)","ATR % (14)","Vol. Medio (M)","Avg Streak Neg.","N° Inversioni"]
df_show = sf[display_cols].copy()

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
    .format({"Prezzo (€)":"{:.3f}","Var % (1d)":"{:+.2f}%","RSI (14)":"{:.1f}",
             "ATR % (14)":"{:.2f}%","Vol. Medio (M)":"{:.2f}M","Avg Streak Neg.":"{:.2f}"}, na_rep="—")
    .set_properties(**{"background-color":"#111520","color":"#c9d1d9",
                       "border-color":"#1e2535","font-family":"IBM Plex Mono","font-size":"13px"})
    .set_table_styles([{"selector":"th","props":[
        ("background-color","#0d0f14"),("color","#6e7f9a"),
        ("font-size","11px"),("letter-spacing","0.08em"),
        ("text-transform","uppercase"),("border-bottom","1px solid #1e2535"),
    ]},{"selector":"tr:hover td","props":[("background-color","#1a2030")]}])
)
st.dataframe(styled, use_container_width=True, height=400)

# ── Drill-down ────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">◼ Drill-Down · Calendario Giornaliero per Mese</p>', unsafe_allow_html=True)

ticker_labels = sorted([t.replace(".MI","") for t in data.keys()])
selected_label = st.selectbox("Seleziona un titolo", ticker_labels)
selected_full = selected_label + ".MI"

if selected_full in data:
    df_sel = data[selected_full].copy()
    last = df_sel.iloc[-1]
    mr = mean_rev_stats(df_sel["pct"].dropna())

    m1,m2,m3,m4,m5 = st.columns(5)
    for col, label, val, fmt, cls in [
        (m1,"Prezzo Attuale", float(last["Close"]), "€{:.3f}", ""),
        (m2,"Var % (1d)", float(last["pct"]), "{:+.2f}%", "pos" if last["pct"]>0 else "neg"),
        (m3,"RSI (14)", float(last["RSI"]), "{:.1f}", "neg" if last["RSI"]>70 else "pos" if last["RSI"]<30 else "neu"),
        (m4,"ATR % (14)", float(last["ATR_pct"]), "{:.2f}%", ""),
        (m5,"Avg Streak Neg.", mr["avg"], "{:.2f} gg", ""),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value {cls}">{fmt.format(val)}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown(f"### 📅 {selected_label} · Variazioni giornaliere ↑↓ per mese")
    st.caption("↑ verde = giorno positivo · ↓ rosso = giorno negativo · · = mercato chiuso")
    last_ts = df_sel.index.max()
    st.caption(f"📅 Ultimo dato disponibile: **{last_ts.strftime('%d/%m/%Y')}** · I dati di oggi vengono pubblicati dopo la chiusura di mercato (17:35 CET)")
    cal_html, mobile_html = build_calendar_html(df_sel)

    CSS = """
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap');
    * { box-sizing: border-box; }
    body { margin:0; padding:6px; background:#080a0f; color:#e2e8f0; font-family:'IBM Plex Mono',monospace; }
    /* DESKTOP */
    .cal-wrap { overflow-x: auto; }
    .cal-table { border-collapse:collapse; width:100%; font-size:0.74rem; }
    .cal-table th {
      background:#0d1117; color:#8b949e;
      font-size:0.62rem; letter-spacing:0.1em; font-weight:600;
      text-transform:uppercase; padding:7px 3px; text-align:center;
      border-bottom:2px solid #21262d; white-space:nowrap;
    }
    .cal-table td { padding:4px 2px; text-align:center; border-bottom:1px solid #161b22; min-width:36px; }
    .cal-table tr:hover td { background:#161b22; }
    .day-up { color:#3fb950; font-size:0.7rem; line-height:1.4; font-weight:500; }
    .day-dn { color:#f85149; font-size:0.7rem; line-height:1.4; font-weight:500; }
    .day-na { color:#30363d; font-size:0.7rem; }
    .month-label {
      color:#79c0ff; font-weight:600; text-align:left !important;
      padding-left:10px !important; white-space:nowrap; min-width:120px;
      font-size:0.78rem; letter-spacing:0.03em;
    }
    .stat-cell { color:#d0d7de; font-size:0.7rem; white-space:nowrap; font-weight:500; }
    .stat-pos { color:#3fb950; font-weight:600; } .stat-neg { color:#f85149; font-weight:600; }
    .mobile-cards { display:none; }
    /* MOBILE */
    @media (max-width:640px) {
      .cal-wrap { display:none; }
      .mobile-cards { display:block; }
      .month-card {
        background:#0d1117; border:1px solid #21262d; border-radius:12px;
        margin-bottom:12px; overflow:hidden;
      }
      .mch {
        display:flex; justify-content:space-between; align-items:center;
        padding:12px 16px; border-bottom:1px solid #21262d; background:#080a0f;
      }
      .mch-title { color:#79c0ff; font-weight:700; font-size:0.95rem; letter-spacing:0.02em; }
      .mch-ret { font-size:0.95rem; font-weight:700; }
      .mcs {
        display:flex; gap:16px; padding:8px 16px; border-bottom:1px solid #21262d;
        font-size:0.75rem; color:#8b949e; flex-wrap:wrap;
      }
      .mcs b { font-weight:600; }
      .dgrid { display:grid; grid-template-columns:repeat(7,1fr); gap:3px; padding:8px; }
      .dc { text-align:center; padding:5px 2px; border-radius:6px; font-size:0.64rem; line-height:1.4; font-weight:500; }
      .dc.up { background:#1a3a23; color:#4ade80; }
      .dc.dn { background:#3a1515; color:#fc8181; }
      .dc.na { color:#30363d; }
      .dn-num { font-size:0.56rem; color:#6e7f9a; display:block; margin-bottom:1px; }
    }
    """

    full_html = f"""<html><head><meta name='viewport' content='width=device-width,initial-scale=1'>
    <style>{CSS}</style></head>
    <body>{cal_html}<div class='mobile-cards'>{mobile_html}</div></body></html>"""
    components.html(full_html, height=560, scrolling=True)

else:
    st.warning("Dati non disponibili per il ticker selezionato.")

st.divider()
st.caption("⚠️ Scopo puramente educativo/informativo. Non costituisce consulenza finanziaria. Dati: Yahoo Finance.")
