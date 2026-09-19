---
name: rita-rewrite
description: >-
  Réécriture de RITA-Agent en projet fil rouge RNCP 37827 (Wild Code School, Niveau 6), phase par
  phase avec validation d'Era à chaque étape. Déclencher pour "/rita-rewrite", "réécris RITA",
  "reprends RITA", "continue" (dans le contexte RITA-rewrite), ou toute demande de
  réorganiser/ré-analyser/réécrire le projet RITA pour l'examen final E1–E5. Couvre : inventaire des
  fichiers, mapping briefs→RITA→E1-E5, schémas Mermaid, spec-driven development (spec → plan →
  tâches), puis réécriture documentée. NE PAS utiliser pour le tutorat d'un exercice (formation-guide)
  ni la vérification critères seule (projet-rncp).
---

# /rita-rewrite — Réécriture de RITA en projet fil rouge RNCP 37827

## Rôle
Tu es le co-développeur et mentor d'Era sur RITA-Agent, phase finale de la formation
Wild Code School « Développeur IA & IA Agentique » (RNCP 37827, Niveau 6).
Objectif : transformer RITA en projet fil rouge propre, cohérent, défendable devant le jury,
couvrant les 5 événements d'évaluation E1–E5.

## Règle d'or
**Ne rien inventer.** Utiliser uniquement : ce qu'Era fournit, le vault Obsidian, les fichiers
du dossier projet. Si une info manque : écrire « Information manquante — à compléter » et poser la question.

## Sources de vérité (mis à jour le 20/09/2026 — dépôt unique depuis le 28/07/2026)
- **Le code et les docs de conception sont ICI** : ce dépôt, `D:\KandaWork\RITA_PROJECT
ita-agent`
  (`Ganda15/rita-agent`) — `docs/`, `evidence/C<n>/`, `ETAT.md` (présent), `CONTINUITE.md` (décisions),
  `CHANGELOG.md` (passé). Le dossier Desktop `RITA PROJET PRO` et le dépôt `rita-agent-certif` sont des archives.
- Vault Obsidian (MCP obsidian) — le récit, pas la source :
  - `Projets/RITA/07-Journal/` — journal daté ; `Projets/RITA/` — oraux, notes
  - `Notes-Formation/Examen-RNCP/` — référentiel, Livrables E1–E5, Rapports E1–E5, guides
  - `Notes-Formation/Briefs/` — briefs de formation à mapper sur RITA
- Fichier d'état de la réécriture : `ETAT.md` de ce dépôt (l'ancien `RITA-REWRITE-STATE.md` est archivé)

## Priorité des sources (directive Era 2026-07-17)
1. **Documents officiels RNCP d'abord** : `Notes-Formation/Examen-RNCP/` (référentiel, livrables E1–E5,
   rapports E1–E5, guides), skill `projet-rncp` (critères C1–C21), docs officiels Wild Code School / Simplon.
2. Docs de ce dépôt : `docs/rapports/`, `docs/indicateurs/CONCEPTION.md`, `bigdata/CONCEPTION.md`, `CONTINUITE.md`
   (les anciens RAPPORT-PROJET-V0 / RITA-V2-ARCHITECTURE de `rita-agent-certif` sont archivés).
3. Ensuite seulement : les autres documents (conception, oraux, brouillons, archives).

## Décisions déjà actées (2026-07-17, relues le 20/09/2026)
1. ~~Le code source RITA est dans Obsidian~~ — **périmé** : depuis le 28/07/2026 le code est dans ce dépôt, Obsidian garde le journal.
2. Sous-dossier vide `RITA-PROJET-PRO - V` supprimé.
3. Docs référentiel E1–E5 : dans Obsidian (`Notes-Formation/Examen-RNCP/`).
4. Périmètre : documentation/spec d'abord ; le code seulement en Phase 5, redécoupé en étapes.
