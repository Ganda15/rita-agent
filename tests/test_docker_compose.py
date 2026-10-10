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


def test_l_api_en_conteneur_recoit_les_fournisseurs_approuves_ue(compose):
    """Carte #82 (10/10/2026) : la cascade du conteneur est celle du code, Azure en Data Zone EU puis Mistral par son
    adresse européenne. Jusqu'ici le conteneur ne recevait que les clés d'Anthropic et d'OpenRouter, ordre
    `anthropic,openrouter` par défaut : sans garantie de région, et sans Azure."""
    env = compose["services"]["api"].get("environment") or {}
    for nom in ("AZURE_FOUNDRY_ENDPOINT", "AZURE_FOUNDRY_API_KEY", "AZURE_FOUNDRY_DEPLOYMENT", "MISTRAL_API_KEY", "MISTRAL_MODEL"):
        assert nom in env, f"{nom} absente du service api"
    assert "ANTHROPIC_API_KEY" not in env and "OPENROUTER_API_KEY" not in env
    ordre = str(env.get("LLM_ORDRE", ""))
    assert ordre.startswith("${LLM_ORDRE") and ordre.rstrip("}").endswith(":-foundry,mistral"), ordre


def test_aucune_cle_de_modele_n_est_ecrite_dans_compose(compose):
    env = compose["services"]["api"].get("environment") or {}
    for nom in ("AZURE_FOUNDRY_API_KEY", "MISTRAL_API_KEY"):
        valeur = str(env.get(nom, ""))
        assert valeur.startswith("${" + nom), f"{nom} doit être interpolée depuis l'environnement, pas écrite"
        assert valeur.rstrip("}").endswith(":-"), f"{nom} doit avoir une valeur par défaut VIDE : {valeur}"
