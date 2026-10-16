"""Tests du pipeline d'agrégation (C3) — sources et base simulées.

Ce qu'on vérifie ici n'est pas « les données arrivent » (prouvé par l'exécution réelle dans
`evidence/C3/`), mais les **règles d'agrégation** : dédoublonnage, tolérance aux pannes,
mode simulation, et le fait qu'une étape en échec n'emporte pas les autres.
"""
from datetime import date
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


def test_ecb_quatre_devises_en_echec_est_un_echec_declare():
    """Carte #55 (27/09/2026) : chaque devise en echec etait attrapee, mais si les quatre echouaient
    `Bilan.erreur` restait None et le resume du soir comptait l'etape parmi les reussies, sans une ligne
    ecrite. La valorisation en euros aurait tourne sur un taux ancien sans alerte."""
    with patch("sources.ecb.fetch_taux_change", side_effect=ConnectionError("BCE injoignable")):
        b = ingest.etape_taux_change(_curseur(), simulation=False)

    assert b.ok is False
    assert b.erreur and "BCE" in b.erreur
    assert b.ecrites == 0
    assert b.rejetees == len(ingest.DEVISES_SUIVIES)


def test_ecb_une_seule_devise_recue_reste_un_succes_partiel():
    """Le succes partiel est conserve : une devise sur quatre suffit a ecrire quelque chose (et l'euro)."""
    def une_seule(devise):
        if devise != "USD":
            raise ConnectionError("BCE injoignable")
        return {"devise": "USD", "date": "2026-08-01", "valeur": 1.14}

    with patch("sources.ecb.fetch_taux_change", side_effect=une_seule),          patch("pipelines.ingest.execute_values"):
        b = ingest.etape_taux_change(_curseur(), simulation=False)

    assert b.ok is True and b.erreur is None
    assert b.ecrites == 2            # USD + EUR
    assert b.rejetees == len(ingest.DEVISES_SUIVIES) - 1


def test_ecb_simulation_n_ecrit_rien():
    with patch("sources.ecb.fetch_taux_change",
               return_value={"devise": "USD", "date": "2026-08-01", "valeur": 1.14}):
        b = ingest.etape_taux_change(_curseur(), simulation=True)
    assert b.lues > 0 and b.ecrites == 0


# --- articles -----------------------------------------------------------------

def test_articles_dedoublonne_sur_le_lien():
    """Deux flux reprennent souvent la même dépêche — le lien est la première clé.

    Depuis le 06/09/2026 il y en a une seconde, (titre, jour) : le troisième article
    porte donc un titre distinct, sinon il serait — à raison — compté comme un jumeau."""
    articles = [_Article("https://a.fr/1"), _Article("https://a.fr/1"),
                _Article("https://a.fr/2", titre="Un autre article, le meme jour")]
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


def test_articles_dedoublonne_sur_le_titre_et_la_date_dans_le_lot():
    """Mesuré le 06/09/2026 : 26 lignes en trop sur 566 — même titre, lien différent
    (Google News donne parfois deux adresses pour un même papier). Le lien ne suffit pas.
    La clé est (titre normalisé, jour de publication) : 25 groupes sur 26 partagent le
    jour ; le 26ᵉ (« BNP : la tendance baissière peut reprendre », 28/08 et 02/09) est
    une vraie analyse récurrente et doit rester."""
    a = _Article("https://a.fr/1", titre="L'Oréal bondit en Bourse")
    b = _Article("https://b.fr/9", titre="L’Oreal bondit en bourse")      # apostrophe typographique, sans accent
    c = _Article("https://c.fr/3", titre="L'Oréal bondit en Bourse")
    c.publie_le = "2026-08-02T06:00:00+00:00"                              # même titre, autre jour : conservé
    with patch("sources.rss.collecter",
               return_value={"articles": [a, b, c], "articles_bloques": [],
                             "flux_ok": ["bfm"], "flux_echec": [], "total": 3}):
        bilan = ingest.etape_articles(_curseur(), simulation=False)

    assert bilan.ecrites == 2
    assert bilan.rejetees == 1


def test_articles_deja_en_base_au_meme_titre_et_jour_sont_ignores():
    """Deux jumeaux ne doivent pas non plus entrer à deux collectes différentes.

    Sprint 3, tâche B1 : la lecture des positions a disparu, la requête de dédoublonnage est donc la première (et la
    seule) lecture de l'étape. L'ancien premier `[]` répondait à la lecture des positions."""
    cur = _curseur()
    cur.fetchall.side_effect = [[("L'Oréal bondit en Bourse", "2026-08-01")]]
    with patch("sources.rss.collecter",
               return_value={"articles": [_Article("https://z.fr/1", titre="L'Oreal bondit en bourse")],
                             "articles_bloques": [], "flux_ok": ["bfm"], "flux_echec": [], "total": 1}):
        bilan = ingest.etape_articles(cur, simulation=False)

    assert bilan.ecrites == 0
    assert bilan.rejetees == 1


# --- Sprint 3, tâche B1 : plus aucune requête Google News (décision D3, CA4.4) ------------------------------------
# Chaque soir, la collecte envoyait à Google News le nom des entreprises détenues, donc une information tirée du
# portefeuille. La décision D3 l'arrête : l'étape n'interroge plus que les trois flux de presse générale et ne lit plus
# les positions. Les articles Google News déjà en base restent dans le corpus (registre, tâche C1).

def _collecte_vide():
    return {"articles": [], "articles_bloques": [], "flux_ok": ["bfm_eco"], "flux_echec": [], "total": 0}


@pytest.mark.parametrize("periode", [None, ("2026-09-12", "2026-09-18")])
def test_la_collecte_n_interroge_plus_google_news(periode):
    cur = _curseur()
    cur.fetchall.return_value = [("SANOFI",)]          # une entreprise détenue, si l'étape allait la chercher
    with patch("sources.rss.collecter", return_value=_collecte_vide()) as collecte:
        ingest.etape_articles(cur, simulation=True, periode=periode)
    assert "flux_supplementaires" not in collecte.call_args.kwargs
    assert "news.google.com" not in repr(collecte.call_args)


def test_la_collecte_ne_lit_plus_les_positions():
    cur = _curseur()
    cur.fetchall.return_value = []
    with patch("sources.rss.collecter", return_value=_collecte_vide()):
        ingest.etape_articles(cur, simulation=True)
    requetes = " ".join(str(appel.args[0]) for appel in cur.execute.call_args_list if appel.args).lower()
    assert "position" not in requetes


def test_le_module_rss_ne_sait_plus_interroger_google_news():
    import inspect

    from sources import rss
    assert not hasattr(rss, "flux_par_entreprise")
    assert not hasattr(rss, "MODELE_GOOGLE_NEWS")
    assert "flux_supplementaires" not in inspect.signature(rss.collecter).parameters
    assert all("news.google.com" not in url for url in rss.FLUX.values())


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
    def indexation_ko(cur, simulation, dsn=None):   # même signature que l'étape réelle (dsn depuis le 20/09)
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


# --- revue automatisée, PR #1 (19/09/2026) : l'indexation doit utiliser le DSN du pipeline --------------

def test_l_indexation_recoit_le_dsn_choisi_par_le_pipeline():
    """Avant : `indexer()` sans argument — avec `--dsn`, les articles allaient dans une base et
    l'index se reconstruisait depuis une autre (ou échouait sans DATABASE_URL)."""
    from rag.indexation import Resultat
    with patch("rag.indexation.indexer", return_value=Resultat(1, 1, 0, 0)) as indexer:
        ingest.etape_indexation(_curseur(), simulation=False, dsn="postgresql://x/y")
    indexer.assert_called_once_with(dsn="postgresql://x/y")


def test_le_pipeline_transmet_le_dsn_a_l_etape_indexation():
    assert "indexation" in ingest.ETAPES_AVEC_DSN


# --- revue automatisée, PR #13 : le conteneur one-shot doit ECHOUER quand l'indexation échoue ----------------

def test_en_mode_strict_un_echec_d_etape_donne_un_code_de_sortie_non_nul():
    """`docker compose run --rm indexation` rendait 0 même avec un bilan en échec : un opérateur ou un
    script ne pouvait pas voir que le volume restait vide. `--strict` : une étape en échec = code 1.
    Le pipeline nocturne, lui, garde son comportement (une panne BCE ne doit pas marquer la nuit en échec)."""
    resultat = {"bilans": [ingest.Bilan("indexation", erreur="ImportError: cygrpc")], "etapes_ok": 0}
    assert ingest.code_de_sortie(resultat, strict=True) == 1
    assert ingest.code_de_sortie(resultat, strict=False) == 0
    assert ingest.code_de_sortie({"bilans": [ingest.Bilan("indexation", lues=3, ecrites=3)], "etapes_ok": 1}, strict=True) == 0


def test_le_service_compose_indexation_est_strict():
    import yaml
    from pathlib import Path
    compose = yaml.safe_load((Path(__file__).parent.parent / "docker-compose.yml").read_text(encoding="utf-8"))
    assert "--strict" in compose["services"]["indexation"]["command"]


# --- 27/09/2026 : issues #49, #48 et #52 -------------------------------------------

def test_un_cours_scrape_le_samedi_est_range_au_vendredi(sans_execute_values):
    """Collecte du samedi 26/09/2026 à 19h00 (17h00 UTC) : la page montre la clôture du
    vendredi. La ranger sous le samedi créait une séance fictive (#49)."""
    cotation = _Cotation()
    cotation.collecte_le = "2026-09-26T17:00:00+00:00"
    cur = _curseur(retour=("MC.PA", "FR0000121014"))
    with patch("sources.scraper.collecter",
               return_value={"cotations": [cotation], "echecs": []}):
        ingest.etape_cours_scrapes(cur, simulation=False)

    ligne = sans_execute_values.call_args.args[2][0]
    assert ligne[1] == date(2026, 9, 25)


def test_les_valeurs_radiees_ne_sont_plus_demandees_a_yahoo():
    """ZC.PA, ELE.PA, GTO.PA échouaient chaque soir (« possibly delisted ») : #48."""
    cur = _curseur()
    cur.fetchall.return_value = [("MC.PA", date(2026, 9, 24), "OK"),
                                 ("ZC.PA", date(2018, 3, 22), "DELISTEE")]
    with patch("sources.cotations.fetch_cotations", return_value=[]) as fetch:
        b = ingest.etape_cotations(cur, simulation=True)

    demandes = [t for appel in fetch.call_args_list for t in appel.args[0]]
    assert demandes == ["MC.PA"]
    assert any("radi" in d for d in b.details)


def test_l_etape_fred_ecrit_les_observations(sans_execute_values):
    def fausse_serie(serie, limite=1):
        return [{"date": "2026-09-24", "valeur": 5.18}]

    with patch("sources.fred.fetch_indicateur", side_effect=fausse_serie):
        b = ingest.etape_fred(_curseur(), simulation=False)

    lignes = sans_execute_values.call_args.args[2]
    assert ("DGS10", date(2026, 9, 24), 5.18) in lignes
    assert b.ecrites == 3                          # DGS10, CPIAUCSL, DFF


def test_une_serie_fred_en_echec_n_emporte_pas_les_autres(sans_execute_values):
    def parfois(serie, limite=1):
        if serie == "CPIAUCSL":
            raise RuntimeError("FRED indisponible")
        return [{"date": "2026-09-24", "valeur": 3.88}]

    with patch("sources.fred.fetch_indicateur", side_effect=parfois):
        b = ingest.etape_fred(_curseur(), simulation=False)

    assert b.ecrites == 2
    assert b.rejetees == 1


def test_fred_fait_partie_de_la_collecte_du_soir():
    assert "fred" in ingest.ETAPES


def test_l_etape_fred_est_en_echec_quand_aucune_serie_ne_repond(sans_execute_values):
    """Revue automatisée, PR #54 : clé absente ou FRED indisponible, toutes les séries échouent,
    mais `Bilan.erreur` restait None et le résumé du soir comptait l'étape parmi les
    réussies, sans une ligne écrite. Succès partiel conservé ; zéro ligne = échec."""
    with patch("sources.fred.fetch_indicateur", side_effect=RuntimeError("cle absente")):
        b = ingest.etape_fred(_curseur(), simulation=False)

    assert b.ok is False
    assert b.ecrites == 0
    assert "FRED" in b.erreur
