"""Carte #76, tâche T2 : une seule fonction donne à l'API l'adresse de sa base (plan validé le 06/11/2026).

`POSTGRES_DSN_API` (le rôle `rita_api`) si elle existe, sinon `DATABASE_URL` : le poste de développement ne change pas.
Les deux lecteurs de la base dans le processus de l'API, `sources/database.py` et `indicateurs/socle.py`, passent par
elle. L'import et la collecte (`db/importer.py`, `pipelines/ingest.py`) gardent `DATABASE_URL`, le propriétaire : ce sont
les seuls à écrire.
"""
import pytest

from indicateurs import socle
from sources import database


@pytest.fixture
def adresses(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://rita@hote/base_proprietaire")
    monkeypatch.delenv("POSTGRES_DSN_API", raising=False)
    return monkeypatch


def test_sans_adresse_dediee_l_api_prend_database_url(adresses):
    assert database.dsn_api() == "postgresql://rita@hote/base_proprietaire"


def test_avec_l_adresse_dediee_l_api_prend_le_role_rita_api(adresses):
    adresses.setenv("POSTGRES_DSN_API", "postgresql://rita_api@hote/base")
    assert database.dsn_api() == "postgresql://rita_api@hote/base"


def test_les_requetes_de_l_api_se_connectent_a_l_adresse_dediee(adresses):
    adresses.setenv("POSTGRES_DSN_API", "postgresql://rita_api@hote/base")
    vues = []
    adresses.setattr(database.psycopg2, "connect", lambda dsn, **_: vues.append(dsn) or (_ for _ in ()).throw(RuntimeError))
    with pytest.raises(RuntimeError):
        database._connexion()
    assert vues == ["postgresql://rita_api@hote/base"]


def test_le_socle_des_indicateurs_se_connecte_a_la_meme_adresse(adresses):
    adresses.setenv("POSTGRES_DSN_API", "postgresql://rita_api@hote/base")
    vues = []
    adresses.setattr(socle.psycopg2, "connect", lambda dsn, **_: vues.append(dsn) or (_ for _ in ()).throw(RuntimeError))
    with pytest.raises(RuntimeError):
        socle._executer("select 1")
    assert vues == ["postgresql://rita_api@hote/base"]


def test_une_adresse_passee_explicitement_garde_la_priorite(adresses):
    adresses.setenv("POSTGRES_DSN_API", "postgresql://rita_api@hote/base")
    vues = []
    adresses.setattr(database.psycopg2, "connect", lambda dsn, **_: vues.append(dsn) or (_ for _ in ()).throw(RuntimeError))
    with pytest.raises(RuntimeError):
        database._connexion("postgresql://autre@hote/base")
    assert vues == ["postgresql://autre@hote/base"]
