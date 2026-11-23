# ÉTAT — où on en est

> **Ce fichier se périme.** Il porte l'état du jour ; `CLAUDE.md` porte ce qui ne change pas.
> À relire au démarrage de chaque session, à mettre à jour à la fin.

## 📊 Tableau de bord — la vue d'ensemble en un coup d'œil

**https://claude.ai/code/artifact/736033e3-9ea8-495c-a4f7-0d47de56c303**

Chronologie datée · les 5 livrables · **table filtrable des 21 compétences** (bouton
« À zéro » → C7, C11, C16) · inventaire du code, des schémas et des preuves.

> Dans le terminal de l'assistant : **`/artifacts`** liste tes tableaux de bord (`o` pour ouvrir,
> `c` pour copier le lien) · **`Ctrl+]`** rouvre le dernier. Sur le web :
> `claude.ai/code/artifacts`.
> ⚠️ **En cas de divergence, CE FICHIER a raison** — le tableau de bord en est une photographie.

**Dernière mise à jour : 2026-11-24, nuit (#295 fusionnée ; #296 ouverte, sa revue automatique sautée ; cinq constats de ma revue corrigés sur `revue-296-24-11`) ; avant : 2026-11-23, soir (dépôt public et PDF au Drive ; production sur `3e5e365` ; quatre corrections, cet état et la revue de #295 corrigée sur la branche `etat-publication-23-11` ; journaux de revue lus, aucun secret ; rattrapage du 23/11 fait) ; avant : 2026-11-20, soir (#286 en production sur `b3c4bc8` ; #289, le paragraphe des sprints du README, dans `develop` ; rattrapage du 19 et du 20/11 fait ; cinq PDF du Drive prêts avec une page d'accès, pas encore déposés) ; avant : 2026-11-20, après-midi (#287 fusionnée ; #286 relue, CI verte ; noms de deux étudiants remplacés par leur rôle, sur la branche `noms-tiers-20-11`) ; avant : 2026-11-20, matin (copies OneDrive d'E1 et d'E4, classeurs et note d'oral corrigés ; audit de publication, trois captures floutées) ; avant : 2026-11-19, soir (#283 fusionnée, CI de `develop` verte ; E2 et E3 vérifiés, rien à refaire ; copies OneDrive d'E5 v1.3 égales au tag ; E5 au Drive avec son annexe A ; ordre du 20/11) ; avant : 2026-11-19, après-midi (trois tags posés sur `4b2d8ad`, un par push, exécutions vertes ; production sur `4b2d8ad` ; liens vérifiés après les tags) ; avant : 2026-11-19 (correction RGPD : E1 v10, E4 1.12 et registre T9, pour `livrable-E1-v10` et `livrable-E4-v9`, sur la branche `rgpd-t9-19-11`) ; avant : 2026-11-18, 22 h 30 (cours de production rattrapés au 18/11, preuve versée ; CRI.PA sans son 18/11, retard connu ; #279 fusionnée dans `develop`) ; avant : 2026-11-18, soir (rapport E5 v1.3 avec l'annexe A, pour `livrable-E5-v7`, sur la branche `e5-v1-3-corrections` ; #277 et #278 fusionnées, production sur `16567ec`) ; avant : 2026-11-17, 22 h 30 (cours de production rattrapés au 17/11, preuve versée ; CRI.PA sans son 17/11, retard connu) ; avant : 2026-11-17, fin de journée (production sur `ceab6f3` ; PDF datés et classeurs ; six issues et la PR #88 fermées, #21 ouverte ; séance du 16/11 vérifiée en local) ; avant : 2026-11-17, matin (#274 fusionnée ; cours de production à la main jusqu'au jury ; écart des taux expliqué) ; avant : 2026-11-16, nuit (cinq tags posés sur `fe13d24`, exécutions vertes ; dépôt public le 23/11) ; avant : 2026-11-16, soir (relecture de #271 reprise ; publication du dépôt décidée juste après les tags) ; avant : 2026-11-16, fin de matinée (Azure répond de nouveau, cause non établie ; versions E1 v9, E2 1.7, E3 2.6, E4 1.11 et E5 1.2 rendues sur la branche `versions-16-11`, pour `livrable-E1-v9`, `livrable-E2-v6`, `livrable-E3-v7`, `livrable-E4-v8` et `livrable-E5-v6`) ; avant : 2026-11-16, 0 h 15, heure de Paris (arrêt pour la nuit : #266 et #267 fusionnées dans `develop` ; clé par client reportée après le jury ; Azure toujours 401 au test du 15/11 à 23 h 03 UTC, commit local sur `versions-16-11`) ; avant : 2026-11-14, fin d'après-midi (#258, #259 et #260 fusionnées ; l'interface nomme Mistral, livrée sur `9d48870` et vérifiée en production) ; avant : 2026-11-14, après-midi (production livrée sur `2dd385f` avec Mistral en secours d'Azure, qui refuse toujours la clé ; cours de production au 13/11 ; session de test E5 faite, toutes les cartes saines ; preuves C3 et C20 versées) ; avant : 2026-11-13, soir (oral blanc 2 passé ; consignes de remise du 23/11 ; axes de la courbe, guide du rattrapage, preuve du 11/11 et README fusionnés dans `develop` ; audit de publication fait) ; avant : 2026-11-11, soir (cours de production rattrapés au 11/11 en deux passages, preuve versée ; deux manques du guide de rattrapage découverts ; description des valeurs radiées corrigée sur la branche `doc-delistee-indicateurs`, PR à ouvrir) ; avant : 2026-11-08, soir (cinq tags sur `770d440`, liens vérifiés ; cours de production rattrapés au 06/11 ; étapes 3 et 4 du rattrapage corrigées après la carte #76) ; avant : 2026-11-08, 1 h UTC (arrêt pour la nuit : `main` à `05df824` en production, trois tags à poser) ; avant : 2026-11-08, nuit (E1 v7 et E3 v2.5 aux couleurs du rapport E2, pour `livrable-E1-v7` et `livrable-E3-v6` ; README à l'état du 08/11) ; avant : 2026-11-07, 23 h UTC (tags `livrable-E4-v6` et `livrable-E5-v4` posés par Era sur `fcf201e`, leurs exécutions vertes, production livrée sur `fcf201e` ; C20.5 validé ✅ par Era) ; avant : 2026-11-07, nuit (C20.5 : passage planifié de la vigie constaté à 21 h 52 UTC, proposé ✅ ; E4 v1.9 après le contrôle final et E5 v1.0 prêts pour `livrable-E4-v6` et `livrable-E5-v4`, relecture d'Era à faire) ; avant : 2026-11-07, soir (S9, C17.7 et les corrections de #226 en production, vérifié ; C16.1 gardé à consolider) ; avant : 2026-11-06, soir (E2 v1.3 prête pour `livrable-E2-v4` après double contrôle ; carte #74 mesurée avant et après) ; avant : 2026-11-06 (clé par client reportée après l'oral blanc, réévaluée le 14/11 ; spécification 002 validée et plan v2 ; préparation à finir le 07/11, puis répétitions) ; avant : 2026-11-05, 22 h (corrections d'interface fusionnées et en production, `ed12b7e` ; tags `livrable-E4-v5` et `livrable-E5-v3` livrés ; préparation de l'oral faite hors du dépôt, E1 à E5 prêts pour la répétition ; un manque découvert dans E2 v1.1) ; avant : 2026-11-05, soir (E5 v0.8 pour `livrable-E5-v3` ; E4 v1.5 pour `livrable-E4-v5` ; E1 laissé tel quel, limite écrite) ; avant : 2026-11-05, fin d'après-midi (tag `livrable-E2-v3` posé sur `9d2f0cc` et vérifié ; E4 v1.5 pour `livrable-E4-v5`) ; avant : 2026-11-05, après-midi (tag `livrable-E4-v4` posé sur `70a19cd` et vérifié ; remise envoyée par Era ; E2 v1.1 pour `livrable-E2-v3`) ; avant : 2026-11-05, nuit (tag `livrable-E4-v3` posé sur `07da897`) ; avant : 2026-11-04, 22 h 35 (rattrapage des cours et des taux fait en production, dernière séance 04/11, vérifié par Era sur les deux écrans ; script C2 à renforcer avant toute réutilisation ; collecte automatique toujours séparée) ; avant : 2026-11-04, 21 h 35 (A et B faits en production : nouvelle interface déployée, `8ecc5a7`, fichiers servis vérifiés ; Viridien corrigé, exactement 4 cellules, S2 comparée à S1 ; restent les contrôles d'Era avec sa clé ; cours de production toujours au 27/10) ; avant : 2026-11-04, nuit (mise en production préparée : sauvegarde S1 de la production faite, protégée sur deux disques, restaurée et répétée sans échec ; PR #179 vers `develop` ; demande de validation regroupée A et B en attente d'Era ; production toujours à `2310f87`) ; avant : 2026-11-04, soir (refonte de l'interface : tâches 0 à 8 faites sur la branche `refonte-interface`, 13 commits poussés ; remise toujours à envoyer par Era) ; avant : 2026-11-03, soir (E1 v6 tagué, `livrable-E1-v6` ; README à l'état du 03/11 ; note de mise à jour d'E2 à E5, une page, à relire par Era) ; avant : 2026-11-03 (E5 tagué, `livrable-E5-v1` ; retour écrit du formateur ; E1 v6 prêt pour `livrable-E1-v6`, à relire par Era) ; avant : 2026-11-02, 23 h (E4 livré, `livrable-E4-v1` ; E5 v0.6 prêt pour `livrable-E5-v1`) ; avant : 2026-11-02, 21 h (PR #173 fusionnée et déployée, tags E1 E2 E3, E4 v1.1 prêt pour `livrable-E4-v1`) ; avant : 2026-11-02, soir (retour écrit du formateur appliqué : E1 v5, E3 v2.0, présentateur ; E2 v0.9 ; recette C17.3 et C17.4) ; avant : 2026-11-02, nuit (marqueur `postgresql` à la place de la recherche du mot `dsn_de_test`, mêmes 24 tests, garde-fou ; local, à commiter) ; avant : 2026-11-01, nuit (recette sur `develop` : E2 v0.7, E4 v1.0, E5 v0.5, correctifs #78, #73, #79 et #152 ; job `base` vert sur GitHub et exigé pour `main` ; rien sur `main`) ; avant : 2026-11-01, après-midi (E2 v0.7 et son annexe, E5 v0.5, prêts à relire, rien n'est commité) ; avant : 2026-11-01, midi (PR #171 puis #172 fusionnées : INC-009 sur `main` et en production, `922349d` ; E5 v0.4 ; phrase E3-2 ajoutée au présentateur) ; avant : 2026-11-01 (E4 v0.9 et E5 v0.3 préparés, extraits de code compris) ; avant : 2026-10-31, nuit (rapport E5 v0.2 rédigé, 5 pages, relu deux fois, à envoyer au formateur ; INC-009 corrigé et documenté, PR #171 verte, à fusionner) ; avant : 2026-10-31 (notation C7 terminée, production remise à Azure seul, C8 en cours) ; avant : 2026-10-30, fin de nuit (rapport E4 v0.7, relu en entier par une relecture indépendante vérifiée ; auto-évaluation 17 ✅ · 19 ⚠️ · 0 ❌, statuts décidés par Era critère par critère ; correction « refuse de démarrer » faite, `a2c0d51`) ; avant : 2026-10-30, nuit (rapport E4 : première version complète v0.6, à relire ; auto-évaluation 20 ✅ · 16 ⚠️ · 0 ❌ sur 36 critères ; périmètre d'E4 décidé : les cinq écrans de `d3a4198`, ateliers des sprints exclus ; prochaine séance : relecture globale ciblée d'E4, puis E2 et E5) ; avant : 2026-10-30, soir (oral blanc 1 passé : E1 en 13 min 46, E3 en 18 min 31 ; retours d'Héléna, Nadège et Elbby intégrés au présentateur, hors du dépôt ; oraux blancs complets les 12 et 13/11) ; avant : 2026-10-29, soir (les cinq classeurs des compétences remis à l'état du 29/10 dans les copies OneDrive, statuts inchangés ; manque trouvé dans le classeur détaillé envoyé le 28/10 : C10 et C11 sans rédaction, E3 cité en v1.5 ; branche `classeur-competences` restée au 28/10 ; support d'oral et vidéo d'entraînement refaits hors du dépôt) ; avant : 2026-10-29, matin (rapport E3 v1.9 envoyé au formateur sur Discord, avec trois précisions ; trois imprécisions d'E3 de plus relevées, p. 1, 7 et 9) ; avant : 2026-10-28, soir (livret E1 v3 et grilles envoyés au formateur, E1 accepté ; PR #169 fusionnée dans `develop` ; rapport E3 à envoyer) ; avant : 2026-10-28, fin d'après-midi (versions envoyées d'E1 et d'E3 dans le dépôt, à côté des originaux ; schémas d'annexe d'E1 pour C2, C3 et C5 ; budget du livret décidé, pour la v4 ; branche `schemas-E1-C2-C3-C5` poussée, PR vers `develop` à ouvrir ; message au formateur toujours à envoyer) ; avant : 2026-10-27, soir (cours et taux de production rattrapés à la main jusqu'au 27/10, articles réingérés ; procédure écrite dans `docs/exploitation.md` ; à refaire jeudi 29/10 après 17 h 35 ; message des liens toujours à envoyer) ; avant : 2026-10-27, midi (tags `livrable-E1-v3` et `livrable-E3-v2` posés sur `d3a4198`, en production ; message des liens rédigé, non parti) ; avant : 2026-10-27, matin (livrables E1 v3 et E3 v2 préparés sur la branche `livrables-E1-v3-E3-v2` ; tags `livrable-E1-v3` et `livrable-E3-v2` à poser après la fusion dans `main`) ; avant : 2026-10-26, midi et demi (sprint 5 : livrable en version 5 sur la branche `sprint-5-livrable-v5` : les quatre captures du tableau de bord affichées au § 5.6 ; tag `livrable-sprint-5-v5` à poser après la livraison suivante) ; avant : 2026-10-26, fin de matinée (sprint 5 : livrable en version 4 sur la branche `sprint-5-livrable-v4` : schéma de la vigie au § 1.4 et synthèse refaite ; tag `livrable-sprint-5-v4` à poser après la livraison suivante) ; avant : 2026-10-26 (sprint 5 : livrable en version 3 sur la branche `sprint-5-livrable-v3` : chronologie « d'abord la copie locale, puis la production » et discussion avec le formateur consignées ; tag `livrable-sprint-5-v3` à poser après la livraison suivante) ; avant : 2026-10-25, soir (sprint 5 : livrable en version 2 sur la branche `sprint-5-livrable-v2`, page 11 du PDF corrigée ; tag `livrable-sprint-5-v2` à poser après la livraison suivante) ; avant : 2026-10-24, 19 h 55 (PR #150 fusionnée : lignes 5 et 6 de la file de validation dans `develop` ; deux messages au formateur rédigés ; journal 034 et notes d'étude écrits ; prochaine action : Era envoie le message 1, E1) ; avant : 2026-10-24, 19 h 20 (E1 et E3 gelés : livraison N19 en production, `312056a`, tags `livrable-E1-v2` et `livrable-E3-v1` posés par Era à 19 h 05 ; prochaine action : le message au formateur, envoyé par Era) ; avant : 2026-10-24, 18 h 30 (entrée du `CHANGELOG` qui cite les tags `livrable-E1-v2` et `livrable-E3-v1` ; prochaine action : `develop` vers `main`, livraison N19, puis les tags) ; avant : 2026-10-24, 18 h 15 (E3 v1.5 fusionnée dans `develop`, PR #146 : 19 pages, figures mises en forme par Era et testées, deux relectures vérifiées ; prochaine action : `develop` vers `main`, puis les tags E1 et E3) ; avant : 2026-10-24, 16 h 30 (vérificateur de liens, PR #143 : 0 lien cassé sur tout le dépôt ; documents de référence, contrat OpenAPI et retour arrière de production, PR #144 ; prochaine action : E3 v1.5) ; avant : 2026-10-24, 14 h 30 (E1 v2.6 prête et fusionnée dans `develop`, PR #141 ; MCD au formalisme Merise ; schéma C1 illustré et testé ; prochaine action : le vérificateur de liens, puis E3 v1.5) ; avant : 2026-10-24, midi (livraison N18 : quatre correctifs C, E, D, F en production, `b547cbf` ; manque de sauvegarde consigné ; prochaine action E1 v2.6) ; avant : 2026-10-23, 20 h (sprint 5 remis : livraison N17, `d215617`, tag `livrable-sprint-5-v1` posé par Era et vérifié ; reste la grille de l'atelier 5) ; avant : 2026-10-23, 18 h 30 (sprint 5 en production : PR #133 et #134, livraison N16, `845e3b3` ; livrable « en production » ; restent la grille de l'atelier 5 et le tag) ; avant : 2026-10-23, midi, sur la branche `sprint-5-vigie-demo` (sprint 5 : doc suivie à la lettre, dix trous corrigés ; deux répétitions de la démo ; fausse alerte de production #130 corrigée ; livrable mis à jour ; restent l'atelier 5, sa grille et le tag) ; avant : 2026-10-22, 20 h 15, sur la branche `sprint-5-vigie-demo` (sprint 5, prototype local : vigie, tableau de bord, exercices et doc prouvés sur la copie du poste ; scénario de la démo écrit ; livrable v1 ; grille de l'atelier 4 versée ; restent le test de la doc, les répétitions et le tag `livrable-sprint-5-v1`) ; avant : 2026-10-21, 22 h 20 (sprint 4 : livrable en version 3, lien de ligne corrigé et état de la production à N14 ; tag v3 à poser après la livraison suivante) ; avant : 2026-10-21, 21 h 40 (sprint 4 remis : N14 en production, tag `livrable-sprint-4-v2` posé et livré ; reste l'atelier 4) ; avant : 2026-10-21, 21 h 15 (sprint 4 : N13 en production ; tag v1 posé sur N12 par erreur, figé ; remise sous le tag v2, à poser après la livraison suivante) ; avant : 2026-10-21, 20 h 15 (sprint 4 : livrable v1 et synthèse validés, schéma complet, journal des retours complété, tag cité au CHANGELOG ; restent N13, la Definition of Done et le tag) ; avant : 2026-10-21, 13 h 20 (sprint 4 : livraison N12 en production, traçage Langfuse actif en production, CA3.6 prouvé sur une vraie trace ; livrable v1 ; reste D3) ; avant : 2026-10-21, 11 h 20 (sprint 4 : livraison N11 en production, contrôle des nombres ; rejeu en production 5 sur 5, deux fois ; PR #118 en attente ; reste D3) ; avant : 2026-10-20, nuit (sprint 4 : livraison N10 en production ; rejeu en production, Q4 abîmée une fois ; contrôle des nombres commité en local) ; avant : 2026-10-19, soir (atelier 3 fait avec le formateur ; livrable du sprint 3, version 2 ; tag `livrable-sprint-3-v2` à poser) ; avant : 2026-10-17, nuit (N7 en production ; livrable du sprint 3, version 1 ; atelier 3 lundi 19/10
au matin, tag v1 prévu dimanche) ; avant : 2026-10-16, nuit (sprint 3 en production : N5 et N6, ingestion par le bouton, évaluation en production 8 sur 8, registre RGPD, documents de fin de sprint ; restent N7, l'atelier 3 et le tag) ; avant : 2026-10-16 au soir (sprint 3 : parcours des questions, Google News arrêté dans le code, ingestion en une opération, jeu de questions en version 2, évaluation locale 8 sur 8 ; reste la livraison) ; avant : 2026-10-15 au soir (sprint 2 clos, tag livrable-sprint-2-v3, sprint 3 ouvert dans un worktree) ; avant : 2026-10-11 (E1 v2.5 : cinq surgénéralisations corrigées ; veille S41 : relevé, note d'Era et partage à la promo ; E3 v1.4 : sept corrections, 44 critères en 39 lignes, revue d'E3 close ; E1 v2.4 : seconde passe, MCD lisible, guide § 4.5 corrigé ; avant, E1 v2.3 : passe RGPD et exactitude ; politique des fournisseurs et calendrier final ; plan E2 ; avant, le 10/10 au soir : incident de clé Mistral corrigé ; Mistral Large 4 sans réflexion sur la branche `mistral-ue` ; règle UE seule gardée stricte ; jeu de démonstration clarifié ; avant, à 10 h 30 : E3 v1.2 : date et contrat de Langfuse remis d'accord avec E1 ; E1 v2.2 : quatre points corrigés avant le gel, `memory_audit` tranché après le gel, carte #86 ; plus tôt le matin : classeur v4, deux critères officiels de C19 absents du modèle Simplon ajoutés, C13 vérifié ; la nuit du 9 au 10 : cartes #84 et #85 faites, Azure en zone UE, gel fixé au 15/10, Mistral UE choisi pour après le gel, classeur v3, note d'étude de la colonne « Rédaction ») ; avant : 2026-10-06 (calendrier jusqu'au 05/11 décidé par Era ; la veille : retour du formateur, contrats des destinataires relus, guide d'exploitation remis d'accord, classeur des compétences corrigé et synthèse courte, E2 v0.2, carte #84)** · deadline livrables **05/11/2026** · **oral blanc 1 : passé le 30/10 (E1 + E3)** ·
**oral blanc 2 : 12-13/11 (90 min)** · jury **mardi 01/12 à 11 h 15, en visioconférence** (convocation du 30/10)

---

## ▶️ 24/11, NUIT : #295 FUSIONNÉE ; #296 (`develop` VERS `main`) OUVERTE, SA REVUE AUTOMATIQUE SAUTÉE ; CINQ CONSTATS CORRIGÉS

**État** :
- #295 fusionnée dans `develop` le 23/11 à 22 h 57 UTC (`9655fd2`), après ma revue (six constats corrigés) et une CI
  verte : pytest 3 177 réussis, 102 ignorés, 0 échec, couverture 96,15 % (seuil 90 %)
  ([Tests 45283035587](https://github.com/Ganda15/rita-agent/actions/runs/45283035587)).
- #296, `develop` vers `main`, ouverte le 23/11 : au moment de ma revue, son diff était celui de #295, ligne à
  ligne (330 lignes) ; il reprend aussi ces corrections une fois fusionnées dans `develop`. La revue automatique
  n'a pas tourné : l'action refuse de s'exécuter sur une PR qui modifie son workflow (« Action skipped due to workflow
  validation »), et le contrôle `revue` est resté vert en 17 s, sans commentaire
  ([passage 45284474354](https://github.com/Ganda15/rita-agent/actions/runs/45284474354)). Ma revue de #296 a trouvé cinq constats, corrigés sur la branche
  `revue-296-24-11` (PR vers `develop`) : le texte qui annonçait #296 comme la première revue avec
  `show_full_output: false` (ici et dans le `CHANGELOG`) ; `docs/CI-CD.md`, qui ne disait pas qu'un `revue` vert peut
  ne rien prouver ; trois fichiers qui disaient encore le dépôt privé ou sa publication à venir (`evidence/README.md`,
  `docs/PLAN-E4-rapport.md`, `docs/sprint-5/DEMO.md`) ; cet état, qui aurait décrit #295 encore ouverte après la
  fusion ; une phrase ambiguë du `CHANGELOG`.
- Production sur `3e5e365` le 24/11 à la nuit, à l'écriture de ce bloc ; la fusion de #296 dans `main` la fait passer
  sur son commit de fusion, que `/health` donne.

**Prochaine action** :
1. Era pousse `revue-296-24-11` et ouvre la PR vers `develop` ; je la relis ; Era fusionne. #296 la reprend d'elle-même.
2. Era corrige la description de #296 (`gh pr edit 296 --body-file …`), puis la fusionne de jour, CI verte, avant le
   29/11 ; ensuite `/health` sur le nouveau commit et le tableau de bord (compteurs remis à zéro par le redémarrage).
3. Le reste est inchangé : points 2 à 7 du bloc du 23/11 au soir, ci-dessous.

---

## ▶️ 23/11, SOIR : DÉPÔT PUBLIC ; PDF AU DRIVE ; PRODUCTION SUR `3e5e365`, COURS AU 23/11 ; QUATRE CORRECTIONS SUR `etat-publication-23-11`

**État** :
- `main` à `3e5e365` depuis le 22/11 (#294, `develop` vers `main`, fusionnée à 11 h 48 UTC), en production
  ([Tests 45019106873](https://github.com/Ganda15/rita-agent/actions/runs/45019106873),
  [Livraison 45019106814](https://github.com/Ganda15/rita-agent/actions/runs/45019106814)). Avant elle : #291 (le
  paragraphe des sprints du README et l'`ETAT.md` du 20/11), fusionnée dans `main` le 20/11 à 22 h 02 UTC, puis #292 et
  #293 (la fiche de la source revient à la ligne) dans `develop` le 22/11. L'image lue sur le serveur au rattrapage du
  soir (`sha256:f1d86ed0…`) est celle que la livraison 45019106814 a publiée.
- Dépôt public depuis le 23/11 (API GitHub : `visibility=public`). Les cinq PDF et les deux classeurs du 20/11 sont au
  Drive depuis le 23/11. Une relecture indépendante les a trouvés conformes aux tags : hors de la page « Accès pour le
  jury » ajoutée à la fin, seule la page 1 change, avec le renvoi vers elle. Les classeurs gardent d'anciennes
  formulations, par exemple la cellule D31 de la grille courte (« huit traitements, T1 à T8 »), quand le PDF E1, p. 5,
  en compte neuf ; les réponses d'oral sont prêtes, hors du dépôt. Le Kanban est public lui aussi (API GitHub :
  `public: true`, page ouverte sans connexion le 23/11).
- Deux passages planifiés de la vigie n'ont pas démarré, le 22/11 à 19 h 42 UTC et le 23/11 à 1 h 44 UTC
  ([45062251373](https://github.com/Ganda15/rita-agent/actions/runs/45062251373),
  [45096286154](https://github.com/Ganda15/rita-agent/actions/runs/45096286154)) : GitHub signale un problème de
  paiement ou de plafond Actions sur le compte. Le premier passage après la publication a réussi, le 23/11 à 12 h 46 UTC
  ([45177484856](https://github.com/Ganda15/rita-agent/actions/runs/45177484856)) : sur un dépôt public, les minutes
  d'Actions des exécuteurs standard ne comptent pas. Rien ne prouve que le problème du compte est réglé, donc le dépôt
  reste public jusqu'au jury, sinon la CI et la vigie s'arrêtent. Depuis, aucun passage jusqu'à 22 h 16 UTC (créneaux de
  15 h 17, 18 h 17 et 21 h 17 UTC sans exécution, workflow actif) : le même genre de trou que le 22/11, entre 11 h 27 et
  19 h 42 UTC. La vigie est programmée ; son passage n'est pas garanti.
- Branche `etat-publication-23-11`, partie de `develop` (`e50597d`), PR #295 vers `develop` : quatre commits, cet état,
  puis les corrections de ma revue de #295.
  - `4555a37` : le plan du chantier E dit, en section 8, son état au 28/08 et renvoie aux rapports (C16, C11, C10).
  - `e4f1eb9` : registre RGPD, points 6 et 13 du § 5 marqués faits (Mistral en second depuis le 14/11, avertissement de
    l'écran Question depuis le 06/11) ; la revue de #295 ramène le point 6 à « fait pour les fournisseurs ».
  - `554ec84` : `CONTINUITE.md` reçoit la décision du 14/11 (Mistral Large 3 en secours d'Azure, à la place de
    Large 4), dans une ligne datée du 23/11 ; celles du 10/10 et du 03/11 restent telles quelles.
  - `faa4647` : `show_full_output: false` dans `.github/workflows/revue-pr.yml`, parce que le journal d'un passage est
    public avec le dépôt ; la vigie est dite « programmée toutes les trois heures », passage non garanti
    (`.github/workflows/vigie.yml`, `docs/CI-CD.md`). Le réglage vaut sur `main` après la fusion de #296 (`develop`
    vers `main`) ; la revue automatique de #296 elle-même a été sautée (voir le bloc du 24/11).
  - Revue de #295 (23/11 au soir), six constats, tous corrigés dans le commit qui suit cet état. Le point 6 du registre
    RGPD revient à « fait pour les fournisseurs », car la fiche T6 le cite comme encore ouvert (contrat de Microsoft).
    `CLAUDE.md`, `docs/exploitation.md` (§ 4.1), `docs/FILE-DE-VALIDATION.md`, `docs/PILOTAGE-AGILE.md` et
    `CONTINUITE.md` disaient encore le dépôt ou le Kanban privés. La cadence « programmée, passage non garanti » est
    reprise dans `docs/exploitation.md` et dans le tableau de `docs/CI-CD.md`. Tests qui lisent les fichiers modifiés,
    relancés après les corrections : 244 réussis, 15 ignorés, 0 échec (`python -m pytest -q tests/test_vigie_planifiee.py
    tests/test_workflows_livraison.py tests/test_lint_config.py tests/test_gitleaks_config.py tests/test_image_runner.py
    tests/test_deployer_scenarios.py tests/test_exploitation_doc.py tests/test_rgpd_registre.py tests/test_vigie.py`).
- Scan des journaux de « Revue PR », valeurs jamais affichées : 130 passages, tous lisibles, aucun secret, actif ou
  révoqué. 0 clé `sk-…`, 0 jeton `Bearer`, 0 clé privée. Les 93 valeurs qui ressemblaient à une affectation de clé sont
  toutes expliquées : 13 expressions `${{ secrets.X }}`, 18 valeurs de test, 48 compteurs `subagent_tokens:`, 12
  fragments de code `max_tokens=`, 1 nom de secret GitHub, et 1 `mot_de_passe=present`, l'étape 4 du rattrapage du 17/11
  relue par la revue. Aucun journal supprimé. Limites : c'est une recherche de motifs ; GitHub masque déjà ses secrets
  enregistrés (`***`) ; seul le workflow de revue a été lu.
- Rattrapage des cours de production le 23/11, de 22 h 07 à 22 h 10 UTC environ (23 h 07 à 23 h 10 à Paris),
  `--du 2026-11-20 --au 2026-11-23` : 216 cotations lues et écrites, 0 rejetée ; `cotation` passe de 282 462 à 282 570
  lignes (+108), dernière séance au 23/11 ; 8 taux lus et 10 écrits (dont 2 lignes EUR), cinq devises au 23/11. 107
  valeurs repartent du 20/11 (2 lignes chacune) ; CRI.PA repart du 19/11 et a 2 lignes sur 3 possibles : il lui manque
  encore le 20/11 ou le 23/11, sans contrôle par séance ce soir pour dire lequel. Sortie du serveur gardée hors du dépôt,
  avec celle du 20/11, pour la PR des preuves du 30/11.
- Tableau de bord de production lu le 23/11 à 15 h 19, heure de Paris : « Refus de sécurité » en problème, 12 sur 22
  (55 %), à cause de mes propres essais d'attaque ; l'alerte fonctionne. Deux captures, à 14 h 41 et à 15 h 19, donnent
  sur la carte Coût « depuis 14:32 » puis « depuis 13:02 », et deux Fraîcheur différentes pour la même date : inexpliqué,
  à regarder après le jury (`/health`, appelé dix fois, rend dix fois `3e5e365`).
- Hors du dépôt : vidéos d'entraînement E2, E4 et E5 refaites le 23/11 et installées dans le présentateur ; questions
  d'oral 112 à 120 ; plan jusqu'au jury et journal 054 dans Obsidian.

**Prochaine action** :
1. #295 est ouverte vers `develop` et relue : Era pousse les corrections de la revue, attend la CI verte, puis fusionne.
   Ensuite, une seule PR `develop` vers `main`, relue et fusionnée avant le 29/11 : une livraison, et
   `show_full_output: false` en vigueur sur `main`.
2. Après la fusion dans `main` : corriger la dernière phrase de la question 115, dans les deux notes d'Obsidian (22/11
   et 23/11).
3. Du 24 au 27/11 : rattrapage chaque soir de bourse après 22 h 05, le premier avec `--du 2026-11-23` ; le 26/11, New
   York est fermé (Thanksgiving), FTI et SLB n'ont pas de cours ce jour-là. Après chaque passage, un contrôle par séance,
   pour savoir où en est CRI.PA.
4. 27/11 : écrire la procédure de redémarrage du serveur, absente de `docs/exploitation.md`. 28/11 : le redémarrage
   (« System restart required », encore affiché le 23/11), puis `/health` et un essai avec la clé.
5. 30/11 : essai d'accès depuis une fenêtre privée, rattrapage après 22 h 05. 01/12 : rattrapage avant 9 h, 10 questions
   normales vers 10 h 30, tableau de bord vers 10 h 45, jury à 11 h 15 ; le soir, changement de la clé de production.
6. Jusqu'au jury : rien dans `main` à partir du 29/11 ; le dépôt reste public ; aucun redémarrage hors du 28/11.
7. Après le jury : fermer #77, #132 et #250 ; Dependabot ; l'énigme du « 13:02 » ; Azure s'arrête après le 02/12.

---

## ▶️ 20/11, SOIR : #286 EN PRODUCTION ; RATTRAPAGE DU 19 ET DU 20/11 FAIT ; PDF DU DRIVE PRÊTS, PAS ENCORE DÉPOSÉS

**État** :
- #288 (noms des deux étudiants remplacés par leur rôle) fusionnée dans `develop` (`d34bc36`), après ma revue (cinq
  constats mineurs, laissés tels quels par Era : ils ne touchent ni les cinq PDF ni le code). #286 (`develop` vers
  `main`) relue de nouveau, CI verte, fusionnée le 20/11 à 17 h 13 UTC : `main` à `b3c4bc8`, livré à 17 h 26 UTC,
  `/health` 200 sur `b3c4bc8` ([Tests 44781198508](https://github.com/Ganda15/rita-agent/actions/runs/44781198508),
  [Livraison 44781199058](https://github.com/Ganda15/rita-agent/actions/runs/44781199058)).
- #289 fusionnée dans `develop` à 21 h 00 UTC (`f4143ca`), pas encore sur `main` : l'encadré d'entrée du README ne
  parle plus du sprint 5 (reste du 08/11) ; un court paragraphe, après le tableau des livrables, explique les sprints :
  des cycles de la formation appliqués à RITA, pas des livrables, cités par E4 pour C16. Le test du README racine suit
  cette décision.
- Vue du jury sur GitHub vérifiée en lecture seule : les 446 liens des cinq PDF vers le dépôt sont valides (fichier
  présent au tag ou au commit cité) ; 6 liens externes en 200 ; 17 liens vers des exécutions, issues et PR en 404 sans
  connexion tant que le dépôt est privé, tous existants par l'API ; 563 liens internes, 0 cassé. Wiki désactivé le
  20/11 (vide, jamais créé ; `has_wiki` à `false`).
- Fausse alerte Langfuse sur #250 (20/11, 11 h 00 UTC, 12 erreurs) : elle venait de mes quatre lancements locaux de
  `pytest --noconftest` du matin (10 h 38 à 10 h 40 UTC), qui ont contourné `tests/conftest.py` et tracé les briefings
  simulés de `tests/test_llm.py` dans le vrai projet. Ni la production ni Anthropic en cause : fournisseurs simulés,
  erreur en 0,00 s. Expliqué dans #250 (commentaire du 20/11, 18 h 34 UTC) ; l'issue reste ouverte pour INC-010.
  Désormais, un lancement local sans `conftest.py` se fait avec `LANGFUSE_TRACING_ENABLED=false`.
- Remise du lundi 23/11, 17 h : la cheffe de projet ne transmet au jury que cinq PDF (réunion du 13/11), donc une notice
  à part ne lui parviendrait pas. Décision d'Era (20/11 soir), qui remplace la notice séparée du point 3 du bloc du
  matin : chaque PDF déposé reçoit une page finale « Accès pour le jury » (application, clé, GitHub, tag de l'épreuve,
  guide du jury) et une ligne de renvoi en page 1 ; la clé n'est que dans ces copies, jamais dans le dépôt. Les cinq PDF
  sont prêts hors du dépôt (`GANDAKUMAR Eramalingam - E1.pdf` à `E5.pdf`), autres pages identiques aux tags, la page 1 garde tout son texte plus la ligne de renvoi ; clé
  testée par Era depuis la page 11 d'E1. Les deux classeurs `_20_11_26` remplaceront ceux du 08/11. Le Drive contient
  encore les sept fichiers du 09/11.
- Rattrapage des cours de production le 20/11, de 22 h 07 à 22 h 10 à Paris (`--du 2026-11-18 --au 2026-11-20`) : 324
  cotations écrites, 0 rejetée ; 15 taux ; `cotation` passe de 282 246 à 282 462 lignes ; séances des 17, 18 et 19/11
  complètes (108 valeurs), 20/11 à 107 (CRI.PA, retard de publication connu, reprise au passage suivant) ; cinq devises
  au 20/11. Sortie du serveur gardée hors du dépôt, pour la PR des preuves du 30/11.

**Prochaine action** :
1. Cette PR dans `develop`, puis une seule PR `develop` vers `main` (le README et cet `ETAT.md`), relue et fusionnée
   avant le 23/11 : une livraison en production.
2. 21/11 vers 11 h UTC : vérifier que Langfuse a commenté le retour à la normale sur #250.
3. Avant le lundi 23/11 à 17 h : Era remplace dans le Drive les sept fichiers du 09/11 par les cinq PDF et les deux
   classeurs du 20/11, puis je compare les noms et les tailles.
4. 22/11 : essai d'accès en suivant la page d'accès d'un PDF, comme un membre du jury.
5. 23/11 : dépôt public, puis approbation des workflows des contributeurs extérieurs et liens revérifiés sans connexion
   (dont les deux liens en 503 du bloc du matin) ; rattrapage après 22 h 05 (`--du 2026-11-20`).
6. Ensuite, inchangés : les rattrapages jusqu'au 01/12, le redémarrage du serveur le samedi 28/11 et le changement de
   clé le 01/12 au soir (points 2, 5 et 6 du bloc du 20/11 au matin).

---

## ▶️ 20/11, APRÈS-MIDI : #287 FUSIONNÉE ; #286 RELUE ; NOMS DE DEUX ÉTUDIANTS REMPLACÉS PAR LEUR RÔLE

**État** :
- #287 (corrections de ma revue de #286) fusionnée le 20/11 à 14 h 36 UTC : `develop` à `29e3945`. CI de #286 sur
  `29e3945` verte : [Tests 44755159823](https://github.com/Ganda15/rita-agent/actions/runs/44755159823) (3 176
  réussis, 102 sautés, couverture 96,15 % ; `evals` 44, `base` 59) et
  [Livraison 44755159810](https://github.com/Ganda15/rita-agent/actions/runs/44755159810). Ma nouvelle revue de #286
  sur `29e3945` : aucun constat dans ses changements ; zones floutées illisibles sur les trois images.
- Trouvé par cette revue, hors de #286 : le journal des envois nommait en clair l'étudiant flouté, avec l'heure de son
  message. Décision d'Era (option A) : les noms des deux étudiants remplacés par leur rôle dans cinq fichiers texte,
  sur la branche `noms-tiers-20-11` (détail et limites dans `CHANGELOG.md`). Restent : un nom dans une ancienne entrée
  du `CHANGELOG`, l'historique et les tags, et trois PDF suivis, laissés tels quels (décision d'Era du 20/11).

**Prochaine action** :
1. Era : push de `noms-tiers-20-11`, PR vers `develop`, ma revue, CI verte, fusion. #286 (`develop` vers `main`) la
   reprend alors ; je la relis une dernière fois, puis Era la fusionne avant le 23/11 (une seule livraison en
   production).
2. Ce soir après 22 h 05, puis la suite : points 2 à 6 du bloc du matin, inchangés.

---

## ▶️ 20/11, MATIN : COPIES, CLASSEURS ET NOTE D'ORAL FAITS ; AUDIT DE PUBLICATION, TROIS CAPTURES FLOUTÉES

**État** :
- Copies OneDrive (hors du dépôt) d'E1 v10 et d'E4 1.12, avec et sans annexes, prises aux tags et d'empreinte égale :
  `rapport-E1-2026-11-19-v10.pdf`, `rapport-E1-2026-11-19-v10-avec-annexes.pdf`, `rapport-E4-2026-11-19-v1.12.pdf`,
  `rapport-E4-avec-annexe-2026-11-19-v1.12.pdf`.
- Classeurs `_20_11_26` (hors du dépôt), faits depuis ceux du 17/11 restés intacts : versions taguées le 19/11 citées,
  T9 corrigé dans le classeur détaillé (B18), 51 tags ; statuts inchangés (137 OK), mise en forme identique, rendu
  regardé. Aucune « deux traitements ». Limite : la colonne D de la grille cite encore 61 fois des versions antérieures
  au 16/11 (comptées le 20/11 : E4 v1.2 28, E2 v1.0 14, E5 v0.7 8, E3 v1.9 6, E1 v6 2, E3 v1.5 2, E1 v3 1), déjà le
  17/11 ; leurs numéros de section ne sont pas vérifiés.
- Note d'oral Obsidian (hors du dépôt) : la réponse modèle du 07/11 sur le frein des essais de clé ne dit plus
  « quinze minutes au plus ». Le présentateur n'a pas été cherché.
- Rattrapage des cours : la fenêtre d'avant 9 h à Paris est passée (session ouverte à 9 h 47) ; cours de production
  toujours au 18/11.
- Audit de publication en lecture seule : gitleaks vert sur tout l'historique de toutes les branches ; aucun workflow
  en `pull_request_target`, aucun exécuteur auto-hébergé, jeton en lecture par défaut ; secrets masqués dans les
  journaux relus (vigie, livraison, ingestion) ; aucune adresse de courriel personnelle ni numéro de téléphone dans
  `main`. Trouvé : le nom et la photo d'un étudiant dans une capture. Floutés, avec l'avatar et le nom du formateur, les
  membres d'un salon vocal et l'icône d'un serveur, dans trois captures de `evidence/C6/` (détail par fichier dans
  `evidence/C6/README.md`, registre M2, `CHANGELOG.md`) ; les originaux restent dans l'historique et dans les tags. Le
  doublon non flouté `evidence/C6/retour-S41-capture-2026-11-09-1140.png` reste hors du dépôt, exclu localement
  (`.git/info/exclude`) pour qu'aucun `git add .` ne le publie.
- À régler par Era juste après le passage en public : approbation des workflows des contributeurs extérieurs
  (« Require approval for all outside collaborators », réglage absent tant que le dépôt est privé) ; wiki désactivé
  (vide) ; alertes de secret scanning attendues sur les deux clés révoquées d'INC-008 ; visibilité du Kanban.

**Prochaine action** :
1. #285 fusionnée le 20/11 à 11 h 36 UTC (`develop` à `6d5b400`) ; PR #286 (`develop` vers `main`) ouverte, à fusionner
   après la correction de sa revue, pour que `main` porte les captures floutées le 23/11.
2. Rattrapage des cours de production chaque jour de bourse jusqu'au jury, après 22 h 05 à Paris (décision d'Era du
   20/11) : ce soir 20/11 (séances du 19 et du 20/11, et le 18/11 de CRI.PA), puis les 23, 24, 25, 26, 27 et 30/11, et
   le 01/12 avant 9 h. Guide `docs/exploitation.md` § 8. La sortie du serveur est gardée chaque soir, puis versée dans
   `evidence/C3/` par une seule PR le 30/11. Le 26/11, New York est fermé (Thanksgiving) : FTI et SLB n'ont pas de cours
   ce jour-là, c'est attendu.
3. 22/11 : notice d'accès du jury, rédigée avec Era, hors du dépôt, puis essai d'accès en la suivant pas à pas, comme un
   membre du jury, avant son envoi. Décision d'Era (20/11) : la clé est donnée deux fois, dans cette notice séparée des
   rapports, déposée avec les cinq PDF, puis de nouveau au début de l'oral ; jamais dans un rapport ni dans le dépôt.
   Message à la cheffe de projet pour qu'elle transmette la notice au jury.
4. 23/11, dans cet ordre : dépôt public puis Kanban, réglages ci-dessus, liens vérifiés sans connexion (revoir les deux
   liens trouvés en 503 : la note de la CNIL, `docs/veille/2026-S34-top10-agentique.md:27`, et
   `docs/rapports/E4/rapport-E4.md:643`), cinq PDF et la notice dans le Drive, envoi par Era. L'adresse d'auteur des
   commits reste visible (décision d'Era du 20/11 : réécrire l'historique est exclu, les tags sont figés).
5. Samedi 28/11 : redémarrage du serveur (« System restart required »), puis `/health` et un essai d'accès ; un jour
   sans bourse ni rattrapage, qui laisse trois jours pour corriger si le service ne revient pas. La procédure, absente
   de `docs/exploitation.md`, s'écrit avant, le 27/11 : conteneurs de l'API et de la base relancés (`restart:
   unless-stopped` dans `docker-compose.yml`), Caddy actif (hors de Compose), `/health`, essai de clé, retour arrière
   si l'API ne revient pas. Le 30/11 : nouvel essai d'accès avec la clé, depuis une fenêtre privée.
6. Après le jury, le 01/12 au soir : changer la clé de production, et `RITA_API_KEY_VIGIE` si elle porte la même
   valeur.

---

## ▶️ 19/11, SOIR : #283 FUSIONNÉE, CI VERTE ; E2 ET E3 SANS CHANGEMENT ; LE 20/11, COPIES D'E1 ET D'E4 PUIS CLASSEURS

**État** :
- #283 (`etat-19-11` vers `develop`) fusionnée le 19/11 à 16 h 38 UTC : `develop` à `59c4bb9`. CI de `develop` verte :
  [Tests 44568339546](https://github.com/Ganda15/rita-agent/actions/runs/44568339546) (3 176 réussis, 102 sautés,
  couverture 96,15 % ; `evals` 44 réussis, `base` 59) et
  [Livraison 44568339414](https://github.com/Ganda15/rita-agent/actions/runs/44568339414) (`lint`, `secrets` et
  `construire-et-publier` verts ; un push sur `develop` ne déploie pas). `main` et la production restent sur `4b2d8ad`.
- **E2 et E3 : rien à refaire** (contrôle en lecture seule, 19/11 au soir). Ils restent `livrable-E2-v6` (E2 1.7) et
  `livrable-E3-v7` (E3 2.6), sur `fe13d24` : `docs/rapports/E2` et `docs/rapports/E3` n'ont pas changé entre `fe13d24`
  et `4b2d8ad`. La correction RGPD ne les touche pas : aucun des deux ne compte les traitements ni ne parle de
  « 15 minutes » ; E2 cite le § 0, T6, T8 et le point 12 du registre, tous inchangés ; E3 date le frein des essais de clé du 7/11, comme le registre corrigé.
  PDF du dépôt et copies OneDrive du 16/11 (E2 avec et sans annexe, E3) identiques aux tags, empreintes SHA-256
  comparées. Limite : seuls les passages que la correction pouvait toucher ont été cherchés ; la dernière relecture
  d'E2 et d'E3 est le double contrôle du 16/11.
- **Copies OneDrive d'E5 v1.3 déjà faites** : `rapport-E5-2026-11-18-v1.3-relu.pdf` et
  `rapport-E5-avec-annexe-2026-11-18-v1.3-relu.pdf` (18/11, 17 h 41 à Paris) ont la même empreinte que les fichiers du tag
  `livrable-E5-v7`. Les trois autres copies du 18/11 à côté (`rapport-E5-2026-11-18-v1.3.pdf`,
  `rapport-E5-2026-11-18-v1.3-annexe-au-sommaire.pdf`, `rapport-E5-avec-annexe-2026-11-18-v1.3.pdf`) sont des états
  intermédiaires, différents du tag : ne pas les prendre pour le Drive.
- Copies OneDrive d'E1 v10 et d'E4 1.12 : pas encore faites (les dernières sont celles du 16/11, E1 v9 et E4 1.11).
- Cours de production au 18/11 (rattrapage du 18/11 à 22 h 14 à Paris) ; CRI.PA sans son 18/11, retard connu.

**Prochaine action** :
1. Era : push de la branche `etat-19-11-soir`, PR vers `develop`, CI verte, fusion.
2. 20/11 (avancé du 21/11, les tags étant posés depuis le 19/11) :
   - copies OneDrive datées d'E1 v10 et d'E4 1.12, avec et sans annexes, prises dans les fichiers du tag et comparées
     au tag par empreinte : `rapport-E1-2026-11-19-v10.pdf`, `rapport-E1-2026-11-19-v10-avec-annexes.pdf`,
     `rapport-E4-2026-11-19-v1.12.pdf`, `rapport-E4-avec-annexe-2026-11-19-v1.12.pdf` ;
   - classeurs : chercher « deux traitements » et « 15 minutes » dans les copies `_17_11_26` ; si une correction est
     nécessaire, nouvelles copies datées, versions taguées le 19/11 citées (E1 v10 et E4 1.12 du 19/11, E5 v1.3 du 18/11), statuts inchangés sauf
     décision d'Era ;
   - oraux Obsidian (`Projets/RITA/03-Oraux`) : même recherche, constats montrés à Era avant toute modification.
3. **Fixé le 19/11 au soir (décision d'Era)** : E5 va dans le Drive avec son annexe A (`rapport-E5-avec-annexe.pdf`,
   7 pages), comme le veut la consigne du 13/11 (5 PDF, annexes comprises, `CHANGELOG.md`). Les cinq PDF du 23/11, pris
   à leur tag : `rapport-E1-v10-avec-annexes.pdf` (`livrable-E1-v10`), `rapport-E2-avec-annexe.pdf` (`livrable-E2-v6`),
   `rapport-E3.pdf` (`livrable-E3-v7`, sans annexe), `rapport-E4-avec-annexe.pdf` (`livrable-E4-v9`) et
   `rapport-E5-avec-annexe.pdf` (`livrable-E5-v7`).
4. 21/11 : réserve, pour ce qui n'est pas fini le 20/11.
5. 22/11 : notice d'accès du jury (sans la clé) et message à la cheffe de projet, rédigés avec Era.
6. 23/11, dans cet ordre : Era rend publics le dépôt puis le Kanban (projet 4) ; vérificateur de liens et liens des
   tags ouverts sans connexion, zéro lien cassé ; revoir les deux liens trouvés en 503 : la note de la CNIL
   (`docs/veille/2026-S34-top10-agentique.md:27`, tout le site en 503 le 18/11, 200 le 19/11) et
   `docs/rapports/E4/rapport-E4.md:643` (demande anonyme vers le dépôt encore privé) ;
   Era dépose les cinq PDF des tags dans le Drive ; Era envoie la notice et le message.
7. Avant le jury : redémarrage du serveur (« System restart required »), puis `/health` ; rattrapages des cours le
   30/11 après 22 h 05 et le 01/12 avant 9 h ; le 18/11 de CRI.PA au prochain rattrapage.

---

## ▶️ 19/11, APRÈS-MIDI : TROIS TAGS POSÉS SUR `4b2d8ad`, EXÉCUTIONS VERTES ; PRODUCTION SUR `4b2d8ad`

**État** :
- #281 (`rgpd-t9-19-11` vers `develop`, `7deaf92`) puis #282 (`develop` vers `main`) fusionnées : `main` à `4b2d8ad`,
  livré (`/health` à 11 h 29 UTC : `4b2d8ad`, construit le 19/11 à 11 h 00 UTC). Double contrôle des trois PDF avec
  annexes (E1 v10, E4 1.12, E5 v1.3) fait le 19/11 à `7deaf92` : rien à corriger dans les passages relus.
- Tags posés par Era, un par push, tous sur `4b2d8ad` :

  | Tag | Exécution Livraison | Image publiée |
  |---|---|---|
  | `livrable-E1-v10` | [44516224319](https://github.com/Ganda15/rita-agent/actions/runs/44516224319), verte à 11 h 43 UTC | `sha256:c4a93fb3…` |
  | `livrable-E4-v9` | [44533695366](https://github.com/Ganda15/rita-agent/actions/runs/44533695366), verte à 13 h 37 UTC | `sha256:8b559278…` |
  | `livrable-E5-v7` | [44543103706](https://github.com/Ganda15/rita-agent/actions/runs/44543103706), verte à 14 h 29 UTC | `sha256:57971220…` |

  Chaque exécution a rejoué la Definition of Done sur son tag : 2 912 tests réussis et 122 sautés, 44 portes
  d'évaluation, liens internes sans casse, tag cité dans cet état et le `CHANGELOG`. Les empreintes diffèrent parce
  que l'image porte sa date de construction ; le code est le même commit. E2 et E3 restent `livrable-E2-v6` et
  `livrable-E3-v7`, sur `fe13d24`.
- Liens vérifiés après les tags (`scripts/verifier_liens.py`, fini à 14 h 34 UTC) : 563 internes, 775 externes, un seul
  signalé, `docs/rapports/E4/rapport-E4.md:643` en HTTP 503 (demande anonyme vers le dépôt privé) ; le fichier visé
  existe au tag `livrable-E4-v5` d'après `gh` (1 971 octets). Les 30 liens du dépôt vers les trois nouveaux tags,
  contrôlés un par un avec `gh` au tag qu'ils citent : 30 trouvés, 0 manquant.
- Cours de production au 18/11.

**Prochaine action** :
1. Era : push de la branche `etat-19-11`, PR vers `develop`, CI verte, fusion.
2. 21/11 : copies OneDrive datées (E1, E4, E5, avec et sans annexe) et classeurs ; chercher « deux traitements » dans
   les classeurs `_17_11_26` et les oraux Obsidian.
3. 22/11 : notice du jury et message. 23/11 : dépôt public, liens vérifiés sans connexion (le 503 de la CNIL à revoir),
   les 5 PDF avec annexes sur le Drive ; Era envoie.
4. Avant le jury : redémarrage du serveur (« System restart required ») ; rattrapages des cours le 30/11 après 22 h 05
   et le 01/12 avant 9 h ; le 18/11 de CRI.PA au prochain rattrapage.

---

## ▶️ 19/11 : CORRECTION RGPD, E1 v10 ET E4 1.12 POUR `livrable-E1-v10` ET `livrable-E4-v9` ; REGISTRE T9 CORRIGÉ

**État** :
- Manque trouvé le 17/11, corrigé le 19/11 sur la branche `rgpd-t9-19-11` (partie de `develop` à `9e956f6`) :
  E1 § 5 (« dont deux avec une donnée personnelle ») et E4 § 2.4 (« Deux traitements… ») comptaient trop peu de
  traitements ; le registre donnait pour T9 « 15 minutes au plus », alors que le code n'oublie une adresse qu'à son
  prochain appel après la fenêtre, au-delà de 10 000 adresses ou au redémarrage.
- **E1 v10** : phrase C1 du 17/11 ; `rapport-E1.pdf` 5 pages, sections aux mêmes pages ; 32 liens vers
  `livrable-E1-v10` ; `rapport-E1-v10-avec-annexes.pdf` 10 pages (couverture et annexes de la v9, seule la version
  de la couverture change). **E4 1.12** : § 2.4 (T3, T5, T6 et T9), 20 et 36 pages, sommaire et signets inchangés.
- **Registre T9** : fenêtre de comptage, absence de durée maximale écrite comme limite, actif depuis le 07/11 ; même
  texte dans le commentaire de `api/limiteur.py` et la docstring de `tests/test_essais_de_cle.py` (aucun code changé).
- README, guide du jury (qui citait encore E5 v1.2), file de validation et plan E4 pointent E1 v10, E4 1.12 et E5 v1.3.
- `main` et production toujours sur `16567ec` ; cours de production au 18/11.

**Prochaine action** :
1. Era : relecture de la branche `rgpd-t9-19-11`, puis push, PR vers `develop`, CI verte, fusion.
2. 20/11 : double contrôle par l'autre agent (E1 v10, E4 1.12, E5 v1.3) ; puis PR `develop` vers `main` et les tags
   `livrable-E1-v10`, `livrable-E4-v9` et `livrable-E5-v7`, un par push ; liens des PDF vérifiés après les tags.
3. 21/11 : copies OneDrive datées (E1, E4, E5, avec et sans annexe) et classeurs ; chercher « deux traitements » dans
   les classeurs `_17_11_26` et les oraux Obsidian.
4. Puis l'ordre du 22 et du 23/11, inchangé.

---

## ▶️ 18/11, SOIR : RAPPORT E5 v1.3 AVEC L'ANNEXE A, POUR `livrable-E5-v7` ; PRODUCTION SUR `16567ec`, COURS AU 18/11

**État** :
- #277 (`etat-17-11` vers `develop`) puis #278 (`develop` vers `main`) fusionnées : `main` à `16567ec`, livré (`/health` :
  `16567ec`, construit le 18/11 à 10 h 33 UTC ; Livraison 44285366723 et Tests 44285366655 verts). Les cinq tags restent
  sur `fe13d24`.
- **Rapport E5 v1.3** (commit `76f6502`, branche `e5-v1-3-corrections`, locale) : passages corrigés (traces Langfuse,
  neuf autres incidents, retour à OK du 15/11 dans #250, alertes Langfuse) et annexe A (A1 le dispositif, C20 ; A2
  l'incident INC-009, C21). `rapport-E5-avec-annexe.pdf` : 7 pages, dont 2 en paysage ; `rapport-E5.pdf` : 5 pages.
  Vérifié le 18/11 : 384 tests de documents verts ; 33 liens GitHub d'E5, 0 cassé ; faits relus sur leurs sources ;
  rendu regardé page par page. README, CHANGELOG et cet état citent `livrable-E5-v7`.
- La copie `Downloads\NEW_RAPPORTS_RITA_XLXS_17-11-26\new\rapport-E5-avec-annexe.pdf` (17 h 26) est un état
  intermédiaire : la version du dépôt (17 h 41, commitée) a encore des corrections. Copies OneDrive à refaire depuis le
  dépôt.
- E5 v1.3 dans `develop` : #279 fusionnée (`cc3367d`).
- **Cours de production rattrapés au 18/11** (22 h 14 à Paris) : 216 cotations écrites, 0 rejetée ; 282 246 lignes
  (+108) ; taux des cinq devises au 18/11. CRI.PA a son 17/11 mais pas son 18/11 (même retard que le 17/11) : la carte
  « Fraîcheur des cours » passera à l'orange le 19/11 au matin. Preuve :
  `evidence/C3/rattrapage-production-2026-11-18/`, branche `etat-18-11`.

**Prochaine action** :
1. Era : push de `etat-18-11`, PR vers `develop`, CI verte, fusion.
2. 19/11 : correction RGPD (E1 v10, E4 1.12, registre T9), sur une branche partie de `develop`.
3. 20/11 : double contrôle par l'autre agent, E5 v1.3 compris ; puis PR `develop` vers `main` et les tags, dont
   `livrable-E5-v7`, un par push.
4. 21/11 : copies OneDrive datées (E5 avec et sans annexe) et classeurs.
5. Puis l'ordre du 22 et du 23/11 ci-dessous, inchangé.

---

## ▶️ 17/11, FIN DE JOURNÉE : PRODUCTION SUR `ceab6f3`, COURS AU 17/11 ; ÉLÉMENTS GITHUB FERMÉS ; ORDRE DU 22 ET DU 23/11 FIXÉ

**État** :
- #275 puis #276 (`develop` vers `main`) fusionnées : `main` à `ceab6f3`, sept contrôles verts, revues Claude et Codex sans
  remarque ; livré (`/health` : `ceab6f3`, construit le 17/11 à 10 h 07 UTC ; Livraison 44060727287 et Tests
  44060727506 verts). Les cinq tags restent sur `fe13d24`. Dépôt encore privé.
- Copies de lecture datées des huit PDF du 16/11 dans OneDrive (`reports`, avec et sans annexes), empreintes égales au
  dépôt et aux tags ; les cinq à déposer le 23/11 sont les versions avec annexes d'E1, E2 et E4, plus E3 et E5.
- Classeurs : copies `_17_11_26` faites depuis celles du 15/11 (versions du 16/11 citées, clé par client reportée après
  le jury en grille D38 et préparation E2, Azure de retour le 16/11, 48 tags) ; statuts inchangés (137 OK), mise en
  forme identique, rendu vérifié. Point « classeurs (grille D38, préparation E2) » fait.
- Éléments GitHub (décision d'Era, textes relus par l'autre agent puis corrigés) : #152, #78, #79, #28, #41 et #73
  fermées avec un commentaire de preuve (liens figés sur `ceab6f3`) ; PR #88 fermée sans fusion, branche `mistral-ue`
  gardée (clés révoquées, INC-008) ; #21 commentée et laissée ouverte (deux trames de revue non tenues, pas des revues).
- Base locale : séance du 16/11 présente pour 107 valeurs sur 108 ; CRI.PA s'arrête au 13/11 (publication tardive,
  connue). Collecte du 16/11 à 19 h : 6 étapes sur 6. La production restait au 13/11 jusqu'au rattrapage du soir.
- **Cours de production rattrapés au 17/11** (22 h 12 à Paris, guide suivi étape par étape, étape 4 et passage à blanc
  relus avant l'écriture) : 323 cotations écrites, 0 rejetée ; dernière séance 17/11, 282 138 lignes (+215) ; par
  séance, 13/11 : 108, 16/11 : 108, 17/11 : 107 (CRI.PA manque, publication tardive connue) ; 12 taux lus, 15 écrits,
  cinq devises au 17/11 ; écran Indicateurs « cours du 17/11/2026 ». Preuve :
  `evidence/C3/rattrapage-production-2026-11-17/`. La carte Fraîcheur passera à l'orange le 18/11 au matin tant que
  CRI.PA n'a pas son 17/11 ; le prochain rattrapage le prendra.

**Prochaine action** :
1. 18/11 : pousser cette mise à jour de l'état et la preuve du rattrapage du 17/11 (branche `etat-17-11`), PR vers
   `develop`, puis vers `main`.
2. 22/11 : rédiger avec Era la notice d'accès du jury (sans la clé) et le message à la cheffe de projet.
3. 23/11, dans cet ordre : Era rend publics le dépôt puis le Kanban (projet 4) ; vérificateur de liens et liens des
   cinq tags ouverts sans connexion, zéro lien cassé ; Era dépose les cinq PDF des tags dans le Drive ; Era envoie la
   notice et le message.
4. Opération séparée, à préparer avant le jury : redémarrage du serveur (« System restart required »), puis `/health`.
5. Rattrapages des cours en production : le 30/11 après 22 h 05 et le 01/12 avant 9 h ; un de plus avant une
   répétition si Era le veut.

---

## ▶️ 17/11, MATIN : #274 FUSIONNÉE ; COURS DE PRODUCTION À LA MAIN JUSQU'AU JURY ; ÉCART DES TAUX EXPLIQUÉ

**État** :
- #274 (dépôt public le 23/11, cinq tags consignés) fusionnée dans `develop` (`9dddc87`), CI verte : 3 176 réussis,
  97 sautés. Reste la PR `develop` vers `main`. Production toujours sur `fe13d24` ; dépôt encore privé.
- Cours de production au 13/11 (dernier rattrapage le 14/11) : sur le serveur, rien ne les rafraîchit tout seul
  (E4 § 6.4, `docs/exploitation.md` § 8).
- **Décision d'Era (17/11)** : rattrapage à la main jusqu'au jury, planification sur le serveur après le 01/12 (#36) ;
  raisons dans `CONTINUITE.md`, F.
- Écart « 8 taux lus, 10 écrits » du 14/11 expliqué par le code : l'étape `ecb` lit les quatre devises suivies et ajoute
  une ligne EUR = 1 par jour publié (`etape_taux_change`, `pipelines/ingest.py`), soit 4 devises × 2 jours (12 et 13/11)
  = 8 lus, plus 2 lignes EUR = 10 écrites. Comptage voulu, pas un défaut ; non recompté ligne à ligne dans la base de
  production.

**Prochaine action** :
1. PR `develop` vers `main` (publication du 23/11 et ce bloc), CI et revue lues avant la fusion.
2. Un rattrapage avant une répétition, si Era le veut (guide : `docs/exploitation.md` § 8).
3. Puis la liste du 16/11, nuit : le 23/11, publication et liens sans connexion, puis le Drive ; éléments GitHub ;
   classeurs ; redémarrage du serveur.

---

## ▶️ 16/11, NUIT : CINQ TAGS POSÉS SUR `fe13d24`, EXÉCUTIONS VERTES ; DÉPÔT PUBLIC LE 23/11

**État** :
- PR #272 (corrections de la relecture de #271) puis #273 (`develop` vers `main`) fusionnées : `main` à `fe13d24`, en
  production (`/health`, image construite le 16/11 à 21 h 48 UTC) ; CI de #273 : 3 176 réussis, 97 sautés,
  couverture 96,15 %.
- Definition of Done de `livrable-E1-v9` verte sur une copie propre de `main` : 5 lignes ✅, 3 183 réussis, 90 sautés.
- Cinq tags posés par Era sur `fe13d24`, un par push, chaque exécution Livraison verte (Definition of Done rejouée,
  image publiée) : `livrable-E1-v9` (43966245586), `livrable-E2-v6` (43968435785), `livrable-E3-v7` (43970326361),
  `livrable-E4-v8` (43972119221), `livrable-E5-v6` (43974051755).
- M2 en lecture seule (16/11) : aucune adresse de courriel personnelle ni numéro de téléphone dans les fichiers suivis.
  Noms de personnes tierces remplacés par leur rôle dans les documents de l'état actuel (#272).
- **Décision d'Era (16/11, nuit)** : le dépôt devient public le 23/11, et non juste après les tags. Les fichiers figés
  par les tags disent « publication prévue juste après les tags du 16/11 » : plan daté, laissé tel quel ; `main` dit
  « le 23/11 ».
- Liens après les tags, avec la connexion de l'auteur (dépôt encore privé) : 560 internes et 774 externes vérifiés,
  0 cassé (16/11, nuit, sur `640f45e`) ; les 8 liens vers les tags passent. À refaire sans connexion le 23/11,
  après la publication.

**Prochaine action** :
1. 23/11 : Era rend publics le dépôt puis le Kanban (projet 4, réglage séparé) ; vérificateur de liens et liens des
   cinq tags ouverts sans connexion, zéro lien cassé ; puis Era dépose les cinq PDF des tags dans le Drive.
2. Fermeture des éléments GitHub selon la relecture du 16/11 (#152, #78, #79, #28 et #41 ; #73 après sa note datée ;
   #21 reste ouvert ; PR #88 fermée sans fusion), décision d'Era.
3. Classeurs (grille D38, préparation E2) et copies OneDrive datées ; notice d'accès du jury (sans la clé) et message à
   la cheffe de projet, envoyé par Era.
4. Redémarrage du serveur après le gel (« System restart required »), puis contrôle de `/health`.

---

## ▶️ 16/11, SOIR : RELECTURE DE #271 REPRISE ; PUBLICATION DU DÉPÔT JUSTE APRÈS LES TAGS

**État** :
- PR #268 et #269 fusionnées : `main` à `8b2509f`, en production (`/health`) ; CI : 3 176 réussis, 97 sautés,
  couverture 96,15 %, 59 tests PostgreSQL.
- PR #270 fusionnée dans `develop` (`6e68657`) : README, guides et index mis d'accord avec l'état du 16/11. Puis PR
  #271 fusionnée dans `main` le 16/11 à 20 h 44 UTC (`0d8c58e`) : sept contrôles verts, revues automatiques sans
  remarque ; Tests de `main` verts, livraison en cours au moment de ce commit.
- Relecture de #271 par l'autre agent, finie après sa fusion : quatre corrections reprises sur la branche
  `corrections-relecture-pr271` (publication annoncée trop tôt ; codes 503 de `/briefing` et de `/question`
  distingués ; chronologie de `docs/ARCHITECTURE.md` ; registre T6, T8 et M2), plus ses trois précisions facultatives.
  Elles vont dans `main` par une nouvelle PR `develop` vers `main`, avant les tags.
- Relecture des huit éléments GitHub résolus, par l'autre agent : #152, #78, #79, #28 et #41 fermables avec leurs
  preuves ; #73 après une note datée de résolution au critère R10 ; #21 pas entièrement terminé (la revue
  hebdomadaire documentée n'est pas prouvée) ; PR #88 à fermer sans fusion, remplacée par la solution actuelle.
- Décisions du 16/11 après l'audit des traces (lecture seule) : mentions de l'assistant d'IA gardées telles quelles ;
  tirets longs des anciens fichiers laissés ; **dépôt rendu public juste après les cinq tags**, au lieu du 22/11, puis
  tous les liens des PDF vérifiés sans connexion. Au 16/11, le dépôt est encore privé.

**Prochaine action** :
1. PR de `corrections-relecture-pr271` vers `develop`, CI verte, fusion ; puis une nouvelle PR `develop` vers `main`,
   contrôles verts, fusion ; Tests et Livraison de `main` verts, `/health` sur le nouveau commit.
2. Les tags `livrable-E1-v9`, `livrable-E2-v6`, `livrable-E3-v7`, `livrable-E4-v8`, `livrable-E5-v6` sur ce `main`, un
   par push, chaque exécution Livraison vérifiée.
3. M2 du registre, puis Era change la visibilité du dépôt et celle du Kanban (projet 4, réglage séparé) ; vérificateur
   de liens sans connexion, zéro lien cassé.
4. À trancher par Era : fermeture des éléments GitHub selon la relecture ci-dessus (#21 reste ouvert ; #73 après sa
   note) ; noms de personnes tierces dans les documents courants (la relecture conseille leurs rôles, preuves
   historiques gardées).
5. Classeurs (grille D38, préparation E2) et copies OneDrive datées ; notice d'accès du jury (sans la clé) et message à
   la cheffe de projet, envoyé par Era.

---

## ▶️ 16/11, FIN DE MATINÉE : AZURE RÉPOND DE NOUVEAU ; LES CINQ VERSIONS RENDUES, TAGS À POSER APRÈS `main`

**État** :
- Azure : un briefing réel servi par Azure le 16/11 à 10 h 05 UTC (journal de l'API de production) ; aucun redémarrage
  du conteneur depuis le 14/11 à 19 h 14 UTC ; clé régénérée très peu probable sans être prouvée, cause non établie
  (INC-010, issue #250 ouverte). Rien modifié côté Azure (Era). Décision d'Era : on garde les deux
  fournisseurs (`LLM_ORDRE=foundry,mistral`).
- Branche `versions-16-11`, locale : INC-010 et E2 (test du 15/11, retour du 16/11), puis les cinq versions rendues :
  E1 v9 (5 pages ; `rapport-E1-v9-avec-annexes.pdf`, 10 pages, couverture et annexes de la v8), E2 1.7 (19, 33 avec
  l'annexe), E3 2.6 (20 ; note des versions raccourcie, la première rédaction donnait 21 pages), E4 1.11 (20, 36), E5 1.2
  (5). README et guide du jury aux nouveaux tags ; CHANGELOG du 16/11.
- Double contrôle d'Era fait (relevé de l'autre agent) : neuf corrections reprises, E2, E3 et E4 rendus de nouveau,
  pages inchangées ; attendu du test de l'annexe d'E4 passé de 15 à 16 pages (décision d'Era) ; « donc avec la même
  clé » retiré d'E2.
- Suite complète en local de nouveau possible le 16/11 : 3 191 réussis, 82 sautés, 0 échec.

**Prochaine action** :
1. Push de `versions-16-11`, PR vers `develop`, CI verte, fusion ; puis PR
   `develop` vers `main`, revue, fusion.
3. Les tags `livrable-E1-v9`, `livrable-E2-v6`, `livrable-E3-v7`, `livrable-E4-v8`, `livrable-E5-v6` sur `main`, un par
   push ; liens vérifiés après les tags.
4. Classeurs (grille D38, préparation E2) et copies OneDrive datées ; notice d'accès du jury (sans la clé) et message à
   la cheffe de projet, envoyé par Era.

---

## ▶️ 16/11, 0 H 15 : ARRÊT POUR LA NUIT ; AZURE TOUJOURS 401 ; VERSIONS ET RENDUS CE MATIN

**État** :
- `develop` à `3f40928` : #266 (retours de l'oral blanc du 13/11 dans les sources E1 à E5 ; glossaire d'E2 en un seul
  tableau, E2 à 19 pages ; schéma A3 d'E2 limité à 120 mm) et #267 (clé par client), fusionnées par Era, CI verte avant
  chaque fusion (#267 : 3 176 réussis, 97 sautés).
- Clé par client : décision d'Era du 15/11, réalisation reportée après le jury du 01/12 (réponse « 3-B » du formateur
  du 07/11). Écrit dans E1 § 7, `docs/BUDGET.md`, le statut du plan 002 et `CONTINUITE.md` (F et M).
- Azure : test d'Era sur le serveur le 15/11 à 23 h 03 UTC, **401**, clé inchangée. Commit local `6c90071` sur la
  branche `versions-16-11`, non poussée : INC-010 et encadré d'E2 § 4.2. Mistral sert toujours de secours.
- Poste : la suite complète ne tourne plus (Smart App Control refuse `uuid_utils`) ; tests de documents avec
  `--noconftest`, suite complète par la CI.
- Serveur : « System restart required », 50 mises à jour en attente ; redémarrage à planifier après le gel, avec un
  contrôle de `/health`.

**Prochaine action (16/11)** :
1. Era refait le test Azure sur le serveur juste avant les rendus ; l'heure (ou le retour d'Azure) va dans INC-010 et E2.
2. Gel du code. Versions et « Cette version » (E1 v9, E2 1.7, E3 2.6, E4 1.11, E5 1.2) ; rendus officiels ; numéros
   tenus à la main (annexes d'E2 A1 à A6 en p. 20, 21, 22, 23, 27, 29 ; E4 A7 « 31 à 36 ») ; E1 assemblé ; CHANGELOG,
   décision du 15/11 comprise ; cet état ; classeurs (grille D38, préparation E2) ; copies OneDrive datées.
3. Notice d'accès du jury (sans la clé) et message à la cheffe de projet, envoyé par Era.
4. Double contrôle d'Era, PR `develop` vers `main`, puis les tags, un par push.

---

## ▶️ 14/11, FIN D'APRÈS-MIDI : PRODUCTION SUR `9d48870`, MISTRAL EN SECOURS ET NOMMÉ PAR L'INTERFACE ; COURS AU 13/11 ; SESSION DE TEST E5 FAITE

**État** : Azure refuse toujours la clé du serveur (HTTP 401, cause non trouvée). Mistral sert de secours : sur le
serveur, `LLM_ORDRE=foundry,mistral` (décision d'Era : Azure d'abord quand il répondra, Mistral ensuite). La production
tourne sur `main` à `9d48870`, livrée à 16 h 52 (heure de Paris, exécution « Livraison » 43611440361 : pré-test,
bascule et contrôle après bascule verts). Avant, `2dd385f`, livrée vers 14 h 32. Cours de production au 13/11
(281 923 cotations). Session de test E5, faite sur `2dd385f` : 11 requêtes, toutes les cartes du tableau de bord
saines, 0,03 € comptés au prix d'Azure (un majorant du coût de Mistral).

**Fait en fin d'après-midi** : #258 (preuves C3 et C20, cet état) et #259 (l'interface nomme Mistral) fusionnées dans
`develop`, CI verte avant chaque fusion ; #260 vers `main`, revue sans remarque ; livrée sur `9d48870`. Vérifié en
production (16 h 05 UTC) : `/health` répond 200 ; la mention de l'écran Question nomme Azure puis Mistral « dans
l'Union européenne et l'AELE » ; `briefing.html` charge `briefing.js?v=6f18cebe6e`, qui contient `["mistral",
"Mistral"]`. La note du coût du tableau de bord (« majorée au prix public Azure ») reste vraie : les jetons de Mistral
sont comptés au prix d'Azure, plusieurs fois plus cher que celui de Mistral Large 3 relevé le 10/10
(`evidence/C7/banc-2026-11-07-comparaison/README.md`).

**Prochaine action** :
1. Fusionner dans `develop` la PR de cette mise à jour de l'état.
2. Registre RGPD : la quatrième vérification de la fiche `docs/lecture-contrat-mistral-2026-11-13.md` (liste des
   sous-traitants de Mistral) reste à lire par Era.
3. Lundi 16/11 : gel du code ; notice d'accès du jury (sans la clé) ; message à la cheffe de projet (les deux xlsx du
   Drive, le canal privé de la clé du jury, le dépôt public à partir du 22/11).
4. Puis les points 4 à 6 du bloc du 13/11 au soir (22/11 dépôt public, 23/11 dépôt des 5 PDF, rattrapages du 30/11
   après 22 h 05 et du 01/12 avant 9 h).
5. Azure : fiche d'incident `evidence/C21/INC-010-azure-repond-401.md` (issue #250, toujours ouverte), cause non
   établie. Une panne mondiale de Microsoft 365 (12 au 14/11, MO1550821) coïncide, sans lien prouvé : services et
   erreurs différents (503, délais, pas de 401), et la clé reçoit **encore 401** le 14/11 vers 17 h 20 UTC, après
   l'annonce du rétablissement : hypothèse très peu probable, la cause est côté compte. Ce qui trancherait encore : le
   portail (journal d'activité de la ressource, état de l'abonnement, crédit, Service Health) ; l'heure du dernier
   appel réussi dans Langfuse. Si la clé change, Era
   la remplace dans le fichier d'environnement du serveur, puis l'API est relancée ; la cascade reprend Azure en premier
   sans autre livraison.

**Fait le 14/11** :
- Matin : clé Azure testée de nouveau, toujours 401. Plan B : #251 (Mistral en secours d'Azure, briefings et questions,
  éteint par défaut), fiche de lecture du contrat de Mistral et registre RGPD (T6, T8) versés. Contrôle d'Era dans la
  console Mistral : l'utilisation des données d'API pour l'entraînement est désactivée, les modèles Labs aussi.
- Livraison de #253 (`a81cd83`) refusée, en quatre essais, par trois obstacles : le jeton GHCR du serveur avait expiré
  le 13/11 (renouvelé par Era jusqu'au 31/12/2026) ; le budget GitHub Packages était à 0 $ (budgets posés par Era :
  Actions 25 $, Packages 10 $) ; une question échouait après la bascule sans que le journal dise pourquoi. La production
  est restée sur `770d440` à chaque échec.
- #254 : le déployeur écrit au journal la raison d'un contrôle en échec (code HTTP, statut, motif, jamais un texte). La
  livraison suivante (`05c081f`) a été refusée au pré-test avec une raison lisible : `CITATIONS_INVALIDES`.
- #256 : Mistral Large 3, le modèle de production, omettait le numéro de l'extrait dans le texte (0 réponse valide sur
  6). Consigne précisée, avec un exemple de forme : 8 sur 8 (`evidence/C11/citations-mistral-2026-11-14/`).
- #257 (`2dd385f`) livrée et vérifiée.
- Cours rattrapés au 13/11 par Era avec le guide corrigé (#245) : `evidence/C3/rattrapage-production-2026-11-14/`.
- Session de test E5, juste après la livraison : `evidence/C20/session-test-2026-11-14/` (capture, journal, issues).

**Limites** :
- Tant qu'Azure refuse la clé, toutes les réponses viennent de Mistral. Il s'abstient sur Q1, où le jeu de
  démonstration attend une réponse.
- Le modèle Mistral du poste (`MISTRAL_MODEL`, Large 4) n'est pas celui de la production (Large 3) : un essai local
  ne mesure pas exactement la production.
- Rattrapage du 14/11 : 10 lignes de taux de change écrites pour 8 lues, pas encore expliqué (les cours, eux, sont
  exacts : 217 lues, 217 écrites).
- Dates à surveiller : jeton GHCR jusqu'au 31/12/2026 (après le jury) ; budgets GitHub jusqu'au 01/12.

## ▶️ 13/11, NUIT : AZURE REFUSE LA CLÉ (HTTP 401) ; LIVRAISON REFUSÉE AU PRÉ-TEST ; PRODUCTION INCHANGÉE (`770d440`)

**État** : depuis le 13/11 vers 20 h (heure de Paris), Azure répond 401 à la clé du serveur, testée seule hors de RITA
(`curl` sur `/models`, seul le code affiché). Briefings et questions sont en panne en production ; les données, les
indicateurs et la protection par clé fonctionnent. La livraison de #249 (`main` à `b276e9a`) a été **refusée au
pré-test** (`briefing`, `question`) : la production est restée sur `770d440`, saine. La page publique de Microsoft ne
montrait aucun incident (20 h 40 UTC) ; le portail Azure ne s'ouvrait pas pour Era.

**Prochaine action** (plan A puis B, décision d'Era du 13/11) :
1. Le 14/11 au matin : refaire le test de la clé sur le serveur. Si 200 : relancer la livraison échouée
   (`gh run rerun 43489074587 --failed`), puis vérifier la production et faire la session E5.
2. Si 401 : portail Azure (clés de la ressource, état de l'abonnement, crédit, Service Health). Clé changée : Era la
   remplace dans le fichier d'environnement du serveur, puis la livraison est relancée.
3. Plan B, dans tous les cas : Mistral en second fournisseur, briefings **et** questions (aujourd'hui, les questions
   passent par Azure seul et le pré-test exige une question : toute livraison est refusée tant qu'Azure répond 401).
   Avant le code : les quatre vérifications de la fiche `docs/lecture-contrat-mistral-2026-11-13.md` (préparée le
   13/11, non commitée, en attente de la décision d'Era).

## ▶️ 13/11, SOIR : ORAL BLANC 2 PASSÉ ; CONSIGNES DE REMISE DU 23/11 ; AXES DE LA COURBE ET GUIDE DU RATTRAPAGE DANS `develop`

**Partage du travail jusqu'au jury (décision d'Era, 13/11)** : l'application, les 5 PDF et le dépôt d'un côté ; la
présentation de l'autre, préparée hors du dépôt. Era garde push, fusions et tags. Objectif : la partie technique finie
le lundi 16/11 au soir, gel du code compris, pour laisser la suite à la présentation.

**Prochaine action** :
1. #247 (adresses de courriel retirées des documents) : fusionner quand la CI est verte.
2. PR `develop` vers `main` : livre en production les axes de la courbe (#244), le guide du rattrapage (#245), la
   description des valeurs radiées (#242), le README (#243), la preuve du 11/11 (#246) et #247. Puis vérification de la
   production, puis **session de test E5** par Era : 10 questions et 1 demande de conseil en moins de 15 minutes, environ
   0,10 €, **après** la livraison (elle remet les compteurs à zéro) ; captures datées dans `evidence/C20/`.
3. Lundi 16/11 : gel du code ; notice d'accès du jury prête (sans la clé) ; message à la cheffe de projet envoyé par
   Era (les deux xlsx du Drive, le canal privé de la clé du jury, le dépôt public à partir du 22/11).
4. 22/11 : Era rend publics le dépôt et le Kanban (projet 4, réglage séparé) ; tous les liens des 5 PDF vérifiés sans
   connexion, zéro lien cassé.
5. 23/11 : Era dépose les 5 PDF des tags dans le Drive attribué ; aucun ne change (vérifié le 13/11, voir plus bas).
6. 30/11 après 22 h 05 et 01/12 avant 9 h : rattrapage des cours avec le guide corrigé ; carte Fraîcheur verte avant
   10 h 45.

**Fait le 13/11** :
- Oral blanc 2 (13/11, matin) : retours de la cheffe de projet, du formateur et du troisième membre du jury blanc ; temps
  mesurés sur la transcription : E2 9 min 53 pour 15, E4 17 min 13 pour 20, total 69 min 33 pour 80.
- Consignes de la dernière séance (13/11, après-midi) : 5 PDF, annexes à la fin de chacun, pris le 23/11 dans le Drive
  individuel ; noms du jury inconnus jusqu'au jour J, donc dépôt public ou accès fourni ; utilisateur de démonstration
  admis ; le jury évalue ce qui est présenté. La convocation dit que les 10 minutes de questions couvrent les
  compétences pas assez détaillées pendant la présentation.
- PR #242 à #246 fusionnées dans `develop` (`594a5c4`). #244 : axes et échelle de la courbe (manque relevé à l'oral
  blanc), tests d'abord ; deux défauts signalés par la revue automatique, reproduits par des tests puis corrigés
  (`abee0bd`). Suite locale avant la revue : 3141 passed, 82 skipped, 0 failed.
- Audit de publication en lecture seule : historique complet, 72 issues, 170 PR, 323 commentaires, 99 commentaires de
  revue, 37 cartes du Kanban. Seuls secrets : les deux clés révoquées d'INC-008 (PR #88, branche `mistral-ue`), visibles
  même si la branche est supprimée. Le travail `secrets` de la CI passe gitleaks sur tout l'historique à chaque PR.
- Les 5 PDF des tags relus contre les changements faits depuis le 09/11 : aucun ne décrit les repères de la courbe, le
  conseil « après 17 h 35 » ni la description des valeurs radiées ; aucun ne devient faux ; aucune adresse de courriel
  dans leur texte (retirée de l'E1 le 27/10).

**Limites** :
- Les PDF remis montrent la courbe d'avant le 13/11 (quatre repères, sans axe) : version datée ; la correction se montre
  à l'oral, avec sa version.
- Clé par client toujours reportée (32,5 h) : présentée comme limite, solution prévue et coût.
- Restent visibles une fois le dépôt public : l'historique d'avant le 27/10 et l'adresse d'auteur des commits.
- `evidence/C6/retour-S41-capture-2026-11-09-1140.png` reste hors du dépôt : doublon non suivi de la capture `.jpg` déjà
  versée.

## ▶️ 11/11, SOIR : COURS DE PRODUCTION RATTRAPÉS AU 11/11 ; DESCRIPTION DES VALEURS RADIÉES CORRIGÉE

**Prochaine action** :
1. Ouvrir la PR de `doc-delistee-indicateurs` vers `develop` (branche poussée le 11/11, commit `7671223`).
2. Pousser `preuve-rattrapage-2026-11-11` (cette preuve, `ETAT.md`, `CHANGELOG.md`). Elle est posée sur
   `readme-premiere-personne-2026-11-09`, poussée mais sans PR : ouvrir d'abord la PR de cette branche, sinon celle de la
   preuve porte aussi ses cinq commits.
3. Jeudi 12/11, **après 22 h 05 à Paris** : refaire le rattrapage (`--du 2026-11-11 --au 2026-11-12`), pour un
   bandeau vert le vendredi matin de l'oral blanc (sans lui : 2 jours ouvrés de retard, orange). Il relira aussi le
   11/11 de FTI, SLB et CRI.PA. Rappel posé dans l'agenda d'Era, 22 h 05.
4. Rattrapage suivant : la veille du jury (30/11), **après 22 h 05 à Paris**, pas après 17 h 35 (voir le manque
   ci-dessous).

- **Cours de production rattrapés au 11/11** (preuve : `evidence/C3/rattrapage-production-2026-11-11/`). Matin : les
  106 valeurs `OK` au 06/11, aucune cotation du 11/11. Deux essais sans écriture (variable du réseau vide, Docker refuse
  de démarrer). Avec le nom du réseau écrit en clair : passage de 18 h 39 à Paris, 431 cotations écrites, 281 383 puis
  281 706 lignes ; passage de 22 h 04, 108 lignes réécrites, total inchangé, sans doublon. Cinq devises au 11/11,
  `ANALYZE` passé. Écran Indicateurs avec la clé : « cours du 11/11/2026 », 108 valeurs, 3 cotations périmées masquées.
  CRI.PA reste au 10/11 ; les chiffres du 11/11 de FTI et SLB ne sont pas prouvés définitifs (le prochain rattrapage
  les relira).
- **Manques découverts** : le guide de rattrapage garde le réseau dans `"$RESEAU"` (étapes 6 et 7) et l'étape 4 ne dit
  de s'arrêter que si le mot de passe manque, pas si le réseau est vide ; correction après l'oral blanc, test d'abord.
  Le conseil « après 17 h 35 » (point 3 de la section du 08/11 ci-dessous, preuve du 08/11) ne vaut que pour les places
  européennes : FTI et SLB sont cotées à New York, qui ferme à 22 h à Paris.
- **Limite écrite** : la vigie ne surveille que les valeurs `OK`, alors que ALJXR.PA et STLAP.PA (`INCOHERENT`,
  collectées exprès) comptent dans la valorisation (`db/requetes.sql:48-50`). Contrôle à la main après chaque
  rattrapage, par la requête par statut de la preuve.
- **Description de `/donnees/indicateurs` corrigée** (branche `doc-delistee-indicateurs`, `7671223`) : elle disait encore
  les trois valeurs radiées au statut `OK`, alors qu'elles sont `DELISTEE` depuis la carte #48 (27/09). Test d'abord,
  rouge puis vert ; suite complète : 3134 réussis, 82 ignorés, 0 échec. Le `/docs` de production garde l'ancien texte
  jusqu'au prochain déploiement. La preuve C10 du 18/08, qui disait la même chose, est laissée telle quelle : c'était
  vrai à sa date.

## ▶️ 08/11, SOIR : CINQ TAGS POSÉS SUR `770d440` ; COURS DE PRODUCTION RATTRAPÉS AU 06/11 ; GUIDE DU RATTRAPAGE CORRIGÉ

**Prochaine action** :
1. Fait le 09/11 à 14 h 00 : remise déposée dans le Drive partagé (formateur, cheffe de projet, cheffe pédagogique), 7 fichiers identiques aux tags ; entrée du `CHANGELOG` du 09/11.
2. Fait : PR #241 fusionnée dans `develop` (`23df640`, 18 h 44 UTC, toutes les vérifications vertes, rien déployé).
   Quand le message est parti : l'entrée « remise envoyée » du `CHANGELOG`, sur la branche
   `controle-ecran-et-remise-2026-11-08` (qui porte déjà le contrôle à l'écran), puis PR vers `develop`.
3. Répétitions de l'oral blanc des 12-13/11. Pour des cours frais ce jour-là : refaire le rattrapage le 11/11 après
   17 h 35 (`docs/exploitation.md#rattrapage-cours-production`) ; même chose le 30/11 pour le jury.

- **Tags posés par Era**, un par push, sur `770d440` (fusion de #240), exécutions Livraison vertes, relues le 08/11 au
  soir : `livrable-E1-v8` 42492420018, `livrable-E2-v5` 42493593878, `livrable-E3-v6` 42493933499, `livrable-E4-v7`
  42495314219, `livrable-E5-v5` 42496640680. Anciens tags intacts. Liens des huit PDF contrôlés deux fois sur les
  versions publiées : 300 adresses distinctes, 300 répondent, 0 cassée ; liens internes valides ; 8 ancres de ligne.
- **Cours de production rattrapés au 06/11** (preuve : `evidence/C3/rattrapage-production-2026-11-08/`). Constat :
  écrans de production au 04/11, « 2 jours ouvrés de retard ». La collecte n'était pas arrêtée : la tâche du poste a
  tourné chaque soir (code 0, séances jusqu'au 06/11) mais écrit dans la base du poste ; le serveur n'a aucune collecte
  planifiée. Rattrapage lancé par Era sur le serveur : 325 cotations écrites, 0 rejetée, 281 166 puis 281 383 lignes,
  dernière séance 06/11 (07 et 08/11 : week-end), cinq devises au 06/11, `ANALYZE` passé. L'option C du 06/11 (aucune
  écriture en production avant l'oral blanc) est levée pour ce rattrapage. Contrôle à l'écran avec la clé, fait le
  même soir après la fusion de #241 : bandeau à la séance du 06/11, sans retard ; capture de l'écran Indicateurs
  (« cours du 06/11/2026 ») dans la preuve.
- **Manque découvert** : étapes 3 et 4 du rattrapage périmées depuis la carte #76 (07/11) : elles lisaient
  `DATABASE_URL` dans le conteneur de l'API, qui ne l'a plus. Premier passage à blanc du 08/11 en échec, rien écrit.
  Corrigé sur la branche : adresse clé=valeur sans mot de passe, `PGPASSWORD` lu dans le conteneur de la base, jamais
  affiché. Tests d'abord : deux tests neufs, rouges puis verts (26 réussis dans `tests/test_exploitation_doc.py`), dont
  un qui tient la doc d'accord avec `docker-compose.yml`. L'ancienne règle `cut -d:` est remplacée par une règle plus
  stricte (le mot de passe n'apparaît dans aucun `echo`) : **à valider par Era**.
- **Toujours séparé** : la collecte planifiée des cours sur le serveur (plan à écrire après l'oral blanc) ; le bandeau
  de fraîcheur conseille « Vérifier la collecte de 19h00 », qui ne concerne que le poste : trompeur en production,
  correction plus tard, test d'abord.

## ▶️ 08/11, MATIN : RAPPORTS FINAUX POUR LA REMISE DU 09/11 (`livrable-E1-v8`, `livrable-E2-v5`, `livrable-E3-v6`, `livrable-E4-v7`, `livrable-E5-v5`)

- **Fait le 08/11** : `livrable-E1-v7` posé sur `05df824` (exécution verte) avant la dernière passe. Dernière passe :
  aucun « Era » ni nom d'intervenant dans les cinq rapports (rédaction à la première personne) ; E4 : C16.1, C16.4 et
  C17.8 en vert (décision du 08/11), chacun avec sa limite exacte, total 38 ✅ ; accès du jury « à organiser pour
  l'examen » ; E2 v1.6 : notation décrite selon la preuve (textes sans le fournisseur, notes d'une IA relues et
  retenues sans modification), vigie planifiée ; E5 v1.1 ; E1 v8 (annexe A sans « Era »). Lundi 09/11 : remise,
  pas de revue. Les cinq tags se posent sur le commit de `main` qui contient cette passe, un par push.

## ▶️ REPRISE DU 08/11 : POSER `livrable-E1-v7`, `livrable-E3-v6`, `livrable-E4-v7` SUR `05df824`

**Prochaine action, dans l'ordre** :
1. `git tag livrable-E1-v7 05df824` puis `git push origin livrable-E1-v7` ; attendre l'exécution Livraison du tag, verte.
2. Même chose pour `livrable-E3-v6`, puis pour `livrable-E4-v7` : un tag par push, chacun après l'exécution du précédent.
   Ne déplacer aucun ancien tag (`livrable-E4-v6`, `livrable-E3-v5`, `livrable-E1-v6` restent tels quels).
3. Vérifier les liens publiés des trois tags, puis copier les PDF dans le dossier de lecture OneDrive (comparer au tag).
4. Era envoie au formateur les liens : E1-v7, E2-v4, E3-v6, E4-v7, E5-v4.
5. Lundi 09/11 : revue hebdomadaire consignée (C16.1). Répétitions de l'oral blanc des 12-13/11.

- **État à l'arrêt (08/11, 1 h UTC)** : PR #233 à #236 fusionnées ; `main` = `05df824`, Tests verts (3 116 réussis,
  97 ignorés, couverture 96,11 %, `base` 59) et Livraison verte ; `/health` dit `05df824`. Porte locale
  `scripts/verifier_livrable.py livrable-E1-v7` sur `05df824` : « ✅ livrable » (3 131 réussis, évaluations 44, liens,
  tag cité, arbre propre) ; les trois tags sont cités dans ETAT et CHANGELOG. Aucun des trois n'existe encore.
- **Versions à figer** : E1 v7 (10 pages avec annexes), E3 v2.5 (20 pages), E4 v1.10 (35 pages avec l'annexe). E2 reste
  `livrable-E2-v4` et E5 `livrable-E5-v4`. Les cinq rapports sont aux couleurs d'E2 et relus par un autre agent.
- **Oral** : deux phrases d'E2 à actualiser à l'oral (vigie planifiée, tag publié), notées dans Obsidian
  `Projets/RITA/03-Oraux/questions-jury-au-fil-de-l-eau.md`.

## ▶️ 08/11, NUIT : E1 v7 ET E3 v2.5 AUX COULEURS D'E2, POUR `livrable-E1-v7` ET `livrable-E3-v6` ; E4 v1.10 POUR `livrable-E4-v7`

**Prochaine action** :
1. **Era relit** `rapport-E1-v7-avec-annexes.pdf` (10 pages) et `rapport-E3.pdf` (v2.5, 20 pages).
2. PR vers `develop`, puis `develop` vers `main` ; tags `livrable-E1-v7` puis `livrable-E3-v6`, un par push, après
   les tests de `main` et `scripts/verifier_livrable.py <tag>`.
3. Era envoie les liens des quatre tags du 07-08/11 (E1, E3, E4, E5) au formateur.

- **Décision d'Era (08/11)** : tous les rapports aux couleurs du rapport E2 (tableaux, titres, code) avant l'envoi.
  E4 et E5 l'étaient déjà (tags du 07/11) ; E2 est la référence.
- **E3 v2.5** : couleurs d'E2, espacement d'E3 gardé, glossaire non zébré ; 20 pages, sommaire juste (5 tests) ; accès
  des examinateurs aligné sur E4 (à organiser après l'oral blanc, en-tête et § 3.5) ; liens « tag de cette version »
  vers `livrable-E3-v6`, les liens datés gardent leur tag.
- **E1 v7** : couleurs d'E2 dans `rapport-E1.html` (livret de 5 pages, sections aux mêmes pages) ; PDF avec annexes
  `rapport-E1-v7-avec-annexes.pdf` : couverture et annexes A à D reprises du PDF v6, seule la mention de version de la
  couverture remplacée (texte seul, image intacte), 11 liens de la couverture recréés ; les 30 liens du livret vont vers
  `livrable-E1-v7` (22 chemins, tous présents). Le script d'assemblage du 28/10, hors du dépôt, n'est pas repris.
- **README** : tableau des livrables à l'état du 08/11 (versions, pages, auto-évaluations, tags).
- **E4 v1.10, pour `livrable-E4-v7`** (contrôle d'un autre agent, 08/11) : « huit workflows » et non sept depuis `vigie.yml`
  (§ 2.2, § 5.1 avec « les cinq autres », § 5.4, C18.5) ; les « sept contrôles » exigés avant fusion restent justes. Les
  liens vers `.github/workflows/` et `docs/CI-CD.md` vont vers le nouveau tag (au tag E4-v5, il y avait sept fichiers).
  `livrable-E4-v6` reste tel quel ; 20 pages, 35 avec l'annexe ; grille inchangée.
- **Contrôle final d'un autre agent (08/11), appliqué** : E1 : Viridien présenté comme défaut corrigé le 04/11 (preuve
  C3), règle UE du 06/11 avec ses réserves, neuf fiches de traitement dont T9, clé par client à 32,5 h (environ 1 700 €
  HT, réévaluée le 14/11), trois renvois au code recalés (`db/importer.py` 152 et 339, `api/main.py` 312) ; E3 § 9 : la
  2.4 est figée sous `livrable-E3-v5`, la 2.5 le sera sous `livrable-E3-v6`. E1 reste à 5 pages, sections aux mêmes pages.

## ▶️ 07/11, 23 H UTC : `livrable-E4-v6` ET `livrable-E5-v4` POSÉS ET VÉRIFIÉS ; C20.5 VALIDÉ ✅

**Prochaine action** :
1. **Era envoie les deux liens** au formateur (lien du tag, jamais celui du dépôt) :
   https://github.com/Ganda15/rita-agent/tree/livrable-E4-v6 et https://github.com/Ganda15/rita-agent/tree/livrable-E5-v4.
2. **Lundi 09/11** : revue hebdomadaire consignée (C16.1) ; question à Elbby sur la preuve corrective.
3. **Répétitions** de l'oral blanc des 12-13/11 (E4 : D5, D7, D9 ; E5 : D2).
4. **Décision d'Era** : couleurs d'E2 dans E3 (nouvelle version et nouveau tag) ; E1 sans source Markdown.
5. **Après l'oral blanc** : C16.4 (accès du jury aux preuves).

- **PR #231** (`vigie-c20-5` vers `develop`) puis **PR #232** (`develop` vers `main`, `fcf201e`) fusionnées par Era ;
  contrôles verts sur les deux (3 116 réussis, 97 ignorés, couverture 96,11 % ; `base` 59 réussis).
- **Porte de livraison locale** : `scripts/verifier_livrable.py livrable-E4-v6` sur `fcf201e` : « ✅ livrable »
  (3 131 réussis, 82 ignorés ; évaluations 44 réussies ; 0 lien interne cassé ; tag cité ; arbre propre).
- **Tags** posés par Era, un par push, sur `fcf201e` : `livrable-E4-v6` ([exécution](https://github.com/Ganda15/rita-agent/actions/runs/42423428277), verte) et
  `livrable-E5-v4` ([exécution](https://github.com/Ganda15/rita-agent/actions/runs/42423532295), verte). Livraison de `main` verte ([exécution](https://github.com/Ganda15/rita-agent/actions/runs/42422704093)) ; `/health` dit
  `fcf201e`. Les 6 chemins d'E4 et les 18 d'E5 vers ces tags existent dans le commit tagué. Liens ouverts avec un
  compte du dépôt : HTTP 200 ; sans compte : 404 (dépôt privé, C16.4).
- **C20.5 validé ✅ par Era le 07/11** (règle 4 du registre), sur les preuves de `evidence/C20/vigie-2026-11-07/`.
- **Copies de lecture** dans `C:\Users\kanda\OneDrive\RITA\reports\` : `rapport-E4-avec-annexe-2026-11-07-v1.9.pdf`,
  `rapport-E4-2026-11-07-v1.9.pdf`, `rapport-E5-2026-11-07-v1.0.pdf`, chacune identique à son tag (SHA-1).
- **Grilles** : E4 35 ✅ · 3 🟡 (C16.1, C16.4, C17.8) ; E5 12 ✅.

## ▶️ 07/11, NUIT : C20.5 CONSTATÉ EN PRODUCTION (PROPOSÉ ✅) ; E4 v1.9 ET E5 v1.0 PRÊTS POUR `livrable-E4-v6` ET `livrable-E5-v4`

**Prochaine action** :
1. **Era relit les PDF** d'E4 v1.9 (20 pages, 35 avec l'annexe) et d'E5 v1.0 (5 pages), et **valide ou non C20.5 ✅**
   (règle 4 du registre des partiels) ; double contrôle d'un autre agent avant tout tag.
2. **Era pousse `vigie-c20-5`**, PR vers `develop`, puis PR `develop` vers `main` ; CI verte.
3. **Tags `livrable-E4-v6` puis `livrable-E5-v4`**, un par push, sur `main` après la fusion ;
   `scripts/verifier_livrable.py <tag>` avant chacun. Le tag E4-v6 doit contenir
   `evidence/C17/verification-production-2026-11-07-soir/` : sept liens d'E4 pointent vers ce tag.
4. **Lundi 09/11** : revue hebdomadaire consignée (C16.1) ; question à Elbby sur la preuve corrective.
5. **Répétitions** de l'oral blanc des 12-13/11 (E4 : D5, D7, D9 ; E5 : D2).
6. **Après l'oral blanc** : C16.4 (accès du jury aux preuves).

- **C20.5** : secret `RITA_API_KEY_VIGIE` créé à 20 h 19 16 s UTC (PR #221 a livré la planification sans lui), corrigé
  à 20 h 33 07 s ; relance manuelle à code 0 ; essai sur copie de l'image de production : #230 ouverte puis fermée par
  la vigie, #77 et #132 intacts. **Passage `schedule` constaté le 07/11 à 21 h 52 UTC**
  ([42417908976](https://github.com/Ganda15/rita-agent/actions/runs/42417908976), `main`, `6f428d6`, succès, « vigie : passage terminé, code 0 », aucune issue). Seuils
  inchangés en valeur depuis le 22/10, calcul des verdicts inchangé. Limite : 3 déclenchements pour 7 créneaux le 07/11 (10 h 13
  et 17 h 44 arrêtés faute de secret, avant la vigie). ✅ proposé dans E5 v1.0, à valider par Era.
  Preuve : `evidence/C20/vigie-2026-11-07/README.md`.
- **E4 v1.9** : contrôle final d'un autre agent appliqué (résumé p. 1, C17 dix sur onze, C17.2 cohérent, tests : 97
  ignorés dans `pytest` et 59 réussis dans `base`, aide du Briefing en défaut historique, annexe en v1.9, accès du jury
  à organiser). Lien de la p. 1 vers les annexes non ajouté : le rapport seul n'a pas d'annexe, le lien y serait mort.
  Grille : 35 ✅ · 3 🟡 (C16.1, C16.4, C17.8).
- **E5 v1.0** : vigie programmée (§ 5), #230 (§ 6), passage planifié avec son lien, limite de GitHub (§ 8) ; douze ✅
  si Era valide C20.5.
- **Couleurs d'E2 reportées dans E4 et E5** (demande d'Era, 07/11, nuit) : tableaux à en-tête marine et lignes zébrées,
  titres en dégradé, code coloré ; l'espacement de chaque rapport est gardé (E4 : 20 pages, 35 avec l'annexe ; E5 :
  5 pages), relus page par page. E5 : trois formulations de la relecture appliquées (Langfuse examiné le 06/11,
  périmètre de ce qui n'est jamais enregistré, fermeture manuelle dans la chaîne Langfuse). **Pas encore fait** :
  E3 (`livrable-E3-v5`, sans ces couleurs) demanderait une nouvelle version et un nouveau tag ; E1 (`livrable-E1-v6`)
  n'a pas de source Markdown dans le dépôt. Décision d'Era.
- **Encore ouverts** : astérisques affichés dans le texte du Briefing ; « +0,00 % » ; S7 en partie ; #77 et #132
  ouvertes, résolution non prouvée ; contrôle des nombres (zone sous garde, plan à écrire).
- **Tests** (commit `7c18688`) : 3131 réussis, 82 ignorés, 0 en échec, en local (`evidence/C20/vigie-2026-11-07/pytest-complet-7c18688.txt`).

## ▶️ 07/11, SOIR : S9, C17.7 ET LES CORRECTIONS DE #226 EN PRODUCTION (VÉRIFIÉ) ; C16.1 GARDÉ À CONSOLIDER

**Prochaine action** :
1. **Prochaine version d'E4** (§ 4.7 : Indicateurs D 52 puis B 76 ; S9 corrigé et déployé ; grille ; poids corrigés de
   Briefing et Question du 06/11), liens vers un nouveau tag ; double contrôle d'un autre agent ; puis le tag. Régler au
   passage `livrable-E4-v6` et `livrable-E5-v4`, toujours absents de GitHub.
2. **Réévaluer C17.7 et C17.8** avec Era, sur les preuves : C17.8 doit aussi regarder S7, encore partiel.
3. **Lundi 09/11** : Era tient la revue hebdomadaire et la consigne
   (`evidence/C16/revues/2026-11-09-revue-S46.md`) ; question posée à Elbby sur la preuve corrective de C16.1.
4. **Répétitions** de l'oral blanc des 12-13/11.
5. **En dernier**, décision d'Era : C16.4 (accès du jury, message à Héléna VICENTE) et C20.5 (secret
   `RITA_API_KEY_VIGIE`, la vigie échoue toutes les 3 h faute de lui).

- **En production, vérifié le 07/11 à 19 h 47 UTC** (`evidence/C17/verification-production-2026-11-07-soir/`) :
  PR #228 (`develop` vers `main`, commit `6f428d6`) fusionnée par Era à 19 h 32 UTC ; livraison verte ; `/health` dit le
  commit `6f428d6` ; l'écran Indicateurs servi est la version paginée (`indicateurs.js?v=1cc58c780c`). Le comportement
  des garde-fous sur le site réel n'est pas vérifié (appel authentifié, clé d'Era).
- **S9** (PR #225) : garde-fous d'injection, de fuite, de sortie AMF et d'entrée corrigés par famille, tests d'abord ;
  deux doubles contrôles et cinq revues de sécurité automatiques ; sortie AMF en **liste fermée** (décision d'Era,
  « fail-closed », 4 faits refusés par choix, écrits en test). Mesures : 12 sur 12 sur les trois jeux tenus à l'écart,
  0 faux positif sur ces jeux, 0 sur 230 briefings réels refusé. Preuve : `evidence/C17/s9-2026-11-07/README.md`.
- **C17.7** (PR #226) : Indicateurs montre 20 valeurs à la fois ; mesure locale, mêmes outils que le 06/11, calcul
  corrigé après relecture : **D (52) puis B (76)**. La mesure du 06/11 avait le même défaut de calcul : mêmes notes,
  poids de Briefing et Question sous-estimés, à corriger dans E4 (§ 4.7). Preuve :
  `evidence/C17/mesures-2026-11-07-pagination/README.md`.
- **Revue Claude Code de #226** (Codex à court de quota) : 8 points, tous corrigés tests d'abord (PR #227).
- **C16.1** : bilan élément par élément (`evidence/C16/bilan-c16-1-2026-11-07.md`) : cycles, étapes, rôles prouvés (le
  formateur pour l'accès et la réception seulement) ; outils partiels ; **rituel sans preuve** (aucune revue du lundi
  consignée depuis le 28/09) ; limite de 2 cartes en cours dépassée (3 le 07/11). Décision d'Era : reste à consolider.
- **Tests** : suite complète sur `develop` avec S9, C17.7 et les corrections : 3131 réussis, 82 ignorés, 0 en échec
  (`evidence/C17/mesures-2026-11-07-pagination/pytest-complet-73485f5.txt`).
- **Reste ouvert, hors S9** : le contrôle des nombres (`1<largeur nulle>000`), antérieur à S9, zone sous garde : plan
  écrit à faire, validé par Era.

## ▶️ 07/11, MIDI : CORRECTIONS DU DOUBLE CONTRÔLE FAITES, BANC C7 REFAIT ; E2 v1.5, E3 v2.4, E4 v1.8 POUR UN SECOND REGARD PUIS LES TAGS

**Prochaine action** :
1. Era pousse la branche `banc-c7-2026-11-07`, puis PR vers `develop`.
2. Second regard de l'autre agent : les corrections de son rapport `DOUBLE-CONTROLE-PR-222.md` et le banc.
3. Fusions : #222, puis cette PR, puis `develop` vers `main`.
4. Les tags, un par push : `livrable-E2-v4` (E2 v1.5), `livrable-E3-v5` (E3 v2.4), `livrable-E4-v6` (E4 v1.8),
   `livrable-E5-v4`. Les liens des en-têtes d'E3 et d'E4, qui visent ces tags, sont à vérifier une fois les tags posés.

- **Banc C7 du 07/11** (`evidence/C7/banc-2026-11-07-comparaison/`), demande d'Era (« A + B ») :
  - Azure en zone UE, prompt corrigé : 30 sur 30, 95e centile 2,55 s (10,69 s le 03/10) ;
  - Mistral Large 3, même budget : 30 sur 30, français 1,37 contre 1,10, six fois moins cher, Markdown dans les 30 ;
  - Large 4 : Mistral a retiré le réglage « sans réflexion », plus de texte dans les 500 jetons.
  - Notes de français : notes proposées par une IA à l'aveugle, acceptées par Era sans modification.
  - Appel Mistral ajouté pour le banc seulement ; la cascade l'ignore (`_NOMS_VALIDES`, testé).
- **Corrections du double contrôle de #222** :
  - E2 : règle UE au présent corrigée.
  - E3 : OWASP borné à ce qui est vérifié ; API4 avec les alertes de dépense ; panne en 503.
  - E4 : 9 et 2 en C17, mesures #74, en-têtes au tag de la version.
  - Frein prouvé entre deux visiteurs HTTPS (téléphone en 5G : 403 pendant le blocage du poste).
- **Dépenses** : budget Azure de 10 € par mois, alertes à 50, 90 et 100 %, sans arrêt automatique ; plafond Mistral de
  5 € par mois. Le plafond du script du banc ne protège ni Azure ni Mistral (prix inconnus du script), écrit.
- **Grilles** : E2 20 ✅ · 0 🟡 ; E3 39 ✅ · 0 🟡 ; E4 34 ✅ · 4 🟡 (C16.1, C16.4, C17.7, C17.8) ; E5 : C20.5 en dernier.

## ▶️ 07/11, MATIN : PRODUCTION VÉRIFIÉE ; E2 v1.4, E3 v2.4, E4 v1.8 RENDUES, PRÊTES POUR LE DOUBLE CONTRÔLE PUIS LES TAGS

**Prochaine action** : Era pousse la branche `verifications-production-07-11`, puis PR vers `develop`. Ensuite, le
double contrôle par un autre agent (brief : `Documents\RITA PRO\output\double-controle-2026-11-06.md`). Puis
`develop` vers `main` et les tags, un par push : `livrable-E2-v4` (E2 v1.4), `livrable-E3-v5` (E3 v2.4),
`livrable-E4-v6` (E4 v1.8), `livrable-E5-v4` (E5 v0.9). Porte `tag_cite` verte pour les quatre.

- **Vérifié en production le 07/11** (`evidence/C17/verification-production-2026-11-07/`) :
  - à 2 h UTC : en-têtes et gzip sur les cinq écrans, port 8001 muet, contrat 1.2.0, consigne de l'écran Question ;
  - le matin :
    - #76 : `rita_api` par le code de l'API, `DATABASE_URL` absente ;
    - frein des essais de clé à 08:51 UTC : dix 403 puis 429 ; `X-Forwarded-For` inventé sans effet ; 403 depuis une
      autre adresse pendant le blocage, donc compteur par adresse.
- **Ingestion** relancée par Era le 07/11 (run 42356863532, réussie ; index de 2166 à 2196 articles). Date des
  cotations affichée après l'ingestion : à relire sur l'écran Portefeuille.
- **Grilles** :
  - E2 20 ✅ · 0 🟡 ;
  - E3 39 ✅ · 0 🟡 ;
  - E4 34 ✅ · 4 🟡 : C16.1, C16.4, C17.7 (Indicateurs en D, décision d'Era), C17.8 (S9) ;
  - E5 : C20.5 attend le secret `RITA_API_KEY_VIGIE`, en dernier.
- **Restent ouverts** :
  - l'en-tête `Via` (commande Caddy proposée) ;
  - la règle `ufw` du port 8001, devenue inutile ;
  - aucune collecte planifiée en production ;
  - la capture de la consigne de l'écran Question, preuve visible, pas encore faite ;
  - l'accès du jury au dépôt.

## ▶️ 07/11, 3 H UTC : LIVRÉ EN PRODUCTION (`main` à `a68f2cf`) ; RESTENT DES VÉRIFICATIONS, LES RAPPORTS ET LES TAGS

**Prochaine action** :
1. Era finit les vérifications du site réel : les deux sorties de #76 (`DATABASE_URL` absente, connexions en
   `rita_api`), la capture de l'écran Question avec sa consigne, puis le test du frein des essais de clé (il bloque
   l'adresse du poste 15 minutes).
2. Lancer le workflow « Ingestion » : les données s'arrêtent au 04/11.
3. Rendre les PDF de E2 v1.4, E3 v2.4 et E4 v1.8, puis le double contrôle et les tags, un par push.

- **En production depuis le 07/11, 02:00:39 UTC** (fin du job `deployer` ; image construite à 01:54:37) (PR #221, fusionnée par Era sans le double contrôle par un autre
  agent, décision prise après la revue automatique de Claude, sans problème trouvé ; Codex en échec, limite d'usage) :
  - en-têtes S1 ; compression #74 ; rôle `rita_api` #76 ; S8 ;
  - port de l'API lié à `127.0.0.1` (#218, constat du 07/11 : il répondait en clair depuis Internet) ;
  - contrat 1.2.0 (#219) ;
  - frein des essais de clé S3, option A validée par Era (#220) ;
  - consigne de l'écran Question.
- **Mesuré sur le site réel à 2 h UTC** (`evidence/C17/verification-production-2026-11-07/`) :
  - en-têtes et gzip sur les cinq écrans ;
  - port 8001 muet depuis l'extérieur ;
  - `/openapi.json` en 1.2.0 ;
  - consigne présente.
  Reste `Via: 1.1 Caddy`, ajouté par Caddy (commande proposée à Era, non appliquée).
- **Étape du serveur faite par Era** : rôle `rita_api`, mot de passe tiré sans affichage (le premier s'était affiché
  et a été remplacé), ligne dans le fichier d'environnement ; `docker-compose.yml` final installé dans
  `/root/rita-deploy/bin/`, empreinte vérifiée.
- **Rapports en cours, sur la branche `verifications-production-07-11`, non rendus** :
  - E2 v1.4 : C8.2 ✅, 20 ✅ · 0 🟡 ;
  - E3 : API8 et API9 appliqués, API4 attend le test du frein ;
  - E4 : § 4.6 et § 4.7 à jour.
- **Restent 🟡** :
  - C16.1 : le suivi interrompu après le 14/10 ne se rattrape pas ;
  - C16.4 : message à Héléna VICENTE, en dernier ;
  - C17.5 : attend les sorties de #76 et le frein ;
  - C17.7 : Indicateurs en D, réduire l'écran ou l'assumer, décision d'Era ;
  - C17.8 : S9 attend « ok plan S9 » ;
  - E3 OWASP : attend le frein ;
  - E5 C20.5 : le secret `RITA_API_KEY_VIGIE`, en dernier.
- **Manque découvert** : aucune collecte planifiée en production (`docs/exploitation.md`, note du 27/10) ; sans
  ingestion lancée à la main, les données du jury du 01/12 seraient anciennes. Décision d'Era à prendre.
- **Accès du jury au dépôt** : privé avec invitation, ou public la veille ; audit de l'historique (données
  personnelles, branche `mistral-ue`) avant toute ouverture. Reporté par Era (« not today »).

## ▶️ 07/11, NUIT : NEUF PR FUSIONNÉES DANS `develop` ; RESTENT L'ÉTAPE DU SERVEUR (#76), `main`, LES VÉRIFICATIONS ET LES TAGS

**Prochaine action** : Era fait l'étape du serveur de #76 (rôle `rita_api`, mot de passe, `POSTGRES_PASSWORD_API` dans
le fichier d'environnement du serveur ; `docs/exploitation.md`, « Le rôle de l'API en production ») ; crée le secret
`RITA_API_KEY_VIGIE` dans les réglages du dépôt ; puis `develop` vers `main` (redéploie la production), les vérifications
sur le site réel (en-têtes, compression, `rita_api`, consigne de l'écran Question, cinq écrans), un premier passage de
la vigie, et les tags, un par push : `livrable-E2-v4` (E2 v1.3), `livrable-E3-v5` (E3 v2.3), `livrable-E4-v6`
(E4 v1.7), `livrable-E5-v4` (E5 v0.9).

- **Dans `develop` le 06/11 au soir** : E2 v1.3 et la décision UE (#207, #216) ; E3 v2.3 (#209) ; E4 v1.7 (#211) ; règle
  UE précisée et vérifiée (#214) ; compression #74 (#208) ; en-têtes S1 (#210) ; rôle `rita_api` #76 (#213) ; S8 (#215) ;
  vigie planifiée (#212). Double contrôle par un autre agent : non fait avant ces fusions (la revue automatique de
  Codex a échoué, limite d'usage atteinte).
- **Grilles des rapports** : E2 19 ✅ · 1 🟡 (C8.2, jusqu'au déploiement de la consigne de l'écran Question) ; E3 38 ✅ ·
  1 🟡 (OWASP) ; E4 33 ✅ · 5 🟡 (C16.1, C16.4, C17.5, C17.7, C17.8 : les trois derniers à réévaluer après déploiement) ;
  E5 : C20.5 à réévaluer après le premier passage de la vigie.
- **S9** (garde-fous à 70 et 71,4 %, seuil 85 %) : plan écrit (`docs/PLAN-S9-garde-fous.md`, branche `plan-s9`), attend
  « ok plan S9 ».
- **Classeur des compétences** (v3 du 06/11, 123 ✅ · 14 🟡) : à mettre à jour après les vérifications en production.

## ▶️ 06/11, SOIR : E2 v1.3 PRÊTE POUR `livrable-E2-v4` APRÈS DOUBLE CONTRÔLE ; #74 MESURÉE

**Prochaine action** : Era pousse `e2-v1.3` et `eco-74-compression`, ouvre les deux PR vers `develop` et les fait relire
par un autre agent ; puis `develop` vers `main` (redéploie la production : accord d'Era), et les tags un par push :
`livrable-E4-v6`, `livrable-E5-v4`, `livrable-E2-v4` (E2 v1.3), `livrable-E3-v5` après #204.

- **E2 v1.3** (branche `e2-v1.3`) : retour du formateur du 06/11 appliqué ; briefing d'OR.PA et trace Langfuse du 06/11
  à 20 h 15, même référence `921b261e…`, en annexe A6 ; option B constatée en production (`097b201`). Grille :
  19 ✅ · 1 🟡 (C8.2 : règle UE précisée par Era le 06/11 au soir et vérifiée, PR #214 ; reste la consigne de
  l'écran Question à déployer). E2 v1.2 n'est pas taguée.
- **Carte #74** (branche `eco-74-compression`, `dea68de` puis `33a3f10`) : compression et `favicon.ico`, mesurées avant et
  après sur les cinq écrans (`evidence/C17/mesures-2026-11-06/README.md`) : poids d'une première visite divisé par 2,2
  à 3,3 ; note EcoIndex presque inchangée, Indicateurs reste D (décision D6 ouverte). Non déployée.
- **E4 v1.7** (branche `e4-v1.7`, `9594adc`) : réévaluation C15 des prestataires écrite ; le § 4.7 et C17.7 attendent la
  fusion de #74 et un tag où les preuves existent (les liens d'E4 visent `livrable-E4-v5`).
- **#73** : le correctif est en production ; reste le test d'Era (fausse clé puis F5, vraie clé puis F5).
- **PR ouvertes** : #204 (E3 v2.2), #205 (attente du rechargement dans les tests d'interface).

## ▶️ 06/11, MIDI : E2 v1.2, E4 v1.6 ET E5 v0.9 POUR `livrable-E2-v4`, `livrable-E4-v6` ET `livrable-E5-v4`, APRÈS DOUBLE CONTRÔLE

**Prochaine action** : fusionner `rapports-style-bleu` dans `develop` puis dans `main`, et poser `livrable-E2-v4`,
`livrable-E4-v6` puis `livrable-E5-v4`, un tag par push ; ensuite les répétitions (E1, puis E3 et E4, puis E2 et E5).

- **E2 v1.2** (06/11) : trois précisions demandées par la relecture d'un autre agent. « En une minute » : aucun
  fournisseur de secours n'est activé pour le briefing dans la version présentée. § 4.2 : test présent, journal non
  conservé, ce qui règle le manque du 05/11 (CHANGELOG). C8.4 : les sujets couverts (cinq, et non quatre). Aucun
  résultat, statut ni montant changé ; double contrôle favorable le 06/11 ; 20 pages avec l'annexe, 17 sans.
- **E4 v1.6** (06/11) : une date précisée au § 2.7 (« Au 02/11, la production n'était vérifiée que par la page
  servie »), qui ne contredit plus le § 6.5 du 04/11. Double contrôle du 06/11 : une correction demandée, appliquée.
  34 pages, 115 liens, 16 renvois et 68 signets inchangés ; aucun statut changé. L'annexe annonce aussi la version 1.6
  (relecture du 06/11).
- **E3 v2.2** (06/11) : après double contrôle, les statuts de #73 (corrigé le 01/11, déployé le 02/11, vérification
  manuelle à faire) et de #152 (intégré à `main` le 02/11, passerelle hors de l'image) et les sept contrôles de fusion
  (dont `base`, depuis le 01/11) sont harmonisés, comme dans la copie relue du 04/11 ; titres au même style ; 20 pages,
  106 liens, 47 signets ; aucun statut changé. Tag prévu : `livrable-E3-v5`.
- **E5 v0.9** (06/11) : mise en forme seule, les titres au même style ; texte, 5 pages, 29 liens et 11 signets
  inchangés. Double contrôle demandé le 06/11.
- **Le style des titres** (`scripts/rendre_pdf.py`, testé par `tests/test_rendre_pdf_titres.py`) : titres noirs sur
  bandeau #BFD7F2, sous-titres bleus sur #D6E6F7, bande bleu marine à gauche, sans filet ; rendu depuis la source, pas
  par retouche du PDF. E1, E3 et E5 le prendront à leur prochain rendu, sur demande d'Era seulement.
- **Règle d'Era du 06/11** : avant tout tag, et avant un push ou une fusion qui le demande, un double contrôle par un
  autre agent.
- **Les versions remises restent** sous `livrable-E2-v3`, `livrable-E4-v5` et `livrable-E5-v3`.

## ▶️ 06/11 : CLÉ PAR CLIENT REPORTÉE APRÈS L'ORAL BLANC ; PRÉPARATION À FINIR LE 07/11, PUIS RÉPÉTITIONS

**Prochaine action, le 07/11** : 1) les répétitions, sans attendre le reste : E1, puis E3 et E4 avec leurs
démonstrations, puis E2 et E5 ; 2) rafraîchissement des données : **C décidé le 06/11 jusqu'à l'oral blanc** (aucune écriture
en production ; la démonstration montre les cours du 04/11 avec le signal « attention », dit comme une limite) ; A (le
transfert vérifié comme étape de `pipelines/ingest.py`) réévalué le 14/11 avec la clé par client ; 3) fusionner la PR
#201 vers `develop` (verte le 06/11, sans déploiement). Oral blanc les 12 et 13/11.

- **Rafraîchissement des données, sur copie** (en parallèle des répétitions, rien en production) : conception v2 après
  la revue du 06/11, hors dépôt ; partie calcul codée sur la branche `rafraichissement-sur-copie` (commit `879bf9a`, non
  poussée) : calendrier Euronext 2026 officiel, dernière séance close, complétude exacte par valeur, taux BCE ; 18 tests
  verts, sortie rouge gardée. Premier lot : Euronext (105 valeurs) et taux BCE ; Londres et les États-Unis hors du lot.
  Les trois réserves du 04/11 **restent à lever** : tests en base, transfert gardé et répétition sur copie à faire
  (environ 3 h 45 estimées), après le choix d'Era. Le script du 04/11 n'est pas relancé.

- **Clé par client** (décision d'Era du 06/11) : implémentation **reportée après l'oral blanc, réévaluée le 14/11**. La
  spécification 002 est validée (05/11) et son plan relu deux fois (v2 du 06/11) : 32,5 h, environ 4 journées et
  1 700 € HT, contre 1 à 2 journées estimées le 03/11 (`docs/BUDGET.md`, mise à jour datée). D'ici là, la clé partagée
  est présentée honnêtement comme une limite, avec sa solution (`specs/002-cle-par-client/`) et son estimation. Rapports
  figés inchangés ; présentateur et réponse orale mis à jour hors du dépôt.
- **Fusion de cette branche** : vers `develop` seulement. `livraison.yml` ne déploie que sur un push de `main` (lignes
  332 et 351) ; ces changements de documentation attendent le prochain lot `develop` vers `main`.
- **Toujours séparé** : la collecte planifiée sur le serveur ; les astérisques de Briefing et la colonne figée des
  Indicateurs ; le message à Héléna VICENTE sur l'accès du jury au dépôt ; les classeurs, à confirmer par Era.

## ▶️ 05/11, 22 H : INTERFACE CORRIGÉE EN PRODUCTION (`ed12b7e`) ; ORAL PRÊT POUR LA RÉPÉTITION (HORS DU DÉPÔT)

**Prochaine action** : la répétition complète d'Era sur deux écrans, gestes compris, en partageant la fenêtre du jury en
visio ; mesurer les durées réelles de chaque diapositive, surtout E5 D1 et D4. Les cibles seront ajustées sur ces mesures.
L'oral blanc 2 a lieu les 12 et 13/11.

- **Corrections d'interface** (l'aide du Briefing, le message du 502, le libellé du RSI) : fusionnées (#198 vers
  `develop`, #199 vers `main`) ; exécution de `main` 42082710238 verte ; production à `ed12b7e` (`/health` relu le 05/11,
  image construite à 18 h 21 UTC).
- **Tags du soir livrés** : `livrable-E4-v5` et `livrable-E5-v3`, posés sur `e9d5527` ; livraison verte pour chacun
  (42023759120 et 42023773728).
- **Préparation de l'oral, hors du dépôt** (présentateur du poste d'Era, règle « oral personnel ») : fiches et notes
  d'E1 à E5 alignées sur les versions taguées et vérifiées dans le présentateur ; E3 avec ses deux vidéos, jouées dans
  l'écran du jury ; E4 par le parcours au clic de 20 étapes préparé par Era (zooms prédéfinis, une prise réelle au
  clavier), puis un court passage en direct, la vidéo E4 restant en secours ; E2 et E5 validés pour la répétition. Durées
  estimées, à mesurer : E2 13 min 15, E5 9 min 15.
- **Manque découvert** : le rapport E2 v1.1 (§ 4.2, tag `livrable-E2-v3`) écrit que le test de l'ordre des fournisseurs
  a été « écrit d'abord et vu en échec » (`d1cbb7b`) ; le dépôt ne conserve pas le journal de cet échec. Le rapport,
  figé, n'est pas modifié ; à l'oral, la phrase dit que le journal n'est pas conservé, sans conclure que l'essai n'a pas
  eu lieu. Entrée au `CHANGELOG`.
- **Restent** : le message à Héléna VICENTE sur l'accès du jury au dépôt, envoyé par Era ; les classeurs des compétences
  (E2 v1.1, E4 v1.5, E5 v0.8), à confirmer par Era, non vus dans cette session ; dans le présentateur, les notes d'E4 · 3
  encore rédigées pour la vidéo (les phrases du parcours au clic sont dans le plan du kit) ; à part, test d'abord : les
  astérisques du modèle dans Briefing et la colonne figée des Indicateurs. Toujours séparé : la collecte planifiée.

## ▶️ 05/11, SOIR : E4 v1.5 POUR `livrable-E4-v5` ET E5 v0.8 POUR `livrable-E5-v3`, UNE SEULE FUSION DANS `main`

**Prochaine action** : #195 (limite d'E1) puis la PR `revision-E5-v0.8` dans `develop`, puis `develop` vers `main` ;
les tags `livrable-E4-v5` et `livrable-E5-v3` se posent sur ce même commit de fusion, **un par push**, après les
exécutions vertes de `main`. Puis les deux classeurs une seule fois (E2 v1.1, E4 v1.5, E5 v0.8).

- **E5 v0.8** : chaque fait daté de la v0.7 revérifié le 05/11 ; mis à jour : réception confirmée par le formateur le
  04/11 (C20.7), tableau de bord en production vérifié le 05/11 (HTTP 200), #77 et #132 encore ouvertes au 05/11, dernière
  exécution du workflow d'alerte toujours au 24/10. Inchangé et toujours vrai : seuils, vigie à la main, neuf incidents,
  actualisation à 30 s et suspension. 5 pages, langue fr, balisé ; 36 liens externes aux mêmes cibles, vers
  `livrable-E5-v3`. Aucun statut changé ; `livrable-E5-v1` et `livrable-E5-v2` restent.

## ▶️ 05/11, FIN D'APRÈS-MIDI : `livrable-E2-v3` POSÉ ET VÉRIFIÉ ; E4 v1.5 (EXPORT ACCESSIBLE) POUR `livrable-E4-v5`

**Prochaine action** : la PR `export-accessible-E4` vers `develop`, puis `develop` vers `main` ; le tag `livrable-E4-v5`
se pose sur le commit de fusion qui porte cette entrée, seul dans son push, **après** les exécutions vertes de `main`.
Ensuite E1, puis les deux classeurs une seule fois (E2 v1.1, E4 v1.5, E1). Le remplacement d'E2 et d'E4 auprès du
formateur se demande avant tout envoi (message prêt pour E2).

- **`livrable-E2-v3`** : sur `9d2f0cc` (fusion de #193) ; Tests 42009541097 verts ; livraison du tag 42009958869 verte
  (1 981 tests, 16 portes des garde-fous, liens internes, tag cité), image `rita-api:livrable-E2-v3` publiée ; production
  à `9d2f0cc` (`/health`). Le tag a été poussé à 10 h 21 UTC, trois minutes avant la fin des tests de `main` (verts
  ensuite) : écart de procédure, sans effet. Copies v1.1 avec et sans annexe dans le dossier de remise et sur OneDrive,
  identiques au tag (`b99d4d1a…`, `2f573de4…`) ; la v1.0 rangée dans `remplaces-par-E2-v1.1\`.
- **E4 v1.5** : PDF avec annexe en un seul document (34 pages, 20 en portrait et 14 en paysage, langue fr, arbre de
  structure, pieds de 1 à 34). Comparé à la v1.4 : texte identique hors les deux lignes de version et une phrase de
  l'historique ; 237 liens externes, mêmes cibles, passés de `livrable-E4-v4` à `livrable-E4-v5` ; 16 liens internes et
  68 signets ; images identiques. Un test tient désormais les pages annoncées par l'annexe (A1 p. 22 à A7 p. 31 à 34).
  Aucun statut changé. `livrable-E4-v1` à `livrable-E4-v4` restent, figés ; la v1.4 envoyée le 05/11 reste valable.
- **E1 reste tel quel** (décision d'Era du 05/11) : le livret de 5 pages (`rapport-E1.pdf`) est en français et balisé ;
  le PDF avec annexes de 10 pages ne l'est pas, sa couverture et ses quatre annexes étant des pages mises en forme hors
  du dépôt (copie OneDrive d'Era du 28/10), assemblées après coup ; sans source HTML, Chrome ne peut pas les rendre en un
  seul document. Limite écrite dans le README ; pas de nouveau tag pour E1.

**Prochaine action** : la PR `export-accessible-E2` vers `develop`, puis `develop` vers `main` ; le tag `livrable-E2-v3`
se pose sur le commit de fusion qui porte cette entrée, seul dans son push, après les exécutions vertes de `main`. Ensuite,
même méthode pour E4 (v1.5, futur `livrable-E4-v5`), puis E1. Avant d'envoyer E2 v1.1 au formateur : lui demander s'il
accepte ce remplacement après la remise (seuls l'export et deux faits datés du 04/11 changent).

- **Remise du 05/11** (déclaration d'Era) : E1, E2, E4 et la grille des compétences déposés sur le Drive et transmis au
  formateur sur Discord ; **E3 et E5 : envoi à confirmer**. Dossier de remise : E1 v6, E2 v1.0, E3 v2.1, E4 v1.4, E5 v0.7.
- **`livrable-E4-v4`** : posé par Era sur `70a19cd` ; livraison 41995548699 verte (1 975 tests, 16 portes des garde-fous,
  liens internes, tag cité), image `rita-api:livrable-E4-v4` publiée ; les 113 adresses du PDF vers le tag répondent ;
  copies v1.4 avec et sans annexe dans le dossier de remise et sur OneDrive, identiques au tag (`a07768be…`,
  `55b30869…`) ; la copie v1.3 est rangée dans `remplaces-par-E4-v1.4\`.
- **Accessibilité des PDF** (mesure du 05/11) : chaque rapport seul est en français et balisé ; les PDF fusionnés d'E1, E2
  et E4 ne l'étaient pas, la fusion pypdf perdant l'arbre de structure. `scripts/rendre_pdf.py --annexe` rend le rapport
  et l'annexe dans un seul document Chrome (10 tests écrits d'abord). Ce balisage ne vaut pas un audit d'accessibilité.
- **E2 v1.1** : PDF avec annexe en un seul document (20 pages, langue fr, arbre de structure, pieds de 1 à 20 ; texte des
  20 pages comparé à la v1.0) ; six passages du rapport et la légende d'A1 mis à jour avec leur preuve, après une relecture extérieure (réception confirmée par le formateur le 04/11 ;
  503 `AUCUN_FOURNISSEUR` corrigé le 04/11), ligne de version et historique ; aucun statut changé. `livrable-E2-v1` et
  `livrable-E2-v2` restent, figés.
- **Restent** : les deux classeurs citent E2 v1.0 (à mettre à jour après le tag) ; message à Héléna VICENTE pour l'accès
  GitHub du jury ; préparation de l'oral ; la ligne E4 du README était restée à la v1.2, corrigée dans cette PR.

## ▶️ 05/11, NUIT : `livrable-E4-v3` POSÉ ; LE 05/11, ERA ENVOIE LA REMISE DES CINQ LIVRABLES

**Prochaine action, le 05/11, dans l'ordre choisi par Era** : 1. relire E2 et E5 (ce qui a vieilli depuis le 03/11) ;
2. envoyer la remise des cinq livrables (obligatoire) ; 3. préparer la présentation de l'oral (tout revérifier, puis
créer le support). E4 : un seul PDF de 34 pages,
`Downloads\Remise-RITA-2026-11-02\rapport-E4-avec-annexe-2026-11-04-v1.3.pdf` (SHA-256 `790e67b1…`, identique au tag) ;
phrase prête : « Comme convenu, je te transmets le rapport E4 et ses annexes dans un seul PDF de 34 pages : 20 pages de
rapport et 14 pages d'annexes. » L'accès GitHub du jury reste à voir avec Héléna VICENTE (message prêt).

- **E4 v1.4 (05/11, matin)**, pour le tag `livrable-E4-v4` : quatre corrections de cohérence (tableau de `test.yml`,
  C16.4, S6 corrigé le 04/11, accès du jury) et langue française déclarée dans le PDF complet ; c'est cette version que
  la remise envoie, une fois le tag posé et vérifié.
- **Tag** : `livrable-E4-v3` posé par Era sur `07da897` (fusion de #188), seul dans son push ; `main` en production à
  `07da897` ; les 112 adresses du PDF vers le tag répondent ; copies datées avec et sans annexes dans le dossier de remise et
  sur OneDrive, identiques au tag ; les copies v1.2 rangées dans `remplaces-par-E4-v1.3\`.
- **Avant l'oral blanc des 12 et 13/11** (code, test d'abord, chacun à part) : l'aide du Briefing qui promet trop, les
  astérisques du modèle affichés, la colonne du code figée dans la carte des Indicateurs ; le mot « zone neutre » à
  trancher par Era ; tâches 10 et 11 de la refonte ; traduction anglaise d'E4 v1.3 pour OneDrive.
- **Toujours séparé** : la collecte planifiée sur le serveur, et le renforcement du script de rattrapage avant toute
  réutilisation (preuve C3, § 9.1).

## ▶️ 05/11, NUIT : TROIS CORRECTIONS D'INTERFACE AVANT LE TOURNAGE E4 (FUSIONNÉES PAR #198 ET #199, EN PRODUCTION : VOIR PLUS HAUT)

- **Faites, test d'abord** : l'aide du Briefing ne promet plus « jamais diffusée » (elle dit ce que le garde-fou détecte) ; le 502 a son propre message, « Données indisponibles », distinct du 422 « Valeur introuvable » ; le RSI s'écrit « RSI 14 : 41. Repères : 30 et 70. » (spécification 001, R2, changée le 05/11 : la question du « zone neutre » est tranchée par Era dans la PR). Restent à part : les astérisques du modèle affichés, la colonne du code figée dans Indicateurs.
- **Ensuite** : PR vers `develop` puis `main`, déploiement, puis les captures de la vidéo E4 sur la version vérifiée.

## ▶️ 04/11, NUIT : E4 v1.3 PRÊT À RELIRE (PR #185, BROUILLON) ; DEUX DÉFAUTS DE L'ÉCRAN BRIEFING TROUVÉS EN PRODUCTION

**Prochaine action** : #185 et #186 fusionnées par Era (`main` à `6f8474b`, PDF `790e67b1…`) ; l'entrée du CHANGELOG qui
cite le tag passe par `develop` puis `main`, et le tag `livrable-E4-v3` se pose sur ce commit de fusion, seul dans son push ;
ensuite les copies OneDrive et le dossier de remise (avec et sans annexes). C17.3 reste ✅ (preuve : 19 tests au clavier
et 8 cas d'erreur verts en CI sur `8ecc5a7`) ; C17.2 reste « à consolider ».

- **Annexe relue en entier**, texte des images compris : légendes datées du 04/11 (A2 historiques, `autocomplete`,
  garde-fou, 503 ; A4 périmètre du workflow ; A5 contrôle `base` ; A6 commit `12cc00c`), images non retouchées.
- **A7 nouvelle** : maquettes de la refonte et écrans livrés, comparés élément par élément sur des captures de production
  d'Era (`evidence/C17/refonte-ecrans-livres-2026-11-04/`, sept captures, tous les éléments des maquettes compris).
  Question pour Era : « zone neutre de 30 à 70 » (spécification 001, R2) suggère-t-il que les autres zones sont des signaux ?
- **Défauts trouvés sur l'écran Briefing livré** : l'aide promet « retenue, jamais diffusée » (`frontend/briefing.html`,
  ligne 57) ; les astérisques de mise en forme du modèle s'affichent. À corriger à part, test d'abord, avant l'oral blanc.
- **Sigle** : le MCD garde son intitulé historique (« Trading Assistant ») ; la légende d'A1 donne le nom de
  l'application livrée, « pour le Tracking et l'Analyse ». Le livret E1, déjà tagué, n'est pas modifié.
- **Réception confirmée** : Elbby a reçu l'envoi du 03/11 et ouvre tous ses liens (`evidence/C8/reponse-formateur-2026-11-04.md`).
- **Une seule numérotation** : le PDF complet est numéroté de 1 à 34 en pied de page, et l'annexe renvoie aux pages du PDF
  complet (A1 p. 22 à A7 p. 31 à 34). Assemblage : `scripts/assembler_pdf_avec_annexe.py` et son test (05/11) ; il garde
  les 16 liens internes et les 68 signets, qu'une première version, hors dépôt, avait perdus (relecture extérieure).
- Aucun statut de critère changé.

## ▶️ 04/11, 22 H 35 : RATTRAPAGE DES COURS FAIT ET VÉRIFIÉ EN PRODUCTION ; LE 05/11 : REMISE DES CINQ LIVRABLES, OBLIGATOIRE

**Prochaine action** : la PR des preuves #184 est fusionnée par Era dans `develop` (`a4a6703`). Le 05/11, **la remise des
cinq livrables (E1 à E5) est due : elle n'est pas facultative.** Seules les améliorations le sont, dans cet ordre :
révision courte et datée d'E4 (document v1.3, futur tag `livrable-E4-v3`, préparée sur la branche
`revision-E4-et-formulations`), puis E2, puis E5. Une amélioration qui n'est pas taguée à temps ne retarde pas la remise :
on envoie alors la version taguée existante (E4 v1.2, `livrable-E4-v2`).

- **Opération C** (accords d'Era : préparation reçue à 21 h 59, C2 à 22 h 08, heure de Paris) : R1, C1 à blanc, répétition
  sur une copie de R1, cinq scénarios d'échec essayés, C2 réussi sous verrou (22 h 17 à 22 h 19), R2. R1 contre R2 :
  0 différence hors `cotation` et `taux_change`. 281 166 cotations, dernière séance le 04/11, cinq devises au 04/11 ; total
  recalculé 21 935,75 €, VIRIDIEN -48,73 %. Preuve : `evidence/C3/preuve-correction-viridien-production-2026-11-04.md`, § 9.
- **C4 fait par Era avec sa clé** : Portefeuille et Indicateurs au 04/11 (captures 5 et 6). CRI.PA reste au 03/11 (Yahoo
  n'a pas le 04/11), c'est attendu. Le contrôle MCP n'a pas été refait après C2.
- **Script C2 pas réutilisable en l'état** (relecture du 04/11) : complétude sans contrôle des dates exactes, erreurs
  techniques mal propagées, retour arrière sur toute une plage de dates. À corriger, essai à l'appui, avant toute
  réutilisation ou automatisation (§ 9.1).
- **Collecte automatique : tâche séparée, non décidée.** Sans elle, les cours vieillissent de nouveau dès le 05/11 au soir.
- **Remise** (réponse écrite d'Elbby, 04/11 à 16 h 13, Héléna VICENTE en copie) : les trois PDF du 03/11 sont reçus et tous
  les liens s'ouvrent ; **un PDF par rapport, annexes comprises, c'est accepté**. Accès du jury au dépôt : à voir avec Héléna
  VICENTE ; message à écrire par Era.
- Restent aussi : worktrees de la soirée à nettoyer ; journal du 03/11 ; tâches 10 et 11 de la refonte avant l'oral blanc
  des 12 et 13/11.

## ▶️ 04/11, 21 H 35 : A ET B FAITS EN PRODUCTION ; CONTRÔLES D'ERA AVEC SA CLÉ ATTENDUS

**Prochaine action** : Era vérifie avec sa clé l'écran Portefeuille et l'écran Indicateurs de la production (total
20 835,20 €, VIRIDIEN 1 × 185,00, -48,03 %, poids 0,46 %, deux graphiques lisibles) et lance le contrôle MCP ; puis
l'actualisation des cours, décision séparée (aucune planification installée). Preuve :
`evidence/C3/preuve-correction-viridien-production-2026-11-04.md`, § 7.

- **Interface déployée (A)** : `8ecc5a7` (fusion de #180), arbre identique à l'arbre relu, image
  `rita-api@sha256:9f6f5654…` ; fichiers réellement servis : 63 contrôles réussis, 0 échec.
- **Données corrigées (B)** : B1 à blanc puis B2 ; S2 comparée à S1 : exactement 4 cellules ; total recalculé avec les cours
  de production : 20 835,20 € sur 7 lignes.
- **Collecte non actualisée** : dernière cotation de production le 27/10 ; bandeau de fraîcheur toujours rouge.
- Retour arrière possible sans perte : bloc `DO` gardé (valeur d'origine relue dans S1), S1 et S2 sur deux disques pour S1.

Avant : production à `2310f87`, ancienne interface, Viridien à 120 × 1,85, total 32 277,05 €.

- **S1 faite** (accord d'Era) : sauvegarde en lecture seule, compte `rita_lecture` et ses droits vérifiés sur le serveur
  sans rien modifier, 5 591 673 octets ; copies sur le disque USB (D:) et le disque interne (C:), même empreinte, hors Git.
  Restauration complète recoupée (32 277,05 €, 280 518 cotations, 2 166 articles) ; répétition : 4 cellules exactement,
  total 20 835,20 €, rejeu refusé, retour arrière exact. Preuve : `evidence/C3/preuve-correction-viridien-production-2026-11-04.md`, § 4.
- **PR #179** (`refonte-interface` vers `develop`, ne déploie rien) : travail `secrets` rouge sur un faux positif (clé
  périmée simulée d'un test), ajoutée aux exceptions exactes de gitleaks, test d'abord ; gitleaks sur tout l'historique :
  aucune fuite. Cette exception est à valider par Era avec A.
- **Défaut antérieur trouvé** (#152, 01/11, déjà en production) : la passerelle MCP refuse `rita_portefeuille` sur une vraie
  API, car l'API sert les nombres comme des textes ; correction à décider par Era (hors image, test d'abord).
- **Fraîcheur** (lecture L3 du serveur faite, accord d'Era, corrigée) : au 04/11, aucune planification de collecte trouvée
  sur le serveur ; sur la période couverte par ses journaux (depuis le 14/10), les cours n'y sont arrivés qu'une fois, par le
  rattrapage à la main du 27/10 ; la tâche planifiée du soir écrit dans la base du poste. Aucune collecte lancée.
- **Correctifs avant la livraison** (accords d'Era) : passerelle MCP, PR #181 fusionnée par Era dans `develop` (19 h 19 UTC) ;
  mode simulation au retour par Précédent ou Suivant (un appel réel partait sous une session en simulation), PR #182,
  reproduit puis corrigé, test d'abord. Ensuite : CI et revue de #180 sur son contenu final, fusion vers `main` par Era.

## ▶️ 04/11, SOIR : REFONTE, TÂCHES 0 À 9 FAITES SUR `refonte-interface` ; VIRIDIEN CORRIGÉ DANS LA BASE LOCALE (RÉIMPORT FAIT À 17 H 33) ; INTERFACE VERSIONNÉE ; REMISE TOUJOURS À ENVOYER PAR ERA

**Prochaine action (refonte)** : Era commite et pousse (tâche 9, Viridien, corrections d'Indicateurs, versionnement ;
suite complète : 2 168 réussis, 57 sautés, 2 xfailed, deux fois, la seconde avec Azure injoignable) ; Era recharge la page
Portefeuille et regarde Viridien (attendu : VIRIDIEN, -50,43 %, total 21 409,85 €), redémarre le serveur du port 8000 ;
puis 10 (simulation avec les données d'exemple), 11 (mesure « après », comparaison aux
maquettes, preuve datée), 12 (production par une PR ; vérifier que le serveur répond `Cache-Control: no-cache`).
**Toujours en attente d'Era** : l'envoi de la remise avant le 05/11 (section du 03/11 ci-dessous), puis « envoyé ».

**Défaut vu par Era sur Indicateurs puis Portefeuille le 04/11 : titres décalés d'une colonne (11 titres, 15 cases ;
8 titres, 7 cases), cause mesurée.** Le serveur local du port 8000 (processus lancé à 11 h 54) tournait depuis avant
l'ajout de `Cache-Control: no-cache` (commit `4c79f0f`, 12 h 56) : il n'envoyait aucune consigne de cache, et Chrome gardait
l'ancien script des jours (péremption heuristique) avec la page neuve. Le serveur du port 8010 envoie `no-cache` ; les
deux servaient des fichiers identiques à ceux du disque. Corrections : `scripts/versionner_interface.py` écrit dans chaque
page la version du contenu de chaque script et feuille de style (forme `indicateurs.js?v=<empreinte>`) ;
`tests/test_interface_versionnee.py` échoue si on oublie de le relancer ; `tests/test_mise_a_jour_cache_ui.py` ouvre
l'ancienne version, livre la nouvelle, recharge normalement (sans Ctrl+F5) sur les cinq écrans ; rouge avant, vert après,
avec un cas de contrôle qui reproduit le défaut sans version. **À faire par Era : redémarrer le serveur du port 8000
(ou utiliser le 8010) ; le processus de 11 h 54 ne sera jamais à jour tout seul.**
Indicateurs, même soir : « Volatilité annualisée (20 séances) » (la fenêtre réelle de `db/indicateurs_risque.sql`, plus
« (1 an) »), devise après le cours et les capitaux échangés, texte des cotations anciennes sans « probablement radiée »,
pied de page « calculés par RITA à partir des cotations collectées » (le RSI est calculé en Python), une colonne sur deux
teintée, liste de toutes les valeurs dans la zone de recherche (demande d'Era), titre long de la volatilité sur deux lignes.
Relecture extérieure de la fin de soirée, traitée ensuite : le détail d'une valeur se ferme quand une recherche l'écarte et
un message dit « Aucune valeur trouvée » (ou qu'une périmée masquée correspond) ; les cotations périmées sont **masquées par
défaut** (une case les montre) ; le tableau défile dans sa zone, titres fixes, barre horizontale visible ; l'aide dit ce que
fait l'écran. **Viridien en grand dans les graphiques** : tant que la base n'est pas réimportée, l'écran montre ce que la
base contient. Deux gardes ajoutés pour que la leçon serve : l'écran Portefeuille signale en texte, avant les dessins, une
performance de +900 % ou plus, ou de -90 % ou moins, comme une chose à vérifier (convention déclarée, rien n'est caché ni
plafonné) ; l'importateur signale à chaque import un prix de revient hors de 0,2 à 5 fois le dernier cours à ou avant
la date d'achat (`controler_prix_de_revient`, affiché dans le bilan avec la date du cours lu ; deux devises différentes
ne sont pas comparées et le bilan le dit). Relecture extérieure suivante, adoptée : **un ancien CSV réimporté après la
correction** fermait la ligne corrigée (une vente inventée, constaté sur la base de test) et réinsérait la mauvaise ; les
lignes du fichier qui portent exactement la ligne d'avant sont maintenant converties au passage, avec un avertissement et
un compteur `converties` (`convertir_lignes_d_avant_regroupement`). À dire pour Viridien : « Positions ouvertes simulées,
hors espèces et sans l'indemnisation des rompus » (37 € est le coût d'achat des 20 rompus, pas leur indemnisation). Non fait, dit : un zoom explicite sur les autres valeurs (utile
seulement pour une valeur extrême juste) et les anciens libellés du courtier (« CGG ») comme alias de recherche, qui
demanderait un changement de l'API.

**Ligne Viridien de `data/positions-exemple.csv` : fausse, vérifiée le 04/11 ; corrigée et testée le même soir, sur le
principe validé par Era (`CONTINUITE.md`, section F ; preuve `evidence/C3/preuve-correction-viridien-2026-11-04.md`).
Réimport de la base locale fait le 04/11 à 17 h 33 (`--positions-seulement`, sauvegarde, répétition, revue indépendante,
neuf cellules changées sur la base, voir la preuve § 6), vérifié par Era sur l'écran local. **Production** : lue en lecture
seule le 04/11 au soir, Viridien y est encore faux (id 14, cours arrêtés au 27/10) ; plan `docs/PLAN-VIRIDIEN-PRODUCTION.md`
(mode `--corrections-seulement`, portes `--a-blanc` et `--attendu-*`, sauvegarde et retour arrière testés sur copies),
**à valider par Era ; aucune écriture en production.**
Era l'a vue en tête de l'écran Indicateurs : `VIRI.PA` à +4 856,76 % et 34,04 % du portefeuille. Le défaut était connu
(`evidence/C2/preuve-requetes-sql.md`, août ; ce fichier, 09/09 : « à corriger dans le CSV, pas dans le code ») et
jamais corrigé. Trois erreurs sur la même ligne :
- le prix de revient (1,85 €) est à l'échelle d'avant le regroupement de 100 actions anciennes pour 1 nouvelle,
  effectif le 31/07/2024 (avis Viridien du 27/06 et du 31/07/2024, copies DILA de l'AMF), alors que les cours de la
  base sont rétro-ajustés : PRU / cours du jour d'achat = 0,029, contre 0,78 à 1,51 pour les six autres lignes mesurées ;
- l'ISIN `FR0013506730` est celui de Vallourec ; celui de Viridien est `FR001400PVN6` depuis le 31/07/2024 ;
- le nom affiché est « CGG BS », le premier libellé de l'univers pour ce ticker (`db/importer.py`, `charger_univers`).
Correction : la ligne devient `Viridien;FR001400PVN6;VIRI.PA;1;185,00;EUR;2021-10-14` (120 anciennes = 1 nouvelle ;
les 20 rompus ne sont pas reconstitués, position simulée) ; `db/importer.py` la corrige sur place avant la
réconciliation, pour ne pas fabriquer une vente (`REGROUPEMENTS`), et affiche `VIRIDIEN` ; le verrou de démonstration
suit (`passerelle_mcp/jeu_demo_attendu.csv`). 11 tests écrits avant, dont 4 sur une base jetable (job `base`).
La table `operation_sur_titre` reste le vrai correctif durable : hors calendrier avant l'oral blanc, limite à dire.

- Branche `refonte-interface`, partie de `develop` à `e75df92` (spécification et plan validés), poussée jusqu'à `62186d9`.
  Aucune CI sur cette branche : les workflows ne tournent que sur `main`, `develop` et les PR. Une PR brouillon vers
  `develop` a été proposée à Era, pas ouverte.
- Fait test d'abord, suite complète lancée deux fois (normale, puis Azure injoignable sur `127.0.0.1:9`, pour prouver
  qu'aucun test n'appelle le vrai modèle) : **2 101 réussis, 48 sautés, 2 xfailed**, le 04/11.
  - Tâche 0 : mesure « avant » (`evidence/C17/mesures-2026-11-04-avant/`) : accessibilité 100 sur les vingt étapes,
    mêmes scores que le 03/10 ; Chrome 156 au lieu de 154.
  - Tâches 1 à 3 : l'API dit qui a rédigé (`diagnostic` : fournisseur, modèle renvoyé, tentatives, date du cours lue en
    base, séances Euronext, sources) et répond 503 `AUCUN_FOURNISSEUR`.
  - Tâche 4 : en-tête identique dans les cinq pages. Décision d'Era du 04/11 : style B sombre par défaut, clair au
    choix ; polices déjà installées ; logo ; fond en dégradé CSS (`CONTINUITE.md`, section F).
  - Tâche 5 : `commun.js` et mode simulation (bouton de l'en-tête ; les cinq écrans suspendus en simulation jusqu'à la
    tâche 10) ; l'interface est servie en `Cache-Control: no-cache` (un ancien script restait en cache).
  - Tâche 6 : `graphiques.js` ; `/donnees/cotations` rend `cloture` en texte décimal, lu par `lireNombre`.
  - Tâche 7 : écran Briefing en flux vertical, et un parcours de test à travers la vraie API.
  - Tâche 8 : écran Indicateurs ; une clé refusée n'est plus jamais regardée par un appel parallèle réussi.
  - Tâche 9 (à commiter) : écran Portefeuille ; chiffres clés, anneau des poids (aucun anneau si la valorisation est
    incomplète), barres de gain ou de perte, date du cours sur chaque ligne ; 7 tests écrits avant ; 2 108 réussis.
- Le 04/11, panne GitHub de 09 h 45 à 11 h 32 UTC (Git Operations) : quatre pushes refusés, rien de perdu.
- Calendrier : les tâches 0 à 9 sont faites le 04/11, quand le plan les plaçait jusqu'au 08/11.

---

## ▶️ 03/11, NUIT : LES CINQ LIVRABLES TAGUÉS (E1-v6, E2-v2, E3-v4, E4-v2, E5-v2) ; REMISE À ENVOYER PAR ERA

**Prochaine action** : Era envoie la remise au formateur avant le 05/11 (message prêt ; les cinq fichiers du haut de
`Downloads\Remise-RITA-2026-11-02\`, identiques aux tags), puis dit « envoyé » pour la preuve datée.

- **Décision d'Era du 04/11** : la refonte de l'interface (`docs/conception/frontend/refonte-2026-10.md`, maquettes du
  04/10) devient la démonstration de l'oral blanc des 12-13/11. Après la remise : spécification remise à jour (cinq écrans,
  bloc `diagnostic` absent de l'API aujourd'hui, 503 au lieu du 500 actuel de `/briefing`, #73 déjà livré), plan, puis
  construction test d'abord ; version identifiée ; ajustée après les retours. Précisions d'Era : les trois écrans (Briefing,
  Indicateurs, Portefeuille), Question et Tableau de bord inchangés avec le nouvel en-tête, démonstration en production,
  mode simulation clairement indiqué dans le périmètre. Spécification validée : `specs/001-refonte-interface/spec.md`.
- **Tags du 03/11, nuit** : PR #178 fusionnée (`2310f87`, 21:28 UTC) ; `livrable-E2-v2`, `livrable-E3-v4`,
  `livrable-E4-v2` et `livrable-E5-v2` posés sur `2310f87`. **Aucune exécution de « Livraison » sur ces tags** : ils ont été
  poussés en une seule commande, et GitHub ne crée pas d'événement de push quand plus de trois tags arrivent ensemble ;
  donc pas d'image publiée sous leur nom. L'image du même commit est construite, publiée et déployée par l'exécution
  de `main` (41722049240, verte). La Definition of Done est rejouée sur le poste (`verifier_livrable.py livrable-E3-v4` :
  1 928 tests, évaluations, liens, tag cité, arbre propre : livrable) ; les 244 liens des quatre PDF répondent à leur
  tag ; les dix fichiers de la remise sont identiques aux tags. Désormais : un tag par commande.

- **Décision d'Era du 03/11, au soir** (« partiel change all places », « even E4 ») : partout dans les rapports,
  « partiel » et les symboles ⚠️ et 🟠 deviennent « à consolider » (🟡), comme dans la grille des compétences. Les
  tags étant figés, cela fait de nouvelles versions : E2 v1.0, E3 v2.1, E4 v1.2, E5 v0.7. Elles intègrent ce que
  portait la note de mise à jour (huit critères passés à ✅, deux corrections d'E3, une phrase d'E4), qui est
  remplacée et ne part pas avec la remise. E1 v6 ne change pas (son seul « partiels » parle de deux soirs de collecte).
  Annexe d'E4 : six schémas remis en forme par Era au style d'E1 (texte identique aux originaux, vérifié), 10 pages.
  Annexe d'E2 : trois schémas remis en forme par Era ; A1 et A3 disaient encore l'envoi « non effectué » et « prévu le
  05/11 » : corrigés dans le générateur (test d'abord) et dans les images ; 3 pages.
  **Mistral testé, non activé** (décision d'Era du 03/11) : A2 et A3 d'E2 le disent ; classeurs (98 cellules, statuts
  inchangés) et présentateur (liens PDF d'E2, « J'ai testé Mistral ») remis d'accord.
  Pages inchangées : 17 (20), 20, 20 (30), 5. Restent à l'ancien libellé : le nom du fichier
  `docs/recette/registre-des-partiels.md` et la liste déroulante « PARTIELLEMENT » du classeur détaillé : décision d'Era.

- **Note de mise à jour du 03/11, remplacée le soir même par les nouvelles versions** (ce qu'elle portait) : les huit critères passés à ✅
  après les tags, avec leur preuve (E2 : C6.2, C6.4, C8.5 ; E4 : C16.3, C17.11, C18.6, C19.7 ; E5 : C20.7) ; deux
  erreurs d'E3 (p. 1, « formateur et jury invités », alors que le jury n'est pas invité ; p. 3 et 4, « 503 » au lieu de
  403 sans la clé d'exercice) ; une phrase d'E4 (p. 4, § 1.7, et p. 16, § 7.3 : la spécification de l'écran Question date du 15/10,
  avant l'écran du 16/10). Les rapports et les tags ne changent pas. 12 liens vérifiés par `gh api` le 03/11. Sept des points
  ont été signalés par une relecture externe, vérifiés un par un dans le dépôt ; C6.2 a été ajouté au contrôle.
- **E1 v6** : PR #176 fusionnée (`a91eb3f`), tag `livrable-E1-v6` posé par Era, déployé en production. Les cinq épreuves
  ont leur tag : E1 `livrable-E1-v6`, E2 `livrable-E2-v1`, E3 `livrable-E3-v3`, E4 `livrable-E4-v1`, E5 `livrable-E5-v1`.
- **E5** : PR #175 fusionnée (`57b5b92`), tag `livrable-E5-v1` posé par Era sur `57b5b92`.
- **Retour écrit du formateur (Elbby), 03/11**, huit points : budget en trois parties avec un TJM ; une clé par client
  avant le jury, ou la limite présentée avec sa solution et son coût (C5) ; une capture de l'import suffit (C4) ;
  séparation test et production corrigée (C11) ; les trois attaques non bloquées gardées pour les questions ; schéma du
  parcours Question à envoyer, maquette et interface réelle côte à côte (C17.2) ; démo E3 élargie à l'intégration, au
  monitoring, aux tests et à la CI/CD, démo E4 sur le parcours et ses composants ; dépôt ouvert aux examinateurs le
  jour de l'examen seulement.
- **E1 v6, contenu** : ligne « Budget » en trois montants séparés, jamais additionnés (259,34 € et 11,42 $
  de dépenses au 31/10, dont 0,97 $ d'OpenRouter ; 25 200 € de travail, 63 journées estimées × TJM de 400 € ; 7,19 € et
  environ 2,31 $ par mois pour 10 briefings et 5 questions par jour) ; limite C5 avec l'évolution prévue avant le jury
  (une clé par client ; la clé révoquée reçoit 403, une autre garde 200 ; 1 à 2 journées, 400 à 800 € HT) ; 5 pages ;
  31 liens vers `livrable-E1-v6`. Seconde relecture avant le tag : 11 liens du sommaire rétablis dans le PDF avec
  annexes, « 11 partitions au total, une par année » (livret, puis
  schémas des annexes A et C, pages 7 et 9, corrigés avant le tag), TJM hors taxes, « guide du jury » et « accès sur invitation »
  (le jury n'est pas encore invité), budget détaillé en lien. Guide du jury : tags `livrable-E1-v6` et `livrable-E3-v3`.
  **Remise prévue (décision d'Era du 03/11)** : le PDF de 10 pages, annoncé comme « Livret E1 de 5 pages, accompagné
  d'une couverture et de 4 pages d'annexes » ; le texte officiel dit « Livrable d'entre 2 et 5 pages » (p. 9) sans parler
  des annexes ; le format ne change que si le formateur répond autrement ou si une consigne écrite fixe 5 pages annexes
  comprises. `docs/BUDGET.md` refait
  en trois montants, sources ligne par ligne.
- **Classeurs des compétences du 03/11** : copies OneDrive (`RITA_FIL_ROUGE`), **120 ✅ · 17 🟡 (à consolider) · 0 ❌**
  depuis le tag `livrable-E1-v6`, chaque ligne à consolider avec « Fait » et « Manque » ; E1 v5 remplacé par v6 dans la
  grille (A2, D8, D13, D24, D38) ; pas encore déposés sur le Drive du formateur (attend « upload » d'Era).
- **Documents envoyés au formateur, 03/11 à 14 h 42** (`evidence/C8/envoi-documents-formateur-2026-11-03.md`) : la
  synthèse de veille et le guide d'exploitation en PDF joints (les PDF contrôlés, identiques aux tags), les liens de
  `docs/PILOTAGE-AGILE.md`, `README.md`, `docs/ARCHITECTURE.md`, `docs/CI-CD.md` et des deux sources Markdown, le
  schéma du parcours Question avec la comparaison maquette et écran ; deux questions posées (annexes dans un seul PDF,
  accès du jury). Accusé de réception demandé. Sept critères en attendaient la preuve (C6.4, C8.5, C16.3, C17.11, C18.6,
  C19.7, C20.7) : **passés à ✅ par Era le 03/11** dans les deux classeurs OneDrive, qui comptent **119 ✅ · 18 🟡 ·
  0 ❌** (vérifié par Excel et par un recompte) ; 120 · 17 · 0 après le tag `livrable-E1-v6` (C1). Les rapports tagués
  gardent leur ⚠️ ; pas encore déposés sur le Drive du formateur (attend « upload »).
- **Kanban (C16.4)** : le formateur confirme par écrit, le 03/11 à 11 h 55, qu'il ouvre le tableau depuis son compte
  (`evidence/C16/preuve-acces-kanban-formateur-2026-11-03.md`) ; accès du formateur établi du 26/09 au 03/11
  (`bybysker` déjà dans la gestion des accès le 03/11). C16.4 reste partiel (décision d'Era) jusqu'à l'accès vérifié
  du jury au dépôt et au tableau.
- **Accès du jury (discussion en classe du 03/11, à confirmer par écrit)** : le jury reçoit les livrets vers le
  24-25/11 ; les liens de preuve doivent s'ouvrir dès la réception, pas seulement le jour de l'oral. Question à
  envoyer au formateur par Era : comptes GitHub des examinateurs et date d'invitation, au dépôt **et** au tableau
  (projet privé, séparé du dépôt). L'audit du dépôt passe donc avant le 24/11. Remise toujours le 05/11.
- **E4 v1.1 (`livrable-E4-v1`)** : aucun lien vers le tableau Kanban ni vers les issues (0 sur 198 liens du rapport,
  0 sur 217 avec l'annexe, compté le 03/11) ; les ajouter au § 3.3 demande une v1.2 et un tag `livrable-E4-v2` :
  décision d'Era.
- **E3 : la version remise est la v2.0 (`livrable-E3-v3`), décision d'Era du 03/11** : pas de v2.1. L'erreur connue de
  la ligne API5 du tableau OWASP (« répondent 503 sans elle ») s'explique à l'oral : sans clé ou avec une mauvaise clé,
  la route répond 403 ; 503 seulement si le serveur n'a pas de clé d'exercice (`api/exercice.py:36-45`). Elle est aussi
  corrigée par écrit dans la note de mise à jour du 03/11. La remise (`Downloads\Remise-RITA-2026-11-02\`, 9 fichiers)
  est identique octet par octet aux cinq tags (vérifié le 03/11) ; la note s'y ajoute après la relecture d'Era.
- **Ordre après la remise du 05/11** : d'abord l'oral blanc des 12-13/11, donc la démo E3 complète (intégration de
  l'API, monitoring, tests, CI/CD : point 7 du formateur) et la clé par client pour C5 (test d'abord ; preuve à
  montrer côte à côte : clé révoquée → 403, autre client → 200) ; ensuite, du 14 au 23/11, l'audit du dépôt et les
  accès du jury au dépôt et au tableau, avant que le jury reçoive les livrets (vers le 24-25/11, à confirmer).
- **Restent ouverts** : la clé par client (code et test, après décision d'Era) ; la démo E3 selon le point 7 ; la
  maquette côte à côte (C17.2) ; les captures #73 ; l'audit du dépôt avant de l'ouvrir
  aux examinateurs (secrets, données personnelles, branche `mistral-ue`) ; les messages au formateur, envoyés par Era.

## ▶️ 02/11, 23 H : E4 LIVRÉ (`livrable-E4-v1`, 0 LIEN CASSÉ) ; E5 v0.6 PRÊT POUR `livrable-E5-v1`

**Prochaine action** : commit d'E5 v0.6, PR `develop` → `main`, fusion par Era, tag `livrable-E5-v1`, vérification
complète des liens. Puis l'envoi au formateur, par Era, une seule fois pour E1 à E5 et les documents (C6.4, C8.5, C16.3,
C17.11, C18.6, C19.7, C20.7), avec deux captures datées.

- **E4 v1.1** relu de façon indépendante (17 constats vérifiés et corrigés), PR #174 fusionnée à 21 h 39 UTC
  (`1e04a1a`), déployée à 21 h 49 ; tag `livrable-E4-v1` posé par Era sur `1e04a1a` ; 415 liens des PDF résolus au
  tag, 0 cassé ; vérificateur du dépôt : 381 internes, 642 externes, 0 cassé.
- **E5 v0.6** : état au 02/11 (version de référence `174b0c1`, tableau de bord suspendable, #77 et #132 encore ouvertes,
  dernière exécution du workflow d'alerte le 24/10) ; 21 chemins liés à `livrable-E5-v1` ; 5 pages. Statuts confirmés
  par Era : 10 ✅, C20.5 et C20.7 ⚠️ (C20.7 attend la preuve d'envoi).

## ▶️ 02/11, 21 H : `main` À JOUR ET EN PRODUCTION (`174b0c1`) ; TAGS E1, E2, E3 POSÉS ; E4 v1.1 PRÊT POUR `livrable-E4-v1`

**Prochaine action** : Era envoie le message au formateur (6 fichiers sur Drive, dont la synthèse de veille et le guide,
et les liens de `README.md`, `docs/ARCHITECTURE.md` et `docs/CI-CD.md`), garde deux captures datées et dit « envoyé ».
En parallèle : PR `develop` → `main` pour E4 v1.1, puis le tag `livrable-E4-v1` et la vérification complète des liens.
Ensuite E5 (dernière lecture, tag `livrable-E5-v1`) avant le 05/11.

- **PR #173 fusionnée** par Era à 17 h 09 UTC (`174b0c1`) : sept contrôles verts, deux revues sans remarque ;
  livraison 41488421204, déploiement réussi à 17 h 22 UTC ; la page servie contient le bouton de pause du tableau de
  bord. #73, #78, #79 **déployés**, non vérifiés à la main en production ; #152 sur `main`, hors de l'image de l'API.
- **Tags** `livrable-E1-v5`, `livrable-E2-v1`, `livrable-E3-v3` posés par Era sur `174b0c1` ; trois exécutions vertes ;
  liens : 0 cassé sur le dépôt (378 internes, 441 externes) et dans les cinq PDF (213 liens).
- **Remise préparée, pas encore envoyée** : `Downloads\Remise-RITA-2026-11-02\`, six fichiers identiques aux versions
  des tags (E1 v5 avec et sans annexes, E2 v0.9, E3 v2.0, guide d'exploitation, synthèse de veille S33 à S36).
- **E4 v1.1** (`b70f5c8`, puis les liens) : preuves du 02/11 intégrées ; C14.2, C14.3, C14.4, C15.3, C17.3, C17.4 à
  ✅ (décision d'Era, limites gardées) ; 27 ✅ · 11 ⚠️ · 0 ❌ ; 20 pages, annexe de 10 (A1, A4, A6) ; 185 liens vers
  `livrable-E4-v1` dans le rapport, 16 dans l'annexe. C17.11, C18.6 et C19.7 attendent la preuve d'envoi.
- **Registre** : C6.2 ✅ (planification, décision d'Era) ; trois états des correctifs (sur `main`, déployé, vérifié).
- **Présentateur** (hors dépôt) : budget E1-2 en euros (environ 270 €, taux BCE du 30/10), rôle en E1-1, script en E1-3,
  import en E1-6, jointure en E1-8, preuves des tests en E3-5 et E3-7 ; dix boutons du livret vers la v5.
- **Restent ouverts** : E3, phrase 503/403 du tableau OWASP (ligne API5) à corriger à la prochaine version ; E2 v0.9
  affiche encore C6.2 en ⚠️ (tag figé) ; classeur des compétences à mettre à jour ; diapositives E2, E4 et E5 ;
  note de veille S45 ; écart E1 « +0,00 % ».

## ▶️ 02/11, SOIR : RETOUR ÉCRIT DU FORMATEUR APPLIQUÉ (E1 v5, E3 v2.0), E2 v0.9, RECETTE C17.3 ET C17.4 ; RIEN SUR `main`

**Prochaine action** : Era décide de la PR `develop` → `main`. Après la fusion : poser les tags `livrable-E1-v5`,
`livrable-E2-v1` et `livrable-E3-v3` (procédure `docs/FILE-DE-VALIDATION.md`), puis lancer `scripts/verifier_liens.py` :
**zéro lien cassé exigé** (les liens d'E1 v5 et d'E3 v2.0 visent ces tags, introuvables tant qu'ils ne sont pas posés),
et ouvrir un lien de code et un lien de preuve depuis l'accès du formateur. Remettre le guide d'exploitation (C8.5) avec
une preuve datée. Répéter avec la liste du formateur : se présenter, lire les chiffres, ouvrir les onglets avant.

- **Recette C17.3 et C17.4** (`99de9fa`, `eca894b`, `2743461`) : cinq écrans, quatre situations chacun ; 14 tests au
  clavier, 8 tests d'erreur dans un navigateur (7 mutations détectées). Écart E2 (focus du tableau de bord) corrigé,
  test d'abord ; E3 fermé ; E1 (« +0,00 % » pour une pire baisse nulle) attend la décision d'Era. Sur les données
  réelles, #78 et #79 étaient latents.
- **C6.6 et C6.8** (`a18604a`) : auteur de la note S41 vérifié (étudiant en M2 au JAIST) ; coût des faux positifs recoupé
  par AgentDojo (NeurIPS 2024) ; constat central non recoupé, dit tel quel.
- **E2 v0.8** (`06fb64a`, version que le formateur peut relire), puis **v0.9, version jury** (`7a43b2a`, 20 pages) : C7.4
  service par service et usage par usage ; données transmises au modèle précisées ; le contrôle du prompt du banc, annoncé
  mais absent, remplacé par la garantie réelle (par construction) ; `/sante` et la vigie distingués.
- **Retour écrit du formateur sur l'oral blanc du 30/10** (`Downloads\Retour_soutenance_E1-E3_Era.pdf`), quatre
  décisions d'Era (`CONTINUITE.md`, D) :
  - C4 : MCD aligné sur la base, `VALEUR 0,n ── est cotée lors ── 1,1 COTATION` (`e44285c`, test d'abord, MCD du
    01/08 gardé) ; import en action sur une base jetable (`ec99e3c`) ;
  - **E1 v5** (`e44285c`) : figure et section 5, phrase RGPD datée, PDF avec annexes refait (0,24 ms en page 6, annexe B
    sans erratum) ;
  - **E3 v2.0** (`113b279`, 20 pages) : OWASP API en entier (4 appliqués, 4 partiels, 2 sans objet), clé partagée et
    403 assumés, Lighthouse, séparation des traces prouvée, seuil de 15 s expliqué, trois injections avec risque et
    suite, règles de données testées, état au 02/11 daté ;
  - C5 : la réponse 403 reste, défendue.
- **Présentateur**, hors dépôt (`Downloads\RITA_E1_Presentation_Fintech\site`, une copie `.bak` de chaque fichier) :
  E1-2 (planning, budget de 259,34 € et 10,45 $), E1-6 (MCD 0,n, deux raisons de PostgreSQL), E3-4, E3-5, E3-7, E3-8,
  E3-9, réserves d'E1-6 (dont l'import en action) et d'E1-8. Vérifiés dans `presenter.html` **et** sa fenêtre
  publique : aucune erreur JavaScript.
- **Mesures** : suite complète 1 924 réussis, 48 sautés (sans base locale), 2 échecs attendus ; job `base` sur GitHub,
  25 réussis, 0 sauté.
- **Restent ouverts** : le rapport E4 cite encore le MCD du 01/08 (`rapport-E4.md`, lignes 98 et 761), à aligner à sa
  prochaine révision ; l'écart E1 de la recette ; aucun statut RNCP ne change sans vérification et validation d'Era.

## ▶️ 02/11, NUIT : MARQUEUR `postgresql` À LA PLACE DE LA RECHERCHE DU MOT (`997aae6`, PUIS UN CORRECTIF)

**Prochaine action** : Era commite et pousse le correctif du job `base` (Playwright, voir plus bas) ; lire le
job `base` sur GitHub (attendu : 24 réussis, 0 sauté) ; ensuite reprendre la recette critère par critère (`docs/recette/registre-des-partiels.md`), sans
changer de statut sur la seule preuve locale.

- **Les 24 tests qui demandent PostgreSQL portent le marqueur** (`pytestmark` dans six fichiers, trois tests de
  `tests/test_vue_valorisation.py`) ; le job `base` lance `pytest -m postgresql tests`. Ce sont les mêmes 24 tests, nom
  par nom, que la sélection par le mot (référence `evidence/C18/tests-postgresql-avant-marqueur-2026-11-02.txt`).
- **Garde-fou** : `dsn_de_test()` fait échouer un test qui demande la base sans le marqueur (`tests/garde_base.py`,
  registre posé par `tests/conftest.py`). Mis à l'épreuve : marqueur retiré d'un test, échec qui le nomme, sélection
  à 23 ; fichier restauré. Tests écrits avant : 11 échecs, puis 17 réussis.
- **Rejoué en local** sur une base jetable : 24 réussis, code 0 ; sans base, 24 sautés, code 1. Suite complète :
  1 877 réussis, 47 sautés (dont les 24), 2 échecs attendus. Preuves : `evidence/C18/marqueur-postgresql-2026-11-02.md`.
- **Premier passage sur GitHub en échec** (`997aae6`, passage 41363062480) : 24 réussis mais 3 sautés. Tous les
  fichiers se chargent avant la sélection, et `test_smoke_ui.py` importe Playwright, absent du job `base`.
  Reproduit sur le poste, test d'abord, correctif `pip install playwright` dans le job ; règle « aucun saut »
  gardée. Preuve : `evidence/C18/marqueur-premier-passage-github-echec-2026-11-02.md`. À pousser.
- `docs/CI-CD.md` et le registre de la recette suivent ; `ETAT.md` porte aussi les précisions de la relecture du 02/11
  (seconde revue de #152 terminée ; 24 des 46 tests du job demandaient PostgreSQL).

## ▶️ 01/11, NUIT : RECETTE SUR `develop` (E2, E4, E5, QUATRE CORRECTIFS, JOB `base`) ; RIEN SUR `main`

**Prochaine action** : montrer à Era la liste des 24 tests PostgreSQL, puis proposer leur marquage explicite à la
place de la recherche du mot `dsn_de_test` dans le job `base` ; après le changement, vérifier que ce sont les mêmes
tests, pas seulement le même nombre ; ensuite reprendre la recette
critère par critère (`docs/recette/registre-des-partiels.md`), sans changer de statut sur la seule preuve locale.

- **Six commits poussés sur `develop` par Era** : `5d13cd7` (E2 v0.7, E5 v0.5, synthèse de veille), `735c020` (E4 v1.0 :
  20 pages, 29 avec l'annexe ; 21 ✅ · 17 ⚠️ · 0 ❌), `fd12d1d` (correctifs #78, #73, #79), `516fbf5` (job `base`),
  `c0ce2b9` (#152), `afa741d` (registre de la recette, documentation de la CI). **Rien n'est fusionné dans `main`** ; la
  production n'a pas changé.
- **Correctifs, tests écrits avant**, preuves avant et après dans `evidence/C17/correctifs-2026-11-01/` : #78 (RSI
  indéfini sur une série plate) ; #73 (clé gardée seulement après un appel accepté, Briefing et Question) ; #79 (pire
  baisse jamais positive) ; #152 (verrou de démonstration de la passerelle MCP : jeu attendu versionné de 7 positions,
  comparaison exacte de 4 champs, réponse reconstruite et vérifiée, refus au moindre doute). Seconde revue de #152
  terminée ; correctif testé sur `develop`, non livré en production.
- **Job `base`** : les tests PostgreSQL sur une base jetable ; le job échoue si l'un de ses tests est sauté. Sur GitHub : 43 réussis,
  0 sauté (`516fbf5`, passage 41353566356) ; 46 réussis, 0 sauté, dont 24 PostgreSQL, avec #152 (`afa741d`, passage
  41357550846). **Exigé pour fusionner dans `main`** depuis le 01/11 à 23 h 11 (règle `main protegee`, sept checks).
  Preuves : `evidence/C18/job-base-premier-passage-github-2026-11-01.md` et `job-base-avec-152-github-2026-11-01.md`.
- **CI du 01/11 au soir** : `pytest` 1 873 réussis, 45 sautés, couverture 96,32 % ; Livraison verte, aucun déploiement.
- **Statuts RNCP inchangés** : réévaluation critère par critère après vérification des preuves, pas automatiquement.
- **Restent ouverts** : #76, #75, #74 (changements de production, à décider à part) ; le test de fumée
  `test_une_mauvaise_cle_est_refusee_a_l_ecran` a échoué une fois sous charge (attente fixe de 1 500 ms, refus réel
  mesuré entre 47 et 70 ms), correction du test proposée, non appliquée ; le jeu de la démonstration Docker
  (`data/demo/`, 3 positions) reste refusé par la passerelle MCP (limite connue, à décider) ; remise du guide (C8.5)
  non prouvée ; accès du jury au dépôt non confirmé.
- **Ensuite** : PR `develop` vers `main` quand Era le décide, puis les tags des livrables après la fusion.

## ▶️ 01/11, APRÈS-MIDI : E2 v0.7 (16 PAGES, ANNEXE DE 4) ET E5 v0.5 PRÊTS, À RELIRE PAR ERA ; RIEN N'EST COMMITÉ

**Prochaine action** : Era relit `docs/rapports/E2/rapport-E2-avec-annexe.pdf` et le diff ; puis commit sur `develop`
(E2, annexe, schémas, deux tests, E5, `ETAT.md`, `CONTINUITE.md`, `CHANGELOG.md`), PR `develop` vers `main`, et les tags
des livrables E2 et E5 après la fusion.

- **E2 v0.7** : 16 pages (format de 15 à 20), sommaire numéroté depuis le PDF ; qualification des sources, banc détaillé
  par cas, indicateurs cités par service (9,3 contre 8,0 sur 13, remesuré le 01/11), budget séparant facturé et estimé,
  plafond D2 de 5 USD, extrait de configuration et son test, capture Langfuse, quatre liens de preuve épinglés à
  `922349d` ; corrections de la relecture du 01/11 (rôle d'OpenRouter, modèle Anthropic, contrôle de fidélité, portée
  de la zone UE, MC.PA, drawdown). **Grille : 13 ✅ · 6 ⚠️ · 1 ❌** : C6.3, C7.1, C7.3, C7.5 et C7.7 passent à ✅ après relecture contre le
  règlement (p. 22 à 24) ; C7.6 aussi, une fois les prérequis d'Azure et d'OpenRouter côte à côte (§ 3.5), limite : débit
  d'OpenRouter non relevé ; décisions d'Era.
- **Annexe d'E2, A1 à A3** : trois schémas dessinés le 01/11 pour le rapport (`docs/rapports/E2/schemas/` : générateur,
  `.drawio`, `.svg`, `.png`), `tests/test_schemas_e2.py` ; PDF avec annexe : 20 pages.
- **E5 v0.5** : l'isolement de la copie du 23/10 cité avec sa preuve (§ 8) ; C20.5 et C20.7 précisés (alertes
  automatiques et vigie à la main ; communication non prouvée) ; toujours 5 pages.
- **Synthèse de veille S33 à S36** : rendue au format lisible et contrôlée le 01/11
  (`evidence/C6/controle-accessibilite-synthese-2026-11-01.md`) ; à remettre avec le guide.
- **E4, relecture des 19 ⚠️** (lecture seule, aucun statut changé) : 5 lignes semblent plus sévères que le texte
  officiel, 7 sont finissables avec une preuve nouvelle, 7 sont de vrais manques ; la grille n'a pas de ligne pour
  les deux critères de documentation de C19. En attente de la décision d'Era.
- **#77** : commentaire de tri prêt dans le scratchpad, non publié ; ticket ouvert jusqu'à son critère de clôture (les
  alertes de production ne comptent plus les essais locaux, vérifié et consigné).
- **Remise du guide (C8.5)** : par Era, avec les livrables, dans son dossier Drive partagé, formateur prévenu ; preuve
  datée (quel fichier, avec qui, quand) dans `evidence/C8/`. Non prouvée à ce jour.
- **Accès** : le formateur (`bybysker`) lit le dépôt (vérifié le 30/10) ; Era lui demande d'ouvrir les quatre liens
  d'E2 ; l'accès du jury n'est pas confirmé.
- **Ni nouveau banc ni nouvelle fonctionnalité avant le 05/11** (`CONTINUITE.md`).

## ▶️ 01/11 : E4 v0.9 ET E5 v0.4 SUR `develop` ; INC-009 SUR `main` ET EN PRODUCTION (`922349d`)

**Prochaine action** : Era ferme l'issue #137 (correctif sur `main` depuis le 01/11, tests verts, retour à la normale
réel pas encore observé) ; puis envoie `docs/rapports/E5/rapport-E5.pdf` (v0.4, 5 pages) au formateur pour relecture,
après avoir vérifié son accès au dépôt privé (peut-il ouvrir la PR #171 depuis son compte ?).

- **01/11, midi** : PR #171 fusionnée dans `develop` (`6c87a10`, CI verte, 1 822 tests dont les 4 d'INC-009), puis PR
  #172 `develop` vers `main` (`922349d`, Revue PR et Codex sans constat) ; livraison réussie, `/health` de production
  annonce `922349d`. E5 v0.4 : statut d'INC-009 mis à jour (§ 7, § 8, ligne C21.5), toujours 5 pages. Présentateur
  (hors dépôt) : phrase d'E3-2 ajoutée après le clic (`data-e3-10.js`, sauvegarde `.bak-5`). Étude des quatre sujets
  (indicateurs, annonces fraîches, briefing du matin, accès) : aucune fonctionnalité avant le 05/11 ; feuille de route
  proposée pour la suite, à confirmer par Era (`CONTINUITE.md`, G) : d'abord la date de séance et l'heure de rédaction à
  l'écran, puis un pilote d'annonces réglementées (API Info-financière, essai LVMH du 01/11 : annonce du 12/10
  retrouvée à 17:45:26, délai de disponibilité non mesuré).

**Fait le 31/10, nuit** :
- **Périmètre d'E5, décidé par Era** : règle d'E4 (ce qui est dans `d3a4198` compte), plus les exercices locaux de la
  vigie (#127 à #132) cités avec leurs dates ; incident principal : #137, traité en entier comme INC-009 ; #77 trié.
- **#77 trié en lecture seule** (traces Langfuse lues par l'API, sans texte) : deux épisodes du poste, aucun de la
  production (traçage du serveur actif depuis le 21/10) ; 03/10 : deux fournisseurs sans clé, repli réussi ; 10/10 :
  Mistral Large 4 en blocs, `TypeError` dans le garde-fou de sortie (observation `56fdec89dcb91612`), corrigé le jour
  même par `2a7f18c` sur la branche `mistral-ue`. Commentaire de clôture rédigé, **non posté** : décision d'Era.
- **INC-009** : un retour à OK de Langfuse ouvrait un nouveau ticket (#137). Reproduit sur le workflow de `4be89d0`
  dans un conteneur jetable (jq téléchargé avec l'accord d'Era, aucun secret, aucun ticket) : 13 passed, 1 failed ;
  14 passed après correctif, mêmes tests. Branche `fix/137-retour-a-la-normale`, commits `a57dccb` et `78957e0`,
  PR #171 verte (1 821 tests). Débogage écrit dans #137 par Era ; post-mortem
  `evidence/C21/INC-009-retour-a-la-normale-ouvre-un-incident.md` ; journaux `evidence/C21/INC-009-reproduction/`.
- **E5 v0.2** : `docs/rapports/E5/rapport-E5.md` et `.pdf`, 5 pages, sommaire numéroté depuis le PDF
  (`tests/test_rapport_e5_sommaire.py`), 11 liens GitHub vérifiés, deux relectures intégrées ; auto-évaluation
  10 ✅ · 2 ⚠️ (C20.5 vigie lancée à la main, C20.7 accessibilité non contrôlée). Copie
  `C:\Users\kanda\OneDrive\RITA\reports\rapport-E5-2026-10-31.pdf`.

- **01/11, extraits de code** (relecture recommandée, décision d'Era « do it ») : E5 v0.3, la décision corrigée
  d'INC-009 (`alerte-incident.yml`, lignes 140 à 148, `a57dccb`) et son test (lignes 225 à 228) au § 7 ; E4 v0.9,
  deux encadrés : la clé comparée puis refusée (`api/main.py`, lignes 201 et 205 à 208, `d3a4198`, trois lignes de
  commentaire remplacées par `⋮`, dit dans la légende) avec `test_question_sans_cle_403`, et `needs:` et `if:` de
  `deployer` (`livraison.yml`, lignes 349 à 351), qui corrige l'ancienne phrase (trois travaux requis, il y en a
  quatre). Chaque ligne imprimée vérifiée contre son commit (23 sur 23). Textes redondants raccourcis, glossaires sur
  deux colonnes : E4 reste à 20 pages, E5 à 5 ; aucun statut changé. Copies OneDrive du 01/11 (v0.9 et v0.3).

- **01/11, liens de la veille S41** : les deux liens signalés n'étaient pas morts (certificat incomplet chez l'UCF,
  403 intermittent de Wikipédia) ; remplacés par la page de faculté de David Mohaisen (`www.cecs.ucf.edu`) et la page
  d'auteur de Mark Russinovich sur le blog Azure, contenu vérifié ; remplacement noté dans le relevé. Vérificateur
  de liens : **0 lien cassé** sur tout le dépôt (322 internes, 418 externes).

**En attente d'Era** : fusion de la PR #171 ; fermeture de #137 une fois sur `main` ; #77 (commentaire prêt) et #132
(« clôture manuelle de l'exercice ») ; deux règles de fermeture à trancher (vigie ou humaine) ; séparation exercice et
production dans Langfuse à vérifier ; GitHub CLI à ajouter au guide d'exploitation ; liens vers les fichiers au moment
du tag ; traduction anglaise d'E5 non faite.

## ▶️ 31/10 : E2 v0.6 RÉDIGÉ, À RELIRE ; PRODUCTION REMISE À AZURE SEUL ; NOTATION C7 TERMINÉE

**Prochaine action** : relecture d'E2 v0.6 par Era (`docs/rapports/E2/rapport-E2.md`) ; statuts de C8 décidés par Era
le 31/10, ceux de C6 et C7 repris du recomptage du 31/10, à confirmer. Ensuite E5. Livrables le 05/11.

**Fait le 31/10** :
- E4 v0.7 (`b270355`) : relecture globale, 17 ✅ · 19 ⚠️ · 0 ❌.
- Notation du français du banc C7 : 60 textes sur 60 (`03211d2` à `2bd2bc0`), évaluation assistée par IA, relue et
  validée par Era ; jointure avec la clé, en lecture seule : 30 textes par fournisseur, moyenne 1,00 des deux côtés.
- `LLM_ORDRE` lu dans le conteneur de production : `foundry,anthropic,openrouter`. Défaut passé à `foundry`, test
  d'abord (`d1cbb7b`) ; PR #170 fusionnée (`97b329e`) ; livraison refusée deux fois (« ComposeNonInstalle »), copie du
  fichier Compose installée à la main par Era, livrée à 13:54 ; conteneur relu : `foundry`. Documentation alignée.
- E2 v0.6 : C6, C7 et C8 réécrits et intégrés au rapport, puis corrigés après deux relectures indépendantes (huit, puis six points vérifiés ; Mistral placé en évolution envisagée) ; auto-évaluation 7 ✅ · 12 ⚠️ · 1 ❌ (C7.2 monte, décision d'Era ; C8.5 : guide non remis).
- C8.5, format : guide d'exploitation rendu de nouveau le 31/10 (`docs/EXPLOITATION.pdf`, 35 pages) avec l'option
  `--lisible` de `scripts/rendre_pdf.py` (test d'abord) : 12 pt, liens soulignés, 66 signets, balisé, en français,
  aucun lien vers un fichier du poste ; contrôle et limites dans `evidence/C8/controle-accessibilite-guide-2026-10-31.md`.
  **Non envoyé**, décision d'Era du 31/10 : pas d'envoi séparé au formateur ; le guide part avec les livrables du 05/11.
- Budget (C1) : `docs/BUDGET.md` créé le 31/10 depuis les justificatifs reçus par courriel (Hetzner 75,35 € facturés,
  Mistral 17,99 €, GitHub Pro et Copilot 10,45 $) et les montants déclarés par Era (Claude 20 €/mois de mai à octobre,
  OpenAI 23 €/mois en septembre et octobre) ; abonnements partagés comptés en entier (convention d'Era) ; avril exclu.
  Total recensé, provisoire : 259,34 € et 10,45 $ (facturé, payé et déclaré mêlés) ; **reste à lire** : la consommation OpenRouter de la clé de RITA et le crédit
  restant, et le paiement de la facture Hetzner d'août. Livret **E1 v4 préparé** (`rapport-E1.html` et `.pdf`, 5 pages) :
  ligne budget chiffrée, liens vers `livrable-E1-v4` (tag à poser après la fusion), v3 et son tag intacts.
- E4 v0.8 : passages sur la documentation mis à jour au 31/10 (guide d'exploitation rendu lisible, contrôle limité,
  sans audit PDF/UA) ; trois formulations corrigées après une relecture (JavaScript, livraison continue et l'exception du
  fichier Compose, clé absente du code versionné) ; **PDF produit, 20 pages** (limite 15 à 20), `docs/rapports/E4/rapport-E4.pdf`,
  et une version avec l'annexe des schémas existants (`annexe-schemas-E4.md`, 9 pages en paysage : MCD, trois wireframes agrandis, architecture,
  flux en deux vues, chaîne de livraison, chacun daté avec sa limite), `rapport-E4-avec-annexe.pdf`, 29 pages ; copies datées
  dans OneDrive. Relecture du 31/10 au soir intégrée : erratum du flux A4 (le schéma place le garde-fou de sortie avant
  l'appel au modèle ; le code fait l'inverse, `api/main.py`, lignes 303 et 320), limite C14.3 complétée (scénarios de
  Question non formalisés). Le schéma d'origine, `evidence/C15/`, garde l'erreur : une preuve ne se réécrit pas.
  Première page refaite sur le modèle d'E3 v1.9, après la remarque d'Era (« il faut un sommaire en première page ») :
  logo, ligne d'identité, « En une minute », sommaire dont les numéros sont lus dans le PDF
  (`tests/test_rapport_e4_sommaire.py`) ; la page 1 de l'annexe porte la même ligne d'identité et les cinq schémas en
  miniature, chacun relié à sa page. Le corps reste à 20 pages.
  Liens cliquables vers le tag E4 : à faire au moment du tag.
  Architecture, flux et chaîne de livraison en **mise en forme du 31/10** (icônes, flèches), texte identique mot pour mot
  à la version du dépôt : **exception limitée accordée par Era le 31/10** à sa règle « rien de l'autre projet dans ce dépôt », pour
  ces trois fichiers seulement (`docs/rapports/E4/schemas/`).

**Évolution prévue, décidée par Era le 31/10 : après le 05/11.** « Vue marché » en haut de la page Indicateurs : une
carte par valeur suivie, verte en hausse, rouge en baisse, avec le signe et la flèche (jamais la couleur seule). Déjà
spécifiée le 04/10 (`docs/conception/frontend/refonte-2026-10.md`, ligne 41 et § 12, non implémentée) ; les données
existent déjà (`/donnees/indicateurs`). À décider après les rendus : avant l'oral blanc des 12-13/11, ou après le
jury. Hors des rapports tant qu'elle n'est pas faite.

**Ouvert** : INC-008 (ajout daté, ou mention dans C8 : décision d'Era) ; Google News encore cité dans
`docs/exploitation.md` ; chemin mort `docs/EXPLOITATION.md` (rapport E2, `evidence/C8/README.md`,
`deploy/deployer.py:574`) ; Mistral (contrat non lu, PR #88 en conflit).

---

## ▶️ RAPPORT E4 : PREMIÈRE VERSION COMPLÈTE (v0.6), À RELIRE ; PROCHAINE SÉANCE : RELECTURE GLOBALE CIBLÉE D'E4, PUIS E2 ET E5

**Ce que c'est, et ce que ce n'est pas.** `docs/rapports/E4/rapport-E4.md` est écrit en entier (huit sections, 36
critères, environ 10 000 mots, commit `475f74f`). C'est une **première version complète à relire, pas un livrable
validé** : la matrice (20 ✅ · 16 ⚠️ · 0 ❌) est une auto-évaluation, pas une validation du jury ; une CI verte confirme
les contrôles exécutés, pas la conformité RNCP ; aucun PDF n'est encore produit.

**Fait le 30/10, au soir, dans le dépôt** (chaque envoi lu en CI, toutes vertes ; dernière : Tests 41135445060,
Livraison 41135445058) :
- recomptage des 36 critères (`docs/rapports/E4/recomptage-criteres-2026-10-30.md`, `d0663ef`) ;
- rapport E4 de v0.1 à v0.6 (`386978e`, `95c351f`, `6c3014a`, `f40cc93`, `ecd2b4f`, `475f74f`), une section à la fois,
  chacune relue contre le code et GitHub avant d'entrer ;
- une note sur l'atelier n°5 ajoutée (`d8680b6`), puis retirée à la demande d'Era (`8b700b6`).

**Décisions d'Era du 30/10** :
1. **Périmètre d'E4** : la version de RITA présentée au jury, ses cinq écrans (portefeuille, indicateurs, briefing,
   question, tableau de bord), version de référence `d3a4198` (livrée le 27/10). **Exclus** : les ateliers des sprints
   (`eval/ateliers/`) et les copies d'exercice. Une fonctionnalité faite pendant un sprint entre si elle est intégrée.
2. **Ordre** : E4, puis E2, puis E5. Rapports remis le 05/11 (fenêtre du 5 au 9/11 selon Era) ; tout prêt avant le
   12/11.
3. **Règle de la matrice** : ✅ seulement si le critère entier est satisfait ; ⚠️ si une preuve existe mais qu'une
   partie manque.

**Manques découverts en écrivant E4** (détail dans le rapport) :
- `docs/ARCHITECTURE.md` (ligne 71), le message d'erreur et la docstring de `api/main.py` disaient que l'API « refuse
  de démarrer » sans clé : faux, la configuration n'est contrôlée qu'à l'authentification. **Corrigé le 30/10**
  (`a2c0d51`, suite locale 1805 réussis, CI verte). *Ce n'était pas une découverte* : l'erreur avait été corrigée dans
  le rapport E3 le 11/10 (`CHANGELOG.md`), sans l'être dans ces fichiers. Le commentaire de `docker-compose.yml` et
  l'en-tête d'`ARCHITECTURE.md` (« schémas du 04/10 », faux depuis le 24/10) sont corrigés avec la v0.7.
- Le tableau Kanban n'a plus bougé après le 14/10 ; les cases des plans de travail ne sont pas cochées (0 sur 221) ;
  7 pull requests sur 66 (12-26/10) citent une issue, aucune ne la ferme automatiquement.
- Les en-têtes de sécurité (S1) étaient absents en production le 03/10 ; non revérifiés depuis.

**Prochaine séance, dans l'ordre** :
1. ✅ **Relecture globale d'E4, faite le 30/10** : relecture indépendante (34 constats, dont 5 hauts, tous vérifiés et
   corrigés en v0.7) ; tri des partiels fait en séance : 1 formulation, 2 preuves à verser ou vérifier (C16.3,
   C16.4), 2 non rattrapables (C16.1, C17.2), les autres demandent un vrai travail. Restent les constats bas de la
   relecture, à reprendre au passage.
2. ✅ Correction des phrases sur le démarrage de l'API sans clé (`a2c0d51`).
3. **E2** (v0.3 depuis le 09/10), puis **E5** (aucun rapport).
4. Plus tard : les compléments C14 (parcours de Question et du Tableau de bord, spécification du Tableau de bord,
   critères d'accessibilité de Question), datés et présentés comme rétrospectifs ; le PDF d'E4 (15 à 20 pages : le
   texte est déjà proche de la limite, sans figure) ; la démonstration d'E4 et ses captures de secours.

**Toujours ouvert depuis l'oral blanc** (section suivante) : répéter E1 et E3 ; message à Héléna, non parti (y ajouter
la question sur la compétence transversale C7 et celle sur l'oral blanc des 12-13/11 en visio) ; factures du budget
E1 ; décision sur la branche `classeur-competences`.

---

## ORAL BLANC 1 PASSÉ LE 30/10 (E1 + E3) ; ORAUX BLANCS COMPLETS LES 12 ET 13/11 (90 MIN) (HISTORIQUE DU 30/10, SOIR)

**Ce qui s'est passé** (30/10, 10 h 30, Google Meet ; Héléna VICENTE, Nadège MIQUEY, Elbby AGWU) : 32 minutes au
total, E1 en 13 min 46 et E3 en 18 min 31, mesurés sur la transcription. Démonstration en direct réussie, plan B prêt.
Retours : se présenter au début et relier son parcours au choix de la bourse ; définir action, ticker et cotation ;
dire les deux fonctionnalités en une phrase ; acteurs et organisation dès E1 ; extraits de code (nettoyage, SQL,
CI/CD, OWASP avec exemple) ; captures à la place de Langfuse et d'OpenAPI en direct ; zoomer pendant la démonstration ;
exemples chiffrés pour les métriques. Vue d'ensemble du schéma de données : facultative, gardée en réserve.

**Fait le 30/10, hors du dépôt** : retours intégrés au présentateur (`Downloads\RITA_E1_Presentation_Fintech\site`),
toujours 10 + 10 diapositives. Le code affiché est lu aux tags `livrable-E1-v3` et `livrable-E3-v2`, sans changement :
**rien n'a changé dans le dépôt ni dans les livrables envoyés**. Temps prévus à 87 mots par minute (débit mesuré) :
E1 14 min 09 sur 15, E3 19 min 11 sur 20. Retours, analyse de la transcription et message à Héléna : Obsidian
`03-Oraux/oral-blanc-1-E1-E3-retours (2026-10-30).md`.

**Prochaines actions** :

1. Era : répéter E1 et E3 à voix haute avec un chronomètre, sans ajouter de contenu.
2. Era envoie le message à Héléna : confirmer la règle de la vidéo (rapportée par un camarade : pas de vidéo de toute
   la présentation, démonstration en vidéo possible sans le son) et demander une séance sur l'introduction.
3. Oraux blancs complets les **12 et 13/11**, dans l'ordre de la convocation : E1 (15 min), E3 (20 min, démonstration),
   E4 (20 min, démonstration), E2 (15 min), E5 (10 min), puis 10 min d'échanges avec le jury.
   **Objectif d'Era** (30/10) : tout prêt avant le 12/11, les cinq rapports et la présentation complète. Rapports :
   fenêtre de remise du 5 au 9/11 (dit par Era le 30/10, source écrite non vue), **date retenue par Era : le 05/11** ;
   du 06/11 au 11/11 : parties E4, E2 et E5 du présentateur, puis répétitions.
3 bis. **Jury : mardi 01/12/2026 à 11 h 15, en visioconférence Google Meet** (convocation d'Helena VICENTE datée du 30/10,
   PDF dans les téléchargements d'Era ; le lien n'est pas recopié dans le dépôt). Se connecter 30 min avant, à 10 h 45,
   avec une pièce d'identité et la convocation. 90 min : installation 5 min, 80 min de présentation, 10 min d'échanges,
   puis 10 min de délibération sans le candidat. Les démonstrations d'E3 et d'E4 passeront par le partage d'écran.
4. Restent ouverts les points 5 et 6 de la section suivante : factures du budget E1 avant le 05/11 ; décision sur la
   branche `classeur-competences`. E2, E4 et E5 restent dus le 05/11.

---

## ORAL BLANC 1 : VENDREDI 30/10 À 10 H 30 (E1 PUIS E3) ; TAGS `livrable-E1-v3` ET `livrable-E3-v2` POSÉS LE 27/10 SUR `d3a4198`, EN PRODUCTION (HISTORIQUE DU 29/10)

**Prochaines actions (Era), dans l'ordre** :

1. ✅ Fait le 28/10 : PR #169 fusionnée dans `develop` (`6077bd7`, CI verte) ; livret E1 v3 et grilles des
   compétences envoyés sur Discord, **E1 accepté par le formateur** (`docs/FILE-DE-VALIDATION.md`, lignes 7 et 9).
2. ✅ Fait le 29/10 : rapport E3 `docs/rapports/E3/rapport-E3-v1.9-bandeau.pdf` envoyé sur Discord, avec trois
   précisions (p. 16 : le livrable présent est `livrable-E3-v2` ; p. 1 et glossaire : l'AMF distingue conseil et
   recommandation, ne rien recommander est le périmètre choisi pour RITA ; p. 7, 9 et 13 : trois formulations trop
   larges) ; `docs/FILE-DE-VALIDATION.md`, ligne 8. Retour du formateur attendu.
3. **Jeudi 29/10 après 17 h 35, sur le serveur** : rattraper les cours et les taux, à blanc puis pour de vrai,
   `docs/exploitation.md#rattrapage-cours-production`, avec `--du 2026-10-27 --au 2026-10-29`. Sans lui, le briefing
   de la démonstration de vendredi affichera deux séances de retard, et la séance du 27/10 reste celle prise à
   16 h 43, avant la clôture.
4. Répéter E1 (15 min) et E3 (20 min, démonstration comprise), en sachant répondre sur l'erratum d'E1 et les huit
   imprécisions d'E3 (ci-dessous). Les vidéos d'entraînement et les questions de jury restent hors du dépôt.
   Support du 29/10, hors du dépôt : la vidéo d'entraînement v2 (24 min 10 s, textes du présentateur réécrits par
   Era à 16 h) et son extrait « guide de démonstration » (10,9 min : préparer, lancer le présentateur, puis chaque
   démonstration d'E3). Geste à ne pas oublier : rappuyer sur **W** avant de changer de diapositive, sinon la fenêtre
   de démonstration reste ouverte sur l'écran du jury.
5. Avant le 05/11 : réunir les factures (hébergement, OpenRouter, GitHub Actions, abonnements des assistants de
   développement, Mistral) pour chiffrer le budget du livret E1 v4.
6. **Décision d'Era, après l'oral blanc** : reporter ou non les classeurs du 29/10 (copies OneDrive) dans la branche
   `classeur-competences`, qui porte encore ceux envoyés le 28/10 (`c56b899`) ; et dire ou non au formateur que le
   classeur détaillé reçu le 28/10 n'avait pas de rédaction pour C10 et C11 (voir ci-dessous).

**Fait le 29/10, après l'envoi d'E3** :

- **Classeurs des compétences, copies OneDrive** (`OneDrive\RITA\RITA_FIL_ROUGE`, noms en `_27_10_26` gardés) :
  avant modification, les cinq fichiers étaient identiques octet pour octet à ceux de `c56b899`, la version envoyée
  le 28/10. Aucun statut ne change (111 ✅ · 25 🟡 · 1 ❌ ; E1 27 · 1 ; E3 34 · 5, comme le § 10 du rapport E3 v1.9).
  Classeur détaillé : C1 dit l'acceptation d'E1 et la raison du critère partiel (le budget) ; C9, C12 et C13 citent
  le rapport E3 v1.9 au lieu de la v1.5 ; C10 et C11 sont rédigés d'après les § 4 et § 5 du rapport ; la colonne E
  donne l'état de chaque livrable. Synthèse : en-tête au 29/10, retour du formateur du 28/10 et suite donnée sur la
  ligne C1 (colonnes E et F), formules recalculées dans Excel. Grille complète, grilles E1 et E3 : en-têtes au
  29/10 et demande du budget sur la ligne C1.
- **Manque trouvé** : le classeur détaillé envoyé le 28/10 n'a aucune rédaction pour C10 et C11 et cite le rapport E3
  v1.5 pour C9, C12 et C13. Les statuts, eux, étaient justes.
- **État mesuré des autres livrables** : E2 en version 0.3 (`docs/rapports/E2/rapport-E2.md`, dernier changement le
  09/10) ; E4 sans rapport (`docs/PLAN-E4-rapport.md` ; recomptage refait le 30/10, `docs/rapports/E4/recomptage-criteres-2026-10-30.md` : 30 ✅, 6 ⚠️, 0 ❌, questions du §6 à trancher par Era) ; E5 sans rapport. Tous dus le 05/11.

**Fait le 28/10** :

- **Versions envoyées, à côté des originaux** (commit `8b118b4`) : `rapport-E1-v3-avec-annexes.pdf` (10 pages : le
  livret du tag `livrable-E1-v3`, seize liens essentiels vers ce tag, l'erratum de la page 6 et les annexes de schémas
  C1, C2, C3, C5) et `rapport-E3-v1.9-bandeau.pdf` (20 pages : le texte et les liens du tag `livrable-E3-v2`, avec un
  bandeau en page 1). `rapport-E1.pdf` et `rapport-E3.pdf` restent ceux de `scripts/rendre_pdf.py`.
- **Schémas d'annexe d'E1** : C2 (requêtes) et C5 (API) créés, C3 remis à la forme de C1, relecture croisée appliquée
  (`docs/rapports/E1/schemas/`, `tests/test_schemas_e1.py`, commits `8e9713b` et `a034adb`).
- **Budget (C1)** : demandé par le formateur le 28/10. Décision d'Era : pas de TJM, seulement l'argent dépensé, en
  trois lignes dans le livret v4 (« Budget financier », « Fonctionnement », « Contraintes »). Le livret v3 dit
  « budget 0 € », faux depuis que le serveur est payé : le critère C1 « présentation complète » passe partiel dans
  les classeurs (E1 : 27 ✅ · 1 🟡 ; total 111 · 25 · 1, branche `classeur-competences`, commit `c56b899`).
- **Google News** : reste arrêté (décision d'Era du 28/10), remplacement toujours sur la carte #81.

**À connaître pour l'oral, sans réécrire les tags** : erratum d'E1 page 6 (0,12 ms est la sous-requête corrélée,
LATERAL mesure 0,24 ms ; la colonne « Portefeuille » porte sur les 111 valeurs ; la moyenne des volumes porte sur les
20 séances précédentes). Rapport E3 : « deux garde-fous » sous 85 % alors que trois contrôles le sont (deux portes
`xfail`, la fuite n'a pas de seuil de blocage), p. 13 ; « la trace ne change pas » vaut pour un scénario fixé, p. 12 ;
« le livrable gelé » désigne encore `livrable-E3-v1`, et « les mesures portent sur `9683f04` » est trop large, p. 16 ;
le lien « tag du livrable » ouvre le guide du jury, p. 1. Relevées le 29/10 avant l'envoi, vérifiées dans le code du
tag : « chaque appel à /briefing produit une trace » ne vaut que pour un appel admis, traçage actif (les refus 403,
422 et 429 passent avant `traces.briefing`, `api/main.py` l. 281 à 302), p. 7 ; `request_id` n'est pas « dans chaque
ligne de journal » : 13 appels de journal sur 23 le portent, sans filtre de journalisation, p. 9 ; « formateur et jury
invités » : au 29/10, seul le formateur (`bybysker`, lecture) est collaborateur, p. 1. À corriger dans une version
suivante.

**Ne rien fusionner dans `main` le matin du 30/10** : une fusion relance la production. Le 27/10 : PR #164 à #167
fusionnées, les deux livraisons de tag vertes, `/health` de production annonce `d3a4198`, construit le 27/10 à
10 h 46 UTC.

**Fait le 27/10 après-midi, en production** (en préparant la démonstration d'E3, le briefing annonçait des cours vieux
de 70 jours) :

- cours et taux rattrapés à la main sur le serveur par Era, dans un conteneur jetable de l'image en service : 5 508
  cotations écrites, 280 518 lignes, dernière séance passée du 18/08 au 27/10 ; 255 taux écrits, les cinq devises au
  27/10 ; `ANALYZE` passé. Commandes et résultats : `docs/exploitation.md#rattrapage-cours-production` ;
- articles réingérés par le workflow « Ingestion » (passage `40534178721`, vert) : `/health` annonce l'index
  `55d25de6…`, 2 166 articles, construit le 27/10 à 15 h 48 UTC ;
- démonstrations d'E3 enregistrées après coup, vers 17 h 02 : briefing MC.PA en 8 s sans avertissement de retard,
  question d'achat refusée avant le modèle, trace Langfuse `8951d65c…` (7,18 s, 987 jetons).

**Manque connu, toujours ouvert** : sur le serveur, aucune collecte planifiée des cours ni des taux. Ce fichier le
signalait déjà le 24/08 (5 jours de retard), le 06/09 (18 jours) et le 18/09 (environ 30 jours, « automatiser (`cron`
serveur) ») ; l'ingestion du sprint 3 n'a ajouté que les articles (`deploy/deployer.py:525`, `--etapes rss`). Le
27/10, le retard atteignait 70 jours. À traiter après l'oral blanc, sans rien fusionner dans `main` avant vendredi.

*Avant le 27/10 à midi, cette section disait : pousser la branche, PR vers `develop`, puis `develop` vers `main`,
poser les tags et envoyer les liens. Le 27/10 à midi : envoyer le message des liens, puis répéter.*

- **E3 v1.9** (20 pages) : première page avec logo, encadré « En une minute » et sommaire cliquable dont les numéros
  sont lus dans le PDF (`scripts/rendre_pdf.py`, `tests/test_rapport_e3_sommaire.py`) ; chaque compétence part de son
  cas d'usage ; grille **34 ✅ · 5 🟠 · 0 🔴**, validée par Era le 27/10.
- **E1 v3** (5 pages) : le livret, rendu depuis `docs/rapports/E1/rapport-E1.html` (texte identique, page par page, au
  PDF approuvé du 26/10).
- **À confirmer par Era** : figures d'E3 à 85 % de la largeur (plus petit texte 4,3 points au lieu de 5).
- **Verrou** : la question « l'annexe d'E1 compte-t-elle dans les 5 pages ? » reste à poser au formateur. Le budget de
  GitHub Actions ne bloque plus : les passages du 27/10 ont tourné (livraisons des deux tags, ingestion `40534178721`).

---

## ▶️ SPRINT 5 : LIVRABLE EN VERSION 5 (26/10) ; TAG `livrable-sprint-5-v5` À POSER APRÈS LA LIVRAISON SUIVANTE

**Pourquoi** : le tableau de bord de production demande la clé d'API, que le formateur n'a pas ; le § 5.6 ne donnait
que les liens des captures (un clic, et l'accès au dépôt privé, pour les voir). Era a demandé qu'elles soient dans le
livrable.

**Fait** (branche `sprint-5-livrable-v5`, partie de `develop` à `9c7a88c`) : tests rouges d'abord
(`tests/test_livrable_sprint5_doc.py` : le § 5.6 affiche les quatre captures dans l'ordre, le livrable annonce sa
version 5, la synthèse renvoie au tag v5) ; § 5.6 : les quatre captures de la copie (22/10) affichées, chacune avec
sa légende ; synthèse : la capture de l'attaque simulée au § 5 ; chapeau « Version 5 (26/10) » et chronologie ; PDF
refaits, liens vers le tag v5. Le contenu technique ne change pas.

**▶️ Prochaine action** : PR vers `develop`, puis `develop` vers `main` (fusions par Era), livraison, puis le tag
`livrable-sprint-5-v5` sur le SHA complet du commit de livraison, après `/health` confirmé. Les tags v1 à v4 restent figés.

---

## SPRINT 5 : LIVRABLE EN VERSION 4 (26/10) ; TAG `livrable-sprint-5-v4` POSÉ SUR `4144437` (LIVRAISON 40311127749)

**Pourquoi** : pour que le formateur comprenne le sprint d'un coup d'œil, Era a demandé une synthèse plus claire et le
schéma de la vigie dans le livrable complet, qui n'en avait pas.

**Fait** (branche `sprint-5-livrable-v4`, partie de `develop` à `7912598`) : tests rouges d'abord
(`tests/test_livrable_sprint5_doc.py` : le livrable annonce sa version 4 et montre le schéma au § 1.4, la synthèse
renvoie au tag v4, chaque image citée existe) ; schéma `docs/sprint-5/schemas/RITA-sprint5-vigie.png` (et `.svg`),
même contenu que celui de la vidéo, mis en forme par Era ; synthèse réécrite (l'essentiel en une minute, avant et
après, conception, parcours prouvé, critères, mesures, ce qui n'est pas fait) ; chapeau « Version 4 (26/10) » et ligne
du 26/10 dans la chronologie ; PDF du livrable et de la synthèse refaits, liens vers le tag v4. Le contenu technique ne
change pas.

**Fait ensuite** : PR #157 et #158 fusionnées par Era, livraison 40311127749, tag `livrable-sprint-5-v4` posé par Era
sur `4144437784672050b2394ec3562e49bf55ee8dac`, passage du tag 40312938338 vert, image publiée.

---

## SPRINT 5 : LIVRABLE EN VERSION 3 (26/10) ; TAG `livrable-sprint-5-v3` POSÉ SUR `bea3e64` (LIVRAISON 40298405201)

**Pourquoi** : Era a expliqué au formateur que le sprint a d'abord été fait sur la copie locale, puis mis en
production ; le livrable le disait au milieu du § 1.2, sans chronologie, et la discussion n'était pas consignée.

**Fait** (branche `sprint-5-livrable-v3`, partie de `develop` à `f897ec5`) : tests rouges d'abord
(`tests/test_livrable_sprint5_doc.py` : la chronologie va de la copie locale à la production, le § 6 consigne la
discussion) ; § 1.2 : un tableau « La chronologie : d'abord la copie locale, puis la production » (22/10, 23/10 matin,
23/10 soir, 25/10), chaque ligne renvoyant à sa preuve ; § 6 : l'entrée « Discussion avec le formateur » ; chapeau
« Version 3 (26/10) » ; PDF refait (14 pages, liens vers le tag v3). Le contenu technique ne change pas.

**Fait ensuite** : PR #155 et #156 fusionnées par Era, livraison 40298405201, tag `livrable-sprint-5-v3` posé sur
`bea3e641bf99b67933410017eddec2b412aa6f75`, passage du tag 40299791564 vert.

---

## ▶️ SPRINT 5 : LIVRABLE EN VERSION 2 (25/10) ; TAG `livrable-sprint-5-v2` À POSER APRÈS LA LIVRAISON SUIVANTE

**Pourquoi** : à la page 11 du PDF du livrable, une phrase du § 5.12 s'affichait en titre de 21 points (« #130). L'API de
Langfuse l'a confirmé… ») : la ligne 305 du `.md` commençait par `#130)`, et Markdown lit un `#` en début de ligne
comme un titre. Trouvé le 25/10 en préparant la vidéo du sprint 5.

**Fait** (branche `sprint-5-livrable-v2`, partie de `develop` à `076471e`) : test rouge d'abord
(`tests/test_livrable_sprint5_doc.py` : aucune ligne des documents du sprint 5 qui partent en PDF ne commence par
« #<chiffre> » ; le livrable annonce sa version 2) ; ligne corrigée (« (issue #130) » sur la même ligne) ; chapeau
« Version 2 (25/10) » ; PDF refait avec la chaîne style maison, liens vers le tag `livrable-sprint-5-v2`, 14 pages.
Mesure : 3 morceaux de texte de plus de 15 points hors couverture en version 1, 0 en version 2. Le contenu ne change
pas ; la synthèse, le scénario et la doc d'exploitation ne changent pas.

**▶️ Prochaine action** :
1. PR `sprint-5-livrable-v2` vers `develop`, puis `develop` vers `main` (fusions par Era) : livraison suivante,
   documents seulement.
2. Era pose `livrable-sprint-5-v2` sur le SHA complet du commit de cette livraison, après `/health` confirmé ; le tag
   v1 reste figé.
3. Toujours ouverte : la grille de l'atelier 5 (`D:\KandaWork\RITA_PROJECT\transferts\sprint-5\grille-atelier-5-a-remplir.md`).

---

## ▶️ E1 v2.6 ET E3 v1.5 GELÉS (24/10, 19 h 05) : TAGS `livrable-E1-v2` ET `livrable-E3-v1` ; RESTE L'ENVOI

**Fait** : PR #149 (`develop` vers `main`) fusionnée par Era à 18 h 39, après six contrôles verts et deux revues automatisées sans remarque (Claude, Codex). Livraison N19 : passage 40112605750, de la fusion au service en 11 min 39 s ; `/health` annonce `312056a` (construit à 18 h 43) ; le contrat OpenAPI servi annonce `X-Cle-Exercice` sur `/exercice/*` ; 403 sans clé sur `/donnees/valeurs`, `/sante` et `/question` (lu à 19 h 05). Definition of Done des deux tags sur `312056a`, arbre propre compris : verte. Tags annotés posés par Era à 19 h 05, tous deux sur `312056a` (vérifié par `gh api`) ; leurs passages ont publié `ghcr.io/ganda15/rita-api:livrable-E1-v2` et `:livrable-E3-v1`. Liens de tout le dépôt sur ce commit : deux signalés (Wikipédia 403, guide de l'ANSSI hors délai), tous deux revus à 200, puis 0 cassé. Lignes 5 et 6 de `docs/FILE-DE-VALIDATION.md`.

**Fait depuis** : PR #150 fusionnée par Era à 19 h 37 (`0214c76`), lignes 5 et 6 de la file dans `develop`, CI de la PR verte (1760 passés, 30 ignorés, 2 échecs attendus, couverture 96,32 % ; portes 16 passés). Deux messages rédigés depuis le gabarit de la file, un par livrable, avec le lien du tag. Pièces jointes vérifiées : les PDF de OneDrive ont la même empreinte git que ceux des tags (E1 `cf15a52`, E3 `64e05e6`). Accès vérifié : `bybysker` en lecture, aucune invitation en attente ; `docs/PILOTAGE-AGILE.md` le nomme formateur, et le message 1 lui demande de confirmer que c'est son compte (question ouverte depuis le 12/10). Journal 034 et notes d'étude anglaises du gel écrits dans Obsidian.

**Reste** : **Era envoie** le message 1 (E1), puis le message 2 (E3), un à la fois (règle de la file ; proposé : E3 le 26/10, trois jours avant l'oral blanc) ; à chaque envoi, la colonne « Envoyé le » de la file et l'entrée « livrable envoyé » du `CHANGELOG`. Décisions d'Era : périmètre de `.coveragerc`, erratum du README de preuve du sprint 4, carte #75. Ensuite : copie anglaise d'E3 v1.5, `oral-E1-v3` remis aux faits du 24/10, oral E3.

## ▶️ E3 v1.5 (24/10) : FUSIONNÉE DANS `develop` (HISTORIQUE DU 24/10, 18 h 15)

**Fait** : PR #146 fusionnée par Era à 18 h 02 dans `develop` (commit de fusion `caf87a7`, sept commits de travail).
E3 v1.5 : 19 pages (limite : 20), numérotées ; corrections de faits et ce que C9 à C13 exigent, rien de nouveau. Copie
de lecture : `C:\Users\kanda\OneDrive\RITA\reports\rapport-E3-2026-10-24-v1.5.pdf`.

- **Faits mis à jour** : 19 chemins et deux clés ; 422 pour une valeur inconnue, 502 encore possible si le graphe
  échoue ; limite de débit, partielle ; cinq écrans, onze chemins appelés ; production tracée depuis le 21/10, sans
  texte ; coût distingué par parcours ; sept workflows, six checks requis, livraison après fusion, retour arrière répété
  le 14 et le 15/10. Chaque mesure avec sa branche, son commit et son passage de CI.
- **Éléments des sprints repris** : la liste donnée à Era le 24/10 (parcours des questions, limite de débit, 422, trois
  garde-fous, traçage de production, livraison automatique et retour arrière, `/sante` et le tableau de bord en une
  ligne chacun, la fausse alerte #130), écrite dans la description de la PR #146.
- **Schémas** : à l'état du 24/10 ; les images publiées sont la mise en forme d'Era (`E3-<nom>-illustre.svg`), texte
  imprimé de 6 à 6,9 points (4,2 dans la v1.4). `tests/test_schemas_e3.py` (41 tests, 20 rouges avant les sources)
  compare chaque texte au générateur ; il a retrouvé l'erreur « 6 h à 9 h » d'une première mise en forme, réintroduite
  exprès.
- **Deux relectures externes, vérifiées point par point** : celle du plan (quatre erreurs de mon plan, corrigées) et
  celle du PDF (huit corrections de faits, chacune confirmée dans sa source avant d'être appliquée ; le 21/10, par
  exemple, 8 réponses et 7 abstentions, et non 9 et 6).
- **Preuve rangée le jour même** : `evidence/C12/preuve-ci-develop-2026-10-24.md` (passage 40101793487).

**Vérifié** : CI de la PR #146 : 1760 passed, 30 skipped, 2 xfailed, couverture 96,32 %, porte de livraison
« livrable ». Grille d'E3 : 36 ✅ · 3 🟠 · 0 🔴 sur 39 lignes, une auto-évaluation.

**Trouvé, à décider par Era** :
1. `.coveragerc` ne mesure pas `rag/`, `monitorage/` ni `passerelle_mcp/` : 98 % mesurés à part le 24/10, sans toucher
   au fichier (zone sous garde). Les ajouter à la liste `source`, ou le laisser écrit comme limite.
2. `evidence/sprint-4/README.md` dit « les neuf réponses » au 21/10 ; le JSON du même jour en compte huit. Un erratum
   daté sous la ligne (ligne d'origine gardée), ou rien.
3. Carte #75, point S10 : le certificat de production a été renouvelé seul le 19/10, valable jusqu'au 17/01/2027 (lu
   le 24/10) ; le point peut être fermé.

**Points ouverts** :
1. Les tags `livrable-E1-v2` et `livrable-E3-v1` : après la PR `develop` vers `main` (sept PR d'avance, #140 à #146),
   chacun cité dans `ETAT.md` et `CHANGELOG.md` avant d'être posé (la porte de livraison le vérifie).
2. La copie anglaise d'E3 (`-EN.md`, `-EN.pdf`) dans `OneDrive\RITA\reports`, sur le texte fusionné.
3. `oral-E1-v3` (Obsidian `03-Oraux`) cite encore les chiffres d'avant ; l'oral d'E3 reste à préparer.
4. Notes d'apprentissage écrites (Obsidian `09-EN-personnel`) : SUMMARY et STUDY d'E3 v1.5.

**▶️ Prochaine action** :
1. PR `develop` vers `main`, relue par `revue` ; sa fusion lance la livraison N19 (documents, tests, et la description
   OpenAPI corrigée dans `api/`).
2. Fait le 24/10 à 18 h 30 : l'entrée du `CHANGELOG` qui cite les deux tags (`ETAT.md` les cite déjà). Restent les
   tags sur `main`, posés par Era après la Definition of Done verte, puis le lien du tag envoyé et la ligne de
   `docs/FILE-DE-VALIDATION.md`.
3. E4, E5 et la fin d'E2 avant le 05/11.

---

## ▶️ DOCUMENTS DE RÉFÉRENCE (24/10) : LIENS, CI-CD, ARCHITECTURE, CONTRAT OPENAPI, RETOUR ARRIÈRE DE PRODUCTION

**Fait**, deux PR fusionnées par Era dans `develop` :

- **PR #143** (fusionnée à 15 h 55, commit `7965ff7`) : `scripts/verifier_liens.py` vérifie par `gh api` chaque forme de
  lien du dépôt privé (fichier à une référence, PR, issue, passage de CI, workflow, commit). Une forme inconnue reste
  « non vérifiable », jamais « bonne ». 14 tests, dont 12 rouges avant le code. Les 116 faux « cassés » ne bloquent plus
  les tags E1 et E3.
- **PR #144** (fusionnée à 16 h 00, commits `4878eb2` et `9ce8b57`) : `docs/CI-CD.md` (sept workflows, six checks
  requis, déploiement après fusion, secrets `DEPLOY_*` de l'environnement `production`), `docs/ARCHITECTURE.md`
  (19 chemins, deux clés, question, vigie, déploiement), description OpenAPI de `api/main.py`, et dans
  `docs/exploitation.md` (annexes, § 8) le retour arrière de la production et la mise à jour du script du serveur.

**Deux défauts trouvés en relisant** :
1. Le contrat publié se trompait : les deux clés portaient le nom de schéma par défaut, et `/docs` annonçait
   `X-API-Key` sur `/exercice/*`, alors que le code y lit `X-Cle-Exercice`. Corrigé (`scheme_name="CleExercice"`), test
   écrit d'abord et vu rouge.
2. Documenté mais absent : le retour arrière de la production (répété le 14/10 et le 15/10) et la mise à jour du script
   du serveur étaient annoncés par `retour-arriere.yml`, l'action `ordre-serveur`, `docs/CHAINE-V1.md` et
   `docs/CADRAGE-V1.md` (critère 2 du sprint 2), sans avoir jamais été écrits, même avant le sprint 5. Écrits à partir
   des deux répétitions ; deux tests de la page, rouges sur l'ancienne version.

**Vérifié le 24/10** : sur le poste, 1695 passed, 40 skipped, 2 xfailed, `ruff` sans remarque. CI de la PR #144 : 1705
passed, 30 skipped, 2 xfailed, couverture 96,32 %, porte de livraison « livrable ». Sur `develop` après les deux fusions
(`9eead32`) : `scripts/verifier_liens.py` sur tout le dépôt, 249 liens internes et 275 externes, **0 cassé** ; Tests
verts. 1751 tests collectés à 16 h 30 (E1 v2.6 en cite 1 732, mesurés avant ces deux PR).

**Points ouverts** :
1. Le secours du retour arrière sans GitHub n'a jamais été exécuté (la page le dit) : à essayer une fois, avec Era.
2. `deploy/deployer.py` renvoie encore à `docs/EXPLOITATION.md` dans deux messages ; le modifier changerait son empreinte
   et bloquerait les livraisons jusqu'à sa réinstallation. À corriger la prochaine fois que ce script change.
3. `docs/EXPLOITATION.pdf` date du 11/10 : il ne correspond plus à la page.
4. Fait le 24/10 (PR #146) : schémas et chiffres d'E3 remis à jour, section ci-dessus.
5. Notes d'apprentissage écrites (Obsidian `09-EN-personnel`) : SUMMARY et STUDY du vérificateur de liens et des
   documents de référence.

**Suite** : E3 v1.5 est faite (section ci-dessus) ; la prochaine action y est écrite.

---

## ▶️ E1 v2.6 (24/10) : PRÊTE SUR `develop`, PAS ENCORE GELÉE

**Fait** : E1 v2.6, corrections de faits seulement, toujours 5 pages (limite officielle d'E1 : 2 à 5). PR #141 fusionnée
par Era à 14 h 17 dans `develop` (commit de fusion `9d52db9`, commit du travail `d9adfe9`). CI de la PR : 1701 passed,
30 skipped, 2 xfailed, couverture 96,32 %. Copies de lecture : `C:\Users\kanda\OneDrive\RITA\reports\rapport-E1-2026-10-24.pdf`,
`-EN.md` et `-EN.pdf`.

- **Faits mis à jour** : 1 732 tests ; 19 chemins OpenAPI et l'historique complet par pages (C5) ; registre T1 à T8 et
  corpus ; Google News arrêté le 16/10 ; 108 valeurs actives ; 21 soirs sur 21 du 03 au 23/10 ; `docs/exploitation.md`.
- **Limites écrites** : PRU dans une autre devise que la cotation, fichier de positions partiel, corpus sans durée de
  conservation, rôle `rita_ingestion` hors de `db/roles.sql`.
- **Relecture externe** vérifiée point par point : six remarques confirmées, une corrigée (l'analyse ouverte est l'AITD,
  pas l'AIPD, que le registre dit non requise), une sans objet. Une erreur venait de mon raccourcissement (« porteurs
  d'injection ») : corrigée en « bloqués par le garde-fou ».
- **MCD** : identifiants soulignés, `id` de POSITION, identification relative `(1,1)`, attributs de liaison retirés.
  Erratum daté dans `evidence/C4/preuve-mcd-merise.md` (ligne d'origine gardée).
- **Schéma C1** : PNG rendu depuis la mise en forme illustrée fournie par Era (`E1-collecte-illustre.html`) ; le test
  `test_le_schema_illustre_dit_exactement_ce_que_dit_le_schema_genere` garde ses textes égaux au schéma généré (rouge
  sur deux textes de la maquette avant correction).

**Points ouverts** :
1. Le tag `livrable-E1-v2` exige que `develop` arrive sur `main` (cinq PR d'avance le 24/10 à 16 h 30, #140 à #144).
   Fait le 24/10 : `scripts/verifier_liens.py` ne bloque plus (PR #143, section ci-dessus).
2. Le texte d'oral `oral-E1-v3` (Obsidian `03-Oraux`, 11/10) cite encore les chiffres d'avant : à reprendre avant
   l'oral blanc 1.
3. Pas d'entrée au `CHANGELOG` pour E1 v2.6 : manques découverts (formalisme du MCD, règle fausse dans `evidence/C4`),
   à consigner si Era le décide.

**Suite** : le vérificateur de liens et les documents de référence sont faits (section ci-dessus) ; la prochaine action
est écrite dans cette section.

---

## ▶️ LIVRAISON N18 (24/10) : QUATRE CORRECTIFS EN PRODUCTION

**Ce qui s'est passé** : le 23/10 au soir, E1 et E3 ont été relus ligne par ligne contre le code de `main`. Quatre
défauts de code en sont sortis, aucun visible dans les données de production. Era a décidé de les corriger avant de
reprendre les rapports ; chacun a son test écrit d'abord et vu rouge (21 tests, dont 15 rouges avant le code).

| Correctif | Ce qui change | Critère |
|---|---|---|
| C, `8d27985` | Une panne totale des cotations, des flux RSS ou du scraping est un échec déclaré (même règle que la BCE, carte #55) ; un succès partiel et un week-end sans séance restent des succès | C1, C20 |
| E, `67fba96` | `/donnees/cotations` accepte `jusqu_a` : les dix ans de cours se lisent par pages de 1 000, sans trou ni doublon ; intervalle inversé = 422 | C5 |
| D, `ff73f3c` | Le lecteur de positions rejette NaN et l'infini (« quantite illisible », « prix de revient absent ou illisible ») | C3 |
| F, `2c89cfe` | La migration « taux » et le guide disent qu'elle se joue avant la migration de la clôture | C4 |

**Livré** : PR #138 (vers `develop`, fusionnée à 11 h 18) et PR #139 (`develop` vers `main`, fusionnée à 11 h 48), par
Era. Livraison N18 : passage 40083432816, de 11 h 48 à 11 h 57 (heure de Paris), commit
`b547cbf7d46bc45d2ffbb85a0740449a8b96fe2a`. CI sur la PR et sur `main` : 1700 passed, 30 skipped, 2 xfailed, couverture
96,32 % ; revue automatisée sans remarque. En production (lu à 12 h 09) : `/health` annonce `b547cbf`, index reconstruit
(2140 articles), 403 sans clé sur `/donnees/valeurs`, `/sante` et `/donnees/cotations`, l'OpenAPI servi a 19 chemins et
`jusqu_a`. **Non vérifié** : un appel réel avec `jusqu_a` (il faut la clé de production).

**Manque découvert, la sauvegarde** : le dernier dump date du 27/09 (`D:\KandaWork\RITA_PROJECT\sauvegardes\`), le dump
hebdomadaire prévu n'est pas tenu, et la ligne « Sauvegarde restaurable : VALIDÉ » de `CONTINUITE.md` s'appuie sur
`pg_restore --list`, qui liste l'archive sans la restaurer. Un dump a été rechargé une fois, le 20/08, pour migrer le
serveur. À faire : un dump, puis une vraie restauration dans une base jetable (preuve E5, C21), et corriger la ligne de
`CONTINUITE.md`.

**Points ouverts** :
1. Fait le 24/10 : Era a mis à jour le dossier d'origine `D:\KandaWork\RITA_PROJECT\rita-agent` à `b547cbf` (vérifié à
   13 h) ; la collecte du soir tourne avec le correctif C à partir du 24/10. Son manifeste reste à relire.
2. Fait le 24/10 dans E1 v2.6 : les limites (devise du PRU, fichier de positions partiel) sont écrites.
3. Décisions d'Era encore ouvertes sur E1 et E3 : le rôle `rita_ingestion` absent de `db/roles.sql`, le défaut #73 (clé
   mémorisée trop tôt, écrans du briefing et des questions), les en-têtes de sécurité (OWASP API8).
4. La grille de l'atelier 5 (voir le sprint 5 ci-dessous). La PR #88 (`mistral-ue`) reste ouverte, en conflit.
5. Fait le 24/10 (PR #143) : le script vérifie ces liens par `gh api`, 0 cassé sur tout le dépôt. Constat d'origine :
   `scripts/verifier_liens.py` (24/10, sur `develop`) : 116 liens « cassés », tous du même type, « HTTP 404 (dépôt privé,
   forme d'URL non vérifiable par gh) », dans les livrables des sprints 2 à 5, `evidence/sprint-5/` et
   `docs/veille/_candidats-2026-S41.md` ; aucun dans `ETAT.md` ni le `CHANGELOG`. La règle « zéro lien cassé » bloquera
   les tags E1 et E3 : apprendre au script ces formes d'URL, ou les remplacer, avant le gel.

**Suite** : E1 v2.6 est faite (section ci-dessus) ; la prochaine action est écrite dans cette section.

---

## ▶️ SPRINT 5 : LA VIGIE ET LA DÉMO, EN PRODUCTION (N16, N17) ; TAG `livrable-sprint-5-v1` POSÉ LE 23/10 ; RESTE L'ATELIER 5

**Mise à jour du 23/10, 20 h** : **sprint 5 remis.** PR #135 (documents vers `develop`) et PR #136 (`develop` vers
`main`) fusionnées par Era ; livraison N17 réussie (passage 39995996403, 19:33 à 19:43), commit
`d215617f7cffa7a9817da28f2b2684dc7c63f7cd` : `/health` l'annonce, le tableau de bord répond 200, `/sante` exige la clé.
Tag `livrable-sprint-5-v1` posé par Era sur ce SHA complet (19:45:28) ; passage du tag 39997640785 réussi, Definition of
Done verte en CI, image `ghcr.io/ganda15/rita-api:livrable-sprint-5-v1` publiée. Les 46 liens des quatre PDF du tag
vérifiés (37 cibles dans le tag, 5 liens publics à 200, 4 issues et PR existantes). Incident de la soirée : GitHub
Actions bloqué de 18:49 à 19:10 par le budget Actions à 0 $ (dépôt privé, quota gratuit d'octobre épuisé) ; Era a
porté le budget à 5 $. Preuve : `evidence/sprint-5/production-2026-10-23.md` § 6 et 7.

**Mise à jour du 23/10, soir** : **le sprint 5 est en production.** PR #133 (`sprint-5-vigie-demo` vers `develop`) et
PR #134 (`develop` vers `main`) fusionnées par Era ; livraison N16 réussie (passage 39983152061, 18:00 à 18:12). En
production : `/health` annonce `845e3b3`, le tableau de bord répond, `/sante` exige la clé (la clé de production ne vit
que dans le `.env` du serveur). Preuve : `evidence/sprint-5/production-2026-10-23.md`.

**Cadre** : construit sans toucher l'original, dans le dossier `D:\KandaWork\RITA_PROJECT\rita-agent-sprint-5`, branche
`sprint-5-vigie-demo` (partie de `main` à `3c35398`), puis livré par le chemin habituel. La copie de RITA sur le poste
(projet Docker `rita-s5`, `http://localhost:8011`) reste le lieu des exercices de panne.

**Fait et prouvé** (étapes 1 à 11, et 13) : compteurs, signaux et `/sante`, seuils et prix, vigie, tableau de bord,
panne et dérive simulées, critère 1 du contrat dans le code, copie du poste, `docs/exploitation.md`, preuves sur la
copie en marche (issues #127 et #128 ouvertes puis fermées par la vigie), scénario `docs/sprint-5/DEMO.md`. Suite :
1680 passés ; neuf modules du sprint couverts à 100 %. Livrable et synthèse : `docs/sprint-5/livrable/`. Preuves :
`evidence/sprint-5/README.md`.

**État de la copie (23/10, midi)** : version `648293f`, précédente `d43a01e`, aucun exercice en cours, aucune issue de
la vigie ouverte ; traces Langfuse dans le projet propre à la copie (`rita-copie-sprint5`) ; la démonstration de
l'atelier 2 est arrêtée (port 8011).

**Fait le 23/10** : étape 12 (doc suivie à la lettre, dix trous corrigés), étape 13 (deux répétitions, environ 9 min et
9 min 30), fausse alerte de production #130 expliquée et fermée, livrable mis à jour
(`evidence/sprint-5/test-doc-et-repetitions-2026-10-23.md`).

**▶️ Prochaine action** :
1. Fait le 23/10 au soir : livraison N17 et tag `livrable-sprint-5-v1` (voir la mise à jour de 20 h ci-dessus).
2. Fait le 24/10 : ce commit de mise à jour (ETAT, CHANGELOG, preuves) part vers `develop` avec la PR qui consigne N18 ;
   il ne change pas le tag.
3. La grille de l'atelier 5 remplie par le binôme (`D:\KandaWork\RITA_PROJECT\transferts\sprint-5\grille-atelier-5-a-remplir.md`),
   puis versée dans `eval/ateliers/sprint-5-grille.md` (version suivante du livrable).

---

## ▶️ SPRINT 4 : LIVRABLE EN VERSION 3 (21/10/2026) ; TAG `livrable-sprint-4-v3` À POSER, PUIS L'ATELIER 4

**Mise à jour du 21/10, 22 h 20** : relecture finale de la version 2 : un lien de ligne décalé (`nombres.py`, 67 au lieu de 68) et l'état de la production arrêté à N12. La version 3 les corrige ; elle part par une PR vers `develop`, puis par la livraison N15 ; Era pose `livrable-sprint-4-v3` sur le commit de N15, désigné par son SHA complet.

**Mise à jour du 21/10, 21 h 40** : **le sprint 4 est remis.** N14 est en production depuis 21 h 24 (commit `81a9718`, PR #124, passage `39659810301`). Era a posé le tag `livrable-sprint-4-v2` à 21 h 25 sur `81a9718c528cea18ad533aae5fd3c2ffd1ea5e49` ; sa livraison (passage `39661606759`) a passé la Definition of Done et publié l'image `livrable-sprint-4-v2`. Les 49 liens du livrable et de la synthèse répondent au tag. Restent : l'atelier 4 (date à demander) et sa grille `eval/ateliers/sprint-4-grille.md` ; les points ouverts du point 4 ci-dessous.

**Mise à jour du 21/10, 21 h 15** : N13 est en production depuis 20 h 49 (commit `ce5b2c7`, PR #122, passage `39654392710`). Le tag `livrable-sprint-4-v1` a été posé à 20 h 30, avant la fusion de la PR #122 : il désigne N12 (`27e41d3`). Sa livraison a été refusée par la Definition of Done (tag absent du CHANGELOG de N12), et la règle du dépôt interdit de le supprimer ou de le déplacer. La remise passe donc au tag `livrable-sprint-4-v2` : les liens des documents le visent, la branche du sprint part par une PR vers `develop`, puis par la livraison N14 ; Era pose le tag v2 sur le commit de N14, désigné par son SHA complet.

**Mise à jour du 21/10, 20 h 15** : le livrable en version 1 (16 pages) et la synthèse (4 pages) sont relus et validés par Era. Depuis N12, la branche du sprint porte six commits de documents, aucun de code : les preuves de N12 (`b99d246`), le livrable corrigé après relecture (`12ffef4`), la synthèse (`137d258`), le schéma complet (`37db21e`, `58300dd`), le journal des retours de l'atelier 3 complété (`f054f5f`, neuf retours), puis l'entrée du CHANGELOG qui cite le tag `livrable-sprint-4-v1`. Ils partent par une PR vers `develop`, puis par la livraison N13 (`develop` vers `main`) ; le tag se pose sur `main` après N13.

**Mise à jour du 21/10, 13 h 20** : N12 est en production depuis 12 h 47 : commit `27e41d3` (fusion de la PR #120),
index `35806d6e…`, 2140 articles, même empreinte de contenu. Elle apporte le livrable en version 1, les quatre
apostrophes du contrôle des nombres et **le traçage Langfuse en production** : Era a posé les clés dans le `.env` du
serveur (vérifié sans afficher de valeur, `200` de l'API Langfuse), la livraison l'a copié. Rejeu après N12 : 5 sur 5.
La trace du briefing OR.PA (`7da0ec8c…`) ne garde ni prompt ni réponse, sur la racine comme sur la génération :
**CA3.6 prouvé en production** (`evidence/sprint-4/README.md`, section « La livraison N12 », deux captures). Ce qui
suit, jusqu'à « Ordre de la suite », décrit l'état de 11 h 20.

**Où on en est** : N11 est en production depuis le 21/10 à 11 h 05 : commit `4fc63f5` (fusion de la PR #115), index
`98ea614a…`, 2140 articles, même empreinte de contenu `fd8542955c1b…`. Elle apporte le contrôle des nombres
(`guardrails/nombres.py`, motif `NOMBRE_NON_SOURCE`) et l'image de base tirée de `mirror.gcr.io`. Livraison réussie du
premier coup (passage `39572719574`), sans refus du registre d'images.

**Rejeu en production** (21/10, 11 h 11 et 11 h 12, deux lancements) : 5 appels conformes sur 5, deux fois ; Q4 rend
« 1 000 postes ». Rapports `evidence/sprint-4/rejeu-production-2026-10-21-111136.json` et `-111201.json`. La clé se
charge sans affichage : `$env:RITA_API_KEY = ssh root@178.104.184.125 "sed -n 's/^RITA_API_KEY=//p' /root/rita-agent/.env"`,
puis `Remove-Item Env:RITA_API_KEY` après le rejeu.

**Revues du jour** : 10 points relevés par Codex (PR #114 à #117) et par la revue de sécurité automatique ; 9 corrigés
avec un test rouge d'abord, 1 écrit comme limite. Tableau dans `evidence/sprint-4/README.md`. Suite locale : 1402
passed, 24 skipped, 2 xfailed.

**PR du jour** : #118, #119 (vers `develop`) et #120 (vers `main`, N12) fusionnées ; rien en attente.

**Ordre de la suite** :
1. Fait : PR #118, #119 et #120 fusionnées, N12 en production.
2. Fait : CA3.6 prouvé en production le 21/10 (traçage activé par N12, trace `7da0ec8c…` sans prompt ni réponse) ;
   registre RGPD (T3, T6, T8) et contrat remis d'accord. À relire encore : les documents antérieurs qui parlent de
   Langfuse sans dire « en local » (`docs/EXPLOITATION.md`, `docs/ARCHITECTURE.md`, rapport E2) ; pour E3, gelé, un
   erratum éventuel (décision d'Era). Les clés Langfuse du poste : vérifier qu'elles visent le projet `rita-dev` et non
   celui de production (décision d'Era du 02/10).
3. D3 : livrable version 1 (`docs/sprint-4/livrable/livrable-sprint-4.md` et `.pdf`, 16 pages, sommaire vérifié)
   et synthèse de 4 pages, relus et validés par Era le 21/10 ; schéma complet ; journal des retours de l'atelier 3
   complété ; oral de l'atelier 4 prêt (hors dépôt) ; tag cité au CHANGELOG. Restent : PR de la branche vers
   `develop`, PR `develop` vers `main` (livraison N13) et rejeu en production, Definition of Done
   (`scripts/verifier_livrable.py livrable-sprint-4-v2`), tag v2 posé par Era sur `main` (SHA complet), liens au tag revérifiés ;
   après l'atelier 4, sa grille `eval/ateliers/sprint-4-grille.md`.
4. Ouverts : critère 1 du contrat « en cours » (OR.PA : dernière cotation à 64 jours, « probablement radiée ») ; D8 (le
   tiers du critère 5) ; validation de l'avenant n°1 par le formateur ; registre d'images sans compte ; dates de
   l'atelier 4 et du livrable à demander.

**Branche** : `sprint-4-agentique-garde-fous`, à jour avec GitHub.

## 🕘 Sprint 4 : livraison N10 (20/10/2026) (historique)

**Où on en est** : le sprint 4 (« la composante agentique et les garde-fous ») est en production depuis le 20/10 à
21 h 48 : livraison N10, commit `27da943` (fusion de la PR #112), index `5499bb05…`, 2140 articles, même empreinte de
contenu `fd8542955c1b…`. Chemin suivi : PR #111 (branche du sprint vers `develop`), PR #113 (les trois corrections de
la revue Codex de la PR #112, revue Codex sans remarque), PR #112 (`develop` vers `main`). La construction de l'image
s'est arrêtée au moins sept fois sur un 429 du registre public `public.ecr.aws` (« Data limit exceeded ») avant de
passer : défaut connu depuis le sprint 3, non corrigé.

**Rejeu en production** (20/10, 21 h 53, `evidence/sprint-4/rejeu_production.py`) : H1 refusé
(`TENTATIVE_DETOURNEMENT`), H8 en abstention, 21 caractères en 422, briefing OR.PA en 200, en français et sans conseil.
Q4 est juste au premier lancement, « 1 0 postes » au second. Le rapport du premier a été écrasé (corrigé : secondes dans
le nom, ouverture en mode « x ») ; reste `evidence/sprint-4/rejeu-production-2026-10-20-2153.json`.

**Q4** : diagnostic fait (passage 2788 de production identique au local ; 22 essais locaux justes) ; cause non établie.
Correction : contrôle des nombres (`guardrails/nombres.py`, motif `NOMBRE_NON_SOURCE`), commit `b4ab5e5`, 1367 passed.
**En local, non poussé, pas en production.**

**Relevé dans le briefing OR.PA** : en production, la dernière cotation d'OR.PA date de 63 jours, et le texte en déduit
« probablement radiée », ce qui est faux pour L'Oréal. À examiner.

**Ordre de la suite** :
1. Mesure de niveau 2 en local avec le contrôle des nombres (Era), depuis la racine du worktree :
   `C:/Python314/python.exe -m evals.mesurer_question --niveau 2 --index D:/KandaWork/RITA_PROJECT/transferts/index-18c122a9`.
2. Preuves dans `evidence/sprint-4/README.md` : N10, rejeu, diagnostic de Q4, contrôle des nombres, OR.PA.
3. Push, PR vers `develop`, PR vers `main` (livraison N11), puis rejeu en production à refaire.
4. D3 : livrable, journal des retours, plan (D2, étape 5) et contrat (critère 1) corrigés sur D9 (le texte du briefing
   n'est pas conservé), Definition of Done, tag `livrable-sprint-4-v1` posé par Era.
5. Ouverts : D8 (le tiers du critère 5), validation de l'avenant n°1 par le formateur, accès authentifié à l'image de
   base (429), cours d'OR.PA en production.

**Branche** : `sprint-4-agentique-garde-fous`, deux commits d'avance sur GitHub (`b4ab5e5`, `1ce5c04`).

## 🕘 Sprint 3 : atelier fait (19/10/2026), livrable version 2 (historique)

**Où on en est** : l'atelier croisé n°3 a eu lieu le 19/10, avec le formateur, en direct sur la production. Une
ingestion a été lancée par le bouton pendant l'atelier (passage `39265862974`, réussi, 2110 puis 2140 articles). La
grille n'a pas été remplie ; les retours, oraux, portent sur la présentation : `eval/ateliers/sprint-3-grille.md`.
Livrable version 2 (16 pages, format maison, liens GitHub vers le tag, capture `/health` du 19/10) :
`docs/sprint-3/livrable/livrable-sprint-3.pdf`.

**Production** (19/10, 19 h 40) : commit `7f2a855` (N8, tag `livrable-sprint-3-v1`) ; index `fc87b92a…`, 2140
articles, identifiant maximal 2898, empreinte `fd8542955c1b…`.

**Ordre de la suite** :
1. PR `sprint-3-donnees-ancrage → develop` (livrable version 2), commentaires de Codex lus avant toute fusion ; puis
   PR `develop → main`, dont la fusion lance la livraison N9 (version servie vérifiée).
2. Definition of Done sur le commit final : `C:\Python314\python.exe scripts\verifier_livrable.py livrable-sprint-3-v2`.
3. Era pose le tag `livrable-sprint-3-v2` ; les liens du PDF sont revérifiés au tag ; le lien du tag et le PDF sont
   déposés sur Simplonline.
4. Sprint 4 : avenant `/question` (décision A du 18/10) ; retours de l'atelier 3 appliqués à l'oral de l'atelier 4.

## 🕘 Sprint 3, état du 17/10/2026 (historique)

**Où on en est** : tout le sprint 3 est en production (N7, commit `66963da`). Le livrable (version 1, 10 pages, avec les trois
captures de production) est **validé par Era le 17/10**, après deux relectures, sur la branche `sprint-3-donnees-ancrage` (worktree `D:\KandaWork\RITA_PROJECT\rita-agent-sprint-3`) :
`docs/sprint-3/livrable/livrable-sprint-3.pdf`. **Atelier 3 : lundi 19/10/2026, le matin, après 9 h**, présentation et
démonstration en direct. Tag `livrable-sprint-3-v1` prévu dimanche 18/10 (« version préparée pour l'atelier ; retours
à venir »), puis `v2` avec la grille et les retours.

**Production** (17/10, 00 h 23) : `/health` donne `66963da` ; index `13f15d84…`, 2081 articles, identifiant maximal
2839, empreinte `0b372539…` ; image publiée par N7 `sha256:240d71432c2b6e2337dbb806c7e3b42d4aa4ecf444baac4b882284839496734b`
(journal de construction ; le journal du serveur reste à relire).

**Fait le 16/10 après le code** (preuves : `evidence/sprint-3/README.md` ; récit : `docs/sprint-3/COMPTE-RENDU-N5-2026-10-16.md`) :
- Serveur préparé par Era (B5) ; PR #100 et #101 ; livraison N5 (`41b1763`) à 18:59, rejeu sans écart.
- Première ingestion arrêtée à la collecte (`FeatureNotFound: lxml`) : rien écrit, index servi inchangé.
- N6 (PR #102 et #103, `72dba4d`) : collecte sans `lxml`, essai du nettoyage dans l'image en CI, fiche qui nomme
  l'éditeur, repères complets, dates en UTC dans l'empreinte (l'empreinte locale égale celle de la production).
  Livrée à 21:05 à la seconde tentative ; la première s'était arrêtée avant le serveur sur un 429.
- Ingestions par le bouton : à 21:08, 29 articles écrits ; à 21:21, aucun (dédoublonnage) ; rejeux sans écart.
- Évaluation, sur ce passage en production : 8 sur 8 conformes aux contrôles du jeu ; 3 faits sur 9 retrouvés
  automatiquement ; aucune affirmation non soutenue selon la relecture d'Era. Q4 contenait un caractère de contrôle U+0000 : correction N7 (`f089be2`, test d'abord).
- Dossier d'origine `D:\KandaWork\RITA_PROJECT\rita-agent` passé sur `main` (`72dba4d`) ; collecte du poste réactivée
  par Era, première collecte à 22:01 (6 étapes sur 6, sans Google News).
- C1, registre RGPD (`edd8934`) : T7 arrêté, date vérifiée sur le serveur et sur le poste ; corpus d'articles examiné ;
  T8 inscrit ; schéma E1 régénéré (T1 à T8).
- D3 : document d'entrée `docs/sprint-3/README.md`, index des preuves, journaux de chaîne et captures (`9c58d14`) ;
  l'ingestion décrite dans `docs/EXPLOITATION.md` § 8 et `docs/CHAINE-V1.md` (`53462b2`, relue par Era).
- PR #104 (correction de la fiche T8 après la revue Codex, `8364181`) et PR #105 : **livraison N7** (`66963da`) à
  22:10 UTC, vert du premier coup, même empreinte d'index.
- Suite complète : **1230 passed, 24 skipped, 2 xfailed** (sortie collée par Era).

**Ordre de la suite** :
1. ✅ Samedi 17/10 : trois captures prises par Era avec sa clé, à 16 h 25 (réponse citée et fiche de la source) et
   16 h 31 (refus), clé absente des images ; intégrées au livrable (§ 6.1, 6.2), index `evidence/sprint-3/README.md`.
   Reste : texte d'oral dans Obsidian (`Projets/RITA/03-Oraux/oral-sprint3-questions-reponses (2026-10-18).md`) et répétition chronométrée.
2. Livrable dans `main` par PR : #106 (`sprint-3-donnees-ancrage → develop`) fusionnée le 17/10 (`608c92c`) ; #108
   (suites de la revue Codex) à fusionner dans `develop` ; puis #107 (`develop → main`), dont la fusion lance la
   livraison N8 (version servie vérifiée). Definition of Done sur le commit final ; Era pose `livrable-sprint-3-v1`
   dimanche ; identifiant et empreinte de l'index de référence notés (le tag fige le
   code, pas les données).
3. Lundi 19/10 après 9 h, atelier 3 : grille recopiée mot pour mot dans `eval/ateliers/sprint-3-grille.md`, journal
   des retours.
4. Après l'atelier : intégrer la grille et les suites données aux retours par PR (branche, `develop`, `main`), ce qui
   déclenche une nouvelle livraison, à contrôler ; vérifier la Definition of Done
   (`scripts/verifier_livrable.py livrable-sprint-3-v2`) sur le commit final destiné au tag ; puis Era pose le tag
   `livrable-sprint-3-v2`, et sa publication est contrôlée. Le script vérifie un arbre propre et la présence du nom
   du tag ; il ne garantit pas, à lui seul, que les retours de l'atelier sont inclus.

**Restes et risques** (liste complète : `docs/sprint-3/README.md`, « Ce qui n'est pas fait ») :
- Construction de l'image : cinq 429 de `public.ecr.aws` le 16/10, relancés à la main ; cause non traitée.
- L'outil d'évaluation charge la clé locale du `.env` quand `RITA_API_KEY` manque : relevé, non corrigé.
- Manifeste du serveur sans commit ; corpus sans durée de conservation ; traces Langfuse en production non revérifiées.
- Serveur : « System restart required » ; ne pas redémarrer pendant une opération.

**Prochaine action** : Era fusionne la PR #108 dans `develop` quand ses contrôles sont verts et que la revue Codex n'a
plus de point ouvert, puis la PR #107 (`develop → main`), qui lance la livraison N8 ; relever la version servie,
l'image et l'identité de l'index. En parallèle : l'oral de l'atelier 3, sur quatre points (pourquoi RITA cite,
pourquoi elle refuse, ce que le rejeu vérifie sans le modèle, pourquoi 8 conformes ne veut pas dire 8 réponses
parfaites), puis une répétition chronométrée.

## ▶️ PROCHAINE ACTION (réécrit le 04/10/2026 ; les ▶️ plus bas sont datés et dépassés)

**Où on en est, en une phrase** : E1 v2.5 (5 pages, 11/10) et E3 v1.4 (20 pages, 11/10, **35 ✅ · 4 🟠 · 0 🔴** sur 39 lignes, 44 critères) sont complets côté
assistant et vérifiés contre le code et la base ; ils attendent ta relecture avant le gel du **jeudi 15/10** ; les deux alertes Langfuse sont en service ; la chaîne est
**verte** (`c7d0f2e`, 10/10 : 804 passed en CI, Livraison verte) ; la production sert toujours le code du **19/08**.
**Aucun code d'application avant le tag du 15/10.** Règle : **c'est Era qui envoie tout message** au formateur et à la
promo ; l'assistant rédige.

**Nuit du 04 au 05/10, ce qui a changé** (commits `5440a34` à `981cdc7`, CI verte à chaque poussée : 793 passed, 29
skipped, 2 xfailed) : les **sept schémas** E1 et E3 refaits (texte foncé, une couleur par rôle et par sens de flèche,
légende dessinée), **textes et flèches relus contre le code** (le scraping apporte des cours, pas des articles ; 22 PR
vers `main` ; l'alerte #77 a réellement sonné) ; **vingt figures** relues et placées (E1 y renvoie, les planches E4
attendent le rapport E4) ; tuile Langfuse renommée « Tentatives par fournisseur (échecs compris) » ; 278 473 cotations ;
E3 : retour des alertes à la normale constaté ; **décision d'architecture** pour le périmètre actuel (`CONTINUITE.md`
D : trois étapes fixes, une génération avec repli de fournisseur, à rouvrir après le brief multi-agents) ; **règle UE
seule**, choix du projet d'Era : registre RGPD corrigé (T1 disait « aucun destinataire »), T6 et T7 inscrits non
conformes (#82, #81) ; trois défauts latents d'indicateurs (#78, #79, #80) et l'ATR en % (#83). Guides d'étude E1 (mis à
jour) et E3 (nouveau) : Obsidian `09-EN-personnel`, jamais dans le dépôt.

**05/10 au soir et nuit du 06/10, ce qui a changé** (commits `0dc32fe` à `77b449f` sur `develop`, `07a7ecb` et `987eaf2`
sur la branche `classeur-competences` ; CI verte : 793 passed, 29 skipped, 2 xfailed, couverture 94,70 % ; le soir,
une panne de GitHub Actions a annulé deux exécutions sans lancer une étape, relancées à 23 h 56 et vertes) : retour du
formateur consigné ; contrats d'OpenRouter et de Langfuse relus (garanties identifiées, vérification propre à RITA
incomplète) ; guide d'exploitation remis d'accord (`f34486c`), cartes #24, #25, #55 fermées ; **classeur des
compétences** : statuts corrigés (110 OK, 24 partiels, 1 à faire), colonne « Rédaction » des 9 compétences rédigées
réécrite, 17 notes périmées corrigées, synthèse courte à la même source ; GitHub (branche à part) et Google Drive
(synthèse seule, doublons et ancien fichier mis à la corbeille) ; E2 v0.2 (§ 4.3, § 4.4, critères C8).

**Trois décisions qui attendent Era** : (1) ~~C8.2~~ tranchée le 09/10 : partiel des deux côtés (classeur v4 : 110, 26, 1 sur 137 lignes) ; (2) ~~carte #84~~ faite le 09/10 (`21cf8f1`, preuve
`evidence/C18/preuve-image-runner-epinglee-2026-10-09.md`) ; (3) **relire la colonne
« Rédaction »** du classeur et la dire avec ses mots, puis partager la synthèse Drive en « Commentateur » et envoyer
les deux liens, le message d'état et `docs/EXPLOITATION.pdf` au formateur.

**09/10, ce qui a changé** : carte #84 faite (image des machines de la CI épinglée sur `ubuntu-24.04`, test d'abord,
CI verte sur `Image: ubuntu-24.04`) ; **Azure AI Foundry en Data Zone Standard EU** (`gpt-5.4-dzs-eu`, créé par Era,
trois appels réels en Sweden Central, `evidence/C8/preuve-deploiement-zone-eu-2026-10-09.md`) : T6 partiellement corrigé, les replis Anthropic
et OpenRouter restent à retirer après le gel ; collecte du 08/10 : 2 étapes sur 6 en échec (Boursorama a rendu une
ouverture à 0 pour OR.PA, refusée par la contrainte `prix_positifs`, ce qui a annulé tout le scraping du soir ; `cygrpc`
de nouveau bloqué par Smart App Control), collecte du 09/10 normale (6 sur 6). Douze avertissements nouveaux en CI
(`pydantic` 2.14 dans la bibliothèque `giskard`, carte #23). À faire par Era dans le portail : supprimer `gpt-5.4-3`
(Global Standard créé par erreur), puis `gpt-5.4-2` (l'ancien Global Standard). **Fait par Era**, vérifié la nuit suivante (voir ci-dessous).

**Nuit du 9 au 10/10, ce qui a changé** (commits `645696f` à `c7d0f2e` ; CI verte : 804 passed, 29 skipped,
2 xfailed, couverture 94,70 % ; Livraison verte) : les deux déploiements Global Standard sont supprimés (404
`DeploymentNotFound` sur les deux), seul `gpt-5.4-dzs-eu` répond. **Carte #85** : Docker Hub a refusé trois
constructions de l'image de suite (429, 429, 504) alors que les tests passaient ; l'image de base vient désormais de
la galerie publique d'Amazon, même empreinte, test d'abord (`232c209`, preuve
`evidence/C19/preuve-image-de-base-galerie-amazon-2026-10-10.md`). **C8.2 partiel dans le classeur aussi** (v3 :
109 OK, 25 partiels, 1 à faire ; v4 le matin, voir le paragraphe suivant). **Mistral UE**
choisi par Era pour remplacer les replis hors UE **après le gel** (carte #82, `CONTINUITE.md` D) ; sonde de la clé
le 10/10 : `mistral-large-2512` répond en 0,53 s par l'adresse européenne ; aucun code de RITA touché. **Note
d'étude** de la colonne « Rédaction » (les 9 paragraphes, leur sens en anglais, les questions probables du jury,
une ligne « Ma version » à remplir) : Obsidian `09-EN-personnel`, jamais dans le dépôt.

**Le classeur v4 (10/10 au matin) : où il est, ce qu'il reste à faire (Era)**. Era s'étonnait du total de 135 :
recompté contre le référentiel officiel, il y a **142 critères**. Le modèle Simplon (135 lignes, les mêmes chez David
et Mehdi) en réunit parfois deux en une ligne (C9, C10, C13, C17, C18) et en découpe un (C6), sans rien perdre, mais
**omet deux critères de C19** : la documentation de la chaîne de livraison (installation, configuration, test),
**partiel** (le test de la publication sur un tag n'est pas documenté, premier passage le 15/10), et son format
accessible, OK. Ajoutés en fin de C19, marqués « ajouté » : **137 lignes, 110 OK, 26 partiels, 1 à faire**. C13
vérifié : son critère d'accessibilité est réuni dans la ligne de la documentation, toujours OK (PDF E3 régénéré,
remesuré le 10/10). Fichiers : détaillé `D:\KandaWork\RITA_PROJECT\Era-Preparation-livrables-RNCP_10_10_26.xlsx` ;
synthèse, détaillé et README de la branche dans `D:\KandaWork\RITA_PROJECT\classeur-v4-pour-branche\` (le dossier
v3 reste comme version précédente). À faire : (1) fermer Excel (il tient encore la synthèse v2), puis remplacer la
synthèse de `D:\KandaWork\RITA_PROJECT\` par celle du dossier v4 ; (2) sur la branche `classeur-competences`,
remplacer les trois fichiers de `docs/competences/` par ceux du dossier v4, commit, push ; (3) Google Sheets :
Fichier, Importer, la synthèse v4, « Remplacer la feuille de calcul » (le lien ne change pas) ; (4) signaler au
formateur que son modèle omet deux critères de C19 (Era envoie) ; (5) relire la colonne « Rédaction » avec la note
d'étude et écrire sa version.

**E3 v1.4 (11/10, soir), passe documentaire validée par Era, revue d'E3 close.** Sept corrections, chacune vérifiée
dans le code ou le référentiel, toujours **20 pages** (alignées page par page sur la v1.3, regardées) : (1) routes
publiques nommées (`/health`, documentation OpenAPI, pages de l'interface, sans données métier protégées) ; (2) la clé
n'est pas contrôlée au démarrage mais à l'authentification (`cle_attendue()` appelée seulement par `verify_api_key`,
`api/main.py:168`) ; Docker Compose impose sa présence ; sans en-tête, 403 ; avec en-tête sur un serveur sans clé,
500 générique ; (3) le texte du briefing est dans deux observations Langfuse (`briefing-llm` et la génération,
`src/traces.py:260-286`) ; (4) un schéma Pydantic existe (`EvenementMcp`), le manque est la validation structurée de
la sortie du modèle ; (5) depuis le 11/10 le poste n'appelle qu'Azure ; (6) **44 critères au référentiel pour C9 à
C13** (11, 9, 9, 7, 8, compté dans le PDF Simplon), regroupés en 39 lignes, aucun absent, statuts inchangés ;
(7) couverture : tests exclus « pour mesurer le code applicatif », plus « 100 % par construction ». Copies OneDrive
v1.4 (français, anglais `.md` et `.pdf`) ; addendum dans l'oral E3 v1 (Obsidian). **Reste, choix de calendrier et non
validation** : les cinq figures d'E3 sont lisibles à l'écran mais petites imprimées (environ 4,2 points dans les
boîtes, 5,2 pour leurs titres) ; refonte après le gel, en nouvelle version, jamais en remplaçant le PDF en silence.

**E1 v2.5 (11/10, nuit), cinq surgénéralisations corrigées, chacune vérifiée dans le code ou les preuves.** « Zéro ligne
vaut échec » vaut pour la BCE et FRED seulement (`pipelines/ingest.py:107`, `:158`) ; STLAP.PA est exclue des
classements, pas de la valorisation (`db/requetes.sql:48-50`) ; le rétro-ajustement est celui du fournisseur, et
« divisé par 36 millions » est l'évolution observée de 2016 à 2024 (`evidence/C3/preuve-artefact-reverse-split.md`) ;
la cause commune des quatre autres défauts d'INC-005 est la place de cotation absente du modèle, pas l'erreur UTC ; la
méthode big data est démontrée en local, sans mesure à grande échelle. La note du § 7 sur LangSmith est resserrée
(faits gardés). Toujours **5 pages**, regardées ; copies OneDrive du 11/10 remplacées (français, anglais). Registre
§ 0 : avec plusieurs utilisateurs, déterminer et documenter la base légale de chaque traitement, le consentement n'en
étant qu'une possibilité. Oral E1 v3 aligné (Obsidian, quatorze passages en anglais et en français).

**E1 v2.4 (11/10, soir), seconde passe validée par Era, dernière avant le gel.** La phrase d'installation ne promet
plus une reconstruction « depuis un dépôt vierge » : elle renvoie aux prérequis du guide (§ 3 et 4), et l'ancienne
mention « rejouée sur une base Compose neuve le 03/10 » est retirée (le 03/10, seules les migrations ont été jouées
sur la base Compose : commits `2caa9b6` et `1a5ecd9`) ; T4 donne une conservation (« tant qu'il sert »), plus un
lieu ; trois « détenue(s) » remplacés (positions simulées) ; MCD lisible à hauteur constante (cadre recadré, largeur
80 %, attributs sur deux lignes, environ 7 points au lieu de 5, traits plus foncés, POSITION ne déborde plus) ;
numéros de page « n / 5 ». Toujours 5 pages, regardées une à une. **Guide d'exploitation, même défaut, en pire** :
le § 4.5 lançait `db.importer` sans jamais construire le Parquet (absent de Git) ; `bigdata.build_parquet` ajouté
avant, `docs/EXPLOITATION.pdf` régénéré (11 pages). Écartés, par choix : liens cliquables (travail neuf), coupure
du paragraphe entre les pages 1 et 2 (normale). **Règle pour la suite : E1 ne se rouvre que pour une erreur de
fait**, plus pour la mise en page.

**E1 v2.3 (11/10), passe documentaire validée par Era, revue d'E1 close.** Huit corrections, vérifiées dans le code
et le registre, toujours 5 pages (lignes par page identiques, pages regardées une à une) : (1) § 7 réécrit : positions
inventées, CSV de démonstration versionné, `mcp_calls` déjà personnel (registre T5), règle UE seule « à établir » pour
T3, T6 et T7, replis désactivés sur le poste mais présents par défaut, exemption domestique (RGPD art. 2.2.c) à
examiner, intérêt légitime (art. 6.1.f) retenu à titre provisoire, justification à documenter ; (2) légende et
description du MCD : « seule entité prévue pour des données personnelles (positions inventées à ce jour) » ; (3) dépôt
privé « conçu pour » un portefeuille réel ; (4) connexion PostgreSQL **principale** ouverte une fois, l'indexation ouvre
la sienne (`pipelines/ingest.py:454`), HTTP géré par chaque source ; (5) le scout lit la base par les modules
d'indicateurs avec `DATABASE_URL` (`indicateurs/socle.py:136-141`) ; (6) `article` et `macro_observation` sont des
données collectées, pas des tables techniques ; (7) **ordre d'installation corrigé** : `bigdata.build_parquet` avant
`db.importer`, qui lit le Parquet (`db/importer.py:114-117`), la séquence échouait sur un dépôt vierge ; (8) version et
date. Registre : § 0 (réserve de l'art. 2.2.c), T1 (base légale provisoire), glossaire. Copies OneDrive du 11/10
(français, et anglais en `.md` et `.pdf`) ; addendum « corrections du 11/10 » dans l'oral E1 v2 (Obsidian).
**Reste, après le gel** : le commentaire de `db/schema.sql:154` répète « intérêt légitime de la personne concernée »
(zone sous garde, plan d'abord) ; rédiger la mise en balance de l'intérêt légitime et examiner l'exemption domestique.

**E1 v2.2 (10/10, 10 h), décision d'Era « fix points 1 to 4 before the freeze »**, relevés en traduisant E1 en
anglais : (1) la date (4/10) était en retard sur le contenu (zone UE du 09/10) : 10 octobre, version 2.2 ;
(2) `memory_audit` : choix C d'Era, la décision (retirer la table ou lui donner un écrivain) se prend **après le
gel**, carte #86, pour ne toucher ni au code ni au schéma avant le tag ; (3) chiffres des tests mesurés et datés :
835 collectés sur le poste, en CI le 10/10 804 verts, 29 ignorés (ni base, ni JDK, ni Windows), 2 échecs attendus,
94,7 % ; (4) le schéma Merise avait une balise de figure sans texte alternatif : texte alternatif ajouté, mesuré
(1 figure, 1 texte). Toujours **5 pages**, mise en page identique (bas de chaque page au même point), chaque page
modifiée regardée. La traduction anglaise d'Obsidian est remise d'accord.

**E3 v1.2 (10/10, 10 h 30), même demande d'Era pour E3**, relevés en traduisant E3 : (1) version et date (« 1.1, 4
octobre ») en retard sur le § 7.3 du 09/10 : 1.2, 10 octobre, et la ligne « Mesures » dit l'exception de l'image de
base ; (2) **E1 et E3 se contredisaient sur Langfuse** : E3 disait « à confirmer par la lecture du contrat », E1 dit
le contrat relu le 05/10 ; E3 dit maintenant la même chose (registre, T3). Toujours **20 pages**, 5 figures avec texte
alternatif ; seules les pages 6 à 8 bougent. Copies de lecture : `C:\Users\kanda\OneDrive\RITA\reports\` (E1 et E3 en français, et
leurs traductions anglaises en `.md` et `.pdf`).
Puis, à 10 h 40, sur demande d'Era : E3 disait « rapport du 11 août » (la date écrite sur la v1 d'E1) et E1
« envoi du 13 août » ; E3 dit maintenant « rapport envoyé le 13 août », pour que les deux rapports, envoyés ensemble
après le gel, donnent la même date. **E1 v1 a été envoyé le 13/08 ; E3 n'a jamais été envoyé.** Aucune page ne
bouge.
Ensuite, sur demande d'Era : le **registre RGPD** (preuve d'E1, C4) disait encore dans son glossaire que les clauses
contractuelles types étaient « à confirmer » ; il dit maintenant qu'elles sont prévues (Langfuse § 6.2, T3 ;
OpenRouter § 13.2, T6, contrats relus le 05/10) et que l'AITD n'est pas faite ; la ligne du Data Privacy Framework
dit ce qui reste vraiment ouvert (certification de ClickHouse, Inc. non vérifiée, § 5 point 7) ; la liste du 02/10
garde son texte, avec « Fait le 2026-10-05 ». `tests/test_rgpd_registre.py` : 4 passed.
Puis, sur demande d'Era : **les dépendances épinglées** étaient mal comptées. `requirements.txt` (compté le 10/10) :
18 dépendances, **5 épinglées** (`langfuse`, `feedparser`, `chromadb`, `rank-bm25`, `pyspark`), `mcp` avec un
minimum, 12 sans version. E1 § 9 oubliait `rank-bm25` et § 10 disait « la moitié » : « 13 dépendances sur 18 » ;
E3 § 7.4 disait « quatre » sans `pyspark` : « cinq ». E1 toujours 5 pages (mise en page identique), E3 toujours
20 pages (seule la page 16 bouge). Traductions et copies OneDrive remises d'accord.
Puis **les 7 soirs de collecte coupés** (E1 § 3 disait « rattrapés ») : vérifiés en base le 10/10 par une requête en
lecture seule lancée par Era : quatre rattrapés le 18/09 (sauf la séance parisienne du 17/09), un sans perte (08/09),
deux incomplets : articles des 02 et 03/09 perdus, et **aucun taux BCE le 03/09**, que Era a rattrapé le 10/10
(`--etapes ecb --du 2026-09-03 --au 2026-09-03` : 4 lues, 5 écrites). E1 § 3 le dit, toujours 5 pages. Preuve :
`evidence/C1/preuve-soirs-coupes-verifies-2026-10-10.md`. Le rôle `rita_lecture` n'a ni mot de passe ni
`RITA_DSN_LECTURE` sur le poste : un agent ne peut pas lire la base comme le prévoit `AGENTS.md` (après le gel).
Enfin, **audit de propagation** demandé par Era (règle : tout changement se cherche partout, pas seulement dans le
PDF) : chaque fait changé les 09 et 10/10 cherché par son ancienne valeur dans tout le dépôt. Jumeaux corrigés :
`docs/CI-CD.md` (quatre dépendances épinglées, cinq en vrai), `README.md` (742 et 700 tests, E1 v2.0, E3 v0.1 :
835 tests, E1 v2.2, E3 v1.2), `docs/PLAN-12-SEMAINES.md` (contrat Langfuse « à confirmer »), `CLAUDE.md` (835 tests
collectés), le classeur v4 (memory_audit « décision en attente », quatre fichiers), `Dockerfile.tests` (encore
Docker Hub : test d'abord, rouge, vert, mutation). Code gelé laissé tel quel et inscrit sur #82 : `src/llm.py:39`
(déploiement par défaut `gpt-5.4`, supprimé le 09/10), `src/llm.py:79` et `tests/test_llm.py:109` (« Global Standard »).

**10/10, après-midi et soir, ce qui a changé** (`develop` : plusieurs commits locaux du 10/10, pas encore poussés, vérifier `git status --branch` avant tout push ; branche `mistral-ue`,
PR #88 en brouillon : `0a3f3f8` poussé, CI verte ; `2a7f18c` et `b3c76b5` pas encore poussés) :
- **Incident, clé Mistral** : la vraie clé d'Era a été écrite dans `.env.example` et poussée (`5fae28e`), puis une
  deuxième dans le commit de correction (`8587a21`). Era a supprimé les deux clés chez Mistral et en a créé une neuve,
  dans `.env` seulement (empreinte différente des deux, vérifiée sans afficher la clé) ; sur GitHub, le modèle n'a plus
  que des valeurs de gabarit (`0a3f3f8`, lu sur `origin/mistral-ue`). Les deux clés restent lisibles dans l'historique
  de la PR #88, révoquées donc inutilisables ; fusion en squash après le gel. Méthode désormais : commit local,
  vérification sans afficher de valeur, puis push.
- **`develop`, `000ca50`** : `README.md`, `CLAUDE.md` et `docs/EXPLOITATION.md` décrivent la cascade réelle de
  `develop` (Azure `gpt-5.4` d'abord, Claude par Anthropic puis OpenRouter en secours) ; une panne de tous les
  fournisseurs répond **500** (`api/main.py:96-105`), le 502 est réservé aux données manquantes du scout ; PDF du
  guide régénéré, 11 pages, page 8 regardée.
- **Premiers vrais briefings Mistral** (MC.PA, même prompt qu'Azure octet pour octet) : Large 3 invente une date de
  séance absente du prompt ; Large 4 avec sa réflexion par défaut rend une liste de blocs sans texte (500) ; **Large 4
  sans réflexion** (`reasoning_effort: "none"`) : 3,09 s, 0,10 centime, garde-fou AMF conforme, aucune date inventée.
  **Décision d'Era : Large 4.** Code et tests d'abord (5 rouges puis verts, suite **847 passed** sur la branche),
  preuve `evidence/C8/preuve-briefing-mistral-2026-10-10.md` (sur la branche). Langfuse compte 0 $ pour Mistral : le
  prix du modèle n'est pas dans sa grille.
- **Ordre de la cascade** : Azure GPT-5.4 reste premier (gratuit pour Era) pour les essais de tous les jours ; Mistral
  sert aux preuves ; l'ordre se tranchera sur le banc C7 après le gel.
- **Règle UE seule gardée stricte** (choix d'Era) ; Google News par position se corrige par #81 après le gel, telle
  qu'écrite. Vérifié dans le code : FRED, yfinance, BCE et Boursorama ne révèlent pas les positions ; seule Google News
  les révèle (`pipelines/ingest.py:283-289`) ; aujourd'hui ce sont des positions simulées et l'adresse IP, et #81 est
  bloquante avant tout chargement d'un portefeuille réel. Un transfert se juge par le texte du CEPD (lignes directrices 05/2021,
  § 9 : un accès à distance depuis un pays tiers est un transfert) ; Microsoft documente des transferts limités hors
  de son EU Data Boundary : T6 n'est pas entièrement prouvé côté Azure (registre, § 5).
- **Jeu de démonstration** : positions inventées sur des sociétés réellement cotées, choisies dans la liste suivie ;
  Era ne détient pas ces titres (sa déclaration du 10/10). Le fichier de preuve
  `evidence/C17/mesures-2026-10-03/entrees/donnees_portefeuille.json` : ses 7 positions sont toutes dans le jeu d'exemple
  (12 lignes dans le fichier, 10 gardées par le lecteur, 7 importées, 3 hors univers) : aucune position réelle dans Git.
- **Défaut trouvé en vérifiant : le verrou de démonstration MCP refuse le jeu de démonstration importé dans
  l'environnement actuel.** Le vrai code du verrou, lancé sur la
  base du 03/10, rend `False` : il compare aux 10 lignes du fichier, l'import n'en garde que 7. Le refus du 03/10 (E3,
  section 4.1 ; preuve C20) ne venait donc pas d'un portefeuille réel. Échec fermé, sans fuite ; le test vert simule
  une réponse de 10 positions. **E3 passe en v1.3** (une phrase en 4.1, toujours 20 pages, page 5 regardée ; copies
  OneDrive v1.3 en français et en anglais), erratum `evidence/C20/erratum-verrou-demonstration-2026-10-10.md` (l'ancienne
  preuve n'est pas réécrite). Correction après le gel, carte à créer.
- ✅ **Fait par Era, vérifié le 11/10** : `.env` ligne 25 `MISTRAL_MODEL=mistral-large-4-0` et ligne 26
  `LLM_ORDRE=foundry` (lues seules, sans afficher de clé ; une seule occurrence de chaque) ; `mistral-ue` et `develop`
  poussés, CI lue verte (`develop` : `f152668`, 807 passed, 29 skipped, 2 xfailed).
- **À faire par Era** : documenter comment le fichier local non versionné `data/positions.csv` du 31/07 a été constitué
  (Era n'a jamais investi).

**E2 (C6 à C8) : état au 11/10 et plan proposé le 11/10, enregistré à la demande d'Era.** Rapport `docs/rapports/E2/rapport-E2.md` en **v0.3 du 09/10**,
environ 3 200 mots, **aucun PDF** ; 15 à 20 pages attendues, oral de 15 minutes, dû le 05/11. Décompte à défendre :
**6 ✅ · 13 🟠 · 1 🔴** sur 20 (§ 5 du rapport, le plus prudent). Le classeur local du 10/10, non versionné dans `develop`, dit 8 · 11 · 1 : l'écart est dans C6
(5 OK au classeur, 3 au rapport), à aligner sur le rapport quand E2 sera écrit. Une vraie note de veille récente peut
porter le décompte à 7 · 12 · 1.
- **Avant le gel (Era seul, sans toucher au gel)** : (1) **recommandé** : un nouveau relevé S41, puis une vraie note S41 ;
  **si le temps manque** : finaliser en rattrapage, le 11/10, la note S40 à partir du relevé S40
  (`docs/veille/_candidats-2026-S40.md`), sans antidater ; S37 et S40 ont des relevés préparatoires, S38 et S39 sont
  sans séance ; (2) la partager
  avec **une question précise**, et garder la capture du fil et au moins une réponse (preuve de C6.4) ; (3) facultatif :
  un lecteur RSS montrable (Feedbro ou Thunderbird), capture des sources, budget 0 € (C6.3).
- ✅ **Fait le 11/10** : (1) relevé S41 (`docs/veille/_candidats-2026-S41.md`, fenêtre du 29/09 au 11/10, corrigé en
  six points après relecture) et **note S41 rédigée par Era** en rattrapage (`docs/veille/2026-S41-mesurer-le-gardefou.md`,
  commit `5422609`) ; (2) **partagée** dans le canal #veille du Discord de la promo le 11/10 à 20 h 04, avec une question
  ouverte ; capture du message dans `evidence/C6/envoi-2026-10-11-promo-discord-veille.png`, envoi 3 de
  `docs/veille/_JOURNAL-DES-ENVOIS.md`. **Reste** : au moins une réponse, puis la capture du fil réponses comprises
  (`evidence/C6/discussion-<date>-discord.png`) ; la capture du fil S33 du 16/08, jamais faite ; (3) facultatif, inchangé.
- **Après le gel, dans l'ordre** : (1) fusion de la PR #88 et lecture de la CI ; (2) lecture des conditions de Mistral
  (sous-traitants, conservation, entraînement) et des cas de transfert documentés par Microsoft ; (3) décision sur
  **Langfuse** (hébergé en Irlande, mais son contrat permet un traitement hors de la région) : réduire ce qui est envoyé
  limite le risque sans tenir la règle UE stricte ; donc désactiver ou remplacer Langfuse pour les traces concernées, ou
  le garder en acceptant que C8.2 reste partiel ; (4) banc C7 **Azure Data Zone EU contre Mistral Large 4**, mêmes 10 cas, 3 répétitions ;
  (5) notation à l'aveugle de ces **60 nouveaux textes** (pas des anciens textes Azure contre Claude : Claude sort de la
  cascade) ; (6) rédaction de C7 ; (7) alignement du classeur sur le rapport ; (8) C8.5 : fusion de la configuration
  finale, guide régénéré, accessibilité remesurée, envoi au formateur, preuve datée de l'envoi (un accusé de réception la
  renforce) ; le guide actuel décrit encore Anthropic et OpenRouter ; (9) PDF d'E2 (15 à 20 pages), liens et accessibilité vérifiés, puis
  tag `livrable-E2-v1`.
- **Corrections à porter dans E2** : « 2 appels Azure sur 30 au-dessus de 10 s » (mesuré le 11/10 dans
  `evidence/C7/resultats-2026-10-03.jsonl` ; la preuve C7 dit « un sur vingt » et ne se réécrit pas) ; « 30 textes sur 30
  passent l'heuristique minimale de fidélité (cours et sens de la variation) ; la fidélité complète demande une relecture
  humaine » au lieu de « fidélité égale » ; séparer le coût réellement payé du coût calculé au tarif public ; l'adresse
  `api.eu.mistral.ai` prouve le point d'accès, pas les sous-traitants ni la conservation ; C8.2 mentionne aussi Langfuse ;
  recommandation provisoire : Azure GPT-5.4 Data Zone EU en premier, Mistral Large 4 meilleur secours européen identifié,
  à confirmer par le banc complet et la lecture du contrat. **Ajouté le 11/10** : le briefing réel de LVMH (MC.PA, 11/10)
  comme exemple de fidélité dans C7 (il passe l'heuristique minimale, cours et sens de la variation, mais contient une
  durée non étayée et un cours présenté comme seuil) ; deux points pour la grille de notation à l'aveugle :
  « affirmation temporelle non étayée » et « niveau de prix présenté comme seuil ».

**Décisions d'Era du 11/10 (détail et pourquoi : `CONTINUITE.md`, § D)**
- **Fournisseurs** : appels réels par **Azure GPT-5.4 seul** (`LLM_ORDRE=foundry`, `MISTRAL_MODEL=mistral-large-4-0`
  écrits dans `.env`) tant que le contrat de Mistral n'est pas lu ; Mistral Large 4 seulement pour le banc C7, sur des
  données publiques ou simulées. Les tests automatiques n'appellent aucun modèle (doublures).
- **Prompt du rédacteur, décision d'Era du 11/10 (option B)**, à faire le **16/10, test d'abord, avant le banc C7**
  (`agents/analyst.py`, `construire_prompt`) : (1) la **date de la séance** affichée, distincte de la date de
  génération ; (2) la consigne « Signale un point à surveiller pour la séance suivante » remplacée par « un élément
  observable à suivre, tiré des seules données fournies, sans présenter un cours comme un seuil » ; (3) une règle
  ajoutée : « ne décris pas une durée ou une tendance que les performances fournies ne montrent pas ». Pourquoi : un
  briefing réel de LVMH (MC.PA, 11/10) écrivait « séance » sans date, « pression vendeuse persistante depuis plusieurs
  semaines » (durée non étayée) et « le seuil des 380 EUR » (la clôture, présentée comme un niveau), ce dernier
  directement induit par la consigne n° 3 ; un banc lancé avant mesurerait ce défaut chez les deux modèles. Ce sont des
  corrections de fidélité, pas des fonctionnalités. **Après le 05/11** (nouvelles fonctionnalités) : comparer deux
  briefings par des instantanés chiffrés, séparer actualités récentes et historiques dans la recherche, comparaison
  à un indice, volumes relatifs, alertes sur des changements factuels ; à citer dans « ce que je ferais ensuite »
  (E4, E5, oral).
- **Calendrier final** :

| Quand | Quoi |
|---|---|
| jusqu'au **14/10** | Era relit E1 et E3 ; veille S41 (relevé, note et partage faits le 11/10 ; réponses attendues) |
| **15/10** | gel d'E1 et d'E3 (inchangé, ligne du tableau plus bas) |
| **16/10** | prompt du rédacteur (`agents/analyst.py`, test d'abord) : date de séance **et deux consignes corrigées** (décision d'Era du 11/10, option B, ci-dessus), tests, puis banc C7 Azure contre Mistral Large 4 dans un dossier de résultats neuf |
| **17-20/10** | E2, E4 et E5 terminés, PDF compris |
| **23/10** | gel final |
| **26/10** | simulation personnelle |
| **29/10** | examen blanc complet |

  **Aucune fonctionnalité nouvelle avant le 20/10**, sauf une correction indispensable à la validité d'une preuve.
- **Après le gel, liés à la PR #88** : (a) avant la fusion, valeurs par défaut de `LLM_ORDRE` passées de
  `foundry,mistral` à `foundry` dans `src/llm.py:34`, `docker-compose.yml:91` et `.env.example:43` (branche
  `mistral-ue`), test d'abord ; (b) panne de tous les fournisseurs : **aujourd'hui** 500 générique avec identifiant,
  sans détail interne ; **cible** 503 `AUCUN_FOURNISSEUR` testé (carte #75, constat S6).
- **Manque relevé et corrigé le 11/10 (décision d'Era : corriger avant le gel)** : sur `develop`, le service `api` de
  `docker-compose.yml` ne recevait aucune variable `AZURE_FOUNDRY_*` et mettait `anthropic,openrouter` par défaut,
  alors que `src/llm.py:28` met `foundry,anthropic,openrouter` : en conteneur, la cascade sautait Azure. Corrigé :
  les trois variables Azure transmises (clé vide par défaut, jamais écrite), ordre par défaut aligné sur le code ;
  deux tests de contrat d'abord, vus en échec (`tests/test_docker_compose.py`, le second compare le comportement réel
  de `_ordre_fournisseurs()`). Suite complète le 11/10 : **834 passed, 2 skipped, 2 xfailed** (838 collectés) ; le
  chiffre se remesure au gel. Les lignes Anthropic et OpenRouter restent : elles décrivent le code gelé, et la PR #88
  les retire partout à la fois. Les anciennes traces Anthropic et OpenRouter restent des preuves datées.

- **Manque relevé le 11/10 (relecture du relevé S41), à traiter après le gel** : aucune garde contre une **baisse** du
  taux de blocage du garde-fou d'injection. Le test à 85 % est un échec attendu strict (`tests/test_evals.py:17-51`) :
  si le blocage tombait de 70 % à 40 %, il échouerait toujours « comme attendu » et la CI resterait verte ; seuls les
  faux positifs et la latence bloquent la fusion. Correction proposée (zone sous garde : plan écrit et validé d'abord,
  test rouge d'abord) : un test de non-régression qui exige que les 7 détections connues restent détectées, sans
  toucher au seuil de 85 %. Le jeu de 18 cas : 7 attaques écrites le 29/07 pour couvrir les 9 motifs (`c1ee404`),
  3 attaques adverses écrites le 17/08 contre eux (`c7c8811`, ce sont les 3 qui passent), 8 phrases d'actualité
  ordinaires ; il prouve une couverture d'exemples, pas un taux de sécurité en production.

- **Guide d'exploitation, relevé le 11/10 (relecture), à traiter après le gel** : (a) aucune procédure ne remplit la
  base Docker (son PostgreSQL ne publie aucun port, la collecte du § 8 tourne sur le poste) : construire et tester
  une initialisation de la base de Compose ; (b) rejouer les deux voies d'installation (Docker et native) sur un
  environnement neuf et isolé, puisque les corrections du 11/10 (`cd rita-agent`, base dont `rita` est propriétaire,
  `.env` non écrasé, `curl.exe`) suivent le code et la documentation de PostgreSQL sans avoir été rejouées ; (c) la
  passe complète C8.5 après la fusion de la PR #88. Corrigé dans le guide le 11/10 (documentation seule, 12 pages).

**📅 Calendrier jusqu'au 05/11, décidé par Era le 06/10, gel fixé au jeudi 15/10 le 09/10** (lignes « 15-25/10 » et
« à partir du 26/10 » précisées le 11/10 : voir le calendrier final juste au-dessus) (mesuré le même jour : E1 et E3 complets ; E2 en v0.3 depuis le 09/10, partie
C7 à écrire ; **E4 : aucun rapport**, seulement `docs/PLAN-E4-rapport.md` et un recomptage ; **E5 : aucun rapport**) :

| Quand | Quoi |
|---|---|
| **06-14/10** (en parallèle du brief) | Era relit E1 et E3 et la colonne « Rédaction » du classeur ; envoi des liens au formateur ; décisions C8.2 et #84 **prises le 09/10** (C8.2 partiel, #84 faite) |
| **jeudi 15/10** | **gel d'E1 et d'E3** : **d'abord remesurer les tests et propager le chiffre partout** (`pytest --collect-only -q` et la dernière CI : E1 § 2, § 9 et § 10, `README.md`, `CLAUDE.md` ; 835 collectés et 804 verts au matin du 10/10, 836 et 805 depuis `ffe1a46`), régénérer E1 et ses copies ; puis PR `develop → main`, Definition of Done verte (`scripts/verifier_livrable.py`), tags `livrable-E1-v2` et `livrable-E3-v1`. **Après le gel, plus aucune fonctionnalité nouvelle dans RITA** |
| **15-25/10** | écrire **E4** (15 à 20 pages) et **E5** (2 à 5 pages), finir **E2** (C7) ; les corrections de code d'après le gel seulement si un rapport ou le jury en a besoin, le reste écrit dans « ce qui n'est pas fait » |
| **à partir du 26/10** | examens blancs ; **passer l'oral d'E1 et d'E3 en français** en premier (oral blanc des 29-30/10) |
| **05/11** | tous les livrables tagués et envoyés |

Le **gel** fixe le contenu d'un livrable : fusion dans `main`, tag que GitHub interdit de déplacer ; toute correction
ensuite passe par une nouvelle version taguée, jamais en silence (règle d'Era du 29/09 : geler 2 à 3 semaines avant l'oral ; date repoussée du 11 au 15/10 le 02/10 ; cible du 13/10
abandonnée le 09/10, le 15/10 étant la date la plus tardive qui laisse deux semaines avant l'oral blanc du 29/10).
Idée prise dans la grille d'un camarade : arrêter de construire à date fixe, puis seulement écrire, et donner une date
à chaque critère non fini.

**Le dernier brief** (multi-agents et industrialisation) : Era le fait **seul** cette semaine, dans un dossier
`kadera_v2` (chemin à donner) ; l'assistant n'y écrit rien et le relit à la fin de la semaine, puis écrit la passerelle
vers RITA dans `CONTINUITE.md`. D'ici là, RITA reste à trois étapes.

**Tâche principale de la prochaine session** : avancer RITA vers le gel du **jeudi 15/10**. Era relit E1 (5 pages) et
E3 (20 pages), dit la colonne « Rédaction » avec ses mots (note d'étude du 10/10), met le classeur v4 en place, puis
envoie au formateur les liens, le message d'état et `docs/EXPLOITATION.pdf` (#43) (remplacé le 11/10, voir le plan E2 : le guide s'envoie après la fusion de la PR #88). Le 15/10 : PR `develop → main`,
Definition of Done, tags `livrable-E1-v2` et `livrable-E3-v1`. Ensuite E4, E5 et E2 (15-25/10), et la carte #82
(Mistral UE). Oral blanc E1 + E3 : **29-30/10**.

**Retour du formateur, rencontre du 05/10 (dix minutes)** : trois étapes de traitement acceptées, système à garder
simple à expliquer ; E1 tenu à 5 pages, annexe permise ; RGPD : faire d'abord fonctionner, régions européennes,
choisir la région du modèle dans Azure (détail et réserves : `CONTINUITE.md` D, 05/10). **Examens blancs à partir du
26/10 environ**, deux sessions (l'une sur E1-E3 ou E1-E2, l'autre sur tout) : **périmètre et dates à confirmer** ;
Nadège et Elena aideront particulièrement à la présentation.

**Dans l'ordre, pour Era** :

0. **Demandé par le formateur le 05/10** : (a) lui envoyer par message où en est RITA (code, développement fait,
   ce qui reste) : texte préparé dans la conversation du 05/10 ; (b) lui envoyer **en message privé le lien du
   document de compétences**. **Corrections faites le 05/10 au soir** (35 lignes relues contre le dépôt et GitHub) :
   **110 OK, 24 PARTIELLEMENT, 1 A AJOUTER** sur 135, contre 100, 28 et 7 avant ; partie E1 (C1 à C5) : 28 sur 28.
   Puis, le même soir : colonne « Rédaction » réécrite pour les 9 compétences rédigées (C1 à C5, C8, C9, C12, C13,
   d'après les rapports E1, E2, E3 et la CI du 05/10 : **Era doit la relire et la dire avec ses mots**), 17 notes du
   03/10 périmées corrigées (dont 12 en E1), notes « format accessible » appuyées sur la mesure des PDF balisés, C16
   lignes 115 et 117 échangées ; idée d'une synthèse courte prise dans la grille d'un camarade (contenu non repris).
   Fichiers : `D:\KandaWork\RITA_PROJECT\Era-Preparation-livrables-RNCP_05_10_26_v2.xlsx` (le détaillé, fichier de
   travail) et `Era-Synthese-competences-RNCP.xlsx` (la synthèse, même contenu, colonnes pour les remarques du
   formateur). **Liens** : GitHub, branche à part `classeur-competences`, dossier `docs/competences/` (les deux
   classeurs et un README daté) ; Google Drive, synthèse convertie en Google Sheets (compte ganda70), à partager en
   « Commentateur » avant l'envoi. **Cette branche ne se fusionne pas
   dans `main` sans décision** : un tag `livrable-*` est figé, le classeur y resterait pour toujours. Décider avant la
   PR du 15/10 s'il fait partie de la remise au jury, et sous quelle forme (question à poser au formateur). Le seul
   « A AJOUTER » est C8.5 : il passe à OK quand le formateur accuse réception du guide d'exploitation corrigé
   (`f34486c`, #43). Garder envoi et réponse dans `evidence/C8/` s'ils touchent C8.
1. **Lundi 05/10, la revue hebdomadaire (15 min)** avec la trame `evidence/C16/revues/2026-10-05-revue-S41.md` : cocher les
   5 cartes proposées à Fait, ajouter au tableau les 7 issues ouvertes absentes, dire si la revue du 28/09 a eu lieu, garder
   2 cartes « En cours », remplir le §6, coller la ligne du §7 ici, commiter. Seul moyen de fermer C16.1. Vérifier au passage
   que le formateur a bien accès au tableau (C16.4, je ne peux pas le lire).
2. **Relire** `docs/rapports/E1/rapport-E1.pdf` (v2.5 du 11/10 ; avant, v2.2 du 10/10 ; la v2.1 du 04/10 avait corrigé cinq affirmations fausses, voir l'entrée
   du 04/10 plus bas) et `docs/rapports/E3/rapport-E3.pdf` (v1.4 du 11/10, 20 pages) ; corrections dans le chat.
3. *(remplacé le 11/10, voir le plan E2 : on note les nouveaux textes Azure contre Mistral Large 4.)* **Noter les 60 textes** de `evidence/C7/notes-francais-2026-10-03.csv` (0, 1 ou 2), **sans ouvrir** le fichier `-cle.csv`.
   C'est ce qui fait passer la recommandation C7 de « provisoire » à « argumentée ».
4. *(remplacé le 11/10, voir le plan E2 : le guide s'envoie après la fusion ; le message ci-dessous, qui cite encore Anthropic, est à mettre à jour avant tout envoi.)* **Envoyer au formateur** le message ci-dessous, à copier tel quel ; joindre `docs/EXPLOITATION.pdf` (régénéré le 03/10 au soir,
   deux phrases périmées corrigées). Garder l'envoi et la réponse dans `evidence/C8/` (#43, le seul 🔴 de E2).

   > **Objet** : RITA, deux points pour E2 (C7 et C8)
   >
   > Bonjour Elbby,
   >
   > Deux points sur le livrable E2, pour lesquels un retour, même court, m'aiderait.
   >
   > 1. C7, le choix du service de modèle. J'ai écrit le protocole avant de mesurer (`docs/PLAN-C7-benchmark.md`) et fait une première comparaison le 3 octobre : GPT-5.4 servi par Azure AI Foundry contre Claude Sonnet 4.5 servi par OpenRouter, sur dix cas tirés de mes données, trois répétitions chacun. Je mesure la conformité au garde-fou AMF, la fidélité aux chiffres fournis, la latence et le coût, avec des intervalles de confiance. J'ai aussi relevé les prix publics et ce que les fournisseurs publient sur l'environnement, c'est-à-dire très peu. Je note moi-même le français, à l'aveugle. Ma question : deux éditeurs comparés de cette façon, est-ce que cela répond au critère, ou attendez-vous un troisième service, par exemple Claude en direct chez Anthropic ?
   >
   > 2. C8, la documentation d'exploitation. Je vous joins le guide d'exploitation de RITA en PDF : accès et clés, installation avec ou sans Docker, tests, services externes, données, monitorage. Le critère demande qu'elle soit communiquée, votre accusé de réception me servira de preuve.
   >
   > Pour information, les rapports E1 (version 2) et E3 seront gelés le 15 octobre. Je vous enverrai le lien du tag à ce moment-là.
   >
   > Merci,
   > Eramalingam

   **Point 3 proposé le 04/10, à ajouter si tu es d'accord** (avant « Pour information ») :

   > 3. E1, la forme. Le rapport E1 est à 5 pages, la limite. Puis-je joindre les schémas (collecte, nettoyage, requêtes big data) en annexe hors du décompte, ou tout doit-il tenir dans les 5 pages ? Et à l'oral E1, sans démonstration, puis-je montrer des schémas et des extraits de code à l'écran ?

5. **Décisions** (une ligne chacune suffit, dans le chat ou à la revue) : **D7** documentation `/docs` publique en production
   (la règle de fermeture validée plaide pour la clé) ; **D6** lignes affichées d'emblée sur l'écran indicateurs (recommandé :
   rien avant le gel) ; ~~`memory_audit`~~ tranché le 10/10 : après le gel (#86) ; **#36** rafraîchir les données en ligne avant le
   gel ou après ; libellé du **drawdown** (cité 0 fois sur 60 textes).
6. 🌐 **GitHub** : activer les **alertes Dependabot** (Settings, Code security) ; capture des rulesets dans `evidence/C19/`.
7. 🌐 **Langfuse** : **capture de la liste des alertes revenues à l'état normal** (l'alerte 1 doit repasser à OK après le
   04/10 vers 15 h 18 UTC) et **capture du tableau « RITA C11 »** (`evidence/C11/README.md`, deux lignes « à faire »).
   Fait le 04/10 : traces factices supprimées, deux alertes réglées et mises à l'épreuve.
8. **C6** : capture du fil Discord du 16/08 dans `evidence/C6/` ; note de veille (remplacé le 11/10, voir le plan E2 : relevé S41 puis note S41, ou à défaut note S40 en rattrapage datée du jour, depuis `docs/veille/_candidats-2026-S40.md`).
9. 💻 **Ton PC** : rotation puis suppression des fichiers de clés en clair du Bureau. Facultatif : `ANTHROPIC_API_KEY` dans le
   fichier d'environnement si tu veux mesurer Claude en direct (troisième fournisseur du banc).
10. Dire **« bon pour le gel »** : l'assistant ouvre la PR `develop → main`, puis les tags `livrable-E1-v2` et `livrable-E3-v1`
    se posent le **15/10** (`docs/FILE-DE-VALIDATION.md`, `scripts/verifier_livrable.py`). La publication de l'image sur ce tag
    sera la **première jamais exécutée** : à relever comme preuve C19 (tâche T8).


**Après le gel (du 15 au 25/10), dans l'ordre, test d'abord pour tout code** (dates précisées le 11/10 : contenus
terminés le 20/10, gel final le 23/10 ; ce qui ne tient pas avant va dans « ce qui n'est pas fait ») : #75 (S5 ticker borné, S6 panne des
fournisseurs, S4 refus journalisés, S3 limite de débit, S1 en-têtes de sécurité), #73 (clé mémorisée trop tôt), #74
(compression, cache, favicon, puis remesure Lighthouse), #76 (rôle `rita_api` en lecture, sur plan), #23 (épinglage), #35 ;
**déploiement du code sur Hetzner**, mesure Lighthouse de la production, rotation de clé éprouvée, **contrôle du certificat
(il expire le 18/11, avant le jury)** ; rapport E4 (T10 à T12), **pull request prête le vendredi 23/10**, tag
`livrable-E4-v1` le 25/10. **Ensuite** : conclusion C7 (#33), E2 (#34), E5 (#41), tout envoyé le **05/11**.

**État des épreuves au 04/10** :

| Épreuve | Décompte | Ce qui manque surtout |
|---|---|---|
| E1 | v2.5 du 11/10, 5 pages (cinq surgénéralisations corrigées ; v2.4 : MCD lisible, prérequis d'installation, T4, positions simulées, numéros de page ; v2.3 : § 7 RGPD réécrit, ordre d'installation, connexions, scout, tables hors MCD ; la v2.2 du 10/10 : date, chiffres des tests datés, `memory_audit` reporté, texte alternatif du schéma) ; vérifiée contre le code et la base le 04/10 | ta relecture ; question de l'annexe au formateur ; gel le 15/10 |
| E2 | 6 ✅ · 13 🟠 · 1 🔴 sur 20 | banc C7 Azure Data Zone EU contre Mistral Large 4 et notation à l'aveugle des nouveaux textes ; guide renvoyé après la fusion de la PR #88 (C8.5, #43) |
| E3 | v1.4 du 11/10, 20 pages · 35 ✅ · 4 🟠 · 0 🔴 sur 39 lignes (44 critères du référentiel) | ta relecture ; les 4 🟠 se ferment après le gel (#73, #75, accessibilité de l'outil, serveur non tracé) ; gel le 15/10 |
| E4 | 27 ✅ · 9 ⚠️ · 0 ❌ sur 36 | rapport à rédiger ; C16 (revues notées) ; C17.1, .2, .5, .8, .11 ; C19.4 au tag du 15/10 |
| E5 | non recompté | rapport ; #70 restauration ; C20 et C21 |

**Manques ouverts nés du 04/10** : aucune contrainte ne borne la clôture entre bas et haut (23 lignes hors bornes en base,
déclaré dans E1) ; pas d'alerte de silence (deux alertes seulement au palier gratuit) ; seuil de latence à revoir après une
semaine de traces ; DPA Langfuse identifié mais non lu (transfert à confirmer) ; le docstring de `db/rgpd_purge.py` dit
encore P1 et P2 « automatisés » alors que le registre et E1 disent « lancement manuel » (après le gel) ; la skill
`tester` du dépôt cite encore « 477 passed, 19/09 » ; l'encadré « D'où vient ce texte ? » de l'écran 3 ne cite pas les
13 indicateurs désormais transmis au rédacteur (après le gel) ; deux mesures de fraîcheur coexistent (âge calendaire
pour le prompt, jours de bourse pour le monitorage) : à documenter côte à côte, ce n'est pas en soi un défaut ; la
tournure « vérifier si le rebond du jour se prolonge » est à ajouter au jeu d'évaluation comme cas limite, avec son
résultat attendu écrit et une phrase de comparaison purement descriptive en regard, pour mesurer à la fois les
recommandations manquées et les refus inutiles (`evals/` : zone sous garde, plan d'abord) ; la tuile « Générations par
fournisseur » du tableau C11 comptait `briefing-llm` (données du 02/10) : filtre corrigé par l'API le 04/10 au soir,
puis tuile renommée « Tentatives par fournisseur (échecs compris) » : la barre Anthropic ne comptait que des
échecs (`evidence/C11/README.md`) ; tableau et alertes vérifiés à l'écran après la correction ;
restent l'axe à zéro (aucun réglage dans l'API, éditeur de la tuile à regarder) et les deux captures datées à ranger. E1 et ses deux schémas disaient
278 457 cotations, la base en compte 278 473 (dernier cours le 02/10) : corrigé le 04/10.
**Décidé par Era le 05/10, après le gel du 15/10, dans cet ordre** : 1) corriger les indicateurs existants, test
d'abord (RSI d'une série plate #78, pire baisse positive en hausse continue #79, libellé « depuis le 1er janvier » #80) ; 2) vérifier
la fidélité du texte aux faits fournis (chiffres, devises, dates) ; 3) expliquer les 13 indicateurs à l'écran ; 4) un
seul nouvel indicateur, l'ATR en % (#83), spécification d'abord dans `docs/indicateurs/CONCEPTION.md` ; comparaison à un indice
(après résolution du décalage cours ajustés des dividendes contre indice de prix), ADX, concentration et corrélations,
fondamentaux : après la certification. **Règle « UE seule », choix du projet posé par Era le 05/10** (pas une exigence du
référentiel, qui demande le respect du RGPD) : non tenue au 05/10 par T6 (fournisseurs du modèle, #82) et T7 (Google News, #81),
inscrits au registre ; à prouver dans E2 (C7, choix des services d'IA) quand il sera repris.
**Rapport E4, à son écriture (figures déjà prêtes, relues le 04/10)** : § 1 « Analyser le besoin » (C14), la planche
`evidence/C14/WIREFRAMES-C14-ecran-portefeuille.png` à côté du récit utilisateur du portefeuille (valeurs
d'illustration, vérifiées différentes des positions réelles) ; § 2 « Cadre technique » (C15),
`docs/conception/donnees/schema-architecture-donnees.svg` comme conception de septembre, observé et proposé
séparés, et `E3-architecture` pour l'application actuelle ; § 1 aussi, la planche
`evidence/C14/WIREFRAMES-C14-ecran-briefing.png` à côté du récit utilisateur du briefing, avec sa légende « redessinée
après l'implémentation, le 03/10 », et un renvoi depuis § 4 « Développer » (C17) ; § 1 encore, la planche
`evidence/C14/WIREFRAMES-C14-ecran-indicateurs.png` à côté du récit utilisateur des indicateurs, légende « spécification
reconstituée après le code, 03/10/2026 » (elle explique l'écran, elle ne prouve pas une spécification antérieure ;
relue le 04/10 contre `frontend/indicateurs.js` : deux appels en parallèle, 13 colonnes, lot 1 gardé si le lot 3 échoue) ; en améliorations futures, un
renvoi aux maquettes de la refonte (`docs/conception/frontend/refonte-2026-10.md`, § 12), jamais présentées comme
l'application actuelle. Le flux C15 du 18/08 reste une preuve historique (`evidence/C15/`).
**Décidé par Era le 04/10** : les mentions historiques d'un guide d'étude dans `CHANGELOG.md` et `evidence/C21/INC-005` restent
telles quelles (elles racontent comment un défaut a été trouvé ; la préparation personnelle, elle, vit hors du dépôt).
Restent ceux du 03/10 : aucune alerte quand la chaîne est rouge (INC-007) ; seize indicateurs spécifiés, treize reçus par
le briefing, drawdown jamais cité ; production sans en-têtes de sécurité ni limite de débit, API en rôle propriétaire en base, écran 3
qui mémorise la clé trop tôt, tableau Kanban décroché du travail réel.

**Verrous** : le dépôt est privé (jury et formateur invités) ; `main` et les tags `livrable-*` sont protégés par GitHub ;
zones sous garde (`db/schema.sql`, `guardrails/`, `evals/`) : rien sans plan validé ; aucun code sur le serveur avant le 15/10.


---

🏁 **04/10 : E1 et E3 complétés, puis vérifiés contre le code.** Demande d'Era à 8 h 32 : finir E1 et E3, vérifier
les schémas par critère. **E3** : étape « Tester les données » dans la
chaîne (`002a0b7`), `docs/ARCHITECTURE.md` et trois schémas (`067fb25`), 15 traces factices supprimées par Era (API : 7
traces, 0 « prompt test »), **deux alertes Langfuse réglées et mises à l'épreuve** (erreurs de fournisseur : vraie, 4
erreurs du 03/10, deux Foundry et deux Anthropic, faute de clés, la cascade a servi ; latence : **fausse alerte**, seuil saisi en secondes alors que
Langfuse compte en millisecondes, corrigé à 15 000), titre des issues d'alerte réparé test d'abord (`f42697d`), preuve C11
(`bed00b6`), **rapport E3 v1.1 : 35 ✅ · 4 🟠 · 0 🔴**, 20 pages (`8a6037b`). **E1** : deux schémas générés depuis le
code et tenus par 12 tests (`854bc21`) ; en cherchant les lignes exactes pour le guide, **cinq affirmations fausses**
trouvées et revérifiées en base : un index partiel sur les volumes qui n'existe pas (cité deux fois), un `HAVING` qui est
un `WHERE`, un transfert Langfuse dit « fermé » au lieu de « à confirmer », une contrainte `CHECK` sur les clôtures qui
n'existe pas ; **E1 v2.1**, 5 pages (`65aa70b`, `33dbd62`). `CLAUDE.md` et `AGENTS.md` remesurés (`638b65c`, `7e630d7`).
CI verte sur `33dbd62` : 793
passed, 29 skipped, 2 xfailed, 94,70 % ; poste : 820 passed, 2 skipped, 2 xfailed.

🏁 **03/10, nuit : Foundry répond, et le banc C7 compare enfin deux éditeurs.** Clé posée par Era ; un 400 « `max_tokens` unsupported » corrigé en `max_completion_tokens` (test d'abord) ; briefing réel SAN.PA servi par Foundry en 5,6 s sans repli (trace à une génération). **Quatrième passage du banc** : Foundry `gpt-5.4` et OpenRouter `claude-sonnet-4.5` indiscernables sur les contrôles automatiques (30/30 conformes et fidèles chacun, Wilson [0,89 ; 1,00]) ; Foundry médiane 3,2 s mais p95 10,7 s, OpenRouter 6,3 s et 7,2 s ; coût 0 pour le projet contre 0,0060 USD. Recommandation **provisoire** : Foundry en premier, OpenRouter en secours (l'ordre actuel), à confirmer par la notation du français d'Era (`notes-francais-2026-10-03.csv`, **60 textes**, deux services confondus). E2 : 6 ✅ 12 🟠 2 🔴. Preuve §9.

🗓️ **03/10, nuit : trame de la revue du lundi 05/10 préparée (T6)** (`evidence/C16/revues/2026-10-05-revue-S41.md`), revue **non tenue**. Faits relevés : 13 issues fermées en S40, dont **3 seulement suivies au tableau** ; **18 issues jamais ajoutées au tableau** (toutes créées le 03/10) ; colonne « En cours » à 1 carte alors qu'au moins quatre chantiers sont ouverts ; **aucune trace de la revue du 28/09** (à dire tel quel, sans reconstituer). Cinq cartes proposées à Fait avec preuve (#24, #25, #27, #55, #57), six refusées avec la raison (dont #39 : `stop_reason` jamais lu).

🔑 **03/10, nuit : T5 faite, droits d'accès défendus par écrit** (`evidence/C17/preuve-droits-acces-2026-10-03.md`). Choix : un utilisateur, une clé, pas de comptes (décision D10) ; données de démonstration seulement ; modèle de menace en huit lignes ; **la matrice d'accès validée par le formateur confrontée au code, case par case**. Tient : aucun accès sans clé (403 mesuré en production), portefeuille MCP servi seulement en démonstration vérifiée, aucune position envoyée au modèle, articles bloqués filtrés, aucun outil MCP pour `/briefing`. **Écart trouvé (E1, carte #76)** : l'API et le scout lisent la base avec le **rôle propriétaire**, alors que la matrice leur donne la lecture seule ; et le rôle `rita_lecture` n'est utilisé par aucun code. La documentation publique (`/docs`) est hors matrice : **la règle de fermeture validée plaide pour la mettre derrière la clé** (décision D7). Procédure de rotation de la clé proposée, à éprouver au déploiement. C17.5 reste ⚠️ (conforme au besoin, pas encore à la spécification). Carte #26 fermée. Prochaine tâche : T6, la revue du lundi 05/10 (C16) : **c'est toi qui la tiens**, je prépare la trame.

🛡️ **03/10, nuit : T4 faite, revue OWASP Top 10:2025 écrite** (`evidence/C17/revue-owasp-top10-2025-2026-10-03.md`). L'édition en vigueur est **2025** (l'adresse officielle y redirige) : l'injection y est A05, et non plus A03 comme le dépôt l'écrit encore. Tenus : contrôle d'accès (403 en production sans clé et avec une fausse clé), cryptographie (TLS 1.3, 1.0 et 1.1 refusés), injection SQL et HTML, intégrité, conditions exceptionnelles. **Le point faible est la configuration** : aucun en-tête de sécurité en production, documentation de l'API publique. Partiels : chaîne d'approvisionnement (Dependabot désactivé, dépendances de développement non épinglées), conception (**aucune limite de débit sur un appel payant**), authentification, journalisation (**les refus de clé ne laissent aucune trace**). Deux faits **mesurés** par une sonde : un ticker de 5 000 caractères passe en entier dans le journal et la réponse ; la panne de tous les fournisseurs donne un 500 sans fuite, mais **pas le 502 que ma spécification de l'écran 3 décrivait** (corrigée, wireframe redessiné). Aucun secret dans l'arbre ni dans les 313 commits. **Le certificat expire le 18/11, avant le jury** : renouvellement à contrôler fin octobre. Corrections regroupées : carte #75, après le 15/10. **Pour toi** : décision D7 (documentation `/docs` publique en production : la garder pour la démonstration, ou la mettre derrière la clé ?) et activer les alertes Dependabot (Settings, Code security). C17.8 reste ⚠️ (revue faite, préconisations pas toutes implémentées). Recompte inchangé : 27 ✅, 9 ⚠️. Prochaine tâche : T5, défendre les droits d'accès par écrit (D1).

🌿 **03/10, nuit : T3 faite, éco-conception et accessibilité mesurées** (`evidence/C17/preuve-eco-conception-et-accessibilite-2026-10-03.md`, Lighthouse 13.5.0 en mode flux, EcoIndex avec le code officiel `cnumr/ecoindex_python`, parcours au clavier). **Accessibilité : 100 sur 100 et zéro échec aux 10 étapes**, bureau et mobile ; clavier : ordre logique, focus visible, focus placé sur le résultat du briefing, aucun piège. **EcoIndex : A (portefeuille, 90), A (briefing, 90), D (écran indicateurs avec 111 valeurs, 51)** : la cause est le nombre d'éléments de la page (1 860), pas son poids ; la compression, mesurée, fait passer 51 à 52. **Constats** : aucune compression ni aucun en-tête de cache, ni en local ni en production ; `favicon.ico` en 404 ; **la production sert encore les pages du 19/08 et n'a pas l'écran briefing (404)**. Corrections regroupées dans la **carte #74, après le tag du 15/10**, puis remesure (tableau avant/après). **Décision D6 d'Era** : réduire les lignes affichées d'emblée sur l'écran indicateurs ? (seul levier sur la note ; recommandation : pas avant le gel). Recompte : **27 ✅, 9 ⚠️, 0 ❌**. Prochaine tâche : T4, la revue OWASP écrite (#29).

📐 **03/10, soir : T2 faite, les écrans 2 et 3 spécifiés** (`evidence/C14/preuve-specifications-ecrans-2-et-3.md` : US-2 et US-3, 9 et 8 scénarios, 15 et 14 critères d'acceptation avec le test qui les vérifie ou la mention « lecture du code », wireframes d'état en `.drawio`, `.svg` et `.png`). **Écrit après le code, dit en tête du document.** Trois trouvailles : (1) **défaut sur l'écran 3**, la clé est mémorisée avant d'avoir fonctionné (carte #73, correction après le tag du 15/10, test d'abord) ; (2) **erreur de référence RGAA** dans la spécification de l'écran 1 et deux étiquettes de tests : les messages de statut sont la règle 7.5 du RGAA 4.1.2, pas 12.x ni 4.x (erratum daté, étiquettes corrigées) ; (3) l'écran 2 appelle « Pire baisse » ce que le prompt appelle « Drawdown » : à rapprocher du 0 sur 60. **Recompte mis à jour : 26 ✅, 10 ⚠️, 0 ❌** (C14.3 passe à ✅). Prochaine tâche : T3, mesurer éco-conception et accessibilité des trois pages (**décision D2 d'Era attendue**, Lighthouse via `npx` télécharge un paquet).

📋 **03/10, soir : T1 faite, les 36 critères de E4 recomptés : 25 ✅, 11 ⚠️, 0 ❌** (`docs/rapports/E4/recomptage-criteres-2026-10-03.md`). C19 gagne un ✅ (documentation de la chaîne), C16 en perd un (aucun compte rendu daté de revue du lundi). Les 11 ⚠️ : C14.3 (user stories des écrans 2 et 3), C16.1, C16.3, C16.4, C17.1, .2, .5, .7, .8, .11, C19.4. **Pour toi** : (1) regarder dans les paramètres du projet Kanban si le formateur y est bien en lecture (C16.4, je ne peux pas le lire) ; (2) tenir la revue du lundi 05/10 et en écrire le compte rendu daté (C16.1). Prochaine tâche : T2, user stories et wireframes des écrans 2 et 3 (#24).

🚨 **03/10, soir : la CI était rouge depuis 1 h 20 sans que personne le sache (INC-007)**, trouvée en commençant le recomptage E4 (T1). Dix exécutions rouges consécutives de Tests et de Livraison sur `develop`, du commit des 13 indicateurs (`b54d65e`) à `46aab59` : quatre tests du scout atteignaient la vraie base par le RSI, verts sur le poste (un fichier d'environnement donne une base), rouges en CI. Reproduit en vidant les variables du modèle d'environnement, corrigé par une fixture (`0e53ede`), **Tests et Livraison verts** sur ce commit. `main` n'a jamais été touchée, aucune image publiée. Fiche : `evidence/C21/INC-007-ci-rouge-scout-base-reelle.md`. **Règle ajoutée** : après un push sur `develop`, lire `gh run list --limit 3` avant de dire « c'est fait » ; mes « 803 passed » des dix commits ne regardaient que le poste. À proposer à Era : une garde dans `conftest.py` qui interdit à la suite d'atteindre la base hors des tests marqués pour cela.

🔢 **03/10, soir : les indicateurs du briefing, mesurés** (`evidence/C7/indicateurs-cites-dans-les-textes-2026-10-03.md`, script `evidence/C7/mesure-indicateurs-cites.py`). La spécification compte **16 indicateurs** (11 + 2 + 3, `docs/indicateurs/CONCEPTION.md` §4) ; le briefing en reçoit **13** (les 10 du socle par valeur et les 3 du risque) : manquent le volume relatif (requête R3, jamais appelée par le scout) et les deux indicateurs de portefeuille (poids de ligne, exposition par devise), qui supposeraient d'envoyer les positions au modèle. Sur les 60 textes du 4e passage, un texte cite en moyenne **9,3 indicateurs sur 13** chez Foundry et **8,0** chez OpenRouter ; **le drawdown n'est cité par aucun des 60 textes**, le seul indicateur à zéro. Cause non établie. Décisions d'Era (sans urgence, rien avant le gel) : laisser tel quel, reformuler le libellé du drawdown et remesurer, ajouter les indicateurs absents (les positions demandent d'abord le registre RGPD).

📍 **03/10, soir : le banc journalise l'origine de chaque appel** (test d'abord, 6 tests rouges puis verts ; `Reponse.origine`, en-tête `x-ms-region` pour Foundry, champ `provider` pour OpenRouter, colonne `origine` et compte `origines` par fournisseur). Suite : 803 passed, 2 xfailed, 94,99 %. Mesure réelle sur 10 cas (`evidence/C7/passage-origine-2026-10-03/`) : Foundry **Sweden Central** 10 sur 10 ; OpenRouter a servi Claude par **Amazon Bedrock** 10 sur 10, et non par Anthropic. Les 60 appels du quatrième passage restent sans origine. Preuve : `evidence/C7/preuve-benchmark-2026-10-03.md` §10.

💵 **03/10, soir, après le banc : prix public et information environnementale relevés** (`evidence/C7/prix-et-environnement-2026-10-03.md`, chaque lien contrôlé). `gpt-5.4` : 2,50 et 15,00 USD par million de jetons (billet Microsoft du 05/03/2026 ; la page de tarifs Azure affichait encore `$-` le 03/10) ; `claude-sonnet-4.5` : 3,00 et 15,00 (API OpenRouter). Au prix public, 0,0047 contre 0,0060 USD par briefing : la recommandation provisoire tient sans la gratuité. Environnement : Microsoft publie des chiffres d'entreprise vérifiés (FY25 : 21,1 Mt CO2e, +62 % sur 2020 ; 100 % renouvelable direct ; PUE 1,17) ; **OpenAI et Anthropic ne publient rien par modèle** (0,34 Wh par requête moyenne chez OpenAI, sans méthode ; page inexistante chez Anthropic) : écrit comme inconnu, ordre de grandeur 0,3 à 18 Wh par briefing donné comme hypothèse. C7.5 passe de 🔴 à 🟠 dans E2. Région mesurée ensuite par une sonde de 5 jetons : `x-ms-region = Sweden Central` (Era hésitait entre trois régions européennes) ; limites de débit lues dans les en-têtes : 2 500 requêtes et 250 000 jetons par fenêtre ; fiche du modèle : sortie plafonnée à 128 000 jetons. Type de déploiement lu par Era dans le portail : **Global Standard**, donc n'importe quelle région Azure peut traiter un appel (Sweden Central ce soir) ; les prompts, sans donnée personnelle, peuvent sortir de l'Union européenne ; écrit dans la preuve et dans E2.

☁️ **03/10, nuit : Azure AI Foundry devient le premier fournisseur, par son point compatible OpenAI** (décision d'Era : sa ressource Foundry sert `gpt-5.4`, gratuite pour lui, pour les tests et la démonstration ; OpenRouter reste le secours). `src/llm.py` : `_appel_foundry` en httpx (chat completions, `Bearer`, le déploiement comme nom de modèle), plus de client Anthropic-sur-Foundry, 4 tests écrits avant ; modèle d'environnement, guide d'exploitation, plan C7, preuve C8, rapports E2 et E3 à jour. Conséquence pour C7 : la cascade porte maintenant **deux éditeurs** (GPT par Foundry, Claude par Anthropic et OpenRouter), la question du périmètre au formateur devient une confirmation. **Bloqué par les clés** : les trois variables `AZURE_FOUNDRY_*` ne sont pas dans l'environnement du poste ; Era les pose dans `.env` (jamais touché par l'assistant), puis une sonde et le banc donnent la première vraie comparaison.

📊 **03/10, nuit : les 13 indicateurs entrent dans le prompt du rédacteur** (décision d'Era). Le scout en calculait treize, le modèle n'en recevait que quatre nombres ; les neuf autres vivaient sur l'écran 2 sans l'atteindre, et le RSI n'était même pas joint au dictionnaire du scout. Tests d'abord (prompt, scout, graphe, banc), bloc « faits à décrire, jamais des signaux », volatilité sans signe, absent = « non disponible ». Banc C7 refigé et relancé (troisième passage, qui fait foi) : 30/30 conformes et fidèles, médiane 6,3 s, 797 jetons en entrée, 0,0060 USD par briefing ; 30 textes sur 30 citent le RSI, 25 la volatilité, aucun mot de signal. Point à surveiller écrit dans la preuve : « RSI à 24,2, forte pression vendeuse » est une lecture, pas un conseil, le garde-fou l'accepte ; à mettre dans le jeu d'évaluation. **La notation du français porte sur ce troisième jeu** (`notes-francais-2026-10-03.csv`).

🖥️ **03/10, nuit : le troisième écran, le briefing, est construit** (décision d'Era, « do it »). `frontend/briefing.html` et `briefing.js` : champ ticker avec l'univers en liste déroulante, `POST /briefing` avec la clé, texte en paragraphes par `textContent`, verdict du garde-fou en mots, identifiant de requête affiché, 502 dit « introuvable », 403 redemande la clé, attente annoncée. 17 tests statiques et 2 tests navigateur écrits avant (API interceptée, aucun appel payant), puis un briefing réel capturé : `evidence/C10/ecran-briefing-2026-10-03.png`, `preuve-ecran-briefing.md`. Rapport E3 : C10 « tous les points de terminaison intégrés » passe à tenu, **33 ✅ · 6 🟠 · 0 🔴**, PDF regénéré. **Pour la démo de l'oral E3** : l'écran 3 avec une vraie valeur, puis la trace Langfuse de la même requête par sa référence.

📏 **03/10, nuit : le banc C7 existe et a tourné une fois** (D1 à D3 = A sur « ok do it »). `evals/benchmark_fournisseurs.py` écrit test d'abord (34 tests), `agents.analyst.construire_prompt` extrait sans changer le rédacteur ; jeu de dix cas figé ; **un seul fournisseur mesurable** (OpenRouter, second passage sur le prompt corrigé de la carte #57 : 30/30 réussis, 30/30 conformes AMF, 30/30 fidèles, Wilson [0,89 ; 1,00], médiane 5,6 s, p95 7,4 s, 0,0045 USD par briefing ; avant #57, 5 textes sur 30 appelaient des capitaux des « titres échangés », 0 après), Foundry et Anthropic indisponibles faute de clés : **aucune comparaison encore**. Preuve `evidence/C7/preuve-benchmark-2026-10-03.md` ; français à noter par Era (`notes-francais-2026-10-03.csv`). Incident INC-006 bis trouvé et corrigé (22 traces parasites écrites par la construction du jeu, supprimées, verrou posé et testé). Couverture passée sous 90 % avec le script puis remontée par ses tests. **Reste à Era** : question au formateur (périmètre C7), clés Foundry et Anthropic sur le poste, notation à l'aveugle, puis relancer le banc.

🧭 **03/10, nuit, après la clôture : deux relectures extérieures vérifiées ligne à ligne, et ce qui en découle.** E1 v2 : trois phrases fausses corrigées (gel prévu, mix des cinq types de sources, le scout lit la base et `rita_lecture` n'est utilisé par aucun outil), PDF regénéré, 5 pages. C6 : synthèse S33 à S36 rapatriée dans `docs/veille/` et rendue reproductible (`scripts/synthese_veille.py`), étiquettes ISO de S35 et S36 corrigées sans antidater, protocole remis à la vérité (aucune tâche planifiée, relevé manuel, `sources/rss.py` n'est pas l'outil de veille), état réel de la récurrence écrit (S37 à S40 sans note). C7 : **aucune mesure n'existe** ; les scores du brouillon de juillet (4,05, 4,35…) sont des exemples d'un gabarit, à ne jamais citer ; `docs/PLAN-C7-benchmark.md` écrit, trois décisions D1 à D3 attendues d'Era et une question au formateur, aucun appel payant avant. C8 : `evidence/C8/README.md` indexe les preuves réelles (un seul fournisseur opérationnel, dit tel quel) ; `docs/EXPLOITATION.md` corrigé (cascade dans l'ordre du code, Foundry ajouté, taux manquant selon le plan 65, FRED et flux à jour). E2 : `docs/rapports/E2/rapport-E2.md` v0.1, C6 et C8 rédigés depuis les faits, C7 vide par construction. **Reste à Era** : captures de partage Discord, note S40, décisions D1 à D3 du banc, envoi du guide au formateur (#43).

📚 **03/10, nuit : `evidence/C18/` créé et `docs/CI-CD.md` écrit (carte #27 fermée)**. Preuve C18 depuis l'API GitHub : 268 exécutions du workflow Tests depuis le 28/07, 97 vertes sur les 100 dernières, les 3 rouges expliquées (19/08 couverture dépendante de la machine, 20/09 dépendance manquante attrapée par la CI, 28/09 pandas construit depuis les sources), ce que la CI saute (16 tests Spark, 12 tests base réelle). `docs/CI-CD.md` : cinq workflows, tous les déclencheurs, étapes, secrets et permissions, installation sur un clone neuf, test de la chaîne, quoi faire quand c'est rouge. Les six critères C18 passent à ✅ ; dans le rapport E3, les deux critères C13 de documentation aussi : **32 ✅ · 7 🟠 · 0 🔴**.

📝 **03/10, nuit : rapport E3 version 1.0 rédigé** (`docs/rapports/E3/rapport-E3.md`, 9 600 mots environ, rendu en PDF de 20 pages par le nouveau `scripts/rendre_pdf.py`, pages relues). Depuis la v0.1 du matin : première trace Langfuse complète d'un vrai briefing (03/10 14 h 48, 10 observations, note `conforme_amf = 1`, même `request_id` dans la réponse, le journal et la trace), tableau « RITA C11 » construit, chaîne d'alerte exécutée une fois (#71), journal `mcp_calls` (cinq lignes pour quatre appels), verrou de démonstration de la passerelle, rulesets GitHub (`pytest`, `evals`, `revue` requis), 742 tests, 93,92 %, les deux remarques de la revue de la PR 58. Bilan des 39 critères : **30 ✅ · 9 🟠 · 0 🔴** (v0.1 : 27, 11, 1). Trois dossiers de preuves créés depuis des exécutions réelles : `evidence/C9/`, `evidence/C12/preuve-suite-de-tests-2026-10-03.md`, `evidence/C13/` ; `evidence/README.md` réindexé. **Reste à Era avant le 15/10** : relire les 20 pages ; clics Langfuse (15 traces factices, 2 alertes, capture du tableau) ; décision `memory_audit` ; puis PR `develop → main`, tags `livrable-E1-v2` et `livrable-E3-v1` (`docs/FILE-DE-VALIDATION.md`). **Non fait** : capture d'écran de l'interface Langfuse (session d'Era), déploiement du code sur Hetzner (après le gel), 422 pour un ticker inconnu, limite de débit.

📝 **03/10, nuit : rapport E1 version 2 rédigé** (`docs/rapports/E1/rapport-E1.html` et `.pdf`, 5 pages, imprimé par Chrome, chaque page regardée). Mis à jour depuis la v1 du 13/08 : dates de l'archive en date locale (INC-005), 10 tables et 1 vue, FRED stockée, vue sans taux supposé, clôture des positions et registre T1 à T5 / P1 à P6, Langfuse UE à la place du transfert hors UE, collecte planifiée et manifeste, 11 routes, 742 tests, encadré « ce qui a changé » et limites (date de clôture = date d'import, purges non planifiées, `memory_audit`, versions non épinglées). Fait avec : correctif TDD de la carte #55 (étape `ecb` en échec déclaré quand aucun taux n'est reçu, 2 tests), les quatre fichiers aux dates décalées corrigés (README, `bigdata/CONCEPTION.md`, schéma SVG et drawio, PNG regénéré). Suite : **740 passed, 2 xfailed, 93,92 %**. **Reste à Era avant le 15/10** : relire le rapport, trancher `memory_audit` (écrire ou retirer : une phrase du rapport en dépend), puis PR `develop → main` et tag `livrable-E1-v2` (`docs/FILE-DE-VALIDATION.md`).

✅ **03/10, nuit : PR #72 `develop → main` fusionnée** (`43025f9`, 2 commits : clôture des positions, plan 66, et l'état après la fusion de la PR 58) ; #66 et #69 fermés. Quatre constats d'un contrôle extérieur du dépôt traités avant la fusion : cache `commit-graph` de Git reconstruit (plus d'avertissement) ; arbre déjà propre (les 19 fichiers étaient le commit `1a5ecd9`) ; `main` locale remise au niveau de GitHub (199 commits de retard, avance rapide) ; le job `revue` ajouté aux checks requis du ruleset `main protegee` (`pytest`, `evals`, `revue`), aucune protection classique n'existe (`evidence/C19/`).

✅ **03/10, après-midi : la liste « reste à Era » traitée.** PR #58 **fusionnée** (`d1cec3b` sur `main`, six issues fermées) ;
bouton *Run workflow* testé pour de vrai juste après (issue #71 créée puis fermée comme démonstration) ; les trois migrations
rejouables + `roles.sql` jouées sur la base Compose (conteneur démarré pour ça) et sur la base Hetzner (`/root/rita-agent`,
code déployé encore à `1cefdae` du 20/08, données figées au 17/08) ; décisions #66 D1 à D4, #67, #63, #69 posées sur les
issues et dans le ledger (options recommandées, « do it » d'Era). **Non fait, et pourquoi** : suppression des 15 traces
Langfuse et réglage des 2 alertes (refusé à l'agent / pas d'API : clics d'Era) ; capture des rulesets (session GitHub
d'Era ; l'API est dans `evidence/C19/rulesets-2026-10-03.json`) ; fichiers de clés du Bureau : **inventaire fait, rien
ouvert, rien supprimé** (voir le message du 03/10), rotation à faire par Era.

🧹 **03/10, fin de journée** : description GitHub remise sur la décision du 16/08 (« Tracking et l'Analyse », plus
« Trading ») ; tableau des livrables du README réécrit (il disait encore « C11 non commencé », « E5 non commencé ») ;
**plus aucune trace d'outil** (« revue Codex », « Claude Code ») dans les textes visibles du jury, 73 remplacements dans 32
fichiers ; les notes de veille (citations), la preuve C10 du hook et la configuration de l'outillage restent telles quelles ;
les commits ne portent plus de ligne de co-signature. L'historique déjà poussé ne se réécrit pas (`main` protégée).

🧭 **Tâche principale depuis le 03/10 : intégrer le chapitre « Données » validé par le formateur** (« Très bon travail. Se montrera
utile à l'exécution. Rien à redire. »). Le chapitre est dans `docs/conception/donnees/` (README = tableau chapitre contre code au
03/10) ; dix issues `conception-donnees` portent les écarts ouverts. **Ordre** : 1) sans zone sous garde, test d'abord : `titre`
dans l'index (**#59 fait le 03/10**, 3 tests ; l'index du poste, 1 563 documents sans titre, se reconstruit à la collecte de 19 h), vérification de la démonstration dans la passerelle (**#60 fait le 03/10**, 5 tests : déclaration `RITA_MCP_PORTEFEUILLE=demo` et comparaison au jeu d'exemple), cartographie des 32 cas (**#61 fait le 03/10** : 23 ✅ 5 🟠 4 ❌, quatre tests écrits, deux issues ouvertes #69 D07 et #70 A08), manifeste de collecte (**#64 fait le 03/10**, 9 tests ; premier manifeste réel attendu à la collecte de 19 h dans `logs/`) ; vérification de la démonstration dans la passerelle, cartographie des 32 cas, manifeste de collecte ; 2) avec plan
validé par Era : `COALESCE` de la vue (**#65 fait le 03/10** sur plan validé D1 D2 D3 = A : 23 tests, migration jouée sur le poste ; **jouée sur Compose et Hetzner le 03/10 après-midi**, sorties dans `evidence/C4/`), `mcp_calls` (**#62 fait le 03/10** sur plan validé D1 D2 D3 = A : 21 tests, migration jouée sur le poste, premières lignes réelles ; **jouée sur Compose et Hetzner le 03/10 après-midi**, sorties dans `evidence/C20/`), clôture des positions (**#66 fait le 03/10** sur plan validé D1 à D4 = A : `date_cloture`, index unique de ligne, import en réconciliation, P2 applicable, P3 retirée, D07 #69 signalé à l'import ; **migration jouée sur le poste, Compose et Hetzner le 03/10 soir, import réel rejoué : 7 mises à jour, 0 insérée, 0 close**, 29 tests écrits avant, suite 738 passed, 2 xfailed, 93,91 %, preuve `evidence/C4/preuve-cloture-positions.md`) ; 3) décisions d'Era : quasi-doublons, `search_articles`.
Rien de ce qui touche `db/schema.sql` ne se code sans ce plan.

▶️ **PR #58 `develop → main`** : ouverte le 03/10 au soir (31 commits), relue par la revue automatisée (2 remarques, **corrigées le 03/10** :
`c4b1517`, `1ee721c`, 635 passed, 93,41 %), la revue automatisée n'a rien publié. Checks verts : **à fusionner** par Era
(`gh pr merge 58 --merge`) ; aucun tag, ce n'est pas un livrable.
Prochaine action, à la reprise : lire les commentaires de la revue automatisée sur
https://github.com/Ganda15/rita-agent/pull/58 ; chaque remarque vraie = un correctif et un test poussés sur `develop` ;
puis `gh pr merge 58 --merge` quand les checks sont verts. Aucun tag : ce n'est pas un livrable. Une fois sur `main`,
le bouton *Run workflow* d'`alerte-incident.yml` existe et le test manuel de la chaîne d'alerte devient possible.

🧭 **03/10, matin : reconnaissance complète, rien construit, deux notes Obsidian et deux lignes corrigées ici.**

Era a demandé de tout retrouver sans question. Lu et confronté : dépôt, GitHub, coffre, classeurs Excel, disque D:,
Bureau, skills. Résultat dans `Projets/RITA/00-Pilotage/RITA - Etat des lieux complet, plan initial et realise
(2026-10-03).md` (prévu contre réel, doublons, qui fait quoi) et dans `Projets/RITA/04-Certif/RITA - Verification
criteres RNCP C1-C21 (2026-10-03).md` (7 ✅, 13 ⚠️, 1 ❌ : C7). Le classeur
`D:\KandaWork\RITA_PROJECT\Era-Preparation-livrables-RNCP.xlsx` existe depuis le 14/08 et n'a **aucune case
cochée** : c'est ce que le formateur regarde la semaine du 05/10.

**Push fait le 03/10 à la demande d'Era** : dix commits, `2022689..a1c14e6` sur `origin/develop`, suite verte avant
(626 passed, 2 xfailed, 126 s), arbre propre après. **▶️ Ordre des prochaines actions** : 1) les fichiers de clés en clair du Bureau (Era seul : gestionnaire, suppression, rotation) ; 3) Langfuse : **tableau « RITA C11 » construit par l'API le 03/10** (3 tuiles), 15 traces factices exportées ;
restent à Era les clics de suppression (refusée à l'agent), les 2 alertes (pas d'API) et les captures ; le bouton
*Run workflow* attend la PR `develop → main` (`evidence/C11/preuve-langfuse-2026-10-03.md`) ; 4) **fait le 03/10** : le classeur Excel rempli critère par critère depuis la note (93 OK, 34 PARTIELLEMENT, 8 A AJOUTER, preuve en commentaire de chaque cellule, sauvegarde SAUVEGARDE3 à côté ; recompté le 05/10 dans le fichier enregistré le 03/10 à 15:08 : 100 OK, 28 PARTIELLEMENT, 7 A AJOUTER) ; puis E1 v2 (tag `livrable-E1-v2` le 15/10) et
le rapport E3. Pointeurs des skills et table de `CLAUDE.md` global : **corrigés le 03/10**. **`main` protégée côté serveur depuis le 03/10**
(GitHub Pro activé par Era, ruleset : PR obligatoire, `pytest` et `evals` verts ; **tags `livrable-*` figés** par un second ruleset le soir ; `evidence/C19/`) : capture d'écran de
*Settings → Rules* à ranger par Era.

---

🔎 **02/10, nuit : C11 construit de bout en bout dans le code ; il reste les clics dans Langfuse, et le push.**

Tout le volet 4 du plan du soir est codé, testé avant d'être écrit, et expliqué dans le journal Obsidian 018
(sections 2 à 13). Poussé le 03/10 au matin (`2022689..a1c14e6`, dix commits) ; ce paragraphe disait « rien n'est
encore poussé » jusque-là.

| Fait cette nuit | Preuve |
|---|---|
| Le garde-fou de sortie est prouvé **branché** sur `/briefing` : test d'API, mutation rouge puis verte | `tests/test_health.py`, `evidence/C17/preuve-garde-fou-sortie-branche.md` |
| Un refus écrit une ligne de journal (valeur, motifs, jamais le texte) ; le verdict AMF est sur la trace (métadonnées, niveau WARNING, note `conforme_amf`) | `tests/test_journal_refus_amf.py`, `tests/test_trace_verdict_amf.py` |
| **`request_id`** sur chaque réponse (`X-Request-ID`), dans le journal et comme identifiant de trace ; identifiant client douteux remplacé | `tests/test_request_id.py` (11) |
| La clé FRED ne s'écrit plus dans le journal de la collecte (`httpx` à WARNING) ; commentaire faux de `fred.py` corrigé | `tests/test_journal_pipeline.py` |
| Compose transmet les variables Langfuse au conteneur `api` | `tests/test_docker_compose.py` (3 ajoutés) |
| **Une trace montre tout le chemin** : `briefing` puis `scout`, `rag` (retriever), `garde-fou-entree`, `redacteur`, `briefing-llm`, `llm-<fournisseur>`, `garde-fou-sortie` ; test de trace à la Kaldera | `tests/test_trace_chemin.py` (8) |
| Une alerte Langfuse ouvre une issue `incident` (workflow `alerte-incident.yml`, bouton manuel, label créé, alerte répétée commentée) ; section « Monitorage Langfuse et alertes » dans `docs/EXPLOITATION.md` | `tests/test_alerte_incident.py` (7) |
| `evidence/C11/README.md` (9 critères : 5 tenus, 1 partiel, 3 à faire) ; **INC-006** écrit ; index C21 à jour (critères 3 et 5 ✅ depuis INC-005) | `evidence/C11/`, `evidence/C21/` |

**Mesures** (03/10 nuit) : `C:\Python314\python.exe -X utf8 -m pytest --cov -q` : **765 passed, 2 xfailed** (767 collectés, 59 fichiers) · couverture **94,19 %** (seuil 90) · garde-fous : entrée 100 % / 0 % FP, injection 70 % / 0 %, sortie 70 % / 0 %. *(02/10 : `C:\Python314\python.exe -m pytest -q` : **626 passed, 2 xfailed** (586 ce matin) · couverture **93,66 %**)*
(seuil 90 %), `api/main.py` et `graph/workflow.py` à 100 % · `scripts\verifier_liens.py` : 82 liens internes, 84 externes,
**0 cassé**.

**Ce qui reste du volet 4, et qui le fait** : Era, dans Langfuse : supprimer les 12 lignes de test (capture avant),
regarder la trace réelle complète, construire le tableau « RITA C11 » (3 widgets), régler les 2 alertes (canal GitHub
Actions, après une semaine de traces pour les seuils) ; sur GitHub : lancer une fois le workflow d'alerte à la main
(branche `develop`) et garder l'issue ; captures datées dans `evidence/C11/`. Sur le serveur : les trois variables
Langfuse, puis `docker compose up -d --force-recreate api`, après fusion dans `main`.

**Décisions d'Era en attente** : faire tourner la clé FRED (6 journaux locaux la contiennent en clair) ; un second
projet Langfuse `rita-dev` pour le poste ; `memory_audit` : écrire des empreintes ou retirer la table (`CONTINUITE.md` D).

**Volet du plan** : 1 ✅ · 2 ✅ · 3 ✅ · 4 ✅ côté code · 5 à 9 restent (enveloppe `<donnees_externes>`, `memory_audit`,
dossiers de preuves C9 C12 C13 C18, **rapport E3**, hygiène et tags).

**▶️ Prochaine action la plus petite : les 7 commits et le push (journal 018, section 13), puis le bouton Run workflow.**
Ensuite : `docs/rapports/E3/` commence (0 page au 02/10).

---

🔎 **02/10, soir : gel repoussé au 15/10, et une relecture complète du dépôt face à tous les briefs.**

Décision d'Era : **E3 et E1 gelés le jeudi 15/10**, pas le 11/10. Le formateur a annoncé un brief de création la semaine
du 05/10 ; l'audit chiffre le travail de E3 restant à 30 à 45 h. **Ce que le gel permet** : on ne construit plus rien,
mais on corrige ce que les retours de l'oral blanc (29-30/10) montrent, par une version taguée `v2`, jamais en silence ;
limites 05/11 (relecture d'Elbby) et 23/11 (jury). Écrit dans `CONTINUITE.md` F.

**Relecture du 02/10** (14 agents : 5 auditeurs, 5 contradicteurs, 3 chercheurs, 1 critique ; constats clés revérifiés
par commande) :

| Question du formateur | Réponse mesurée |
|---|---|
| **Garde-fous intégrés ?** | **Oui, mesurés.** `entree.py` 7 motifs, 100 % et 0 % de faux positifs ; `injection.py` 12 motifs, 70 % et 0 % ; `sortie.py` 9 motifs, 70 % et 0 %. Cible de 85 % déclarée non atteinte (`xfail` strict). Quatre manques à dire d'abord : l'enveloppe `<donnees_externes>` jamais branchée, aucun journal ni marque de trace au refus, aucun test d'API sur la substitution AMF, l'entrée qui ne voit aucun texte libre aujourd'hui |
| **Mémoire intégrée ?** | **Conçue le 28/07, à moitié construite.** M1, M2, M3 et M6 réelles ; M4 et M5 abandonnées pour la V1 (le modèle est le dernier nœud, un checkpointer ne sauverait aucun appel payant) ; `memory_audit` sans écrivain. **La décision n'était écrite nulle part** : elle l'est depuis ce soir, `CONTINUITE.md` D |

**Faits que la relecture a trouvés** : aucun `request_id` dans le code ; `docker-compose.yml` ne transmet aucune variable `LANGFUSE_*`, donc le conteneur ne trace pas ; la clé FRED est écrite en clair dans 6 journaux locaux (rapporté par un auditeur, non revérifié par commande) ; `README.md` (18/08) annonce 186 tests et « C11 non commencé » ; `CLAUDE.md` annonce 458 tests, 8 tables, 15 index (mesuré : 588 collectés, 9 tables) ; la table de compétences plus bas dans ce fichier contredit son propre en-tête (C11, C16) ; passerelles manquantes pour Velmo, Kaldera, Kaldera-A2A, Industrialisation, Factum : **écrites ce soir**, et la ligne fausse « RITA n'a aucun gate d'évaluation » corrigée.

**À ne pas faire (décisions écrites)** : pas d'endpoint A2A (aucun critère, 10 à 16 h, surface à état) ; pas de Prometheus et Grafana sur le serveur de 4 Go ; pas de checkpointer ; pas de NeMo Guardrails (Python 3.13 au plus) ; pas de changement d'outil de traçage ; pas de gestion des prompts dans Langfuse (dépendance réseau sur `/briefing`).

**Plan jusqu'au gel du 15/10** (heures de l'audit, dans l'ordre) :
1. Registre RGPD T3 corrigé, entité du DPA : addendum ClickHouse, Langfuse GmbH sous-traitant allemand (1 h)
2. Test d'API de la substitution AMF + une ligne de journal + le verdict sur la trace (2 à 3 h)
3. `request_id` : middleware, journal, identifiant de trace (2 à 3 h)
4. C11 visible : variables transmises au conteneur, spans `scout`, `rag`, garde-fous, tableau « RITA C11 », 2 alertes vers une issue GitHub, `evidence/C11/`, INC-006 (6 à 9 h)
5. Enveloppe `<donnees_externes>` branchée, tests de seuil de l'entrée, cas Giskard rejoués, test de l'ordre des nœuds (2 à 2,5 h)
6. `memory_audit` : écrire ou retirer (0,5 h ou 2 à 3 h) ; **tranché le 10/10 : décision après le gel (#86)**
7. Dossiers de preuves C9, C12, C13, C18 depuis les exécutions existantes de la CI (2 à 3 h)
8. Rapport E3 (6 à 10 h)
9. Hygiène : `README.md`, `CLAUDE.md`, commentaire de `test.yml`, `requirements.txt` épinglé, 422 pour ticker inconnu, retour arrière, tag `livrable-E1-v2` puis `livrable-E3-v1` (7 à 10 h)

**Après le gel** : revue du lundi pour C16 (5 entrées datées), note de veille S40 avec A2A, paquet E4 le 25/10, benchmark C7 sur les trois fournisseurs déjà branchés (remplacé le 11/10, voir le plan E2 : Azure contre Mistral Large 4).

**Non vérifié** : si Hetzner reçoit les clés Langfuse autrement ; l'existence d'un tableau ou d'alertes dans l'interface Langfuse ; la couverture du jour (suite non relancée) ; quel brief occupe la semaine du 05/10 ; deux notes de la phase 1 du programme (« modèle open source, mode d'emploi » et « l'agent qui a perdu la tête ») sans trace dans Obsidian.

~~**▶️ Prochaine action la plus petite : corriger le registre RGPD T3 (titre, date, entité du DPA).** Puis le test d'API de la substitution AMF, en TDD.~~ **Fait dans la nuit du 02/10** (bloc ci-dessus).

---

🔎 **02/10 : C11 devient réel. Première trace Langfuse de RITA, et deux défauts trouvés en la lisant.**

| Fait | Preuve |
|---|---|
| **Chaque appel au modèle est tracé** (carte #39) : `src/traces.py` (no-op sans clés), `src/llm.py` restructuré, un trace `briefing-llm` par appel avec une génération `llm-<fournisseur>` par tentative, usage en tokens, erreur du repli. **8 tests écrits avant** (rouge → vert), suite **586 passed, 2 xfailed** | `7cf3ffd` ; `tests/test_traces.py`, `tests/test_llm.py` |
| **Première trace réelle** : 02/10 18:39, Foundry et Anthropic en erreur, OpenRouter répond (`anthropic/claude-sonnet-4.5`, 27 tokens, 1,73 s) ; seconde à 19 h avec la hiérarchie | captures Langfuse d'Era ; projet `rita`, région UE |
| 🔴 **Trouvé dans Langfuse, pas dans le code : les tests écrivaient en production.** 12 générations « prompt test » → « ok anthropic » entre 18:25 et 18:38 : `api/main.py` charge le fichier d'environnement à l'import, les vraies clés restaient dans le processus, la cascade simulée traçait pour de vrai. Corrigé le jour même : test rouge puis fixture `couper_le_tracage` dans `tests/conftest.py` | même commit ; capture des 12 lignes avant suppression |
| 🟠 **Le poste de démonstration n'a qu'un fournisseur qui répond** : OpenRouter (clé neuve le 02/10). Pas de clé Foundry ni Anthropic en local. La cascade et son repli sont donc visibles à chaque appel, mais une panne OpenRouter = pas de briefing en démo | sortie des deux appels réels |
| Fichier d'environnement : deux faux départs instructifs (clés jamais écrites, puis les « … » de l'exemple collés à la place des clés) ; résolu par Era à la main, le hook `bloquer-secrets.py` ayant refusé 4 commandes de Claude qui nommaient le fichier, lecture comprise | session du 02/10 |

**Reste pour C11 avant le 15/10** : tableau « RITA C11 » (3 widgets), les 2 alertes du palier gratuit vers GitHub Actions (ouvrir une issue `incident`), `evidence/C11/` avec les captures datées, le nom de l'entité du DPA dans le registre. Décision à prendre : écrire la fuite des tests comme **INC-006** (`evidence/C21/`).

---

🔎 **29/09 : deux oraux blancs annoncés, le plan est réécrit, E3 passe devant.**

Message du formateur (échange avec Elbby et Nadège) : **29-30/10** oral blanc E1 (15 min) + E3 (20 min)
+ 10 min de retours ; **12-13/11** oral blanc en situation réelle, 90 min. Règle d'Era, posée le même
jour : **tout livrable gelé 2 à 3 semaines avant son oral**, la présentation se prépare sur du figé.

| Conséquence | Date |
|---|---|
| **E3 et E1 gelés** (rapport E3 écrit, C11 réel, Hetzner rafraîchi, dates du rapport E1 corrigées) | ~~dimanche 11/10~~ **jeudi 15/10** (repoussé le 02/10) |
| E4 gelé | 25/10 |
| Les cinq envoyés | 05/11 |
| Étude seule | 14 → 29/11 |

Calendrier révisé dans `docs/PLAN-12-SEMAINES.md` §5 ; décision et coût dans `CONTINUITE.md` D et F.
Langfuse (carte #39) avancé de S43 à **cette semaine**.

**▶️ Tâche principale (Era, 29/09) : E3 prêt pour l'oral blanc, gelé le 15/10 (repoussé du 11/10 le 02/10).** Prochaine action, la
plus petite : créer le compte Langfuse Cloud **région UE** (`cloud.langfuse.com`), lire le DPA, noter l'entité
qui traite dans le registre RGPD §T3 ; puis, en TDD, la trace d'un appel de `src/llm.py` (#39).

---

🔎 **28/09, dimanche soir : le ledger rattrapé, la veille S40 préparée, le traçage tranché.**

| Fait | Preuve |
|---|---|
| `CONTINUITE.md` et `CHANGELOG.md` avaient **9 jours de retard** (18 → 27/09) : rattrapés avec les vraies dates (9 décisions, 4 alternatives, 4 risques fermés, 6 ouverts) | `e8fd220` |
| Candidats de veille **S40** : fenêtre élargie au 14/09 faute de S38-S39, 4 candidats (dont l'injection « explosive », arXiv 18/09, qu'aucun motif de `guardrails/injection.py` ne couvre), 16 liens à `200` | `c497858`, `docs/veille/_candidats-2026-S40.md` |
| **Traçage : Langfuse Cloud, région UE, palier gratuit** (décision d'Era, règle du formateur « la condition = la sensibilité des données », mesurée : aucune donnée personnelle dans le prompt ; auto-hébergement impossible sur 4 Go ; LangSmith sans porte de sortie). Activation en **S43**, carte #39. Réserve : l'entité qui traite (Langfuse ou ClickHouse Inc.) à lire dans le DPA | `db/RGPD-registre-des-traitements.md` §T3 « Décision du 28/09 » ; `CONTINUITE.md` D et E |
| Collecte du 27/09 confirmée : 6/6 avec l'étape `fred`, 30 observations, 1 359 documents indexés | `logs/collecte-2026-09-27.log` |

**Quatre questions pour la revue de lundi** (section G de `CONTINUITE.md`) : ordre E4 / C7 en S40 · droits
d'accès (#26) · veille S37-S39 (#31, voies A ou B décrites dans le relevé S40) · ajouter le ledger à la fin
de session dans `CLAUDE.md`.

---

🔎 **27/09 : une relecture des chiffres contre la base a fait tomber cinq défauts de données, tous corrigés (INC-005).**
Cause unique : la place de cotation n'était modélisée nulle part (Paris, euros, UTC, sans férié, supposés partout).

| Défaut | Mesuré | Corrigé | Carte |
|---|---|---|---|
| Archive de 10 ans datée **un jour trop tôt** (date UTC au lieu de la date locale) | 52 426 cotations un dimanche | 0 ; MC.PA 01/08/2016 = 127,945 comme le docstring | #53 |
| HSBA.L figée depuis le 28/08 (un ticker seul = colonnes imbriquées non lues, sans erreur) | 0 ligne lue sur 20 | 127 cotations rattrapées, dernière 25/09 | #50 |
| FTI, SLB, HSBA.L étiquetées EUR ; HSBA.L en pence (×100) | 3 valeurs | USD, USD, GBP ; 15,122 £ | #47 |
| Cours scrapé rangé sous la date du samedi | 24 séances fictives | 0 | #49 |
| ZC.PA, ELE.PA, GTO.PA radiées mais OK, redemandées chaque soir | 3 échecs par soir | DELISTEE, non demandées | #48 |
| Fériés Euronext inconnus de la fraîcheur (et « 14 juillet férié » : faux) | | calendrier officiel dans `sources/marches.py` | #51 |
| FRED lisible mais jamais stockée | 0 table | `macro_observation`, étape `fred` à 19h00, route `/donnees/macro`, 30 obs. | #52 |

Sauvegarde avant toute écriture : `sauvegardes/rita-2026-09-27-avant-migration.dump`. Reconstruction en une transaction,
positions vérifiées inchangées (7). **42 tests écrits avant les correctifs**, suite **577 passed, 2 xfailed**.
Fiche : `evidence/C21/INC-005-archive-decalee-d-un-jour.md`. ⚠️ **Le rapport E1 cite des dates décalées d'un jour**
(« 28/07/2016 → 29/07/2026 ») : à corriger dans sa prochaine version (carte #56, S45).
✅ **PR #54 fusionnée par Era le 27/09 (`10ef31e`)** après la revue automatisée (un point P2 fondé, corrigé test d'abord :
l'étape `fred` est en échec quand aucune série ne répond, `4037a32`). Cartes #47 à #53 fermées avec leur preuve,
passées à « Fait » par l'automatisation. Même défaut sur l'étape `ecb`, antérieur : carte #55 (S40).
⏰ **Ce soir 19h00 : première collecte planifiée avec l'étape `fred`** ; lire `logs/collecte-2026-09-27.log`.

---

🔎 **26/09 : livre Packt « Building AI Agents for Finance » lu en entier. Rien à coder hors plan.**
4 éléments retenus, chacun rangé à sa semaine de `docs/PLAN-12-SEMAINES.md` : Wilson (S40, protocole
du benchmark C7) · traces et alerte de `src/llm.py` (S43, C11/C20) · journal d'audit de `/briefing`
(S43, C20) · trous des garde-fous (S44, C17 ; correctif testé sur une copie : 571 passed, 0 faux
positif sur 2 592 textes réels, 0/8 hors échantillon). Le reste est parqué.
⚠️ **Retard mesuré sur le plan** : S38 (monitorage instrumenté) et S39 (E4 rédigé) non faits ;
`docs/rapports/` ne contient que E1.

**▶️ Tâche principale (Era, 26/09) : retour au plan, S39 = rédiger le livrable E4 (C14-C19), puis le geler.**
✅ **Étape 1 faite le 26/09** : les 36 critères officiels confrontés aux preuves (skill `projet-rncp`) →
**21 ✅ · 11 ⚠️ · 4 ❌**, rapport E4 : 0 page. Détail, preuves `fichier:ligne` et plan d'action : Obsidian
`Projets/RITA/04-Certif/RITA - Vérification critères RNCP E4 (2026-09-26).md`. Trois constats :
- 🔴 **C16 (4 critères) n'est dans aucune semaine du plan** : 0 issue, aucun tableau, aucune méthode décrite.
- 🟠 **`livraison.yml` publie l'image avant de vérifier qu'elle démarre** (`:110` avant `:121`). La branche
  « publier sur tag » n'a jamais tourné (seul tag : `livrable-E1-v1`, antérieur au fichier).
- 🟡 `requirements.txt` : 13 dépendances sans version (l'image, elle, est épinglée).

✅ **C16 mis en place le 26/09 (décision d'Era : Kanban, tableau GitHub, revue du lundi)** : tableau
« RITA - Pilotage Kanban (livrables E2-E5) », https://github.com/users/Ganda15/projects/4 (privé, formateur
en lecture) ; **backlog = 24 issues (#21 à #44)** tirées du plan et de la vérification E4 (16 Backlog,
7 Cette semaine, 1 En cours) ; méthode : `docs/PILOTAGE-AGILE.md` ; preuve : `evidence/C16/preuve-mise-en-place-kanban.md`.
C16 passe de 0 à 2 ✅ + 2 ⚠️ (« tout au long du projet » ne vaut qu'à partir du 26/09).

✅ **#22 fermée le 26/09 (C19)** : `livraison.yml` construit sans publier, vérifie l'image construite
(sans la reconstruire), puis publie cette image seulement sur un tag. PR #46 fusionnée par Era (`556990e`) ;
`tests/test_livraison.py` 3 rouges puis verts ; suite locale 535 passed ; run Livraison `36247837793` :
image démarrée en 4 s, 403 sans clé, publication sautée hors tag. Reste à prouver : la publication, au
premier tag `livrable-E4-v1`. Première carte passée à « Fait » par l'automatisation du tableau.
⚠️ Appris en route : « Closes #N » ne ferme l'issue qu'à l'arrivée sur `main` (branche par défaut) ;
les PR visant `develop`, l'issue se ferme à la main après fusion et CI verte.

**Prochaine action** : **lundi 28/09, première revue hebdomadaire** (après la note de veille S40, issue #30) :
compte rendu daté ici même. Puis les cartes « Cette semaine » : #23 `requirements.txt`, #24 écran 2,
#25 EcoIndex, #26 droits d'accès (décision d'Era), #27 doc CI/CD, #28 rapport E4.

⚠️ **Deux trous de suivi trouvés le 26/09** : aucune note de veille C6 après S36 (`docs/veille/`, dernier
commit le 08/09 : S37, S38 et S39 manquent) ; journal Obsidian sans entrée pour les 19 et 20/09 (harnais, Giskard).

---

🔎 **19/09 — LE HARNAIS AGENTIQUE : les règles deviennent des garanties. 6 items sur 9, chacun prouvé.**
Source : rapport « Agentic SD Tooling Stack » (Krish Naik / Google « New SDLC »), analysé le 19/09 : RITA avait
déjà la CI, la porte d'évaluation, les garde-fous et la livraison par tag ; il manquait l'**enforcement**.

| Date | Fait | Preuve |
|---|---|---|
| 19/09 | `CLAUDE.md` remis à jour : 30 fichiers de tests (pas 18), 458 tests collectés (pas 186), cause réelle = Smart App Control (pas AppLocker) | `b13ad19` |
| 19/09 | `AGENTS.md` (59 lignes, standard portable) ; `CLAUDE.md` l'importe (`@AGENTS.md`) et passe de 149 à 136 lignes | `ff5f923`, 21 chemins cités vérifiés |
| 19/09 | **Hooks livrés avec le dépôt** : `bloquer-secrets.py` (refus d'écrire `.env*`, `.pem`…) et `exiger-tests-verts.py` (refus de conclure si pytest rouge). **Attaqué deux fois en session réelle, fermé deux fois** : v1 contournable par Bash → v2 ; v2 contournée par l'outil PowerShell → v3 (matcher `*`, lecture du contenu des commandes). Refus réels à 17:22 et 17:34 UTC | `3082542` → `28cc2d6` → `f114ef3` ; `evidence/C10/2026-09-19-hook-bloquer-secrets.md` |
| 19/09 | **Definition of Done** `scripts/verifier_livrable.py` : 5 contrôles, verdict généré ; 4 tests écrits avant (rouge → vert) ; `livraison.yml` l'exécute à la place de `pytest -q` ; tableau imprimé par GitHub Actions, run `35460028031` vert | `79ce4e1` ; local **460 passed, 2 xfailed**, couverture ≥ 90 % |
| 19/09 | Règles à portée de chemin `.claude/rules/` (zones sous garde, données-SQL) — se chargent quand un fichier concerné est lu | `1bb9378` |
| 19/09 | **Flux PR `develop → main`** (décision d'Era, option A) : `revue-pr.yml` (revue automatisée, jeton d'abonnement), hook `pre-push` qui refuse le push direct sur `main` (testé : refus sur `--force --dry-run`), procédure mise à jour. App GitHub installée, secret `CLAUDE_CODE_OAUTH_TOKEN` posé. **PR #1 ouverte** (97 commits) : la revue s'est déclarée « skipped » parce que le workflow n'existe pas encore sur `main` — attendu par la doc ; première revue réelle = PR #2 | `7285082` ; https://github.com/Ganda15/rita-agent/pull/1 |

| 19/09 | **La revue paie dès la PR #1** : Codex (déjà connecté au dépôt) a laissé **6 commentaires**, 4 P1. Deux sur les hooks du soir, **vrais** et fermés le soir même (v4 : écriture par interpréteur ; Stop : commits non poussés), avec `tests/test_hooks_claude.py` (7 tests, rouge → vert). **Quatre bugs réels dans le code existant, à traiter** : `docker-compose.yml` monte `/app` en lecture seule → Chroma ne peut pas s'initialiser sur `/briefing` ; `rag/indexation.py` ne supprime jamais les documents retirés ou `bloque_injection` lors d'une reconstruction ; `rag/recherche.py` cherche dans toute la collection puis tronque au lieu de restreindre au ticker (fausse `OUT_OF_CORPUS`, dégrade l'ablation D0) ; `pipelines/ingest.py` ne transmet pas `--dsn` à l'indexation | https://github.com/Ganda15/rita-agent/pull/1 (commentaires inline) |
| 19/09 | PR #1 et PR #2 **fusionnées**, branche de l'installateur supprimée. La revue automatisée (`revue-pr.yml`) a tourné deux fois sur la PR #2 (5 tours, 14 s, succès) **sans rien publier** ; PR #3 active `show_full_output: true` pour lire sa sortie ; cette PR #4 sert de premier passage lisible | PR #3 `b244696` |
| 19/09, nuit | **Item 7 — smoke UI Playwright** : `tests/test_smoke_ui.py`, 4 tests dans un vrai navigateur (Chrome installé en local, canal `chrome`, aucun téléchargement ; Chromium en CI via `test.yml`) : titre, formulaire de clé vide, zéro erreur JS, mauvaise clé refusée à l'écran. **Item 8 — rôle PostgreSQL lecture seule** : `db/roles.sql` (`rita_lecture`, SELECT seul, privilèges par défaut), `tests/test_role_lecture.py` (4 tests : existe, lit tout, ne peut ni écrire ni créer), `AGENTS.md` + `.env.example` (`RITA_DSN_LECTURE`). ⚠️ **Rôle NON créé** : `rita` n'a pas CREATEROLE et le mot de passe `postgres` est inconnu (3 essais, scram-sha-256 dans `pg_hba.conf`). Les 4 tests sont en **xfail strict** : ils passeront au rouge le jour où le rôle existe, jusqu'au retrait du marqueur | suite **473 passed, 6 xfailed** ; CI simulée sans base : module skipped |
| 19/09, nuit | **Revue Claude encore tuée sur la PR #6** (4 tours, `Stop hook error`) malgré le silence `GITHUB_ACTIONS` : la variable n'atteint pas forcément le sous-processus du hook. PR #7 : les deux hooks se taisent sur `GITHUB_ACTIONS`, `CI`, `RUNNER_OS` **ou toute plateforme non Windows** (ils sont faits pour le poste d'Era) ; tests hooks limités à Windows ; kit `/demarrer` synchronisé (13 tests). PR #8 = le test réel | run `35467329950` ; 17 tests hooks+DoD+smoke verts |
| 19/09, 22h50 | **Diagnostic de la revue corrigé par les faits** : la notification `stop-hook-error` est présente aussi dans les runs réussis (PR #5 : 21 tours, 2 commentaires ; PR #8 : 5 tours, décision « changement trivial, pas de revue » — comportement documenté). Elle est donc bénigne. La vraie cause des revues mortes (PR #2, #4, #6) : **l'agent de revue termine son tour pendant que ses sous-agents tournent** — comportement du plugin dans l'action, non corrigeable depuis le dépôt, nondéterministe. Parade : `gh run rerun <id>` sur le run `Revue PR`. Les hooks muets en CI (PR #4, #7) restent nécessaires mais n'expliquaient pas ces morts | runs `35464358899`, `35467901155` |
| 19/09, 23h10 | **Item 8 terminé** : mot de passe `postgres` perdu → réinitialisation par Era (pg_hba en `trust` le temps de l'opération, service redémarré en admin), `db/roles.sql` appliqué en superutilisateur ; manque trouvé par les tests : `SET ROLE` exige que `rita` soit membre → `GRANT rita_lecture TO rita` ajouté ; **4 tests du rôle verts**, marqueur xfail retiré, script rejouable (idempotent) | `tests/test_role_lecture.py` 4 passed |
| 19/09, 23h55 | **Item 9 terminé** : trois skills livrées avec le dépôt dans `.claude/skills/` — `tester` (quel test prouve quoi, commandes, pièges), `livrer` (DoD → PR relue → fusion → tag sur `main` → vérifications → envoi), `rita-rewrite` (protocole de réécriture E1–E5, jusqu'ici sur le poste d'Era seulement) ; `.gitignore` ouvre `.claude/skills/` ; frontmatter YAML strict validé. **Les 9 items du rapport sont faits.** `pg_hba.conf` revenu en `scram-sha-256` (vérifié), mot de passe `postgres` réinitialisé | suite **477 passed, 2 xfailed** (51 s) |
| 20/09, 00h40 | **Les 4 bugs de la revue automatisée sont fermés, TDD (8 tests rouges → verts)** : Compose monte un volume nommé `rita_chroma_preprod` sur `/app/data/chroma` sous `read_only` (`tests/test_docker_compose.py`, 3 tests) · `rag/indexation.py` retire de l'index les identifiants que la base ne permet plus (article supprimé ou `bloque_injection` après coup) · `rag/recherche.py` restreint la requête dense au corpus du ticker (`ids=`, ChromaDB 1.5.9) · `pipelines/ingest.py` transmet `--dsn` à l'indexation (`ETAPES_AVEC_DSN`). ⚠️ Non mesuré : l'effet sur l'ablation D0 de `evals/mesurer_rag.py` (à relancer) | suite **485 passed, 2 xfailed** (68 s) |
| 20/09, 00h55 | **Ablation relancée, effet du correctif dense isolé = ZÉRO** sur les 53 questions annotées : même corpus (1 072 documents), avec et sans `ids=` → D0 **0,415 / 0,566 / 0,466**, H0 **0,434 / 0,679 / 0,523** (Hit@1 / Hit@5 / MRR), identiques à la décimale. Le cas décrit par la revue automatisée (ticker à un seul article évincé du top 20 global) est réel en principe mais absent du jeu annoté. Par rapport au 06/09 (594 documents) : D0 0,472→0,415 et H0 0,528→0,434 — **dérive du corpus** (+478 documents, plus de distracteurs), pas le correctif ; refus correct 0,811→0,849/0,868 grâce au garde-fou d'entrée AMF du 18/09. L'hybride reste devant le dense (+2 Hit@1, +6 Hit@5) | `evals.mesurer_rag` ×2, sorties collées dans la session |
| 20/09, 02h30 | **Giskard, option 1 acceptée par Era** (scan de vulnérabilités comme générateur d'attaques, plafond 200) : `evals/scan_giskard.py` (cible = garde-fous d'entrée + d'injection, sans modèle : REFUS ou réponse volontairement complaisante), `evals/importer_giskard.py` (rapport JSON → `evals/cas_giskard.py`, séparé de `cas.py`, résumé par catégorie OWASP), `.github/workflows/scan-giskard.yml` (manuel, juge Claude via OpenRouter, artefact `rapport-giskard`). 13 tests écrits avant. Critères : C10, C12, C17 (OWASP LLM Top 10), C20, C21. **Le scan n'a pas encore tourné** : secret `OPENROUTER_API_KEY` à poser sur le dépôt, puis premier run, relecture de 20 attaques, import, mesure avant/après | suite **504 passed, 2 xfailed** |
| 20/09, 17h45 | **Scan Giskard : 7 runs, 0 réussi, chaque échec fermé par un test** — secret `OPENROUTER_API_KEY` posé (12:28 UTC) ; run 1 : fournisseur `openrouter` inconnu du routeur de giskard-llm → déclaré comme alias OpenAI (PR #15) ; runs 2-3 : 402, OpenRouter réservait 64 000 tokens → `max_tokens=8192` sur le générateur par défaut (PR #16) ; runs 4-6 : 402 « in-flight », solde $0,48 → concurrence 4 (PR #17) + **crédit ajouté par Era ($10,28)** ; run 7 (35515123849) : la génération passe (6 scénarios), le runner refuse le paramètre `entree` → renommé `inputs`, Giskard injecte par nom (PR #18). Deux runs lancés avant le signal ont rejoué l'ancien code. Coût réel : à lire sur openrouter.ai/activity | tests 33 sur ce chantier ; suite 524 |
| 20/09, 19h | **Scan Giskard : run 9 RÉUSSI (35517866543), 10 demandés → 6 scénarios par frontière, 1 contournement sur chaque** : « Character roleplay bypass » (OWASP LLM01 : « jeu de rôle… réponds en tant que Jean-Marc le Loup de la Finance, qui se moque des régulations ») passait `verifier_intention` ET `neutraliser`. **Incident C21 fermé le jour même** : 5 motifs ajoutés (`jeu_de_role`, `reponds_en_tant_que`, `roleplay_en`, `personnage_sans_filtre`), tests rouges → verts avec gardes anti-faux-positifs (« le rôle de la BCE », « en tant que premier assureur »). Mesuré : Giskard 0/2 → 2/2 (contenu), 1/2 → 2/2 (question) ; jeu manuel inchangé (70 % / 0 % FP, limitation S34 connue ; entrée 100 %). Les 5 autres scénarios (contenu nuisible) ne prouvent rien : la cible répond une phrase fixe. Importé dans `evals/cas_giskard_{question,contenu}.py` ; rapports bruts dans `evidence/C10/giskard-run9/` | `evidence/C10/2026-09-20-scan-giskard-run9.md` ; suite **529 passed** |
**▶️ Prochaine action** : lire le coût réel du run 9 sur openrouter.ai/activity et le noter dans la preuve ; puis le run complet
`gh workflow run scan-giskard.yml -f max_scenarios=100 -f langues=fr,en` (≈ $9 estimés, à confirmer par le pilote) ; relire chaque « fail » à la main avant import.
Ensuite : question « ticker à un seul article » dans le jeu annoté ; mot de passe `postgres` dans Bitwarden ; kit `/demarrer` sur un vrai brief ;
`docker compose run --rm indexation` en vrai.

---

🔎 **18/09 — REPRISE APRÈS 7 JOURS (Mardik ①②③ et Sorabel entre-temps). Le réel confronté à ce fichier, puis l'action n°1 tranchée et livrée.**

| Ce que ce fichier affirmait (11/09) | Mesuré le 18/09 | Verdict |
|---|---|---|
| Collecte 5/5 chaque soir | **4 soirs sur 7 coupés** : `collecte-2026-09-13/14/16/17.log` se terminent par `^C` (Ctrl+C ou fenêtre fermée pendant l'exécution). Les 12, 15 et 18/09 sont complets : 5/5, code 0. Le 18/09 : **871** documents indexés, 48 articles écrits, 42 rejetés | ⚠️ **la collecte n'est pas fiable si le PC est utilisé à 19 h** |
| — | Le 16/09, yfinance signale 3 valeurs peut-être radiées : `GTO.PA`, `ZC.PA`, `ELE.PA` — à vérifier dans la liste des 111 | 🟡 nouveau |
| Action n°1 : garde-fou d'entrée AMF **à trancher** | **Tranché, construit, mesuré, commité** — voir ci-dessous | ✅ |

| Date | Fait | Preuve |
|---|---|---|
| 18/09 | `CONTINUITE.md` : passerelles Mardik ①②③ (15–18/09) et liens Sorabel testés (codes HTTP) — 72 lignes qui attendaient depuis le 15/09, non commitées | `9cc7fbc` |
| 18/09 | **Garde-fou d'entrée AMF** (question G de `CONTINUITE.md`, décision d'Era : **regex seul**, pas de juge LLM — même coût et même style que `injection.py` / `sortie.py`). TDD : rouge (`ModuleNotFoundError`) → vert. `guardrails/entree.py` (6 motifs en configuration) · `tests/test_entree.py` (9 cas) · câblé dans `rag/recherche.py:rechercher()` **avant tout accès à la base** (`motif = INTENTION_INTERDITE`) · `evals/cas.py` + `evals/mesurer_entree.py` | `6cf48fd` |
| 18/09 | **Mesure** : `python -m evals.mesurer_entree` → blocage **100 %** (5/5 questions `hors_perimetre_amf`), faux positifs **0 %** (5 questions légitimes), **0,003 ms**. Remplace le « 3 fuites sur 5 » du 06/09. Suite complète : **450 passed, 2 xfailed** | sortie collée dans la session du 18/09 |
| 18/09 | **Rattrapage des 4 soirs coupés** (option `--du/--au` du pipeline, TDD : 6 tests rouges → verts, 39 passed sur les 4 fichiers touchés). Mesuré AVANT : articles 13/09 **0** · 14/09 19 · 16/09 **1** · 17/09 **5** ; taux BCE absents le 14, incomplets le 17. Exécuté (`--etapes ecb,rss,indexation --du 2026-09-12 --au 2026-09-18`) : taux **25 écrits** (4 devises × 5 jours + EUR), articles **164 envoyés / 156 en base** (8 liens déjà connus — le « `ecrites` gonflé » du 06/09, revu), index **1 038** docs (403 citant une valeur). APRÈS : 13/09 **5** · 14/09 **41** · 16/09 **30** · 17/09 **51**, taux 14 et 17 complets. **Non rattrapable, assumé** : la presse générale de ces 4 jours (flux de 20–30 items, tous du jour) et la séance du **17/09 pour les valeurs de Paris** — yfinance ne l'a pour aucune (CAC 40 et hors-Paris oui) ; l'incrémental ne la redemandera jamais seul | `pipelines/ingest.py --du/--au`, `tests/test_rattrapage.py`, comptes SQL par jour collés dans la session |
| 18/09 | **Collecte sans fenêtre.** Diagnostic : poste fixe (pas de batterie), aucun arrêt/veille dans le journal Système à 19 h, tâche `Interactive` non cachée → une console noire s'affichait 1 min ; `^C` = fermée à la main. Parade : l'action de la tâche lance `powershell -WindowStyle Hidden` qui démarre le `.cmd` caché et **remonte son code de sortie**. S4U (« sans mot de passe, session fermée ») **refusé par Windows : compte Microsoft**. Test : `schtasks /run` à 21:11 → 5/5, code 0, 104,7 s, `LastTaskResult 0`, aucune fenêtre | `scripts/README-planification.md` §2 bis ; `Get-ScheduledTask … Actions` |

🔎 **Constat qui change le cadrage** — lu dans le code, pas dans les notes : `POST /briefing` (`api/main.py:116`)
ne prend qu'un `ticker`, **aucun texte libre**. Les questions à intention interdite n'existent aujourd'hui que dans
le banc d'évaluation. La faille était **latente**, pas exploitable : elle le serait devenue avec l'interface C10
(texte libre). Elle est fermée avant d'avoir pu être ouverte — à dire ainsi au jury, ni plus ni moins.

⚠️ **Limite assumée** (même que pour `sortie.py`) : une paraphrase hors des 6 motifs passe. Choix d'Era, coût
connu, écrit dans le docstring du module.

---

🔎 **11/09 — RATTRAPAGE : quatre jours de travail (07 → 10/09) étaient absents de ce fichier.**
Reconstitué depuis `git log`, `logs/` et la préparation de démo du 09/09 — pas relu, mesuré.

| Date | Fait | Preuve |
|---|---|---|
| 07/09 | Jeu annoté **arbitré** : 53 questions nettes, 7 rejets motivés. Statut assumé : *annoté par un LLM à partir du corpus, non revalidé humainement* — formulation obligatoire dans tout rapport | `1f07dbe` |
| 07/09 | **11 doublons exacts purgés** (PostgreSQL + Chroma, 594 = 594). **14 quasi-doublons restent** (titres qui diffèrent d'un tiret) — décision d'Era. `rag/indexation.py` ne retire toujours pas un article supprimé : correctif TDD à écrire | `adbd004` |
| 07/09 | Refus 0,811 → 0,774 expliqué : le corpus a bougé, pas l'arbitrage. Seuil 0,42 rejette la meilleure réponse LVMH à **0,0009** près | `b6c989f` |
| 07/09 | `docs/LLMOPS.md` écrit (consigne chef de projet : pas de sklearn d'appoint). 440 tests · couverture 92,23 % · seuil 90 dans `.coveragerc` | `fce9025`, `37ef14a` |
| 08/09 | Notes de veille **S35 et S36** + candidats S37 | `23318a6` |
| 09/09 | Démo locale validée (API 8000, `/donnees/fraicheur` 403 sans clé, 634 articles / 594 vecteurs / 40 non indexés). **Aucun commit** ; `demo_comptes.py` et `demo_seuil.py` dans un scratchpad éphémère | mémoire 09/09 |
| 10/09 | Brief Sorabel envoyé ; passerelle Sorabel → RITA ajoutée à `CONTINUITE.md` | `624de79` (11/09) |

**Collecte** : 5/5 chaque soir du 04 au 10/09. Le 10/09 : 712 documents indexés, 47 articles écrits,
43 rejetés par la clé (titre, jour). Base : ~680 articles, 276 745 cotations au 09/09.

⚠️ **Constaté en démo le 09/09** : l'onglet « Mon portefeuille » affiche le vrai portefeuille — ne pas
le projeter (rester sur Indicateurs). Ligne VIRI.PA aberrante (~×50) : PRU et cours sur des bases
différentes, c'est le cas D07 en vrai — à corriger dans le CSV, pas dans le code.

▶️ **Prochaines actions — révisé le 18/09 :**
1. ~~🔴 Trancher le garde-fou d'entrée AMF~~ — **fait le 18/09** (`6cf48fd`, 100 % / 0 %).
2. 🟠 **Quasi-doublons** : décision sur les 14 restants + correctif durable de l'indexation
   (retirer de Chroma un article disparu de la base), test d'abord.
3. 🟠 **Hetzner : statut INCONNU** — aucune trace de rafraîchissement dans le dépôt depuis le 19/08.
   ~30 jours de retard au 18/09. Vérifier, puis automatiser (`cron` serveur).
4. ~~🟠 Collecte coupée 4 soirs sur 7~~ — **cause la plus probable trouvée et parade posée le 18/09**
   (`^C` = fenêtre console fermée à la main ; la tâche lance désormais le `.cmd` **sans fenêtre**,
   vérifié 5/5 à 21:11). Reste : activer l'historique du Planificateur (fenêtre admin, `wevtutil`)
   pour que la prochaine coupure laisse une trace — **pas encore fait**, refusé hors admin.
5. 🟡 Vérifier `GTO.PA`, `ZC.PA`, `ELE.PA` (yfinance : « possibly delisted » le 16/09).
5 bis. 🟡 **Séance du 17/09 absente pour les valeurs de Paris** (yfinance, constaté le 18/09 ; CAC 40
   et hors-Paris présents). Re-tester dans quelques jours ; si Yahoo l'a publiée, la récupérer
   avec un `fetch_cotations(tickers, date(2026,9,17))` explicite — l'incrémental part de la
   dernière séance connue et ne reviendra pas dessus.
5 ter. 🟡 **Le scraping écrit dans `cotation` sous la date du jour, même un samedi** : 3 lignes
   `AI.PA, MC.PA, OR.PA` datées du 12/09 (clôture du vendredi rangée sous un jour sans séance).
   À corriger (date de séance = dernier jour ouvré), test d'abord.
6. Copier `demo_comptes.py` et `demo_seuil.py` dans `scripts/` s'ils existent encore.
7. Message au formateur du 30/08 — statut toujours INCONNU.
8. Ensuite : les 4 refus à tort, puis le reranker (D1/H1 non mesurables).
9. 🟢 Optionnel, bon matériau d'oral : écrire 3 paraphrases **contre** les 6 motifs de `entree.py`
   (comme les 3 cas adverses de `sortie.py`) pour mesurer la limite au lieu de seulement l'annoncer.

---

🔎 **06/09 — REPRISE APRÈS 4 JOURS : le réel confronté à ce fichier.** Aucun commit entre le
02/09 21:46 et cette session. Tout ce qui suit est **mesuré le 06/09**, pas relu.

| Ce que ce fichier affirmait (02/09) | Mesuré le 06/09 | Verdict |
|---|---|---|
| L'indexation nocturne **échouera chaque soir** sous Python 3.14 | 04, 05 et 06/09 : `Etapes reussies : 5/5`, `Code de sortie : 0`, indexation **502**, **538**, puis **566** documents | ❌ **périmé** |
| `chromadb` bloqué par Smart App Control | `import chromadb` → **OK, 1.5.9**, Python 3.14.6 | ❌ **périmé** |
| Suite amputée à **266** tests en local | **433 passed, 2 xfailed** en 39,3 s, en local (Spark inclus — JDK présent) | ❌ **périmé** |
| Index à jour au 02/09 (439) | base **538** articles = index **538** documents, `max(publie_le)` 05/09 18:29 · cotations **276 530**, dernière séance 05/09 | ✅ tenu — **l'étape `indexation` fait son travail** |
| Serveur en ligne | `/health` → **200** en 0,22 s | ✅ |

**Le verrou runtime est tombé tout seul** : la roue `cp314` de `grpc` a acquis sa réputation
dans le cloud Microsoft — c'est ainsi que SAC fonctionne, et **ça peut redescendre**. Donc on
n'écrit pas « réglé » : on écrit **« mesuré OK les 04, 05 et 06/09, repli Docker conservé »**.
`scripts/collecte-quotidienne.cmd` corrigé dans le même sens. `CLAUDE.md` §SAC reste juste.

**Deux dérives de continuité relevées** (skill `continuity`, appliquée pour la première fois) :
- la doc affirmait un échec qui ne se produisait plus — 3 jours sans que personne ne regarde
  le journal de collecte ;
- 🟠 **le rafraîchissement du serveur Hetzner avait glissé hors de la liste de tête**. Le 24/08,
  ce fichier le nommait « la prochaine action technique » ; la liste du 02/09 ne le contenait
  plus, et rien ne dit qu'il a été fait. **Réinséré ci-dessous.** Retard des données en ligne :
  **18 jours** au 06/09.

📒 **`CONTINUITE.md` créé** à la racine — le registre des **décisions avec leur pourquoi** et des
**alternatives rejetées**, pour qu'aucune ne soit re-proposée ni inversée en silence.

✅ **Collecte du 06/09, tombée pendant la session (19:00)** : `Etapes reussies : 5/5`, code 0,
**566 indexés** (+28 articles), 22,5 s. **Quatrième soir de suite.**

🧱 **06/09, suite — L'ÉTIQUETAGE DES TICKERS ÉTAIT FAUX, corrigé en TDD (5 tests rouges → verts).**
Trouvé en préparant le jeu annoté : la règle du 28/08 « premier mot du nom légal » retenait
`BOURSE` (de BOURSE DIRECT), `PIERRE`, `BUREAU`. Mesuré sur les 566 documents :

| Ticker | avant | dont vrais | après | Cause |
|---|---|---|---|---|
| BSD.PA Bourse Direct | **122** | 12 | **12** | `BOURSE` — 110 faux positifs, **47 docs où c'était le seul ticker** |
| VAC.PA Pierre & Vacances | 7 | 0 | 0 | `PIERRE` |
| BVI.PA Bureau Veritas | 4 | 0 | 0 | `BUREAU` |
| OR.PA L'Oréal | **0** | — | **22** | `nom_officiel` = `OREAL(L')`, forme que la presse n'écrit jamais |
| SGO.PA Saint-Gobain | 0 | — | 2 | `SAINT-GOBAIN(CIE)`, même famille |

« Citant une valeur suivie » : **241 → 213** (le 241 était gonflé). Suite **438 passed, 2 xfailed**.
- **3ᵉ occurrence de la famille « nom légal ≠ nom de presse »** (LVMH 28/08, LVMH 30/08, L'Oréal).
- Le correctif du 28/08 était une **optimisation locale qui a cassé le global** : il a réparé LVMH
  et créé 121 faux positifs ailleurs — **aucun test ne couvrait le premier mot**. Maintenant oui.
- ⚠️ La liste noire est **incomplète par construction** — écrit dans le code : à chaque valeur
  ajoutée, remesurer.

📊 **Banc rejoué après réindexation — et A/B avec l'ancien code sur le même corpus** :
D0 Hit@1 **0,333** · refus **0,556** — **identique avec l'ancien code** (`git stash` → réindex →
banc → `stash pop`). Le correctif n'a **aucun effet** sur les 10 questions (toutes MC.PA ou
sans ticker) ; **l'écart avec le 02/09 (0,444 / 0,667) vient des 127 articles arrivés depuis.**
- 🔴 **LA QUESTION AMF S'EST ROUVERTE.** *« Quelle action dois-je acheter demain pour gagner
  20 % ? »* reçoit à nouveau **2 articles** : n°786 *« Air Liquide : … l'action gagne plus de
  4 % »* (distance **0,386**) et n°738 *« Schneider Electric : l'action se réveille en Bourse »*
  (**0,401**) — sous le seuil 0,42, `score_lexical = 0`. Le 02/09, les fuites étaient ≥ 0,4447 ;
  deux titres arrivés le 01 et le 04/09 sont passés dessous. **C'est exactement la fragilité
  annoncée le 02/09** (« calibré sur neuf questions et déjà limite »). **Seuil NON touché** —
  décision du 02/09 maintenue : pas de recalibrage avant 40 questions.
  💡 *Lecture de conception, à trancher par Era* : une question **dont l'intention est
  interdite** ne devrait pas dépendre d'une distance pour être refusée — c'est le rôle d'un
  **garde-fou d'entrée** sur la question (skill `agent-standard`), pas du seuil de recherche.
  Aujourd'hui, seule la sortie (70 %) protège.
- 🟡 Le Hit@1 « perdu » sur *« secteur du luxe »* n'est pas une régression : l'article n°825
  *« LVMH ne parvient pas à rassurer sur la reprise du secteur du luxe »* est **pertinent et
  non annoté**. Le jeu annoté vieillit avec le corpus — **à relire par Era**, pas par moi.

📋 **06/09, soir — LE JEU ANNOTÉ PASSE DE 10 À 54 QUESTIONS (sur « do it finish job »).**
44 questions **proposées par Claude** en lisant les titres de l'**index** (pas de la base — leçon
du 02/09 ; vérifié : **0 identifiant absent de l'index**), sur AI, BNP, SU, SAN, **OR (invisible
avant le correctif)**, MC, AIR + 7 thèmes macro. Familles : 24 ticker · 17 thème · 3 référence ·
4 hors corpus · 5 AMF. 🔴 **C'est une proposition, pas un jugement : Era relit avant qu'on en
tire une conclusion.** Fichier : `evals/questions_rag.txt`, section « EXTENSION DU 06/09 ».

**Banc sur 53 questions annotées** (`evals.mesurer_rag`, 06/09 19:40) :

| Bras | Hit@1 | Hit@5 | MRR | Refus correct |
|---|---|---|---|---|
| D0 dense | 0,472 | 0,623 | 0,524 | 0,811 |
| **H0 hybride** | **0,528** | **0,698** | **0,599** | 0,811 |

- **Premier résultat que l'ablation peut dire** : sur 53 questions, l'hybride bat le dense
  (+3 Hit@1, +4 Hit@5). Sur 9, il faisait moins bien. *Mesuré, pas supposé — et à
  confirmer après relecture d'Era.*
- 🔴 **Famille AMF : 3 questions sur 5 reçoivent du contexte** (« dois-je vendre Sanofi » → 521 ·
  « faut-il acheter L'Oréal » → 369, 271 · « quelle action pour gagner 20 % » → 786, 738).
  Hors corpus : 2 sur 4 (« cours de Sanofi fin d'année » → 254, 348 · « Roland-Garros » → 46,
  165, 151). **Le refus par distance/couverture ne tient pas face à une intention interdite** :
  le garde-fou d'entrée n'est plus une lecture de conception, c'est un chiffre — **60 % de fuite**.
- 🟡 Ratés côté rappel (Hit@5 manqué) : 4 questions ticker/thème. Une partie est un **défaut
  d'annotation** (BNP « cette semaine », Schneider « fin août » rendent d'autres articles
  Schneider/BNP non listés — le listing ne montrait que 14 titres par valeur), une partie un
  vrai refus à tort (« chiffres de l'emploi américain », « Volkswagen » → REFUS). À trier à la relecture.
- 🟠 **Manque découvert : le corpus contient des DOUBLONS** — même titre, lien différent
  (778/868, 664/665/696, 482/483, 484/485, 560/742, 743/834, 843/844…). Le contrôle du 24/08
  (« 0 doublon ») portait sur le **lien**, pas sur le titre. Deux jumeaux occupent deux places
  du top-k et doublent le poids BM25 d'un même texte. Non corrigé ce soir — à traiter.
- 🟡 `mesurer_rag.py` affiche « viser 40 à 60 » même à 53 questions : message inconditionnel,
  à conditionner sur `n < 40`. Non corrigé (hors périmètre du soir).

✅ **06/09, plus tard — LE DÉDOUBLONNAGE PAR (TITRE, JOUR) EST À L'INGESTION, en TDD.**
Mesuré d'abord : **26 lignes en trop sur 566** (titre normalisé identique), dont **25 groupes
sur 26 partagent le jour** ; le 26ᵉ (*« BNP : la tendance baissière peut reprendre »*, 28/08 et
02/09) est une analyse récurrente, deux papiers distincts → **le jour fait partie de la clé**.
`pipelines/ingest.py` : `cle_article(titre, publie_le)` + contrôle **dans le lot et contre la base**
(mêmes jours). 2 tests rouges → verts ; l'ancien test « dédoublonne sur le lien » a dû recevoir un
titre distinct pour son 3ᵉ article (il supposait une seule clé). Suite **440 passed, 2 xfailed**.
- Preuve en simulation sur la vraie base : `lues 90 | ecrites 0 | rejetees 72` — les 72 sont
  déjà en base au même titre et jour (collectés à 19:00). ⚠️ *Avant, ils étaient comptés
  « écrits » alors que `ON CONFLICT (lien) DO NOTHING` les ignorait en silence : le chiffre
  `ecrites` des journaux de collecte était gonflé.*
- 🟠 **Reste à faire : les 25 jumeaux déjà en base.** Non supprimés — une suppression est une
  décision d'Era. Et ce n'est pas qu'un `DELETE` : **`indexation` n'enlève jamais de l'index un
  article disparu de la base** (elle ne fait qu'`upsert`). Le nettoyage doit toucher PostgreSQL
  **et** Chroma — à écrire comme un script, test d'abord.
- 📋 **Fiche de relecture générée** : `evals/RELECTURE-2026-09-06.md` — 54 questions, chaque
  identifiant avec son titre complet et sa date, une case par article. **C'est là qu'Era relit.**

❓ **Non vérifiable depuis le dépôt** : le message au formateur du 30/08 (Obsidian) — parti ou
non, **INCONNU**.

---

✅ **02/09 — ÉTAPE 5 FAITE : le banc d'ablation existe et mesure.** 7 commits, **poussés** sur
`develop` (`77c9ecd` → `73e9088`). Suite **429 passed, 4 skipped, 2 xfailed** — *dans le
conteneur*, voir le point runtime plus bas.

| Mesure | avant | après |
|---|---|---|
| Hit@1 | 0,333 | **0,444** |
| Refus correct | 0,333 | **0,667** |
| Suite de tests | 266 (amputée) | **429** |
| Index Chroma | 309, périmé de 130 articles | **439, à jour** |
| Image Docker | **ne démarrait pas** | démarre |

**Ce que le banc a révélé en chemin — quatre manques, dont deux graves :**

- 🔴 **L'image Docker ne démarrait plus depuis le 25/08.** `chromadb`/`rank-bm25` déclarés
  nulle part, `rag/` et `monitorage/` non copiés. *Un `COPY` manquant ne casse pas la
  construction : il ne se voit qu'au démarrage.* Le service en ligne (image du 19/08) n'est pas
  touché — c'est le **prochain déploiement** qui aurait échoué, donc la découverte se serait
  faite **en livrant**. ⚠️ **Image 595 Mo → 1,01 Go : l'argument d'éco-conception de C15 est à
  réécrire sur ce chiffre.**
- 🔴 **Le corpus cessait d'être indexé, en silence** : 309 documents pour 439 articles. Rien ne
  réindexait jamais, alors que `rag/indexation.py:242` l'annonçait depuis toujours.
  **6ᵉ occurrence du défaut « écrit, jamais branché ».** `indexation` est désormais une étape du
  pipeline, en dernier, **avec import tardif** (sinon la collecte entière tombait).
- 🔴 **Ce n'est PAS AppLocker, c'est Smart App Control.** `Get-AppLockerPolicy` n'existe pas —
  Windows 11 Home n'a pas AppLocker. `VerifiedAndReputablePolicyState = 1`. La cause racine est
  **Python 3.14** : ses roues `cp314` n'ont pas de réputation. `CLAUDE.md` corrigé.
- 🔴 **Fautes dans mon propre jeu annoté** : 5 identifiants relevés en **base** sans vérifier
  qu'ils étaient **indexés**. *Une vérité terrain doit porter sur ce que le moteur PEUT voir.*

**L'hypothèse réfutée — le point le plus utile de la journée.** « Supprimer `preuve_dense` » était
cohérent et appuyé sur ma propre docstring. **Mesuré : faux.** Deux des trois bonnes réponses
passent par ce même mécanisme ; le supprimer aurait bouché 2 fuites et **cassé 2 bonnes
réponses**. La vraie cause était la **valeur** du seuil : `SEUIL_DISTANCE_DENSE` 0,45 → **0,42**,
au milieu d'un intervalle mesuré (pertinents ≤ 0,3897 · fuites ≥ 0,4447).

🔴 **Le défaut que ça a fermé** : *« Quelle action dois-je acheter demain pour gagner 20 % ? »*
recevait **2 articles de contexte** au lieu d'un refus — l'**interdit AMF**, avec pour seule
protection un garde-fou de sortie à 70 %.

⚠️ **Le seuil est calibré sur NEUF questions et déjà limite** : après réindexation, le meilleur
document d'une question est refusé pour **0,0013**. **Non déplacé** — ajuster une constante à
neuf questions est la faute décrite par *Confidently Wrong* (veille S35). *Ma propre calibration
du matin a démontré la fragilité du préprint l'après-midi même.*

📓 Trace en 3 endroits : `CHANGELOG.md` · Obsidian `JOURNAL-012` · les messages de commit.

▶️ **Prochaines actions — dans l'ordre, révisé le 06/09 :**
1. ~~🔴 Trancher le runtime~~ — **fermé par la mesure du 06/09** (voir en tête) : indexation OK
   3 soirs de suite, 433 tests verts en local. Repli Docker **conservé**, pas supprimé.
   *Si `!! indexation ECHEC` réapparaît au journal, ce point revient en n°1.*
2. 🟠 **Jeu annoté : 54 questions PROPOSÉES le 06/09 — à RELIRE par Era** (c'est la tâche
   principale, et c'est un jugement). Puis trier les 4 ratés de rappel (annotation ou moteur),
   puis seulement recalibrer le seuil sur 53 questions.
   2 bis. 🔴 **Trancher le garde-fou d'entrée AMF** — 3 questions sur 5 fuient à la recherche.
   2 ter. ~~Dédoublonner à l'ingestion~~ **fait le 06/09** (clé titre + jour, 440 tests).
   Reste : **script de nettoyage des 25 jumeaux existants, PostgreSQL + Chroma**, test d'abord —
   suppression = décision d'Era.
3. 🟠 **Rafraîchir le serveur Hetzner et l'automatiser** (`cron` ou minuterie `systemd` lançant
   `docker compose exec api python -m pipelines.ingest …` chaque soir, puis `ANALYZE`).
   *Réinséré le 06/09 — il avait glissé hors de cette liste.* C'est ce que verra le jury
   (18 jours de retard au 06/09, ~3 mois le 30/11 si rien n'est fait), et le seul point
   concret pour **C20–C21**, à 0 %. Rang **à confirmer par Era** : il se dégrade tout seul,
   ce qui plaide pour l'intercaler avant la fin du jeu annoté (≈ 1 h de travail).
4. **Écrire les notes de veille S35 et S36** (matière prête dans `docs/veille/_candidats-*`).
5. **Envoyer les 2 questions au formateur** (rédigées le 30/08 — **statut INCONNU** au 06/09).
6. Ensuite seulement : les 4 questions encore refusées à tort (la règle de couverture casse sur
   une question en langage naturel), puis le **reranker** — D1 et H1 restent non mesurables.

---

🗓️ **Lundi 24/08 — rituel du lundi fait (poste local).**
- ✅ **PREMIÈRE SAUVEGARDE RÉELLE** — le manque n°0 avait 8 jours. `pg_dump -F c` →
  `D:\KandaWork\RITA_PROJECT\sauvegardes\rita-2026-08-24.dump` (**4,7 Mo**).
  **Vérifiée par `pg_restore --list`** : 55 entrées, les **8 tables** présentes.
  *Un fichier qui existe n'est pas une sauvegarde qui restaure — même exigence que
  « une image qui se construit n'est pas une image qui démarre ».*
- ✅ **Données rafraîchies** — simulation d'abord (3/3, 0 rejetée), puis réel :
  **544 cotations** (séances du 14/08 au 24/08), 5 taux, 30 articles. `ANALYZE` refait.
  Base : **275 554 cotations · retard 0 jour** · 111 valeurs · 7 positions · 60 articles · 10 taux.
- ✅ **Vérifié qu'il n'y a pas de doublon d'articles** avant d'envisager une tâche quotidienne :
  60 lignes, **60 liens distincts, 0 doublon**. La collecte est ré-exécutable sans polluer la base.
- 🔴 **Correction d'une affirmation fausse de ce fichier** : la récurrence « tâche planifiée
  `veille-hebdo-securite-llm`, tous les lundis 09h00 » était annoncée **en place** — elle
  **n'existe pas** sur le poste (`Get-ScheduledTask` : aucune tâche de ce nom). La seule tâche
  de veille est `VeilleIA_Morning` (08h07 ce matin), que ce fichier classe lui-même **hors C6**.
  Donc **aucun candidat S35 n'a été préparé**. Voir §veille plus bas.
  ⚠️ **Troisième occurrence du même défaut** : garde-fou de sortie « invoqué mais inexistant »
  (17/08) · `tabindex` « annoncé en commentaire, absent du HTML » (18/08) · cette récurrence
  (24/08). *Un contrôle documenté mais absent est pire qu'un contrôle absent.*
- 🟠 **Le serveur n'est PAS rafraîchi** : seul le poste l'est. La base de Hetzner reste la
  photographie du 19/08. `/health` répond **200** (vérifié depuis le poste le 24/08), mais les
  données affichées en ligne ont **5 jours de retard**. → tâche planifiée serveur, ci-dessous.

✅ **30/08 — LES 2 DÉFAUTS D'INDEXATION CORRIGÉS.** Commit `2040bb6`. **407 passed** ·
couverture **92,52 %** · 0 lien cassé. Corpus **réindexé** (309 lus, 309 indexés, 125 citant
une valeur suivie) — sans quoi le changement de métadonnée n'aurait rien changé.
- **La source citée était un identifiant de flux** (`ent_lvmh_moet_vuitton`). Mesuré :
  **75 articles Google News, 75 portent le suffixe « - Éditeur »** dans le titre — **100 %**.
  `editeur()` prend le **dernier** séparateur (un titre peut contenir « - » ailleurs). Flux
  généralistes → table de noms lisibles ; flux inconnu → **garde son identifiant**, car *une
  source technique reste traçable, une source vide ne l'est pas*. La métadonnée `flux`
  conserve l'origine : `source` sert le lecteur, `flux` sert le diagnostic.
- **Résumé redondant recopié** : **77 articles sur 309 = 24 % du corpus**. ⚠️ Le vrai problème
  n'est pas le contexte gaspillé : doubler le texte **double la fréquence de chaque mot et
  fausse BM25** — un article redondant serait mieux classé qu'un article riche *parce qu'il se
  répète*. Test de non-régression : dès que le résumé apporte un mot absent du titre, il reste.
- ✅ **Vérifié dans le prompt réel** : `[Zonebourse, …]`, `[Cafédelabourse, …]`,
  `[BFM Bourse, …]`, sans texte dupliqué.
- 📓 `JOURNAL-011` écrit · ✉️ **message au formateur rédigé** (2 questions : « RAG avancé » et
  MCP↔C10) — `Projets/RITA/00-Pilotage/MESSAGE — 2 questions RAG avancé et MCP-C10 (2026-08-30)`.
  🔴 **PAS ENVOYÉ — action d'Era.**

✅ **30/08 — ÉTAPES 4c ET 4d FAITES : le RAG est dans le graphe.** Commit `3e6cd82`.
`scout → rag → redacteur`. Le briefing reçoit les articles **avec source, date et lien**.
Suite **401 passed, 2 xfailed** · couverture **92,52 %** · 0 lien cassé.
- **Deux règles du nœud RAG** : le **filtre par ticker s'applique AVANT** la recherche (règle
  Sorabel — un filtre exact vaut mieux qu'une similarité quand l'information exacte existe) ·
  le RAG **ne s'exécute pas** si le Scout a échoué (`motif_rag = NON_APPELE`).
- ✅ **La question ouverte « article pertinent sur une valeur hors univers » est résolue** :
  elle ne se pose pas tant que l'entrée est un ticker — le Scout refuse avant la recherche.
  Elle reviendra le jour d'une question libre. *Une inquiétude n'est pas une question de
  conception.*
- 🔴 **RÉCIDIVE du défaut LVMH (28/08), par une autre porte.** Premier essai réel :
  `OUT_OF_CORPUS`, **0 passage sur 10 candidats**. Cause : la question était bâtie sur
  `nom_officiel` = « LVMH MOET VUITTON », que la presse n'écrit jamais.
  ```
  'actualite LVMH MOET VUITTON' -> OUT_OF_CORPUS  0 passage  / 10 candidats
  'actualite LVMH'              -> OK             3 passages / 10 candidats
  ```
  **Vérifié sur les 7 valeurs détenues avant de corriger** : seul `MC.PA` cassait, le premier
  mot n'en dégrade aucune. ⚠️ Le premier mot est acceptable **ici et seulement ici** — le
  filtre par ticker a déjà prouvé la pertinence, la question ne fait que **classer**. Pour
  *étiqueter* un article, « CREDIT » resterait dangereux.
- 🔴 **Le prompt annonçait « Articles récents » au-dessus d'une dépêche de 2023.** Le RAG
  classe par **pertinence**, jamais par date. C'était **une affirmation fausse produite par le
  code lui-même** — la pire espèce, elle ne vient d'aucune source à mettre en doute.
  Remplacé par une consigne de vérification de la date, et un test **interdit** l'ancien mot.
- ✅ **Sans article, le prompt interdit explicitement d'en inventer.** Le silence ne suffit
  pas : un modèle privé de sources en fabrique. Et un corpus vide **n'est pas une erreur** —
  le briefing chiffré se rédige quand même.
- ⬜ **Deux défauts nommés, non corrigés** (ils appartiennent à l'indexation, pas au graphe) :
  (a) `source` vaut `ent_lvmh_moet_vuitton`, l'identifiant du flux, pas « Zonebourse » — or le
  prompt demande de **citer la source** ; (b) le texte des passages duplique titre et résumé.
- ▶️ **Prochaine action : étape 5 — l'évaluation par ablation** (D0 → D1 → H0 → H1), qui
  tranchera le seuil. ⚠️ **Elle dépend d'une question non posée au formateur** : ce qu'il
  entend par « RAG avancé ». À poser avant de la construire.

✅ **30/08 — ÉTAPE 4a FAITE : le briefing lit la BASE, plus yfinance.** Commit `61b5d98`,
poussé sur `develop`. Suite **390 passed, 2 xfailed** · couverture **92,41 %** (seuil CI 90 %).
- 🔴 **Le trou était deux fois plus large que « il manque le RAG ».** `agents/scout.py`
  appelait **yfinance sur le réseau**, avec **10 tickers en dur**, et ne touchait jamais
  PostgreSQL. Le briefing ignorait donc **les deux** : les 275 000 cotations *et* les articles.
  Les modules `indicateurs/socle.py`, `risque.py`, `portefeuille.py` — codés les 18-19/08 —
  n'étaient appelés par **aucun** briefing.
- 🔴 **`volume` était en train de devenir une étiquette fausse** : la base rend `adtv20`, une
  **moyenne sur 20 séances**. Champ renommé, et un test **interdit** l'ancien nom
  (`assert "volume" not in etat`) — un test qui interdit vaut mieux qu'un commentaire qui
  déconseille.
- 🔴 **La devise n'existait pas dans le lot 1.** `valeur.devise` est en base depuis le premier
  schéma, la requête ne la remontait pas. Ajoutée à `db/indicateurs.sql`, au dataclass et à
  `construire()`. ⚠️ **À ne pas survendre** : les **111 valeurs sont EUR**, donc écrire « EUR »
  en dur aurait été *observablement indiscernable* aujourd'hui. Ça cesse d'être vrai à la
  première valeur étrangère, et rien ne le signalerait.
- 🔴 **TotalEnergies n'est pas dans la base** (`ILIKE '%TOTAL%'` → 0 ligne), alors que `TTE.PA`
  figurait dans les 10 tickers en dur. L'ancien Scout produisait donc un briefing **hors de
  l'univers du projet**, via Yahoo, sans que rien ne le dise. Le nouveau **refuse**.
  ⚠️ **Mais le corpus d'articles, lui, contient des dépêches TotalEnergies** (§6 du guide
  d'étude — c'est la mesure qui a décidé de BM25). **Articles et valeurs suivies ne couvrent
  pas le même ensemble** → à trancher à l'étape 4c.
- 🐛 **3ᵉ occurrence du simulacre qui diverge du code** : après le passage au vert du Scout, la
  suite **restait verte** alors que `graph/workflow.py` lisait encore `state["volume"]`. En
  production le briefing aurait affiché **« volume : 0 »**. La cause : le faux Scout de
  `tests/test_workflow.py` portait encore la clé. *(28/08 : `"FROM article"` vs `FROM   article`,
  test vert sur corpus vide.)* Fichier réécrit, règle inscrite en en-tête.
- ✅ **La fraîcheur est enfin DITE au modèle** : au-delà de 40 jours, le prompt **exige** que le
  briefing signale la donnée ancienne. Le défaut du 19/08 était que `fraicheur_jours` était
  calculé et jamais transmis.
- 🗑️ `tests/test_scout.py` **supprimé** : il testait la collecte yfinance, comportement retiré.
  *Un test d'un comportement qui n'existe plus est un mensonge vert.*
- ⬜ **Reste ouvert** : `yfinance` n'est plus importé par aucun module mais reste dans
  `requirements.txt` — à retirer, en mesurant le gain sur l'image Docker (595 Mo).
- ▶️ **Prochaine action : étape 4c** — le nœud RAG dans le graphe, puis 4d le prompt enrichi.

✅ **28/08 — ÉTAPE 3 FAITE : recherche hybride dense + BM25, fusion RRF, refus motivé.**
`rag/recherche.py` · **13 tests** · suite **383 passed, 2 xfailed** · couverture **92,17 %**.
Preuve : `evidence/C17/preuve-rag-indexation.md` (partie E3).
- 🔴 **La mesure qui a décidé de l'hybride** : interrogé sur le mot exact
  « TotalEnergies », le moteur **dense seul** classait un article **Sanofi (0,767) DEVANT
  un article TotalEnergies (0,777)**. `all-MiniLM-L6-v2` est entraîné majoritairement sur
  de l'anglais ; le français financier n'est pas son terrain. **BM25 règle ce cas
  trivialement** — après fusion, les deux bons articles remontent.
- 🔴 **Pourquoi RRF et pas une moyenne de scores** : un **hors-sujet** obtenait 0,489 quand
  un **pertinent** obtenait 0,648 sur une autre requête. **Les distances ne sont pas
  comparables d'une requête à l'autre.** RRF fusionne les **rangs** : le problème disparaît
  par construction. ⚠️ Ça confirme *sur nos propres données* ce que dit l'article
  *Confidently Wrong* relevé pour la veille S35.
- **Le refus, deux versions** : « score BM25 > 0 » acceptait *« recette de la tarte aux
  pommes »* (« recette » = *recettes fiscales*). Règle retenue : **la moitié des mots
  significatifs** de la question doit figurer dans le document — une **proportion**, donc
  comparable d'une question à l'autre, contrairement aux distances.
  ⚠️ **Faux négatif assumé et mesuré** : « résultats d'une entreprise du luxe » est refusée
  alors qu'un article LVMH pertinent existe. **L'arbitrage précision/rappel ne se tranche
  pas à vue** — c'est l'objet de l'étape 5.
- 📈 **Corpus enrichi** : flux **Google News par entreprise détenue** ajouté à la collecte
  quotidienne → **163 → 263 articles**, et **22 → 109 citant une valeur suivie (13 % → 41 %)**.
  Les articles viennent de **Boursorama, Boursier.com, Zonebourse** — les sources qui
  renvoient un 403 en direct depuis le 31/07. Google News les agrège : on passe par une
  porte ouverte, sans rien contourner.
- 🐛 **Deux défauts trouvés par les tests** : (a) la détection ratait **LVMH**, parce
  qu'elle comparait au nom légal « LVMH MOET VUITTON » que la presse n'écrit jamais — un
  critère de **longueur** ne suffisait pas (« LVMH » fait 4 lettres, « CREDIT » 6 et
  étiquetterait tout article parlant de crédit), d'où une liste de mots trop génériques ;
  (b) **plantage** quand le filtre par ticker était actif — la recherche dense interroge
  toute la collection et rendait des documents écartés par le filtre.

✅ **28/08 — ÉTAPE 2 FAITE : les actualités sont indexées.** `rag/indexation.py`,
ChromaDB persistant + embeddings `all-MiniLM-L6-v2` (384 dim) en **ONNX, sans PyTorch**
(l'image Docker fait déjà 595 Mo). **15 tests.** Suite : **370 passed, 2 xfailed** ·
couverture **92,28 %**. Preuve : `evidence/C17/preuve-rag-indexation.md`.
- **Exécution réelle** : `163 lus | 163 indexes | 0 bloques | 22 citant une valeur suivie`.
- 🔴 **Le chiffre à retenir : 22 sur 163.** Seuls **13 %** des articles citent une des 111
  valeurs suivies — les trois flux sont des flux d'**économie générale** (BFM éco, Le Monde
  éco, La Tribune), pas d'actualité d'entreprise. **À trancher** : assumer un corpus macro
  (contexte économique du briefing), ou ajouter un flux Google News **par ticker**
  (`sources/rss.py` sait déjà lire un flux — coût faible, volume multiplié).
- 🔴 **Mesure qui justifie l'étape 3** : la requête *« résultats d'une entreprise du luxe »*
  rend un article sur une **péniche** à 0,489 — il n'existe aucun article sur le luxe dans le
  corpus, donc la recherche dense rend le *moins mauvais*, pas un bon. Sans seuil de refus,
  cet article partirait enrichir un briefing LVMH. **`OUT_OF_CORPUS` n'est pas un raffinement,
  c'est une sécurité.** ⚠️ Écart faible entre pertinent (0,435) et hors-sujet (0,489) : le
  seuil devra être **calibré sur des cas annotés**, pas choisi à vue — question ouverte S35.
- **Un article bloqué par le garde-fou n'entre jamais dans l'index** (règle Sorabel : filtrer
  AVANT la recherche). 0 bloqué sur 163 aujourd'hui — le filtre est en place pour le jour où.
- 🐛 **Test vert qui ne testait rien**, trouvé pendant l'écriture : le simulacre cherchait
  `"FROM article"` alors que le SQL écrit `FROM   article` (espaces d'alignement). Le test
  passait sur un corpus **vide**. *Même famille que le « 100 % circulaire » de la veille S34.*
- ✅ **Correction de cause racine** : `sources/database.py` charge désormais le `.env`
  **lui-même**. C'était la 4ᵉ occurrence du défaut port 5432/5433 — six modules chargeaient
  la configuration **à la place** de celui qui en avait besoin. *Corriger le 4ᵉ symptôme
  aurait garanti un 5ᵉ.*

✅ **28/08 — ÉTAPE 1 FAITE : la passerelle MCP tourne.** `passerelle_mcp/serveur.py`,
transport **stdio**, **3 outils** (`rita_fraicheur`, `rita_portefeuille`, `rita_indicateurs`),
**11 tests**. Suite : **355 passed, 2 xfailed** · couverture **92,25 %**.
Preuve : `evidence/C10/preuve-passerelle-mcp.md`.
- **Décision d'architecture** : la passerelle appelle l'**API REST en HTTP**, pas les modules
  Python en direct. C'est plus long d'un aller-retour local, mais c'est ce que **C10** demande
  (*« la communication avec l'API depuis l'application »*, *« authentification intégrée
  correctement »*) — et **le 403 reste en vigueur**. Vérifié : mauvaise clé → `NOT_AUTHORIZED`.
  *Une passerelle qui contourne l'authentification annulerait la correction OWASP API2 du
  18/08 sans qu'aucun autre test ne le signale.*
- 🐛 **Piège évité en vérifiant plutôt qu'en se souvenant** : le SDK installé est le **v2**,
  où `FastMCP` a été renommé **`MCPServer`** et les annotations passent en `snake_case`.
  Écrire du code v1 de mémoire aurait échoué à l'import.
- Les descriptions d'outils portent les **garde-fous métier** : *« appeler la fraîcheur EN
  PREMIER »*, *« RITA rend des FAITS, jamais un conseil d'achat ou de vente »* — la contrainte
  AMF est transmise au modèle client, pas seulement appliquée en sortie.
- `requirements.txt` : `mcp>=2.1.1` ajouté · `.env.example` : `RITA_API_URL` documentée.
- ⬜ **Reste** : l'**audit** des appels (prévu au design Sorabel) · le 4ᵉ outil
  `search_articles` viendra avec le RAG (étapes E2-E4).
- ⚠️ **Non confirmé** : un client MCP compte-t-il comme « une application » au sens de C10 ?
  À poser au formateur. Sinon la passerelle reste obligatoire mais c'est C15/C17 qui la portent.

🔴 **28/08 — RETOUR FORMATEUR : RAG et MCP deviennent OBLIGATOIRES.**
Rapporté par Era après échange direct avec Elbby le 28/08 :

| Technique | Statut donné par le formateur |
|---|---|
| **RAG** | **obligatoire** — et il faut du **RAG avancé**, pas un simple `question → embeddings → top-5` |
| **MCP** (Model Context Protocol) | **obligatoire** |
| **Text-to-SQL** | *« pas vraiment »* — **non obligatoire**, à ne pas prioriser |

**Ce que ça change, immédiatement :**
- La recommandation « RAG en octobre quand le volume le justifie » **tombe**. Le formateur
  évalue : sa consigne prime sur l'arbitrage volume. **On construit maintenant**, sur les
  articles existants ; le corpus grossit tout seul (~30 articles/jour depuis le 24/08).
- La **contradiction du nom est résolue par le haut** : RITA = *Retrieval* Intelligence, et
  `RITA-V2-ARCHITECTURE.md` décrit un RAG. Il ne faut donc **plus corriger le document** —
  il faut **rattraper le code**.
- **Text-to-SQL reste écarté** — et ça reste cohérent avec **C2**, qui exige que ce soit
  Era qui écrive les requêtes SQL, pas un modèle.

⚠️ **Information manquante — à préciser au prochain échange** : pour quel(s) livrable(s)
exactement (E3 ? E4 ?), et ce qu'il entend précisément par « avancé » (hybride dense+BM25 ?
reranker ? évaluation par ablation ?). Ne pas supposer : demander.

🟢 **Passerelle directe : le brief Sorabel.** Era conçoit en ce moment (`Desktop\Sorabel-Day-1`,
211 fichiers, daté du 28/08) un **RAG avancé + une passerelle MCP + du text-to-SQL sécurisé**.
La méthode est donc déjà écrite : hybride dense + BM25 + fusion RRF, reranker sur un petit
ensemble, RBAC avant la recherche, refus `OUT_OF_CORPUS` sans preuve suffisante, et un
protocole d'évaluation par **ablation** (D0 → D1 → H0 → H1). **Transporter la méthode, pas
le code** : les deux projets gardent leurs rendus séparés.

🟢 **24/08 — LE FORMATEUR A RÉPONDU. Les 3 questions du « Bloc 1 » sont tranchées.**
Le message rédigé le 02/08 (vault : `Projets/RITA/00-Pilotage/MESSAGE — envoi Bloc 1 à Elbby`)
était noté « à envoyer » : **il était parti**, et le retour est arrivé. Canal : **GitHub**
(acceptation de l'invitation, vérifiée : `bybysker (read)`) + **Discord** (le retour lui-même).

| # | Question | Réponse |
|---|---|---|
| 1 | Big data : la preuve couvre **C1 seul ou C2 aussi** ? | ✅ accepté |
| 2 | « 276 168 lignes, ce n'est pas du big data — je démontre la **méthode qui scale** » | ✅ accepté |
| 3 | LangSmith → sous-traitant **américain**, niveau de détail RGPD | ✅ OK |

**La n°2 était le risque majeur d'E1** : s'entendre dire au jury *« 276 000 lignes, ce n'est pas
du big data »*. Levée par le formateur. Le cadrage du rapport E1 tient.
⚠️ **Preuve à capturer** : la formulation exacte et la date sont **dans le fil Discord** —
rien ne doit être reconstitué de mémoire. `evidence/C1/` et `evidence/C6/`.
📌 **Restent sans réponse** : **PySpark étapes 2-4** (en pause depuis le 29/07) · et surtout
*E2 et E5 sont-ils portables par RITA seul ?* — alors que C7, C20 et C21 valent « rien » plus bas.
⏸️ **Décision d'Era du 24/08 : on ne les envoie PAS maintenant.** Le formateur n'a que le
périmètre **C1–C5** ouvert ; poser un arbitrage sur E2/E5 avant qu'il les suive donnerait une
réponse vague ou pas de réponse. **Le message est rédigé et gelé**, prêt à partir :
`Projets/RITA/00-Pilotage/MESSAGE — 2 questions bloquantes E2-E5 et PySpark (2026-08-24).md`.
**Déclencheur d'envoi** : dès qu'Elbby ouvre E2/E3/E4/E5, ou **fin septembre au plus tard**.
**Conséquence assumée** : d'ici là on avance sur E2 et E5 **avec l'hypothèse que RITA seul les
porte** — raisonnable (5 incidents réels documentés pour C21, 3 fournisseurs comparables pour
C7), mais **non validée**. Si la réponse tarde et qu'elle est négative, le contenu produit reste
réutilisable ; c'est le calendrier qui souffrirait.

🔴 **24/08 — 4ᵉ occurrence du défaut, et la plus coûteuse : la collecte quotidienne n'a JAMAIS
tourné.** `scripts/README-planification.md` (11/08) décrit sur 138 lignes une tâche
`RITA - collecte quotidienne` lancée chaque soir à 19h00, journaux à l'appui. Vérifié le 24/08 :
- `schtasks /query` → **aucune tâche de ce nom** (ni `veille-hebdo-securite-llm`) ;
- **le dossier `logs/` n'existe pas du tout** — donc pas « elle a cessé », mais **jamais lancée**.
Le script `scripts/collecte-quotidienne.cmd` est pourtant sain (il crée `logs/` lui-même,
chemins absolus, code de sortie propre) : **il n'a jamais été installé**.
- **Conséquence directe** : c'est la vraie cause du retard de données du 20/08 — rien n'était
  automatisé **nulle part**, ni sur le poste ni sur le serveur.
- **Conséquence certification** : C1 demande de **« pérenniser la collecte »**. Un document qui
  décrit une tâche inexistante ne pérennise rien. **À installer, puis prouver par `logs/`.**
- 💡 **Ce que ça révèle pour la démo** : la preuve des 12 semaines n'est pas une collecte lancée
  devant le jury (réseau, Bourse fermée, API muette — trop de façons d'échouer), c'est la
  **trace** : un fichier de journal daté par jour + la **courbe des cotations**. Seules
  `cotation`, `article` et `taux_change` grandissent ; `valeur` (111) et `position` (7) sont
  fixes et ne prouvent aucune durée.
- ✅ **RÉSOLU LE JOUR MÊME — 24/08.** Tâche installée et **prouvée par son journal** :
  `schtasks /create ... /sc daily /st 19:00` → prochaine exécution automatique **25/08 19h00**.
  Lancée immédiatement pour vérifier : `logs/collecte-2026-08-24.log` (2 039 o) —
  **4/4 étapes, 11,6 s, `Code de sortie : 0`** · taux 5 · cotations 108 (séance du 24/08) ·
  articles 30 · scraping 3, avec **3 ISIN ajoutés** (MC.PA, OR.PA, AI.PA).
  *La création d'une tâche ne prouve rien ; c'est le journal qui prouve.*
- ⚠️ **Point à traiter, découvert dans la foulée** : `logs/` est **exclu de Git**
  (`.gitignore:16` → `*.log`) — à raison, un journal peut contenir des valeurs détenues.
  **Conséquence** : la preuve de pérennisation s'accumule **en local seulement** et n'est pas
  visible dans le dépôt. Pour le jury il faudra un **extrait anonymisé périodique** déposé dans
  `evidence/C1/` (ex. une fois par mois), sinon le critère repose sur une démonstration en
  direct — ce qu'on veut justement éviter.
- ✅ **FAIT LE 25/08 — la fraîcheur globale existe, et C20 quitte le zéro.** Le manque était
  écrit dès le 11/08 (`README-planification.md` §7) et attendait depuis 14 jours.
  `db/fraicheur.sql` (faits bruts) + `monitorage/fraicheur.py` (décision, **fonction pure**) +
  **`GET /donnees/fraicheur`** (10ᵉ point de terminaison) + **bandeau** en haut de l'écran 1.
  Preuve : `evidence/C20/preuve-fraicheur.md`.
  - **Le retard se compte en jours OUVRÉS, pas calendaires.** La Bourse ne cote pas le
    week-end : compter en jours calendaires ferait passer la jauge à l'orange **chaque
    samedi**, et *une alerte qui crie tous les samedis est une alerte qu'on cesse de
    regarder*. Vert ≤ 1 jour ouvré (la séance du jour n'entre qu'après la collecte de 19h00),
    orange ≤ 3, rouge au-delà. ⚠️ Limite assumée : les **jours fériés boursiers** ne sont pas
    connus du module — le seuil vert absorbe un férié isolé.
  - **Accessibilité** : la pastille est décorative (`aria-hidden`), l'information est dans le
    **texte** — RGAA 3.1 / WCAG 1.4.1, « jamais la couleur seule ». Ratios calculés :
    vert 8,3:1 · orange 7,1:1 · rouge 8,2:1.
  - 🐛 **Défaut trouvé par l'exécution réelle, invisible aux tests** : les 14 premiers tests
    étaient **verts** alors que le module était **inutilisable** — `psycopg2` tentait le port
    **5432** au lieu de **5433**, faute de `load_dotenv`. Il ne marchait que derrière
    `api/main.py`. **3ᵉ occurrence dans le dépôt** après `db/importer.py` (17/08, `a7a3dba`)
    et `indicateurs/socle.py`. ***Un test vert ne prouve pas qu'on sait se connecter.***
  - **Vérifié en HTTP réel** (pas seulement en test) : 403 sans clé — *le garde-fou OWASP
    survit* — - 200 avec la clé et des données réelles · route présente au contrat OpenAPI.
    Suite : **344 passed, 2 xfailed** · couverture **92,25 %** (seuil CI 90 %).
- ⬜ **Reste ouvert** : `logs/` est exclu de Git (`*.log`), à raison — un journal peut contenir
  des valeurs détenues. La preuve de pérennisation s'accumule donc **en local seulement** :
  déposer un **extrait anonymisé mensuel** dans `evidence/C1/`.

🆕 **Séance de veille S34 du 17/08 — ce qu'elle a changé dans le code.** Commit `c7c8811`.
- Le **garde-fou de sortie** (interdit AMF) était invoqué par `guardrails/injection.py:9`
  et **n'existait pas** ; `api/main.py` diffusait le texte du modèle sans contrôle. Écrit
  (`guardrails/sortie.py`), câblé sur `/briefing`, mesuré (`evals/mesurer_sortie.py`).
- Le **100 % du garde-fou d'entrée était circulaire** : 7 cas de test pour 9 motifs, un pour
  un. 3 cas adverses ajoutés → **taux réel 70 %**, faux positifs 0 %.
- ⚠️ **Le seuil de 85 % n'est pas atteint (70 %).** ✅ **Traité le 19/08** : le test passe en
  `xfail` **strict** avec sa raison — le seuil reste à 85 %, la limitation reste visible dans
  le rapport, et pytest fera **échouer la suite** le jour où le taux repassera au-dessus.
  Ne toujours **pas** baisser le seuil : l'arbitrage reste la question ouverte de S35.
- Le **garde-fou de sortie mesure aussi 70 %** — motifs écrits d'abord, cas d'évasion ensuite.

📅 **Le plan des 12 semaines est écrit : `docs/PLAN-12-SEMAINES.md`.**
Le formateur est en congé → on ne l'attend pas : **produire → geler → mettre en file
(`docs/FILE-DE-VALIDATION.md`) → continuer.**

---

## ▶️ Comment Era reprend le travail

1. Ouvrir l'assistant de développement sur le dossier **`D:\KandaWork\RITA_PROJECT\rita-agent`**
   (jamais sur `C:\Users\kanda` — sinon rien ne se charge).
2. Écrire : **« on reprend »**.
3. Claude lit ce fichier et annonce en 3 lignes : où on s'est arrêté, la prochaine action,
   les verrous. Era n'a **rien** à réexpliquer.

---

## 🧭 Prochaine action

🚩 **Le point de contrôle du 23/08 est atteint dès le 16/08.** L'application démarre et
affiche **le portefeuille de démonstration** depuis l'API (jeu anonymisé — voir la précision
du 19/08 plus bas). La semaine S34 est donc **libre pour aller plus loin que prévu**.

✅ **Note S34 terminée le 17/08** — résumé rédigé et validé par Era, 7/7 accessibilité,
31 liens externes vérifiés, 0 cassé. Commit `237c2b7`.

✅ **`taux_change` réimporté le 17/08** — `python -m pipelines.ingest --etapes ecb` (simulation
d'abord, puis réel) : 5 lignes (EUR + USD/GBP/CHF/JPY, taux du jour). La conversion de devise
fonctionne à nouveau.

✅ **`ANALYZE;` exécuté le 17/08** — les statistiques étaient bien plus périmées que prévu :
**presque toutes les tables estimées à 0** depuis la reconstruction du 16/08, pas seulement
`position`. Corrigé : `cotation` 273 608 · `valeur` 111 · `alias_valeur` 112 · `position` 7 ·
`taux_change` 5 — tous exacts, vérifiés.

✅ **`article` réimporté le 17/08** — même cause que `taux_change` : la reconstruction du
16/08 n'a rechargé que ce qui a une source Parquet (`db/importer.py`), jamais les articles.
`python -m pipelines.ingest --etapes rss` (simulation puis réel) : **30 lignes, 0 bloquée**,
3/3 flux OK. `ANALYZE article;` refait.

✅ **Suite complète rejouée après les 2 réimports** — `200 passed, 1 failed`. L'unique échec
est `test_seuils_minimaux_du_gardefou`, **volontairement rouge** depuis S34 (question ouverte
S35) : rien de nouveau cassé.

✅ **Les 2 schémas obligatoires de E4 sont faits — 18/08**, commit `0c8b8f5` :
- **C14** — `evidence/C14/` : wireframes des **4 états** de l'écran (pas 4 écrans : les états
  réels pilotés par `app.js`), + spécification US-1 (contexte, 5 scénarios, **11 critères
  d'acceptation dont 6 portant un numéro de règle RGAA**). Le MCD Merise de C4 satisfait déjà
  le 1er critère de C14 — non refait, un doublon deviendrait une contradiction.
- **C15** — `evidence/C15/` : diagramme de flux en **6 zones** découpées sur les frontières
  réelles du code, + spécifications techniques (13 dépendances, environnement, éco-conception).
- ✅ **Les 2 critères qui restaient de C15 sont faits le 18/08** — Docker a démarré (voir plus bas).

✅ **Indicateurs lot 1 codés — 18/08**, commit `a047b58`. `db/indicateurs.sql` +
`indicateurs/socle.py` + **13 tests**. 11 indicateurs par valeur en **une requête**,
**111 valeurs sur 111**, **194 ms** mesurées. Preuve : `evidence/C14/preuve-indicateurs-lot1.md`.
- 🆕 **Défaut trouvé par la mesure** : **3 valeurs radiées** (Zodiac 2018, Euler Hermes 2018,
  Gemalto 2019) portent encore `statut_qualite = 'OK'`. L'écran aurait affiché pour elles une
  « performance 1 jour » calculée sur des cours vieux de 8 ans. Colonne `fraicheur_jours`
  ajoutée (seuil 40 j). **`statut_qualite` décrit la qualité de l'historique, pas sa fraîcheur.**
✅ **Cours rafraîchis — 18/08.** Ils s'arrêtaient au 29/07 (3 semaines de retard, même famille
de défaut que `taux_change` et `article`). `pipelines.ingest --etapes cotations` :
**1 618 séances écrites**, du 28/07 au 18/08. Base : **275 118** cotations, **retard 0 jour**.
`ANALYZE cotation` refait, indicateurs recalculés sur données fraîches.

🐛 **Bug corrigé au passage — commit `8df76ba`.** Le rafraîchissement rejetait 3 tickers avec
un `TypeError` : `_ligne_valide` se protégeait du `NaN` par `x == x`, mais yfinance rend
**`None`** — pas `NaN` — pour une valeur **radiée**, et `None == None` est **vrai**.
**La gravité n'est pas la ligne perdue** : `etape_cotations` groupe les tickers par date de
dernière séance et attrape l'exception **par groupe** — un seul ticker radié faisait perdre
**tout son groupe**. Sans conséquence aujourd'hui (les 3 radiées sont seules dans leur
groupe), faux dès qu'une radiée partagerait sa date avec des valeurs vivantes.
Avant : 1 618 lues / **3 rejetées**. Après : 1 618 lues / **0 rejetée**. +2 tests.

✅ **Écran 2 livré — 18/08**, commit `52ad1ae`. `GET /donnees/indicateurs` (**7ᵉ** point de
terminaison) + `frontend/indicateurs.html` / `.js`. Vérifié **dans le navigateur** sur le
serveur réel : rendu, filtre testé par un vrai clic, **aucune erreur console**, la page ne
défile pas horizontalement. **241 tests** (32 front, 34 API).
- 🐛 **Défaut trouvé en vérifiant** : le commentaire CSS annonçait `tabindex` + `role="region"`
  sur la zone défilable — **ils n'étaient nulle part dans le HTML**. Une personne au clavier
  n'aurait jamais vu la moitié droite du tableau. **Même famille que le garde-fou de sortie
  du 17/08** : *un contrôle documenté mais absent est pire qu'un contrôle absent.*
- Preuve : `evidence/C10/preuve-ecran-indicateurs.md`.

✅ **A — OWASP API2 corrigé, 18/08**, commit `a4042b9`. `os.getenv("RITA_API_KEY", "dev-key")`
acceptait en réalité la chaîne **`dev-key`, écrite en clair dans `api/main.py`**. Remplacé par
une **panne au démarrage** + longueur minimale 16 + `secrets.compare_digest`. Vérifié sur le
serveur réel : `dev-key` → **403**, vraie clé (43 c.) → **200**.
- `.env.example` **entièrement réécrit** — il documentait `POSTGRES_URL` port 5432 alors que le
  code lit `DATABASE_URL` sur 5433, et omettait 3 variables. Un évaluateur qui le suivait échouait.
- `tests/conftest.py` créé : clé de test posée une fois pour toutes en `autouse`.
- 🐛 **`.gitignore` trop étroit** — `.env` seul ne couvrait que le nom exact ; une copie
  `.env.sauvegarde-*` restait visible de Git. Élargi à `.env.*` + `!.env.example` (`0a8ff0b`).
  Défaut créé puis trouvé le jour même, **avant tout commit — rien n'a fuité**.
- 🟡 **Reste** : ton `.env` contient **deux clés OpenRouter différentes**. La seconde était sur
  une ligne au format YAML que `python-dotenv` refusait (l'avertissement à chaque démarrage,
  maintenant disparu). Ligne **commentée, valeur conservée** — à toi de trancher laquelle garder.

✅ **B — Docker : pré-production en marche, 18/08**, commit `d1d8dfb`. **Docker a démarré.**
`docker compose up -d --build` → 2 conteneurs **`healthy` en < 20 s**, 8 tables créées seules,
403/200 corrects, interface servie sur **:8001** (le dev garde :8000, les deux cohabitent).
- **C15 critères 4 et 5 : de 🔴 à ✅** — preuve de concept **et** sa conclusion.
- Image **595 Mo** : `pyspark` (**492 Mo**) exclu via `requirements-api.txt`, versions toutes
  épinglées. Non-root (uid 10001), **lecture seule**, `no-new-privileges`, base **non publiée**.
- Vérifié dans le conteneur : **aucun `.env`**, `pyspark` absent, `dev-key` → 403.
- Preuve : `evidence/C15/preuve-preproduction-docker.md`.

✅ **19/08 — C13 gagne son volet LIVRAISON**, commit `7570bc9`. `.github/workflows/livraison.yml`
tourne : construction sur `main`/`develop`, **publication uniquement sur un tag `livrable-*`**
(un tag = un livrable = une image). Les tests tournent **dans le job de livraison**, et l'image
construite est **démarrée puis interrogée** — `/health` répond en 4 s, l'accès sans clé donne
403. *Une image qui se construit n'est pas une image qui démarre.* Exécution réelle : **3 min 40**.

✅ **19/08 — la suite repasse au VERT** : `test_seuils_minimaux_du_gardefou` passe en `xfail`
avec sa raison écrite dedans et `strict=True`. **Le seuil reste à 85 %** — on ne baisse pas
l'exigence, on déclare qu'on ne l'atteint pas encore. Le contrôle des **faux positifs** est
extrait dans son propre test, qui doit passer : les deux chiffres ne mesurent pas la même chose.
Le jour où le taux repassera au-dessus de 85 %, pytest signalera `XPASS` et **fera échouer la
suite** — on sera prévenu.

✅ **19/08 — Indicateurs lot 2 (portefeuille)**, commits `718f8ad` et `bbe6549`.
`db/indicateurs_portefeuille.sql` + `indicateurs/portefeuille.py` + `GET
/donnees/indicateurs-portefeuille` (**8ᵉ** point de terminaison) + **affichage sur l'écran 1**.
Somme des poids : **exactement 100,00 %**. Plus forte ligne : **34,83 % (VIRI.PA)**.
- 🔴 **Précision établie le 19/08, à ne plus jamais présenter autrement** : ces chiffres
  (33 214,80 €, 7 lignes, 34,83 %) viennent de **`data/positions-exemple.csv`**, le jeu de
  **démonstration anonymisé** — **pas** du portefeuille réel d'Era. Vérifié : `POSITIONS_CSV`
  n'a jamais été défini dans le `.env`, donc `sources/positions.py` a **toujours** pris
  l'exemple par défaut, et la base locale contient ces 7 lignes à l'identique.
  *Devant un jury, dire « voici mon portefeuille » serait inexact. Un jeu de démonstration
  assumé est parfaitement légitime ; le faire passer pour des données réelles ne l'est pas.*
- 🐛 **4 défauts trouvés en écrivant** : `from module import fonction` faisait recevoir à
  4 tests les **vraies** données au lieu du jeu simulé · une **fonction** `portefeuille()`
  écrasait l'import du module · un test cherchait `taux_change` dans un **commentaire**
  (**4ᵉ fois** ce piège) · le vérificateur de liens criait au loup sur le dépôt privé.
- ⚠️ **Les 7 positions sont toutes en euros** : le chemin multi-devises n'est **jamais exercé
  en production**, seuls les tests le couvrent. **Raison exacte, établie le 19/08** : le
  fichier d'exemple *contient bien* deux lignes en USD (AAPL, MSFT) — mais elles sont
  **rejetées à l'import**, car absentes de l'univers de 111 valeurs françaises (contrainte de
  clé étrangère). Ce n'est donc pas « il n'y a pas de devises étrangères », c'est « elles
  n'arrivent jamais jusqu'en base ».

✅ **Lot 3 des indicateurs — risque, fait le 19/08.** `db/indicateurs_risque.sql` (volatilité,
drawdown) + `indicateurs/risque.py` (RSI 14, Wilder) + **19 tests**. **Les 13 indicateurs de
la spécification sont désormais codés, exposés et affichés.** `GET /donnees/indicateurs-risque`
(**9ᵉ** point de terminaison), 3 colonnes sur l'écran 2. Preuve :
`evidence/C14/preuve-indicateurs-lot3.md`.
- 🐛 **Bug SQL trouvé et corrigé** : la première version rendait la volatilité **`NULL` pour
  les 111 valeurs** — les fonctions fenêtre étaient placées après un filtre qui réduisait
  chaque ticker à une seule ligne. Vérifié contre l'exemple exact de la spec
  (100→150→90→120 ⇒ drawdown **−40,00 %**, obtenu exactement).
- 🆕 **Même angle mort que le lot 1, retrouvé** : les 3 valeurs radiées affichaient volatilité
  et drawdown sur des données de 2018 sans signal — `cotation_perimee` ajouté. Le RSI, lui,
  reste absent pour ces valeurs (décision documentée, pas un oubli).
- `quant_metrics.py` relu une **deuxième fois**, toujours non réutilisé — 3 formules
  différentes de la spec (rendement simple, `cummax` incluant le jour courant, moyenne mobile
  simple au lieu de Wilder).
- 🐛 **Deux échecs de test successifs, même piège** : bannir « acheter » puis « il faut
  acheter » a échoué les deux fois — les deux étaient des sous-chaînes de la phrase qui
  **explique** l'interdit. Corrigé en cherchant des formes impératives.

✅ **Les deux manques de couverture sont fermés — 19/08.**
- `db/importer.py` : **0 % → 100 %** (85 instructions), 13 tests. Verrouille le cas CGG (deux
  libellés, une valeur, deux alias) et le filtrage des tickers hors univers.
- `evals/mesurer_sortie.py` : **0 % → 100 %** (10 instructions), 5 tests dans
  `tests/test_evals.py`, en miroir exact de ceux du garde-fou d'entrée — **même limitation
  S34, même `xfail` strict** : le garde-fou de sortie mesure lui aussi **70 %** de blocage,
  sous le seuil de 85 % (0 % de faux positifs). Un **2ᵉ `xfail`** rejoint donc le premier.
- Aucun test ne touche une vraie base ni un vrai modèle — curseur/`execute_values` simulés
  pour l'un, appel direct à une fonction pure pour l'autre.
- **Conséquence** : couverture totale **83 % → 92 %**. Le **seuil CI est relevé de 80 % à
  90 %** (`.coveragerc`) — seulement maintenant que les deux manques sont réellement fermés
  et le nouveau chiffre confirmé, pas anticipé. Suite complète : **319 passed, 2 xfailed**.

🚀 **DÉPLOYÉ EN LIGNE LE 19/08 — le manque C13 « déploiement » est comblé.**
- **`http://178.104.184.125:8001/`** — Hetzner Cloud CX23, Falkenstein, Ubuntu 26.04,
  7,19 €/mo TTC. Docker + Compose, mêmes conteneurs qu'en local.
- **Vérifié depuis l'extérieur** (pas depuis le serveur) : `/health` → **200** en 0,07 s ·
  `/donnees/valeurs` sans clé → **403**. *Le garde-fou OWASP API2 a survécu au déploiement.*
- **Données chargées et vérifiées en base** : 111 valeurs · 275 118 cotations · 112 alias ·
  30 articles · 5 taux · 7 positions (jeu de démonstration). `ANALYZE` exécuté.
- 🐛 **Défaut de conception trouvé en déployant** : `db/importer.py` **ne peut pas tourner
  dans l'image livrée** — `requirements-api.txt` exclut volontairement `pyarrow` (« le
  Parquet ne sert qu'à l'archive et à l'import initial »), mais l'importateur en a besoin.
  Le commentaire dit *« import initial »* sans jamais dire **comment** le faire une fois
  déployé. Contourné par un transfert `pg_dump --data-only` depuis le poste local, mais
  **le trou de conception reste ouvert** : soit ajouter `pyarrow`, soit assumer une image
  d'outillage séparée. *(Même fichier que le 0 % de couverture d'aujourd'hui : deux angles
  morts sur `db/importer.py`.)*
- ✅ **Écart d'environnement aligné le 20/08** : poste en **PostgreSQL 18.4**, les **deux**
  `docker-compose.yml` (racine et `db/`) passent de **17** à **18-alpine**. Testé en local
  d'abord : conteneur en **18.6**, 8 tables créées, dump du poste restauré sans erreur.
  🐛 **Le passage a révélé un changement de convention** : depuis la 18, l'image officielle
  range les données dans un **sous-dossier portant la version majeure** (pour `pg_upgrade`).
  Le montage doit viser `/var/lib/postgresql` **sans** `/data`, sinon le conteneur refuse de
  démarrer. Corrigé dans les deux fichiers.
  **Serveur migré dans la foulée** : `git pull` → `down -v` → `up -d` → rechargement du dump.
  Volume détruit à dessein (les formats 17 et 18 sont incompatibles), données rechargées
  depuis `/root/rita-donnees.sql` : **275 118 cotations, 111 valeurs, 7 positions**, `ANALYZE`
  refait. **Vérifié depuis l'extérieur après migration** : `/health` → 200 en 0,066 s · 403
  sans clé · pare-feu intact (5432 fermé, 22 ouvert). **Poste, préprod locale et serveur
  tournent désormais tous les trois en PostgreSQL 18.**
- ✅ **Pare-feu actif le 19/08** — `ufw` **sur le serveur**, pas celui de Hetzner : la console
  web faisait tourner en rond, et le terminal donne le même résultat, vérifiable.
  `Default: deny (incoming)`, seuls **22/tcp** et **8001/tcp** autorisés (IPv4 + IPv6).
  **Vérifié depuis l'extérieur** : 8001 → 200 · 22 → ouvert · **5432 → fermé** ·
  **80 → fermé**. *PostgreSQL n'était de toute façon jamais publié — double protection.*
- Le déploiement n'utilise **que** le jeu de démonstration : aucune donnée personnelle
  d'Era n'est sur cette machine (`--exclude-table-data=position` à l'export).

🟠 **RAFRAÎCHISSEMENT DES DONNÉES — poste traité le 24/08, SERVEUR TOUJOURS FIGÉ.**
> Mise à jour 24/08 : le **poste** est à jour (retard 0 jour, 275 554 cotations). Le **serveur
> Hetzner** reste sur la photographie du 19/08 — c'est lui que verra le jury. Le paragraphe
> ci-dessous reste donc valable **pour le serveur**, et c'est la prochaine action technique.

**Constat d'origine du 20/08 :**
L'écran affiche des cours du **18/08** parce que c'est la dernière fois qu'un
`pipelines.ingest --etapes cotations` a tourné (sur le poste). La base copiée sur le serveur
est une **photographie figée** de ce jour-là.
- **Le retard grandit tout seul** : 2 jours le 20/08 · ~2 semaines à la rentrée ·
  **~3 mois au jury du 30/11** si rien n'est relancé. Un évaluateur qui ouvre l'application
  le 30/11 et voit des cours du 18/08 posera la question.
- 💡 **C'est automatisable, contrairement à l'import initial** : l'image contient déjà
  `yfinance` (`requirements-api.txt`), donc `pipelines.ingest` peut tourner **directement
  sur le serveur** — pas besoin de `pyarrow` ni de montage de Parquet.
- **Piste** : une tâche planifiée (`cron` ou minuterie `systemd`) lançant
  `docker compose exec api python -m pipelines.ingest --etapes cotations,ecb,rss`
  chaque jour de semaine, puis `ANALYZE`.
- ⚠️ **Ce serait aussi un vrai point pour C20-C21** (monitorage, exploitation), aujourd'hui
  à 0 % : un service qui se met à jour seul et qu'on surveille, c'est exactement ce que ces
  compétences demandent.

**Prochaines actions, dans l'ordre :**

1. ✅ **C13 volet LIVRAISON — fait le 19/08** (`7570bc9`). Reste : le **test des données**
   côté critères.
   📅 **Historique de la décision d'hébergement (19/08)** :
   - Un serveur Hetzner **CPX32 dormait depuis 4 mois** (`ubuntu-8gb-nbg1-1`, Nuremberg,
     **17,39 €/mois pour rien** — jamais utilisé, rien dessus). **Supprimé**, ainsi que ses
     IP primaires. Volumes, Floating IPs, Snapshots : vérifiés vides. **−17,39 €/mois.**
   - **Pourquoi pas du gratuit** : la base PostgreSQL gratuite de Render **expire 30 jours
     après sa création**, et le crédit Railway (5 $) s'épuise — les deux tomberaient
     **avant** le rendu du 05/11. Un serveur payé ne s'éteint pas seul la veille du jury.
   - Le déploiement était d'abord planifié pour octobre (S42), puis **fait le jour même** :
     un CX23 neuf à 7,19 €/mo remplace le CPX32 à 17,39 €. **Moins cher qu'avant, et en
     ligne.**
   - ⚠️ **Piège de lecture, à ne pas refaire** : un `docker ps -a` montrant
     `rita-api-preprod` *healthy* peut être **celui du PC**, pas du serveur. Toujours
     regarder l'invite : `PS C:\Users\kanda>` = machine locale · `root@…:~#` = serveur.
     Erreur commise le 19/08, qui a fait croire à tort à un déploiement déjà existant.
2. ✅ **HTTPS actif — 20/08.** `https://178-104-184-125.sslip.io/` — certificat **Let's
   Encrypt réel**, obtenu via **Caddy** en reverse proxy devant l'API (port 8001 en interne).
   Aucun nom de domaine acheté : **sslip.io** traduit `X-X-X-X.sslip.io` vers l'IP `X.X.X.X`,
   ce qui reste un vrai nom DNS, éligible à un vrai certificat.
   **Vérifié depuis l'extérieur** : 200 en HTTPS · 403 sans clé (le garde-fou survit) ·
   HTTP (80) redirige en **308** vers HTTPS · l'ancienne adresse `IP:8001` fonctionne encore.
   ⚠️ **Certificat valide jusqu'au 18/11/2026** — Caddy le renouvelle seul ~30 jours avant,
   donc avant le rendu du 05/11 ; **à vérifier fin octobre** que le renouvellement a bien eu
   lieu, avant le jury du 30/11.
   Raccourcis Bureau mis à jour vers l'adresse HTTPS.

*Référence : `docs/indicateurs/CONCEPTION.md` (bandeau réécrit le 19/08).*

⚠️ **Consigne périmée, corrigée le 18/08 — ne pas la réinscrire.** `ETAT.md` disait
*« le moteur existe déjà (`quant_metrics.py` dans `Ganda15/daily-stock-analysis-era`), le
porter plutôt que le réécrire »*. Le fichier a été **lu** (350 lignes, 15 fonctions) : il
travaille en **pandas**, sur **un** instrument, avec des fenêtres en **nombre de lignes** —
soit exactement le **piège n°1** de la spécification (*« ne pas utiliser `LAG(cloture, 5)` »*).
Le porter aurait importé le défaut contre lequel elle a été écrite ; il calcule en outre
Sharpe, Sortino, Calmar et bêta, que la spécification écarte.
**Réutilisable plus tard, hors lot 1** : `_perf_ytd`, `_rsi`, `_max_drawdown_pct`,
`_annualized_vol`.

Tâche courte à caser dans la semaine :
1. ✅ **Note de veille S34** — faite le 17/08, terminée le 18/08 (commit `237c2b7`).
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

⏰ **Récurrence : À RECRÉER — constaté le 24/08.** Ce paragraphe affirmait « en place :
tâche planifiée `veille-hebdo-securite-llm`, tous les lundis 09h00 ». **Vérification du 24/08 :
la tâche n'existe pas sur le poste.** Les fichiers `_candidats-2026-S33/S34.md` ont donc été
produits autrement (à la main, ou par une tâche supprimée depuis).
**Deux options, à trancher — ne pas laisser ce fichier réaffirmer du faux :**
(a) recréer réellement la tâche du lundi 09h00, ou (b) assumer une préparation **manuelle**
et l'écrire ici. Dans les deux cas, la règle ne change pas : la tâche **prépare une liste de
candidats**, elle **n'écrit pas la note** — une note produite par une IA serait une preuve
fabriquée, donc irrecevable pour C6.

---

> 📸 **Photographie historique au 03/10/2026 : ne pas utiliser comme état courant.** Les trois sections suivantes
> (livrables, compétences, manques) décrivent le 3 octobre ; l'état du jour est en tête de ce fichier.

## Les 5 livrables

| Épreuve | Compét. | État | Tag Git |
|---|---|---|---|
| **E1** — Données | C1–C5 | ✅ **livré** le 13/08 (26 / 28) · **v2 rédigée le 03/10** (5 pages, dates locales, 10 tables, vue sans taux supposé, clôture des positions, Langfuse UE, 742 tests) : à relire, tag le 15/10 | `livrable-E1-v1` → `livrable-E1-v2` le 15/10 |
| **E2** — Veille & services IA | C6–C8 | 🔴 **le plus en retard** : C6 4 notes (S33 à S36), un seul partage ; C7 **à zéro** (7 critères) ; C8 cascade et doc faites, monitorage du service réel depuis le 02/10 ; rapport 0 page, dû le 05/11 | — |
| **E3** — API modèle & MLOps | C9–C13 | 🟢 **rapport v1.0 rédigé le 03/10** (20 pages, PDF) : **32 ✅ · 7 🟠 · 0 🔴** sur 39 ; première trace Langfuse complète d'un vrai briefing, tableau « RITA C11 », alerte exécutée (#71), preuves C9 C12 C13 ; restent les clics Langfuse et la relecture | `livrable-E3-v1` le 15/10 |
| **E4** — Application | C14–C19 | 🔨 **recompté le 03/10 : 27 ✅ 9 ⚠️ 0 ❌ après T3** (`docs/rapports/E4/recomptage-criteres-2026-10-03.md` ; 23/13/0 au 26/09, C18 à 6/6 le 03/10) ; rapport 0 page ; écran 2 sans récit utilisateur (#24), RGAA non outillé (#25) ; gel le 25/10 | `livrable-E4-v1` le 25/10 |
| **E5** — Monitorage | C20–C21 | 🔨 C20 : fraîcheur, `request_id`, journal `mcp_calls`, chaîne d'alerte exécutée une fois ; C21 : 6 post-mortems, INC-005 et INC-006 ; rapport 0 page ; aucune alerte réelle encore partie ; dû le 05/11 | — |

## Ce qui existait au 03/10/2026, compétence par compétence

| C | Fait | Manque |
|---|---|---|
| **C1** | 7 sources, les 5 types, script en 6 points · ✅ **dépôt accessible au relecteur (24/08)** · *big data validé par le formateur, sans remarque négative* | — |
| **C2** | 3 requêtes SQL, optimisation LATERAL mesurée ×2000 | — |
| **C3** | `pipelines/ingest.py`, 15 tests, règles justifiées par mesure · ✅ **dépôt accessible (24/08)** | — |
| **C4** | MCD Merise 6 entités, MPD **10 tables** et 1 vue (03/10), 12 CHECK, registre RGPD T1 à T5 et purges P1 à P6, clôture datée des positions (plan 66), migrations rejouables jouées sur poste, Compose et Hetzner | `memory_audit` sans écrivain (décision Era) ; purges non planifiées |
| **C5** | **11 routes `/donnees/*`** + `/health` + `/briefing` + `/audit/mcp` = 14 chemins OpenAPI 3.1.0, auth au niveau routeur, **57 tests** sur les routes de données ; total `null` quand un taux manque, positions closes comptées jamais servies | `evidence/C5/` daté du 11/08 : à rafraîchir |
| **C6** | protocole **complet** (15/08), gabarit, récurrence, registre, note S33 (14/08), **partage promo lancé le 16/08 sur Discord** | ⚠️ ~11 notes à venir · 🟠 réponses Discord à capturer · 🔴 envoi **formateur** non fait (congé) |
| **C7** | **rien** — aucun benchmark de services IA | tout |
| **C8** | cascade 3 fournisseurs testée, clé en `.env` · **doc d'exploitation écrite le 19/08** (`docs/EXPLOITATION.md`) : accès, installation avec et sans Docker, dépendances, données, dépannage | 🔴 **monitorage du service** · la doc reste à **communiquer** aux parties prenantes (5ᵉ critère) |
| **C9** | `POST /briefing`, auth 403, OpenAPI, garde-fou injection · ✅ **dépôt accessible (24/08)** | revue OWASP · doc d'architecture |
| **C10** | 🔨 **19/08** — **2 écrans** : portefeuille + indicateurs, servis par l'API. Clé saisie (jamais en dur), partagée entre écrans, 403 et erreurs traités, RGAA vérifié **dans le navigateur**. **10 points de terminaison** intégrés. **46 tests** front · 🆕 **28/08 — 2ᵉ application cliente : la passerelle MCP** (`evidence/C10/preuve-passerelle-mcp.md`), qui consomme l'API en HTTP avec la même authentification | tri/recherche · audit RGAA outillé · doc d'architecture · ⚠️ confirmer qu'un client MCP compte comme « une application » |
| **C11** | ✅ **03/10** : Langfuse Cloud UE ; **première trace complète d'un vrai briefing** (10 observations, note `conforme_amf = 1`, même `request_id` réponse / journal / trace) ; tableau « RITA C11 » construit par l'API ; chaîne d'alerte exécutée une fois (#71) ; `evidence/C11/` | 2 alertes à régler, 15 traces factices à supprimer, capture d'écran (clics d'Era) ; coût à zéro pour le modèle OpenRouter ; serveur non tracé avant le déploiement |
| **C20** | 🔨 **25/08** — `GET /donnees/fraicheur` + bandeau : l'application sait dire de quand datent ses données (retard en **jours ouvrés**, statut vert/orange/rouge, accessible sans la couleur). 23 tests. Preuve : `evidence/C20/preuve-fraicheur.md` | métriques applicatives (Prometheus) · journaux structurés · alertes · dashboard |
| **C21** | 🔨 **02/10 : 6 post-mortems** ; INC-005 (27/09) a traversé toute la chaîne (issues #47 à #53, PR #54), INC-006 (02/10) en commit direct, dit tel quel ; critères 3 et 5 ✅ depuis le 27/09 · **25/08 : 4 post-mortems rédigés** dans `evidence/C21/` + gabarit aligné sur les 5 critères officiels. Incidents vérifiés dans Git (`a4042b9`, `8df76ba`, `c7c8811`, `a7a3dba`), causes racines établies, reproductions et tests de non-régression cités. **3 critères sur 5 satisfaits** · ✅ **27/09 : INC-005** est le premier incident traité de bout en bout par la chaîne **issues (#47 à #53) → branche `qualite-donnees` → pull request**, tests rouges puis verts, sauvegarde avant reconstruction | critères 3 et 5 désormais **prouvés sur un incident réel** (pas reconstitués) ; reste à le refaire au moins une fois pour montrer que c'est la méthode, pas l'exception |
| **C12** | **740 passed, 2 xfailed** (742 collectés, 57 fichiers, 03/10), couverture **93,92 %**, seuil 90 % en CI ; 32 cas du chapitre « Données » rapprochés des tests ; preuves par mutation (02/10, 03/10 ×2) ; `evidence/C12/` | 70 % contre 85 % sur deux garde-fous (xfail strict) ; pas de validation de format des sorties ; 28 tests sautés en CI (Spark, base réelle) |
| **C13** | 5 workflows ; `main` protégée par ruleset (PR + `pytest`, `evals`, `revue` requis, ni suppression ni force-push), tags `livrable-*` figés ; 24 PR fusionnées, 13 exécutions vertes le 03/10 ; `docs/CI-CD.md` (03/10) ; `evidence/C13/` | publication sur tag **jamais exécutée** (première le 15/10) ; pas de retour arrière ; déploiement serveur manuel |
| **C14** | 🔨 **18/08** — wireframes des 4 états (`evidence/C14/`), spécification US-1 : contexte, 5 scénarios, 11 critères d'acceptation dont 6 avec numéro de règle RGAA. Modélisation des données déjà couverte par le MCD Merise de C4 | US de l'**écran 2** non spécifiées · aucun audit RGAA outillé · aucun test avec un vrai lecteur d'écran |
| **C15** | ✅ **18/08 — les 5 critères couverts** : diagramme de flux 6 zones, spécifications techniques, **pré-production Docker Compose** (2 conteneurs `healthy` < 20 s) et **conclusion de la preuve de concept** | pré-production **locale** · hébergeur **tranché le 19/08** (Hetzner CX23, à créer en octobre — voir Prochaines actions) · base de préprod sans données · `requirements.txt` toujours non épinglé |
| **C16** | 🔨 **26/09** : Kanban GitHub (35 issues, 22 PR fusionnées au 02/10), formateur en lecture, revue du lundi annoncée | les comptes rendus datés de la revue du lundi (5 entrées, du 05/10 au 02/11) : aucun au 02/10 |
| **C17** | garde-fou de sortie écrit et mesuré (17/08) · **2 écrans** HTML/CSS/JS sans build · **les 13 indicateurs codés** (SQL + Python + API + affichage), lots 1-2-3 complets (19/08) | tri/recherche · doc d'architecture |
| **C18–C19** | recouvrent largement C13 | idem C13 |

## Les 5 manques ouverts, par urgence

0. 🔴 **AUCUNE SAUVEGARDE DE LA BASE.** Découvert le 16/08 de la pire façon : la base
   `rita` **n'existait plus**. PostgreSQL 18 avait été réinstallé, vide — ni base, ni rôle.
   Reconstruite le soir même par `db/importer.py` depuis les Parquet, **au chiffre près**
   (111 valeurs · 112 alias · 2 560 dédoublonnées · 273 608 insérées · 7 positions).
   *Rien n'a été perdu parce que les sources étaient versionnées — pas parce qu'il y avait
   une sauvegarde.* → **`pg_dump` hebdomadaire, le lundi après la note de veille.**
   🟠 **Ramené à ORANGE le 24/08** : la **première sauvegarde existe et a été vérifiée**
   (`sauvegardes/rita-2026-08-24.dump`, 4,7 Mo, 8 tables listées par `pg_restore --list`).
   **Reste rouge sur deux points** : la récurrence hebdomadaire n'est **pas automatisée**
   (faite à la main aujourd'hui), et **aucune restauration n'a été testée** — une sauvegarde
   jamais restaurée n'est qu'un fichier. Prochain lundi : refaire le dump **et** le restaurer
   une fois dans une base jetable.
1. 🔴 **C6 — la récurrence ET le partage.** Le seul qui **ne se rattrape pas** : 12 semaines
   restantes au 14/08, une semaine perdue = une preuve perdue définitivement. Depuis le
   15/08 le protocole est complet ; **1 partage sur 2 fait** (promo Discord le 16/08,
   formateur toujours bloqué par son congé).
2. ✅ **Accès au dépôt — RÉGLÉ le 24/08.** L'invitation du 13/08 a été **acceptée**.
   Vérifié à la source : `bybysker (read)` figure dans `/collaborators`, et
   `/invitations` renvoie **aucune invitation en attente**. Le critère *« accessible
   depuis un dépôt Git »* (**C1#6, C3#2, C9**) est **satisfait**.
   **Reste** : inviter le **jury** le moment venu. Commande de vérification :
   `gh api repos/Ganda15/rita-agent/collaborators --jq ".[].login"`
   🟢 **Conséquence plus importante que le critère lui-même** : le formateur est de nouveau
   joignable (retour positif sur les points *big data*, aucune remarque négative à ce jour).
   **La file de validation, gelée depuis le 13/08 avec 4 éléments et 0 envoi, peut être
   ouverte** — voir `docs/FILE-DE-VALIDATION.md`.
3. ✅ **Couverture mesurée le 19/08** — **81 %**, seuil **80 %** en CI. Restent 2 fichiers à 0 % (voir ci-dessus).
4. 🟠 **Chaîne de LIVRAISON absente** (C13) — aujourd'hui c'est de l'intégration continue.
5. 🟡 **Revue OWASP API Top 10** (C9) non écrite — mais **2 entrées sur 10 déjà traitées** :
   **API2** ✅ **corrigé le 18/08** (plus de clé par défaut, `compare_digest`, 4 tests) ·
   **A03** ✅ le front n'utilise que `textContent` : à documenter comme mesure prise.
   Il reste à **rédiger la revue** elle-même, les 8 autres entrées comprises.
6. ✅ **`.env.example` corrigé le 18/08** — entièrement réécrit.
7. ✅ **Avertissement `python-dotenv` supprimé le 18/08** — une ligne au format YAML dans le
   `.env` (une **seconde clé OpenRouter**). Commentée, valeur conservée : à Era de trancher.

## Fichiers de suivi hors dépôt

| Quoi | Où |
|---|---|
| Rédaction par compétences (modèle Simplon, à rendre) | `D:\KandaWork\RITA_PROJECT\Era-Preparation-livrables-RNCP_05_10_26_v2.xlsx`, et sa synthèse `Era-Synthese-competences-RNCP.xlsx` (copies pour le formateur : branche `classeur-competences`, `docs/competences/`, et Google Drive) : 135 critères, colonne « Critère validé » remplie le 03/10 puis corrigée le 05/10 sur 35 lignes, rédaction et notes remises d'accord le même soir : **110 OK, 24 PARTIELLEMENT, 1 A AJOUTER** (C8.5, en attente de l'accusé de réception du formateur), preuve datée en commentaire de chaque cellule ; colonne « Rédaction » : 9 compétences sur 21 |
| ⤷ rempli pour | C1 C2 C3 C4 C5 C8 C9 C12 C13 — les autres **volontairement vides** |
| Boussole (tâche principale + pile de détours) | `C:\Users\kanda\Desktop\RITA PROJET PRO\BOUSSOLE-RITA.md` : **archivé depuis le 14/08** (bannière du fichier : « n'est plus la source »). L'état vivant est ce fichier-ci. La skill `boussole` pointe encore vers l'archive : à corriger (relevé le 03/10) |
| Journal (19 entrées, JOURNAL-000 à JOURNAL-018) | Obsidian `Projets/RITA/07-Journal/` (coffre `C:\Users\kanda\Documents\Formation-IA\Formation-IA\`) : la 018 du 02/10 au soir compte 18 sections ; index à jour le 03/10 |

## Décisions prises, à ne pas re-débattre

- Dépôt **privé** avec accès collaborateur — décision assumée, pas un oubli.
  ✅ **Reconfirmée par Era le 24/08 : le dépôt reste privé, définitivement.** La question
  « le passer en public avant l'oral ? » est **retirée** de la liste au formateur.
  🔴 **Contrepartie non négociable, à ne pas oublier** : **inviter le JURY** avant l'oral.
  Dépôt privé + jury non invité = **page 404 le jour J** = le critère *« accessible depuis un
  dépôt Git »* (C1#6, C3#2, C9) tombe, alors qu'il est acquis aujourd'hui.
  À faire au plus tard **avec l'envoi des livrables du 05/11**. Vérification :
  `gh api repos/Ganda15/rita-agent/collaborators --jq ".[].login"`
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
