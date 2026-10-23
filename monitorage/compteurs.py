"""Les compteurs de la vigie : ce que deviennent les appels à `/question` et `/briefing` (sprint 5, étape 1).

Plan du sprint 5, § 2 « Mesures » et « Ce qu'on compte ». Livrable : E5 (C20, surveiller).

## Ce qu'on compte

Une **observation** par appel : la route, la catégorie, le motif, la durée et les jetons. Jamais de texte : ni la
question, ni la réponse, ni un message d'erreur (règle D2 des journaux, D9 des traces).

La catégorie est le **résultat métier**, pas le code HTTP : `/question` refuse en HTTP 200 (une question hors corpus
n'est pas une panne). Six catégories :

    reponse              une réponse, ou un briefing diffusé
    refus_securite       un garde-fou a joué : détournement, conseil demandé, fuite, sortie non conforme
    refus_corpus         rien dans les articles : hors corpus, abstention du modèle
    refus_qualite        la réponse du modèle n'était pas fiable : citations, nombres
    erreur_technique     le service n'a pas pu répondre : 5xx, fournisseur, erreur imprévue
    rejet_acces_saisie   l'appel n'est jamais entré : 403 (clé), 422 (saisie), 429 (débit)

Un motif inconnu compte comme `erreur_technique`, avec une ligne de journal : il veut dire que le code a changé sans
que la vigie le sache, et une mesure inconnue n'est jamais verte.

## Pourquoi en mémoire, et pourquoi un verrou

Même choix que le limiteur de débit (`api/limiteur.py`) : la production sert l'API avec un seul processus `uvicorn`,
donc un seul jeu de compteurs. Mais les routes sont des fonctions synchrones : FastAPI les sert dans plusieurs fils
d'exécution en même temps. Oublier les anciennes observations, puis ajouter la nouvelle, sont deux opérations : sans
verrou, deux appels simultanés pourraient se marcher dessus.

## Deux bornes, et deux files

On oublie ce qui a plus de 24 h, et on garde au plus 20 000 observations : les rejets 403 et 422 ne passent pas par le
quota de débit, donc la durée seule ne borne pas la mémoire. `debut()` dit depuis quand la période est complète : le
démarrage tant que rien n'est oublié, puis l'heure de la dernière observation oubliée (« mesures depuis HH:MM »).
Limite écrite : tout repart à zéro au redémarrage.

Les rejets ont leur **propre file**, avec son propre plafond (revue de sécurité du commit d8232b4, 22/10/2026) : un 403
ne demande aucune clé et ne passe pas par le quota. Dans une file commune, 20 000 appels sans clé effaceraient les refus
de sécurité et les erreurs déjà comptés, donc cacheraient une attaque à la vigie. Un flot de rejets reste visible (il
remplit sa file), il n'efface plus rien d'autre. `debut()` vaut pour les résultats, `debut_rejets()` pour les rejets.

## Les jetons de toutes les tentatives

Le coût se calcule plus tard, à partir des jetons (étape 3, `monitorage/prix.json`). Ici, chaque route ouvre un
compteur de consommation (`debuter_consommation`), et `src/llm.py` y ajoute les jetons de chaque tentative qui en rend.
Le compteur est un objet modifiable rangé dans une variable de contexte : un fil lancé par la route (le graphe du
briefing) reçoit une copie du contexte, mais le même objet, donc ses jetons comptent aussi.
"""
from __future__ import annotations

import contextvars
import heapq
import logging
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from operator import attrgetter

logger = logging.getLogger(__name__)

CATEGORIES = ("reponse", "refus_securite", "refus_corpus", "refus_qualite", "erreur_technique", "rejet_acces_saisie")
DUREE_DE_VIE_S = 24 * 3600
PLAFOND = 20_000
ROUTES_MESUREES = ("/question", "/briefing")
CODES_DE_REJET = frozenset({403, 422, 429})

MOTIFS_SECURITE = frozenset({"TENTATIVE_DETOURNEMENT", "INTENTION_INTERDITE", "FUITE_BLOQUEE", "SORTIE_NON_CONFORME"})
MOTIFS_CORPUS = frozenset({"OUT_OF_CORPUS", "ABSTENTION"})
MOTIFS_QUALITE = frozenset({"CITATIONS_INVALIDES", "NOMBRE_NON_SOURCE"})


@dataclass(frozen=True)
class Observation:
    """Un appel mesuré. Aucun champ ne porte de texte saisi ou produit."""

    horodatage: float
    route: str
    categorie: str
    motif: str
    duree_ms: int
    jetons_entree: int
    jetons_sortie: int


def categorie(code_http: int, statut: str | None, motif: str | None) -> str:
    """La catégorie d'un appel, à partir de son code HTTP et de son résultat métier."""
    if code_http in CODES_DE_REJET:
        return "rejet_acces_saisie"
    if code_http >= 500 or statut == "erreur":
        return "erreur_technique"
    if statut == "reponse":
        return "reponse"
    if statut == "refus":
        if motif in MOTIFS_SECURITE:
            return "refus_securite"
        if motif in MOTIFS_CORPUS:
            return "refus_corpus"
        if motif in MOTIFS_QUALITE:
            return "refus_qualite"
    # `%r` : le motif vient du code, mais on ne laisse aucune valeur forger une fausse ligne de journal.
    logger.warning("vigie : motif inconnu, compte comme erreur technique : code=%d statut=%r motif=%r",
                   code_http, statut, motif)
    return "erreur_technique"


class _File:
    """Une file d'observations bornée, et l'heure de la dernière observation qu'elle a oubliée."""

    def __init__(self, plafond: int):
        self.observations: deque[Observation] = deque(maxlen=plafond)
        self.dernier_oubli: float | None = None

    def oublier(self, limite: float) -> None:
        while self.observations and self.observations[0].horodatage <= limite:
            self.dernier_oubli = self.observations.popleft().horodatage

    def ajouter(self, observation: Observation) -> None:
        if len(self.observations) == self.observations.maxlen:
            # Le plafond va faire partir la plus ancienne : la période complète commence après elle.
            self.dernier_oubli = self.observations[0].horodatage
        self.observations.append(observation)


class Compteurs:
    """Les observations des dernières 24 h, sous un verrou : les résultats et les rejets, 20 000 au plus chacun."""

    def __init__(self, horloge: Callable[[], float] = time.time, duree_de_vie_s: float = DUREE_DE_VIE_S,
                 plafond: int = PLAFOND):
        self._horloge, self.duree_de_vie_s = horloge, duree_de_vie_s
        self._resultats, self._rejets = _File(plafond), _File(plafond)
        self._verrou = threading.Lock()
        self._demarrage = horloge()

    def _oublier(self, maintenant: float) -> None:
        """Retire ce qui a plus de 24 h, dans les deux files. À appeler sous le verrou."""
        limite = maintenant - self.duree_de_vie_s
        self._resultats.oublier(limite)
        self._rejets.oublier(limite)

    def noter(self, route: str, code_http: int, statut: str | None, motif: str | None, duree_ms: int,
              jetons: tuple[int, int] = (0, 0)) -> None:
        observation_categorie = categorie(code_http, statut, motif)
        with self._verrou:
            maintenant = self._horloge()
            self._oublier(maintenant)
            file = self._rejets if observation_categorie == "rejet_acces_saisie" else self._resultats
            file.ajouter(Observation(maintenant, route, observation_categorie, motif or "", int(duree_ms),
                                     int(jetons[0]), int(jetons[1])))

    def observations(self) -> list[Observation]:
        """Une copie des observations encore gardées, des deux files, de la plus ancienne à la plus récente."""
        with self._verrou:
            self._oublier(self._horloge())
            return list(heapq.merge(self._resultats.observations, self._rejets.observations,
                                    key=attrgetter("horodatage")))

    def debut(self) -> float:
        """Le début de la période complète des résultats : le démarrage, ou la dernière observation oubliée."""
        with self._verrou:
            return self._demarrage if self._resultats.dernier_oubli is None else self._resultats.dernier_oubli

    def debut_rejets(self) -> float:
        """La même chose pour les rejets, qu'un flot d'appels sans clé peut faire avancer seul."""
        with self._verrou:
            return self._demarrage if self._rejets.dernier_oubli is None else self._rejets.dernier_oubli


# --- La consommation d'un appel ---------------------------------------------------------------------------------------
_consommation: contextvars.ContextVar[list[int] | None] = contextvars.ContextVar("consommation", default=None)


def debuter_consommation() -> None:
    """Ouvre le compteur de jetons de l'appel en cours. Chaque route l'appelle à son début."""
    _consommation.set([0, 0])


def ajouter_jetons(entree: int | None, sortie: int | None) -> None:
    """Ajoute les jetons d'une tentative. Hors d'un appel ouvert (un script, une mesure), ne fait rien."""
    courant = _consommation.get()
    if courant is None:
        return
    courant[0] += int(entree or 0)
    courant[1] += int(sortie or 0)


def consommation() -> tuple[int, int]:
    """(jetons d'entrée, jetons de sortie) de l'appel en cours ; (0, 0) hors d'un appel."""
    courant = _consommation.get()
    return (0, 0) if courant is None else (courant[0], courant[1])


COMPTEURS = Compteurs()
