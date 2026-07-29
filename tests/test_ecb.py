from unittest.mock import patch, MagicMock

import pytest

from sources.ecb import fetch_taux_change


def _fausse_reponse(valeur=1.138, date="2026-07-29"):
    r = MagicMock()
    r.raise_for_status.return_value = None
    r.json.return_value = {
        "dataSets": [{"series": {"0:0:0:0:0": {"observations": {"0": [valeur, 0, 0, None, None]}}}}],
        "structure": {"dimensions": {"observation": [{"values": [{"id": date}]}]}},
    }
    return r


def test_retourne_devise_date_et_valeur():
    with patch("sources.ecb.httpx.get", return_value=_fausse_reponse()) as mock_get:
        r = fetch_taux_change("USD")

    assert r == {"devise": "USD", "date": "2026-07-29", "valeur": 1.138}
    mock_get.assert_called_once()


def test_devise_par_defaut_est_usd():
    with patch("sources.ecb.httpx.get", return_value=_fausse_reponse()):
        assert fetch_taux_change()["devise"] == "USD"


def test_autre_devise_construit_la_bonne_url():
    with patch("sources.ecb.httpx.get", return_value=_fausse_reponse()) as mock_get:
        fetch_taux_change("GBP")

    assert "D.GBP.EUR.SP00.A" in mock_get.call_args[0][0]


def test_structure_inattendue_leve_une_erreur_explicite():
    r = MagicMock()
    r.raise_for_status.return_value = None
    r.json.return_value = {"dataSets": [], "structure": {}}
    with patch("sources.ecb.httpx.get", return_value=r):
        with pytest.raises((KeyError, IndexError)):
            fetch_taux_change()
