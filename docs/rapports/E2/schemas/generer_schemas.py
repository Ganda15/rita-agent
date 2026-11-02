"""Les trois schémas de l'annexe du rapport E2, générés depuis une seule description : .drawio ET .svg.

Pourquoi ces schémas existent : le 01/11/2026, Era a relevé que le rapport E2 n'avait aucun schéma, alors que E1, E3
et E4 en ont. Aucun schéma propre à E2 n'existait dans le dépôt, et ceux d'E3 disent encore « cascade, Azure
d'abord », vrai au 24/10 mais plus aujourd'hui. Ces trois schémas sont donc dessinés le 01/11 pour le rapport, à partir
des preuves qu'il cite : ce sont des figures de synthèse, pas des documents de conception d'époque, et chaque légende le
dit.

Le dessin réutilise le moteur du générateur d'E3 (boîtes, flèches, légende, contrôle de place) pour garder la même
charte ; seules les descriptions sont ici. Le `.png` se rend depuis le `.svg` par Chrome sans fenêtre (README du
dossier).

Lancer :  C:\\Python314\\python.exe -X utf8 docs\\rapports\\E2\\schemas\\generer_schemas.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ICI = Path(__file__).parent
_E3 = ICI.parent.parent / "E3" / "schemas" / "generer_schemas.py"
_spec = importlib.util.spec_from_file_location("schemas_e3_moteur", _E3)
moteur = importlib.util.module_from_spec(_spec)
sys.modules["schemas_e3_moteur"] = moteur   # dataclass relit son module dans sys.modules
_spec.loader.exec_module(moteur)

Schema, Boite, Fleche = moteur.Schema, moteur.Boite, moteur.Fleche

DESSIN = "dessiné le 01/11/2026 pour ce rapport, corrigé le 02/11"

# =============================================================================
# B1 : la veille, de la source à la décision (C6)
# =============================================================================
VEILLE = Schema(
    nom="E2-veille", largeur=1400, hauteur=660,
    titre="La veille (C6) : de la source à ce qui change dans RITA",
    sous_titre=f"Rapport E2, section 2 · {DESSIN}, d'après docs/veille/README.md et les notes S33 à S41",
    boites=[
        Boite("za", 40, 100, 420, 400, "1. CHERCHER ET TRIER", genre="zone"),
        Boite("src", 56, 134, 388, 100, "Les sources", ["5 principales : OWASP, ANSSI, CNIL,", "NIST, Simon Willison ; 2 sous", "condition : éditeurs, arXiv"], "normal"),
        Boite("tri", 56, 254, 388, 100, "Le tri", ["écartés : LinkedIn et X, blogs", "d'éditeurs d'outils de sécurité,", "agrégateurs générés par IA"], "garde"),
        Boite("rel", 56, 374, 388, 100, "Le relevé, chaque lundi", ["9 h à 10 h : flux RSS et Atom, pages ;", "les candidats de la semaine dans", "docs/veille/_candidats-2026-Sxx.md"], "lavis"),

        Boite("zb", 490, 100, 420, 400, "2. QUALIFIER ET ÉCRIRE", genre="zone"),
        Boite("qua", 506, 134, 388, 100, "Qualifier chaque source", ["auteur identifié ? intérêt", "commercial ? confirmée ailleurs ?", "l'incertain est écrit dans la note"], "garde"),
        Boite("note", 506, 254, 388, 100, "La note de la semaine", ["sujet, sources qualifiées, résumé,", "« ce que ça change dans RITA » ;", "docs/veille/2026-Sxx-*.md"], "lavis"),
        Boite("fmt", 506, 374, 388, 100, "Le format", ["Markdown lisible sur GitHub ;", "synthèse S33 à S36 en PDF ;", "liste de contrôle d'accessibilité"], "note"),

        Boite("zc", 940, 100, 420, 400, "3. UTILISER ET PARTAGER", genre="zone"),
        Boite("chg", 956, 134, 388, 100, "Ce que ça change dans RITA", ["S34 (17/08) : 3 cas adverses,", "le filtre d'injection bloque 7 sur 10 ;", "seuil 85 %, test en échec attendu"], "lavis"),
        Boite("par", 956, 254, 388, 100, "Le partage", ["11/10 : note S41 sur Discord,", "canal #veille ; capture versée ;", "aucune réponse au 31/10"], "normal"),
        Boite("lec", 956, 374, 388, 100, "La leçon, S41 va dans ce sens", ["un détecteur peut réussir le test", "sur lequel il a été réglé, et rater", "presque tout sur un autre jeu"], "note"),

        Boite("lim", 40, 520, 1320, 80, "Limites", ["7 relevés et 5 notes de S33 à S44, dont 3 en rattrapage ; rien depuis le 11/10 · aucun échange collectif documenté", "accessibilité des notes non consignée (cases non cochées en S41) · envoi au formateur non effectué"], "manque"),
    ],
    fleches=[
        Fleche("src", "tri", sortie="b", entree="h"),
        Fleche("tri", "rel", sortie="b", entree="h"),
        Fleche("rel", "qua", sortie="d", entree="g"),
        Fleche("qua", "note", sortie="b", entree="h"),
        Fleche("note", "fmt", sortie="b", entree="h", sens="ecriture"),
        Fleche("note", "chg", sortie="d:0.3", entree="g:0.7"),
        Fleche("note", "par", sortie="d:0.7", entree="g:0.7"),
    ],
    legende="Sources : docs/veille/README.md (§ 2 à § 5), relevés et notes S33 à S41, rapport E2, sections 2.2 à 2.7.",
    cles_boites={"normal": "entrée ou sortie", "garde": "contrôle de fiabilité", "lavis": "travail de chaque semaine",
                 "note": "format, leçon", "manque": "limites"},
    cles_fleches={"flux": "enchaînement", "ecriture": "publié en"},
)

# =============================================================================
# B2 : le banc du 03/10, puis les décisions datées (C7)
# =============================================================================
BANC = Schema(
    nom="E2-banc-decision", largeur=1400, hauteur=636,
    titre="Le choix du service (C7) : le banc du 03/10, puis les décisions datées",
    sous_titre=f"Rapport E2, section 3 · {DESSIN}, d'après evidence/C7/ et CONTINUITE.md",
    boites=[
        Boite("zb", 40, 100, 1320, 168, "LE BANC DU 03/10", genre="zone"),
        Boite("jeu", 56, 134, 306, 116, "Le jeu figé", ["10 cas, construits par le", "vrai code : 7 du portefeuille,", "hausse, baisse, Londres"], "stock"),
        Boite("srv", 382, 134, 306, 116, "2 services, 3 passages", ["Azure gpt-5.4 (Global", "Standard), Claude par", "OpenRouter : 60 résultats"], "lavis"),
        Boite("ctl", 708, 134, 306, 116, "Les contrôles", ["garde-fou de sortie, fidélité", "minimale, latence, coût ;", "français noté le 31/10"], "garde"),
        Boite("res", 1034, 134, 306, 116, "Le résultat", ["égalité : 30 sur 30 partout ;", "médiane 3,21 s contre 6,33 s ;", "prix public par briefing :", "0,0047 contre 0,0060 USD"], "note"),

        Boite("zd", 40, 288, 1320, 168, "PUIS, LES DÉCISIONS DATÉES", genre="zone"),
        Boite("d1", 56, 322, 240, 116, "05/10, règle UE", ["aucune donnée", "personnelle hors de", "l'Union européenne"], "garde"),
        Boite("d2", 318, 322, 240, 116, "09/10, zone UE", ["gpt-5.4-dzs-eu ;", "3 appels réels,", "Sweden Central"], "lavis"),
        Boite("d3", 580, 322, 240, 116, "10/10, Mistral", ["futur second, sous", "conditions ; PR #88", "non fusionnée"], "manque"),
        Boite("d4", 842, 322, 240, 116, "11/10, poste", ["Azure seul sur", "le poste ; Claude", "plus appelé"], "lavis"),
        Boite("d5", 1104, 322, 240, 116, "31/10, production", ["Azure seul, défaut", "du code ; conteneur", "relu le 31/10"], "lavis"),

        Boite("lim", 40, 476, 1320, 100, "Limites", ["banc mesuré en Global Standard, pas rejoué en zone UE · notes de français toutes à 1 sur 2 : elles ne départagent pas", "2 appels Azure sur 30 au-dessus de 10 s, tous sur MC.PA · fidélité minimale : 3 erreurs passées (textes 26, 32, 35)", "Anthropic direct jamais mesuré, faute de clé · contrat de Microsoft non relu en entier"], "manque"),
    ],
    fleches=[
        Fleche("jeu", "srv"),
        Fleche("srv", "ctl"),
        Fleche("ctl", "res"),
        Fleche("d1", "d2"),
        Fleche("d2", "d3"),
        Fleche("d3", "d4"),
        Fleche("d4", "d5"),
    ],
    legende="Sources : evidence/C7/preuve-benchmark-2026-10-03.md, resultats-2026-10-03.jsonl, CONTINUITE.md ; rapport E2, sections 3.3 à 3.6.",
    cles_boites={"stock": "jeu de test", "lavis": "mesure, décision appliquée", "garde": "contrôle, règle",
                 "note": "résultat", "manque": "pas actif, limite"},
    cles_fleches={"flux": "puis"},
)

# =============================================================================
# B3 : le service retenu aujourd'hui (C8)
# =============================================================================
SERVICE = Schema(
    nom="E2-service-aujourdhui", largeur=1400, hauteur=760,
    titre="Le service retenu aujourd'hui (C8) : accès, réglage, surveillance",
    sous_titre=f"Rapport E2, section 4 · {DESSIN} · état de main 922349d, en production depuis le 01/11",
    boites=[
        Boite("za", 40, 100, 1320, 200, "L'APPEL D'UN BRIEFING", genre="zone"),
        Boite("cli", 56, 134, 300, 100, "Écran ou client", ["/briefing, /question ;", "clé X-API-Key exigée"], "normal"),
        Boite("gf", 386, 134, 300, 100, "Les garde-fous", ["avant et après l'appel ;", "sortie : jamais de conseil", "d'achat ou de vente (AMF)"], "garde"),
        Boite("llm", 716, 134, 300, 100, "src/llm.py", ["LLM_ORDRE absent : Azure seul", "(test_llm.py, lignes 13-18) ;", "max_completion_tokens"], "lavis"),
        Boite("az", 1046, 134, 298, 100, "Azure AI Foundry", ["déploiement gpt-5.4-dzs-eu,", "configuré en Data Zone EU ;", "Sweden Central lu le 09/10"], "stock"),
        Boite("cle", 1046, 246, 298, 44, "AZURE_FOUNDRY_API_KEY", [], "note"),

        Boite("zs", 40, 320, 1320, 200, "LA SURVEILLANCE", genre="zone"),
        Boite("lf", 386, 354, 300, 100, "Langfuse, région UE", ["une trace par briefing ;", "métadonnées seules depuis", "le 20/10"], "stock"),
        Boite("al", 716, 354, 300, 100, "2 alertes, depuis le 04/10", ["erreurs > 0 sur 1 jour ;", "p95 > 15 000 ms sur 1 jour"], "garde"),
        Boite("is", 1046, 354, 298, 100, "Issue GitHub", ["alerte-incident.yml ; un retour", "à OK n'ouvre plus d'issue", "(INC-009, main du 01/11)"], "normal"),
        Boite("vg", 56, 354, 300, 100, "/sante, puis la vigie", ["/sante : mesures et verdicts ;", "la vigie l'interroge de dehors", "et ouvre ou met à jour l'issue"], "garde"),
        Boite("gd", 56, 466, 1288, 44, "Guide d'exploitation, docs/exploitation.md : accès, installation, tests, services, données ; remise prévue le 05/11", [], "note"),

        Boite("zm", 40, 540, 1320, 160, "CE QUI MANQUE", genre="zone"),
        Boite("m1", 56, 574, 300, 110, "Pas de secours", ["une panne d'Azure rend", "le briefing indisponible"], "manque"),
        Boite("m2", 386, 574, 300, 110, "Mistral Large 4", ["branche mistral-ue, PR #88", "non fusionnée ; contrat", "pas encore lu"], "manque"),
        Boite("m3", 716, 574, 300, 110, "Code présent, inutilisé", ["appels Anthropic, OpenRouter :", "seulement si LLM_ORDRE les", "nomme ; plus en production"], "manque"),
        Boite("m4", 1046, 574, 298, 110, "Limites du suivi", ["portail Azure non décrit ;", "poste et production ont partagé", "un projet Langfuse ; #77 ouvert"], "manque"),
    ],
    fleches=[
        Fleche("cli", "gf"),
        Fleche("gf", "llm"),
        Fleche("llm", "az"),
        Fleche("cle", "llm", sortie="g", entree="d:0.85", sens="lecture"),
        Fleche("llm", "lf", sortie="b:0.1", entree="h:0.9", sens="ecriture", etiquette="trace", pos=0.5),
        Fleche("lf", "al"),
        Fleche("al", "is"),
    ],
    legende="Sources : src/llm.py et tests/test_llm.py à 922349d, evidence/C8/, evidence/C11/preuve-alertes-2026-10-04.md ; rapport E2, section 4.",
    cles_boites={"normal": "client, ticket", "garde": "contrôle, alerte", "lavis": "réglage du fournisseur",
                 "stock": "service externe", "note": "clé, guide", "manque": "manque, pas actif"},
    cles_fleches={"flux": "appel", "lecture": "lit", "ecriture": "écrit"},
)

SCHEMAS = (VEILLE, BANC, SERVICE)


def ecrire(s: Schema) -> None:
    (ICI / f"{s.nom}.svg").write_text(moteur.svg(s), encoding="utf-8", newline="\n")
    (ICI / f"{s.nom}.drawio").write_text(moteur.drawio(s), encoding="utf-8", newline="\n")
    print("écrit", s.nom, ".svg et .drawio")


if __name__ == "__main__":
    trop = [d for schema in SCHEMAS for d in moteur.debordements(schema)]
    if trop:
        raise SystemExit("Texte qui déborde, rien n'est écrit :\n" + "\n".join(trop))
    for schema in SCHEMAS:
        ecrire(schema)
