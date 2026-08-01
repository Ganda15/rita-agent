"""Tests de l'extraction SQL — connexion simulée, aucune base requise.

On ne teste pas PostgreSQL : on teste **notre code autour**. Que le SQL soit correct est
prouvé par l'exécution réelle documentée dans `evidence/C2/`. Ce que ces tests garantissent,
c'est que le module passe les bons paramètres, ferme sa connexion et rend des dictionnaires.
"""
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from sources import database

LIGNES_PORTEFEUILLE = [
    {"ticker": "MC.PA", "nom_officiel": "LVMH", "statut_qualite": "OK",
     "quantite": Decimal("12"), "pru": Decimal("632.40"), "devise": "EUR",
     "date_cours": "2026-07-28", "cours": Decimal("466.80"),
     "investi_eur": Decimal("7588.80"), "valorisation_eur": Decimal("5601.60"),
     "performance_pct": Decimal("-26.19")},
    {"ticker": "AAPL", "nom_officiel": "Apple", "statut_qualite": "OK",
     "quantite": Decimal("6"), "pru": Decimal("178.45"), "devise": "USD",
     "date_cours": "2026-07-29", "cours": Decimal("212.50"),
     "investi_eur": Decimal("940.86"), "valorisation_eur": Decimal("1120.39"),
     "performance_pct": Decimal("19.08")},
]


def _connexion(lignes: list[dict]) -> MagicMock:
    """Simule psycopg2.connect() utilisé comme gestionnaire de contexte."""
    curseur = MagicMock()
    curseur.fetchall.return_value = lignes
    curseur.__enter__ = MagicMock(return_value=curseur)
    curseur.__exit__ = MagicMock(return_value=False)

    conn = MagicMock()
    conn.cursor.return_value = curseur
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    conn._curseur = curseur          # accès pour les assertions
    return conn


# --- R1 portefeuille ----------------------------------------------------------

def test_portefeuille_retourne_des_dictionnaires():
    with patch("sources.database.psycopg2.connect",
               return_value=_connexion(LIGNES_PORTEFEUILLE)):
        e = database.portefeuille()

    assert e.nom == "portefeuille"
    assert e.nb == 2 and len(e) == 2
    assert e.lignes[0]["ticker"] == "MC.PA"
    assert isinstance(e.lignes[0], dict)


def test_total_portefeuille_additionne_les_valorisations():
    """Le total n'a de sens que parce que la requête a déjà converti en euros."""
    with patch("sources.database.psycopg2.connect",
               return_value=_connexion(LIGNES_PORTEFEUILLE)):
        e = database.portefeuille()

    assert database.total_portefeuille(e) == Decimal("6721.99")


def test_total_ignore_les_valorisations_absentes():
    """Une valeur suspendue de cotation a un cours NULL — elle ne doit pas casser le total."""
    lignes = LIGNES_PORTEFEUILLE + [{"valorisation_eur": None}]
    with patch("sources.database.psycopg2.connect", return_value=_connexion(lignes)):
        e = database.portefeuille()

    assert database.total_portefeuille(e) == Decimal("6721.99")


def test_portefeuille_sans_parametre_sql():
    """R1 n'a pas de paramètre : on ne doit pas passer un dict vide à execute()."""
    conn = _connexion([])
    with patch("sources.database.psycopg2.connect", return_value=conn):
        database.portefeuille()

    assert conn._curseur.execute.call_args.args[1] is None


# --- R2 mouvements ------------------------------------------------------------

def test_mouvements_passe_la_limite_en_parametre():
    """Paramètre lié, pas de f-string : c'est ce qui empêche l'injection SQL."""
    conn = _connexion([])
    with patch("sources.database.psycopg2.connect", return_value=conn):
        database.mouvements(limite=3)

    sql, params = conn._curseur.execute.call_args.args
    assert params == {"limite": 3}
    assert "%(limite)s" in sql          # marqueur, pas la valeur interpolée
    assert "LIMIT 3" not in sql


def test_mouvements_limite_par_defaut():
    conn = _connexion([])
    with patch("sources.database.psycopg2.connect", return_value=conn):
        database.mouvements()
    assert conn._curseur.execute.call_args.args[1] == {"limite": 5}


# --- R3 volumes ---------------------------------------------------------------

def test_volumes_passe_seuil_et_limite():
    conn = _connexion([])
    with patch("sources.database.psycopg2.connect", return_value=conn):
        database.volumes_anormaux(seuil=3.5, limite=20)

    assert conn._curseur.execute.call_args.args[1] == {"seuil": 3.5, "limite": 20}


def test_volumes_valeurs_par_defaut():
    conn = _connexion([])
    with patch("sources.database.psycopg2.connect", return_value=conn):
        database.volumes_anormaux()
    assert conn._curseur.execute.call_args.args[1] == {"seuil": 2.0, "limite": 10}


# --- garde-fous SQL -----------------------------------------------------------

@pytest.mark.parametrize("sql", [database.SQL_PORTEFEUILLE,
                                 database.SQL_MOUVEMENTS,
                                 database.SQL_VOLUMES])
def test_les_requetes_excluent_les_valeurs_incoherentes_ou_les_signalent(sql):
    """STLAP.PA et ALJXR.PA doivent être filtrés, ou leur statut remonté."""
    assert "statut_qualite" in sql


@pytest.mark.parametrize("sql", [database.SQL_MOUVEMENTS, database.SQL_VOLUMES])
def test_la_derniere_seance_est_calculee_par_ticker(sql):
    """Mesuré le 01/08 : un max(date_seance) global ne remontait que 2 valeurs sur 111,
    les places de cotation n'ayant pas le même calendrier."""
    assert "GROUP  BY ticker" in sql or "GROUP BY ticker" in sql


def test_r1_utilise_lateral_et_pas_distinct_on_sur_cotation():
    """Mesuré : LATERAL 1,19 ms contre DISTINCT ON 295,19 ms sur 273 608 lignes."""
    assert "LATERAL" in database.SQL_PORTEFEUILLE
    assert "DISTINCT ON (ticker)" not in database.SQL_PORTEFEUILLE


def test_r1_utilise_left_join_pour_ne_pas_masquer_une_position():
    """Un INNER JOIN ferait disparaître du briefing une valeur suspendue de cotation."""
    assert "LEFT JOIN LATERAL" in database.SQL_PORTEFEUILLE
    assert "COALESCE" in database.SQL_PORTEFEUILLE
