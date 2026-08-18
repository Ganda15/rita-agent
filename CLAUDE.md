# RITA — projet fil rouge RNCP 37827

> ## 🚦 À FAIRE AU DÉBUT DE CHAQUE SESSION — avant toute autre chose
>
> 1. **Lire `ETAT.md`** (à la racine, à côté de ce fichier).
> 2. **Annoncer à Era, en 3 lignes** : où on s'est arrêté · la prochaine action · les verrous.
> 3. **Ne rien commencer d'autre** tant que ces 3 lignes ne sont pas dites.
>
> Era peut avoir laissé passer un jour ou trois semaines. Il ne doit **jamais** avoir à
> réexpliquer où on en était : c'est le travail de ce dépôt, pas le sien.
>
> ## 🏁 À FAIRE À LA FIN DE CHAQUE SESSION
>
> 1. **Mettre `ETAT.md` à jour** — prochaine action en tête, état des compétences, manques.
> 2. **Ajouter une entrée à `CHANGELOG.md`** *si et seulement si* il y a eu un **livrable
>    envoyé**, une **décision structurante**, ou un **manque découvert**. Sinon, rien :
>    un changelog nourri de commits devient un doublon de `git log` et meurt en deux semaines.
> 3. **Écrire au journal** si une étape est terminée (voir `ETAT.md` pour le chemin).
>
> Une session qui se termine sans `ETAT.md` à jour est une session à moitié perdue.

> ## 📐 Les 4 fichiers, et leur temps — ne jamais les mélanger
>
> | Fichier | Temps | Règle |
> |---|---|---|
> | `CLAUDE.md` | **toujours vrai** | ce qui reste vrai dans 3 mois |
> | `ETAT.md` | **le présent** | réécrit à chaque session |
> | `CHANGELOG.md` | **le passé** | append-only — **on ne réécrit jamais une entrée** |
> | journal Obsidian | **le pourquoi** | le récit long, pédagogique |
>
> Un fichier qui ne prétend jamais être à jour ne peut pas être périmé.

Eramalingam GANDAKUMAR · Simplon × Wild Code School · deadline livrables **05/11/2026**
Dépôt : `Ganda15/rita-agent` (**privé** — accès par invitation collaborateur)

## Ce qu'est RITA

Collecte de données boursières et macro-économiques → PostgreSQL (conception Merise) →
API REST → briefing **rédigé** en français par Claude.

Une aide à la lecture, **jamais** une recommandation d'achat ou de vente : contrainte AMF,
inscrite en dur dans le prompt du rédacteur et vérifiée par le garde-fou d'injection.

## Stack réelle

- **Python** 3.13 (CI) / 3.14 (local) · **FastAPI** · **PostgreSQL** · **PySpark + Parquet**
- **LangGraph** — graphe Scout → Rédacteur (`graph/workflow.py`)
- **Claude** en cascade 3 fournisseurs : Foundry → Anthropic → OpenRouter (`src/llm.py`)
- **Modèle FOURNI** — aucun entraînement, aucun réglage fin. Ce qui se teste n'est pas une
  métrique d'apprentissage mais le **comportement sous garde-fous**.

## Dossiers

```
agents/     Scout (collecte) + Analyst (rédaction)
api/        FastAPI — /donnees (C5) et /briefing (C9)
bigdata/    PySpark + Parquet — 11 partitions, 10 ans
db/         schema.sql · requetes.sql · registre RGPD · importer.py
docs/       rapports/ (un dossier par épreuve) · veille/ (C6)
evals/      mesure des garde-fous — porte de qualité de la CI
evidence/   preuves par compétence : C1/ … C5/
graph/      LangGraph — état + workflow
guardrails/ garde-fou injection de prompt
pipelines/  ingestion (ingest.py)
scripts/    planification de la collecte
sources/    les 5 types de sources C1
src/        appel du modèle (llm.py)
tests/      pytest — 18 fichiers
```

## Chiffres à ne jamais réinventer — les vérifier avant de les citer

**186** tests · **8** tables · **1** vue · **15** index · **273 608** lignes ·
**111** valeurs · **112** alias · **7** positions · **11** partitions Parquet ·
OpenAPI **3.1.0** · **8** chemins documentés

## Règles de travail

- **Ne rien affirmer sans avoir ouvert le fichier.** Les README mentent en vieillissant :
  `evidence/README.md` annonçait encore l'état du 28/07 le 11/08.
- Un chiffre se cite **mesuré**, jamais estimé. Une cardinalité, une optimisation, un taux
  de blocage : chacun doit pointer vers la commande qui l'a produit.
- Preuves dans `evidence/C<n>/` — **constituées au fil de l'eau, jamais reconstituées après**.
- Ordre imposé par le formateur : une compétence prouvée → envoyée en revue → **puis** la
  suivante.
- Journal écrit **dès qu'une étape est terminée**, sans qu'on le demande :
  fait / pourquoi / raté / preuve.
- Chaque terme technique défini à sa 1re occurrence + **glossaire** en fin de document.
- **Donner le code et la commande — c'est Era qui applique**, sauf s'il dit « do it ».
- Signaler les manques franchement. Un document qui ne signale aucune faiblesse n'est pas
  crédible devant un jury.

## Environnement — pièges de cette machine

- `venv` et `pip.exe` bloqués par AppLocker → utiliser `C:\Python314\python.exe -m pytest -q`
- PostgreSQL sur le port **5433**
- PySpark exige un **JDK 21** dans `JAVA_HOME` — sinon `tests/test_spark.py` est *ignoré*,
  pas en échec
- Fichiers destinés à Excel ou Word : **nom ASCII pur**, sans tiret long `—`, sans accents,
  sans parenthèses — sinon Windows refuse de les ouvrir

## Commandes

```powershell
C:\Python314\python.exe -m pytest -q                          # les 186 tests
C:\Python314\python.exe -m evals.mesurer_gardefou             # taux de blocage + faux positifs
C:\Python314\python.exe -X utf8 -m pipelines.ingest --simulation
C:\Python314\python.exe -m uvicorn api.main:app --reload      # API sur :8000
C:\Python314\python.exe scripts\verifier_liens.py             # liens internes + externes
```

## 📤 Envoyer un livrable — le lien du TAG, jamais celui du dépôt

`main` est la branche par défaut et elle **avance** : au 18/08 elle comptait 29 commits de
plus que le tag `livrable-E1-v1`. Qui ouvre `github.com/Ganda15/rita-agent` voit le projet
**d'aujourd'hui**, pas le livrable.

```
❌  https://github.com/Ganda15/rita-agent
✅  https://github.com/Ganda15/rita-agent/tree/livrable-E1-v1
```

Procédure complète, gabarit de message et vérifications : **`docs/FILE-DE-VALIDATION.md`**.

## 🔗 Avant CHAQUE envoi de livrable — vérifier les liens

```powershell
C:\Python314\python.exe scripts\verifier_liens.py
```

**Zéro lien cassé exigé.** Le script contrôle les liens externes (HTTP) **et** internes (le
fichier visé existe-t-il, et est-il bien **dans** le dépôt). *Un livrable ne pointe jamais
hors du dépôt* — règle établie le 11/08 après avoir trouvé `bigdata/CONCEPTION.md` qui
renvoyait ses schémas vers une adresse Obsidian, invisible pour un évaluateur.

**Ne jamais écrire une URL sans l'avoir testée** — dans un fichier comme dans le chat.

## État des livrables

Voir **`ETAT.md`**. — **Ne jamais écrire l'état du jour dans ce fichier-ci** : ce qui est
ici doit rester vrai dans trois mois.
