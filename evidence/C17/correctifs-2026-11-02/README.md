# Correctifs du 02/11/2026 : les deux écarts du tableau de bord

Trouvés en écrivant la spécification de l'écran 5 (`evidence/C14/preuve-specifications-ecrans-4-et-5.md`, § 4).
Tests écrits d'abord, sur le code de `d97d5bb` ; correction ensuite. Locaux et non commités au moment de l'écriture ;
rien n'est en production.

| Écart | Avant | Après | Correction |
|---|---|---|---|
| T17, WCAG 2.2.2 : l'actualisation automatique (toutes les 30 secondes) ne se suspendait pas | `tableau-de-bord-avant.txt` : le bouton manque ; le test dans un vrai navigateur, horloge simulée, s'arrête sur son absence | `tableau-de-bord-apres.txt` : 140 réussis | bouton à bascule « Suspendre l'actualisation automatique » (`aria-pressed`), texte visible de l'état ; « Actualiser » reste possible à la main sans relancer l'automatique ; reprise : une lecture aussitôt, puis toutes les 30 secondes |
| Le pied de page disait « Prototype local du sprint 5 », faux depuis la mise en production du 23/10 | même fichier : le test du pied de page échoue | même fichier | pied de page aligné sur les autres écrans |

Le test du navigateur compte les vrais appels à `/sante` sous une horloge simulée, dans un contexte à part : 1 appel au
chargement, 1 de plus après 31 secondes (témoin), aucun pendant 61 secondes de suspension, 1 à la main sans relance,
puis la reprise. Captures de la barre d'outils, suspendue, en largeur normale et à 375 px :
`tableau-de-bord-barre-large-suspendue.png`, `tableau-de-bord-barre-375px-suspendue.png`.

Limite : le bouton enfoncé ne change pas d'aspect par lui-même ; l'état est dit par le texte placé dessous et par
`aria-pressed` pour les lecteurs d'écran.

## Ajout du 02/11/2026, 11 h 30 : le focus sur le champ de clé (écart E2 de la recette)

Trouvé par la recette des cinq écrans (`evidence/C17/recette-2026-11-02/README.md`, écart E2) : à l'ouverture, le
tableau de bord était le seul écran à ne pas poser le focus sur le champ de clé. Test écrit d'abord, sur le code de
`99de9fa`, correction ensuite, sur décision d'Era.

| Écart | Avant | Après | Correction |
|---|---|---|---|
| Écran 5 : à l'ouverture sans clé, rien n'a le focus (WCAG 2.4.3) | `focus-cle-avant.txt` : 4 écrans réussis, le tableau de bord échoue : le focus reste sur la page, sur aucun champ | `focus-cle-apres.txt` : 54 réussis (recette au clavier et tests du tableau de bord) | une ligne dans `montrerConnexion` (`frontend/tableau-de-bord.js`), la même que sur les quatre autres écrans ; elle vaut aussi après une clé refusée |
