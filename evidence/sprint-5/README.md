# Preuves du sprint 5 : la vigie et la démo (prototype local)

Branche `sprint-5-vigie-demo`, dossier `D:\KandaWork\RITA_PROJECT\rita-agent-sprint-5`. Les preuves portent sur la copie
de RITA lancée sur le poste (projet Docker `rita-s5`, `http://localhost:8011`), sur le code de la branche, et, depuis le
23/10 au soir, sur la production (livraison N16). Aucune clé n'est recopiée ici, ni aucun texte de question.

## Index des preuves

| Preuve | Fichier | Ce qu'elle prouve |
|---|---|---|
| Mesures des étapes 1 à 5 | [`mesures/README.md`](mesures/README.md) | les tests rouges avant le code, étape par étape ; la suite complète et la couverture au commit `d4a41be` |
| Suite complète, fin du sprint | [`mesures/suite-complete-2026-10-23.txt`](mesures/suite-complete-2026-10-23.txt) | 1680 passés, 24 ignorés, 2 échecs attendus, 0 échec |
| Couverture des neuf modules du sprint 5 | [`mesures/tests-et-couverture-sprint-5-fin-2026-10-22.txt`](mesures/tests-et-couverture-sprint-5-fin-2026-10-22.txt) | 286 tests passés ; 100 % des 764 instructions (compteurs, signaux, seuils, vigie, exercices, `/sante`, copie du poste) |
| Analyse statique | [`mesures/ruff-sprint-5-2026-10-22.txt`](mesures/ruff-sprint-5-2026-10-22.txt) | aucune remarque |
| Tableau de bord, données fabriquées | [`captures/tableau-de-bord-bureau-donnees-fabriquees.png`](captures/tableau-de-bord-bureau-donnees-fabriquees.png), [`captures/tableau-de-bord-mobile-donnees-fabriquees.png`](captures/tableau-de-bord-mobile-donnees-fabriquees.png) | la page sur un écran de bureau et de téléphone (375 px), avant la copie en marche |
| La copie lancée sur le poste (étape 9) | [`copie-locale-2026-10-22.md`](copie-locale-2026-10-22.md) | image propre au sprint 5, `/health` qui annonce le commit, cours collectés jusqu'au 22/10, `rita-api:local` inchangée |
| Les preuves sur la copie en marche (étape 11) | [`preuves-copie-2026-10-22.md`](preuves-copie-2026-10-22.md) | déploiement, retour arrière, second retour refusé ; panne simulée diagnostiquée avec la doc ; service rétabli puis alerte résolue ; dérive détectée ; issues #127 et #128 ouvertes puis fermées par la vigie ; coût 0,009486 € |
| Le journal brut de l'étape 11 | [`preuves-copie-2026-10-22-journal.txt`](preuves-copie-2026-10-22-journal.txt) | chaque commande et sa sortie, dans l'ordre |
| Le test de la doc à la lettre et les deux répétitions (étapes 12 et 13, 23/10) | [`test-doc-et-repetitions-2026-10-23.md`](test-doc-et-repetitions-2026-10-23.md) | dix trous de la doc trouvés et corrigés ; panne inconnue diagnostiquée en 11 minutes ; deux répétitions sous 10 minutes, issues #129 et #131 fermées par la vigie ; la fausse alerte de production #130 expliquée, la copie passée sur son propre projet Langfuse |
| La mise en production (23/10, livraison N16) | [`production-2026-10-23.md`](production-2026-10-23.md) | PR #133 et #134 aux contrôles verts ; livraison N16 réussie (18:00 à 18:12) ; en production : `/health` annonce `845e3b3`, le tableau de bord répond, `/sante` exige la clé |
| Captures de la copie en marche | [`captures/copie-0-redemarrage-pendant-le-retour-arriere.webp`](captures/copie-0-redemarrage-pendant-le-retour-arriere.webp), [`copie-1`](captures/copie-1-panne-en-cours.webp), [`copie-2`](captures/copie-2-service-retabli-alerte-ouverte.webp), [`copie-3`](captures/copie-3-derive-refus-securite.webp) | le tableau de bord pendant le retour arrière, la panne, le service rétabli avec l'alerte encore ouverte, la dérive |

## Ce qui n'a pas encore de preuve

- Le test de `docs/exploitation.md` par une personne qui ne l'a pas écrite (critères 3 à 5 de la grille) : il se fait à
  l'atelier n°5, avec l'évaluateur.
