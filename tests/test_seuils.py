"""Sprint 5, étape 3 : les seuils argumentés et le prix daté (plan du sprint 5, § 2 « Seuils » et « Coût »).

Chaque seuil a sa valeur, son pourquoi, son action et sa résolution : un seuil sans pourquoi ou sans action est refusé
au chargement. Le coût est estimé à partir des jetons et d'un prix public daté et sourcé. Les verdicts (sain,
attention, problème, inconnu) se calculent dans `/sante` : le tableau de bord et la vigie lisent le même.
"""
import json

import pytest
from fastapi.testclient import TestClient

from api.main import app
from monitorage import compteurs, fraicheur, seuils, signaux
from monitorage.compteurs import Compteurs
from tests.conftest import CLE_DE_TEST

CLE = {"X-API-Key": CLE_DE_TEST}
SIGNAUX = {"service", "erreurs_techniques", "refus_securite", "latence_p95_ms", "cout_24h_usd", "fraicheur",
           "rejets_15_min"}


def _taux(numerateur, effectif):
    return {"valeur": round(numerateur / effectif, 4) if effectif else None, "numerateur": numerateur,
            "effectif": effectif}


def _etat(**surcharges):
    """Un état de `/sante` où tout va bien ; chaque test change ce qu'il vérifie."""
    etat = {"erreurs_techniques": _taux(0, 20), "refus_securite": _taux(0, 20),
            "latence_p95_ms": {"valeur": 3000, "effectif": 20}, "rejets_15_min": 0,
            "cout_24h": {"valeur": 0.2, "devise": "USD"},
            "fraicheur": {"pire": "vert", "nb_valeurs": 3, "en_retard": [], "message": ""}}
    etat.update(surcharges)
    return etat


def _verdict(etat, signal):
    return seuils.evaluer(etat, seuils.charger())[signal]


# --- le fichier des seuils ----------------------------------------------------------------------------------------------

def test_le_fichier_des_seuils_se_charge_et_couvre_chaque_signal():
    assert set(seuils.charger()["signaux"]) == SIGNAUX


@pytest.mark.parametrize("champ", ["pourquoi", "action", "resolution"])
def test_un_seuil_sans_pourquoi_action_ou_resolution_est_refuse(tmp_path, champ):
    donnees = json.loads(seuils.CHEMIN_SEUILS.read_text(encoding="utf-8"))
    del donnees["signaux"]["refus_securite"][champ]
    chemin = tmp_path / "seuils.json"
    chemin.write_text(json.dumps(donnees), encoding="utf-8")
    with pytest.raises(ValueError, match=f"refus_securite.*{champ}"):
        seuils.charger(chemin)


def test_un_orange_au_dessus_du_rouge_est_refuse(tmp_path):
    donnees = json.loads(seuils.CHEMIN_SEUILS.read_text(encoding="utf-8"))
    donnees["signaux"]["erreurs_techniques"]["orange"] = 0.5
    chemin = tmp_path / "seuils.json"
    chemin.write_text(json.dumps(donnees), encoding="utf-8")
    with pytest.raises(ValueError, match="erreurs_techniques"):
        seuils.charger(chemin)


def test_une_action_qui_ne_renvoie_pas_a_la_doc_d_exploitation_est_refusee(tmp_path):
    donnees = json.loads(seuils.CHEMIN_SEUILS.read_text(encoding="utf-8"))
    donnees["signaux"]["fraicheur"]["action"] = "voir avec Era"
    chemin = tmp_path / "seuils.json"
    chemin.write_text(json.dumps(donnees), encoding="utf-8")
    with pytest.raises(ValueError, match="fraicheur.*action"):
        seuils.charger(chemin)


def _ecrire(tmp_path, donnees, nom="seuils.json"):
    chemin = tmp_path / nom
    chemin.write_text(json.dumps(donnees), encoding="utf-8")
    return chemin


def test_un_signal_manquant_est_refuse(tmp_path):
    donnees = json.loads(seuils.CHEMIN_SEUILS.read_text(encoding="utf-8"))
    del donnees["signaux"]["cout_24h_usd"]
    with pytest.raises(ValueError, match="couvrir exactement"):
        seuils.charger(_ecrire(tmp_path, donnees))


def test_une_sonde_sans_essai_est_refusee(tmp_path):
    donnees = json.loads(seuils.CHEMIN_SEUILS.read_text(encoding="utf-8"))
    donnees["signaux"]["service"]["essais"] = 0
    with pytest.raises(ValueError, match="service"):
        seuils.charger(_ecrire(tmp_path, donnees))


def test_un_taux_sans_minimum_de_requetes_est_refuse(tmp_path):
    donnees = json.loads(seuils.CHEMIN_SEUILS.read_text(encoding="utf-8"))
    del donnees["signaux"]["refus_securite"]["minimum_requetes"]
    with pytest.raises(ValueError, match="refus_securite.*minimum_requetes"):
        seuils.charger(_ecrire(tmp_path, donnees))


@pytest.mark.parametrize("champ, valeur", [("entree_par_million", 0), ("sortie_par_million", "cher"),
                                           ("source", "http://non-chiffre.test"), ("en_vigueur_depuis", "")])
def test_un_prix_incomplet_ou_non_source_est_refuse(tmp_path, champ, valeur):
    prix = json.loads(seuils.CHEMIN_PRIX.read_text(encoding="utf-8"))
    prix[champ] = valeur
    with pytest.raises(ValueError, match="prix"):
        seuils.charger_prix(_ecrire(tmp_path, prix, "prix.json"))


def test_les_seuils_de_fraicheur_suivent_les_regles_de_monitorage_fraicheur():
    # Une seule source de vérité pour la couleur : le fichier décrit, monitorage/fraicheur.py décide.
    signal = seuils.charger()["signaux"]["fraicheur"]
    assert signal["orange"] == fraicheur.SEUIL_VERT_JOURS_OUVRES + 1
    assert signal["rouge"] == fraicheur.SEUIL_ORANGE_JOURS_OUVRES + 1


# --- le prix et le coût -------------------------------------------------------------------------------------------------

def test_le_prix_est_date_source_et_au_bon_montant():
    prix = seuils.charger_prix()
    assert (prix["entree_par_million"], prix["sortie_par_million"], prix["devise"]) == (2.75, 16.5, "USD")
    assert prix["en_vigueur_depuis"] == "2026-03-01"
    assert prix["source"].startswith("https://prices.azure.com/")


def test_un_million_de_jetons_d_entree_et_cent_mille_de_sortie_coutent_4_40_usd():
    jetons = {"entree": 1_000_000, "sortie": 100_000}
    assert seuils.cout_24h(jetons, seuils.charger_prix()) == pytest.approx(4.40)


# --- les verdicts ---------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("numerateur, effectif, attendu", [
    (12, 14, "probleme"),
    (2, 14, "sain"),
    (12, 12, "probleme"),
    (3, 5, "inconnu"),        # sous le minimum de 10 requêtes
])
def test_le_verdict_des_refus_de_securite(numerateur, effectif, attendu):
    assert _verdict(_etat(refus_securite=_taux(numerateur, effectif)), "refus_securite")["etat"] == attendu


@pytest.mark.parametrize("numerateur, effectif, attendu", [(1, 6, "attention"), (5, 6, "probleme"), (0, 6, "sain")])
def test_le_verdict_des_erreurs_techniques(numerateur, effectif, attendu):
    assert _verdict(_etat(erreurs_techniques=_taux(numerateur, effectif)), "erreurs_techniques")["etat"] == attendu


def test_un_verdict_garde_sa_valeur_son_effectif_et_son_action():
    verdict = _verdict(_etat(refus_securite=_taux(12, 14)), "refus_securite")
    assert (verdict["numerateur"], verdict["effectif"], verdict["rouge"]) == (12, 14, 0.30)
    assert verdict["action"].startswith("docs/exploitation.md#") and verdict["pourquoi"]


@pytest.mark.parametrize("valeur, attendu", [(3000, "sain"), (12_000, "attention"), (25_000, "probleme"),
                                             (None, "inconnu")])
def test_le_verdict_de_la_latence(valeur, attendu):
    effectif = 0 if valeur is None else 20
    assert _verdict(_etat(latence_p95_ms={"valeur": valeur, "effectif": effectif}), "latence_p95_ms")["etat"] == attendu


@pytest.mark.parametrize("valeur, attendu", [(0.2, "sain"), (1.5, "attention"), (6.0, "probleme"), (None, "inconnu")])
def test_le_verdict_du_cout(valeur, attendu):
    assert _verdict(_etat(cout_24h={"valeur": valeur, "devise": "USD"}), "cout_24h_usd")["etat"] == attendu


@pytest.mark.parametrize("pire, attendu", [("vert", "sain"), ("orange", "attention"), ("rouge", "probleme"),
                                           ("inconnu", "inconnu")])
def test_le_verdict_de_la_fraicheur(pire, attendu):
    etat = _etat(fraicheur={"pire": pire, "nb_valeurs": 3, "en_retard": [], "message": ""})
    assert _verdict(etat, "fraicheur")["etat"] == attendu


@pytest.mark.parametrize("nombre, attendu", [(3, "sain"), (25, "attention"), (150, "probleme")])
def test_le_verdict_des_rejets(nombre, attendu):
    assert _verdict(_etat(rejets_15_min=nombre), "rejets_15_min")["etat"] == attendu


def test_le_service_n_est_pas_juge_par_l_api_elle_meme():
    # Une API arrêtée ne peut pas annoncer sa propre panne : la sonde du service est faite par la vigie (étape 4).
    assert "service" not in seuils.evaluer(_etat(), seuils.charger())


# --- /sante rend le coût et les verdicts ----------------------------------------------------------------------------------

def test_sante_rend_le_cout_date_et_les_verdicts(monkeypatch):
    mesures = Compteurs()
    mesures.noter("/question", 200, "reponse", "OK", 900, (2000, 300))
    monkeypatch.setattr(compteurs, "COMPTEURS", mesures)
    monkeypatch.setattr(signaux, "lire_fraicheur_par_valeur", lambda dsn=None: None)
    corps = TestClient(app).get("/sante", headers=CLE).json()
    assert corps["cout_24h"]["valeur"] == pytest.approx(2000 * 2.75e-6 + 300 * 16.5e-6)
    assert (corps["cout_24h"]["devise"], corps["cout_24h"]["prix_du"]) == ("USD", "2026-03-01")
    assert corps["verdicts"]["fraicheur"]["etat"] == "inconnu"
    assert corps["verdicts"]["refus_securite"]["etat"] == "inconnu"       # 1 requête, sous le minimum
    assert set(corps["verdicts"]) == SIGNAUX - {"service"}


# --- étape 4 : la résolution d'une alerte, pour la vigie -----------------------------------------------------------------

@pytest.mark.parametrize("signal, surcharge, attendu", [
    ("refus_securite", {"refus_securite": _taux(0, 3)}, True),          # plus aucun refus dans la fenêtre
    ("refus_securite", {"refus_securite": _taux(2, 20)}, True),         # 10 % avec au moins 10 requêtes
    ("refus_securite", {"refus_securite": _taux(3, 5)}, False),         # des refus, sous le minimum : on attend
    ("erreurs_techniques", {"erreurs_techniques": _taux(5, 6)}, False),  # 83 % : les erreurs sont encore là
    ("latence_p95_ms", {"latence_p95_ms": {"valeur": None, "effectif": 0}}, True),
    ("latence_p95_ms", {"latence_p95_ms": {"valeur": 25_000, "effectif": 20}}, False),
    ("cout_24h_usd", {"cout_24h": {"valeur": 2.0, "devise": "USD"}}, True),
    ("cout_24h_usd", {"cout_24h": {"valeur": None, "devise": "USD"}}, False),
    ("rejets_15_min", {"rejets_15_min": 40}, True),
    ("fraicheur", {"fraicheur": {"pire": "orange", "nb_valeurs": 3, "en_retard": [], "message": ""}}, True),
    ("fraicheur", {"fraicheur": {"pire": "rouge", "nb_valeurs": 3, "en_retard": [], "message": ""}}, False),
])
def test_la_resolution_suit_la_regle_ecrite_du_seuil(signal, surcharge, attendu):
    assert seuils.est_resolu(signal, _verdict(_etat(**surcharge), signal)) is attendu
