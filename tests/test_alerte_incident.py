"""Une alerte Langfuse devient une issue `incident` dans le dépôt (C11, C20, C21).

Audit du 02/10/2026 : RITA mesurait (traces) mais n'alertait personne. Le palier gratuit de
Langfuse offre deux alertes, et ses canaux sont Slack, un webhook signé ou un déclencheur
GitHub Actions ; pas de courriel. Le dépôt est déjà l'endroit où vivent les incidents
(evidence/C21, issues, PR) : une alerte y ouvre donc une issue, et la chaîne « seuil franchi,
issue ouverte, diagnostic, correctif par PR » est la boucle que C21 demande.

Le fichier de workflow est un contrat : on le teste comme du code, comme livraison.yml.
"""
import re
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).parent.parent
CHEMIN = RACINE / ".github/workflows/alerte-incident.yml"


@pytest.fixture(scope="module")
def flux():
    assert CHEMIN.exists(), "workflow .github/workflows/alerte-incident.yml absent"
    return yaml.safe_load(CHEMIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def declencheurs(flux):
    # PyYAML lit la clé `on` comme le booléen True : c'est connu, on prend les deux.
    return flux.get("on") if "on" in flux else flux.get(True)


@pytest.fixture(scope="module")
def etapes(flux):
    (job,) = flux["jobs"].values()
    return job, job["steps"]


def test_le_workflow_se_declenche_depuis_langfuse_et_a_la_main(declencheurs):
    """`repository_dispatch` : ce que Langfuse envoie. `workflow_dispatch` : le bouton
    « Run workflow », pour prouver la chaîne devant le jury sans attendre une vraie alerte."""
    assert "repository_dispatch" in declencheurs and "workflow_dispatch" in declencheurs
    assert "alerte-langfuse" in (declencheurs["repository_dispatch"].get("types") or [])


def test_le_workflow_n_a_que_le_droit_d_ecrire_des_issues(flux, etapes):
    job, _ = etapes
    permissions = flux.get("permissions") or job.get("permissions") or {}
    assert permissions.get("issues") == "write"
    autres = {k: v for k, v in permissions.items() if k != "issues"}
    assert all(v == "read" for v in autres.values()), f"droits au-delà du nécessaire : {autres}"


def test_une_etape_ouvre_une_issue_incident_avec_le_jeton_du_depot(etapes):
    _, steps = etapes
    creation = [e for e in steps if "gh issue create" in (e.get("run") or "")]
    assert creation, "aucune étape ne lance `gh issue create`"
    etape = creation[0]
    assert "incident" in etape["run"]
    env = {**etape.get("env", {})}
    assert "GITHUB_TOKEN" in str(env.get("GH_TOKEN", "")), "le jeton doit être celui du dépôt, pas un PAT"


def test_une_alerte_qui_se_repete_commente_l_issue_ouverte_au_lieu_d_en_creer_une_autre(etapes):
    _, steps = etapes
    script = "\n".join(e.get("run") or "" for e in steps)
    assert "gh issue list" in script and "--label incident" in script
    assert "gh issue comment" in script, "une alerte répétée doit commenter, pas empiler des issues"


def test_le_label_incident_est_cree_s_il_manque(etapes):
    _, steps = etapes
    script = "\n".join(e.get("run") or "" for e in steps)
    assert re.search(r"gh label create\s+incident", script), "le dépôt n'a pas encore ce label : le workflow doit le créer"


def test_aucun_secret_n_est_ecrit_dans_le_workflow():
    texte = CHEMIN.read_text(encoding="utf-8")
    assert not re.search(r"pk-lf-[A-Za-z0-9]{8,}|sk-lf-[A-Za-z0-9]{8,}|ghp_[A-Za-z0-9]{8,}|github_pat_", texte)


def test_le_document_d_exploitation_decrit_la_chaine_d_alerte():
    doc = (RACINE / "docs/EXPLOITATION.md").read_text(encoding="utf-8")
    assert "alerte-incident.yml" in doc and "Langfuse" in doc
