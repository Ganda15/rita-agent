"""Source ECB — taux de change de référence publiés par la Banque centrale européenne.

Type de source C1 : **service web (API REST)**.
Aucune clé d'API requise — l'API SDMX de la BCE est publique et libre d'accès.

Structure de la réponse vérifiée en direct le 2026-07-29 (et non supposée) :
    dataSets[0].series["0:0:0:0:0"].observations["0"] = [valeur, ...]
    structure.dimensions.observation[0].values[i].id = date
"""
import httpx

ECB_URL = "https://data-api.ecb.europa.eu/service/data/EXR/D.{devise}.EUR.SP00.A"


def fetch_taux_change(devise: str = "USD") -> dict:
    """Récupère le dernier taux de change de référence <devise>/EUR publié par la BCE.

    Args:
        devise: code ISO de la devise étrangère, ex. 'USD', 'GBP', 'CHF', 'JPY'.

    Returns:
        {devise, date, valeur} — 1 EUR vaut `valeur` unités de `devise`.

    Raises:
        httpx.HTTPStatusError: si la BCE renvoie une erreur.
        KeyError: si la structure de la réponse a changé.
    """
    reponse = httpx.get(
        ECB_URL.format(devise=devise),
        params={"format": "jsondata", "lastNObservations": 1},
        timeout=30.0,
    )
    reponse.raise_for_status()
    donnees = reponse.json()

    serie = donnees["dataSets"][0]["series"]["0:0:0:0:0"]["observations"]
    index_str, valeurs = next(iter(serie.items()))
    dates = donnees["structure"]["dimensions"]["observation"][0]["values"]

    return {
        "devise": devise,
        "date": dates[int(index_str)]["id"],
        "valeur": float(valeurs[0]),
    }
