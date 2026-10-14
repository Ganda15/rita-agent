"""Script du serveur de RITA (sprint 2) : livrer une image testée et revenir à la version précédente.

Installé par Era dans `/root/rita-deploy/bin/` ; lancé seulement par la clé SSH dédiée, à commande forcée, via
`deploy/deployer.sh`. Bibliothèque standard seulement : le serveur n'a rien d'autre à installer.

Cette partie (tâche 7) ne contient que les RÈGLES, sans Docker ni réseau :
- calculs purs : analyse des ordres, créneau du matin, transitions d'état ;
- opérations sur fichiers : état, journal, marque d'opération, verrou.
L'orchestration (livrer, revenir, contrôles) vient à la tâche 8. Conception : `docs/CHAINE-V1.md` § 4 et § 5.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import math
import os
import re
import time
from dataclasses import asdict, dataclass
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
    if not isinstance(donnees, dict):
        raise EtatIllisible(f"{chemin} : un objet JSON était attendu")
    return Etat(active=_version(donnees.get("active")), precedente=_version(donnees.get("precedente")),
                observee=donnees.get("observee"), sante=donnees.get("sante"))


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
