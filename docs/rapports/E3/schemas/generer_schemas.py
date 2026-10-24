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

Remis à l'état du 24/10/2026 pour E3 v1.5 : les cinq schémas disaient encore l'état du 4 octobre (cinq workflows,
serveur non tracé, 502 pour une valeur inconnue). Le texte des boîtes passait à 4 points une fois imprimé : tailles
relevées (lignes de 11,5 à 15,5 px), textes raccourcis, et un contrôle (`debordements`) refuse d'écrire un schéma
dont une ligne ne tient plus dans sa boîte.

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
T_TITRE, T_SOUS_TITRE, T_ZONE, T_BOITE, T_LIGNE, T_ETIQUETTE, T_LEGENDE = 32, 17, 16, 17.5, 15.5, 15, 15
INTERLIGNE, Y_TITRE_BOITE, Y_PREMIERE_LIGNE = 20, 24, 46
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
    "neuf":   ("#15803D", "#E8F5E9", "#14532D"),   # codé au sprint 4 (schéma de la composante, 21/10/2026)
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
LIGNE_LEGENDE = 30 # une ligne de légende de plus quand elle ne tient pas en largeur
DATE_DRAWIO = "2026-10-24T00:00:00.000Z"   # date inscrite dans chaque .drawio


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
    return (f'<mxfile host="app.diagrams.net" modified="{DATE_DRAWIO}" agent="RITA" version="24.0.0" type="device">\n'
            f'  <diagram id="{s.nom}" name="{e(s.titre)}">\n'
            f'    <mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{s.largeur}" pageHeight="{s.hauteur_totale}" math="0" shadow="0">\n'
            '      <root>\n        ' + "\n        ".join(cells) + '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')


# Contrôle de place (24/10/2026) : une ligne trop longue déborde de sa boîte sans que rien ne le dise. Coefficients
# prudents pour Segoe UI dans Chrome (largeur moyenne d'un caractère, en fraction de la taille) ; même méthode que le
# générateur des schémas d'E1.
CAR_NORMAL, CAR_GRAS = 0.48, 0.55
MARGE_TEXTE = BANDE + 10 + 16


def debordements(s: Schema) -> list[str]:
    """Chaque titre ou ligne de boîte qui ne tient pas dans sa largeur, et chaque boîte trop basse pour ses lignes."""
    trop = []
    for b in s.boites:
        if b.genre == "zone":
            if len(b.titre) * T_ZONE * CAR_GRAS > b.w - 28:
                trop.append(f"{s.nom}/{b.id} : titre de zone trop long")
            continue
        utile = b.w - MARGE_TEXTE
        if len(b.titre) * T_BOITE * CAR_GRAS > utile:
            trop.append(f"{s.nom}/{b.id} : titre trop long ({len(b.titre)} car.)")
        for ligne in b.lignes:
            if len(ligne) * T_LIGNE * CAR_NORMAL > utile:
                trop.append(f"{s.nom}/{b.id} : ligne trop longue ({len(ligne)} car.) « {ligne} »")
        if b.lignes and Y_PREMIERE_LIGNE + (len(b.lignes) - 1) * INTERLIGNE + 10 > b.h:
            trop.append(f"{s.nom}/{b.id} : boîte trop basse pour {len(b.lignes)} lignes")
    return trop


ETAT = "état au 24 octobre 2026 (develop, 9683f04)"

# =============================================================================
# Schéma 1 : l'architecture autour du modèle (C9 à C11)
# =============================================================================
ARCHI = Schema(
    nom="E3-architecture", largeur=1400, hauteur=860,
    titre="RITA : deux chemins vers le modèle, et ce qui les surveille",
    sous_titre=f"Rapport E3, section 2 · {ETAT} · un utilisateur, un modèle fourni, aucune action",
    boites=[
        Boite("zc", 40, 100, 270, 330, "CLIENTS (C10)", genre="zone"),
        Boite("web", 56, 132, 238, 80, "Interface web", ["5 écrans, HTML et JS", "clé saisie à l'écran"], "normal"),
        Boite("mcp", 56, 226, 238, 80, "Passerelle MCP", ["3 outils en lecture seule,", "par l'API, avec la clé"], "normal"),
        Boite("curl", 56, 320, 238, 80, "curl, /docs", ["contrat OpenAPI 3.1.0,", "19 chemins"], "normal"),

        Boite("api", 340, 132, 380, 120, "api/main.py : l'API (C9)", ["X-Request-ID sur toute réponse", "X-API-Key exigée : 403 sinon", "valeur inconnue : 422, sans modèle", "quota partagé : 429 au-delà"], "lavis"),
        Boite("par", 340, 282, 380, 80, "Deux parcours, arêtes fixes", ["/briefing : scout, rag, redacteur", "/question : recherche, puis JSON strict"], "lavis"),
        Boite("gav", 340, 392, 380, 80, "Garde-fous avant le modèle", ["question : intention AMF, détournement", "articles : injection, revérifiée ici"], "garde"),
        Boite("llm", 340, 502, 380, 80, "src/llm.py : le modèle fourni", ["briefing : cascade, Azure d'abord", "question : Azure seul (gpt-5.4)"], "lavis"),
        Boite("gap", 340, 612, 380, 80, "Garde-fous après le modèle", ["sortie : recommandation, fuite", "question : citations et nombres"], "garde"),
        Boite("rep", 340, 722, 380, 80, "Réponse JSON", ["texte ou refus, verdict AMF, sources", "en-tête X-Request-ID"], "normal"),

        Boite("pg", 750, 282, 270, 80, "PostgreSQL 18 (E1)", ["10 tables, 1 vue", "lue par le scout et l'API"], "stock"),
        Boite("chroma", 750, 392, 270, 80, "ChromaDB, l'index", ["les articles, vectorisés", "identité annoncée par /health"], "stock"),
        Boite("coll", 750, 522, 270, 120, "Collecte des articles", ["poste : chaque soir à 19 h", "prod. : ingestion au bouton", "écrit la base, puis l'index", "injection filtrée à l'entrée"], "normal"),

        Boite("zo", 1050, 100, 310, 540, "SURVEILLANCE (C11)", genre="zone"),
        Boite("lf", 1066, 132, 278, 120, "Langfuse Cloud (UE)", ["une trace par requête,", "sans prompt ni réponse,", "jetons, durée, verdict AMF", "production tracée dès le 21/10"], "lavis"),
        Boite("al", 1066, 282, 278, 100, "Alertes Langfuse (2)", ["erreur fournisseur ; p95 lent", "issue « incident » GitHub", "#77 réelle ; #130 fausse"], "normal"),
        Boite("sante", 1066, 412, 278, 100, "/sante, tableau de bord", ["compteurs tenus par l'API,", "verdicts contre seuils écrits,", "remis à zéro au redémarrage"], "normal"),
        Boite("fr", 1066, 542, 278, 80, "GET /donnees/fraicheur", ["retard en jours ouvrés,", "bandeau de l'écran 1"], "normal"),
        Boite("sb", 1050, 660, 310, 80, "Bac à sable", ["les tests ne tracent jamais ;", "la copie : son propre projet"], "note"),
    ],
    fleches=[
        Fleche("web", "api", sortie="d", entree="g:0.25"), Fleche("mcp", "api", sortie="d", entree="g:0.55"),
        Fleche("curl", "api", sortie="d", entree="g:0.85"),
        Fleche("api", "par", sortie="b", entree="h"), Fleche("par", "gav", sortie="b", entree="h"),
        Fleche("gav", "llm", sortie="b", entree="h"), Fleche("llm", "gap", sortie="b", entree="h"),
        Fleche("gap", "rep", sortie="b", entree="h"),
        Fleche("pg", "par", sortie="g", entree="d", sens="lecture"),
        Fleche("chroma", "par", "cherche", sortie="g:0.3", entree="d:0.8", sens="lecture"),
        Fleche("coll", "chroma", "indexe", sortie="h", entree="b", sens="ecriture"),
        Fleche("api", "lf", "trace", sortie="d:0.5", entree="g:0.5"),
        Fleche("lf", "al", "déclenche", sortie="b", entree="h"),
    ],
    legende="État du code au 24/10/2026, develop 9683f04 ; la production sert b547cbf. Mesures : rapport E3, sections 3 à 7.",
    cles_boites={"normal": "présent et testé", "lavis": "cœur du traitement", "garde": "garde-fou",
                 "stock": "réserve de données", "note": "bac à sable"},
    cles_fleches={"flux": "appel, passage", "ecriture": "écriture", "lecture": "lecture seule"},
)

# =============================================================================
# Schéma 2 : la chaîne de livraison (C13)
# =============================================================================
CHAINE = Schema(
    nom="E3-chaine-livraison", largeur=1400, hauteur=800,
    titre="RITA : la chaîne de livraison continue, du poste à la production",
    sous_titre=f"Rapport E3, section 7 · sept workflows GitHub Actions · {ETAT}",
    boites=[
        Boite("zp", 40, 100, 260, 332, "POSTE D'ERA", genre="zone"),
        Boite("dev", 56, 132, 228, 80, "Branche develop", ["tests écrits avant le code", "un commit, une intention"], "normal"),
        Boite("hook", 56, 232, 228, 80, "Hook pre-push", ["refuse la poussée", "directe sur main"], "lavis"),
        Boite("dod", 56, 332, 228, 80, "verifier_livrable.py", ["tests, portes, liens,", "tag cité : la DoD"], "normal"),

        Boite("zgh", 330, 100, 670, 648, "GITHUB (dépôt privé Ganda15/rita-agent)", genre="zone"),
        Boite("test", 346, 132, 310, 120, "test.yml : poussée et PR", ["1. test des données : 296 verts", "2. suite et couverture ≥ 90 %", "job evals : portes non", "compensables (xfail à 85 %)"], "lavis"),
        Boite("pr", 674, 132, 310, 120, "revue-pr.yml : PR vers main", ["relecture automatisée de la PR", "grille : AGENTS.md, CLAUDE.md", "remarque traitée par un commit", "check requis pour fusionner"], "lavis"),
        Boite("regle", 346, 272, 638, 80, "main : le ruleset « main protegee »", ["PR obligatoire et 6 checks verts : lint, secrets, pytest, evals,", "construire-et-publier, revue ; ni suppression, ni force-push"], "normal"),
        Boite("liv", 346, 372, 638, 140, "livraison.yml : poussée, PR, tag livrable-*", ["lint (ruff), puis secrets (gitleaks, tout l'historique) ;", "tests, porte de livraison ; image construite, jamais publiée ici ;", "l'image démarre, annonce son commit, refuse sans clé (403) ;", "publiée après une fusion dans main, ou sur un tag ;", "après une fusion seulement : livrée au serveur"], "lavis"),
        Boite("ghcr", 346, 532, 310, 100, "Image sur GHCR", ["mirror.gcr.io, python:3.13-slim", "non-root (UID 10001)", "étiquettes :sha-…, :<tag>"], "stock"),
        Boite("main", 674, 532, 310, 100, "Lancés à la main", ["retour-arriere.yml : 14 et 15/10", "ingestion.yml : articles, index", "scan-giskard.yml : attaques"], "normal"),
        Boite("alerte", 346, 652, 310, 80, "alerte-incident.yml", ["envoi de Langfuse : une issue", "« incident » (#77, #130)"], "normal"),
        Boite("rien", 674, 652, 310, 80, "Pas construit", ["filtre de chemin, version de", "prompt, approbation avant prod."], "manque"),

        Boite("zs", 1030, 100, 330, 532, "SERVEUR HETZNER", genre="zone"),
        Boite("srv", 1046, 132, 298, 140, "deploy/deployer.py (root)", ["clé SSH à commande forcée ;", "essaie l'image à part (pré-test),", "rejoue les questions de démo,", "bascule, contrôle, et remet", "l'ancienne si un contrôle échoue"], "lavis"),
        Boite("cren", 1046, 292, 298, 80, "Créneau du matin", ["8 h à 9 h : rien ne bascule ;", "livraison reprise après 9 h"], "normal"),
        Boite("prod", 1046, 392, 298, 100, "Production, HTTPS (Caddy)", ["/health : commit et index", "N18 (b547cbf), le 24/10 :", "de la fusion au service, 9 min"], "normal"),
        Boite("rb", 1046, 512, 298, 100, "Retour arrière, un ordre", ["version précédente remise :", "28 s (14/10), 35 s (15/10) ;", "un pas, base non restaurée"], "normal"),

        Boite("refus", 40, 452, 260, 120, "Refus justes", ["PR #93, cassée exprès :", "fusion bloquée (15/10) ;", "tag sprint-4-v1 refusé :", "absent du CHANGELOG"], "note"),
    ],
    fleches=[
        Fleche("dev", "test", "push", sortie="d", entree="g:0.4"),
        Fleche("test", "pr", sortie="d", entree="g"),
        Fleche("pr", "regle", sortie="b", entree="h:0.8"),
        Fleche("regle", "liv", "", sortie="b", entree="h"),
        Fleche("liv", "ghcr", sortie="b:0.25", entree="h"),
        Fleche("liv", "srv", sortie="d:0.3", entree="g:0.6"),
        Fleche("hook", "regle", "refus", sortie="d", entree="g", sens="erreur"),
        Fleche("main", "rb", "revenir", sortie="d", entree="g:0.7", sens="manuel"),
    ],
    legende="Mesures du 14 au 24/10/2026. Détail : rapport E3, section 7, et docs/CI-CD.md.",
    cles_boites={"normal": "étape, poste ou état", "lavis": "tourne tout seul", "stock": "artefact publié",
                 "manque": "pas construit", "note": "à retenir"},
    cles_fleches={"flux": "enchaînement automatique", "manuel": "lancé à la main", "erreur": "refus"},
)

# =============================================================================
# Schéma 3 : C10, une demande de briefing depuis l'écran, et ses refus
# =============================================================================
INTEGRATION = Schema(
    nom="E3-integration-briefing", largeur=1400, hauteur=660,
    titre="RITA : une demande de briefing, de l'écran au modèle et retour",
    sous_titre=f"Rapport E3, section 4 · écran du briefing (frontend/briefing.js) · {ETAT}",
    boites=[
        Boite("u", 40, 120, 244, 100, "1. L'utilisateur", ["saisit la clé (masquée),", "choisit une valeur dans", "la liste de l'univers suivi"], "normal"),
        Boite("e", 309, 120, 244, 100, "2. L'écran envoie", ["POST /briefing?ticker=…", "en-tête X-API-Key", "attente annoncée (aria-live)"], "lavis"),
        Boite("a", 578, 120, 244, 100, "3. L'API vérifie", ["clé, valeur connue (422),", "quota partagé (429),", "puis scout, rag, redacteur"], "lavis"),
        Boite("m", 847, 120, 244, 100, "4. Le modèle écrit", ["cascade, Azure d'abord ;", "garde-fous de sortie :", "recommandation, fuite"], "lavis"),
        Boite("ok", 1116, 120, 244, 100, "5. L'écran affiche", ["le verdict EN MOTS,", "le texte (textContent),", "la référence de requête"], "normal"),

        Boite("z", 40, 250, 1320, 256, "LES RÉPONSES QUI NE SONT PAS UN BRIEFING, ET CE QUE L'ÉCRAN EN FAIT", genre="zone"),
        Boite("enet", 56, 290, 236, 100, "Aucune réponse", ["message à l'écran :", "« Le serveur ne", "répond pas. »"], "normal"),
        Boite("e403", 320, 290, 236, 100, "403 : clé refusée", ["clé oubliée, retour", "à la saisie, message", "en clair"], "normal"),
        Boite("e422", 584, 290, 236, 100, "422 : valeur inconnue", ["« Valeur introuvable »,", "avant le graphe, sans", "appel au modèle"], "normal"),
        Boite("e429", 848, 290, 236, 100, "429 : quota atteint", ["10 appels par minute,", "partagés avec /question ;", "refus poli à l'écran"], "normal"),
        Boite("e5xx", 1112, 290, 236, 100, "502, 500 : pannes", ["502 : le graphe échoue ;", "500 : aucun fournisseur,", "message générique (#75)"], "manque"),
        Boite("ecle", 56, 410, 500, 80, "La clé gardée trop tôt (#73), non corrigé", ["briefing et question : dès l'envoi ; tableau de bord :", "après une panne réseau ou une erreur 500"], "manque"),
        Boite("autres", 584, 410, 764, 80, "Les autres clients de l'API", ["écran des questions : même clé, mêmes refus, POST /question", "passerelle MCP : 3 outils en lecture seule, aucun accès au modèle"], "note"),

        Boite("t", 40, 526, 1320, 80, "Preuves", ["tests/test_frontend.py (92) · tests/test_smoke_ui.py (13, vrai navigateur, appels interceptés)", "tests/test_health.py (12) · tests/test_briefing_422.py (5) · tests/test_limiteur.py (7) · evidence/C10/"], "note"),
    ],
    fleches=[
        Fleche("u", "e"), Fleche("e", "a"), Fleche("a", "m"), Fleche("m", "ok"),
        Fleche("e", "enet", "réseau coupé", sortie="b:0.2", entree="h:0.7", sens="erreur", pos=0.3),
        Fleche("a", "e403", "clé fausse", sortie="b:0.1", entree="h:0.8", sens="erreur", pos=0.3),
        Fleche("a", "e422", "valeur inconnue", sortie="b:0.5", entree="h:0.5", sens="erreur", pos=0.3),
        Fleche("a", "e429", "quota", sortie="b:0.9", entree="h:0.2", sens="erreur", pos=0.3),
        Fleche("m", "e5xx", "panne", sortie="b:0.9", entree="h:0.3", sens="erreur", pos=0.3),
    ],
    legende="Comportement relu le 24/10/2026 contre frontend/briefing.js, frontend/question.js, frontend/tableau-de-bord.js et api/main.py.",
    cles_boites={"normal": "côté écran ou réponse gérée", "lavis": "côté serveur", "manque": "écart connu",
                 "note": "preuve ou contexte"},
    cles_fleches={"flux": "parcours normal", "erreur": "réponse d'erreur"},
)

# =============================================================================
# Schéma 4 : C11, la chaîne de monitorage du modèle
# =============================================================================
MONITORAGE = Schema(
    nom="E3-monitorage", largeur=1400, hauteur=740,
    titre="RITA : surveiller le modèle, collecte, alerte et restitution",
    sous_titre=f"Rapport E3, section 5 · src/traces.py, Langfuse Cloud (région UE), /sante · {ETAT}",
    boites=[
        Boite("zc", 40, 100, 430, 388, "COLLECTE", genre="zone"),
        Boite("br", 56, 132, 398, 140, "Chaque briefing, chaque question", ["une trace, identifiant = X-Request-ID ;", "une étape par nœud et par garde-fou ;", "une génération par fournisseur essayé :", "durée, jetons, modèle ; aucun texte"], "lavis"),
        Boite("jr", 56, 292, 398, 80, "Journal de l'API", ["une ligne par briefing ou question,", "avec l'identifiant ; jamais le texte"], "normal"),
        Boite("cpt", 56, 392, 398, 80, "Compteurs de l'API", ["erreurs, refus, latence, coût estimé ;", "remis à zéro au redémarrage"], "normal"),

        Boite("lf", 500, 132, 300, 120, "Langfuse Cloud (UE)", ["reçoit les traces (palier gratuit),", "calcule latence, jetons, erreurs ;", "production tracée dès le 21/10"], "stock"),

        Boite("zr", 840, 100, 520, 288, "RESTITUTION", genre="zone"),
        Boite("tb", 856, 132, 488, 80, "Tableau de bord Langfuse « RITA C11 »", ["essais par fournisseur, échecs compris ; p95 du modèle ;", "observations en ERROR ou WARNING"], "lavis"),
        Boite("tbm", 856, 222, 488, 80, "Tableau de bord de RITA (/sante)", ["le verdict de chaque signal contre un seuil écrit,", "en mots, pas seulement en couleur"], "lavis"),
        Boite("bd", 856, 312, 488, 60, "Bandeau de fraîcheur, écran 1", ["retard des cours en jours ouvrés"], "normal"),

        Boite("za", 840, 408, 520, 168, "ALERTE", genre="zone"),
        Boite("al", 856, 440, 230, 120, "2 règles Langfuse", ["erreur sur 1 jour ;", "p95 au-dessus de", "15 000 ms sur 1 jour"], "normal"),
        Boite("gh", 1110, 440, 234, 120, "alerte-incident.yml", ["ouvre une issue", "« incident » : #77", "réelle, #130 fausse"], "normal"),

        Boite("sb", 40, 508, 760, 80, "Bac à sable : rien de factice en production", ["la suite de tests ne trace jamais (conftest.py, INC-006) ; la copie du", "poste a son propre projet Langfuse depuis le 23/10, après la fausse alerte #130"], "note"),
        Boite("lim", 40, 608, 1320, 80, "Ce qui manque", ["coût de /question non calculé par Langfuse (jetons en métadonnées) · une seule trace de production relue (21/10) ·", "pas d'alerte de silence · capture du tableau Langfuse non rangée · compteurs de /sante remis à zéro au redémarrage"], "manque"),
    ],
    fleches=[
        Fleche("br", "lf", sortie="d:0.4", entree="g:0.5"),
        Fleche("lf", "tb", "", sortie="d:0.3", entree="g"),
        Fleche("lf", "al", "", sortie="d:0.85", entree="g:0.3"),
        Fleche("al", "gh"),
        Fleche("cpt", "tbm", "", sortie="d:0.4", entree="g:0.6"),
    ],
    legende="Preuves : evidence/C11/ ; trace de production du 21/10 : evidence/sprint-4/README.md.",
    cles_boites={"lavis": "collecte et restitution principales", "normal": "présent et prouvé",
                 "stock": "service externe", "manque": "à faire", "note": "bac à sable"},
    cles_fleches={"flux": "envoi des mesures ou de l'alerte"},
)

# =============================================================================
# Schéma 5 : C12, la stratégie de test
# =============================================================================
TESTS = Schema(
    nom="E3-strategie-tests", largeur=1400, hauteur=660,
    titre="RITA : ce qui est testé, par quoi, et où",
    sous_titre="Rapport E3, section 6 · 1 751 tests collectés le 24 octobre 2026 (develop, 9683f04), dans 100 fichiers",
    boites=[
        Boite("d", 40, 120, 315, 100, "Données : 337", ["collecte, nettoyage, import,", "schéma, RGPD, fraîcheur ;", "299 dans l'étape « données »"], "lavis"),
        Boite("m", 375, 120, 315, 100, "Modèle et parcours : 163", ["prompt, cascade, graphe,", "contrat JSON de /question,", "banc C7 des fournisseurs"], "lavis"),
        Boite("g", 710, 120, 315, 100, "Garde-fous et évals : 213", ["taux mesurés à chaque poussée ;", "faux positifs ≤ 15 % ;", "blocage ≥ 85 % non atteint"], "lavis"),
        Boite("r", 1045, 120, 315, 100, "Recherche : 112", ["index, filtre par valeur,", "hybride dense + BM25,", "jeu de 26 questions"], "lavis"),
        Boite("a", 40, 240, 315, 100, "API et MCP : 172", ["toutes les routes, 403, 422,", "429, identifiant de requête,", "journal des appels MCP"], "normal"),
        Boite("o", 375, 240, 315, 100, "Monitorage : 238", ["ordre des étapes de la trace,", "aucun texte gardé, compteurs,", "seuils, vigie, alerte"], "normal"),
        Boite("i", 710, 240, 315, 100, "Interface : 137", ["aucune clé, textContent,", "accessibilité ; 27 dans un", "vrai navigateur (Playwright)"], "normal"),
        Boite("l", 1045, 240, 315, 100, "Livraison, outillage : 379", ["script du serveur (183),", "workflows, image, Compose,", "liens, DoD, hooks"], "normal"),

        Boite("zw", 40, 360, 1320, 148, "OÙ ILS TOURNENT", genre="zone"),
        Boite("p", 56, 392, 310, 100, "Poste", ["1 751 collectés ; le 24/10 :", "1 709 verts, 40 ignorés,", "2 xfail (passage local)"], "normal"),
        Boite("c1", 382, 392, 310, 100, "CI, job pytest", ["1. données : 296 verts, 3 ignorés", "2. suite : 1 719 verts, 30", "ignorés, 2 xfail ; 96,32 %"], "lavis"),
        Boite("c2", 708, 392, 310, 100, "CI, job evals", ["mesure des garde-fous, puis", "portes non compensables :", "16 verts, 2 xfail (24/10)"], "lavis"),
        Boite("mg", 1034, 392, 310, 100, "À la main, payant", ["scan Giskard (20/09),", "banc C7 (03/10), mesure", "des questions niveau 2 (21/10)"], "note"),

        Boite("lim", 40, 528, 1320, 80, "Limites", ["aucun jeu de référence pour les briefings · rag/, monitorage/ et passerelle_mcp/ hors du périmètre de couverture (98 % à part) ·", "16 tests sur la base réelle et 5 Spark ignorés en CI · garde-fous à 70 % sur deux positions · nombres : présence, pas le sens"], "manque"),
    ],
    fleches=[],
    legende="Chiffres : pytest --collect-only (1 751) ; CI : passage 40101793487 ; poste : passage local du 24/10.",
    cles_boites={"lavis": "protège le comportement du modèle", "normal": "protège l'application autour",
                 "note": "manuel, payant", "manque": "limites"},
)


def ecrire(s: Schema) -> None:
    (ICI / f"{s.nom}.svg").write_text(svg(s), encoding="utf-8", newline="\n")
    (ICI / f"{s.nom}.drawio").write_text(drawio(s), encoding="utf-8", newline="\n")
    print("écrit", s.nom, ".svg et .drawio")


SCHEMAS = (ARCHI, CHAINE, INTEGRATION, MONITORAGE, TESTS)

if __name__ == "__main__":
    trop = [d for schema in SCHEMAS for d in debordements(schema)]
    if trop:
        raise SystemExit("Texte qui déborde, rien n'est écrit :\n" + "\n".join(trop))
    for schema in SCHEMAS:
        ecrire(schema)
