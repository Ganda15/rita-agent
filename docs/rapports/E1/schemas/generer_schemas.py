"""Les deux schémas du rapport E1, générés depuis le code : collecte (C1) et nettoyage (C3).

Pourquoi un générateur (04/10/2026) : le schéma de collecte dessiné à la main le 11/08
(`evidence/C1/SCHEMA-C1-collecte-multisource.svg`, conservé comme preuve datée) affichait encore
« 9 motifs, 100 % blocage » et « 8 tables » deux mois plus tard. Ici, les chiffres qui bougent
avec le code sont lus dans le code au moment de la génération (`faits()`), et
`tests/test_schemas_e1.py` vérifie que les fichiers rangés sont exactement ceux qu'on obtiendrait
aujourd'hui. Les chiffres datés (analyse de juillet, comptages du 02/10) restent écrits avec leur date.

Le dessin (boîtes, flèches, .svg et .drawio) est celui des schémas E3 : même module, même charte.

Lancer :  C:\\Python314\\python.exe -X utf8 docs\\rapports\\E1\\schemas\\generer_schemas.py
Puis le rendu PNG (commande dans le README du dossier).
"""
from __future__ import annotations

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
Boite, Fleche, Schema, svg, drawio = _e3.Boite, _e3.Fleche, _e3.Schema, _e3.svg, _e3.drawio


def _lire(chemin: str) -> str:
    return (RACINE / chemin).read_text(encoding="utf-8")


def faits() -> dict:
    """Ce qui se lit dans le code au moment de la génération. Aucun accès réseau ni base."""
    from evals.mesurer_gardefou import mesurer
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
        "flux_generaux": len(FLUX),
        "etapes": re.findall(r'^\s*"(\w+)":', bloc_etapes, re.M),
        "devises": re.search(r"DEVISES_SUIVIES = \(([^)]*)\)", ingest).group(1).replace('"', "").replace(" ", ""),
        "traitements_rgpd": sorted(set(re.findall(r"\bT[1-9]\b", registre))),
        "procedures_rgpd": sorted(set(re.findall(r"\bP[1-9]\b", registre))),
    }


# =============================================================================
# Schéma 1 : C1, la collecte multi-source (cinq types exigés, et ce que RITA en fait)
# =============================================================================
def collecte() -> Schema:
    f = faits()
    t_premier, t_dernier = f["traitements_rgpd"][0], f["traitements_rgpd"][-1]
    p_premier, p_dernier = f["procedures_rgpd"][0], f["procedures_rgpd"][-1]
    return Schema(
        nom="E1-collecte", largeur=1500, hauteur=860,
        titre="RITA : la collecte multi-source, cinq types de sources sur cinq",
        sous_titre="Rapport E1, section 3 (C1) · chiffres du code lus à la génération, comptages datés · état au 4 octobre 2026",
        boites=[
            Boite("zs", 40, 90, 470, 640, "1. SOURCES, PAR TYPE EXIGÉ PAR C1", genre="zone"),
            Boite("bce", 56, 118, 438, 58, "SERVICE WEB · Banque centrale européenne", ["sources/ecb.py · taux de change contre l'euro :", f"{f['devises'].replace(',', ', ')} ; zéro taux reçu = étape en échec"], "normal"),
            Boite("fred", 56, 186, 438, 58, "SERVICE WEB · FRED (Réserve fédérale)", ["sources/fred.py · 3 séries macro américaines", "seule source à clé, jamais écrite dans un journal"], "normal"),
            Boite("yahoo", 56, 254, 438, 58, "SERVICE WEB · Yahoo Finance", ["sources/cotations.py · 111 valeurs, incrémental", "rejouable (ON CONFLICT DO UPDATE)"], "normal"),
            Boite("scrap", 56, 322, 438, 58, "PAGE WEB (scraping) · Boursorama", ["sources/scraper.py · robots.txt lu et mis en cache", "structure changée : exception StructurePageModifiee"], "normal"),
            Boite("rss", 56, 390, 438, 58, "COMPLÉMENT · flux RSS d'actualité", [f"sources/rss.py · {f['flux_generaux']} flux généraux + 1 flux Google News", "par valeur détenue (10 flux le 03/10)"], "note"),
            Boite("csv", 56, 470, 438, 58, "FICHIER · export courtier (CSV des positions)", ["sources/positions.py · « ; », cp1252, nombres à la française", "seule donnée personnelle du projet"], "normal"),
            Boite("parq", 56, 538, 438, 58, "SYSTÈME BIG DATA · Parquet + Spark", ["bigdata/ · dix ans de cotations, 11 partitions par année", "276 168 lignes ; requêtes Spark SQL (C2)"], "normal"),
            Boite("pgl", 56, 626, 438, 58, "BASE DE DONNÉES · PostgreSQL relu", ["sources/database.py · requêtes paramétrées", "lue par le nœud scout ; rôle rita_lecture (SELECT seul)"], "normal"),

            Boite("zo", 560, 90, 420, 640, "2. TRAITEMENTS", genre="zone"),
            Boite("ing", 576, 118, 388, 150, "pipelines/ingest.py : la collecte du soir", ["tâche planifiée Windows, chaque soir à 19 h", f"{len(f['etapes'])} étapes : {', '.join(f['etapes'])}", "une étape en échec n'arrête pas les suivantes", "un COMMIT par étape ; zéro ligne reçue = échec", "manifeste JSON par exécution (versions, comptages)", "40 journaux du 24/08 au 02/10, 33 à code 0"], "lavis"),
            Boite("gf", 576, 284, 388, 86, "Garde-fou d'injection (guardrails/injection.py)", [f"{f['motifs_injection']} motifs, appliqué aux articles RSS et scrapés", f"mesure du jour : {f['blocage_injection']} % de blocage, {f['faux_positifs_injection']} % de faux positifs", "article bloqué : marqué, conservé pour l'audit"], "lavis"),
            Boite("imp", 576, 470, 388, 126, "db/importer.py : l'import", ["archive Parquet : dédoublonnage (ticker, date),", "  alias de portefeuille résolus (voir C3)", "positions : réconciliation ; une ligne retirée", "  du fichier est close à la date du jour,", "  jamais supprimée"], "lavis"),
            Boite("lect", 576, 626, 388, 58, "Lecture, sans écriture", ["le scout lit la base pour chaque briefing ;", "Spark lit le Parquet sans passer par la base"], "normal"),

            Boite("zd", 1030, 90, 430, 640, "3. DESTINATION ET CONFORMITÉ", genre="zone"),
            Boite("pg", 1046, 118, 398, 120, "PostgreSQL 18 (Merise, C4)", [f"{f['tables']} tables, {f['vues']} vue, {f['check']} contraintes CHECK", "écrit par la collecte et l'import, seulement", "278 473 cotations (29/07/2016 au 02/10/2026)", "1 563 articles ; séries FRED stockées", "servi par l'API /donnees/* (C5)"], "stock"),
            Boite("chroma", 1046, 254, 398, 58, "Index ChromaDB (étape indexation)", ["articles vectorisés pour la recherche documentaire", "reconstruit après chaque collecte"], "stock"),
            Boite("rgpd", 1046, 470, 398, 126, "RGPD (registre art. 30, db/rgpd_purge.py)", [f"traitements {t_premier} à {t_dernier}, procédures de tri {p_premier} à {p_dernier}", "une seule table personnelle : position", "fichier source hors de Git, jamais envoyé au modèle", "purge en simulation par défaut ;", "lancement manuel, écrit comme tel"], "normal"),

            Boite("cov", 40, 750, 1420, 56, "Couverture de C1 : service web ✓ · page web ✓ · fichier ✓ · base de données ✓ · système big data ✓",
                  ["Cinq types sur cinq, plus le RSS en complément. Une preuve par source dans evidence/C1/ ; la figure du 11/08 qui s'y trouve est une preuve datée : ses chiffres de tables et de garde-fou ne sont plus à jour."], "note"),
        ],
        fleches=[
            Fleche("bce", "ing", sortie="d", entree="g:0.15"),
            Fleche("fred", "ing", sortie="d", entree="g:0.4"),
            Fleche("yahoo", "ing", sortie="d", entree="g:0.65"),
            Fleche("scrap", "gf", sortie="d", entree="g:0.4"),
            Fleche("rss", "gf", sortie="d", entree="g:0.75"),
            Fleche("csv", "imp", sortie="d", entree="g:0.3"),
            Fleche("parq", "imp", sortie="d", entree="g:0.75"),
            Fleche("ing", "pg", "écrit", sortie="d:0.3", entree="g:0.3"),
            Fleche("gf", "pg", "articles admis", sortie="d:0.5", entree="g:0.8"),
            Fleche("imp", "pg", "insère", sortie="d:0.2", entree="g:0.95"),
            Fleche("ing", "chroma", sortie="d:0.85", entree="g:0.5"),
            Fleche("imp", "rgpd", "positions", sortie="d:0.6", entree="g:0.6", pointille=True),
            Fleche("pgl", "lect", sortie="d", entree="g"),
        ],
        legende="Bleu clair : code qui écrit en base. Gris : réserves de données. Blanc : source ou lecture. Génération : docs/rapports/E1/schemas/generer_schemas.py, vérifiée par tests/test_schemas_e1.py.",
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

            Boite("zr", 40, 230, 1420, 400, "DÉFAUT MESURÉ  →  DÉCISION  →  FICHIER QUI L'APPLIQUE", genre="zone"),
            Boite("d1", 56, 258, 440, 58, "5 120 lignes en double (2 560 paires), surtout VIRI.PA", ["sans règle : l'import échoue sur la clé primaire"], "normal"),
            Boite("r1", 520, 258, 520, 58, "Dédoublonnage sur (ticker, date_seance) avant insertion", ["la collecte du soir est rejouable : ON CONFLICT DO UPDATE"], "lavis"),
            Boite("f1", 1064, 258, 380, 58, "db/importer.py", ["preuve : evidence/C3/preuve-dedoublonnage-cgg.md"], "note"),

            Boite("d2", 56, 330, 440, 58, "1 533 clôtures hors de [bas, haut], dont 1 142 STLAP.PA", ["sans règle : des variations aberrantes au briefing"], "normal"),
            Boite("r2", 520, 330, 520, 58, "STLAP.PA marquée INCOHERENT : exclue des requêtes, gardée", ["aucune contrainte ne borne la clôture (db/schema.sql refuse haut < bas) :", "23 lignes hors bornes en base le 04/10, limite déclarée"], "manque"),
            Boite("f2", 1064, 330, 380, 58, "db/importer.py (QUALITE), sources/database.py", ["les requêtes ne lisent que statut_qualite = 'OK'"], "note"),

            Boite("d3", 56, 402, 440, 58, "Cours maximal 7 156 748 (ALJXR.PA)", ["regroupement d'actions rétro-ajusté (prix ÷ 36 millions)"], "normal"),
            Boite("r3", 520, 402, 520, 58, "Marquée INCOHERENT, conservée, mécanisme identifié", ["la table operation_sur_titre est conçue, pas construite"], "manque"),
            Boite("f3", 1064, 402, 380, 58, "evidence/C3/preuve-artefact-reverse-split.md", ["statut_qualite : exclure sans supprimer"], "note"),

            Boite("d4", 56, 474, 440, 58, "Libellés du portefeuille différents des tickers", ["« CGG BS », « CGG RGPT » : aucune position rattachée"], "normal"),
            Boite("r4", 520, 474, 520, 58, "Entité ALIAS au modèle : une valeur, plusieurs noms", ["112 alias pour 111 valeurs"], "lavis"),
            Boite("f4", 1064, 474, 380, 58, "db/importer.py, table alias_valeur", ["cardinalité VALEUR 1,n / ALIAS 1,1 (Merise, C4)"], "note"),

            Boite("d5", 56, 546, 440, 70, "INC-005 (27/09) : 52 426 cotations un dimanche", ["date UTC d'un « minuit à Paris » = la veille à 22 h ;", "même cause : pence de Londres, dollars, samedi, fériés"], "normal"),
            Boite("r5", 520, 546, 520, 70, "La place de cotation entre dans le modèle", ["fuseau, devise et unité de prix par place, fériés Euronext ;", "correctif en une transaction, 42 tests écrits d'abord"], "lavis"),
            Boite("f5", 1064, 546, 380, 70, "sources/marches.py, sources/cotations.py", ["leçon : compter aussi par jour de la semaine"], "note"),

            Boite("pos", 40, 650, 700, 96, "Le fichier des positions (export courtier)", ["sources/positions.py : séparateur « ; », encodage cp1252 détecté,", "« 632,40 » et « 1 250 » (espace insécable) convertis, en-têtes variables ;", "chaque ligne invalide est rejetée avec sa cause, jamais ignorée en silence"], "normal"),
            Boite("vol", 760, 650, 700, 96, "Ce qui reste visible plutôt que corrigé", ["2 802 séances à volume nul conservées : la requête des volumes anormaux", "  (R3, db/requetes.sql) exige une moyenne sur 20 séances > 0, sinon division par zéro ;", "les valeurs douteuses portent un statut_qualite au lieu d'être supprimées"], "normal"),
        ],
        fleches=[
            Fleche("brut", "eda"), Fleche("eda", "agr"), Fleche("agr", "res"),
            Fleche("d1", "r1"), Fleche("r1", "f1"),
            Fleche("d2", "r2"), Fleche("r2", "f2"),
            Fleche("d3", "r3"), Fleche("r3", "f3"),
            Fleche("d4", "r4"), Fleche("r4", "f4"),
            Fleche("d5", "r5"), Fleche("r5", "f5"),
        ],
        legende="Blanc : défaut mesuré. Bleu clair : décision appliquée. Pointillé orange : limite déclarée, ou décision conçue non construite. Gris : fichier ou preuve à ouvrir. Chiffres de juillet et du 02/10 : rapport E1, section 4.",
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
