"""Étape 1 — Récupérer le prix d'une action via yfinance."""

import yfinance as yf


def fetch_price(ticker: str) -> dict:
    """Récupère le dernier prix de clôture d'un ticker boursier.

    Args:
        ticker: Code boursier, ex. 'AAPL' pour Apple.

    Returns:
        dict avec ticker, prix de clôture, variation %, devise.
    """
    stock = yf.Ticker(ticker)
    history = stock.history(period="2d")

    if history.empty:
        raise ValueError(f"Aucune donnée trouvée pour {ticker}")

    last_close = float(history["Close"].iloc[-1])
    prev_close = float(history["Close"].iloc[-2])
    change_pct = ((last_close - prev_close) / prev_close) * 100

    return {
        "ticker": ticker,
        "price": round(last_close, 2),
        "change_pct": round(change_pct, 2),
        "currency": stock.info.get("currency", "USD"),
    }


if __name__ == "__main__":
    data = fetch_price("MC.PA")
    print(data)
