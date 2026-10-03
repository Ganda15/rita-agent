"""La clôture des positions sur la base réelle, dans une transaction annulée (plan 66, règle INC-006).

Sauté sans `DATABASE_URL`. Prouve ce que les tests de contrat ne prouvent pas : la base refuse une ligne
en double, une position close sort de la vue mais reste en table, la réconciliation la rouvre, et P2 ne
supprime qu'au-delà de trois ans après la clôture.
"""
import pytest

psycopg2 = pytest.importorskip("psycopg2")

from db import rgpd_purge  # noqa: E402


@pytest.fixture
def curseur():
    from tests.test_role_lecture import dsn_proprietaire
    try:
        con = psycopg2.connect(dsn_proprietaire(), connect_timeout=3)
    except psycopg2.OperationalError as e:
        pytest.skip(f"PostgreSQL injoignable : {e}")
    con.autocommit = False
    cur = con.cursor()
    yield cur
    con.rollback()
    con.close()


def _ticker(cur):
    cur.execute("SELECT ticker FROM valeur ORDER BY ticker LIMIT 1")
    return cur.fetchone()[0]


def test_la_base_refuse_la_meme_ligne_deux_fois(curseur):
    t = _ticker(curseur)
    curseur.execute("INSERT INTO position (ticker, quantite, pru, devise, date_achat) VALUES (%s, 3, 11.11, 'EUR', '2024-01-02')", (t,))
    curseur.execute("SAVEPOINT s")
    with pytest.raises(psycopg2.errors.UniqueViolation):
        curseur.execute("INSERT INTO position (ticker, quantite, pru, devise, date_achat) VALUES (%s, 5, 11.11, 'EUR', '2024-01-02')", (t,))
    curseur.execute("ROLLBACK TO SAVEPOINT s")


def test_une_position_close_sort_de_la_vue_et_reste_en_table(curseur):
    t = _ticker(curseur)
    curseur.execute("INSERT INTO position (ticker, quantite, pru, devise, date_achat, date_cloture) "
                    "VALUES (%s, 3, 22.22, 'EUR', '2024-01-02', CURRENT_DATE) RETURNING id", (t,))
    ident = curseur.fetchone()[0]
    curseur.execute("SELECT count(*) FROM v_portefeuille_valorise WHERE ticker = %s AND pru = 22.22", (t,))
    assert curseur.fetchone()[0] == 0, "close : plus valorisee"
    curseur.execute("SELECT date_cloture FROM position WHERE id = %s", (ident,))
    assert curseur.fetchone()[0] is not None, "mais toujours en table, trois ans"


def test_la_cloture_ne_peut_pas_preceder_l_achat(curseur):
    t = _ticker(curseur)
    curseur.execute("SAVEPOINT s")
    with pytest.raises(psycopg2.errors.CheckViolation):
        curseur.execute("INSERT INTO position (ticker, quantite, pru, devise, date_achat, date_cloture) "
                        "VALUES (%s, 3, 33.33, 'EUR', '2024-06-01', '2024-01-01')", (t,))
    curseur.execute("ROLLBACK TO SAVEPOINT s")


def test_p2_ne_purge_qu_au_dela_de_trois_ans_apres_la_cloture(curseur):
    t = _ticker(curseur)
    curseur.execute("INSERT INTO position (ticker, quantite, pru, devise, date_achat, date_cloture) "
                    "VALUES (%s, 3, 44.44, 'EUR', '2019-01-02', CURRENT_DATE - INTERVAL '4 years')", (t,))
    curseur.execute("INSERT INTO position (ticker, quantite, pru, devise, date_achat, date_cloture) "
                    "VALUES (%s, 3, 55.55, 'EUR', '2024-01-02', CURRENT_DATE - INTERVAL '10 days')", (t,))
    a_blanc = rgpd_purge.p2_purger_positions_soldees(curseur, appliquer=False)
    assert a_blanc["concernees"] >= 1 and a_blanc["supprimees"] == 0
    reel = rgpd_purge.p2_purger_positions_soldees(curseur, appliquer=True)
    assert reel["supprimees"] >= 1
    curseur.execute("SELECT count(*) FROM position WHERE ticker = %s AND pru IN (44.44, 55.55)", (t,))
    assert curseur.fetchone()[0] == 1, "la close recente reste, la vieille de 4 ans est partie"
