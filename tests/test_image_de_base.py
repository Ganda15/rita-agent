"""L'image de base du Dockerfile vient de la galerie publique d'Amazon, pas de Docker Hub sans compte (C13, C19, carte #85).

Le 09/10/2026, la construction de l'image dans `livraison.yml` a échoué trois fois de suite, sur trois exécutions, parce
que Docker Hub refusait le téléchargement de `python:3.13-slim` fait sans compte (429 deux fois, puis 504 sur son serveur
d'authentification), alors que les tests passaient. Le jour du gel, le tag publie l'image pour la première fois : cette
étape ne doit pas dépendre de la limite de Docker Hub. Docker publie ses images officielles aussi dans la galerie
publique d'Amazon ; le 09/10, les deux registres renvoyaient la même empreinte pour `python:3.13-slim` (même image).
"""
import re
from pathlib import Path

RACINE = Path(__file__).parent.parent
SOURCE = "public.ecr.aws/docker/library/"
FROM = re.compile(r"^\s*FROM\s+(\S+)", re.IGNORECASE | re.MULTILINE)


def _images():
    """L'image de chaque instruction FROM du Dockerfile, dans l'ordre."""
    return FROM.findall((RACINE / "Dockerfile").read_text(encoding="utf-8"))


def test_les_deux_etapes_sont_lues():
    """Garde contre un test vide : le Dockerfile a deux étapes (construction, exécution) le 09/10/2026."""
    assert len(_images()) >= 2


def test_chaque_image_de_base_vient_de_la_galerie_publique_amazon():
    fautives = [image for image in _images() if not image.startswith(SOURCE)]
    assert fautives == [], f"images tirées hors de {SOURCE} : {fautives}"


def test_l_image_reste_python_3_13_slim():
    """Changer de registre ne doit pas changer d'image : même nom, même version."""
    assert all(image == SOURCE + "python:3.13-slim" for image in _images())


def test_l_image_de_tests_vient_aussi_de_la_galerie_publique_amazon():
    """`Dockerfile.tests` (image des tests sur le poste, 02/09/2026) suit la même source que l'image livrée : sinon la
    même limite de Docker Hub la casse, et les deux images ne partent plus du même `python:3.13-slim` (10/10/2026)."""
    images = FROM.findall((RACINE / "Dockerfile.tests").read_text(encoding="utf-8"))
    assert images, "aucun FROM lu dans Dockerfile.tests"
    assert all(image == SOURCE + "python:3.13-slim" for image in images), images
