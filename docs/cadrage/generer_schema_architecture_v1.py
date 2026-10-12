"""Le schéma d'architecture complète de la V1 (sprint 1), généré avec la charte des schémas E3 : .drawio ET .svg.

Pourquoi un schéma de plus (12/10/2026). Le brief du sprint 1 demande de « produire le schéma d'architecture complète
(données → agent(s) + garde-fous → interface → API) », et le formateur a demandé la conception du fil rouge FINI.
`E3-architecture` montre l'état du code au 04/10 : il ne suit pas l'ordre du brief, montre encore la cascade de trois
fournisseurs (Azure seul depuis le 11/10) et ne montre rien des six jours de la V1. Ce schéma-ci montre le système une
fois la V1 faite : les quatre zones dans l'ordre du brief, et les ajouts de la V1 en pointillé rouge (jours 1 à 5).

La charte, les boîtes, les flèches et la légende viennent de `docs/rapports/E3/schemas/generer_schemas.py` : un seul
style pour tous les schémas du dépôt. Le `.png` est rendu depuis le `.svg` par Chrome sans fenêtre (commande dans
`README.md` de ce dossier).

Lancer, depuis la racine :  C:\\Python314\\python.exe -X utf8 docs\\cadrage\\generer_schema_architecture_v1.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ICI = Path(__file__).parent
sys.path.insert(0, str(ICI.parent / "rapports" / "E3" / "schemas"))

from generer_schemas import Boite, Fleche, Schema, drawio, svg  # noqa: E402  (la charte E3, réutilisée telle quelle)

ARCHI_V1 = Schema(
    nom="CADRAGE-architecture-v1", largeur=1500, hauteur=1060,
    titre="RITA : l'architecture complète de la V1, des données à l'API",
    sous_titre="Sprint 1, cadrage V1 · lecture : 1 données → 2 agent et garde-fous → 3 interface → 4 API, puis le pilotage autour",
    boites=[
        # 1 · Données : les sources, la collecte du soir, les deux réserves.
        Boite("z1", 40, 100, 480, 576, "1 · DONNÉES", genre="zone"),
        Boite("src", 56, 130, 448, 112, "Sources (C1), collectées chaque soir", [
            "services web : BCE (taux de change), FRED (taux US),",
            "  Yahoo Finance (cours) · page web : Boursorama",
            "flux RSS d'actualité · fichier : positions (CSV)",
            "big data : archive Parquet (Spark, hors image)"], "normal"),
        Boite("nuit", 56, 300, 220, 84, "Collecte du soir, 19 h", [
            "pipelines/ingest.py", "6 étapes indépendantes", "manifeste par exécution"], "normal"),
        Boite("pg", 316, 300, 188, 84, "PostgreSQL", [
            "10 tables, 1 vue", "cours, taux, articles,", "positions (RGPD)"], "stock"),
        Boite("inj", 56, 480, 220, 84, "Garde-fou d'injection", [
            "guardrails/injection.py", "relit chaque article", "bloqué : marqué, gardé"], "garde"),
        Boite("ch", 316, 480, 188, 84, "ChromaDB", [
            "articles découpés", "et vectorisés,", "reconstruit chaque soir"], "stock"),
        Boite("envoi", 56, 590, 448, 66, "Ce qui part chez le fournisseur du modèle", [
            "le prompt seul : cours, variation, indicateurs,",
            "au plus 3 extraits d'articles ; jamais une position"], "note"),

        # 2 · Agent et garde-fous : le graphe à arêtes fixes, du scout au garde-fou de sortie.
        Boite("z2", 560, 100, 340, 760, "2 · AGENT + GARDE-FOUS (LangGraph)", genre="zone"),
        Boite("fixe", 576, 130, 308, 84, "Un chemin fixe, toujours le même", [
            "graph/workflow.py : scout, rag, redacteur ;",
            "le modèle ne choisit jamais le chemin :",
            "chaque briefing se rejoue et se trace"], "note"),
        Boite("scout", 576, 300, 308, 84, "scout", [
            "lit PostgreSQL : cours, variation,", "13 indicateurs par valeur",
            "aucune position, aucun prix de revient"], "normal"),
        Boite("ge", 576, 404, 308, 56, "Garde-fou d'entrée (début de rag)", [
            "intention AMF refusée avant la recherche"], "garde"),
        Boite("rag", 576, 480, 308, 84, "rag", [
            "ChromaDB : filtre par valeur,", "recherche hybride dense + BM25",
            "3 passages ; refus si aucun article"], "normal"),
        Boite("red", 576, 584, 308, 66, "redacteur", [
            "agents/analyst.py : la consigne,", "interdit AMF écrit dedans"], "normal"),
        Boite("mod", 576, 670, 308, 66, "Modèle fourni : Azure, zone UE", [
            "src/llm.py ; gpt-5.4-dzs-eu", "LLM_ORDRE=foundry (11/10)"], "lavis"),
        Boite("gs", 576, 756, 308, 84, "Garde-fou de sortie", [
            "guardrails/sortie.py, échec fermé", "recommandation : texte remplacé",
            "par un refus, conforme_amf=false"], "garde"),

        # 3 · Interface : les deux clients.
        Boite("z3", 940, 100, 520, 134, "3 · INTERFACE", genre="zone"),
        Boite("web", 956, 130, 300, 84, "Interface web (frontend/)", [
            "3 écrans : portefeuille, indicateurs,", "  briefing ; clé saisie à l'écran",
            "verdict AMF écrit en mots"], "normal"),
        Boite("mcp", 1272, 130, 172, 84, "Passerelle MCP", [
            "3 outils en lecture", "seule, avec la clé", "aucun accès à /briefing"], "normal"),

        # 4 · API : les routes et la clé, les ajouts de la V1, le journal, la réponse.
        Boite("z4", 940, 260, 520, 600, "4 · API (FastAPI, api/main.py)", genre="zone"),
        Boite("routes", 956, 300, 488, 84, "Routes, clé, identifiant de requête", [
            "GET /health (public) · 11 routes GET /donnees/*",
            "POST /briefing?ticker= : le seul chemin vers le modèle",
            "clé X-API-Key 16 car. min. ; 403 ; X-Request-ID"], "lavis"),
        Boite("j1", 956, 404, 240, 56, "J1 · /health dit sa version", ["le manifeste de version servi"], "manque"),
        Boite("j3", 1204, 404, 240, 56, "J3 · valeur inconnue : 422", ["sans appel au modèle (502 auj.)"], "manque"),
        Boite("j4", 956, 476, 240, 56, "J4 · limite de débit", ["sur POST /briefing (429)"], "manque"),
        Boite("j5", 1204, 476, 240, 56, "J5 · refus de clé journalisé", ["une ligne avec son request_id"], "manque"),
        Boite("journal", 956, 560, 488, 84, "Journal de l'API", [
            "une ligne par briefing servi ou refusé,", "avec son request_id ; jamais le texte",
            "POST /audit/mcp : les refus de la passerelle MCP"], "normal"),
        Boite("rep", 956, 756, 488, 84, "Réponse JSON", [
            "ticker, prix, variation, briefing,", "conforme_amf, motifs_amf",
            "en-tête X-Request-ID sur chaque réponse"], "normal"),

        # Autour : le pilotage (détaillé dans E3-chaine-livraison et E3-monitorage).
        Boite("zp", 40, 880, 1420, 130, "AUTOUR : PILOTAGE ET SIGNAUX (détail : E3-chaine-livraison, E3-monitorage)", genre="zone"),
        Boite("ci", 56, 910, 380, 84, "GitHub Actions (CI/CD)", [
            "tests, garde-fous mesurés, image vérifiée",
            "main ne change que par une PR relue",
            "un livrable = un tag livrable-E<n>-v<k>"], "lavis"),
        Boite("lf", 456, 910, 400, 84, "Langfuse Cloud, région UE", [
            "une trace par briefing, même request_id",
            "étapes, durée, jetons, verdict AMF",
            "2 alertes → une issue « incident »"], "stock"),
        Boite("prod", 876, 910, 280, 84, "Production : Hetzner, Caddy", [
            "conteneur, déploiement manuel", "J1 : déployer le code du 15/10",
            "(sert le code du 19/08)"], "normal"),
        Boite("j2", 1176, 910, 268, 84, "J2 · retour arrière outillé", [
            "tag précédent, jamais reconstruit", "procédure dans EXPLOITATION.md",
            "critère 5 : N-1 en < 10 min"], "manque"),
    ],
    fleches=[
        # Données : sources → collecte → réserves ; les articles passent par le garde-fou d'injection.
        Fleche("src", "nuit", sortie="b:0.25", entree="h"),
        Fleche("nuit", "pg", sens="ecriture"),
        Fleche("nuit", "inj", "articles", sortie="b", entree="h"),
        Fleche("inj", "ch", sens="ecriture"),
        # Lecture des réserves par le graphe.
        Fleche("pg", "scout", sens="lecture"),
        Fleche("ch", "rag", sens="lecture"),
        # Le graphe, du haut vers le bas.
        Fleche("scout", "ge", sortie="b", entree="h"),
        Fleche("ge", "rag", sortie="b", entree="h"),
        Fleche("rag", "red", sortie="b", entree="h"),
        Fleche("red", "mod", sortie="b", entree="h"),
        Fleche("mod", "gs", sortie="b", entree="h"),
        # Interface → API → graphe, puis la réponse relue revient à l'API.
        Fleche("web", "routes", sortie="b", entree="h:0.31"),
        Fleche("mcp", "routes", sortie="b", entree="h:0.83"),
        Fleche("routes", "scout", sortie="g", entree="d"),
        Fleche("gs", "rep", sortie="d", entree="g"),
        # Chaque briefing laisse une trace.
        Fleche("gs", "lf", "trace", sortie="b", entree="h:0.685"),
    ],
    legende="Sprint 1, cadrage V1 · relu le 12/10/2026 contre api/main.py, api/donnees.py, src/llm.py, ARCHITECTURE.md et EXPLOITATION.md · "
            "pointillé rouge : construit pendant les six jours de la V1.",
    cles_boites={"normal": "composant présent", "lavis": "cœur du traitement", "garde": "garde-fou",
                 "stock": "réserve de données, service externe", "manque": "à construire dans la V1 (jour n)",
                 "note": "à retenir"},
    cles_fleches={"flux": "appel, passage", "ecriture": "écriture", "lecture": "lecture seule"},
)


if __name__ == "__main__":
    (ICI / f"{ARCHI_V1.nom}.svg").write_text(svg(ARCHI_V1), encoding="utf-8", newline="\n")
    (ICI / f"{ARCHI_V1.nom}.drawio").write_text(drawio(ARCHI_V1), encoding="utf-8", newline="\n")
    print("écrit", ARCHI_V1.nom, ".svg et .drawio ; taille de rendu :", f"{ARCHI_V1.largeur},{ARCHI_V1.hauteur_totale}")
