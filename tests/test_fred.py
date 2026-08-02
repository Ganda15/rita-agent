"""Tests de la source FRED — aucun appel réseau réel.

`httpx.get` est remplacé par un double. Les tests doivent tourner sans clé,
sans internet, et sans consommer le quota de l'API.

Les données factices reproduisent la **forme réelle** de la réponse, relevée
en direct le 2026-08-02 : valeurs en chaîne à 10 décimales, trous notés `"."`.
"""
from unittest.mock import MagicMock, patch

import pytest

from sources.fred import SERIES, CleFredAbsente, fetch_indicateur


def _fausse_reponse(observations: list[dict]) -> MagicMock:
    """Fabrique une réponse FRED factice, dans la forme réelle de l'API."""
    reponse = MagicMock()
    reponse.json.return_value = {"observations": observations}
    reponse.raise_for_status.return_value = None
    return reponse


def test_retourne_date_et_valeur(monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "cle-de-test")
    rep = _fausse_reponse([{"date": "2026-07-30", "value": "4.6800000000"}])
    with patch("sources.fred.httpx.get", return_value=rep) as appel:
        resultat = fetch_indicateur("DGS10")

    assert resultat == [{"date": "2026-07-30", "valeur": 4.68}]
    appel.assert_called_once()


def test_la_valeur_est_un_nombre_pas_une_chaine(monkeypatch):
    """FRED renvoie "4.6800000000" en texte. Sans conversion, toute moyenne planterait."""
    monkeypatch.setenv("FRED_API_KEY", "cle-de-test")
    rep = _fausse_reponse([{"date": "2026-07-30", "value": "4.6800000000"}])
    with patch("sources.fred.httpx.get", return_value=rep):
        assert isinstance(fetch_indicateur("DGS10")[0]["valeur"], float)


def test_ignore_les_observations_manquantes(monkeypatch):
    """Mesuré sur données réelles : 17 trous sur 400, tous des jours fériés US.
    Le 2026-07-03 ci-dessous en est un vrai."""
    monkeypatch.setenv("FRED_API_KEY", "cle-de-test")
    rep = _fausse_reponse([
        {"date": "2026-07-03", "value": "."},
        {"date": "2026-07-02", "value": "4.7000000000"},
    ])
    with patch("sources.fred.httpx.get", return_value=rep):
        resultat = fetch_indicateur("DGS10", limite=2)

    assert resultat == [{"date": "2026-07-02", "valeur": 4.70}]


def test_la_cle_ne_se_retrouve_jamais_dans_l_url(monkeypatch):
    """Une clé dans l'URL finit dans les journaux du serveur. Elle reste en paramètre."""
    monkeypatch.setenv("FRED_API_KEY", "cle-de-test")
    rep = _fausse_reponse([{"date": "2026-07-30", "value": "4.6800000000"}])
    with patch("sources.fred.httpx.get", return_value=rep) as appel:
        fetch_indicateur("DGS10")

    assert "cle-de-test" not in appel.call_args.args[0]
    assert appel.call_args.kwargs["params"]["api_key"] == "cle-de-test"


def test_la_plus_recente_est_demandee_en_premier(monkeypatch):
    """Sans sort_order=desc, limit=1 renverrait l'observation de 1962."""
    monkeypatch.setenv("FRED_API_KEY", "cle-de-test")
    rep = _fausse_reponse([{"date": "2026-07-30", "value": "4.6800000000"}])
    with patch("sources.fred.httpx.get", return_value=rep) as appel:
        fetch_indicateur("DGS10")

    assert appel.call_args.kwargs["params"]["sort_order"] == "desc"


def test_sans_cle_erreur_explicite(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    with pytest.raises(CleFredAbsente, match="FRED_API_KEY absente"):
        fetch_indicateur("DGS10")


def test_aucun_appel_reseau_sans_cle(monkeypatch):
    """L'erreur doit tomber AVANT la requête, pas après un aller-retour inutile."""
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    with patch("sources.fred.httpx.get") as appel:
        with pytest.raises(CleFredAbsente):
            fetch_indicateur("DGS10")

    appel.assert_not_called()


def test_une_cle_vide_est_traitee_comme_absente(monkeypatch):
    """Une ligne `FRED_API_KEY=` dans .env donne une chaîne vide, pas None."""
    monkeypatch.setenv("FRED_API_KEY", "   ")
    with pytest.raises(CleFredAbsente):
        fetch_indicateur("DGS10")


def test_les_series_retenues_sont_documentees():
    """Un code FRED seul ne dit rien : chaque série porte son libellé."""
    assert set(SERIES) == {"DGS10", "CPIAUCSL", "DFF"}
    assert all(SERIES.values())
