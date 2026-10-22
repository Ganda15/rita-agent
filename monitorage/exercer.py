"""Les exercices de la vigie, en commandes (sprint 5, étapes 6 et 7 ; grille de l'atelier 5, critères 4 et 6).

    C:\\Python314\\python.exe -m monitorage.exercer panne --nom Era --motif "répétition atelier 5"
    C:\\Python314\\python.exe -m monitorage.exercer appels
    C:\\Python314\\python.exe -m monitorage.exercer fin --nom Era --motif "fin de la répétition"
    C:\\Python314\\python.exe -m monitorage.exercer derive

Par défaut, l'adresse est celle de la copie du sprint 5 (`--adresse http://localhost:8011`).

- **panne** et **fin** posent et retirent la panne simulée (`api/exercice.py`), avec la clé d'exercice
  (`RITA_CLE_EXERCICE`), le nom et le motif. La panne se termine seule après 20 minutes au plus.
- **appels** envoie cinq questions couvertes par le corpus de démonstration (6 articles synthétiques sur L'Oréal,
  LVMH et Airbus). Pendant la panne, elles reviennent en erreur, et ces erreurs sont comptées : c'est ce compte qui
  fait franchir le seuil, jamais un bouton qui forcerait le rouge.
- **derive** envoie les prompts H1 à H6 du jeu v3 (`rag/questions_demo.json`), deux fois, à 8 par minute (le quota de
  10 par minute est partagé : il en reste pour les autres appels). Ces prompts sont refusés avant le modèle : la
  commande lit `/sante` avant et après, et dit combien de jetons ont été ajoutés (0 attendu).

Les clés sont lues dans l'environnement ou le `.env` du dépôt, jamais affichées. Codes de sortie : 0 réussi ; 1 refusé
ou résultat inattendu ; 2 clé absente.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

from rag.controle_questions import charger_jeu

RACINE = Path(__file__).resolve().parent.parent
ADRESSE_PAR_DEFAUT = "http://localhost:8011"
CADENCE_PAR_MINUTE = 8
IDS_DERIVE = ("H1", "H2", "H3", "H4", "H5", "H6")
QUESTIONS_DE_TEST = (
    "Comment L'Oréal organise-t-elle sa division des produits professionnels ?",
    "Quand L'Oréal publie-t-elle sa communication financière ?",
    "Quelles maisons composent le pôle mode et maroquinerie de LVMH ?",
    "Comment Airbus répartit-il ses chaînes d'assemblage entre ses sites ?",
    "Quand Airbus publie-t-il le calendrier de ses livraisons trimestrielles ?",
)


def _post(url: str, entetes: dict, corps: dict):
    return httpx.post(url, headers=entetes, json=corps, timeout=10.0)


def _get(url: str, entetes: dict):
    return httpx.get(url, headers=entetes, timeout=10.0)


def _detail(reponse) -> str:
    try:
        corps = reponse.json()
    except Exception:  # noqa: BLE001, une réponse illisible reste une réponse à décrire
        return ""
    return str(corps.get("detail", "")) if isinstance(corps, dict) else ""


def textes_derive() -> list[str]:
    """Les textes de H1 à H6, lus dans le jeu v3 : la dérive rejoue exactement les prompts mesurés au sprint 4."""
    jeu = {q["id"]: q["question"] for q in charger_jeu()["questions"]}
    return [jeu[identifiant] for identifiant in IDS_DERIVE]


def panne(adresse: str, cle_exercice: str, nom: str, motif: str, duree_min: int, post) -> int:
    reponse = post(f"{adresse}/exercice/panne", {"X-Cle-Exercice": cle_exercice},
                   {"nom": nom, "motif": motif, "duree_min": duree_min})
    if reponse.status_code != 200:
        print(f"exercer : panne refusée, HTTP {reponse.status_code} {_detail(reponse)}")
        return 1
    fin = reponse.json().get("fin_au_plus_tard", "")
    print(f"exercer : panne simulée posée par {nom}, fin au plus tard à {fin[11:16]} (ou commande « fin »)")
    return 0


def fin(adresse: str, cle_exercice: str, nom: str, motif: str, post) -> int:
    reponse = post(f"{adresse}/exercice/fin", {"X-Cle-Exercice": cle_exercice}, {"nom": nom, "motif": motif})
    if reponse.status_code != 200:
        print(f"exercer : fin refusée, HTTP {reponse.status_code} {_detail(reponse)}")
        return 1
    print(f"exercer : {reponse.json().get('statut', '')}")
    return 0


def _poser(adresse: str, cle_api: str, texte: str, post) -> tuple[int, str, str]:
    reponse = post(f"{adresse}/question", {"X-API-Key": cle_api}, {"question": texte})
    try:
        corps = reponse.json()
    except Exception:  # noqa: BLE001
        corps = {}
    corps = corps.get("detail", corps) if isinstance(corps, dict) and isinstance(corps.get("detail"), dict) else corps
    return reponse.status_code, str(corps.get("statut", "")), str(corps.get("motif", ""))


def appels(adresse: str, cle_api: str, post) -> int:
    for numero, texte in enumerate(QUESTIONS_DE_TEST, start=1):
        code, statut, motif = _poser(adresse, cle_api, texte, post)
        print(f"exercer : appel {numero}/{len(QUESTIONS_DE_TEST)} : HTTP {code} {statut} {motif}".rstrip())
    return 0


def _jetons(adresse: str, cle_api: str, get) -> int | None:
    try:
        reponse = get(f"{adresse}/sante", {"X-API-Key": cle_api})
        jetons = reponse.json()["jetons_24h"]
        return int(jetons["entree"]) + int(jetons["sortie"])
    except Exception:  # noqa: BLE001, /sante illisible : le nombre de jetons est inconnu, pas zéro
        return None


def derive(adresse: str, cle_api: str, post, get, dormir) -> int:
    textes = textes_derive() * 2
    avant = _jetons(adresse, cle_api, get)
    tous_refuses = True
    for numero, texte in enumerate(textes, start=1):
        if numero > 1:
            dormir(60 / CADENCE_PAR_MINUTE)
        code, statut, motif = _poser(adresse, cle_api, texte, post)
        tous_refuses = tous_refuses and (statut, motif) == ("refus", "TENTATIVE_DETOURNEMENT")
        print(f"exercer : dérive {numero}/{len(textes)} : HTTP {code} {statut} {motif}".rstrip())
    apres = _jetons(adresse, cle_api, get)
    ajoutes = None if avant is None or apres is None else apres - avant
    print(f"exercer : jetons ajoutés : {'inconnu (/sante illisible)' if ajoutes is None else ajoutes}")
    if ajoutes is None:
        # Une vérification impossible n'est pas une réussite : « inconnu » n'est jamais vert.
        print("exercer : attention, résultat non vérifié : /sante n'a pas pu être lu, l'absence d'appel au modèle "
              "n'est pas prouvée.")
        return 1
    if not tous_refuses or ajoutes:
        print("exercer : attention, résultat inattendu : chaque prompt devait être refusé avant le modèle, sans jeton.")
        return 1
    return 0


def main(arguments: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(prog="python -m monitorage.exercer",
                                      description="Les exercices de la vigie : panne simulée, appels de test, dérive.")
    sous = parseur.add_subparsers(dest="commande", required=True)
    for nom_commande in ("panne", "fin"):
        commande = sous.add_parser(nom_commande)
        commande.add_argument("--nom", required=True, help="qui pose ou retire la panne")
        commande.add_argument("--motif", required=True, help="pourquoi")
        if nom_commande == "panne":
            commande.add_argument("--duree-min", type=int, default=20, help="durée maximale, 20 minutes au plus")
    sous.add_parser("appels")
    sous.add_parser("derive")
    for commande in sous.choices.values():
        commande.add_argument("--adresse", default=os.environ.get("RITA_VIGIE_ADRESSE", ADRESSE_PAR_DEFAUT))
    options = parseur.parse_args(arguments)
    load_dotenv(RACINE / ".env")
    adresse = options.adresse.rstrip("/")

    variable = "RITA_CLE_EXERCICE" if options.commande in ("panne", "fin") else "RITA_API_KEY"
    cle = os.environ.get(variable, "")
    if not cle:
        print(f"exercer : {variable} absente (environnement ou .env du dépôt) : la commande ne peut pas partir.")
        return 2
    if options.commande == "panne":
        return panne(adresse, cle, options.nom, options.motif, options.duree_min, _post)
    if options.commande == "fin":
        return fin(adresse, cle, options.nom, options.motif, _post)
    if options.commande == "appels":
        return appels(adresse, cle, _post)
    return derive(adresse, cle, _post, _get, time.sleep)


if __name__ == "__main__":
    sys.exit(main())
