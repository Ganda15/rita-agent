"""Le registre RGPD suit le code : un traitement nouveau a sa fiche le jour où la table existe (plan 62)."""
from pathlib import Path

REGISTRE = (Path(__file__).resolve().parent.parent / "db" / "RGPD-registre-des-traitements.md").read_text(encoding="utf-8")


def test_le_journal_mcp_a_sa_fiche_t5():
    i = REGISTRE.index("### T5")
    fiche = REGISTRE[i:REGISTRE.index("### ", i + 1)]
    assert "mcp_calls" in fiche
    assert "90 jours" in fiche
    for rubrique in ("Finalité", "Base légale", "Catégories de données", "Durée de conservation", "Sécurité"):
        assert rubrique in fiche, rubrique


def test_la_purge_du_journal_mcp_est_une_procedure_automatisee():
    assert "| **P6** |" in REGISTRE and "mcp_calls" in REGISTRE[REGISTRE.index("| **P6** |"):][:300]
