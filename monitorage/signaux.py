"""Les signaux de la vigie, calculés à partir des compteurs et de la base (sprint 5, étape 2).

Plan du sprint 5, § 3, étape 2. Livrable : E5 (C20, surveiller). `GET /sante` (api/sante.py) rend `etat_sante()` : le
tableau de bord (étape 5) et la vigie (étape 4) lisent la même source, donc ils disent la même chose.

## Ce qui est calculé, et sur quelle période

- **Les taux** (erreurs techniques, refus de sécurité, de corpus, de qualité) : sur les **résultats** des 15 dernières
  minutes, c'est-à-dire les appels entrés dans la route. Les rejets (403, 422, 429) se comptent à part : un flot
  d'appels sans clé ne doit pas faire baisser le taux d'erreurs.
- **La latence p95** : sur les mêmes résultats. Calcul entier, `(95 * n + 99) // 100`, jamais de virgule flottante.
- **Les jetons** : sur les 24 dernières heures disponibles, avec le début réel de la période. Le coût, qui demande un
  prix daté, vient à l'étape 3.
- **La fraîcheur** : PAR VALEUR (`db/fraicheur_par_valeur.sql`), avec les règles de `monitorage/fraicheur.py`
  (jours ouvrés, vert jusqu'à 1, orange jusqu'à 3, rouge au-delà).

## « Inconnu » n'est jamais vert

Aucune requête dans la fenêtre : `"valeur": None`, pas 0. Base injoignable ou sans valeur suivie : fraîcheur
« inconnu ». Ce module ne fixe aucun seuil et ne colore rien : il rend les valeurs brutes avec leur effectif. Les
seuils argumentés viennent à l'étape 3.
"""
from __future__ import annotations

import logging
from datetime import date, datetime
from pathlib import Path

from monitorage import fraicheur
from monitorage.compteurs import Compteurs, Observation
from sources import database

logger = logging.getLogger(__name__)

FENETRE_S = 15 * 60
_REQUETE = Path(__file__).parent.parent / "db" / "fraicheur_par_valeur.sql"
_GRAVITE = {"vert": 0, "orange": 1, "rouge": 2}


def _heure(horodatage: float) -> str:
    return datetime.fromtimestamp(horodatage).astimezone().isoformat(timespec="seconds")


def p95_ms(durees: list[int]) -> int | None:
    """La durée sous laquelle passent 95 % des appels ; `None` sans appel."""
    if not durees:
        return None
    rang = (95 * len(durees) + 99) // 100        # arrondi au-dessus, en entiers
    return sorted(durees)[rang - 1]


def taux(resultats: list[Observation], categories: set[str]) -> dict:
    numerateur = sum(1 for o in resultats if o.categorie in categories)
    effectif = len(resultats)
    return {"valeur": round(numerateur / effectif, 4) if effectif else None, "numerateur": numerateur,
            "effectif": effectif}


def fraicheur_par_valeur(lignes: list[dict] | None, aujourdhui: date) -> dict:
    """Le retard de chaque valeur suivie ; `pire` est la plus mauvaise couleur, « inconnu » sans données."""
    if not lignes:
        message = "base injoignable" if lignes is None else "aucune valeur suivie"
        return {"pire": "inconnu", "nb_valeurs": None if lignes is None else 0, "en_retard": [], "message": message}
    etats = []
    for ligne in lignes:
        derniere = ligne.get("derniere_seance")
        if derniere is None:
            retard, statut = None, "rouge"
        else:
            retard = fraicheur.jours_ouvres_ecoules(derniere, aujourdhui)
            statut = ("vert" if retard <= fraicheur.SEUIL_VERT_JOURS_OUVRES
                      else "orange" if retard <= fraicheur.SEUIL_ORANGE_JOURS_OUVRES else "rouge")
        etats.append({"ticker": ligne["ticker"], "derniere_seance": derniere.isoformat() if derniere else None,
                      "retard_jours_ouvres": retard, "statut": statut})
    en_retard = sorted((e for e in etats if e["statut"] != "vert"),
                       key=lambda e: (-1 if e["retard_jours_ouvres"] is None else 0, -(e["retard_jours_ouvres"] or 0)))
    pire = max((e["statut"] for e in etats), key=_GRAVITE.__getitem__)
    return {"pire": pire, "nb_valeurs": len(etats), "en_retard": en_retard, "message": ""}


def lire_fraicheur_par_valeur(dsn: str | None = None) -> list[dict] | None:
    """Les lignes de `db/fraicheur_par_valeur.sql` ; `None` si la base ne répond pas (la vigie dit alors « inconnu »)."""
    try:
        return database._executer(_REQUETE.read_text(encoding="utf-8"), "fraicheur_par_valeur", dsn).lignes
    except Exception as erreur:  # noqa: BLE001, le type seul : un message de connexion peut porter le DSN
        logger.warning("vigie : fraicheur par valeur illisible : %s", type(erreur).__name__)
        return None


def etat_sante(compteurs: Compteurs, lignes_fraicheur: list[dict] | None, maintenant: float,
               aujourdhui: date) -> dict:
    """Tous les signaux, en valeurs brutes, avec leur effectif et leur période."""
    observations = compteurs.observations()
    resultats = [o for o in observations if o.categorie != "rejet_acces_saisie"]
    recents = [o for o in resultats if o.horodatage > maintenant - FENETRE_S]
    rejets_recents = [o for o in observations
                      if o.categorie == "rejet_acces_saisie" and o.horodatage > maintenant - FENETRE_S]
    debut = _heure(compteurs.debut())
    return {
        "mesures_depuis": debut,
        "rejets_depuis": _heure(compteurs.debut_rejets()),
        "fenetre_min": FENETRE_S // 60,
        "erreurs_techniques": taux(recents, {"erreur_technique"}),
        "refus_securite": taux(recents, {"refus_securite"}),
        "refus_corpus": taux(recents, {"refus_corpus"}),
        "refus_qualite": taux(recents, {"refus_qualite"}),
        "latence_p95_ms": {"valeur": p95_ms([o.duree_ms for o in recents]), "effectif": len(recents)},
        "rejets_15_min": len(rejets_recents),
        "jetons_24h": {"entree": sum(o.jetons_entree for o in resultats),
                       "sortie": sum(o.jetons_sortie for o in resultats), "depuis": debut},
        "fraicheur": fraicheur_par_valeur(lignes_fraicheur, aujourdhui),
    }
