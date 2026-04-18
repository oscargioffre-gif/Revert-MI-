# 📊 BorsaITA · Mean Reversion Scanner

Applicazione Streamlit per l'analisi dei titoli di **Borsa Italiana (Milano)** con focus su pattern di inversione statistica.

## 🚀 Features

| Feature | Dettaglio |
|---|---|
| **Data sourcing** | `yfinance` · ultimi 365 giorni · refresh live |
| **Filtro universo** | Solo titoli `.MI` con Volume Medio > 500K |
| **RSI (14)** | Con colorazione ipercomprato/ipervenduto |
| **ATR % (14)** | `(ATR / Prezzo) × 100` |
| **Mean Reversion** | Avg streak negativa prima di un rimbalzo |
| **Drill-down mensile** | Insight testuali per ogni mese Gen–Dic |
| **Grafici** | Candlestick + Volume + RSI + ATR (Plotly) |

## 🛠 Installazione locale

```bash
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Deploy su Streamlit Cloud

1. Fai fork / push del repository su GitHub
2. Vai su [share.streamlit.io](https://share.streamlit.io)
3. Connetti il repo → seleziona `app.py`
4. Deploy!

Ogni `git push` aggiornerà automaticamente l'app.

## 📂 Struttura

```
├── app.py            # App principale
├── requirements.txt  # Dipendenze Python
└── README.md
```

## ⚠️ Disclaimer

Strumento a scopo puramente **educativo/informativo**. Non costituisce consulenza finanziaria. Dati forniti da Yahoo Finance tramite `yfinance`.
