"""La table `mcp_calls` sur la base réelle, dans une transaction annulée (plan 62, règle INC-006).

Sauté sans `DATABASE_URL` (la CI n'a pas de PostgreSQL). Prouve ce qu'un test de contrat ne peut pas
prouver : la table accepte une ligne conforme, refuse un statut hors liste, le rôle `rita_lecture`
peut lire mais pas écrire, et la purge P6 compte sans supprimer en simulation.
"""
import pytest

psycopg2 = pytest.importorskip("psycopg2")

from db import rgpd_purge  # noqa: E402


# 02/11/2026 : chaque test de ce fichier demande PostgreSQL ; le job `base` de la CI les choisit par ce marqueur.
pytestmark = pytest.mark.postgresql


@pytest.fixture
def curseur():
    from tests.garde_base import dsn_de_test
    try:
        con = psycopg2.connect(dsn_de_test(), connect_timeout=3)
    except psycopg2.OperationalError as e:
        pytest.skip(f"PostgreSQL injoignable : {e}")
    con.autocommit = False
    cur = con.cursor()
    yield cur
    con.rollback()
    con.close()


INSERTION = ("INSERT INTO mcp_calls (request_id, client_id, outil, statut, code_erreur, duree_ms, version_politique) "
             "VALUES (%s, 'passerelle-mcp', 'rita_portefeuille', %s, %s, 3, 'matrice-acces-2026-09-07')")


def test_une_ligne_conforme_entre_et_se_relit(curseur):
    curseur.execute(INSERTION, ("t" * 32, "refuse", "NOT_AUTHORIZED"))
    curseur.execute("SELECT client_id, outil, statut, code_erreur, version_politique FROM mcp_calls WHERE request_id = %s",
                    ("t" * 32,))
    assert curseur.fetchone() == ("passerelle-mcp", "rita_portefeuille", "refuse", "NOT_AUTHORIZED", "matrice-acces-2026-09-07")


def test_un_statut_hors_liste_est_refuse_par_la_base(curseur):
    curseur.execute("SAVEPOINT s")
    with pytest.raises(psycopg2.errors.CheckViolation):
        curseur.execute(INSERTION, ("u" * 32, "bizarre", None))
    curseur.execute("ROLLBACK TO SAVEPOINT s")


def test_le_role_lecture_lit_mais_n_ecrit_pas(curseur):
    curseur.execute(INSERTION, ("v" * 32, "succes", None))
    curseur.execute("SET ROLE rita_lecture")
    curseur.execute("SELECT count(*) FROM mcp_calls WHERE request_id = %s", ("v" * 32,))
    assert curseur.fetchone()[0] == 1
    curseur.execute("SAVEPOINT s")
    with pytest.raises(psycopg2.errors.InsufficientPrivilege):
        curseur.execute(INSERTION, ("w" * 32, "succes", None))
    curseur.execute("ROLLBACK TO SAVEPOINT s")
    curseur.execute("RESET ROLE")


def test_la_purge_p6_compte_sans_supprimer_en_simulation(curseur):
    curseur.execute("INSERT INTO mcp_calls (request_id, client_id, outil, statut, version_politique, horodatage) "
                    "VALUES (%s, 'passerelle-mcp', 'rita_fraicheur', 'succes', 'matrice-acces-2026-09-07', now() - INTERVAL '120 days')",
                    ("x" * 32,))
    r = rgpd_purge.p6_purger_mcp_calls(curseur, appliquer=False)
    assert r["concernees"] >= 1 and r["supprimees"] == 0
    curseur.execute("SELECT count(*) FROM mcp_calls WHERE request_id = %s", ("x" * 32,))
    assert curseur.fetchone()[0] == 1, "en simulation, rien n'est supprime"
