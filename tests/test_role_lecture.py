"""Rôle PostgreSQL en lecture seule pour tout outil d'agent — C11 (OWASP : moindre privilège).

Pourquoi : un agent qui explore la base (MCP, script, text-to-SQL) ne doit pas pouvoir écrire.
Le rôle `rita_lecture` a SELECT sur toutes les tables et vues du schéma public, rien d'autre.
On le prouve sans mot de passe : connecté en propriétaire, `SET ROLE rita_lecture`, puis on
tente d'écrire — la base doit refuser. Item 8 du harnais (rapport Agentic SD, 19/09/2026).
"""
import os
import re
from pathlib import Path

import pytest

psycopg2 = pytest.importorskip("psycopg2")

RACINE = Path(__file__).parent.parent


def dsn_proprietaire() -> str:
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    env = RACINE / ".env"
    if env.exists():
        for l in env.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*DATABASE_URL\s*=\s*(.*)$", l)
            if m:
                return m.group(1).strip().strip('"').strip("'")
    pytest.skip("pas de DATABASE_URL : base locale absente (CI)", allow_module_level=True)


@pytest.fixture
def curseur():
    try:
        con = psycopg2.connect(dsn_proprietaire(), connect_timeout=3)
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
