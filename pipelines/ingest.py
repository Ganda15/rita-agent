"""Pipeline d'ingestion — collecte 5 ans de données et sauvegarde en Parquet (C1 big data)."""
import yfinance as yf
import pandas as pd
from pathlib import Path

TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "BRK-B", "JPM", "V",
    "JNJ", "WMT", "PG", "MA", "HD",
    "CVX", "MRK", "ABBV", "PEP", "KO"
]

DATA_DIR = Path(__file__).parent.parent / "data"


def ingest_all():
    """Télécharge 5 ans de données OHLCV pour les 20 tickers et sauvegarde en Parquet."""
    DATA_DIR.mkdir(exist_ok=True)
    all_frames = []

    for ticker in TICKERS:
        print(f"Collecte {ticker}...")
        try:
            df = yf.download(ticker, period="5y", auto_adjust=True)
            df["ticker"] = ticker
            df = df.reset_index()
            all_frames.append(df)
        except Exception as e:
            print(f"Erreur {ticker} : {e}")

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        output = DATA_DIR / "ohlcv_5y.parquet"
        combined.to_parquet(output, index=False)
        print(f"Sauvegardé : {output} — {len(combined):,} lignes")
        return combined
    return pd.DataFrame()


if __name__ == "__main__":
    ingest_all()
