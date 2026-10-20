"""Garde-fou de DÉTOURNEMENT : refuse l'injection et la tentative d'extraction dans la question, avant la recherche
(sprint 4, tâche A3 ; spec CA2.1, CA2.2, CA2.4 à CA2.6, décision D2).

**Ce qu'il couvre.** Deux familles, celles de la spec (§ 4, US2) :
- l'**injection** : faire désobéir le modèle à ses consignes (« ignore tes consignes »), lui faire changer de rôle
  (« tu es maintenant… »), lui glisser de fausses balises ;
- l'**extraction** : obtenir un secret (« ta clé d'API »), les consignes du système (« ton prompt système »), ou des
  données internes (« le portefeuille de l'utilisateur »).

**Pourquoi un module à part de `guardrails/entree.py`.** L'intention AMF (« dois-je acheter ») et l'attaque (« ignore
tes consignes ») sont deux questions différentes ; chacune se mesure par ses deux chiffres, taux de blocage et taux de
faux positifs (agent-standard, point 6). Celui-ci passe en premier : quand une question est à la fois une attaque et une
demande de conseil, le journal dit qu'il s'agit d'une attaque.

**Pourquoi des règles, et pas un juge LLM (D2).** Même choix et même coût que les autres garde-fous : quelques
microsecondes, mesurables, sans envoi de plus vers un tiers. La consigne « donnée, jamais consigne » du prompt reste en
défense, comme la règle de pertinence et le garde-fou de sortie.

**Chaque motif exige qu'on s'adresse au système** (« tes consignes », « ton prompt », « ta clé »), jamais un mot isolé :
« Quelles instructions l'AMF a-t-elle données ? », « la clé du succès », « le système bancaire » ou « le rôle de la
BCE » sont des questions légitimes (L2 à L5 du jeu).

**Limite connue et acceptée.** Une reformulation polie peut échapper aux motifs : la liste n'est jamais finie (point 7),
d'où les motifs en tête de module et les reformulations réservées (`evals/cas.py`), écrites avant ces règles et jamais
utilisées pour les écrire, qui mesurent ce qui passe encore.
"""
import re
import unicodedata

# (motif, nom, famille). Le texte est normalisé avant la recherche (`_normaliser`) : apostrophes typographiques en «'»,
# espaces et retours à la ligne réduits à un seul espace ; la casse est ignorée.
MOTIFS_DETOURNEMENT = [
    # --- injection --------------------------------------------------------------------------------------------------
    (r"\b(ignore[sz]?|oublie[sz]?|outrepasse[sz]?|contourne[sz]?)\b[^.?!]{0,40}\b(tes|vos)\s+"
     r"(consignes|instructions|r[èe]gles|directives)\b", "ignorer_les_consignes", "injection"),
    (r"\b(ignore|disregard|forget)\s+(all\s+)?(the\s+)?(previous|prior|above|earlier)\s+(instructions|rules)\b",
     "ignore_previous_instructions", "injection"),
    (r"\b(tu\s+es|vous\s+[êe]tes)\s+(maintenant|d[ée]sormais|dor[ée]navant)\b", "changement_de_role", "injection"),
    (r"\byou\s+are\s+now\b", "role_change", "injection"),
    (r"</?\s*(question|extraits|system|donnees_externes)\s*>", "fausse_balise", "injection"),
    # --- extraction -------------------------------------------------------------------------------------------------
    (r"\b(affiche|montre|r[ée]v[èe]le|donne|r[ée]p[èe]te|dis|[ée]cris|liste|partage)[sz]?(?:[-\s]moi)?\b[^.?!]{0,40}"
     r"\b(tes|vos|ton|votre)\s+(consignes|instructions|r[èe]gles|prompt)\b", "consignes_du_systeme", "extraction"),
    (r"\b(prompt|message)\s+(syst[èe]me|initial)\b", "prompt_systeme", "extraction"),
    (r"\bsystem\s+prompt\b", "system_prompt", "extraction"),
    (r"\b(ta|ton|tes|votre|vos)\s+(cl[ée]f?s?|mots?\s+de\s+passe|jetons?|tokens?|secrets?|identifiants?)\b",
     "secret_du_systeme", "extraction"),
    (r"\b(your)\s+(api\s+keys?|passwords?|secret\s+keys?|access\s+tokens?)\b", "system_secret", "extraction"),
    (r"\bvariables?\s+d['e]\s*environnement\b", "variables_d_environnement", "extraction"),
    (r"\b(portefeuille|positions)\s+(de\s+l['e]\s*utilisateur|des\s+utilisateurs|du\s+client|des\s+clients)\b",
     "donnees_internes", "extraction"),
]

_COMPILES = [(re.compile(motif, re.IGNORECASE), nom, famille) for motif, nom, famille in MOTIFS_DETOURNEMENT]
_APOSTROPHES = str.maketrans({"’": "'", "‘": "'", "ʼ": "'"})

MESSAGE_REFUS = ("Je ne peux pas traiter cette demande : elle cherche à changer mon fonctionnement ou à obtenir des "
                 "informations internes. Je réponds seulement aux questions sur l'actualité économique de mes articles.")


def _normaliser(texte: str) -> str:
    """Une même attaque écrite autrement reste la même : formes Unicode compatibles (NFKC), apostrophes simples,
    espaces et retours à la ligne réduits."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", texte).translate(_APOSTROPHES))


def verifier_detournement(question: str) -> dict:
    """Contrôle la question avant qu'elle n'atteigne la recherche.

    Returns:
        {bloque, motifs_detectes, familles}. Si bloque=True, la recherche (`rag/recherche.py:rechercher`) ne doit pas
        être appelée : la question est refusée avec le motif TENTATIVE_DETOURNEMENT. Les noms des motifs vont au
        journal et à la trace ; ils ne sont jamais montrés à l'écran.
    """
    texte = _normaliser(question)
    trouves = [(nom, famille) for regex, nom, famille in _COMPILES if regex.search(texte)]
    return {
        "bloque": bool(trouves),
        "motifs_detectes": [nom for nom, _ in trouves],
        "familles": sorted({famille for _, famille in trouves}),
    }
