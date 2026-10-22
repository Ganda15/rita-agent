"""La copie du sprint 5 sur le poste : déployer, revenir, initialiser, collecter, état (sprint 5, étape 9).

Plan du sprint 5, § 2 « Déployer et rollback ». Le prototype local tourne dans un projet Compose à part (`rita-s5`,
`docker-compose.sprint5.yml`), avec sa propre image par commit (`rita-api:s5-<12 premiers caractères du commit>`).

    C:\\Python314\\python.exe scripts\\copie_sprint5.py deployer      construire l'image du commit courant, relancer
    C:\\Python314\\python.exe scripts\\copie_sprint5.py initialiser   la première fois : jeu de démonstration et index
    C:\\Python314\\python.exe scripts\\copie_sprint5.py collecter     collecter les cours dans la copie
    C:\\Python314\\python.exe scripts\\copie_sprint5.py revenir       relancer la version précédente, sans reconstruire
    C:\\Python314\\python.exe scripts\\copie_sprint5.py etat          versions courante et précédente, /health

Les règles, chacune testée (tests/test_copie_sprint5.py) :
- **déployer** refuse de partir pendant une panne simulée ; garde la version qui tournait comme « précédente » ;
  construit l'image avec le commit (`GIT_SHA`) et vérifie que `/health` annonce ce commit ; sur un échec, l'état ne
  change pas.
- **revenir** relance l'image précédente **sans la reconstruire** (`--no-build`), puis vérifie le commit annoncé par
  `/health` ET l'identifiant de l'image du conteneur ; comme en production, il consomme la version précédente (un
  second retour est refusé). Pendant une panne simulée, il refuse : une panne du fournisseur ne se règle pas par un
  retour arrière, on retire d'abord l'exercice. La base n'est pas restaurée.
- `docker` et `git` sont appelés avec une liste d'arguments, jamais par un shell. Aucune clé n'est affichée.

L'état (versions courante et précédente) vit dans `.copie-sprint5.json`, ignoré par Git. Codes de sortie : 0 réussi,
1 refusé ou échec.
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

RACINE = Path(__file__).resolve().parent.parent
PROJET = "rita-s5"
FICHIERS = ("docker-compose.yml", "docker-compose.sprint5.yml")
ADRESSE = "http://localhost:8011"
CONTENEUR_API = "rita-api-s5"
CHEMIN_ETAT = RACINE / ".copie-sprint5.json"
ATTENTE_S = 120
PAS_S = 3


def compose(*arguments: str) -> list[str]:
    commande = ["docker", "compose", "-p", PROJET]
    for fichier in FICHIERS:
        commande += ["-f", str(RACINE / fichier)]
    return commande + list(arguments)


def _http_get(url: str, entetes: dict | None):
    return httpx.get(url, headers=entetes or {}, timeout=5.0)


class Copie:
    def __init__(self, executer=subprocess.run, http_get=_http_get, dormir=time.sleep, chemin_etat: Path = CHEMIN_ETAT,
                 adresse: str = ADRESSE):
        self._executer, self._http_get, self._dormir = executer, http_get, dormir
        self._chemin_etat, self._adresse = Path(chemin_etat), adresse

    # --- outils ------------------------------------------------------------------------------------------------------
    def _lancer(self, arguments: list[str], variables: dict | None = None, capturer: bool = False) -> str:
        resultat = self._executer(arguments, cwd=RACINE, env={**os.environ, **(variables or {})}, check=True,
                                  capture_output=capturer, text=True, encoding="utf-8")
        return (resultat.stdout or "").strip() if capturer else ""

    def _lire_etat(self) -> dict:
        if not self._chemin_etat.exists():
            return {"courante": None, "precedente": None}
        return json.loads(self._chemin_etat.read_text(encoding="utf-8"))

    def _ecrire_etat(self, etat: dict) -> None:
        self._chemin_etat.write_text(json.dumps(etat, indent=1), encoding="utf-8")

    @staticmethod
    def _variables(version: dict, construit_le: str | None = None) -> dict:
        variables = {"RITA_S5_VERSION": version["version"], "RITA_S5_GIT_SHA": version["commit"]}
        if construit_le:
            variables["RITA_S5_CONSTRUIT_LE"] = construit_le
        return variables

    def _exercice_en_cours(self, cle: str) -> dict | None:
        """La panne simulée en cours, lue dans /sante ; `None` si aucune, ou si la copie ne répond pas encore."""
        try:
            reponse = self._http_get(f"{self._adresse}/sante", {"X-API-Key": cle})
            return reponse.json().get("exercice") if reponse.status_code == 200 else None
        except Exception:  # noqa: BLE001, une copie arrêtée n'a pas d'exercice en cours
            return None

    def _attendre_commit(self, commit: str) -> bool:
        for _ in range(ATTENTE_S // PAS_S):
            try:
                reponse = self._http_get(f"{self._adresse}/health", None)
                if reponse.status_code == 200 and reponse.json().get("commit") == commit:
                    return True
            except Exception:  # noqa: BLE001, le conteneur démarre encore
                pass
            self._dormir(PAS_S)
        return False

    # --- les actions --------------------------------------------------------------------------------------------------
    def deployer(self, cle: str) -> int:
        exercice = self._exercice_en_cours(cle)
        if exercice:
            print(f"copie : déploiement refusé : un exercice de panne est en cours (posé par {exercice['nom']}). "
                  "Le retirer d'abord : python -m monitorage.exercer fin --nom ... --motif ...")
            return 1
        commit = self._lancer(["git", "rev-parse", "HEAD"], capturer=True)
        nouvelle = {"version": commit[:12], "commit": commit}
        variables = self._variables(nouvelle, datetime.now().astimezone().isoformat(timespec="seconds"))
        print(f"copie : construction de l'image rita-api:s5-{nouvelle['version']} (la première fois, plusieurs minutes)")
        self._lancer(compose("build", "api"), variables)
        self._lancer(compose("up", "-d", "postgres", "api"), variables)
        if not self._attendre_commit(commit):
            print(f"copie : échec : /health n'annonce pas le commit {commit[:12]} après {ATTENTE_S} s "
                  "(docker logs rita-api-s5 pour le détail). L'état de la copie n'est pas modifié.")
            return 1
        etat = self._lire_etat()
        courante = etat.get("courante")
        precedente = courante if courante and courante["version"] != nouvelle["version"] else etat.get("precedente")
        self._ecrire_etat({"courante": nouvelle, "precedente": precedente})
        print(f"copie : déployée, /health annonce {commit[:12]} ; version précédente gardée : "
              f"{precedente['version'] if precedente else 'aucune'}")
        return 0

    def revenir(self, cle: str) -> int:
        if self._exercice_en_cours(cle):
            print("copie : retour arrière refusé : un exercice de panne est en cours. Une panne du fournisseur "
                  "ne la règle pas ; retirer d'abord l'exercice (python -m monitorage.exercer fin).")
            return 1
        etat = self._lire_etat()
        precedente = etat.get("precedente")
        if not precedente:
            print("copie : retour arrière refusé : aucune version précédente (déjà consommée, ou un seul déploiement).")
            return 1
        self._lancer(compose("up", "-d", "--no-build", "api"), self._variables(precedente))
        if not self._attendre_commit(precedente["commit"]):
            print(f"copie : échec : /health n'annonce pas {precedente['version']} après {ATTENTE_S} s.")
            return 1
        image_conteneur = self._lancer(["docker", "inspect", "--format", "{{.Image}}", CONTENEUR_API], capturer=True)
        image_attendue = self._lancer(["docker", "image", "inspect", "--format", "{{.Id}}",
                                       f"rita-api:s5-{precedente['version']}"], capturer=True)
        if image_conteneur != image_attendue:
            print(f"copie : échec : le conteneur tourne sur l'image {image_conteneur}, pas sur {image_attendue}.")
            return 1
        self._ecrire_etat({"courante": precedente, "precedente": None})
        print(f"copie : revenue à {precedente['version']} ; /health l'annonce, image vérifiée ({image_conteneur}). "
              "La base n'est pas restaurée ; un second retour sera refusé.")
        return 0

    def _ponctuel(self, service: str) -> int:
        courante = self._lire_etat().get("courante")
        if not courante:
            print("copie : déployer d'abord (python scripts\\copie_sprint5.py deployer).")
            return 1
        self._lancer(compose("--profile", "outils", "run", "--rm", service), self._variables(courante))
        return 0

    def initialiser(self) -> int:
        return self._ponctuel("initialisation")

    def collecter(self) -> int:
        return self._ponctuel("collecte")

    def etat(self) -> int:
        etat = self._lire_etat()
        for cle in ("courante", "precedente"):
            version = etat.get(cle)
            print(f"copie : version {cle} : {version['version'] if version else 'aucune'}")
        try:
            sante = self._http_get(f"{self._adresse}/health", None).json()
            print(f"copie : /health : commit {str(sante.get('commit'))[:12]}, construit le {sante.get('construit_le')}")
        except Exception:  # noqa: BLE001
            print(f"copie : /health ne répond pas sur {self._adresse}")
        return 0


def main(arguments: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(prog="python scripts/copie_sprint5.py",
                                      description="La copie du sprint 5 sur le poste (prototype local).")
    parseur.add_argument("action", choices=["deployer", "revenir", "initialiser", "collecter", "etat"])
    options = parseur.parse_args(arguments)
    load_dotenv(RACINE / ".env")
    copie = Copie()
    cle = os.environ.get("RITA_API_KEY", "")
    actions = {"deployer": lambda: copie.deployer(cle), "revenir": lambda: copie.revenir(cle),
               "initialiser": lambda: copie.initialiser(), "collecter": lambda: copie.collecter(),
               "etat": lambda: copie.etat()}
    try:
        return actions[options.action]()
    except subprocess.CalledProcessError as erreur:
        print(f"copie : la commande a échoué (code {erreur.returncode}) : {' '.join(erreur.cmd[:6])} ...")
        return 1


if __name__ == "__main__":
    sys.exit(main())
