"""Tests du pipeline d'agrégation (C3) — sources et base simulées.

Ce qu'on vérifie ici n'est pas « les données arrivent » (prouvé par l'exécution réelle dans
`evidence/C3/`), mais les **règles d'agrégation** : dédoublonnage, tolérance aux pannes,
mode simulation, et le fait qu'une étape en échec n'emporte pas les autres.
"""
from unittest.mock import MagicMock, patch

import pytest

from pipelines import ingest


@pytest.fixture(autouse=True)
def sans_execute_values():
    """`execute_values` de psycopg2 encode le SQL via `cur.connection.encoding` — ce qu'un
    curseur simulé ne fournit pas. On le remplace par un double et on inspecte ses appels."""
    with patch("pipelines.ingest.execute_values") as faux:
        yield faux


def _curseur(retour=None) -> MagicMock:
    cur = MagicMock()
    cur.fetchone.return_value = retour
    cur.__enter__ = MagicMock(return_value=cur)
    cur.__exit__ = MagicMock(return_value=False)
    return cur


class _Article:
    def __init__(self, lien, titre="Titre", bloque=False, motifs=None):
        self.source, self.titre, self.lien = "bfm", titre, lien
        self.publie_le, self.resume = "2026-08-01T06:00:00+00:00", "resume"
        self.bloque, self.motifs_injection = bloque, motifs or []


class _Cotation:
    def __init__(self, symbole="1rPMC", isin="FR0000121014", complet=True):
        self.symbole, self.isin = symbole, isin
        self.ouverture = self.haut = self.bas = self.dernier = 100.0 if complet else None
        self.volume = 1000
        self.collecte_le = "2026-08-01T10:00:00+00:00"


# --- taux de change -----------------------------------------------------------

def test_ecb_ajoute_l_euro_a_1(sans_execute_values):
    """Sans la ligne EUR=1, la valorisation des positions en euros retombe sur COALESCE."""
    with patch("sources.ecb.fetch_taux_change",
               return_value={"devise": "USD", "date": "2026-08-01", "valeur": 1.14}):
        b = ingest.etape_taux_change(_curseur(), simulation=False)

    assert b.ecrites == len(ingest.DEVISES_SUIVIES) + 1     # +1 pour EUR
    lignes = sans_execute_values.call_args.args[2]
    assert ("EUR", "2026-08-01", 1.0) in lignes


def test_ecb_une_devise_en_echec_ne_bloque_pas_les_autres():
    appels = {"n": 0}

    def parfois(devise):
        appels["n"] += 1
        if devise == "GBP":
            raise ConnectionError("BCE injoignable")
        return {"devise": devise, "date": "2026-08-01", "valeur": 1.1}

    with patch("sources.ecb.fetch_taux_change", side_effect=parfois):
        b = ingest.etape_taux_change(_curseur(), simulation=False)

    assert b.rejetees == 1
    assert b.lues == len(ingest.DEVISES_SUIVIES) - 1
    assert any("GBP" in d for d in b.details)


def test_ecb_simulation_n_ecrit_rien():
    with patch("sources.ecb.fetch_taux_change",
               return_value={"devise": "USD", "date": "2026-08-01", "valeur": 1.14}):
        b = ingest.etape_taux_change(_curseur(), simulation=True)
    assert b.lues > 0 and b.ecrites == 0


# --- articles -----------------------------------------------------------------

def test_articles_dedoublonne_sur_le_lien():
    """Deux flux reprennent souvent la même dépêche — le lien est la clé métier."""
    articles = [_Article("https://a.fr/1"), _Article("https://a.fr/1"),
                _Article("https://a.fr/2")]
    with patch("sources.rss.collecter",
               return_value={"articles": articles, "articles_bloques": [],
                             "flux_ok": ["bfm"], "flux_echec": [], "total": 3}):
        b = ingest.etape_articles(_curseur(), simulation=False)

    assert b.ecrites == 2          # 3 lus, 1 doublon retiré
    assert b.rejetees == 1


def test_articles_bloques_sont_conserves_pas_supprimes():
    """Un article piégé reste en base pour audit — l'index partiel l'exclut des lectures."""
    hostile = _Article("https://a.fr/x", bloque=True, motifs=["ignore_instructions_fr"])
    with patch("sources.rss.collecter",
               return_value={"articles": [], "articles_bloques": [hostile],
                             "flux_ok": ["bfm"], "flux_echec": [], "total": 1}):
        b = ingest.etape_articles(_curseur(), simulation=False)

    assert b.ecrites == 1
    assert any("bloque" in d for d in b.details)


def test_articles_sans_lien_sont_ignores():
    """Le lien est la clé d'unicité en base — sans lui, la ligne est inexploitable."""
    with patch("sources.rss.collecter",
               return_value={"articles": [_Article("")], "articles_bloques": [],
                             "flux_ok": ["bfm"], "flux_echec": [], "total": 1}):
        b = ingest.etape_articles(_curseur(), simulation=False)
    assert b.ecrites == 0


# --- cours scrapés ------------------------------------------------------------

def test_scraping_rejette_une_cotation_incomplete():
    """La base impose NOT NULL sur l'OHLCV : une cotation partielle ne doit pas partir."""
    with patch("sources.scraper.collecter",
               return_value={"cotations": [_Cotation(complet=False)], "echecs": []}):
        b = ingest.etape_cours_scrapes(_curseur(), simulation=False)

    assert b.ecrites == 0 and b.rejetees == 1
    assert any("incomplet" in d for d in b.details)


def test_scraping_rejette_un_symbole_hors_univers():
    with patch("sources.scraper.collecter",
               return_value={"cotations": [_Cotation()], "echecs": []}):
        b = ingest.etape_cours_scrapes(_curseur(retour=None), simulation=False)

    assert b.ecrites == 0 and b.rejetees == 1
    assert any("hors univers" in d for d in b.details)


def test_scraping_enrichit_l_isin_manquant():
    """C3 — homogénéisation : la source qui possède la donnée comble celle qui ne l'a pas."""
    cur = _curseur(retour=("MC.PA", None))          # isin absent en base
    with patch("sources.scraper.collecter",
               return_value={"cotations": [_Cotation()], "echecs": []}):
        b = ingest.etape_cours_scrapes(cur, simulation=False)

    requetes = " ".join(str(a) for a in cur.execute.call_args_list)
    assert "UPDATE valeur SET isin" in requetes
    assert any("ISIN" in d for d in b.details)


def test_scraping_n_ecrase_pas_un_isin_deja_connu():
    cur = _curseur(retour=("MC.PA", "FR0000121014"))
    with patch("sources.scraper.collecter",
               return_value={"cotations": [_Cotation()], "echecs": []}):
        ingest.etape_cours_scrapes(cur, simulation=False)

    assert "UPDATE valeur SET isin" not in " ".join(str(a) for a in cur.execute.call_args_list)


# --- orchestration ------------------------------------------------------------

def test_une_etape_en_echec_n_emporte_pas_les_autres():
    """Une panne de la BCE ne doit pas priver le briefing des actualités."""
    def etape_ok(cur, simulation):
        return ingest.Bilan("ok", lues=1, ecrites=1)

    def etape_ko(cur, simulation):
        raise RuntimeError("source injoignable")

    with patch.dict(ingest.ETAPES, {"bonne": etape_ok, "mauvaise": etape_ko}, clear=True), \
         patch("pipelines.ingest.psycopg2.connect", return_value=MagicMock()):
        r = ingest.executer(etapes=["mauvaise", "bonne"])

    assert r["etapes_ok"] == 1
    assert [b.ok for b in r["bilans"]] == [False, True]
    assert "RuntimeError" in r["bilans"][0].erreur


def test_etape_inconnue_leve_avant_toute_connexion():
    """On échoue AVANT d'ouvrir une connexion : pas de ressource ouverte pour rien."""
    with patch("pipelines.ingest.psycopg2.connect") as connexion:
        with pytest.raises(ValueError, match="Etape\\(s\\) inconnue"):
            ingest.executer(etapes=["nexiste_pas"])
    connexion.assert_not_called()


def test_simulation_annule_la_transaction():
    conn = MagicMock()
    with patch.dict(ingest.ETAPES,
                    {"x": lambda cur, sim: ingest.Bilan("x")}, clear=True), \
         patch("pipelines.ingest.psycopg2.connect", return_value=conn):
        ingest.executer(simulation=True)

    conn.rollback.assert_called()
    conn.commit.assert_not_called()


def test_execution_reelle_valide_la_transaction():
    conn = MagicMock()
    with patch.dict(ingest.ETAPES,
                    {"x": lambda cur, sim: ingest.Bilan("x")}, clear=True), \
         patch("pipelines.ingest.psycopg2.connect", return_value=conn):
        ingest.executer(simulation=False)

    conn.commit.assert_called()


def test_la_connexion_est_fermee_meme_en_cas_d_erreur():
    conn = MagicMock()

    def explose(cur, simulation):
        raise RuntimeError("boum")

    with patch.dict(ingest.ETAPES, {"x": explose}, clear=True), \
         patch("pipelines.ingest.psycopg2.connect", return_value=conn):
        ingest.executer()

    conn.close.assert_called_once()


# --- l'indexation du RAG, étape à part entière (E5) ---------------------------

def test_l_indexation_est_une_etape_du_pipeline():
    """Le défaut qu'elle corrige, mesuré le 02/09/2026 : la collecte de 19h00 écrivait
    130 articles que l'index ne voyait pas (309 indexés pour 439 en base). Le RAG
    cherchait dans un corpus périmé d'un peu plus chaque jour, et rien ne le signalait.
    `rag/indexation.py` disait pourtant déjà, dans sa docstring, qu'on pouvait la
    relancer après chaque collecte."""
    assert "indexation" in ingest.ETAPES


def test_l_indexation_en_simulation_ne_touche_pas_a_l_index():
    """Le mode simulation doit rester vrai de bout en bout. Un `--simulation` qui
    réécrit l'index serait pire qu'inutile : il donnerait confiance à tort."""
    with patch("rag.indexation.indexer") as indexer:
        bilan = ingest.etape_indexation(_curseur(), simulation=True)

    indexer.assert_not_called()
    assert bilan.ok


def test_l_indexation_rend_les_chiffres_de_l_index_pas_un_ok():
    from rag.indexation import Resultat

    with patch("rag.indexation.indexer",
               return_value=Resultat(lus=439, indexes=439, ignores_bloques=0,
                                     avec_ticker=184)) as indexer:
        bilan = ingest.etape_indexation(_curseur(), simulation=False)

    indexer.assert_called_once()
    assert bilan.lues == 439
    assert bilan.ecrites == 439
    assert bilan.ok


def test_l_indexation_indisponible_n_emporte_pas_la_collecte():
    """⚠️ LE test qui protège la collecte de 19h00. Sur le poste d'Era, chromadb ne se
    charge pas (Smart App Control refuse une roue cp314 sans réputation). L'import doit
    donc être TARDIF : s'il était en tête de `pipelines/ingest.py`, le module entier
    deviendrait inimportable et la collecte quotidienne — taux, cotations, articles —
    s'arrêterait complètement. Ici l'étape échoue seule, et les autres passent."""
    def indexation_ko(cur, simulation):
        raise ImportError("DLL load failed while importing cygrpc")

    with patch.dict(ingest.ETAPES,
                    {"indexation": indexation_ko,
                     "rss": lambda cur, sim: ingest.Bilan("rss", lues=30, ecrites=30)},
                    clear=True), \
         patch("pipelines.ingest.psycopg2.connect", return_value=MagicMock()):
        r = ingest.executer(etapes=["indexation", "rss"])

    assert r["etapes_ok"] == 1
    assert r["bilans"][0].ok is False
    assert "ImportError" in r["bilans"][0].erreur
    assert r["bilans"][1].ecrites == 30
