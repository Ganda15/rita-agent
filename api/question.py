"""La route des questions libres (sprint 3, tâche A5 ; spec US1, US2, CA4.3).

`POST /question` : 200 pour une réponse citée ou un refus motivé ; 503 pour une panne technique (fournisseur
indisponible, réponse tronquée, format invalide) ; 500 `ERREUR_INTERNE` pour toute erreur imprévue. La clé `X-API-Key`
est exigée par le montage du routeur (`api/main.py`), comme pour `/donnees`.

Aucun texte de question ni de réponse n'est écrit dans un journal ni dans une trace (décision D2) : une ligne de
journal par question (identifiant de requête, statut, motif, longueur, identifiants cités, durée), et une trace qui ne
porte que des métadonnées. Une erreur imprévue est attrapée ICI, à l'intérieur de la trace : elle n'atteint ni le
middleware (qui journalise le message des exceptions, `api/main.py`), ni la sortie du gestionnaire de traces.
"""
from __future__ import annotations

import logging
import time
from dataclasses import asdict

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from agents import question as parcours
from rag import indexation
from src import traces

logger = logging.getLogger(__name__)

routeur = APIRouter(tags=["question"])


class DemandeQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=500,
                          description="La question, en français : de 3 à 500 caractères.")


@routeur.post("/question", summary="Répondre à une question à partir du corpus, avec ses sources, ou refuser")
def poser_question(demande: DemandeQuestion):
    """Répond à partir des articles du corpus, en citant ses sources ; refuse ce qui sort du corpus.

    Les références (table `article`, identifiant, titre, source, date, lien, extrait) viennent des données stockées,
    jamais du texte du modèle. `index` : l'identité de l'index servi (tâche A1).
    """
    from api.main import request_id_courant   # import différé : `api.main` importe ce module au chargement

    request_id = request_id_courant()
    debut = time.perf_counter()
    longueur = len(demande.question)
    with traces.question(request_id) as racine:
        try:
            resultat = parcours.repondre(demande.question)
        except Exception as erreur:  # noqa: BLE001, aucune erreur ne sort avec son message (décision D2)
            logger.error("question en erreur interne : request_id=%s type=%s longueur=%d",
                         request_id, type(erreur).__name__, longueur)
            traces.noter_issue_question(racine, "erreur", "ERREUR_INTERNE", longueur, [])
            return JSONResponse(status_code=500, content={"statut": "erreur", "motif": "ERREUR_INTERNE"})
        ids = [reference.id for reference in resultat.references]
        traces.noter_issue_question(racine, resultat.statut, resultat.motif, longueur, ids)

    logger.info("question servie : request_id=%s statut=%s motif=%s longueur=%d ids=%s duree_ms=%d",
                request_id, resultat.statut, resultat.motif, longueur, ids,
                int((time.perf_counter() - debut) * 1000))

    if resultat.statut == "erreur":
        return JSONResponse(status_code=503,
                            content={"statut": resultat.statut, "motif": resultat.motif, "texte": resultat.texte})
    return {
        "statut": resultat.statut,
        "motif": resultat.motif,
        "texte": resultat.texte,
        "references": [asdict(reference) for reference in resultat.references],
        "index": indexation.lire_identite(),
    }
