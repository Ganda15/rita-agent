from unittest.mock import patch, MagicMock
import pandas as pd
from agents.scout import collect, TICKERS


def test_collect_returns_expected_fields_on_success():
    fake_hist = pd.DataFrame({"Close": [95.0, 97.5], "Volume": [1000, 1200]})
    with patch("agents.scout.yf.Ticker") as mock_ticker:
        instance = MagicMock()
        instance.history.return_value = fake_hist
        instance.info = {"currency": "EUR"}
        mock_ticker.return_value = instance

        resultat = collect("MC.PA")

    assert resultat["ticker"] == "MC.PA"
    assert resultat["price"] == 97.5
    assert resultat["currency"] == "EUR"
    assert resultat["error"] == ""


def test_collect_handles_empty_history():
    with patch("agents.scout.yf.Ticker") as mock_ticker:
        instance = MagicMock()
        instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = instance

        resultat = collect("XXX.PA")

    assert resultat["error"] == "no data"


def test_tickers_are_european_pea_eligible():
    assert all(ticker.endswith(".PA") for ticker in TICKERS)
    assert "MC.PA" in TICKERS
