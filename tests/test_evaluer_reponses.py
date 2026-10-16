"""Tâche D1 du sprint 3 : évaluer les réponses et leurs citations (spec CA1.7, CA6.4).

L'évaluation pose chaque question du jeu à `POST /question`, lit `/health`, et note pour chaque question : le statut et
le motif, la conformité à l'attendu, les articles cités, ceux qui sont hors des sources validées, et les faits attendus
retrouvés dans le texte. Un fait est « retrouvé » quand tous ses repères y figurent, comparés sans accents, sans casse
et sans tenir compte des espaces insécables. Ce contrôle automatique ne remplace pas la relecture d'Era : une réponse
fausse accompagnée d'une référence existante reste un échec, et seule une lecture le voit.

La clé d'API est lue dans `RITA_API_KEY`, jamais passée en argument, jamais écrite. Le transport HTTP est simulé.
"""
import json

import httpx
import pytest

from evals import evaluer_reponses as ev

CLE = "cle-d-essai-qui-ne-doit-apparaitre-nulle-part-0123"
IDENTITE = {"nb_articles": 2052, "id_max": 2809, "empreinte": "e" * 64, "identifiant": "id-essai"}
SANTE = {"status": "ok", "commit": "abc1234", "index": IDENTITE}


def _jeu(*questions):
    return {"version": 2, "revise_le": "2026-10-16", "corpus": {}, "questions": list(questions)}


def _q(identifiant, attendu, validees=(), motif=None, reperes=()):
    q = {"id": identifiant, "question": f"Question {identifiant} ?", "attendu": attendu,
         "sources_attendues": list(validees), "sources_validees": list(validees),
         "faits_attendus": [f"fait {i}" for i, _ in enumerate(reperes)], "reperes_attendus": [list(r) for r in reperes]}
    if motif:
        q["motif_attendu"] = motif
    return q


def _reponse(texte, *ids):
    return {"statut": "reponse", "motif": "OK", "texte": texte,
            "references": [{"n": i + 1, "table": "article", "id": a} for i, a in enumerate(ids)], "index": IDENTITE}


def _refus(motif):
    return {"statut": "refus", "motif": motif, "texte": "Je ne trouve pas cette information.", "references": []}


def _transport(par_question, appels=None):
    """`par_question` : texte de la question -> corps JSON, ou (code HTTP, corps), ou une exception à lever."""
    def gerer(requete):
        if appels is not None:
            appels.append(requete)
        if requete.url.path == "/health":
            return httpx.Response(200, json=SANTE)
        reponse = par_question[json.loads(requete.content)["question"]]
        if isinstance(reponse, Exception):
            raise reponse
        code, corps = reponse if isinstance(reponse, tuple) else (200, reponse)
        return httpx.Response(code, json=corps)
    return httpx.MockTransport(gerer)


@pytest.fixture(autouse=True)
def cle(monkeypatch):
    monkeypatch.setenv("RITA_API_KEY", CLE)


# --- les repères d'un fait -----------------------------------------------------------------------------------------

def test_un_fait_est_retrouve_sans_accents_ni_casse():
    texte = "Sanofi échappe à l'amende : l'affaire portait sur des soupçons d'ENTRAVE à la Concurrence [1]."
    assert ev.fait_retrouve(texte, ["entrave", "concurrence"])
    assert ev.fait_retrouve("Lufthansa a été DESIGNEE face à Air France–KLM [1].", ["désignée", "Air France-KLM"])
    assert not ev.fait_retrouve(texte, ["entrave", "vaccin"])     # tous les repères, pas un seul


def test_les_nombres_sont_compares_sans_espaces_insecables():
    # Le modèle écrit parfois « 1 000 » avec une espace fine insécable, ou « 6 % » collé : c'est le même fait.
    assert ev.fait_retrouve("Netflix supprime 1 000 postes, soit 6\xa0% [1].", ["1 000 postes", "6 %"])
    assert ev.fait_retrouve("Netflix supprime 1000 postes, soit 6% [1].", ["1 000 postes", "6 %"])
    assert ev.fait_retrouve("au plus 0,5 % en 2027 [1]", ["0,5 %", "2027"])


# --- la conformité à l'attendu -------------------------------------------------------------------------------------

@pytest.mark.parametrize("attendu, motif_attendu, obtenu, conforme", [
    ("reponse", None, _reponse("Texte [1].", 2788), True),
    ("reponse", None, _refus("OUT_OF_CORPUS"), False),
    ("refus", "OUT_OF_CORPUS", _refus("OUT_OF_CORPUS"), True),
    ("refus", "OUT_OF_CORPUS", _reponse("Texte [1].", 2788), False),
    ("refus", "INTENTION_INTERDITE", _refus("OUT_OF_CORPUS"), False),        # un refus, mais pas pour la bonne raison
    ("reponse_ou_abstention", None, _refus("ABSTENTION"), True),
    ("reponse_ou_abstention", None, _reponse("Texte [1].", 2788), True),
    ("reponse_ou_abstention", None, _refus("CITATIONS_INVALIDES"), False),
])
def test_un_statut_contraire_a_l_attendu_est_signale(attendu, motif_attendu, obtenu, conforme):
    jeu = _jeu(_q("Q", attendu, validees=[2788] if attendu != "refus" else [], motif=motif_attendu))
    resultat = ev.evaluer("http://api.test", jeu, transport=_transport({"Question Q ?": obtenu}))
    (ligne,) = resultat["resultats"]
    assert ligne["conforme"] is conforme
    assert (ligne["statut"], ligne["motif"]) == (obtenu["statut"], obtenu["motif"])


def test_une_reponse_qui_ne_cite_aucune_source_validee_n_est_pas_conforme():
    # Le cas mesuré de Q2 version 1 : l'article 661, d'avant la décision. Cité seul, il ne justifie pas la réponse.
    jeu = _jeu(_q("Q2", "reponse", validees=[2778, 2784]))
    resultat = ev.evaluer("http://api.test", jeu, transport=_transport({"Question Q2 ?": _reponse("T [1].", 661)}))
    (ligne,) = resultat["resultats"]
    assert ligne["conforme"] is False
    assert (ligne["cites"], ligne["hors_sources_validees"]) == ([661], [661])


def test_les_faits_retrouves_sont_notes_un_par_un():
    jeu = _jeu(_q("Q4", "reponse", validees=[2788], reperes=[["1 000 postes", "6 %"], ["courriel"]]))
    obtenu = _reponse("Netflix supprime 1 000 postes, soit 6 % de ses effectifs [1].", 2788)
    resultat = ev.evaluer("http://api.test", jeu, transport=_transport({"Question Q4 ?": obtenu}))
    (ligne,) = resultat["resultats"]
    assert [f["retrouve"] for f in ligne["faits"]] == [True, False]
    assert ligne["texte"] == obtenu["texte"]      # gardé pour la relecture de la fidélité par Era


def test_des_reperes_incomplets_arretent_l_evaluation():
    # Revue automatique de la PR #100 (P2) : `zip` s'arrêtait à la liste la plus courte. Un fait sans repère sortait
    # du décompte, et le total des faits attendus baissait sans que rien ne le signale.
    incomplete = _q("Q4", "reponse", validees=[2788], reperes=[["1 000 postes"]])
    incomplete["faits_attendus"].append("un fait sans repère")
    obtenu = _reponse("Netflix supprime 1 000 postes [1].", 2788)
    with pytest.raises(ValueError):
        ev.evaluer("http://api.test", _jeu(incomplete), transport=_transport({"Question Q4 ?": obtenu}))


def test_une_panne_est_notee_sans_arreter_l_evaluation():
    jeu = _jeu(_q("Q1", "reponse", validees=[2799]), _q("Q4", "reponse", validees=[2788]),
               _q("Q5", "reponse", validees=[2792]))
    transport = _transport({"Question Q1 ?": (503, {"statut": "erreur", "motif": "FOURNISSEUR_INDISPONIBLE",
                                                     "texte": "Le service n'a pas pu répondre."}),
                            "Question Q4 ?": httpx.ConnectError("connexion refusee"),
                            "Question Q5 ?": _reponse("0,5 % en 2027 [1].", 2792)})
    lignes = ev.evaluer("http://api.test", jeu, transport=transport)["resultats"]
    assert [(l["id"], l["statut"], l["conforme"]) for l in lignes] == [
        ("Q1", "erreur", False), ("Q4", "erreur", False), ("Q5", "reponse", True)]
    assert lignes[0]["motif"] == "FOURNISSEUR_INDISPONIBLE" and lignes[1]["motif"] == "ConnectError"


def test_l_evaluation_note_le_commit_et_l_identite_de_l_index():
    # CA6.4 : un résultat d'évaluation est lié à une version du code ET de l'index.
    jeu = _jeu(_q("Q6", "refus", motif="OUT_OF_CORPUS"))
    resultat = ev.evaluer("http://api.test", jeu, transport=_transport({"Question Q6 ?": _refus("OUT_OF_CORPUS")}))
    assert (resultat["commit"], resultat["index"]) == ("abc1234", IDENTITE)
    assert resultat["jeu"]["version"] == 2


# --- la clé d'API ---------------------------------------------------------------------------------------------------

def test_la_cle_n_est_jamais_ecrite(tmp_path, monkeypatch, capsys):
    appels = []
    transport = _transport({"Question Q4 ?": _reponse("1 000 postes [1].", 2788)}, appels)
    jeu_chemin = tmp_path / "jeu.json"
    jeu_chemin.write_text(json.dumps(_jeu(_q("Q4", "reponse", validees=[2788], reperes=[["1 000 postes"]]))),
                          encoding="utf-8")
    code = ev.main(["http://api.test", "--jeu", str(jeu_chemin), "--dossier", str(tmp_path)], transport=transport)
    assert code == 0
    # La clé est bien envoyée dans l'en-tête de la question...
    assert any(a.url.path == "/question" and a.headers["X-API-Key"] == CLE for a in appels)
    # ...mais n'apparaît ni dans le fichier écrit, ni sur la sortie.
    (fichier,) = tmp_path.glob("evaluation-*.json")
    sortie = capsys.readouterr()
    assert CLE not in fichier.read_text(encoding="utf-8") + sortie.out + sortie.err


def test_sans_cle_aucune_requete_n_est_envoyee(monkeypatch):
    monkeypatch.delenv("RITA_API_KEY")
    appels = []
    with pytest.raises(RuntimeError, match="RITA_API_KEY"):
        ev.evaluer("http://api.test", _jeu(_q("Q6", "refus", motif="OUT_OF_CORPUS")),
                   transport=_transport({}, appels))
    assert appels == []


# --- le jeu porte des repères pour chaque fait ----------------------------------------------------------------------

def test_le_jeu_porte_des_reperes_pour_chaque_fait():
    from rag.controle_questions import charger_jeu
    for q in charger_jeu()["questions"]:
        if q["attendu"] == "refus":
            continue
        reperes = q.get("reperes_attendus")
        assert isinstance(reperes, list) and len(reperes) == len(q["faits_attendus"]), q["id"]
        assert all(isinstance(r, list) and r and all(isinstance(m, str) and m.strip() for m in r) for r in reperes)
