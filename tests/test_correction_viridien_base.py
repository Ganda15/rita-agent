"""La correction d'un regroupement sur une vraie base, dans une transaction annulée (04/11/2026).

Ce que les tests sans base ne prouvent pas : réimporter un CSV dont le PRU a changé ne doit pas fabriquer une vente.
La réconciliation (plan 66) identifie une ligne par (ticker, PRU, date d'achat) ; sans la correction, l'ancienne ligne
serait close à la date du réimport et une ligne neuve insérée. Corriger une donnée n'est pas constater une vente.
Une valeur et un CSV fictifs (`ESSAI.VR`), jamais les positions d'exemple ni une vraie base.
"""
from datetime import date
from decimal import Decimal

import pytest

psycopg2 = pytest.importorskip("psycopg2")

from db import importer  # noqa: E402

# Chaque test de ce fichier demande PostgreSQL ; le job `base` de la CI les choisit par ce marqueur.
pytestmark = pytest.mark.postgresql

TICKER = "ESSAI.VR"
REGROUPEMENT = ({"ticker": TICKER, "date_achat": "2021-10-14", "quantite": Decimal("120"), "pru": Decimal("1.85"),
                 "parite": 100, "source": "essai, regroupement fictif"},)
ENTETE = "Libellé;Code ISIN;Ticker;Quantité;Prix de revient;Devise;Date d'achat\n"
CORRIGEE = [(Decimal("1.0000"), Decimal("185.0000"), None)]
ANCIEN_CSV = ENTETE + f"Essai;FR0000000000;{TICKER};120;1,85;EUR;2021-10-14\n"   # la ligne d'avant le regroupement


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
def base(curseur, tmp_path, monkeypatch):
    """La ligne fausse déjà en base (120 à 1,85), et le CSV corrigé (1 à 185) que l'import va lire."""
    curseur.execute("INSERT INTO valeur (ticker, nom_officiel) VALUES (%s, 'Valeur d''essai regroupee') "
                    "ON CONFLICT (ticker) DO NOTHING", (TICKER,))
    curseur.execute("INSERT INTO position (ticker, quantite, pru, devise, date_achat) "
                    "VALUES (%s, 120, 1.85, 'EUR', '2021-10-14')", (TICKER,))
    csv = tmp_path / "positions.csv"
    csv.write_text(ENTETE + f"Essai;FR0000000000;{TICKER};1;185,00;EUR;2021-10-14\n", encoding="utf-8")
    monkeypatch.setenv("POSITIONS_CSV", str(csv))
    monkeypatch.setattr(importer, "REGROUPEMENTS", REGROUPEMENT)
    return curseur


def _lignes(cur):
    cur.execute("SELECT quantite, pru, date_cloture FROM position WHERE ticker = %s ORDER BY id", (TICKER,))
    return cur.fetchall()


def test_la_correction_met_a_jour_la_ligne_sans_la_clore(base):
    bilan = importer.importer_positions(base)
    assert bilan["corrigees"] == 1
    assert _lignes(base) == CORRIGEE, "une seule ligne, ouverte, corrigée sur place"


def test_rejouer_ne_cree_ni_doublon_ni_cloture(base):
    importer.importer_positions(base)
    second = importer.importer_positions(base)
    assert (second["corrigees"], second["inserees"]) == (0, 0)
    assert _lignes(base) == CORRIGEE


def test_sans_la_correction_le_reimport_fabriquerait_une_vente(base, monkeypatch):
    """Le danger que la correction écarte, constaté sur la base : la ligne fausse close, une ligne neuve insérée."""
    monkeypatch.setattr(importer, "REGROUPEMENTS", ())
    importer.importer_positions(base)
    lignes = _lignes(base)
    assert len(lignes) == 2
    assert lignes[0][2] is not None and lignes[1][2] is None


def test_la_vue_valorise_la_ligne_corrigee(base):
    base.execute("INSERT INTO cotation (ticker, date_seance, ouverture, haut, bas, cloture, volume) "
                 "VALUES (%s, '2026-11-03', 91.70, 91.70, 91.70, 91.70, 1)", (TICKER,))
    importer.importer_positions(base)
    base.execute("SELECT quantite, valorisation_eur, performance_pct FROM v_portefeuille_valorise "
                 "WHERE ticker = %s", (TICKER,))
    # (91,70 - 185) / 185 = -50,43 % ; une action à 91,70 € vaut 91,70 €.
    assert base.fetchall() == [(Decimal("1.0000"), Decimal("91.70"), Decimal("-50.43"))]


def _importer_ce_csv(curseur, tmp_path, monkeypatch, contenu):
    fichier = tmp_path / "autre.csv"
    fichier.write_text(contenu, encoding="utf-8")
    monkeypatch.setenv("POSITIONS_CSV", str(fichier))
    return importer.importer_positions(curseur)


def test_un_ancien_csv_apres_la_correction_ne_reintroduit_rien_et_ne_ferme_rien(base, tmp_path, monkeypatch):
    """Relecture extérieure du 04/11 : la base est corrigée (1 × 185), puis quelqu'un réimporte l'ANCIEN fichier (120 × 1,85).
    Sans précaution, l'ancienne ligne revient et la ligne corrigée, absente du fichier, est close : une vente inventée.
    Les lignes du fichier qui portent exactement la ligne d'avant sont converties au passage, avec un avertissement."""
    importer.importer_positions(base)                                                # le CSV corrigé
    bilan = _importer_ce_csv(base, tmp_path, monkeypatch, ANCIEN_CSV)                # puis l'ancien
    assert _lignes(base) == CORRIGEE, "ni la mauvaise ligne réintroduite, ni la bonne close"
    assert (bilan["closes"], bilan["inserees"], bilan["converties"]) == (0, 0, 1)


def test_un_ancien_csv_sur_une_base_jamais_corrigee_donne_la_ligne_corrigee(base, tmp_path, monkeypatch):
    bilan = _importer_ce_csv(base, tmp_path, monkeypatch, ANCIEN_CSV)
    assert _lignes(base) == CORRIGEE
    assert (bilan["corrigees"], bilan["converties"], bilan["closes"], bilan["inserees"]) == (1, 1, 0, 0)


def _cotation(cur, jour, cloture):
    cur.execute("INSERT INTO cotation (ticker, date_seance, ouverture, haut, bas, cloture, volume) "
                "VALUES (%s, %s, %s, %s, %s, %s, 1)", (TICKER, jour, cloture, cloture, cloture, cloture))


def _du_ticker(lignes):
    return [l for l in lignes if l["ticker"] == TICKER]


def test_le_garde_signale_le_prix_de_revient_hors_echelle_puis_se_tait_apres_correction(base):
    """La ligne fausse (120 à 1,85, cours de 64,44 le jour d'achat) est signalée avec son rapport et la date du cours lu,
    puis plus rien une fois corrigée sur place (185 à 64,44 : rapport 2,87)."""
    _cotation(base, "2021-10-14", "64.44")
    avant = _du_ticker(importer.controler_prix_de_revient(base)["hors_echelle"])
    assert [(l["pru"], l["cloture"], l["rapport"], l["date_cours"]) for l in avant] == [
        (Decimal("1.8500"), Decimal("64.4400"), Decimal("0.0287"), date(2021, 10, 14))]
    importer.importer_positions(base)
    assert _du_ticker(importer.controler_prix_de_revient(base)["hors_echelle"]) == []


def test_le_garde_ne_compare_pas_deux_devises_differentes(base):
    """Un prix de revient en dollars contre un cours en euros ne se compare pas : le contrôle n'est pas fait, et il le dit
    (des bornes larges ne rendent pas cette comparaison correcte)."""
    _cotation(base, "2021-10-14", "64.44")
    base.execute("INSERT INTO position (ticker, quantite, pru, devise, date_achat) VALUES (%s, 5, 1.86, 'USD', '2021-10-14')", (TICKER,))
    controle = importer.controler_prix_de_revient(base)
    assert Decimal("1.8600") not in [l["pru"] for l in _du_ticker(controle["hors_echelle"])]
    assert [(l["pru"], l["devise_pru"], l["devise_cours"]) for l in _du_ticker(controle["non_controlees"])] == [
        (Decimal("1.8600"), "USD", "EUR")]


def test_le_garde_donne_la_date_du_cours_reellement_utilise(base):
    """Achat un samedi : le dernier cours à ou avant cette date est celui du vendredi, et c'est sa date que le message donne."""
    _cotation(base, "2021-10-15", "64.44")
    base.execute("UPDATE position SET date_achat = '2021-10-16' WHERE ticker = %s", (TICKER,))
    (ligne,) = _du_ticker(importer.controler_prix_de_revient(base)["hors_echelle"])
    assert (ligne["date_achat"], ligne["date_cours"]) == (date(2021, 10, 16), date(2021, 10, 15))
