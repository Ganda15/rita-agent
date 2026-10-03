"""Rédacteur — génère le briefing en français via src/llm.py (C8, C9, C10)."""
from src.llm import generer_texte


def _bloc_articles(passages: list[dict] | None) -> str:
    """Les articles retrouvés, ou l'interdiction explicite d'en inventer.

    ⚠️ Le silence ne suffit pas. Un modèle privé de sources **en invente** : c'est le
    risque central d'un RAG, et il ne se traite pas en omettant la section, mais en
    écrivant la consigne. *Un briefing qui cite une actualité fausse est pire qu'un
    briefing sans actualité.*

    ⚠️ **Jamais le mot « récents ».** Le RAG classe par PERTINENCE, pas par date :
    mesuré le 30/08, MC.PA remonte une dépêche de **2023**. L'en-tête doit demander
    au modèle de vérifier la date, pas lui affirmer une fraîcheur que rien ne garantit.
    """
    if not passages:
        return (
            "\n\nArticles : aucun article pertinent n'a été trouvé dans le corpus."
            "\n- N'invente AUCUNE actualité, AUCUN événement, AUCUNE déclaration."
            "\n- Rédige uniquement à partir des chiffres ci-dessus."
        )

    lignes = [f"{i}. [{p['source']}, {p['publie_le']}] {p['texte']}"
              for i, p in enumerate(passages, 1)]
    return (f"\n\nArticles retrouvés ({len(passages)}) — classés par PERTINENCE, pas par date : vérifie leur date avant de t'en servir, et ne présente jamais une dépêche ancienne comme une actualité du jour. Quand tu t'appuies sur l'un d'eux, "
            f"cite la source et la date. Chaque affirmation tirée des articles doit être soutenue par l'un des articles "
            f"ci-dessous ; si deux articles se contredisent, dis-le au lieu de choisir en silence :\n" + "\n".join(lignes))


def generate_briefing(ticker: str, price: float, change_pct: float,
                      adtv20: float | None, currency: str,
                      fraicheur_jours: int = 0,
                      cotation_perimee: bool = False,
                      passages: list[dict] | None = None) -> str:
    """Rédige un briefing français à partir des données lues en base et des articles.

    Args:
        ticker: code boursier, ex. 'MC.PA'.
        price: cours de la dernière séance collectée.
        change_pct: performance sur 1 jour, en pourcentage.
        adtv20: volume MOYEN sur 20 séances. `None` si l'historique est trop court.
        currency: devise de la valeur, lue dans `valeur.devise`.
        fraicheur_jours: âge de la cotation, en jours.
        cotation_perimee: vrai au-delà de 40 jours — la valeur est probablement radiée.
        passages: articles retrouvés par le RAG. Liste vide ou `None` = aucun article,
            et le prompt interdit alors explicitement d'en inventer.

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

    articles = _bloc_articles(passages)

    prompt = f"""Tu es un analyste financier français qui rédige des briefings courts pour des investisseurs particuliers.

Données de la dernière séance collectée :
- Action : {ticker}
- Cours de clôture : {price} {currency}
- Variation sur 1 jour : {change_pct}% ({direction})
- Volume moyen sur 20 séances : {volume_moyen}{avertissement}{articles}

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
