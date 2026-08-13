# docs/archive — documents historiques

> ⚠️ **Rien ici n'est un livrable de certification.**
> Ces documents décrivent des états **antérieurs** du projet. Ils sont conservés pour la
> trace de l'évolution de la conception, pas comme référence technique.

## Ce que contient ce dossier

| Document | Date | Ce que c'était |
|---|---|---|
| `RAPPORT-PROJET-V0.md` | mai 2026 | premier rapport de projet, version 0 |
| `RITA-V2-ARCHITECTURE.md` | mai 2026 | architecture envisagée pour une version 2 |
| `RITA-V2-DIFFERENTIATORS.md` | mai 2026 | positionnement concurrentiel |

## Pourquoi ils sont ici et pas dans `docs/`

Ils ne correspondent plus au code. Vérifié le 13/08/2026 :

- **Trois flux RSS qu'ils citent ne répondent plus** — `rss.lesechos.fr` (pas de réponse),
  `bfmtv.com/rss/economie/bourse/` (404), `rss.boursorama.com/actualites` (503).
  Le module réel `sources/rss.py` en utilise **trois autres**, tous vérifiés à 200 :
  `bfmtv.com/rss/economie/`, `latribune.fr/feed.xml`, `lemonde.fr/economie/rss_full.xml`.
  Le code documente d'ailleurs lui-même pourquoi les anciens ont été abandonnés.
- L'architecture décrite diffère de l'implémentation actuelle.
- Aucun document vivant du dépôt ne les référence.

Le nom `RAPPORT-PROJET-V0.md` posé dans `docs/`, à côté de `docs/rapports/E1/`, pouvait
laisser croire à un livrable. D'où le déplacement.

## Où est la référence à jour

| Quoi | Où |
|---|---|
| Vue d'ensemble et état des livrables | [README](../../README.md) |
| Livrable E1 (C1–C5) | [rapport-E1.pdf](../rapports/E1/rapport-E1.pdf) |
| Preuves par compétence | [evidence/](../../evidence/) |
| Architecture réelle | le code — `sources/`, `db/`, `api/`, `graph/`, `bigdata/` |
