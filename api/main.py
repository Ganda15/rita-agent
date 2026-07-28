from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv
import os

from graph.workflow import generer_briefing_complet

load_dotenv()

app = FastAPI(title="RITA API", version="1.0.0")

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    expected = os.getenv("RITA_API_KEY", "dev-key")
    if api_key != expected:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.get("/health")
def health():
    return {"status": "ok", "project": "RITA"}

@app.post("/briefing")
def briefing(ticker: str, api_key: str = Security(verify_api_key)):
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
