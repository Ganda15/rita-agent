# Sprint 5 : synthèse

> RITA, fil rouge de la phase 6. Le sprint 5 rend le système pilotable et reprenable. Version 1, prototype local,
> avant l'atelier croisé n°5. Le détail est dans le [livrable](livrable-sprint-5.md).

## Sommaire

1. Le brief, et ce qui est livré
2. Les critères de la grille, et où en est chacun
3. Ce qui est mesuré
4. Ce qui n'est pas fait

## 1. Le brief, et ce qui est livré

Le brief demande des métriques et des traces, un tableau de bord lisible par un non-développeur, des alertes à seuils
argumentés liées chacune à une action, et une documentation d'exploitation qu'un tiers peut suivre seul.

Le sprint 5 est un **prototype local** : il ne touche ni la production ni la branche `main`. Tout se démontre sur une
copie de RITA lancée sur le poste avec Docker, construite depuis la branche du sprint.

| Livré | Où |
|---|---|
| Les traces de chaque appel dans Langfuse, sans texte, reliées au journal par le `request_id` ; un projet propre à la copie | `src/traces.py`, projet Langfuse `rita-copie-sprint5` |
| Des compteurs en six catégories, des signaux sur 15 minutes et sur 24 h, servis par `GET /sante` | `monitorage/compteurs.py`, `monitorage/signaux.py`, `api/sante.py` |
| Sept seuils provisoires, chacun avec son pourquoi, son action et sa règle de résolution ; un coût en euros au prix public daté | `monitorage/seuils.json`, `monitorage/prix.json` |
| Un tableau de bord de sept cartes : un mot, une valeur en clair, « Que faire » | `frontend/tableau-de-bord.html` |
| Une vigie hors de l'API : une issue GitHub par alerte, commentée au retour du service, fermée à la résolution | `monitorage/vigie.py` |
| Une panne et une dérive simulées, sûres et réversibles | `monitorage/exercice.py`, `monitorage/exercer.py` |
| Déployer et revenir en arrière sur la copie, commit et image vérifiés | `scripts/copie_sprint5.py` |
| La documentation d'exploitation | `docs/exploitation.md` |
| Le scénario de la démo, 9 min 30 | `docs/sprint-5/DEMO.md` |

## 2. Les critères de la grille, et où en est chacun

| # | Critère | État |
|---|---|---|
| 1 | Du signal à l'action | **prêt** : dérive jouée le 22/10, issue #128 ouverte par la vigie, action suivie, issue fermée |
| 2 | Tableau de bord lisible | **prêt** : testé dans chaque état, vu sur la copie en panne, rétablie, en dérive |
| 3 | Doc : déployer | suivie à la lettre par son auteur le 23/10, deux trous corrigés ; **le test par un tiers se fait à l'atelier** |
| 4 | Doc : diagnostiquer | panne inconnue trouvée en 11 minutes avec la doc le 23/10, cinq trous corrigés ; **tiers à l'atelier** |
| 5 | Doc : rollback | retour arrière en 5 s, commit et image vérifiés, sans trou ; **tiers à l'atelier** |
| 6 | Démo prête | **prêt** : deux répétitions le 23/10, environ 9 minutes et 9 minutes 30 |
| 7 | Série complète | **prêt** : grilles 1 à 4 versées, avec les retours et leur suite ; grille 5 remplie à l'atelier |

## 3. Ce qui est mesuré

| Mesure | Résultat |
|---|---|
| Suite complète | 1680 passés, 24 ignorés, 2 échecs attendus, 0 échec |
| Couverture des neuf modules du sprint 5 | 100 % (764 instructions, 286 tests) |
| Panne simulée | 5 erreurs sur 5, issue #127 ouverte ; service rétabli à 19 h 00 ; alerte résolue et issue fermée à 19 h 14 |
| Dérive simulée | 12 refus sur 12, 0 jeton consommé ; issue #128 ouverte à 19 h 16, fermée à 19 h 32 |
| Retour arrière | 6 s, sans reconstruction ; un second retour est refusé |
| Coût des exercices du 22/10 | 0,009486 € estimés, sous le plafond de 0,10 € fixé avant |
| Test de la doc à la lettre (23/10) | dix trous trouvés et corrigés, chacun couvert par un test |
| Répétitions de la démo (23/10) | environ 9 minutes, puis environ 9 minutes 30 ; dérive et alerte jouées les deux fois |

## 4. Ce qui n'est pas fait

- La production n'a pas de vigie ; la livraison de la copie se lance par une commande (la livraison automatique est
  celle de la production, citée, pas rejouée).
- La documentation n'a pas encore été suivie par un tiers : elle l'a été à la lettre par son auteur, le test autonome
  se fait à l'atelier.
- Les seuils sont provisoires ; les mesures repartent à zéro au redémarrage ; la vigie et la collecte des cours se
  lancent à la main.
- L'écart de fraîcheur des cours en production reste ouvert.
