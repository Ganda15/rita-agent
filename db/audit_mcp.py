"""Journal des appels MCP : un seul écrivain, l'API (plan 62, chapitre « Données » §3.7, C20).

Décisions d'Era du 03/10/2026 : D1, seuls les appels qui portent `X-Client-Id` sont journalisés ;
D2, les refus locaux de la passerelle remontent par `POST /audit/mcp` ; D3, une panne d'écriture se
voit (compteur `echecs()` exposé par `/donnees/fraicheur`, ligne WARNING), mais ne fait jamais
échouer l'appel métier : l'isolation va dans un seul sens, comme pour le traçage Langfuse.

Ce qui n'entre jamais ici : les paramètres de l'appel (un ticker est un intérêt personnel), les
prompts, les clés, les positions ou totaux rendus, un message d'erreur libre. Huit colonnes.
Rétention 90 jours : procédure P6 de `db/rgpd_purge.py`, traitement T5 du registre.
"""
from __future__ import annotations

import logging
import re

from sources import database

logger = logging.getLogger(__name__)

STATUTS = ("succes", "refuse", "erreur")
# L'étiquette des règles d'accès en vigueur : la matrice du chapitre (07/09/2026). Elle change
# quand la matrice change, pas à chaque déploiement : un vieux refus se relit avec ses règles.
VERSION_POLITIQUE = "matrice-acces-2026-09-07"
CLIENT_PASSERELLE = "passerelle-mcp"
_IDENTIFIANT_SAIN = re.compile(r"^[A-Za-z0-9_.\-]{1,60}$")

_echecs = 0

SQL_INSERTION = """
    INSERT INTO mcp_calls (request_id, client_id, outil, statut, code_erreur, duree_ms, version_politique)
    VALUES (%(request_id)s, %(client_id)s, %(outil)s, %(statut)s, %(code_erreur)s, %(duree_ms)s, %(version_politique)s)
"""


def echecs() -> int:
    """Combien d'écritures ont échoué depuis le démarrage : le vecteur C20 de la règle 7 du chapitre."""
    return _echecs


def reinitialiser_compteur() -> None:
    global _echecs
    _echecs = 0


def _sain(valeur: str | None, longueur: int) -> str:
    """Un identifiant ou un nom d'outil douteux n'est pas recopié : il devient « invalide »."""
    valeur = (valeur or "").strip()
    if not _IDENTIFIANT_SAIN.match(valeur):
        return "invalide"
    return valeur[:longueur]


def statut_depuis_code(code_http: int) -> tuple[str, str | None]:
    """Le statut et le code typé qu'un code HTTP veut dire pour le journal."""
    if code_http < 400:
        return "succes", None
    if code_http in (401, 403):
        return "refuse", "NOT_AUTHORIZED"
    if code_http == 404:
        return "refuse", "NOT_FOUND"
    if code_http == 422:
        return "refuse", "PARAMETRE_INVALIDE"
    if code_http < 500:
        return "refuse", "REFUS_HTTP"
    if code_http in (502, 503, 504):
        return "erreur", "SERVICE_INDISPONIBLE"
    return "erreur", "ERREUR_API"


def enregistrer(request_id: str, client_id: str, outil: str, statut: str,
                code_erreur: str | None = None, duree_ms: int | None = None,
                dsn: str | None = None) -> bool:
    """Écrit une ligne ; rend vrai si elle est partie. Ne lève jamais pour une panne de base."""
    if statut not in STATUTS:
        raise ValueError(f"statut inconnu : {statut!r}, attendu {STATUTS}")
    global _echecs
    params = {
        "request_id": _sain(request_id, 64),
        "client_id": _sain(client_id, 40),
        "outil": _sain(outil, 60),
        "statut": statut,
        "code_erreur": _sain(code_erreur, 40) if code_erreur else None,
        "duree_ms": max(0, int(duree_ms)) if duree_ms is not None else None,
        "version_politique": VERSION_POLITIQUE,
    }
    try:
        with database._connexion(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(SQL_INSERTION, params)
        return True
    except Exception as erreur:  # noqa: BLE001, la journalisation ne fait jamais tomber l'appel
        _echecs += 1
        logger.warning("audit mcp non ecrit (%d echec(s)) : outil=%s statut=%s : %s",
                       _echecs, params["outil"], statut, f"{type(erreur).__name__}: {erreur}"[:160])
        return False
