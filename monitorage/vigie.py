"""La vigie de RITA : elle regarde l'API de dehors et ouvre une issue par signal en problème (sprint 5, étape 4).

Plan du sprint 5, § 2 « Vigie » et « Alerte ». Livrable : E5 (C20 surveiller, C21 incidents).

    C:\\Python314\\python.exe -m monitorage.vigie --adresse http://localhost:8011            (à blanc)
    C:\\Python314\\python.exe -m monitorage.vigie --adresse http://localhost:8011 --github   (pour de vrai)

## Un passage

1. **La sonde** : `/health`, deux essais à 10 secondes d'écart (`monitorage/seuils.json`, signal `service`). Une API
   arrêtée ne peut pas annoncer sa propre panne : c'est pour cela que la vigie tourne hors de l'API. Deux échecs
   ouvrent l'alerte « service » et le passage s'arrête : `/sante` ne répondrait pas non plus.
2. **Les verdicts** : `/sante`, avec la clé. Un signal en « problème » ouvre UNE issue, au titre stable ; si elle est
   déjà ouverte, rien de plus (une vigie lancée toutes les quelques minutes ne commente pas à chaque passage).
3. **La résolution** : un signal dont la résolution écrite est atteinte (`seuils.est_resolu`) ferme son issue, avec un
   commentaire « Retour à la normale ».
4. **Après une panne**, deux constats distincts : dès qu'un appel aboutit de nouveau, un seul commentaire « Service
   rétabli », avec l'heure à laquelle l'alerte de taux devrait se résoudre ; la fermeture vient quand les erreurs sont
   sorties de la fenêtre de 15 minutes.

## Les conventions de l'issue

Les mêmes que `.github/workflows/alerte-incident.yml` (alertes Langfuse) : étiquette `incident` (et `E5`), titre stable
qui permet de retrouver l'issue déjà ouverte. « prototype local » dans le titre la distingue d'un incident de
production. Le corps donne le signal, la valeur, le seuil, l'heure, le pourquoi, le lien vers l'action et la
résolution. Jamais la clé, jamais le texte d'une question.

## Sécurité

Sans `--github`, rien n'est envoyé à GitHub : la vigie affiche ce qu'elle ferait. La clé est lue dans l'environnement
(`RITA_API_KEY`, ou le `.env` du dépôt) et n'est jamais affichée. `gh` est appelé avec une liste d'arguments, sans
shell : une valeur ne peut pas devenir une commande.

Codes de sortie : 0 tout est sain ; 1 au moins un problème ; 2 la vigie n'a pas pu lire `/sante` (ou pas de clé).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

from monitorage import seuils as module_seuils

RACINE = Path(__file__).resolve().parent.parent
DEPOT = "Ganda15/rita-agent"
BRANCHE_DOC = "sprint-5-vigie-demo"
ETIQUETTES = ("incident", "E5")
PREFIXE_TITRE = "Incident : vigie (prototype local)"
ADRESSE_PAR_DEFAUT = "http://localhost:8011"


def titre(signal: str) -> str:
    """Le titre stable d'une alerte : c'est lui qui retrouve l'issue déjà ouverte."""
    return f"{PREFIXE_TITRE} « {signal} »"


def _hh_mm(horodatage: float) -> str:
    return datetime.fromtimestamp(horodatage).strftime("%H:%M")


def _heure(horodatage: float) -> str:
    return datetime.fromtimestamp(horodatage).strftime("%d/%m/%Y %H:%M")


def _fr(nombre: float, decimales: int = 1) -> str:
    return f"{nombre:.{decimales}f}".replace(".", ",")


def _http_get(url: str, entetes: dict | None):
    return httpx.get(url, headers=entetes or {}, timeout=10.0)


# --- Lire un verdict comme une phrase ------------------------------------------------------------------------------------

def _valeur_lisible(nom: str, verdict: dict) -> str:
    valeur = verdict.get("valeur")
    if nom in module_seuils.SIGNAUX_EN_TAUX:
        if valeur is None:
            return f"aucune requête sur les {verdict['fenetre_min']} dernières minutes"
        return (f"{_fr(valeur * 100)} % ({verdict['numerateur']} sur {verdict['effectif']} résultats, "
                f"{verdict['fenetre_min']} dernières minutes)")
    if nom == "latence_p95_ms":
        if valeur is None:
            return f"aucune requête sur les {verdict['fenetre_min']} dernières minutes"
        return f"{_fr(valeur / 1000)} s (p95 de {verdict['effectif']} résultats, {verdict['fenetre_min']} dernières minutes)"
    if nom == "cout_24h":
        return "inconnu" if valeur is None else f"{_fr(valeur, 2)} € sur les 24 dernières heures disponibles"
    if nom == "fraicheur":
        retards = [f"{e['ticker']} ({'aucune cotation' if e['retard_jours_ouvres'] is None else str(e['retard_jours_ouvres']) + ' jours ouvrés'})"
                   for e in verdict.get("en_retard", [])]
        return ", ".join(retards) or "aucune valeur en retard"
    return f"{valeur} sur les 15 dernières minutes"


def _seuil_lisible(nom: str, verdict: dict) -> str:
    orange, rouge = verdict["orange"], verdict["rouge"]
    if nom in module_seuils.SIGNAUX_EN_TAUX:
        texte = f"problème à partir de {_fr(rouge * 100)} %, attention à partir de {_fr(orange * 100)} %"
    elif nom == "latence_p95_ms":
        texte = f"problème à partir de {_fr(rouge / 1000, 0)} s, attention à partir de {_fr(orange / 1000, 0)} s"
    elif nom == "cout_24h":
        texte = f"problème à partir de {_fr(rouge, 2)} €, attention à partir de {_fr(orange, 2)} €"
    elif nom == "fraicheur":
        texte = f"problème à partir de {rouge} jours ouvrés de retard, attention à partir de {orange}"
    else:
        texte = f"problème à partir de {rouge}, attention à partir de {orange}"
    if "minimum_requetes" in verdict:
        texte += f" ; au moins {verdict['minimum_requetes']} requêtes"
    return texte


def _lien(action: str) -> str:
    return f"[{action}](https://github.com/{DEPOT}/blob/{BRANCHE_DOC}/{action})"


def _corps(libelle: str, nom: str, verdict_mot: str, valeur: str, seuil: str, pourquoi: str, action: str,
           resolution: str, adresse: str, maintenant: float) -> str:
    return "\n".join([
        f"## Alerte de la vigie, le {_heure(maintenant)} (heure du poste de la vigie)",
        "",
        "| | |",
        "|---|---|",
        f"| Signal | {libelle} (`{nom}`) |",
        f"| Verdict | {verdict_mot} |",
        f"| Valeur | {valeur} |",
        f"| Seuil | {seuil} |",
        f"| Adresse surveillée | {adresse} |",
        "",
        f"**Pourquoi ce seuil** : {pourquoi}",
        "",
        f"**Que faire** : {_lien(action)}",
        "",
        f"**Résolution** : {resolution}",
        "",
        "Issue ouverte par `monitorage/vigie.py` (sprint 5, prototype local). Elle se ferme seule, avec un "
        "commentaire, quand la résolution est atteinte.",
    ])


# --- La sonde, puis un passage complet ----------------------------------------------------------------------------------

def sonder_service(http_get, adresse: str, essais: int, intervalle_s: float, dormir) -> bool:
    """`/health` répond-il 200 ? Jusqu'à `essais` tentatives, espacées de `intervalle_s` secondes."""
    for essai in range(essais):
        if essai:
            dormir(intervalle_s)
        try:
            if http_get(f"{adresse}/health", None).status_code == 200:
                return True
        except Exception:  # noqa: BLE001, une connexion refusée est une sonde en échec, pas une erreur de la vigie
            pass
    return False


def passage(adresse: str, cle: str, http_get, github, dormir, horloge, config: dict) -> tuple[list[str], int]:
    """Un passage de la vigie : la sonde, puis les verdicts. Rend les actions faites et le code de sortie."""
    actions: list[str] = []
    ouvertes = github.issues_ouvertes()
    maintenant = horloge()
    service = config["signaux"]["service"]

    if not sonder_service(http_get, adresse, service["essais"], service["intervalle_s"], dormir):
        if titre("service") not in ouvertes:
            valeur = (f"{service['essais']} sondes de /health sans réponse 200, à {service['intervalle_s']} s "
                      "d'écart")
            github.ouvrir(titre("service"), _corps(service["libelle"], "service", "problème", valeur,
                                                   "deux sondes en échec", service["pourquoi"], service["action"],
                                                   service["resolution"], adresse, maintenant))
            actions.append(f"ouverte : {titre('service')}")
        return actions, 1
    if titre("service") in ouvertes:
        github.fermer(ouvertes[titre("service")],
                      f"Retour à la normale le {_heure(maintenant)} : /health répond de nouveau 200.")
        actions.append(f"fermée : {titre('service')}")

    reponse = http_get(f"{adresse}/sante", {"X-API-Key": cle})
    if reponse.status_code != 200:
        actions.append(f"/sante illisible : HTTP {reponse.status_code} (clé de la vigie, ou API d'une autre version)")
        return actions, 2
    etat = reponse.json()

    code = 0
    for nom, verdict in etat["verdicts"].items():
        cle_titre = titre(nom)
        if verdict["etat"] == "probleme":
            code = 1
            if cle_titre not in ouvertes:
                github.ouvrir(cle_titre, _corps(verdict["libelle"], nom, "problème", _valeur_lisible(nom, verdict),
                                                _seuil_lisible(nom, verdict), verdict["pourquoi"], verdict["action"],
                                                verdict["resolution"], adresse, maintenant))
                actions.append(f"ouverte : {cle_titre}")
                continue
        if cle_titre not in ouvertes:
            continue
        numero = ouvertes[cle_titre]
        if module_seuils.est_resolu(nom, verdict):
            github.fermer(numero, f"Retour à la normale le {_heure(maintenant)} : {verdict['resolution']} "
                                  f"Valeur actuelle : {_valeur_lisible(nom, verdict)}.")
            actions.append(f"fermée : {cle_titre}")
        elif nom == "erreurs_techniques":
            actions += _service_retabli(github, numero, cle_titre, etat, verdict)
    return actions, code


def _service_retabli(github, numero: int, cle_titre: str, etat: dict, verdict: dict) -> list[str]:
    """Après une panne : le service répond de nouveau, mais les erreurs restent dans la fenêtre. Un seul commentaire."""
    dernier = etat.get("dernier_resultat")
    derniere_erreur = etat.get("derniers", {}).get("erreur_technique")
    if not dernier or dernier["categorie"] == "erreur_technique" or not derniere_erreur:
        return []
    if any(c.startswith("Service rétabli") for c in github.commentaires(numero)):
        return []
    retabli = _hh_mm(datetime.fromisoformat(dernier["a"]).timestamp())
    fin = _hh_mm(datetime.fromisoformat(derniere_erreur).timestamp() + verdict["fenetre_min"] * 60)
    github.commenter(numero, f"Service rétabli à {retabli} : le dernier appel a abouti. L'alerte de taux reste "
                             f"ouverte jusqu'à {fin} environ, quand les erreurs sortiront de la fenêtre de "
                             f"{verdict['fenetre_min']} minutes.")
    return [f"commentée : {cle_titre} (service rétabli)"]


# --- GitHub ---------------------------------------------------------------------------------------------------------------

class GitHubCli:
    """Les issues par `gh` (déjà connecté sur le poste). Une liste d'arguments, jamais de shell."""

    def __init__(self, depot: str = DEPOT, executer=subprocess.run):
        self.depot, self._executer = depot, executer

    def _gh(self, *arguments: str, entree: str | None = None) -> str:
        resultat = self._executer(["gh", *arguments, "-R", self.depot], input=entree, capture_output=True, text=True,
                                  encoding="utf-8", check=True)
        return resultat.stdout

    def issues_ouvertes(self) -> dict[str, int]:
        sortie = self._gh("issue", "list", "--state", "open", "--label", ETIQUETTES[0], "--json", "number,title",
                          "--limit", "100")
        return {i["title"]: i["number"] for i in json.loads(sortie or "[]") if i["title"].startswith(PREFIXE_TITRE)}

    def ouvrir(self, titre_issue: str, corps: str) -> None:
        etiquettes = [option for etiquette in ETIQUETTES for option in ("--label", etiquette)]
        self._gh("issue", "create", "--title", titre_issue, "--body-file", "-", *etiquettes, entree=corps)

    def commenter(self, numero: int, corps: str) -> None:
        self._gh("issue", "comment", str(numero), "--body-file", "-", entree=corps)

    def fermer(self, numero: int, commentaire: str) -> None:
        self._gh("issue", "close", str(numero), "--comment", commentaire)

    def commentaires(self, numero: int) -> list[str]:
        sortie = self._gh("issue", "view", str(numero), "--json", "comments")
        return [c["body"] for c in json.loads(sortie or "{}").get("comments", [])]


class GitHubABlanc:
    """Sans `--github` : la vigie dit ce qu'elle ferait, et GitHub n'est pas touché."""

    def issues_ouvertes(self) -> dict[str, int]:
        return {}

    def ouvrir(self, titre_issue: str, corps: str) -> None:
        print(f"[à blanc] ouvrirait l'issue : {titre_issue}")

    def commenter(self, numero: int, corps: str) -> None:
        print(f"[à blanc] commenterait l'issue {numero}")

    def fermer(self, numero: int, commentaire: str) -> None:
        print(f"[à blanc] fermerait l'issue {numero}")

    def commentaires(self, numero: int) -> list[str]:
        return []


def main(arguments: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(prog="python -m monitorage.vigie",
                                      description="La vigie de RITA : sonde /health, lit /sante, ouvre et ferme les "
                                                  "issues d'alerte.")
    parseur.add_argument("--adresse", default=os.environ.get("RITA_VIGIE_ADRESSE", ADRESSE_PAR_DEFAUT),
                         help=f"l'API surveillée (défaut : {ADRESSE_PAR_DEFAUT}, la copie du sprint 5)")
    parseur.add_argument("--github", action="store_true",
                         help="ouvrir, commenter et fermer les issues pour de vrai ; sans cette option : à blanc")
    options = parseur.parse_args(arguments)
    load_dotenv(RACINE / ".env")
    cle = os.environ.get("RITA_API_KEY", "")
    if not cle:
        print("vigie : RITA_API_KEY absente (environnement ou .env du dépôt) : /sante ne peut pas être lu.")
        return 2
    github = GitHubCli() if options.github else GitHubABlanc()
    if not options.github:
        print("vigie : mode à blanc, aucune issue n'est créée ni fermée (ajouter --github pour agir).")
    actions, code = passage(options.adresse.rstrip("/"), cle, _http_get, github, time.sleep, time.time,
                            module_seuils.charger())
    for action in actions:
        print(f"vigie : {action}")
    print(f"vigie : passage terminé, code {code} (0 sain, 1 problème, 2 /sante illisible)")
    return code


if __name__ == "__main__":
    sys.exit(main())
