"""Sprint 5, étape 2 : les signaux de la vigie et `GET /sante` (plan du sprint 5, § 3, étape 2).

Une seule source pour le tableau de bord et la vigie : ils disent donc la même chose. Les taux portent sur les
résultats des 15 dernières minutes ; les rejets (403, 422, 429) se comptent à part. Aucune requête veut dire
« inconnu » (`None`), jamais 0. La fraîcheur se lit PAR VALEUR : `db/fraicheur.sql` prend la dernière séance de
toutes les cotations, et cache ainsi une valeur qui ne reçoit plus de cours tant qu'une autre est à jour.
"""
from datetime import date

import pytest
from fastapi.testclient import TestClient

from api import limiteur
from api.main import app
from monitorage import compteurs, signaux
from monitorage.compteurs import Compteurs
from tests.conftest import CLE_DE_TEST

CLE = {"X-API-Key": CLE_DE_TEST}
MAINTENANT = 1_000_000.0
AUJOURDHUI = date(2026, 10, 22)          # un jeudi


class _Horloge:
    def __init__(self, t=MAINTENANT):
        self.t = t

    def __call__(self):
        return self.t


def _mesures(*appels, horloge=None):
    """Des compteurs remplis : chaque appel est (secondes avant maintenant, code, statut, motif, durée)."""
    horloge = horloge or _Horloge()
    mesures = Compteurs(horloge=horloge)
    for avant, code, statut, motif, duree in appels:
        horloge.t = MAINTENANT - avant
        mesures.noter("/question", code, statut, motif, duree, (100, 10))
    horloge.t = MAINTENANT
    return mesures


REPONSE = (60, 200, "reponse", "OK", 1000)
ERREUR = (60, 503, "erreur", "FOURNISSEUR_INDISPONIBLE", 1000)
DETOURNEMENT = (60, 200, "refus", "TENTATIVE_DETOURNEMENT", 50)
REJET = (60, 403, None, "HTTP_403", 1)


# --- les taux, sur 15 minutes -----------------------------------------------------------------------------------------

def test_vingt_resultats_dont_deux_erreurs_donnent_dix_pour_cent():
    etat = signaux.etat_sante(_mesures(*[REPONSE] * 18, *[ERREUR] * 2), [], MAINTENANT, AUJOURDHUI)
    assert etat["erreurs_techniques"] == {"valeur": 0.1, "numerateur": 2, "effectif": 20}


def test_aucune_requete_donne_inconnu_jamais_zero():
    etat = signaux.etat_sante(_mesures(), [], MAINTENANT, AUJOURDHUI)
    assert etat["erreurs_techniques"] == {"valeur": None, "numerateur": 0, "effectif": 0}
    assert etat["latence_p95_ms"] == {"valeur": None, "effectif": 0}


def test_une_observation_de_seize_minutes_sort_des_taux_mais_reste_dans_les_jetons():
    ancienne = (16 * 60, 503, "erreur", "FOURNISSEUR_INDISPONIBLE", 1000)
    etat = signaux.etat_sante(_mesures(ancienne, REPONSE), [], MAINTENANT, AUJOURDHUI)
    assert etat["erreurs_techniques"] == {"valeur": 0.0, "numerateur": 0, "effectif": 1}
    assert (etat["jetons_24h"]["entree"], etat["jetons_24h"]["sortie"]) == (200, 20)


def test_les_rejets_se_comptent_a_part_hors_du_denominateur():
    etat = signaux.etat_sante(_mesures(DETOURNEMENT, REPONSE, REJET, REJET), [], MAINTENANT, AUJOURDHUI)
    assert etat["refus_securite"] == {"valeur": 0.5, "numerateur": 1, "effectif": 2}
    assert etat["rejets_15_min"] == 2


def test_la_derive_simulee_franchit_le_taux_de_refus_de_securite():
    # Le scénario de l'étape 7 : deux questions, puis H1 à H6 deux fois.
    etat = signaux.etat_sante(_mesures(REPONSE, REPONSE, *[DETOURNEMENT] * 12), [], MAINTENANT, AUJOURDHUI)
    assert etat["refus_securite"]["numerateur"] == 12 and etat["refus_securite"]["effectif"] == 14


def test_l_etat_dit_depuis_quand_il_mesure():
    etat = signaux.etat_sante(_mesures(), [], MAINTENANT, AUJOURDHUI)
    assert etat["fenetre_min"] == 15
    assert etat["mesures_depuis"] == etat["jetons_24h"]["depuis"]
    assert etat["mesures_depuis"].startswith("1970-01-12")


# --- la latence p95, en calcul entier ----------------------------------------------------------------------------------

@pytest.mark.parametrize("durees, attendu", [
    ([], None),
    ([700], 700),
    ([100] * 19 + [5000], 100),
    ([100] * 18 + [3000, 5000], 3000),
])
def test_p95_en_calcul_entier(durees, attendu):
    assert signaux.p95_ms(durees) == attendu


def test_la_latence_ne_compte_pas_les_rejets():
    etat = signaux.etat_sante(_mesures(REPONSE, REJET), [], MAINTENANT, AUJOURDHUI)
    assert etat["latence_p95_ms"] == {"valeur": 1000, "effectif": 1}


# --- la fraîcheur, par valeur --------------------------------------------------------------------------------------------

def test_une_valeur_sans_cours_depuis_six_jours_ouvres_est_rouge_meme_si_les_autres_sont_a_jour():
    lignes = [{"ticker": "MC.PA", "derniere_seance": date(2026, 10, 21)},
              {"ticker": "OR.PA", "derniere_seance": date(2026, 10, 14)}]
    fraicheur = signaux.fraicheur_par_valeur(lignes, AUJOURDHUI)
    assert fraicheur["pire"] == "rouge"
    assert fraicheur["nb_valeurs"] == 2
    assert fraicheur["en_retard"] == [{"ticker": "OR.PA", "derniere_seance": "2026-10-14",
                                       "retard_jours_ouvres": 6, "statut": "rouge"}]


def test_une_valeur_sans_aucune_cotation_est_rouge():
    fraicheur = signaux.fraicheur_par_valeur([{"ticker": "AIR.PA", "derniere_seance": None}], AUJOURDHUI)
    assert fraicheur["pire"] == "rouge"
    assert fraicheur["en_retard"][0]["retard_jours_ouvres"] is None


def test_toutes_les_valeurs_a_jour_donnent_vert():
    fraicheur = signaux.fraicheur_par_valeur([{"ticker": "MC.PA", "derniere_seance": date(2026, 10, 21)}],
                                             AUJOURDHUI)
    assert (fraicheur["pire"], fraicheur["en_retard"]) == ("vert", [])


@pytest.mark.parametrize("lignes", [None, []])
def test_une_base_injoignable_ou_vide_donne_inconnu(lignes):
    assert signaux.fraicheur_par_valeur(lignes, AUJOURDHUI)["pire"] == "inconnu"


def test_la_lecture_rend_none_quand_la_base_ne_repond_pas(monkeypatch):
    def en_panne(*args, **kwargs):
        raise ConnectionError("base injoignable")

    monkeypatch.setattr(signaux.database, "_executer", en_panne)
    assert signaux.lire_fraicheur_par_valeur() is None


def test_la_lecture_rend_les_lignes_de_la_requete(monkeypatch):
    class _Extraction:
        lignes = [{"ticker": "MC.PA", "derniere_seance": date(2026, 10, 21), "aujourdhui": AUJOURDHUI}]

    requetes = []
    monkeypatch.setattr(signaux.database, "_executer",
                        lambda sql, nom, dsn=None, **p: requetes.append(sql) or _Extraction())
    assert signaux.lire_fraicheur_par_valeur() == _Extraction.lignes
    assert "statut_qualite = 'OK'" in requetes[0] and "GROUP BY v.ticker" in requetes[0]


# --- la route GET /sante -------------------------------------------------------------------------------------------------

@pytest.fixture
def sante_sans_base(monkeypatch):
    mesures = _mesures(REPONSE, ERREUR, horloge=_Horloge())
    monkeypatch.setattr(compteurs, "COMPTEURS", mesures)
    monkeypatch.setattr(signaux, "lire_fraicheur_par_valeur",
                        lambda dsn=None: [{"ticker": "OR.PA", "derniere_seance": date(2026, 10, 14),
                                           "aujourdhui": AUJOURDHUI}])
    return mesures


def test_sante_sans_cle_est_refusee(sante_sans_base):
    assert TestClient(app).get("/sante").status_code == 403


def test_sante_avec_la_cle_rend_les_signaux(sante_sans_base):
    reponse = TestClient(app).get("/sante", headers=CLE)
    assert reponse.status_code == 200
    corps = reponse.json()
    assert {"mesures_depuis", "fenetre_min", "erreurs_techniques", "refus_securite", "refus_corpus", "refus_qualite",
            "latence_p95_ms", "rejets_15_min", "jetons_24h", "fraicheur"} <= set(corps)
    assert corps["fraicheur"]["pire"] == "rouge"


def test_sante_repond_meme_quand_la_base_ne_repond_pas(monkeypatch):
    monkeypatch.setattr(compteurs, "COMPTEURS", Compteurs())
    monkeypatch.setattr(signaux, "lire_fraicheur_par_valeur", lambda dsn=None: None)
    reponse = TestClient(app).get("/sante", headers=CLE)
    assert reponse.status_code == 200
    assert reponse.json()["fraicheur"]["pire"] == "inconnu"


def test_sante_ne_consomme_pas_le_quota(sante_sans_base, monkeypatch):
    monkeypatch.setattr(limiteur, "LIMITEUR", limiteur.Limiteur(1))
    assert [TestClient(app).get("/sante", headers=CLE).status_code for _ in range(3)] == [200, 200, 200]
