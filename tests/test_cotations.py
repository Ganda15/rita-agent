"""Tests du rafraîchissement quotidien des cotations — aucun appel réseau réel.

`yfinance.download` est remplacé par un double. Les tests doivent tourner sans internet
et sans dépendre de l'état du marché un jour donné.
"""
from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from sources.cotations import fetch_cotations


def _fausse_reponse(index, valeurs: dict) -> pd.DataFrame:
    """Reproduit la forme réelle de yfinance : colonnes imbriquées (ticker, champ)."""
    cadres = {}
    for ticker, lignes in valeurs.items():
        for champ, serie in lignes.items():
            cadres[(ticker, champ)] = serie
    return pd.DataFrame(cadres, index=pd.DatetimeIndex(index))


UNE_SEANCE = ["2026-07-30"]


def test_retourne_le_contrat_attendu():
    rep = _fausse_reponse(UNE_SEANCE, {
        "MC.PA": {"Open": [467.3], "High": [474.0], "Low": [466.0],
                  "Close": [473.3], "Volume": [538828]},
        "OR.PA": {"Open": [381.3], "High": [395.0], "Low": [380.0],
                  "Close": [394.0], "Volume": [569573]},
    })
    with patch("yfinance.download", return_value=rep):
        r = fetch_cotations(["MC.PA", "OR.PA"], date(2026, 7, 30))

    assert len(r) == 2
    assert r[0] == {"ticker": "MC.PA", "date_seance": date(2026, 7, 30),
                    "ouverture": 467.3, "haut": 474.0, "bas": 466.0,
                    "cloture": 473.3, "volume": 538828}


def test_la_date_est_un_date_pas_un_horodatage():
    """La colonne `cotation.date_seance` est un DATE : un Timestamp la ferait échouer."""
    rep = _fausse_reponse(UNE_SEANCE, {"MC.PA": {
        "Open": [1.0], "High": [2.0], "Low": [0.5], "Close": [1.5], "Volume": [10]}})
    with patch("yfinance.download", return_value=rep):
        r = fetch_cotations(["MC.PA", "OR.PA"], date(2026, 7, 30))

    assert isinstance(r[0]["date_seance"], date)
    assert not hasattr(r[0]["date_seance"], "hour")


def test_les_cours_sont_demandes_AJUSTES(monkeypatch):
    """L'archive est en cours ajustés. Demander des cours bruts créerait une cassure
    de 22 % dans la série — mesuré sur MC.PA au 2016-08-01."""
    appel = MagicMock(return_value=_fausse_reponse(UNE_SEANCE, {"MC.PA": {
        "Open": [1.0], "High": [2.0], "Low": [0.5], "Close": [1.5], "Volume": [10]}}))
    with patch("yfinance.download", appel):
        fetch_cotations(["MC.PA", "OR.PA"], date(2026, 7, 30))

    assert appel.call_args.kwargs["auto_adjust"] is True


def test_la_borne_de_fin_inclut_aujourd_hui():
    """yfinance exclut la borne de fin : sans +1 jour, la séance du jour manque."""
    appel = MagicMock(return_value=_fausse_reponse(UNE_SEANCE, {"MC.PA": {
        "Open": [1.0], "High": [2.0], "Low": [0.5], "Close": [1.5], "Volume": [10]}}))
    with patch("yfinance.download", appel):
        fetch_cotations(["MC.PA", "OR.PA"], date(2026, 7, 30))

    assert appel.call_args.kwargs["end"] > date.today().isoformat()


def test_une_ligne_incoherente_est_ecartee():
    """haut < bas violerait la contrainte `bornes_coherentes` et ferait échouer le lot."""
    rep = _fausse_reponse(["2026-07-29", "2026-07-30"], {"MC.PA": {
        "Open": [1.0, 1.0], "High": [0.5, 2.0], "Low": [2.0, 0.5],   # 1re ligne : haut < bas
        "Close": [1.5, 1.5], "Volume": [10, 10]}})
    with patch("yfinance.download", return_value=rep):
        r = fetch_cotations(["MC.PA", "OR.PA"], date(2026, 7, 29))

    assert len(r) == 1
    assert r[0]["date_seance"] == date(2026, 7, 30)


def test_un_cours_nul_est_ecarte():
    """`prix_positifs` exige cloture > 0 ET ouverture > 0."""
    rep = _fausse_reponse(UNE_SEANCE, {"MC.PA": {
        "Open": [0.0], "High": [2.0], "Low": [0.5], "Close": [1.5], "Volume": [10]}})
    with patch("yfinance.download", return_value=rep):
        assert fetch_cotations(["MC.PA", "OR.PA"], date(2026, 7, 30)) == []


def test_une_valeur_manquante_est_ecartee():
    """Un jour férié renvoie NaN. `float('nan')` passerait le NOT NULL et fausserait tout."""
    rep = _fausse_reponse(UNE_SEANCE, {"MC.PA": {
        "Open": [float("nan")], "High": [2.0], "Low": [0.5],
        "Close": [1.5], "Volume": [10]}})
    with patch("yfinance.download", return_value=rep):
        assert fetch_cotations(["MC.PA", "OR.PA"], date(2026, 7, 30)) == []


def test_une_valeur_radiee_rend_None_et_ne_fait_pas_planter_le_groupe():
    """Une valeur RADIÉE rend `None`, pas `NaN` — et `None == None` est vrai.

    Le garde-fou `x == x` attrapait donc le NaN mais laissait passer le None, et
    la comparaison `c > 0` levait `TypeError`. Mesuré le 18/08/2026 sur ZC.PA
    (Zodiac Aerospace, radiée en 2018).

    La gravité n'est pas la ligne perdue : `etape_cotations` regroupe les tickers
    par date de dernière séance et attrape l'exception **par groupe**. Un seul
    ticker radié faisait donc perdre TOUT son groupe.
    """
    rep = _fausse_reponse(UNE_SEANCE, {"MC.PA": {
        "Open": [None], "High": [None], "Low": [None],
        "Close": [None], "Volume": [None]}})
    with patch("yfinance.download", return_value=rep):
        assert fetch_cotations(["MC.PA", "OR.PA"], date(2026, 7, 30)) == []


def test_un_seul_None_suffit_a_ecarter_la_ligne():
    """Une séance partiellement renseignée n'est pas rattrapable : la base impose
    NOT NULL sur les cinq colonnes."""
    rep = _fausse_reponse(UNE_SEANCE, {"MC.PA": {
        "Open": [1.0], "High": [2.0], "Low": [0.5],
        "Close": [None], "Volume": [10]}})
    with patch("yfinance.download", return_value=rep):
        assert fetch_cotations(["MC.PA", "OR.PA"], date(2026, 7, 30)) == []


def test_un_ticker_absent_de_la_reponse_ne_plante_pas():
    """yfinance omet silencieusement un ticker inconnu — ce n'est pas une raison
    pour perdre les autres."""
    rep = _fausse_reponse(UNE_SEANCE, {"MC.PA": {
        "Open": [1.0], "High": [2.0], "Low": [0.5], "Close": [1.5], "Volume": [10]}})
    with patch("yfinance.download", return_value=rep):
        r = fetch_cotations(["MC.PA", "TICKER.INEXISTANT"], date(2026, 7, 30))

    assert [l["ticker"] for l in r] == ["MC.PA"]


def test_reponse_vide_retourne_liste_vide():
    """Un week-end ne renvoie aucune séance. Ce n'est pas une erreur."""
    with patch("yfinance.download", return_value=pd.DataFrame()):
        assert fetch_cotations(["MC.PA", "OR.PA"], date(2026, 8, 1)) == []


def test_sans_ticker_erreur_explicite():
    with pytest.raises(ValueError, match="Aucun ticker"):
        fetch_cotations([], date(2026, 7, 30))


# --- 27/09/2026 : issues #50 et #47 --------------------------------------------
# Tous les tests ci-dessus demandent DEUX tickers. Le cas d'un ticker seul n'était pas
# couvert, et c'est lui qui a figé HSBA.L un mois : yfinance imbrique aussi les colonnes
# pour un seul ticker, et le code les lisait à plat, donc écartait chaque ligne.

def test_un_ticker_seul_est_lu_malgre_les_colonnes_imbriquees():
    rep = _fausse_reponse(UNE_SEANCE, {"HSBA.L": {
        "Open": [1515.4], "High": [1524.0], "Low": [1507.6],
        "Close": [1512.2], "Volume": [10200809]}})
    with patch("yfinance.download", return_value=rep):
        r = fetch_cotations(["HSBA.L"], date(2026, 7, 30))

    assert len(r) == 1


def test_les_pence_de_londres_sont_convertis_en_livres():
    """Yahoo cote Londres en pence : 1 512,2 pence = 15,122 livres."""
    rep = _fausse_reponse(UNE_SEANCE, {"HSBA.L": {
        "Open": [1515.4], "High": [1524.0], "Low": [1507.6],
        "Close": [1512.2], "Volume": [10200809]}})
    with patch("yfinance.download", return_value=rep):
        r = fetch_cotations(["HSBA.L"], date(2026, 7, 30))

    assert r[0]["cloture"] == pytest.approx(15.122)
    assert r[0]["ouverture"] == pytest.approx(15.154)
    assert r[0]["volume"] == 10200809          # un nombre de titres, pas un prix


def test_un_ticker_seul_non_imbrique_reste_lu():
    """Si une future version de yfinance revenait aux colonnes à plat, rien ne casse."""
    rep = pd.DataFrame({"Open": [100.0], "High": [101.0], "Low": [99.0],
                        "Close": [100.5], "Volume": [1000]},
                       index=pd.DatetimeIndex(UNE_SEANCE))
    with patch("yfinance.download", return_value=rep):
        assert len(fetch_cotations(["MC.PA"], date(2026, 7, 30))) == 1
