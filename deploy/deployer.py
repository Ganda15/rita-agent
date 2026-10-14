"""Script du serveur de RITA (sprint 2) : livrer une image testée et revenir à la version précédente.

Installé par Era dans `/root/rita-deploy/bin/` ; lancé seulement par la clé SSH dédiée, à commande forcée, via
`deploy/deployer.sh`. Bibliothèque standard seulement : le serveur n'a rien d'autre à installer.

Deux parties :
- les RÈGLES (tâche 7), sans Docker ni réseau : analyse des ordres, créneau du matin, transitions d'état ; état,
  journal, marque d'opération et verrou sur le disque ;
- l'ORCHESTRATION (tâche 8) : préparer une version, pré-test en préproduction, bascule de l'API seule, contrôles
  d'après bascule, retour automatique ou manuel, et `main`, le point d'entrée appelé par SSH.
Conception : `docs/CHAINE-V1.md` § 4, § 5 et § 11 (périmètre de l'atelier).

Codes de sortie de `main` : 0 réussi ; 1 refusé ou en échec ; 2 ordre refusé ; 75 livraison reportée par le créneau.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta
from datetime import time as heure
from pathlib import Path
from zoneinfo import ZoneInfo

PARIS = ZoneInfo("Europe/Paris")
DEBUT_CRENEAU = heure(8, 0)
FIN_CRENEAU = heure(9, 0)
CODE_CRENEAU = 75  # « livraison reportée par le créneau du matin, rien n'a changé »


class OrdreRefuse(Exception):
    """L'ordre reçu par SSH n'est pas l'un des trois ordres permis, écrit en entier."""


class EtatIllisible(Exception):
    """Le fichier d'état existe mais ne se lit pas : on s'arrête, on ne devine jamais."""


class AucunePrecedente(Exception):
    """Retour arrière demandé alors qu'aucune version précédente validée n'est connue."""


class OperationInachevee(Exception):
    """Une opération précédente a laissé sa marque : l'état réel doit être vérifié avant toute autre."""


class VerrouOccupe(Exception):
    """Une autre opération tient le verrou du serveur au-delà de l'attente permise."""


# --- Les ordres ----------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Ordre:
    nom: str
    argument: str | None = None


# `fullmatch` exige que TOUT le texte corresponde : un caractère de plus, un retour à la ligne final ou une commande
# collée (« ; rm -rf / ») suffisent à refuser l'ordre, sans rien exécuter.
_ORDRES = (
    ("livrer", re.compile(r"livrer (ghcr\.io/ganda15/rita-api@sha256:[0-9a-f]{64})")),
    ("revenir", re.compile(r"revenir ([0-9]{1,20})")),
    ("version", re.compile(r"version")),
)


def analyser_ordre(texte: str) -> Ordre:
    for nom, motif in _ORDRES:
        trouve = motif.fullmatch(texte)
        if trouve:
            return Ordre(nom, trouve.group(1) if motif.groups else None)
    raise OrdreRefuse(f"ordre refusé ({len(texte)} caractères) : seuls livrer, revenir et version sont permis")


# --- Le créneau du matin -------------------------------------------------------------------------------------------

def _a_paris(maintenant: datetime) -> datetime:
    if maintenant.tzinfo is None:
        raise ValueError("heure sans fuseau : ambiguë, refusée")
    return maintenant.astimezone(PARIS)


def _secondes_jusqu_a_9h(maintenant: datetime, debut: heure) -> int:
    local = _a_paris(maintenant)
    if not debut <= local.time() < FIN_CRENEAU:
        return 0
    fin = datetime.combine(local.date(), FIN_CRENEAU, tzinfo=PARIS)
    return math.ceil((fin - local).total_seconds())  # 08:59:59,5 compte encore une seconde


def secondes_avant_ouverture(maintenant: datetime) -> int:
    """0 hors du créneau protégé (8 h à 9 h, Paris) ; sinon les secondes jusqu'à 9 h. Utilisé par le serveur."""
    return _secondes_jusqu_a_9h(maintenant, DEBUT_CRENEAU)


def secondes_avant_livraison(maintenant: datetime, marge_minutes: int = 30) -> int:
    """Le même calcul, créneau élargi vers l'avant (7 h 30 à 9 h par défaut) : utilisé par l'attente dans GitHub,
    pour qu'une livraison ne commence pas son pré-test juste avant 8 h."""
    debut = (datetime.combine(datetime(2000, 1, 1), DEBUT_CRENEAU) - timedelta(minutes=marge_minutes)).time()
    return _secondes_jusqu_a_9h(maintenant, debut)


# --- L'état et ses transitions -------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Version:
    image: str   # empreinte GHCR (ou étiquette locale pour l'image d'août)
    config: str  # dossier de configuration sauvegardé sur le serveur
    profil: str  # liste de contrôles adaptée à la version : « complet » (ou « aout », après l'atelier)
    # Le volume Docker de l'index d'articles de CETTE version (choix A d'Era, 14/10) : un par livraison, rempli et
    # vérifié par le pré-test, puis servi en production ; un retour arrière retrouve exactement le sien.
    index: str


CHAMPS_ETAT = {"active", "precedente", "observee", "sante"}
SANTES = {"sain", "degrade", "indisponible", None}


@dataclass(frozen=True)
class Etat:
    active: Version | None = None
    precedente: Version | None = None
    observee: str | None = None  # image que Docker exécute vraiment, lue à la fin de chaque opération
    sante: str | None = None     # « sain », « degrade » ou « indisponible »


def apres_livraison(etat: Etat, nouvelle: Version) -> Etat:
    return Etat(active=nouvelle, precedente=etat.active)


def apres_retour(etat: Etat) -> Etat:
    if etat.precedente is None:
        raise AucunePrecedente("aucune version précédente validée : retour arrière refusé")
    return Etat(active=etat.precedente, precedente=None)


def _version(valeur) -> Version | None:
    if valeur is None:
        return None
    if not isinstance(valeur, dict) or set(valeur) != {"image", "config", "profil", "index"} \
            or not all(isinstance(v, str) for v in valeur.values()):
        raise EtatIllisible("version mal formée dans le fichier d'état")
    return Version(**valeur)


def lire_etat(chemin: Path) -> Etat:
    """Absent : état vide (aucune livraison encore). Présent mais illisible : `EtatIllisible`, jamais un état vide."""
    if not chemin.exists():
        return Etat()
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as erreur:
        raise EtatIllisible(f"{chemin} illisible : {type(erreur).__name__}") from erreur
    # Les quatre champs sont obligatoires, avec leur type : un champ manquant, en trop ou mal typé ne doit jamais faire
    # passer le fichier pour un état vide (une première livraison) et faire oublier la version active.
    if not isinstance(donnees, dict) or set(donnees) != CHAMPS_ETAT:
        raise EtatIllisible(f"{chemin} : les champs attendus sont {sorted(CHAMPS_ETAT)}")
    if donnees["observee"] is not None and not isinstance(donnees["observee"], str):
        raise EtatIllisible(f"{chemin} : « observee » doit être du texte ou null")
    if not isinstance(donnees["sante"], (str, type(None))) or donnees["sante"] not in SANTES:
        raise EtatIllisible(f"{chemin} : « sante » doit valoir {sorted(s for s in SANTES if s)} ou null")
    return Etat(active=_version(donnees["active"]), precedente=_version(donnees["precedente"]),
                observee=donnees["observee"], sante=donnees["sante"])


def ecrire_etat(chemin: Path, etat: Etat) -> None:
    """Écriture atomique : un fichier temporaire, puis un seul renommage. Le fichier final est entier ou inchangé."""
    temporaire = chemin.with_name(chemin.name + ".tmp")
    try:
        with open(temporaire, "w", encoding="utf-8") as fichier:
            json.dump(asdict(etat), fichier, ensure_ascii=False, indent=2)
            fichier.flush()
            os.fsync(fichier.fileno())
        os.replace(temporaire, chemin)
    finally:
        if temporaire.exists():
            temporaire.unlink()


# --- La marque d'opération et le journal ---------------------------------------------------------------------------

def _marque(dossier: Path) -> Path:
    return dossier / "operation-en-cours.json"


def ouvrir_operation(dossier: Path, ordre: Ordre, maintenant: datetime | None = None) -> None:
    """Pose la marque AVANT toute bascule ; mode « x » : échoue si elle existe déjà, même entre deux processus."""
    quand = (maintenant or datetime.now(PARIS)).isoformat(timespec="seconds")
    try:
        with open(_marque(dossier), "x", encoding="utf-8") as fichier:
            json.dump({"ordre": ordre.nom, "argument": ordre.argument, "debut": quand}, fichier)
    except FileExistsError as erreur:
        raise OperationInachevee("une opération précédente n'a pas été close : vérifier l'état réel") from erreur


def fermer_operation(dossier: Path) -> None:
    _marque(dossier).unlink(missing_ok=True)


def journaliser(dossier: Path, maintenant: datetime | None = None, **champs) -> None:
    """Ajoute une ligne JSON à `journal.jsonl` : on n'y efface ni n'y modifie jamais rien."""
    ligne = {"date": (maintenant or datetime.now(PARIS)).astimezone(PARIS).isoformat(timespec="seconds"), **champs}
    with open(dossier / "journal.jsonl", "a", encoding="utf-8") as fichier:
        fichier.write(json.dumps(ligne, ensure_ascii=False) + "\n")


# --- Le verrou -----------------------------------------------------------------------------------------------------

@contextlib.contextmanager
def prendre_verrou(chemin: Path, attente_max: int):
    """Un seul déploiement ou retour arrière à la fois sur le serveur. Linux seulement (`fcntl`).

    Le verrou est relâché à la fermeture du fichier, y compris après une exception, et il n'est jamais tenu pendant
    une attente horaire (le créneau est refusé avant de le prendre).
    """
    import fcntl

    fichier = open(chemin, "a+")
    try:
        debut = time.monotonic()
        while True:
            try:
                fcntl.flock(fichier, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() - debut >= attente_max:
                    raise VerrouOccupe(f"verrou tenu par une autre opération depuis plus de {attente_max} s")
                time.sleep(1)
        yield
    finally:
        fichier.close()


def empreinte_du_script() -> str:
    """`sha256` de ce fichier : la chaîne la compare à celle du dépôt avant chaque livraison (ordre `version`)."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


# === L'orchestration (tâche 8) ======================================================================================

DOSSIER = Path("/root/rita-deploy")          # état, journal, marque, verrou, configurations, sauvegardes
DEPOT = Path("/root/rita-agent")             # dossier de projet Compose et `.env` du serveur
PROJET_COMPOSE = "rita-agent"                # nom de projet de production : à confirmer sur le serveur (tâche 10)
CONTENEUR = "rita-api-preprod"               # le conteneur de production (nom fixé par docker-compose.yml)
CONTENEUR_PRETEST = "rita-api-pretest"
IMAGE_AOUT = "rita-api:avant-chaine"         # l'image d'août, mise de côté avant la première bascule
PORT_PRODUCTION = 8001
PORT_PRETEST = 8003      # relevé du 14/10 : 8002 est pris sur le serveur par le conteneur `glossary`
URL_PRODUCTION = f"http://127.0.0.1:{PORT_PRODUCTION}"
URL_PRETEST = f"http://127.0.0.1:{PORT_PRETEST}"
VARIABLES_REQUISES = ("RITA_API_KEY", "RITA_DSN_LECTURE")
FICHIERS_COMPOSE = ("docker-compose.yml", "compose.prod.yml")  # embarqués dans l'image ET installés dans bin/

# Délais maximaux, en secondes (relecture du 14/10) : chaque commande Docker et chaque appel HTTP est borné, pour qu'une
# opération qui tient le verrou finisse toujours. Valeurs à ajuster aux durées mesurées à la première livraison.
DELAI_COURT = 60          # inspect, create, cp, rm, logs, volume, run -d, compose config
DELAI_TIRAGE = 600        # docker pull
DELAI_INDEXATION = 900    # indexation de test du pré-test
DELAI_BASCULE = 300       # docker compose up, arrêt de l'ancienne API compris
ECHEANCE_DISPONIBLE = 180  # attente, en tout, que /health réponde après un démarrage
DELAI_SONDE = 5           # un appel /health pendant cette attente
PAUSE_SONDE = 2
DELAI_CONTROLE = 10       # /health, 403, écran
DELAI_BRIEFING = 90       # le briefing appelle le modèle

# Bornes calculées (pas mesurées) des durées, phase par phase ; deux tests rejouent le pire chemin et vérifient
# que la somme des délais réellement demandés reste dessous.
DUREE_MAX_DISPONIBLE = ECHEANCE_DISPONIBLE + DELAI_SONDE + PAUSE_SONDE
DUREE_MAX_CONTROLE = 3 * DELAI_CONTROLE + DELAI_BRIEFING + DELAI_COURT                 # plus `docker logs`
DUREE_MAX_MISE_EN_SERVICE = (DELAI_BASCULE + DELAI_COURT + DUREE_MAX_DISPONIBLE         # bascule, commit, attente
                             + DUREE_MAX_CONTROLE + DELAI_COURT)                       # contrôles, image observée
DUREE_MAX_PRETEST = (DELAI_TIRAGE + 4 * DELAI_COURT + DELAI_COURT                       # pull, extraction, commit
                     + DELAI_COURT + DELAI_INDEXATION + DELAI_COURT                     # config, index, run
                     + DUREE_MAX_DISPONIBLE + DUREE_MAX_CONTROLE + DELAI_COURT)         # attente, contrôles, arrêt
DUREE_MAX_LIVRER = (2 * DELAI_COURT + DUREE_MAX_PRETEST                                 # image d'août, index actif
                    + 2 * DUREE_MAX_MISE_EN_SERVICE + 2 * DELAI_COURT)                  # observée, index candidat
DUREE_MAX_REVENIR = DELAI_COURT + 2 * DUREE_MAX_MISE_EN_SERVICE + DELAI_COURT           # index de la cible
# Le retour d'urgence attend plus longtemps qu'une livraison ne peut durer, et inversement : il n'abandonne jamais.
ATTENTE_VERROU = {"livrer": DUREE_MAX_REVENIR + 60, "revenir": DUREE_MAX_LIVRER + 60}


class ComposeNonInstalle(Exception):
    """Les fichiers Compose de l'image diffèrent de ceux qu'Era a installés sur le serveur : livraison refusée."""


class EnvIllisible(Exception):
    """Une variable de l'environnement de production ne peut pas passer au pré-test : livraison refusée."""


_NOM_DE_VARIABLE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


@dataclass(frozen=True)
class Reponse:
    statut: int
    entetes: dict      # noms en minuscules
    corps: bytes


def requete(methode: str, url: str, entetes: dict | None = None, delai: float = 90) -> Reponse:
    """Un appel HTTP. Un code d'erreur HTTP est une réponse ; une connexion impossible lève `OSError`."""
    demande = urllib.request.Request(url, method=methode, headers=entetes or {})
    try:
        with urllib.request.urlopen(demande, timeout=delai) as reponse:
            return Reponse(reponse.status, {k.lower(): v for k, v in reponse.headers.items()}, reponse.read())
    except urllib.error.HTTPError as erreur:
        return Reponse(erreur.code, {k.lower(): v for k, v in erreur.headers.items()}, erreur.read())


def lire_env(chemin: Path) -> dict[str, str]:
    """Lit le `.env` du serveur (NOM=valeur) ; les valeurs ne sont jamais affichées ni journalisées."""
    valeurs = {}
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        nom, _, valeur = ligne.partition("=")
        valeurs[nom.strip()] = valeur.strip().strip('"').strip("'")
    return valeurs


def env_du_pretest(environnement: dict) -> str:
    """Le fichier d'environnement du pré-test, à partir de l'environnement que Compose donne à l'API de production
    (`Docker.environnement_api`) : le même, valeurs par défaut comprises, sauf ce qui permet d'écrire dans la base
    (`DATABASE_URL`, `POSTGRES_*`) ; sa base, le pré-test la reçoit à part (le compte rita_lecture). Une variable du
    `.env` absente du bloc `environment` de docker-compose.yml n'arrive donc ni à la production, ni au pré-test.
    `docker run --env-file` lit une variable par ligne, sans guillemets : une valeur sur plusieurs lignes lève
    `EnvIllisible`, avec le nom de la variable et jamais sa valeur."""
    lignes = []
    for nom in sorted(environnement):
        valeur = environnement[nom]
        if nom == "DATABASE_URL" or nom.startswith("POSTGRES_") or valeur is None:
            continue
        if not _NOM_DE_VARIABLE.fullmatch(nom) or "\n" in str(valeur) or "\r" in str(valeur):
            raise EnvIllisible(f"{nom} : nom ou valeur impossible a passer au pre-test par docker run --env-file")
        lignes.append(f"{nom}={valeur}")
    return "\n".join(lignes) + "\n"


def _ecrire_secret(chemin: Path, contenu: str) -> None:
    """Écrit un fichier lisible par root seul dès sa création (droits 600), en fins de ligne LF."""
    descripteur = os.open(chemin, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descripteur, "w", encoding="utf-8", newline="\n") as fichier:
        fichier.write(contenu)


class Docker:
    """Les commandes Docker du serveur, toujours en liste d'arguments, jamais par un interpréteur de commandes."""

    def __init__(self, executer=subprocess.run, projet: str = PROJET_COMPOSE, depot: Path = DEPOT):
        self.executer, self.projet, self.depot = executer, projet, depot

    def _lancer(self, args: list[str], env: dict | None = None, delai: float = DELAI_COURT) -> str:
        """Lance une commande qui doit réussir ; au-delà de `delai`, elle est arrêtée et `TimeoutExpired` est levée."""
        return self.executer(args, check=True, capture_output=True, text=True, env=env, timeout=delai).stdout

    def _essayer(self, args: list[str]) -> None:
        """Lance une commande de nettoyage : son échec ou sa lenteur n'interrompt rien."""
        try:
            self.executer(args, check=False, capture_output=True, text=True, timeout=DELAI_COURT)
        except subprocess.TimeoutExpired:
            pass

    def tirer(self, ref: str) -> None:
        self._lancer(["docker", "pull", ref], delai=DELAI_TIRAGE)

    def image_existe(self, ref: str) -> bool:
        try:
            self._lancer(["docker", "image", "inspect", ref])
            return True
        except subprocess.SubprocessError:
            return False

    def commit_de_l_image(self, ref: str) -> str | None:
        sortie = self._lancer(["docker", "image", "inspect", "--format", "{{range .Config.Env}}{{println .}}{{end}}", ref])
        for ligne in sortie.splitlines():
            if ligne.startswith("RITA_GIT_SHA="):
                return ligne.split("=", 1)[1]
        return None

    def image_du_conteneur(self, nom: str) -> str | None:
        try:
            return self._lancer(["docker", "inspect", "--format", "{{.Config.Image}}", nom]).strip() or None
        except subprocess.SubprocessError:
            return None

    def index_existe(self, nom: str) -> bool:
        """Le volume d'index d'une version existe-t-il encore ? Jamais recréé vide : un retour vers une version sans
        son index est refusé."""
        try:
            self._lancer(["docker", "volume", "inspect", nom])
            return True
        except subprocess.SubprocessError:
            return False

    def supprimer_index(self, nom: str) -> None:
        """Supprime l'index d'une candidate refusée. Sans `-f` : un volume encore utilisé n'est jamais retiré."""
        self._essayer(["docker", "volume", "rm", nom])

    def extraire_config(self, ref: str, dossier: Path) -> None:
        """Copie les fichiers Compose embarqués dans l'image : l'empreinte désigne le code ET ces fichiers."""
        temporaire = "rita-extraction-config"
        try:
            self._lancer(["docker", "create", "--name", temporaire, ref])
            for nom in ("docker-compose.yml", "compose.prod.yml"):
                self._lancer(["docker", "cp", f"{temporaire}:/app/deploy/{nom}", str(dossier / nom)])
        finally:
            self._essayer(["docker", "rm", "-f", temporaire])

    def _compose(self, config: Path) -> list[str]:
        """Le début de toute commande Compose de production : projet, dossier, fichiers et `.env` de CETTE version."""
        return ["docker", "compose", "-p", self.projet, "--project-directory", str(self.depot),
                "-f", str(config / "docker-compose.yml"), "-f", str(config / "compose.prod.yml"),
                "--env-file", str(config / ".env")]

    @staticmethod
    def _variables_compose(version: Version) -> dict:
        """Les deux variables lues par compose.prod.yml : l'image par son empreinte, et l'index de CETTE version."""
        return {**os.environ, "RITA_IMAGE": version.image, "RITA_INDEX": version.index}

    def environnement_api(self, version: Version) -> dict:
        """L'environnement que Compose donnera à l'API de production pour cette version (`docker compose config`) :
        seulement les variables du bloc `environment` de docker-compose.yml, valeurs par défaut comprises."""
        sortie = self._lancer([*self._compose(Path(version.config)), "config", "--format", "json"],
                              env=self._variables_compose(version))
        return json.loads(sortie)["services"]["api"]["environment"]

    def demarrer_pretest(self, version: Version, dsn_lecture: str) -> None:
        """La préproduction : compte PostgreSQL en lecture seule, et l'index de la version, rempli ici puis gardé : si le
        pré-test est vert, c'est cet index vérifié que la production utilisera (choix A d'Era, 14/10).
        Le pré-test reçoit l'environnement de la production sans accès en écriture à la base ; le DSN de lecture passe
        par l'environnement de la commande `docker` (`-e DATABASE_URL` sans valeur), jamais par ses arguments."""
        config = Path(version.config)
        fichier_env = config / "pretest.env"
        _ecrire_secret(fichier_env, env_du_pretest(self.environnement_api(version)))
        commun = ["--network", f"{self.projet}_default", "--env-file", str(fichier_env),
                  "-e", "DATABASE_URL",
                  "-v", f"{version.index}:/app/data/chroma",
                  "-v", f"{self.projet}_rita_cache_preprod:/home/rita/.cache"]
        avec_dsn = {**os.environ, "DATABASE_URL": dsn_lecture}
        self._lancer(["docker", "run", "--rm", *commun, version.image,
                      "python", "-m", "pipelines.ingest", "--etapes", "indexation", "--strict"],
                     env=avec_dsn, delai=DELAI_INDEXATION)
        self._lancer(["docker", "run", "-d", "--name", CONTENEUR_PRETEST, *commun,
                      "-p", f"127.0.0.1:{PORT_PRETEST}:8000", version.image], env=avec_dsn)

    def arreter_pretest(self) -> None:
        """Arrête le conteneur d'essai et GARDE l'index : s'il est vérifié, la production s'en servira."""
        self._essayer(["docker", "rm", "-f", CONTENEUR_PRETEST])

    def remplacer_production(self, version: Version) -> None:
        """Remplace l'API seule (`--no-deps` : PostgreSQL n'est pas touché), sur l'image désignée par son empreinte,
        avec la configuration sauvegardée et l'index de CETTE version. compose.prod.yml déclare l'index comme volume
        externe : s'il manque, Compose refuse de démarrer au lieu de créer un index vide."""
        self._lancer([*self._compose(Path(version.config)),
                      "up", "-d", "--no-deps", "--no-build", "--pull", "never", "api"],
                     env=self._variables_compose(version), delai=DELAI_BASCULE)

    def journal_du_conteneur(self, nom: str) -> str:
        try:
            resultat = self.executer(["docker", "logs", "--since", "15m", nom], check=False, capture_output=True,
                                     text=True, timeout=DELAI_COURT)
        except subprocess.TimeoutExpired:
            return ""
        return (resultat.stdout or "") + (resultat.stderr or "")


def preparer_version(docker, ref: str, dossier: Path, source_env: Path, maintenant: datetime) -> Version:
    """Un dossier de configuration UNIQUE par livraison, jamais réécrit : les fichiers Compose de l'image, plus une
    copie du `.env` du serveur à cet instant. L'empreinte de l'image ne désigne donc pas toute la configuration
    effective : le `.env` est sauvegardé à part, pour chaque livraison.
    Les fichiers Compose s'exécutent en root : ceux de l'image doivent être identiques, octet pour octet, à ceux
    qu'Era a installés dans `bin/` à côté du script. Sinon, `ComposeNonInstalle`, avant tout pré-test."""
    cible = dossier / "configs" / f"{maintenant:%Y%m%d-%H%M%S}-{ref.rsplit(':', 1)[-1][:12]}"
    cible.mkdir(parents=True, exist_ok=False)
    docker.extraire_config(ref, cible)
    for nom in FICHIERS_COMPOSE:
        installe, venu = dossier / "bin" / nom, cible / nom
        # Un lien symbolique copié depuis l'image passerait la comparaison, puis sa cible pourrait changer avant la
        # bascule : seul un fichier ordinaire, dans ce dossier créé à l'instant, est accepté.
        if (venu.is_symlink() or not venu.is_file() or not installe.is_file()
                or installe.read_bytes() != venu.read_bytes()):
            raise ComposeNonInstalle(f"{nom} de l'image differe de la copie installee sur le serveur ({installe}) : "
                                     "la relire, puis l'installer a la main (docs/EXPLOITATION.md)")
    shutil.copy2(source_env, cible / ".env")
    os.chmod(cible / ".env", 0o600)
    return Version(ref, str(cible), "complet", f"rita-index-{cible.name}")   # un index par livraison


@dataclass(frozen=True)
class Controle:
    sante: str            # « sain », « degrade » ou « indisponible »
    echecs: tuple = ()    # les contrôles en échec, pour comparer deux versions ; « bascule » si Compose a échoué
    detail: str = ""      # la commande en cause, décrite sans ses arguments


def _json(reponse: Reponse) -> dict:
    try:
        valeur = json.loads(reponse.corps or b"{}")
        return valeur if isinstance(valeur, dict) else {}
    except ValueError:
        return {}


def controler(base: str, cle: str, profil: str, commit_attendu: str | None, journal, http=requete) -> Controle:
    """Les contrôles d'une version. `pretest` : version dans /health, 403 sans clé, un briefing conforme dont le
    X-Request-ID est dans le journal. `complet` (production réelle) : les mêmes, plus l'écran `/briefing.html`.
    Chaque appel a son délai maximal : la durée d'un contrôle est bornée (`DUREE_MAX_CONTROLE`)."""
    try:
        sante = http("GET", f"{base}/health", delai=DELAI_CONTROLE)
    except OSError:
        return Controle("indisponible", ("health",))
    if sante.statut != 200:
        return Controle("indisponible", ("health",))
    echecs = []
    if commit_attendu is not None and _json(sante).get("commit") != commit_attendu:
        echecs.append("version")
    try:
        if http("GET", f"{base}/donnees/valeurs", delai=DELAI_CONTROLE).statut != 403:
            echecs.append("403")
        if profil == "complet" and http("GET", f"{base}/briefing.html", delai=DELAI_CONTROLE).statut != 200:
            echecs.append("ecran")
        briefing = http("POST", f"{base}/briefing?ticker=OR.PA", {"X-API-Key": cle}, delai=DELAI_BRIEFING)
    except OSError:
        return Controle("degrade", tuple(echecs) + ("connexion",))
    corps = _json(briefing)
    if briefing.statut != 200 or not str(corps.get("briefing", "")).strip() or corps.get("conforme_amf") is not True:
        echecs.append("briefing")
    elif f"request_id={briefing.entetes.get('x-request-id', '?')}" not in journal():
        echecs.append("journal")
    # Choix A d'Era (14/10) : un briefing est rédigé même sans article ; seul ce compte rend un index vide visible.
    articles = corps.get("articles_transmis")
    if briefing.statut == 200 and not (isinstance(articles, int) and articles >= 1):
        echecs.append("articles")
    return Controle("sain" if not echecs else "degrade", tuple(echecs))


def attendre_disponible(base: str, http=requete, dormir=time.sleep, echeance: float = ECHEANCE_DISPONIBLE,
                        pause: float = PAUSE_SONDE, horloge=time.monotonic) -> bool:
    """Laisse le temps à l'API de démarrer : des appels courts à /health jusqu'à l'échéance, jamais au-delà. Le nombre
    d'appels est borné lui aussi (échéance divisée par la pause) : l'attente finit même si l'horloge ne bouge pas."""
    fin = horloge() + echeance
    for _ in range(math.ceil(echeance / pause)):
        if horloge() >= fin:
            break
        try:
            if http("GET", f"{base}/health", delai=DELAI_SONDE).statut == 200:
                return True
        except OSError:
            pass
        dormir(pause)
    return False


def _manquantes(env: dict) -> list[str]:
    return [nom for nom in VARIABLES_REQUISES if not env.get(nom)]


def _cle(version: Version) -> str:
    """La clé d'API de CETTE version, lue dans son `.env` sauvegardé : une version ancienne peut avoir une autre clé
    que la configuration actuelle. Fichier absent ou illisible : chaîne vide, et le contrôle du briefing échoue."""
    try:
        return lire_env(Path(version.config) / ".env").get("RITA_API_KEY", "")
    except (OSError, UnicodeDecodeError):
        return ""


def _decrire(erreur: BaseException) -> str:
    """Décrit une erreur sans jamais recopier une commande : ses arguments et sa sortie peuvent porter un secret."""
    if isinstance(erreur, subprocess.TimeoutExpired):
        return f"commande trop longue : {_commande(erreur.cmd)} (plus de {erreur.timeout:g} s)"
    if isinstance(erreur, subprocess.CalledProcessError):
        return f"commande en echec : {_commande(erreur.cmd)} (code {erreur.returncode})"
    return f"{type(erreur).__name__} : {erreur}"


def _commande(cmd) -> str:
    return " ".join(str(mot) for mot in list(cmd)[:2])


# Avant la bascule, la production n'a pas bougé : ces erreurs refusent la livraison proprement, opération fermée.
ERREURS_AVANT_BASCULE = (subprocess.SubprocessError, OSError, ValueError, KeyError, ComposeNonInstalle, EnvIllisible)


def _essai_en_preproduction(version: Version, docker, env: dict, http, dormir) -> Controle:
    """Remplit l'index de la version et la contrôle sur le port du pré-test. Le conteneur d'essai est toujours
    arrêté, même après une erreur ; son index reste, pour la production ou pour être supprimé par l'appelant."""
    try:
        commit = docker.commit_de_l_image(version.image)
        docker.demarrer_pretest(version, env["RITA_DSN_LECTURE"])
        attendre_disponible(URL_PRETEST, http, dormir)
        return controler(URL_PRETEST, _cle(version), "pretest", commit,
                         lambda: docker.journal_du_conteneur(CONTENEUR_PRETEST), http)
    finally:
        docker.arreter_pretest()


def _mettre_en_service(version: Version, docker, http, dormir) -> Controle:
    """Bascule l'API de production sur `version`, puis la contrôle avec SA clé. Si Compose échoue ou dépasse son
    délai, le remplacement a pu commencer : le contrôle vaut « indisponible », et l'appelant relit l'état réel
    (`image_du_conteneur`) puis remet la version du début."""
    try:
        docker.remplacer_production(version)
        commit = docker.commit_de_l_image(version.image)
    except subprocess.SubprocessError as erreur:
        return Controle("indisponible", ("bascule",), _decrire(erreur))
    attendre_disponible(URL_PRODUCTION, http, dormir)
    return controler(URL_PRODUCTION, _cle(version), version.profil, commit,
                     lambda: docker.journal_du_conteneur(CONTENEUR), http)


def _details(**controles: Controle) -> dict:
    return {f"detail_{nom}": controle.detail for nom, controle in controles.items() if controle.detail}


def livrer(ref: str, docker, dossier: Path, env: dict, maintenant, http=requete, dormir=time.sleep,
           source_env: Path | None = None) -> int:
    """Livre une image par son empreinte : pré-test, bascule de l'API, contrôles, retour automatique si échec.
    Spec § 4 (étapes 5 à 8) et § 5.3 ; périmètre de l'atelier § 11 (première livraison sans retour automatique)."""
    chemin = dossier / "etat.json"
    trace = {"operation": "livrer", "vers": ref}
    if _manquantes(env):
        journaliser(dossier, maintenant(), **trace, resultat="refusee",
                    message=f"variable absente du .env du serveur : {', '.join(_manquantes(env))}")
        return 1
    try:
        etat = lire_etat(chemin)
    except EtatIllisible as erreur:
        journaliser(dossier, maintenant(), **trace, resultat="refusee", message=str(erreur))
        return 1
    premiere = etat.active is None
    if premiere and not ((dossier / "sauvegardes" / "avant-chaine").is_dir() and docker.image_existe(IMAGE_AOUT)):
        journaliser(dossier, maintenant(), **trace, resultat="refusee",
                    message="sauvegarde d'aout absente : premiere livraison impossible (tache 10)")
        return 1
    if not premiere and not docker.index_existe(etat.active.index):
        # Sans l'index de l'active, un retour automatique serait impossible : on ne bascule pas.
        journaliser(dossier, maintenant(), **trace, resultat="refusee",
                    message=f"index de la version active absent ({etat.active.index}) : retour automatique impossible")
        return 1

    ouvrir_operation(dossier, Ordre("livrer", ref), maintenant())
    version = None
    try:
        docker.tirer(ref)
        version = preparer_version(docker, ref, dossier, source_env or DEPOT / ".env", maintenant())
        pretest = _essai_en_preproduction(version, docker, env, http, dormir)
    except ERREURS_AVANT_BASCULE as erreur:
        if version is not None:
            docker.supprimer_index(version.index)
        journaliser(dossier, maintenant(), **trace, resultat="refusee", message=_decrire(erreur),
                    observee=docker.image_du_conteneur(CONTENEUR))
        fermer_operation(dossier)
        return 1
    if pretest.sante != "sain":
        docker.supprimer_index(version.index)
        journaliser(dossier, maintenant(), **trace, resultat="refusee au pre-test", echecs=list(pretest.echecs))
        fermer_operation(dossier)
        return 1
    if secondes_avant_ouverture(maintenant()) > 0:  # l'heure relue juste avant la bascule
        docker.supprimer_index(version.index)       # la reprise de 9 h préparera une nouvelle livraison
        journaliser(dossier, maintenant(), **trace, resultat="reportee",
                    message="creneau du matin atteint pendant le pre-test : rien n'a change")
        fermer_operation(dossier)
        return CODE_CRENEAU

    apres = _mettre_en_service(version, docker, http, dormir)
    if apres.sante == "sain":
        nouvel = replace(apres_livraison(etat, version), observee=docker.image_du_conteneur(CONTENEUR), sante="sain")
        ecrire_etat(chemin, nouvel)
        journaliser(dossier, maintenant(), **trace, de=etat.active.image if etat.active else None, resultat="livree")
        fermer_operation(dossier)
        return 0

    if premiere:  # exception de l'atelier : pas de retour automatique vers l'image d'août
        ecrire_etat(chemin, Etat(observee=docker.image_du_conteneur(CONTENEUR), sante=apres.sante))
        journaliser(dossier, maintenant(), **trace, resultat="echec apres bascule", echecs=list(apres.echecs),
                    message="restauration manuelle d'aout requise (procedure de docs/EXPLOITATION.md)",
                    **_details(bascule=apres))
        fermer_operation(dossier)
        return 1

    # Retour automatique : la version ACTIVE AU DÉBUT de l'opération, avec sa configuration (jamais la précédente).
    restaure = _mettre_en_service(etat.active, docker, http, dormir)
    ecrire_etat(chemin, replace(etat, observee=docker.image_du_conteneur(CONTENEUR), sante=restaure.sante))
    if restaure.sante == "sain":
        resultat, message = "livraison refusee, version active du debut restauree", ""
    else:
        resultat, message = "restauration en echec, intervention necessaire", ""
        if set(apres.echecs) & set(restaure.echecs):
            message = "cause externe possible (modele, base) ou configuration commune incorrecte, a diagnostiquer"
    if restaure.sante == "sain":
        docker.supprimer_index(version.index)       # la candidate n'est plus servie : son index ne sert plus
    journaliser(dossier, maintenant(), **trace, de=etat.active.image, resultat=resultat, message=message,
                echecs=list(apres.echecs), echecs_restauration=list(restaure.echecs),
                **_details(bascule=apres, restauration=restaure))
    fermer_operation(dossier)
    return 1


def revenir(numero: str, docker, dossier: Path, env: dict, maintenant, http=requete, dormir=time.sleep) -> int:
    """Retour arrière manuel vers la précédente validée, à toute heure. S'il échoue, l'active du début revient."""
    chemin = dossier / "etat.json"
    trace = {"operation": "revenir", "passage": numero}
    if _manquantes(env):
        journaliser(dossier, maintenant(), **trace, resultat="refuse",
                    message=f"variable absente du .env du serveur : {', '.join(_manquantes(env))}")
        return 1
    try:
        etat = lire_etat(chemin)
    except EtatIllisible as erreur:
        journaliser(dossier, maintenant(), **trace, resultat="refuse", message=str(erreur))
        return 1
    if etat.active is None or etat.precedente is None:
        journaliser(dossier, maintenant(), **trace, resultat="refuse : aucune version precedente")
        return 1
    if not docker.index_existe(etat.precedente.index):
        journaliser(dossier, maintenant(), **trace, resultat="refuse",
                    message=f"index de la version precedente absent ({etat.precedente.index}) : jamais recree vide")
        return 1

    ouvrir_operation(dossier, Ordre("revenir", numero), maintenant())
    depart, cible = etat.active, etat.precedente
    controle = _mettre_en_service(cible, docker, http, dormir)
    if controle.sante == "sain":
        ecrire_etat(chemin, replace(apres_retour(etat), observee=docker.image_du_conteneur(CONTENEUR), sante="sain"))
        journaliser(dossier, maintenant(), **trace, de=depart.image, vers=cible.image, resultat="retour arriere")
        fermer_operation(dossier)
        return 0

    remise = _mettre_en_service(depart, docker, http, dormir)
    ecrire_etat(chemin, replace(etat, observee=docker.image_du_conteneur(CONTENEUR), sante=remise.sante))
    journaliser(dossier, maintenant(), **trace, de=depart.image, vers=cible.image, resultat="retour refuse",
                echecs=list(controle.echecs), echecs_remise=list(remise.echecs),
                **_details(bascule=controle, remise=remise))
    fermer_operation(dossier)
    return 1


def main(environ=None, docker=None, dossier: Path = DOSSIER, maintenant=None, http=requete,
         verrou=prendre_verrou, dormir=time.sleep, source_env: Path | None = None) -> int:
    """Point d'entrée de la clé SSH à commande forcée. Ordre : analyser l'ordre ; pour `livrer`, refuser le créneau
    AVANT tout verrou ; prendre le verrou ; exécuter ; l'heure est relue juste avant la bascule."""
    environ = os.environ if environ is None else environ
    maintenant = maintenant or (lambda: datetime.now(PARIS))
    try:
        ordre = analyser_ordre(environ.get("SSH_ORIGINAL_COMMAND", ""))
    except OrdreRefuse as erreur:
        print(erreur, file=sys.stderr)
        return 2
    if ordre.nom == "version":
        print(empreinte_du_script())
        return 0
    if ordre.nom == "livrer" and secondes_avant_ouverture(maintenant()) > 0:
        print("livraison reportee : creneau du matin (8 h a 9 h, heure de Paris), rien n'a change")
        return CODE_CRENEAU

    source_env = source_env or DEPOT / ".env"
    env = lire_env(source_env)
    docker = docker or Docker()
    try:
        with verrou(dossier / "verrou", attente_max=ATTENTE_VERROU[ordre.nom]):
            if ordre.nom == "livrer":
                code = livrer(ordre.argument, docker, dossier, env, maintenant, http, dormir, source_env)
            else:
                code = revenir(ordre.argument, docker, dossier, env, maintenant, http, dormir)
    except VerrouOccupe as erreur:
        print(erreur, file=sys.stderr)
        return 1
    except OperationInachevee as erreur:
        journaliser(dossier, maintenant(), operation=ordre.nom, resultat="refusee : operation inachevee",
                    observee=docker.image_du_conteneur(CONTENEUR))
        print(erreur, file=sys.stderr)
        return 1
    except subprocess.SubprocessError as erreur:
        # Dernier filet : le message de cette erreur recopie toute la commande, secrets compris, et la sortie d'erreur
        # part par SSH jusqu'au journal de GitHub. Seuls le nom de la commande et son code (ou son délai) sortent ;
        # une marque d'opération ouverte le reste, et l'opération suivante vérifiera l'état réel.
        journaliser(dossier, maintenant(), operation=ordre.nom, resultat="interrompue", message=_decrire(erreur))
        print(f"{_decrire(erreur)} ; operation interrompue, voir journal.jsonl", file=sys.stderr)
        return 1
    print({0: "operation reussie", CODE_CRENEAU: "livraison reportee par le creneau du matin"}.get(
        code, "operation refusee ou en echec : voir journal.jsonl sur le serveur"))
    return code


if __name__ == "__main__":
    sys.exit(main())
