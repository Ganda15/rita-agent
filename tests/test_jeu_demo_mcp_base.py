"""#152 : le jeu de démonstration attendu par la passerelle MCP est bien ce que le vrai import produit (01/11/2026).

`passerelle_mcp/jeu_demo_attendu.csv` est la référence du verrou de démonstration. Ce fichier la relie au code qui écrit
en base : sur la base de test, dans une transaction annulée, l'univers puis le fichier d'exemple passent par
`db/importer.py` (les fonctions de production, pas une copie), la requête R1 lit le résultat, la route
`/donnees/portefeuille` le met en forme, FastAPI le sérialise, et la passerelle doit le servir. Une position personnelle
ou une position close ajoutée ensuite doit le faire refuser.

Sauté sans base de test déclarée (`tests/garde_base.py`) ; en CI, le job `base` fait échouer tout saut.
"""
import json
import os
from collections import Counter
from unittest.mock import patch

import pytest

psycopg2 = pytest.importorskip("psycopg2")

from db.importer import charger_univers, importer_positions, importer_valeurs  # noqa: E402
from passerelle_mcp import serveur as passerelle  # noqa: E402
from sources.positions import EXEMPLE  # noqa: E402


# 02/11/2026 : chaque test de ce fichier demande PostgreSQL ; le job `base` de la CI les choisit par ce marqueur.
pytestmark = pytest.mark.postgresql


@pytest.fixture
def curseur(monkeypatch):
    # Le fichier fictif du dépôt, imposé : jamais le portefeuille réel qu'un POSITIONS_CSV du poste désignerait. Poser la
    # variable (plutôt que l'effacer) tient même si un module importé plus tard relit le `.env` : `load_dotenv` ne
    # remplace jamais une variable déjà posée. `_importer_le_jeu_d_exemple` le vérifie avant d'écrire.
    monkeypatch.setenv("POSITIONS_CSV", str(EXEMPLE))
    from tests.garde_base import dsn_de_test
    try:
        con = psycopg2.connect(dsn_de_test(), connect_timeout=3)
    except psycopg2.OperationalError as e:
        pytest.skip(f"PostgreSQL injoignable : {e}")
    except UnicodeDecodeError:
        # Même cas que `tests/test_indicateurs_risque_base.py` : message du serveur en Windows-1252, illisible.
        pytest.skip("connexion refusée par PostgreSQL : vérifier le compte et le mot de passe de la base de test")
    con.autocommit = False
    cur = con.cursor()
    yield cur
    con.rollback()
    con.close()


def _importer_le_jeu_d_exemple(cur) -> dict:
    assert os.environ.get("POSITIONS_CSV") == str(EXEMPLE), "l'import ne lit que le fichier fictif du dépôt"
    importer_valeurs(cur, *charger_univers())
    return importer_positions(cur)


def _reponse_de_l_api(cur) -> dict:
    """Ce que `GET /donnees/portefeuille` rendrait sur cette transaction : la requête R1 du dépôt, la route elle-même
    (ses deux lectures remplacées par celles de la transaction), puis la sérialisation de FastAPI."""
    from fastapi.encoders import jsonable_encoder

    from api import donnees
    from sources import database

    cur.execute(database.SQL_PORTEFEUILLE)
    noms = [c.name for c in cur.description]
    lignes = [dict(zip(noms, r)) for r in cur.fetchall()]
    cur.execute("SELECT count(*) FROM position WHERE date_cloture IS NOT NULL")
    closes = cur.fetchone()[0]
    extraction = database.Extraction(nom="portefeuille", lignes=lignes, nb=len(lignes))
    with patch.object(database, "portefeuille", return_value=extraction), \
         patch.object(database, "positions_closes", return_value=closes):
        corps = donnees.portefeuille()
    return json.loads(json.dumps(jsonable_encoder(corps)))


def test_le_vrai_import_du_fichier_d_exemple_donne_le_jeu_attendu_et_la_passerelle_le_sert(curseur):
    bilan = _importer_le_jeu_d_exemple(curseur)
    assert (bilan["lignes"], bilan["ignorees"]) == (7, 3), "TTE.PA, AAPL et MSFT sont hors univers"
    curseur.execute("SELECT ticker, quantite, pru, devise FROM position WHERE date_cloture IS NULL")
    en_base = Counter(tuple(r) for r in curseur.fetchall())
    assert en_base == passerelle._jeu_attendu(), "NUMERIC de la base et fichier versionné, comparés sans arrondi"
    # Une ligne avec un cours, les six autres sans : les deux formes que la requête R1 rend passent les contrôles.
    curseur.execute("INSERT INTO cotation (ticker, date_seance, ouverture, haut, bas, cloture, volume) "
                    "VALUES ('MC.PA', '2026-10-30', 690, 700, 680, 695.6, 1000)")
    servie = passerelle._reponse_de_demonstration(_reponse_de_l_api(curseur))
    assert servie is not None and servie["nb"] == 7
    mc = next(p for p in servie["positions"] if p["ticker"] == "MC.PA")
    assert (mc["cours"], mc["date_cours"], mc["valorisation_eur"]) == (695.6, "2026-10-30", 8347.2)
    assert servie["total_eur"] is None, "six lignes sans cotation : pas de total"


def test_une_position_personnelle_ajoutee_apres_l_import_fait_refuser(curseur):
    _importer_le_jeu_d_exemple(curseur)
    assert passerelle._reponse_de_demonstration(_reponse_de_l_api(curseur)) is not None, "servi avant l'ajout"
    curseur.execute("INSERT INTO position (ticker, quantite, pru, devise, date_achat) "
                    "VALUES ('MC.PA', 3, 710, 'EUR', '2025-02-03')")
    assert passerelle._reponse_de_demonstration(_reponse_de_l_api(curseur)) is None


def test_une_position_close_dans_la_base_fait_refuser_le_mode_strict(curseur):
    _importer_le_jeu_d_exemple(curseur)
    assert passerelle._reponse_de_demonstration(_reponse_de_l_api(curseur)) is not None, "servi avant l'ajout"
    curseur.execute("INSERT INTO position (ticker, quantite, pru, devise, date_achat, date_cloture) "
                    "VALUES ('OR.PA', 2, 300, 'EUR', '2024-01-02', CURRENT_DATE)")
    reponse = _reponse_de_l_api(curseur)
    assert (reponse["nb"], reponse["positions_closes"]) == (7, 1), "la close ne sort pas, elle est seulement comptée"
    assert passerelle._reponse_de_demonstration(reponse) is None
