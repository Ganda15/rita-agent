"""Rôle PostgreSQL en lecture seule pour tout outil d'agent — C11 (OWASP : moindre privilège).

Pourquoi : un agent qui explore la base (MCP, script, text-to-SQL) ne doit pas pouvoir écrire.
Le rôle `rita_lecture` a SELECT sur toutes les tables et vues du schéma public, rien d'autre.
On le prouve sans mot de passe : connecté en propriétaire, `SET ROLE rita_lecture`, puis on
tente d'écrire — la base doit refuser. Item 8 du harnais (rapport Agentic SD, 19/09/2026).
"""
import pytest

from tests.garde_base import dsn_de_test

psycopg2 = pytest.importorskip("psycopg2")


@pytest.fixture
def curseur():
    try:
        con = psycopg2.connect(dsn_de_test(), connect_timeout=3)
    except psycopg2.OperationalError as e:
        pytest.skip(f"PostgreSQL injoignable : {e}")
    con.autocommit = False
    cur = con.cursor()
    yield cur
    con.rollback()
    con.close()


def test_le_role_lecture_existe_et_peut_se_connecter(curseur):
    curseur.execute("select rolcanlogin, rolsuper, rolcreatedb from pg_roles where rolname = 'rita_lecture'")
    ligne = curseur.fetchone()
    assert ligne is not None, "rôle rita_lecture absent : lancer db/roles.sql"
    assert ligne == (True, False, False)


def test_le_role_lecture_lit_toutes_les_tables(curseur):
    curseur.execute("set role rita_lecture")
    curseur.execute("select table_name from information_schema.tables where table_schema = 'public'")
    tables = [t[0] for t in curseur.fetchall()]
    assert tables, "aucune table visible"
    for t in tables:
        curseur.execute(f'select 1 from "{t}" limit 1')  # lecture permise partout


def test_le_role_lecture_ne_peut_pas_ecrire(curseur):
    curseur.execute("set role rita_lecture")
    curseur.execute("select table_name from information_schema.tables where table_schema = 'public' and table_type = 'BASE TABLE' limit 1")
    table = curseur.fetchone()[0]
    with pytest.raises(psycopg2.errors.InsufficientPrivilege):
        curseur.execute(f'delete from "{table}" where false')


def test_le_role_lecture_ne_peut_pas_creer_de_table(curseur):
    curseur.execute("set role rita_lecture")
    with pytest.raises(psycopg2.errors.InsufficientPrivilege):
        curseur.execute("create table _test_lecture (x int)")
