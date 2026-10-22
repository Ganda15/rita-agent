"""La route `GET /sante` : les signaux de la vigie (sprint 5, étape 2 ; E5, C20).

`/health` dit que le service répond. `/sante` dit comment il se porte : erreurs, refus, latence, jetons, fraîcheur des
données. Le calcul est dans `monitorage/signaux.py`. La clé est exigée par le montage du routeur (`api/main.py`), comme
pour `/donnees` ; la route n'appelle jamais le modèle, donc elle ne passe pas par la limite de débit : la vigie et le
tableau de bord la lisent souvent.
"""
from __future__ import annotations

import time
from datetime import date

from fastapi import APIRouter

from monitorage import compteurs, signaux

routeur = APIRouter(tags=["service"])


@routeur.get("/sante", summary="Les signaux de la vigie : erreurs, refus, latence, jetons, fraîcheur")
def sante() -> dict:
    lignes = signaux.lire_fraicheur_par_valeur()
    aujourdhui = (lignes[0].get("aujourdhui") if lignes else None) or date.today()
    return signaux.etat_sante(compteurs.COMPTEURS, lignes, time.time(), aujourdhui)
