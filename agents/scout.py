"""Scout agent — collecte les données boursières via yfinance (C1)."""
import yfinance as yf
from typing import TypedDict


TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "BRK-B", "JPM", "V",
    "JNJ", "WMT", "PG", "MA", "HD",
    "CVX", "MRK", "ABBV", "PEP", "KO"
]


class ScoutState(TypedDict):
    ticker: str
    price: float
    change_pct: float
    volume: int
    error: str


def collect(ticker: str) -> ScoutState:
    """Collecte les données du jour pour un ticker."""
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="2d")
        if hist.empty or len(hist) < 2:
            return {"ticker": ticker, "price": 0.0, "change_pct": 0.0, "volume": 0, "error": "no data"}
        today = hist.iloc[-1]
        yesterday = hist.iloc[-2]
        change_pct = ((today["Close"] - yesterday["Close"]) / yesterday["Close"]) * 100
        return {
            "ticker": ticker,
            "price": round(float(today["Close"]), 2),
            "change_pct": round(float(change_pct), 2),
            "volume": int(today["Volume"]),
            "error": ""
        }
    except Exception as e:
        return {"ticker": ticker, "price": 0.0, "change_pct": 0.0, "volume": 0, "error": str(e)}
