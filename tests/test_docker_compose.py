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
