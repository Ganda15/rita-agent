"""La pire baisse sur un an, calculée par `db/indicateurs_risque.sql` sur la base de test, dans une transaction annulée.

#79 (recette du 01/11/2026). Le test existant lit le texte de la requête ; celui-ci la fait tourner sur des cours
choisis. Quand le cours ne fait que monter, il n'y a aucune baisse : la pire baisse doit valoir 0 %, pas un gain.
Sauté sans base de test déclarée (`tests/garde_base.py`) ; les valeurs d'essai sont créées dans la transaction du test
et annulées avec elle.
"""
from decimal import Decimal

import pytest

psycopg2 = pytest.importorskip("psycopg2")

from psycopg2.extras import RealDictCursor  # noqa: E402

from indicateurs.risque import _charger_requete  # noqa: E402


@pytest.fixture
def curseur():
    from tests.garde_base import dsn_de_test
    try:
        con = psycopg2.connect(dsn_de_test(), connect_timeout=3)
    except psycopg2.OperationalError as e:
        pytest.skip(f"PostgreSQL injoignable : {e}")
    except UnicodeDecodeError:
        # Le serveur répond en français, encodé en Windows-1252 : psycopg2 ne sait pas lire son message (reproduit le
        # 01/11 avec un mot de passe faux, « authentification par mot de passe échouée »). L'adresse n'est pas montrée.
        pytest.skip("connexion refusée par PostgreSQL : vérifier le compte et le mot de passe de la base de test")
    con.autocommit = False
    cur = con.cursor(cursor_factory=RealDictCursor)
    yield cur
    con.rollback()
    con.close()


def _pire_baisse(cur, ticker: str, clotures: list[float]) -> Decimal:
    cur.execute("INSERT INTO valeur (ticker, nom_officiel) VALUES (%s, %s)", (ticker, f"Essai {ticker}"))
    for i, cloture in enumerate(clotures):
        cur.execute("INSERT INTO cotation (ticker, date_seance, ouverture, haut, bas, cloture, volume) "
                    "VALUES (%s, DATE '2026-10-01' + %s, %s, %s, %s, %s, 1)",
                    (ticker, i, cloture, cloture, cloture, cloture))
    cur.execute(_charger_requete())
    lignes = [l for l in cur.fetchall() if l["ticker"] == ticker]
    assert len(lignes) == 1
    return lignes[0]["drawdown_max_1a_pct"]


def test_hausse_continue_aucune_baisse_vaut_zero(curseur):
    """#79 : 100, 110, 120. Aucune séance sous le plus haut de la veille : la pire baisse vaut 0 %, pas +9,09 %."""
    assert _pire_baisse(curseur, "ESSAI.R79A", [100.0, 110.0, 120.0]) == Decimal("0.00")


def test_baisse_continue_garde_la_pire_baisse(curseur):
    """120, 110, 100 : le pire jour est 100 contre un plus haut de 120, soit −16,67 %."""
    assert _pire_baisse(curseur, "ESSAI.R79B", [120.0, 110.0, 100.0]) == Decimal("-16.67")


def test_baisse_puis_reprise_garde_la_pire_baisse(curseur):
    """100, 80, 90, 120 : le pire jour est 80 contre 100, soit −20 % ; la reprise ne l'efface pas."""
    assert _pire_baisse(curseur, "ESSAI.R79C", [100.0, 80.0, 90.0, 120.0]) == Decimal("-20.00")


def test_une_seule_cotation_n_a_pas_de_pire_baisse(curseur):
    """Une seule séance : aucun plus haut antérieur, donc pas de pire baisse calculable ; la valeur reste indisponible
    (`NULL`), pas 0."""
    assert _pire_baisse(curseur, "ESSAI.R79D", [100.0]) is None


def test_serie_plate_vaut_zero(curseur):
    """100, 100, 100 : le cours ne passe jamais sous le plus haut de la veille ; la pire baisse vaut 0 %."""
    assert _pire_baisse(curseur, "ESSAI.R79E", [100.0, 100.0, 100.0]) == Decimal("0.00")
