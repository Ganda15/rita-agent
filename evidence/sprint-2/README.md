# Preuves du sprint 2 : le socle et la chaîne

Preuves versionnées de l'atelier croisé n°2 (14 et 15/10/2026). Les journaux de chaîne sont des extraits des passages
GitHub, relevés avec `gh` ; les valeurs des secrets n'y figurent pas (GitHub les masque, et les extraits ne gardent que
les lignes utiles).

| Preuve | Fichier | Critère de la grille |
|---|---|---|
| Première livraison N0 : deux refus, puis la réussite | `N0-premiere-livraison-2026-10-14.md` | 2 |
| Livraison N1, retour arrière N1 vers N0, relivraison | `N1-retour-arriere-2026-10-14.md` | 2 et 4 |
| Journal de chaîne de la livraison N1 (fusion de la PR #92) | `journaux/livraison-N1.txt` | 2 |
| Journal de chaîne de la livraison N2 (fusion de la PR #95, version 1 du livrable) | `journaux/livraison-N2.txt` | 2 |
| Journal de chaîne du commit cassé (PR #93), bloqué | `journaux/pr-93-commit-casse.txt` | 3 |
| Journal de chaîne des deux retours arrière | `journaux/retours-arriere.txt` | 4 |
| Capture de `/health` en production : N1, puis N2 | `captures/production-health-2026-10-15.png`, `captures/production-health-N2-2026-10-15.png` | 1 |
| Capture de l'écran de briefing en production | `captures/production-briefing-2026-10-15.png` | 1 |

Commandes pour relire les journaux à la source :

```
gh pr checks 93 --repo Ganda15/rita-agent
```

```
gh run view 38636271353 --repo Ganda15/rita-agent
```

```
gh run view 38637911060 --repo Ganda15/rita-agent
```

```
gh run view 38707804718 --repo Ganda15/rita-agent
```

Le document de synthèse du sprint est `docs/sprint-2/livrable/livrable-sprint-2.pdf`.
