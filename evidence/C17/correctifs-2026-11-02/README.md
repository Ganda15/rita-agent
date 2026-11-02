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
