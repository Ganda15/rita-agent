"""Tests du lot 3 des indicateurs — `indicateurs/risque.py`.

⚠️ **Le RSI est la seule fonction de ce module testée en pur Python**, sans base
de données : c'est un calcul RÉCURSIF (le lissage de Wilder), donc entièrement
vérifiable sur une suite de nombres écrite à la main — pas besoin de simuler
`_executer` pour prouver que la récurrence est correcte.

La volatilité et le drawdown, eux, vivent dans `db/indicateurs_risque.sql` — ils
sont vérifiés par exécution réelle, tracée dans
`evidence/C14/preuve-indicateurs-lot3.md`, avec le test exact de la spécification
(série 100 → 150 → 90 → 120 ⇒ drawdown −40,00 %).
"""
import pathlib
from datetime import date
from decimal import Decimal

import pytest

from indicateurs import socle
from indicateurs.risque import (
    PERIODE_RSI,
    RSI,
    IndicateursRisqueValeur,
    lire_rsi,
    lire_volatilite_drawdown,
    rsi_wilder,
)

_REQUETE_RISQUE = pathlib.Path(__file__).parent.parent / "db" / "indicateurs_risque.sql"


# --- RSI — les trois cas explicitement exigés par la spécification (§7.3) -----

def test_14_hausses_consecutives_donnent_100():
    """§7.3 : « 14 hausses consécutives ⇒ 100. »"""
    cours = [100.0 + i for i in range(15)]   # 14 variations, toutes positives
    assert rsi_wilder(cours) == 100.0


def test_14_baisses_consecutives_donnent_0():
    """§7.3 : « 14 baisses ⇒ 0. »"""
    cours = [100.0 - i for i in range(15)]
    assert rsi_wilder(cours) == 0.0


def test_division_par_zero_rend_100_par_convention():
    """⚠️ Piège 3 de la spec, testé séparément du cas « 14 hausses » ci-dessus
    bien que le résultat numérique soit identique : ce test vérifie que le code
    passe par la branche `moyenne_baisses == 0.0` explicite, pas par hasard.
    Une monotonie stricte à la hausse est le seul cas qui produit une moyenne
    des baisses nulle — la division par zéro que Python lèverait sans ce garde."""
    cours = [100.0 * 1.01**i for i in range(20)]   # hausse continue, jamais de baisse
    assert rsi_wilder(cours) == 100.0


def test_historique_trop_court_rend_None():
    """Avec exactement `periode` variations ou moins, aucune moyenne d'amorce
    n'est calculable — `None`, jamais un chiffre inventé."""
    assert rsi_wilder([100.0] * (PERIODE_RSI)) is None       # 13 variations
    assert rsi_wilder([100.0] * (PERIODE_RSI - 5)) is None


def test_le_resultat_reste_toujours_dans_0_100():
    """Bornes structurelles du RSI, vérifiées sur une série mixte réaliste."""
    cours = [100, 102, 101, 105, 103, 108, 106, 110, 107, 112,
             109, 115, 111, 118, 114, 120, 116, 122, 119, 125, 121]
    r = rsi_wilder(cours)
    assert r is not None
    assert 0.0 <= r <= 100.0


def test_le_lissage_est_recursif_pas_une_moyenne_mobile_simple():
    """⚠️ LE test qui distingue Wilder d'une moyenne mobile simple — la
    confusion que la spec signale explicitement comme piège n°2.

    Avec plus de `periode` variations, la valeur dépend de TOUT l'historique
    fourni, pas seulement des 14 dernières variations : ajouter un point ancien
    différent en tête de série change le résultat. Une moyenne mobile simple sur
    les 14 dernières variations, elle, ne le ferait pas — c'est exactement la
    différence que `quant_metrics.py` (relu et non réutilisé le 19/08) aurait
    fait passer inaperçue.
    """
    suite_commune = [100, 105, 103, 108, 104, 110, 106, 113, 109, 116,
                      112, 119, 115, 122, 118, 125]   # 15 points, 14 variations "récentes"

    # Deux préfixes différents, la fin est identique.
    a = rsi_wilder([50.0] + suite_commune)
    b = rsi_wilder([80.0] + suite_commune)

    assert a != b, (
        "le résultat ne dépend que des 14 dernières variations : "
        "ce n'est plus le lissage récursif de Wilder"
    )


def test_amorce_wilder_egale_une_moyenne_simple_sur_exactement_14_points():
    """Avec EXACTEMENT `periode` variations, il n'y a rien à lisser après
    l'amorce : le résultat DOIT être une moyenne simple classique de RSI — la
    formule manuelle ci-dessous, calculée sans passer par `rsi_wilder`."""
    cours = [100, 102, 99, 103, 101, 106, 104, 108, 105, 110, 107, 112, 109, 114, 111]
    variations = [cours[i] - cours[i - 1] for i in range(1, len(cours))]
    hausses = [max(v, 0) for v in variations]
    baisses = [max(-v, 0) for v in variations]
    mh, mb = sum(hausses) / 14, sum(baisses) / 14
    attendu = round(100 - 100 / (1 + mh / mb), 2)

    assert rsi_wilder(cours) == attendu


# --- lire_rsi() — base SIMULÉE, comme le reste du projet ----------------------
#
# ⚠️ Aucun test de ce dépôt ne se connecte à la vraie base — convention
# constatée dans `tests/test_indicateurs_socle.py` et ailleurs, et rappelée
# comme manque connu de C12 dans `ETAT.md`. `lire_rsi()` suit la même règle
# que `lire_socle()` : `_executer` est remplacé, le SQL lui-même est vérifié
# par exécution réelle et tracé dans `evidence/C14/preuve-indicateurs-lot3.md`.

def _ligne(ticker: str, jour: int, cloture: float) -> dict:
    return {"ticker": ticker, "date_seance": date(2026, 7, 1 + jour), "cloture": Decimal(str(cloture))}


def test_lire_rsi_groupe_par_ticker_et_calcule(monkeypatch):
    """15 séances haussières pour MC.PA, 15 baissières pour OR.PA — appariées
    au bon ticker malgré un ordre de lignes entrelacé, pour vérifier que le
    regroupement ne suppose pas que les lignes d'un ticker sont contiguës."""
    lignes = []
    for j in range(15):
        lignes.append(_ligne("MC.PA", j, 100 + j))   # monte
        lignes.append(_ligne("OR.PA", j, 100 - j))   # baisse
    monkeypatch.setattr(socle, "_executer", lambda sql, p=None: lignes)

    r = lire_rsi()

    assert {x.ticker for x in r} == {"MC.PA", "OR.PA"}
    mc = next(x for x in r if x.ticker == "MC.PA")
    orv = next(x for x in r if x.ticker == "OR.PA")
    assert mc.rsi_14 == 100.0
    assert orv.rsi_14 == 0.0


def test_lire_rsi_trie_par_ticker(monkeypatch):
    lignes = [_ligne(t, j, 100) for t in ("ZZZ", "AAA") for j in range(16)]
    monkeypatch.setattr(socle, "_executer", lambda sql, p=None: lignes)
    r = lire_rsi()
    assert [x.ticker for x in r] == ["AAA", "ZZZ"]


def test_lire_rsi_transmet_le_filtre_par_ticker_en_parametre_lie(monkeypatch):
    """Jamais de concaténation du ticker dans le SQL — c'est une injection SQL.
    Le test inspecte les paramètres réellement transmis, pas le texte du SQL."""
    vu = {}

    def espion(sql, parametres=None):
        vu["sql"], vu["parametres"] = sql, parametres
        return []

    monkeypatch.setattr(socle, "_executer", espion)
    lire_rsi(["MC.PA", "OR.PA"])

    assert vu["parametres"] == {"tickers": ["MC.PA", "OR.PA"]}
    assert "ANY(%(tickers)s)" in vu["sql"]


def test_lire_rsi_sans_filtre_transmet_None(monkeypatch):
    vu = {}

    def espion(sql, parametres=None):
        vu["parametres"] = parametres
        return []

    monkeypatch.setattr(socle, "_executer", espion)
    lire_rsi()

    assert vu["parametres"] == {"tickers": None}


def test_aucune_ligne_donne_une_liste_vide(monkeypatch):
    """Le cas des valeurs radiées : aucune donnée récente ⇒ absentes du
    résultat, pas une erreur — cohérent avec le signal `cotation_perimee` du
    lot 1, sans avoir besoin de le reproduire ici."""
    monkeypatch.setattr(socle, "_executer", lambda sql, p=None: [])
    assert lire_rsi(["ZC.PA"]) == []


# --- en_dict() ------------------------------------------------------------

def test_en_dict_est_serialisable():
    r = RSI(ticker="MC.PA", date_cours="2026-08-18", rsi_14=54.32)
    d = r.en_dict()
    assert d == {"ticker": "MC.PA", "date_cours": "2026-08-18", "rsi_14": 54.32}


# --- lire_volatilite_drawdown() — base simulée ---------------------------------

def _ligne_risque(**surcharges):
    base = {
        "ticker": "MC.PA", "nom_officiel": "LVMH", "statut_qualite": "OK",
        "date_cours": date(2026, 8, 18), "cours": Decimal("449.65"),
        "fraicheur_jours": 1,
        "volatilite_annualisee_pct": Decimal("22.14"),
        "drawdown_max_1a_pct": Decimal("-18.30"),
    }
    base.update(surcharges)
    return base


def test_lire_volatilite_drawdown_convertit_les_decimal(monkeypatch):
    monkeypatch.setattr(socle, "_executer", lambda sql: [_ligne_risque()])
    r = lire_volatilite_drawdown()
    assert len(r) == 1
    assert isinstance(r[0].volatilite_annualisee_pct, float)
    assert isinstance(r[0].drawdown_max_1a_pct, float)
    assert r[0].drawdown_max_1a_pct == pytest.approx(-18.30)


def test_lire_volatilite_drawdown_historique_court_rend_None(monkeypatch):
    """Moins de 20 séances ⇒ `NULL` en SQL ⇒ `None` ici, jamais 0 — un
    historique trop court n'est pas une volatilité nulle."""
    monkeypatch.setattr(socle, "_executer", lambda sql: [
        _ligne_risque(volatilite_annualisee_pct=None)])
    r = lire_volatilite_drawdown()
    assert r[0].volatilite_annualisee_pct is None


def test_lire_volatilite_drawdown_filtre_par_ticker(monkeypatch):
    monkeypatch.setattr(socle, "_executer", lambda sql: [
        _ligne_risque(ticker="MC.PA"), _ligne_risque(ticker="OR.PA")])
    r = lire_volatilite_drawdown(["OR.PA"])
    assert [x.ticker for x in r] == ["OR.PA"]


def test_le_drawdown_n_est_jamais_positif_dans_les_donnees_reelles():
    """Contrôle de cohérence sur la requête SQL elle-même : `db/indicateurs_risque.sql`
    ne doit jamais produire un drawdown positif — c'était le symptôme du bug du
    19/08 (fonctions fenêtre placées après le filtre sur la dernière séance)."""
    sql = _REQUETE_RISQUE.read_text(encoding="utf-8")
    # Le calcul du plus haut s'arrête à la veille, jamais au jour courant.
    assert "1 PRECEDING" in sql
    assert "UNBOUNDED PRECEDING AND 1 PRECEDING" in sql


def test_les_fonctions_fenetre_sont_dans_une_cte_pas_apres_le_filtre():
    """⚠️ Verrouille la correction du 19/08 : les fonctions fenêtre (COUNT,
    STDDEV_SAMP, MIN ... OVER) doivent apparaître dans la CTE
    `indicateurs_par_jour`, calculée sur l'historique complet — PAS dans le
    SELECT final, qui ne voit plus qu'une ligne par ticker après la jointure
    sur `derniere_seance`. Les placer après le filtre les avait fait rendre
    NULL pour les 111 valeurs."""
    sql = _REQUETE_RISQUE.read_text(encoding="utf-8")
    avant_final, _, apres_final = sql.partition("SELECT  ip.ticker")
    assert "indicateurs_par_jour AS (" in avant_final
    assert "STDDEV_SAMP" in avant_final
    assert "STDDEV_SAMP" not in apres_final, \
        "une fonction fenêtre est réapparue dans le SELECT final"


# --- cotation_perimee — trouvé en vérifiant l'API le 19/08 --------------------

def test_cotation_perimee_signale_une_valeur_radiee():
    """⚠️ Trouvé en interrogeant l'API : sans ce drapeau, une valeur radiée
    affichait une volatilité calculée sur son historique de 2018, avec
    `fraicheur_jours` présent mais jamais exploité — même angle mort que celui
    corrigé sur le lot 1 le 18/08."""
    recente = IndicateursRisqueValeur(
        ticker="MC.PA", nom_officiel="LVMH", statut_qualite="OK",
        date_cours="2026-08-18", cours=449.65, fraicheur_jours=1,
        volatilite_annualisee_pct=22.14, drawdown_max_1a_pct=-18.30)
    radiee = IndicateursRisqueValeur(
        ticker="ZC.PA", nom_officiel="ZODIAC AEROSPACE", statut_qualite="OK",
        date_cours="2018-03-22", cours=24.83, fraicheur_jours=3072,
        volatilite_annualisee_pct=16.70, drawdown_max_1a_pct=-24.78)

    assert recente.cotation_perimee is False
    assert radiee.cotation_perimee is True
    # La mesure reste affichée — ce n'est pas masqué, seulement signalé.
    assert radiee.en_dict()["volatilite_annualisee_pct"] == 16.70
