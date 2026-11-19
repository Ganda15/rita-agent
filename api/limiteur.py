"""La limite de débit de `/briefing` et `/question` (sprint 4, tâche C3 ; décision D6, spec CA1.4).

Annoncée pour le sprint 4 par le plan du sprint 1 (« débit, refus journalisés »). Ces deux routes appellent le modèle :
un seul compteur, partagé, protège le coût et le service. Fenêtre glissante : on compte les appels acceptés pendant les
`fenetre_s` dernières secondes. Un verrou rend le compte juste quand plusieurs appels arrivent en même temps (FastAPI
sert les routes synchrones dans un groupe de fils d'exécution).

Pourquoi en mémoire, et pas `slowapi` : un seul compteur ne justifie pas une dépendance de plus. Condition vérifiée le
20/10/2026 sur le serveur : la production tourne avec un seul processus `uvicorn` ; plusieurs processus auraient chacun
leur compteur, et il faudrait alors un stockage partagé, avec `slowapi` comme avec ce module. Limite écrite : le
compteur repart à zéro à chaque redémarrage.

Le quota se règle par la variable `RITA_QUOTA_PAR_MINUTE` (10 par défaut), lue dans l'environnement ou dans le `.env`
du dépôt. Le module charge ce `.env` lui-même, comme `sources/database.py` : il ne dépend pas de l'ordre des imports
d'`api/main.py` (revue Codex de la PR #111, 20/10/2026). En production, la variable n'est pas transmise au conteneur
(absente du bloc `environment` de `docker-compose.yml`) : le quota y vaut 10.
"""
import logging
import math
import os
import threading
import time
from collections import OrderedDict, deque
from collections.abc import Callable
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

TEXTE_REFUS = "Trop de demandes en peu de temps. Réessayez dans une minute."


class Limiteur:
    """Au plus `quota` appels acceptés par fenêtre glissante de `fenetre_s` secondes."""

    def __init__(self, quota: int, fenetre_s: float = 60.0, horloge: Callable[[], float] = time.monotonic):
        if quota < 1:
            raise ValueError(f"quota invalide : {quota!r}, au moins 1")
        self.quota, self.fenetre_s, self._horloge = quota, fenetre_s, horloge
        self._acceptes: deque[float] = deque()
        self._verrou = threading.Lock()

    def autoriser(self) -> tuple[bool, int]:
        """(accepté, secondes avant qu'une place se libère). Un appel refusé ne compte pas dans le quota."""
        with self._verrou:
            maintenant = self._horloge()
            while self._acceptes and self._acceptes[0] <= maintenant - self.fenetre_s:
                self._acceptes.popleft()
            if len(self._acceptes) < self.quota:
                self._acceptes.append(maintenant)
                return True, 0
            return False, max(1, math.ceil(self._acceptes[0] + self.fenetre_s - maintenant))


load_dotenv(Path(__file__).resolve().parent.parent / ".env")
LIMITEUR = Limiteur(int(os.environ.get("RITA_QUOTA_PAR_MINUTE", "10")))


def limiter_debit(request: Request) -> None:
    """Dépendance FastAPI, placée APRÈS la vérification de la clé : un appel sans clé valide ne consomme pas le quota.

    Au-delà du quota : 429, en-tête `Retry-After`, un refus poli, et une ligne de journal avec l'identifiant de requête
    et la route.
    """
    accepte, attente = LIMITEUR.autoriser()
    if accepte:
        return
    # Import au moment de l'appel : api.main importe ce module, l'inverse au chargement serait circulaire.
    from api.main import request_id_courant

    logger.warning("limite de debit atteinte : request_id=%s route=%s quota=%d", request_id_courant(),
                   request.url.path, LIMITEUR.quota)
    raise HTTPException(status_code=429, headers={"Retry-After": str(attente)},
                        detail={"statut": "refus", "motif": "LIMITE_DE_DEBIT", "texte": TEXTE_REFUS})


# --- Le frein des essais de clé (constat S3, carte #75 point 4 ; plan validé par Era le 07/11/2026) -------------------
# Rien ne freinait les essais de clé. La clé de production est longue : la deviner n'est pas réaliste ; le risque réel
# est un flot d'essais qui remplit le journal et occupe le service (OWASP API4:2023). Par adresse, pas un compteur pour
# tous : un compteur unique laisserait n'importe qui bloquer Era en envoyant de fausses clés.
#
# L'adresse est celle que voit l'API. Derrière Caddy, `uvicorn` la lit dans `X-Forwarded-For` parce que le service
# `api` reçoit `FORWARDED_ALLOW_IPS` (docker-compose.yml) ; c'est sûr seulement parce que le port n'écoute que la
# machine (`127.0.0.1:8001`, tests/test_port_api_local.py). Donnée personnelle : en mémoire seulement, jamais écrite
# dans le journal ; les clés refusées sont comptées sur une fenêtre de 15 minutes, et une adresse est oubliée à son
# prochain appel après la fenêtre, au-delà de 10 000 adresses suivies, ou au redémarrage (registre RGPD, T9).

TEXTE_TROP_D_ESSAIS = "Trop de clés refusées depuis cette adresse. Réessayez dans quelques minutes."


class FreinDesEssais:
    """Au-delà de `seuil` mauvaises clés depuis une adresse, sur une fenêtre glissante de `fenetre_s` secondes, l'adresse
    est bloquée jusqu'à ce que le plus ancien échec sorte de la fenêtre. Au plus `max_adresses` adresses suivies : au-delà,
    la plus anciennement vue est oubliée (un flot d'adresses ne fait pas grossir la mémoire sans fin)."""

    def __init__(self, seuil: int = 10, fenetre_s: float = 900.0, max_adresses: int = 10_000,
                 horloge: Callable[[], float] = time.monotonic):
        if seuil < 1:
            raise ValueError(f"seuil invalide : {seuil!r}, au moins 1")
        self.seuil, self.fenetre_s, self.max_adresses, self._horloge = seuil, fenetre_s, max_adresses, horloge
        self._echecs: OrderedDict[str, deque[float]] = OrderedDict()
        self._verrou = threading.Lock()

    def __len__(self) -> int:
        return len(self._echecs)

    def _recents(self, adresse: str, maintenant: float) -> deque[float] | None:
        """Les échecs encore dans la fenêtre ; l'adresse est oubliée quand il n'en reste aucun."""
        echecs = self._echecs.get(adresse)
        if echecs is None:
            return None
        while echecs and echecs[0] <= maintenant - self.fenetre_s:
            echecs.popleft()
        if not echecs:
            del self._echecs[adresse]
            return None
        return echecs

    def bloquee(self, adresse: str) -> tuple[bool, int]:
        """(bloquée, secondes avant que l'adresse repasse)."""
        with self._verrou:
            maintenant = self._horloge()
            echecs = self._recents(adresse, maintenant)
            if echecs is None or len(echecs) < self.seuil:
                return False, 0
            return True, max(1, math.ceil(echecs[-self.seuil] + self.fenetre_s - maintenant))

    def noter_echec(self, adresse: str) -> bool:
        """Compte une mauvaise clé. Vrai seulement pour l'échec qui fait franchir le seuil : une ligne par blocage."""
        with self._verrou:
            maintenant = self._horloge()
            echecs = self._recents(adresse, maintenant)
            if echecs is None:
                echecs = self._echecs[adresse] = deque()
            echecs.append(maintenant)
            self._echecs.move_to_end(adresse)
            while len(self._echecs) > self.max_adresses:
                self._echecs.popitem(last=False)
            return len(echecs) == self.seuil


def frein_depuis_l_environnement() -> FreinDesEssais:
    """Le seuil se règle par `RITA_ESSAIS_DE_CLE_MAX` (10 par défaut), transmise au conteneur par docker-compose.yml :
    sur l'écran Portefeuille, une clé mal tapée part dans trois appels à la fois et compte donc trois fois."""
    return FreinDesEssais(seuil=int(os.environ.get("RITA_ESSAIS_DE_CLE_MAX", "10")))


FREIN = frein_depuis_l_environnement()


def adresse_du_client(request: Request) -> str:
    return request.client.host if request.client else "inconnue"


def refuser_si_bloquee(request: Request) -> None:
    """Appelé AVANT la comparaison de la clé : une adresse bloquée reçoit 429, quelle que soit la clé envoyée."""
    bloquee, attente = FREIN.bloquee(adresse_du_client(request))
    if bloquee:
        raise HTTPException(status_code=429, headers={"Retry-After": str(attente)},
                            detail={"statut": "refus", "motif": "TROP_D_ESSAIS", "texte": TEXTE_TROP_D_ESSAIS})


def noter_mauvaise_cle(request: Request) -> None:
    """Appelé quand une clé PRÉSENTE est fausse. Une seule ligne de journal par blocage, sans clé ni adresse."""
    if FREIN.noter_echec(adresse_du_client(request)):
        from api.main import request_id_courant   # même raison que dans `limiter_debit`

        logger.warning("essais de cle bloques : request_id=%s route=%s seuil=%d fenetre=%ds", request_id_courant(),
                       request.url.path, FREIN.seuil, int(FREIN.fenetre_s))
