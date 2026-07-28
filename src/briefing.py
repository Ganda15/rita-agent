"""Étape 2 — Générer un briefing financier en français via Claude."""

from anthropic import Anthropic
from dotenv import load_dotenv

from src.ingest import fetch_price

load_dotenv()

client = Anthropic()

MODEL = "claude-sonnet-4-6"


def generate_briefing(price_data: dict) -> str:
    """Génère un briefing en français à partir des données prix.

    Args:
        price_data: dict retourné par fetch_price() — ticker, price, change_pct, currency.

    Returns:
        Texte du briefing en français (3 à 5 phrases).
    """
    direction = "hausse" if price_data["change_pct"] >= 0 else "baisse"

    prompt = f"""Tu es un analyste financier français qui rédige des briefings courts pour des investisseurs particuliers.

Données du jour :
- Action : {price_data['ticker']}
- Prix de clôture : {price_data['price']} {price_data['currency']}
- Variation : {price_data['change_pct']}% ({direction})

Rédige un briefing de 3 à 5 phrases en français qui :
1. Résume la performance du jour avec ce ton factuel
2. Indique le niveau de variation (faible / modérée / forte)
3. Signale un point à surveiller pour la séance suivante

Règles strictes :
- AUCUNE recommandation d'achat ou de vente
- Pas d'invention de chiffres ou d'événements non fournis
- Ton neutre, professionnel, accessible"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


if __name__ == "__main__":
    data = fetch_price("MC.PA")
    print(f"Données : {data}\n")
    print("─" * 60)
    print("BRIEFING DU JOUR")
    print("─" * 60)
    briefing = generate_briefing(data)
    print(briefing)
