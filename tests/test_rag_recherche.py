"""Tests de la recherche hybride — `rag/recherche.py` (E3).

## Ce que ces tests protègent

La recherche hybride existe parce qu'une mesure du 28/08 a montré que le moteur dense
seul classait un article **Sanofi** devant un article **TotalEnergies** quand on
cherchait « TotalEnergies ». Les tests ci-dessous verrouillent les trois mécanismes qui
corrigent ça :

1. **La fusion RRF remonte un document mal classé par un moteur** s'il est bien classé
   par l'autre. C'est toute la raison d'être de l'hybride.
2. **Le refus exige une preuve.** « Recette de la tarte aux pommes » ne doit rien rendre,
   alors qu'un seul mot commun (« recette », au sens de *recettes fiscales*) suffisait à
   passer dans la première version.
3. **Le filtre par ticker est déterministe** et s'applique **avant** la recherche.

Les tests de fusion et de refus n'utilisent **ni base ni ChromaDB** : ils portent sur les
fonctions pures. Les tests de bout en bout construisent un index jetable dans `tmp_path`.
"""
from pathlib import Path

import pytest

from rag import indexation, recherche
from rag.recherche import decouper_en_mots, _rrf, K_RRF


# --- découpage en mots --------------------------------------------------------

def test_les_mots_vides_sont_ecartes():
    """Sans ce filtre, BM25 juge « les » aussi informatif que « TotalEnergies »,
    et toute question finit par ressembler à toutes les autres."""
    assert decouper_en_mots("les resultats de la societe") == ["resultats", "societe"]


def test_les_accents_sont_retires_pour_comparer():
    assert decouper_en_mots("résultats trimestriels") == ["resultats", "trimestriels"]


def test_les_mots_d_une_lettre_sont_ecartes():
    assert decouper_en_mots("l'action a monte") == ["action", "monte"]


# --- fusion RRF ---------------------------------------------------------------

def test_le_premier_rang_vaut_plus_que_le_second():
    assert _rrf(0) > _rrf(1) > _rrf(2)


def test_rrf_amortit_l_ecart_entre_les_premiers_rangs():
    """C'est la propriété qui rend la fusion utile : l'écart entre le 1ᵉʳ et le 2ᵉ est
    faible, donc un document bien classé dans **les deux** listes passe devant un
    document premier dans une seule."""
    ecart_haut = _rrf(0) - _rrf(1)
    somme_deux_seconds = _rrf(1) + _rrf(1)
    assert somme_deux_seconds > _rrf(0)      # deux 2ᵉ places battent une 1ʳᵉ
    assert ecart_haut < _rrf(0) / 2          # l'écart reste modéré


def test_la_constante_rrf_est_celle_de_la_litterature():
    assert K_RRF == 60


# --- bout en bout, sur un index jetable --------------------------------------

def _index_jetable(monkeypatch, tmp_path: Path, articles):
    """Construit un index ChromaDB de test à partir d'articles simulés."""
    from datetime import datetime

    lignes = [{"id": i, "source": "test", "titre": t, "resume": r,
               "lien": f"https://exemple.test/{i}", "publie_le": datetime(2026, 8, 28),
               "bloque_injection": False}
              for i, (t, r) in enumerate(articles, start=1)]

    def faux(sql, nom, dsn=None, **kw):
        class E:
            pass
        e = E()
        if "bloque_injection" in sql:
            e.lignes = lignes
        elif "nom_officiel" in sql:
            e.lignes = [{"ticker": "MC.PA", "nom_officiel": "LVMH MOET VUITTON"}]
        else:
            e.lignes = []
        return e

    monkeypatch.setattr(indexation.database, "_executer", faux)
    indexation.indexer(chemin=tmp_path)


CORPUS = [
    ("LVMH publie des resultats semestriels en hausse", "Le numero un du luxe progresse"),
    ("La BCE maintient ses taux directeurs", "La banque centrale europeenne temporise"),
    ("Le Livret A regagne de l interet", "Les depots progressent en juillet"),
]


def test_une_question_couverte_par_le_corpus_rend_un_passage(monkeypatch, tmp_path):
    _index_jetable(monkeypatch, tmp_path, CORPUS)
    r = recherche.rechercher("resultats semestriels du luxe", chemin=tmp_path, k=2)
    assert r.trouve is True
    assert r.motif == "OK"
    assert "LVMH" in r.passages[0].texte


def test_une_question_hors_corpus_est_REFUSEE(monkeypatch, tmp_path):
    """LE test du fichier. Sans refus, la recherche rendrait le *moins mauvais*
    document — mesuré le 28/08 : la question « résultats d'une entreprise du luxe »
    rendait une dépêche sur une péniche, faute de mieux dans le corpus."""
    _index_jetable(monkeypatch, tmp_path, CORPUS)
    r = recherche.rechercher("recette de la tarte aux pommes", chemin=tmp_path)
    assert r.trouve is False
    assert r.motif == "OUT_OF_CORPUS"
    assert r.passages == []


def test_une_question_a_intention_interdite_est_refusee_avant_la_base(monkeypatch, tmp_path):
    """Garde-fou d'ENTREE (18/09, question G de CONTINUITE.md) : une intention interdite
    se refuse sur la question elle-même. AUCUN _index_jetable ici — le refus doit
    intervenir avant tout accès au corpus, sinon ce n'est pas un garde-fou d'entrée."""
    r = recherche.rechercher("Quelle action dois-je acheter demain pour gagner 20 % ?",
                              chemin=tmp_path)
    assert r.trouve is False
    assert r.motif == "INTENTION_INTERDITE"
    assert r.passages == []


def test_un_seul_mot_commun_ne_suffit_PAS_a_repondre(monkeypatch, tmp_path):
    """Première version du refus : « score BM25 > 0 ». Elle acceptait « recette de la
    tarte aux pommes » parce que « recette » veut aussi dire *recettes fiscales*.
    La règle exige désormais la **moitié** des mots significatifs de la question."""
    _index_jetable(monkeypatch, tmp_path, CORPUS)
    r = recherche.rechercher("taux de change du yen japonais", chemin=tmp_path)
    # « taux » est présent dans l'article BCE, mais 1 mot sur 4 ne fait pas une réponse
    assert r.motif == "OUT_OF_CORPUS"


def test_le_passage_rendu_porte_de_quoi_le_citer(monkeypatch, tmp_path):
    """Un RAG qui ne cite pas ses sources ne vaut pas mieux qu'un modèle qui invente."""
    _index_jetable(monkeypatch, tmp_path, CORPUS)
    p = recherche.rechercher("resultats semestriels du luxe", chemin=tmp_path).passages[0]
    assert p.source == "test"
    assert p.lien.startswith("https://")
    assert p.publie_le.startswith("2026-08-28")


def test_le_filtre_par_ticker_restreint_avant_la_recherche(monkeypatch, tmp_path):
    _index_jetable(monkeypatch, tmp_path, CORPUS)
    r = recherche.rechercher("resultats semestriels", ticker="MC.PA", chemin=tmp_path)
    assert r.nb_candidats == 1               # seul l'article LVMH porte ce ticker
    assert r.passages[0].tickers == ["MC.PA"]


def test_un_ticker_absent_du_corpus_donne_un_refus_et_non_une_erreur(monkeypatch, tmp_path):
    """⚠️ Écrit après un vrai plantage : la recherche dense interroge toute la
    collection, donc elle rendait des identifiants écartés par le filtre, et la suite
    plantait sur `list.index(x): x not in list`."""
    _index_jetable(monkeypatch, tmp_path, CORPUS)
    r = recherche.rechercher("resultats", ticker="INEXISTANT.PA", chemin=tmp_path)
    assert r.motif == "OUT_OF_CORPUS"
    assert r.nb_candidats == 0


def test_les_rangs_des_deux_moteurs_sont_rendus(monkeypatch, tmp_path):
    """La traçabilité de la fusion : on doit pouvoir dire d'où vient un résultat.
    Sans ça, impossible de conduire l'ablation D0 → H1 de l'étape E5."""
    _index_jetable(monkeypatch, tmp_path, CORPUS)
    p = recherche.rechercher("resultats semestriels du luxe", chemin=tmp_path).passages[0]
    assert p.rang_dense is not None or p.rang_lexical is not None
    assert p.score_lexical >= 0


# --- ce que l'ablation D0 → H1 exige du moteur (étape E5) ---------------------

def test_un_passage_porte_l_identifiant_de_son_article(monkeypatch, tmp_path):
    """Sans lui, impossible de comparer un résultat au jeu annoté : la vérité terrain
    est écrite en identifiants d'articles (`evals/questions_rag.txt`), et un passage
    qui ne dit pas d'où il vient ne peut être ni compté juste ni compté faux."""
    _index_jetable(monkeypatch, tmp_path, CORPUS)
    p = recherche.rechercher("resultats semestriels du luxe", chemin=tmp_path).passages[0]
    assert p.article_id == 1          # LVMH est le 1ᵉʳ article du corpus de test


def test_le_mode_dense_n_utilise_pas_le_classement_lexical(monkeypatch, tmp_path):
    """Le bras **D0** de l'ablation : dense seul, sans BM25 ni fusion RRF.

    Sans ce mode, on ne peut pas mesurer ce que l'hybride apporte — on ne pourrait
    qu'affirmer qu'il apporte quelque chose. C'est exactement la différence entre
    « avancé » et « annoncé »."""
    _index_jetable(monkeypatch, tmp_path, CORPUS)
    r = recherche.rechercher("resultats semestriels du luxe", chemin=tmp_path, mode="dense")
    assert r.trouve is True
    assert all(p.rang_lexical is None for p in r.passages)
    assert all(p.rang_dense is not None for p in r.passages)


def test_le_mode_hybride_reste_celui_par_defaut(monkeypatch, tmp_path):
    """L'ajout du paramètre ne doit RIEN changer aux appelants existants :
    `graph/workflow.py` appelle `rechercher()` sans mode."""
    _index_jetable(monkeypatch, tmp_path, CORPUS)
    defaut = recherche.rechercher("resultats semestriels du luxe", chemin=tmp_path)
    explicite = recherche.rechercher("resultats semestriels du luxe", chemin=tmp_path,
                                     mode="hybride")
    assert [p.article_id for p in defaut.passages] == [p.article_id for p in explicite.passages]


def test_un_mode_inconnu_est_refuse_bruyamment(monkeypatch, tmp_path):
    """Une faute de frappe dans un nom de bras fausserait silencieusement toute une
    campagne de mesure : « dense » écrit « dese » retomberait sur l'hybride et on
    conclurait que les deux bras se valent."""
    _index_jetable(monkeypatch, tmp_path, CORPUS)
    with pytest.raises(ValueError, match="mode"):
        recherche.rechercher("resultats", chemin=tmp_path, mode="dese")
