# Journal des livrables et décisions — RITA

> **Append-only** : on ajoute en haut, on ne réécrit **jamais** une entrée passée.
> Le présent est dans `ETAT.md` · le pourquoi détaillé dans le journal Obsidian ·
> le détail technique dans `git log`.
>
> **Une entrée = un livrable envoyé, une décision structurante, ou un manque découvert.**
> Pas les commits de code : Git les garde mieux, horodatés et infalsifiables.

---

## 2026-08-14 — C6 : la veille est lancée

- **Thématique arrêtée** : **sécurité des agents LLM — l'injection de prompt**. Retenue parce
  qu'elle porte sur un risque **réel** du projet (RITA lit des pages et des flux écrits par des
  tiers) et sur un outil qu'il possède déjà (`guardrails/injection.py`), pas sur un sujet
  choisi pour l'exercice.
- **Ajouté** `docs/veille/README.md` — le protocole : 7 sources **pesées une par une** sur les
  critères de fiabilité du référentiel (auteur identifié, notoriété, intérêts), dont deux
  gardées **sous condition** (éditeurs de modèles = intérêt commercial ; arXiv = non relu par
  les pairs), trois écartées avec motif. Outil d'agrégation : **RSS via `sources/rss.py`**, le
  code que le projet possède déjà — **budget 0 €**. Plus les 7 règles d'accessibilité
  appliquées à chaque note.
- **Ajouté** `docs/veille/_MODELE-note-hebdomadaire.md`, avec la section obligatoire
  **« Ce que ça change dans RITA »** et une liste de contrôle d'accessibilité.
- **Récurrence en place** : tâche planifiée `veille-hebdo-securite-llm`, **lundi 09h00**.
- **Décidé** : la tâche planifiée **prépare** une liste de candidats, elle **n'écrit pas la
  note**. *Une note de veille produite par une IA serait une preuve fabriquée devant le jury —
  et ne prouverait aucune compétence.*
- **Reste** : les notes elles-mêmes. **0 écrite à ce jour.**

## 2026-08-14 — Continuité entre sessions

- **Ajouté** `CLAUDE.md` (identité du projet, invariante) et `ETAT.md` (état du jour) à la
  racine du dépôt, plus ce `CHANGELOG.md`. Le rituel début/fin de session est inscrit en
  tête de `CLAUDE.md`.
- **Décidé** : `ETAT.md` devient la **source unique** de l'état. `BOUSSOLE-RITA.md` (Bureau)
  passe en archive — elle vivait hors du dépôt, ne se chargeait que si on pensait à
  l'ouvrir, et s'est retrouvée fausse sur 3 points le 13/08.
  *Deux fichiers pour un même rôle finissent toujours par se contredire.*
- **Ajouté** `C:\Users\kanda\.claude\CLAUDE.md` — règles de travail valables dans tous les
  projets, pour ne plus dépendre de la mémoire rangée par dossier.
- **Découvert** : le vrai vault Obsidian est
  `C:\Users\kanda\Documents\Formation-IA\Formation-IA\`. Les deux dossiers de `D:\` qui
  ressemblent à des vaults sont des **leurres vides** datés de mai 2026. Le journal RITA
  n'avait jamais bougé — c'est la méthode de recherche qui était mauvaise (`find` sur le
  disque au lieu du MCP Obsidian).
- **Rédigé** dans le modèle Simplon (`D:\KandaWork\RITA_PROJECT\Era-Preparation-livrables-RNCP.xlsx`) :
  C1 C2 C3 C4 C5 C8 C9 C12 C13. **C6, C7, C10 et C11 laissés délibérément vides — rien n'est
  fait.** Une cellule vide se rattrape ; une affirmation fausse devant le jury, non.
- **Vérifié sur GitHub** (`gh api`) l'état réel de l'accès au dépôt, au lieu de le supposer :
  dépôt `PRIVATE`, un seul collaborateur (`Ganda15`, admin), et **une invitation envoyée le
  13/08 à 15h16 à `bybysker` en droit `read`, toujours en attente d'acceptation**.
  L'action a donc bien été faite le 13/08 — mais tant que l'invitation n'est pas acceptée,
  le critère *« accessible depuis un dépôt Git »* n'est pas satisfait.
  *Une invitation envoyée n'est pas un accès donné.*
- **Manque confirmé, le plus urgent** : C6 exige *« à minima une récurrence d'une heure
  hebdomadaire »*. `docs/veille/` ne contient que `.gitkeep`. **12 semaines avant la
  deadline** — c'est le seul critère qui ne se rattrape pas rétroactivement.

## 2026-08-13 — Livrable E1 envoyé · tag `livrable-E1-v1`

- **Livré** E1 (C1–C5) — **26 critères sur 28**.
- **Restent** C1#6 et C3#2 : *« accessible depuis un dépôt Git »*. Le dépôt est privé —
  c'est un **accès à donner** (invitation en collaborateur), pas du travail à produire.
- **Décidé** : le dépôt **reste privé**, accès par invitation. Décision assumée, pas un oubli.
- **Corrigé** le `README.md` : retrait de Prometheus, Grafana, Docker et d'une version de
  Python — tous annoncés alors qu'ils n'existent pas dans le projet.
  *Un README qui promet ce qui n'existe pas est un mensonge au jury.*
- **Bascule** de la tâche principale : **E1 → E3**.

## 2026-08-11 — Preuves C4 remises dans le dépôt

- **Découvert** que `evidence/C4/` était **vide** alors que le MCD Merise existait depuis le
  01/08 : il n'avait jamais été copié dans le dépôt. Corrigé le jour même
  (`.png`, `.drawio`, `preuve-mcd-merise.md`).
- **Corrigé** `evidence/README.md`, qui annonçait encore l'état du 28/07 — soit le premier
  fichier qu'un évaluateur ouvre.
  *Un document d'état daté reste faux tant que personne ne lit la date.*
- **Corrigé** le compte de tables : le texte annonçait 7 tables en se contredisant avec son
  propre tableau (6 entités + 2 tables techniques = **8**). Vérifié en rejouant
  `db/schema.sql` sur une instance neuve.
