"""Configuration commune à toute la suite de tests.

Créé le 18/08/2026, en même temps que la correction OWASP API2 : l'API ne retombe
plus sur une clé par défaut `dev-key` et **refuse de démarrer** sans `RITA_API_KEY`.

Les tests doivent donc fournir cette variable eux-mêmes. Ils le font ici, une fois
pour toutes, plutôt que dans chaque fichier : sinon le prochain fichier de tests
échouerait pour une raison qui n'a rien à voir avec ce qu'il vérifie.
"""
import os

import pytest

# Clé utilisée par TOUTE la suite. Elle n'a rien de secret : c'est une valeur de test,
# et le fait qu'elle apparaisse ici est sans conséquence. La vraie clé vit dans `.env`,
# ignoré par Git.
#
# ⚠️ Elle doit respecter la longueur minimale exigée par `api.main.cle_attendue()` —
# sinon les tests échoueraient sur le garde-fou de longueur au lieu de tester leur sujet.
CLE_DE_TEST = "cle-de-test-pour-la-suite-pytest-32c"


@pytest.fixture(autouse=True)
def cle_api_de_test(monkeypatch):
    """Pose `RITA_API_KEY` avant chaque test, et la retire après.

    `autouse=True` : aucun test n'a à la demander. Un test d'API qui l'oublierait
    échouerait avec un `RuntimeError` au démarrage de l'application — un message
    déroutant, sans rapport avec ce qu'il cherche à vérifier.

    `monkeypatch` restaure l'environnement à la fin de chaque test : la suite ne
    laisse aucune trace dans les variables d'environnement du système.
    """
    monkeypatch.setenv("RITA_API_KEY", CLE_DE_TEST)
    yield


@pytest.fixture
def sans_cle_api(monkeypatch):
    """Retire `RITA_API_KEY` — pour vérifier que l'API refuse bien de servir sans elle."""
    monkeypatch.delenv("RITA_API_KEY", raising=False)
    yield


@pytest.fixture(autouse=True)
def couper_le_tracage(monkeypatch):
    """Aucun test n'envoie de trace à Langfuse, même quand les vraies clés sont dans le processus.

    Mesuré le 02/10/2026 : `api/main.py` charge le fichier d'environnement à l'import ; après le
    premier test d'API, les clés réelles étaient là, et la cascade simulée de `test_llm.py` a
    écrit 12 fausses générations (« prompt test » → « ok anthropic ») dans le projet de production.
    Le drapeau `LANGFUSE_TRACING_ENABLED=false` est lu par `src/traces.py` avant toute autre
    chose ; `reinitialiser()` oublie un client qu'un test précédent aurait résolu.
    Les tests de `test_traces.py` qui veulent un client posent eux-mêmes un double.
    """
    from src import traces

    monkeypatch.setenv("LANGFUSE_TRACING_ENABLED", "false")
    traces.reinitialiser()
    yield
    traces.reinitialiser()
