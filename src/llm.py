"""Appel au modèle, cascade de fournisseurs approuvés UE (Foundry → Mistral).

Depuis le 03/10/2026, Azure AI Foundry sert un point de terminaison **compatible OpenAI**
(`.../openai/v1`, ressource d'Era, gratuite pour lui). Depuis le 09/10/2026, le déploiement est
`gpt-5.4-dzs-eu` : même modèle `gpt-5.4`, en Data Zone Standard EU.

Carte #82, règle « UE seule » d'Era : les replis Anthropic et OpenRouter, sans garantie de région,
sont retirés. Le repli est Mistral, par son adresse européenne, écrite ici et non dans un réglage.
Un nom inconnu dans `LLM_ORDRE` (dont `anthropic` ou `openrouter`) est ignoré avec un avertissement.

Depuis le 02/10/2026, chaque tentative est tracée dans Langfuse (`src/traces.py`, C11,
carte #39) : fournisseur, modèle, prompt, sortie, usage en tokens, et l'erreur quand un
fournisseur échoue. Sans clés Langfuse, le traçage est un no-op : la cascade ne change pas.
"""
import logging
import os
import sys

import httpx

from src import traces
from src.traces import Reponse

logger = logging.getLogger(__name__)

# Adresse européenne de Mistral, écrite dans le code (carte #82) : une variable mal posée ne peut pas envoyer la
# cascade hors de l'UE. Mistral ne renvoie aucun en-tête de région (sonde du 10/10/2026) : l'origine notée est
# l'adresse appelée, et le lieu de traitement se prouve par son contrat.
MISTRAL_HOTE = "api.eu.mistral.ai"
MISTRAL_URL = f"https://{MISTRAL_HOTE}/v1/chat/completions"


def _ordre_fournisseurs() -> list[str]:
    ordre = os.getenv("LLM_ORDRE", "foundry,mistral")
    return [nom.strip() for nom in ordre.split(",") if nom.strip()]


def _modele_prevu(nom: str) -> str:
    """Le modèle que la configuration annonce pour un fournisseur, avant l'appel.

    Sert à ouvrir la trace : le modèle réellement servi, s'il diffère, est écrit à la
    fin par `Reponse.modele`.
    """
    return {
        # `gpt-5.4` (Global Standard) a été supprimé le 09/10/2026 : la valeur par défaut vise le déploiement qui existe.
        "foundry": os.getenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-5.4-dzs-eu"),
        # Large 4 plutôt que Large 3 (`mistral-large-2512`) : mesure du 10/10/2026, sans date inventée, même coût à 0,01
        # centime près (evidence/C8/preuve-briefing-mistral-2026-10-10.md).
        "mistral": os.getenv("MISTRAL_MODEL", "mistral-large-4-0"),
    }[nom]


def _usage_openai(corps: dict) -> dict | None:
    """L'usage en tokens d'une réponse au format chat completions (Foundry et Mistral)."""
    usage = corps.get("usage") or {}
    if not usage:
        return None
    return {"input": usage.get("prompt_tokens", 0), "output": usage.get("completion_tokens", 0)}


def _appel_foundry(prompt: str, max_tokens: int) -> Reponse:
    """Azure AI Foundry par son point compatible OpenAI (chat completions), comme Mistral.

    `AZURE_FOUNDRY_ENDPOINT` se termine par `/openai/v1` ; le déploiement sert de nom de modèle.
    Une variable absente lève `KeyError` : c'est « indisponible », la cascade passe au suivant.
    Pas de dépendance `openai` : httpx suffit, et une bibliothèque de moins est une surface de moins."""
    base = os.environ["AZURE_FOUNDRY_ENDPOINT"].rstrip("/")
    reponse = httpx.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['AZURE_FOUNDRY_API_KEY']}"},
        json={
            "model": _modele_prevu("foundry"),
            # Les modèles GPT-5 refusent `max_tokens` (400 « unsupported parameter », mesuré le 03/10) :
            # le nom est `max_completion_tokens` sur ce point de terminaison.
            "max_completion_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60.0,
    )
    reponse.raise_for_status()
    corps = reponse.json()
    return Reponse(
        texte=corps["choices"][0]["message"]["content"],
        modele=corps.get("model"),
        usage=_usage_openai(corps),
        # Data Zone Standard EU depuis le 09/10/2026 : l'en-tête `x-ms-region` dit, appel par appel, quelle région
        # a traité la demande. Une région supposée n'est pas une région mesurée.
        origine=(getattr(reponse, "headers", None) or {}).get("x-ms-region"),
    )


def _appel_mistral(prompt: str, max_tokens: int) -> Reponse:
    """Mistral par son adresse européenne (chat completions, même forme que Foundry), sans SDK.

    `MISTRAL_API_KEY` absente lève `KeyError` : c'est « indisponible », la cascade passe au suivant.
    `reasoning_effort: "none"` : Large 4 est un modèle à raisonnement ; sans ce réglage, sa réflexion consommait les
    500 jetons du rédacteur et il ne rendait aucun texte (mesuré le 10/10/2026)."""
    reponse = httpx.post(
        MISTRAL_URL,
        headers={"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"},
        json={
            "model": _modele_prevu("mistral"),
            "max_tokens": max_tokens,
            "reasoning_effort": "none",
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60.0,
    )
    reponse.raise_for_status()
    corps = reponse.json()
    return Reponse(
        texte=_texte_mistral(corps["choices"][0]["message"]["content"]),
        modele=corps.get("model"),
        usage=_usage_openai(corps),
        origine=MISTRAL_HOTE,
    )


def _texte_mistral(contenu) -> str:
    """Le texte d'une réponse Mistral : une chaîne telle quelle ; une liste de blocs (modèle à raisonnement), ses
    seuls blocs `text`, jamais la réflexion. Sans aucun texte, `ValueError` : la cascade passe au suivant au lieu
    d'un 500 plus loin dans le garde-fou."""
    if isinstance(contenu, str):
        return contenu
    texte = "".join(b.get("text", "") for b in contenu or [] if isinstance(b, dict) and b.get("type") == "text")
    if not texte.strip():
        raise ValueError("Réponse Mistral sans texte (réflexion seule ou vide).")
    return texte


# Les seuls fournisseurs approuvés UE (carte #82). Tout autre nom de `LLM_ORDRE` est ignoré par la cascade.
_NOMS_VALIDES = {"foundry", "mistral"}


def generer_texte(prompt: str, max_tokens: int = 500) -> str:
    erreurs: list[str] = []
    module = sys.modules[__name__]
    tentative = 0
    texte_final: str | None = None
    # Un appel = un trace Langfuse (span racine), les tentatives dessous. Sans clés,
    # `appel` et `generation` rendent None et tout ce qui suit est un no-op (src/traces.py).
    with traces.appel(prompt) as racine:
        for nom in _ordre_fournisseurs():
            if nom not in _NOMS_VALIDES:
                logger.warning("Fournisseur inconnu ou non approuvé UE, ignoré : %s", nom)
                continue
            tentative += 1
            fonction = getattr(module, f"_appel_{nom}")
            with traces.generation(nom, _modele_prevu(nom), prompt, tentative) as gen:
                try:
                    resultat = fonction(prompt, max_tokens)
                    # Un fournisseur (ou un test) peut rendre une simple chaîne : accepté.
                    reponse = resultat if isinstance(resultat, Reponse) else Reponse(texte=resultat)
                    traces.terminer(gen, reponse)
                    logger.info("Réponse obtenue via %s", nom)
                except Exception as erreur:  # noqa: BLE001, on passe au fournisseur suivant
                    traces.echouer(gen, erreur)
                    erreurs.append(f"{nom} : {erreur}")
                    logger.warning("Fournisseur %s indisponible — %s", nom, erreur)
                    continue
            texte_final = reponse.texte
            traces.terminer_appel(racine, texte_final)
            break
        if texte_final is None:
            traces.echouer(racine, RuntimeError("aucun fournisseur disponible"))
    # Le flush vient APRÈS la fermeture du span racine : un span encore ouvert n'est pas exporté.
    traces.vider()
    if texte_final is None:
        raise RuntimeError("Aucun fournisseur LLM disponible." + chr(10) + chr(10).join(erreurs))
    return texte_final
