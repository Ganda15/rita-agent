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


# --- importer_positions : la résolution des alias, puis la réconciliation (plan 66) --------------
#
# Depuis le 03/10/2026, `importer_positions` rend un bilan (dict) et fait trois choses : upsert des
# lignes du CSV sur la clé (ticker, PRU, date d'achat), clôture datée des lignes absentes, garde-fous.
# Le curseur simulé répond, dans l'ordre : les recherches de ticker/alias (une ou deux par position),
# puis le compte des actives, puis le compte des rouvertures.

def _cur_positions(*recherches, actives=7, rouvertes=0, closes=0):
    cur = MagicMock()
    cur.fetchone.side_effect = list(recherches) + [(actives,), (rouvertes,)]
    cur.rowcount = closes
    return cur


def _requetes(cur):
    return [str(c.args[0]).upper() for c in cur.execute.call_args_list]


def test_importer_positions_resout_directement_par_ticker(sans_execute_values):
    cur = _cur_positions(("MC.PA", "EUR"))          # trouvé directement dans `valeur`
    with patch("sources.positions.lire", return_value=_Portefeuille([_Position("MC.PA", "LVMH")])):
        bilan = importer.importer_positions(cur)
    assert bilan["lignes"] == 1
    lignes = sans_execute_values.call_args.args[2]
    assert lignes[0][0] == "MC.PA"


def test_importer_positions_resout_par_alias_quand_le_ticker_a_change(sans_execute_values):
    """Cas CGG : la position porte l'ancien libellé, pas le ticker canonique VIRI.PA."""
    cur = _cur_positions(None, ("VIRI.PA", "EUR"))   # 1er SELECT (ticker) rien, 2e (alias) trouvé
    with patch("sources.positions.lire", return_value=_Portefeuille([_Position("CGG", "CGG BS")])):
        bilan = importer.importer_positions(cur)
    assert bilan["lignes"] == 1
    assert sans_execute_values.call_args.args[2][0][0] == "VIRI.PA"


def test_importer_positions_ignore_sans_correspondance(sans_execute_values):
    cur = _cur_positions(None, None)                 # ni ticker ni alias trouvé
    with patch("sources.positions.lire", return_value=_Portefeuille([_Position("FANTOME", "Inconnue")])):
        bilan = importer.importer_positions(cur)
    assert bilan["lignes"] == 0 and bilan["ignorees"] == 1
    sans_execute_values.assert_not_called()


def test_importer_positions_portefeuille_vide_n_insere_rien_et_ne_clot_rien(sans_execute_values):
    """D4 : un CSV sans ligne valide ne vend pas un portefeuille ; il le dit."""
    cur = MagicMock()
    with patch("sources.positions.lire", return_value=_Portefeuille([])):
        bilan = importer.importer_positions(cur)
    assert bilan["lignes"] == 0 and bilan["closes"] == 0
    assert "aucune position close" in bilan["avertissement"]
    sans_execute_values.assert_not_called()
    assert not any("UPDATE POSITION" in q for q in _requetes(cur))


def test_les_lignes_presentes_sont_upsertees_sur_la_cle_et_rouvertes(sans_execute_values):
    """D1 et D2 : ON CONFLICT sur (ticker, pru, date d'achat) ; une ligne revenue rouvre la même ligne."""
    cur = _cur_positions(("MC.PA", "EUR"), rouvertes=1)
    sans_execute_values.return_value = [(False,)]           # une mise à jour, aucune insertion
    with patch("sources.positions.lire", return_value=_Portefeuille([_Position("MC.PA", "LVMH", date_achat="2023-04-18")])):
        bilan = importer.importer_positions(cur)
    sql = sans_execute_values.call_args.args[1].upper()
    assert "ON CONFLICT (TICKER, PRU, COALESCE(DATE_ACHAT, DATE '1900-01-01')) DO UPDATE" in sql
    assert "DATE_CLOTURE = NULL" in sql
    assert bilan["rouvertes"] == 1 and bilan["mises_a_jour"] == 1 and bilan["inserees"] == 0


def test_les_lignes_absentes_du_csv_sont_closes_a_la_date_du_jour(sans_execute_values):
    """Jamais supprimées : closes, datées du jour où le CSV ne les porte plus."""
    cur = _cur_positions(("MC.PA", "EUR"), actives=3, closes=2)
    with patch("sources.positions.lire", return_value=_Portefeuille([_Position("MC.PA", "LVMH")])):
        bilan = importer.importer_positions(cur)
    cloture = [q for q in _requetes(cur) if "UPDATE POSITION" in q]
    assert len(cloture) == 1
    assert "SET DATE_CLOTURE = CURRENT_DATE" in cloture[0]
    assert "WHERE DATE_CLOTURE IS NULL" in cloture[0] and "NOT IN" in cloture[0]
    assert not any("DELETE" in q for q in _requetes(cur)), "l'import ne supprime jamais"
    assert bilan["closes"] == 2


def test_moins_de_la_moitie_des_actives_clot_quand_meme_mais_avertit(sans_execute_values):
    cur = _cur_positions(("MC.PA", "EUR"), actives=7, closes=6)
    with patch("sources.positions.lire", return_value=_Portefeuille([_Position("MC.PA", "LVMH")])):
        bilan = importer.importer_positions(cur)
    assert bilan["closes"] == 6
    assert "fichier partiel" in bilan["avertissement"]


def test_une_devise_de_pru_differente_de_la_cotation_est_importee_mais_signalee(sans_execute_values, caplog):
    """Cas D07 (#69, décision a) : PRU en USD sur une valeur cotée en EUR."""
    import logging
    cur = _cur_positions(("MC.PA", "EUR"))
    with patch("sources.positions.lire", return_value=_Portefeuille([_Position("MC.PA", "LVMH", devise="USD")])), \
         caplog.at_level(logging.WARNING, logger="db.importer"):
        bilan = importer.importer_positions(cur)
    assert bilan["lignes"] == 1 and bilan["devises_differentes"] == 1
    assert any("D07" in r.getMessage() for r in caplog.records)


# --- importer() : l'orchestration ---------------------------------------------------

def test_importer_assemble_les_statistiques_et_commit(monkeypatch):
    """Vérifie le câblage (connexion, commit, fusion des stats) — la logique de chaque
    étape est déjà verrouillée par les tests ci-dessus, pas reproduite ici."""
    monkeypatch.setattr(importer, "charger_univers",
                         lambda: ({"AC.PA": {}}, [("ACCOR", "AC.PA")]))
    monkeypatch.setattr(importer, "importer_valeurs", MagicMock())
    monkeypatch.setattr(importer, "importer_cotations",
                         MagicMock(return_value={"lues": 10, "dedoublonnees": 1, "inserees": 9}))
    bilan_positions = {"lignes": 7, "inserees": 0, "mises_a_jour": 7, "rouvertes": 0, "closes": 0,
                       "ignorees": 0, "devises_differentes": 0, "avertissement": None}
    monkeypatch.setattr(importer, "importer_positions", MagicMock(return_value=bilan_positions))

    with patch("db.importer.psycopg2.connect") as connect:
        r = importer.importer("postgresql://test", limite_annees=3)

    connect.assert_called_once_with("postgresql://test")
    connect.return_value.__enter__.return_value.commit.assert_called_once()
    assert r == {"lues": 10, "dedoublonnees": 1, "inserees": 9,
                 "valeurs": 1, "alias": 1, "positions": 7, "positions_detail": bilan_positions}


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


# --- Sprint 2, tâche 5 : le mode « démonstration » (`--demo`) --------------------------------------------------------
# La base de démonstration porte une marque (le commentaire de la base). L'import refuse toute base qui contient déjà
# des données sans porter cette marque : les tickers seuls ne disent pas si la destination est une vraie base.

from pathlib import Path as _Path

from psycopg2 import sql as _sql

DOSSIER_DEMO = _Path(__file__).resolve().parent.parent / "data" / "demo"
TABLES_DU_SCHEMA = ["devise", "valeur", "alias_valeur", "cotation", "position", "taux_change", "macro_observation",
                    "article", "memory_audit", "mcp_calls"]


def _texte(requete) -> str:
    """Le texte d'une requête, qu'elle soit une chaîne ou composée avec `psycopg2.sql`."""
    if isinstance(requete, str):
        return requete
    if isinstance(requete, _sql.Composed):
        return "".join(_texte(partie) for partie in requete.seq)
    if isinstance(requete, _sql.Identifier):
        return ".".join(f'"{s}"' for s in requete.strings)
    if isinstance(requete, _sql.Literal):
        return repr(requete.wrapped)
    return requete.string


class FauxCurseurDemo:
    """Répond aux requêtes du mode démonstration comme le ferait une base avec ces tables remplies et cette marque."""

    def __init__(self, tables_remplies=(), marque=None, rowcount=1):
        self.tables_remplies, self.marque, self.rowcount_insert = set(tables_remplies), marque, rowcount
        self.executions, self._resultat, self.rowcount = [], [], 0

    def execute(self, requete, params=None):
        texte = _texte(requete)
        self.executions.append(texte)
        self.rowcount = 0
        if "shobj_description" in texte:
            self._resultat = [(self.marque,)]
        elif "information_schema.tables" in texte:
            self._resultat = [(t,) for t in TABLES_DU_SCHEMA]
        elif texte.startswith("SELECT EXISTS"):
            table = texte.split("FROM", 1)[1].strip().strip(')').strip('"')
            self._resultat = [(table in self.tables_remplies,)]
        elif "current_database()" in texte:
            self._resultat = [("rita",)]
        elif texte.startswith("COMMENT ON DATABASE"):
            self.marque = importer.MARQUE_DEMO
        elif texte.lstrip().startswith("INSERT"):
            self.rowcount = self.rowcount_insert

    def fetchone(self):
        return self._resultat[0]

    def fetchall(self):
        return self._resultat

    def inserts(self):
        return [t for t in self.executions if t.lstrip().startswith("INSERT")]

    def comments(self):
        return [t for t in self.executions if t.startswith("COMMENT ON DATABASE")]


def test_demo_refuse_une_base_reelle_avec_les_memes_tickers():
    # Une base réelle qui ne contiendrait que OR.PA, MC.PA et AIR.PA ressemble au jeu : seule la marque tranche.
    cur = FauxCurseurDemo(tables_remplies={"valeur", "cotation"})
    with pytest.raises(importer.BaseNonDemo):
        importer.preparer_base_demo(cur)
    assert cur.inserts() == [] and cur.comments() == []


@pytest.mark.parametrize("table", ["taux_change", "macro_observation", "memory_audit", "mcp_calls"])
def test_demo_refuse_une_base_non_vide_sans_marque(table):
    cur = FauxCurseurDemo(tables_remplies={table})
    with pytest.raises(importer.BaseNonDemo):
        importer.preparer_base_demo(cur)
    assert cur.comments() == []


def test_demo_ignore_les_devises_de_reference():
    # db/schema.sql remplit `devise` : une base neuve n'est jamais vide au sens strict.
    cur = FauxCurseurDemo(tables_remplies={"devise"})
    importer.preparer_base_demo(cur)
    assert cur.marque == importer.MARQUE_DEMO


def test_demo_marque_une_base_vide_puis_importe():
    cur = FauxCurseurDemo()
    importer.preparer_base_demo(cur)
    importer.importer_demo(cur, DOSSIER_DEMO)
    commentaire = cur.executions.index(cur.comments()[0])
    premiere_insertion = cur.executions.index(cur.inserts()[0])
    assert commentaire < premiere_insertion
    assert "'rita-demonstration'" in cur.comments()[0] and '"rita"' in cur.comments()[0]


def test_demo_accepte_une_base_deja_marquee():
    cur = FauxCurseurDemo(tables_remplies={"valeur", "cotation"}, marque=importer.MARQUE_DEMO)
    importer.preparer_base_demo(cur)
    assert cur.comments() == []


def test_importer_demo_rend_les_lignes_inserees():
    cur = FauxCurseurDemo()
    assert importer.importer_demo(cur, DOSSIER_DEMO) == {"valeurs": 3, "cotations": 222, "articles": 6, "positions": 3}


def test_importer_demo_deux_fois_n_insere_rien():
    # Deuxième exécution : tout existe déjà, chaque insertion touche 0 ligne (ON CONFLICT DO NOTHING).
    cur = FauxCurseurDemo(marque=importer.MARQUE_DEMO, rowcount=0)
    assert importer.importer_demo(cur, DOSSIER_DEMO) == {"valeurs": 0, "cotations": 0, "articles": 0, "positions": 0}
    assert all("ON CONFLICT DO NOTHING" in t or "NOT EXISTS" in t for t in cur.inserts())


def test_importer_demo_complet_marque_importe_et_valide_en_une_transaction():
    # Ajouté après le code (lignes que la couverture montrait non exercées) : la marque puis l'import, puis commit.
    cur = FauxCurseurDemo()
    conn = MagicMock()
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cur
    with patch.object(importer.psycopg2, "connect", return_value=conn) as connexion:
        bilan = importer.importer_demo_complet("postgresql://demo", DOSSIER_DEMO)
    connexion.assert_called_once_with("postgresql://demo")
    assert bilan["cotations"] == 222 and cur.marque == importer.MARQUE_DEMO
    conn.commit.assert_called_once()
