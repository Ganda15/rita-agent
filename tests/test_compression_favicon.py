"""Éco-conception, carte #74 (constats F1 et F3 de la mesure Lighthouse et EcoIndex du 03/10/2026).

Pourquoi : la mesure du 03/10 (`evidence/C17/preuve-eco-conception-et-accessibilite-2026-10-03.md`) a relevé qu'aucune
réponse n'était compressée (F1 ; gain mesuré en gzip : statique -62 %, JSON des indicateurs -84 %) et que `favicon.ico`
répondait 404 (F3 : une erreur dans la console, Bonnes pratiques à 96). Relevé de nouveau en production le 06/11 : même
état. F2 (en-têtes de cache des fichiers statiques) est traité depuis le 04/11 (`tests/test_cache_frontend.py`).
"""
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_un_fichier_de_l_interface_est_compresse_quand_le_navigateur_l_accepte():
    reponse = client.get("/style.css", headers={"Accept-Encoding": "gzip"})
    assert reponse.status_code == 200
    assert reponse.headers.get("content-encoding") == "gzip"


def test_sans_accord_du_navigateur_la_reponse_n_est_pas_compressee():
    reponse = client.get("/style.css", headers={"Accept-Encoding": "identity"})
    assert reponse.status_code == 200
    assert "content-encoding" not in reponse.headers


def test_la_compression_garde_la_regle_de_cache_de_l_interface():
    reponse = client.get("/index.html", headers={"Accept-Encoding": "gzip"})
    assert reponse.headers.get("content-encoding") == "gzip"
    assert reponse.headers.get("cache-control") == "no-cache"


def test_une_petite_reponse_n_est_pas_compressee_pour_rien():
    reponse = client.get("/health", headers={"Accept-Encoding": "gzip"})
    assert reponse.status_code == 200
    assert "content-encoding" not in reponse.headers


def test_favicon_ico_ne_repond_plus_404():
    reponse = client.get("/favicon.ico")
    assert reponse.status_code == 200
    assert reponse.headers.get("content-type", "").startswith("image/")
