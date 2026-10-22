"""Les seuils argumentés et le prix daté de la vigie (sprint 5, étape 3).

Plan du sprint 5, § 2 « Seuils » et « Coût ». La grille de l'atelier 5 demande, pour chaque signal, « signal, seuil,
alerte, action » : `monitorage/seuils.json` porte la valeur, le pourquoi, l'action (un lien vers la doc
d'exploitation) et la résolution de chaque seuil. Un seuil incomplet est refusé au chargement : un test le prouve.

Le coût est estimé : jetons × prix public daté et sourcé (`monitorage/prix.json`, relevé dans l'API publique des prix
Azure). Les verdicts se calculent ici et sont rendus par `/sante` : le tableau de bord et la vigie lisent les mêmes.

Règle : « attention » à partir de `orange`, « problème » à partir de `rouge`. Sous le minimum de requêtes, ou sans
donnée, le verdict est « inconnu », jamais « sain ». Le signal `service` n'est pas jugé ici : une API arrêtée ne peut
pas annoncer sa propre panne, c'est la vigie qui la sonde (étape 4).
"""
from __future__ import annotations

import json
from pathlib import Path

ICI = Path(__file__).parent
CHEMIN_SEUILS = ICI / "seuils.json"
CHEMIN_PRIX = ICI / "prix.json"
SIGNAUX = ("service", "erreurs_techniques", "refus_securite", "latence_p95_ms", "cout_24h_usd", "fraicheur",
           "rejets_15_min")
SIGNAUX_EN_TAUX = ("erreurs_techniques", "refus_securite")
PREFIXE_ACTION = "docs/exploitation.md#"
_ETAT_FRAICHEUR = {"vert": "sain", "orange": "attention", "rouge": "probleme", "inconnu": "inconnu"}


def _verifier_signal(nom: str, signal: dict) -> None:
    for champ in ("libelle", "pourquoi", "action", "resolution"):
        if not isinstance(signal.get(champ), str) or not signal[champ].strip():
            raise ValueError(f"seuil « {nom} » : le champ « {champ} » manque ou est vide")
    if not signal["action"].startswith(PREFIXE_ACTION):
        raise ValueError(f"seuil « {nom} » : l'action doit renvoyer à la doc d'exploitation ({PREFIXE_ACTION}...)")
    if nom == "service":
        if not (isinstance(signal.get("essais"), int) and signal["essais"] >= 1 and signal.get("intervalle_s", 0) > 0):
            raise ValueError("seuil « service » : « essais » (au moins 1) et « intervalle_s » (positif) sont exigés")
        return
    orange, rouge = signal.get("orange"), signal.get("rouge")
    if not all(isinstance(v, (int, float)) for v in (orange, rouge)) or orange > rouge:
        raise ValueError(f"seuil « {nom} » : « orange » et « rouge » sont des nombres, et orange ≤ rouge")
    if nom in SIGNAUX_EN_TAUX + ("latence_p95_ms",):
        if not (isinstance(signal.get("minimum_requetes"), int) and signal["minimum_requetes"] >= 1):
            raise ValueError(f"seuil « {nom} » : « minimum_requetes » (au moins 1) est exigé")


def charger(chemin: Path = CHEMIN_SEUILS) -> dict:
    """Lit les seuils et refuse au premier défaut : un seuil sans pourquoi ou sans action n'est pas un seuil."""
    donnees = json.loads(Path(chemin).read_text(encoding="utf-8"))
    signaux = donnees.get("signaux", {})
    if set(signaux) != set(SIGNAUX):
        raise ValueError(f"les seuils doivent couvrir exactement {sorted(SIGNAUX)}, pas {sorted(signaux)}")
    for nom, signal in signaux.items():
        _verifier_signal(nom, signal)
    return donnees


def charger_prix(chemin: Path = CHEMIN_PRIX) -> dict:
    prix = json.loads(Path(chemin).read_text(encoding="utf-8"))
    for champ in ("entree_par_million", "sortie_par_million"):
        if not (isinstance(prix.get(champ), (int, float)) and prix[champ] > 0):
            raise ValueError(f"prix : « {champ} » doit être un nombre positif")
    if not (prix.get("devise") and prix.get("en_vigueur_depuis") and str(prix.get("source", "")).startswith("https://")):
        raise ValueError("prix : la devise, la date d'effet et une source https sont exigées")
    return prix


def cout_24h(jetons: dict, prix: dict) -> float:
    """Le coût estimé, dans la devise du prix : jetons d'entrée et de sortie × prix par million."""
    cout = (jetons["entree"] * prix["entree_par_million"] + jetons["sortie"] * prix["sortie_par_million"]) / 1_000_000
    # Six décimales : une question coûte environ 0,01 USD ; arrondir à quatre fausserait chaque question d'environ 0,5 %.
    return round(cout, 6)


def _niveau(valeur: float | None, signal: dict) -> str:
    if valeur is None:
        return "inconnu"
    if valeur >= signal["rouge"]:
        return "probleme"
    return "attention" if valeur >= signal["orange"] else "sain"


def est_resolu(nom: str, verdict: dict) -> bool:
    """La « résolution » écrite dans `monitorage/seuils.json`, appliquée à un verdict (pour la vigie, étape 4).

    Un taux est résolu quand plus aucun événement ne reste dans la fenêtre, ou quand il repasse sous le rouge avec
    assez de requêtes. Des événements encore présents sous le minimum de requêtes ne résolvent rien : on attend.
    """
    if nom in SIGNAUX_EN_TAUX:
        assez = verdict["effectif"] >= verdict["minimum_requetes"]
        return verdict["numerateur"] == 0 or (assez and verdict["valeur"] < verdict["rouge"])
    if nom == "latence_p95_ms":
        assez = verdict["effectif"] >= verdict["minimum_requetes"]
        return verdict["effectif"] == 0 or (assez and verdict["valeur"] < verdict["rouge"])
    if nom == "fraicheur":
        return verdict["etat"] in ("sain", "attention")
    return verdict["valeur"] is not None and verdict["valeur"] < verdict["rouge"]


def evaluer(etat: dict, config: dict) -> dict:
    """Un verdict par signal mesuré par l'API (tous sauf `service`), avec sa valeur, ses seuils et son action."""
    signaux = config["signaux"]
    verdicts = {}
    for nom in SIGNAUX:
        if nom == "service":
            continue
        signal = signaux[nom]
        verdict = {"libelle": signal["libelle"], "unite": signal["unite"], "orange": signal["orange"],
                   "rouge": signal["rouge"], "pourquoi": signal["pourquoi"], "action": signal["action"],
                   "resolution": signal["resolution"]}
        if nom in SIGNAUX_EN_TAUX or nom == "latence_p95_ms":
            mesure = etat[nom]
            assez = mesure["effectif"] >= signal["minimum_requetes"]
            verdict.update(valeur=mesure["valeur"], effectif=mesure["effectif"],
                           minimum_requetes=signal["minimum_requetes"], fenetre_min=signal["fenetre_min"],
                           etat=_niveau(mesure["valeur"], signal) if assez else "inconnu")
            if "numerateur" in mesure:
                verdict["numerateur"] = mesure["numerateur"]
        elif nom == "cout_24h_usd":
            valeur = etat["cout_24h"]["valeur"]
            verdict.update(valeur=valeur, etat=_niveau(valeur, signal))
        elif nom == "rejets_15_min":
            verdict.update(valeur=etat["rejets_15_min"], etat=_niveau(etat["rejets_15_min"], signal))
        else:   # fraicheur : la couleur vient de monitorage/fraicheur.py, une seule source de vérité
            fraicheur = etat["fraicheur"]
            retards = [e["retard_jours_ouvres"] for e in fraicheur["en_retard"]]
            verdict.update(valeur=max((r for r in retards if r is not None), default=None),
                           en_retard=fraicheur["en_retard"], etat=_ETAT_FRAICHEUR[fraicheur["pire"]])
        verdicts[nom] = verdict
    return verdicts
