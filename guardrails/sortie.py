"""Garde-fou de SORTIE — interdit AMF sur le texte rédigé par le modèle (C9, C17).

Standard Velmo 2.0, point 4 : entrée / SORTIE / résultats d'outils. `injection.py` couvre
l'entrée et les résultats d'outils. Ce module couvre le troisième, qui manquait.

**Pourquoi ce module existe, et pourquoi il n'existait pas avant.** Le docstring de
`guardrails/injection.py` (ligne 9) invoquait « le garde-fou de sortie » comme s'il
existait ; `api/main.py` renvoyait pourtant `resultat["briefing"]` sans aucun contrôle.
Un contrôle documenté mais absent est pire qu'un contrôle absent : on cesse de le chercher.
Écart constaté et comblé le 17/08/2026 (veille S34).

**Pourquoi filtrer la sortie plutôt que durcir l'entrée.** On ne peut pas énumérer toutes
les façons de formuler une injection — mesuré : les 9 motifs d'entrée laissent passer une
reformulation polie sans verbe à l'impératif. En revanche **on peut énumérer le petit
ensemble de sorties interdites** : RITA n'a le droit de produire aucune recommandation
d'achat ou de vente. C'est le principe posé par OWASP dans l'édition 2026 du Top 10 —
cesser de vouloir un modèle qu'on ne peut pas tromper, et construire autour de lui pour que
le tromper ne serve à rien.

Point 5 : coût sur le chemin critique. Regex, quelques microsecondes — négligeable face à
l'appel au modèle qui précède (plusieurs centaines de millisecondes).
"""
import re

# Sorties interdites — l'interdit AMF (conseil en investissement non agréé).
# Chaque motif exige une POSTURE de recommandation, pas le simple mot « achat » :
# « volume d'achat » ou « rachat d'actions » sont des faits, pas des conseils.
MOTIFS_AMF = [
    (r"(recommand|conseill|pr[ée]conis)\w*\s+(l'|d'|de\s+|à\s+)?"
     r"(achat|acheter|vente|vendre)", "recommandation_explicite_fr"),
    (r"(suggestion|opportunit[ée]|occasion)\s+d['’]achat", "suggestion_achat_fr"),
    (r"\b(achetez|vendez)\b", "imperatif_fr"),
    (r"il\s+(faut|faudrait|convient\s+de|serait\s+judicieux\s+de)\s+"
     r"(acheter|vendre)", "injonction_fr"),
    (r"(privil[ée]gier|favoriser|renforcer)\s+l['’](achat|exposition)",
     "incitation_fr"),
    (r"(vous\s+devriez|tu\s+devrais|il\s+est\s+conseill[ée]\s+de)\s+"
     r"(acheter|vendre|all[ée]ger|renforcer)", "conseil_personnalise_fr"),
    (r"\b(recommend|advise|suggest)\w*\s+(buying|selling|to\s+buy|to\s+sell)",
     "recommandation_en"),
    (r"\b(strong\s+)?(buy|sell)\s+(rating|recommendation|signal)", "notation_en"),
    (r"\b(you\s+should|investors\s+should)\s+(buy|sell)", "conseil_en"),
]

_COMPILES = [(re.compile(m, re.IGNORECASE), nom) for m, nom in MOTIFS_AMF]

MESSAGE_REFUS = (
    "Briefing non diffusé : le texte produit contenait une formulation assimilable "
    "à une recommandation d'investissement, ce que RITA s'interdit (AMF)."
)


def verifier_sortie(texte: str) -> dict:
    """Contrôle le texte du modèle avant diffusion.

    Args:
        texte: le briefing rédigé par le modèle.

    Returns:
        {conforme, motifs_detectes, texte_diffusable}.
        Si conforme=False, `texte_diffusable` porte le message de refus : on **ne diffuse
        pas** le texte d'origine. Choix « fail-closed » — en cas de doute, on ne publie pas.
        Le texte d'origine reste disponible dans `texte_brut` pour l'audit, jamais pour
        l'utilisateur.
    """
    motifs = [nom for regex, nom in _COMPILES if regex.search(texte)]
    conforme = not motifs
    return {
        "conforme": conforme,
        "motifs_detectes": motifs,
        "texte_diffusable": texte if conforme else MESSAGE_REFUS,
        "texte_brut": texte,
    }
