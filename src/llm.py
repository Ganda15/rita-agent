"""Appel au modèle, 3 fournisseurs en cascade (Foundry → Anthropic → OpenRouter).

Depuis le 03/10/2026, Azure AI Foundry sert un point de terminaison **compatible OpenAI**
(`.../openai/v1`, déploiement `gpt-5.4`, ressource d'Era, gratuite pour lui) : un modèle d'un
autre éditeur que Claude, ce qui donne au banc C7 une vraie comparaison. Anthropic en direct et
OpenRouter servent Claude.

Depuis le 02/10/2026, chaque tentative est tracée dans Langfuse (`src/traces.py`, C11,
carte #39) : fournisseur, modèle, prompt, sortie, usage en tokens, et l'erreur quand un
fournisseur échoue. Sans clés Langfuse, le traçage est un no-op : la cascade ne change pas.
"""
import logging
import os
import sys

import httpx
from anthropic import Anthropic

from src import traces
from src.traces import Reponse

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _ordre_fournisseurs() -> list[str]:
    ordre = os.getenv("LLM_ORDRE", "foundry,anthropic,openrouter")
    return [nom.strip() for nom in ordre.split(",") if nom.strip()]


def _modele_prevu(nom: str) -> str:
    """Le modèle que la configuration annonce pour un fournisseur, avant l'appel.

    Sert à ouvrir la trace : le modèle réellement servi, s'il diffère, est écrit à la
    fin par `Reponse.modele`.
    """
    return {
        "foundry": os.getenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-5.4"),
        "anthropic": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5"),
        "openrouter": os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4.5"),
    }[nom]


def _usage_anthropic(reponse) -> dict | None:
    usage = getattr(reponse, "usage", None)
    if usage is None:
        return None
    return {"input": getattr(usage, "input_tokens", 0), "output": getattr(usage, "output_tokens", 0)}


def _appel_foundry(prompt: str, max_tokens: int) -> Reponse:
    """Azure AI Foundry par son point compatible OpenAI (chat completions), comme OpenRouter.

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
    usage = corps.get("usage") or {}
    return Reponse(
        texte=corps["choices"][0]["message"]["content"],
        modele=corps.get("model"),
        usage={"input": usage.get("prompt_tokens", 0), "output": usage.get("completion_tokens", 0)}
        if usage else None,
        # Un déploiement « Global Standard » peut être traité dans n'importe quelle région Azure :
        # la région est le résultat de l'appel, pas une propriété de la ressource.
        origine=(getattr(reponse, "headers", None) or {}).get("x-ms-region"),
    )


def _appel_anthropic(prompt: str, max_tokens: int) -> Reponse:
    client = Anthropic()
    reponse = client.messages.create(
        model=_modele_prevu("anthropic"),
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return Reponse(texte=reponse.content[0].text, modele=getattr(reponse, "model", None),
                   usage=_usage_anthropic(reponse))


def _appel_openrouter(prompt: str, max_tokens: int) -> Reponse:
    reponse = httpx.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json={
            "model": _modele_prevu("openrouter"),
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60.0,
    )
    reponse.raise_for_status()
    corps = reponse.json()
    usage = corps.get("usage") or {}
    return Reponse(
        texte=corps["choices"][0]["message"]["content"],
        modele=corps.get("model"),
        usage={"input": usage.get("prompt_tokens", 0), "output": usage.get("completion_tokens", 0)}
        if usage else None,
        # OpenRouter route vers plusieurs hébergeurs et nomme celui qui a répondu.
        origine=corps.get("provider"),
    )


_NOMS_VALIDES = {"foundry", "anthropic", "openrouter"}


# --- Sprint 3, tâche A3 : le parcours des questions, en JSON, par Azure seul ---------------------------------------
# `generer_texte` (la cascade du briefing) ne change pas. Le parcours des questions n'appelle qu'Azure, le seul
# fournisseur approuvé en zone UE (décision D5), sans repli : une panne est une erreur, jamais un autre fournisseur.
# Aucun texte ne part dans les traces (décision D2) : ni le prompt (qui contient la question), ni la réponse, ni le
# message d'une erreur, qui peut recopier l'un ou l'autre. Seuls le type de l'erreur et des comptes sont tracés.

class FournisseurIndisponible(RuntimeError):
    """Le fournisseur approuvé n'a pas pu répondre. Le message ne porte que le type de l'erreur, jamais le prompt."""


class ReponseTronquee(RuntimeError):
    """Le modèle a atteint la limite de longueur : la réponse est incomplète, donc inutilisable."""


def generer_json(prompt: str, schema: dict, nom_schema: str, max_tokens: int = 800) -> str:
    """Demande à Azure une réponse au format `schema` (mode strict) et rend le JSON brut, à valider par l'appelant.

    Lève `FournisseurIndisponible` (configuration absente, erreur HTTP, délai dépassé, réponse illisible) ou
    `ReponseTronquee` (`finish_reason == "length"`). Les deux sont levées APRÈS la fermeture de l'étape de trace :
    aucune exception portant un texte ne la traverse.
    """
    modele = _modele_prevu("foundry")
    contenu: str | None = None
    panne: str | None = None
    tronquee = False
    with traces.etape("llm-foundry", genre="generation", modele=modele) as etape_llm:
        try:
            base = os.environ["AZURE_FOUNDRY_ENDPOINT"].rstrip("/")
            reponse = httpx.post(
                f"{base}/chat/completions",
                headers={"Authorization": f"Bearer {os.environ['AZURE_FOUNDRY_API_KEY']}"},
                json={
                    "model": modele,
                    "max_completion_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_schema",
                                        "json_schema": {"name": nom_schema, "strict": True, "schema": schema}},
                },
                timeout=60.0,
            )
            reponse.raise_for_status()
            corps = reponse.json()
            choix = corps["choices"][0]
            tronquee = choix.get("finish_reason") == "length"
            contenu = choix["message"]["content"]
            usage = corps.get("usage") or {}
            traces.terminer_etape(etape_llm, metadata={
                "modele": corps.get("model") or modele,
                "region": (getattr(reponse, "headers", None) or {}).get("x-ms-region"),
                "jetons_entree": usage.get("prompt_tokens"),
                "jetons_sortie": usage.get("completion_tokens"),
                "tronquee": tronquee,
            })
        except Exception as erreur:  # noqa: BLE001, toute panne devient une erreur propre, sans son message
            panne = type(erreur).__name__
            traces.terminer_etape(etape_llm, level="ERROR", status_message=panne)
    traces.vider()
    if panne is not None:
        logger.warning("Fournisseur foundry indisponible pour une question : %s", panne)
        raise FournisseurIndisponible(f"fournisseur indisponible ({panne})")
    if tronquee or contenu is None:
        raise ReponseTronquee("reponse tronquee par la limite de longueur")
    return contenu


def generer_texte(prompt: str, max_tokens: int = 500) -> str:
    erreurs: list[str] = []
    module = sys.modules[__name__]
    tentative = 0
    texte_final: str | None = None
    # Un appel = un trace Langfuse (span racine), les tentatives dessous. Sans clés,
    # `appel` et `generation` rendent None et tout ce qui suit est un no-op (src/traces.py).
    # Sprint 4 (B3, D9) : ni le prompt ni la réponse ne partent vers la trace, seulement des métadonnées.
    with traces.appel() as racine:
        for nom in _ordre_fournisseurs():
            if nom not in _NOMS_VALIDES:
                logger.warning("Fournisseur inconnu ignoré : %s", nom)
                continue
            tentative += 1
            fonction = getattr(module, f"_appel_{nom}")
            with traces.generation(nom, _modele_prevu(nom), tentative) as gen:
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
            break
        if texte_final is None:
            traces.echouer(racine, RuntimeError("aucun fournisseur disponible"))
    # Le flush vient APRÈS la fermeture du span racine : un span encore ouvert n'est pas exporté.
    traces.vider()
    if texte_final is None:
        raise RuntimeError("Aucun fournisseur LLM disponible." + chr(10) + chr(10).join(erreurs))
    return texte_final
