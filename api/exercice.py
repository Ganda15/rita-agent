"""Les routes de la panne simulée : `POST /exercice/panne` et `POST /exercice/fin` (sprint 5, étape 6).

Plan du sprint 5, § 2 « Panne simulée ». La clé d'exercice (en-tête `X-Cle-Exercice`, comparée à `RITA_CLE_EXERCICE`)
est **distincte** de la clé des questions : l'utilisateur d'une clé de questions ne peut pas mettre le service en
panne. Sans `RITA_CLE_EXERCICE` (ou trop courte), les routes répondent « exercices désactivés » : aucune panne ne se
pose sans la clé de l'opérateur, et ce code resterait inerte sur un serveur qui ne la définit pas. La clé est exigée
par le montage du routeur (`api/main.py`).

Chaque demande dit qui et pourquoi, comme les boutons GitHub de l'original (ingestion, livraison, retour arrière) :
le journal garde une ligne au début et une à la fin, jamais la clé. Le nom et le motif sont bornés à des caractères
sûrs : ils sont affichés par le tableau de bord et recopiés dans une issue par la vigie.
"""
from __future__ import annotations

import logging
import os
import secrets

from fastapi import APIRouter, HTTPException, Request, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, ConfigDict, Field

from api.limiteur import noter_mauvaise_cle, refuser_si_bloquee
from monitorage import exercice as module_exercice

logger = logging.getLogger(__name__)

# `scheme_name` : sans lui, cette clé et celle des questions portent le même nom par défaut (`APIKeyHeader`), le
# contrat OpenAPI n'en garde qu'une, et `/docs` annonçait `X-API-Key` sur ces routes (relecture du 24/10).
ENTETE_CLE = APIKeyHeader(name="X-Cle-Exercice", scheme_name="CleExercice", auto_error=False,
                          description="Clé de l'opérateur (`RITA_CLE_EXERCICE`), distincte de la clé des questions.")
LONGUEUR_MINIMALE_CLE = 16
NOM = r"^[\w .'-]+$"
MOTIF = r"^[\w .,'’:;()!?/-]+$"


def verifier_cle_exercice(request: Request, cle: str = Security(ENTETE_CLE)) -> None:
    from api.main import request_id_courant   # import différé : `api.main` importe ce module au chargement

    attendue = os.getenv("RITA_CLE_EXERCICE", "")
    if len(attendue) < LONGUEUR_MINIMALE_CLE:
        raise HTTPException(status_code=503,
                            detail="Exercices désactivés : RITA_CLE_EXERCICE absente ou trop courte sur ce serveur.")
    # Constat S3 (07/11/2026) : même frein que la clé d'API, même compteur par adresse (revue de sécurité automatique du
    # 07/11 : sans lui, cette clé restait la seule porte à essais illimités). Une clé absente ne compte pas.
    refuser_si_bloquee(request)
    if not cle or not secrets.compare_digest(cle, attendue):
        logger.warning("cle d'exercice refusee : request_id=%s route=%s", request_id_courant(), request.url.path)
        if cle:
            noter_mauvaise_cle(request)
        raise HTTPException(status_code=403, detail="Clé d'exercice invalide ou absente")


class DemandeDePanne(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nom: str = Field(min_length=1, max_length=40, pattern=NOM, description="Qui pose l'exercice.")
    motif: str = Field(min_length=3, max_length=120, pattern=MOTIF, description="Pourquoi.")
    duree_min: int = Field(default=20, ge=1, le=20, description="Durée maximale, en minutes (20 au plus).")


class DemandeDeFin(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nom: str = Field(min_length=1, max_length=40, pattern=NOM)
    motif: str = Field(min_length=3, max_length=120, pattern=MOTIF)


routeur = APIRouter(prefix="/exercice", tags=["exercice"])


@routeur.post("/panne", summary="Poser une panne simulée du fournisseur du modèle (20 minutes au plus)")
def poser_panne(demande: DemandeDePanne) -> dict:
    from api.main import request_id_courant

    try:
        etat = module_exercice.EXERCICE.poser(demande.nom, demande.motif, demande.duree_min * 60)
    except module_exercice.ExerciceEnCours:
        raise HTTPException(status_code=409, detail="Un exercice de panne est déjà en cours.") from None
    logger.warning("exercice de panne pose : request_id=%s nom=%r motif=%r fin_au_plus_tard=%s",
                   request_id_courant(), demande.nom, demande.motif, etat["fin_au_plus_tard"])
    return {"statut": "panne simulée", **etat}


@routeur.post("/fin", summary="Retirer la panne simulée")
def finir_panne(demande: DemandeDeFin) -> dict:
    from api.main import request_id_courant

    ancien = module_exercice.EXERCICE.finir()
    if ancien is None:
        return {"statut": "aucun exercice en cours"}
    logger.warning("exercice de panne termine : request_id=%s nom=%r motif=%r", request_id_courant(), demande.nom,
                   demande.motif)
    return {"statut": "exercice terminé", "termine": ancien}
