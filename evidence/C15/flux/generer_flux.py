"""Le diagramme de flux de données de RITA, nouvelle version relevée le 02/11/2026 (C15.3).

Pourquoi : le diagramme du 18/08 (`evidence/C15/FLUX-DONNEES-C15-application-RITA.png`, gardé tel quel) ne montre ni
Question, ni l'index des articles, ni la passerelle MCP, ni la vigie, ni Langfuse. Celui-ci est **relevé sur le code**
du commit `dd3c065`, flux par flux (preuve : `evidence/C15/preuve-flux-donnees-2026-11-02.md`). Comme en août, le sens
des flèches est celui de la donnée, pas celui de la requête.

Le dessin réutilise le moteur des schémas d'E3, comme les schémas d'E2 et les parcours de C14.
Le `.png` se rend depuis le `.svg` par Chrome sans fenêtre (README du dossier).

Lancer :  C:\\Python314\\python.exe -X utf8 evidence\\C15\\flux\\generer_flux.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ICI = Path(__file__).parent
_E3 = ICI.parent.parent.parent / "docs" / "rapports" / "E3" / "schemas" / "generer_schemas.py"
_spec = importlib.util.spec_from_file_location("schemas_e3_moteur_c15", _E3)
moteur = importlib.util.module_from_spec(_spec)
sys.modules["schemas_e3_moteur_c15"] = moteur   # dataclass relit son module dans sys.modules
_spec.loader.exec_module(moteur)

Schema, Boite, Fleche = moteur.Schema, moteur.Boite, moteur.Fleche

# Cinq colonnes de 292 px, dans le sens de la donnée ; chaque flèche passe dans l'espace entre deux colonnes. L'espace
# entre l'API et ses destinataires est plus large : onze flux s'y croisent.
X = (40, 352, 664, 976, 1418)
Y = (134, 244, 354, 464, 574)
L, H = 268, 100


def zone(id_, col, titre):
    return Boite(id_, X[col], 100, 292, 590, titre, genre="zone")


def boite(id_, col, rang, titre, lignes, genre="normal"):
    return Boite(id_, X[col] + 12, Y[rang], L, H, titre, lignes, genre)


FLUX = Schema(
    nom="FLUX-DONNEES-C15-application-RITA-2026-11-02", largeur=1750, hauteur=830,
    titre="Les flux de données de RITA, version du 02/11/2026",
    sous_titre="Diagramme de flux de données relevé sur le code (commit dd3c065) ; la flèche suit la donnée, pas la requête",
    boites=[
        zone("za", 0, "SOURCES EXTERNES"),
        boite("cours", 0, 0, "Cours de bourse", ["Yahoo Finance (yfinance) ;", "Boursorama (scraping)"]),
        boite("macro", 0, 1, "Taux et séries macro", ["BCE : taux de change ;", "FRED : séries américaines"]),
        boite("presse", 0, 2, "Presse", ["flux RSS d'éditeurs", "(sources/rss.py)"]),
        boite("positions", 0, 3, "Fichier de positions", ["CSV du poste, jamais dans", "Git : donnée personnelle"]),

        zone("zb", 1, "COLLECTE"),
        boite("injection", 1, 2, "Garde-fou d'injection", ["à la collecte des articles,", "puis de nouveau avant", "le modèle"], "garde"),
        boite("ingest", 1, 0, "pipelines/ingest.py", ["six étapes ; poste : chaque", "soir ; production : à la", "demande (workflow)"], "lavis"),
        boite("importer", 1, 3, "db/importer.py", ["univers, alias, archive", "Parquet, positions"], "lavis"),

        zone("zc", 2, "STOCKAGE"),
        boite("pg", 2, 0, "PostgreSQL", ["10 tables, 1 vue, dont les", "positions (T1) et le journal", "des appels MCP"], "stock"),
        boite("index", 2, 2, "Index des articles", ["ChromaDB : passages", "vectorisés, un par version"], "stock"),
        boite("journaux", 2, 4, "Journaux", ["collecte ; une ligne par", "question, sans son texte"], "stock"),

        zone("zd", 3, "API (CLÉ X-API-KEY)"),
        boite("donnees", 3, 0, "GET /donnees/*", ["12 chemins, lecture seule ;", "dont portefeuille et fiche", "d'un article"], "lavis"),
        boite("briefing", 3, 1, "POST /briefing", ["base, articles, rédacteur ;", "garde-fou de sortie"], "lavis"),
        boite("question", 3, 2, "POST /question", ["garde-fous, recherche,", "contrôles ; références", "lues dans la base"], "lavis"),
        boite("sante", 3, 3, "GET /sante et /health", ["compteurs de l'API,", "verdicts contre les seuils"], "lavis"),

        zone("ze", 4, "DESTINATAIRES"),
        boite("ecrans", 4, 1, "Navigateur : cinq écrans", ["envoie clé et questions ;", "reçoit données, réponses", "et état du service"]),
        boite("mcp", 4, 0, "Passerelle MCP", ["trois outils en lecture ;", "portefeuille : jeu de", "démonstration seulement"]),
        boite("modele", 4, 2, "Modèle fourni, zone UE", ["Azure AI Foundry : reçoit", "faits de marché, passages,", "question ; rend le texte"], "stock"),
        boite("langfuse", 4, 3, "Langfuse, région UE", ["métadonnées seulement :", "jamais prompt ni texte"], "stock"),
        boite("github", 4, 4, "Vigie, puis GitHub", ["une issue par signal en", "problème ; alerte Langfuse", "aussi"]),

        Boite("releve", 40, 710, 1670, 76, "Nouvelle version, l'ancienne du 18/08 est gardée",
              ["Relevé le 02/11/2026 sur sources/, pipelines/, db/, api/, graph/, agents/, guardrails/, src/traces.py, monitorage/, passerelle_mcp/, frontend/.",
               "Le sens des flèches est le sens de la donnée. Ancienne version : evidence/C15/FLUX-DONNEES-C15-application-RITA.png (18/08)."],
              "note"),
    ],
    fleches=[
        Fleche("cours", "ingest", sortie="d", entree="g"),
        Fleche("macro", "ingest", sortie="d", entree="g:0.8"),
        Fleche("presse", "injection", sortie="d", entree="g", etiquette="articles", pos=0.5),
        Fleche("injection", "ingest", sortie="h", entree="b"),
        Fleche("positions", "importer", sortie="d", entree="g", sens="perso"),
        Fleche("ingest", "pg", sortie="d", entree="g", sens="ecriture"),
        Fleche("ingest", "index", sortie="d:0.85", entree="g:0.2", sens="ecriture"),
        Fleche("ingest", "journaux", sortie="d:0.95", entree="g:0.3", sens="ecriture"),
        Fleche("importer", "pg", sortie="d:0.2", entree="g:0.85", sens="perso"),
        Fleche("pg", "donnees", sortie="d", entree="g", sens="perso"),
        Fleche("pg", "briefing", sortie="d:0.8", entree="g:0.3", sens="lecture"),
        Fleche("index", "briefing", sortie="d:0.2", entree="g:0.8", sens="lecture"),
        Fleche("index", "question", sortie="d", entree="g", sens="lecture"),
        Fleche("donnees", "ecrans", sortie="d:0.8", entree="g:0.15", sens="perso"),
        Fleche("donnees", "mcp", sortie="d:0.4", entree="g:0.4"),
        Fleche("ecrans", "question", sortie="g:0.8", entree="d:0.2"),
        Fleche("question", "ecrans", sortie="d:0.05", entree="g:0.95"),
        Fleche("briefing", "ecrans", sortie="d:0.45", entree="g:0.45"),
        Fleche("sante", "ecrans", sortie="d:0.1", entree="g:0.65"),
        Fleche("briefing", "modele", sortie="d:0.6", entree="g:0.2"),
        Fleche("question", "modele", sortie="d", entree="g"),
        Fleche("question", "langfuse", sortie="d:0.85", entree="g:0.2"),
        Fleche("briefing", "langfuse", sortie="d:0.9", entree="g:0.5"),
        Fleche("question", "journaux", sortie="g:0.85", entree="d:0.2", sens="ecriture"),
        Fleche("sante", "github", sortie="d:0.8", entree="g:0.2"),
        Fleche("langfuse", "github", sortie="b", entree="h"),
    ],
    legende="Sources : le code au commit dd3c065, docs/ARCHITECTURE.md (01/11) ; détail flux par flux : evidence/C15/preuve-flux-donnees-2026-11-02.md.",
    cles_boites={"normal": "entité externe", "lavis": "traitement", "stock": "stockage ou service tiers",
                 "garde": "garde-fou", "note": "relevé"},
    cles_fleches={"flux": "donnée transmise", "ecriture": "écriture", "lecture": "lecture",
                  "perso": "donnée personnelle (positions)"},
)


def ecrire(s: Schema) -> None:
    (ICI / f"{s.nom}.svg").write_text(moteur.svg(s), encoding="utf-8", newline="\n")
    (ICI / f"{s.nom}.drawio").write_text(moteur.drawio(s), encoding="utf-8", newline="\n")
    print("écrit", s.nom, ".svg et .drawio ; rendu :", s.largeur, "x", s.hauteur_totale)


if __name__ == "__main__":
    trop = moteur.debordements(FLUX)
    if trop:
        raise SystemExit("Texte qui déborde, rien n'est écrit :\n" + "\n".join(trop))
    ecrire(FLUX)
