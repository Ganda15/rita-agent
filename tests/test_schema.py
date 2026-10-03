"""Tests de contrat sur `db/schema.sql` : la règle écrite, figée par un test (plan 62, table `mcp_calls`).

Un test de contrat lit le fichier SQL comme une donnée. Il ne prouve pas que PostgreSQL l'exécute
(ça, c'est `tests/test_audit_mcp_base.py`, sur la base réelle) ; il prouve que la règle est écrite
et qu'elle ne disparaîtra pas en silence.
"""
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCHEMA = (RACINE / "db" / "schema.sql").read_text(encoding="utf-8")


def _table(nom: str) -> str:
    i = SCHEMA.index(f"CREATE TABLE {nom} (")
    return SCHEMA[i:SCHEMA.index(");", i) + 2]


def test_la_table_mcp_calls_existe_avec_ses_huit_colonnes():
    """Chapitre « Données » §3.7 : huit champs, pas un de plus (tout champ supplémentaire doit répondre
    à un besoin explicite)."""
    table = _table("mcp_calls")
    for colonne in ("request_id", "client_id", "outil", "statut", "code_erreur", "duree_ms",
                    "version_politique", "horodatage"):
        assert re.search(rf"^\s+{colonne}\s", table, re.M), colonne
    assert "id " in table and "BIGSERIAL" in table


def test_le_statut_est_controle_et_la_duree_positive():
    table = _table("mcp_calls")
    assert "CHECK (statut IN ('succes', 'refuse', 'erreur'))" in table
    assert "duree_ms IS NULL OR duree_ms >= 0" in table


def test_un_index_sur_l_horodatage_sert_la_lecture_et_la_purge():
    assert "CREATE INDEX idx_mcp_calls_horodatage ON mcp_calls (horodatage DESC);" in SCHEMA


def test_le_commentaire_dit_ce_qui_n_entre_jamais_dans_la_table():
    i = SCHEMA.index("COMMENT ON TABLE mcp_calls IS")
    commentaire = SCHEMA[i:SCHEMA.index(";", i)].lower()
    for interdit in ("parametre", "prompt", "cle", "portefeuille"):
        assert interdit in commentaire, interdit
    assert "90 jours" in commentaire


def test_la_migration_rejouable_existe_et_cree_la_table_si_absente():
    migration = (RACINE / "db" / "migration-2026-10-03-mcp-calls.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS mcp_calls" in migration
    assert "CREATE INDEX IF NOT EXISTS idx_mcp_calls_horodatage" in migration
