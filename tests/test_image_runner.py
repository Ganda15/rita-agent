"""L'image des machines de la CI est épinglée : elle ne change pas sans qu'on le décide (C13, C18, C19, carte #84).

Le 05/10/2026, les notices des exécutions annonçaient que le label `ubuntu-latest` passerait à Ubuntu 26 à partir du
19/10/2026, quatre jours après le gel d'E1 et d'E3 et avant la remise du 05/11. Avec ce label, la chaîne pouvait tomber
sans aucun changement de code ; l'incident INC-007 du 03/10 a montré qu'une CI rouge peut passer inaperçue. Chaque
travail tourne donc sur `ubuntu-24.04`, l'image que désignait `ubuntu-latest` à cette date. Changer d'image reste
possible, mais par une décision écrite : ce test échoue tant que l'image attendue n'est pas modifiée ici.
"""
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).parent.parent
FLUX = sorted((RACINE / ".github" / "workflows").glob("*.yml"))
IMAGE = "ubuntu-24.04"


def _travaux():
    """Chaque travail de chaque workflow, avec la valeur de son `runs-on`."""
    trouves = []
    for chemin in FLUX:
        flux = yaml.safe_load(chemin.read_text(encoding="utf-8"))
        for nom, travail in (flux.get("jobs") or {}).items():
            trouves.append((chemin.name, nom, travail.get("runs-on")))
    return trouves


TRAVAUX = _travaux()


def test_les_travaux_sont_bien_lus():
    """Garde contre un test vide : cinq workflows et six travaux existaient le 09/10/2026."""
    assert len(FLUX) >= 5
    assert len(TRAVAUX) >= 6


@pytest.mark.parametrize("fichier,travail,image", TRAVAUX, ids=[f"{f}:{t}" for f, t, _ in TRAVAUX])
def test_chaque_travail_tourne_sur_l_image_epinglee(fichier, travail, image):
    assert image == IMAGE, f"{fichier}, travail « {travail} » : runs-on vaut {image!r}, attendu {IMAGE!r}"


def test_aucun_workflow_ne_vise_ubuntu_latest():
    """Vérification sur le texte brut, au cas où le label apparaîtrait ailleurs (matrice, variable)."""
    fautifs = [chemin.name for chemin in FLUX if "ubuntu-latest" in chemin.read_text(encoding="utf-8")]
    assert fautifs == []
