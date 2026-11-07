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

from guardrails.normalisation import textes_de_controle

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

# --- Constat S9, tâche T5 (07/11/2026, plan § 5, validé par Era) : la recommandation qui ne dit pas son nom ----------
# Les motifs ci-dessus exigent un verbe de recommandation ; les contournements de l'ancien jeu n'en avaient aucun (« une
# place dans un portefeuille », « le point d'entrée paraît attractif », « une occasion à saisir »). Une règle par
# FAMILLE de posture, jamais un mot seul : « le portefeuille de commandes », « des prises de bénéfices font reculer le
# titre », « le groupe a profité de la baisse » restent des faits. Jeu tenu à l'écart : `evals/cas_s9_reserves_sortie.py`,
# commité avant ces règles et mesuré sans en lire les textes.
# Double contrôle du 07/11 (autre agent) : des faits étaient refusés (« la banque cherche à renforcer ses fonds propres »,
# « un rendez-vous à ne pas manquer »). Les revues de sécurité automatiques des réécritures suivantes ont chaque fois
# trouvé l'excès inverse : « C'est le moment de renforcer LVMH », puis « lvmh », « Éramet », puis « le meilleur moment
# de vendre LVMH », « acheter de l'or », puis « acheter de la dette publique ». Une liste OUVERTE d'objets de fait a
# toujours des trous. Décision d'Era (07/11), qui suit le choix « fail-closed » de ce module :
# - dans une TOURNURE DE CONSEIL (« moment de / temps de » + un verbe d'achat ou de vente ; « mieux vaut » + éviter,
#   vendre... ; « difficile de rester à l'écart »), le texte est TOUJOURS refusé, sauf un objet de fait admis POUR CE
#   VERBE (`_FAITS_APRES_*`), jamais après acheter, accumuler, se positionner, se placer ou entrer, et seulement si la
#   phrase s'arrête après lui ou finit sur une attribution (« , prévient l'économiste ») sans mot de conseil.
#   Coût, accepté et testé : un fait hors de ces listes est refusé ;
# - les autres familles exigent un contexte d'investissement (un lecteur, un investisseur, un titre, une société nommée).
# Cas : `tests/test_sortie_amf_contexte.py`, écrits avant chaque réécriture.
_SOCIETE = r"(?-i:[A-ZÀ-ÖØ-Þ][\w&'’.-]*)"  # une majuscule, accentuée comprise, lue en respectant la casse
_NOMS_D_INVESTISSEMENT = (r"(titres?|valeurs?|actions?|dossiers?|positions?|lignes?|expositions?|b[ée]n[ée]fices|"
                          r"participations?|parts?|portefeuilles?|secteurs?)")
_MOTS_DE_CONSEIL = (r"(acheter|achetez|achat|vendre|vendez|vente|renforcer|renforcez|all[ée]ger|all[ée]gez|c[ée]der|"
                    r"accumuler|accumulez|investir|investissez|miser|misez|se\s+positionner|positionnez|"
                    rf"{_NOMS_D_INVESTISSEMENT})")
# Après l'objet admis : la fin de la phrase, ou une attribution qui ne contient aucun mot de conseil.
_FIN_DE_PHRASE = r"\s*([.;!?]|$)"
_ATTRIBUTION = (r",\s*(selon|estime|pr[ée]vient|admet|juge|indique|explique|affirme|souligne)\b"
                rf"(?![^.;!?]{{0,80}}?\b{_MOTS_DE_CONSEIL}\b)[^.;!?]{{0,80}}([.;!?]|$)")
_APRES_LE_FAIT = rf"({_FIN_DE_PHRASE}|{_ATTRIBUTION})"
# Les objets de fait, par verbe. Liste fermée : chaque objet vient d'un fait des tests ; en ajouter un passe par un
# test d'abord. Aucun objet admis après un verbe d'achat.
_FAITS_APRES_RENFORCER = r"la\s+gouvernance|(la|sa|leur)\s+coop[ée]ration(\s+avec\s+(ses|leurs)\s+(fournisseurs|partenaires))?"
_FAITS_APRES_SORTIR = (r"du\s+nucl[ée]aire|de\s+la\s+(crise|r[ée]cession)"
                       r"|de\s+(la|sa|leur)\s+d[ée]pendance(\s+au\s+gaz(\s+russe)?)?")
_FAITS_APRES_ALLEGER = r"(la|sa|leur)\s+dette(\s+publique)?|(la|sa|leur)\s+politique(\s+mon[ée]taire)?"
_FAITS_APRES_VENDRE = (r"(sa|ses|leur|leurs)\s+filiales?(\s+am[ée]ricaines?)?"
                       r"|(ses|leurs)\s+actifs(\s+non\s+strat[ée]giques)?")
_FAITS_APRES_EVITER = r"les\s+g[ée]n[ée]ralisations"
_FAITS_APRES_ECART = r"des\s+tensions(\s+commerciales)?"


def _sauf(faits: str) -> str:
    """Le verbe passe seulement suivi d'un de ces objets, puis de la fin de la phrase ou d'une attribution."""
    return rf"(?!\s+({faits}){_APRES_LE_FAIT})"


_LE_MOMENT = r"(\ble\s+moment\s+est\s+venu|\bmoment|\btemps)\s+(de\s+|d['’])"
_ECART = r"(se\s+tenir|rester)\s+[àa]\s+l['’][ée]cart"
_VERBE_D_ENTREPRISE = (r"s['’](implanter|[ée]tendre|agrandir)|se\s+(d[ée]velopper|diversifier|d[ée]sendetter|redresser|"
                       r"restructurer)|le\s+groupe|la\s+soci[ée]t[ée]|l['’]entreprise|la\s+direction")
FAMILLES_AMF = [
    # une place dans un portefeuille de lecteur, jamais le portefeuille d'un indice ou d'activités
    (r"\b(une|sa|toute\s+sa)\s+place\s+dans\s+(un|votre|tout|chaque)\s+portefeuille"
     r"|\b(int[ée]grer|figurer\s+dans)\s+(un|votre|vos|tout|chaque)\s+portefeuilles?"
     r"|\b(ajouter|placer)\s+[^.;]{0,30}?\b(dans|[àa])\s+(un|votre|tout|chaque)\s+portefeuille"
     r"|\bdeserves?\s+a\s+place\s+in", "place_en_portefeuille"),
    # un point d'entrée qualifié, ou le moment d'acheter (tournure de conseil : jamais d'objet admis après un achat)
    (r"\b(bon|meilleur|excellent|attracti\w*|int[ée]ressant|id[ée]al|offre)\s+(un\s+)?point\s+d['’]entr[ée]e"
     r"|point\s+d['’]entr[ée]e\s+(para[iî]t|semble|est)\s+(attracti\w*|int[ée]ressant|id[ée]al)"
     rf"|{_LE_MOMENT}(se\s+positionner|se\s+placer|entrer|acheter|accumuler)\b"
     rf"|{_LE_MOMENT}renforcer\b{_sauf(_FAITS_APRES_RENFORCER)}"
     r"|\b(attractive|good|ideal)\s+entry\s+point|\b(time|moment)\s+to\s+(buy|sell|get\s+in|take\s+profits)", "point_d_entree"),
    # une occasion à ne pas manquer, sauf celle d'une entreprise ; un titre à ne pas manquer ; le tort de l'investisseur
    (rf"\b(opportunit[ée]|occasion)s?\s+[àa]\s+(saisir|ne\s+pas\s+(manquer|laisser\s+passer|rater))"
     rf"(?!\s+pour\s+({_VERBE_D_ENTREPRISE}))"
     r"|\b(titre|valeur)s?\b[^.;]{0,40}?\b[àa]\s+ne\s+pas\s+(manquer|laisser\s+passer|rater)"
     r"|\b(investisseurs?|actionnaires?|[ée]pargnants?|lecteurs?|vous)\s+(aurai(en)?t|auriez)\s+tort\s+de\s+ne\s+pas"
     r"|\b(worth|time\s+for)\s+(adding|buying|owning)", "occasion_a_saisir"),
    # la vente ou l'abstention présentées comme une évidence (tournures de conseil, objets admis par verbe)
    (r"\b(temps|moment)\s+de\s+prendre\s+(ses|vos|des)\s+b[ée]n[ée]fices"
     rf"|{_LE_MOMENT}sortir\b{_sauf(_FAITS_APRES_SORTIR)}"
     rf"|{_LE_MOMENT}all[ée]ger\b{_sauf(_FAITS_APRES_ALLEGER)}"
     rf"|{_LE_MOMENT}(vendre|c[ée]der)\b{_sauf(_FAITS_APRES_VENDRE)}"
     rf"|\bmieux\s+vaut\s+[ée]viter\b{_sauf(_FAITS_APRES_EVITER)}"
     rf"|\bmieux\s+vaut\s+({_ECART}|vendre|sortir|acheter|all[ée]ger|c[ée]der|renforcer)\b"
     r"|\b(rester|se\s+tenir)\s+[àa]\s+l['’][ée]cart\s+(du|de\s+ce|de\s+la)\s+(titre|valeur|dossier|action)", "sortie_evidente"),
    # une consigne de marché sur un titre ou une société nommée, ou l'abstention présentée comme intenable
    (r"\b(titre|valeur)s?\b[^.;]{0,40}?\b[àa]\s+(accumuler|all[ée]ger|renforcer)\b"
     rf"|{_SOCIETE}\s*(:|\s+(reste|est|demeure|serait|semble|para[iî]t))\s+(un\s+titre\s+|une\s+valeur\s+)?"
     r"[àa]\s+(accumuler|all[ée]ger|renforcer)\b"
     r"|:\s*[àa]\s+(accumuler|all[ée]ger|renforcer)\b"
     r"|\b[àa]\s+(accumuler|all[ée]ger|renforcer)\s+(sur|en|au|apr[èe]s|avant)\s+(repli|baisse|faiblesse|rebond|hausse|creux|cours|niveaux?)"
     r"|\b(renforcer|all[ée]ger|accumuler)\s+(votre|vos)\s+(positions?|lignes?|expositions?|participations?)"
     rf"|\bdifficile\s+de\s+rester\s+[àa]\s+l['’][ée]cart{_sauf(_FAITS_APRES_ECART)}", "incitation_douce"),
]
_COMPILES += [(re.compile(m, re.IGNORECASE), nom) for m, nom in FAMILLES_AMF]

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
    # Le texte d'origine et ses copies normalisées (`guardrails/normalisation.py`, revue de sécurité du 07/11).
    controles = textes_de_controle(texte)
    motifs = [nom for regex, nom in _COMPILES if any(regex.search(t) for t in controles)]
    conforme = not motifs
    return {
        "conforme": conforme,
        "motifs_detectes": motifs,
        "texte_diffusable": texte if conforme else MESSAGE_REFUS,
        "texte_brut": texte,
    }


# --- Sprint 4, tâche B2 : le contrôle de FUITE (spec CA3.1, CA3.2, CA3.5) ---------------------------------------------
# Une réponse ne laisse jamais sortir un secret, une valeur de configuration ou un morceau des consignes. Même forme de
# résultat que `verifier_sortie`, pour que les appelants le traitent pareil. Les consignes sont passées par chaque
# parcours : `guardrails/` n'importe jamais `agents/`. Parler d'une fuite de mots de passe ou de « la clé d'un accord »
# n'est pas divulguer : chaque motif vise la FORME d'un secret, jamais un mot.
MOTIFS_FUITE = [
    (r"\bsk-[A-Za-z0-9_-]{16,}", "forme_de_cle"),
    (r"\b(?i:bearer)\s+[A-Za-z0-9._~+/=-]{16,}", "forme_de_cle"),
    (r"\b(?:ghp|gho|ghs|github_pat)_[A-Za-z0-9_]{20,}", "forme_de_cle"),
    (r"\bAKIA[0-9A-Z]{16}\b", "forme_de_cle"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "forme_de_cle"),
    # Une adresse de base de données AVEC compte et mot de passe : « postgresql://compte:secret@hote ».
    (r"\b(?i:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^\s/@:]+:[^\s/@]+@", "chaine_de_connexion"),
    # Un nom de variable de configuration, en majuscules : RITA_API_KEY, DATABASE_URL, AZURE_FOUNDRY_ENDPOINT…
    (r"\b[A-Z][A-Z0-9]*_(?:API_KEY|SECRET_KEY|PUBLIC_KEY|ACCESS_KEY|PASSWORD|TOKEN|SECRET|ENDPOINT|URL|DSN[A-Z0-9_]*)\b",
     "nom_de_variable"),
]
_COMPILES_FUITE = [(re.compile(motif), nom) for motif, nom in MOTIFS_FUITE]

# --- Constat S9 (07/11/2026, plan `docs/PLAN-S9-garde-fous.md`, validé par Era) : la fuite déguisée -----------------
# Les motifs ci-dessus reconnaissent la forme EXACTE d'un secret ; ce qui passait le disait autrement : épelé, en
# morceaux, en clair après son libellé, sous un nom de variable déguisé, ou les consignes paraphrasées. Une règle par
# FAMILLE ; chacune exige la forme d'une divulgation, jamais un mot seul (« la clé de la reprise », « le secret des
# affaires » passent). Jeu tenu à l'écart : `evals/cas_s9_reserves.py`, commité avant ces règles.
_MOT_DE_SECRET = r"\b(cl[ée]|key|jeton|token|secret|mot\s+de\s+passe|password)\b"
FAMILLES_FUITE = [
    # un secret épelé lettre par lettre, en morceaux, ou décrit par son début
    # Revue de sécurité du 07/11 : chaque suite d'espaces est bornée, pour qu'aucune entrée ne provoque un retour arrière
    # catastrophique (tests/test_evals.py, entrées hostiles).
    (_MOT_DE_SECRET + r"[^.\n]{0,60}?((?:\b\w\b[\s,]{1,3}){5,40}|en\s{1,3}morceaux|par\s{1,3}morceaux|s['’][ée]crit"
     r"|lettre\s{1,3}par\s{1,3}lettre|caract[èe]re\s{1,3}par\s{1,3}caract[èe]re|(commence|se\s{1,3}termine)\s{1,3}par\s{1,3}(\b\w\b|[\"«]))",
     "secret_epele_ou_morcele"),
    # un mot de passe ou un secret dit en clair après son libellé : la valeur a la forme d'un secret (chiffre, tiret,
    # tiret bas ou trois majuscules), pas celle d'un mot (« le mot de passe unique devient obligatoire » passe)
    (r"\b(mot\s{1,3}de\s{1,3}passe|password|passwd|secret|code\s{1,3}d['’]acc[èe]s)"
     r"(?:\s{1,3}(?:de|du|des|d['’])\s{0,2}[^\s,.:]{1,25}(?:\s{1,2}[^\s,.:]{1,25})?)?"
     r"[\s:=]{0,6}(?:(?:est|vaut)[\s:]{1,4})?(?=[^\s]{0,40}[\d_\-]|[^\s]{0,40}(?-i:[A-Z]{3}))[^\s]{8,80}", "secret_en_clair"),
    # un nom de variable de configuration en minuscules, ou écrit avec des espaces
    (r"\b[a-z][a-z0-9]*_(api_key|secret_key|access_key|password|token|secret|dsn)\b|\b(api|secret|access)\s+key\s*[=:]",
     "variable_deguisee"),
    # les consignes paraphrasées : qui parle de SES instructions, ou de leurs termes propres à RITA
    (r"\b(mes|nos)\s+(instructions|consignes)\b|\bon\s+m['’]a\s+(demand[ée]|dit)\s+de\s+(r[ée]pondre|ne\s+jamais|refuser)"
     r"|extraits\s+num[ée]rot[ée]s|entre\s+les\s+balises", "consignes_paraphrasees"),
]
_COMPILES_FAMILLES_FUITE = [(re.compile(motif, re.IGNORECASE), nom) for motif, nom in FAMILLES_FUITE]

# Un fragment de consigne, c'est 8 mots consécutifs des consignes retrouvés dans la réponse : huit mots ne se
# rencontrent pas par hasard, un mot isolé (« instructions », « système ») ne suffit jamais.
FENETRE_CONSIGNES = 8

MESSAGE_REFUS_FUITE = "La réponse produite contenait une information interne : elle n'est pas affichée."


def _fenetres(texte: str) -> set[tuple[str, ...]]:
    mots = re.findall(r"\w+", texte.casefold())
    return {tuple(mots[i:i + FENETRE_CONSIGNES]) for i in range(len(mots) - FENETRE_CONSIGNES + 1)}


def verifier_fuite(texte: str, consignes: tuple[str, ...] = ()) -> dict:
    """Contrôle que le texte du modèle ne laisse sortir ni secret, ni configuration, ni consigne.

    Args:
        texte: la réponse ou le briefing rédigé par le modèle.
        consignes: les textes fixes du prompt de ce parcours.

    Returns:
        {conforme, motifs_detectes, texte_diffusable}. Si conforme=False, `texte_diffusable` porte le message de
        refus : le texte d'origine n'est jamais diffusé, ni écrit au journal. Les noms des motifs, eux, y vont.
    """
    # Les règles lisent le texte d'origine et ses copies normalisées : espaces ramenés à un seul, caractères invisibles
    # retirés, pleine chasse ramenée aux lettres ordinaires (`guardrails/normalisation.py`, revue de sécurité du 07/11).
    # Les séparateurs des règles par famille restent bornés contre le retour arrière.
    controles = textes_de_controle(texte)
    motifs = list(dict.fromkeys(
        nom for regex, nom in _COMPILES_FUITE + _COMPILES_FAMILLES_FUITE if any(regex.search(t) for t in controles)))
    fenetres = set().union(*(_fenetres(t) for t in controles))
    if any(fenetres & _fenetres(consigne) for consigne in consignes):
        motifs.append("fragment_consignes")
    conforme = not motifs
    return {
        "conforme": conforme,
        "motifs_detectes": motifs,
        "texte_diffusable": texte if conforme else MESSAGE_REFUS_FUITE,
    }
