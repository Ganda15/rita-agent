"""Refonte 001, tâche 5 : l'interface ne doit jamais tourner avec un mélange de fichiers anciens et nouveaux.

Mesuré le 04/11 dans le navigateur : sans en-tête `Cache-Control`, Chrome a gardé l'ancien `tableau-de-bord.js` (sans la
garde de simulation) à côté du nouveau `commun.js` ; la page montrait le vrai tableau sous la mention « Simulation ».
Après un déploiement, le navigateur d'Era aurait pu faire de même pendant l'oral. `no-cache` : le navigateur garde sa
copie mais demande à chaque fois si elle a changé ; si non, le serveur répond 304, sans renvoyer le fichier.
"""
import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


@pytest.mark.parametrize("chemin", ["/", "/index.html", "/tableau-de-bord.js", "/commun.js", "/style.css",
                                    "/logo-rita-sombre.png"])
def test_l_interface_est_revalidee_a_chaque_visite(chemin):
    reponse = client.get(chemin)
    assert reponse.status_code == 200
    assert reponse.headers.get("cache-control") == "no-cache", chemin


def test_un_fichier_inchange_repond_304_sans_corps():
    """Éco-conception : revalider coûte un en-tête, pas le fichier."""
    premiere = client.get("/tableau-de-bord.js")
    seconde = client.get("/tableau-de-bord.js", headers={"If-None-Match": premiere.headers["etag"]})
    assert seconde.status_code == 304 and seconde.content == b""


def test_l_api_ne_change_pas_de_regle_de_cache():
    """Seuls les fichiers de l'interface sont concernés : les réponses de l'API gardent leurs en-têtes."""
    assert client.get("/health").headers.get("cache-control") is None
