# File de validation — ce qui attend le formateur

> **Créée le 2026-08-16**, parce que le formateur est en congé et que le travail ne peut pas
> attendre son retour. Règle appliquée : `docs/PLAN-12-SEMAINES.md` §3 —
> **on produit → on gèle → on met en file → on continue.**

## Pourquoi ce fichier existe

L'ordre imposé par le formateur — *une compétence prouvée → envoyée en revue → puis la
suivante* — sert à empêcher d'empiler du travail non relu. **Il ne dit pas d'attendre un
absent.**

Ce registre est ce qui rend la démarche défendable devant un jury : il montre une recherche
de validation **systématique et datée**. Ce qui se reproche, c'est de n'avoir jamais cherché
la validation — pas d'avoir continué à produire pendant l'absence du relecteur.

## Comment on s'en sert

1. Dès qu'un livrable est **gelé** (commité, tests verts, liens vérifiés), on ajoute une ligne.
2. **Rien n'attend dans la file pour démarrer la suite.** La file est une boîte d'envoi, pas
   une salle d'attente.
3. Au retour du formateur : envoi **un par un, dans l'ordre de la file** — pas tout d'un bloc.
   Trois livrables envoyés le même jour reçoivent un seul retour, superficiel.
4. Un retour reçu se note **le jour où il arrive**, avec ce qu'il change.

⚠️ **Ce fichier ne remplace pas `docs/veille/_JOURNAL-DES-ENVOIS.md`** : celui-là trace le
partage **de la veille** (critère C6). Celui-ci trace la **validation des livrables**. Deux
besoins, deux registres.

---

## ⛔ La règle d'envoi : le lien du TAG, jamais l'adresse du dépôt

> **Le problème, constaté le 18/08/2026.** `main` est la branche par défaut : c'est elle que
> GitHub affiche à qui ouvre le dépôt. Or `main` **avance** — au 18/08 elle comptait déjà
> **29 commits de plus** que le tag `livrable-E1-v1`, dont le renommage du projet, le premier
> écran d'E4 et la reconstruction de la base.
>
> Un formateur qui ouvre `github.com/Ganda15/rita-agent` ne voit donc **pas** le livrable E1 :
> il voit le projet d'aujourd'hui. Il jugerait E1 sur du travail qui n'en fait pas partie.

**Ce qui règle le problème, et qui existe déjà** : chaque livrable est figé par un tag. Il
suffit d'envoyer **l'adresse du tag**.

| ❌ Ne jamais envoyer | ✅ Toujours envoyer |
|---|---|
| `https://github.com/Ganda15/rita-agent` | `https://github.com/Ganda15/rita-agent/tree/livrable-E1-v1` |

### Vérifier avant d'envoyer — quatre commandes

La première est la **Definition of Done** (ajoutée le 19/09/2026) : cinq contrôles, un verdict
généré depuis leurs codes de sortie. Rien ne se tague tant qu'une ligne est rouge.

```powershell
C:\Python314\python.exe scripts\verifier_livrable.py livrable-E1-v1
```
```powershell
gh api repos/Ganda15/rita-agent/git/ref/tags/livrable-E1-v1 --jq .object.sha
```
```powershell
gh api repos/Ganda15/rita-agent/collaborators --jq ".[].login"
```
```powershell
C:\Python314\python.exe scripts\verifier_liens.py
```

-1. **La pull request `develop → main` est fusionnée** après la revue automatisée (`Revue PR`) :
   `gh pr create --base main --head develop`, lire les commentaires, corriger, fusionner sur GitHub.
   Le tag se pose sur `main`, jamais sur `develop` (depuis le 19/09/2026 ; avant : fusion directe).
0. **La Definition of Done est verte** : tests + couverture ≥ 90 %, portes d'évaluation,
   liens internes, tag cité dans `ETAT.md` et `CHANGELOG.md`, arbre git propre.
1. **Le tag existe** sur GitHub, et pointe où on croit.
2. **Le lien du tag s'ouvre pour le destinataire.** Au 16/11, le dépôt est encore privé : vérifier que le
   destinataire est collaborateur (une invitation envoyée n'est pas un accès donné). Publication prévue juste
   après les tags du 16/11, par un changement de visibilité ; ensuite, ouvrir le lien sans connexion, dans une
   fenêtre privée.
3. **Zéro lien cassé** dans le dépôt.

### Gabarit du message

> Bonjour,
>
> Le livrable **E1 — Données (C1 à C5)** est prêt. Deux éléments :
>
> - **Le rapport** : `rapport-E1.pdf` (ci-joint)
> - **Le code, figé au jour de l'envoi** :
>   <https://github.com/Ganda15/rita-agent/tree/livrable-E1-v1>
>
> ⚠️ Ce lien pointe sur un **tag Git**, pas sur la branche principale. Il montre le dépôt
> exactement tel qu'il était lors de la remise. La branche principale, elle, continue
> d'avancer avec les livrables suivants — l'ouvrir donnerait une image faussée d'E1.
>
> [Seulement une fois le dépôt rendu public et le lien ouvert sans connexion :] Le dépôt est public : le lien
> du tag s'ouvre sans compte GitHub.
>
> Bien à vous,
> Eramalingam GANDAKUMAR

**Pourquoi expliquer le tag dans le message** : personne n'est tenu de connaître cette
convention. Un lien qu'on ne comprend pas est un lien qu'on remplace par celui qu'on connaît.

### ⚠️ Le piège du tag — rencontré deux fois

**Un tag ne suit pas les commits** : il reste sur celui où on l'a posé. Tant que le lien
**n'est pas parti**, on peut le déplacer. **Une fois parti, on ne le déplace plus** — on crée
un `-v2`, sinon le destinataire et l'expéditeur ne regardent plus la même chose.

Et GitHub refuse `git push --force` sur un tag annoté (erreur 500). La séquence qui marche :

```powershell
git push origin refs/tags/livrable-E1-v1:refs/tags/livrable-E1-v1
```

---

## La file

> **État au 16/11** : la file ci-dessous s'arrête au 28/10. Depuis, les remises sont consignées dans `CHANGELOG.md` :
> remise du 09/11 (`livrable-E1-v8`, `livrable-E2-v5`, `livrable-E3-v6`, `livrable-E4-v7`, `livrable-E5-v5`), puis versions
> du 16/11 (`livrable-E1-v9`, `livrable-E2-v6`, `livrable-E3-v7`, `livrable-E4-v8`, `livrable-E5-v6`) ; les cinq PDF vont
> dans le Drive du jury le 23/11.

| # | Gelé le | Livrable | Compétences | Tag / commit | Envoyé le | Retour reçu | Ce que le retour change |
|---|---|---|---|---|---|---|---|
| 1 | 2026-08-13 | **E1 — Données** | C1–C5 | `livrable-E1-v1` | ✅ **relu avant le gel** (message « Bloc 1 », début août) | ✅ **3 réponses reçues** — voir ci-dessous | Le cadrage big data d'E1 est **validé** |
| 2 | 2026-08-15 | Protocole de veille C6 (complet) | C6 | `27ff359` | ⬜ | ⬜ | — |
| 3 | 2026-08-15 | Conception des indicateurs (E4) | — *(conception)* | `81780cb` | ⬜ | ⬜ | — |
| 4 | 2026-08-14 | **Note de veille S33** — injection de prompt | C6 | `1da976f` | ⬜ **prête, non partie** | ⬜ | — |
| 5 | 2026-10-24 | **E1 : Données, version 2.6** (5 pages) | C1-C5 | `livrable-E1-v2` (commit `312056a`, livraison N19) | ⬜ | ⬜ | pas encore |
| 6 | 2026-10-24 | **E3 : API du modèle, intégration, monitorage, tests, livraison, version 1.5** (19 pages) | C9-C13 | `livrable-E3-v1` (commit `312056a`, livraison N19) | ⬜ | ⬜ | pas encore |
| 7 | 2026-10-27 | **E1 : Données, livret version 3** (5 pages, chemins cliquables au tag), pour l'oral blanc ; remplace la ligne 5 | C1-C5 | `livrable-E1-v3` (commit `d3a4198`, en production le 27/10) | ✅ **2026-10-28**, sur Discord | ✅ **2026-10-28 : accepté par le formateur** (réponse sur Discord, rapportée par Era ; capture à verser) | E1 v3 retenu pour l'oral blanc ; le budget (C1) reste à chiffrer sur factures dans la v4 |
| 8 | 2026-10-27 | **E3 : rapport version 1.9** (20 pages, sommaire, un cas d'usage par compétence, grille 34 ✅ · 5 🟠), pour l'oral blanc ; remplace la ligne 6 | C9-C13 | `livrable-E3-v2` (commit `d3a4198`, en production le 27/10) ; page du jury `docs/jury/README.md` | ✅ **2026-10-29**, sur Discord : `docs/rapports/E3/rapport-E3-v1.9-bandeau.pdf` (empreinte `579890bfba43e18a`), avec trois précisions écrites dans le message (p. 16 ; AMF, p. 1 et glossaire ; p. 7, 9 et 13) | ⬜ | retour du formateur attendu ; oral blanc le 30/10 |
| 9 | 2026-10-28 | **Grilles des compétences** : grilles d'E1 et d'E3, grille complète, synthèse et classeur détaillé (111 ✅ · 25 🟡 · 1 ❌, auto-évaluation) | C1-C21 | branche `classeur-competences` (commit `c56b899`), jamais fusionnée sans décision d'Era | ✅ **2026-10-28**, sur Discord | ⬜ | pas encore |

**Légende** : ⬜ = pas encore fait · ✅ = fait, avec la date.

### 🔴 28/08 — Retour formateur reçu, noté LE JOUR MÊME

**RAG et MCP sont obligatoires. Text-to-SQL : « pas vraiment ».** Et le RAG doit être
**avancé**. Échange direct avec le formateur, rapporté par Era le 28/08.

*Noté ici le jour même, contrairement aux trois réponses du Bloc 1 qui sont restées non
tracées pendant trois semaines — c'est précisément la faute que ce registre existe pour
éviter.*

⚠️ **Reste à préciser** : pour quel livrable (E3/E4 ?), et ce que « avancé » recouvre
exactement. À poser au prochain échange plutôt qu'à supposer.

---

### 🔴 Correction du 24/08 — ce registre sous-estimait le travail réel

Ce fichier, créé le 16/08, affirmait **« 4 éléments en file, 0 envoyé »**. **C'est faux, et à
la défaveur d'Era** : le **message « Bloc 1 »** (rédigé le 02/08, ajusté le 07/08, conservé dans
le vault Obsidian `Projets/RITA/00-Pilotage/`) **est bien parti**, et le formateur **y a répondu
sur les trois questions** :

| # | Question posée | Réponse |
|---|---|---|
| 1 | La preuve big data couvre-t-elle **C1 seul ou C2 aussi** ? | ✅ accepté |
| 2 | « 276 168 lignes, ce n'est pas du big data — je démontre la **méthode qui scale** » | ✅ accepté — **le cadrage du rapport E1 tient** |
| 3 | LangSmith → sous-traitant **américain**, quel niveau de détail RGPD ? | ✅ OK |

**Nuance de date à ne pas gommer** : cette relecture portait sur l'état d'**avant le gel** ; le
tag `livrable-E1-v1` a été posé le **13/08**, après. Le fond validé est le même, la version
figée est postérieure.

⚠️ **Date exacte et formulation du retour : à reprendre de la capture Discord**, pas d'ici.
Le canal était **GitHub** (accès au dépôt) + **Discord** (le retour lui-même).

> **Leçon, et c'est la 5ᵉ du même genre** : un registre qui n'est pas tenu au fil de l'eau finit
> par **mentir dans les deux sens** — ici il effaçait une validation obtenue. Les quatre autres
> (garde-fou de sortie, `tabindex`, récurrence veille, collecte quotidienne) faisaient l'inverse :
> ils affirmaient un contrôle inexistant.

> **État au 2026-08-16 : 4 éléments en file, 0 envoyé.** Le formateur est en congé.
> **La note de veille S33 est écrite et prête, mais n'est pas partie** — voir la ligne 4
> ci-dessus et `docs/veille/_JOURNAL-DES-ENVOIS.md`, qui reste vide et le dit.

### 🟢 2026-08-24 — LE VERROU SAUTE : la file peut s'ouvrir

Le formateur est de nouveau joignable : **l'invitation du 13/08 a été acceptée**, et il a validé
les points *big data* sans aucune remarque négative à ce jour.

**Les trois vérifications d'avant-envoi ont été passées le 24/08, dans l'ordre du protocole
ci-dessus — les trois sont vertes :**

| # | Vérification | Résultat du 24/08 |
|---|---|---|
| 1 | Le tag existe sur GitHub et pointe où on croit | ✅ `livrable-E1-v1` → objet-tag `85e2adf` → commit **`659c047`**, tagué le **13/08 14h40**. **Local et GitHub identiques** |
| 2 | Le destinataire est bien collaborateur | ✅ `bybysker (read)` dans `/collaborators` · **aucune invitation en attente** |
| 3 | Zéro lien cassé dans le dépôt | ✅ `verifier_liens.py` : 52 fichiers, **74 liens internes + 32 externes, 0 cassé** |

⚠️ **Piège de lecture écarté au passage** : la commande du protocole
(`git/ref/tags/... --jq .object.sha`) renvoie le SHA de l'**objet-tag**, pas celui du **commit** —
il diffère donc de `git rev-parse livrable-E1-v1^{}` en local **sans que rien ne soit anormal**.
Vérifié en déréférençant l'objet-tag côté GitHub : il vise bien `659c047`.
*Ajouter `^{}` pour comparer des commits, sinon on compare une étiquette à une page.*

Le rapport est à `docs/rapports/E1/rapport-E1.pdf`.

**➡️ E1 est prêt à partir. Un seul envoi aujourd'hui** — la règle §3 tient : trois livrables
envoyés le même jour reçoivent un seul retour, superficiel.

---

## Ce qui reste à mettre en file, dans l'ordre du plan

> **État au 16/11** : tout ce tableau est livré (E4, C7 dans E2, E3, E5) ; voir la note en tête de la file.

| Attendu en | Livrable | Compétences |
|---|---|---|
| S39 | **E4 — Application** | C10, C14–C19 |
| S41 | **C7 — Benchmark de services IA** | C7 |
| S42 | **E3 — API modèle & MLOps** : en file depuis le 24/10 (ligne 6) | C9, C11, C12, C13 |
| S43 | **E5 — Monitorage** | C20, C21 |

---

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Geler** (*freeze*) | Arrêter de modifier : commiter, taguer, tests verts, liens vérifiés |
| **Tag Git** | Étiquette posée sur un commit précis, qui permet de retrouver exactement l'état envoyé — même si le code a changé depuis |
| **Mettre en file** | Inscrire ici un livrable prêt, pour ne pas dépendre de la disponibilité du relecteur |
