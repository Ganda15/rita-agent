"""Le fichier Compose de pré-production est un contrat : on le teste comme du code (C13).

Revue Codex, PR #1 (19/09/2026) : le service `api` est monté en lecture seule (`read_only: true`,
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


# --- revue Codex, PR #12 : le volume doit être inscriptible par `rita` ET rempli par quelqu'un -------

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
