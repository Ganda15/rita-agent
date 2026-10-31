"""Une alerte Langfuse devient une issue `incident` dans le dépôt (C11, C20, C21).

Audit du 02/10/2026 : RITA mesurait (traces) mais n'alertait personne. Le palier gratuit de
Langfuse offre deux alertes, et ses canaux sont Slack, un webhook signé ou un déclencheur
GitHub Actions ; pas de courriel. Le dépôt est déjà l'endroit où vivent les incidents
(evidence/C21, issues, PR) : une alerte y ouvre donc une issue, et la chaîne « seuil franchi,
issue ouverte, diagnostic, correctif par PR » est la boucle que C21 demande.

Le fichier de workflow est un contrat : on le teste comme du code, comme livraison.yml.
"""
import json
import os
import re
import shutil
import subprocess
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
    doc = (RACINE / "docs/exploitation.md").read_text(encoding="utf-8")
    assert "alerte-incident.yml" in doc and "Langfuse" in doc


# --- Le nom de l'alerte (04/10/2026) -----------------------------------------------------
# Les deux premières vraies alertes (issue #77, exécutions 37194357268 et 37194875460) sont
# arrivées sous le nom générique « alerte Langfuse » : le workflow cherchait le nom dans
# `.name`, `.alertName`, `.title`, alors que Langfuse l'envoie dans `.payload.message.title`,
# précédé de la gravité (« [ALERT] RITA : ... »). Conséquence : deux alertes différentes
# commentaient la même issue. Charge utile ci-dessous : celle reçue le 04/10 à 10:17 UTC,
# copiée de l'issue #77 (champs utiles seulement).
CHARGE_LANGFUSE_04_10 = {
    "apiVersion": "v1",
    "id": "c7c224ff-b0df-4491-907e-fef302110178",
    "payload": {
        "filters": [{"column": "name", "operator": "any of", "type": "stringOptions",
                     "value": ["briefing-llm"]}],
        "message": {
            "body": "`p95(observations.latency)` is **above** `15` over the last **1d**",
            "title": "[ALERT] RITA : appel au modèle trop lent",
        },
        "severity": "ALERT",
        "view": "observations",
        "window": "1d",
    },
    "type": "monitor-alert",
}


def _script_contenu(etapes):
    _, steps = etapes
    (etape,) = [e for e in steps if e.get("id") == "contenu"]
    return etape["run"]


def test_le_nom_de_l_alerte_est_lu_dans_le_message_envoye_par_langfuse(etapes):
    """Contrôle statique, valable sur tout poste : le chemin où Langfuse met vraiment le nom."""
    assert ".payload.message.title" in _script_contenu(etapes)


@pytest.mark.skipif(not (shutil.which("bash") and shutil.which("jq")),
                    reason="bash et jq requis (présents sur le runner GitHub, pas sur ce poste)")
@pytest.mark.parametrize("charge, nom_attendu", [
    (CHARGE_LANGFUSE_04_10, "RITA : appel au modèle trop lent"),
    ({}, "alerte Langfuse"),
])
def test_l_etape_construit_un_titre_par_alerte_sans_la_gravite(etapes, tmp_path, charge, nom_attendu):
    """On exécute le vrai script de l'étape, avec la vraie charge utile. La gravité est retirée
    du titre : sinon une même alerte qui changerait d'état ouvrirait une autre issue."""
    sortie = tmp_path / "sortie.txt"
    env = {**os.environ, "EVENEMENT": "repository_dispatch", "CHARGE_UTILE": json.dumps(charge),
           "ALERTE_MANUELLE": "", "DETAIL_MANUEL": "", "LIEN_EXECUTION": "https://exemple.invalid/run",
           "GITHUB_OUTPUT": str(sortie)}
    subprocess.run(["bash", "-c", _script_contenu(etapes)], cwd=tmp_path, env=env, check=True)
    assert f"titre=Incident : alerte Langfuse « {nom_attendu} »" in sortie.read_text(encoding="utf-8")
    corps = (tmp_path / "corps.md").read_text(encoding="utf-8")
    assert f"| Alerte | {nom_attendu} |" in corps
    if charge:
        assert "| Gravité | ALERT |" in corps
        assert "p95(observations.latency)" in corps.split("<details>")[0], "le détail doit se lire sans déplier"


# --- Le retour à la normale (INC-009, issue #137, 31/10/2026) ----------------------------
# Le 24/10 à 08:30 UTC, Langfuse a envoyé « [OK] RITA : fournisseur en erreur » (« recovered »).
# L'issue #130 de cette alerte avait été fermée à la main la veille, fausse alerte qualifiée. L'étape
# n'a trouvé aucune issue ouverte sous ce titre et en a créé une nouvelle, #137, de gravité OK : une
# notification de retour à la normale traitée comme un incident. Charge utile ci-dessous : celle de
# l'issue #137 (champs utiles seulement). Les tests rejouent les deux vraies étapes du workflow, avec un
# faux `gh` qui note ses appels au lieu de les faire : aucune issue n'est créée.
CHARGE_LANGFUSE_24_10_OK = {
    "apiVersion": "v1",
    "id": "57467bab-5cb8-4868-8f38-8974e14bdeb5",
    "payload": {
        "filters": [{"column": "level", "operator": "any of", "type": "stringOptions", "value": ["ERROR"]}],
        "message": {"body": "`count(observations.count)` recovered", "title": "[OK] RITA : fournisseur en erreur"},
        "severity": "OK",
        "view": "observations",
        "window": "1d",
    },
    "type": "monitor-alert",
}
CHARGE_LANGFUSE_ALERTE = {**CHARGE_LANGFUSE_24_10_OK, "payload": {
    **CHARGE_LANGFUSE_24_10_OK["payload"], "severity": "ALERT",
    "message": {"body": "`count(observations.count)` is **above** `0` over the last **1d**",
                "title": "[ALERT] RITA : fournisseur en erreur"}}}
TITRE_FOURNISSEUR = "Incident : alerte Langfuse « RITA : fournisseur en erreur »"
SORTIE_DE_ETAPE = re.compile(r"^\$\{\{\s*steps\.contenu\.outputs\.(\w+)\s*\}\}$")


def _rejouer(etapes, tmp_path, charge, issues_ouvertes):
    """Rejoue l'étape « contenu » puis l'étape « ouvrir ou commenter », telles qu'elles sont écrites dans le
    workflow. Rend les appels faits à `gh`, un par ligne."""
    _, steps = etapes
    sortie = tmp_path / "sortie.txt"
    env = {**os.environ, "EVENEMENT": "repository_dispatch", "CHARGE_UTILE": json.dumps(charge),
           "ALERTE_MANUELLE": "", "DETAIL_MANUEL": "", "LIEN_EXECUTION": "https://exemple.invalid/run",
           "GITHUB_OUTPUT": str(sortie)}
    subprocess.run(["bash", "-c", _script_contenu(etapes)], cwd=tmp_path, env=env, check=True)
    sorties = dict(ligne.split("=", 1) for ligne in sortie.read_text(encoding="utf-8").splitlines() if "=" in ligne)

    journal = tmp_path / "appels-gh.txt"
    faux_gh = tmp_path / "bin" / "gh"
    faux_gh.parent.mkdir()
    faux_gh.write_text("#!/usr/bin/env bash\n"
                       f'echo "$*" >> "{journal.as_posix()}"\n'
                       f"if [ \"$1 $2\" = \"issue list\" ]; then echo '{json.dumps(issues_ouvertes)}'; fi\n",
                       encoding="utf-8")
    faux_gh.chmod(0o755)

    (etape,) = [e for e in steps if "gh issue create" in (e.get("run") or "")]
    env_etape = {}
    for nom, valeur in (etape.get("env") or {}).items():
        lien = SORTIE_DE_ETAPE.match(str(valeur))
        env_etape[nom] = sorties.get(lien.group(1), "") if lien else "faux"
    env = {**os.environ, **env_etape, "PATH": f"{faux_gh.parent}{os.pathsep}{os.environ['PATH']}"}
    subprocess.run(["bash", "-c", etape["run"]], cwd=tmp_path, env=env, check=True)
    return journal.read_text(encoding="utf-8").splitlines() if journal.exists() else []


bash_et_jq = pytest.mark.skipif(not (shutil.which("bash") and shutil.which("jq")),
                                reason="bash et jq requis (présents sur le runner GitHub, pas sur ce poste)")


@bash_et_jq
def test_une_alerte_sans_issue_ouverte_cree_une_issue(etapes, tmp_path):
    appels = _rejouer(etapes, tmp_path, CHARGE_LANGFUSE_ALERTE, issues_ouvertes=[])
    assert any(a.startswith("issue create") and TITRE_FOURNISSEUR in a for a in appels), appels


@bash_et_jq
def test_une_alerte_repetee_commente_l_issue_ouverte(etapes, tmp_path):
    appels = _rejouer(etapes, tmp_path, CHARGE_LANGFUSE_ALERTE,
                      issues_ouvertes=[{"number": 130, "title": TITRE_FOURNISSEUR}])
    assert any(a.startswith("issue comment 130") for a in appels), appels
    assert not any(a.startswith("issue create") for a in appels), appels


@bash_et_jq
def test_un_retour_a_la_normale_sans_issue_ouverte_ne_cree_aucune_issue(etapes, tmp_path):
    """Le cas de #137 : l'incident a été fermé, puis le retour à la normale arrive. Rien à ouvrir."""
    appels = _rejouer(etapes, tmp_path, CHARGE_LANGFUSE_24_10_OK, issues_ouvertes=[])
    assert not any(a.startswith("issue create") for a in appels), f"un retour à OK a créé une issue : {appels}"


@bash_et_jq
def test_un_retour_a_la_normale_commente_l_issue_ouverte_sans_la_fermer(etapes, tmp_path):
    """Un retour à OK dit que la condition d'alerte n'est plus remplie, pas que le défaut est corrigé :
    il s'écrit dans l'issue ouverte, et la fermeture reste une décision humaine."""
    appels = _rejouer(etapes, tmp_path, CHARGE_LANGFUSE_24_10_OK,
                      issues_ouvertes=[{"number": 130, "title": TITRE_FOURNISSEUR}])
    assert any(a.startswith("issue comment 130") for a in appels), appels
    assert not any(a.startswith(("issue create", "issue close")) for a in appels), appels
