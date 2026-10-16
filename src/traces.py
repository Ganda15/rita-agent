"""Traçage des appels au modèle : Langfuse Cloud, région UE (C11, carte #39).

Décision d'Era du 28/09/2026 (`CONTINUITE.md` D, registre RGPD §T3) : Langfuse Cloud,
région UE, palier gratuit. Mesuré avant de décider : le prompt du rédacteur ne contient
aucune donnée personnelle (ticker, cours, ADTV20, passages de presse), donc rien à masquer
aujourd'hui ; la condition est écrite dans le registre pour le jour où ça changerait.

**Pourquoi un module séparé de `src/llm.py`.** Le traçage ne doit jamais faire échouer un
briefing : sans clés (CI, tests, poste sans compte), tout ici est un no-op silencieux. Et un
seul endroit décide « actif ou non », au lieu de trois `if` dans trois fournisseurs.

**Et quand Langfuse casse en route** (exportateur injoignable, quota, SDK en erreur) : revue
automatisée de la PR #58 (03/10/2026), un `flush()` qui levait transformait un briefing valide en 500.
Depuis, chaque opération Langfuse passe par `_observation`, `_maj` ou `_flush`, qui avalent
l'erreur et laissent une ligne WARNING. L'isolation va dans un seul sens : une erreur du
métier remonte toujours, une erreur du traçage jamais.

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
import sys
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
    # Où l'appel a réellement été traité : région Azure (en-tête `x-ms-region`) ou point de sortie
    # d'OpenRouter (champ `provider`). None quand le fournisseur ne le dit pas : on n'invente pas.
    origine: str | None = None


def reinitialiser() -> None:
    """Oublie le client résolu : les tests changent les variables entre deux cas."""
    global _client, _resolu
    _client, _resolu = None, False


def _actif() -> bool:
    interrupteur = os.getenv("LANGFUSE_TRACING_ENABLED", "true").strip().lower()
    if interrupteur in {"false", "0", "no", "non", "off"}:
        return False
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


def _signaler(operation: str, erreur: BaseException) -> None:
    """Une panne du traçage vaut une ligne WARNING, jamais une exception : le message est
    tronqué et ne contient aucune clé (le SDK ne les met pas dans ses erreurs)."""
    logger.warning("Langfuse : %s a echoue, le briefing continue sans trace : %s",
                   operation, f"{type(erreur).__name__}: {erreur}"[:200])


@contextmanager
def _observation(client, **options):
    """Ouvre une observation Langfuse sans jamais laisser une erreur du SDK remonter.

    Si l'ouverture échoue, le corps reçoit `None` et tout ce qui suit est un no-op. Si la
    fermeture échoue, on la signale et on continue. Une exception du corps (le métier), elle,
    traverse : on la transmet au SDK pour qu'il marque l'observation, puis on la relance.
    """
    try:
        gestionnaire = client.start_as_current_observation(**options)
        observation = gestionnaire.__enter__()
    except Exception as erreur:  # noqa: BLE001
        _signaler(f"l'ouverture de {options.get('name')!r}", erreur)
        yield None
        return
    try:
        yield observation
    except BaseException:
        try:
            gestionnaire.__exit__(*sys.exc_info())
        except Exception as erreur:  # noqa: BLE001
            _signaler(f"la fermeture de {options.get('name')!r}", erreur)
        raise
    else:
        try:
            gestionnaire.__exit__(None, None, None)
        except Exception as erreur:  # noqa: BLE001
            _signaler(f"la fermeture de {options.get('name')!r}", erreur)


def _maj(observation, methode: str = "update", **champs) -> None:
    """`update(...)` ou `score_trace(...)` sur une observation, sans jamais lever."""
    if observation is None:
        return
    try:
        getattr(observation, methode)(**champs)
    except Exception as erreur:  # noqa: BLE001
        _signaler(f"la mise a jour ({methode})", erreur)


def _flush(client) -> None:
    """Envoie ce qui attend ; une panne d'export est signalée, pas propagée."""
    if client is None:
        return
    try:
        client.flush()
    except Exception as erreur:  # noqa: BLE001
        _signaler("l'export (flush)", erreur)


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
def briefing(ticker: str, request_id: str | None = None):
    """Racine du trace d'UN briefing complet, ouverte à la frontière de l'API.

    `request_id` : l'identifiant de la requête HTTP (en-tête `X-Request-ID`). Il sert de
    graine à l'identifiant de trace Langfuse : le même identifiant se lit dans la réponse,
    dans la ligne de journal et dans la trace. Une ligne « briefing refusé » dans le journal
    retrouve ainsi SA trace, et pas une autre. Il est aussi copié en métadonnées, cherchable.

    Pourquoi ici et pas dans `appel` : le garde-fou de sortie s'exécute APRÈS l'appel au
    modèle (api/main.py). Quand le verdict existe, le span `briefing-llm` est déjà fermé et
    ne peut plus le porter. Une racine ouverte plus haut le peut, et elle contient tout :
    le contexte OpenTelemetry traverse LangGraph (mesuré le 02/10/2026 avec un exporteur en
    mémoire), donc `briefing-llm` et ses tentatives se rangent dessous sans rien changer.

    Le flush vient APRÈS la fermeture de la racine, même si la route lève une erreur : un
    span encore ouvert n'est pas exporté. Rend `None` si le traçage est coupé.
    """
    client = client_traces()
    if client is None:
        yield None
        return
    options: dict = {"metadata": {"ticker": ticker}}
    if request_id:
        options["metadata"]["request_id"] = request_id
        # Un identifiant de trace Langfuse fait 32 hexadécimaux : la graine le dérive de façon
        # déterministe, donc le même `request_id` donne toujours la même trace.
        try:
            options["trace_context"] = {"trace_id": client.create_trace_id(seed=request_id)}
        except Exception as erreur:  # noqa: BLE001
            _signaler("la derivation de l'identifiant de trace", erreur)
    try:
        with _observation(client, as_type="span", name="briefing", **options) as racine:
            yield racine
    finally:
        _flush(client)


def noter_verdict_amf(racine, ticker: str, conforme: bool, motifs: list[str],
                      request_id: str | None = None) -> None:
    """Pose le verdict du garde-fou de sortie sur la racine du trace.

    Trois façons de le lire dans Langfuse : les métadonnées (le détail des motifs), le niveau
    WARNING quand le texte est refusé (filtrable), et une note booléenne `conforme_amf`
    (1 ou 0) qu'un tableau peut compter et qu'une alerte peut surveiller.

    **Jamais le texte refusé ici** : il reste dans la génération, pour comprendre pourquoi un
    motif a déclenché, mais la racine, celle qu'on regarde en premier, ne le répète pas.
    """
    if racine is None:
        return
    details: dict = {"metadata": {"ticker": ticker, "conforme_amf": conforme, "motifs_amf": motifs}}
    if request_id:
        details["metadata"]["request_id"] = request_id  # la mise à jour ne doit pas l'effacer
    if not conforme:
        details["level"] = "WARNING"
        details["status_message"] = "refus AMF : " + ",".join(motifs)
    _maj(racine, **details)
    _maj(racine, "score_trace", name="conforme_amf", value=1.0 if conforme else 0.0, data_type="BOOLEAN")


@contextmanager
def etape(nom: str, genre: str = "span", **metadonnees):
    """Un span par étape du chemin (scout, rag, garde-fous, rédacteur), sous la racine.

    Pourquoi : la racine disait « un briefing a pris 4 s » sans dire où. Avec une étape par
    nœud, la trace se lit comme le graphe : qui a tourné, dans quel ordre, combien de temps.
    C'est aussi le test de trace du brief Kaldera : le texte d'un modèle varie, pas la trace.
    `genre` suit le vocabulaire Langfuse (`span`, `retriever`). No-op sans client.
    """
    client = client_traces()
    if client is None:
        yield None
        return
    options: dict = {"as_type": genre, "name": nom}
    if metadonnees:
        options["metadata"] = metadonnees
    with _observation(client, **options) as span:
        yield span


def terminer_etape(span, **champs) -> None:
    """Complète une étape (sortie, métadonnées, niveau). Jamais un texte de briefing ici :
    la sortie d'une étape est un résumé (compte, motif, durée), pas le contenu."""
    if span is not None and champs:
        _maj(span, **champs)


def noter_garde_fou(span, bloque: bool, motifs: list[str]) -> None:
    """Le verdict d'un garde-fou sur son span : bloqué ou non, et les motifs. Niveau WARNING
    si bloqué, pour filtrer les refus d'un clic. Le texte examiné ne passe jamais ici."""
    if span is None:
        return
    champs: dict = {"metadata": {"bloque": bloque, "motifs": motifs}}
    if bloque:
        champs["level"] = "WARNING"
    _maj(span, **champs)


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
    with _observation(client, as_type="span", name="briefing-llm", input=prompt) as racine:
        yield racine


def terminer_appel(racine, texte: str) -> None:
    """Pose la sortie finale sur le trace : ce que le rédacteur a vraiment reçu."""
    if racine is not None:
        _maj(racine, output=texte)


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
    with _observation(
        client,
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
    _maj(gen, **details)


def echouer(gen, erreur: BaseException) -> None:
    """Marque la tentative en erreur ; le message est tronqué, jamais la clé d'API."""
    if gen is None:
        return
    _maj(gen, level="ERROR", status_message=f"{type(erreur).__name__}: {erreur}"[:300])


def vider() -> None:
    """Envoie ce qui attend. Appelé une fois par `generer_texte` : l'API vit longtemps,
    un script court s'arrête juste après, dans les deux cas la trace doit partir."""
    _flush(client_traces())


# --- Sprint 3, tâche A3 : le parcours des questions -----------------------------------------------------------------
# Une question peut contenir une donnée personnelle tapée par un visiteur (décision D2) : sa trace ne porte que des
# métadonnées. Ni `input` ni `output` ici, contrairement à `appel` et `generation`, que ce parcours n'utilise pas.

@contextmanager
def question(request_id: str | None = None):
    """Racine du trace d'UNE question, ouverte à la frontière de l'API ; `None` si le traçage est coupé.

    Même dérivation de l'identifiant que `briefing` : la ligne de journal et la trace se retrouvent par le même
    `request_id`. Le flush vient après la fermeture de la racine, même si la route lève une erreur.
    """
    client = client_traces()
    if client is None:
        yield None
        return
    options: dict = {"metadata": {"parcours": "question"}}
    if request_id:
        options["metadata"]["request_id"] = request_id
        try:
            options["trace_context"] = {"trace_id": client.create_trace_id(seed=request_id)}
        except Exception as erreur:  # noqa: BLE001
            _signaler("la derivation de l'identifiant de trace", erreur)
    try:
        with _observation(client, as_type="span", name="question", **options) as racine:
            yield racine
    finally:
        _flush(client)


def noter_issue_question(racine, statut: str, motif: str, longueur: int, ids: list[int]) -> None:
    """Pose l'issue d'une question sur sa racine : statut, motif, longueur de la question, identifiants cités.
    Niveau WARNING pour un refus, ERROR pour une erreur technique, afin de les filtrer d'un clic. Jamais le texte."""
    if racine is None:
        return
    champs: dict = {"metadata": {"statut": statut, "motif": motif, "longueur": longueur, "ids": list(ids)}}
    if statut == "refus":
        champs["level"] = "WARNING"
    elif statut == "erreur":
        champs["level"] = "ERROR"
        champs["status_message"] = motif
    _maj(racine, **champs)
