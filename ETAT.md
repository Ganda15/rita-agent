# ÉTAT — où on en est

> **Ce fichier se périme.** Il porte l'état du jour ; `CLAUDE.md` porte ce qui ne change pas.
> À relire au démarrage de chaque session, à mettre à jour à la fin.

**Dernière mise à jour : 2026-08-14** · deadline livrables **05/11/2026** · jury **30/11–01/12**

---

## ▶️ Comment Era reprend le travail

1. Ouvrir Claude Code sur le dossier **`D:\KandaWork\RITA_PROJECT\rita-agent`**
   (jamais sur `C:\Users\kanda` — sinon rien ne se charge).
2. Écrire : **« on reprend »**.
3. Claude lit ce fichier et annonce en 3 lignes : où on s'est arrêté, la prochaine action,
   les verrous. Era n'a **rien** à réexpliquer.

---

## 🧭 Prochaine action

**Trancher les deux trous du protocole de veille C6** — repérés le 14/08 en relisant
JOURNAL-005 :

1. **La veille partagée n'est pas traitée.** Deux critères sur huit exigent qu'elle soit
   *« communiquée aux parties prenantes »* et menée *« en animant le travail collectif »*.
   **Une veille solo n'en coche aucun.** → décider **à qui** les synthèses sont envoyées.
2. **L'outil de veille existant est ignoré** : `C:\Users\kanda\Desktop\Veille-IA\` (Google
   News, Hacker News, arXiv, envoi Telegram). Le protocole propose RSS via `sources/rss.py`
   sans le mentionner. → dire **lequel fait quoi**.

✅ **Note S33 faite le 14/08** — `docs/veille/2026-S33-injection-de-prompt.md`
(OWASP Top 10 2026 vérifié à la source · trifecta : 2 conditions sur 3, la 3ᵉ absente par
construction · agent sans outil ni écriture en base). **1 note sur ~12.**

- Gabarit : `docs/veille/_MODELE-note-hebdomadaire.md`
- Protocole complet (sources, fiabilité, accessibilité) : `docs/veille/README.md`

Thématique arrêtée le 14/08 : **sécurité des agents LLM — injection de prompt**. Choisie
parce qu'elle est déjà branchée sur `guardrails/injection.py` et `evals/cas.py` : chaque note
finit par « ce que ça change dans RITA », ce qui satisfait le *« formuler des recommandations
pour le projet »* du référentiel sans travail supplémentaire.

⏰ Récurrence en place : tâche planifiée `veille-hebdo-securite-llm`, **tous les lundis 09h00**.
Elle prépare une liste de candidats — **elle n'écrit pas la note** (une note produite par une
IA serait une preuve fabriquée).

---

## Les 5 livrables

| Épreuve | Compét. | État | Tag Git |
|---|---|---|---|
| **E1** — Données | C1–C5 | ✅ **livré** — 26 critères / 28 | `livrable-E1-v1` |
| **E2** — Veille & services IA | C6–C8 | 🔴 C6 et C7 **non commencés** · C8 partiel | — |
| **E3** — API modèle & MLOps | C9–C13 | 🔨 C9/C12/C13 partiels · C10 et C11 **non commencés** | — |
| **E4** — Application | C14–C19 | ⬜ non commencé | — |
| **E5** — Monitorage | C20–C21 | ⬜ non commencé | — |

## Ce qui existe vraiment, compétence par compétence

| C | Fait | Manque |
|---|---|---|
| **C1** | 7 sources, les 5 types, script en 6 points | invitation `bybysker` en attente d'acceptation |
| **C2** | 3 requêtes SQL, optimisation LATERAL mesurée ×2000 | — |
| **C3** | `pipelines/ingest.py`, 15 tests, règles justifiées par mesure | invitation en attente d'acceptation |
| **C4** | MCD Merise 6 entités, MPD 8 tables, registre RGPD, purge testée | — |
| **C5** | 6 endpoints, OpenAPI 3.1.0, auth au niveau routeur, 25 tests | — |
| **C6** | protocole, gabarit, récurrence (tâche planifiée + agenda), **1re note écrite le 14/08 (S33)** | ⚠️ ~11 notes à venir · la veille **partagée** (2 critères sur 8) non traitée |
| **C7** | **rien** — aucun benchmark de services IA | tout |
| **C8** | cascade 3 fournisseurs testée, clé en `.env` | monitorage du service · doc d'exploitation |
| **C9** | `POST /briefing`, auth 403, OpenAPI, garde-fou injection | revue OWASP · doc d'architecture · invitation en attente |
| **C10** | **rien** — `frontend/` est vide | tout |
| **C11** | **rien** | tout |
| **C12** | 186 tests, 15 cas d'éval, seuils non compensables en CI | ⚠️ **couverture non mesurée** (`pytest-cov` absent) · DVC |
| **C13** | GitHub Actions, 2 jobs, porte garde-fous | packaging · Docker · déploiement · test des données |

## Les 5 manques ouverts, par urgence

1. 🔴 **C6 — récurrence hebdomadaire de veille.** Le seul qui **ne se rattrape pas** :
   12 semaines restantes au 14/08, une semaine perdue = une preuve perdue définitivement.
2. 🟠 **Accès au dépôt — invitation envoyée, pas encore acceptée.** Vérifié sur GitHub le
   14/08 : `bybysker` a été invité le **13/08 à 15h16** en droit `read`. Il est dans
   `/invitations`, **pas encore dans `/collaborators`** — donc le critère *« accessible
   depuis un dépôt Git »* (C1#6, C3#2, C9) n'est **pas encore satisfait**.
   **Reste à faire** : relancer si l'invitation n'est pas acceptée · inviter le **jury**
   le moment venu. Commande de vérification :
   `gh api repos/Ganda15/rita-agent/collaborators --jq '.[].login'`
3. 🟠 **Couverture de tests non mesurée** (C12) — `pytest-cov` à brancher, seuil à fixer.
4. 🟠 **Chaîne de LIVRAISON absente** (C13) — aujourd'hui c'est de l'intégration continue.
5. 🟡 **Revue OWASP API Top 10** (C9) non écrite.

## Fichiers de suivi hors dépôt

| Quoi | Où |
|---|---|
| Rédaction par compétences (modèle Simplon, à rendre) | `D:\KandaWork\RITA_PROJECT\Era-Preparation-livrables-RNCP.xlsx` |
| ⤷ rempli pour | C1 C2 C3 C4 C5 C8 C9 C12 C13 — les autres **volontairement vides** |
| Boussole (tâche principale + pile de détours) | `C:\Users\kanda\Desktop\RITA PROJET PRO\BOUSSOLE-RITA.md` |
| Journal (7 entrées, JOURNAL-000 → 005) | `C:\Users\kanda\Documents\Formation-IA\Formation-IA\Projets\RITA\07-Journal\` — ou via le MCP Obsidian : `Projets/RITA/07-Journal/` |

## Décisions prises, à ne pas re-débattre

- Dépôt **privé** avec accès collaborateur — décision assumée, pas un oubli.
- Une seule clé d'API (mono-utilisateur, décision D10) — pas de système de comptes.
- `article` et `memory_audit` hors du MCD : collecte brute et journal technique ne sont pas
  des entités métier. 6 entités + 2 tables techniques = 8 tables.
- `/briefing` relève de **C9**, pas de C5 : c'est une rédaction, pas de la donnée.
