"""La limite de débit de `/briefing` et `/question` (sprint 4, tâche C3 ; décision D6, spec CA1.4).

Annoncée pour le sprint 4 par le plan du sprint 1 (« débit, refus journalisés »). Ces deux routes appellent le modèle :
un seul compteur, partagé, protège le coût et le service. Fenêtre glissante : on compte les appels acceptés pendant les
`fenetre_s` dernières secondes. Un verrou rend le compte juste quand plusieurs appels arrivent en même temps (FastAPI
sert les routes synchrones dans un groupe de fils d'exécution).

Pourquoi en mémoire, et pas `slowapi` : un seul compteur ne justifie pas une dépendance de plus. Condition vérifiée le
20/10/2026 sur le serveur : la production tourne avec un seul processus `uvicorn` ; plusieurs processus auraient chacun
leur compteur, et il faudrait alors un stockage partagé, avec `slowapi` comme avec ce module. Limite écrite : le
compteur repart à zéro à chaque redémarrage.

Le quota se règle par la variable `RITA_QUOTA_PAR_MINUTE` (10 par défaut).
"""
import logging
import math
import os
import threading
import time
from collections import deque
from collections.abc import Callable

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
