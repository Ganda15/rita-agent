"""Carte #76 : l'API lit la base avec son propre rôle, `rita_api`, plus avec le propriétaire (plan validé le 06/11/2026).

Pourquoi : la matrice d'accès validée par le formateur le 03/10 (chapitre « Données », § 3.5) donne à l'API la lecture des
tables qu'elle sert et l'écriture du seul journal d'audit `mcp_calls`. Or l'API se connectait avec `rita`, le
propriétaire, qui a tous les droits (`evidence/C17/preuve-droits-acces-2026-10-03.md`, § 4.2). La preuve attendue : les
lectures et l'audit fonctionnent ; les écritures métier et les changements de structure sont refusés.

Comme pour `rita_lecture`, sans mot de passe : connecté en propriétaire, `SET ROLE rita_api`, puis on tente.
"""
import pytest

from tests.garde_base import dsn_de_test

psycopg2 = pytest.importorskip("psycopg2")

pytestmark = pytest.mark.postgresql

TABLES_LUES = ["devise", "valeur", "alias_valeur", "cotation", "position", "taux_change", "macro_observation", "article",
               "mcp_calls"]


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


def test_le_role_api_existe_peut_se_connecter_et_n_a_aucun_pouvoir_d_administration(curseur):
    curseur.execute("select rolcanlogin, rolsuper, rolcreatedb, rolcreaterole from pg_roles where rolname = 'rita_api'")
    assert curseur.fetchone() == (True, False, False, False), "rôle rita_api absent ou trop puissant : lancer db/roles.sql"


@pytest.mark.parametrize("table", TABLES_LUES)
def test_le_role_api_lit_les_tables_qu_il_sert(curseur, table):
    curseur.execute("set role rita_api")
    curseur.execute(f'select 1 from "{table}" limit 1')


def test_le_role_api_ecrit_dans_le_journal_d_audit(curseur):
    curseur.execute("set role rita_api")
    curseur.execute("insert into mcp_calls (request_id, client_id, outil, statut, version_politique) "
                    "values ('test-76', 'test', 'test', 'succes', 'test') returning id")
    assert curseur.fetchone()[0] > 0   # la séquence de `id` est utilisable


@pytest.mark.parametrize("ordre", [
    "update cotation set volume = volume where false",
    "delete from cotation where false",
    "update position set quantite = quantite where false",
    "delete from position where false",
    "insert into valeur (ticker) values ('TEST.76')",
    "update mcp_calls set statut = statut where false",
    "delete from mcp_calls where false",
], ids=["update-cotation", "delete-cotation", "update-position", "delete-position", "insert-valeur",
        "update-audit", "delete-audit"])
def test_le_role_api_ne_peut_pas_modifier_les_donnees_metier_ni_l_audit(curseur, ordre):
    curseur.execute("set role rita_api")
    with pytest.raises(psycopg2.errors.InsufficientPrivilege):
        curseur.execute(ordre)


@pytest.mark.parametrize("ordre", ["create table _test_76 (x int)", "drop table cotation", "alter table valeur add column x int",
                                   "truncate mcp_calls"],
                         ids=["create", "drop", "alter", "truncate"])
def test_le_role_api_ne_peut_pas_changer_la_structure(curseur, ordre):
    curseur.execute("set role rita_api")
    with pytest.raises(psycopg2.errors.InsufficientPrivilege):
        curseur.execute(ordre)
