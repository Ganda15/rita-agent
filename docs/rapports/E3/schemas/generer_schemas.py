"""Les cinq schémas du rapport E3, générés depuis une seule description : .drawio ET .svg.

Pourquoi un générateur plutôt que deux fichiers dessinés à la main : la règle du dépôt veut un
`.drawio` éditable (pour corriger) ET une image lisible (pour voir), et deux fichiers tenus à la
main divergent à la première retouche. Ici, une liste de boîtes et de flèches produit les deux ;
le `.png` est ensuite rendu depuis le `.svg` par Chrome sans fenêtre (commande dans le README du
dossier).

Charte refaite le 04/10/2026 à la demande d'Era, sur un modèle qu'il a fourni : le texte gris en
9 px ne se lisait pas une fois le schéma réduit à la largeur d'une page, et des boîtes presque
toutes bleues ne disaient pas leur rôle. Désormais : texte presque noir et nettement plus grand,
traits épais ; une couleur par RÔLE de boîte (bande à gauche, bordure, fond) ; une couleur par
SENS de flèche (flux, écriture, lecture, erreur, manuel, données personnelles) ; une légende
dessinée en bas de chaque schéma, avec un échantillon de chaque couleur employée.

Lancer :  C:\\Python314\\python.exe docs\\rapports\\E3\\schemas\\generer_schemas.py
"""
from __future__ import annotations

import html
from dataclasses import dataclass, field
from pathlib import Path

ICI = Path(__file__).parent

NAVY, INK, SOFT, ACCENT, RULE = "#0B2A5B", "#111827", "#1F2937", "#1565C0", "#94A3B8"
POLICE = "Segoe UI,Calibri,Arial,sans-serif"

# Tailles, en pixels du schéma (largeur 1400 à 1500, réduite ensuite à la largeur d'une page).
T_TITRE, T_SOUS_TITRE, T_ZONE, T_BOITE, T_LIGNE, T_ETIQUETTE, T_LEGENDE = 30, 15, 13.5, 14, 11.5, 12.5, 12.5
INTERLIGNE, Y_TITRE_BOITE, Y_PREMIERE_LIGNE = 15.5, 21, 40
DECALAGE = 16      # le contenu descend sous un titre devenu plus grand
BANDE, TRAIT_BOITE, TRAIT_FLECHE = 7, 2, 3

# Une couleur par rôle de boîte : (bande et bordure, fond, titre).
ROLES = {
    "normal": ("#1E293B", "#FFFFFF", NAVY),        # élément : source, client, étape, défaut mesuré
    "lavis":  ("#1565C0", "#E3F0FD", NAVY),        # le cœur : code qui traite, décision appliquée
    "garde":  ("#C2410C", "#FFF1E6", "#9A3412"),   # garde-fou, contrôle
    "stock":  ("#6D28D9", "#F1EAFE", "#4C1D95"),   # réserve de données, service externe, artefact
    "manque": ("#D32F2F", "#FDECEC", "#C62828"),   # conçu non construit, limite, défaut connu (pointillé)
    "note":   ("#475569", "#F1F5F9", NAVY),        # preuve, fichier à ouvrir, contexte
}
# Une couleur par sens de flèche : (couleur, pointillé).
SENS = {
    "flux":     (NAVY, ""),            # passage, appel, enchaînement
    "ecriture": ("#1565C0", ""),       # écrit en base ou dans un index
    "lecture":  ("#15803D", ""),       # lecture seule
    "erreur":   ("#D32F2F", "9,6"),    # réponse d'erreur, refus
    "manuel":   ("#64748B", "9,6"),    # manuel, ou pas encore exécuté
    "perso":    ("#A21CAF", "9,6"),    # données personnelles (RGPD)
}
LEGENDE_H = 40     # hauteur ajoutée sous le schéma pour la ligne de source
LIGNE_LEGENDE = 28 # une ligne de légende de plus quand elle ne tient pas en largeur


@dataclass
class Boite:
    id: str
    x: int
    y: int
    w: int
    h: int
    titre: str
    lignes: list[str] = field(default_factory=list)
    genre: str = "normal"   # normal | lavis | garde | stock | manque | zone | note


@dataclass
class Fleche:
    de: str
    vers: str
    etiquette: str = ""
    pointille: bool = False
    # points de sortie et d'entrée : "d" droite, "g" gauche, "h" haut, "b" bas
    sortie: str = "d"
    entree: str = "g"
    sens: str = ""          # flux | ecriture | lecture | erreur | manuel | perso ; vide : flux, ou manuel si pointillé
    pos: float = 0.5        # où poser l'étiquette le long de la flèche (0 départ, 1 arrivée)

    @property
    def genre(self) -> str:
        return self.sens or ("manuel" if self.pointille else "flux")


@dataclass
class Schema:
    nom: str
    titre: str
    sous_titre: str
    largeur: int
    hauteur: int            # la légende dessinée occupe le bas de cette hauteur
    boites: list[Boite]
    fleches: list[Fleche]
    legende: str                                              # la source des chiffres, en une ligne
    cles_boites: dict[str, str] = field(default_factory=dict)   # rôle → ce qu'il veut dire ICI
    cles_fleches: dict[str, str] = field(default_factory=dict)  # sens → ce qu'il veut dire ICI

    @property
    def hauteur_totale(self) -> int:
        return self.hauteur + DECALAGE + LEGENDE_H + LIGNE_LEGENDE * (len({l for *_, l in _disposer_legende(self)}) - 1)


def _ancre(b: Boite, cote: str) -> tuple[float, float]:
    """`cote` vaut d, g, h ou b, suivi au besoin de `:f` (fraction de la largeur ou de la hauteur)
    pour sortir d'une boîte ailleurs qu'en son centre et éviter de traverser une voisine."""
    lettre, _, frac = cote.partition(":")
    f = float(frac) if frac else 0.5
    return {"d": (b.x + b.w, b.y + b.h * f), "g": (b.x, b.y + b.h * f),
            "h": (b.x + b.w * f, b.y), "b": (b.x + b.w * f, b.y + b.h)}[lettre]


def _largeur_texte(texte: str, taille: float) -> float:
    """Estimation pour espacer la légende (la vraie mesure se fait au rendu, dans un navigateur)."""
    return len(texte) * taille * 0.5


def _disposer_legende(s: Schema) -> list[tuple[str, str, str, float, int]]:
    """(type, clé, libellé, x, ligne) de chaque entrée ; passe à la ligne avant le bord droit."""
    places, x, ligne = [], 124.0, 0
    entrees = [("boite", k, v) for k, v in s.cles_boites.items()] + [("fleche", k, v) for k, v in s.cles_fleches.items()]
    for genre, cle, libelle in entrees:
        largeur = (36 if genre == "boite" else 50) + _largeur_texte(libelle, T_LEGENDE)
        if x + largeur > s.largeur - 40 and x > 124:
            x, ligne = 124.0, ligne + 1
        places.append((genre, cle, libelle, x, ligne))
        x += largeur + 30
    return places or [("rien", "", "", 124.0, 0)]


def _legende_svg(s: Schema) -> list[str]:
    e = html.escape
    out, y0 = [], s.hauteur - 8
    nb = len({l for *_, l in _disposer_legende(s)})
    out.append(f'<rect x="40" y="{s.hauteur - 34}" width="{s.largeur - 80}" height="1.5" fill="{RULE}"/>')
    out.append(f'<text x="40" y="{y0 + 5}" font-size="{T_LEGENDE + 1}" font-weight="700" fill="{NAVY}">Légende</text>')
    for genre, cle, libelle, x, ligne in _disposer_legende(s):
        y = y0 + ligne * LIGNE_LEGENDE
        if genre == "boite":
            trait, fond, _ = ROLES[cle]
            dash = ' stroke-dasharray="5,3"' if cle == "manque" else ""
            out.append(f'<rect x="{x}" y="{y - 9}" width="28" height="18" fill="{fond}" stroke="{trait}" stroke-width="{TRAIT_BOITE}"{dash}/>')
            out.append(f'<rect x="{x}" y="{y - 9}" width="6" height="18" fill="{trait}"/>')
            out.append(f'<text x="{x + 36}" y="{y + 5}" font-size="{T_LEGENDE}" fill="{INK}">{e(libelle)}</text>')
        elif genre == "fleche":
            couleur, dash = SENS[cle]
            d = f' stroke-dasharray="{dash}"' if dash else ""
            out.append(f'<line x1="{x}" y1="{y}" x2="{x + 40}" y2="{y}" stroke="{couleur}" stroke-width="{TRAIT_FLECHE}"{d} marker-end="url(#fl-{cle})"/>')
            out.append(f'<text x="{x + 50}" y="{y + 5}" font-size="{T_LEGENDE}" fill="{INK}">{e(libelle)}</text>')
    out.append(f'<text x="40" y="{s.hauteur + 26 + (nb - 1) * LIGNE_LEGENDE}" font-size="{T_LEGENDE}" fill="{SOFT}">{e(s.legende)}</text>')
    return out


def svg(s: Schema) -> str:
    e = html.escape
    marqueurs = "".join(
        f'<marker id="fl-{nom}" markerWidth="5" markerHeight="5" refX="4.2" refY="2.5" orient="auto" markerUnits="strokeWidth"><polygon points="0 0,5 2.5,0 5" fill="{couleur}"/></marker>'
        for nom, (couleur, _) in SENS.items())
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<svg xmlns="http://www.w3.org/2000/svg" width="{s.largeur}" height="{s.hauteur_totale}" viewBox="0 0 {s.largeur} {s.hauteur_totale}" font-family="{POLICE}">',
           f'<defs>{marqueurs}</defs>',
           f'<rect width="{s.largeur}" height="{s.hauteur_totale}" fill="#FFFFFF"/>',
           f'<rect x="40" y="16" width="{s.largeur - 80}" height="5" fill="{ACCENT}"/>',
           f'<text x="40" y="54" font-size="{T_TITRE}" font-weight="700" fill="{NAVY}">{e(s.titre)}</text>',
           f'<text x="40" y="80" font-size="{T_SOUS_TITRE}" fill="{SOFT}">{e(s.sous_titre)}</text>']
    out.append(f'<g transform="translate(0,{DECALAGE})">')
    par_id = {b.id: b for b in s.boites}
    # Les zones d'abord (fond), puis les boîtes, puis les flèches, puis les titres de zone.
    for b in s.boites:
        if b.genre == "zone":
            out.append(f'<rect x="{b.x}" y="{b.y}" width="{b.w}" height="{b.h}" fill="#F8FAFC" stroke="{RULE}" stroke-width="1.5" stroke-dasharray="8,6"/>')
    for b in s.boites:
        if b.genre == "zone":
            continue
        trait, fond, titre = ROLES[b.genre]
        dash = ' stroke-dasharray="8,5"' if b.genre == "manque" else ""
        out.append(f'<rect x="{b.x}" y="{b.y}" width="{b.w}" height="{b.h}" fill="{fond}" stroke="{trait}" stroke-width="{TRAIT_BOITE}"{dash}/>')
        out.append(f'<rect x="{b.x}" y="{b.y}" width="{BANDE}" height="{b.h}" fill="{trait}"/>')
        tx = b.x + BANDE + 10
        out.append(f'<text x="{tx}" y="{b.y + Y_TITRE_BOITE}" font-size="{T_BOITE}" font-weight="700" fill="{titre}">{e(b.titre)}</text>')
        for i, l in enumerate(b.lignes):
            out.append(f'<text x="{tx}" y="{b.y + Y_PREMIERE_LIGNE + i * INTERLIGNE}" font-size="{T_LIGNE}" fill="{INK}">{e(l)}</text>')
    for f in s.fleches:
        a, bb = par_id[f.de], par_id[f.vers]
        x1, y1 = _ancre(a, f.sortie)
        x2, y2 = _ancre(bb, f.entree)
        couleur, dash = SENS[f.genre]
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{couleur}" stroke-width="{TRAIT_FLECHE}" marker-end="url(#fl-{f.genre})"{d}/>')
        if f.etiquette:
            mx, my = x1 + (x2 - x1) * f.pos, y1 + (y2 - y1) * f.pos
            out.append(f'<text x="{mx:.1f}" y="{my + 4:.1f}" font-size="{T_ETIQUETTE}" font-weight="700" fill="{couleur}" text-anchor="middle" stroke="#FFFFFF" stroke-width="5" paint-order="stroke">{e(f.etiquette)}</text>')
    # Titres de zone en dernier, avec un liseré blanc : une flèche qui passe dessous ne les coupe pas.
    for b in s.boites:
        if b.genre == "zone":
            out.append(f'<text x="{b.x + 14}" y="{b.y + 22}" font-size="{T_ZONE}" font-weight="700" fill="{NAVY}" letter-spacing="0.3" stroke="#F8FAFC" stroke-width="5" paint-order="stroke">{e(b.titre)}</text>')
    out += _legende_svg(s)
    out.append("</g>")
    out.append("</svg>")
    return "\n".join(out)


def _style_boite(genre: str) -> str:
    if genre == "zone":
        return f"rounded=0;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor={RULE};strokeWidth=1.5;dashed=1;align=left;verticalAlign=top;fontSize={T_ZONE};fontStyle=1;fontColor={NAVY};spacingLeft=12;"
    trait, fond, _ = ROLES[genre]
    return (f"rounded=0;whiteSpace=wrap;html=1;fillColor={fond};strokeColor={trait};strokeWidth={TRAIT_BOITE};"
            + ("dashed=1;" if genre == "manque" else "")
            + f"align=left;spacingLeft=14;fontSize={T_LIGNE};fontColor={INK};verticalAlign=top;")


def drawio(s: Schema) -> str:
    e = html.escape
    cells = ['<mxCell id="0" />', '<mxCell id="1" parent="0" />',
             f'<mxCell id="topline" value="" style="line;strokeWidth=5;html=1;strokeColor={ACCENT};" vertex="1" parent="1"><mxGeometry x="40" y="12" width="{s.largeur - 80}" height="10" as="geometry" /></mxCell>',
             f'<mxCell id="ttl" value="{e(s.titre)}" style="text;html=1;align=left;fontSize={T_TITRE};fontStyle=1;fontColor={NAVY};" vertex="1" parent="1"><mxGeometry x="40" y="26" width="{s.largeur - 100}" height="36" as="geometry" /></mxCell>',
             f'<mxCell id="sub" value="{e(s.sous_titre)}" style="text;html=1;align=left;fontSize={T_SOUS_TITRE};fontColor={SOFT};" vertex="1" parent="1"><mxGeometry x="40" y="64" width="{s.largeur - 100}" height="22" as="geometry" /></mxCell>']
    for b in sorted(s.boites, key=lambda b: b.genre != "zone"):
        if b.genre == "zone":
            valeur = e(b.titre)
        else:
            _, _, titre = ROLES[b.genre]
            corps = "<br>".join(f'<font style="font-size:{T_LIGNE}px;color:{INK}">{e(l)}</font>' for l in b.lignes)
            valeur = e(f'<b><font style="font-size:{T_BOITE}px;color:{titre}">{e(b.titre)}</font></b>' + ("<br>" + corps if corps else ""))
        cells.append(f'<mxCell id="{b.id}" value="{valeur}" style="{_style_boite(b.genre)}" vertex="1" parent="1"><mxGeometry x="{b.x}" y="{b.y + DECALAGE}" width="{b.w}" height="{b.h}" as="geometry" /></mxCell>')
        if b.genre != "zone":
            cells.append(f'<mxCell id="{b.id}-bande" value="" style="rounded=0;html=1;fillColor={ROLES[b.genre][0]};strokeColor=none;" vertex="1" parent="1"><mxGeometry x="{b.x}" y="{b.y + DECALAGE}" width="{BANDE}" height="{b.h}" as="geometry" /></mxCell>')
    for i, f in enumerate(s.fleches):
        couleur, dash = SENS[f.genre]
        style = (f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor={couleur};strokeWidth={TRAIT_FLECHE};endArrow=block;endFill=1;"
                 f"fontColor={couleur};fontStyle=1;fontSize={T_ETIQUETTE};labelBackgroundColor=#FFFFFF;" + ("dashed=1;" if dash else ""))
        cells.append(f'<mxCell id="f{i}" value="{e(f.etiquette)}" style="{style}" edge="1" parent="1" source="{f.de}" target="{f.vers}"><mxGeometry relative="1" as="geometry" /></mxCell>')
    # Légende dessinée : mêmes échantillons que le .svg
    y0 = s.hauteur - 17 + DECALAGE
    nb = len({l for *_, l in _disposer_legende(s)})
    cells.append(f'<mxCell id="leg-r" value="" style="line;strokeWidth=1.5;html=1;strokeColor={RULE};" vertex="1" parent="1"><mxGeometry x="40" y="{s.hauteur - 38 + DECALAGE}" width="{s.largeur - 80}" height="8" as="geometry" /></mxCell>')
    cells.append(f'<mxCell id="leg-t" value="Légende" style="text;html=1;align=left;fontSize={T_LEGENDE + 1};fontStyle=1;fontColor={NAVY};" vertex="1" parent="1"><mxGeometry x="40" y="{y0 - 4}" width="80" height="24" as="geometry" /></mxCell>')
    for genre, cle, libelle, x, ligne in _disposer_legende(s):
        y = y0 + ligne * LIGNE_LEGENDE
        largeur = _largeur_texte(libelle, T_LEGENDE) + 16
        if genre == "boite":
            cells.append(f'<mxCell id="leg-b-{cle}" value="" style="{_style_boite(cle)}" vertex="1" parent="1"><mxGeometry x="{x:.0f}" y="{y}" width="28" height="18" as="geometry" /></mxCell>')
            cells.append(f'<mxCell id="leg-bt-{cle}" value="{e(libelle)}" style="text;html=1;align=left;fontSize={T_LEGENDE};fontColor={INK};" vertex="1" parent="1"><mxGeometry x="{x + 34:.0f}" y="{y - 3}" width="{largeur:.0f}" height="24" as="geometry" /></mxCell>')
        elif genre == "fleche":
            couleur, dash = SENS[cle]
            style = f"endArrow=block;endFill=1;html=1;strokeColor={couleur};strokeWidth={TRAIT_FLECHE};" + ("dashed=1;" if dash else "")
            cells.append(f'<mxCell id="leg-f-{cle}" value="" style="{style}" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{x:.0f}" y="{y + 9}" as="sourcePoint" /><mxPoint x="{x + 40:.0f}" y="{y + 9}" as="targetPoint" /></mxGeometry></mxCell>')
            cells.append(f'<mxCell id="leg-ft-{cle}" value="{e(libelle)}" style="text;html=1;align=left;fontSize={T_LEGENDE};fontColor={INK};" vertex="1" parent="1"><mxGeometry x="{x + 48:.0f}" y="{y - 3}" width="{largeur:.0f}" height="24" as="geometry" /></mxCell>')
    cells.append(f'<mxCell id="leg" value="{e(s.legende)}" style="text;html=1;align=left;fontSize={T_LEGENDE};fontColor={SOFT};" vertex="1" parent="1"><mxGeometry x="40" y="{s.hauteur + 10 + DECALAGE + (nb - 1) * LIGNE_LEGENDE}" width="{s.largeur - 80}" height="24" as="geometry" /></mxCell>')
    return ('<mxfile host="app.diagrams.net" modified="2026-10-04T00:00:00.000Z" agent="RITA" version="24.0.0" type="device">\n'
            f'  <diagram id="{s.nom}" name="{e(s.titre)}">\n'
            f'    <mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{s.largeur}" pageHeight="{s.hauteur_totale}" math="0" shadow="0">\n'
            '      <root>\n        ' + "\n        ".join(cells) + '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')


# =============================================================================
# Schéma 1 : l'architecture autour du modèle (chemin d'une requête, le 03/10/2026)
# =============================================================================
ARCHI = Schema(
    nom="E3-architecture", largeur=1500, hauteur=910,
    titre="RITA : le chemin d'un briefing, et tout ce qui le regarde passer",
    sous_titre="Rapport E3, section 2 · état du code au 4 octobre 2026 · un seul utilisateur, un modèle fourni, aucune action",
    boites=[
        Boite("zc", 40, 90, 274, 310, "CLIENTS (C10)", genre="zone"),
        Boite("web", 56, 118, 242, 82, "Interface web", ["frontend/, HTML, CSS, JS sans build", "3 écrans : portefeuille, indicateurs, briefing", "clé saisie, sessionStorage, 403 affiché"], "normal"),
        Boite("mcp", 56, 210, 242, 82, "Passerelle MCP", ["passerelle_mcp/serveur.py", "3 outils en lecture seule", "appelle l'API par HTTP, avec la clé"], "normal"),
        Boite("curl", 56, 302, 242, 82, "curl, /docs (OpenAPI 3.1.0)", ["POST /briefing?ticker=MC.PA", "le seul chemin vers le modèle", "aucun texte libre : un ticker"], "normal"),

        Boite("api", 340, 118, 358, 120, "api/main.py : l'API (C9)", ["middleware : un request_id par requête (X-Request-ID)", "clé X-API-Key, 16 car. min., temps constant, 403", "aucune clé par défaut (INC-001, OWASP API2)", "14 chemins ; /briefing est le seul qui parle au modèle", "journal : servi, refusé, 502 (request_id, jamais le texte)"], "lavis"),

        Boite("zg", 340, 262, 358, 368, "LangGraph (graph/workflow.py), arêtes fixes", genre="zone"),
        Boite("scout", 356, 292, 326, 66, "scout", ["lit PostgreSQL : 13 indicateurs par valeur", "âge du dernier cours en jours calendaires, cotation périmée"], "normal"),
        Boite("rag", 356, 372, 326, 98, "rag", ["garde-fou d'ENTRÉE : intention AMF, 7 motifs,", "  100 % / 0 % (03/10), avant tout accès à la base", "ChromaDB : filtre ticker puis hybride dense + BM25", "refus OUT_OF_CORPUS si rien ne cite la valeur"], "normal"),
        Boite("red", 356, 484, 326, 66, "redacteur", ["agents/analyst.py : prompt (interdit AMF écrit)", "src/llm.py : la cascade"], "normal"),
        Boite("casc", 356, 564, 326, 52, "Foundry (gpt-5.4) → Anthropic → OpenRouter", ["une génération tracée par essai ; repli ≈ 0,3 s"], "lavis"),

        Boite("sortie", 340, 648, 358, 70, "guardrails/sortie.py : garde-fou de SORTIE (C17)", ["9 motifs, 70 % / 0 % (03/10) ; échec fermé", "texte remplacé par un refus, HTTP 200, conforme_amf=false"], "garde"),
        Boite("rep", 340, 736, 358, 66, "Réponse JSON", ["ticker, prix, variation, briefing, conforme_amf,", "motifs_amf ; en-tête X-Request-ID"], "normal"),

        Boite("pg", 730, 292, 260, 66, "PostgreSQL 18 (E1)", ["10 tables, 1 vue, dix ans de cotations", "écrit par le seul pipeline"], "stock"),
        Boite("chroma", 730, 372, 240, 66, "ChromaDB (index)", ["articles vectorisés, reconstruit chaque nuit", "1 359 documents (27/09)"], "stock"),
        Boite("nuit", 730, 648, 260, 114, "Collecte nocturne, 19 h", ["pipelines/ingest.py, tâche planifiée Windows", "yfinance, RSS, scraping, FRED, BCE", "garde-fou d'INJECTION sur les articles :", "  12 motifs, 70 % / 0 % (03/10)", "40 journaux du 24/08 au 02/10"], "normal"),

        Boite("zo", 1030, 90, 420, 570, "OBSERVABILITÉ (C11, C20)", genre="zone"),
        Boite("lf", 1046, 118, 388, 176, "Langfuse Cloud, région UE (Irlande)", ["une trace par briefing, identifiant = request_id :", "  briefing  (verdict AMF, note conforme_amf)", "  ├─ scout", "  ├─ rag ─ garde-fou-entree", "  ├─ redacteur ─ briefing-llm ─ llm-<fournisseur>", "  └─ garde-fou-sortie", "jetons, erreur du repli, niveau WARNING au refus", "première trace réelle : 02/10 18:39 ; palier gratuit"], "lavis"),
        Boite("fr", 1046, 416, 388, 66, "GET /donnees/fraicheur + bandeau", ["retard en jours ouvrés, 3 états, lisible sans couleur", "la panne la plus fréquente : la collecte d'hier"], "normal"),
        Boite("al", 1046, 318, 388, 82, "Alertes (2, palier gratuit) → GitHub Actions", ["erreurs de fournisseur ; p95 de l'appel au modèle", "alerte-incident.yml ouvre une issue « incident »", "réglées le 04/10, ont sonné : issue #77"], "normal"),
        Boite("tb", 1046, 498, 388, 66, "Tableau de bord « RITA C11 » (03/10, par l'API)", ["tentatives par fournisseur, échecs compris · p95 de briefing-llm", "observations en ERROR ou WARNING"], "lavis"),
        Boite("cout", 1046, 580, 388, 66, "Coût par briefing", ["à zéro pour OpenRouter : nom de modèle absent", "de la grille de prix Langfuse ; à corriger"], "manque"),

        Boite("sand", 1030, 680, 420, 82, "Bac à sable", ["la suite de tests ne trace jamais", "(conftest.py, INC-006) ; doubles de client", "805 tests, 94,70 % (04/10)"], "note"),
        Boite("test", 1030, 776, 420, 82, "Tests en CI à chaque poussée", ["test.yml : données, puis suite + couverture ≥ 90 %,", "puis garde-fous mesurés, portes xfail strict"], "note"),
    ],
    fleches=[
        Fleche("web", "api"), Fleche("mcp", "api"), Fleche("curl", "api"),
        Fleche("api", "scout", sortie="b", entree="h"),
        Fleche("scout", "rag", sortie="b", entree="h"), Fleche("rag", "red", sortie="b", entree="h"), Fleche("red", "casc", sortie="b", entree="h"),
        Fleche("casc", "sortie", sortie="b", entree="h"), Fleche("sortie", "rep", sortie="b", entree="h"),
        Fleche("pg", "scout", sortie="g", entree="d", sens="lecture"), Fleche("chroma", "rag", sortie="g", entree="d", sens="lecture"),
        Fleche("nuit", "pg", "écrit", sortie="h:0.95", entree="b:0.95", sens="ecriture"), Fleche("nuit", "chroma", "indexe", sortie="h:0.45", entree="b:0.5", sens="ecriture"),
        Fleche("api", "lf", "trace (racine et générations)", sortie="d", entree="g"),
        Fleche("lf", "al", "déclenche", sortie="b", entree="h"),
    ],
    legende="État du code au 04/10/2026. Mesures datées dans le rapport E3, section 6.",
    cles_boites={"normal": "composant présent et testé", "lavis": "cœur du traitement", "garde": "garde-fou",
                 "stock": "réserve de données", "manque": "à corriger ou non construit", "note": "tests"},
    cles_fleches={"flux": "appel, passage", "ecriture": "écriture", "lecture": "lecture seule"},
)

# =============================================================================
# Schéma 2 : la chaîne de livraison (C13), ce qui tourne et ce qui manque
# =============================================================================
CHAINE = Schema(
    nom="E3-chaine-livraison", largeur=1400, hauteur=746,
    titre="RITA : la chaîne de livraison continue, du poste au serveur",
    sous_titre="Rapport E3, section 7 · cinq workflows GitHub Actions · état au 4 octobre 2026",
    boites=[
        Boite("zp", 40, 90, 260, 284, "POSTE D'ERA", genre="zone"),
        Boite("dev", 56, 118, 228, 82, "Branche develop", ["un commit = une intention", "tests écrits avant le code (TDD)", "git push origin develop"], "normal"),
        Boite("hook", 56, 214, 228, 66, "Hook pre-push (.githooks/)", ["refuse la poussée directe sur main", "activé une fois par clone"], "lavis"),
        Boite("dod", 56, 294, 228, 66, "scripts/verifier_livrable.py", ["Definition of Done : tests, liens,", "ETAT et CHANGELOG, arbre propre"], "normal"),

        Boite("zgh", 340, 90, 620, 610, "GITHUB (dépôt privé Ganda15/rita-agent)", genre="zone"),
        Boite("test", 356, 118, 280, 112, "test.yml : à chaque poussée et PR", ["job pytest : 1. TEST DES DONNÉES (260 verts, 5 s)", "  2. suite + couverture ≥ 90 % (.coveragerc)", "job evals : garde-fous mesurés,", "  portes non compensables (xfail strict à 85 %)", "778 passed, 29 skipped, 94,70 % (04/10)"], "lavis"),
        Boite("pr", 664, 118, 280, 112, "revue-pr.yml : chaque PR vers main", ["relecture adversariale automatisée", "(action officielle, jeton d'abonnement en secret)", "grille : AGENTS.md et les règles du dépôt", "22 PR fusionnées vers main au 04/10"], "lavis"),
        Boite("main", 356, 250, 280, 66, "Branche main", ["ne bouge que par une PR depuis develop", "un livrable = un tag livrable-E<n>-v<k>"], "normal"),
        Boite("liv", 356, 336, 588, 128, "livraison.yml : poussée, PR, et tag livrable-*", ["1. tests, porte de livraison (rien n'est construit si rouge)", "2. construction de l'image, jamais publiée ici", "3. l'image construite démarre et répond sur /health", "4. l'accès est restreint : 403 sans clé", "5. publication sur ghcr.io/ganda15/rita-api, seulement sur un tag", "   (issue #22 : avant, la publication précédait la vérification)"], "lavis"),
        Boite("gisk", 664, 250, 280, 66, "scan-giskard.yml : manuel", ["scan d'attaques, deux frontières", "plafond de coût saisi ; run 9 le 20/09"], "normal"),
        Boite("alerte", 664, 586, 280, 98, "alerte-incident.yml", ["reçu de Langfuse (repository_dispatch)", "ou bouton manuel ; ouvre ou commente", "une issue « incident » ; label créé", "a sonné pour de vrai le 04/10 (#77)"], "normal"),
        Boite("ghcr", 356, 484, 588, 82, "Image sur GHCR", ["python:3.13-slim, deux étapes, non-root (UID 10001)", "ghcr.io/ganda15/rita-api:livrable-E<n>-v<k>", "jamais publiée pour de vrai au 03/10"], "stock"),

        Boite("zs", 1000, 90, 360, 290, "SERVEUR HETZNER (CX23, 4 Go, HTTPS Caddy)", genre="zone"),
        Boite("srv", 1016, 118, 328, 86, "docker compose (manuel, par SSH)", ["pull de l'image taguée, up -d --force-recreate api", "conteneur en lecture seule, no-new-privileges", "variables Langfuse transmises depuis le 02/10"], "normal"),
        Boite("gel", 1016, 218, 328, 66, "Copie figée depuis le 19/08/2026", ["première livraison de cette chaîne à faire", "les variables Langfuse ne sont pas encore posées"], "manque"),
        Boite("lfs", 1016, 298, 328, 66, "Langfuse Cloud UE", ["traces du poste depuis le 02/10 ;", "du serveur dès que les variables y sont"], "note"),

        Boite("zm", 1000, 400, 360, 216, "CONÇU, NON CONSTRUIT (brief Mardik ③)", genre="zone"),
        Boite("rb", 1016, 428, 328, 50, "rollback.yml : retour arrière", ["tag précédent redéployé, jamais reconstruit"], "manque"),
        Boite("man", 1016, 490, 328, 50, "Manifeste de version, GET /version", ["modèle daté, prompt_version, config, index"], "manque"),
        Boite("filtre", 1016, 552, 328, 50, "Filtre de chemin + gate sur le vrai modèle", ["porte payante seulement si prompt ou jeu changent"], "manque"),

        Boite("note", 40, 400, 260, 100, "Ce que la chaîne coche pour C13", ["test → construction → démarrage vérifié →", "accès vérifié → publication sur tag,", "exécuté par la plateforme à chaque poussée.", "Un Dockerfile seul ne coche aucun critère."], "note"),
        Boite("rouge", 40, 516, 260, 98, "La CI a refusé, et c'était juste", ["28/09 : pandas reconstruit (#23, non épinglé)", "03/10 : dix exécutions rouges, tests liés au", "poste (INC-007), corrigé le jour même", "aucune alerte sur une exécution rouge"], "note"),
    ],
    fleches=[
        Fleche("dev", "test", "push", sortie="d", entree="g"),
        Fleche("test", "pr", "PR", sortie="d", entree="g"),
        Fleche("pr", "main", "fusion relue", sortie="b", entree="h"),
        Fleche("main", "liv", "tag livrable-*", sortie="b", entree="h"),
        Fleche("liv", "ghcr", "étape 5", sortie="b", entree="h"),
        Fleche("ghcr", "srv", "pull", sortie="d:0.3", entree="g:0.5", pointille=True),
        Fleche("hook", "main", "refus", sortie="d", entree="g", sens="erreur"),
        Fleche("lfs", "alerte", sortie="g", entree="d"),
    ],
    legende="Dates mesurées au 04/10/2026. Détail : rapport E3, section 7.",
    cles_boites={"normal": "étape ou poste", "lavis": "workflow qui tourne", "stock": "artefact publié",
                 "manque": "conçu, non construit", "note": "à retenir"},
    cles_fleches={"flux": "enchaînement automatique", "manuel": "manuel ou pas encore exécuté", "erreur": "refus"},
)


# =============================================================================
# Schéma 3 : C10, une demande de briefing depuis l'écran, et ses refus
# =============================================================================
INTEGRATION = Schema(
    nom="E3-integration-briefing", largeur=1400, hauteur=680,
    titre="RITA : une demande de briefing, de l'écran au modèle et retour",
    sous_titre="Rapport E3, section 4 · écran 3 (frontend/briefing.html, briefing.js) · état au 4 octobre 2026",
    boites=[
        # Le parcours normal, de gauche à droite.
        Boite("u", 40, 104, 236, 128, "1. L'utilisateur", ["saisit la clé (champ masqué)", "choisit un code dans la liste,", "remplie par GET /donnees/valeurs", "envoie : bouton ou touche Entrée"], "normal"),
        Boite("e", 302, 104, 256, 128, "2. L'écran envoie", ["POST /briefing?ticker=MC.PA", "en-tête X-API-Key", "annonce l'attente : 5 à 15 s", "  (zone de statut, aria-live)"], "lavis"),
        Boite("a", 584, 104, 262, 128, "3. L'API vérifie", ["clé : 16 car. min., temps constant", "identifiant X-Request-ID", "puis le graphe :", "  scout, rag, redacteur"], "lavis"),
        Boite("m", 872, 104, 262, 128, "4. Le modèle écrit", ["cascade de fournisseurs :", "  Foundry → Anthropic → OpenRouter", "puis garde-fou de SORTIE", "  (texte retenu si recommandation)"], "lavis"),
        Boite("ok", 1160, 104, 200, 128, "5. L'écran affiche", ["le verdict EN MOTS", "le texte (textContent)", "la référence de requête", "focus sur le résultat"], "normal"),

        # Les réponses qui ne sont pas un briefing, dans l'ordre où elles peuvent arriver.
        Boite("z", 40, 262, 1320, 266, "LES RÉPONSES QUI NE SONT PAS UN BRIEFING, ET CE QUE L'ÉCRAN EN FAIT", genre="zone"),
        Boite("enet", 56, 340, 307, 88, "Pas de réponse du serveur", ["exception attrapée (try/catch) :", "« Le serveur ne répond pas.", "  Vérifiez que l'API est démarrée. »"], "normal"),
        Boite("e403", 383, 340, 307, 88, "403 : clé refusée", ["la clé est oubliée (sessionStorage)", "retour à la saisie,", "message en clair"], "normal"),
        Boite("e502", 710, 340, 307, 88, "502 : valeur absente de la base", ["« Valeur introuvable : … n'est pas", "  dans l'univers suivi. »"], "normal"),
        Boite("e500", 1037, 340, 307, 88, "500 : aucun fournisseur ne répond", ["mesuré le 03/10 : « Erreur 500 »", "générique, sans fuite ;", "message dédié prévu (#75)"], "manque"),
        Boite("ecle", 56, 444, 634, 68, "Défaut connu : la clé est mémorisée avant d'avoir servi (#73)", ["les écrans 1 et 2 attendent un appel réussi ; l'écran 3 non.", "Correction après le gel du 15/10, test d'abord."], "manque"),
        Boite("emcp", 710, 444, 634, 68, "Le deuxième client : la passerelle MCP", ["mêmes routes, même clé ; trois outils en lecture seule ;", "aucun outil ne donne accès à /briefing"], "note"),

        Boite("t", 40, 548, 1320, 60, "Preuves", ["tests/test_frontend.py (72, statiques) · tests/test_smoke_ui.py (7, vrai navigateur, /briefing intercepté) · tests/test_health.py, test_api_donnees.py (l'API) · evidence/C10/"], "note"),
    ],
    fleches=[
        Fleche("u", "e"), Fleche("e", "a"), Fleche("a", "m"), Fleche("m", "ok"),
        Fleche("e", "enet", "réseau coupé", sortie="b:0.3", entree="h:0.62", sens="erreur", pos=0.72),
        Fleche("a", "e403", "clé absente ou fausse", sortie="b:0.2", entree="h:0.75", sens="erreur", pos=0.72),
        Fleche("a", "e502", "valeur inconnue", sortie="b:0.8", entree="h:0.35", sens="erreur", pos=0.72),
        Fleche("m", "e500", "aucun fournisseur", sortie="b:0.6", entree="h:0.4", sens="erreur", pos=0.72),
    ],
    legende="Comportement présent et testé au 04/10/2026, relu contre frontend/briefing.js et api/main.py. Preuves : evidence/C10/.",
    cles_boites={"normal": "côté écran ou réponse gérée", "lavis": "côté serveur", "manque": "écart connu, corrigé après le gel",
                 "note": "preuve ou contexte"},
    cles_fleches={"flux": "parcours normal", "erreur": "réponse d'erreur"},
)

# =============================================================================
# Schéma 4 : C11, la chaîne de monitorage du modèle
# =============================================================================
MONITORAGE = Schema(
    nom="E3-monitorage", largeur=1400, hauteur=560,
    titre="RITA : surveiller le modèle, collecte, alerte et restitution",
    sous_titre="Rapport E3, section 5 · src/traces.py, Langfuse Cloud (région UE), GitHub Actions · état au 4 octobre 2026",
    boites=[
        Boite("zc", 40, 90, 420, 330, "COLLECTE", genre="zone"),
        Boite("br", 56, 118, 388, 120, "Chaque briefing (POST /briefing)", ["une trace racine « briefing », identifiant = X-Request-ID", "une étape par nœud : scout, rag, redacteur", "une génération par tentative de fournisseur :", "  durée, jetons, modèle réel, erreur du repli", "un score conforme_amf (verdict du garde-fou)"], "lavis"),
        Boite("jr", 56, 252, 388, 70, "Journal de l'API", ["une ligne par briefing servi ou refusé, avec", "l'identifiant de requête ; jamais le texte"], "normal"),
        Boite("fr", 56, 336, 388, 70, "Fraîcheur des données", ["GET /donnees/fraicheur : retard en jours ouvrés", "la panne la plus fréquente : la collecte d'hier"], "normal"),

        Boite("lf", 500, 118, 300, 120, "Langfuse Cloud, région UE", ["reçoit les traces (palier gratuit)", "calcule latence, volumes, erreurs", "accès : compte du propriétaire", "reçoit des chiffres de marché, jamais une position"], "stock"),

        Boite("zr", 840, 90, 520, 170, "RESTITUTION", genre="zone"),
        Boite("tb", 856, 118, 488, 64, "Tableau de bord « RITA C11 » (créé par l'API, 03/10)", ["tentatives par fournisseur, échecs compris (le repli se voit) ·", "latence p95 de l'appel au modèle · observations en ERROR ou WARNING"], "lavis"),
        Boite("bd", 856, 190, 488, 56, "Bandeau de fraîcheur, écran 1 · export CSV des tuiles", ["lisible sans la couleur ; CSV pour un lecteur d'écran ou un tableur"], "normal"),

        Boite("za", 840, 280, 520, 140, "ALERTE", genre="zone"),
        Boite("al", 856, 308, 230, 98, "2 règles Langfuse (04/10)", ["ERROR > 0 sur 1 jour", "p95 de briefing-llm", "  > 15 000 ms sur 1 jour", "toutes deux ont sonné"], "normal"),
        Boite("gh", 1110, 308, 234, 98, "alerte-incident.yml", ["repository_dispatch", "ouvre ou commente une", "issue « incident » par alerte", "à la main : #71 ; réel : #77"], "normal"),

        Boite("sb", 40, 440, 660, 70, "Bac à sable : la suite de tests ne trace jamais", ["tests/conftest.py coupe le traçage (INC-006) ; le banc C7 aussi (LANGFUSE_TRACING_ENABLED=false) ;", "doubles de client dans tests/test_traces*.py, test_trace_chemin.py (l'ordre exact des étapes)"], "note"),
        Boite("lim", 720, 440, 640, 70, "Ce qui manque", ["serveur de production pas encore tracé (code du 19/08) · coût OpenRouter à zéro ·", "pas d'alerte de silence (deux alertes au palier gratuit) · seuils à revoir après une semaine"], "manque"),
    ],
    fleches=[
        Fleche("br", "lf"),
        Fleche("lf", "tb", "", sortie="d:0.3", entree="g"),
        Fleche("lf", "al", "", sortie="d:0.8", entree="g:0.3"),
        Fleche("al", "gh"),
        Fleche("fr", "bd", "", sortie="d:0.5", entree="g:0.8"),
    ],
    legende="Preuves : evidence/C11/ (alertes : preuve-alertes-2026-10-04.md).",
    cles_boites={"lavis": "collecte et restitution principales", "normal": "présent et prouvé",
                 "stock": "service externe", "manque": "à faire", "note": "bac à sable"},
    cles_fleches={"flux": "envoi des mesures ou de l'alerte"},
)

# =============================================================================
# Schéma 5 : C12, la stratégie de test
# =============================================================================
TESTS = Schema(
    nom="E3-strategie-tests", largeur=1400, hauteur=580,
    titre="RITA : ce qui est testé, par quoi, et où",
    sous_titre="Rapport E3, section 6 · 805 tests collectés par pytest le 4 octobre 2026, regroupés par ce qu'ils protègent",
    boites=[
        Boite("d", 40, 100, 300, 104, "Données : 283", ["collecte (ingest, sources), nettoyage,", "import, schéma, vue de valorisation,", "RGPD (purge, registre), fraîcheur", "→ étape CI « Tester les données »"], "lavis"),
        Boite("m", 360, 100, 300, 104, "Modèle, prompt et graphe : 90", ["prompt du rédacteur (13 indicateurs),", "cascade de fournisseurs, graphe,", "indicateurs calculés en SQL et en Python", "aucun entraînement : rien à valider"], "lavis"),
        Boite("g", 680, 100, 320, 104, "Garde-fous et évaluations : 95", ["entrée, injection, sortie : taux mesurés", "portes : faux positifs ≤ 15 %, latence < 250 ms,", "blocage ≥ 85 % déclaré non atteint (xfail strict)", "scan Giskard, banc C7"], "lavis"),
        Boite("r", 1020, 100, 340, 104, "Recherche documentaire : 68", ["index, filtre par valeur, hybride", "dense + BM25, refus hors corpus", "mesure par ablation (evals/mesurer_rag)"], "lavis"),
        Boite("a", 40, 222, 300, 90, "API : 128", ["toutes les routes, 403 sans clé,", "identifiant de requête (500 compris),", "journal des appels MCP, rôle lecture"], "normal"),
        Boite("o", 360, 222, 300, 90, "Monitorage : 36", ["une trace par briefing, l'ordre exact", "des étapes, verdict AMF, panne du", "traçage sans effet sur le briefing"], "normal"),
        Boite("i", 680, 222, 320, 90, "Interface : 79", ["72 statiques (aucune clé, textContent,", "accessibilité) · 7 dans un vrai", "navigateur (Playwright)"], "normal"),
        Boite("l", 1020, 222, 340, 90, "Livraison et outillage : 26", ["ordre de livraison.yml, Compose,", "Definition of Done, hooks de l'assistant"], "normal"),

        Boite("zw", 40, 334, 1320, 134, "OÙ ILS TOURNENT", genre="zone"),
        Boite("p", 56, 368, 300, 84, "Poste", ["C:\\Python314\\python.exe -m pytest --cov", "805 : 803 verts, 2 xfail (base réelle", "en transactions annulées)"], "normal"),
        Boite("c1", 376, 368, 300, 84, "CI, job pytest", ["1. test des données : 260 verts, 3 sautés", "2. suite : 778 verts, 29 sautés (sans base),", "2 xfail ; couverture 94,70 % (seuil 90)"], "lavis"),
        Boite("c2", 696, 368, 320, 84, "CI, job evals", ["mesure des garde-fous à chaque poussée", "portes non compensables : bloque", "la fusion si elle régresse"], "lavis"),
        Boite("mg", 1036, 368, 308, 84, "Manuel, payant", ["scan Giskard (200 scénarios, 20/09)", "banc C7 (60 appels réels, 03/10)", "plafond de coût saisi"], "note"),

        Boite("lim", 40, 484, 1320, 50, "Limites", ["aucun schéma sur le texte produit ni sur les flux RSS · pas de jeu de référence de briefings · 29 tests ne tournent qu'avec une base (poste) · garde-fous à 70 % sur deux positions"], "manque"),
    ],
    fleches=[],
    legende="Chiffres : pytest --collect-only (805), CI run 37190015570 (04/10).",
    cles_boites={"lavis": "protège le comportement du modèle", "normal": "protège l'application autour",
                 "note": "manuel, payant", "manque": "limites"},
)


def ecrire(s: Schema) -> None:
    (ICI / f"{s.nom}.svg").write_text(svg(s), encoding="utf-8", newline="\n")
    (ICI / f"{s.nom}.drawio").write_text(drawio(s), encoding="utf-8", newline="\n")
    print("écrit", s.nom, ".svg et .drawio")


if __name__ == "__main__":
    for schema in (ARCHI, CHAINE, INTEGRATION, MONITORAGE, TESTS):
        ecrire(schema)
