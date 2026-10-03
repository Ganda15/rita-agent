"""Tests du script d'import PostgreSQL (C4) — curseur simulé, aucune base requise.

`db/importer.py` était à **0 % de couverture** malgré une exigence C4 explicite : « le
script d'import fourni est fonctionnel ». Il n'est PAS exclu dans `.coveragerc`,
contrairement aux scripts `bigdata/` (ceux-ci ne tournent jamais dans l'image livrée ;
celui-ci en a le devoir).

Ce qu'on verrouille ici : le dédoublonnage (ticker, date_seance), le filtrage des
tickers hors univers (contrainte de clé étrangère), la résolution des alias de
portefeuille — dont le cas CGG (deux libellés, une valeur) — et le fait qu'un
portefeuille vide ou sans correspondance n'insère jamais rien.
"""
from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from db import importer


@pytest.fixture(autouse=True)
def sans_execute_values():
    """`execute_values` de psycopg2 encode le SQL via `cur.connection` — ce qu'un
    curseur simulé ne fournit pas. Même remède que `pipelines/ingest.py` (test_ingest.py)."""
    with patch("db.importer.execute_values") as faux:
        yield faux


def _curseur(tickers_connus=()) -> MagicMock:
    cur = MagicMock()
    cur.fetchall.return_value = [(t,) for t in tickers_connus]
    return cur


def _df_cotations(lignes):
    """lignes : liste de (ticker, date_iso, annee)."""
    return pd.DataFrame([
        {"ticker": t, "date": pd.Timestamp(d), "annee": a,
         "ouverture": 100.0, "haut": 101.0, "bas": 99.0, "cloture": 100.5, "volume": 1000}
        for t, d, a in lignes
    ])


class _Position:
    def __init__(self, ticker, nom, quantite=10, pru=100.0, devise="EUR", date_achat=None):
        self.ticker, self.nom = ticker, nom
        self.quantite, self.pru, self.devise, self.date_achat = quantite, pru, devise, date_achat


class _Portefeuille:
    def __init__(self, positions):
        self.positions = positions


# --- charger_univers : le cas CGG (deux libellés, une valeur, deux alias) --------

def test_charger_univers_resout_cgg_en_une_valeur_deux_alias(tmp_path, monkeypatch):
    csv = tmp_path / "univers.csv"
    csv.write_text(
        "nom,ticker,statut,lignes_10ans,premiere_date,note\n"
        "CGG BS,VIRI.PA,OK,100,2016-01-01,\n"
        "CGG RGPT,VIRI.PA,OK,100,2016-01-01,\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(importer, "UNIVERS", csv)

    valeurs, alias = importer.charger_univers()

    assert list(valeurs) == ["VIRI.PA"]          # une seule valeur pour les 2 libellés
    assert ("CGG BS", "VIRI.PA") in alias
    assert ("CGG RGPT", "VIRI.PA") in alias
    assert len(alias) == 2


def test_charger_univers_ignore_les_statuts_non_ok(tmp_path, monkeypatch):
    csv = tmp_path / "univers.csv"
    csv.write_text(
        "nom,ticker,statut,lignes_10ans,premiere_date,note\n"
        "VIVANT,AC.PA,OK,100,2016-01-01,\n"
        "SORTIE,XX.PA,SORTIE,0,,\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(importer, "UNIVERS", csv)

    valeurs, _ = importer.charger_univers()

    assert "XX.PA" not in valeurs
    assert "AC.PA" in valeurs


def test_charger_univers_marque_les_valeurs_incoherentes(tmp_path, monkeypatch):
    """STLAP.PA doit sortir avec statut INCOHERENT et sa note — pas supprimée."""
    csv = tmp_path / "univers.csv"
    csv.write_text(
        "nom,ticker,statut,lignes_10ans,premiere_date,note\n"
        "STELLANTIS,STLAP.PA,OK,100,2016-01-01,\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(importer, "UNIVERS", csv)

    valeurs, _ = importer.charger_univers()

    assert valeurs["STLAP.PA"]["statut"] == "INCOHERENT"
    assert valeurs["STLAP.PA"]["note"] is not None


# --- importer_valeurs -------------------------------------------------------------

def test_importer_valeurs_insere_valeurs_et_alias(sans_execute_values):
    cur = _curseur()
    valeurs = {"AC.PA": {"ticker": "AC.PA", "nom": "ACCOR", "statut": "OK", "note": None}}
    alias = [("ACCOR", "AC.PA")]

    importer.importer_valeurs(cur, valeurs, alias)

    assert sans_execute_values.call_count == 2       # 1 INSERT valeur, 1 INSERT alias_valeur
    sql_valeur, lignes_valeur = sans_execute_values.call_args_list[0].args[1:3]
    assert "INSERT INTO valeur" in sql_valeur
    assert lignes_valeur == [("AC.PA", "ACCOR", "OK", None, "EUR")]
    sql_alias, lignes_alias = sans_execute_values.call_args_list[1].args[1:3]
    assert "INSERT INTO alias_valeur" in sql_alias
    assert lignes_alias == alias


# --- importer_cotations ------------------------------------------------------------

def test_importer_cotations_leve_si_parquet_absent(monkeypatch):
    monkeypatch.setattr(importer, "PARQUET", importer.RACINE / "n-existe-pas.parquet")
    with pytest.raises(FileNotFoundError, match="build_parquet"):
        importer.importer_cotations(_curseur())


def test_importer_cotations_dedoublonne_ticker_date(monkeypatch, sans_execute_values):
    df = _df_cotations([
        ("AC.PA", "2026-01-02", 2026),
        ("AC.PA", "2026-01-02", 2026),   # doublon exact (ticker, date_seance)
        ("AC.PA", "2026-01-03", 2026),
    ])
    monkeypatch.setattr(importer, "PARQUET", importer.RACINE)      # .exists() -> True
    monkeypatch.setattr(importer.pd, "read_parquet", lambda _chemin: df)

    r = importer.importer_cotations(_curseur(tickers_connus=["AC.PA"]))

    assert r["lues"] == 3
    assert r["dedoublonnees"] == 1
    assert r["inserees"] == 2


def test_importer_cotations_filtre_les_tickers_hors_univers(monkeypatch, sans_execute_values):
    """Un ticker absent de `valeur` ne peut pas entrer (clé étrangère) — filtré, pas planté."""
    df = _df_cotations([
        ("AC.PA", "2026-01-02", 2026),
        ("INCONNU.PA", "2026-01-02", 2026),
    ])
    monkeypatch.setattr(importer, "PARQUET", importer.RACINE)
    monkeypatch.setattr(importer.pd, "read_parquet", lambda _chemin: df)

    r = importer.importer_cotations(_curseur(tickers_connus=["AC.PA"]))

    assert r["inserees"] == 1
    lignes = sans_execute_values.call_args_list[0].args[2]
    assert all(ligne[0] == "AC.PA" for ligne in lignes)


def test_importer_cotations_respecte_la_limite_d_annees(monkeypatch, sans_execute_values):
    df = _df_cotations([
        ("AC.PA", "2020-01-02", 2020),
        ("AC.PA", "2026-01-02", 2026),
    ])
    monkeypatch.setattr(importer, "PARQUET", importer.RACINE)
    monkeypatch.setattr(importer.pd, "read_parquet", lambda _chemin: df)

    r = importer.importer_cotations(_curseur(tickers_connus=["AC.PA"]), limite_annees=1)

    assert r["lues"] == 2          # comptées avant le filtre des N dernières années
    assert r["inserees"] == 1      # seule la ligne 2026 passe le filtre


# --- importer_positions : la résolution des alias ---------------------------------

def test_importer_positions_resout_directement_par_ticker(sans_execute_values):
    cur = MagicMock()
    cur.fetchone.return_value = ("MC.PA",)     # trouvé directement dans `valeur`

    with patch("sources.positions.lire",
               return_value=_Portefeuille([_Position("MC.PA", "LVMH")])):
        n = importer.importer_positions(cur)

    assert n == 1
    lignes = sans_execute_values.call_args.args[2]
    assert lignes[0][0] == "MC.PA"


def test_importer_positions_resout_par_alias_quand_le_ticker_a_change(sans_execute_values):
    """Cas CGG : la position porte l'ancien libellé, pas le ticker canonique VIRI.PA."""
    cur = MagicMock()
    cur.fetchone.side_effect = [None, ("VIRI.PA",)]  # 1er SELECT (ticker) rien, 2e (alias) trouvé

    with patch("sources.positions.lire",
               return_value=_Portefeuille([_Position("CGG", "CGG BS")])):
        n = importer.importer_positions(cur)

    assert n == 1
    lignes = sans_execute_values.call_args.args[2]
    assert lignes[0][0] == "VIRI.PA"      # résolu vers le ticker canonique, pas "CGG"


def test_importer_positions_ignore_sans_correspondance(sans_execute_values):
    cur = MagicMock()
    cur.fetchone.side_effect = [None, None]    # ni ticker ni alias trouvé

    with patch("sources.positions.lire",
               return_value=_Portefeuille([_Position("FANTOME", "Inconnue")])):
        n = importer.importer_positions(cur)

    assert n == 0
    sans_execute_values.assert_not_called()


def test_importer_positions_portefeuille_vide_n_insere_rien(sans_execute_values):
    with patch("sources.positions.lire", return_value=_Portefeuille([])):
        n = importer.importer_positions(MagicMock())

    assert n == 0
    sans_execute_values.assert_not_called()


# --- importer() : l'orchestration ---------------------------------------------------

def test_importer_assemble_les_statistiques_et_commit(monkeypatch):
    """Vérifie le câblage (connexion, commit, fusion des stats) — la logique de chaque
    étape est déjà verrouillée par les tests ci-dessus, pas reproduite ici."""
    monkeypatch.setattr(importer, "charger_univers",
                         lambda: ({"AC.PA": {}}, [("ACCOR", "AC.PA")]))
    monkeypatch.setattr(importer, "importer_valeurs", MagicMock())
    monkeypatch.setattr(importer, "importer_cotations",
                         MagicMock(return_value={"lues": 10, "dedoublonnees": 1, "inserees": 9}))
    monkeypatch.setattr(importer, "importer_positions", MagicMock(return_value=7))

    with patch("db.importer.psycopg2.connect") as connect:
        r = importer.importer("postgresql://test", limite_annees=3)

    connect.assert_called_once_with("postgresql://test")
    connect.return_value.__enter__.return_value.commit.assert_called_once()
    assert r == {"lues": 10, "dedoublonnees": 1, "inserees": 9,
                 "valeurs": 1, "alias": 1, "positions": 7}


# --- 27/09/2026 : issues #53, #47 et #48 ----------------------------------------

def test_la_date_de_seance_est_la_date_locale_de_la_place_pas_la_date_utc(monkeypatch, sans_execute_values):
    """Le Parquet stocke minuit heure de Paris converti en UTC, soit 22h la veille.
    Prendre la date UTC a décalé dix ans d'archive d'un jour (52 426 « dimanches »)."""
    df = _df_cotations([("MC.PA", "2016-07-31", 2016)])
    df["date"] = pd.Timestamp("2016-07-31 22:00", tz="UTC")
    monkeypatch.setattr(importer, "PARQUET", importer.RACINE)
    monkeypatch.setattr(importer.pd, "read_parquet", lambda _chemin: df)

    importer.importer_cotations(_curseur(["MC.PA"]))

    lignes = sans_execute_values.call_args.args[2]
    assert lignes[0][1] == date(2016, 8, 1)


def test_les_pence_de_l_archive_sont_convertis_en_livres(monkeypatch, sans_execute_values):
    df = _df_cotations([("HSBA.L", "2026-07-30", 2026)])
    df[["ouverture", "haut", "bas", "cloture"]] = [1515.4, 1524.0, 1507.6, 1512.2]
    monkeypatch.setattr(importer, "PARQUET", importer.RACINE)
    monkeypatch.setattr(importer.pd, "read_parquet", lambda _chemin: df)

    importer.importer_cotations(_curseur(["HSBA.L"]))

    ligne = sans_execute_values.call_args.args[2][0]
    assert ligne[5] == pytest.approx(15.122)


def test_importer_valeurs_renseigne_la_devise_de_cotation(sans_execute_values):
    valeurs = {t: {"ticker": t, "nom": t, "statut": "OK", "note": None}
               for t in ("MC.PA", "HSBA.L", "FTI")}
    importer.importer_valeurs(_curseur(), valeurs, [])

    lignes = sans_execute_values.call_args_list[0].args[2]
    devises = {l[0]: l[-1] for l in lignes}
    assert devises == {"MC.PA": "EUR", "HSBA.L": "GBP", "FTI": "USD"}


@pytest.mark.parametrize("ticker", ["ZC.PA", "ELE.PA", "GTO.PA"])
def test_les_trois_valeurs_radiees_sont_marquees_delistee(tmp_path, monkeypatch, ticker):
    """Classées OK_PARTIEL dans l'univers, elles devenaient OK en base (#48)."""
    csv = tmp_path / "u.csv"
    csv.write_text("nom,ticker,statut,lignes_10ans,premiere_date,note\n"
                   f"X,{ticker},OK_PARTIEL,400,2016-07-29,serie partielle\n", encoding="utf-8")
    monkeypatch.setattr(importer, "UNIVERS", csv)

    valeurs, _ = importer.charger_univers()

    assert valeurs[ticker]["statut"] == "DELISTEE"
