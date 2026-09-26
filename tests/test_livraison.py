"""La chaîne de livraison est un contrat : l'image publiée doit être l'image vérifiée (C19).

Vérification des critères E4 du 26/09/2026 (issue #22) : sur un tag `livrable-*`,
`livraison.yml` publiait l'image dans l'étape de construction, AVANT l'étape « Vérifier que
l'image démarre et répond ». Et cette vérification reconstruisait sa propre image : ce
n'était même pas l'image publiée qui était testée. La branche « publier sur tag » n'avait
jamais tourné, le défaut était donc invisible. Ces tests le rendent impossible à réintroduire.
"""
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).parent.parent
DEMARRE = "Vérifier que l'image démarre et répond"
ACCES = "Vérifier que l'accès est bien restreint"


@pytest.fixture(scope="module")
def etapes():
    flux = yaml.safe_load((RACINE / ".github/workflows/livraison.yml").read_text(encoding="utf-8"))
    return flux["jobs"]["construire-et-publier"]["steps"]


def _indice(etapes, nom):
    return next(i for i, e in enumerate(etapes) if e.get("name") == nom)


def _indice_publication(etapes):
    indices = [i for i, e in enumerate(etapes) if "docker push" in (e.get("run") or "")]
    assert indices, "aucune étape ne publie l'image vérifiée (docker push)"
    return indices[0]


def test_la_construction_ne_publie_jamais(etapes):
    """Publier pendant la construction, c'est publier avant toute vérification."""
    for e in etapes:
        if "docker/build-push-action" in (e.get("uses") or ""):
            assert e.get("with", {}).get("push", False) is False, e.get("name")


def test_la_verification_teste_l_image_construite_sans_la_reconstruire(etapes):
    """Une seconde construction produirait une autre image que celle qui sera publiée."""
    assert "docker build" not in etapes[_indice(etapes, DEMARRE)]["run"]


def test_la_publication_vient_apres_les_deux_verifications_et_seulement_sur_un_tag(etapes):
    publication = _indice_publication(etapes)
    assert publication > _indice(etapes, DEMARRE)
    assert publication > _indice(etapes, ACCES)
    assert "refs/tags/livrable-" in etapes[publication].get("if", "")
