"""L'image de base du Dockerfile vient du miroir public de Docker Hub tenu par Google (C13, C19, carte #85, puis 21/10).

Historique, daté :
- 09/10/2026 : Docker Hub refuse trois constructions de suite (téléchargement sans compte : 429 deux fois, puis 504 sur
  son serveur d'authentification), alors que les tests passaient. L'image passe à la galerie publique d'Amazon
  (`public.ecr.aws`), qui renvoyait la même empreinte pour `python:3.13-slim` (carte #85).
- 16 au 21/10/2026 : la galerie d'Amazon refuse à son tour, 19 fois (429, « Data limit exceeded » : 11 au sprint 3,
  8 au sprint 4), y compris un matin après une nuit sans aucune construction. Attendre ne suffit plus.
- 21/10/2026 : `mirror.gcr.io`, le miroir public de Docker Hub tenu par Google, rend `python:3.13-slim` sans compte,
  avec la même empreinte que la galerie d'Amazon le même jour (`sha256:98ce6fb1…`) : c'est la même image.

Limite : c'est encore un registre sans compte. La solution durable reste un compte (Docker Hub ou Amazon), avec des
secrets posés dans GitHub.
"""
import re
from pathlib import Path

RACINE = Path(__file__).parent.parent
SOURCE = "mirror.gcr.io/library/"
FROM = re.compile(r"^\s*FROM\s+(\S+)", re.IGNORECASE | re.MULTILINE)


def _images():
    """L'image de chaque instruction FROM du Dockerfile, dans l'ordre."""
    return FROM.findall((RACINE / "Dockerfile").read_text(encoding="utf-8"))


def test_les_deux_etapes_sont_lues():
    """Garde contre un test vide : le Dockerfile a deux étapes (construction, exécution) le 09/10/2026."""
    assert len(_images()) >= 2


def test_chaque_image_de_base_vient_du_miroir_de_google():
    fautives = [image for image in _images() if not image.startswith(SOURCE)]
    assert fautives == [], f"images tirées hors de {SOURCE} : {fautives}"


def test_l_image_reste_python_3_13_slim():
    """Changer de registre ne doit pas changer d'image : même nom, même version."""
    assert all(image == SOURCE + "python:3.13-slim" for image in _images())


def test_l_image_de_tests_vient_aussi_du_miroir_de_google():
    """`Dockerfile.tests` (image des tests sur le poste, 02/09/2026) suit la même source que l'image livrée : sinon la
    même limite la casse, et les deux images ne partent plus du même `python:3.13-slim` (10/10/2026)."""
    images = FROM.findall((RACINE / "Dockerfile.tests").read_text(encoding="utf-8"))
    assert images, "aucun FROM lu dans Dockerfile.tests"
    assert all(image == SOURCE + "python:3.13-slim" for image in images), images
