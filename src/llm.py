"""Appel Claude à 3 fournisseurs en cascade (Foundry → Anthropic → OpenRouter)."""
import logging
import os
import sys

import httpx
from anthropic import Anthropic, AnthropicFoundry

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _ordre_fournisseurs() -> list[str]:
    ordre = os.getenv("LLM_ORDRE", "foundry,anthropic,openrouter")
    return [nom.strip() for nom in ordre.split(",") if nom.strip()]


def _appel_foundry(prompt: str, max_tokens: int) -> str:
    client = AnthropicFoundry(
        api_key=os.environ["AZURE_FOUNDRY_API_KEY"],
        base_url=os.environ["AZURE_FOUNDRY_ENDPOINT"],
    )
    reponse = client.messages.create(
        model=os.getenv("AZURE_FOUNDRY_DEPLOYMENT", "claude-opus-4-8"),
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return reponse.content[0].text


def _appel_anthropic(prompt: str, max_tokens: int) -> str:
    client = Anthropic()
    reponse = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5"),
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return reponse.content[0].text


def _appel_openrouter(prompt: str, max_tokens: int) -> str:
    reponse = httpx.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json={
            "model": os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4.5"),
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60.0,
    )
    reponse.raise_for_status()
    return reponse.json()["choices"][0]["message"]["content"]


_NOMS_VALIDES = {"foundry", "anthropic", "openrouter"}


def generer_texte(prompt: str, max_tokens: int = 500) -> str:
    erreurs: list[str] = []
    module = sys.modules[__name__]
    for nom in _ordre_fournisseurs():
        if nom not in _NOMS_VALIDES:
            logger.warning("Fournisseur inconnu ignoré : %s", nom)
            continue
        appel = getattr(module, f"_appel_{nom}")
        try:
            texte = appel(prompt, max_tokens)
            logger.info("Réponse obtenue via %s", nom)
            return texte
        except Exception as erreur:
            erreurs.append(f"{nom} : {erreur}")
            logger.warning("Fournisseur %s indisponible — %s", nom, erreur)
    raise RuntimeError("Aucun fournisseur LLM disponible.\n" + "\n".join(erreurs))
