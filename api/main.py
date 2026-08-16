"""API REST de RITA — mise à disposition des données (C5) et du briefing (C9).

Deux familles de points de terminaison, et la distinction est celle du référentiel :

    /donnees/*    le JEU DE DONNÉES brut, filtrable            -> C5
    /briefing     un TEXTE rédigé par un modèle d'IA           -> C9

Documentation interactive : http://127.0.0.1:8000/docs
Contrat OpenAPI :           http://127.0.0.1:8000/openapi.json
"""
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from api.donnees import routeur as routeur_donnees
from graph.workflow import generer_briefing_complet

load_dotenv()

DESCRIPTION = """
API de **RITA** — *Retrieval Intelligence pour le Tracking et l'Analyse*.

### Authentification
Tous les points de terminaison sauf `/health` exigent l'en-tête **`X-API-Key`**.
Une clé absente ou invalide renvoie **403**.

### Deux familles
| Préfixe | Contenu | Compétence |
|---|---|---|
| `/donnees/*` | le jeu de données brut, filtrable | C5 |
| `/briefing` | un texte rédigé par un modèle | C9 |

### ⚠️ Données personnelles
`/donnees/portefeuille` expose des données financières personnelles (RGPD, traitement T1).
"""

app = FastAPI(
    title="RITA API",
    version="1.1.0",
    description=DESCRIPTION,
    contact={"name": "RITA — projet fil rouge RNCP 37827"},
)

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    """Autorisation par clé d'API.

    Volontairement simple : une seule clé, comparée à `RITA_API_KEY`. RITA est
    mono-utilisateur (décision D10) — un système de comptes serait de la complexité sans
    besoin. La contrepartie est assumée : pas de révocation partielle, pas de traçabilité
    par appelant.
    """
    attendue = os.getenv("RITA_API_KEY", "dev-key")
    if api_key != attendue:
        raise HTTPException(status_code=403, detail="Cle d'API invalide ou absente")
    return api_key


@app.get("/health", tags=["service"], summary="Vérifier que le service répond")
def health():
    """Seul point de terminaison **non protégé** : il ne révèle aucune donnée."""
    return {"status": "ok", "project": "RITA"}


# --- C5 : le jeu de données -------------------------------------------------
# La dépendance est posée sur le ROUTEUR entier : impossible d'ajouter un point de
# terminaison non protégé par oubli. C'est un garde-fou de conception, pas de discipline.
app.include_router(routeur_donnees, dependencies=[Depends(verify_api_key)])


# --- C9 : le briefing rédigé ------------------------------------------------
@app.post("/briefing", tags=["briefing IA"],
          summary="Générer un briefing rédigé pour une valeur")
def briefing(ticker: str, api_key: str = Security(verify_api_key)):
    """Produit un texte en français à partir des données de la valeur.

    Relève de **C9** (exposer un modèle), pas de C5 : la sortie est une rédaction, pas de
    la donnée. Le garde-fou AMF s'applique — aucune recommandation d'achat ou de vente.
    """
    resultat = generer_briefing_complet(ticker)
    if resultat["error"]:
        raise HTTPException(status_code=502, detail=resultat["error"])
    return {
        "ticker": resultat["ticker"],
        "price": resultat["price"],
        "change_pct": resultat["change_pct"],
        "currency": resultat["currency"],
        "briefing": resultat["briefing"],
    }
