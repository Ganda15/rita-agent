"""Les schémas du rapport E1, générés depuis le code : collecte (C1), requêtes (C2), nettoyage (C3), API (C5).

Pourquoi un générateur (04/10/2026) : le schéma de collecte dessiné à la main le 11/08
(`evidence/C1/SCHEMA-C1-collecte-multisource.svg`, conservé comme preuve datée) affichait encore
« 9 motifs, 100 % blocage » et « 8 tables » deux mois plus tard. Ici, les chiffres qui bougent
avec le code sont lus dans le code au moment de la génération (`faits()`), et
`tests/test_schemas_e1.py` vérifie que les fichiers rangés sont exactement ceux qu'on obtiendrait
aujourd'hui. Les chiffres datés (analyse de juillet, comptages du 02/10) restent écrits avec leur date.

Les couleurs (une par rôle de boîte et par sens de flèche) viennent du module des schémas E3. Le tracé est celui
de la collecte depuis le 24/10/2026, sur un modèle fourni par Era : bandeaux de colonne pleins, flèches à angle
droit, étiquettes en pastille, légende sur une ligne. Le 27/10, à sa demande, le nettoyage passe au même tracé, et
C2 et C5 ont leur schéma. Pour ces trois-là, la mise en forme illustrée (icônes, formes de base de données) sort
aussi du générateur (`illustre`) ; celle de la collecte reste la page fournie par Era.

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
Boite, Schema = _e3.Boite, _e3.Schema
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
    """Un Schema, plus ses tracés à angle droit et la couleur du bandeau de chaque colonne.
    `formes` (27/10) : pour l'illustration, la forme et l'icône de chaque boîte, {id: (forme, icône)}."""

    def __init__(self, *, traces: list[Trace], bandeaux: dict[str, str],
                 formes: dict[str, tuple[str, str]] | None = None, **champs) -> None:
        super().__init__(**champs)
        self.traces, self.bandeaux, self.formes = traces, bandeaux, formes or {}


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
    """Le tracé propre (tous les schémas E1 depuis le 27/10), le tracé commun des schémas E3 sinon."""
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
# 27/10/2026, à la demande d'Era : même tracé que la collecte, trois colonnes à bandeau. Les textes sont ceux
# du 4 octobre, inchangés : seuls la mise en page et les flèches changent.
def nettoyage() -> SchemaPropre:
    lignes = [300, 402, 504, 606, 708]   # haut de chacune des cinq rangées défaut → décision → fichier
    rangees = [Trace([(496, y + 46), (532, y + 46)]) for y in lignes] + [Trace([(1048, y + 46), (1084, y + 46)]) for y in lignes]
    return SchemaPropre(
        nom="E1-nettoyage", largeur=1500, hauteur=1030,
        titre="RITA : nettoyer et agréger, chaque défaut mesuré devient une règle",
        sous_titre="Rapport E1, section 4 (C3) · analyse exploratoire de juillet 2026, INC-005 du 27/09 · comptages du 4 octobre, schéma revu le 28 octobre 2026",
        boites=[
            Boite("brut", 40, 104, 300, 124, "1. Le jeu brut", ["dix ans de cotations, 111 valeurs", "Parquet, 11 partitions par année", "276 168 lignes analysées", "0 valeur manquante"], "stock"),
            Boite("eda", 380, 104, 330, 124, "2. Analyse exploratoire (juillet)", ["compter avant de modéliser :", "doublons, bornes, volumes, extrêmes,", "libellés ; preuves dans evidence/C3/", "chaque défaut → une décision de schéma"], "lavis"),
            Boite("agr", 750, 104, 330, 124, "3. Agrégation en un seul jeu", ["dates ISO 8601 dans le fuseau de la place", "devises ISO 4217, nombres français convertis", "codes ISIN complétés", "puis chargement par db/importer.py"], "lavis"),
            Boite("res", 1120, 104, 340, 124, "4. Le jeu contrôlé, en base", ["276 168 lues → 2 560 doublons écartés", "→ 273 608 insérées (juillet 2026)", "→ 278 473 cotations au 02/10/2026", "après 40 collectes du soir"], "stock"),

            Boite("zd", 28, 248, 480, 566, "DÉFAUT MESURÉ", genre="zone"),
            Boite("zr", 520, 248, 540, 566, "DÉCISION", genre="zone"),
            Boite("zf", 1072, 248, 400, 566, "FICHIER QUI L'APPLIQUE", genre="zone"),
            Boite("d1", 40, 300, 456, 92, "5 120 lignes en double (2 560 paires), surtout VIRI.PA", ["sans règle : l'import échoue sur la clé primaire"], "normal"),
            Boite("r1", 532, 300, 516, 92, "Dédoublonnage sur (ticker, date), avant insertion", ["la date de l'archive, avant le calcul de date_seance ;", "la collecte du soir, elle, rejoue : ON CONFLICT DO UPDATE"], "lavis"),
            Boite("f1", 1084, 300, 376, 92, "db/importer.py", ["preuve : evidence/C3/preuve-dedoublonnage-cgg.md"], "note"),

            Boite("d2", 40, 402, 456, 92, "1 533 clôtures hors de [bas, haut], dont 1 142 STLAP.PA", ["sans règle : des variations aberrantes au briefing"], "normal"),
            Boite("r2", 532, 402, 516, 92, "STLAP.PA marquée INCOHERENT : exclue des classements, gardée", ["aucune contrainte ne borne la clôture (db/schema.sql refuse haut < bas) :", "23 lignes hors bornes en base le 04/10, limite déclarée"], "manque"),
            Boite("f2", 1084, 402, 376, 92, "db/importer.py (QUALITE), sources/database.py", ["R2 et R3 : seulement 'OK' ; R1 affiche le statut"], "note"),

            Boite("d3", 40, 504, 456, 92, "Cours maximal 7 156 748 (ALJXR.PA)", ["regroupement d'actions rétro-ajusté (prix ÷ 36 millions)"], "normal"),
            Boite("r3", 532, 504, 516, 92, "Marquée INCOHERENT, conservée, mécanisme identifié", ["la table operation_sur_titre est conçue, pas construite"], "manque"),
            Boite("f3", 1084, 504, 376, 92, "evidence/C3/preuve-artefact-reverse-split.md", ["statut_qualite : écartée des classements, gardée"], "note"),

            Boite("d4", 40, 606, 456, 92, "Libellés du portefeuille différents des tickers", ["« CGG BS », « CGG RGPT » : aucune position rattachée"], "normal"),
            Boite("r4", 532, 606, 516, 92, "Entité ALIAS au modèle : une valeur, plusieurs noms", ["112 alias pour 111 valeurs ; deux libellés, un ticker :", "pas la preuve d'un même instrument (addendum du 26/10) ;", "une position « CGG BS » serait valorisée au cours de l'action"], "manque"),
            Boite("f4", 1084, 606, 376, 92, "db/importer.py, table alias_valeur", ["cardinalité VALEUR 1,n / ALIAS 1,1 (Merise, C4)"], "note"),

            Boite("d5", 40, 708, 456, 92, "INC-005 (27/09) : 52 426 cotations un dimanche", ["date UTC d'un « minuit à Paris » = la veille à 22 h ;", "même racine, la place de cotation non modélisée :", "pence de Londres, dollars, samedi, fériés"], "normal"),
            Boite("r5", 532, 708, 516, 92, "La place de cotation entre dans le modèle", ["fuseau, devise et unité de prix par place, fériés Euronext ;", "correctif en une transaction, 42 tests écrits d'abord"], "lavis"),
            Boite("f5", 1084, 708, 376, 92, "sources/marches.py, sources/cotations.py", ["leçon : compter aussi par jour de la semaine"], "note"),

            Boite("pos", 40, 834, 700, 110, "Le fichier des positions (export courtier)", ["sources/positions.py : séparateur « ; », encodage cp1252 détecté,", "« 632,40 » et « 1 250 » (espace insécable) convertis, en-têtes variables ;", "chaque ligne invalide est rejetée avec sa cause, jamais ignorée en silence"], "normal"),
            Boite("vol", 760, 834, 700, 110, "Ce qui reste visible plutôt que corrigé", ["2 802 séances à volume nul conservées : la requête des volumes anormaux", "  (R3, db/requetes.sql) exige une moyenne sur 20 séances > 0, sinon division par zéro ;", "les valeurs douteuses portent un statut_qualite au lieu d'être supprimées"], "normal"),
        ],
        fleches=[],
        traces=[Trace([(340, 166), (380, 166)]), Trace([(710, 166), (750, 166)]), Trace([(1080, 166), (1120, 166)])] + rangees,
        bandeaux={"zd": NAVY, "zr": "#1565C0", "zf": "#475569"},
        formes={"brut": ("cylindre", "parquet"), "eda": ("code", ""), "agr": ("code", ""), "res": ("cylindre", "elephant"),
                **{f"d{i}": ("boite", "alerte") for i in range(1, 6)},
                "r1": ("boite", "coche"), "r5": ("boite", "coche"),
                "r2": ("boite", "drapeau"), "r3": ("boite", "drapeau"), "r4": ("boite", "drapeau"),
                **{f"f{i}": ("fichier", "document") for i in range(1, 6)},
                "pos": ("fichier", "tableur"), "vol": ("boite", "oeil")},
        legende="Chiffres de juillet et du 02/10 : rapport E1, section 4.",
        cles_boites={"stock": "jeu de données", "normal": "défaut mesuré", "lavis": "décision appliquée",
                     "manque": "limite déclarée, ou conçu non construit", "note": "fichier ou preuve à ouvrir"},
        cles_fleches={"flux": "mène à"},
    )


# =============================================================================
# Schéma 3 : C2, interroger : du SQL sur PostgreSQL, du Spark SQL sur Parquet, chaque optimisation mesurée
# =============================================================================
# Lignes par partition de l'archive Parquet, comptées le 27/10/2026 (métadonnées des fichiers, pyarrow).
# L'archive n'est pas dans le dépôt : le comptage est donc daté, et tests/test_schemas_e1.py le compare à
# l'archive quand elle est sur la machine.
PARQUET_27_10 = {2016: 11980, 2017: 27770, 2018: 27610, 2019: 27463, 2020: 27488, 2021: 27589,
                 2022: 27480, 2023: 27454, 2024: 27648, 2025: 27783, 2026: 15903}


def _n(nombre: int) -> str:
    """12345 → « 12 345 », l'écriture du rapport."""
    return f"{nombre:,}".replace(",", " ")


def faits_requetes() -> dict:
    """Les filtres et le réglage de Spark, lus dans le code ; les volumes lus s'en déduisent."""
    from bigdata.query_spark import S2_AMPLITUDE, S3_EXTREMES
    return {
        "annee_s2": int(re.search(r"annee >= (\d{4})", S2_AMPLITUDE).group(1)),
        "annee_s3": int(re.search(r"annee >= (\d{4})", S3_EXTREMES).group(1)),
        "having_s2": int(re.search(r"HAVING COUNT\(\*\) >= (\d+)", S2_AMPLITUDE).group(1)),
        "shuffle": int(re.search(r'shuffle\.partitions", "(\d+)"', _lire("bigdata/session_spark.py")).group(1)),
    }


def requetes() -> SchemaPropre:
    f, tables = faits_requetes(), faits()["tables"]
    p = PARQUET_27_10
    nb, total = len(p), sum(p.values())

    def lues(depuis: int) -> tuple[int, int]:
        annees = [a for a in p if a >= depuis]
        return len(annees), sum(p[a] for a in annees)

    (n2, l2), (n3, l3) = lues(f["annee_s2"]), lues(f["annee_s3"])
    par_annee = [f"{a} : {_n(n)}" for a, n in p.items()]
    return SchemaPropre(
        nom="E1-requetes", largeur=1500, hauteur=860,
        titre="RITA : interroger en SQL et en Spark SQL, optimisations expliquées, mesures datées",
        sous_titre="Rapport E1, section 6 (C2) · filtres lus dans le code à la génération, comptages et mesures datés · état au 27 octobre 2026",
        boites=[
            Boite("zs", 20, 104, 446, 584, "1. DEUX SYSTÈMES, DEUX LANGAGES", genre="zone"),
            Boite("pg", 32, 160, 422, 130, "SGBD · PostgreSQL 18 (Merise, C4)", [f"{tables} tables, 278 473 cotations au 02/10/2026", "clé primaire (ticker, date_seance), index sur la date", "sources/database.py : les requêtes de db/requetes.sql,", "  valeurs passées par %(nom)s, jamais concaténées"], "stock"),
            Boite("parq", 32, 358, 422, 130, "SYSTÈME BIG DATA · Parquet + Spark", [f"data/bigdata/ohlcv/annee=AAAA/ : {nb} partitions", f"{_n(total)} lignes, 111 valeurs, 14 Mo (comptés le 27/10)", "du 29/07/2016 au 29/07/2026, écrit par build_parquet.py", f"Spark en local[*], {f['shuffle']} partitions de shuffle (et non 200)"], "stock"),
            Boite("part", 32, 538, 422, 130, "Lignes par partition (comptées le 27/10)", [" · ".join(par_annee[i:i + 3]) for i in range(0, nb, 3)] + ["2016 et 2026 incomplètes : dix ans depuis le 29/07/2016"], "note"),

            Boite("zo", 566, 104, 384, 584, "2. LES REQUÊTES, DANS LE CODE", genre="zone"),
            Boite("sql", 578, 160, 360, 178, "db/requetes.sql : le SQL de PostgreSQL", ["R1 portefeuille en euros : LEFT JOIN LATERAL,", "  dernier cours de chaque valeur, dernier taux", "R1 bis positions closes, pour le propriétaire seul", "R2 plus fortes variations : LAG() par valeur,", "  filtre de date avant la fenêtre, statut OK", "R3 volumes anormaux : moyenne des 20 séances", "  précédentes, sur les 60 derniers jours"], "lavis"),
            Boite("spark", 578, 358, 360, 160, "bigdata/query_spark.py : Spark SQL", ["S1 volumétrie : GROUP BY annee, sans filtre", f"S2 amplitude moyenne : WHERE annee >= {f['annee_s2']},", f"  HAVING COUNT(*) >= {f['having_s2']} séances", f"S3 meilleure séance : WHERE annee >= {f['annee_s3']},", "  LAG() puis RANK() OVER (PARTITION BY ticker)", "le même vocabulaire que PostgreSQL, un autre moteur"], "lavis"),
            Boite("choix", 578, 538, 360, 100, "Les choix, écrits devant chaque requête", ["OBJECTIF, CHOIX (sélection, jointure, filtre),", "OPTIMISATION, dans les deux fichiers", "sorties réelles : evidence/C2/preuve-requetes-sql.md"], "normal"),

            Boite("zd", 1060, 104, 420, 584, "3. LE COÛT, MESURÉ", genre="zone"),
            Boite("expl", 1072, 160, 396, 178, "PostgreSQL : EXPLAIN ANALYZE (août 2026)", ["dernier cours des 111 valeurs :", "  DISTINCT ON 295,19 ms, LATERAL 1,19 ms", "les 7 positions : CTE DISTINCT ON 258,00 ms,", "  sous-requête corrélée 0,12 ms, LATERAL 0,24 ms", "DISTINCT ON triait les 273 608 cotations ;", "  LATERAL va chercher par l'index (cotation_pkey)", "l'optimisation prévue était la mauvaise"], "note"),
            # 28/10 (relecture croisée) : le plan montre les partitions écartées du scan, pas « des fichiers jamais
            # ouverts » ; et ces nombres valent pour le jeu compté le 27/10 et les filtres d'aujourd'hui.
            Boite("plan", 1072, 358, 396, 160, "Spark : partitions lues (comptées le 27/10)", [f"S1 lit {nb}/{nb} partitions : {_n(total)} lignes", f"S2 lit {n2}/{nb} : {_n(l2)} lignes, {nb - n2} partitions écartées", f"S3 lit {n3}/{nb} : {_n(l3)} lignes, {nb - n3} partitions écartées", "preuve dans le plan, pour annee = 2024 :", "  PartitionFilters: [isnotnull(annee), (annee = 2024)]", f"  1 partition lue sur {nb}, {_n(p[2024])} lignes", "coût qui reste : le shuffle (GROUP BY, PARTITION BY)"], "note"),
            Boite("cmp", 1072, 538, 396, 100, "Optimiser ne veut pas dire la même chose", ["PostgreSQL : choisir le bon chemin d'accès, l'index", "Spark : ne pas lire les partitions inutiles", "ce qui coûte : trier toute la table / le shuffle"], "normal"),

            Boite("cov", 20, 706, 1460, 66, "Couverture de C2 : requêtes fonctionnelles ✓ · choix documentés ✓ · optimisations expliquées ✓",
                  [f"SGBD et système big data, chacun dans son langage. Limite : {_n(total)} lignes et 14 Mo ne sont pas du big data ; la méthode est montrée en local (cadrage accepté par le formateur en août)."], "neuf"),
        ],
        fleches=[],
        traces=[
            Trace([(454, 225), (578, 225)], "lecture", "lit", (516, 225)),
            Trace([(454, 423), (578, 423)], "lecture", "lit", (516, 423)),
            Trace([(938, 249), (1072, 249)], "flux", "mesuré", (1005, 249)),
            Trace([(938, 438), (1072, 438)], "flux", "plan", (1005, 438)),
        ],
        bandeaux={"zs": NAVY, "zo": "#1565C0", "zd": "#475569"},
        formes={"pg": ("cylindre", "elephant"), "parq": ("cylindre", "parquet"), "part": ("boite", "barres"),
                "sql": ("code", ""), "spark": ("code", ""), "choix": ("boite", "liste"),
                "expl": ("boite", "chrono"), "plan": ("boite", "entonnoir"), "cmp": ("boite", "balance")},
        legende="Génération : docs/rapports/E1/schemas/generer_schemas.py, vérifiée par tests/test_schemas_e1.py.",
        cles_boites={"stock": "système de données", "lavis": "requêtes, dans le code", "note": "comptage ou mesure daté",
                     "normal": "choix et comparaison"},
        cles_fleches={"lecture": "lecture seule", "flux": "mesure ou plan d'exécution"},
    )


# =============================================================================
# Schéma 4 : C5, servir le jeu de données : une API REST, une clé sur tout le routeur
# =============================================================================
def faits_api() -> dict:
    """Les routes, le contrat et les réglages de l'API, lus dans le code. Aucun appel réseau, aucune base."""
    from api.main import LONGUEUR_MINIMALE_CLE, app
    donnees = _lire("api/donnees.py")
    contrat = app.openapi()
    return {
        "routes": re.findall(r'@routeur\.get\(\s*"([^"]+)"', donnees),
        "limite": int(re.search(r"^LIMITE_MAX = (\d+)", donnees, re.M).group(1)),
        "cle_min": LONGUEUR_MINIMALE_CLE,
        "openapi": contrat["openapi"],
        "chemins": len(contrat["paths"]),
        "chemins_donnees": len([c for c in contrat["paths"] if c.startswith("/donnees")]),
        "securite": "APIKeyHeader" if "APIKeyHeader" in contrat["components"]["securitySchemes"] else "aucun",
        "outils_mcp": len(re.findall(r"@serveur\.tool\(", _lire("passerelle_mcp/serveur.py"))),
        "tests_api": len(re.findall(r"^def test_", _lire("tests/test_api_donnees.py"), re.M)),
    }


def _par_lignes(morceaux: list[str], largeur: int = 48) -> list[str]:
    """Les routes, regroupées en lignes d'au plus `largeur` caractères, séparées par « · »."""
    lignes, courante = [], ""
    for m in morceaux:
        essai = f"{courante} · {m}" if courante else m
        if len(essai) > largeur and courante:
            lignes.append(courante)
            essai = m
        courante = essai
    return lignes + [courante]


def api() -> SchemaPropre:
    f = faits_api()
    milieux = [210, 326, 437, 543]   # milieu vertical des quatre clients
    bus = [Trace([(454, y), (496, y)], pointe=False) for y in milieux]
    return SchemaPropre(
        nom="E1-api", largeur=1500, hauteur=870,
        titre="RITA : servir le jeu de données, une API REST protégée par une clé",
        sous_titre="Rapport E1, section 7 (C5) · routes et contrat lus dans le code à la génération · état au 27 octobre 2026",
        boites=[
            Boite("zc", 20, 104, 446, 590, "1. LES CLIENTS DU JEU DE DONNÉES", genre="zone"),
            Boite("web", 32, 160, 422, 100, "Interface web (frontend/)", ["écrans : portefeuille, indicateurs, risque, fraîcheur,", "  valeurs, fiche d'un article cité", "clé saisie à l'écran, jamais écrite dans frontend/"], "normal"),
            Boite("mcp", 32, 276, 422, 100, "Passerelle MCP (passerelle_mcp/serveur.py)", [f"{f['outils_mcp']} outils : rita_fraicheur, rita_portefeuille,", "  rita_indicateurs ; trois lectures, avec la clé"], "normal"),
            Boite("dep", 32, 392, 422, 90, "Contrôle après livraison (deploy/deployer.py)", ["sans clé, GET /donnees/valeurs doit répondre 403,", "  sinon le contrôle de la livraison échoue"], "normal"),
            Boite("doc", 32, 498, 422, 90, "curl et navigateur : /docs", ["le contrat essayé à l'écran (Swagger UI)", "la clé se colle une fois, dans « Authorize »"], "normal"),

            Boite("za", 566, 104, 384, 590, "2. L'API REST (FastAPI)", genre="zone"),
            Boite("main", 578, 160, 360, 130, "api/main.py : la clé sur tout le routeur", ["include_router(routeur_donnees,", "  dependencies=[Depends(verify_api_key)])", "une route ajoutée est protégée d'office", "X-Request-ID sur toute réponse, refus compris"], "lavis"),
            Boite("cle", 578, 316, 360, 150, "Contrôle d'accès : verify_api_key", ["en-tête X-API-Key, comparé par compare_digest", "absente ou fausse : 403, une ligne de journal,", "  jamais la clé, ni un morceau", f"clé d'au moins {f['cle_min']} caractères, sans défaut"], "garde"),
            Boite("routes", 578, 512, 360, 172, f"api/donnees.py : {len(f['routes'])} points de terminaison",
                  _par_lignes(f["routes"]) + [f"limite plafonnée par route, {_n(f['limite'])} au plus ;", "  /cotations se lit par pages, avec jusqu_a", "422 saisie invalide, 404 ticker ou article inconnu"], "lavis"),

            Boite("zd", 1060, 104, 420, 590, "3. DONNÉES, CONTRAT ET PREUVES", genre="zone"),
            # 28/10 (relecture croisée) : un appel de la passerelle MCP, /donnees compris, laisse une ligne dans
            # mcp_calls (api/main.py, X-Client-Id) ; « en lecture seule » était donc faux pour l'API.
            Boite("pg", 1072, 160, 396, 120, "PostgreSQL 18 : /donnees lit les données", ["sources/database.py : les requêtes de db/requetes.sql", "indicateurs/ : calculs déterministes, sans modèle", "appel de la passerelle MCP : une ligne d'audit", "  (mcp_calls), écrite après la réponse"], "stock"),
            Boite("contrat", 1072, 300, 396, 100, f"Contrat OpenAPI {f['openapi']}, généré par FastAPI", [f"{f['chemins']} chemins, dont {f['chemins_donnees']} sous /donnees", f"schéma de sécurité {f['securite']} déclaré", "/openapi.json et /docs, tenus à jour par le code"], "stock"),
            Boite("tests", 1072, 560, 396, 120, "Les preuves : tests/test_api_donnees.py", [f"{f['tests_api']} fonctions de test, dont :", "chaque route de /donnees, sans clé : 403", f"2 600 séances fictives, pages de {_n(f['limite'])} (SQLite", "  en mémoire) : ni trou ni doublon"], "note"),

            Boite("cov", 20, 712, 1460, 66, "Couverture de C5 : points de terminaison documentés ✓ · authentification documentée ✓ · standard OpenAPI ✓ · accès restreint ✓ · données nécessaires récupérables ✓",
                  ["Limites : une seule clé partagée, sans droits par utilisateur (décision D10) ; pas de quota sur /donnees (seulement /briefing et /question, qui appellent le modèle) ; taux de change sans route propre, ils servent à convertir le portefeuille."], "neuf"),
        ],
        fleches=[],
        traces=bus + [
            Trace([(496, milieux[0]), (496, milieux[-1])], pointe=False),
            Trace([(496, 225), (578, 225)]),                                       # les clients entrent par la clé
            Trace([(758, 290), (758, 316)]),
            Trace([(758, 466), (758, 512)], "flux", "clé valide", (758, 489)),
            Trace([(938, 530), (1003, 530), (1003, 215), (1072, 215)], "lecture", "lit", (970, 530)),
            Trace([(938, 560), (1035, 560), (1035, 350), (1072, 350)], "flux", "décrit", (986, 560)),
            Trace([(1072, 640), (938, 640)], "flux", "vérifie", (1005, 640)),
            Trace([(578, 668), (243, 668), (243, 588)], "flux", "réponse JSON aux clients", (400, 668)),   # 28/10
        ],
        bandeaux={"zc": NAVY, "za": "#1565C0", "zd": "#6D28D9"},
        formes={"web": ("boite", "ecran"), "mcp": ("boite", "prise"), "dep": ("boite", "coche"), "doc": ("boite", "terminal"),
                "main": ("code", ""), "cle": ("bouclier", "cle"), "routes": ("code", ""),
                "pg": ("cylindre", "elephant"), "contrat": ("fichier", "accolades"), "tests": ("fichier", "eprouvette")},
        legende="Génération : docs/rapports/E1/schemas/generer_schemas.py, vérifiée par tests/test_schemas_e1.py.",
        cles_boites={"normal": "client du jeu de données", "lavis": "code de l'API", "garde": "contrôle d'accès",
                     "stock": "données et contrat", "note": "preuve"},
        cles_fleches={"flux": "appel HTTP ou contrôle", "lecture": "lecture seule"},
    )


# =============================================================================
# La mise en forme illustrée (27/10/2026) : celle de la collecte, produite par le générateur
# =============================================================================
# Même toile que la page fournie par Era pour la collecte (1920 px de large, soit 1,28 fois le schéma généré),
# mêmes formes (base de données en cylindre, fenêtre de code, fichier à coin plié, bouclier du contrôle), mêmes
# couleurs. Les positions sont celles du schéma généré, multipliées par K : une boîte déplacée là-bas l'est ici.
K = 1.28
# (trait, fond, couleur du titre) de chaque rôle, repris de la page de la collecte.
ROLES_ILLUSTRE = {"normal": ("#1f2a44", "#ffffff", "#0f1f3d"), "lavis": ("#1565c0", "#e6f0fc", "#0d3c78"),
                  "garde": ("#c2410c", "#fff1e6", "#9a3412"), "stock": ("#6d28d9", "#f1eafe", "#5b21b6"),
                  "manque": ("#d32f2f", "#fdecec", "#991b1b"), "note": ("#5b6b82", "#eef2f7", "#0f1f3d")}
ICONES = {   # dessins de 48 × 48 ; les huit premiers sont ceux de la page de la collecte
    "banque": '<path d="M4,16 L24,6 L44,16 Z" fill="#1f2a44"/><rect x="6" y="38" width="36" height="5" fill="#1f2a44"/><rect x="9" y="19" width="5" height="17" fill="#1f2a44"/><rect x="17" y="19" width="5" height="17" fill="#1f2a44"/><rect x="26" y="19" width="5" height="17" fill="#1f2a44"/><rect x="34" y="19" width="5" height="17" fill="#1f2a44"/>',
    "globe": '<circle cx="24" cy="24" r="17" fill="none" stroke="#1f2a44" stroke-width="3"/><ellipse cx="24" cy="24" rx="7" ry="17" fill="none" stroke="#1f2a44" stroke-width="2.5"/><path d="M7,24 H41 M10,15 H38 M10,33 H38" stroke="#1f2a44" stroke-width="2"/>',
    "tableur": '<path d="M10,4 H30 L40,14 V44 H10 Z" fill="#fff" stroke="#1f2a44" stroke-width="2.5"/><path d="M15,22 H35 M15,29 H35 M15,36 H35 M22,18 V40 M29,18 V40" stroke="#15803d" stroke-width="2"/>',
    "parquet": '<ellipse cx="24" cy="38" rx="16" ry="5" fill="#fde68a" stroke="#1f2a44" stroke-width="2"/><ellipse cx="24" cy="28" rx="16" ry="5" fill="#fde68a" stroke="#1f2a44" stroke-width="2"/><ellipse cx="24" cy="18" rx="16" ry="5" fill="#fde68a" stroke="#1f2a44" stroke-width="2"/><path d="M36,2 L39,9 L46,10 L40,14 L42,21 L36,17 L30,21 L32,14 L26,10 L33,9 Z" fill="#f97316"/>',
    "elephant": '<circle cx="24" cy="20" r="14" fill="#336791"/><ellipse cx="12" cy="20" rx="8" ry="11" fill="#5b8fbf"/><path d="M30,28 Q34,40 28,45 Q25,46 26,42 Q29,36 24,30 Z" fill="#336791"/><circle cx="29" cy="16" r="2.3" fill="#fff"/>',
    "oeil": '<path d="M3,24 Q24,4 45,24 Q24,44 3,24 Z" fill="#fff" stroke="#1f2a44" stroke-width="3"/><circle cx="24" cy="24" r="7" fill="#1f2a44"/>',
    "cadenas": '<path d="M15,22 V15 A9,9 0 0 1 33,15 V22" fill="none" stroke="#a21caf" stroke-width="4"/><rect x="10" y="21" width="28" height="22" rx="4" fill="#a21caf"/><circle cx="24" cy="31" r="3.5" fill="#fff"/>',
    "code": '<path d="M15,14 L5,24 L15,34 M33,14 L43,24 L33,34 M28,10 L20,38" fill="none" stroke="#1565c0" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>',
    "alerte": '<path d="M24,5 L44,41 H4 Z" fill="#f59e0b" stroke="#1f2a44" stroke-width="2.5" stroke-linejoin="round"/><path d="M24,18 V29" stroke="#1f2a44" stroke-width="4" stroke-linecap="round"/><circle cx="24" cy="35" r="2.6" fill="#1f2a44"/>',
    "coche": '<circle cx="24" cy="24" r="19" fill="#15803d"/><path d="M14,24 L21,31 L34,17" fill="none" stroke="#fff" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>',
    "drapeau": '<path d="M10,44 V6" stroke="#991b1b" stroke-width="3.5" stroke-linecap="round"/><path d="M11,7 H38 L32,15 L38,23 H11 Z" fill="#d32f2f"/>',
    "document": '<path d="M12,4 H30 L40,14 V44 H12 Z" fill="#fff" stroke="#1f2a44" stroke-width="2.5"/><path d="M30,4 V14 H40" fill="none" stroke="#1f2a44" stroke-width="2.5"/><path d="M17,22 H35 M17,29 H35 M17,36 H29" stroke="#475569" stroke-width="2.5" stroke-linecap="round"/>',
    "barres": '<path d="M4,44 H44" stroke="#1f2a44" stroke-width="2.5"/><rect x="7" y="30" width="6" height="13" fill="#94a3b8"/><rect x="15" y="12" width="6" height="31" fill="#94a3b8"/><rect x="23" y="12" width="6" height="31" fill="#1565c0"/><rect x="31" y="12" width="6" height="31" fill="#94a3b8"/><rect x="39" y="24" width="5" height="19" fill="#94a3b8"/>',
    "liste": '<rect x="6" y="6" width="36" height="36" rx="6" fill="#fff" stroke="#1f2a44" stroke-width="2.5"/><path d="M14,17 H34 M14,24 H34 M14,31 H26" stroke="#1565c0" stroke-width="3" stroke-linecap="round"/>',
    "chrono": '<circle cx="24" cy="27" r="16" fill="#fff" stroke="#1f2a44" stroke-width="3"/><path d="M24,27 V17 M24,27 L31,31" stroke="#c2410c" stroke-width="3" stroke-linecap="round"/><rect x="19" y="4" width="10" height="5" rx="2" fill="#1f2a44"/>',
    "entonnoir": '<path d="M5,7 H43 L28,25 V40 L20,44 V25 Z" fill="#1565c0" stroke="#0d3c78" stroke-width="2" stroke-linejoin="round"/>',
    "balance": '<path d="M24,6 V42 M12,42 H36 M8,14 H40" stroke="#1f2a44" stroke-width="3" stroke-linecap="round"/><path d="M8,14 L3,27 H13 Z M40,14 L35,27 H45 Z" fill="#6d28d9" stroke="#1f2a44" stroke-width="1.5"/>',
    "ecran": '<rect x="4" y="6" width="40" height="28" rx="3" fill="#fff" stroke="#1f2a44" stroke-width="3"/><path d="M18,42 H30 M24,34 V42" stroke="#1f2a44" stroke-width="3" stroke-linecap="round"/><path d="M10,14 H30 M10,20 H38 M10,26 H24" stroke="#15803d" stroke-width="2.5" stroke-linecap="round"/>',
    "prise": '<path d="M16,4 V14 M32,4 V14" stroke="#1f2a44" stroke-width="3.5" stroke-linecap="round"/><path d="M9,14 H39 V22 Q39,34 24,34 Q9,34 9,22 Z" fill="#fff" stroke="#1f2a44" stroke-width="3"/><path d="M24,34 V44" stroke="#1f2a44" stroke-width="3.5" stroke-linecap="round"/>',
    "terminal": '<rect x="3" y="7" width="42" height="34" rx="5" fill="#0f172a"/><path d="M11,17 L18,24 L11,31" fill="none" stroke="#22c55e" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M22,32 H34" stroke="#e2e8f0" stroke-width="3.5" stroke-linecap="round"/>',
    "accolades": '<path d="M18,6 Q10,6 10,14 V20 Q10,24 5,24 Q10,24 10,28 V34 Q10,42 18,42 M30,6 Q38,6 38,14 V20 Q38,24 43,24 Q38,24 38,28 V34 Q38,42 30,42" fill="none" stroke="#6d28d9" stroke-width="3.5" stroke-linecap="round"/>',
    "cle": '<path d="M24,3 L42,10 V22 Q42,38 24,45 Q6,38 6,22 V10 Z" fill="#c2410c"/><circle cx="19" cy="22" r="5.5" fill="none" stroke="#fff" stroke-width="3"/><path d="M24,22 H35 M31,22 V28" stroke="#fff" stroke-width="3" stroke-linecap="round"/>',
    "eprouvette": '<path d="M18,4 H30 M20,4 V18 L8,40 Q6,44 11,44 H37 Q42,44 40,40 L28,18 V4" fill="#fff" stroke="#1f2a44" stroke-width="2.5" stroke-linejoin="round"/><path d="M13,32 H35 L39,40 Q40,42 37,42 H11 Q8,42 9,40 Z" fill="#15803d"/>',
}


def _px(v: float) -> int:
    return round(v * K)


def _forme(forme: str, w: int, h: int, trait: str, fond: str) -> tuple[str, tuple[int, int, int], tuple[int, int]]:
    """Le dessin de fond d'une boîte, la marge du texte (gauche, haut, droite) et la place de l'icône."""
    if forme == "cylindre":
        rx = (w - 3) / 2
        return (f'<path d="M1.5,10 L1.5,{h - 10} A{rx:g},10 0 0 0 {w - 1.5:g},{h - 10} L{w - 1.5:g},10" fill="{fond}" stroke="{trait}" stroke-width="2.5"/>'
                f'<ellipse cx="{w / 2:g}" cy="10" rx="{rx:g}" ry="8.5" fill="#fff" stroke="{trait}" stroke-width="2.5"/>'), (22, 24, 70), (w - 64, 22)
    if forme == "code":
        return (f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="10" fill="{fond}" stroke="{trait}" stroke-width="2.5"/>'
                f'<path d="M1.5,28 V11.5 A10,10 0 0 1 11.5,1.5 H{w - 11.5:g} A10,10 0 0 1 {w - 1.5:g},11.5 V28 Z" fill="{trait}"/>'
                + "".join(f'<circle cx="{x}" cy="14.5" r="4" fill="#fff" opacity=".8"/>' for x in (16, 30, 44))
                + f'<g transform="translate({w - 40},2) scale(.5)"><path d="M15,14 L5,24 L15,34 M33,14 L43,24 L33,34 M28,10 L20,38" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></g>'), (22, 34, 22), (0, 0)
    if forme == "fichier":
        return (f'<path d="M1.5,1.5 H{w - 22:g} L{w - 1.5:g},22 V{h - 1.5:g} H1.5 Z" fill="{fond}" stroke="{trait}" stroke-width="2.5"/>'
                f'<path d="M{w - 22:g},1.5 V22 H{w - 1.5:g}" fill="#dbe3ee" stroke="{trait}" stroke-width="2.5"/>'), (22, 12, 76), (w - 76, 26)
    if forme == "bouclier":
        return (f'<path d="M{w / 2:g},1.5 L{w - 1.5:g},14 V{h - 46:g} Q{w - 1.5:g},{h - 26:g} {w / 2:g},{h - 1.5:g} Q1.5,{h - 26:g} 1.5,{h - 46:g} V14 Z" fill="{fond}" stroke="{trait}" stroke-width="2.5"/>'), (34, 22, 80), (w - 76, 20)
    tirets = ' stroke-dasharray="9 6"' if trait == ROLES_ILLUSTRE["manque"][0] else ""
    return (f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="14" fill="{fond}" stroke="{trait}" stroke-width="2.5"{tirets}/>'), (22, 12, 70), (w - 64, 10)


def _icone(nom: str, taille: int = 48) -> str:
    return f'<svg width="{taille}" height="{taille}" viewBox="0 0 48 48" style="position:static">{ICONES[nom]}</svg>'


def illustre(s: SchemaPropre) -> str:
    """La page illustrée d'un schéma : mêmes textes que le .svg généré (contrôlé par tests/test_schemas_e1.py)."""
    e = html.escape
    W, H = 1920, _px(s.hauteur)
    out = ['<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>' + e(s.titre) + '</title><style>',
           f'@page{{size:{W}px {H}px;margin:0}}*{{box-sizing:border-box;margin:0}}',
           f"body{{width:{W}px;height:{H}px;position:relative;background:#fff;font-family:'Segoe UI','Noto Sans','DejaVu Sans',sans-serif;color:#1e293b;overflow:hidden}}",
           '.bar{position:absolute;left:0;top:0;width:1920px;height:10px;background:linear-gradient(90deg,#0f2d5c,#1565c0,#6d28d9,#a21caf)}',
           'h1{position:absolute;left:40px;top:28px;font-size:40px;font-weight:800;color:#0f2d5c}',
           '.st{position:absolute;left:42px;top:86px;font-size:19px;color:#475569}',
           '.col{position:absolute;border-radius:16px;background:#f8fafc;border:1.5px solid #e2e8f0}',
           '.hd{position:absolute;height:44px;border-radius:10px;color:#fff;font-weight:800;font-size:18px;letter-spacing:.5px;display:flex;align-items:center;padding-left:18px}',
           'svg{position:absolute;left:0;top:0}',
           '.pill{position:absolute;transform:translate(-50%,-50%);background:#fff;border:2px solid;border-radius:999px;padding:3px 12px;font-size:14.5px;font-weight:800;white-space:nowrap}',
           '.cov{position:absolute;border-radius:12px;background:#ecfdf5;border:2px solid #15803d;border-left-width:9px;padding:10px 18px}',
           '.cov b{font-size:18px;color:#14532d}.cov div{font-size:15px;margin-top:4px}',
           '.leg{position:absolute;left:40px;display:flex;align-items:center;gap:20px;font-size:15px;flex-wrap:nowrap}',
           '.leg span{display:flex;align-items:center;gap:7px;white-space:nowrap}',
           '.ft{position:absolute;left:40px;font-size:13.5px;color:#64748b}',
           '.n{position:absolute}.n svg{position:absolute;left:0;top:0;overflow:visible}.n .t{position:absolute}'
           '.n b{display:block;font-size:17.5px;font-weight:800;margin-bottom:5px}.n .t div{font-size:15px;line-height:1.45}'
           '</style></head><body><div class="bar"></div>',
           f'<h1>{e(s.titre)}</h1>', f'<div class="st">{e(s.sous_titre)}</div>']
    for b in s.boites:
        if b.genre == "zone":
            x, y, w, h = _px(b.x), _px(b.y), _px(b.w), _px(b.h)
            out.append(f'<div class="col" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"></div>'
                       f'<div class="hd" style="left:{x + 10}px;top:{y + 10}px;width:{w - 20}px;background:{s.bandeaux[b.id]}">{e(b.titre)}</div>')
    icone_du_role: dict[str, str] = {}
    for b in s.boites:
        if b.genre == "zone":
            continue
        x, y, w, h = _px(b.x), _px(b.y), _px(b.w), _px(b.h)
        titre = e(" ".join(b.titre.split("\n")))
        lignes = "".join(f"<div>{e(ligne.strip())}</div>" for ligne in b.lignes)
        if b.genre == "neuf":
            out.append(f'<div class="cov" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><b>{titre}</b>{lignes}</div>')
            continue
        forme, icone = s.formes.get(b.id, ("boite", ""))
        trait, fond, couleur = ROLES_ILLUSTRE[b.genre]
        dessin, (gauche, haut, droite), (ix, iy) = _forme(forme, w, h, trait, fond)
        if icone:   # la légende montre l'icône d'une boîte du rôle ; celle de la fenêtre de code en dernier recours
            dessin += f'<g transform="translate({ix},{iy})">{ICONES[icone]}</g>'
            if icone_du_role.get(b.genre, "code") == "code":
                icone_du_role[b.genre] = icone
        elif forme == "code":
            icone_du_role.setdefault(b.genre, "code")
        out.append(f'<div class="n" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><svg width="{w}" height="{h}">{dessin}</svg>'
                   f'<div class="t" style="left:{gauche}px;top:{haut}px;right:{droite if icone else 22}px"><b style="color:{couleur}">{titre}</b>{lignes}</div></div>')
    marqueurs = "".join(f'<marker id="m-{nom}" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
                        f'<path d="M0,0 L10,5 L0,10 z" fill="{couleur.lower()}"/></marker>' for nom, (couleur, _) in SENS.items())
    out.append(f'<svg width="{W}" height="{H}"><defs>{marqueurs}</defs>')
    for t in s.traces:
        couleur, dash = SENS[t.sens]
        d = "M" + " L".join(f"{_px(x)},{_px(y)}" for x, y in t.points)
        tirets = ' stroke-dasharray="10 7"' if dash else ""
        fin = f' marker-end="url(#m-{t.sens})"' if t.pointe else ""
        out.append(f'<path d="{d}" fill="none" stroke="{couleur.lower()}" stroke-width="3.5" stroke-linejoin="round"{tirets}{fin}/>')
    out.append("</svg>")
    for t in s.traces:
        if t.etiquette:
            couleur = SENS[t.sens][0].lower()
            out.append(f'<div class="pill" style="left:{_px(t.ou[0])}px;top:{_px(t.ou[1])}px;color:{couleur};border-color:{couleur}">{e(t.etiquette)}</div>')
    legende = [f'<div class="leg" style="top:{H - 74}px"><b style="color:#0f2d5c;font-size:16px">Légende</b>']
    for role, libelle in s.cles_boites.items():
        if role in icone_du_role:
            echantillon = _icone(icone_du_role[role], 30)
        else:
            trait, fond, _ = ROLES_ILLUSTRE[role]
            tirets = "dashed" if role == "manque" else "solid"
            echantillon = f'<span style="display:inline-block;width:28px;height:18px;border-radius:4px;border:2px {tirets} {trait};border-left-width:6px;background:{fond}"></span>'
        legende.append(f"<span>{echantillon}{e(libelle)}</span>")
    for sens, libelle in s.cles_fleches.items():
        couleur, dash = SENS[sens]
        couleur = couleur.lower()
        tirets = ' stroke-dasharray="7 5"' if dash else ""
        legende.append(f'<span><svg width="44" height="14" style="position:static"><line x1="2" y1="7" x2="32" y2="7" stroke="{couleur}" stroke-width="3.5"{tirets}/>'
                       f'<path d="M31,1 L43,7 L31,13z" fill="{couleur}"/></svg>{e(libelle)}</span>')
    out.append("\n".join(legende) + "</div>")
    # La source des chiffres, quand le pied du schéma généré en donne une, reste écrite (le nettoyage : ses dates).
    source = "" if s.legende.startswith("Génération :") else f"<span>{e(s.legende)}</span> "
    out.append(f'<div class="ft" style="top:{H - 33}px">{source}Mise en forme illustrée de {s.nom}.svg, produite par docs/rapports/E1/schemas/generer_schemas.py ; '
               f'mêmes textes, vérifiés par tests/test_schemas_e1.py.</div></body></html>')
    return "\n".join(out) + "\n"


SCHEMAS = {"E1-collecte": collecte, "E1-requetes": requetes, "E1-nettoyage": nettoyage, "E1-api": api}
ILLUSTRES_GENERES = ("E1-nettoyage", "E1-requetes", "E1-api")   # la collecte garde la page fournie par Era


def ecrire(nom: str) -> None:
    s = SCHEMAS[nom]()
    (ICI / f"{s.nom}.svg").write_text(svg(s), encoding="utf-8", newline="\n")
    (ICI / f"{s.nom}.drawio").write_text(drawio(s), encoding="utf-8", newline="\n")
    if nom in ILLUSTRES_GENERES:
        (ICI / f"{s.nom}-illustre.html").write_text(illustre(s), encoding="utf-8", newline="\n")
    print("écrit", s.nom, ".svg et .drawio" + (", et l'illustration" if nom in ILLUSTRES_GENERES else ""))


if __name__ == "__main__":
    for nom in SCHEMAS:
        ecrire(nom)
