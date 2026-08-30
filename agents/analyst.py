"""Rédacteur — génère le briefing en français via src/llm.py (C8, C9, C10)."""
from src.llm import generer_texte


def generate_briefing(ticker: str, price: float, change_pct: float,
                      adtv20: float | None, currency: str,
                      fraicheur_jours: int = 0,
                      cotation_perimee: bool = False) -> str:
    """Rédige un briefing français à partir des données lues en base.

    Args:
        ticker: code boursier, ex. 'MC.PA'.
        price: cours de la dernière séance collectée.
        change_pct: performance sur 1 jour, en pourcentage.
        adtv20: volume MOYEN sur 20 séances. `None` si l'historique est trop court.
        currency: devise de la valeur, lue dans `valeur.devise`.
        fraicheur_jours: âge de la cotation, en jours.
        cotation_perimee: vrai au-delà de 40 jours — la valeur est probablement radiée.

    Returns:
        Briefing en français, 3 à 5 phrases.
    """
    direction = "hausse" if change_pct >= 0 else "baisse"
    volume_moyen = f"{adtv20:,.0f}" if adtv20 is not None else "non disponible"

    # La fraîcheur est DITE au modèle, pas seulement calculée. Le défaut du 19/08 :
    # `fraicheur_jours` existait et n'était jamais exploité — trois valeurs radiées
    # sortaient des chiffres de 2018 présentés comme ceux du jour.
    if cotation_perimee:
        avertissement = (
            f"\n⚠️ ATTENTION : cette cotation date de {fraicheur_jours} jours. "
            "Tu DOIS commencer le briefing en signalant que la donnée est ancienne "
            "et que la valeur est probablement radiée."
        )
    else:
        avertissement = f"\n- Fraîcheur de la donnée : {fraicheur_jours} jour(s)"

    prompt = f"""Tu es un analyste financier français qui rédige des briefings courts pour des investisseurs particuliers.

Données de la dernière séance collectée :
- Action : {ticker}
- Cours de clôture : {price} {currency}
- Variation sur 1 jour : {change_pct}% ({direction})
- Volume moyen sur 20 séances : {volume_moyen}{avertissement}

Rédige un briefing de 3 à 5 phrases en français qui :
1. Résume la performance du jour avec un ton factuel
2. Indique le niveau de variation (faible / modérée / forte)
3. Signale un point à surveiller pour la séance suivante

Règles strictes :
- AUCUNE recommandation d'achat ou de vente
- Pas d'invention de chiffres ou d'événements non fournis
- Ne présente JAMAIS le volume moyen 20 séances comme le volume du jour
- Ton neutre, professionnel, accessible"""

    return generer_texte(prompt, max_tokens=500)
