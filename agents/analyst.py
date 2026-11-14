"""Rédacteur — génère le briefing en français via src/llm.py (C8, C9, C10)."""
import logging
from dataclasses import replace
from datetime import date

from agents.mise_en_forme import sans_marques_markdown
from guardrails.injection import neutraliser
from guardrails.normalisation import sans_invisibles
from src.llm import ResultatTexte, generer_texte_detaille

logger = logging.getLogger(__name__)

# Les parties fixes du prompt du rédacteur (sprint 4, tâche B2) : le contrôle de fuite (`guardrails/sortie.py`,
# `verifier_fuite`) refuse un briefing qui en recopierait un morceau. `construire_prompt` les assemble sans changer un
# caractère du prompt d'avant.
ROLE_REDACTEUR = ("Tu es un analyste financier français qui rédige des briefings courts pour des investisseurs "
                  "particuliers.")
# Option B (décision du 11/10, CONTINUITE.md ; appliquée le 06/11) : la consigne n° 3 ne demande plus un « point à
# surveiller pour la séance suivante », qui poussait au pronostic ; la séance porte sa date, lue dans les données.
CONSIGNES_REDACTION = """Rédige un briefing de 3 à 5 phrases en français qui :
1. Résume la performance de la séance, en citant sa date si elle est fournie, avec un ton factuel
2. Indique le niveau de variation (faible / modérée / forte)
3. Relève un élément observable à suivre, tiré des seules données fournies, sans présenter un cours comme un seuil

Règles strictes :
- AUCUNE recommandation d'achat ou de vente
- Pas d'invention de chiffres ou d'événements non fournis
- Ne décris pas une durée ou une tendance que les performances fournies ne montrent pas
- N'écris aucune date de séance si elle n'est pas fournie
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

    # Le modèle reçoit le texte de l'article sans ses caractères invisibles (catégorie Unicode Cf,
    # `guardrails/normalisation.py`) ; le passage conservé, lui, reste celui d'origine (revue de sécurité du 07/11).
    lignes = [f"{i}. [{sans_invisibles(p['source'])}, {sans_invisibles(str(p['publie_le']))}] "
              f"{sans_invisibles(p['texte'])}"
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


def _date_seance(indicateurs: dict | None) -> str | None:
    """La date de la dernière séance collectée, au format JJ/MM/AAAA, ou None si les données ne la donnent pas.

    Option B (décision du 11/10, CONTINUITE.md) : la date vient des données (`indicateurs["date_cours"]`, chaîne ISO
    rendue par le scout, ou objet `date`), jamais de l'horloge. Absente ou illisible, elle n'est pas devinée.
    """
    valeur = (indicateurs or {}).get("date_cours")
    if isinstance(valeur, date):
        return valeur.strftime("%d/%m/%Y")
    if isinstance(valeur, str):
        try:
            return date.fromisoformat(valeur[:10]).strftime("%d/%m/%Y")
        except ValueError:
            return None
    return None


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
    #
    # Sprint 5, étape 8 (critère 1 du contrat, docs/sprint-4/CONTRAT.md § 3) : le prompt ordonnait d'écrire que la valeur
    # était « probablement radiée ». Une cotation ancienne ne prouve pas une radiation : en production, OR.PA n'avait plus
    # de cours parce que la collecte des cours ne tournait pas. Le modèle dit l'âge de la donnée et n'en tire rien.
    if cotation_perimee:
        avertissement = (
            f"\n⚠️ ATTENTION : la dernière cotation disponible date de {fraicheur_jours} jours. "
            "Tu DOIS commencer le briefing en signalant que les cours ne sont pas à jour. "
            "N'en déduis rien sur la cotation de la valeur (ni radiation, ni suspension) : "
            "la cause peut être la collecte des données."
        )
    else:
        avertissement = f"\n- Fraîcheur de la donnée : {fraicheur_jours} jour(s)"

    articles = _bloc_articles(passages)
    bloc_indicateurs = _bloc_indicateurs(indicateurs, currency)
    date_seance = _date_seance(indicateurs) or "non fournie"

    prompt = f"""{ROLE_REDACTEUR}

Données de la dernière séance collectée :
- Action : {ticker}
- Date de la séance : {date_seance}
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
    """Le texte seul, pour les appelants qui n'ont pas besoin de savoir qui l'a écrit (banc C7, essais du sprint 4).

    Mêmes paramètres et même prompt que `generate_briefing_detaille`, dont elle rend `.texte`.
    """
    return generate_briefing_detaille(ticker, price, change_pct, adtv20, currency,
                                      fraicheur_jours, cotation_perimee, passages, indicateurs).texte


def generate_briefing_detaille(ticker: str, price: float, change_pct: float,
                               adtv20: float | None, currency: str,
                               fraicheur_jours: int = 0,
                               cotation_perimee: bool = False,
                               passages: list[dict] | None = None,
                               indicateurs: dict | None = None) -> ResultatTexte:
    """Rédige un briefing français à partir des données lues en base et des articles.

    Args:
        ticker: code boursier, ex. 'MC.PA'.
        price: cours de la dernière séance collectée.
        change_pct: performance sur 1 jour, en pourcentage.
        adtv20: capitaux échangés en moyenne par séance sur 20 séances (AVG(volume × clôture), en devise
            de la valeur). `None` si l'historique est trop court.
        currency: devise de la valeur, lue dans `valeur.devise`.
        fraicheur_jours: âge de la cotation, en jours.
        cotation_perimee: vrai au-delà de 40 jours : les cours ne sont pas à jour (ce qui ne prouve pas une radiation).
        passages: articles retrouvés par le RAG. Liste vide ou `None` = aucun article,
            et le prompt interdit alors explicitement d'en inventer.
        indicateurs: le dictionnaire du scout (13 indicateurs) ; `None` = prompt d'avant le 03/10/2026.

    Returns:
        Le briefing en français (3 à 5 phrases) et qui l'a écrit : fournisseur, modèle renvoyé, tentatives
        (refonte 001, exigence R4 : l'écran du briefing les affiche).
    """
    prompt = construire_prompt(ticker, price, change_pct, adtv20, currency,
                               fraicheur_jours, cotation_perimee, passages, indicateurs)
    resultat = generer_texte_detaille(prompt, max_tokens=500)
    # 14/11/2026 : l'écran affiche le texte tel quel ; les marques Markdown de Mistral (« *BFM Bourse* ») se voyaient.
    # Retirées ici, avant le garde-fou de sortie (api/main.py), qui lit donc exactement le texte affiché. Sans marque,
    # le résultat du fournisseur est rendu tel quel.
    texte = sans_marques_markdown(resultat.texte)
    return resultat if texte == resultat.texte else replace(resultat, texte=texte)
