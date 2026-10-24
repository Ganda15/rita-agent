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


# --- plan 66 (03/10/2026, D1 a D4 = A) : la cloture des positions ---------------------------------

def test_la_position_a_une_date_de_cloture_nullable_posterieure_a_l_achat():
    table = _table("position")
    assert re.search(r"^\s+date_cloture\s+DATE,", table, re.M), "NULL = detenue"
    assert "CONSTRAINT cloture_apres_achat" in table
    assert "date_cloture >= date_achat" in table


def test_une_ligne_de_portefeuille_a_une_cle_unique_ticker_pru_date_achat():
    """D1 : deux achats du meme titre a des prix differents restent deux lignes ; la meme ligne deux
    fois est refusee par la base, plus par une procedure P3 qui ne faisait que signaler."""
    assert "CREATE UNIQUE INDEX uq_position_ligne ON position (ticker, pru, COALESCE(date_achat, DATE '1900-01-01'));" in SCHEMA


def test_le_commentaire_de_la_cloture_dit_qui_la_pose_et_quand_elle_purge():
    i = SCHEMA.index("COMMENT ON COLUMN position.date_cloture IS")
    c = SCHEMA[i:SCHEMA.index("';", i)].lower()     # la fin de la chaîne, pas un ';' dedans
    assert "import" in c and "csv" in c
    assert "trois ans" in c or "3 ans" in c


def test_la_migration_de_la_cloture_est_rejouable_et_refuse_d_agir_sur_des_doublons():
    m = (RACINE / "db" / "migration-2026-10-03-cloture-positions.sql").read_text(encoding="utf-8")
    assert "ADD COLUMN IF NOT EXISTS date_cloture" in m
    assert "CREATE UNIQUE INDEX IF NOT EXISTS uq_position_ligne" in m
    assert "RAISE EXCEPTION" in m and "HAVING count(*) > 1" in m, "compter les doublons avant de poser l index"


# --- 24/10/2026 : l'ordre des deux migrations de la vue (relevé le 23/10) ----------------------------------------
# La migration « taux » du 03/10 décrit la vue AVANT le plan 66 : sans le filtre des positions closes. Jouée avant la
# migration de la clôture, tout va bien ; rejouée après, elle ferait revenir les positions closes dans la valorisation.

MIGRATION_TAUX = (RACINE / "db" / "migration-2026-10-03-vue-valorisation-taux.sql").read_text(encoding="utf-8")


def test_la_vue_finale_ne_valorise_jamais_une_position_close():
    """L'état final, par une installation neuve comme par la dernière migration, garde le filtre."""
    cloture = (RACINE / "db" / "migration-2026-10-03-cloture-positions.sql").read_text(encoding="utf-8")
    assert "p.date_cloture IS NULL" in SCHEMA
    assert "p.date_cloture IS NULL" in cloture


def test_le_guide_joue_la_migration_taux_avant_celle_de_la_cloture():
    guide = (RACINE / "docs" / "exploitation.md").read_text(encoding="utf-8")
    assert (guide.index("-f db\\migration-2026-10-03-vue-valorisation-taux.sql")
            < guide.index("-f db\\migration-2026-10-03-cloture-positions.sql"))


def test_l_entete_de_la_migration_taux_dit_qu_elle_se_joue_avant_la_cloture():
    """Avant : l'en-tête se disait « meme texte » que le schéma, et rejouable sans condition. C'était faux depuis le
    plan 66 : le schéma a gagné le filtre des positions closes, pas cette migration."""
    entete = MIGRATION_TAUX[:MIGRATION_TAUX.index("BEGIN;")]
    assert "meme texte" not in entete
    assert "migration-2026-10-03-cloture-positions.sql" in entete
    assert "AVANT" in entete
