# Sprint 5 : la vigie et la démo

Document d'entrée du sprint 5 du fil rouge RITA. Le sprint rend le système pilotable et reprenable : des mesures, un
tableau de bord, des alertes à seuils argumentés liées chacune à une action, une documentation d'exploitation.

- **Prototype local** : tout vit sur la branche `sprint-5-vigie-demo` et se démontre sur une copie de RITA lancée sur
  le poste avec Docker (`http://localhost:8011`). La production, le serveur et la branche `main` ne sont pas touchés.
- **Synthèse du sprint, à lire en premier** : [`livrable/synthese-sprint-5.md`](livrable/synthese-sprint-5.md) et sa version PDF ([`synthese-sprint-5.pdf`](livrable/synthese-sprint-5.pdf)).
- **Livrable du sprint** : [`livrable/livrable-sprint-5.md`](livrable/livrable-sprint-5.md) et sa version PDF ([`livrable-sprint-5.pdf`](livrable/livrable-sprint-5.pdf)).
- **Documentation d'exploitation** : [`docs/exploitation.md`](../exploitation.md) (déployer, diagnostiquer une panne,
  revenir en arrière, les alertes) ; ses procédures en PDF : [`exploitation-sprint-5.pdf`](livrable/exploitation-sprint-5.pdf).
- **Scénario de la démo** : [`DEMO.md`](DEMO.md) et sa version PDF ([`scenario-demo-sprint-5.pdf`](livrable/scenario-demo-sprint-5.pdf)).
- **Preuves** : index dans [`evidence/sprint-5/README.md`](../../evidence/sprint-5/README.md).

## Lancer la copie et sa vigie

| Geste | Commande |
|---|---|
| Déployer la version courante de la branche | `C:\Python314\python.exe scripts\copie_sprint5.py deployer` |
| Voir la version servie et la précédente | `C:\Python314\python.exe scripts\copie_sprint5.py etat` |
| Ouvrir le tableau de bord | `http://localhost:8011/tableau-de-bord.html` (clé de l'API demandée) |
| Lancer un passage de la vigie, à blanc | `C:\Python314\python.exe -m monitorage.vigie --adresse http://localhost:8011` |

Le pas à pas complet, avec le résultat attendu de chaque commande, est dans `docs/exploitation.md`.
