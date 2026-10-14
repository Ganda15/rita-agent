"""Le fichier Compose de pré-production est un contrat : on le teste comme du code (C13).

Revue automatisée, PR #1 (19/09/2026) : le service `api` est monté en lecture seule (`read_only: true`,
durcissement voulu), mais ChromaDB écrit dans `data/chroma` à l'ouverture de la collection.
Sans montage inscriptible à cet endroit, `/briefing` échouait pour tout ticker valide, en
conteneur seulement — invisible en local. Un test le rend impossible à perdre.
"""
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).parent.parent
CHEMIN_CHROMA_CONTENEUR = "/app/data/chroma"


@pytest.fixture(scope="module")
def compose():
    return yaml.safe_load((RACINE / "docker-compose.yml").read_text(encoding="utf-8"))


def _montages(service: dict) -> list[str]:
    """Les cibles des volumes d'un service, sous les deux formes acceptées par Compose."""
    cibles = []
    for v in service.get("volumes", []) or []:
        if isinstance(v, str):
            cibles.append(v.split(":")[1] if ":" in v else v)
        elif isinstance(v, dict):
            cibles.append(v.get("target", ""))
    return cibles


def test_l_api_reste_en_lecture_seule(compose):
    assert compose["services"]["api"].get("read_only") is True


def test_chroma_a_un_montage_inscriptible_dans_l_api_en_lecture_seule(compose):
    api = compose["services"]["api"]
    assert CHEMIN_CHROMA_CONTENEUR in _montages(api), (
        f"aucun volume monté sur {CHEMIN_CHROMA_CONTENEUR} : ChromaDB ne peut pas s'initialiser")


def test_le_volume_chroma_est_declare_et_persistant(compose):
    api = compose["services"]["api"]
    noms = [v.split(":")[0] for v in api.get("volumes", []) if isinstance(v, str) and ":" in v
            and v.split(":")[1] == CHEMIN_CHROMA_CONTENEUR]
    assert noms, "le montage Chroma doit être un volume nommé, pas un tmpfs : l'index survit au redémarrage"
    assert noms[0] in (compose.get("volumes") or {}), f"volume {noms[0]} non déclaré en tête de fichier"


# --- revue automatisée, PR #12 : le volume doit être inscriptible par `rita` ET rempli par quelqu'un -------

def test_le_dossier_chroma_est_cree_et_donne_a_rita_avant_de_changer_d_utilisateur():
    """Un volume nommé hérite, à sa création, du propriétaire du dossier dans l'image. Sans `chown`
    avant `USER rita`, le point de montage est à root et ChromaDB (UID 10001) ne peut rien y écrire."""
    lignes = (RACINE / "Dockerfile").read_text(encoding="utf-8").splitlines()
    i_user = next(i for i, l in enumerate(lignes) if l.strip() == "USER rita")
    prepare = [i for i, l in enumerate(lignes)
               if "data/chroma" in l and "mkdir" in l and "chown" in l and "rita" in l]
    assert prepare, "aucune ligne `mkdir ... data/chroma ... chown rita` dans le Dockerfile"
    assert prepare[0] < i_user, "le dossier Chroma doit être préparé AVANT `USER rita`"


def test_un_service_compose_remplit_le_volume_chroma(compose):
    """Le volume nommé démarre vide et l'indexation planifiée écrit sur l'hôte, pas dans le conteneur.
    Un service `indexation` (profil `outils`, jamais démarré par défaut) partage le volume et lance
    l'étape d'indexation contre le PostgreSQL de Compose : `docker compose run --rm indexation`."""
    services = compose["services"]
    assert "indexation" in services, "service `indexation` absent"
    s = services["indexation"]
    assert CHEMIN_CHROMA_CONTENEUR in _montages(s)
    assert s.get("image") == services["api"].get("image"), "même image que l'API : même code, même Chroma"
    assert "outils" in (s.get("profiles") or []), "profil `outils` : ne démarre pas avec `docker compose up`"
    commande = " ".join(s["command"]) if isinstance(s.get("command"), list) else str(s.get("command"))
    assert "pipelines.ingest" in commande and "indexation" in commande


# --- revue automatisée, PR #13 : le modèle d'embedding se télécharge dans ~/.cache — impossible en lecture seule ---

CHEMIN_CACHE_CONTENEUR = "/home/rita/.cache"


@pytest.mark.parametrize("service", ["api", "indexation"])
def test_le_cache_du_modele_d_embedding_est_inscriptible(compose, service):
    """ChromaDB télécharge `all-MiniLM-L6-v2` sous `~/.cache/chroma/onnx_models` au premier `upsert`
    ET à la première `query`. Racine en lecture seule + rien de monté là = ni indexation ni recherche
    en conteneur. Un volume nommé partagé par les deux services, persistant : un seul téléchargement."""
    s = compose["services"][service]
    assert CHEMIN_CACHE_CONTENEUR in _montages(s), f"{service} : aucun montage inscriptible sur {CHEMIN_CACHE_CONTENEUR}"
    noms = [v.split(":")[0] for v in s.get("volumes", []) if isinstance(v, str) and v.split(":")[1] == CHEMIN_CACHE_CONTENEUR]
    assert noms and noms[0] in (compose.get("volumes") or {}), "le cache doit être un volume nommé déclaré"


# --- audit du 02/10/2026 : le conteneur ne traçait pas, Compose ne transmettait aucune variable Langfuse ---

VARIABLES_LANGFUSE = ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST", "LANGFUSE_TRACING_ENABLED")


def test_l_api_recoit_les_variables_langfuse(compose):
    """Sans ces variables, `src/traces.py` est un no-op silencieux : l'API en conteneur
    (pré-production et serveur) servait des briefings que Langfuse ne voyait jamais, et la
    preuve C11 n'existait qu'en local. Constaté par l'audit du 02/10/2026."""
    env = compose["services"]["api"].get("environment") or {}
    manquantes = [v for v in VARIABLES_LANGFUSE if v not in env]
    assert not manquantes, f"variables Langfuse absentes du service api : {manquantes}"


def test_aucune_cle_langfuse_n_est_ecrite_dans_compose(compose):
    """Une clé se lit dans l'environnement de la machine, jamais dans un fichier versionné.
    La forme attendue est `${NOM:-}` : interpolée, et vide par défaut pour que l'absence de
    compte Langfuse laisse l'API démarrer (le traçage se coupe tout seul sans clés)."""
    env = compose["services"]["api"].get("environment") or {}
    for nom in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"):
        valeur = str(env.get(nom, ""))
        assert valeur.startswith("${" + nom), f"{nom} doit être interpolée depuis l'environnement, pas écrite"
        assert valeur.rstrip("}").endswith(":-"), f"{nom} doit avoir une valeur par défaut VIDE : {valeur}"


def test_le_tracage_en_conteneur_peut_etre_coupe_sans_toucher_aux_cles(compose):
    """`LANGFUSE_TRACING_ENABLED=false` dans l'environnement de la machine doit suffire à
    couper le traçage du conteneur : c'est l'interrupteur que `src/traces.py` lit déjà."""
    env = compose["services"]["api"].get("environment") or {}
    assert str(env.get("LANGFUSE_TRACING_ENABLED", "")).startswith("${LANGFUSE_TRACING_ENABLED")


# --- relevé du 11/10/2026 : le conteneur sautait Azure, premier fournisseur de la cascade ---

VARIABLES_AZURE = ("AZURE_FOUNDRY_ENDPOINT", "AZURE_FOUNDRY_API_KEY", "AZURE_FOUNDRY_DEPLOYMENT")


def test_l_api_recoit_les_variables_azure(compose):
    """Compose ne transmet au conteneur que ce qui est listé sous `environment:`. Les trois
    variables Azure n'y étaient pas : en conteneur, `foundry` échouait faute de clé et la cascade
    passait au fournisseur suivant. La clé reste interpolée, vide par défaut, jamais écrite."""
    env = compose["services"]["api"].get("environment") or {}
    manquantes = [v for v in VARIABLES_AZURE if v not in env]
    assert not manquantes, f"variables Azure absentes du service api : {manquantes}"
    for nom in VARIABLES_AZURE:
        assert str(env[nom]).startswith("${" + nom), f"{nom} doit être interpolée depuis l'environnement"
    cle = str(env["AZURE_FOUNDRY_API_KEY"])
    assert cle.rstrip("}").endswith(":-"), f"la clé Azure doit avoir une valeur par défaut VIDE : {cle}"


def test_le_conteneur_garde_l_ordre_par_defaut_du_code(compose, monkeypatch):
    """Sans `LLM_ORDRE` dans l'environnement, Compose remplace l'ordre du code par sa propre
    valeur par défaut (`${LLM_ORDRE:-...}`). Les deux doivent donner la même cascade : on compare
    le comportement réel de `_ordre_fournisseurs()`, pas le texte de `src/llm.py`."""
    from src.llm import _ordre_fournisseurs

    monkeypatch.delenv("LLM_ORDRE", raising=False)
    valeur = str((compose["services"]["api"].get("environment") or {}).get("LLM_ORDRE", ""))
    assert valeur.startswith("${LLM_ORDRE:-") and valeur.endswith("}"), f"forme inattendue : {valeur}"
    defaut_compose = [nom.strip() for nom in valeur[len("${LLM_ORDRE:-"):-1].split(",") if nom.strip()]
    assert defaut_compose == _ordre_fournisseurs()


# --- Sprint 2, tâche 6 : reconstruire RITA depuis le dépôt (service `initialisation`, surcharge de démonstration) ----

import json as _json
import shutil as _shutil
import subprocess as _subprocess


class _ChargeurCompose(yaml.SafeLoader):
    """PyYAML ne connaît pas les balises de Compose (`!override`, `!reset`) : elles sont lues comme la valeur nue."""


for _balise in ("!override", "!reset"):
    _ChargeurCompose.add_constructor(
        _balise, lambda chargeur, noeud: chargeur.construct_sequence(noeud) if isinstance(noeud, yaml.SequenceNode)
        else chargeur.construct_mapping(noeud) if isinstance(noeud, yaml.MappingNode)
        else chargeur.construct_scalar(noeud))


def _demo():
    return yaml.load((RACINE / "docker-compose.demo.yml").read_text(encoding="utf-8"), Loader=_ChargeurCompose)


def test_le_service_initialisation_remplit_une_base_neuve_puis_l_index(compose):
    service = compose["services"]["initialisation"]
    assert service["profiles"] == ["outils"] and service["image"] == "rita-api:local"
    assert service["depends_on"]["postgres"]["condition"] == "service_healthy"
    # Le compte propriétaire, comme `indexation` : il faut écrire dans la base de démonstration et poser sa marque.
    assert service["environment"]["DATABASE_URL"] == compose["services"]["indexation"]["environment"]["DATABASE_URL"]
    montages = service["volumes"]          # la liste brute : source, destination, mode
    assert "./data/demo:/app/data/demo:ro" in montages
    assert "rita_chroma_preprod:/app/data/chroma" in montages and "rita_cache_preprod:/home/rita/.cache" in montages
    commande = " ".join(service["command"]) if isinstance(service["command"], list) else service["command"]
    assert "python -m db.importer --demo /app/data/demo" in commande
    assert "python -m pipelines.ingest --etapes indexation --strict" in commande
    assert commande.index("db.importer") < commande.index("pipelines.ingest")      # la base d'abord, l'index ensuite
    assert service["read_only"] is True and "/tmp" in service["tmpfs"]
    assert "no-new-privileges:true" in service["security_opt"]


def test_la_surcharge_de_demonstration_isole_les_conteneurs_et_le_port():
    services = _demo()["services"]
    for nom in ("postgres", "api"):
        assert "${RITA_DEMO_ID:?" in services[nom]["container_name"], nom
    assert services["api"]["ports"] == ["${RITA_DEMO_PORT:-8011}:8000"]
    texte = (RACINE / "docker-compose.demo.yml").read_text(encoding="utf-8")
    assert "ports: !override" in texte          # remplace la liste de l'API au lieu de s'y ajouter


@pytest.mark.skipif(_shutil.which("docker") is None, reason="Docker absent : la chaîne et le poste l'ont")
def test_la_surcharge_ne_publie_que_le_port_de_demonstration():
    # Compose lui-même fusionne les deux fichiers ; on n'affiche jamais la configuration complète (elle contient les
    # clés résolues) : seulement les ports de l'API. Le fichier d'environnement est fictif et versionné.
    sortie = _subprocess.run(
        ["docker", "compose", "--env-file", str(RACINE / "tests" / "donnees" / "env-fictif"),
         "-f", str(RACINE / "docker-compose.yml"), "-f", str(RACINE / "docker-compose.demo.yml"),
         "config", "--format", "json"], capture_output=True, text=True, cwd=RACINE, timeout=60)
    assert sortie.returncode == 0, sortie.stderr[-400:]
    ports = _json.loads(sortie.stdout)["services"]["api"]["ports"]
    assert len(ports) == 1 and str(ports[0]["published"]) == "8011" and ports[0]["target"] == 8000
