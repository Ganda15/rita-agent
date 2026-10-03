"""Appel Claude à 3 fournisseurs en cascade (Foundry → Anthropic → OpenRouter).

Depuis le 02/10/2026, chaque tentative est tracée dans Langfuse (`src/traces.py`, C11,
carte #39) : fournisseur, modèle, prompt, sortie, usage en tokens, et l'erreur quand un
fournisseur échoue. Sans clés Langfuse, le traçage est un no-op : la cascade ne change pas.
"""
import logging
import os
import sys

import httpx
from anthropic import Anthropic, AnthropicFoundry

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
        "foundry": os.getenv("AZURE_FOUNDRY_DEPLOYMENT", "claude-opus-4-8"),
        "anthropic": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5"),
        "openrouter": os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4.5"),
    }[nom]


def _usage_anthropic(reponse) -> dict | None:
    usage = getattr(reponse, "usage", None)
    if usage is None:
        return None
    return {"input": getattr(usage, "input_tokens", 0), "output": getattr(usage, "output_tokens", 0)}


def _appel_foundry(prompt: str, max_tokens: int) -> Reponse:
    client = AnthropicFoundry(
        api_key=os.environ["AZURE_FOUNDRY_API_KEY"],
        base_url=os.environ["AZURE_FOUNDRY_ENDPOINT"],
    )
    reponse = client.messages.create(
        model=_modele_prevu("foundry"),
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return Reponse(texte=reponse.content[0].text, modele=getattr(reponse, "model", None),
                   usage=_usage_anthropic(reponse))


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
    )


_NOMS_VALIDES = {"foundry", "anthropic", "openrouter"}


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
                logger.warning("Fournisseur inconnu ignoré : %s", nom)
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
