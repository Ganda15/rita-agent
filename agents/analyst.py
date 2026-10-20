"""Rédacteur — génère le briefing en français via src/llm.py (C8, C9, C10)."""
import logging

from guardrails.injection import neutraliser
from src.llm import generer_texte

logger = logging.getLogger(__name__)

# Les parties fixes du prompt du rédacteur (sprint 4, tâche B2) : le contrôle de fuite (`guardrails/sortie.py`,
# `verifier_fuite`) refuse un briefing qui en recopierait un morceau. `construire_prompt` les assemble sans changer un
# caractère du prompt d'avant.
ROLE_REDACTEUR = ("Tu es un analyste financier français qui rédige des briefings courts pour des investisseurs "
                  "particuliers.")
CONSIGNES_REDACTION = """Rédige un briefing de 3 à 5 phrases en français qui :
1. Résume la performance du jour avec un ton factuel
2. Indique le niveau de variation (faible / modérée / forte)
3. Signale un point à surveiller pour la séance suivante

Règles strictes :
- AUCUNE recommandation d'achat ou de vente
- Pas d'invention de chiffres ou d'événements non fournis
- Ne présente JAMAIS ces capitaux moyens ni comme un volume du jour, ni comme un nombre de titres
- Ton neutre, professionnel, accessible"""


def articles_surs(passages: list[dict] | None) -> list[dict]:
    """Les articles qui peuvent entrer dans le prompt du briefing (sprint 4, tâche A4 ; spec CA2.8).

    Même filtre que le parcours des questions (`agents/question.py`, `passages_surs`) : un article qui porte une
    injection (`guardrails/injection.py`) est écarté, avec une ligne de journal sans son texte. Appelé par le nœud `rag`
    du graphe, pour que le compte des articles transmis et la trace disent la vérité, et par `_bloc_articles`, pour
    que tout appelant du prompt soit couvert.
    """
    surs = []
    for passage in passages or []:
        verdict = neutraliser(passage.get("texte") or "", source="index")
        if verdict["bloque"]:
            logger.warning("passage ecarte avant le prompt : article_id=%s motifs=%s", passage.get("article_id"),
                           ",".join(verdict["motifs_detectes"]))
            continue
        surs.append(passage)
    return surs


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
    passages = articles_surs(passages)
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


# Les neuf indicateurs que le scout calcule et que le prompt ne recevait pas (03/10/2026, décision d'Era).
# Chaque ligne : la clé du dictionnaire du scout, son libellé, son unité ("pct" = pourcentage signé,
# "devise" = montant dans la devise de la valeur, "" = nombre nu). L'ordre est celui de la lecture.
INDICATEURS_DU_PROMPT = (
    ("perf_1s_pct", "Performance sur 1 semaine", "pct"),
    ("perf_1m_pct", "Performance sur 1 mois", "pct"),
    ("perf_ytd_pct", "Performance depuis le 1er janvier", "pct"),
    ("perf_1a_pct", "Performance sur 1 an", "pct"),
    ("ma20", "Moyenne mobile 20 séances", "devise"),
    ("ma50", "Moyenne mobile 50 séances", "devise"),
    ("distance_plus_haut_1a_pct", "Distance au plus haut sur 1 an", "pct"),
    ("volatilite_annualisee_pct", "Volatilité annualisée", "pct_sans_signe"),   # une amplitude, pas une direction
    ("drawdown_max_1a_pct", "Drawdown maximal sur 1 an", "pct"),
    ("rsi_14", "RSI 14", ""),
)


def _valeur_indicateur(valeur, unite: str, currency: str) -> str:
    """Un indicateur absent est « non disponible », jamais 0 : absent et nul ne sont pas la même chose."""
    if valeur is None:
        return "non disponible"
    if unite == "pct":
        return f"{valeur:+.2f} %".replace(".", ",")
    if unite == "pct_sans_signe":
        return f"{valeur:.2f} %".replace(".", ",")
    if unite == "devise":
        return f"{valeur:.2f} {currency}"
    return f"{valeur:.1f}"


def _bloc_indicateurs(indicateurs: dict | None, currency: str) -> str:
    """Les indicateurs calculés, comme des faits. Vide quand l'appelant n'en fournit pas (compatibilité)."""
    if not indicateurs:
        return ""
    lignes = [f"- {libelle} : {_valeur_indicateur(indicateurs.get(cle), unite, currency)}"
              for cle, libelle, unite in INDICATEURS_DU_PROMPT]
    return ("\n\nIndicateurs calculés sur l'historique, à la dernière séance collectée (" + str(len(lignes))
            + " autres ; avec le cours, la variation du jour et les capitaux moyens, les 13 calculés par RITA) :\n"
            + "\n".join(lignes)
            + "\nCes indicateurs sont des faits à décrire, jamais des signaux : ne tire d'aucun d'eux une "
            "recommandation d'achat ou de vente, ni un pronostic ; un RSI ou une moyenne mobile se citent "
            "comme des mesures, sans dire ce qu'il faudrait faire.")


def construire_prompt(ticker: str, price: float, change_pct: float,
                      adtv20: float | None, currency: str,
                      fraicheur_jours: int = 0,
                      cotation_perimee: bool = False,
                      passages: list[dict] | None = None,
                      indicateurs: dict | None = None) -> str:
    """Le prompt du rédacteur, sans appel au modèle.

    Extrait de `generate_briefing` le 03/10/2026 pour le banc C7 (`evals/benchmark_fournisseurs.py`) :
    les fournisseurs se comparent sur le prompt réel, pas sur une copie qui dériverait. Mêmes arguments,
    même texte ; `generate_briefing` l'appelle puis appelle le modèle.

    Args:
        voir `generate_briefing`.
    """
    direction = "hausse" if change_pct >= 0 else "baisse"
    # Carte #57 (03/10/2026) : `adtv20` est AVG(volume × clôture), des CAPITAUX en devise, pas un nombre de
    # titres. Nommé « volume moyen » jusqu'ici, le modèle écrivait « 299 millions d'unités ». Le nom dit la mesure.
    capitaux_moyens = f"{adtv20:,.0f} {currency}" if adtv20 is not None else "non disponible"

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
    bloc_indicateurs = _bloc_indicateurs(indicateurs, currency)

    prompt = f"""{ROLE_REDACTEUR}

Données de la dernière séance collectée :
- Action : {ticker}
- Cours de clôture : {price} {currency}
- Variation sur 1 jour : {change_pct}% ({direction})
- Capitaux échangés en moyenne par séance sur 20 séances : {capitaux_moyens}{avertissement}{bloc_indicateurs}{articles}

{CONSIGNES_REDACTION}"""

    return prompt


def generate_briefing(ticker: str, price: float, change_pct: float,
                      adtv20: float | None, currency: str,
                      fraicheur_jours: int = 0,
                      cotation_perimee: bool = False,
                      passages: list[dict] | None = None,
                      indicateurs: dict | None = None) -> str:
    """Rédige un briefing français à partir des données lues en base et des articles.

    Args:
        ticker: code boursier, ex. 'MC.PA'.
        price: cours de la dernière séance collectée.
        change_pct: performance sur 1 jour, en pourcentage.
        adtv20: capitaux échangés en moyenne par séance sur 20 séances (AVG(volume × clôture), en devise
            de la valeur). `None` si l'historique est trop court.
        currency: devise de la valeur, lue dans `valeur.devise`.
        fraicheur_jours: âge de la cotation, en jours.
        cotation_perimee: vrai au-delà de 40 jours — la valeur est probablement radiée.
        passages: articles retrouvés par le RAG. Liste vide ou `None` = aucun article,
            et le prompt interdit alors explicitement d'en inventer.
        indicateurs: le dictionnaire du scout (13 indicateurs) ; `None` = prompt d'avant le 03/10/2026.

    Returns:
        Briefing en français, 3 à 5 phrases.
    """
    prompt = construire_prompt(ticker, price, change_pct, adtv20, currency,
                               fraicheur_jours, cotation_perimee, passages, indicateurs)
    return generer_texte(prompt, max_tokens=500)
