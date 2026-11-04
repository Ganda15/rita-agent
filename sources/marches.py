"""Les places de cotation : fuseau horaire, devise, unité de prix, jours fériés Euronext.

Pourquoi ce module existe (27/09/2026). Le guide « Markets and finance in RITA » a fait
apparaître cinq défauts qui ont une seule cause : RITA traitait toutes ses valeurs comme
si elles cotaient à Paris, en euros, en heure UTC, sans jour férié.

* **#53** : l'archive de dix ans prenait la date UTC d'un horodatage « minuit à Paris »,
  soit 22h00 ou 23h00 **la veille**. 52 426 cotations étaient rangées un dimanche.
* **#47** : FTI et SLB cotent à New York en dollars, HSBA.L à Londres en **pence** ; les
  trois étaient étiquetées EUR, et HSBA.L était lue 100 fois trop haut.
* **#49** : un cours relevé le samedi prenait la date du samedi.
* **#51** : la fraîcheur ne connaissait pas les fériés Euronext (et citait à tort le
  14 juillet, jour où Euronext Paris cote).

Une place inconnue **échoue bruyamment** : deviner « EUR » par défaut est précisément ce
qui a produit #47.

Fériés Euronext (page officielle, lue le 27/09/2026) :
https://live.euronext.com/en/resources/trading-hours-holidays
1er janvier, Vendredi saint, lundi de Pâques, 1er mai, 25 et 26 décembre. Les fériés
propres à Londres ou à New York ne sont pas modélisés : seule la fraîcheur du jeu (qui
suit Paris) et la date du scraping (qui ne lit que Paris) s'en servent.
"""
from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

# suffixe Yahoo -> (fuseau de la place, devise de cotation, facteur vers l'unité de la devise)
PLACES: dict[str, tuple[str, str, float]] = {
    ".PA": ("Europe/Paris", "EUR", 1),
    ".AS": ("Europe/Amsterdam", "EUR", 1),
    ".BR": ("Europe/Brussels", "EUR", 1),
    ".L": ("Europe/London", "GBP", 0.01),     # Yahoo cote Londres en pence (GBp)
    "": ("America/New_York", "USD", 1),       # sans suffixe : NYSE ou Nasdaq
}


# Le nom de la place, pour dire quel calendrier compte les séances (refonte 001, tâche 3). Seuls les fériés Euronext
# sont modélisés ici : Londres et New York sont nommés, leurs séances ne sont pas comptées.
NOMS_DES_PLACES: dict[str, str] = {".PA": "Euronext", ".AS": "Euronext", ".BR": "Euronext", ".L": "Londres",
                                   "": "New York"}


def _suffixe(ticker: str) -> str:
    return "." + ticker.rsplit(".", 1)[1] if "." in ticker else ""


def _place(ticker: str) -> tuple[str, str, float]:
    suffixe = _suffixe(ticker)
    try:
        return PLACES[suffixe]
    except KeyError:
        raise ValueError(f"Place de cotation inconnue pour {ticker!r} (suffixe {suffixe!r})") from None


def place_de_cotation(ticker: str) -> str:
    """La place où la valeur cote : « Euronext », « Londres » ou « New York ». Une place inconnue lève `ValueError`."""
    _place(ticker)   # même refus bruyant que les autres fonctions du module
    return NOMS_DES_PLACES[_suffixe(ticker)]


def devise_de_cotation(ticker: str) -> str:
    """La devise dans laquelle la valeur cote : EUR, GBP ou USD."""
    return _place(ticker)[1]


def facteur_prix(ticker: str) -> float:
    """Ce qu'il faut multiplier au prix Yahoo pour l'exprimer dans l'unité de la devise."""
    return _place(ticker)[2]


def date_de_seance(horodatage: pd.Timestamp, ticker: str) -> date:
    """La date de la séance **à l'heure de la place**, pas la date UTC.

    Un horodatage sans fuseau est lu comme de l'UTC, la convention du Parquet.
    """
    ts = pd.Timestamp(horodatage)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert(_place(ticker)[0]).date()


def paques(annee: int) -> date:
    """Dimanche de Pâques (calendrier grégorien, algorithme dit « anonyme »)."""
    a, b, c = annee % 19, annee // 100, annee % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    semaine = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * semaine) // 451
    mois = (h + semaine - 7 * m + 114) // 31
    jour = (h + semaine - 7 * m + 114) % 31 + 1
    return date(annee, mois, jour)


def jours_feries_euronext(annee: int) -> set[date]:
    p = paques(annee)
    return {
        date(annee, 1, 1),
        p - timedelta(days=2),          # Vendredi saint
        p + timedelta(days=1),          # lundi de Pâques
        date(annee, 5, 1),
        date(annee, 12, 25),
        date(annee, 12, 26),
    }


def est_jour_de_bourse(jour: date) -> bool:
    """Euronext Paris cote-t-il ce jour-là ?"""
    return jour.weekday() < 5 and jour not in jours_feries_euronext(jour.year)


def derniere_seance(jour: date) -> date:
    """La dernière séance Euronext à ou avant `jour`."""
    while not est_jour_de_bourse(jour):
        jour -= timedelta(days=1)
    return jour
