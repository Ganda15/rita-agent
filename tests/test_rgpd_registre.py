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


# --- sprint 3, tâche C1 (spec CA4.1 à CA4.4) : T7 arrêté, le corpus d'articles analysé, T8 inscrit ---------------

def _fiche(titre: str) -> str:
    """La fiche qui commence au titre `titre`, jusqu'au titre suivant de même niveau ou de niveau supérieur."""
    debut = REGISTRE.index(titre)
    fins = [i for i in (REGISTRE.find("\n### ", debut + 1), REGISTRE.find("\n## ", debut + 1)) if i != -1]
    return REGISTRE[debut:min(fins)] if fins else REGISTRE[debut:]


def test_t7_est_arrete_et_dit_pourquoi():
    # CA4.4 et plan C1 : la date de prise d'effet est vérifiée aux deux endroits où la collecte tourne (le serveur et le
    # poste), par le code réellement exécuté et le premier manifeste de chaque collecte après le changement.
    fiche = _fiche("### T7")
    entete = fiche.splitlines()[0]
    assert "ARRÊTÉ" in entete and "ACTIF" not in entete
    assert "D3" in fiche and "2026-10-16" in fiche
    assert "serveur" in fiche and "poste" in fiche
    assert "72dba4d" in fiche
    assert "manifeste-2026-10-16-190839.json" in fiche and "manifeste-poste-2026-10-16-220139.json" in fiche
    assert "conserv" in fiche, "le sort des articles déjà collectés par Google News est dit"


def test_le_corpus_d_articles_a_son_analyse():
    # CA4.1 et CA4.2 : chaque source du corpus, et l'examen des champs réellement indexés ; l'ancien argument trop court
    # (« on ne les traite pas en tant que personnes ») disparaît.
    from sources.rss import FLUX
    fiche = _fiche("### Corpus d'articles")
    for flux in FLUX:
        assert flux in fiche, f"la source {flux} n'est pas listée"
    assert "licite" in fiche and "Google News" in fiche
    for champ in ("titre", "résumé", "source", "lien", "date", "auteur"):
        assert champ in fiche, champ
    for rubrique in ("personnes", "minimisation", "bloque_injection", "Durée de conservation"):
        assert rubrique in fiche, rubrique
    assert "cnil.fr/fr/recommandations-reutilisateurs-donnees-internet" in fiche
    assert "on ne les traite pas en tant que personnes" not in REGISTRE


def test_t8_existe_et_ne_conserve_pas_le_texte():
    # CA4.3 : le texte des questions et des réponses n'est conservé nulle part sous le contrôle de RITA ; seules des
    # métadonnées le sont. Ce que Microsoft garde est relu dans sa documentation et écrit au registre.
    fiche = _fiche("### T8")
    for rubrique in ("Finalité", "Base légale", "Catégories de données", "Destinataire", "Durée de conservation"):
        assert rubrique in fiche, rubrique
    assert "jamais conservé" in fiche
    for metadonnee in ("motif", "longueur", "identifiants", "heure"):
        assert metadonnee in fiche, metadonnee
    assert "Azure" in fiche and "UE" in fiche
    assert "learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy" in fiche
    assert "journaux" in fiche and "traces" in fiche
