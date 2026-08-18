"""Tests du lot 1 des indicateurs — `indicateurs/socle.py`.

⚠️ **Limite connue de ces tests, dite d'emblée.** Ils vérifient la conversion des
lignes et les règles métier du module Python. Ils ne vérifient **pas** le SQL :
`_executer` est remplacé. C'est le même défaut que celui relevé le 17/08 sur toute
la suite (`ETAT.md`, C12) — aucun test ne se connecte à la vraie base, et un défaut
de schéma est resté invisible pendant des semaines à cause de cela.

Le SQL est vérifié par **exécution réelle**, tracée dans
`evidence/C14/preuve-indicateurs-lot1.md`. Les deux vérifications sont
complémentaires, aucune ne remplace l'autre.
"""
from datetime import date
from decimal import Decimal

import pytest

from indicateurs import socle
from indicateurs.socle import (
    SEUIL_PERIME_JOURS,
    IndicateursValeur,
    construire,
    lire_socle,
)


def ligne(**surcharges):
    """Une ligne telle que la requête la rend. Les NUMERIC arrivent en Decimal."""
    base = {
        "ticker": "MC.PA",
        "nom_officiel": "LVMH",
        "statut_qualite": "OK",
        "date_cours": date(2026, 7, 28),
        "cours": Decimal("545.2000"),
        "fraicheur_jours": 21,
        "perf_1j_pct": Decimal("-1.10"),
        "perf_1s_pct": Decimal("2.40"),
        "perf_1m_pct": Decimal("-3.80"),
        "perf_ytd_pct": Decimal("5.20"),
        "perf_1a_pct": Decimal("-11.10"),
        "ma20": Decimal("552.3000"),
        "ma50": Decimal("561.9000"),
        "adtv20": Decimal("128456789"),
        "distance_plus_haut_1a_pct": Decimal("-14.20"),
    }
    base.update(surcharges)
    return base


# --- conversion ---------------------------------------------------------------

def test_les_decimal_deviennent_des_float():
    """PostgreSQL rend du NUMERIC. Laisser des Decimal remonter jusqu'à l'API
    obligerait chaque appelant à s'en méfier — on normalise une fois, ici."""
    i = construire(ligne())
    for champ in ("cours", "perf_1j_pct", "ma20", "adtv20"):
        assert isinstance(getattr(i, champ), float), champ
    assert i.cours == pytest.approx(545.20)


def test_un_historique_trop_court_rend_None_et_non_zero():
    """Une performance 1 an calculée sur 3 mois de données serait un chiffre
    inventé. La requête rend NULL ; le module doit rendre None, pas 0.0."""
    i = construire(ligne(perf_1a_pct=None, ma50=None))
    assert i.perf_1a_pct is None
    assert i.ma50 is None
    assert i.ma20 is not None      # les autres colonnes ne sont pas affectées


def test_la_date_reste_une_date():
    i = construire(ligne())
    assert i.date_cours == date(2026, 7, 28)


# --- règle métier : la fraîcheur ---------------------------------------------

def test_une_cotation_recente_n_est_pas_perimee():
    assert construire(ligne(fraicheur_jours=3)).cotation_perimee is False


def test_le_seuil_lui_meme_n_est_pas_perime():
    """Le seuil est une borne inclusive : 40 jours passe, 41 ne passe plus.
    Testé explicitement — c'est le genre de limite qui dérive silencieusement."""
    assert construire(ligne(fraicheur_jours=SEUIL_PERIME_JOURS)).cotation_perimee is False
    assert construire(ligne(fraicheur_jours=SEUIL_PERIME_JOURS + 1)).cotation_perimee is True


def test_une_valeur_radiee_est_signalee_meme_si_son_statut_est_OK():
    """LE test qui compte. Zodiac Aerospace est radiée depuis 2018 et porte
    toujours `statut_qualite = 'OK'` : le statut décrit la qualité de l'historique,
    pas sa fraîcheur. Sans ce signalement, l'écran afficherait une « performance
    1 jour » calculée sur des cours vieux de huit ans."""
    i = construire(ligne(
        ticker="ZC.PA", nom_officiel="ZODIAC AEROSPACE",
        statut_qualite="OK", date_cours=date(2018, 3, 22), fraicheur_jours=3071,
    ))
    assert i.statut_qualite == "OK"
    assert i.cotation_perimee is True


def test_le_dict_expose_la_peremption_et_une_date_serialisable():
    """L'API doit pouvoir renvoyer l'objet tel quel : une `date` Python n'est pas
    du JSON, et le drapeau de péremption doit voyager avec les chiffres."""
    d = construire(ligne(fraicheur_jours=3071)).en_dict()
    assert d["date_cours"] == "2026-07-28"
    assert d["cotation_perimee"] is True
    assert isinstance(d["cours"], float)


# --- lecture ------------------------------------------------------------------

def test_lire_socle_convertit_toutes_les_lignes(monkeypatch):
    monkeypatch.setattr(socle, "_executer",
                        lambda sql, p=None: [ligne(), ligne(ticker="OR.PA")])
    r = lire_socle()
    assert [i.ticker for i in r] == ["MC.PA", "OR.PA"]
    assert all(isinstance(i, IndicateursValeur) for i in r)


def test_le_filtre_par_ticker_passe_par_un_parametre_lie(monkeypatch):
    """Jamais de concaténation d'un ticker dans le SQL : ce serait une injection
    SQL. Le test inspecte la requête réellement envoyée."""
    vu = {}

    def espion(sql, parametres=None):
        vu["sql"], vu["parametres"] = sql, parametres
        return [ligne()]

    monkeypatch.setattr(socle, "_executer", espion)
    lire_socle(["MC.PA", "OR.PA"])

    assert vu["parametres"] == (["MC.PA", "OR.PA"],)
    assert "ANY(%s)" in vu["sql"]
    assert "MC.PA" not in vu["sql"]          # le ticker n'entre pas dans le texte


def test_sans_filtre_aucun_parametre_n_est_envoye(monkeypatch):
    """psycopg2 n'interpole que si le second argument n'est pas None. Avec un
    tuple vide il tenterait l'interpolation et échouerait sur le moindre « % »
    du SQL — y compris dans un commentaire. Défaut rencontré le 18/08."""
    vu = {}

    def espion(sql, parametres=None):
        vu["parametres"] = parametres
        return []

    monkeypatch.setattr(socle, "_executer", espion)
    lire_socle()
    assert vu["parametres"] is None


# --- le SQL existe et porte les garde-fous de conception ----------------------

def _code_sql_seul() -> str:
    """La requête, commentaires retirés.

    Indispensable : le fichier *explique* dans ses commentaires les pièges à
    éviter, et cite donc les tournures interdites. Chercher `LAG(` dans le texte
    brut ferait échouer le test sur la phrase qui dit de ne pas s'en servir.
    """
    lignes = []
    for l in socle._REQUETE.read_text(encoding="utf-8").splitlines():
        code = l.split("--", 1)[0]
        if code.strip():
            lignes.append(code)
    return "\n".join(lignes)


def test_la_requete_ne_fait_pas_de_decalage_en_nombre_de_lignes():
    """Piège n°1 de la spec : un `LAG(cloture, 5)` supposerait que toutes les
    valeurs cotent les mêmes jours. Elles ne le font pas — trois places, trois
    calendriers. Ce test verrouille le choix de conception."""
    sql = _code_sql_seul().upper()
    assert "LAG(" not in sql
    assert "LATERAL" in sql                  # la référence est « à ou avant la date cible »


def test_la_derniere_seance_est_calculee_par_ticker():
    """Un MAX(date_seance) global ne remontait que 2 valeurs sur 111 (10/08)."""
    assert "GROUP BY ticker" in _code_sql_seul()


def test_le_sql_ne_contient_aucun_pour_cent():
    """Un « % » dans le SQL — même en commentaire — casse `cur.execute` dès qu'un
    paramètre est passé. Constaté le 18/08 sur le filtre par ticker."""
    sql = socle._REQUETE.read_text(encoding="utf-8")
    assert "%s" not in sql, "le seul marqueur autorisé est inséré dynamiquement"
    assert "%" not in sql
