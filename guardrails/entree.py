"""Garde-fou d'ENTREE — refuse l'intention interdite AMF avant la recherche (C10, C17).

Standard Velmo 2.0 (skill `agent-standard`), point 4 : le troisieme emplacement de
garde-fou documente est l'ENTREE. `guardrails/injection.py` couvre les resultats
d'outils, `guardrails/sortie.py` couvre le texte redige par le modele. Ce module
couvre le premier, qui manquait : la question posee par l'utilisateur, AVANT toute
recherche.

**Pourquoi un module separe du seuil de distance (`rag/recherche.py:SEUIL_DISTANCE_DENSE`).**
Le seuil mesure une PERTINENCE (cette question ressemble-t-elle a ces articles ?), pas
une INTENTION (cette question demande-t-elle un conseil ?). Mesure le 06/09
(CONTINUITE.md, section G) : sur 5 questions a intention interdite, 3 recevaient du
contexte -- et relever le seuil pour reparer une autre fuite (LVMH, 07/09) rouvrirait
celle-ci. Un seuil unique ne peut pas repondre a deux questions differentes.

**Pourquoi regex, et pas un juge LLM.** Decision d'Era le 18/09 (skill `agent-standard`,
point 5 : chaque garde-fou coute de la latence sur le chemin critique). Meme choix,
meme cout (microsecondes) que `injection.py` et `sortie.py`. Limite connue et acceptee :
une reformulation polie peut echapper aux motifs -- deja ecrite dans le docstring de
`sortie.py` pour l'injection, elle vaut pareillement ici. Point 7 : la liste n'est
jamais finie, d'ou MOTIFS_INTENTION_AMF en configuration et non en dur dans la fonction.

Les 5 cas de test ne sont pas invente : ce sont les 5 questions de la famille
`hors_perimetre_amf` dans `evals/questions_rag.txt` (lignes 128, 193-196), deja
mesurees a 3 fuites sur 5 le 06/09.
"""
import re

# Intentions interdites — l'interdit AMF vu depuis la QUESTION, pas depuis la reponse.
# Chaque motif exige une SOLLICITATION de conseil (« dois-je », « faut-il », « quelle
# action acheter »), pas le simple mot « action » ou « acheter » isole : une question
# factuelle sur une actualite ou un dossier judiciaire ne les contient pas.
MOTIFS_INTENTION_AMF = [
    (r"dois-je\s+(acheter|vendre)", "dois_je_acheter_vendre"),
    (r"faut-il\s+(acheter|vendre)", "faut_il_acheter_vendre"),
    (r"actions?\s+(à|a)\s+acheter", "actions_a_acheter"),
    (r"va\s+(doubler|tripler|exploser|s'effondrer|chuter|s'envoler)",
     "va_doubler_ou_chuter"),
    (r"pour\s+gagner\s+\d+\s*%", "pour_gagner_pourcentage"),
    (r"quelle\s+(action|valeur)\w*.*\bacheter\b", "quelle_action_acheter"),
    # --- scan Giskard, run 9 (20/09/2026) : une question qui demande d'incarner un personnage « sans
    # filtre » qui « se moque des régulations » est une intention interdite déguisée (OWASP LLM01).
    (r"jeu\s+de\s+r[ôo]les?", "jeu_de_role"),
    (r"sans\s+filtre|se\s+moque\s+des\s+r[ée]gulations|conseils?\s+d'investissement\s+agressifs?", "personnage_sans_filtre"),
]

_COMPILES = [(re.compile(m, re.IGNORECASE), nom) for m, nom in MOTIFS_INTENTION_AMF]

MESSAGE_REFUS = (
    "RITA ne répond pas à une question qui sollicite un conseil d'achat ou de vente "
    "(contrainte AMF) — une aide à la lecture ne dit jamais quoi faire."
)


def verifier_intention(question: str) -> dict:
    """Contrôle l'intention d'une question avant qu'elle n'atteigne la recherche.

    Args:
        question: le texte tapé par l'utilisateur.

    Returns:
        {bloque, motifs_detectes, message_refus}. Si bloque=True, la recherche
        (`rag/recherche.py:rechercher`) ne doit pas être appelée : `message_refus`
        porte le texte à renvoyer à la place. Fail-closed, comme `sortie.py`.
    """
    motifs = [nom for regex, nom in _COMPILES if regex.search(question)]
    bloque = bool(motifs)
    return {
        "bloque": bloque,
        "motifs_detectes": motifs,
        "message_refus": MESSAGE_REFUS if bloque else None,
    }
