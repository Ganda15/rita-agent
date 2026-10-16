"""Sprint 2, tâche 9 : la publication, le déploiement et le retour arrière dans GitHub Actions.

Ce que ces tests vérifient, dans `livraison.yml`, `retour-arriere.yml` et l'action composite `ordre-serveur` :
- la publication de l'image après chaque fusion dans `main`, et son empreinte rendue en sortie ;
- un déploiement qui n'attend que des contrôles verts et ne part que sur `main`, un seul à la fois ;
- l'attente du créneau du matin hors du groupe de concurrence, et la reprise automatique après un code 75 ;
- le retour arrière dans son propre groupe, avec un acteur et un motif obligatoires ;
- l'ingestion (sprint 3, `ingestion.yml`) : manuelle, son propre groupe, l'ordre `ingerer` ;
- aucune entrée saisie dans GitHub n'arrive dans une commande, et des délais qui laissent au serveur le temps de finir.
Les étapes bash de l'action sont jouées avec un faux `ssh` : ces simulations tournent dans la chaîne (Linux).
La structure est lue avec PyYAML, comme `tests/test_lint_config.py` (écart au plan, qui prévoyait une lecture du texte).
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from deploy import deployer as d

RACINE = Path(__file__).resolve().parent.parent
LIVRAISON = RACINE / ".github" / "workflows" / "livraison.yml"
RETOUR = RACINE / ".github" / "workflows" / "retour-arriere.yml"
INGESTION = RACINE / ".github" / "workflows" / "ingestion.yml"     # sprint 3, tâche B4
ACTION = RACINE / ".github" / "actions" / "ordre-serveur" / "action.yml"
EMPREINTE = "${{ needs.construire-et-publier.outputs.empreinte }}"
BASH = pytest.mark.skipif(sys.platform == "win32" or shutil.which("bash") is None,
                          reason="simulation en bash : tourne dans la chaîne (Linux)")


def _charger(chemin):
    return yaml.safe_load(chemin.read_text(encoding="utf-8"))


def _travaux():
    return _charger(LIVRAISON)["jobs"]


def _retour():
    return _charger(RETOUR)["jobs"]["revenir"]


def _ingestion():
    return _charger(INGESTION)["jobs"]["ingerer"]


def _liste(valeur):
    return [valeur] if isinstance(valeur, str) else list(valeur or [])


def _appel_action(travail):
    return next(e for e in travail["steps"] if e.get("uses") == "./.github/actions/ordre-serveur")


def _etape_action(nom):
    return next(e for e in _charger(ACTION)["runs"]["steps"] if e.get("name") == nom)


def _environnement(travail):
    valeur = travail.get("environment")
    return valeur.get("name") if isinstance(valeur, dict) else valeur


# --- La publication -----------------------------------------------------------------------------------------------

def test_publication_sur_main():
    etapes = _travaux()["construire-et-publier"]["steps"]
    publier = next(e for e in etapes if e.get("name") == "Publier l'image vérifiée")
    connexion = next(e for e in etapes if e.get("name") == "S'authentifier sur le registre")
    assert "refs/heads/main" in publier["if"] and "github.event_name == 'push'" in publier["if"]
    assert "refs/tags/livrable-" in publier["if"]
    assert connexion["if"] == publier["if"]


def test_l_empreinte_publiee_est_une_sortie_du_travail():
    travail = _travaux()["construire-et-publier"]
    assert travail["outputs"]["empreinte"] == "${{ steps.empreinte.outputs.ref }}"
    etape = next(e for e in travail["steps"] if e.get("id") == "empreinte")
    assert "refs/heads/main" in etape["if"]
    assert "{{index .RepoDigests 0}}" in etape["run"]
    # L'empreinte est vérifiée avec le même motif que le script du serveur, avant d'être transmise.
    assert r"^ghcr\.io/ganda15/rita-api@sha256:[0-9a-f]{64}$" in etape["run"]


# --- Le déploiement -----------------------------------------------------------------------------------------------

def test_deployer_attend_tous_les_controles_et_ne_part_que_sur_main():
    deployer = _travaux()["deployer"]
    assert set(_liste(deployer["needs"])) == {"lint", "secrets", "construire-et-publier", "attendre-creneau"}
    assert "github.ref == 'refs/heads/main'" in deployer["if"] and "github.event_name == 'push'" in deployer["if"]
    appel = _appel_action(deployer)
    assert appel["with"]["ordre"] == "livrer" and appel["with"]["argument"] == EMPREINTE
    assert appel["with"]["empreinte-bloquante"] == "true"


def test_attente_du_creneau_hors_du_groupe():
    # Une attente dans le groupe `production` y bloquerait tout le reste pendant une heure et demie.
    for nom in ("attendre-creneau", "attendre-reprise"):
        assert "concurrency" not in _travaux()[nom], nom
    etape = "\n".join(e.get("run", "") for e in _travaux()["attendre-creneau"]["steps"])
    assert "secondes_avant_livraison" in etape and 'sleep "$attente"' in etape


def test_un_seul_deploiement_a_la_fois():
    for nom in ("deployer", "deployer-reprise"):
        assert _travaux()[nom]["concurrency"] == {"group": "production", "cancel-in-progress": False}, nom


def test_environnement_production():
    for travail in (_travaux()["deployer"], _travaux()["deployer-reprise"], _retour()):
        assert _environnement(travail) == "production"


def test_code_75_declenche_une_reprise_automatique():
    travaux = _travaux()
    assert travaux["deployer"]["outputs"]["reporte"] == "${{ steps.ordre.outputs.reporte }}"
    for nom in ("attendre-reprise", "deployer-reprise"):
        assert "needs.deployer.outputs.reporte == 'true'" in travaux[nom]["if"], nom
    assert "deployer" in _liste(travaux["attendre-reprise"]["needs"])
    assert {"deployer", "attendre-reprise", "construire-et-publier"} <= set(_liste(travaux["deployer-reprise"]["needs"]))
    premier, reprise = _appel_action(travaux["deployer"]), _appel_action(travaux["deployer-reprise"])
    assert premier["with"]["argument"] == reprise["with"]["argument"] == EMPREINTE   # la MÊME empreinte
    assert premier["with"]["accepter-report"] == "true" and reprise["with"]["accepter-report"] == "false"


# --- Le retour arrière --------------------------------------------------------------------------------------------

def test_retour_arriere_dans_son_propre_groupe():
    # GitHub remplace une exécution en attente par la suivante du même groupe : dans le groupe `production`, un retour
    # en attente derrière une livraison pourrait être annulé par la livraison suivante.
    assert _retour()["concurrency"] == {"group": "retour-arriere", "cancel-in-progress": False}


def test_retour_arriere_exige_acteur_et_motif():
    entrees = _charger(RETOUR)[True]["workflow_dispatch"]["inputs"]   # PyYAML lit la clé `on` comme True
    assert set(entrees) == {"acteur", "motif"}
    assert all(entree["required"] is True for entree in entrees.values())


def test_retour_arriere_envoie_le_numero_du_passage_et_ne_bloque_pas_sur_l_empreinte():
    appel = _appel_action(_retour())
    assert appel["with"]["ordre"] == "revenir" and appel["with"]["argument"] == "${{ github.run_id }}"
    assert appel["with"]["empreinte-bloquante"] == "false" and appel["with"]["accepter-report"] == "false"
    assert "::warning::" in _etape_action("Comparer le script du serveur à celui du dépôt")["run"]


# --- Sprint 3, tâche B4 : l'ingestion en une opération (spec CA3.1) ------------------------------------------------

def test_le_workflow_d_ingestion_est_manuel_et_envoie_ingerer():
    declencheurs = _charger(INGESTION)[True]          # PyYAML lit la clé `on` comme True
    assert set(declencheurs) == {"workflow_dispatch"}  # ni push, ni horaire : une décision humaine, notée
    entrees = declencheurs["workflow_dispatch"]["inputs"]
    assert set(entrees) == {"acteur", "motif"} and all(e["required"] is True for e in entrees.values())
    appel = _appel_action(_ingestion())
    assert appel["with"]["ordre"] == "ingerer" and appel["with"]["argument"] == "${{ github.run_id }}"
    # Bloquante : un script du serveur qui ne connaît pas encore `ingerer` refuserait l'ordre ; on le dit avant.
    assert appel["with"]["empreinte-bloquante"] == "true" and appel["with"]["accepter-report"] == "false"
    assert (appel["with"]["cle-ssh"], appel["with"]["hote"], appel["with"]["known-hosts"]) == (
        "${{ secrets.DEPLOY_SSH_KEY }}", "${{ secrets.DEPLOY_HOST }}", "${{ secrets.DEPLOY_KNOWN_HOSTS }}")


def test_l_ingestion_a_son_propre_groupe_et_l_environnement_production():
    # Même raison que le retour arrière : dans le groupe `production`, une ingestion en attente pourrait être annulée
    # par la livraison suivante, ou l'inverse. L'exclusion entre les trois opérations est assurée par le verrou du
    # serveur (tests/test_deployer_scenarios.py, `test_le_verrou_est_partage_avec_les_livraisons`).
    travail = _ingestion()
    assert travail["concurrency"] == {"group": "ingestion", "cancel-in-progress": False}
    assert _environnement(travail) == "production"
    assert travail["permissions"] == {"contents": "read"}


def test_l_ingestion_laisse_au_serveur_le_temps_de_finir():
    assert _ingestion()["timeout-minutes"] * 60 >= d.ATTENTE_VERROU["ingerer"] + d.DUREE_MAX_INGERER + 300


def test_l_action_connait_l_ordre_ingerer():
    entrees = _charger(ACTION)["inputs"]
    assert "ingerer" in entrees["ordre"]["description"] and "ingerer" in entrees["argument"]["description"]


# --- Les garde-fous communs ---------------------------------------------------------------------------------------

def test_aucune_entree_utilisateur_dans_une_commande():
    # Une entrée recopiée dans un `run:` serait exécutée par le shell : elle ne passe que par une variable d'un bloc env.
    motif = re.compile(r"^\s+[A-Z_]+: \$\{\{ inputs\.[a-z-]+ \}\}$")
    for chemin in (LIVRAISON, RETOUR, INGESTION, ACTION):
        texte = chemin.read_text(encoding="utf-8")
        assert "github.event.inputs" not in texte
        for ligne in texte.splitlines():
            if "${{ inputs." in ligne:
                assert motif.match(ligne), f"{chemin.name} : {ligne.strip()}"


def test_la_cle_ssh_est_ecrite_en_prive_et_effacee_dans_tous_les_cas():
    preparer = _etape_action("Préparer la clé SSH dédiée")["run"]
    assert "umask 077" in preparer
    effacer = _etape_action("Effacer la clé SSH")
    assert effacer["if"] == "always()" and "rm -f" in effacer["run"]
    for etape in _charger(ACTION)["runs"]["steps"]:
        if "ssh " in etape.get("run", ""):
            assert "StrictHostKeyChecking=yes" in etape["run"] and "BatchMode=yes" in etape["run"], etape["name"]


def test_les_travaux_laissent_au_serveur_le_temps_de_finir():
    # Relecture du 14/10 : le serveur attend le verrou puis travaille, chaque étape bornée ; un travail GitHub coupé
    # avant lui laisserait croire à un échec pendant que la livraison continue.
    marge = 300
    travaux = _travaux()
    for nom in ("deployer", "deployer-reprise"):
        assert travaux[nom]["timeout-minutes"] * 60 >= d.ATTENTE_VERROU["livrer"] + d.DUREE_MAX_LIVRER + marge, nom
    assert _retour()["timeout-minutes"] * 60 >= d.ATTENTE_VERROU["revenir"] + d.DUREE_MAX_REVENIR + marge
    for nom in ("attendre-creneau", "attendre-reprise"):
        assert travaux[nom]["timeout-minutes"] * 60 > d.secondes_avant_livraison.__defaults__[0] * 60 + 3600, nom


# --- Les étapes de l'action, jouées avec un faux ssh -------------------------------------------------------------

def _simuler(tmp_path, nom_etape, code_ssh, sortie_ssh="", **variables):
    faux = tmp_path / "ssh"
    faux.write_text('#!/bin/sh\nprintf "%s" "$FAUSSE_SORTIE"\nexit "$FAUX_CODE"\n', encoding="utf-8")
    faux.chmod(0o755)
    sortie = tmp_path / "sortie-github"
    sortie.write_text("", encoding="utf-8")
    environnement = dict(os.environ, PATH=f"{tmp_path}{os.pathsep}{os.environ['PATH']}", HOME=str(tmp_path),
                         FAUX_CODE=str(code_ssh), FAUSSE_SORTIE=sortie_ssh, GITHUB_OUTPUT=str(sortie),
                         HOTE="serveur.exemple", **variables)
    # La commande que GitHub utilise pour `shell: bash`.
    resultat = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", _etape_action(nom_etape)["run"]],
                              env=environnement, capture_output=True, text=True, cwd=RACINE)
    return resultat, sortie.read_text(encoding="utf-8")


@BASH
@pytest.mark.parametrize("code_ssh, accepter, reussit, reporte", [
    (0, "true", True, "false"), (75, "true", True, "true"), (75, "false", False, None),
    (1, "true", False, None), (2, "true", False, None), (255, "true", False, None),
])
def test_un_vrai_echec_reste_bloquant(tmp_path, code_ssh, accepter, reussit, reporte):
    resultat, sortie = _simuler(tmp_path, "Envoyer l'ordre au serveur", code_ssh, ORDRE="livrer", ARGUMENT="x",
                                ACCEPTER_REPORT=accepter)
    assert (resultat.returncode == 0) is reussit, resultat.stdout + resultat.stderr
    if reporte:
        assert f"reporte={reporte}" in sortie


@BASH
@pytest.mark.parametrize("bloquante, reussit", [("true", False), ("false", True)])
def test_une_empreinte_differente_bloque_la_livraison_mais_pas_le_retour(tmp_path, bloquante, reussit):
    resultat, _ = _simuler(tmp_path, "Comparer le script du serveur à celui du dépôt", 0, sortie_ssh="0" * 64,
                           BLOQUANTE=bloquante)
    assert (resultat.returncode == 0) is reussit, resultat.stdout + resultat.stderr
    assert ("::warning::" in resultat.stdout) is reussit


@BASH
def test_la_meme_empreinte_passe(tmp_path):
    empreinte = hashlib.sha256((RACINE / "deploy" / "deployer.py").read_bytes()).hexdigest()
    resultat, _ = _simuler(tmp_path, "Comparer le script du serveur à celui du dépôt", 0, sortie_ssh=empreinte,
                           BLOQUANTE="true")
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
