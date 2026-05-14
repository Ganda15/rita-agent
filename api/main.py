from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv
import os

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
    # Placeholder — will call Claude API in later step
    return {"ticker": ticker, "briefing": "À implémenter"}
