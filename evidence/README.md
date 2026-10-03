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

## État au 11/08/2026

| Dossier | Compétence | Preuve | État |
|---|---|---|---|
| `C1/` | Extraction depuis plusieurs types de sources | 10 preuves — une par source + big data séparée + analyse exploratoire | ✅ **7 sources · les 5 types** |
| `C2/` | Requêtes SQL d'extraction | `preuve-requetes-sql.md` — 3 requêtes, sorties réelles, jointures et optimisations mesurées | ✅ |
| `C3/` | Règles d'agrégation et nettoyage | 3 preuves — déduplication, artefact de regroupement, pipeline d'agrégation | ✅ |
| `C4/` | Base de données dans le respect du RGPD | `preuve-mcd-merise.md` + le MCD (`.png` et `.drawio`) · MPD dans `../db/schema.sql` · RGPD dans `../db/RGPD-registre-des-traitements.md` | ✅ |
| `C5/` | API et tests | `preuve-api-jeu-de-donnees.md` (OpenAPI 3.1.0, 8 chemins) + `mesure-garde-fou-injection.md` | ✅ |
| `C9/` | API exposant le modèle | `preuve-api-modele-2026-10-03.md` : un briefing réel servi (200, `request_id`, journal), contrat OpenAPI à 14 chemins, tests qui le tiennent, manques (502 au lieu de 422, pas de limite de débit) | ✅ créé le 03/10/2026 |
| `C11/` | Monitorage du modèle | `README.md` (9 critères), `preuve-langfuse-2026-10-03.md` (tableau par l'API, INC-006 recompté, clics restants, première trace complète réelle du 03/10), définition du tableau et export des traces factices en JSON | ✅ depuis le 02/10/2026 |
| `C12/` | Tests automatisés du modèle | `preuve-suite-de-tests-2026-10-03.md` (740 passed, 93,92 %, répartition par fichier, garde-fous mesurés, mutations) · `cas-de-verification-chapitre-donnees.md` (03/10/2026) : les 32 cas du chapitre « Données » rapprochés des tests du dépôt, 23 ✅ 5 🟠 4 ❌, quatre tests écrits le jour même | 🟠 dossier ouvert le 03/10, le reste de C12 est prouvé dans le rapport E3 |
| `C13/` | Chaîne de livraison continue | `preuve-chaine-livraison-2026-10-03.md` : treize exécutions réelles d'une journée (deux pull requests, deux fusions, une alerte manuelle), rulesets GitHub, ce qui n'a jamais tourné (publication sur tag) | ✅ créé le 03/10/2026 |
| `C6/` | Veille technique et réglementaire | protocole et notes dans `../docs/veille/` — **le dossier de preuves est vide** : rien n'a encore été partagé | 🔴 **1 note sur ~12 · 0 envoi** |

**186 tests verts** (`pytest -q`). Base : 8 tables · 1 vue · 15 index · 9 contraintes `CHECK` ·
273 608 lignes importées.

### Les schémas, et où ils sont

| Schéma | Couvre | Emplacement |
|---|---|---|
| Flux de collecte multi-source | **C1** | [`C1/SCHEMA-C1-collecte-multisource.png`](C1/SCHEMA-C1-collecte-multisource.png) |
| *Partition pruning* Parquet + Spark | **C1** | [`../bigdata/schemas/`](../bigdata/schemas/) |
| Les 3 requêtes Spark SQL | **C2** | [`../bigdata/schemas/`](../bigdata/schemas/) |
| MCD Merise | **C4** | [`C4/MCD-MERISE-RITA.png`](C4/MCD-MERISE-RITA.png) |

Chaque schéma a sa **source éditable** à côté (`.svg`, et `.drawio` quand il existe) — un
schéma qu'on ne peut pas rouvrir est un schéma qu'on ne peut pas corriger.

> ⚠️ **Ce tableau annonçait encore l'état du 28/07** (`C2` `C3` `C4` non commencées, `C1` à
> « 1 source sur 7 ») **jusqu'au 11/08/2026**. Le travail avait avancé, ce fichier non — et
> c'est le premier fichier qu'un évaluateur ouvre. Corrigé, et la leçon est notée : **un
> document d'état daté reste faux si personne ne lit la date.**

## Ce qui reste

| Critère | Ce qui manque | Nature |
|---|---|---|
| **C1#6** · **C3#2** | *« accessible depuis un dépôt Git »* — le dépôt est **privé** et n'a pour l'instant qu'un seul compte autorisé | ⚠️ **accès à donner** (invitation en collaborateur), pas du travail à produire |

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
