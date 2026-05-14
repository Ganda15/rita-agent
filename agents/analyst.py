"""Analyst agent — génère un briefing via Claude API (C8, C9, C10)."""
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()


def generate_briefing(ticker: str, price: float, change_pct: float, volume: int) -> str:
    """Envoie les données à Claude et retourne un briefing en français."""
    prompt = f"""Tu es un analyste financier senior. Génère un briefing concis en français pour :
- Ticker : {ticker}
- Prix de clôture : {price} USD
- Variation : {change_pct:+.2f}%
- Volume : {volume:,}

Briefing en 3 phrases maximum : tendance, signal notable, conseil de surveillance."""

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Erreur génération briefing : {e}"
