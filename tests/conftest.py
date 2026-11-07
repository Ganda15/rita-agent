"""Configuration commune à toute la suite de tests.

Créé le 18/08/2026, en même temps que la correction OWASP API2 : l'API ne retombe
plus sur une clé par défaut `dev-key` et **refuse tout accès protégé** sans `RITA_API_KEY`.

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


def pytest_configure(config):
    # 02/11/2026 : le marqueur des tests qui demandent PostgreSQL ; le job `base` de la CI les choisit par lui.
    config.addinivalue_line("markers", "postgresql: test qui demande la base PostgreSQL de test (job base de la CI)")


def pytest_collection_finish(session):
    """Donne à `tests/garde_base.py` la liste des tests marqués : `dsn_de_test()` refuse un test qui ne l'est pas."""
    from tests import garde_base
    garde_base.TESTS_MARQUES.clear()
    garde_base.TESTS_MARQUES.update(item.nodeid for item in session.items
                                    if item.get_closest_marker(garde_base.MARQUEUR))


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


@pytest.fixture(autouse=True)
def valeurs_connues_par_defaut(monkeypatch):
    """Pendant les tests, toute valeur demandée à `/briefing` est connue du référentiel (sprint 4, tâche C1).

    La route vérifie dans la base que la valeur existe avant tout appel au modèle (critère 3 du contrat du sprint 1).
    Les tests de la route n'ont pas de base (la CI) ou une base de test vide : sans cette règle, tous ceux qui appellent
    `/briefing` recevraient une erreur ou un 422 sans rapport avec ce qu'ils vérifient. Les tests du 422
    (`tests/test_briefing_422.py`) remplacent cette règle ; `raising=False` la pose même avant que la vérification
    n'existe.
    """
    import api.main

    monkeypatch.setattr(api.main, "valeur_existe", lambda ticker: True, raising=False)
    yield


@pytest.fixture(autouse=True)
def limiteur_neuf(monkeypatch):
    """Chaque test part d'un limiteur de débit neuf, au quota assez haut pour ne jamais gêner (sprint 4, tâche C3).

    Le limiteur garde son compte en mémoire, d'un appel à l'autre : sans cette règle, la suite complète atteindrait le
    quota de `/briefing` et `/question`, et les tests suivants recevraient un 429 sans rapport avec ce qu'ils vérifient.
    Les tests du limiteur (`tests/test_limiteur.py`) posent leur propre quota.
    """
    from api import limiteur

    monkeypatch.setattr(limiteur, "LIMITEUR", limiteur.Limiteur(10_000))
    # Même raison pour le frein des essais de clé (constat S3, 07/11) : beaucoup de tests envoient une mauvaise clé.
    # Ses propres tests (`tests/test_essais_de_cle.py`) posent le seuil du plan, 10.
    monkeypatch.setattr(limiteur, "FREIN", limiteur.FreinDesEssais(seuil=10_000))
    yield


def faux_resultat_texte(texte: str = "x"):
    """Ce que la cascade rend réellement depuis la refonte 001 (tâche 1) : le texte et qui l'a écrit.

    Les tests qui remplacent le modèle rendent cet objet, jamais une simple chaîne : un faux qui diverge du code
    donne des tests verts sur du code cassé (défaut du 28/08).
    """
    from src.llm import ResultatTexte

    return ResultatTexte(texte=texte, fournisseur="foundry", modele="gpt-5.4-2026-03-05",
                         tentatives=[{"fournisseur": "foundry", "reussi": True}])
