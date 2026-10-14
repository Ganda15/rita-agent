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
    if not isinstance(valeur, dict) or set(valeur) != {"image", "config", "profil"} \
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
VOLUME_INDEX_PRETEST = "rita-index-pretest"  # index Chroma propre au pré-test, jeté après
IMAGE_AOUT = "rita-api:avant-chaine"         # l'image d'août, mise de côté avant la première bascule
PORT_PRODUCTION = 8001
PORT_PRETEST = 8002
URL_PRODUCTION = f"http://127.0.0.1:{PORT_PRODUCTION}"
URL_PRETEST = f"http://127.0.0.1:{PORT_PRETEST}"
VARIABLES_REQUISES = ("RITA_API_KEY", "RITA_DSN_LECTURE")


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


class Docker:
    """Les commandes Docker du serveur, toujours en liste d'arguments, jamais par un interpréteur de commandes."""

    def __init__(self, executer=subprocess.run, projet: str = PROJET_COMPOSE, depot: Path = DEPOT):
        self.executer, self.projet, self.depot = executer, projet, depot

    def _lancer(self, args: list[str], env: dict | None = None) -> str:
        return self.executer(args, check=True, capture_output=True, text=True, env=env).stdout

    def _essayer(self, args: list[str]) -> None:
        self.executer(args, check=False, capture_output=True, text=True)

    def tirer(self, ref: str) -> None:
        self._lancer(["docker", "pull", ref])

    def image_existe(self, ref: str) -> bool:
        try:
            self._lancer(["docker", "image", "inspect", ref])
            return True
        except subprocess.CalledProcessError:
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
        except subprocess.CalledProcessError:
            return None

    def extraire_config(self, ref: str, dossier: Path) -> None:
        """Copie les fichiers Compose embarqués dans l'image : l'empreinte désigne le code ET ces fichiers."""
        temporaire = "rita-extraction-config"
        try:
            self._lancer(["docker", "create", "--name", temporaire, ref])
            for nom in ("docker-compose.yml", "compose.prod.yml"):
                self._lancer(["docker", "cp", f"{temporaire}:/app/deploy/{nom}", str(dossier / nom)])
        finally:
            self._essayer(["docker", "rm", "-f", temporaire])

    def demarrer_pretest(self, ref: str, config: Path, dsn_lecture: str) -> None:
        """La préproduction : compte PostgreSQL en lecture seule, index Chroma construit pour l'essai puis jeté."""
        commun = ["--network", f"{self.projet}_default", "--env-file", str(config / ".env"),
                  "-e", f"DATABASE_URL={dsn_lecture}",
                  "-v", f"{VOLUME_INDEX_PRETEST}:/app/data/chroma",
                  "-v", f"{self.projet}_rita_cache_preprod:/home/rita/.cache"]
        self._essayer(["docker", "volume", "rm", "-f", VOLUME_INDEX_PRETEST])
        self._lancer(["docker", "run", "--rm", *commun, ref,
                      "python", "-m", "pipelines.ingest", "--etapes", "indexation", "--strict"])
        self._lancer(["docker", "run", "-d", "--name", CONTENEUR_PRETEST, *commun,
                      "-p", f"127.0.0.1:{PORT_PRETEST}:8000", ref])

    def arreter_pretest(self) -> None:
        self._essayer(["docker", "rm", "-f", CONTENEUR_PRETEST])
        self._essayer(["docker", "volume", "rm", "-f", VOLUME_INDEX_PRETEST])

    def remplacer_production(self, version: Version) -> None:
        """Remplace l'API seule (`--no-deps` : PostgreSQL n'est pas touché), sur l'image désignée par son empreinte,
        avec la configuration sauvegardée de CETTE version."""
        config = Path(version.config)
        self._lancer(["docker", "compose", "-p", self.projet, "--project-directory", str(self.depot),
                      "-f", str(config / "docker-compose.yml"), "-f", str(config / "compose.prod.yml"),
                      "--env-file", str(config / ".env"),
                      "up", "-d", "--no-deps", "--no-build", "--pull", "never", "api"],
                     env={**os.environ, "RITA_IMAGE": version.image})

    def journal_du_conteneur(self, nom: str) -> str:
        resultat = self.executer(["docker", "logs", "--since", "15m", nom], check=False, capture_output=True, text=True)
        return (resultat.stdout or "") + (resultat.stderr or "")


def preparer_version(docker, ref: str, dossier: Path, source_env: Path, maintenant: datetime) -> Version:
    """Un dossier de configuration UNIQUE par livraison, jamais réécrit : les fichiers Compose de l'image, plus une
    copie du `.env` du serveur à cet instant. L'empreinte de l'image ne désigne donc pas toute la configuration
    effective : le `.env` est sauvegardé à part, pour chaque livraison."""
    cible = dossier / "configs" / f"{maintenant:%Y%m%d-%H%M%S}-{ref.rsplit(':', 1)[-1][:12]}"
    cible.mkdir(parents=True, exist_ok=False)
    docker.extraire_config(ref, cible)
    shutil.copy2(source_env, cible / ".env")
    os.chmod(cible / ".env", 0o600)
    return Version(ref, str(cible), "complet")


@dataclass(frozen=True)
class Controle:
    sante: str            # « sain », « degrade » ou « indisponible »
    echecs: tuple = ()    # les contrôles en échec, pour comparer deux versions


def _json(reponse: Reponse) -> dict:
    try:
        valeur = json.loads(reponse.corps or b"{}")
        return valeur if isinstance(valeur, dict) else {}
    except ValueError:
        return {}


def controler(base: str, cle: str, profil: str, commit_attendu: str | None, journal, http=requete) -> Controle:
    """Les contrôles d'une version. `pretest` : version dans /health, 403 sans clé, un briefing conforme dont le
    X-Request-ID est dans le journal. `complet` (production réelle) : les mêmes, plus l'écran `/briefing.html`."""
    try:
        sante = http("GET", f"{base}/health")
    except OSError:
        return Controle("indisponible", ("health",))
    if sante.statut != 200:
        return Controle("indisponible", ("health",))
    echecs = []
    if commit_attendu is not None and _json(sante).get("commit") != commit_attendu:
        echecs.append("version")
    try:
        if http("GET", f"{base}/donnees/valeurs").statut != 403:
            echecs.append("403")
        if profil == "complet" and http("GET", f"{base}/briefing.html").statut != 200:
            echecs.append("ecran")
        briefing = http("POST", f"{base}/briefing?ticker=OR.PA", {"X-API-Key": cle})
    except OSError:
        return Controle("degrade", tuple(echecs) + ("connexion",))
    corps = _json(briefing)
    if briefing.statut != 200 or not str(corps.get("briefing", "")).strip() or corps.get("conforme_amf") is not True:
        echecs.append("briefing")
    elif f"request_id={briefing.entetes.get('x-request-id', '?')}" not in journal():
        echecs.append("journal")
    return Controle("sain" if not echecs else "degrade", tuple(echecs))


def attendre_disponible(base: str, http=requete, dormir=time.sleep, essais: int = 30, pause: float = 2) -> bool:
    """Laisse le temps à l'API de démarrer : jusqu'à `essais` appels à /health."""
    for _ in range(essais):
        try:
            if http("GET", f"{base}/health").statut == 200:
                return True
        except OSError:
            pass
        dormir(pause)
    return False


def _manquantes(env: dict) -> list[str]:
    return [nom for nom in VARIABLES_REQUISES if not env.get(nom)]


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

    ouvrir_operation(dossier, Ordre("livrer", ref), maintenant())
    try:
        docker.tirer(ref)
        version = preparer_version(docker, ref, dossier, source_env or DEPOT / ".env", maintenant())
        commit = docker.commit_de_l_image(ref)
        docker.demarrer_pretest(ref, Path(version.config), env["RITA_DSN_LECTURE"])
        attendre_disponible(URL_PRETEST, http, dormir)
        pretest = controler(URL_PRETEST, env["RITA_API_KEY"], "pretest", commit,
                            lambda: docker.journal_du_conteneur(CONTENEUR_PRETEST), http)
    finally:
        docker.arreter_pretest()
    if pretest.sante != "sain":
        journaliser(dossier, maintenant(), **trace, resultat="refusee au pre-test", echecs=list(pretest.echecs))
        fermer_operation(dossier)
        return 1
    if secondes_avant_ouverture(maintenant()) > 0:  # l'heure relue juste avant la bascule
        journaliser(dossier, maintenant(), **trace, resultat="reportee",
                    message="creneau du matin atteint pendant le pre-test : rien n'a change")
        fermer_operation(dossier)
        return CODE_CRENEAU

    docker.remplacer_production(version)
    attendre_disponible(URL_PRODUCTION, http, dormir)
    apres = controler(URL_PRODUCTION, env["RITA_API_KEY"], "complet", commit,
                      lambda: docker.journal_du_conteneur(CONTENEUR), http)
    if apres.sante == "sain":
        nouvel = replace(apres_livraison(etat, version), observee=docker.image_du_conteneur(CONTENEUR), sante="sain")
        ecrire_etat(chemin, nouvel)
        journaliser(dossier, maintenant(), **trace, de=etat.active.image if etat.active else None, resultat="livree")
        fermer_operation(dossier)
        return 0

    if premiere:  # exception de l'atelier : pas de retour automatique vers l'image d'août
        ecrire_etat(chemin, Etat(observee=docker.image_du_conteneur(CONTENEUR), sante=apres.sante))
        journaliser(dossier, maintenant(), **trace, resultat="echec apres bascule", echecs=list(apres.echecs),
                    message="restauration manuelle d'aout requise (procedure de docs/EXPLOITATION.md)")
        fermer_operation(dossier)
        return 1

    # Retour automatique : la version ACTIVE AU DÉBUT de l'opération, avec sa configuration (jamais la précédente).
    docker.remplacer_production(etat.active)
    attendre_disponible(URL_PRODUCTION, http, dormir)
    restaure = controler(URL_PRODUCTION, env["RITA_API_KEY"], etat.active.profil,
                         docker.commit_de_l_image(etat.active.image),
                         lambda: docker.journal_du_conteneur(CONTENEUR), http)
    ecrire_etat(chemin, replace(etat, observee=docker.image_du_conteneur(CONTENEUR), sante=restaure.sante))
    if restaure.sante == "sain":
        resultat, message = "livraison refusee, version active du debut restauree", ""
    else:
        resultat, message = "restauration en echec, intervention necessaire", ""
        if set(apres.echecs) & set(restaure.echecs):
            message = "cause externe possible (modele, base) ou configuration commune incorrecte, a diagnostiquer"
    journaliser(dossier, maintenant(), **trace, de=etat.active.image, resultat=resultat, message=message,
                echecs=list(apres.echecs), echecs_restauration=list(restaure.echecs))
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

    ouvrir_operation(dossier, Ordre("revenir", numero), maintenant())
    depart, cible = etat.active, etat.precedente
    docker.remplacer_production(cible)
    attendre_disponible(URL_PRODUCTION, http, dormir)
    controle = controler(URL_PRODUCTION, env["RITA_API_KEY"], cible.profil, docker.commit_de_l_image(cible.image),
                         lambda: docker.journal_du_conteneur(CONTENEUR), http)
    if controle.sante == "sain":
        ecrire_etat(chemin, replace(apres_retour(etat), observee=docker.image_du_conteneur(CONTENEUR), sante="sain"))
        journaliser(dossier, maintenant(), **trace, de=depart.image, vers=cible.image, resultat="retour arriere")
        fermer_operation(dossier)
        return 0

    docker.remplacer_production(depart)
    attendre_disponible(URL_PRODUCTION, http, dormir)
    remise = controler(URL_PRODUCTION, env["RITA_API_KEY"], depart.profil, docker.commit_de_l_image(depart.image),
                       lambda: docker.journal_du_conteneur(CONTENEUR), http)
    ecrire_etat(chemin, replace(etat, observee=docker.image_du_conteneur(CONTENEUR), sante=remise.sante))
    journaliser(dossier, maintenant(), **trace, de=depart.image, vers=cible.image, resultat="retour refuse",
                echecs=list(controle.echecs))
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
        with verrou(dossier / "verrou", attente_max=600 if ordre.nom == "livrer" else 900):
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
    print({0: "operation reussie", CODE_CRENEAU: "livraison reportee par le creneau du matin"}.get(
        code, "operation refusee ou en echec : voir journal.jsonl sur le serveur"))
    return code


if __name__ == "__main__":
    sys.exit(main())
