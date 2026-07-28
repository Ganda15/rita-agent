"""Scout agent — collecte les données boursières via yfinance (C1)."""
import yfinance as yf
from typing import TypedDict

TICKERS = [
    "MC.PA",   # LVMH
    "OR.PA",   # L'Oréal
    "SAN.PA",  # Sanofi
    "AI.PA",   # Air Liquide
    "BNP.PA",  # BNP Paribas
    "TTE.PA",  # TotalEnergies
    "AIR.PA",  # Airbus
    "DG.PA",   # Vinci
    "SU.PA",   # Schneider Electric
    "CS.PA",   # AXA
]
# Liste PEA-éligible, 10 valeurs pour le MVP — complétée jusqu'à 20 en Q2 (SPEC v3, US-1).


class ScoutState(TypedDict):
    ticker: str
    price: float
    change_pct: float
    volume: int
    currency: str
    error: str


def collect(ticker: str) -> ScoutState:
    """Collecte les données du jour pour un ticker : prix, variation, volume, devise."""
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="2d")
        if hist.empty or len(hist) < 2:
            return {"ticker": ticker, "price": 0.0, "change_pct": 0.0, "volume": 0,
                     "currency": "", "error": "no data"}
        today = hist.iloc[-1]
        yesterday = hist.iloc[-2]
        change_pct = ((today["Close"] - yesterday["Close"]) / yesterday["Close"]) * 100
        return {
            "ticker": ticker,
            "price": round(float(today["Close"]), 2),
            "change_pct": round(float(change_pct), 2),
            "volume": int(today["Volume"]),
            "currency": data.info.get("currency", "EUR"),
            "error": "",
        }
    except Exception as e:
        return {"ticker": ticker, "price": 0.0, "change_pct": 0.0, "volume": 0,
                 "currency": "", "error": str(e)}
