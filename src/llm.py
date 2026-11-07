"""Appel au modèle : les fournisseurs nommés par `LLM_ORDRE`, essayés dans l'ordre (Foundry seul par défaut).

Trois fournisseurs sont codés (Foundry, Anthropic, OpenRouter). Depuis le 31/10/2026, l'ordre par défaut est
`foundry` (règle UE seule, décision du 11/10) : Anthropic et OpenRouter ne sont appelés que si `LLM_ORDRE` les nomme.

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
from dataclasses import dataclass

import httpx
from anthropic import Anthropic

from monitorage import compteurs
from src import traces
from src.traces import Reponse

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# Mistral, pour le banc C7 seulement (07/11/2026, repris de la PR #88) : hors de la cascade tant que son contrat n'est
# pas lu. L'adresse européenne est écrite ici, pas dans un réglage : une variable mal posée ne peut pas sortir de l'UE.
MISTRAL_HOTE = "api.eu.mistral.ai"
MISTRAL_URL = f"https://{MISTRAL_HOTE}/v1/chat/completions"


def _ordre_fournisseurs() -> list[str]:
    # Azure seul par défaut (règle UE seule, CONTINUITE.md, décision du 11/10) : l'ancien défaut gardait Anthropic et
    # OpenRouter en repli, et la production l'a pris (conteneur lu le 31/10). Mistral viendra en second après la
    # lecture de son contrat (PR #88) ; d'ici là, un autre ordre ne s'obtient qu'en posant `LLM_ORDRE`.
    ordre = os.getenv("LLM_ORDRE", "foundry")
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
        # Large 3 et non Large 4 (07/11) : Large 4 réfléchit sur tout le budget du rédacteur, sans texte (test_llm_mistral).
        "mistral": os.getenv("MISTRAL_MODEL", "mistral-large-2512"),
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


def _appel_mistral(prompt: str, max_tokens: int) -> Reponse:
    """Mistral par son adresse européenne (chat completions, même forme que Foundry), sans SDK. Banc C7 seulement.

    `MISTRAL_API_KEY` absente lève `KeyError` : c'est « indisponible ». Le réglage de réflexion n'est envoyé que si
    `MISTRAL_REASONING_EFFORT` le demande (low, medium, high, pour Large 4) : Large 3 le refuse (400), et `none` n'est
    plus accepté par Mistral depuis le 10/10 (mesuré le 07/11)."""
    corps = {"model": _modele_prevu("mistral"), "max_tokens": max_tokens,
             "messages": [{"role": "user", "content": prompt}]}
    if os.getenv("MISTRAL_REASONING_EFFORT"):
        corps["reasoning_effort"] = os.environ["MISTRAL_REASONING_EFFORT"]
    reponse = httpx.post(
        MISTRAL_URL,
        headers={"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"},
        json=corps,
        timeout=60.0,
    )
    reponse.raise_for_status()
    corps = reponse.json()
    usage = corps.get("usage") or {}
    return Reponse(
        texte=_texte_mistral(corps["choices"][0]["message"]["content"]),
        modele=corps.get("model"),
        usage={"input": usage.get("prompt_tokens", 0), "output": usage.get("completion_tokens", 0)}
        if usage else None,
        origine=MISTRAL_HOTE,
    )


def _texte_mistral(contenu) -> str:
    """Une chaîne telle quelle ; une liste de blocs (modèle à raisonnement), ses seuls blocs `text`, jamais la
    réflexion. Sans aucun texte, `ValueError` : une panne du fournisseur, pas une réponse."""
    if isinstance(contenu, str):
        return contenu
    texte = "".join(b.get("text", "") for b in contenu or [] if isinstance(b, dict) and b.get("type") == "text")
    if not texte.strip():
        raise ValueError("Réponse Mistral sans texte (réflexion seule ou vide).")
    return texte


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
            # Sprint 5 (étape 1) : une réponse tronquée ou mal formée est facturée aussi ; ses jetons comptent.
            compteurs.ajouter_jetons(usage.get("prompt_tokens"), usage.get("completion_tokens"))
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


def _resume_erreur(erreur: BaseException) -> str:
    """Le type de l'erreur, et son code HTTP s'il y en a un ; jamais son message, qui peut recopier le prompt (sprint 4,
    D9 ; revue de sécurité automatique du commit dc2b323). Le code suffit à distinguer une clé refusée (401), un quota
    atteint (429) ou une panne du fournisseur (5xx)."""
    code = getattr(getattr(erreur, "response", None), "status_code", None)
    return f"{type(erreur).__name__} (HTTP {code})" if code else type(erreur).__name__


@dataclass
class ResultatTexte:
    """Le texte, et qui l'a écrit (refonte 001, exigence R4 : l'écran du briefing le montre).

    `modele` est celui que le fournisseur a renvoyé (`Reponse.modele`), `None` s'il ne le dit pas : jamais celui que la
    configuration annonce (`_modele_prevu`). Une tentative ne garde que le nom du fournisseur et son issue,
    `{"fournisseur": str, "reussi": bool}`, jamais le message de son erreur, qui peut recopier le prompt (sprint 4, D9).
    """
    texte: str
    fournisseur: str
    modele: str | None
    tentatives: list[dict]


class AucunFournisseur(RuntimeError):
    """Tous les fournisseurs de `LLM_ORDRE` ont échoué.

    Hérite de `RuntimeError` : les appelants qui l'attrapaient déjà restent justes. `/briefing` la reconnaît pour
    répondre 503 au lieu de 500 (refonte 001, tâche 3). `tentatives` a la même forme que dans `ResultatTexte`.
    """

    def __init__(self, message: str, tentatives: list[dict]):
        super().__init__(message)
        self.tentatives = tentatives


def generer_texte(prompt: str, max_tokens: int = 500) -> str:
    """Le texte seul, pour les appelants qui n'ont pas besoin de savoir qui a répondu."""
    return generer_texte_detaille(prompt, max_tokens).texte


def generer_texte_detaille(prompt: str, max_tokens: int = 500) -> ResultatTexte:
    erreurs: list[str] = []
    tentatives: list[dict] = []
    module = sys.modules[__name__]
    tentative = 0
    texte_final: str | None = None
    fournisseur_final: str | None = None
    modele_final: str | None = None
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
                    # Sprint 5 (étape 1) : les jetons de la tentative qui en rend (monitorage/compteurs.py).
                    if reponse.usage:
                        compteurs.ajouter_jetons(reponse.usage.get("input"), reponse.usage.get("output"))
                    logger.info("Réponse obtenue via %s", nom)
                except Exception as erreur:  # noqa: BLE001, on passe au fournisseur suivant
                    traces.echouer(gen, erreur)
                    erreurs.append(f"{nom} : {_resume_erreur(erreur)}")
                    tentatives.append({"fournisseur": nom, "reussi": False})
                    logger.warning("Fournisseur %s indisponible : %s", nom, _resume_erreur(erreur))
                    continue
            tentatives.append({"fournisseur": nom, "reussi": True})
            texte_final, fournisseur_final, modele_final = reponse.texte, nom, reponse.modele
            break
        if texte_final is None:
            traces.echouer(racine, RuntimeError("aucun fournisseur disponible"))
    # Le flush vient APRÈS la fermeture du span racine : un span encore ouvert n'est pas exporté.
    traces.vider()
    if texte_final is None:
        raise AucunFournisseur("Aucun fournisseur LLM disponible." + chr(10) + chr(10).join(erreurs), tentatives)
    return ResultatTexte(texte=texte_final, fournisseur=fournisseur_final, modele=modele_final, tentatives=tentatives)
