"""Les deux schémas du rapport E3, générés depuis une seule description : .drawio ET .svg.

Pourquoi un générateur plutôt que deux fichiers dessinés à la main : la règle du dépôt veut un
`.drawio` éditable (pour corriger) ET une image lisible (pour voir), et deux fichiers tenus à la
main divergent à la première retouche. Ici, une liste de boîtes et de flèches produit les deux ;
le `.png` est ensuite rendu depuis le `.svg` par Chrome sans fenêtre (commande dans le README du
dossier). Mêmes couleurs que les schémas de C4 et des rapports : encre #16202B, accent #14607F,
lavis #ECF3F7, signal #9E4318.

Lancer :  C:\\Python314\\python.exe docs\\rapports\\E3\\schemas\\generer_schemas.py
"""
from __future__ import annotations

import html
from dataclasses import dataclass, field
from pathlib import Path

ICI = Path(__file__).parent

INK, SOFT, ACCENT, WASH, RULE = "#16202B", "#4A5766", "#14607F", "#ECF3F7", "#D5DCE4"
FLAG, FLAG_WASH, STORE = "#9E4318", "#FBF1EC", "#D8E3EA"


@dataclass
class Boite:
    id: str
    x: int
    y: int
    w: int
    h: int
    titre: str
    lignes: list[str] = field(default_factory=list)
    genre: str = "normal"   # normal | lavis | stock | manque | zone | note


@dataclass
class Fleche:
    de: str
    vers: str
    etiquette: str = ""
    pointille: bool = False
    # points de sortie et d'entrée : "d" droite, "g" gauche, "h" haut, "b" bas
    sortie: str = "d"
    entree: str = "g"


@dataclass
class Schema:
    nom: str
    titre: str
    sous_titre: str
    largeur: int
    hauteur: int
    boites: list[Boite]
    fleches: list[Fleche]
    legende: str


STYLES_SVG = {
    "normal": dict(fill="#FFFFFF", stroke=ACCENT, dash=""),
    "lavis": dict(fill=WASH, stroke=ACCENT, dash=""),
    "stock": dict(fill=STORE, stroke="none", dash=""),
    "manque": dict(fill=FLAG_WASH, stroke=FLAG, dash="6,4"),
    "zone": dict(fill="none", stroke=RULE, dash="7,5"),
    "note": dict(fill="#F7F9FB", stroke=RULE, dash=""),
}
STYLES_DRAWIO = {
    "normal": f"rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor={ACCENT};align=left;spacingLeft=8;fontSize=9;verticalAlign=top;",
    "lavis": f"rounded=0;whiteSpace=wrap;html=1;fillColor={WASH};strokeColor={ACCENT};align=left;spacingLeft=8;fontSize=9;verticalAlign=top;",
    "stock": f"rounded=0;whiteSpace=wrap;html=1;fillColor={STORE};strokeColor=none;align=left;spacingLeft=8;fontSize=9;verticalAlign=top;",
    "manque": f"rounded=0;whiteSpace=wrap;html=1;fillColor={FLAG_WASH};strokeColor={FLAG};dashed=1;align=left;spacingLeft=8;fontSize=9;verticalAlign=top;",
    "zone": f"rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor={RULE};dashed=1;align=left;verticalAlign=top;fontSize=9;fontColor={SOFT};spacingLeft=6;",
    "note": f"rounded=0;whiteSpace=wrap;html=1;fillColor=#F7F9FB;strokeColor={RULE};align=left;spacingLeft=8;fontSize=8.5;fontColor={SOFT};verticalAlign=top;",
}


def _ancre(b: Boite, cote: str) -> tuple[float, float]:
    """`cote` vaut d, g, h ou b, suivi au besoin de `:f` (fraction de la largeur ou de la hauteur)
    pour sortir d'une boîte ailleurs qu'en son centre et éviter de traverser une voisine."""
    lettre, _, frac = cote.partition(":")
    f = float(frac) if frac else 0.5
    return {"d": (b.x + b.w, b.y + b.h * f), "g": (b.x, b.y + b.h * f),
            "h": (b.x + b.w * f, b.y), "b": (b.x + b.w * f, b.y + b.h)}[lettre]


def svg(s: Schema) -> str:
    e = html.escape
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<svg xmlns="http://www.w3.org/2000/svg" width="{s.largeur}" height="{s.hauteur}" viewBox="0 0 {s.largeur} {s.hauteur}" font-family="Segoe UI,Calibri,Arial,sans-serif">',
           f'<defs><marker id="fl" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><polygon points="0 0,10 4,0 8" fill="{SOFT}"/></marker></defs>',
           f'<rect width="{s.largeur}" height="{s.hauteur}" fill="#FFFFFF"/>',
           f'<rect x="40" y="18" width="{s.largeur - 80}" height="3" fill="{ACCENT}"/>',
           f'<text x="40" y="46" font-family="Georgia,serif" font-size="19" font-weight="600" fill="{INK}">{e(s.titre)}</text>',
           f'<text x="40" y="66" font-family="Georgia,serif" font-size="11" font-style="italic" fill="{SOFT}">{e(s.sous_titre)}</text>']
    par_id = {b.id: b for b in s.boites}
    for b in s.boites:
        st = STYLES_SVG[b.genre]
        dash = f' stroke-dasharray="{st["dash"]}"' if st["dash"] else ""
        out.append(f'<rect x="{b.x}" y="{b.y}" width="{b.w}" height="{b.h}" fill="{st["fill"]}" stroke="{st["stroke"]}" stroke-width="1.2"{dash}/>')
        couleur_titre = SOFT if b.genre in ("zone", "note") else (FLAG if b.genre == "manque" else INK)
        taille = 9.5 if b.genre == "zone" else 10.5
        out.append(f'<text x="{b.x + 8}" y="{b.y + 16}" font-size="{taille}" font-weight="700" fill="{couleur_titre}">{e(b.titre)}</text>')
        for i, l in enumerate(b.lignes):
            out.append(f'<text x="{b.x + 8}" y="{b.y + 31 + i * 13}" font-size="9" fill="{SOFT}">{e(l)}</text>')
    for f in s.fleches:
        a, bb = par_id[f.de], par_id[f.vers]
        x1, y1 = _ancre(a, f.sortie)
        x2, y2 = _ancre(bb, f.entree)
        dash = ' stroke-dasharray="5,4"' if f.pointille else ""
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{SOFT}" stroke-width="1.3" marker-end="url(#fl)"{dash}/>')
        if f.etiquette:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 5
            out.append(f'<text x="{mx}" y="{my}" font-size="8.5" fill="{SOFT}" text-anchor="middle">{e(f.etiquette)}</text>')
    out.append(f'<text x="40" y="{s.hauteur - 16}" font-size="9" fill="{SOFT}">{e(s.legende)}</text>')
    out.append("</svg>")
    return "\n".join(out)


def drawio(s: Schema) -> str:
    e = html.escape
    cells = ['<mxCell id="0" />', '<mxCell id="1" parent="0" />',
             f'<mxCell id="topline" value="" style="line;strokeWidth=2.5;html=1;strokeColor={ACCENT};" vertex="1" parent="1"><mxGeometry x="40" y="14" width="{s.largeur - 80}" height="10" as="geometry" /></mxCell>',
             f'<mxCell id="ttl" value="{e(s.titre)}" style="text;html=1;align=left;fontSize=17;fontStyle=1;fontColor={INK};fontFamily=Georgia;" vertex="1" parent="1"><mxGeometry x="40" y="28" width="{s.largeur - 100}" height="24" as="geometry" /></mxCell>',
             f'<mxCell id="sub" value="{e(s.sous_titre)}" style="text;html=1;align=left;fontSize=10.5;fontStyle=2;fontColor={SOFT};fontFamily=Georgia;" vertex="1" parent="1"><mxGeometry x="40" y="52" width="{s.largeur - 100}" height="16" as="geometry" /></mxCell>']
    for b in s.boites:
        corps = "<br>".join(f'<font style="font-size:8.5px;color:{SOFT}">{e(l)}</font>' for l in b.lignes)
        valeur = f"<b>{e(b.titre)}</b>" + ("<br>" + corps if corps else "")
        cells.append(f'<mxCell id="{b.id}" value="{e(valeur)}" style="{STYLES_DRAWIO[b.genre]}" vertex="1" parent="1"><mxGeometry x="{b.x}" y="{b.y}" width="{b.w}" height="{b.h}" as="geometry" /></mxCell>')
    for i, f in enumerate(s.fleches):
        style = f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor={SOFT};strokeWidth=1.3;endArrow=classic;" + ("dashed=1;" if f.pointille else "")
        cells.append(f'<mxCell id="f{i}" value="{e(f.etiquette)}" style="{style}" edge="1" parent="1" source="{f.de}" target="{f.vers}"><mxGeometry relative="1" as="geometry" /></mxCell>')
    cells.append(f'<mxCell id="leg" value="{e(s.legende)}" style="text;html=1;align=left;fontSize=9;fontColor={SOFT};" vertex="1" parent="1"><mxGeometry x="40" y="{s.hauteur - 30}" width="{s.largeur - 80}" height="20" as="geometry" /></mxCell>')
    return ('<mxfile host="app.diagrams.net" modified="2026-10-03T00:00:00.000Z" agent="RITA" version="24.0.0" type="device">\n'
            f'  <diagram id="{s.nom}" name="{e(s.titre)}">\n'
            f'    <mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{s.largeur}" pageHeight="{s.hauteur}" math="0" shadow="0">\n'
            '      <root>\n        ' + "\n        ".join(cells) + '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')


# =============================================================================
# Schéma 1 : l'architecture autour du modèle (chemin d'une requête, le 03/10/2026)
# =============================================================================
ARCHI = Schema(
    nom="E3-architecture", largeur=1500, hauteur=900,
    titre="RITA : le chemin d'un briefing, et tout ce qui le regarde passer",
    sous_titre="Rapport E3, section 2 · état du code au 3 octobre 2026 · un seul utilisateur, un modèle fourni, aucune action",
    boites=[
        Boite("zc", 40, 90, 250, 300, "CLIENTS (C10)", genre="zone"),
        Boite("web", 56, 118, 218, 72, "Interface web", ["frontend/, HTML, CSS, JS sans build", "2 écrans : portefeuille, indicateurs", "clé saisie, sessionStorage, 403 affiché"], "normal"),
        Boite("mcp", 56, 204, 218, 72, "Passerelle MCP", ["passerelle_mcp/serveur.py", "3 outils en lecture seule", "appelle l'API par HTTP, avec la clé"], "normal"),
        Boite("curl", 56, 290, 218, 72, "curl, /docs (OpenAPI 3.1.0)", ["POST /briefing?ticker=MC.PA", "le seul chemin vers le modèle", "aucun texte libre : un ticker"], "normal"),

        Boite("api", 340, 118, 290, 120, "api/main.py : l'API (C9)", ["middleware : un request_id par requête (X-Request-ID)", "clé X-API-Key, 16 car. min., temps constant, 403", "aucune clé par défaut (INC-001, OWASP API2)", "13 routes ; /briefing est la seule qui parle au modèle", "journal : servi, refusé, 502 (request_id, jamais le texte)"], "lavis"),

        Boite("zg", 340, 262, 290, 330, "graph/workflow.py : LangGraph, 3 nœuds, arêtes fixes", genre="zone"),
        Boite("scout", 356, 290, 258, 58, "scout", ["lit PostgreSQL : cours, variation, ADTV20", "fraîcheur en jours ouvrés, cotation périmée"], "normal"),
        Boite("rag", 356, 362, 258, 86, "rag", ["garde-fou d'ENTRÉE : intention AMF, 7 motifs,", "  100 % / 0 % (03/10), avant tout accès à la base", "ChromaDB : filtre ticker puis hybride dense + BM25", "refus OUT_OF_CORPUS si rien ne cite la valeur"], "normal"),
        Boite("red", 356, 462, 258, 58, "redacteur", ["agents/analyst.py : prompt (interdit AMF écrit)", "src/llm.py : la cascade"], "normal"),
        Boite("casc", 356, 532, 258, 48, "Foundry → Anthropic → OpenRouter", ["une génération tracée par essai ; repli ≈ 0,3 s"], "lavis"),

        Boite("sortie", 340, 612, 290, 70, "guardrails/sortie.py : garde-fou de SORTIE (C17)", ["9 motifs, 70 % / 0 % (03/10) ; échec fermé", "texte remplacé par un refus, HTTP 200, conforme_amf=false"], "lavis"),
        Boite("rep", 340, 700, 290, 56, "Réponse JSON", ["ticker, prix, variation, briefing, conforme_amf,", "motifs_amf ; en-tête X-Request-ID"], "normal"),

        Boite("pg", 700, 290, 190, 58, "PostgreSQL 18 (E1)", ["9 tables, 1 vue, 273 608 lignes (11/08)", "écrit par le seul pipeline"], "stock"),
        Boite("chroma", 700, 362, 190, 58, "ChromaDB (index)", ["articles vectorisés, reconstruit chaque nuit", "1 359 documents (27/09)"], "stock"),
        Boite("nuit", 700, 612, 220, 100, "Collecte nocturne, 19 h", ["pipelines/ingest.py, tâche planifiée Windows", "yfinance, RSS, scraping, FRED, BCE", "garde-fou d'INJECTION sur les articles :", "  12 motifs, 70 % / 0 % (03/10)", "40 journaux du 24/08 au 02/10"], "normal"),

        Boite("zo", 1040, 90, 380, 600, "OBSERVABILITÉ (C11, C20)", genre="zone"),
        Boite("lf", 1056, 118, 348, 196, "Langfuse Cloud, région UE (Irlande)", ["une trace par briefing, identifiant = request_id :", "  briefing  (verdict AMF, note conforme_amf)", "  ├─ scout", "  ├─ rag ─ garde-fou-entree", "  ├─ redacteur ─ briefing-llm ─ llm-<fournisseur>", "  └─ garde-fou-sortie", "jetons, erreur du repli, niveau WARNING au refus", "première trace réelle : 02/10 18:39 ; palier gratuit"], "lavis"),
        Boite("fr", 1056, 416, 348, 58, "GET /donnees/fraicheur + bandeau", ["retard en jours ouvrés, 3 états, lisible sans couleur", "la panne la plus fréquente : la collecte d'hier"], "normal"),
        Boite("al", 1056, 330, 348, 70, "Alertes (2, palier gratuit) → GitHub Actions", [".github/workflows/alerte-incident.yml", "ouvre ou commente une issue « incident »", "bouton manuel pour prouver la chaîne"], "normal"),
        Boite("tb", 1056, 490, 348, 56, "Tableau de bord « RITA C11 »", ["générations par fournisseur · p95 de briefing-llm", "observations en ERROR ou WARNING"], "manque"),
        Boite("cout", 1056, 562, 348, 56, "Coût par briefing", ["à zéro pour OpenRouter : nom de modèle absent", "de la grille de prix Langfuse ; à corriger"], "manque"),

        Boite("sand", 700, 728, 220, 70, "Bac à sable", ["la suite de tests ne trace jamais", "(conftest.py, INC-006) ; doubles de client", "626 tests, 93,66 % (02/10)"], "note"),
        Boite("test", 700, 814, 220, 56, "Tests en CI à chaque poussée", ["test.yml : suite + couverture ≥ 90 %,", "garde-fous mesurés, portes xfail strict"], "note"),
    ],
    fleches=[
        Fleche("web", "api", "HTTP + clé"), Fleche("mcp", "api", "HTTP + clé"), Fleche("curl", "api"),
        Fleche("api", "scout", sortie="b", entree="h"),
        Fleche("scout", "rag", sortie="b", entree="h"), Fleche("rag", "red", sortie="b", entree="h"), Fleche("red", "casc", sortie="b", entree="h"),
        Fleche("casc", "sortie", sortie="b", entree="h"), Fleche("sortie", "rep", sortie="b", entree="h"),
        Fleche("pg", "scout", "lecture", sortie="g", entree="d"), Fleche("chroma", "rag", "lecture", sortie="g", entree="d"),
        Fleche("nuit", "pg", "écrit", sortie="h:0.95", entree="b:0.97"), Fleche("nuit", "chroma", "indexe", sortie="h:0.45", entree="b:0.5"),
        Fleche("api", "lf", "trace (racine et générations)", sortie="d", entree="g"),
        Fleche("lf", "al", sortie="b", entree="h", pointille=True),
    ],
    legende="Boîtes pleines : code présent et testé au 03/10/2026. Boîtes pointillées orange : conçu, non construit. Mesures datées dans le rapport, section 6.",
)

# =============================================================================
# Schéma 2 : la chaîne de livraison (C13), ce qui tourne et ce qui manque
# =============================================================================
CHAINE = Schema(
    nom="E3-chaine-livraison", largeur=1400, hauteur=760,
    titre="RITA : la chaîne de livraison continue, du poste au serveur",
    sous_titre="Rapport E3, section 7 · cinq workflows GitHub Actions · état au 3 octobre 2026",
    boites=[
        Boite("zp", 40, 90, 260, 260, "POSTE D'ERA", genre="zone"),
        Boite("dev", 56, 118, 228, 70, "Branche develop", ["un commit = une intention", "tests écrits avant le code (TDD)", "git push origin develop"], "normal"),
        Boite("hook", 56, 202, 228, 60, "Hook pre-push (.githooks/)", ["refuse la poussée directe sur main", "activé une fois par clone"], "lavis"),
        Boite("dod", 56, 276, 228, 60, "scripts/verifier_livrable.py", ["Definition of Done : tests, liens,", "ETAT et CHANGELOG, arbre propre"], "normal"),

        Boite("zgh", 340, 90, 620, 500, "GITHUB (dépôt privé Ganda15/rita-agent)", genre="zone"),
        Boite("test", 356, 118, 280, 100, "test.yml : à chaque poussée et PR", ["job pytest : suite + couverture ≥ 90 %", "  (seuil dans .coveragerc, --cov sur la commande)", "job evals : garde-fous mesurés,", "  portes non compensables (xfail strict à 85 %)", "626 passed, 93,66 % le 02/10"], "lavis"),
        Boite("pr", 664, 118, 280, 100, "revue-pr.yml : chaque PR vers main", ["relecture adversariale par Claude Code", "(action officielle, jeton d'abonnement en secret)", "grille de lecture : AGENTS.md et CLAUDE.md", "22 PR fusionnées au 02/10"], "lavis"),
        Boite("main", 356, 236, 280, 56, "Branche main", ["ne bouge que par une PR depuis develop", "un livrable = un tag livrable-E<n>-v<k>"], "normal"),
        Boite("liv", 356, 310, 588, 120, "livraison.yml : poussée, PR, et tag livrable-*", ["1. tests, porte de livraison (rien n'est construit si rouge)", "2. construction de l'image, jamais publiée ici", "3. l'image construite démarre et répond sur /health", "4. l'accès est restreint : 403 sans clé", "5. publication sur ghcr.io/ganda15/rita-api, seulement sur un tag (issue #22 : avant, la publication précédait la vérification)"], "lavis"),
        Boite("gisk", 664, 236, 280, 56, "scan-giskard.yml : manuel", ["scan d'attaques, deux frontières", "plafond de coût saisi ; run 9 le 20/09"], "normal"),
        Boite("alerte", 664, 524, 280, 60, "alerte-incident.yml", ["reçu de Langfuse (repository_dispatch)", "ou bouton manuel ; ouvre ou commente", "une issue « incident » ; label créé"], "normal"),
        Boite("ghcr", 356, 446, 588, 70, "Image sur GHCR", ["python:3.13-slim, deux étapes, non-root (UID 10001)", "ghcr.io/ganda15/rita-api:livrable-E<n>-v<k>", "jamais publiée pour de vrai au 03/10"], "stock"),

        Boite("zs", 1000, 90, 360, 260, "SERVEUR HETZNER (CX23, 4 Go, HTTPS Caddy)", genre="zone"),
        Boite("srv", 1016, 118, 328, 86, "docker compose (manuel, par SSH)", ["pull de l'image taguée, up -d --force-recreate api", "conteneur en lecture seule, no-new-privileges", "variables Langfuse transmises depuis le 02/10"], "normal"),
        Boite("gel", 1016, 220, 328, 56, "Copie figée depuis le 19/08/2026", ["première livraison de cette chaîne à faire", "les variables Langfuse ne sont pas encore posées"], "manque"),
        Boite("lfs", 1016, 290, 328, 44, "Langfuse Cloud UE ← traces du serveur", ["dès que les variables y sont"], "note"),

        Boite("zm", 1000, 380, 360, 210, "CONÇU, NON CONSTRUIT (Mardik ③, Industrialisation)", genre="zone"),
        Boite("rb", 1016, 408, 328, 44, "rollback.yml : retour arrière", ["tag précédent redéployé, jamais reconstruit"], "manque"),
        Boite("man", 1016, 462, 328, 44, "Manifeste de version, GET /version", ["modèle daté, prompt_version, config, index"], "manque"),
        Boite("filtre", 1016, 516, 328, 44, "Filtre de chemin + gate sur le vrai modèle", ["porte payante seulement si prompt ou jeu changent"], "manque"),

        Boite("note", 40, 380, 260, 100, "Ce que la chaîne coche pour C13", ["test → construction → démarrage vérifié →", "accès vérifié → publication sur tag,", "exécuté par la plateforme à chaque poussée.", "Un Dockerfile seul ne coche aucun critère."], "note"),
        Boite("rouge", 40, 500, 260, 90, "Chute réelle de la CI, 28/09", ["requirements.txt non épinglé : pip a", "construit pandas depuis les sources.", "Cause identifiée, correction en attente (#23)."], "note"),
    ],
    fleches=[
        Fleche("dev", "test", "push", sortie="d", entree="g"),
        Fleche("test", "pr", "puis la PR", sortie="d", entree="g"),
        Fleche("pr", "main", "fusion relue", sortie="b", entree="h"),
        Fleche("main", "liv", "tag livrable-*", sortie="b", entree="h"),
        Fleche("liv", "ghcr", "étape 5", sortie="b", entree="h"),
        Fleche("ghcr", "srv", "pull", sortie="d:0.3", entree="g:0.5", pointille=True),
        Fleche("hook", "main", "refuse le direct", sortie="d", entree="g", pointille=True),
        Fleche("lfs", "alerte", "alerte", sortie="g", entree="d", pointille=True),
    ],
    legende="Boîtes pleines : existe et tourne (dates mesurées). Pointillé orange : conçu, non construit. Flèches pointillées : manuel ou non encore exécuté.",
)


def ecrire(s: Schema) -> None:
    (ICI / f"{s.nom}.svg").write_text(svg(s), encoding="utf-8", newline="\n")
    (ICI / f"{s.nom}.drawio").write_text(drawio(s), encoding="utf-8", newline="\n")
    print("écrit", s.nom, ".svg et .drawio")


if __name__ == "__main__":
    ecrire(ARCHI)
    ecrire(CHAINE)
