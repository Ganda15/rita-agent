# Plan des 12 semaines — du 16/08 au 05/11/2026

> **Établi le 2026-08-16.** Deadline livrables **05/11** · jury **30/11–01/12**.
> Ce plan se périme : quand une semaine est passée, elle ne se rediscute pas.
> L'état du jour reste dans `ETAT.md`.

---

## 1. La bonne nouvelle d'abord — l'oral n'est pas dans les 12 semaines

**Entre le 05/11 (livrables) et le 30/11 (jury) il y a 25 jours.** Le guide d'étude, les
scripts d'oral et les répétitions se préparent **là**, pas maintenant.

➡️ **Les 12 semaines qui viennent sont de la production pure.** Ne pas y mélanger la
préparation de soutenance : c'est le meilleur moyen de ne finir ni l'une ni l'autre.

> ⚠️ **Correction du 29/09/2026 : ce paragraphe est devenu faux.** Le formateur a annoncé deux
> oraux blancs : le **29-30/10** (E1 15 min + E3 20 min + 10 min de retours) et le **12-13/11**
> (situation réelle, 90 min, les cinq). Le premier tombe **dans** les 12 semaines. Règle posée par
> Era le 29/09 : **tout livrable est gelé 2 à 3 semaines avant son passage à l'oral**, parce que
> c'est la présentation qui est notée et qu'elle se prépare sur du figé. Conséquence : E3 et E1
> doivent être gelés le **dimanche 11/10**. Le calendrier du §5 est réécrit à partir de S40 ;
> les semaines passées ne bougent pas.

---

## 2. Le principe qui commande tout : deux types de temps

Le temps d'Era n'est pas homogène. Une semaine de vacances et une soirée après les cours ne
valent pas la même chose, et **ne doivent pas recevoir les mêmes tâches**.

| Type de temps | Quand | Ce qu'on y met | Pourquoi |
|---|---|---|---|
| 🔥 **Temps long, sans interruption** | **la semaine de vacances (S34)** | le **chantier le plus long** : l'application | Un chantier long démarré en morceaux ne finit jamais. C'est la ressource la plus rare — elle va au besoin le plus lourd. |
| 🧩 **Temps court, fragmenté** | soirées et créneaux pendant les cours | tâches **fragmentables** : couverture de tests, revue OWASP, doc d'exploitation, notes de veille | Ces tâches se reprennent sans coût de redémarrage. Les garder pour les périodes chargées, c'est ne rien gaspiller. |
| ⏰ **Créneau fixe** | **lundi 09h–10h**, toutes les semaines | la veille C6 | Le seul chantier qui ne se rattrape pas. Il ne cède jamais sa place. |

**L'erreur à ne pas commettre** : occuper la semaine libre avec les petites tâches parce
qu'elles sont satisfaisantes à cocher. La couverture de tests se fait un mardi soir.
Le squelette de l'application, non.

---

## 3. Comment on travaille sans la validation du formateur

Le formateur est en congé. Sa règle — *une compétence prouvée → envoyée en revue → puis la
suivante* — existe pour empêcher d'empiler du travail non relu. **Elle ne dit pas d'attendre
un absent.**

### La règle appliquée pendant son absence

> **On produit → on gèle → on met en file → on continue.**
> On n'attend jamais une réponse pour démarrer la suite.

- **Geler** = commiter, taguer si c'est un livrable, vérifier les liens, tests verts.
- **Mettre en file** = une ligne dans `docs/FILE-DE-VALIDATION.md`.
- À son retour : **on envoie un par un, dans l'ordre de la file**, pas tout d'un bloc.

**Pourquoi ça se défend devant un jury** : la file montre une démarche de validation
**systématique et datée**. Ce qui se reproche, c'est de n'avoir jamais cherché la
validation — pas d'avoir continué à travailler pendant l'absence du relecteur.

⚠️ **Le risque réel, et il faut le nommer** : un retour tardif peut invalider du travail
déjà fait. On le réduit sans le supprimer, en gelant à chaque étape plutôt qu'à la fin —
un retour sur une étape isolée coûte une semaine, un retour sur trois mois coûte tout.

---

## 4. Ce qui reste — pas 13 compétences, 4 chantiers

Listées une par une, il reste **13 compétences**. Présenté ainsi, c'est décourageant et faux :
plusieurs se prouvent avec **le même artefact**.

| Chantier | Compétences couvertes | Le levier |
|---|---|---|
| **A — L'application** | **C10 + C14 à C19** = **7** | `frontend/` est vide. **Un seul** artefact prouve C10 (interface) *et* tout E4. C'est le plus gros levier du projet. |
| **B — Benchmark de services IA** | **C7** (nourrit C8) | Ne part pas de zéro : la **cascade 3 fournisseurs** existe (`src/llm.py`) et `evals/` sait déjà mesurer. Le benchmark, c'est faire tourner l'existant sur les 3 et comparer. |
| **C — Chaîne MLOps** | **C12 + C13** (et la revue OWASP de C9) | 186 tests existent ; il manque la **mesure** de couverture et la **livraison**. |
| **D — Monitorage** | **C20 + C21 + C8** | S'instrumente **pendant** la construction de l'application, jamais après. Rajouter du monitorage sur une app finie coûte le double. |

**Le pari du plan** : le chantier A porte 7 compétences sur 13. **Il passe en premier et il
prend la semaine libre.** S'il échoue, le plan échoue — c'est le risque assumé.

---

## 5. Le calendrier

| Semaine | Dates | Chantier | Ce qui doit exister à la fin |
|---|---|---|---|
| **S34** 🔥 | 17–23/08 | **A** — vacances, temps long | Squelette de l'application : elle démarre, elle affiche le portefeuille réel depuis l'API |
| **S35** | 24–30/08 | **A** | Les écrans, et les indicateurs du **lot 1** branchés |
| **S36** | 31/08–06/09 | **A** | Indicateurs **lot 2** (portefeuille) · l'app est utilisable |
| **S37** | 07–13/09 | **C** | `pytest-cov` branché, seuil fixé, **C12 clos** |
| **S38** | 14–20/09 | **A** + **D** | Monitorage instrumenté **pendant** le développement |
| **S39** | 21–27/09 | **A** | **E4 rédigé** → gelé → **mis en file** |
| ~~**S40**~~ | ~~28/09–04/10~~ | ~~**B**~~ | ~~Protocole de benchmark + première mesure sur les 3 fournisseurs~~ |
| ~~**S41**~~ | ~~05–11/10~~ | ~~**B**~~ | ~~**C7 clos** → gelé → mis en file~~ |
| ~~**S42**~~ | ~~12–18/10~~ | ~~**C**~~ | ~~Packaging + déploiement, **C13 clos**~~ |
| ~~**S43**~~ | ~~19–25/10~~ | ~~**D**~~ | ~~Dérive et alertes, **C20–C21 clos** → E5 gelé~~ |
| ~~**S44**~~ | ~~26/10–01/11~~ | ~~rattrapage~~ | ~~C8 doc d'exploitation · C9 revue OWASP · le retard accumulé~~ |
| ~~**S45**~~ | ~~02–05/11~~ | ~~**gel**~~ | ~~Relecture, `verifier_liens.py`, tests verts, **envoi du 05/11**~~ |

**Calendrier révisé le 29/09/2026** (oraux blancs annoncés, règle « gelé 2 à 3 semaines avant l'oral ») :

| Semaine | Dates | Chantier | Ce qui doit exister à la fin |
|---|---|---|---|
| **S40** | 29/09–04/10 | **E3 d'abord** (C, D) | Langfuse Cloud UE activé (DPA lu), traces de `src/llm.py` + 2 alertes (#39), une vue temps réel C11 (#38) · squelette du rapport E3 depuis `docs/LLMOPS.md` et `evidence/` · E1 : dates corrigées (#56) · veille S40 (#30) |
| **S41** | 05–11/10 | **E3** (C) | Rapport E3 rédigé, C9 à C13, revue OWASP en section (#29), `db/importer.py` dans l'image (#35) · **Hetzner rafraîchi et automatisé** (#36) : la démo de l'oral tourne sur des données du jour · **E3 gelé le 11/10**, tag `livrable-E3-v1`, envoyé à Elbby · script E1 rafraîchi (580 tests, 1 359 documents, calendrier des places) |
| **S42** | 12–18/10 | **E4** (A) + prépa oral | Rapport E4 rédigé (#28) depuis la vérification du 26/09 ; #23, #27 · préparation de l'oral E1 + E3 commence (`coach-soutenance`) : c'est la période de 2,5 semaines demandée |
| **S43** | 19–25/10 | **E4 gelé** + **B** minimal | Tag `livrable-E4-v1`, envoyé · benchmark C7 minimal, protocole + une mesure (#32, #33) · première répétition E1 + E3 |
| **S44** | 26/10–01/11 | **oral blanc 1** (29-30/10) | Passage E1 + E3, retours notés dans le journal · rapport E2 (#34 : veille, C7, C8 #43) · rapport E5 (#40, #41 minimal, les cinq incidents) |
| **S45** | 02–05/11 | **gel** | Relecture, `verifier_liens.py`, tests verts, **envoi des cinq le 05/11** |
| 06–11/11 | | répétition | Deux passages complets de 90 min, `coach-soutenance` |
| **12–13/11** | | **oral blanc 2** | Situation réelle, 90 min, les cinq |
| 14–29/11 | | étude | Révision seule, plus de code |
| **30/11–01/12** | | **jury** | |

**Ce que cet ordre coûte, dit à l'avance** : E2 et E5 ont une semaine chacun (S44), leurs rapports
seront plus courts et le diront. L'alternative (garder C7 en S40-S41) laissait E3 sans C11 et sans
rapport sur la scène du 29/10.

**Toutes les semaines, sans exception** : lundi 09h–10h, la note de veille C6.
12 lundis restants au 16/08 = **12 notes possibles**, S33 comprise. Aucune marge.

---

## 6. Les risques, nommés à l'avance

| # | Risque | Probabilité | Ce qu'on sacrifie si ça arrive |
|---|---|---|---|
| **1** | 🔴 **Docker ne démarre pas sur cette machine.** Déjà constaté, et C13 en dépend. | **avérée** | Documenter le blocage et livrer un packaging **sans** Docker. Un obstacle mesuré et expliqué vaut mieux qu'une case vide. |
| **2** | 🔴 Le chantier A déborde | élevée | **Les indicateurs du lot 3 (risque) et du lot 4 (relatif)** — déjà annoncés comme sacrifiables dans `docs/indicateurs/CONCEPTION.md`. |
| **3** | 🟠 Les briefs de la reprise mangent le temps | élevée | Les tâches fragmentables glissent, **jamais la veille du lundi**. |
| **4** | 🟠 Retour tardif du formateur invalidant du travail | moyenne | On gèle par étape, pas à la fin. Voir §3. |
| **5** | 🟡 **DVC** (versionnement des données, C12) | moyenne | Écarté et assumé si S37 déborde. |

**Ce qui ne se sacrifie jamais** : la veille du lundi, les tests verts, et le fait que chaque
chiffre cité soit mesuré.

---

## 7. Ce que ce plan ne dit pas — à lire avant d'y croire

- **La charge est très élevée.** E1 a demandé environ trois mois pour cinq compétences. Ce
  plan en vise treize en douze semaines, en période de cours. Il ne tient **que** grâce au
  pari du §4 : un artefact pour sept compétences.
- **Aucune durée ici n'est mesurée.** Ce sont des estimations. La première à vérifier est
  S34 : si le squelette de l'application n'existe pas le 23/08, **tout le reste glisse** et
  il faut re-trancher, pas serrer les dents.
- **Le plan ne remplace pas `ETAT.md`.** Lui dit où on va ; `ETAT.md` dit où on est.

---

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Geler** (*freeze*) | Arrêter de modifier : commiter, taguer, tests verts, liens vérifiés. Ce qui est gelé peut être envoyé sans surprise |
| **Chantier** | Un ensemble de travail qui produit **un** artefact et prouve plusieurs compétences d'un coup |
| **Tâche fragmentable** | Tâche qu'on peut arrêter et reprendre sans tout relire — donc adaptée aux créneaux courts |
| **Couverture de tests** | Le pourcentage du code réellement exécuté par les tests. Mesuré par `pytest-cov` |
| **DVC** (*Data Version Control*) | Outil qui versionne les jeux de données comme Git versionne le code |
| **Dérive** (*drift*) | Le fait que les données réelles s'éloignent avec le temps de celles sur lesquelles le système a été réglé |
