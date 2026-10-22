"""La route `GET /sante` : les signaux de la vigie et leurs verdicts (sprint 5, étapes 2 et 3 ; E5, C20).

`/health` dit que le service répond. `/sante` dit comment il se porte : erreurs, refus, latence, coût estimé,
fraîcheur des données, et pour chaque signal un verdict (sain, attention, problème, inconnu) avec son seuil et son
action. Les calculs sont dans `monitorage/signaux.py` et `monitorage/seuils.py`. La clé est exigée par le montage du
routeur (`api/main.py`), comme pour `/donnees` ; la route n'appelle jamais le modèle, donc elle ne passe pas par la
limite de débit : la vigie et le tableau de bord la lisent souvent. Les seuils et le prix sont relus à chaque appel :
un seuil corrigé s'applique sans redémarrer.
"""
from __future__ import annotations

import time
from datetime import date

from fastapi import APIRouter

from monitorage import compteurs, seuils, signaux

routeur = APIRouter(tags=["service"])


def construire(mesures: compteurs.Compteurs, lignes: list[dict] | None, maintenant: float, aujourdhui: date) -> dict:
    """L'état complet que rend `/sante` : signaux, coût estimé, verdicts. Sans réseau ni horloge : testable."""
    etat = signaux.etat_sante(mesures, lignes, maintenant, aujourdhui)
    prix = seuils.charger_prix()
    etat["cout_24h"] = {"valeur": seuils.cout_24h(etat["jetons_24h"], prix), "devise": prix["devise"],
                        "depuis": etat["jetons_24h"]["depuis"], "prix_du": prix["en_vigueur_depuis"],
                        "estimation": "majorant : jetons en cache comptés au prix plein (monitorage/prix.json)"}
    etat["verdicts"] = seuils.evaluer(etat, seuils.charger())
    return etat


@routeur.get("/sante", summary="Les signaux de la vigie et leurs verdicts : erreurs, refus, latence, coût, fraîcheur")
def sante() -> dict:
    lignes = signaux.lire_fraicheur_par_valeur()
    aujourdhui = (lignes[0].get("aujourdhui") if lignes else None) or date.today()
    return construire(compteurs.COMPTEURS, lignes, time.time(), aujourdhui)
