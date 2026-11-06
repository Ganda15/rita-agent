"""Décision D7 (06/11/2026) : la documentation de l'API reste publique ; ce que cela suppose est tenu par ces tests.

Pourquoi : la règle de fermeture de la matrice d'accès refuse toute ressource qui n'est pas listée
(`evidence/C17/preuve-droits-acces-2026-10-03.md`, ligne 6). D7 liste la documentation (`/docs`, `/redoc`,
`/openapi.json`) comme ressource publique. Cette décision ne tient que si le contrat publié ne contient ni secret ni
donnée personnelle, et si chaque route protégée refuse une clé absente ou fausse, quoi que dise la documentation.
"""
import json
import re

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)
CONTRAT = client.get("/openapi.json").text
PUBLICS = {"/health"}
SECRETS = {
    "clé de type sk ou pk": r"\b(?:sk|pk)-[A-Za-z0-9-]{8,}",
    "adresse de base de données": r"postgres(?:ql)?://",
    "courriel": r"[\w.+-]+@[\w-]+\.[a-z]{2,}",
    "adresse IP": r"\b\d{1,3}(?:\.\d{1,3}){3}\b",
    "jeton hexadécimal long": r"\b[0-9a-f]{32,}\b",
    "adresse d'Azure": r"(?i)openai\.azure\.com|cognitiveservices",
    "mot de passe": r"(?i)\bpassword\b|mot de passe",
}


@pytest.mark.parametrize("nom", SECRETS)
def test_le_contrat_publie_ne_contient_aucun_secret(nom):
    assert not re.search(SECRETS[nom], CONTRAT), nom


def test_les_seuls_exemples_du_contrat_sont_des_messages_d_erreur():
    exemples = re.findall(r'"examples?"\s*:\s*(\{.*?\})\s*[,}]', CONTRAT)
    for exemple in exemples:
        assert '"detail"' in exemple   # un corps d'erreur, jamais une donnée


def _routes_protegees():
    for chemin, operations in json.loads(CONTRAT)["paths"].items():
        if chemin in PUBLICS:
            continue
        for verbe in operations:
            yield verbe, chemin.replace("{article_id}", "1")


def test_toutes_les_routes_sauf_health_declarent_la_cle():
    contrat = json.loads(CONTRAT)
    sans_cle = [(v, c) for c, ops in contrat["paths"].items() if c not in PUBLICS for v, op in ops.items()
                if not op.get("security")]
    assert sans_cle == []


@pytest.mark.parametrize("verbe,chemin", [r for r in _routes_protegees() if not r[1].startswith("/exercice/")])
@pytest.mark.parametrize("entetes", [{}, {"X-API-Key": "cle-fausse-pour-le-test"}], ids=["sans-cle", "cle-fausse"])
def test_une_route_protegee_refuse_une_cle_absente_ou_fausse(verbe, chemin, entetes):
    reponse = client.request(verbe.upper(), chemin, headers=entetes)
    assert reponse.status_code in (401, 403), (verbe, chemin, reponse.status_code)


# Les exercices ont leur propre clé (`X-Cle-Exercice`, `api/exercice.py`). Sans `RITA_CLE_EXERCICE` sur le serveur, ce qui
# est le cas en production, ils sont coupés et répondent 503 sans rien poser ; avec elle, une clé absente ou fausse : 403.
EXERCICES = ["/exercice/panne", "/exercice/fin"]


@pytest.mark.parametrize("chemin", EXERCICES)
def test_un_exercice_est_coupe_sans_cle_d_exercice_sur_le_serveur(monkeypatch, chemin):
    monkeypatch.delenv("RITA_CLE_EXERCICE", raising=False)
    assert client.post(chemin, headers={"X-Cle-Exercice": "cle-fausse-pour-le-test"}).status_code == 503


@pytest.mark.parametrize("chemin", EXERCICES)
@pytest.mark.parametrize("entetes", [{}, {"X-Cle-Exercice": "cle-fausse-pour-le-test"}], ids=["sans-cle", "cle-fausse"])
def test_un_exercice_actif_refuse_une_cle_d_exercice_absente_ou_fausse(monkeypatch, chemin, entetes):
    monkeypatch.setenv("RITA_CLE_EXERCICE", "cle-d-exercice-du-test-assez-longue")
    assert client.post(chemin, headers=entetes).status_code == 403
