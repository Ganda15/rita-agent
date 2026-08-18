# ÉTAT — où on en est

> **Ce fichier se périme.** Il porte l'état du jour ; `CLAUDE.md` porte ce qui ne change pas.
> À relire au démarrage de chaque session, à mettre à jour à la fin.

**Dernière mise à jour : 2026-08-17** · deadline livrables **05/11/2026** · jury **30/11–01/12**

🆕 **Séance de veille S34 du 17/08 — ce qu'elle a changé dans le code.** Commit `c7c8811`.
- Le **garde-fou de sortie** (interdit AMF) était invoqué par `guardrails/injection.py:9`
  et **n'existait pas** ; `api/main.py` diffusait le texte du modèle sans contrôle. Écrit
  (`guardrails/sortie.py`), câblé sur `/briefing`, mesuré (`evals/mesurer_sortie.py`).
- Le **100 % du garde-fou d'entrée était circulaire** : 7 cas de test pour 9 motifs, un pour
  un. 3 cas adverses ajoutés → **taux réel 70 %**, faux positifs 0 %.
- ⚠️ **`tests/test_evals.py` est ROUGE et doit le rester** (70 % < seuil 85 %). Ne pas
  baisser le seuil : l'arbitrage est la question ouverte de S35. Suite : `200 passed, 1 failed`.
- Le **garde-fou de sortie mesure aussi 70 %** — motifs écrits d'abord, cas d'évasion ensuite.
- Deux guides d'étude en anglais : `docs/etude/` (les concepts, et la méthode).

📅 **Le plan des 12 semaines est écrit : `docs/PLAN-12-SEMAINES.md`.**
Le formateur est en congé → on ne l'attend pas : **produire → geler → mettre en file
(`docs/FILE-DE-VALIDATION.md`) → continuer.**

---

## ▶️ Comment Era reprend le travail

1. Ouvrir Claude Code sur le dossier **`D:\KandaWork\RITA_PROJECT\rita-agent`**
   (jamais sur `C:\Users\kanda` — sinon rien ne se charge).
2. Écrire : **« on reprend »**.
3. Claude lit ce fichier et annonce en 3 lignes : où on s'est arrêté, la prochaine action,
   les verrous. Era n'a **rien** à réexpliquer.

---

## 🧭 Prochaine action

🚩 **Le point de contrôle du 23/08 est atteint dès le 16/08.** L'application démarre et
affiche le portefeuille réel depuis l'API. La semaine S34 est donc **libre pour aller plus
loin que prévu**.

**Prochaines actions, dans l'ordre :**

0. 🔴 **FINIR LA NOTE S34 — 1 section, ~5 lignes.** ⚠️ Correction du 17/08 en fin de
   journée : le tableau d'analyse de fiabilité **était déjà écrit** (lignes 32-73, avec les
   deux arbitrages justifiés) — cette liste le disait manquant à tort. Il ne reste que :
   - le **résumé en clair** (ligne 9, `docs/veille/2026-S34-top10-agentique.md`) — brouillon
     proposé, à reprendre avec les mots d'Era avant de le fixer.

   Puis les 7 cases d'accessibilité en bas (aucune cochée pour l'instant), puis commit.
   ⚠️ **Ne pas passer aux actions suivantes avant.** Une note à 90 % ne prouve rien, et le
   contexte se perd en une nuit. Méthode pas à pas :
   `docs/etude/STUDY-GUIDE-session-2026-08-17-EN.md` §10.

1. 🟠 **`taux_change` est vide** — les taux BCE n'ont pas été réimportés. Sans eux,
   `COALESCE(t.valeur_pour_eur, 1)` retombe sur 1 : **aucune conversion n'est appliquée**.
   Sans effet aujourd'hui (les 7 positions sont en euros), **faux dès la première ligne en
   devise**. Relancer `sources/ecb.py`. *(Révélé par un `EXPLAIN ANALYZE` : `Seq Scan on
   taux_change … rows=0.00`.)*
2. 🟡 **`ANALYZE;`** — les statistiques du planificateur sont périmées depuis la
   reconstruction (il estime 550 lignes dans `position` là où il y en a 7).
3. **Les deux schémas obligatoires de E4**, jamais faits :
   - **wireframes** des 3 états de l'écran → **C14** (*« modélisation des parcours
     utilisateurs : schéma fonctionnel, wireframes »*)
   - **diagramme de flux de données** de l'application → **C15**
   *(Le MCD Merise existant satisfait déjà le volet « modélisation des données » de C14.)*
4. **Écran 2 — les indicateurs**, 9 colonnes du lot 1 (`docs/indicateurs/CONCEPTION.md`).
   ⚠️ Le moteur existe déjà, écrit par Era hors de ce dépôt : `quant_metrics.py` dans
   `Ganda15/daily-stock-analysis-era` (350 lignes, 13 fonctions, 9 tests verts). **Le porter
   plutôt que le réécrire.**

Deux tâches courtes à caser dans la même semaine :
1. **Note de veille S34**, lundi 17/08 09h00 (créneau fixe, ne cède jamais sa place).
2. **Capturer le fil Discord** — la note S33 y a été postée le **16/08** avec une question
   ouverte. ⚠️ **Attendre 1 à 2 jours** : ce sont les *réponses* qui prouvent l'animation du
   travail collectif, pas le message. Capture → `evidence/C6/discussion-2026-08-__-discord.png`.
   *(L'envoi au formateur reste bloqué par son congé — en file, voir
   `docs/FILE-DE-VALIDATION.md`.)*

✅ **Les deux trous du 14/08 sont comblés** (`docs/veille/README.md`) :
- **§5** — le partage : destinataires, cadence (mensuel au formateur, à chaque note pour la
  promo), registre de trace, et les faiblesses déclarées.
- **§4** — les deux outils : `sources/rss.py` est **l'outil de C6** ; `Veille-IA` est une
  veille personnelle **hors C6** — sa sortie est rédigée par un LLM, ce qui en ferait une
  preuve fabriquée. Mesuré le 15/08 : à l'arrêt depuis le 27/07.

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
| **E4** — Application | C14–C19 | 🔨 **démarré le 16/08** — 1er écran livré | — |
| **E5** — Monitorage | C20–C21 | ⬜ non commencé | — |

## Ce qui existe vraiment, compétence par compétence

| C | Fait | Manque |
|---|---|---|
| **C1** | 7 sources, les 5 types, script en 6 points | invitation `bybysker` en attente d'acceptation |
| **C2** | 3 requêtes SQL, optimisation LATERAL mesurée ×2000 | — |
| **C3** | `pipelines/ingest.py`, 15 tests, règles justifiées par mesure | invitation en attente d'acceptation |
| **C4** | MCD Merise 6 entités, MPD 8 tables, registre RGPD, purge testée | — |
| **C5** | 6 endpoints, OpenAPI 3.1.0, auth au niveau routeur, 25 tests | — |
| **C6** | protocole **complet** (15/08), gabarit, récurrence, registre, note S33 (14/08), **partage promo lancé le 16/08 sur Discord** | ⚠️ ~11 notes à venir · 🟠 réponses Discord à capturer · 🔴 envoi **formateur** non fait (congé) |
| **C7** | **rien** — aucun benchmark de services IA | tout |
| **C8** | cascade 3 fournisseurs testée, clé en `.env` | monitorage du service · doc d'exploitation |
| **C9** | `POST /briefing`, auth 403, OpenAPI, garde-fou injection | revue OWASP · doc d'architecture · invitation en attente |
| **C10** | 🔨 **16/08** — `frontend/` : écran portefeuille servi par l'API, authentification par clé saisie (jamais en dur), 403 et erreurs traités, RGAA (`caption`, `scope`, `aria-live`, signe explicite), **15 tests** dont 2 de non-régression du montage | autres points de terminaison · doc d'architecture |
| **C11** | **rien** | tout |
| **C12** | 201 tests, 15 cas d'éval, seuils non compensables en CI | ⚠️ **couverture non mesurée** (`pytest-cov` absent) · DVC · 🔴 **aucun test ne se connecte à la vraie base** — tous simulent `_executer`, d'où un défaut C4 invisible pendant des semaines |
| **C13** | GitHub Actions, 2 jobs, porte garde-fous | packaging · Docker · déploiement · test des données |

## Les 5 manques ouverts, par urgence

0. 🔴 **AUCUNE SAUVEGARDE DE LA BASE.** Découvert le 16/08 de la pire façon : la base
   `rita` **n'existait plus**. PostgreSQL 18 avait été réinstallé, vide — ni base, ni rôle.
   Reconstruite le soir même par `db/importer.py` depuis les Parquet, **au chiffre près**
   (111 valeurs · 112 alias · 2 560 dédoublonnées · 273 608 insérées · 7 positions).
   *Rien n'a été perdu parce que les sources étaient versionnées — pas parce qu'il y avait
   une sauvegarde.* → **`pg_dump` hebdomadaire, le lundi après la note de veille.**
1. 🔴 **C6 — la récurrence ET le partage.** Le seul qui **ne se rattrape pas** : 12 semaines
   restantes au 14/08, une semaine perdue = une preuve perdue définitivement. Depuis le
   15/08 le protocole est complet ; **1 partage sur 2 fait** (promo Discord le 16/08,
   formateur toujours bloqué par son congé).
2. 🟠 **Accès au dépôt — invitation envoyée, pas encore acceptée.** Vérifié sur GitHub le
   14/08 : `bybysker` a été invité le **13/08 à 15h16** en droit `read`. Il est dans
   `/invitations`, **pas encore dans `/collaborators`** — donc le critère *« accessible
   depuis un dépôt Git »* (C1#6, C3#2, C9) n'est **pas encore satisfait**.
   **Reste à faire** : relancer si l'invitation n'est pas acceptée · inviter le **jury**
   le moment venu. Commande de vérification :
   `gh api repos/Ganda15/rita-agent/collaborators --jq '.[].login'`
3. 🟠 **Couverture de tests non mesurée** (C12) — `pytest-cov` à brancher, seuil à fixer.
4. 🟠 **Chaîne de LIVRAISON absente** (C13) — aujourd'hui c'est de l'intégration continue.
5. 🟡 **Revue OWASP API Top 10** (C9) non écrite. Deux entrées déjà identifiées :
   **API2** — `os.getenv("RITA_API_KEY", "dev-key")` accepte une clé par défaut devinable
   si la variable est absente (et elle l'est) · **A03** — le front n'utilise que
   `textContent`, jamais `innerHTML` : à documenter comme mesure prise.
6. 🟡 **`.env.example` ne permet pas de démarrer le projet** — il documente `POSTGRES_URL`
   port **5432**, alors que le code lit `DATABASE_URL` et que le serveur écoute sur **5433**.
   Un évaluateur qui le suit échoue. Cinq minutes à corriger.
7. 🟡 **`python-dotenv could not parse statement starting at line 5`** — s'affiche à chaque
   démarrage. Sans conséquence, mais pollue toutes les sorties.
8. 🟠 **`taux_change` est vide** — voir « Prochaine action », point 1.

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
- **Le nom du projet — 16/08.** L'expansion du sigle passe de *« Retrieval Intelligence for
  **Trading** Analysis »* à *« Retrieval Intelligence pour le **Tracking** et l'Analyse »*.
  « Trading » = acheter et vendre, ce que RITA refuse de conseiller : le nom contredisait le
  garde-fou AMF dans la même en-tête. **Le sigle RITA ne change pas** — tag, dépôt, journal
  et preuves restent valides.
- **Le front est en HTML/CSS/JS servi par FastAPI — 16/08.** Pas de React, pas de build.
  Trois raisons tirées du texte des critères : l'éco-conception de C17 récompense le léger ·
  le RGAA se contrôle ligne par ligne sur du HTML · Era doit pouvoir défendre chaque ligne
  pendant 20 minutes. **Règle : générer la surface (CSS, mise en page), écrire soi-même la
  couture** (`frontend/app.js` — appels API, authentification, erreurs), car c'est elle
  qui relève de C10 et c'est elle que le jury interrogera.
- **E4 n'est pas six compétences de développement, c'en est une — 16/08.** C14 = spécifications
  et wireframes · C15 = architecture et déploiement en pré-production · C16 = **méthode agile**
  (kanban, backlog, rituels — aucune ligne de code) · **C17 = le seul développement** ·
  C18 = intégration continue · C19 = livraison continue. **C18 et C19 recouvrent largement
  C13 : une seule chaîne CI/CD prouve trois compétences.**
- **Indicateurs de marché — 15/08.** 19 proposés → **13 à coder**, en 4 lots. Le mot
  « stratégie » est banni (indicateur = fait, stratégie = conseil → garde-fou AMF). Sharpe
  écarté. Destination **E4**, pas C2. Spécification figée :
  `docs/indicateurs/CONCEPTION.md`. **Rien à coder avant l'ouverture d'E4** — ne pas rouvrir
  le débat, lire le fichier.
