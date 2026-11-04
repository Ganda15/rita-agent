"""Les cas de vérification du chapitre « Données » (validé par le formateur le 03/10/2026) qui
n'avaient encore aucun test (issue #61).

Le chapitre définit 32 cas (D01-D08 exactitude, R01-R14 pertinence, A01-A10 accès). La
cartographie complète cas → test est dans `evidence/C12/cas-de-verification-chapitre-donnees.md` :
la plupart étaient déjà couverts sous d'autres noms. Ici, les quatre qui manquaient et qui se
testent sans base ni zone sous garde. Chaque test porte le numéro du cas dans son nom, pour
qu'un jury retrouve le cas depuis le rapport de pytest.

Deux sont des tests de contrat sur un fichier SQL : ils lisent le texte et vérifient la règle
écrite. Ils ne prouvent pas que PostgreSQL l'exécute, mais ils figent la règle : le jour où
quelqu'un remplace « à ou avant » par une égalité stricte, la suite le dit.
"""
import re
from pathlib import Path
from unittest.mock import patch

from agents.analyst import generate_briefing
from tests.conftest import faux_resultat_texte
from rag import recherche
from tests.test_analyst import prompt_produit
from tests.test_rag_recherche import _index_jetable

RACINE = Path(__file__).resolve().parent.parent
SCHEMA = (RACINE / "db" / "schema.sql").read_text(encoding="utf-8")
INDICATEURS = (RACINE / "db" / "indicateurs.sql").read_text(encoding="utf-8")


# --- D02 : prix invalide, volume négatif, devise inconnue → rejet ------------------------------
# Prix et volume sont déjà testés (CHECK du schéma, rejets de l'import). Il manquait la devise.

def test_D02_une_devise_inconnue_est_rejetee_par_la_base():
    """Chaque colonne `devise` référence la table `devise` : une devise inconnue ne peut pas
    entrer, ni dans une valeur, ni dans une position, ni dans un taux."""
    cles = re.findall(r"^\s*devise\s+CHAR\(3\)[^\n]*REFERENCES devise \(code\)", SCHEMA, re.M)
    assert len(cles) >= 3, f"attendu valeur, position, taux_change : {len(cles)} trouvée(s)"


# --- D05 : performance sur une période dont la date cible n'a pas de cotation ------------------

def test_D05_la_reference_de_performance_est_la_derniere_seance_a_ou_avant_la_date_cible():
    """Un jour férié ou un week-end à la date cible ne doit pas rendre une performance NULL :
    la référence est la dernière séance à ou avant la cible (`<=` puis `DESC LIMIT 1`).
    La YTD est l'exception voulue : première séance de l'année, donc `>=` et `ASC`."""
    a_ou_avant = re.findall(
        r"date_seance <= t\.cible_(1j|1s|1m|1a)\s+ORDER BY c\.date_seance DESC\s+LIMIT 1", INDICATEURS)
    assert sorted(a_ou_avant) == ["1a", "1j", "1m", "1s"], a_ou_avant
    assert re.search(r"date_seance >= t\.cible_ytd\s+ORDER BY c\.date_seance ASC\s+LIMIT 1", INDICATEURS)
    assert not re.search(r"date_seance = t\.cible_", INDICATEURS), \
        "une égalité stricte sur la date cible rendrait NULL chaque jour sans séance"


# --- R09 : titre ou résumé modifié → version actuelle servie, sans résidu ---------------------

def test_R09_un_article_modifie_est_servi_dans_sa_version_actuelle_sans_residu(monkeypatch, tmp_path):
    """Même identifiant, texte corrigé entre deux indexations : la recherche rend la version
    actuelle, une seule fois, et le titre suit."""
    _index_jetable(monkeypatch, tmp_path, [("LVMH publie des resultats semestriels en hausse", "")])
    _index_jetable(monkeypatch, tmp_path, [("LVMH publie des resultats semestriels en baisse", "")])

    r = recherche.rechercher("resultats semestriels de LVMH", chemin=tmp_path, k=3)
    assert r.trouve and len(r.passages) == 1
    assert "baisse" in r.passages[0].texte and "hausse" not in r.passages[0].texte
    assert r.passages[0].titre.endswith("en baisse")


# --- R13 : résumé à partir de plusieurs passages → chaque affirmation soutenue, contradictions dites

def test_R13_le_prompt_exige_des_affirmations_soutenues_et_des_contradictions_dites():
    """Avec deux passages qui se contredisent, la consigne doit interdire de trancher en silence."""
    passages = [
        {"texte": "LVMH releve ses objectifs annuels", "titre": "LVMH releve ses objectifs",
         "source": "A", "lien": "https://exemple.test/a", "publie_le": "2026-09-01", "tickers": ["MC.PA"],
         "rang_dense": 0, "rang_lexical": 0, "distance_dense": 0.3, "score_lexical": 5.0, "article_id": 1},
        {"texte": "LVMH abaisse ses objectifs annuels", "titre": "LVMH abaisse ses objectifs",
         "source": "B", "lien": "https://exemple.test/b", "publie_le": "2026-09-02", "tickers": ["MC.PA"],
         "rang_dense": 1, "rang_lexical": 1, "distance_dense": 0.31, "score_lexical": 4.0, "article_id": 2},
    ]
    with patch("agents.analyst.generer_texte_detaille", return_value=faux_resultat_texte("x")) as mock_llm:
        generate_briefing(ticker="MC.PA", price=600.0, change_pct=0.4, adtv20=None, currency="EUR",
                          passages=passages)
    prompt = prompt_produit(mock_llm)
    assert "soutenue par l'un des articles" in prompt
    assert "se contredisent" in prompt and "dis-le" in prompt
