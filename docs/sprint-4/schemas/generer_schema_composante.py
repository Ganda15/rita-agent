"""Le schéma complet de la composante agentique du sprint 4 : les deux parcours, chaque garde-fou, et le code qui le fait.

Pourquoi ce schéma (21/10/2026). Aucun schéma du dépôt ne montre le sprint 4 : celui du sprint 1
(`docs/cadrage/CADRAGE-architecture-v1`) ne connaît que le briefing, et ceux du rapport E3 datent du 04/10. Celui-ci
sert à la fois de schéma et de carte du code pour l'oral de l'atelier 4 : chaque boîte donne son fichier, sa fonction et
sa ligne, le nombre de tests qui la tiennent, et le sprint où elle a été codée. Vert : codé au sprint 4 ; orange :
garde-fou déjà là ; [S1], [S3], [S4] : le sprint du code.

Les numéros de ligne sont ceux de la branche `sprint-4-agentique-garde-fous` au 21/10/2026.

La charte, les boîtes, les flèches et la légende viennent de `docs/rapports/E3/schemas/generer_schemas.py`. Le `.png`
est rendu depuis le `.svg` par Chrome sans fenêtre (commande dans `README.md` de ce dossier).

Lancer, depuis la racine :  C:/Python314/python.exe -X utf8 docs/sprint-4/schemas/generer_schema_composante.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ICI = Path(__file__).parent
sys.path.insert(0, str(ICI.parent.parent / "rapports" / "E3" / "schemas"))

from generer_schemas import Boite, Fleche, Schema, drawio, svg  # noqa: E402  (la charte du dépôt, réutilisée telle quelle)

# Les colonnes : le bandeau du haut (6 boîtes), puis A (questions), B (briefing), C (trace et mesure).
HX = [56, 372, 688, 1004, 1320, 1636]
HW = 300
AX, AW = 56, 868
BX, BW = 976, 468
CX, CW = 1496, 448

COMPOSANTE = Schema(
    nom="SPRINT4-composante-garde-fous", largeur=2000, hauteur=1290,
    titre="RITA, sprint 4 : la composante agentique, ses garde-fous, et le code qui les fait",
    sous_titre="Chaque boîte : son fichier, sa fonction, sa ligne et ses tests · vert : codé au sprint 4 · orange : "
               "garde-fou déjà là · [S1] [S3] [S4] : le sprint où c'est codé",
    boites=[
        # 0 · Les écrans et l'API : par où entrent une question et un briefing.
        Boite("z0", 40, 100, 1920, 160, "0 · LES ÉCRANS ET L'API : PAR OÙ TOUT ENTRE (frontend/, api/)", genre="zone"),
        Boite("e1", HX[0], 130, HW, 102, "Écran des questions [S3]", [
            "frontend/question.html, question.js",
            "MOTIFS l.18 : le motif dit en mots [S4]",
            "afficherRefus l.180 : « Pas de réponse »",
            "clé dans un champ masqué"], "normal"),
        Boite("rq", HX[1], 130, HW, 102, "Route POST /question [S3]", [
            "api/question.py : poser_question l.37",
            "appelle agents/question.py repondre",
            "journal « question servie » l.59",
            "3 à 500 caractères"], "normal"),
        Boite("k", HX[2], 130, HW, 102, "Clé [S1], refus journalisé [S4]", [
            "api/main.py : verify_api_key l.162",
            "403 + ligne « cle d'API refusee » l.178",
            "jamais la clé, ni un morceau",
            "tests/test_refus_cle_journal.py (5)"], "neuf"),
        Boite("lim", HX[3], 130, HW, 102, "Limite de débit [S4]", [
            "api/limiteur.py : LIMITEUR l.58",
            "limiter_debit l.61 : 10 appels/min,",
            "partagés par les deux routes ; 429",
            "tests/test_limiteur.py (7)"], "neuf"),
        Boite("rb", HX[4], 130, HW, 102, "Route POST /briefing [S1], 422 [S4]", [
            "api/main.py : briefing l.245",
            "valeur_existe l.257 (indicateurs/socle.py",
            "l.150) : inconnue → 422, sans modèle",
            "tests/test_briefing_422.py (5)"], "neuf"),
        Boite("e2", HX[5], 130, HW, 102, "Écran du briefing [S1]", [
            "frontend/briefing.html, briefing.js",
            "un code de valeur (ticker), pas de texte",
            "422 → « Valeur introuvable » [S4]",
            "clé dans un champ masqué"], "normal"),

        # A · Le parcours des questions, entré dans la composante par l'avenant n°1.
        Boite("za", 40, 280, 900, 980, "A · LES QUESTIONS (avenant n°1) : agents/question.py repondre l.237 orchestre tout",
              genre="zone"),
        Boite("a1", AX, 310, AW, 84, "1. Garde-fou de détournement [S4] : injection, changement de rôle, extraction", [
            "guardrails/detournement.py : MOTIFS_DETOURNEMENT l.32 (règles par famille), verifier_detournement l.69",
            "appelé dans rag/recherche.py l.229, avant tout ; reconnu → refus TENTATIVE_DETOURNEMENT, sans modèle",
            "tests/test_garde_fou_question.py (38) · mesuré : 7 hostiles sur 8 avant le modèle ; 0 reformulation sur 8"], "neuf"),
        Boite("a2", AX, 408, AW, 66, "2. Garde-fou d'intention [S1] : le conseil d'achat ou de vente", [
            "guardrails/entree.py : MOTIFS_INTENTION_AMF l.33, verifier_intention l.54",
            "appelé dans rag/recherche.py l.236 ; reconnu → refus INTENTION_INTERDITE"], "garde"),
        Boite("a3", AX, 488, AW, 66, "3. Recherche dans les articles [S3] : le hors-périmètre", [
            "rag/recherche.py : rechercher l.194 ; par le sens et par les mots, 3 passages ; seuil 0.42 l.114",
            "aucun passage assez proche → refus OUT_OF_CORPUS, sans appeler le modèle"], "normal"),
        Boite("a4", AX, 568, AW, 66, "4. Articles piégés écartés [S4] : l'injection indirecte", [
            "agents/question.py : passages_surs l.219 → guardrails/injection.py neutraliser l.46 (12 motifs, l.18)",
            "passage reconnu → écarté avant le prompt, journal sans son texte · tests/test_article_piege.py (7)"], "neuf"),
        Boite("a5", AX, 648, AW, 66, "5. Le prompt [S3] : la question est une donnée, jamais une consigne", [
            "agents/question.py : construire_prompt l.106, CONSIGNES l.70, _neutraliser l.91",
            "question et passages dans des blocs déclarés comme données ; espaces Unicode ramenées à une seule"], "normal"),
        Boite("a6", AX, 728, AW, 66, "6. Le modèle [S3] : Azure, zone de données de l'UE, seul fournisseur", [
            "src/llm.py : generer_json l.137 ; réponse au format JSON imposé ; il peut s'abstenir (ABSTENTION)",
            "trace : src/traces.py question l.330, métadonnées seules"], "lavis"),
        Boite("a7", AX, 808, AW, 56, "7. Citations vérifiées [S3]", [
            "agents/question.py : citations_valides l.55 ; un numéro inventé → refus CITATIONS_INVALIDES"], "normal"),
        Boite("a8", AX, 878, AW, 66, "8. Contrôle de fuite [S4] : clé, jeton, mot de passe, configuration, consignes", [
            "agents/question.py l.279 → guardrails/sortie.py verifier_fuite l.107, MOTIFS_FUITE l.81 ; FUITE_BLOQUEE",
            "tests/test_garde_fou_fuite.py (9) · mesuré : 5 sorties dangereuses simulées sur 7, 0 faux positif sur 11"], "neuf"),
        Boite("a9", AX, 958, AW, 66, "9. Garde-fou AMF [S1] : le conseil d'achat dans la réponse", [
            "agents/question.py l.284 → guardrails/sortie.py verifier_sortie l.53, MOTIFS_AMF l.28",
            "reconnu → refus SORTIE_NON_CONFORME"], "garde"),
        Boite("a10", AX, 1038, AW, 66, "10. Contrôle des nombres [S4] : un chiffre faux sous une source juste", [
            "agents/question.py l.297 → guardrails/nombres.py nombres_absents l.68 ; absent des sources → NOMBRE_NON_SOURCE",
            "tests/test_controle_nombres.py (46) · né du « 1 0 postes » du 20/10 ; ne lit pas les nombres en lettres"], "neuf"),
        Boite("a11", AX, 1118, AW, 66, "11. La réponse citée [S3]", [
            "agents/question.py : _reference l.214 ; chaque référence vient du passage, jamais du texte du modèle",
            "fiche de la source : GET /donnees/articles/{id} relit l'article dans la base"], "normal"),

        # B · Le briefing, la composante annoncée au sprint 1 : le graphe LangGraph à arêtes fixes.
        Boite("zb", 960, 280, 500, 980, "B · LE BRIEFING [S1] : graph/workflow.py (LangGraph)", genre="zone"),
        Boite("b0", BX, 310, BW, 66, "Un chemin fixe [S1]", [
            "construire_graphe l.91 : scout → rag → redacteur",
            "le modèle ne choisit jamais le chemin"], "note"),
        Boite("b1", BX, 390, BW, 66, "scout [S1]", [
            "noeud_scout l.11 → agents/scout.py collect l.54",
            "PostgreSQL : cours, variation, 13 indicateurs"], "normal"),
        Boite("b2", BX, 470, BW, 56, "rag [S1]", [
            "noeud_rag l.21 : les articles de la valeur"], "normal"),
        Boite("b3", BX, 540, BW, 66, "Articles piégés écartés [S4]", [
            "agents/analyst.py : articles_surs l.26",
            "→ guardrails/injection.py neutraliser l.46"], "neuf"),
        Boite("b4", BX, 620, BW, 66, "redacteur [S1]", [
            "noeud_redacteur l.65 ; agents/analyst.py :",
            "la consigne, avec l'interdit AMF écrit dedans"], "normal"),
        Boite("b5", BX, 700, BW, 66, "Le modèle [S1] : Azure (llm-foundry)", [
            "src/llm.py : generer_texte l.196",
            "trace : src/traces.py briefing l.155"], "lavis"),
        Boite("b6", BX, 780, BW, 66, "Garde-fou AMF [S1]", [
            "api/main.py l.280 → verifier_sortie l.53",
            "texte remplacé ; conforme_amf=false"], "garde"),
        Boite("b7", BX, 860, BW, 66, "Contrôle de fuite [S4]", [
            "api/main.py l.281 → verifier_fuite l.107",
            "les consignes du rédacteur ne sortent jamais"], "neuf"),
        Boite("b8", BX, 940, BW, 66, "Le briefing JSON [S1]", [
            "ticker, prix, variation, briefing, conforme_amf",
            "en-tête X-Request-ID sur chaque réponse"], "normal"),
        Boite("b9", BX, 1020, BW, 84, "Pourquoi deux parcours", [
            "le briefing ne reçoit qu'un code de valeur :",
            "les prompts hostiles en texte libre ne peuvent",
            "viser que les questions (avenant n°1)"], "note"),

        # C · Ce qui garde une trace, sans texte, ce qui mesure, et la production.
        Boite("zc", 1480, 280, 480, 980, "C · TRACE SANS TEXTE, MESURE, PRODUCTION", genre="zone"),
        Boite("c1", CX, 310, CW, 84, "Le journal de l'API [S3, S4]", [
            "api/question.py l.59 : request_id, statut, motif,",
            "longueur, durée ; api/main.py l.178 : refus de clé",
            "jamais le texte d'une question"], "normal"),
        Boite("c2", CX, 408, CW, 84, "Les traces sans texte, règle D9 [S4]", [
            "src/traces.py : generation l.278, terminer l.298,",
            "echouer l.311 : ni prompt, ni réponse, ni message",
            "tests/test_traces_briefing_sans_texte.py (5)"], "neuf"),
        Boite("c3", CX, 506, CW, 84, "Langfuse Cloud UE [S4, en production]", [
            "clés posées par Era, actives depuis N12 (21/10)",
            "trace 7da0ec8c : Input et Output undefined",
            "modèle, jetons, durée, coût : pour le sprint 5"], "stock"),
        Boite("c4", CX, 604, CW, 84, "La mesure à deux niveaux [S4]", [
            "evals/mesurer_question.py : niveau 1 sans modèle,",
            "niveau 2 avec le vrai modèle, verdict D5",
            "rag/questions_demo.json : 26 cas (H, L, V, Q)"], "neuf"),
        Boite("c5", CX, 702, CW, 84, "Les portes de la CI [S4]", [
            "tests/test_evals.py : une attaque ratée ou un",
            "faux positif bloque la fusion ; le jeu est rejoué",
            "avant chaque bascule en production"], "neuf"),
        Boite("c6", CX, 800, CW, 66, "Pas d'action sensible", [
            "lecture seule : rôle rita_lecture (db/roles.sql)",
            "MCP : 3 outils en lecture (passerelle_mcp/)"], "note"),
        Boite("c7", CX, 880, CW, 84, "En production", [
            "N12, commit 27e41d3, 2 140 articles",
            "livrée par la chaîne du sprint 2 (livraison.yml)",
            "rejeu en production : 5 appels conformes sur 5"], "note"),
        Boite("c8", CX, 978, CW, 102, "Mesuré", [
            "7 hostiles sur 8 refusés avant le modèle",
            "0 faux positif sur 17 questions légitimes",
            "0 reformulation reconnue sur 8 (limite)",
            "1 402 tests passés"], "note"),
    ],
    fleches=[
        # Les écrans vers leur route, puis chaque route vers son parcours.
        Fleche("e1", "rq"),
        Fleche("e2", "rb", sortie="g", entree="d"),
        Fleche("rq", "a1", "question", sortie="b", entree="h:0.75"),
        Fleche("rb", "b0", "valeur", sortie="b:0.25", entree="h:0.9"),
        # A : le parcours des questions, du haut vers le bas.
        Fleche("a1", "a2", sortie="b", entree="h"),
        Fleche("a2", "a3", sortie="b", entree="h"),
        Fleche("a3", "a4", sortie="b", entree="h"),
        Fleche("a4", "a5", sortie="b", entree="h"),
        Fleche("a5", "a6", sortie="b", entree="h"),
        Fleche("a6", "a7", sortie="b", entree="h"),
        Fleche("a7", "a8", sortie="b", entree="h"),
        Fleche("a8", "a9", sortie="b", entree="h"),
        Fleche("a9", "a10", sortie="b", entree="h"),
        Fleche("a10", "a11", sortie="b", entree="h"),
        # B : le briefing, du haut vers le bas.
        Fleche("b0", "b1", sortie="b", entree="h"),
        Fleche("b1", "b2", sortie="b", entree="h"),
        Fleche("b2", "b3", sortie="b", entree="h"),
        Fleche("b3", "b4", sortie="b", entree="h"),
        Fleche("b4", "b5", sortie="b", entree="h"),
        Fleche("b5", "b6", sortie="b", entree="h"),
        Fleche("b6", "b7", sortie="b", entree="h"),
        Fleche("b7", "b8", sortie="b", entree="h"),
    ],
    legende="Sprint 4 · relu le 21/10/2026 contre la branche sprint-4-agentique-garde-fous (numéros de ligne de ce jour) · "
            "mesures et tests : evidence/sprint-4/README.md.",
    cles_boites={"normal": "étape déjà codée (sprint 1 ou 3)", "garde": "garde-fou déjà codé (sprint 1)",
                 "neuf": "codé au sprint 4", "lavis": "le modèle", "stock": "service externe", "note": "à retenir"},
    cles_fleches={"flux": "passage"},
)


if __name__ == "__main__":
    (ICI / f"{COMPOSANTE.nom}.svg").write_text(svg(COMPOSANTE), encoding="utf-8", newline="\n")
    (ICI / f"{COMPOSANTE.nom}.drawio").write_text(drawio(COMPOSANTE), encoding="utf-8", newline="\n")
    print("écrit", COMPOSANTE.nom, ".svg et .drawio ; taille de rendu :",
          f"{COMPOSANTE.largeur},{COMPOSANTE.hauteur_totale}")
