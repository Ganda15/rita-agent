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

## Les dossiers, chacun avec sa date

Chaque ligne dit de quand elle date. Les lignes `C1/` à `C5/` décrivent les preuves constituées jusqu'au
11/08/2026 (livrable E1, version 1) ; leurs chiffres d'aujourd'hui sont donnés entre parenthèses. Les lignes
suivantes ont été créées ou complétées du 02 au 04/10/2026.

| Dossier | Compétence | Preuve | État |
|---|---|---|---|
| `C1/` | Extraction depuis plusieurs types de sources | 10 preuves — une par source + big data séparée + analyse exploratoire | ✅ **7 sources · les 5 types** |
| `C2/` | Requêtes SQL d'extraction | `preuve-requetes-sql.md` : 3 requêtes, sorties réelles, jointures et optimisations mesurées (4 au 04/10 : R1 bis, positions closes, ajoutée le 03/10 dans `../db/requetes.sql`) | ✅ |
| `C3/` | Règles d'agrégation et nettoyage | 3 preuves — déduplication, artefact de regroupement, pipeline d'agrégation | ✅ |
| `C4/` | Base de données dans le respect du RGPD | `preuve-mcd-merise.md` + le MCD (`.png` et `.drawio`) · MPD dans `../db/schema.sql` · RGPD dans `../db/RGPD-registre-des-traitements.md` | ✅ |
| `C5/` | API et tests | `preuve-api-jeu-de-donnees.md` (OpenAPI 3.1.0, 8 chemins au 11/08 ; 14 au 04/10, dont 11 de données) + `mesure-garde-fou-injection.md` | ✅ |
| `C9/` | API exposant le modèle | `preuve-api-modele-2026-10-03.md` : un briefing réel servi (200, `request_id`, journal), contrat OpenAPI à 14 chemins, tests qui le tiennent, manques (502 au lieu de 422, pas de limite de débit) | ✅ créé le 03/10/2026 |
| `C11/` | Monitorage du modèle | `README.md` (9 critères), `preuve-langfuse-2026-10-03.md` (tableau par l'API, INC-006 recompté, clics restants, première trace complète réelle du 03/10), définition du tableau et export des traces factices en JSON | ✅ depuis le 02/10/2026 |
| `C12/` | Tests automatisés du modèle | `preuve-suite-de-tests-2026-10-03.md` (740 passed, 93,92 %, répartition par fichier, garde-fous mesurés, mutations) · `cas-de-verification-chapitre-donnees.md` (03/10/2026) : les 32 cas du chapitre « Données » rapprochés des tests du dépôt, 23 ✅ 5 🟠 4 ❌, quatre tests écrits le jour même | 🟠 dossier ouvert le 03/10, le reste de C12 est prouvé dans le rapport E3 |
| `C13/` | Chaîne de livraison continue | `preuve-chaine-livraison-2026-10-03.md` : treize exécutions réelles d'une journée (deux pull requests, deux fusions, une alerte manuelle), rulesets GitHub, ce qui n'a jamais tourné (publication sur tag) | ✅ créé le 03/10/2026 |
| `C18/` | Intégration continue | `preuve-integration-continue-2026-10-03.md` : 268 exécutions du workflow Tests depuis le 28/07, 97 vertes sur les 100 dernières, les 3 rouges expliquées, ce que la CI ne fait pas ; mode d'emploi unique dans `../docs/CI-CD.md` | ✅ créé le 03/10/2026 |
| `C6/` | Veille technique et réglementaire | protocole et notes dans `../docs/veille/` — **le dossier de preuves est vide** : rien n'a encore été partagé | 🔴 **1 note sur ~12 · 0 envoi** |
| `C8/` | Paramétrage du service de modèle | `README.md` (03/10/2026) : index des preuves réelles (cascade, briefing réel, trace, guide d'exploitation corrigé), un seul fournisseur opérationnel dit tel quel, remise non prouvée (#43) | 🟠 créé le 03/10/2026 |
| `C10/` | Intégrer l'API dans une application | `preuve-ecran-briefing.md` et `ecran-briefing-2026-10-03.png` (03/10) : l'écran 3 appelle `/briefing`, un briefing réel capturé ; `preuve-passerelle-mcp.md`, `preuve-ecran-indicateurs.md`, hook `bloquer-secrets`, scan Giskard | ✅ complété le 03/10/2026 |
| `C14/` | Spécifications et wireframes des trois écrans | `preuve-specifications-wireframes.md` (écran 1, 18/08, avec un erratum RGAA du 03/10) ; `preuve-specifications-ecrans-2-et-3.md` (03/10, écrites après le code, dit en tête) ; wireframes `.drawio`, `.svg`, `.png` par écran ; `preuve-indicateurs-lot1.md`, `preuve-indicateurs-lot3.md` | 🟠 US-1 à US-3 spécifiées ; défaut #73 relevé en l'écrivant |
| `C16/` | Pilotage Kanban et revues | `preuve-mise-en-place-kanban.md` (26/09) ; `revues/2026-10-05-revue-S41.md` : trame de la première revue notée, préparée le 03/10, **à tenir par Era** | 🟠 tableau en service, aucune revue encore notée |
| `C17/` | Éco-conception et accessibilité des trois écrans | `preuve-eco-conception-et-accessibilite-2026-10-03.md` : Lighthouse 13.5.0 (accessibilité 100 sur 100, zéro échec), parcours au clavier mesuré, EcoIndex officiel (A, A et D), compression mesurée ; dossier `mesures-2026-10-03/` (rapports, résumés, scripts, entrées rejouables) ; `revue-owasp-top10-2025-2026-10-03.md` : revue OWASP Top 10:2025 entrée par entrée, sondes de production, dix constats ; `preuve-droits-acces-2026-10-03.md` : défense de la clé unique, matrice validée confrontée au code | 🟠 mesuré et revu le 03/10 ; corrections après le 15/10 (cartes #74, #75, #76) |
| `C7/` | Banc des fournisseurs de modèle | `preuve-benchmark-2026-10-03.md` : quatre passages le 03/10, dont la première comparaison (Foundry `gpt-5.4` contre OpenRouter `claude-sonnet-4.5`, 30 appels chacun, intervalles de Wilson, latence, coût) ; `prix-et-environnement-2026-10-03.md` : prix publics datés et information environnementale (rien par modèle chez les deux éditeurs, écrit inconnu) ; `indicateurs-cites-dans-les-textes-2026-10-03.md` : 16 indicateurs spécifiés, 13 reçus par le prompt, 9,3 cités par texte, drawdown cité 0 fois sur 60 ; jeu figé, brut en JSONL, résumés JSON, notation à l'aveugle à remplir par Era | 🟠 créé le 03/10/2026, comparaison le soir même |

**Mesuré le 04/10/2026.** Tests : 824 collectés (`pytest --collect-only -q`) ; en intégration continue, 793 passed,
29 skipped, 2 xfailed. Base locale, lue en SQL : 10 tables · 1 vue · 19 objets d'index (8 explicites) ·
12 contraintes `CHECK` · 6 clés étrangères · 278 473 cotations de 111 valeurs (29/07/2016 au 02/10/2026) ·
112 alias · 1 598 articles. Import initial de juillet 2026 : 273 608 lignes. (Le 11/08, ce paragraphe disait :
186 tests, 8 tables, 15 index, 9 contraintes `CHECK`.)

### Les schémas, et où ils sont

| Schéma | Couvre | Emplacement |
|---|---|---|
| Collecte multi-source, tenue à jour (04/10) | **C1** | [`../docs/rapports/E1/schemas/E1-collecte.png`](../docs/rapports/E1/schemas/E1-collecte.png), générée depuis le code |
| Flux de collecte multi-source, preuve datée du 11/08 | **C1** | [`C1/SCHEMA-C1-collecte-multisource.png`](C1/SCHEMA-C1-collecte-multisource.png) (chiffres d'août, voir `C1/README.md`) |
| Nettoyage : défaut mesuré, décision, fichier (04/10) | **C3** | [`../docs/rapports/E1/schemas/E1-nettoyage.png`](../docs/rapports/E1/schemas/E1-nettoyage.png), générée depuis le code |
| *Partition pruning* Parquet + Spark | **C1** | [`../bigdata/schemas/`](../bigdata/schemas/) |
| Les 3 requêtes Spark SQL | **C2** | [`../bigdata/schemas/`](../bigdata/schemas/) |
| MCD Merise | **C4** | [`C4/MCD-MERISE-RITA-2026-11-02.png`](C4/MCD-MERISE-RITA-2026-11-02.png) (`VALEUR 0,n`, décision du 02/11) ; celui du 01/08 : [`C4/MCD-MERISE-RITA.png`](C4/MCD-MERISE-RITA.png) |

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
