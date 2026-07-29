# evidence/ — une preuve par compétence

> Structure demandée par le formateur (rendez-vous du 28/07/2026) :
> *« It's evidence each evidence for each competency. Like, one evidence per competency. »*
>
> Et une contrainte de séquencement :
> *« you send each one for review before moving on »* — une compétence est prouvée, envoyée en
> revue, **puis** on passe à la suivante.

## Règle

Chaque dossier `C1/` … `C5/` contient **la preuve identifiable** que la compétence est acquise.
La preuve se constitue **au fil de l'eau**, jamais reconstituée après coup.

Une preuve = ce qu'un évaluateur peut ouvrir seul et comprendre sans explication orale :
capture d'écran horodatée, sortie de commande, fichier produit, lien vers un run CI.

## État au 28/07/2026

| Dossier | Compétence | Preuve attendue | État |
|---|---|---|---|
| `C1/` | Automatiser l'extraction depuis plusieurs types de sources | script fonctionnel + sortie réelle par source + tableau de couverture des types + preuve big data séparée | 1 source /7 |
| `C2/` | Requêtes SQL d'extraction | les 3 requêtes + leur sortie + documentation des jointures et optimisations | ⬜ |
| `C3/` | Règles d'agrégation et nettoyage | rapport qualité : entrées corrompues supprimées, formats homogénéisés, vérification croisée | ⬜ |
| `C4/` | Base de données dans le respect du RGPD | MCD + MPD (MERISE) + note RGPD + script d'import | ⬜ |
| `C5/` | API et tests | OpenAPI + tests automatisés + couverture | partiel (Q1 : 15 tests, `/health` + `/briefing`) |

## Ordre de travail imposé

```
C1 prouvée → envoyée en revue → validée → C2 → … → C5
```

Ne pas passer à la compétence suivante avant retour du formateur sur la précédente.

## Ce qui ne va pas ici

- Le code source (il est dans `agents/`, `sources/`, `db/`, `graph/`)
- Les rapports rédigés E1–E5 (ils iront dans `docs/` au moment de la rédaction, Q6–Q8)
- Les notes de travail et le journal (ils sont dans Obsidian)

Ici, **uniquement des preuves** — ce qu'on montre, pas ce qu'on raconte.
