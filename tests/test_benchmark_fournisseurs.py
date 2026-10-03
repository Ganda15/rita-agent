"""Le banc C7 (plan `docs/PLAN-C7-benchmark.md`) : ce qui doit être vrai avant la première mesure payante.

Aucun test ici n'appelle un fournisseur : les appels sont injectés. Ce qui est figé : l'intervalle de Wilson,
le jeu d'essai relu tel quel, un fournisseur injoignable compté comme indisponible et jamais comme un zéro de
qualité, le plafond de dépense qui arrête, la fidélité aux faits fournis, et le résumé par fournisseur.
"""
import json

import pytest

from evals import benchmark_fournisseurs as banc


# --- l'intervalle de Wilson ------------------------------------------------------------------

def test_wilson_sur_30_essais_est_large_et_le_dit():
    bas, haut = banc.wilson(29, 30)
    assert 0.82 < bas < 0.84 and 0.99 < haut <= 1.0


def test_wilson_sans_essai_ne_rend_pas_un_chiffre():
    assert banc.wilson(0, 0) is None


def test_wilson_est_borne_entre_zero_et_un():
    bas, haut = banc.wilson(30, 30)
    assert 0.0 <= bas <= haut <= 1.0


# --- le jeu d'essai ------------------------------------------------------------------------------

CAS = {"ticker": "MC.PA", "price": 378.55, "change_pct": -0.25, "adtv20": 1234.0, "currency": "EUR",
       "fraicheur_jours": 1, "cotation_perimee": False, "passages": []}


def test_le_jeu_est_relu_tel_quel_et_valide(tmp_path):
    chemin = tmp_path / "jeu.json"
    chemin.write_text(json.dumps({"fige_le": "2026-10-03", "cas": [CAS]}), encoding="utf-8")
    jeu = banc.charger_jeu(chemin)
    assert jeu["cas"][0]["ticker"] == "MC.PA"


def test_un_cas_sans_cours_est_refuse(tmp_path):
    chemin = tmp_path / "jeu.json"
    mauvais = {k: v for k, v in CAS.items() if k != "price"}
    chemin.write_text(json.dumps({"fige_le": "2026-10-03", "cas": [mauvais]}), encoding="utf-8")
    with pytest.raises(ValueError):
        banc.charger_jeu(chemin)


def test_le_prompt_du_banc_est_celui_du_redacteur():
    """Le banc ne fabrique pas son propre prompt : il appelle la fonction du rédacteur."""
    from agents.analyst import construire_prompt
    assert banc.prompt_du_cas(CAS) == construire_prompt(**CAS)


# --- la fidélité aux faits fournis ----------------------------------------------------------------

def test_un_texte_qui_reprend_le_cours_et_le_sens_est_fidele():
    assert banc.fidele("LVMH clôture à 378,55 EUR, en légère baisse de 0,25 %.", CAS) is True


def test_un_texte_sans_le_cours_n_est_pas_fidele():
    assert banc.fidele("LVMH termine en baisse, séance calme.", CAS) is False


def test_un_texte_qui_inverse_le_sens_n_est_pas_fidele():
    assert banc.fidele("LVMH clôture à 378,55 EUR, en hausse.", CAS) is False


# --- l'exécution : indisponibilité, plafond, journal brut ------------------------------------------

class _Reponse:
    def __init__(self, texte, usage=None, modele="m"):
        self.texte, self.usage, self.modele = texte, usage or {"input": 600, "output": 200}, modele


def test_un_fournisseur_injoignable_est_indisponible_et_n_est_pas_appele_sur_les_cas():
    appels = []

    def appel(nom, prompt, max_tokens):
        appels.append(nom)
        if nom == "foundry":
            raise KeyError("AZURE_FOUNDRY_API_KEY")
        return _Reponse("LVMH clôture à 378,55 EUR, en baisse.")

    lignes, etat = banc.executer({"cas": [CAS, CAS]}, ["foundry", "openrouter"], repetitions=1,
                                 plafond_usd=5.0, prix={"openrouter": (3.0, 15.0)}, appel=appel)
    assert etat["foundry"]["statut"] == "indisponible" and "AZURE_FOUNDRY_API_KEY" in etat["foundry"]["motif"]
    assert appels.count("foundry") == 1, "une sonde, puis on n'insiste pas"
    assert all(l["fournisseur"] == "openrouter" for l in lignes) and len(lignes) == 2


def test_le_plafond_de_depense_arrete_le_banc():
    def appel(nom, prompt, max_tokens):
        return _Reponse("texte", usage={"input": 1_000_000, "output": 0})   # 3 USD l'appel au prix de test

    lignes, etat = banc.executer({"cas": [CAS] * 10}, ["openrouter"], repetitions=1,
                                 plafond_usd=5.0, prix={"openrouter": (3.0, 15.0)}, appel=appel)
    assert len(lignes) == 2, "le second appel franchit 5 dollars, le troisième ne part pas"
    assert etat["openrouter"]["statut"] == "plafond atteint"


def test_chaque_ligne_brute_porte_ce_que_le_plan_exige():
    def appel(nom, prompt, max_tokens):
        return _Reponse("LVMH clôture à 378,55 EUR, en baisse.", modele="anthropic/claude-sonnet-4.5")

    lignes, _ = banc.executer({"cas": [CAS]}, ["openrouter"], repetitions=1, plafond_usd=5.0,
                              prix={"openrouter": (3.0, 15.0)}, appel=appel)
    l = lignes[0]
    for champ in ("fournisseur", "modele", "ticker", "repetition", "horodatage", "duree_s",
                  "jetons_entree", "jetons_sortie", "cout_usd", "texte", "erreur", "conforme_amf", "fidele"):
        assert champ in l, champ
    assert l["modele"] == "anthropic/claude-sonnet-4.5" and l["erreur"] is None


def test_une_erreur_en_cours_de_banc_est_une_ligne_en_echec_pas_un_arret():
    compteur = {"n": 0}

    def appel(nom, prompt, max_tokens):
        compteur["n"] += 1
        if compteur["n"] == 3:          # 1 = la sonde, 2 = premier cas, 3 = deuxième cas
            raise TimeoutError("60 s")
        return _Reponse("LVMH clôture à 378,55 EUR, en baisse.")

    lignes, etat = banc.executer({"cas": [CAS] * 3}, ["openrouter"], repetitions=1, plafond_usd=5.0,
                                 prix={"openrouter": (3.0, 15.0)}, appel=appel)
    assert len(lignes) == 3 and lignes[1]["erreur"].startswith("TimeoutError")
    assert etat["openrouter"]["statut"] == "mesure"


# --- le résumé par fournisseur ---------------------------------------------------------------------

def test_le_resume_separe_conformite_fidelite_latence_et_cout():
    lignes = [
        {"fournisseur": "openrouter", "erreur": None, "conforme_amf": True, "fidele": True, "duree_s": 1.0,
         "jetons_entree": 600, "jetons_sortie": 200, "cout_usd": 0.001},
        {"fournisseur": "openrouter", "erreur": None, "conforme_amf": False, "fidele": True, "duree_s": 3.0,
         "jetons_entree": 600, "jetons_sortie": 200, "cout_usd": 0.001},
        {"fournisseur": "openrouter", "erreur": "TimeoutError: 60 s", "conforme_amf": None, "fidele": None,
         "duree_s": 60.0, "jetons_entree": 0, "jetons_sortie": 0, "cout_usd": 0.0},
    ]
    r = banc.resumer(lignes)["openrouter"]
    assert r["appels"] == 3 and r["reussis"] == 2
    assert r["conformes_amf"] == 1 and r["intervalle_conformes"] is not None
    assert r["fideles"] == 2
    assert r["latence_p50_s"] == 2.0 and r["latence_p95_s"] == 3.0   # p50 = médiane ; p95 = rang le plus proche
    assert abs(r["cout_total_usd"] - 0.002) < 1e-9


def test_un_fournisseur_sans_appel_reussi_n_a_pas_de_taux():
    lignes = [{"fournisseur": "anthropic", "erreur": "AuthenticationError", "conforme_amf": None, "fidele": None,
               "duree_s": 0.2, "jetons_entree": 0, "jetons_sortie": 0, "cout_usd": 0.0}]
    r = banc.resumer(lignes)["anthropic"]
    assert r["reussis"] == 0 and r["intervalle_conformes"] is None


def test_le_prompt_du_banc_porte_les_indicateurs_quand_le_jeu_les_a():
    from agents.analyst import construire_prompt
    cas = {**CAS, "indicateurs": {"rsi_14": 38.4, "ma20": 404.9}}
    assert banc.prompt_du_cas(cas) == construire_prompt(**CAS, indicateurs=cas["indicateurs"])
    assert "RSI 14 : 38.4" in banc.prompt_du_cas(cas)


def test_un_jeu_fige_sans_indicateurs_reste_lisible(tmp_path):
    chemin = tmp_path / "jeu.json"
    chemin.write_text(json.dumps({"fige_le": "2026-10-03", "cas": [CAS]}), encoding="utf-8")
    assert banc.charger_jeu(chemin)["cas"][0]["ticker"] == "MC.PA"


# --- L'origine de chaque appel est journalisée (03/10/2026, soir) ------------------------------------

class _ReponseAvecOrigine(_Reponse):
    def __init__(self, texte, origine=None, **k):
        super().__init__(texte, **k)
        self.origine = origine


def test_chaque_ligne_brute_porte_l_origine_de_l_appel():
    def appel(nom, prompt, max_tokens):
        return _ReponseAvecOrigine("LVMH clôture à 378,55 EUR, en baisse.", origine="Sweden Central")

    lignes, _ = banc.executer({"cas": [CAS]}, ["foundry"], repetitions=1, plafond_usd=5.0, prix={}, appel=appel)
    assert lignes[0]["origine"] == "Sweden Central"


def test_une_reponse_sans_origine_donne_une_ligne_a_l_origine_inconnue():
    def appel(nom, prompt, max_tokens):
        return _Reponse("LVMH clôture à 378,55 EUR, en baisse.")   # ni attribut, ni valeur

    lignes, _ = banc.executer({"cas": [CAS]}, ["foundry"], repetitions=1, plafond_usd=5.0, prix={}, appel=appel)
    assert "origine" in lignes[0] and lignes[0]["origine"] is None


def test_le_resume_compte_les_origines_par_fournisseur():
    origines = iter([None, "Sweden Central", "Sweden Central", "France Central"])   # la sonde, puis 3 cas

    def appel(nom, prompt, max_tokens):
        return _ReponseAvecOrigine("LVMH clôture à 378,55 EUR, en baisse.", origine=next(origines))

    lignes, _ = banc.executer({"cas": [CAS] * 3}, ["foundry"], repetitions=1, plafond_usd=5.0, prix={}, appel=appel)
    assert banc.resumer(lignes)["foundry"]["origines"] == {"Sweden Central": 2, "France Central": 1}
