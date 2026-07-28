"""Rédacteur — génère le briefing en français via src/llm.py (C8, C9, C10)."""
from src.llm import generer_texte


def generate_briefing(ticker: str, price: float, change_pct: float, volume: int,
                       currency: str) -> str:
    """Rédige un briefing français à partir des données du Scout.

    Args:
        ticker: code boursier, ex. 'MC.PA'.
        price: prix de clôture.
        change_pct: variation en pourcentage.
        volume: volume échangé.
        currency: devise du prix, ex. 'EUR'.

    Returns:
        Briefing en français, 3 à 5 phrases.
    """
    direction = "hausse" if change_pct >= 0 else "baisse"

    prompt = f"""Tu es un analyste financier français qui rédige des briefings courts pour des investisseurs particuliers.

Données du jour :
- Action : {ticker}
- Prix de clôture : {price} {currency}
- Variation : {change_pct}% ({direction})
- Volume : {volume:,}

Rédige un briefing de 3 à 5 phrases en français qui :
1. Résume la performance du jour avec un ton factuel
2. Indique le niveau de variation (faible / modérée / forte)
3. Signale un point à surveiller pour la séance suivante

Règles strictes :
- AUCUNE recommandation d'achat ou de vente
- Pas d'invention de chiffres ou d'événements non fournis
- Ton neutre, professionnel, accessible"""

    return generer_texte(prompt, max_tokens=500)
