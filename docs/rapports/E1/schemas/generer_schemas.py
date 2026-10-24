"""Les deux schémas du rapport E1, générés depuis le code : collecte (C1) et nettoyage (C3).

Pourquoi un générateur (04/10/2026) : le schéma de collecte dessiné à la main le 11/08
(`evidence/C1/SCHEMA-C1-collecte-multisource.svg`, conservé comme preuve datée) affichait encore
« 9 motifs, 100 % blocage » et « 8 tables » deux mois plus tard. Ici, les chiffres qui bougent
avec le code sont lus dans le code au moment de la génération (`faits()`), et
`tests/test_schemas_e1.py` vérifie que les fichiers rangés sont exactement ceux qu'on obtiendrait
aujourd'hui. Les chiffres datés (analyse de juillet, comptages du 02/10) restent écrits avec leur date.

Le dessin du nettoyage (boîtes, flèches, .svg et .drawio) est celui des schémas E3 : même module, même charte
(refaite le 04/10 : texte presque noir, une couleur par rôle de boîte et par sens de flèche, légende dessinée).
Celui de la collecte a son propre tracé depuis le 24/10/2026, à la demande d'Era, sur un modèle qu'il a fourni :
bandeaux de colonne pleins, flèches à angle droit, étiquettes en pastille, légende sur une ligne. Mêmes couleurs.

Lancer :  C:\\Python314\\python.exe -X utf8 docs\\rapports\\E1\\schemas\\generer_schemas.py
Puis le rendu PNG (commande dans le README du dossier).
"""
from __future__ import annotations

import html
import importlib.util
import re
import sys
from pathlib import Path

ICI = Path(__file__).parent
RACINE = ICI.parents[3]   # schemas → E1 → rapports → docs → racine du dépôt
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

_spec = importlib.util.spec_from_file_location("schemas_e3", RACINE / "docs/rapports/E3/schemas/generer_schemas.py")
_e3 = importlib.util.module_from_spec(_spec)
sys.modules["schemas_e3"] = _e3   # dataclass relit son module dans sys.modules : l'y inscrire avant
_spec.loader.exec_module(_e3)
Boite, Fleche, Schema = _e3.Boite, _e3.Fleche, _e3.Schema
ROLES, SENS, NAVY, INK, SOFT, POLICE = _e3.ROLES, _e3.SENS, _e3.NAVY, _e3.INK, _e3.SOFT, _e3.POLICE


# =============================================================================
# Le tracé propre du schéma de collecte (24/10/2026)
# =============================================================================
# Les flèches ne relient plus deux points en diagonale : chacune suit une suite de points à angle droit,
# écrite à la main, pour ne jamais traverser une boîte. Les cinq sources web se rejoignent sur un bus.

T_BANDEAU, T_TITRE_B, T_LIGNE_B, INTERLIGNE_B, T_PASTILLE, T_LEG = 14, 14.5, 12, 17, 12, 12
EPAISSEUR_TRAIT = 2.6


# Classes simples, pas @dataclass : le test charge ce fichier sans l'inscrire dans sys.modules, et
# dataclass y relit le module (même piège que pour le module E3, plus haut).
class Trace:
    """Une flèche à angle droit : une suite de points ; pas de pointe pour un tronçon de bus.
    `ou` est le centre de la pastille qui porte l'étiquette."""

    def __init__(self, points: list[tuple[float, float]], sens: str = "flux", etiquette: str = "",
                 ou: tuple[float, float] | None = None, pointe: bool = True) -> None:
        self.points, self.sens, self.etiquette, self.ou, self.pointe = points, sens, etiquette, ou, pointe


class SchemaPropre(Schema):
    """Un Schema, plus ses tracés à angle droit et la couleur du bandeau de chaque colonne."""

    def __init__(self, *, traces: list[Trace], bandeaux: dict[str, str], **champs) -> None:
        super().__init__(**champs)
        self.traces, self.bandeaux = traces, bandeaux


def _capacite(largeur: float, taille: float, gras: bool = False) -> int:
    """Combien de caractères tiennent sur une ligne (estimation : la vraie mesure se fait au rendu)."""
    return int(largeur / (taille * (0.53 if gras else 0.45)))   # mesuré sur le rendu Chrome du 24/10 (Segoe UI)


def _couper(texte: str, cap: int) -> list[str]:
    """Une ligne trop longue se coupe au dernier espace avant la limite ; la suite est décalée."""
    lignes, reste = [], texte
    while len(reste) > cap and reste.rfind(" ", 0, cap) > 2:
        i = reste.rfind(" ", 0, cap)
        lignes.append(reste[:i])
        reste = "  " + reste[i + 1:]
    return lignes + [reste]


def _textes(b: Boite) -> tuple[list[str], list[str]]:
    interieur = b.w - 34
    titres = [t for p in b.titre.split("\n") for t in _couper(p, _capacite(interieur, T_TITRE_B, gras=True))]
    lignes = [x for ligne in b.lignes for x in _couper(ligne, _capacite(interieur, T_LIGNE_B))]
    return titres, lignes


def _largeur_pastille(texte: str) -> float:
    return len(texte) * T_PASTILLE * 0.6 + 22


def _legende_places(s: SchemaPropre) -> list[tuple[str, str, str, float, float]]:
    """(type, clé, libellé, x, y) de chaque entrée de la légende ; passe à la ligne avant le bord droit."""
    x, y, places = 112.0, s.hauteur - 50.0, []
    for genre, cle, libelle in ([("boite", k, v) for k, v in s.cles_boites.items()]
                                + [("fleche", k, v) for k, v in s.cles_fleches.items()]):
        largeur = (34 if genre == "boite" else 46) + len(libelle) * T_LEG * 0.47
        if x + largeur > s.largeur - 36:
            x, y = 112.0, y + 24
        places.append((genre, cle, libelle, x, y))
        x += largeur + 18
    return places


def _svg_propre(s: SchemaPropre) -> str:
    e = html.escape
    W, H = s.largeur, s.hauteur
    marqueurs = "".join(
        f'<marker id="p-{nom}" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto" markerUnits="strokeWidth"><polygon points="0 0,6 3,0 6" fill="{couleur}"/></marker>'
        for nom, (couleur, _) in SENS.items())
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{POLICE}">',
           f'<defs><linearGradient id="bandeau" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{NAVY}"/>'
           f'<stop offset="0.5" stop-color="#1565C0"/><stop offset="1" stop-color="#7C3AED"/></linearGradient>{marqueurs}</defs>',
           f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
           f'<rect width="{W}" height="6" fill="url(#bandeau)"/>',
           f'<text x="36" y="56" font-size="30" font-weight="700" fill="{NAVY}">{e(s.titre)}</text>',
           f'<text x="36" y="84" font-size="15" fill="{SOFT}">{e(s.sous_titre)}</text>']
    for b in s.boites:
        if b.genre == "zone":
            out.append(f'<rect x="{b.x}" y="{b.y}" width="{b.w}" height="{b.h}" rx="12" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>')
            out.append(f'<rect x="{b.x + 8}" y="{b.y + 8}" width="{b.w - 16}" height="34" rx="7" fill="{s.bandeaux[b.id]}"/>')
            out.append(f'<text x="{b.x + 22}" y="{b.y + 30}" font-size="{T_BANDEAU}" font-weight="700" fill="#FFFFFF" letter-spacing="0.6">{e(b.titre)}</text>')
    for b in s.boites:
        if b.genre == "zone":
            continue
        trait, fond, couleur_titre = ROLES[b.genre]
        out.append(f'<rect x="{b.x + 2}" y="{b.y + 3}" width="{b.w}" height="{b.h}" rx="7" fill="#0F172A" opacity="0.06"/>')
        out.append(f'<rect x="{b.x}" y="{b.y}" width="{b.w}" height="{b.h}" rx="7" fill="{fond}" stroke="{trait}" stroke-width="1.6"/>')
        out.append(f'<rect x="{b.x}" y="{b.y}" width="8" height="{b.h}" rx="3" fill="{trait}"/>')
        titres, lignes = _textes(b)
        y = b.y + 26
        for t in titres:
            out.append(f'<text x="{b.x + 22}" y="{y}" font-size="{T_TITRE_B}" font-weight="700" fill="{couleur_titre}">{e(t)}</text>')
            y += 19
        y += 3
        for ligne in lignes:
            out.append(f'<text x="{b.x + 22}" y="{y}" font-size="{T_LIGNE_B}" fill="{INK}" xml:space="preserve">{e(ligne)}</text>')
            y += INTERLIGNE_B
    for t in s.traces:
        couleur, dash = SENS[t.sens]
        pts = " ".join(f"{x:g},{y:g}" for x, y in t.points)
        fin = f' marker-end="url(#p-{t.sens})"' if t.pointe else ""
        tirets = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<polyline points="{pts}" fill="none" stroke="{couleur}" stroke-width="{EPAISSEUR_TRAIT}" stroke-linejoin="round"{tirets}{fin}/>')
    for t in s.traces:
        if t.etiquette:
            couleur, _ = SENS[t.sens]
            cx, cy = t.ou
            w = _largeur_pastille(t.etiquette)
            out.append(f'<rect x="{cx - w / 2:g}" y="{cy - 12:g}" width="{w:g}" height="24" rx="12" fill="#FFFFFF" stroke="{couleur}" stroke-width="1.8"/>')
            out.append(f'<text x="{cx:g}" y="{cy + 4.5:g}" font-size="{T_PASTILLE}" font-weight="700" fill="{couleur}" text-anchor="middle">{e(t.etiquette)}</text>')
    out.append(f'<text x="36" y="{H - 45}" font-size="13" font-weight="700" fill="{NAVY}">Légende</text>')
    for genre, cle, libelle, x, y in _legende_places(s):
        if genre == "boite":
            trait, fond, _ = ROLES[cle]
            out.append(f'<rect x="{x:g}" y="{y - 8:g}" width="26" height="16" rx="4" fill="{fond}" stroke="{trait}" stroke-width="1.6"/>')
            out.append(f'<rect x="{x:g}" y="{y - 8:g}" width="5" height="16" rx="2" fill="{trait}"/>')
            out.append(f'<text x="{x + 34:g}" y="{y + 4.5:g}" font-size="{T_LEG}" fill="{INK}">{e(libelle)}</text>')
        else:
            couleur, dash = SENS[cle]
            tirets = f' stroke-dasharray="{dash}"' if dash else ""
            out.append(f'<line x1="{x:g}" y1="{y:g}" x2="{x + 36:g}" y2="{y:g}" stroke="{couleur}" stroke-width="{EPAISSEUR_TRAIT}"{tirets} marker-end="url(#p-{cle})"/>')
            out.append(f'<text x="{x + 46:g}" y="{y + 4.5:g}" font-size="{T_LEG}" fill="{INK}">{e(libelle)}</text>')
    out.append(f'<text x="36" y="{H - 14}" font-size="{T_LEG}" fill="{SOFT}">{e(s.legende)}</text>')
    out.append("</svg>")
    return "\n".join(out)


def _drawio_propre(s: SchemaPropre) -> str:
    e = html.escape
    cells = ['<mxCell id="0" />', '<mxCell id="1" parent="0" />',
             f'<mxCell id="bandeau" value="" style="rounded=0;html=1;fillColor={NAVY};gradientColor=#7C3AED;gradientDirection=east;strokeColor=none;" vertex="1" parent="1"><mxGeometry x="0" y="0" width="{s.largeur}" height="6" as="geometry" /></mxCell>',
             f'<mxCell id="ttl" value="{e(s.titre)}" style="text;html=1;align=left;fontSize=30;fontStyle=1;fontColor={NAVY};" vertex="1" parent="1"><mxGeometry x="36" y="24" width="{s.largeur - 72}" height="40" as="geometry" /></mxCell>',
             f'<mxCell id="sub" value="{e(s.sous_titre)}" style="text;html=1;align=left;fontSize=15;fontColor={SOFT};" vertex="1" parent="1"><mxGeometry x="36" y="66" width="{s.largeur - 72}" height="24" as="geometry" /></mxCell>']
    for b in sorted(s.boites, key=lambda b: b.genre != "zone"):
        if b.genre == "zone":
            cells.append(f'<mxCell id="{b.id}" value="" style="rounded=1;arcSize=2;html=1;fillColor=#F8FAFC;strokeColor=#E2E8F0;strokeWidth=1.2;" vertex="1" parent="1"><mxGeometry x="{b.x}" y="{b.y}" width="{b.w}" height="{b.h}" as="geometry" /></mxCell>')
            cells.append(f'<mxCell id="{b.id}-bandeau" value="{e(b.titre)}" style="rounded=1;arcSize=18;html=1;fillColor={s.bandeaux[b.id]};strokeColor=none;fontColor=#FFFFFF;fontStyle=1;fontSize={T_BANDEAU};align=left;spacingLeft=14;" vertex="1" parent="1"><mxGeometry x="{b.x + 8}" y="{b.y + 8}" width="{b.w - 16}" height="34" as="geometry" /></mxCell>')
            continue
        trait, fond, couleur_titre = ROLES[b.genre]
        titres, lignes = _textes(b)
        tete = "<br>".join(f'<b><font style="font-size:{T_TITRE_B}px;color:{couleur_titre}">{e(t)}</font></b>' for t in titres)
        corps = "<br>".join(f'<font style="font-size:{T_LIGNE_B}px;color:{INK}">{e(x)}</font>' for x in lignes)
        valeur = e(tete + ("<br>" + corps if corps else ""))
        style = (f"rounded=1;arcSize=4;whiteSpace=wrap;html=1;fillColor={fond};strokeColor={trait};strokeWidth=1.6;"
                 f"align=left;verticalAlign=top;spacingLeft=18;spacingTop=4;fontSize={T_LIGNE_B};fontColor={INK};")
        cells.append(f'<mxCell id="{b.id}" value="{valeur}" style="{style}" vertex="1" parent="1"><mxGeometry x="{b.x}" y="{b.y}" width="{b.w}" height="{b.h}" as="geometry" /></mxCell>')
        cells.append(f'<mxCell id="{b.id}-bande" value="" style="rounded=1;arcSize=30;html=1;fillColor={trait};strokeColor=none;" vertex="1" parent="1"><mxGeometry x="{b.x}" y="{b.y}" width="8" height="{b.h}" as="geometry" /></mxCell>')
    for i, t in enumerate(s.traces):
        couleur, dash = SENS[t.sens]
        style = (f"edgeStyle=none;rounded=0;html=1;strokeColor={couleur};strokeWidth={EPAISSEUR_TRAIT};"
                 + ("endArrow=block;endFill=1;" if t.pointe else "endArrow=none;")
                 + f"fontColor={couleur};fontStyle=1;fontSize={T_PASTILLE};labelBackgroundColor=#FFFFFF;labelBorderColor={couleur};"
                 + ("dashed=1;" if dash else ""))
        (x1, y1), *milieu, (x2, y2) = t.points
        relais = "".join(f'<mxPoint x="{x:g}" y="{y:g}" />' for x, y in milieu)
        cells.append(f'<mxCell id="t{i}" value="{e(t.etiquette)}" style="{style}" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                     f'<mxPoint x="{x1:g}" y="{y1:g}" as="sourcePoint" /><mxPoint x="{x2:g}" y="{y2:g}" as="targetPoint" />'
                     + (f'<Array as="points">{relais}</Array>' if relais else "") + '</mxGeometry></mxCell>')
    cells.append(f'<mxCell id="leg-t" value="Légende" style="text;html=1;align=left;fontSize=13;fontStyle=1;fontColor={NAVY};" vertex="1" parent="1"><mxGeometry x="36" y="{s.hauteur - 62}" width="80" height="24" as="geometry" /></mxCell>')
    for genre, cle, libelle, x, y in _legende_places(s):
        largeur = len(libelle) * T_LEG * 0.47 + 16
        if genre == "boite":
            trait, fond, _ = ROLES[cle]
            cells.append(f'<mxCell id="leg-b-{cle}" value="" style="rounded=1;arcSize=20;html=1;fillColor={fond};strokeColor={trait};strokeWidth=1.6;" vertex="1" parent="1"><mxGeometry x="{x:g}" y="{y - 8:g}" width="26" height="16" as="geometry" /></mxCell>')
            cells.append(f'<mxCell id="leg-bt-{cle}" value="{e(libelle)}" style="text;html=1;align=left;fontSize={T_LEG};fontColor={INK};" vertex="1" parent="1"><mxGeometry x="{x + 30:g}" y="{y - 12:g}" width="{largeur:.0f}" height="24" as="geometry" /></mxCell>')
        else:
            couleur, dash = SENS[cle]
            style = f"endArrow=block;endFill=1;html=1;strokeColor={couleur};strokeWidth={EPAISSEUR_TRAIT};" + ("dashed=1;" if dash else "")
            cells.append(f'<mxCell id="leg-f-{cle}" value="" style="{style}" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{x:g}" y="{y:g}" as="sourcePoint" /><mxPoint x="{x + 36:g}" y="{y:g}" as="targetPoint" /></mxGeometry></mxCell>')
            cells.append(f'<mxCell id="leg-ft-{cle}" value="{e(libelle)}" style="text;html=1;align=left;fontSize={T_LEG};fontColor={INK};" vertex="1" parent="1"><mxGeometry x="{x + 42:g}" y="{y - 12:g}" width="{largeur:.0f}" height="24" as="geometry" /></mxCell>')
    cells.append(f'<mxCell id="leg" value="{e(s.legende)}" style="text;html=1;align=left;fontSize={T_LEG};fontColor={SOFT};" vertex="1" parent="1"><mxGeometry x="36" y="{s.hauteur - 30}" width="{s.largeur - 72}" height="24" as="geometry" /></mxCell>')
    return ('<mxfile host="app.diagrams.net" modified="2026-10-24T00:00:00.000Z" agent="RITA" version="24.0.0" type="device">\n'
            f'  <diagram id="{s.nom}" name="{e(s.titre)}">\n'
            f'    <mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{s.largeur}" pageHeight="{s.hauteur}" math="0" shadow="0">\n'
            '      <root>\n        ' + "\n        ".join(cells) + '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')


def svg(s: Schema) -> str:
    """Le tracé propre pour la collecte, le tracé commun (schémas E3) pour les autres."""
    return _svg_propre(s) if isinstance(s, SchemaPropre) else _e3.svg(s)


def drawio(s: Schema) -> str:
    return _drawio_propre(s) if isinstance(s, SchemaPropre) else _e3.drawio(s)


def _lire(chemin: str) -> str:
    return (RACINE / chemin).read_text(encoding="utf-8")


def faits() -> dict:
    """Ce qui se lit dans le code au moment de la génération. Aucun accès réseau ni base."""
    from evals.mesurer_gardefou import INJECTIONS, LEGITIMES, mesurer
    from guardrails.injection import MOTIFS
    from sources.rss import FLUX

    schema = _lire("db/schema.sql")
    ingest = _lire("pipelines/ingest.py")
    registre = _lire("db/RGPD-registre-des-traitements.md")
    bloc_etapes = re.search(r"^ETAPES = \{(.*?)^\}", ingest, re.S | re.M).group(1)
    mesure = mesurer()
    return {
        "tables": len(re.findall(r"CREATE TABLE", schema, re.I)),
        "vues": len(re.findall(r"CREATE (?:OR REPLACE )?VIEW", schema, re.I)),
        "check": len(re.findall(r"\bCHECK\s*\(", schema)),
        "motifs_injection": len(MOTIFS),
        "blocage_injection": round(mesure["taux_blocage"]),
        "faux_positifs_injection": round(mesure["taux_faux_positifs"]),
        # Les effectifs à côté des taux (24/10/2026) : « 70 % » sur 10 cas n'est pas une garantie générale.
        "injections": len(INJECTIONS),
        "injections_bloquees": len(INJECTIONS) - len(mesure["injections_ratees"]),
        "legitimes": len(LEGITIMES),
        "faux_positifs_n": len(mesure["faux_positifs"]),
        "flux_generaux": len(FLUX),
        "etapes": re.findall(r'^\s*"(\w+)":', bloc_etapes, re.M),
        "devises": re.search(r"DEVISES_SUIVIES = \(([^)]*)\)", ingest).group(1).replace('"', "").replace(" ", ""),
        "traitements_rgpd": sorted(set(re.findall(r"\bT[1-9]\b", registre))),
        "procedures_rgpd": sorted(set(re.findall(r"\bP[1-9]\b", registre))),
    }


# =============================================================================
# Schéma 1 : C1, la collecte multi-source (cinq types exigés, et ce que RITA en fait)
# =============================================================================
def collecte() -> SchemaPropre:
    f = faits()
    t_premier, t_dernier = f["traitements_rgpd"][0], f["traitements_rgpd"][-1]
    p_premier, p_dernier = f["procedures_rgpd"][0], f["procedures_rgpd"][-1]
    # Trois colonnes. x des boîtes : sources 32 à 454, traitements 578 à 938, destination 1072 à 1468.
    # Les cinq sources web se rejoignent sur un bus vertical (x = 496) qui entre dans la collecte du soir.
    milieux = [198, 286, 374, 462, 550]   # milieu vertical de chacune des cinq boîtes du haut
    bus = [Trace([(454, y), (496, y)], pointe=False) for y in milieux]
    return SchemaPropre(
        nom="E1-collecte", largeur=1500, hauteur=1070,
        titre="RITA : la collecte multi-source, cinq types de sources sur cinq",
        sous_titre="Rapport E1, section 3 (C1) · chiffres du code lus à la génération, comptages datés · état au 24 octobre 2026",
        boites=[
            Boite("zs", 20, 104, 446, 800, "1. SOURCES, PAR TYPE EXIGÉ PAR C1", genre="zone"),
            Boite("bce", 32, 160, 422, 76, "SERVICE WEB · Banque centrale européenne", ["sources/ecb.py · taux de change contre l'euro :", f"{f['devises'].replace(',', ', ')} ; zéro taux reçu = étape en échec"], "normal"),
            Boite("fred", 32, 248, 422, 76, "SERVICE WEB · FRED (Réserve fédérale)", ["sources/fred.py · 3 séries macro américaines", "seule source à clé, jamais écrite dans un journal"], "normal"),
            Boite("yahoo", 32, 336, 422, 76, "SERVICE WEB · Yahoo Finance", ["sources/cotations.py · 108 valeurs actives (3 radiées),", "incrémental, rejouable (ON CONFLICT DO UPDATE)"], "normal"),
            Boite("scrap", 32, 424, 422, 76, "PAGE WEB (scraping) · Boursorama", ["sources/scraper.py · robots.txt lu et mis en cache", "structure changée : exception StructurePageModifiee"], "normal"),
            Boite("rss", 32, 512, 422, 76, "COMPLÉMENT · flux RSS d'actualité", [f"sources/rss.py · {f['flux_generaux']} flux de presse générale ; Google News", "par valeur détenue arrêté le 16/10 (décision D3)"], "note"),
            Boite("csv", 32, 616, 422, 76, "FICHIER · export courtier (CSV des positions)", ["sources/positions.py · « ; », cp1252, nombres à la française", "démonstration : positions inventées, CSV versionné"], "normal"),
            Boite("parq", 32, 704, 422, 76, "SYSTÈME BIG DATA · Parquet + Spark", ["bigdata/ · dix ans de cotations, 11 partitions par année", "276 168 lignes ; requêtes Spark SQL (C2)"], "normal"),
            Boite("pgl", 32, 812, 422, 76, "BASE DE DONNÉES · PostgreSQL relu", ["sources/database.py, indicateurs/ · requêtes paramétrées", "scout : DATABASE_URL ; rita_lecture : outils, pré-test"], "normal"),

            Boite("zo", 566, 104, 384, 800, "2. TRAITEMENTS", genre="zone"),
            Boite("ing", 578, 160, 360, 232, "pipelines/ingest.py : la collecte du soir", ["tâche planifiée Windows, chaque soir à 19 h", f"{len(f['etapes'])} étapes : {', '.join(f['etapes'])}", "une étape en échec n'arrête pas les suivantes", "un COMMIT par étape ; rien reçu sur panne = échec", "manifeste JSON par exécution (versions, comptages)", "du 03 au 23/10 : 21 soirs sur 21, 19 à six étapes sur six"], "lavis"),
            Boite("gf", 578, 416, 360, 172, "Garde-fou d'injection\n(guardrails/injection.py)", [f"{f['motifs_injection']} motifs : articles RSS, et textes de la page", "scrapée (nom, ISIN, place : sources/scraper.py)", f"mesure : {f['blocage_injection']} % de blocage ({f['injections_bloquees']}/{f['injections']}),", f"{f['faux_positifs_injection']} % de faux positifs ({f['faux_positifs_n']}/{f['legitimes']})", "article bloqué : marqué, conservé pour l'audit"], "garde"),
            Boite("imp", 578, 616, 360, 164, "db/importer.py : l'import", ["archive Parquet : dédoublonnage (ticker, date),", "  alias de portefeuille résolus (voir C3)", "positions : réconciliation ; une ligne retirée", "  du fichier est close à la date du jour,", "  jamais supprimée"], "lavis"),
            Boite("lect", 578, 812, 360, 76, "Lecture, sans écriture", ["le scout lit la base pour chaque briefing ;", "Spark lit le Parquet sans passer par la base"], "normal"),

            Boite("zd", 1060, 104, 420, 800, "3. DESTINATION ET CONFORMITÉ", genre="zone"),
            Boite("chroma", 1072, 160, 396, 96, "Index ChromaDB (étape indexation)", ["articles non bloqués, vectorisés pour la recherche", "reconstruit après chaque collecte"], "stock"),
            Boite("pg", 1072, 280, 396, 200, "PostgreSQL 18 (Merise, C4)", [f"{f['tables']} tables, {f['vues']} vue, {f['check']} contraintes CHECK", "écrit par la collecte et l'import, seulement", "278 473 cotations (29/07/2016 au 02/10/2026)", "2 314 articles indexés (23/10) ; séries FRED", "servi par l'API /donnees/* (C5)"], "stock"),
            Boite("rgpd", 1072, 616, 396, 164, "RGPD (registre art. 30, db/rgpd_purge.py)", [f"traitements {t_premier} à {t_dernier}, procédures de tri {p_premier} à {p_dernier}", "personnel : positions réelles, journal MCP, noms du corpus", "fichier réel hors de Git, jamais envoyé au modèle", "purge en simulation par défaut ;", "lancement manuel, écrit comme tel"], "normal"),

            Boite("cov", 20, 924, 1460, 66, "Couverture de C1 : service web ✓ · page web ✓ · fichier ✓ · base de données ✓ · système big data ✓",
                  ["Cinq types sur cinq, plus le RSS en complément. Une preuve par source dans evidence/C1/ ; la figure du 11/08 qui s'y trouve est une preuve datée : ses chiffres de tables et de garde-fou ne sont plus à jour."], "neuf"),
        ],
        fleches=[],
        traces=bus + [
            Trace([(496, milieux[0]), (496, milieux[-1])], pointe=False),
            Trace([(496, 276), (578, 276)]),                                    # le bus entre dans la collecte du soir
            Trace([(758, 392), (758, 416)]),                                    # articles et page scrapée : au garde-fou
            Trace([(454, 654), (578, 654)]),                                    # CSV → import
            Trace([(454, 742), (578, 742)]),                                    # Parquet → import
            Trace([(454, 850), (578, 850)], "lecture"),                         # base relue → lecture
            Trace([(938, 208), (1072, 208)], "ecriture"),                       # indexation → ChromaDB
            Trace([(938, 330), (1072, 330)], "ecriture", "écrit", (1005, 330)),
            Trace([(938, 502), (1003, 502), (1003, 400), (1072, 400)], "ecriture", "articles admis", (1003, 452)),
            Trace([(938, 680), (1035, 680), (1035, 470), (1072, 470)], "ecriture", "insère", (1035, 575)),
            Trace([(938, 740), (1072, 740)], "perso", "positions", (1005, 740)),
        ],
        bandeaux={"zs": NAVY, "zo": "#1565C0", "zd": "#6D28D9"},
        legende="Génération : docs/rapports/E1/schemas/generer_schemas.py, vérifiée par tests/test_schemas_e1.py.",
        cles_boites={"normal": "source ou lecture", "note": "complément", "lavis": "code qui traite et écrit",
                     "garde": "garde-fou", "stock": "réserve de données"},
        cles_fleches={"flux": "données collectées", "ecriture": "écriture", "lecture": "lecture seule",
                      "perso": "données personnelles (RGPD)"},
    )


# =============================================================================
# Schéma 2 : C3, du jeu brut au jeu propre : défaut mesuré, décision, fichier qui l'applique
# =============================================================================
def nettoyage() -> Schema:
    return Schema(
        nom="E1-nettoyage", largeur=1500, hauteur=820,
        titre="RITA : nettoyer et agréger, chaque défaut mesuré devient une règle",
        sous_titre="Rapport E1, section 4 (C3) · analyse exploratoire de juillet 2026, incident INC-005 du 27 septembre · état au 4 octobre 2026",
        boites=[
            Boite("brut", 40, 100, 300, 104, "1. Le jeu brut", ["dix ans de cotations, 111 valeurs", "Parquet, 11 partitions par année", "276 168 lignes analysées", "0 valeur manquante"], "stock"),
            Boite("eda", 380, 100, 330, 104, "2. Analyse exploratoire (juillet)", ["compter avant de modéliser :", "doublons, bornes, volumes, extrêmes,", "libellés ; preuves dans evidence/C3/", "chaque défaut → une décision de schéma"], "lavis"),
            Boite("agr", 750, 100, 330, 104, "3. Agrégation en un seul jeu", ["dates ISO 8601 dans le fuseau de la place", "devises ISO 4217, nombres français convertis", "codes ISIN complétés", "puis chargement par db/importer.py"], "lavis"),
            Boite("res", 1120, 100, 340, 104, "4. Le jeu propre, en base", ["276 168 lues → 2 560 doublons écartés", "→ 273 608 insérées (juillet 2026)", "→ 278 473 cotations au 02/10/2026", "après 40 collectes du soir"], "stock"),

            Boite("zr", 40, 230, 1420, 410, "DÉFAUT MESURÉ  →  DÉCISION  →  FICHIER QUI L'APPLIQUE", genre="zone"),
            Boite("d1", 56, 258, 440, 66, "5 120 lignes en double (2 560 paires), surtout VIRI.PA", ["sans règle : l'import échoue sur la clé primaire"], "normal"),
            Boite("r1", 520, 258, 520, 66, "Dédoublonnage sur (ticker, date_seance) avant insertion", ["la collecte du soir est rejouable : ON CONFLICT DO UPDATE"], "lavis"),
            Boite("f1", 1064, 258, 380, 66, "db/importer.py", ["preuve : evidence/C3/preuve-dedoublonnage-cgg.md"], "note"),

            Boite("d2", 56, 334, 440, 66, "1 533 clôtures hors de [bas, haut], dont 1 142 STLAP.PA", ["sans règle : des variations aberrantes au briefing"], "normal"),
            Boite("r2", 520, 334, 520, 66, "STLAP.PA marquée INCOHERENT : exclue des requêtes, gardée", ["aucune contrainte ne borne la clôture (db/schema.sql refuse haut < bas) :", "23 lignes hors bornes en base le 04/10, limite déclarée"], "manque"),
            Boite("f2", 1064, 334, 380, 66, "db/importer.py (QUALITE), sources/database.py", ["les requêtes ne lisent que statut_qualite = 'OK'"], "note"),

            Boite("d3", 56, 410, 440, 66, "Cours maximal 7 156 748 (ALJXR.PA)", ["regroupement d'actions rétro-ajusté (prix ÷ 36 millions)"], "normal"),
            Boite("r3", 520, 410, 520, 66, "Marquée INCOHERENT, conservée, mécanisme identifié", ["la table operation_sur_titre est conçue, pas construite"], "manque"),
            Boite("f3", 1064, 410, 380, 66, "evidence/C3/preuve-artefact-reverse-split.md", ["statut_qualite : exclure sans supprimer"], "note"),

            Boite("d4", 56, 486, 440, 66, "Libellés du portefeuille différents des tickers", ["« CGG BS », « CGG RGPT » : aucune position rattachée"], "normal"),
            Boite("r4", 520, 486, 520, 66, "Entité ALIAS au modèle : une valeur, plusieurs noms", ["112 alias pour 111 valeurs"], "lavis"),
            Boite("f4", 1064, 486, 380, 66, "db/importer.py, table alias_valeur", ["cardinalité VALEUR 1,n / ALIAS 1,1 (Merise, C4)"], "note"),

            Boite("d5", 56, 562, 440, 66, "INC-005 (27/09) : 52 426 cotations un dimanche", ["date UTC d'un « minuit à Paris » = la veille à 22 h ;", "même cause : pence de Londres, dollars, samedi, fériés"], "normal"),
            Boite("r5", 520, 562, 520, 66, "La place de cotation entre dans le modèle", ["fuseau, devise et unité de prix par place, fériés Euronext ;", "correctif en une transaction, 42 tests écrits d'abord"], "lavis"),
            Boite("f5", 1064, 562, 380, 66, "sources/marches.py, sources/cotations.py", ["leçon : compter aussi par jour de la semaine"], "note"),

            Boite("pos", 40, 660, 700, 96, "Le fichier des positions (export courtier)", ["sources/positions.py : séparateur « ; », encodage cp1252 détecté,", "« 632,40 » et « 1 250 » (espace insécable) convertis, en-têtes variables ;", "chaque ligne invalide est rejetée avec sa cause, jamais ignorée en silence"], "normal"),
            Boite("vol", 760, 660, 700, 96, "Ce qui reste visible plutôt que corrigé", ["2 802 séances à volume nul conservées : la requête des volumes anormaux", "  (R3, db/requetes.sql) exige une moyenne sur 20 séances > 0, sinon division par zéro ;", "les valeurs douteuses portent un statut_qualite au lieu d'être supprimées"], "normal"),
        ],
        fleches=[
            Fleche("brut", "eda"), Fleche("eda", "agr"), Fleche("agr", "res"),
            Fleche("d1", "r1"), Fleche("r1", "f1"),
            Fleche("d2", "r2"), Fleche("r2", "f2"),
            Fleche("d3", "r3"), Fleche("r3", "f3"),
            Fleche("d4", "r4"), Fleche("r4", "f4"),
            Fleche("d5", "r5"), Fleche("r5", "f5"),
        ],
        legende="Chiffres de juillet et du 02/10 : rapport E1, section 4.",
        cles_boites={"stock": "jeu de données", "normal": "défaut mesuré", "lavis": "décision appliquée",
                     "manque": "limite déclarée, ou conçu non construit", "note": "fichier ou preuve à ouvrir"},
        cles_fleches={"flux": "mène à"},
    )


SCHEMAS = {"E1-collecte": collecte, "E1-nettoyage": nettoyage}


def ecrire(nom: str) -> None:
    s = SCHEMAS[nom]()
    (ICI / f"{s.nom}.svg").write_text(svg(s), encoding="utf-8", newline="\n")
    (ICI / f"{s.nom}.drawio").write_text(drawio(s), encoding="utf-8", newline="\n")
    print("écrit", s.nom, ".svg et .drawio")


if __name__ == "__main__":
    for nom in SCHEMAS:
        ecrire(nom)
