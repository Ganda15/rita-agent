"""Sprint 5, étape 9 : la copie du sprint 5 sur le poste (plan du sprint 5, § 2 « Déployer et rollback », étape 9).

`scripts/copie_sprint5.py` déploie, revient en arrière, initialise et collecte, sur un projet Compose à part
(`rita-s5`) avec sa propre image (`rita-api:s5-<commit>`). Les tests vérifient les commandes envoyées à Docker sans
lancer Docker, et les règles : pas de déploiement ni de retour arrière pendant une panne simulée ; un retour arrière
relance l'image précédente sans la reconstruire et vérifie le commit annoncé ET l'identifiant de l'image ; il
consomme la version précédente, comme en production. Le fichier Compose du sprint 5 est vérifié comme un contrat.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from scripts import copie_sprint5 as copie

RACINE = Path(__file__).parent.parent
COMMIT_A = "a" * 40
COMMIT_B = "b" * 40
CLE = "cle-de-test-pour-la-suite-pytest-32c"


class _Resultat:
    def __init__(self, sortie=""):
        self.stdout, self.returncode = sortie, 0


class _Docker:
    """`subprocess.run` remplacé : chaque commande est gardée, avec ses variables ; les réponses sont scriptées."""

    def __init__(self, commit=COMMIT_B, image_conteneur="sha256:img-a", images=None):
        self.appels = []
        self.commit, self.image_conteneur = commit, image_conteneur
        self.images = images or {"a" * 12: "sha256:img-a", "b" * 12: "sha256:img-b"}

    def __call__(self, arguments, **options):
        self.appels.append((arguments, options.get("env") or {}))
        if arguments[:2] == ["git", "rev-parse"]:
            return _Resultat(self.commit + "\n")
        if arguments[:3] == ["docker", "inspect", "--format"]:
            return _Resultat(self.image_conteneur + "\n")
        if arguments[:4] == ["docker", "image", "inspect", "--format"]:
            return _Resultat(self.images[arguments[-1].split(":s5-")[1]] + "\n")
        return _Resultat()

    def compose(self):
        return [(a[a.index("compose") + 1:], env) for a, env in self.appels if "compose" in a]


class _Reponse:
    def __init__(self, code, corps):
        self.status_code, self._corps = code, corps

    def json(self):
        return self._corps


def _http(commit=COMMIT_B, exercice=None, sante_joignable=True):
    def get(url, entetes):
        if url.endswith("/sante"):
            if not sante_joignable:
                raise ConnectionError("copie arrêtée")
            return _Reponse(200, {"exercice": exercice})
        return _Reponse(200, {"status": "ok", "commit": commit})
    return get


def _copie(tmp_path, docker, http, etat=None):
    chemin = tmp_path / ".copie-sprint5.json"
    if etat is not None:
        chemin.write_text(json.dumps(etat), encoding="utf-8")
    return copie.Copie(executer=docker, http_get=http, dormir=lambda s: None, chemin_etat=chemin), chemin


EN_COURS = {"nom": "Era", "motif": "répétition", "depuis": "2026-10-22T16:05:00+02:00",
            "fin_au_plus_tard": "2026-10-22T16:25:00+02:00"}


# --- déployer --------------------------------------------------------------------------------------------------------------

def test_deployer_construit_l_image_du_commit_et_relance_la_copie(tmp_path):
    docker = _Docker()
    outil, chemin = _copie(tmp_path, docker, _http(sante_joignable=False))
    assert outil.deployer(CLE) == 0
    [(construire, env_build), (relancer, env_up)] = docker.compose()
    assert construire[-2:] == ["build", "api"] and relancer[-4:] == ["up", "-d", "postgres", "api"]
    assert env_build["RITA_S5_VERSION"] == "b" * 12 and env_build["RITA_S5_GIT_SHA"] == COMMIT_B
    assert env_build["RITA_S5_CONSTRUIT_LE"]
    assert json.loads(chemin.read_text(encoding="utf-8"))["courante"] == {"version": "b" * 12, "commit": COMMIT_B}


def test_un_second_deploiement_garde_la_version_precedente(tmp_path):
    docker = _Docker()
    outil, chemin = _copie(tmp_path, docker, _http(), etat={"courante": {"version": "a" * 12, "commit": COMMIT_A},
                                                             "precedente": None})
    assert outil.deployer(CLE) == 0
    etat = json.loads(chemin.read_text(encoding="utf-8"))
    assert etat["precedente"] == {"version": "a" * 12, "commit": COMMIT_A}


def test_deployer_pendant_un_exercice_est_refuse(tmp_path, capsys):
    docker = _Docker()
    outil, _ = _copie(tmp_path, docker, _http(exercice=EN_COURS))
    assert outil.deployer(CLE) == 1
    assert docker.compose() == []
    assert "exercice de panne est en cours" in capsys.readouterr().out


def test_un_deploiement_dont_health_n_annonce_pas_le_commit_echoue(tmp_path, capsys):
    outil, chemin = _copie(tmp_path, _Docker(), _http(commit="inconnu", sante_joignable=False))
    assert outil.deployer(CLE) == 1
    assert "n'annonce pas" in capsys.readouterr().out
    assert not chemin.exists()          # l'état ne change pas sur un échec


# --- revenir (rollback) ----------------------------------------------------------------------------------------------------

ETAT_DEUX_VERSIONS = {"courante": {"version": "b" * 12, "commit": COMMIT_B},
                      "precedente": {"version": "a" * 12, "commit": COMMIT_A}}


def test_revenir_relance_l_image_precedente_sans_reconstruire_et_la_verifie(tmp_path, capsys):
    docker = _Docker(image_conteneur="sha256:img-a")
    outil, chemin = _copie(tmp_path, docker, _http(commit=COMMIT_A), etat=ETAT_DEUX_VERSIONS)
    assert outil.revenir(CLE) == 0
    [(relancer, env)] = docker.compose()
    assert relancer[-4:] == ["up", "-d", "--no-build", "api"] and env["RITA_S5_VERSION"] == "a" * 12
    assert all("build" != a for a in relancer)
    etat = json.loads(chemin.read_text(encoding="utf-8"))
    assert etat == {"courante": {"version": "a" * 12, "commit": COMMIT_A}, "precedente": None}
    assert "sha256:img-a" in capsys.readouterr().out


def test_sans_version_precedente_le_retour_est_refuse(tmp_path, capsys):
    docker = _Docker()
    outil, _ = _copie(tmp_path, docker, _http(), etat={"courante": {"version": "b" * 12, "commit": COMMIT_B},
                                                       "precedente": None})
    assert outil.revenir(CLE) == 1
    assert docker.compose() == [] and "aucune version précédente" in capsys.readouterr().out


def test_un_retour_dont_l_image_ne_correspond_pas_echoue(tmp_path, capsys):
    outil, chemin = _copie(tmp_path, _Docker(image_conteneur="sha256:img-b"), _http(commit=COMMIT_A),
                           etat=ETAT_DEUX_VERSIONS)
    assert outil.revenir(CLE) == 1
    assert "image" in capsys.readouterr().out
    assert json.loads(chemin.read_text(encoding="utf-8")) == ETAT_DEUX_VERSIONS


def test_revenir_pendant_un_exercice_est_refuse_et_dit_pourquoi(tmp_path, capsys):
    # Une panne du fournisseur (simulée) ne se règle pas par un retour arrière : on retire d'abord l'exercice.
    docker = _Docker()
    outil, _ = _copie(tmp_path, docker, _http(exercice=EN_COURS), etat=ETAT_DEUX_VERSIONS)
    assert outil.revenir(CLE) == 1
    assert docker.compose() == [] and "ne la règle pas" in capsys.readouterr().out


# --- initialiser, collecter, état -----------------------------------------------------------------------------------------

@pytest.mark.parametrize("action, service", [("initialiser", "initialisation"), ("collecter", "collecte")])
def test_initialiser_et_collecter_lancent_leur_conteneur_ponctuel(tmp_path, action, service):
    docker = _Docker()
    outil, _ = _copie(tmp_path, docker, _http(), etat=ETAT_DEUX_VERSIONS)
    assert getattr(outil, action)() == 0
    [(commande, env)] = docker.compose()
    assert commande[-5:] == ["--profile", "outils", "run", "--rm", service]
    assert env["RITA_S5_VERSION"] == "b" * 12


@pytest.mark.parametrize("action", ["initialiser", "collecter"])
def test_avant_le_premier_deploiement_initialiser_et_collecter_sont_refuses(tmp_path, action, capsys):
    docker = _Docker()
    outil, _ = _copie(tmp_path, docker, _http())
    assert getattr(outil, action)() == 1
    assert docker.compose() == [] and "déployer d'abord" in capsys.readouterr().out


def test_les_commandes_compose_visent_le_projet_et_les_deux_fichiers():
    commande = copie.compose("ps")
    assert commande[:4] == ["docker", "compose", "-p", "rita-s5"]
    assert commande[4:8] == ["-f", str(RACINE / "docker-compose.yml"), "-f", str(RACINE / "docker-compose.sprint5.yml")]


def test_docker_est_appele_sans_shell(tmp_path):
    options_vues = []
    outil, _ = _copie(tmp_path, lambda a, **o: options_vues.append(o) or _Resultat(COMMIT_B), _http(sante_joignable=False))
    outil.deployer(CLE)
    assert options_vues and all(not o.get("shell", False) for o in options_vues)


# --- le fichier Compose du sprint 5, comme un contrat -----------------------------------------------------------------------

@pytest.fixture(scope="module")
def surcharge():
    # Le même chargeur que tests/test_docker_compose.py : PyYAML ne connaît pas la balise `!override` de Compose.
    from tests.test_docker_compose import _ChargeurCompose
    return yaml.load((RACINE / "docker-compose.sprint5.yml").read_text(encoding="utf-8"), Loader=_ChargeurCompose)


@pytest.mark.parametrize("service", ["api", "indexation", "initialisation", "collecte"])
def test_chaque_service_utilise_l_image_du_sprint_5(surcharge, service):
    assert surcharge["services"][service]["image"] == "rita-api:s5-${RITA_S5_VERSION:?RITA_S5_VERSION absente}"


def test_les_conteneurs_et_le_port_sont_ceux_de_la_copie(surcharge):
    services = surcharge["services"]
    assert services["postgres"]["container_name"] == "rita-postgres-s5"
    assert services["api"]["container_name"] == "rita-api-s5"
    assert services["api"]["ports"] == ["8011:8000"]
    assert "ports: !override" in (RACINE / "docker-compose.sprint5.yml").read_text(encoding="utf-8")


def test_le_commit_est_passe_a_la_construction_et_la_cle_d_exercice_au_conteneur(surcharge):
    api = surcharge["services"]["api"]
    assert api["build"]["args"] == {"GIT_SHA": "${RITA_S5_GIT_SHA:-inconnu}",
                                    "CONSTRUIT_LE": "${RITA_S5_CONSTRUIT_LE:-inconnu}"}
    assert api["environment"]["RITA_CLE_EXERCICE"] == "${RITA_CLE_EXERCICE:-}"


def test_le_service_de_collecte_ne_collecte_que_les_cours(surcharge):
    collecte = surcharge["services"]["collecte"]
    assert collecte["profiles"] == ["outils"]
    assert collecte["command"] == ["python", "-m", "pipelines.ingest", "--etapes", "cotations", "--strict"]
    assert collecte["read_only"] is True and "no-new-privileges:true" in collecte["security_opt"]


def test_le_fichier_d_etat_de_la_copie_n_est_jamais_versionne():
    assert ".copie-sprint5.json" in (RACINE / ".gitignore").read_text(encoding="utf-8").splitlines()


@pytest.mark.skipif(shutil.which("docker") is None, reason="Docker absent")
def test_compose_accepte_la_surcharge_et_ne_publie_que_le_port_8011():
    # Compose fusionne lui-même les deux fichiers ; on ne lit que l'image et les ports (la configuration complète
    # contiendrait les clés résolues). Variables fictives, jamais le vrai .env.
    # L'environnement complet du poste (sinon Docker ne trouve plus son greffon compose), plus la version fictive.
    env = {**__import__("os").environ, "RITA_S5_VERSION": "test"}
    sortie = subprocess.run(["docker", "compose", "--env-file", str(RACINE / "tests" / "donnees" / "env-fictif"),
                             "-f", str(RACINE / "docker-compose.yml"), "-f", str(RACINE / "docker-compose.sprint5.yml"),
                             "config", "--format", "json"], capture_output=True, text=True, cwd=RACINE, timeout=60,
                            env=env)
    assert sortie.returncode == 0, sortie.stderr[-400:]
    api = json.loads(sortie.stdout)["services"]["api"]
    assert api["image"] == "rita-api:s5-test"
    assert [(str(p["published"]), p["target"]) for p in api["ports"]] == [("8011", 8000)]


# --- les cas d'échec, l'état, la commande ------------------------------------------------------------------------------

def test_un_retour_dont_health_n_annonce_pas_la_version_echoue(tmp_path, capsys):
    outil, chemin = _copie(tmp_path, _Docker(), _http(commit=COMMIT_B), etat=ETAT_DEUX_VERSIONS)
    assert outil.revenir(CLE) == 1
    assert "n'annonce pas" in capsys.readouterr().out
    assert json.loads(chemin.read_text(encoding="utf-8")) == ETAT_DEUX_VERSIONS


def test_l_attente_survit_a_un_conteneur_qui_demarre_encore(tmp_path):
    reponses = [ConnectionError("pas encore"), _Reponse(200, {"commit": COMMIT_B})]

    def get(url, entetes):
        if url.endswith("/sante"):
            raise ConnectionError("copie arrêtée")
        suivante = reponses.pop(0)
        if isinstance(suivante, Exception):
            raise suivante
        return suivante

    outil, _ = _copie(tmp_path, _Docker(), get)
    assert outil.deployer(CLE) == 0


def test_l_etat_dit_les_versions_et_ce_que_health_annonce(tmp_path, capsys):
    outil, _ = _copie(tmp_path, _Docker(), _http(commit=COMMIT_B), etat=ETAT_DEUX_VERSIONS)
    assert outil.etat() == 0
    sortie = capsys.readouterr().out
    assert f"version courante : {'b' * 12}" in sortie and f"version precedente : {'a' * 12}" in sortie
    assert f"commit {'b' * 12}" in sortie


def test_l_etat_sans_copie_lancee(tmp_path, capsys):
    def injoignable(url, entetes):
        raise ConnectionError("arrêtée")

    outil, _ = _copie(tmp_path, _Docker(), injoignable)
    assert outil.etat() == 0
    sortie = capsys.readouterr().out
    assert "version courante : aucune" in sortie and "ne répond pas" in sortie


@pytest.mark.parametrize("action, methode", [("deployer", "deployer"), ("revenir", "revenir"),
                                             ("initialiser", "initialiser"), ("collecter", "collecter"),
                                             ("etat", "etat")])
def test_la_commande_appelle_la_bonne_action(monkeypatch, action, methode):
    appels = []

    class _Fausse:
        def __getattr__(self, nom):
            return lambda *a: appels.append((nom, a)) or 0

    monkeypatch.setattr(copie, "Copie", _Fausse)
    monkeypatch.setenv("RITA_API_KEY", CLE)
    assert copie.main([action]) == 0
    assert appels[0][0] == methode


def test_une_commande_docker_en_echec_rend_le_code_1_avec_un_message(monkeypatch, capsys):
    class _EnEchec:
        def deployer(self, cle):
            raise subprocess.CalledProcessError(1, ["docker", "compose", "-p", "rita-s5", "build", "api", "--secret"])

    monkeypatch.setattr(copie, "Copie", _EnEchec)
    assert copie.main(["deployer"]) == 1
    sortie = capsys.readouterr().out
    assert "a échoué (code 1)" in sortie and "--secret" not in sortie


def test_l_appel_http_a_un_delai(monkeypatch):
    appels = []
    monkeypatch.setattr(copie.httpx, "get", lambda url, **o: appels.append((url, o)) or "r")
    assert copie._http_get("http://localhost:8011/health", None) == "r"
    assert appels == [("http://localhost:8011/health", {"headers": {}, "timeout": 5.0})]
