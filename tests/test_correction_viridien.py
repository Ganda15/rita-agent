"""Viridien (ex-CGG) : la ligne d'exemple ramenée à l'échelle du regroupement du 31/07/2024 (04/11/2026).

Constat d'Era sur l'écran Indicateurs : VIRI.PA en tête, +4 856,76 % et 34,04 % du portefeuille. La ligne de
`data/positions-exemple.csv` portait 120 actions à 1,85 €, l'échelle d'avant le regroupement de 100 actions anciennes
pour 1 nouvelle (communiqué Viridien du 31/07/2024), alors que les cours de la base sont rétro-ajustés. Elle portait
aussi l'ISIN de Vallourec (FR0013506730), et la valeur s'affichait encore « CGG BS ».

Ces tests tournent partout, CI comprise, sans base ni archive : la règle du regroupement, la ligne d'exemple qui en
découle, le nom et l'ISIN. La correction sur une vraie base (sans fausse clôture, rejouable) est prouvée par
`tests/test_correction_viridien_base.py`. Le contrôle sur l'archive Parquet, à la fin, n'est qu'une alerte.
"""
from decimal import Decimal
from pathlib import Path

import pytest

from db import importer
from sources import positions

RACINE = Path(__file__).resolve().parent.parent
PARQUET = RACINE / "data" / "bigdata" / "ohlcv"


def _viridien():
    return next(r for r in importer.REGROUPEMENTS if r["ticker"] == "VIRI.PA")


def test_cent_anciennes_pour_une_nouvelle():
    # 120 anciennes à 1,85 € : une action entière, au coût des 100 anciennes qu'elle remplace, et 20 rompus.
    assert importer.position_regroupee(Decimal("120"), Decimal("1.85"), 100) == \
        (Decimal("1"), Decimal("185.00"), Decimal("20"))


def test_moins_d_un_bloc_ne_donne_aucune_action():
    # Moins de 100 anciennes : tout part en rompus. Ce serait une vraie sortie du portefeuille, que la correction
    # n'invente pas : elle refuse.
    with pytest.raises(ValueError, match="aucune action nouvelle"):
        importer.position_regroupee(Decimal("50"), Decimal("1.85"), 100)


def test_la_correction_viridien_cite_la_ligne_d_avant_exacte():
    r = _viridien()
    assert (r["quantite"], r["pru"], r["parite"], r["date_achat"]) == (Decimal("120"), Decimal("1.85"), 100, "2021-10-14")
    assert "31/07/2024" in r["source"]


def test_la_ligne_d_exemple_est_la_ligne_regroupee():
    r = _viridien()
    ligne = next(p for p in positions.lire(positions.EXEMPLE).positions if p.ticker == "VIRI.PA")
    quantite, pru, _ = importer.position_regroupee(r["quantite"], r["pru"], r["parite"])
    assert (Decimal(str(ligne.quantite)), Decimal(str(ligne.pru))) == (quantite, pru)
    assert ligne.date_achat == r["date_achat"]
    # L'action regroupée porte le nouvel ISIN (communiqué du 31/07/2024) ; FR0013506730 est celui de Vallourec.
    assert ligne.isin == "FR001400PVN6"


def test_le_jeu_attendu_de_la_passerelle_suit_la_ligne_regroupee():
    # Le verrou de démonstration (#152) compare la base à ce fichier : il doit dire la même ligne que l'exemple.
    texte = (RACINE / "passerelle_mcp" / "jeu_demo_attendu.csv").read_text(encoding="utf-8")
    assert "VIRI.PA;1.0000;185.0000;EUR" in texte
    assert "1.8500" not in texte


def test_le_nom_affiche_est_viridien_et_les_libelles_du_courtier_restent():
    valeurs, alias = importer.charger_univers()
    assert valeurs["VIRI.PA"]["nom"] == "VIRIDIEN"
    assert ("CGG BS", "VIRI.PA") in alias and ("CGG RGPT", "VIRI.PA") in alias


@pytest.mark.skipif(not PARQUET.exists(), reason="archive Parquet absente (hors Git) : alerte locale seulement")
def test_alerte_prix_de_revient_a_l_echelle_des_cours():
    """Alerte, pas preuve : un PRU très loin du cours rétro-ajusté du jour d'achat signale une autre échelle.

    Mesuré le 04/11/2026 : 0,78 à 1,51 pour six lignes, 0,029 pour Viridien avant correction. Un regroupement de
    10 pour 1 donnerait 0,1, de 100 pour 1 0,01 : sous 0,2, ou au-dessus de 5, la ligne est à regarder. Passer ce
    contrôle ne dit pas qu'une ligne est juste : un PRU peut cumuler plusieurs achats et des frais.
    """
    ds = pytest.importorskip("pyarrow.dataset")
    pc = pytest.importorskip("pyarrow.compute")
    archive = ds.dataset(str(PARQUET), format="parquet", partitioning="hive")
    hors_echelle = {}
    for p in positions.lire(positions.EXEMPLE).positions:
        t = archive.to_table(filter=pc.field("ticker") == p.ticker, columns=["date", "cloture"]).to_pandas()
        if t.empty:
            continue
        t["jour"] = t["date"].dt.tz_convert("Europe/Paris").dt.date.astype(str)
        avant = t[t["jour"] <= p.date_achat]
        if avant.empty:
            continue
        rapport = p.pru / float(avant.sort_values("jour")["cloture"].iloc[-1])
        if not 0.2 <= rapport <= 5:
            hors_echelle[p.ticker] = round(rapport, 3)
    assert hors_echelle == {}, f"PRU / cours du jour d'achat hors de [0,2 ; 5] : {hors_echelle}"


# --- le garde de l'importateur : un prix de revient loin du cours du jour d'achat est signalé (04/11/2026 au soir) -----------
# Viridien est resté en tête d'un écran trois mois sans que personne ne le voie. L'importateur lit déjà les positions et les
# cours : il peut dire, à chaque import, qu'une ligne est probablement à une autre échelle que les cours. Une alerte, pas une
# preuve : un prix de revient peut cumuler plusieurs achats et des frais. Les bornes sont une convention déclarée.

@pytest.mark.parametrize("pru, cloture, hors", [
    ("1.85", "64.44", True),     # Viridien avant correction : 0,029
    ("185", "64.44", False),     # après correction : 2,87
    ("20", "100", False),        # 0,2 : la borne basse est comprise
    ("19.99", "100", True),
    ("500", "100", False),       # 5 : la borne haute est comprise
    ("500.01", "100", True),
])
def test_rapport_hors_echelle(pru, cloture, hors):
    assert (importer.rapport_hors_echelle(Decimal(pru), Decimal(cloture)) is not None) is hors


def test_le_rapport_signale_est_arrondi_a_quatre_decimales():
    assert importer.rapport_hors_echelle(Decimal("1.85"), Decimal("64.44")) == Decimal("0.0287")


def test_un_cours_nul_ne_divise_pas_par_zero():
    assert importer.rapport_hors_echelle(Decimal("1.85"), Decimal("0")) is None


def test_la_conversion_d_un_ancien_csv_ne_touche_que_la_ligne_exacte():
    """Le périmètre de la migration : la ligne simulée d'avant, identifiée par ses quatre champs (ticker, date d'achat,
    quantité, prix de revient). Une ligne qui s'en approche n'est pas touchée."""
    lignes = [("VIRI.PA", 120.0, 1.85, "EUR", "2021-10-14"),   # exacte : convertie
              ("VIRI.PA", 121.0, 1.85, "EUR", "2021-10-14"),   # autre quantité
              ("VIRI.PA", 120.0, 1.86, "EUR", "2021-10-14"),   # autre prix de revient
              ("VIRI.PA", 120.0, 1.85, "EUR", "2022-01-03"),   # autre date d'achat
              ("MC.PA", 120.0, 1.85, "EUR", "2021-10-14")]     # autre valeur
    sorties, converties = importer.convertir_lignes_d_avant_regroupement(lignes)
    assert converties == 1
    assert sorties[0] == ("VIRI.PA", Decimal("1"), Decimal("185.00"), "EUR", "2021-10-14")
    assert sorties[1:] == lignes[1:]


def test_une_ligne_deja_corrigee_n_est_pas_convertie_deux_fois():
    lignes = [("VIRI.PA", Decimal("1"), Decimal("185.00"), "EUR", "2021-10-14")]
    assert importer.convertir_lignes_d_avant_regroupement(lignes) == (lignes, 0)
