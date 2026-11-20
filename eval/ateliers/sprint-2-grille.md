# Atelier croisé n°2 : Le socle et la chaîne

Phase 6, fil rouge. Grille remplie par l'évaluateur pendant la démonstration, puis versée dans le dépôt du présenté.

| Présenté | Évaluateur | Date | Projet |
|---|---|---|---|
| Eramalingam GANDAKUMAR (case laissée vide sur la grille) | un pair de la promotion | 15/10/2026 | RITA, document d'entrée [`docs/sprint-2/README.md`](../../docs/sprint-2/README.md) |

**Format (2 h en tout, puis on inverse les rôles).** 2 min de journal des retours, puis 20 min de démonstration en live
sur l'environnement déployé. On note du démontré, jamais du déclaré. 15 min de questions guidées par la grille :
✓ démontré, ~ partiel, ✗ absent. 10 min de conseils : un point fort, un conseil prioritaire, actionnable avant la fin
du sprint suivant.

Recopiée mot pour mot depuis la grille PDF remplie par l'évaluateur (annotations du 15/10/2026, de 16 h 54 à 17 h 04),
fautes de frappe comprises. L'original est versé à côté : [`sprint-2-grille-originale.pdf`](sprint-2-grille-originale.pdf).

**Journal des retours.** Conseil reçu à l'atelier n°1 : ☐ traité ☐ reporté ☐ écarté. Commentaire : *(laissé vide par
l'évaluateur)*

| # | Critère | ✓ / ~ / ✗ | Preuve observée, remarque |
|---|---|---|---|
| 1 | **Ça tourne ailleurs.** J'ai constaté le squelette en marche sur l'URL de production, pas sur la machine du présenté. | ✓ | Url prod VU |
| 2 | **Livraison automatique.** Une fusion déclenche tests, build et déploiement sans action manuelle (vu en live ou journal de chaîne à l'appui). | ✓ | Vu en live |
| 3 | **Un échec bloque.** Le commit volontairement cassé est arrêté par la chaîne, démontré en live. | ✓ | vu en live |
| 4 | **Rollback.** Le retour à la version précédente est montré, en une opération. | ✓ | Monter en demo |
| 5 | **Secrets et reproductibilité.** Pas de secret dans le dépôt, et l'environnement se reconstruit depuis le repo. | ✓ | fichier .md |

**Le point fort :** Era a compris comment ça la CI/CD fonctionne

**Le conseil prioritaire pour le sprint 3 :** RAS

---

## Suite donnée par le présenté

Pour chaque remarque : traitée (commit), reportée (sprint et raison) ou écartée (raison).

| Remarque | Suite | Commit ou raison |
|---|---|---|
| 1 · « Url prod VU » | rien à faire | constat positif |
| 2 · « Vu en live » | rien à faire | constat positif |
| 3 · « vu en live » | rien à faire | constat positif ; preuve versionnée : `evidence/sprint-2/journaux/pr-93-commit-casse.txt` |
| 4 · « Monter en demo » | rien à faire | constat positif ; les passages du retour arrière datent du 14/10 au soir et du 15/10 au matin (`evidence/sprint-2/journaux/retours-arriere.txt`) |
| 5 · « fichier .md » | rien à faire | constat positif ; procédure de reconstruction : `docs/EXPLOITATION.md`, § 3 ter |
| Point fort · CI/CD comprise | rien à faire | point positif |
| Conseil · « RAS » | aucun conseil à traiter | à reporter tel quel dans le journal des retours de l'atelier n°3 |
| Journal des retours · laissé vide | à signaler | le conseil de l'atelier n°1 (rôle de MCP et place du serveur) était traité : `docs/CADRAGE-V1.md`, § 5 |

> Nom de l'évaluateur remplacé par son rôle le 20/11/2026, avant la publication du dépôt (registre RGPD, mesure M2). Le reste de la grille est inchangé ; l'original reste dans l'historique Git et dans les tags.
