"""Source FRED — indicateurs macro-économiques américains (Réserve fédérale de St. Louis).

Type de source C1 : **service web (API REST)**.

⚠️ Contrairement à la BCE, cette API exige une **clé** : `FRED_API_KEY` dans `.env`.
C'est la seule source de RITA qui manipule un secret.

Structure de la réponse vérifiée en direct le 2026-08-02 (et non supposée) :
    observations[i] = {"realtime_start", "realtime_end", "date", "value"}

Deux particularités **mesurées** sur 400 observations réelles de DGS10 :
  * `value` est une **chaîne** à 10 décimales : `"4.6800000000"`, jamais un nombre.
  * une valeur manquante vaut **le point** `"."` — jamais `null`, jamais absente.
    17 cas sur 400 (4,3 %), tous des jours fériés fédéraux américains :
    2026-07-03, 2026-06-19, 2026-05-25, 2026-02-16, 2026-01-19…
    Sans filtre, `float(".")` interrompt la collecte une fois sur vingt-cinq.
"""
import os

import httpx

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"

# Les trois séries retenues pour RITA, et ce qu'elles disent.
# Un code seul ne veut rien dire : chacune porte son libellé.
SERIES = {
    "DGS10": "Rendement du Trésor américain à 10 ans",
    "CPIAUCSL": "Indice des prix à la consommation (inflation US)",
    "DFF": "Taux directeur effectif de la Réserve fédérale",
}


class CleFredAbsente(RuntimeError):
    """Levée quand `FRED_API_KEY` n'est pas dans l'environnement."""


def _cle() -> str:
    """Lit la clé, ou échoue avec un message qui dit quoi faire.

    `os.environ["FRED_API_KEY"]` lèverait un `KeyError` nu, illisible pour qui
    découvre le projet. Ici l'erreur porte son propre remède.
    """
    cle = os.getenv("FRED_API_KEY", "").strip()
    if not cle:
        raise CleFredAbsente(
            "FRED_API_KEY absente. Ajouter FRED_API_KEY=<cle> dans .env "
            "(cle gratuite sur https://fredaccount.stlouisfed.org/apikeys)."
        )
    return cle


def fetch_indicateur(series_id: str, limite: int = 1) -> list[dict]:
    """Récupère les dernières observations d'une série FRED.

    Args:
        series_id: code FRED, ex. 'DGS10', 'CPIAUCSL', 'DFF'.
        limite: nombre d'observations, de la plus récente à la plus ancienne.

    Returns:
        Liste de `{date, valeur}`, la plus récente en premier. Les observations
        manquantes (valeur `"."`) sont écartées — voir la docstring du module.

    Raises:
        CleFredAbsente: si `FRED_API_KEY` n'est pas configurée.
        httpx.HTTPStatusError: si FRED refuse la requête (clé invalide, quota).
        KeyError: si la structure de la réponse a changé.
    """
    reponse = httpx.get(
        FRED_URL,
        params={
            "series_id": series_id,
            # La clé passe en PARAMÈTRE, jamais concaténée dans l'URL : les
            # serveurs journalisent les URL complètes, pas les paramètres.
            "api_key": _cle(),
            "file_type": "json",
            "sort_order": "desc",   # sans ça, limit=1 renverrait l'observation de 1962
            "limit": limite,
        },
        timeout=30.0,
    )
    reponse.raise_for_status()

    return [
        {"date": obs["date"], "valeur": float(obs["value"])}
        for obs in reponse.json()["observations"]
        if obs["value"] != "."
    ]
