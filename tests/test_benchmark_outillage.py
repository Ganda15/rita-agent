"""Le banc C7, côté outillage : construction du jeu, notation à l'aveugle, prix, affichage, et surtout le
traçage coupé. Le 03/10/2026, construire le jeu a écrit 22 traces `rag` dans le projet Langfuse de production
(même défaut qu'INC-006, par un autre chemin) : le banc doit couper le traçage avant de toucher au code de RITA."""
import csv
import json
import os

import pytest

from evals import benchmark_fournisseurs as banc

CAS = {"ticker": "MC.PA", "price": 378.55, "change_pct": -0.25, "adtv20": 1234.0, "currency": "EUR",
       "fraicheur_jours": 1, "cotation_perimee": False, "passages": []}


class _Passage:
    def en_dict(self):
        return {"source": "bfm", "publie_le": "2026-10-01", "texte": "un article", "ticker": "MC.PA", "titre": "t"}


class _Resultat:
    passages = [_Passage()]
    motif = "OK"


def test_construire_jeu_fige_ce_que_le_scout_lit_et_ce_que_la_recherche_retrouve():
    questions = []

    def collecter(t):
        return {**CAS, "ticker": t, "indicateurs": {"nom_officiel": "LVMH Moet Hennessy"}}

    def rechercher(question, ticker=None):
        questions.append((question, ticker)); return _Resultat()

    jeu = banc.construire_jeu(["MC.PA"], collecter=collecter, rechercher=rechercher)
    assert jeu["cas"][0]["ticker"] == "MC.PA" and jeu["cas"][0]["passages"][0]["source"] == "bfm"
    assert questions == [("actualite LVMH", "MC.PA")], "la même question que le nœud rag du graphe"
    assert "fige_le" in jeu


def test_la_notation_a_l_aveugle_separe_les_textes_de_la_cle(tmp_path):
    lignes = [{"fournisseur": "openrouter", "modele": "m", "ticker": "MC.PA", "repetition": 1, "horodatage": "h",
               "erreur": None, "texte": "texte un\nsur deux lignes"},
              {"fournisseur": "anthropic", "modele": "n", "ticker": "OR.PA", "repetition": 1, "horodatage": "h",
               "erreur": None, "texte": "texte deux"},
              {"fournisseur": "openrouter", "modele": "m", "ticker": "AI.PA", "repetition": 1, "horodatage": "h",
               "erreur": "TimeoutError", "texte": None}]
    banc.ecrire_notation_a_l_aveugle(lignes, tmp_path, "2026-10-03")
    notes = list(csv.DictReader(open(tmp_path / "notes-francais-2026-10-03.csv", encoding="utf-8"), delimiter=";"))
    cle = list(csv.DictReader(open(tmp_path / "notes-francais-2026-10-03-cle.csv", encoding="utf-8"), delimiter=";"))
    assert len(notes) == 2 and len(cle) == 2, "l'appel en échec n'est pas à noter"
    assert all("fournisseur" not in n for n in notes) and "\n" not in notes[0]["texte"]
    assert {c["fournisseur"] for c in cle} == {"openrouter", "anthropic"}


def test_le_prix_openrouter_est_lu_sur_la_page_publique_et_cite(monkeypatch):
    class _R:
        def json(self):
            return {"data": [{"id": "anthropic/claude-sonnet-4.5", "pricing": {"prompt": "0.000003", "completion": "0.000015"}}]}

    monkeypatch.setattr("httpx.get", lambda url, timeout: _R())
    prix, source = banc.prix_openrouter("anthropic/claude-sonnet-4.5")
    assert prix == (3.0, 15.0) and source.startswith("https://openrouter.ai")


def test_un_modele_absent_de_la_grille_donne_un_prix_inconnu(monkeypatch):
    class _R:
        def json(self):
            return {"data": []}

    monkeypatch.setattr("httpx.get", lambda url, timeout: _R())
    prix, source = banc.prix_openrouter("x/y")
    assert prix is None and "absent" in source


def test_une_page_de_prix_injoignable_ne_casse_pas_le_banc(monkeypatch):
    def casse(url, timeout):
        raise ConnectionError("hors ligne")

    monkeypatch.setattr("httpx.get", casse)
    prix, source = banc.prix_openrouter("x/y")
    assert prix is None and "inconnu" in source


def test_l_affichage_dit_les_indisponibles_et_les_intervalles(capsys):
    etat = {"foundry": {"statut": "indisponible", "motif": "KeyError"}, "openrouter": {"statut": "mesure", "motif": ""}}
    resume = {"openrouter": {"appels": 2, "reussis": 2, "intervalle_disponibilite": (0.3, 1.0), "conformes_amf": 2,
                             "intervalle_conformes": (0.3, 1.0), "fideles": 1, "intervalle_fideles": (0.1, 0.9),
                             "latence_p50_s": 1.0, "latence_p95_s": 2.0, "jetons_entree_moyen": 500.0,
                             "jetons_sortie_moyen": 200.0, "cout_total_usd": 0.01, "cout_moyen_usd": 0.005}}
    banc._afficher(resume, etat)
    sortie = capsys.readouterr().out
    assert "indisponible" in sortie and "[0.30 ; 1.00]" in sortie


def test_le_banc_coupe_le_tracage_avant_de_toucher_au_code_de_rita(monkeypatch, tmp_path):
    """INC-006 bis : construire le jeu appelle la recherche, qui ouvre une trace Langfuse. Jamais en production."""
    monkeypatch.delenv("LANGFUSE_TRACING_ENABLED", raising=False)
    vus = {}

    def collecter(t):
        vus["tracage"] = os.environ.get("LANGFUSE_TRACING_ENABLED"); return {**CAS, "ticker": t}

    monkeypatch.setattr(banc, "construire_jeu", lambda tickers, collecter=None, rechercher=None:
                        {"fige_le": "2026-10-03", "cas": [collecter_(t) for t in tickers for collecter_ in [collecter or collecter_defaut]]})
    collecter_defaut = collecter
    code = banc.main(["--construire", "MC.PA", "--sortie", str(tmp_path)])
    assert code == 0 and vus["tracage"] == "false"
    assert (tmp_path / "jeu-d-essai-2026-10-03.json").exists() or list(tmp_path.glob("jeu-d-essai-*.json"))


def test_main_sans_jeu_ni_construction_refuse():
    with pytest.raises(SystemExit):
        banc.main([])


def test_main_mesure_depuis_un_jeu_fige_avec_des_appels_injectes(monkeypatch, tmp_path):
    chemin = tmp_path / "jeu.json"
    chemin.write_text(json.dumps({"fige_le": "2026-10-03", "cas": [CAS]}), encoding="utf-8")
    monkeypatch.setattr(banc, "prix_openrouter", lambda modele: ((3.0, 15.0), "test"))

    class _Rep:
        texte, usage, modele = "LVMH clôture à 378,55 EUR, en baisse.", {"input": 10, "output": 5}, "m"

    monkeypatch.setattr(banc, "appel_reel", lambda nom, prompt, max_tokens: _Rep())
    code = banc.main(["--jeu", str(chemin), "--repetitions", "1", "--plafond", "1", "--sortie", str(tmp_path),
                      "--fournisseurs", "openrouter"])
    assert code == 0
    assert list(tmp_path.glob("resultats-*.jsonl")) and list(tmp_path.glob("resume-*.json"))
    assert os.environ.get("LANGFUSE_TRACING_ENABLED") == "false"


# --- Carte #82 (10/10/2026) : le banc compare les fournisseurs approuvés UE ------------------------------------
#
# Anthropic et OpenRouter sont retirés de `src/llm.py`. Les 120 appels OpenRouter du 03/10 restent dans
# `evidence/C7/` comme mesure datée ; le banc relit toujours ces lignes, mais n'appelle plus que Foundry et Mistral.

def test_le_banc_compare_les_fournisseurs_approuves_ue():
    assert banc.FOURNISSEURS == ("foundry", "mistral")


def test_le_prix_de_mistral_est_cite_avec_sa_source():
    """Prix de Mistral Large 4 (`mistral-large-4-0`), le modèle du code depuis le 10/10/2026, lu sur la grille
    officielle de la documentation : prix soldé, le prix normal cité à côté."""
    prix, source = banc.PRIX_PUBLICS["mistral"]
    assert prix == (0.68, 2.09)
    assert "https://docs.mistral.ai/models/pricing" in source and "10/10/2026" in source
    assert "mistral-large-4-0" in source and "1,36" in source and "4,18" in source


def test_le_banc_ne_depend_plus_d_openrouter_pour_ses_prix(tmp_path, monkeypatch):
    """`main` ne lit plus le catalogue d'OpenRouter : il le faisait pour `_modele_prevu("openrouter")`, qui n'existe plus."""
    chemin = tmp_path / "jeu.json"
    chemin.write_text(json.dumps({"fige_le": "2026-10-03", "cas": [CAS]}), encoding="utf-8")

    def interdit(modele):
        raise AssertionError("le catalogue d'OpenRouter ne doit plus être lu")

    monkeypatch.setattr(banc, "prix_openrouter", interdit)

    class _Rep:
        texte, usage, modele = "LVMH clôture à 378,55 EUR, en baisse.", {"input": 10, "output": 5}, "m"

    monkeypatch.setattr(banc, "appel_reel", lambda nom, prompt, max_tokens: _Rep())
    code = banc.main(["--jeu", str(chemin), "--repetitions", "1", "--plafond", "1", "--sortie", str(tmp_path),
                      "--fournisseurs", "mistral"])
    assert code == 0
    lignes = [json.loads(l) for f in tmp_path.glob("resultats-*.jsonl") for l in f.read_text(encoding="utf-8").splitlines()]
    assert lignes and all(l["fournisseur"] == "mistral" for l in lignes)
    assert all(l["cout_usd"] > 0 for l in lignes), "le prix public de Mistral doit servir au coût"
