"""La panne simulée : son état, en mémoire (sprint 5, étape 6 ; grille de l'atelier 5, critère 4).

Plan du sprint 5, § 2 « Panne simulée ». Une panne posée exprès pour s'entraîner à la diagnostiquer avec la doc, sans
toucher à une clé ni à la base : pendant l'exercice, `/question` répond comme si le fournisseur du modèle était tombé
(api/question.py). L'état vit en mémoire, sous un verrou, comme les compteurs.

Trois garanties, pour qu'un exercice ne laisse jamais le service en panne :
- il se termine **seul** après sa durée, 20 minutes au plus, même si personne ne le retire ou si la séance
  s'interrompt ;
- un redémarrage du service l'efface aussi (il est en mémoire) ;
- un second exercice ne peut pas se poser par-dessus le premier.

Qui l'a posé, et pourquoi, est gardé et rendu par `/sante` : une panne simulée ne doit jamais passer pour une vraie.
"""
from __future__ import annotations

import threading
import time
from collections.abc import Callable
from datetime import datetime

DUREE_MAX_S = 20 * 60


class ExerciceEnCours(Exception):
    """Un exercice est déjà en cours : on ne pose pas une panne par-dessus une autre."""


def _heure(horodatage: float) -> str:
    return datetime.fromtimestamp(horodatage).astimezone().isoformat(timespec="seconds")


class Exercice:
    """L'exercice de panne en cours, ou aucun."""

    def __init__(self, horloge: Callable[[], float] = time.time):
        self._horloge = horloge
        self._verrou = threading.Lock()
        self._en_cours: dict | None = None

    def _expirer(self) -> None:
        """Termine l'exercice dont la durée est passée. À appeler sous le verrou."""
        if self._en_cours and self._horloge() >= self._en_cours["fin"]:
            self._en_cours = None

    @staticmethod
    def _public(exercice: dict) -> dict:
        return {"nom": exercice["nom"], "motif": exercice["motif"], "depuis": _heure(exercice["debut"]),
                "fin_au_plus_tard": _heure(exercice["fin"])}

    def poser(self, nom: str, motif: str, duree_s: int = DUREE_MAX_S) -> dict:
        if not 0 < duree_s <= DUREE_MAX_S:
            raise ValueError(f"durée de l'exercice hors bornes : {duree_s} s (de 1 à {DUREE_MAX_S} s)")
        with self._verrou:
            self._expirer()
            if self._en_cours:
                raise ExerciceEnCours("un exercice de panne est déjà en cours")
            debut = self._horloge()
            self._en_cours = {"nom": nom, "motif": motif, "debut": debut, "fin": debut + duree_s}
            return self._public(self._en_cours)

    def finir(self) -> dict | None:
        """Retire l'exercice en cours ; rend ce qui a été retiré, ou `None` s'il n'y en avait pas."""
        with self._verrou:
            self._expirer()
            ancien, self._en_cours = self._en_cours, None
            return self._public(ancien) if ancien else None

    def etat(self) -> dict | None:
        with self._verrou:
            self._expirer()
            return self._public(self._en_cours) if self._en_cours else None


EXERCICE = Exercice()
