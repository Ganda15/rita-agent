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


# --- plan 66 (03/10/2026) : le registre decrit le mecanisme de fin de conservation ---------------------

def test_t1_dit_comment_une_position_devient_soldee_et_quand_elle_est_purgee():
    i = REGISTRE.index("### T1"); fiche = REGISTRE[i:REGISTRE.index("### T2")]
    assert "date_cloture" in fiche
    assert "CSV" in fiche and ("retir" in fiche or "dispara" in fiche), "une ligne retiree du CSV est l'acte de vente"
    assert "3 ans" in fiche


def test_p2_est_applicable_et_p3_n_est_plus_une_procedure_vivante():
    ligne_p2 = REGISTRE[REGISTRE.index("| **P2** |"):][:400]
    assert "date_cloture" in ligne_p2 or "clôture" in ligne_p2
    ligne_p3 = REGISTRE[REGISTRE.index("| **P3** |"):][:400]
    assert "retir" in ligne_p3.lower() or "index unique" in ligne_p3.lower()
