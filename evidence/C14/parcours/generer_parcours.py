"""Les schémas fonctionnels des parcours des écrans 4 (Question) et 5 (Tableau de bord), C14.2, relevés le 02/11/2026.

Pourquoi : la grille de C14 demande que la modélisation des parcours respecte un formalisme ; les écrans 1 à 3 ont des
wireframes d'état (`evidence/C14/WIREFRAMES-*`), les écrans 4 et 5 n'avaient rien. Ces deux schémas sont **relevés
sur la version actuelle** (code et tests du commit `12cc00c`) : ce ne sont pas des maquettes initiales, et la note de
chaque schéma le dit. Ils suivent les scénarios de `evidence/C14/preuve-specifications-ecrans-4-et-5.md`.

Le dessin réutilise le moteur des schémas d'E3 (boîtes, flèches droites, légende, contrôle de place), comme ceux d'E2.
Le `.png` se rend depuis le `.svg` par Chrome sans fenêtre (README du dossier).

Lancer :  C:\\Python314\\python.exe -X utf8 evidence\\C14\\parcours\\generer_parcours.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ICI = Path(__file__).parent
_E3 = ICI.parent.parent.parent / "docs" / "rapports" / "E3" / "schemas" / "generer_schemas.py"
_spec = importlib.util.spec_from_file_location("schemas_e3_moteur_c14", _E3)
moteur = importlib.util.module_from_spec(_spec)
sys.modules["schemas_e3_moteur_c14"] = moteur   # dataclass relit son module dans sys.modules
_spec.loader.exec_module(moteur)

Schema, Boite, Fleche = moteur.Schema, moteur.Boite, moteur.Fleche

# Quatre colonnes de 312 px, quatre rangées de boîtes : chaque flèche passe dans l'espace entre deux colonnes.
X = (40, 376, 712, 1048)
Y = (134, 242, 350, 458)
L, H = 288, 100


def zone(id_, col, titre):
    return Boite(id_, X[col], 100, 312, 474, titre, genre="zone")


def boite(id_, col, rang, titre, lignes, genre="normal"):
    return Boite(id_, X[col] + 12, Y[rang], L, H, titre, lignes, genre)


# =============================================================================
# Écran 4 : poser une question et remonter à la source
# =============================================================================
QUESTION = Schema(
    nom="PARCOURS-C14-ecran-question", largeur=1400, hauteur=700,
    titre="Écran 4, Question : de la question à la source citée",
    sous_titre="Schéma fonctionnel du parcours, relevé le 02/11/2026 sur la version actuelle (commit 12cc00c)",
    boites=[
        zone("za", 0, "1. ENTRER"),
        boite("ouvrir", 0, 0, "Ouvrir l'écran", ["depuis la navigation", "commune aux cinq écrans"]),
        boite("cle", 0, 1, "Une clé dans l'onglet ?", ["sessionStorage, partagée", "avec les autres écrans"], "garde"),
        boite("saisir", 0, 2, "Saisir la clé d'API", ["champ masqué, étiqueté ;", "le focus y est posé"]),
        boite("refusee", 0, 3, "Clé refusée (403)", ["oubliée, puis", "redemandée"], "garde"),

        zone("zb", 1, "2. DEMANDER"),
        boite("question", 1, 0, "Écrire la question", ["3 à 500 caractères ;", "le focus est sur ce champ"]),
        boite("post", 1, 1, "Envoyer : POST /question", ["avec la clé ; statut annoncé :", "« Recherche dans les articles »"], "lavis"),
        boite("bornes", 1, 2, "Hors bornes (422)", ["« de 3 à 500 caractères »,", "dit dans le statut"], "garde"),

        zone("zc", 2, "3. RÉPONDRE OU REFUSER"),
        boite("reponse", 2, 0, "La réponse", ["paragraphes, puis sources", "numérotées ; clé gardée"], "lavis"),
        boite("refus", 2, 1, "Pas de réponse (refus)", ["hors corpus, sans le modèle ;", "conseil, détournement, 429 :", "le motif écrit en mots"], "garde"),
        boite("erreur", 2, 2, "Erreur technique", ["503 ou réponse illisible :", "encart à part, code HTTP"]),
        boite("arret", 2, 3, "API arrêtée", ["« Le serveur ne répond pas.", "Vérifiez que l'API… »"]),

        zone("zd", 3, "4. REMONTER À LA SOURCE"),
        boite("clic", 3, 0, "Ouvrir une source", ["clic sur une référence", "de la liste numérotée"]),
        boite("lire", 3, 1, "Lire la fiche stockée", ["GET /donnees/articles/{id},", "avec la clé"], "lavis"),
        boite("fiche", 3, 2, "La fiche de la source", ["ligne stockée, passage", "transmis ; focus sur la fiche ;", "introuvable (404) : en mots"], "lavis"),

        Boite("releve", 40, 594, 1320, 76, "Relevé du jour, pas une maquette initiale",
              ["Dessiné le 02/11/2026 d'après frontend/question.html, question.js et leurs tests (12cc00c), après le code (16/10).",
               "Spécification : evidence/C14/preuve-specifications-ecrans-4-et-5.md, US-4, scénarios S1 à S10, critères Q1 à Q19."],
              "note"),
    ],
    fleches=[
        Fleche("ouvrir", "cle", sortie="b", entree="h"),
        Fleche("cle", "question", sortie="d", entree="g", etiquette="oui", pos=0.5),
        Fleche("cle", "saisir", sortie="b", entree="h", etiquette="non"),
        Fleche("saisir", "question", sortie="d:0.3", entree="g:0.8", etiquette="saisie", pos=0.35),
        Fleche("question", "post", sortie="b", entree="h"),
        Fleche("post", "reponse", sortie="d:0.2", entree="g", etiquette="réponse", pos=0.55),
        Fleche("post", "refus", sortie="d", entree="g", etiquette="refus"),
        Fleche("post", "erreur", sortie="d:0.75", entree="g:0.4", sens="erreur", etiquette="503", pos=0.55),
        Fleche("post", "arret", sortie="d:0.95", entree="g", sens="erreur", etiquette="réseau", pos=0.6),
        Fleche("post", "bornes", sortie="b", entree="h", sens="erreur", etiquette="422"),
        Fleche("post", "refusee", sortie="g:0.9", entree="d", sens="erreur", etiquette="403", pos=0.5),
        Fleche("refusee", "saisir", sortie="h", entree="b"),
        Fleche("reponse", "clic", sortie="d", entree="g"),
        Fleche("clic", "lire", sortie="b", entree="h"),
        Fleche("lire", "fiche", sortie="b", entree="h"),
    ],
    legende="Sources : frontend/question.html, frontend/question.js, tests/test_frontend.py, tests/test_smoke_ui.py, tests/test_cle_memorisee_ui.py (12cc00c).",
    cles_boites={"normal": "étape", "lavis": "appel ou affichage", "garde": "contrôle, refus", "note": "relevé"},
    cles_fleches={"flux": "suite du parcours", "erreur": "refus ou panne"},
)

# =============================================================================
# Écran 5 : surveiller l'état du service
# =============================================================================
TABLEAU = Schema(
    nom="PARCOURS-C14-ecran-tableau-de-bord", largeur=1400, hauteur=700,
    titre="Écran 5, Tableau de bord : lire l'état du service, et savoir quoi faire",
    sous_titre="Schéma fonctionnel du parcours de l'exploitant, relevé le 02/11/2026 sur la version actuelle (commit 12cc00c)",
    boites=[
        zone("za", 0, "1. ENTRER"),
        boite("ouvrir", 0, 0, "Ouvrir le tableau de bord", ["depuis la navigation", "commune aux cinq écrans"]),
        boite("cle", 0, 1, "Une clé dans l'onglet ?", ["sessionStorage, partagée", "avec les autres écrans"], "garde"),
        boite("saisir", 0, 2, "Saisir la clé d'API", ["champ masqué et étiqueté"]),
        boite("refusee", 0, 3, "Clé refusée (401, 403)", ["oubliée ; retour au", "formulaire de clé"], "garde"),

        zone("zb", 1, "2. LIRE"),
        boite("auto", 1, 0, "Toutes les 30 secondes", ["actualisation automatique,", "sauf si elle est suspendue"], "note"),
        boite("lire", 1, 1, "Lire /health et /sante", ["en parallèle, 5 s au plus ;", "un seul appel à la fois"], "lavis"),
        boite("main", 1, 2, "Actualiser, à la main", ["bouton bloqué pendant", "la lecture"]),

        zone("zc", 2, "3. MONTRER"),
        boite("cartes", 2, 0, "Sept cartes", ["état en mots, valeur, période ;", "« Que faire » s'il faut agir"], "lavis"),
        boite("inconnu", 2, 1, "Sans donnée : INCONNU", ["jamais SAIN ;", "la carte dit pourquoi"], "garde"),
        boite("panne", 2, 2, "Une lecture en panne", ["l'autre reste lisible ;", "mal formée : INCONNU"], "garde"),
        boite("exercice", 2, 3, "Exercice de panne", ["un bandeau le dit, pour ne", "pas le prendre pour une vraie"], "note"),

        zone("zd", 3, "4. LAISSER LIRE"),
        boite("resume", 3, 0, "Seul le résumé est annoncé", ["aria-live : pas les sept", "cartes à chaque lecture"], "note"),
        boite("suspendre", 3, 1, "Suspendre", ["l'actualisation automatique", "s'arrête ; l'état écrit dessous"], "garde"),
        boite("reprendre", 3, 2, "Reprendre", ["une lecture aussitôt, puis", "toutes les 30 secondes"]),

        Boite("releve", 40, 594, 1320, 76, "Relevé du jour, pas une maquette initiale",
              ["Dessiné le 02/11/2026 d'après frontend/tableau-de-bord.html, tableau-de-bord.js et leurs tests (12cc00c), après le code (22/10).",
               "Spécification : evidence/C14/preuve-specifications-ecrans-4-et-5.md, US-5, scénarios S1 à S10, critères T1 à T17."],
              "note"),
    ],
    fleches=[
        Fleche("ouvrir", "cle", sortie="b", entree="h"),
        Fleche("cle", "lire", sortie="d", entree="g", etiquette="oui"),
        Fleche("cle", "saisir", sortie="b", entree="h", etiquette="non"),
        Fleche("saisir", "lire", sortie="d:0.3", entree="g:0.8", etiquette="saisie", pos=0.35),
        Fleche("auto", "lire", sortie="b", entree="h"),
        Fleche("main", "lire", sortie="h", entree="b"),
        Fleche("lire", "cartes", sortie="d:0.2", entree="g", etiquette="lisible", pos=0.55),
        Fleche("lire", "inconnu", sortie="d", entree="g"),   # le titre de la boîte le dit : une étiquette déborderait
        Fleche("lire", "panne", sortie="d:0.8", entree="g:0.4", sens="erreur", etiquette="panne", pos=0.55),
        Fleche("lire", "refusee", sortie="g:0.9", entree="d", sens="erreur", etiquette="401, 403", pos=0.5),
        Fleche("refusee", "saisir", sortie="h", entree="b"),
        Fleche("cartes", "resume", sortie="d", entree="g"),
        Fleche("suspendre", "reprendre", sortie="b", entree="h", etiquette="bascule"),
    ],
    legende="Sources : frontend/tableau-de-bord.html, frontend/tableau-de-bord.js, tests/test_tableau_de_bord.py, tests/test_smoke_tableau_de_bord.py (12cc00c).",
    cles_boites={"normal": "étape", "lavis": "appel ou affichage", "garde": "contrôle, refus", "note": "précision, relevé"},
    cles_fleches={"flux": "suite du parcours", "erreur": "refus ou panne"},
)

SCHEMAS = (QUESTION, TABLEAU)


def ecrire(s: Schema) -> None:
    (ICI / f"{s.nom}.svg").write_text(moteur.svg(s), encoding="utf-8", newline="\n")
    (ICI / f"{s.nom}.drawio").write_text(moteur.drawio(s), encoding="utf-8", newline="\n")
    print("écrit", s.nom, ".svg et .drawio ; rendu :", s.largeur, "x", s.hauteur_totale)


if __name__ == "__main__":
    trop = [d for schema in SCHEMAS for d in moteur.debordements(schema)]
    if trop:
        raise SystemExit("Texte qui déborde, rien n'est écrit :\n" + "\n".join(trop))
    for schema in SCHEMAS:
        ecrire(schema)
