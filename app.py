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
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
  html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; background-color: #0d0f14; color: #c9d1d9; }
  .stApp { background-color: #0d0f14; }
  section[data-testid="stSidebar"] { background-color: #111520; border-right: 1px solid #1e2535; }
  .metric-card { background: #111520; border: 1px solid #1e2535; border-radius: 8px; padding: 14px 18px; margin-bottom: 10px; }
  .metric-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; letter-spacing: 0.12em; text-transform: uppercase; color: #6e7f9a; margin-bottom: 4px; }
  .metric-value { font-family: 'IBM Plex Mono', monospace; font-size: 1.4rem; font-weight: 600; color: #e6edf3; }
  .pos { color: #3fb950; } .neg { color: #f85149; } .neu { color: #d29922; }
  .section-header { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; letter-spacing: 0.18em; text-transform: uppercase; color: #3fb950; border-bottom: 1px solid #1e2535; padding-bottom: 8px; margin-bottom: 20px; margin-top: 28px; }
  .title-banner { background: linear-gradient(135deg, #0d0f14 0%, #111d2c 100%); border: 1px solid #1e2535; border-radius: 10px; padding: 24px 28px; margin-bottom: 24px; position: relative; overflow: hidden; }
  .title-banner::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #1f6feb, #3fb950, #1f6feb); }
  .title-main { font-family: 'IBM Plex Mono', monospace; font-size: 1.6rem; font-weight: 600; color: #e6edf3; margin: 0; }
  .title-sub { font-size: 0.88rem; color: #6e7f9a; margin-top: 6px; }
  .title-badge { display: inline-block; background: #1f3a5f; border: 1px solid #1f6feb; border-radius: 4px; padding: 2px 8px; font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; letter-spacing: 0.1em; color: #79c0ff; text-transform: uppercase; margin-right: 6px; }

  /* Calendar grid */
  .cal-wrap { overflow-x: auto; }
  .cal-table { border-collapse: collapse; width: 100%; font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; }
  .cal-table th { background: #0d0f14; color: #6e7f9a; font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; padding: 6px 4px; text-align: center; border-bottom: 1px solid #1e2535; white-space: nowrap; }
  .cal-table td { padding: 3px 2px; text-align: center; border-bottom: 1px solid #1a1f2e; min-width: 38px; }
  .cal-table tr:hover td { background: #141922; }
  .day-up { color: #3fb950; font-size: 0.72rem; line-height: 1.3; }
  .day-dn { color: #f85149; font-size: 0.72rem; line-height: 1.3; }
  .day-na { color: #3a4558; font-size: 0.72rem; }
  .month-label { color: #79c0ff; font-weight: 600; text-align: left !important; padding-left: 8px !important; white-space: nowrap; }
  .stat-cell { color: #c9d1d9; font-size: 0.7rem; }
  .stat-pos { color: #3fb950; } .stat-neg { color: #f85149; }
</style>
""", unsafe_allow_html=True)

# ── FTSE MIB completo + extra liquid mid-caps ────────────────────────────────
MILAN_TICKERS = [
    "A2A.MI","AMP.MI","ATL.MI","AZM.MI","BAMI.MI","BMPS.MI","BPER.MI",
    "BZU.MI","CNHI.MI","CPR.MI","DIA.MI","ENEL.MI","ENI.MI","ERG.MI",
    "FBK.MI","G.MI","GVS.MI","HER.MI","INW.MI","INWIT.MI","IPG.MI",
    "IREN.MI","ISP.MI","IVG.MI","LDO.MI","MB.MI","MONC.MI","NEXI.MI",
    "PIRC.MI","POSTE.MI","PRY.MI","RACE.MI","REC.MI","RECORDATI.MI",
    "SFER.MI","SRG.MI","STM.MI","TEN.MI","TIT.MI","TRN.MI","UCG.MI",
    "UNI.MI","AMPLIFON.MI","DIASORIN.MI","INTERPUMP.MI","ITALGAS.MI",
    "MEDIOBANCA.MI","MONCLER.MI","BRUNELLO.MI","WEBUILD.MI","FNM.MI",
    "SOL.MI","SAES.MI","MARR.MI","IGD.MI","CIR.MI","SFL.MI","SAVE.MI",
    "OVIND.MI","PIA.MI","TLNT.MI","TOD.MI","ALERION.MI","TERNA.MI",
    "AZIMUT.MI","FCA.MI","SIEM.MI","BRE.MI","FILA.MI","SOS.MI",
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
          <th>↑ Pos</th><th>↓ Neg</th><th>Avg%</th>
        </tr>
      </thead>
      <tbody>
    """

    for (year, month) in ym_pairs:
        month_pcts = [v for (y, m, d), v in day_data.items() if y == year and m == month]
        n_pos = sum(1 for v in month_pcts if v > 0)
        n_neg = sum(1 for v in month_pcts if v < 0)
        avg_m = float(np.mean(month_pcts)) if month_pcts else 0.0
        avg_cls = "stat-pos" if avg_m > 0 else "stat-neg"

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
        </tr>
        """

    html += "</tbody></table></div>"
    return html

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
    cal_html = build_calendar_html(df_sel)
    full_html = f"""
    <html><head>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap');
    body {{ margin:0; padding:0; background:#0d0f14; color:#c9d1d9; font-family:'IBM Plex Mono',monospace; }}
    .cal-wrap {{ overflow-x: auto; padding: 4px; }}
    .cal-table {{ border-collapse: collapse; width: 100%; font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; }}
    .cal-table th {{ background: #0d0f14; color: #6e7f9a; font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; padding: 6px 4px; text-align: center; border-bottom: 1px solid #1e2535; white-space: nowrap; }}
    .cal-table td {{ padding: 3px 2px; text-align: center; border-bottom: 1px solid #1a1f2e; min-width: 38px; }}
    .cal-table tr:hover td {{ background: #141922; }}
    .day-up {{ color: #3fb950; font-size: 0.72rem; line-height: 1.3; }}
    .day-dn {{ color: #f85149; font-size: 0.72rem; line-height: 1.3; }}
    .day-na {{ color: #3a4558; font-size: 0.72rem; }}
    .month-label {{ color: #79c0ff; font-weight: 600; text-align: left !important; padding-left: 8px !important; white-space: nowrap; }}
    .stat-cell {{ color: #c9d1d9; font-size: 0.7rem; }}
    .stat-pos {{ color: #3fb950; }} .stat-neg {{ color: #f85149; }}
    </style></head>
    <body>{cal_html}</body></html>
    """
    components.html(full_html, height=520, scrolling=True)

else:
    st.warning("Dati non disponibili per il ticker selezionato.")

st.divider()
st.caption("⚠️ Scopo puramente educativo/informativo. Non costituisce consulenza finanziaria. Dati: Yahoo Finance.")
