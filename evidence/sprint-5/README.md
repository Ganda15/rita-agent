# Preuves du sprint 5 : la vigie et la démo (prototype local)

Branche `sprint-5-vigie-demo`, dossier `D:\KandaWork\RITA_PROJECT\rita-agent-sprint-5`. Toutes les preuves portent sur
la copie de RITA lancée sur le poste (projet Docker `rita-s5`, `http://localhost:8011`) ou sur le code de la branche ;
aucune ne porte sur la production. Aucune clé n'est recopiée ici, ni aucun texte de question.

## Index des preuves

| Preuve | Fichier | Ce qu'elle prouve |
|---|---|---|
| Mesures des étapes 1 à 5 | [`mesures/README.md`](mesures/README.md) | les tests rouges avant le code, étape par étape ; la suite complète et la couverture au commit `d4a41be` |
| Suite complète, fin du sprint | [`mesures/suite-complete-fin-2026-10-22.txt`](mesures/suite-complete-fin-2026-10-22.txt) | 1674 passés, 24 ignorés, 2 échecs attendus, 0 échec |
| Couverture des neuf modules du sprint 5 | [`mesures/tests-et-couverture-sprint-5-fin-2026-10-22.txt`](mesures/tests-et-couverture-sprint-5-fin-2026-10-22.txt) | 286 tests passés ; 100 % des 764 instructions (compteurs, signaux, seuils, vigie, exercices, `/sante`, copie du poste) |
| Analyse statique | [`mesures/ruff-sprint-5-2026-10-22.txt`](mesures/ruff-sprint-5-2026-10-22.txt) | aucune remarque |
| Tableau de bord, données fabriquées | [`captures/tableau-de-bord-bureau-donnees-fabriquees.png`](captures/tableau-de-bord-bureau-donnees-fabriquees.png), [`captures/tableau-de-bord-mobile-donnees-fabriquees.png`](captures/tableau-de-bord-mobile-donnees-fabriquees.png) | la page sur un écran de bureau et de téléphone (375 px), avant la copie en marche |
| La copie lancée sur le poste (étape 9) | [`copie-locale-2026-10-22.md`](copie-locale-2026-10-22.md) | image propre au sprint 5, `/health` qui annonce le commit, cours collectés jusqu'au 22/10, `rita-api:local` inchangée |
| Les preuves sur la copie en marche (étape 11) | [`preuves-copie-2026-10-22.md`](preuves-copie-2026-10-22.md) | déploiement, retour arrière, second retour refusé ; panne simulée diagnostiquée avec la doc ; service rétabli puis alerte résolue ; dérive détectée ; issues #127 et #128 ouvertes puis fermées par la vigie ; coût 0,009486 € |
| Le journal brut de l'étape 11 | [`preuves-copie-2026-10-22-journal.txt`](preuves-copie-2026-10-22-journal.txt) | chaque commande et sa sortie, dans l'ordre |
| Captures de la copie en marche | [`captures/copie-0-redemarrage-pendant-le-retour-arriere.webp`](captures/copie-0-redemarrage-pendant-le-retour-arriere.webp), [`copie-1`](captures/copie-1-panne-en-cours.webp), [`copie-2`](captures/copie-2-service-retabli-alerte-ouverte.webp), [`copie-3`](captures/copie-3-derive-refus-securite.webp) | le tableau de bord pendant le retour arrière, la panne, le service rétabli avec l'alerte encore ouverte, la dérive |

## Ce qui n'a pas encore de preuve

- Le test de `docs/exploitation.md` par une personne qui ne l'a pas écrite (critères 3 à 5 de la grille) : il se fait à
  l'atelier n°5, avec l'évaluateur.
- Les deux répétitions chronométrées de la démo (critère 6).
