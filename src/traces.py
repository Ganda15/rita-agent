"""Traçage des appels au modèle : Langfuse Cloud, région UE (C11, carte #39).

Décision d'Era du 28/09/2026 (`CONTINUITE.md` D, registre RGPD §T3) : Langfuse Cloud,
région UE, palier gratuit. Mesuré avant de décider : le prompt du rédacteur ne contient
aucune donnée personnelle (ticker, cours, ADTV20, passages de presse), donc rien à masquer
aujourd'hui ; la condition est écrite dans le registre pour le jour où ça changerait.

**Pourquoi un module séparé de `src/llm.py`.** Le traçage ne doit jamais faire échouer un
briefing : sans clés (CI, tests, poste sans compte), tout ici est un no-op silencieux. Et un
seul endroit décide « actif ou non », au lieu de trois `if` dans trois fournisseurs.

**Ce qu'une trace porte** : une *génération* par tentative de la cascade, avec le fournisseur,
le modèle, le prompt en entrée, le texte en sortie, l'usage en tokens quand le fournisseur le
donne (Langfuse en déduit le coût), et `level="ERROR"` avec le message quand une tentative
échoue : c'est le repli d'un fournisseur à l'autre rendu visible, le cœur de C11.

Variables lues (jamais écrites ici) : LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY,
LANGFUSE_HOST (ou LANGFUSE_BASE_URL), LANGFUSE_TRACING_ENABLED (`false` coupe tout).
SDK vérifié le 02/10/2026 : langfuse 4.12.0, `Langfuse(base_url=…, tracing_enabled=…)`,
`start_as_current_observation(as_type="generation", …)`, `update(…)`, `flush()`.
"""
from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from dataclasses import dataclass

logger = logging.getLogger(__name__)

HOTE_UE = "https://cloud.langfuse.com"

_client = None
_resolu = False


@dataclass
class Reponse:
    """Ce qu'un fournisseur rend : le texte, et si possible le modèle réel et l'usage.

    `usage` suit le vocabulaire Langfuse : {"input": n, "output": m} en tokens.
    Un fournisseur qui ne rend qu'une chaîne reste accepté par `generer_texte`.
    """
    texte: str
    modele: str | None = None
    usage: dict | None = None


def reinitialiser() -> None:
    """Oublie le client résolu : les tests changent les variables entre deux cas."""
    global _client, _resolu
    _client, _resolu = None, False


def _actif() -> bool:
    interrupteur = os.getenv("LANGFUSE_TRACING_ENABLED", "true").strip().lower()
    if interrupteur in {"false", "0", "no", "non", "off"}:
        return False
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


def client_traces():
    """Le client Langfuse, ou `None` si le traçage est absent ou coupé. Résolu une fois."""
    global _client, _resolu
    if _resolu:
        return _client
    _resolu = True
    if not _actif():
        return None
    try:
        from langfuse import Langfuse

        hote = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL") or HOTE_UE
        _client = Langfuse(base_url=hote)
    except Exception as erreur:  # noqa: BLE001, l'observabilité ne fait pas tomber le service
        logger.warning("Traçage Langfuse indisponible, on continue sans : %s", erreur)
        _client = None
    return _client


@contextmanager
def appel(prompt: str):
    """Ouvre le trace d'UN appel au rédacteur : un span racine `briefing-llm`.

    Les tentatives (une génération par fournisseur) se rangent dessous. Mesuré le 02/10/2026
    avant cette structure : trois appels donnaient neuf lignes racines dans Langfuse, une par
    fournisseur, illisibles. Une ligne par briefing, qui se déplie, est ce qu'un jury peut lire.
    Rend `None` si le traçage est coupé.
    """
    client = client_traces()
    if client is None:
        yield None
        return
    with client.start_as_current_observation(as_type="span", name="briefing-llm", input=prompt) as racine:
        yield racine


def terminer_appel(racine, texte: str) -> None:
    """Pose la sortie finale sur le trace : ce que le rédacteur a vraiment reçu."""
    if racine is not None:
        racine.update(output=texte)


@contextmanager
def generation(fournisseur: str, modele: str, prompt: str, tentative: int):
    """Ouvre une génération Langfuse pour une tentative ; rend `None` si le traçage est coupé.

    Nommée par fournisseur (`llm-anthropic`…) : dans l'arbre du trace, on lit d'un coup qui a
    répondu et qui a échoué avant.
    """
    client = client_traces()
    if client is None:
        yield None
        return
    with client.start_as_current_observation(
        as_type="generation",
        name=f"llm-{fournisseur}",
        model=modele,
        input=prompt,
        metadata={"fournisseur": fournisseur, "tentative": tentative},
    ) as gen:
        yield gen


def terminer(gen, reponse: Reponse) -> None:
    """Complète la génération avec la sortie, le modèle réel et l'usage s'ils existent."""
    if gen is None:
        return
    details: dict = {"output": reponse.texte}
    if reponse.modele:
        details["model"] = reponse.modele
    if reponse.usage:
        details["usage_details"] = reponse.usage
    gen.update(**details)


def echouer(gen, erreur: BaseException) -> None:
    """Marque la tentative en erreur ; le message est tronqué, jamais la clé d'API."""
    if gen is None:
        return
    gen.update(level="ERROR", status_message=f"{type(erreur).__name__}: {erreur}"[:300])


def vider() -> None:
    """Envoie ce qui attend. Appelé une fois par `generer_texte` : l'API vit longtemps,
    un script court s'arrête juste après, dans les deux cas la trace doit partir."""
    client = client_traces()
    if client is not None:
        client.flush()
