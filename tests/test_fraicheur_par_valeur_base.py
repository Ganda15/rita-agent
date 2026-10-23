"""La fraîcheur par valeur sur la base réelle, dans une transaction annulée (sprint 5, étape 2).

Sauté sans base de test déclarée (`tests/garde_base.py`). Prouve ce que `tests/test_signaux.py` ne prouve pas, puisqu'il
remplace `_executer` : la requête `db/fraicheur_par_valeur.sql` tourne sur le vrai schéma, rend une ligne par valeur
suivie avec sa dernière séance, garde une valeur sans aucune cotation, et ignore une valeur exclue pour qualité.
Les valeurs d'essai sont créées dans la transaction du test et annulées avec elle.
"""
from datetime import date

import pytest

psycopg2 = pytest.importorskip("psycopg2")

from psycopg2.extras import RealDictCursor  # noqa: E402

from monitorage import signaux  # noqa: E402


@pytest.fixture
def curseur():
    from tests.garde_base import dsn_de_test
    try:
        con = psycopg2.connect(dsn_de_test(), connect_timeout=3)
    except psycopg2.OperationalError as e:
        pytest.skip(f"PostgreSQL injoignable : {e}")
    con.autocommit = False
    cur = con.cursor(cursor_factory=RealDictCursor)
    yield cur
    con.rollback()
    con.close()


def _cotation(cur, ticker, jour):
    cur.execute("INSERT INTO cotation (ticker, date_seance, ouverture, haut, bas, cloture, volume) "
                "VALUES (%s, %s, 1, 1, 1, 1, 1)", (ticker, jour))


def test_une_ligne_par_valeur_suivie_avec_sa_derniere_seance(curseur):
    curseur.execute("INSERT INTO valeur (ticker, nom_officiel) VALUES ('ESSAI.S5A', 'Essai a jour'), "
                    "('ESSAI.S5B', 'Essai en retard'), ('ESSAI.S5C', 'Essai sans cours')")
    curseur.execute("INSERT INTO valeur (ticker, nom_officiel, statut_qualite) VALUES ('ESSAI.S5X', 'Essai exclu', "
                    "'DELISTEE')")
    _cotation(curseur, "ESSAI.S5A", "2026-10-20")
    _cotation(curseur, "ESSAI.S5A", "2026-10-21")
    _cotation(curseur, "ESSAI.S5B", "2026-10-14")
    _cotation(curseur, "ESSAI.S5X", "2026-10-21")

    curseur.execute(signaux._REQUETE.read_text(encoding="utf-8"))
    lignes = {ligne["ticker"]: ligne for ligne in curseur.fetchall() if ligne["ticker"].startswith("ESSAI.S5")}

    assert set(lignes) == {"ESSAI.S5A", "ESSAI.S5B", "ESSAI.S5C"}
    assert lignes["ESSAI.S5A"]["derniere_seance"] == date(2026, 10, 21)
    assert lignes["ESSAI.S5B"]["derniere_seance"] == date(2026, 10, 14)
    assert lignes["ESSAI.S5C"]["derniere_seance"] is None
    fraicheur = signaux.fraicheur_par_valeur(list(lignes.values()), date(2026, 10, 22))
    assert fraicheur["pire"] == "rouge"
    assert [e["ticker"] for e in fraicheur["en_retard"]] == ["ESSAI.S5C", "ESSAI.S5B"]
