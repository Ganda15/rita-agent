"""Fraîcheur du jeu de données — C20 (surveiller) et C1 (pérenniser).

Requête : `db/fraicheur.sql`
Livrable : E5 (monitorage) — et preuve visible de C1, la collecte pérennisée.

## Le manque que ce module comble

`/health` répond `{"status":"ok"}` : il dit que le service tourne, pas que
ses données valent quelque chose. Un service parfaitement en ligne servant
des cours vieux de trois mois est un service en panne — silencieuse.

Le besoin était écrit dès le 11/08 dans `scripts/README-planification.md` §7 :

    « Une tâche planifiée s'exécute — elle ne garantit pas que les données
      arrivent. C'est pourquoi la vraie sécurité n'est pas la planification
      mais une requête de fraîcheur. »

## Pourquoi le retard se compte en jours OUVRÉS

La Bourse de Paris ne cote ni le samedi ni le dimanche. Un retard de 2 jours
un dimanche est **normal** ; le même retard un mercredi est une panne. Compter
en jours calendaires ferait passer la jauge au rouge chaque week-end — une
alerte qui crie tous les samedis est une alerte qu'on finit par ignorer.

⚠️ **Limite assumée** : les jours fériés boursiers ne sont pas connus de ce
module. Un 14 juillet ajoute donc 1 jour ouvré apparent. Le seuil VERT tolère
1 jour, ce qui absorbe un férié isolé sans le masquer indéfiniment.

## Pourquoi la décision est en Python et les faits en SQL

`evaluer()` est une **fonction pure** : mêmes entrées, même sortie, aucune
base, aucune horloge implicite (la date du jour est un paramètre). Elle se
teste donc entièrement sans PostgreSQL — la règle du dépôt.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from sources import database

# ⚠️ Sans cette ligne, le module ne lit pas le `.env` : `DATABASE_URL` est absente
# et `sources.database` retombe sur son DSN par défaut, en port **5432** — alors
# que la base tourne sur **5433**. Le module échoue partout SAUF derrière
# `api/main.py`, qui appelle `load_dotenv()` de son côté.
#
# Troisième fois que ce défaut apparaît dans ce dépôt : `db/importer.py` le 17/08
# (commit a7a3dba), `indicateurs/socle.py` ensuite, et ici le 25/08. Les 14 tests
# du module passaient au vert pendant que la lecture réelle était impossible :
# ils simulent `_executer`, donc ils ne touchent jamais la configuration.
# *Un test vert ne prouve pas qu'on sait se connecter.*
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_REQUETE = Path(__file__).parent.parent / "db" / "fraicheur.sql"

# Retard toléré, en jours ouvrés, avant de changer de couleur.
#
# VERT = 1 et pas 0 : la séance du jour n'est écrite qu'après la collecte de
# 19h00 (la Bourse clôture à 17h35). Entre l'ouverture et le soir, la dernière
# séance en base est donc légitimement celle de la veille.
SEUIL_VERT_JOURS_OUVRES = 1
SEUIL_ORANGE_JOURS_OUVRES = 3


def jours_ouvres_ecoules(depuis: date, jusqu_a: date) -> int:
    """Nombre de jours ouvrés strictement après `depuis`, jusqu'à `jusqu_a` inclus.

    Samedi et dimanche ne comptent pas. Rend 0 si `jusqu_a` précède `depuis`
    (une donnée « du futur » n'est pas un retard négatif, c'est zéro retard).

    >>> jours_ouvres_ecoules(date(2026, 8, 21), date(2026, 8, 24))  # ven -> lun
    1
    >>> jours_ouvres_ecoules(date(2026, 8, 21), date(2026, 8, 23))  # ven -> dim
    0
    """
    if jusqu_a <= depuis:
        return 0
    n = 0
    jour = depuis + timedelta(days=1)
    while jour <= jusqu_a:
        if jour.weekday() < 5:  # 0 = lundi … 4 = vendredi
            n += 1
        jour += timedelta(days=1)
    return n


@dataclass(frozen=True)
class Fraicheur:
    """L'état de fraîcheur du jeu de données, à une date donnée."""

    aujourdhui: date
    derniere_seance: date | None
    retard_jours_ouvres: int | None
    statut: str          # "vert" | "orange" | "rouge"
    message: str

    nb_cotations: int
    nb_valeurs: int
    nb_positions: int
    nb_articles: int
    nb_taux: int
    derniere_collecte_article: datetime | None
    dernier_taux: date | None

    def en_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluer(faits: dict, aujourdhui: date) -> Fraicheur:
    """Transforme les faits bruts du SQL en un état lisible. Fonction pure.

    `aujourdhui` est un paramètre, jamais `date.today()` : un test qui dépend
    de l'horloge réelle devient rouge tout seul un samedi.
    """
    derniere = faits.get("derniere_seance")

    if derniere is None:
        return Fraicheur(
            aujourdhui=aujourdhui,
            derniere_seance=None,
            retard_jours_ouvres=None,
            statut="rouge",
            message="Aucune cotation en base — la collecte n'a jamais abouti.",
            nb_cotations=int(faits.get("nb_cotations") or 0),
            nb_valeurs=int(faits.get("nb_valeurs") or 0),
            nb_positions=int(faits.get("nb_positions") or 0),
            nb_articles=int(faits.get("nb_articles") or 0),
            nb_taux=int(faits.get("nb_taux") or 0),
            derniere_collecte_article=faits.get("derniere_collecte_article"),
            dernier_taux=faits.get("dernier_taux"),
        )

    retard = jours_ouvres_ecoules(derniere, aujourdhui)

    if retard <= SEUIL_VERT_JOURS_OUVRES:
        statut = "vert"
        message = f"Données à jour — dernière séance du {derniere:%d/%m/%Y}."
    elif retard <= SEUIL_ORANGE_JOURS_OUVRES:
        statut = "orange"
        message = (f"{retard} jours ouvrés de retard — dernière séance du "
                   f"{derniere:%d/%m/%Y}. Vérifier la collecte de 19h00.")
    else:
        statut = "rouge"
        message = (f"{retard} jours ouvrés de retard — dernière séance du "
                   f"{derniere:%d/%m/%Y}. La collecte ne tourne plus.")

    return Fraicheur(
        aujourdhui=aujourdhui,
        derniere_seance=derniere,
        retard_jours_ouvres=retard,
        statut=statut,
        message=message,
        nb_cotations=int(faits.get("nb_cotations") or 0),
        nb_valeurs=int(faits.get("nb_valeurs") or 0),
        nb_positions=int(faits.get("nb_positions") or 0),
        nb_articles=int(faits.get("nb_articles") or 0),
        nb_taux=int(faits.get("nb_taux") or 0),
        derniere_collecte_article=faits.get("derniere_collecte_article"),
        dernier_taux=faits.get("dernier_taux"),
    )


def lire(dsn: str | None = None) -> Fraicheur:
    """Exécute la requête et rend l'état de fraîcheur.

    La date du jour vient du SERVEUR PostgreSQL (`CURRENT_DATE`), pas de la
    machine qui interroge : c'est l'horloge de la base qui fait foi pour des
    données stockées en base.
    """
    sql = _REQUETE.read_text(encoding="utf-8")
    extraction = database._executer(sql, "fraicheur", dsn)
    faits = extraction.lignes[0] if extraction.lignes else {}
    return evaluer(faits, faits.get("aujourdhui") or date.today())
