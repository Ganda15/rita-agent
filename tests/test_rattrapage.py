"""Rattrapage d'une periode de collecte manquee (C1) — sources et base simulees.

Contexte : 4 collectes sur 7 coupees du 13 au 17/09/2026 (ETAT.md, 18/09). Ce qui se
rattrape : les taux BCE (l'API accepte startPeriod/endPeriod) et les articles Google News
par entreprise (la requete accepte after:/before:). Ce qui ne se rattrape pas : la presse
generale (flux de 20 a 30 items, tous du jour).

Un seul chemin d'ecriture : les etapes existantes recoivent une `periode` optionnelle.
"""
from unittest.mock import MagicMock, patch

from pipelines import ingest
from sources import rss
from sources.ecb import fetch_taux_change_periode

PERIODE = ("2026-09-12", "2026-09-18")


def _curseur() -> MagicMock:
    cur = MagicMock()
    cur.__enter__ = MagicMock(return_value=cur)
    cur.__exit__ = MagicMock(return_value=False)
    return cur


def _fausse_reponse_periode():
    r = MagicMock()
    r.raise_for_status.return_value = None
    r.json.return_value = {
        "dataSets": [{"series": {"0:0:0:0:0": {"observations": {
            "0": [1.1551, 0, 0, None, None],
            "1": [1.1539, 0, 0, None, None],
            "2": [1.1537, 0, 0, None, None]}}}}],
        "structure": {"dimensions": {"observation": [{"values": [
            {"id": "2026-09-14"}, {"id": "2026-09-15"}, {"id": "2026-09-16"}]}]}},
    }
    return r


# --- Google News : la fenetre de dates dans la requete -------------------------

def test_flux_entreprise_avec_periode_porte_after_et_before():
    flux = rss.flux_par_entreprise(["SANOFI"], periode=PERIODE)
    (nom, url), = flux.items()
    assert nom.startswith("ent_")
    assert "after%3A2026-09-12" in url
    assert "before%3A2026-09-18" in url


def test_flux_entreprise_sans_periode_est_inchange():
    (_, url), = rss.flux_par_entreprise(["SANOFI"]).items()
    assert "after" not in url and "before" not in url


# --- BCE : une periode, plusieurs observations ---------------------------------

def test_ecb_periode_rend_une_ligne_par_jour_publie():
    with patch("sources.ecb.httpx.get", return_value=_fausse_reponse_periode()) as mock_get:
        lignes = fetch_taux_change_periode("USD", *PERIODE)

    assert [l["date"] for l in lignes] == ["2026-09-14", "2026-09-15", "2026-09-16"]
    assert lignes[0] == {"devise": "USD", "date": "2026-09-14", "valeur": 1.1551}
    params = mock_get.call_args.kwargs["params"]
    assert params["startPeriod"] == "2026-09-12" and params["endPeriod"] == "2026-09-18"
    assert "lastNObservations" not in params


# --- Les etapes du pipeline avec une periode -----------------------------------

def test_etape_ecb_avec_periode_ecrit_toutes_les_dates_et_l_euro_pour_chacune():
    deux_jours = [{"devise": "USD", "date": "2026-09-14", "valeur": 1.15},
                  {"devise": "USD", "date": "2026-09-16", "valeur": 1.16}]
    with patch("sources.ecb.fetch_taux_change_periode", return_value=deux_jours), \
         patch("pipelines.ingest.execute_values") as ecriture:
        b = ingest.etape_taux_change(_curseur(), simulation=False, periode=PERIODE)

    lignes = ecriture.call_args.args[2]
    assert b.ecrites == len(ingest.DEVISES_SUIVIES) * 2 + 2   # 4 devises x 2 jours + EUR x 2
    assert ("EUR", "2026-09-14", 1.0) in lignes
    assert ("EUR", "2026-09-16", 1.0) in lignes


def test_etape_articles_avec_periode_interroge_google_news_sur_la_fenetre():
    cur = _curseur()
    cur.fetchall.side_effect = [[("SANOFI",)], []]
    with patch("sources.rss.collecter",
               return_value={"articles": [], "articles_bloques": [],
                             "flux_ok": [], "flux_echec": [], "total": 0}) as collecte:
        ingest.etape_articles(cur, simulation=False, periode=PERIODE)

    kwargs = collecte.call_args.kwargs
    assert kwargs["limite_par_flux"] == 100
    (url,) = kwargs["flux_supplementaires"].values()
    assert "after%3A2026-09-12" in url


def test_executer_transmet_la_periode_a_ecb_et_rss_seulement():
    periodes, autres = [], []

    def etape_avec_periode(cur, simulation, periode=None, **kw):
        periodes.append(periode)
        return ingest.Bilan("x")

    def etape_sans_periode(cur, simulation):
        autres.append("appelee sans periode")
        return ingest.Bilan("y")

    with patch.dict(ingest.ETAPES, {"ecb": etape_avec_periode, "cotations": etape_sans_periode,
                                    "rss": etape_avec_periode}, clear=True), \
         patch("pipelines.ingest.psycopg2.connect", return_value=MagicMock()):
        r = ingest.executer(etapes=["ecb", "cotations", "rss"], periode=PERIODE)

    assert r["etapes_ok"] == 3
    assert periodes == [PERIODE, PERIODE]
    assert autres == ["appelee sans periode"]
