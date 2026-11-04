"""--corrections-seulement sur une vraie base, dans une transaction annulée (04/11/2026 au soir).

La preuve demandée par la relecture extérieure : sur une base représentative (d'autres valeurs avec leurs statuts et leurs
notes, des alias, d'autres positions dont une qu'aucun CSV ne porterait), seules les cellules visées changent : la ligne de
la position regroupée (quantité, prix de revient, `importe_le`) et le nom de sa valeur. Tout le reste, horodatages compris,
est comparé cellule à cellule avant et après.
"""
from decimal import Decimal

import pytest

psycopg2 = pytest.importorskip("psycopg2")

from db import importer  # noqa: E402

pytestmark = pytest.mark.postgresql

VISEE, AUTRE = "ESSAI.VC", "ESSAI.AU"
REGROUPEMENT = ({"ticker": VISEE, "date_achat": "2021-10-14", "quantite": Decimal("120"), "pru": Decimal("1.85"),
                 "parite": 100, "source": "essai"},)


@pytest.fixture
def curseur():
    from tests.garde_base import dsn_de_test
    try:
        con = psycopg2.connect(dsn_de_test(), connect_timeout=3)
    except psycopg2.OperationalError as e:
        pytest.skip(f"PostgreSQL injoignable : {e}")
    con.autocommit = False
    cur = con.cursor()
    yield cur
    con.rollback()
    con.close()


@pytest.fixture
def base(curseur, monkeypatch):
    """Une base représentative : la valeur visée et une autre (avec statut et note), deux alias, trois positions."""
    curseur.execute("INSERT INTO valeur (ticker, nom_officiel, statut_qualite, note_qualite) VALUES "
                    "(%s, 'ANCIEN NOM', 'OK', NULL), (%s, 'AUTRE VALEUR', 'INCOHERENT', 'note a garder') "
                    "ON CONFLICT (ticker) DO NOTHING", (VISEE, AUTRE))
    curseur.execute("INSERT INTO alias_valeur (alias, ticker) VALUES ('ALIAS ESSAI VC', %s), ('ALIAS ESSAI AU', %s) "
                    "ON CONFLICT (alias) DO NOTHING", (VISEE, AUTRE))
    curseur.execute("INSERT INTO position (ticker, quantite, pru, devise, date_achat, importe_le) VALUES "
                    "(%s, 120, 1.85, 'EUR', '2021-10-14', TIMESTAMPTZ '2026-08-20 11:03:00+00'), "
                    "(%s, 10, 50, 'EUR', '2023-01-02', TIMESTAMPTZ '2026-08-20 11:03:00+00'), "
                    "(%s, 5, 60, 'EUR', '2024-01-02', TIMESTAMPTZ '2026-08-20 11:03:00+00')", (VISEE, AUTRE, AUTRE))
    monkeypatch.setattr(importer, "REGROUPEMENTS", REGROUPEMENT)
    monkeypatch.setattr(importer, "NOMS_OFFICIELS", {VISEE: "NOUVEAU NOM"})
    return curseur


def _etat(cur):
    etat = {}
    for table, cle in (("valeur", "ticker"), ("alias_valeur", "alias"), ("position", "id")):
        cur.execute(f"SELECT * FROM {table} WHERE ticker IN (%s, %s) ORDER BY 1", (VISEE, AUTRE))
        colonnes = [d[0] for d in cur.description]
        for ligne in cur.fetchall():
            rangee = dict(zip(colonnes, ligne))
            etat[(table, rangee[cle])] = rangee
    return etat


def _differences(avant, apres):
    assert avant.keys() == apres.keys(), "aucune ligne ajoutée ni retirée"
    return {(cle, col) for cle in avant for col in avant[cle] if avant[cle][col] != apres[cle][col]}


def test_seules_les_cellules_visees_changent(base):
    avant = _etat(base)
    bilan = importer.appliquer_corrections(base)
    apres = _etat(base)
    id_visee = next(r["id"] for (t, _), r in avant.items() if t == "position" and r["ticker"] == VISEE)
    assert _differences(avant, apres) == {
        (("position", id_visee), "quantite"), (("position", id_visee), "pru"), (("position", id_visee), "importe_le"),
        (("valeur", VISEE), "nom_officiel")}
    assert apres[("position", id_visee)]["quantite"] == Decimal("1.0000")
    assert apres[("position", id_visee)]["pru"] == Decimal("185.0000")
    assert apres[("valeur", VISEE)]["nom_officiel"] == "NOUVEAU NOM"
    assert (bilan["corrigees"], bilan["noms_corriges"]) == (1, 1)


def test_aucune_position_n_est_close_meme_absente_de_tout_csv(base):
    importer.appliquer_corrections(base)
    base.execute("SELECT count(*) FROM position WHERE ticker IN (%s, %s) AND date_cloture IS NOT NULL", (VISEE, AUTRE))
    assert base.fetchone()[0] == 0


def test_rejouer_ne_change_plus_rien(base):
    importer.appliquer_corrections(base)
    avant = _etat(base)
    bilan = importer.appliquer_corrections(base)
    assert _differences(avant, _etat(base)) == set()
    assert (bilan["corrigees"], bilan["noms_corriges"]) == (0, 0)
