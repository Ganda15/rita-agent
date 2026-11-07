# Journal des livrables et décisions — RITA

> **Append-only** : on ajoute en haut, on ne réécrit **jamais** une entrée passée.
> Le présent est dans `ETAT.md` · le pourquoi détaillé dans le journal Obsidian ·
> le détail technique dans `git log`.
>
> **Une entrée = un livrable envoyé, une décision structurante, ou un manque découvert.**
> Pas les commits de code : Git les garde mieux, horodatés et infalsifiables.

---

## 2026-11-07, soir : S9, C17.7 et les corrections de #226 livrés et vérifiés en production ; C16.1 gardé à consolider

- **Livré** : PR #228 (`develop` vers `main`, `6f428d6`), fusionnée par Era à 19 h 32 UTC ; `/health` du site réel dit
  ce commit, l'écran Indicateurs servi est paginé (`evidence/C17/verification-production-2026-11-07-soir/`).
- **Décision d'Era (S9)** : dans les tournures de conseil, la sortie AMF passe en liste fermée, choix « fail-closed » ;
  coût accepté et testé : 4 faits refusés par choix. Trois réécritures en liste ouverte avaient chacune été contournées.
- **Décision d'Era (C16.1)** : le critère reste à consolider ; la revue du lundi reprend le 09/11, consignée ; aucun
  document passé reconstitué. Règle retenue : un vert avec limites exige que chaque élément du critère soit prouvé.
- **Manque découvert** : le calcul EcoIndex des 03/10 au 06/11 classait des fichiers de l'interface comme des routes de
  l'API ; corrigé le 07/11, notes inchangées, poids de Briefing et Question publiés dans E4 (§ 4.7) sous-estimés.
- **Manque découvert** : aucune revue du lundi n'a jamais été consignée depuis la mise en place de la méthode (28/09).

## 2026-11-07, après-midi : second regard d'un autre agent sur la branche du banc ; E2 v1.5 harmonisée

**Corrigé.** Six phrases d'E2 encore au passé du banc : l'introduction, § 3.7, la latence (une prise ne garantit pas les
suivantes), la décision Langfuse du 06/11, la provenance des notes dans la preuve Azure, les annexes A2 et A3 datées
comme état du 03/11.

**Manque découvert.** `_texte_mistral` acceptait une chaîne vide comme réponse : un appel sans texte aurait été compté
comme disponible au banc. Aucune des 60 réponses n'est concernée ; corrigé avec son test.

---

## 2026-11-07, midi : banc C7 refait (Azure en zone UE, Mistral Large 3) ; corrections du double contrôle de #222 ; E2 v1.5

**Livrables.** E2 v1.5 remplace la v1.4 pour `livrable-E2-v4`. E3 v2.4 et E4 v1.8 corrigées sans changer de numéro de
version (aucune n'est taguée).

**Décisions d'Era.**
- Refaire le banc sur Azure tel qu'il tourne aujourd'hui, puis mesurer Mistral.
- Large 3 au même budget qu'Azure, après le refus de Large 4 par Mistral.
- Les notes de français : notes proposées par une IA à l'aveugle, acceptées par Era sans modification.
- Un budget Azure avec alertes et un plafond Mistral.
- Sur la capture du budget, masquer seulement l'identifiant et les adresses.

**Manques découverts.**
- Mistral a retiré `reasoning_effort: "none"` depuis le 10/10 ; Large 4 ne rend plus de texte dans le budget du rédacteur.
- Le plafond du script du banc ne protège ni Azure ni Mistral : il ne connaît que le prix d'OpenRouter. Une première
  note disait le contraire, corrigée après la relecture d'un autre agent.
- La première prise du frein (08:51) ne conservait pas les en-têtes et ne prouvait pas l'indépendance de deux
  visiteurs HTTPS. Seconde prise complète à 09:46.
- L'heure de livraison écrite au matin (01:54) était celle de la construction de l'image ; la bascule s'est faite à
  02:00:39 (fin du job `deployer`).

---

## 2026-11-07, matin : vérifications en production terminées ; E2 v1.4, E3 v2.4, E4 v1.8 pour leurs tags

**Livrables.**
- E2 v1.4 (C8.2 tenu, 20 ✅) pour `livrable-E2-v4`.
- E3 v2.4 (ligne OWASP tenue, 39 ✅) pour `livrable-E3-v5`.
- E4 v1.8 (C17.5 tenu, 34 ✅ · 4 🟡) pour `livrable-E4-v6`.
- Ces versions remplacent E2 v1.3, E3 v2.3 et E4 v1.7, jamais taguées.
- Chaque changement de statut repose sur une mesure du site réel du 07/11 (`evidence/C17/verification-production-2026-11-07/`).

**Manque.** E4 disait encore « #74 non déployée » et « rôle propriétaire (#76) » à trois endroits ; corrigés.

---

## 2026-11-07, 3 h UTC : livraison en production de `develop` (#221) ; port en clair et collecte non planifiée découverts

**Livré.** `main` à `a68f2cf` le 07/11 à 1 h 54 UTC : en-têtes de sécurité, compression, rôle `rita_api`, mots de passe
sans valeur de secours, port de l'API lié à la machine, contrat 1.2.0, frein des essais de clé, consigne de l'écran
Question. Vérifié sur le site réel à 2 h UTC (`evidence/C17/verification-production-2026-11-07/`).

**Décisions.**
- S3, option A (par adresse), validée par Era.
- La fusion de `develop` dans `main` a été faite sans le double contrôle par un autre agent prévu le 06/11. Choix
  d'Era, après la revue automatique de Claude, sans problème trouvé ; Codex était en échec, limite d'usage.

**Manques découverts.**
- Le port 8001 répondait en clair depuis Internet (corrigé par #218, vérifié après la livraison).
- L'étape du serveur de #76 n'avait pas la réinstallation du fichier Compose, sans laquelle la livraison aurait été
  refusée (ajoutée au guide).
- Le premier mot de passe de `rita_api` s'est affiché dans le terminal (remplacé).
- Aucune collecte planifiée en production : les données s'arrêtaient au 04/11.

---

## 2026-11-07, nuit : E3 v2.3 et E4 v1.7, pour `livrable-E3-v5` et `livrable-E4-v6` ; quatre corrections de sécurité dans `develop`

**Livrables.** E3 v2.3 (38 ✅ · 1 🟡) : #152 prouvé par le job `base` de `main`, #73 vérifié à la main en production avec
deux captures, choix de Langfuse réévalué (accessibilité, règle UE). E4 v1.7 (33 ✅ · 5 🟡) : prestataires réévalués
(C15.2), système de conception écrit et tenu par un test, Question et Tableau de bord comparés (C17.2), mesure de #74
(§ 4.7). Ces deux versions remplacent E3 v2.2 et E4 v1.6 pour leurs tags, qui ne sont pas encore posés.

**Décisions.** D7 : la documentation de l'API reste publique, motivée et vérifiée (47 tests). #76 : l'API lit la base avec
un rôle `rita_api` (lecture, plus l'ajout au journal d'audit), plan validé par Era, essayé sur une copie neuve avant la
production. S1 : en-têtes de sécurité, politique de contenu stricte sur les cinq écrans. S8 : plus de mot de passe par
défaut, base de développement sur `127.0.0.1`. Vigie planifiée toutes les trois heures.

**Manques.** L'API lisait la base avec le propriétaire depuis le début (écart à la matrice d'accès validée le 03/10,
corrigé par #76, pas encore en production). Neuf PR fusionnées sans le double contrôle par un autre agent prévu par la
règle d'Era du 06/11 ; la revue automatique de Codex a échoué (limite d'usage). #207 a été fusionnée sans son dernier
commit, rattrapé par #216 : une PR ne se fusionne qu'avec la vérification que la branche distante porte le dernier commit.

---

## 2026-11-06, nuit : la règle « UE seule » précisée par Era, et vérifiée service par service

**Décision.** Aucun des deux sous-traitants (Microsoft pour Azure, ClickHouse pour Langfuse) ne garantit la lettre de la
règle du 05/10 : leurs contrats prévoient des sorties de la région. Era précise la règle : services configurés dans
leurs régions de l'UE, plus de promesse d'absence absolue de transfert, exceptions identifiées, garanties vérifiées,
données limitées. Vérifié le soir même : DPA de Microsoft du 01/11/2026 et DPA de ClickHouse du 10/04/2026 relus ;
Microsoft Corporation et ClickHouse, Inc. actives au Data Privacy Framework sur la liste officielle. Registre RGPD mis à
jour par ajouts datés (PR #214). **Manque** : l'écran Question n'invitait pas à taire les données personnelles ; la
consigne est écrite, pas encore en production. La décision ne rend aucun critère vert : E2 v1.3 garde C8.2 à
consolider jusqu'à ce déploiement ; l'entrée ci-dessous, écrite plus tôt le même soir, disait la décision ouverte.

---

## 2026-11-06, soir : E2 v1.3, le retour du formateur appliqué, pour `livrable-E2-v4`

**Livrable et manque.** Le formateur demande le 06/11 un exemple de veille complet, des preuves visibles du service et
un texte plus lisible. E2 v1.3 y répond : la source S36 vérifiée critère par critère avec captures (annexe A4),
l'accessibilité des sources relevée par un script, les conditions de Microsoft relues, le service montré en production
(adresse, connexion à clé masquée, portail Azure, puis un briefing d'OR.PA et sa trace Langfuse reliés par la même
référence, annexe A6), des repères pour retrouver chaque critère. La correction du prompt (option B, décidée le 11/10)
est en production depuis le 06/11 (`097b201`). E2 v1.2 n'est pas taguée : `livrable-E2-v4` portera la v1.3, après le
double contrôle par un autre agent. **Manque** : C8.2 reste à consolider, la règle UE seule n'étant pas démontrée pour
Azure ; la décision de risque est écrite comme ouverte, à prendre par Era après l'oral blanc. Les articles fournis au
briefing de démonstration datent du 14 au 17/09.

---

## 2026-11-06 : E3 v2.2, statuts de #73 et #152 et contrôles de fusion harmonisés, pour `livrable-E3-v5`

**Livrable.** Le double contrôle du 06/11 a montré que la v2.1 du dépôt gardait des formulations anciennes, corrigées
seulement dans une copie PDF du 04/11 : #73 « non corrigé », #152 « pas encore en production », six contrôles de fusion au
lieu de sept. La v2.2 reporte ces corrections dans la source (#73 corrigé le 01/11 et déployé le 02/11, vérification manuelle
à faire ; #152 intégré à `main` le 02/11, la passerelle restant hors de l'image de production ; sept contrôles depuis le
01/11, dont `base`) et prend le style des titres. Aucun statut ne change ; code et preuves restent sous `livrable-E3-v4`.
**Leçon** : une correction faite dans une copie PDF doit être reportée dans la source le jour même.

---

## 2026-11-06 : E5 v0.9, mise en forme seule, pour `livrable-E5-v4`

**Livrable.** E5 prend le style de titres d'E2 et d'E4 ; le texte, les 5 pages, les 29 liens et les 11 signets ne
changent pas. La version remise reste sous `livrable-E5-v3`.

---

## 2026-11-06 : E2 v1.2 et E4 v1.6, corrigés après double contrôle, pour `livrable-E2-v4` et `livrable-E4-v6`

**Livrables et décision.** Après la remise du 05/11, Era fait relire E2 et E4 par un autre agent, et décide qu'aucun tag
ne sera plus posé sans ce double contrôle. E2 v1.2 corrige trois formulations : le secours (« aucun fournisseur de
secours n'est activé pour le briefing dans la version présentée »), le test de l'ordre des fournisseurs (« test présent ;
journal non conservé », qui règle le manque du 05/11 ci-dessous) et le nombre de sujets du guide (C8.4). E4 v1.6 date
une phrase du § 2.7 (« Au 02/11 »), qui contredisait le § 6.5. Aucun résultat, statut ni montant ne change. Les deux
rapports prennent le style de titres choisi par Era, rendu depuis la source par `scripts/rendre_pdf.py`. Les versions
remises restent sous `livrable-E2-v3` et `livrable-E4-v5`.

---

## 2026-11-06 : la clé par client est reportée après l'oral blanc, présentée comme une limite

**Décision structurante** (Era) : le retour écrit du formateur du 03/11 demandait une clé par client avant le jury, ou
une limite expliquée avec sa solution et son coût. La spécification 002 est validée le 05/11 et son plan relu deux fois
(v2 du 06/11) : 32,5 h, environ 4 journées et 1 700 € HT, contre 1 à 2 journées estimées le 03/11 (`docs/BUDGET.md`).
L'implémentation est **reportée après l'oral blanc des 12-13/11 et réévaluée le 14/11** ; priorité à la fin de la
préparation le 07/11, puis aux répétitions. D'ici là, la clé partagée est présentée comme une limite, avec sa solution
(`specs/002-cle-par-client/`) et son estimation. Aucun rapport figé n'est modifié.

---

## 2026-11-05, 22 h : E2 v1.1 annonce un test « vu en échec » dont le journal n'est pas conservé

**Manque découvert** (relecture des affirmations d'E2 pendant la préparation de l'oral) : le rapport E2 v1.1 (§ 4.2, tag
`livrable-E2-v3`) écrit que le test de l'ordre par défaut des fournisseurs a été « écrit d'abord et vu en échec »
(`d1cbb7b`). Le commit contient le test et le correctif ensemble, et son message dit « test d abord » ; mais ni
`evidence/` ni le rapport ne gardent la sortie de l'exécution en échec. Cela ne prouve pas que l'essai n'a pas eu lieu :
cela empêche seulement de le montrer. Le rapport, figé, n'est pas modifié. À l'oral : « le journal de l'échec initial
n'est pas conservé ; je peux montrer le test, la correction et leur historique ». Leçon : quand un rapport cite un test
rouge, la sortie de `pytest` avant le correctif va dans `evidence/`, comme pour INC-009 (`pytest-avant.txt`).

---

## 2026-11-05, soir : E5 v0.8, faits revérifiés au 05/11, pour le tag `livrable-E5-v3`

**Livrable** : E5 v0.8, `docs/rapports/E5/rapport-E5.pdf` (5 pages, langue fr, balisé). Chaque fait daté de la v0.7 a
été revérifié le 05/11 : la réception du guide est confirmée par le formateur depuis le 04/11 (C20.7, preuve dans
`evidence/C8/`) ; le tableau de bord de production répond (HTTP 200) ; #77 et #132 sont encore ouvertes ; la dernière
exécution du workflow d'alerte date toujours du 24/10. Le reste est inchangé et toujours vrai. Liens vers le tag
`livrable-E5-v3`, aux mêmes cibles. Aucun statut de critère changé. Le tag se pose sur le commit de fusion qui porte
cette entrée, seul dans son push ; `livrable-E5-v1` et `livrable-E5-v2` restent.

---

## 2026-11-05, fin d'après-midi : E4 v1.5, export accessible, pour le tag `livrable-E4-v5`

**Livrable** : E4 v1.5, `docs/rapports/E4/rapport-E4-avec-annexe.pdf`, rendu comme E2 v1.1 dans un seul document Chrome
(`scripts/rendre_pdf.py --annexe`) : 34 pages (20 en portrait, 14 en paysage), langue fr, arbre de structure, pieds de 1
à 34. La v1.4, assemblée par `scripts/assembler_pdf_avec_annexe.py`, déclarait sa langue mais n'avait pas d'arbre de
structure. Comparé à la v1.4 : texte identique hors les deux lignes de version et une phrase de l'historique ; liens
externes aux mêmes cibles, passés du tag `livrable-E4-v4` au tag `livrable-E4-v5` ; 16 liens internes et 68 signets
gardés. **Manque découvert** : les pages que l'annexe annonce dans le PDF complet n'étaient tenues par aucun test ; un
test les compare désormais aux signets. Aucun statut de critère changé. Le tag `livrable-E4-v5` se pose sur le commit de
fusion qui porte cette entrée, seul dans son push ; `livrable-E4-v1` à `livrable-E4-v4` restent. **Décision d'Era** :
E1 n'est pas refait. Son livret de 5 pages est balisé, mais sa couverture et ses quatre annexes sont des pages mises en
forme hors du dépôt, sans source que Chrome puisse rendre ; la limite est écrite dans le README.

---

## 2026-11-05, après-midi : E2 v1.1, export accessible et deux faits du 04/11, pour le tag `livrable-E2-v3`

**Manque découvert** (mesure du 05/11 sur les fichiers remis) : chaque rapport seul est en français et balisé pour les
lecteurs d'écran, mais les PDF « avec annexe » d'E1, E2 et E4 ne l'étaient pas : la fusion après coup (pypdf) garde
pages, liens et signets, et perd la langue déclarée et l'arbre de structure. E2 v1.0 disait aussi deux faits dépassés
depuis le 04/11 : l'accusé de réception du formateur « demandé », la réponse 503 « pas faite ».

**Décision** : le rapport et son annexe se rendent dans un seul document Chrome (`scripts/rendre_pdf.py --annexe`, tests
d'abord) ; l'annexe garde sa page en paysage et ses règles ne touchent qu'elle. **Livrable** : E2 v1.1,
`docs/rapports/E2/rapport-E2-avec-annexe.pdf` (20 pages, langue fr, arbre de structure, pieds de 1 à 20) ; texte des
20 pages comparé à la v1.0 : seuls changent six passages du rapport et la légende d'A1, mis à jour avec leur preuve (la
relecture extérieure du 05/11 a relevé les deux derniers, § 2.7 et A1), la ligne de version et
l'historique. Aucun statut de critère changé. Le tag `livrable-E2-v3` se pose sur le commit de fusion qui porte cette
entrée, seul dans son push ; `livrable-E2-v1` et `livrable-E2-v2` restent. **Limite** : ce balisage n'est pas un audit
d'accessibilité complet ; E4 et E1 restent à refaire de la même façon.

---

## 2026-11-05, matin : E4 v1.4, quatre corrections de cohérence, pour le tag `livrable-E4-v4`

**Manque découvert** (relecture extérieure du 05/11) : E4 v1.3 gardait quatre incohérences. Le tableau des
workflows coupait la ligne de `test.yml` ; C16.4 disait l'accès au Kanban « non revérifié », alors que le formateur
l'a confirmé le 03/11 ; S6 restait ouvert, alors que `/briefing` répond 503 `AUCUN_FOURNISSEUR` depuis le 04/11,
testé ; l'accès du jury était annoncé « au moment de l'évaluation », au lieu d'avant la consultation des livrables.
Le PDF complet ne déclarait pas non plus sa langue : `scripts/assembler_pdf_avec_annexe.py` la remet, test d'abord.
**Limite** : le balisage d'accessibilité (arbre de structure) des deux documents n'est pas fusionné ; le rapport
seul, rendu par Chrome, reste balisé. Aucun statut de critère changé. `livrable-E4-v3` reste, figé.

---

## 2026-11-05, nuit : E4 v1.3 sur `main`, prête pour le tag `livrable-E4-v3`

**Livrable** : E4 v1.3, `docs/rapports/E4/rapport-E4-avec-annexe.pdf` (34 pages : rapport 20, annexe 14 ; SHA-256
`790e67b1…`), sur `main` par la PR #186 (`6f8474b`). Le tag `livrable-E4-v3` se pose sur le commit de fusion qui porte
cette entrée, seul dans son push ; `livrable-E4-v1` et `livrable-E4-v2` restent. Aucun statut de critère changé.

**Manque découvert** : la porte de livraison exige que le tag soit cité dans `ETAT.md` et `CHANGELOG.md`
(`scripts/verifier_livrable.py`, `tag_cite`) ; sur `6f8474b`, le CHANGELOG ne le citait pas. Le tag posé là aurait été
refusé par la livraison, sans image publiée sous son nom, et un tag `livrable-*` ne se déplace plus : d'où cette entrée
avant le tag.

---

## 2026-11-04, nuit : E4 v1.3 et son annexe relue en entier ; deux défauts de l'écran Briefing livré

**Manque découvert** : la première préparation d'E4 v1.3 avait changé les liens de l'annexe sans relire ses textes ni ceux
de ses images ; une relecture extérieure l'a vu. L'annexe est maintenant relue en entier : légendes datées pour ce qui
promettait trop ou avait vieilli, images non retouchées, et une section A7 qui compare les maquettes de la refonte aux
écrans livrés. Cette comparaison a trouvé deux défauts sur l'écran Briefing en production : l'aide promet qu'une
recommandation est « retenue, jamais diffusée », ce que le garde-fou ne garantit pas, et les astérisques de mise en forme
du modèle s'affichent. À corriger à part, test d'abord. Aucun statut de critère changé.

---

## 2026-11-04, soir : nouvelle interface et Viridien en production, cours rattrapés au 04/11 ; trois manques du script de rattrapage

**Décisions structurantes** (accords d'Era, chacun sur une demande écrite) : la refonte de l'interface est livrée en
production (`8ecc5a7`, fichiers servis vérifiés) ; la ligne Viridien est corrigée en base de production, exactement quatre
cellules, sauvegardes S1 et S2 comparées cellule par cellule ; les cotations et les taux sont rattrapés une fois, jusqu'au
04/11, sous verrou, sauvegardes R1 et R2 sans différence hors `cotation` et `taux_change`. Écrans vérifiés par Era avec sa
clé. Preuve : `evidence/C3/preuve-correction-viridien-production-2026-11-04.md`.

**Manque découvert** (relecture du 04/11) : le script du rattrapage a réussi, mais il n'est pas réutilisable en l'état. Sa
condition de complétude ne vérifie pas les dates exactes ; une erreur technique peut ne pas l'arrêter ; son retour arrière
recharge toute une plage de dates. À corriger, essai à l'appui, avant toute réutilisation ou automatisation (§ 9.1 de la
preuve). La collecte automatique reste une décision séparée : sans elle, les cours vieillissent de nouveau.

**Remise** (réponse écrite d'Elbby du 04/11) : un PDF par rapport, annexes comprises, est accepté ; l'accès du jury au
dépôt se voit avec Héléna VICENTE.

---

## 2026-11-03, nuit : quatre tags posés, sans exécution de livraison

**Livrables figés** : `livrable-E2-v2` (E2 v1.0), `livrable-E3-v4` (E3 v2.1), `livrable-E4-v2` (E4 v1.2) et
`livrable-E5-v2` (E5 v0.7), sur `2310f87`, fusion de la PR #178 ; E1 reste `livrable-E1-v6`.

**Manque découvert** : les quatre tags ont été poussés en une seule commande. GitHub ne crée pas d'événement de push
quand plus de trois tags arrivent ensemble (documentation GitHub, « Events that trigger workflows » :
https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows, lue le 03/11) :
aucune exécution de « Livraison » n'a suivi, donc ni Definition of Done
rejouée par la chaîne, ni image publiée sous ces noms. Les tags ne peuvent être ni supprimés ni déplacés (ruleset), et
le workflow n'a pas de déclencheur manuel. Compensé et prouvé autrement : la même image (commit `2310f87`) est
construite, publiée et déployée par l'exécution de `main` 41722049240 ; la Definition of Done est rejouée sur le poste
(livrable) ; les 244 liens des PDF répondent à leur tag. Règle : un tag par commande, jamais plus de trois à la fois.

---

## 2026-11-03, nuit : « à consolider » dans tous les rapports, E2 v1.0, E3 v2.1, E4 v1.2, E5 v0.7

**Manque découvert** par Era : le libellé « à consolider », choisi le 03/11 pour la grille des compétences, n'avait
pas été reporté dans les rapports. E3 écrivait encore « 🟠 partiel » (11 fois « partiel », 7 🟠), E4 « partiel » (4)
et ⚠️ (15), E2 ⚠️ (8) et « preuve partielle », E5 ⚠️ (2). La recherche de l'ancienne valeur dans tout le dépôt n'avait
pas été faite.

**Décision d'Era** : partout, « à consolider » (🟡). Les tags étant figés, quatre nouvelles versions, figées par les
tags `livrable-E2-v2`, `livrable-E3-v4`, `livrable-E4-v2` et `livrable-E5-v2` à poser sur `main` après la PR #178, qui intègrent
aussi la note de mise à jour écrite plus tôt le même jour : huit critères passés à ✅ après l'envoi du 03/11 (E2 :
C6.2, C6.4, C8.5 ; E4 : C16.3, C17.11, C18.6, C19.7 ; E5 : C20.7), l'en-tête d'E3 (accès des examinateurs) et la clé
d'exercice (403, 503), la phrase d'E4 (§ 1.7 et § 7.3). Chaque remplacement compté avant d'écrire ; liens déplacés
vers les nouveaux tags (E3 : 133, E4 : 185 et 16 dans l'annexe, E5 : 21) ; pages inchangées. La note est remplacée :
elle reste dans le dépôt, elle ne part pas avec la remise. E1 v6 ne change pas. Annexe d'E4 : six schémas (A1, A3, A4,
A5, les deux A6) remplacés par la mise en forme fournie par Era au style des schémas d'E1, texte comparé aux originaux,
identique ; les originaux restent dans `evidence/` ; annexe toujours de 10 pages.
Annexe d'E2 : les trois schémas remplacés par la mise en forme fournie par Era ; deux phrases dépassées, dans A1
(« envoi au formateur non effectué ») et A3 (« remise prévue le 05/11 »), corrigées dans le générateur (test d'abord)
et dans les deux images, pour dire l'envoi du 03/11 ; annexe toujours de 3 pages.

**Décision d'Era, le même soir : « Mistral testé, non activé ».** Azure reste seul en production pour la remise. Le
10/10, Mistral Large 4 a servi un vrai briefing (LVMH) par la route de RITA, sur la branche `mistral-ue` ; avant d'en
faire le secours d'Azure, il reste une comparaison sur les 10 cas du banc et la lecture de son contrat. Annexe d'E2 :
A2 (case du 10/10) et A3 (secours envisagé) le disent, générateur et images d'accord, test d'abord ; la preuve est
citée en texte, sans lien vers la branche ni vers la PR #88, qui reste séparée. Classeurs remis d'accord (B52 décrivait
encore trois fournisseurs en cascade ; versions E2 v1.0, E3 v2.1, E4 v1.2, E5 v0.7 ; 98 cellules, statuts inchangés,
120 ✅ · 17 🟡 · 0 ❌) ; présentateur : six liens PDF d'E2 réparés, « J'ai testé Mistral ».

---

## 2026-11-03, soir : note de mise à jour des rapports E2 à E5

**Manque découvert** par une relecture externe des rapports tagués, vérifiée point par point dans le dépôt : E3 annonce
en en-tête « formateur et jury invités » alors que le jury ne l'est pas (`rapport-E3.md:27`, contredit par la ligne 151),
et dit « 503 » sans la clé d'exercice là où l'API répond 403 (`api/exercice.py:36-45`) ; une phrase d'E4 (§ 1.7, reprise au § 7.3) dit
rétrospective la spécification de l'écran Question, versionnée le 15/10 (`e16ec77`), avant l'écran du 16/10 (`98177c2`).
Les auto-évaluations d'E2, E4 et E5 sont aussi en retard sur huit critères passés à ✅ après leurs tags (C6.2, C6.4,
C8.5, C16.3, C17.11, C18.6, C19.7, C20.7).

**Décision d'Era** : une note d'une page, datée, à côté des rapports
([`docs/rapports/note-mise-a-jour-2026-11-03.pdf`](docs/rapports/note-mise-a-jour-2026-11-03.pdf)), plutôt que de
nouvelles versions à 36 heures de la remise. Chaque correction pointe vers sa preuve, au tag ou au commit ; 12 liens
vérifiés par `gh api`. Les rapports et leurs tags ne changent pas ; la note s'ajoute aux 9 fichiers de la remise.

---

## 2026-11-03, après-midi : annexes A et C d'E1 v6 corrigées avant le tag

**Manque découvert** par une relecture des 10 pages : les schémas des annexes A (collecte) et C (nettoyage) disaient encore
« 11 partitions par année », comme le livret avant sa correction ; le Parquet en a 11 au total, une par année. Corrigé dans
le générateur des schémas (test d'abord), l'illustration de la collecte, les PNG et les pages 7 et 9 du PDF avec annexes,
sur la PR #176, avant le tag `livrable-E1-v6`.

---

## 2026-11-03 : `livrable-E5-v1` posé ; budget d'E1 en trois montants avec TJM ; E1 v6 prêt pour `livrable-E1-v6`

**Décisions d'Era** : fusion de la PR #175 et tag `livrable-E5-v1` ; après le retour écrit du formateur du 03/11, le
budget du livret E1 se présente en trois montants séparés (dépenses, travail au TJM de 400 €, fonctionnement par
mois), ce qui remplace la décision du 28/10 « pas de TJM » ; la clé par client (C5) devient une évolution prévue avant
le jury, chiffrée à 1 à 2 journées ; remise d'E1 en 10 pages (« Livret E1 de 5 pages, accompagné d'une couverture et
de 4 pages d'annexes »), le texte officiel fixant « Livrable d'entre 2 et 5 pages » sans parler des annexes ; tag
`livrable-E1-v6` à poser après la fusion.

**Manques découverts** : par le formateur, la limite C5 présentée sans solution ni coût, et une démo E3 limitée au
service d'IA (intégration, monitoring, tests et CI/CD absents) ; la consommation OpenRouter, « à lire » depuis le 31/10,
relevée à 0,97 $ sur les trois clés du projet. Par la seconde relecture d'E1 v6 : le PDF avec annexes avait perdu les
11 liens du sommaire (rétablis) ; « 11 partitions par année », inexact depuis la v5 (11 au total, une par année) ; le
livret disait le jury invité, alors qu'il ne l'est pas encore ; le guide du jury citait encore `livrable-E1-v3` et
`livrable-E3-v2`.

**Preuve reçue** : le formateur confirme par écrit, le 03/11 à 11 h 55, qu'il ouvre le tableau Kanban privé depuis son
compte (C16.4, `evidence/C16/preuve-acces-kanban-formateur-2026-11-03.md`).

**Envoyé au formateur** (03/11, 14 h 42) : la synthèse de veille et le guide d'exploitation en PDF joints, les liens de
la méthode Kanban et de la documentation technique, le schéma du parcours Question ; preuve datée dans
`evidence/C8/envoi-documents-formateur-2026-11-03.md`. **Décision d'Era** : les sept critères qui attendaient cet
envoi (C6.4, C8.5, C16.3, C17.11, C18.6, C19.7, C20.7) passent à ✅ dans les classeurs, qui comptent 119 ✅ · 18 🟡 ·
0 ❌. **Rien n'est encore envoyé** pour E1 v6.

## 2026-11-02, nuit : `livrable-E4-v1` posé ; E5 v0.6 prêt pour `livrable-E5-v1`

**Décisions d'Era** : fusion de la PR #174 et tag `livrable-E4-v1` ; statuts d'E5 confirmés (10 ✅, C20.5 et C20.7 ⚠️).

**Manques découverts** : la relecture indépendante d'E4 a trouvé 17 écarts entre le rapport et le dépôt (dont des
surpromesses sur l'accessibilité testée et des décomptes périmés), tous corrigés avant le tag ; E5 ne citait pas
l'issue #132, encore ouverte depuis le 23/10.

---

## 2026-11-02, soir : `main` en production (`174b0c1`) ; livrables E1, E2, E3 tagués ; E4 v1.1 prêt pour `livrable-E4-v1`

**Décisions d'Era** : fusion de la PR #173 et déploiement ; tags `livrable-E1-v5`, `livrable-E2-v1`, `livrable-E3-v3` ;
C6.2 réévalué sur la planification ; dans E4 v1.1, C14.2, C14.3, C14.4, C15.3, C17.3 et C17.4 passent à ✅, chaque
limite comparée aux mots du critère et gardée dans sa colonne ; tag `livrable-E4-v1` à poser après la fusion.

**Manques découverts** : la passerelle MCP n'est pas dans l'image de production (#152 n'est donc pas « en production ») ;
le tableau OWASP d'E3 confond 503 et 403 pour les routes d'exercice (le code les distingue) ; le présentateur ouvrait
encore le livret v3 et gardait d'anciennes notes de budget et de MCD (corrigés hors du dépôt).

**Rien n'est encore envoyé au formateur** : l'entrée « livrable envoyé » viendra avec la preuve datée.

---

## 2026-11-02 : retour écrit du formateur appliqué, MCD aligné sur la base ; E1 v5, E2 v0.9 et E3 v2.0 prêts

**Manques découverts** : par la recette des écrans, un focus absent sur le tableau de bord (corrigé) et des cas d'erreur
vérifiés seulement par lecture du code (testés depuis) ; par le formateur, l'écart entre le MCD et la base (un `1,n` que
rien n'imposait) ; par la relecture d'E2, un « contrôle automatique du prompt » annoncé que le banc ne faisait pas, et
`/sante` confondu avec la vigie ; dans le PDF E1 avec annexes, une ancienne page 6 à 0,12 ms.

**Décisions structurantes d'Era** : `VALEUR 0,n` pour la cotation (le modèle s'aligne sur la base, aucun contrôle ajouté
à l'import) ; nouvelles versions E1 v5 et E3 v2.0, et pas seulement un oral ajusté ; la réponse 403 est gardée et
défendue ; E2 v0.8 pour la relecture du formateur, v0.9 pour le jury. Détail dans `CONTINUITE.md`, D.

**Rien n'est envoyé ni fusionné dans `main`** : les tags `livrable-E1-v5`, `livrable-E2-v1` et `livrable-E3-v3` se posent
après la fusion, avant tout envoi, et les liens se vérifient alors (zéro cassé exigé).

---

## 2026-11-01, nuit : recette, quatre manques corrigés avec leurs tests ; job `base` exigé pour fusionner dans `main`

**Manques découverts, puis corrigés sur `develop`, tests écrits avant** (pas encore en production) : #78, un RSI de 100
sur une série plate ; #73, une clé gardée avant d'avoir été acceptée, sur Briefing et Question ; #79, une pire baisse
positive quand le cours ne fait que monter ; #152, un verrou de démonstration de la passerelle MCP qui refusait le jeu
réellement importé, acceptait d'autres prix de revient et absorbait les doublons, puis, à la seconde revue, transmettait
des champs mal formés. Preuves avant et après : `evidence/C17/correctifs-2026-11-01/`.

**Manque découvert dans la CI** : les tests qui demandent PostgreSQL se sautaient en intégration continue, faute de
base, et la chaîne restait verte sans les avoir exécutés.

**Décisions structurantes** : un job `base` (PostgreSQL 18 jetable, schéma et rôles du dépôt, échec au moindre test
sauté), vérifié sur GitHub (43 puis 46 réussis, 0 sauté), puis ajouté le 01/11 à 23 h 11, sur décision d'Era, aux
contrôles exigés de `main protegee` (sept checks). Pour #152 : un jeu de démonstration versionné de sept positions,
relié au vrai import par un test, sans nouvelle route d'API pour les alias. Détail dans `CONTINUITE.md`, D.

**Rapports sur `develop`** : E2 v0.7 (16 pages, annexe de 4), E4 v1.0 (20 pages, 29 avec l'annexe ; 21 ✅ · 17 ⚠️ ·
0 ❌), E5 v0.5 (5 pages). La recette ne change aucun statut d'elle-même : réévaluation critère par critère après
vérification (`docs/recette/registre-des-partiels.md`).

---

## 2026-11-01 : manque découvert dans la chaîne d'alerte (INC-009), corrigé et en production ; E4 v0.9, E5 v0.4 ; décisions avant la remise

**Manque découvert** : un message de retour à la normale de Langfuse (« [OK] … recovered ») a ouvert le 24/10 un
nouveau ticket d'incident, #137, l'issue #130 de la même alerte ayant été fermée la veille. Le workflow
`alerte-incident.yml` lisait la gravité mais ne s'en servait pas pour décider. Trouvé le 31/10 en relisant les issues
`incident` restées ouvertes pour E5 : #137 depuis sept jours, #77 depuis quatre semaines. Aucune routine ne relit ces
issues.

**Corrigé et en production** : reproduit sur le workflow de `4be89d0` dans un conteneur jetable (13 passed, 1 failed),
14 passed après correctif, mêmes tests ; PR #171 vers `develop`, puis PR #172 vers `main` (`922349d`), livrée le 01/11 ;
#137 fermée avec sa justification. Post-mortem `evidence/C21/INC-009-retour-a-la-normale-ouvre-un-incident.md`. Un
retour à la normale réel n'a pas encore été traité par le nouveau code.

**Rapports** : E4 v0.9 (première page et sommaire sur le modèle d'E3, annexe des schémas, deux extraits de code
commentés) et E5 v0.4 (premier rapport E5, cinq pages, un extrait de code), sur `develop` ; E4 aussi sur `main`.

**Décisions d'Era** (détail dans `CONTINUITE.md`, D) : remise du guide d'exploitation avec les livrables du 05/11, dans
son dossier Drive partagé, formateur prévenu, preuve datée à conserver (quel fichier, avec qui, quand) ; périmètre
d'E5 ; ni nouvelle fonctionnalité ni nouveau banc avant le 05/11 ; la preuve de l'isolement de la copie du 23/10 en
entier dans E5, une phrase dans E2. **Manque assumé** : l'accès du jury au dépôt privé n'est pas confirmé (le formateur, lui, le lit).

**Auto-évaluation d'E2 revue contre le règlement** (p. 22 à 24) : C6.3, C7.1, C7.3, C7.5 et C7.7 passent à ✅, sans preuve nouvelle, chacun avec sa limite ; C7.6 aussi, une fois
les prérequis d'Azure et d'OpenRouter présentés côte à côte ; décompte 13 ✅ · 6 ⚠️ · 1 ❌ (avant : 7 · 12 · 1). **Manque découvert** : la
grille d'E4 n'a pas de ligne pour les deux critères de documentation de C19 (installation et test de la chaîne,
format accessible), présents dans le référentiel (p. 21) ; à décider par Era. **Feuille
de route proposée pour la suite, à confirmer par Era** (`CONTINUITE.md`, G) : d'abord la date de séance et l'heure de
rédaction à l'écran, ensuite un pilote d'annonces réglementées sur une entreprise.

---

## 2026-10-31 : manque découvert en production (Claude encore en repli), corrigé et livré ; notation C7 terminée

**Manque découvert** : la variable `LLM_ORDRE` lue dans le conteneur de production valait
`foundry,anthropic,openrouter`, l'ancienne valeur par défaut de `src/llm.py` et de `docker-compose.yml`. Sur une
erreur d'Azure, la production aurait appelé Claude par Anthropic puis par OpenRouter, sans garantie de traitement dans
l'UE. Les décisions du 10/10 (Mistral remplace Anthropic et OpenRouter) et du 11/10 (Azure seul tant que le contrat de
Mistral n'est pas lu) n'étaient appliquées que sur le poste ; le remplacement par Mistral vit sur la PR #88, ouverte et
en conflit. INC-008 (14/10) écrit « `LLM_ORDRE=foundry` » pour la production : contredit par la lecture du 31/10 sur le
conteneur du 27/10 ; l'état du 14/10 n'est plus vérifiable.

**Corrigé et livré** : valeur par défaut `foundry` dans le code, Compose et le modèle de configuration, test d'abord
(`d1cbb7b`) ; PR #170 fusionnée (`97b329e`) ; livraison refusée deux fois par le serveur (« ComposeNonInstalle » : le
fichier Compose installé datait du 14/10), copie relue puis installée à la main par Era, troisième tentative livrée.
Conteneur relu : `LLM_ORDRE=foundry`, `/health` annonce `97b329e`. Documentation alignée (architecture, exploitation,
README, registre RGPD).

**Notation C7** : 60 textes sur 60, tous à 1 sur 2, évaluation assistée par IA, relue et validée par Era ; jointure
avec la clé : 30 textes par fournisseur, moyenne 1,00 des deux côtés. Le français ne départage pas les fournisseurs.

---

## 2026-10-30 (fin de nuit) : relecture globale d'E4, v0.7 ; une précision sur l'entrée précédente

**Fait** : une relecture indépendante a confronté chaque fait d'E4 v0.6 au dépôt et à GitHub (34 constats, dont 5
hauts) ; chaque constat haut vérifié puis corrigé : le schéma d'architecture date du 24/10 et montre le chemin des
questions ; le flux des questions (traitement T8) manquait aux données personnelles ; la preuve en production du
parcours Question (16/10) n'était pas citée ; la mention « revue NON TENUE » de la trame du 05/10 a été écrite avant la
date. Statuts décidés par Era critère par critère : **17 ✅ · 19 ⚠️ · 0 ❌** (C14.1, C14.5 et C15.3 passent en partiel).

**Précision sur l'entrée précédente** : l'affirmation « l'API refuse de démarrer sans clé » n'était pas un manque
découvert le 30/10. Elle avait été corrigée dans le rapport E3 le 11/10, mais pas dans `docs/ARCHITECTURE.md` ni dans
`api/main.py`. Corrigée dans ces fichiers le 30/10 (`a2c0d51`), sans changer le fonctionnement.

---

## 2026-10-30 (nuit) : rapport E4, première version complète à relire ; périmètre d'E4 décidé ; manques découverts

**Décision structurante** (Era) : le rapport E4 décrit la version présentée au jury, ses cinq écrans (`d3a4198`,
livrée le 27/10) ; les ateliers des sprints et les copies d'exercice en sont exclus. Ordre des rapports : E4, puis E2,
puis E5. Règle de la matrice : ✅ seulement si le critère entier est satisfait.

**Fait** : `docs/rapports/E4/rapport-E4.md` de 0 page à une **première version complète (v0.6, `475f74f`)**, huit
sections, auto-évaluation 20 ✅ · 16 ⚠️ · 0 ❌ sur 36 critères. **Pas un livrable validé** : ni relu en entier, ni mis
en PDF, ni envoyé. Recomptage préparatoire : `docs/rapports/E4/recomptage-criteres-2026-10-30.md`.

**Manques découverts** : `docs/ARCHITECTURE.md` (ligne 71) et `api/main.py` affirment que l'API « refuse de démarrer »
sans clé, ce qui est faux (correction en attente d'Era) ; le tableau Kanban n'a plus bougé après le 14/10 ; aucune case
des plans de travail des sprints n'est cochée dans le dépôt (0 sur 221).

---

## 2026-10-29 (soir) : classeurs des compétences remis à l'état du 29/10 ; manque trouvé dans la version envoyée le 28/10

**Manque découvert** : le classeur détaillé envoyé au formateur le 28/10 (branche `classeur-competences`, `c56b899`)
n'a aucune rédaction pour C10 et C11, et cite le rapport E3 v1.5 pour C9, C12 et C13, alors que le rapport envoyé le
29/10 est la v1.9. Les statuts étaient justes : 111 ✅ · 25 🟡 · 1 ❌, les mêmes que le § 10 du rapport E3 v1.9.
**Corrigé hors du dépôt**, dans les copies OneDrive d'Era (identiques à `c56b899` avant modification) : les cinq
classeurs passent à l'état du 29/10, sans changer un seul statut. La branche `classeur-competences` reste au 28/10 ;
la mettre à jour, et prévenir ou non le formateur, sont des décisions d'Era. Détail : `ETAT.md`, « Fait le 29/10 ».

---

## 2026-10-29 (matin) : rapport E3 v1.9 envoyé au formateur ; trois imprécisions de plus relevées

**Livrable envoyé** (Discord, par Era) : le rapport E3 v1.9 (tag `livrable-E3-v2`,
`docs/rapports/E3/rapport-E3-v1.9-bandeau.pdf`, empreinte `579890bfba43e18a`), avec trois précisions dans le message :
le tag du présent livrable (p. 16) ; l'AMF distingue conseil et recommandation, ne rien recommander est le périmètre
choisi pour RITA (p. 1 et glossaire) ; trois formulations trop larges (p. 7, 9 et 13). Contrôlé avant l'envoi :
44 critères en 39 lignes (34 ✅ · 5 🟠), 100 liens sur 100 présents dans le tag, PDF balisé en français.
**Manques découverts** : p. 7, une trace n'est ouverte que pour un appel admis, traçage actif ; p. 9, `request_id`
n'est que dans 13 appels de journal sur 23 ; p. 1, « formateur et jury invités » : au 29/10, seul le formateur est
collaborateur. À corriger dans la version suivante, avec les cinq déjà notées dans `ETAT.md`.
Détail : `docs/FILE-DE-VALIDATION.md`, ligne 8.

---

## 2026-10-28 (soir) : livret E1 v3 et grilles des compétences envoyés au formateur ; E1 accepté

**Livrables envoyés** (Discord, par Era) : le livret E1 v3 (tag `livrable-E1-v3`) et les grilles des compétences
(branche `classeur-competences`, commit `c56b899`). **Retour** : E1 accepté par le formateur le 28/10 (rapporté par Era).
Le rapport E3 v1.9 (tag `livrable-E3-v2`) reste à envoyer, avec ses deux précisions (p. 16 et AMF).
Détail : `docs/FILE-DE-VALIDATION.md`, lignes 7 à 9.

---

## 2026-10-28 : versions d'E1 et d'E3 pour l'oral blanc, budget du livret décidé ; erratum d'E1 et cinq imprécisions d'E3

**Livrables préparés, non encore envoyés** (c'est Era qui envoie) : `docs/rapports/E1/rapport-E1-v3-avec-annexes.pdf`,
le livret du tag `livrable-E1-v3` avec ses liens essentiels, l'erratum de sa page 6 et les annexes de schémas C1, C2,
C3 et C5 ; `docs/rapports/E3/rapport-E3-v1.9-bandeau.pdf`, le rapport du tag `livrable-E3-v2` avec un bandeau en page 1.
Les tags restent figés ; les PDF produits par `scripts/rendre_pdf.py` ne changent pas.

**Décisions d'Era (28/10)** : le budget demandé par le formateur se compte sans TJM, en argent réellement dépensé, en
trois lignes dans le livret E1 v4, après l'oral blanc et sur factures. D'ici là, le critère C1 « présentation complète »
est partiel dans les classeurs (111 ✅ · 25 🟡 · 1 ❌). Google News reste arrêté.

**Manques découverts** : le livret E1 v3 écrit « budget 0 € », faux depuis que le serveur est payé ; le tableau de sa
page 6 porte des étiquettes fausses (erratum ci-dessus, vérifié dans `db/requetes.sql`). Le rapport E3 v1.9 contient
cinq formulations imprécises (pages 1, 12, 13 et 16, détail dans `ETAT.md`), dont « deux garde-fous » sous 85 % quand
le tableau en montre trois : le contrôle de fuite n'a pas de seuil de blocage (`tests/test_evals.py`).

---

## 2026-10-27 (soir) : cours et taux de production rattrapés à la main avant l'oral blanc ; collecte planifiée du serveur toujours absente

**Décision d'Era (27/10)** : la démonstration d'E3 se fait sur la production d'origine, données remises à jour avant ;
les travaux des sprints restent dans leurs branches. Le rattrapage est fait à la main sur le serveur, hors de la chaîne
de livraison, dans un conteneur jetable de l'image en service (`d3a4198`) : 5 508 cotations écrites (dernière séance
passée du 18/08 au 27/10, 280 518 lignes), 255 taux écrits, `ANALYZE` passé ; articles réingérés par le workflow
« Ingestion » (passage `40534178721`, 2 166 articles). Il ne laisse de trace que dans les manifestes du serveur ; la
procédure suivie est écrite dans `docs/exploitation.md` (« Rattraper les cours et les taux en production, à la main »),
avec ses tests (`tests/test_exploitation_doc.py`).

**Manque, connu depuis le 24/08 et resté ouvert** : aucune collecte planifiée des cours ni des taux sur le serveur ;
l'ingestion de production ne collecte que les articles. Le briefing de production annonçait 70 jours de retard le
27/10. Le rattrapage est à refaire à la main le 29/10 après la clôture, puis à automatiser après l'oral blanc.

---

## 2026-10-27 : livrables E1 v3 et E3 v2 préparés pour l'oral blanc ; tags `livrable-E1-v3` et `livrable-E3-v2` à poser après la fusion dans `main`

**Livrables** : le livret E1 v3 (5 pages, `docs/rapports/E1/rapport-E1.html` et `.pdf`, logo et MCD recadré à côté)
remplace la version du tag `livrable-E1-v2` ; le rapport E3 v1.9 (20 pages, `docs/rapports/E3/rapport-E3.md` et `.pdf`)
remplace la version 1.5 du tag `livrable-E3-v1`. Le rapport E3 s'ouvre sur une première page avec sommaire cliquable,
puis les deux usages ; chaque compétence part de son cas d'usage avant la technique ; les preuves de l'entraînement
(sans objet, modèle fourni) et de l'accessibilité de la documentation sont écrites. Les tags `livrable-E1-v1`,
`livrable-E1-v2` et `livrable-E3-v1` restent figés.

**Décision d'Era (27/10)** : la grille E3 passe à 34 ✅ · 5 🟠 · 0 🔴. Deux lignes repassent partielles à la relecture,
sans changement du code : C10 « tous les points de terminaison » (verrou de la passerelle MCP, #152) et C11 « outils
adaptés aux contraintes » (règle « UE seule », registre T3).

**Manques découverts** : pour tenir 20 pages, les figures d'E3 passent à 85 % de la largeur et leur plus petit texte
de 5 à 4,3 points imprimés (`tests/test_schemas_e3.py`), à confirmer par Era. Le 26/10, GitHub n'a pas lancé la
livraison de `5a82279` (paiement en échec ou plafond de dépense) : la chaîne a échoué fermée, sans alerte (rapport E3,
§ 7.4).

---

## 2026-10-26 (midi et demi) : sprint 5, livrable en version 5 (captures du tableau de bord affichées) ; tag `livrable-sprint-5-v5` à poser

**Livrable complété** : le tableau de bord de production demande la clé d'API ; pour qu'un lecteur sans clé le voie,
les quatre captures de la copie (22/10 : panne en cours, service rétabli, attaque simulée, redémarrage) sont affichées
au § 5.6, chacune avec sa légende, au lieu de simples liens ; la synthèse montre celle de l'attaque simulée. Tests
rouges puis verts (`tests/test_livrable_sprint5_doc.py`), PDF refaits. Le contenu technique ne change pas ; les tags
v1 à v4 restent figés, la remise devient `livrable-sprint-5-v5`, posé après la livraison suivante.

---

## 2026-10-26 (fin de matinée) : sprint 5, livrable en version 4 (schéma de la vigie, synthèse refaite) ; tag `livrable-sprint-5-v4` à poser

**Livrable complété** : le schéma de la vigie entre au § 1.4 du livrable complet (`docs/sprint-5/schemas/RITA-sprint5-vigie.png`,
même contenu que celui de la vidéo, mis en forme par Era) ; la synthèse est réécrite pour être comprise en quelques
minutes : l'essentiel en une minute, avant et après le sprint, six choix de conception avec leur raison, l'attaque
simulée minute par minute (#128), les critères, les mesures et ce qui n'est pas fait. Elle corrige aussi une
incohérence de l'ancienne synthèse (retour arrière donné en 5 s puis en 6 s : 6 s le 22/10, 5 s le 23/10). Tests rouges puis
verts (`tests/test_livrable_sprint5_doc.py`), PDF refaits. Le contenu technique ne change pas ; les tags v1 à v3
restent figés, la remise devient `livrable-sprint-5-v4`, posé après la livraison suivante.

---

## 2026-10-26 : sprint 5, livrable en version 3 (chronologie et discussion avec le formateur) ; tag `livrable-sprint-5-v3` à poser

**Livrable complété** : le § 1.2 donne la chronologie du sprint en un tableau, d'abord la copie locale (22 et 23/10),
puis la production (23/10 au soir, N16 et N17 ; 25/10, version 2), chaque ligne avec sa preuve ; le § 6 consigne la
discussion où Era a présenté ce déroulé au formateur. Tests rouges puis verts (`tests/test_livrable_sprint5_doc.py`),
PDF refait. Le contenu technique ne change pas ; les tags v1 et v2 restent figés, la remise devient
`livrable-sprint-5-v3`, posé après la livraison suivante.

---

## 2026-10-25 (soir) : sprint 5, livrable en version 2 (page 11 du PDF corrigée) ; tag `livrable-sprint-5-v2` à poser

**Manque découvert** : à la page 11 du PDF remis sous `livrable-sprint-5-v1`, une phrase du § 5.12 s'affichait comme
un titre de 21 points. La ligne 305 de `livrable-sprint-5.md` commençait par `#130)`, lu par Markdown comme un titre.
Seule occurrence dans les documents du sprint 5. **Livrable corrigé** : la ligne est recomposée, un test empêche le
retour du piège (`tests/test_livrable_sprint5_doc.py`, rouge puis vert), le PDF est refait (0 texte surdimensionné
hors couverture, contre 3 en version 1). Le tag v1 reste figé ; la remise corrigée sera `livrable-sprint-5-v2`, posé
par Era après la livraison suivante.

---

## 2026-10-24 (18 h 30) : E1 v2.6 et E3 v1.5 prêts au gel, tags `livrable-E1-v2` et `livrable-E3-v1` à poser

**Livrable gelé, pas encore envoyé** : E1 v2.6 (5 pages, PR #141) et E3 v1.5 (19 pages, PR #146), avec les documents
de référence qu'E3 cite (PR #144) et le vérificateur de liens qui ne bloque plus les tags (PR #143), tous fusionnés par
Era dans `develop`. Les tags `livrable-E1-v2` et `livrable-E3-v1` seront posés par Era sur le commit de `main` qui
fusionnera `develop` (livraison N19), après la Definition of Done verte ; on enverra le lien du tag, jamais celui du
dépôt.

**Manque découvert** : `.coveragerc` ne mesure ni `rag/`, ni `monitorage/`, ni `passerelle_mcp/` ; les 96,32 % de la
CI ne les comptent pas. Mesurés à part le 24/10, sans toucher au fichier : 98 %. E3 le dit ; la décision d'élargir le
périmètre revient à Era.

**Manque découvert** : `evidence/sprint-4/README.md` annonce « les neuf réponses » pour la mesure du 21/10, alors que
le JSON du même jour compte huit réponses et sept abstentions. E3 cite le JSON ; un erratum daté reste à décider par
Era.

**Décision structurante** : les images des schémas d'E3 sont la mise en forme d'Era, et leurs textes restent ceux du
générateur. Une première mise en forme, faite à partir d'un rendu intermédiaire, disait « 6 h à 9 h » pour le créneau
du matin (8 h à 9 h dans le code) : depuis, `tests/test_schemas_e3.py` compare chaque texte de la mise en forme à ceux
du générateur.

---

## 2026-10-24 (16 h) : trois manques découverts avant E3 v1.5, corrigés le même jour

**Manque découvert** : le contrat OpenAPI publié se trompait de clé. Les deux clés de l'API portaient le nom de schéma
par défaut (`APIKeyHeader`) ; le contrat n'en gardait qu'une, et `/docs` annonçait `X-API-Key` sur `/exercice/*`, alors
que le code y lit `X-Cle-Exercice`. Sa description disait aussi que tout sauf `/health` exige `X-API-Key`. Corrigé par
la PR #144 (`scheme_name="CleExercice"`, description réécrite), tests écrits d'abord et vus rouges.

**Manque découvert** : documenté mais absent. Le retour arrière de la production (répété le 14/10 et le 15/10) et la
mise à jour du script du serveur étaient annoncés dans `docs/EXPLOITATION.md` par `retour-arriere.yml`, l'action
`ordre-serveur`, `docs/CHAINE-V1.md` et `docs/CADRAGE-V1.md` (critère 2 du sprint 2). Aucune version de la page ne les
a jamais contenus (relu sur celles du 14/10 et du 16/10), et le fichier s'appelle `exploitation.md`. Écrits dans
`docs/exploitation.md` (annexes, § 8) à partir des deux répétitions, PR #144 ; le secours sans GitHub y est dit jamais
exécuté. `deploy/deployer.py` garde l'ancien nom dans deux messages : le modifier bloquerait les livraisons jusqu'à sa
réinstallation sur le serveur.

**Manque découvert** : le vérificateur de liens criait au loup. Il ne savait vérifier par `gh` qu'une forme d'URL du
dépôt privé (`/tree/<tag>`) ; 116 liens corrects étaient déclarés cassés, ce qui bloquait les tags E1 et E3 sous la
règle « zéro lien cassé ». Corrigé par la PR #143 : 0 lien cassé sur tout le dépôt le 24/10 (249 internes, 275
externes).

---

## 2026-10-24 (midi) : livraison N18, quatre correctifs ; la sauvegarde n'est pas tenue

**Manque découvert** (23/10, relecture d'E1 et E3 contre le code de `main`) : quatre défauts du code, aucun visible
dans les données de production. (C) Une panne totale des cotations, des flux RSS ou du scraping comptait parmi les
étapes réussies du soir : l'exception ajoutait des rejets sans remplir `erreur`. (E) `/donnees/cotations` n'acceptait
qu'une date de début et 1 000 lignes, soit environ quatre ans par valeur, alors qu'E1 annonce dix ans et que C5 exige
l'ensemble des données prévues par les spécifications. (D) Le lecteur de positions acceptait NaN et l'infini. (F)
L'en-tête de la migration « taux » se disait rejouable sans condition ; rejouée après la migration de la clôture, elle
ferait revenir les positions closes dans la valorisation.

**Livrable envoyé** : les quatre correctifs, tests d'abord (21 tests, dont 15 rouges avant le code) ; PR #138 vers
`develop` et PR #139 (`develop` vers `main`), fusionnées par Era ; livraison N18 (passage 40083432816, 11 h 48 à
11 h 57), commit `b547cbf7d46bc45d2ffbb85a0740449a8b96fe2a`, annoncé par `/health` en production. CI : 1700 passed,
30 skipped, 2 xfailed, couverture 96,32 %.

**Manque découvert** : la sauvegarde. Le dernier dump date du 27/09, le dump hebdomadaire prévu n'est pas tenu, et la
ligne « Sauvegarde restaurable : VALIDÉ » de `CONTINUITE.md` repose sur `pg_restore --list`, qui liste l'archive sans
la restaurer. Reste à faire : un dump et une vraie restauration dans une base jetable.

---

## 2026-10-23 (20 h) : sprint 5 remis, livraison N17 et tag `livrable-sprint-5-v1`

**Livrable envoyé** : PR #135 (documents « en production » vers `develop`) et PR #136 (`develop` vers `main`),
fusionnées par Era ; livraison N17 (passage 39995996403, 19:33 à 19:43), commit
`d215617f7cffa7a9817da28f2b2684dc7c63f7cd`, documents seulement. Tag `livrable-sprint-5-v1` posé par Era sur ce SHA
complet ; passage du tag 39997640785 réussi (Definition of Done verte, image publiée). **Manque découvert** : de 18:49 à
19:10, GitHub Actions a refusé tous les travaux (« spending limit ») ; dépôt privé, quota gratuit d'octobre épuisé,
budget Actions à 0 $. Era l'a porté à 5 $ (0,006 $ la minute en Linux 2 cœurs). Les anciens passages refusés du
`push` sur `develop` ont dû être relancés : leurs échecs bloquaient la fusion malgré les contrôles verts de la PR.

---

## 2026-10-23 (soir) : sprint 5 en production, livraison N16

**Décision révisée par Era** : le sprint 5 passe en production. PR #133 (`sprint-5-vigie-demo` vers `develop`) et
PR #134 (`develop` vers `main`), contrôles verts, fusionnées par Era ; livraison automatique N16 (passage
39983152061, 18:00 à 18:12), commit `845e3b3`. En production : `/health` annonce `845e3b3`, `/tableau-de-bord.html`
répond 200, `/sante` exige la clé (403 sans elle). **Manques découverts par la chaîne Linux, corrigés** : un faux
positif de gitleaks (étiquette d'image Docker, exception ciblée commit et fichier) ; deux tests écrits en heure de
Paris alors que la chaîne est en UTC. Livrable, synthèse, scénario (N16) et preuves mis à jour ; tag
`livrable-sprint-5-v1` à poser sur la livraison suivante, désignée par son SHA complet.

## 2026-10-23 (matin) : sprint 5, la doc suivie à la lettre, deux répétitions, une fausse alerte de production corrigée

**Fait** : `docs/exploitation.md` suivie à la lettre par son auteur sur la copie (déployer, panne simulée inconnue
trouvée en 11 minutes, retour arrière, redéploiement) : dix trous trouvés et corrigés, chacun couvert par un test
(commits `18f34de` et suivant). Deux répétitions de la démo, environ 9 minutes et 9 minutes 30 ; deux corrections du
scénario (`57ebf56`, `648293f`). **Manque découvert** : la copie envoyait ses traces au projet Langfuse de la
production ; sa panne simulée a déclenché l'alerte de production (issue #130, fausse alerte, fermée avec son
explication après vérification par l'API de Langfuse). La copie a désormais son propre projet Langfuse, sans alerte.
**Décision rappelée** (22/10) : le sprint 5 reste un prototype local jusqu'à la remise. Livrable v1 mis à jour ; tag
`livrable-sprint-5-v1` toujours à poser, après l'atelier n°5.

## 2026-10-22 (nuit) : sprint 5, la vigie et la démo, prototype local ; livrable en version 1 (tag `livrable-sprint-5-v1` à poser)

**Décision** : le sprint 5 ne touche pas l'original (ni `main`, ni la production, ni le serveur, ni sa base). Il vit sur
la branche `sprint-5-vigie-demo` et se démontre sur une copie de RITA lancée sur le poste avec Docker
(`http://localhost:8011`). **Livré sur la branche** : compteurs en six catégories, signaux et `GET /sante`, sept seuils
provisoires argumentés et liés à une action, coût en euros au prix public daté, tableau de bord de sept cartes, vigie
hors de l'API (issues GitHub), panne et dérive simulées, déploiement et retour arrière de la copie,
`docs/exploitation.md`, scénario de la démo, livrable et synthèse (`docs/sprint-5/livrable/`). **Prouvé sur la copie le
22/10** : déploiement, retour arrière en 6 s, panne diagnostiquée avec la doc (issue #127), dérive détectée (issue
#128), les deux issues fermées par la vigie ; coût 0,009486 €. Suite : 1674 passés ; neuf modules du sprint couverts à
100 %. **Pas encore fait** : le test de la doc par un tiers, les deux répétitions de la démo, la grille de l'atelier 4 ;
la production n'a pas de vigie. Le tag `livrable-sprint-5-v1` se pose sur la branche après ces vérifications, sur le
commit désigné par son SHA complet ; rien n'est fusionné dans `main`.

## 2026-10-21 (nuit, fin) : livrable du sprint 4, version 3 (tag `livrable-sprint-4-v3`)

**Relecture finale de la version 2** (tag `livrable-sprint-4-v2`) : le lien « `guardrails/nombres.py`, ligne 67 »
ouvrait une ligne vide, la fonction `nombres_absents` étant à la ligne 68 ; la version servie était encore donnée pour
N12 (`27e41d3`), alors que N13 et N14 l'avaient remplacée ; les livraisons s'arrêtaient à N12. **Version 3** : le lien
corrigé ; l'état de la production à N14 (`81a9718`), avec le comportement de N12 ; N13 et N14 ajoutées au § 7.9, au
glossaire et à la synthèse ; `/health` après N14 en annexe. Les liens visent `livrable-sprint-4-v3`, posé par Era sur
le commit de la livraison suivante, désigné par son SHA complet. Le tag v2 reste, figé, sur N14.

## 2026-10-21 (nuit) : livraison N14 ; tag `livrable-sprint-4-v2` posé, remise du sprint 4

**Livré** : N14 à 21 h 24 (commit `81a9718`, PR #124 ; passage `39659810301`, réussi du premier coup), sans changement
de code. **Remise** : le tag `livrable-sprint-4-v2`, posé par Era à 21 h 25 sur
`81a9718c528cea18ad533aae5fd3c2ffd1ea5e49` (SHA complet), après `/health` vérifié. Sa livraison (passage
`39661606759`) a passé la porte de livraison (tests, portes d'évaluation, liens, tag cité : « VERDICT : ✅ livrable »)
et publié l'image `ghcr.io/ganda15/rita-api:livrable-sprint-4-v2`. Les 49 liens du livrable et de la synthèse
répondent au tag.

## 2026-10-21 (soir, fin) : livraison N13 ; le tag v1 posé sur N12 par erreur ; la remise passe au tag `livrable-sprint-4-v2`

**Livré** : N13 à 20 h 49 (commit `ce5b2c7`, PR #122 ; passage `39654392710`, réussi du premier coup) : le livrable
validé, la synthèse, le schéma complet et le journal des retours complété, sans changement de code. **Erreur de
méthode** : le tag `livrable-sprint-4-v1` a été posé à 20 h 30, avant la fusion de la PR #122 (20 h 37), sur
`origin/main` qui était encore N12 (`27e41d3`). La porte de livraison du tag l'a refusé (passage `39653430203` :
« Tag livrable-sprint-4-v1 cité dans ETAT.md et CHANGELOG.md : absent de : CHANGELOG.md ») : aucune image publiée.
La règle du dépôt « tags livrable-* figés » a refusé sa suppression (GH013) : il reste sur N12, et ne sera pas
envoyé. **Décision** : la remise est le tag `livrable-sprint-4-v2`, même contenu que la version 1 validée, posé par
Era sur le commit de la livraison suivante, désigné par son SHA complet comme le prévoit le plan de travail. Les liens
du livrable et de la synthèse visent `livrable-sprint-4-v2`.

## 2026-10-21 (soir) : livrable du sprint 4, version 1, tag `livrable-sprint-4-v1`

**Livrable** : version 1 du livrable du sprint 4 (`docs/sprint-4/livrable/livrable-sprint-4.md` et `.pdf`, 16 pages,
table des matières vérifiée) et sa synthèse de quatre pages (`synthese-sprint-4.md` et `.pdf`), relus et validés par
Era le 21/10. Les chemins cliquables visent le tag `livrable-sprint-4-v1`, posé par Era sur `main` après la livraison
N13, qui porte ces documents. **Ajouts depuis N12** : le schéma complet de la composante et de ses garde-fous
(`docs/sprint-4/schemas/`, chaque boîte avec son fichier, sa ligne et ses tests) ; le journal des retours de l'atelier
n°3 complété : quatre retours oraux manquaient aux notes de séance (l'ordre des modalités du brief, montrer le
construit, rien sur le non-attendu, le code seulement sur question), neuf au total.

**Correction** : la documentation de `guardrails/nombres.py`, les preuves et le livrable disaient qu'un nombre écrit en
lettres (« mille ») était refusé ; il est ignoré. Corrigé, avec deux tests qui fixent les limites du contrôle (nombres
en lettres, unité non vérifiée).

## 2026-10-21 : livraison N12, le traçage Langfuse actif en production

**Décision d'Era** : poser les clés Langfuse sur le serveur (projet de production, région UE) ; il les a saisies
lui-même, après une sauvegarde du `.env`. **Livré** : N12 à 12 h 47 (commit `27e41d3`, PR #120) : le livrable du sprint 4
en version 1, les quatre apostrophes du contrôle des nombres, et le traçage, par le `.env` copié à la livraison.
**Prouvé** : la trace du briefing OR.PA du rejeu de 12 h 51 (`7da0ec8c…`) ne garde ni prompt ni réponse, sur la
racine comme sur la génération du modèle (D9, CA3.6). Le manque de l'entrée suivante est levé.

## 2026-10-21 : manque connu, confirmé : le traçage Langfuse est coupé en production

**Manque connu, confirmé** (et non découvert : il est écrit depuis le 04/10 dans `evidence/C11/`, puis au sprint 2,
`docs/sprint-2/README.md`) : en cherchant une trace de briefing de production (CA3.6), Era n'en a trouvé aucune. Vérifié sur
le serveur, en lecture seule et sans afficher de valeur : aucune clé Langfuse dans le `.env` du serveur, ni dans le
conteneur de l'API ; `src/traces.py` n'envoie donc rien. D9 est tenu de la façon la plus stricte (aucun texte
conservé), mais les durées par étape, les jetons et le coût ne se lisent qu'en local. Les documents qui situent ces
signaux dans Langfuse sans préciser « en local » sont à relire. Poser les clés : décision d'Era, sprint 5.

## 2026-10-20 et 21 : sprint 4 en production (N10, N11), contrôle des nombres, image de base tirée d'un miroir

**Livré** : N10 le 20/10 à 21 h 48 (commit `27da943`) : garde-fou de détournement avant la recherche, passages piégés
écartés avant le prompt, contrôle de fuite après le modèle, traces du briefing réduites aux métadonnées (D9), 422 sur
`/briefing`, refus de clé journalisé, limite de débit partagée. N11 le 21/10 à 11 h 05 (commit `4fc63f5`) : contrôle
des nombres et image de base tirée du miroir. Rejeu en production après N11 : 5 appels conformes sur 5, deux fois.

**Décisions** : avenant n°1, le parcours des questions entre dans la composante agentique (`docs/sprint-4/AVENANT-1.md`) ;
chaque nombre d'une réponse doit figurer, entier, dans le texte d'un article cité, sinon refus `NOMBRE_NON_SOURCE` ; la
date de publication et le nom de la source ne servent pas de source au contrôle (option B, décision d'Era) ; l'image
de base est tirée de `mirror.gcr.io`, même empreinte que la galerie d'Amazon.

**Manques découverts** : Q4 servie en production avec « 1 0 postes » pour un passage qui dit « 1 000 postes »
(20/10, 21 h 53), cause non établie, d'où le contrôle des nombres ; la galerie d'Amazon a refusé 19 constructions du
16 au 21/10 ; OR.PA sans cotation depuis 64 jours en production, et le briefing la dit « probablement radiée » (non
corrigé, critère 1 du contrat « en cours ») ; le garde-fou de détournement ne reconnaît aucune des 8 reformulations
réservées.

## 2026-10-19 : atelier croisé n°3 ; livrable du sprint 3, version 2

**Livré** : démonstration en direct sur la production, avec le formateur ; ingestion lancée par le bouton pendant
l'atelier (passage `39265862974`, 4 min 16 s, réussie ; 2110 puis 2140 articles, index `fc87b92a…`). Livrable
version 2, 16 pages, au format maison : le brief et le projet d'abord, couche par couche ; une section qui dit ce que
montre chaque lien GitHub ; tous les chemins cliquables vers le tag `livrable-sprint-3-v2` ; la capture de `/health`
du 19/10 ; N8, le tag v1 et les onze 429 ; le journal des retours de l'atelier n°3.

**Correction** : ligne E4 du livrable. Les références sont construites à partir des passages retrouvés dans l'index
(`agents/question.py`, ligne 196), pas lues dans la table au moment de répondre ; la fiche de la source relit la base.

**Retours de l'atelier n°3** : grille non remplie ; retours oraux du formateur sur la présentation (trop dense et non
linéaire ; aller droit au but, couche par couche ; partie technique en cinq minutes ; schémas déjà vus montrés vite ;
point positif : un travail réel, une évolution visible). Suite : appliqués au livrable, reportés au sprint 4 pour
l'oral (`eval/ateliers/sprint-3-grille.md`).

**Manque découvert** : les preuves du serveur (journal, manifeste, rejeu) des ingestions du 18 et du 19/10 ne sont
pas copiées dans le dépôt ; les passages GitHub et `/health` en tiennent lieu.

---

## 2026-10-17 (après-midi) : captures de production ; livrable du sprint 3, version 1, validé

**Livré** : trois captures de l'écran de question en production, prises par Era avec sa clé (16 h 25 : la réponse
citée sur Netflix et la fiche de l'article 2788 ; 16 h 31 : le refus `OUT_OF_CORPUS` de la question sur la tarte
Tatin). Les captures entières sont gardées, et les découpes du livrable sont faites dedans sans retouche
(`evidence/sprint-3/captures/`). Le livrable passe à 10 pages.

**Décision d'Era** : livrable v1 validé le 17/10, après deux relectures. Corrections apportées : plus de garantie
absolue sur les conseils d'achat (des contrôles détectent et bloquent) ; « 8 sur 8 » limité aux contrôles de statut
et de références ; « 3 faits sur 9 » expliqué (2 faits de Q3, abstention acceptée ; 1 fait de Q4 manqué à cause du
caractère de contrôle) ; Q1 qualifiée de réponse partielle ; N7 daté du 17/10 à 00 h 01, heure de Paris ; version de
chaque mesure (N5, N6, N7) ; prérequis de l'atelier après 9 h et ingestion reportée relancée à la main.

**Manque découvert** : les vérifications juridiques des sources restent ouvertes (base légale du corpus retenue à titre
provisoire, conditions de réutilisation des éditeurs non relues) ; elles sont maintenant écrites dans le livrable, § 9.

---

## 2026-10-17 (nuit) : N7 en production ; livrable du sprint 3, version 1 ; tag avant l'atelier

**Livré** : N7 (PR #105, `66963da`), le 16/10 à 22:10 UTC, vert du premier coup ; `/health` annonce `66963da` et l'index
`13f15d84…`, même empreinte de contenu (`0b372539c971…`, 2081 articles). La PR #104 avait d'abord corrigé la fiche T8
du registre après la revue Codex : l'outil d'évaluation conserve les questions et les réponses dans ses rapports.

**Décision d'Era** : le tag `livrable-sprint-3-v1` est posé avant l'atelier 3 (lundi 19/10 au matin), comme au
sprint 2, et présenté comme la version préparée pour l'atelier ; la grille et les suites données aux retours iront
dans une version 2. Cela remplace l'ordre écrit le 16/10 (tag seulement après l'atelier).

**Livrable** : `docs/sprint-3/livrable/livrable-sprint-3.pdf` (8 pages), lisible sans accès au dépôt privé : preuves
reprises en extraits datés, journaux recopiés en annexe, déroulé de la démonstration (ingestion lancée après les
questions de l'évaluateur, car sa bascule remplace le conteneur de l'API).

**Manque découvert** : un cinquième 429 de `public.ecr.aws`, sur la construction après la fusion de la PR #104 dans
`develop`, réussie à la troisième tentative.

---

## 2026-10-16 (nuit) : sprint 3 en production (N5, N6), ingestion par le bouton, évaluation en production, registre RGPD

**Livré** : N5 (PR #101, `41b1763`) puis N6 (PR #103, `72dba4d`), en production le 16/10 ; `/health` annonce `72dba4d`
et l'index `c91baa3f…` (2081 articles). Tag prévu : `livrable-sprint-3-v1`, posé par Era sur le commit final, après la livraison N7,
l'atelier 3 et l'intégration de sa grille, et la Definition of Done.

**Manques découverts, et suites** :
- Première ingestion arrêtée à la collecte : `lxml` absent de l'image, présent sur le poste, si bien que la suite
  passait. Corrigé en N6 (`html.parser`), avec un essai du nettoyage dans l'image, en CI, avant publication.
- L'empreinte de l'index dépendait du fuseau de la session PostgreSQL (`+02:00` sur le poste, `+00:00` sur le
  serveur) : dates écrites en UTC (N6) ; même corpus, même empreinte des deux côtés (`50579b43a651…`).
- Revue automatique de la PR #100 : la fiche nommait le flux au lieu de l'éditeur, et un jeu aux repères incomplets
  était accepté ; corrigés en N6. Revue de la PR #102 : un récit rangé dans `evidence/`, alors que la règle veut des
  preuves constituées au fil de l'eau ; déplacé dans `docs/sprint-3/`, fichiers bruts du serveur copiés dans
  `evidence/sprint-3/`.
- Évaluation en production : un caractère de contrôle U+0000 dans une réponse du modèle. Correction implémentée et
  testée sur la branche (`f089be2`, test d'abord), livraison prévue avec N7.
- L'outil d'évaluation charge la clé locale du `.env` quand `RITA_API_KEY` manque : relevé, non corrigé.
- Construction de l'image : quatre 429 de `public.ecr.aws` dans la journée, relancés à la main ; cause non traitée.

**Résultats mesurés** : ingestions à 21:08 (29 articles écrits) et à 21:21 (aucun, dédoublonnage), rejeux sans écart ;
évaluation, sur ce passage en production : 8 sur 8 conformes aux contrôles du jeu ; 3 faits sur 9 retrouvés
automatiquement ; aucune affirmation non soutenue selon la relecture d'Era.

**Décisions** : T7 (Google News) arrêté, date vérifiée sur le serveur (première collecte sans lui à 21:08) et sur le
poste (22:01, dossier d'origine passé sur `main`, tâche réactivée par Era) ; corpus d'articles examiné et inscrit comme
traitement accessoire ; T8, questions de l'écran, inscrit (`db/RGPD-registre-des-traitements.md`).

---

## 2026-10-16 : sprint 3, spec et plan validés, code complet sur la branche, évaluation locale

**Décisions structurantes** (spec `docs/sprint-3/SPEC.md`, validée par Era) : D1, une ingestion prépare un nouvel
index à part, le vérifie (pré-test, rejeu des questions) puis le met en service, l'index précédent et le retour arrière
restent possibles ; D2, RITA ne conserve aucun texte de question ni de réponse sous son contrôle ; D3, arrêt des
requêtes Google News (le nom des sociétés du portefeuille ne sort plus) ; D5, les questions n'appellent qu'Azure en
zone UE. Seuil de pertinence 0,42 gardé comme provisoire.

**Manque découvert, et décision** : mesurée sur la copie du corpus de production, la question Q2 du jeu échouait à la
règle de pertinence (« reprend » ne rejoint pas « reprise »). Era l'a fait reformuler une seule fois ; la version 1 et
son échec sont gardés (`evidence/sprint-3/questions-demo-mesure-2026-10-16.md`). Jeu de questions en version 2.

**Décision** : la base de test locale `rita_sprint3` suit `db/roles.sql`, comme la production (un test de rôle
échouait sur une base plus stricte que la conception).

**Résultat mesuré** : évaluation sur l'API locale, 8 questions sur 8 conformes, aucune affirmation non soutenue à la
relecture d'Era (`evidence/sprint-3/evaluation-2026-10-16-relecture.md`). Pas encore livré en production.

**Collecte du poste** : tâche planifiée désactivée par Era le 16/10 (elle exécutait encore Google News), jusqu'à ce que
le dossier d'origine ait le code du sprint 3.

---

## 2026-10-15 (nuit, fin) : sprint 2 clos, tag `livrable-sprint-2-v3` ; sprint 3 ouvert dans un worktree

**Livrable** : version 3 du livrable du sprint 2, tag `livrable-sprint-2-v3` sur `2268b05` (fusion de la PR #99),
livrée en production par N4 (`/health` = `2268b05`). Les 17 liens du livrable sont vérifiés au tag. Le message au
formateur avait été envoyé par Era avant la pose du tag.

**Deux empreintes pour le même commit** : image déployée par N4
`sha256:086fed50dd3402a4bd5f5a8a03fed326e6223c4f00ef1adf21c253da7b6b7f7e` ; image publiée par le run du tag
`sha256:f2e95c71470ab4c0dfa04ed3dfb7ef23080d7c387725afa0210f45d17d872c92`. **Manque découvert** : le run d'un tag
reconstruit l'image au lieu de réétiqueter celle de `main`, et déplace ainsi `sha-2268b05` et `latest`. La production
n'est pas touchée : elle est lancée par son empreinte. Le `429` du registre `public.ecr.aws` a frappé une quatrième
fois (PR #99) ; relancé sans effet sur le registre, puisqu'un run de PR construit sans publier.

**Décision structurante (D4)** : le sprint 3 se développe dans un worktree séparé,
`D:\KandaWork\RITA_PROJECT\rita-agent-sprint-3`, branche `sprint-3-donnees-ancrage`, avec un `.env` et une base de test
dédiés ; le dossier d'origine n'est pas modifié pendant le sprint.

---

## 2026-10-15 (nuit) : grille de l'atelier n°2 versée ; passage du tag v2 en échec, non relancé

**Grille** : celle remplie par l'évaluateur (Alpha DIALLO) est versée, transcrite mot pour mot
(`eval/ateliers/sprint-2-grille.md`) avec l'original (`eval/ateliers/sprint-2-grille-originale.pdf`) : 5 critères ✓,
conseil « RAS ». **Manque découvert** : le passage `Livraison` déclenché par le tag `livrable-sprint-2-v2`
(`38776441164`) a échoué à la construction (`429 Too Many Requests` du registre d'images) ; rien n'a été déployé. Il
n'est pas relancé : une relance reconstruirait l'image et déplacerait l'étiquette `sha-1cbace0`. La v3 remplacera la
v2 après validation.

---

## 2026-10-15 (soir, fin) : livrable du sprint 2, version 3, tag `livrable-sprint-2-v3`

**Manque relevé par Era** : deux liens du PDF v2 existaient mais ouvraient la mauvaise page. « Dépôt au tag de remise »
menait à la racine du dépôt (README général), et « Production » à l'écran « Mon portefeuille » qui demande la clé.
**Correction** : entrée du sprint 2 au tag (`tree/<tag>/docs/sprint-2`), production par `/health` et
`/briefing.html` ; renvoi vers le sprint 2 en tête du README général. Leçon : vérifier ce qu'un lien affiche, pas
seulement qu'il existe.

---

## 2026-10-15 (soir) : livrable du sprint 2, version 2, tag `livrable-sprint-2-v2`

**Manque découvert après la v1** : les 14 liens GitHub du PDF répondent 404 à un lecteur sans accès au dépôt privé
(vérifié sans connexion ; les 4 liens publics répondent 200). **Correction** : le PDF v2 se lit sans ouvrir aucun lien :
note « Accès aux liens » en § 2, annexe § 11 qui recopie les journaux de chaîne, la règle de protection de `main` et le
journal du serveur ; production N2 (`2048aec`, fusion de la PR #95, 8 min 53 s jusqu'à la production) et son journal.
Les captures des pages GitHub restent impossibles sans compte connecté ; les journaux extraits avec `gh` les remplacent.

---

## 2026-10-15 : livrable du sprint 2 (le socle et la chaîne), tag `livrable-sprint-2-v1`

**Livrable** : `docs/sprint-2/livrable/livrable-sprint-2.pdf` (9 pages) et les preuves versionnées
`evidence/sprint-2/` (journaux de chaîne, captures). Production livrée par la chaîne : N0 (14/10, après deux refus
avant bascule), N1 (fusion de la PR #92, 9 min 24 s jusqu'à la production). Retour arrière répété deux fois (28 s et
35 s). Commit cassé (PR #93) bloqué pendant l'atelier : 2 tests en échec, fusion refusée, livraison jamais lancée.

**Manques découverts** : la procédure de retour sans GitHub, annoncée par `docs/CHAINE-V1.md` § 5.2, est absente de
`docs/EXPLOITATION.md` ; le journal du serveur ne garde pas le code HTTP d'un contrôle en échec ; une bascule coupe la
production 5 à 10 s (502).

---

## 2026-10-11 (nuit, fin bis) : E1 v2.5, cinq surgénéralisations corrigées

**Manques découverts et corrigés dans E1** (relecture de l'oral E1, chaque point vérifié dans le code ou les preuves) :
« zéro ligne vaut échec » présenté comme général, alors qu'il ne vaut que pour la BCE et FRED ; STLAP.PA dite « exclue
des requêtes », alors qu'elle reste visible dans la valorisation ; un rétro-ajustement décrit à l'envers (c'est le
fournisseur qui multiplie les prix passés ; « divisé par 36 millions » est l'évolution observée) ; une cause commune
attribuée à l'erreur UTC, alors que c'est la place de cotation absente du modèle ; une méthode big data dite
« identique à une autre échelle » sans mesure. Toujours 5 pages. Registre § 0 : le consentement n'est qu'une des
bases possibles si RITA devient multi-utilisateur.

---

## 2026-10-11 (nuit, fin) : guide d'exploitation corrigé, deux manques d'installation

**Manques découverts** (relecture du guide, chaque point vérifié dans le code) : la voie Docker aboutit à une base
vide, faute de procédure d'initialisation (le PostgreSQL du conteneur ne publie aucun port, la collecte tourne sur le
poste) ; la création de la base échouait sur PostgreSQL 15 ou plus (`GRANT ALL PRIVILEGES ON DATABASE` ne donne
plus le droit de créer des tables dans `public`) ; `git clone` sans `cd rita-agent`. Corrigés dans le guide le 11/10
(documentation seule, non rejouée sur une installation neuve, et le guide le dit), avec la clé contrôlée à
l'authentification, `OUT_OF_CORPUS`, `curl.exe`, Azure seul depuis le 11/10, chiffres des tests datés. **Reste après
le gel** : construire l'initialisation de la base Docker, rejouer les deux voies sur un environnement neuf.

---

## 2026-10-11 (nuit, suite) : relevé de veille S41, et un manque de la CI

**Relevé S41** fait le 11/10 (fenêtre du 29/09 au 11/10, créneau du 05/10 non tenu, dit tel quel), puis corrigé le
soir même en six points après relecture ; la note S41 reste à écrire par Era.

**Manque découvert** : aucune garde contre une baisse du taux de blocage du garde-fou d'injection. Le test à 85 % est
un échec attendu strict ; une baisse de 70 % à 40 % laisserait la CI verte. Correction après le gel, plan d'abord
(zone sous garde) : exiger que les détections connues restent détectées, sans toucher au seuil.

---

## 2026-10-11 (nuit) : E3 v1.4, passe documentaire, revue d'E3 close

**Manques découverts et corrigés dans E3** (relecture, chaque point vérifié dans le code ou le référentiel) : E3
disait que l'API **refuse de démarrer** sans clé, alors qu'elle la contrôle à l'authentification (le test lui-même
s'appelle « refuse de servir ») ; que toutes les routes sauf `/health` exigent la clé, alors que la documentation et
les pages de l'interface sont publiques ; que le texte du briefing n'est qu'à un endroit des traces, alors qu'il est
dans deux ; qu'aucun schéma Pydantic n'existe, alors qu'il y en a un ; que deux fournisseurs répondent sur le poste,
alors qu'Azure est seul depuis le 11/10 ; que la section 10 comptait « 39 critères », alors que le référentiel en
compte **44** pour C9 à C13, regroupés en 39 lignes, aucun absent. Toujours 20 pages, statuts inchangés. **Reste,
par choix de calendrier** : les figures d'E3 sont petites imprimées (environ 4 points) ; refonte après le gel, en
nouvelle version.

---

## 2026-10-11 (soir) : E1 v2.4 et guide d'exploitation, dernière passe d'E1 avant le gel

**Manque découvert et corrigé** : le guide d'exploitation (§ 4.5) avait le même défaut qu'E1, en pire : il lançait
l'import sans jamais construire le jeu Parquet, absent de Git ; quiconque suivait le guide sur un poste neuf
s'arrêtait sur « Jeu Parquet absent ». Corrigé, PDF régénéré. E1 retire aussi une affirmation non prouvée (« rejouée
sur une base Compose neuve le 03/10 » : seules les migrations l'ont été). E1 v2.4 : MCD lisible, conservation de T4,
positions simulées, numéros de page ; toujours 5 pages. **Décision** : E1 ne se rouvre plus que pour une erreur de fait.

---

## 2026-10-11 (après-midi) : E1 v2.3, passe RGPD et exactitude, revue d'E1 close

**Manques découverts et corrigés dans E1** (relecture d'E1, chaque point vérifié dans le code et le registre) :
E1 disait qu'une seule table porte des données personnelles, alors que le registre classe `mcp_calls` (T5) comme
personnel ; il disait le fichier source jamais versionné, alors que le jeu de démonstration l'est ; il donnait
l'intérêt légitime comme base acquise, sans la réserve de l'exemption domestique (RGPD art. 2.2.c) ni la mise en
balance qu'exige l'art. 6.1.f ; **la séquence d'installation échouait sur un dépôt vierge** (l'import lit le Parquet,
construit après) ; deux phrases sur les connexions et une sur les tables étaient inexactes. E1 passe en v2.3, toujours
5 pages ; registre aligné (§ 0, T1, glossaire). Reste après le gel : le commentaire de `db/schema.sql`, la mise en
balance écrite, l'examen de l'exemption domestique.

---

## 2026-10-11 : Azure seul jusqu'au contrat de Mistral, calendrier final, défaut Docker corrigé

**Décisions structurantes (Era)** : (1) appels réels par Azure GPT-5.4 seul (`LLM_ORDRE=foundry`) tant que le
contrat de Mistral n'est pas lu ; Mistral Large 4 seulement pour le banc C7, sur des données publiques ou simulées ;
valeurs par défaut de la branche `mistral-ue` à passer à `foundry` avant la fusion de la PR #88 ; (2) calendrier
final : contenus terminés le 20/10, gel final le 23/10, simulation le 26/10, examen blanc le 29/10, aucune
fonctionnalité nouvelle avant le 20/10. Détail et pourquoi : `CONTINUITE.md`, § D.

**Manque découvert et corrigé** : en conteneur, la cascade sautait Azure (aucune variable `AZURE_FOUNDRY_*`
transmise par `docker-compose.yml`, ordre par défaut `anthropic,openrouter` au lieu de celui du code). Corrigé avant
le gel, deux tests de contrat d'abord ; la CI n'utilise pas Compose et la production sert toujours le code du 19/08.

---

## 2026-10-10 (nuit) : incident de clé Mistral, Mistral Large 4 choisi, règle UE seule gardée stricte

**Manque découvert (incident)** : la vraie clé Mistral d'Era a été écrite dans `.env.example` et poussée sur la
branche `mistral-ue` (`5fae28e`) ; le commit de correction (`8587a21`) en contenait une deuxième. Le hook
`bloquer-secrets` protège contre l'agent, pas contre un commit fait à la main. Corrigé : les deux clés supprimées chez
Mistral par Era, une clé neuve dans `.env` seulement, modèle remis aux valeurs de gabarit (`0a3f3f8`, vérifié sur
GitHub). Les clés restent lisibles dans l'historique de la PR #88, révoquées. Désormais : commit local, vérification
sans afficher de valeur, puis push ; un hook qui refuse un modèle d'environnement non gabarit est à proposer après
le gel.

**Décisions structurantes (Era)** : (1) **Mistral Large 4 sans réflexion** remplace Large 3 sur la branche
`mistral-ue` : sur un vrai briefing (MC.PA, même prompt qu'Azure), Large 3 invente une date de séance, Large 4 non,
pour 0,10 centime (preuve C8 sur la branche) ; (2) **Azure GPT-5.4 reste premier** (gratuit pour Era), l'ordre se
tranchera sur le banc C7 ; (3) **règle UE seule gardée stricte** : Google News par position, seule source qui révèle
les positions (vérifié dans le code ; aujourd'hui des positions simulées), se corrige par #81 après le gel, et devient
bloquante avant tout chargement d'un portefeuille réel ; (4) **jeu de démonstration** : positions
inventées sur des sociétés réellement cotées, Era ne détient pas ces titres.

**Manques découverts** : Langfuse compte 0 $ pour Mistral (prix hors de sa grille) ; Microsoft documente des
transferts limités hors de son EU Data Boundary, que le CEPD compte comme transferts (T6 pas entièrement prouvé,
registre § 5) ; le registre ne décrivait pas la requête du soir vers Yahoo (yfinance) ; sur `develop`, `README.md`,
`CLAUDE.md` et le guide d'exploitation disaient « Claude » pour le modèle et « 502 » pour une panne de fournisseur
(500 en vrai), corrigés (`000ca50`). **Le verrou MCP refuse actuellement le jeu de démonstration importé** : il attend
10 positions, alors que l'import et l'API en exposent 7 ; le refus du 3 octobre présenté dans E3 et dans la preuve
C20 ne venait pas d'un portefeuille réel. E3 passe en v1.3 (toujours 20 pages), erratum C20 daté, correction après le
gel.

---

## 2026-10-10 (soir) : audit de propagation, les jumeaux restés faux après les corrections du jour

**Décision structurante (règle d'Era)** : tout changement se propage partout où le même fait apparaît, pas seulement
dans le rapport corrigé ; on cherche l'ancienne valeur dans tout le dépôt avant de dire « fait ». `evidence/`, les
entrées passées de ce journal et les journaux ne se réécrivent pas.

**Manques découverts** en appliquant la règle aux changements des 09 et 10/10 : `docs/CI-CD.md` comptait encore quatre
dépendances épinglées ; `README.md` annonçait 742 et 700 tests, E1 v2.0 et E3 v0.1 ; le plan des 12 semaines disait
le contrat de Langfuse « à confirmer » ; le classeur disait la décision sur `memory_audit` « en attente » ;
`Dockerfile.tests` tirait encore son image de Docker Hub (aligné test d'abord). Dans le code gelé, le déploiement Azure
par défaut de `src/llm.py` vise toujours `gpt-5.4`, supprimé le 09/10 : le poste marche parce que son environnement
fixe `gpt-5.4-dzs-eu` ; inscrit sur #82 pour l'après-gel, avec deux commentaires « Global Standard ».

---

## 2026-10-10 (15 h) : les 7 soirs de collecte coupés n'étaient pas tous rattrapés ; taux BCE du 03/09 récupéré

**Manque découvert** en relisant E1 avec Era : § 3 disait les 7 collectes interrompues par l'arrêt du poste « rattrapées
par les plages de dates ». Vérifié en base (lecture seule) : vrai pour quatre soirs (13, 14, 16, 17/09, rattrapés le
18/09, sauf la séance parisienne du 17/09), rien de perdu le 08/09, mais les articles des 02 et 03/09 sont perdus et
le taux BCE du 03/09 manquait. **Récupéré le 10/10** par l'option de rattrapage (5 lignes). E1 § 3 dit maintenant
l'état mesuré, toujours 5 pages. Preuve : `evidence/C1/preuve-soirs-coupes-verifies-2026-10-10.md`.

**Manque découvert aussi** : le rôle en lecture seule `rita_lecture` existe mais n'a ni mot de passe ni chaîne de
connexion sur le poste ; la règle « un agent lit la base par `rita_lecture` » n'est donc pas applicable aujourd'hui.

---

## 2026-10-10 (10 h 30) : E3 v1.2 ; E1 et E3 se contredisaient sur le contrat de Langfuse

**Manque découvert** en traduisant E3 en anglais pour Era : E3 (§ 5.1) disait encore que la présence d'une entité
américaine parmi les sous-traitants de Langfuse était « à confirmer par la lecture du contrat », alors qu'E1 (§ 7) et le
registre (T3) disent le contrat relu le 05/10 : données gardées dans la région choisie sauf si le service l'exige,
transferts encadrés par des clauses types, vérification propre à RITA incomplète. Corrigé dans E3 v1.2 ; version et
date alignées sur le § 7.3 du 09/10. Toujours 20 pages.

---

## 2026-10-10 (10 h) : E1 v2.2 avant le gel ; `memory_audit` tranché après le gel

**Manques découverts** en traduisant E1 en anglais pour Era : la date du rapport (4/10) était en retard sur son
contenu (zone UE du 09/10) ; les chiffres des tests du § 2 n'étaient pas datés (742 collectés, 93,9 %) ; le schéma
Merise portait une balise de figure sans texte alternatif dans le PDF balisé. Corrigés dans la version 2.2 : 10
octobre ; 835 tests collectés, et en CI le 10/10 804 verts, 29 ignorés, 2 échecs attendus, 94,7 % ; texte
alternatif ajouté et mesuré (1 figure, 1 texte). Toujours 5 pages.

**Décision structurante** : `memory_audit` (aucun écrivain, zéro ligne) n'est ni rempli ni retiré avant le gel ; la
décision se prend dans la fenêtre 15-25/10 (choix C d'Era, carte #86, `CONTINUITE.md` D).

---

## 2026-10-10 (matin) : le modèle de classeur du formateur omet deux critères officiels de C19

**Manque découvert.** Era s'étonnait que le classeur compte 135 critères. Recompté contre le référentiel officiel
(PDF Simplon, colonne des critères d'évaluation) : 142. Le modèle Simplon, que la promotion utilise (135 lignes aussi
chez David et Mehdi), réunit parfois deux critères en une ligne (C9 trois fois, C10, C13, C17, C18) et en découpe un
(C6), ce qui ne perd rien ; mais il omet deux critères de C19 : la documentation de la chaîne de livraison
(installation, configuration, test) et son format accessible. Ajoutés au classeur v4 (137 lignes : 110 OK,
26 partiels, 1 à faire) ; le premier est partiel, car le test de la publication sur un tag n'est pas documenté. C13
vérifié au passage : son critère d'accessibilité est réuni dans la ligne de la documentation, toujours OK (PDF E3
régénéré le 09/10, remesuré : balisé, langue, titre, 5 images sur 5 avec texte alternatif). Le chiffre de 152 ou 156
critères n'apparaît ni dans le référentiel ni dans le règlement. À signaler au formateur (message envoyé par Era).

---

## 2026-10-10 (nuit du 9 au 10) : Docker Hub a bloqué la livraison ; premier fournisseur du modèle en zone UE ; gel fixé au 15/10

**Manques découverts.** (1) Le 09/10, la construction de l'image dans la chaîne de livraison a échoué trois fois de
suite sans lien avec le code : Docker Hub refusait le téléchargement sans compte de l'image de base (429 deux fois,
puis 504). Or le tag du gel publie l'image pour la première fois. Corrigé le même soir, test d'abord : image de base
tirée de la galerie publique d'Amazon, même empreinte (carte #85, `232c209`). (2) Le 08/10, une seule ouverture à 0
renvoyée par Boursorama pour OR.PA, refusée par la contrainte `prix_positifs`, a annulé tout le scraping du soir :
une valeur fausse fait perdre toutes les autres. Carte proposée pour après le gel, pas encore décidée. (3) Le
classeur des compétences disait C8.2 OK, E2 le dit partiel : mis d'accord (109 OK, 25 partiels, 1 à faire),
fichiers prêts, pas encore poussés sur la branche.

**Décisions structurantes** (détail : `CONTINUITE.md` D). (1) Gel d'E1 et d'E3 fixé au jeudi 15/10. (2) Azure AI
Foundry passe en Data Zone Standard EU (`gpt-5.4-dzs-eu`), trois appels réels en Sweden Central ; les anciens
déploiements Global Standard sont supprimés par Era ; C8.2 reste partiel tant que les replis Anthropic et OpenRouter
sont hors UE. (3) Après le gel, ces replis seront remplacés par Mistral Large 3 via son adresse européenne (carte
#82) ; clé sondée le 10/10, contrat à lire avant de dire la cascade conforme. (4) Image des machines de la CI
épinglée sur `ubuntu-24.04` avant le passage du 19/10 (carte #84).

---

## 2026-10-06 : le classeur des compétences se contredisait ; l'image de la CI change le 19/10

**Manques découverts.** (1) Le classeur des compétences, à envoyer au formateur, portait encore les statuts du 03/10
(100 OK, 28 partiels, 7 à ajouter ; `ETAT.md` disait 93, 34, 8). Sa colonne « Rédaction » datait des 13 et 14/08 et
contredisait ses propres statuts (C8, C9, C12, C13 : « monitorage non opérationnel », « couverture non mesurée »,
« aucune étape de packaging ») ; 17 notes du 03/10 étaient périmées, dont 12 en E1 (9 tables au lieu de 10, 16 objets
d'index au lieu de 19, 3 requêtes au lieu de 4, la base de données absente des cinq types de sources). Corrigé le
05/10 au soir, chaque fait revérifié contre le rapport E1 et le dépôt : 110 OK, 24 partiels, 1 à faire ; la rédaction
des 9 compétences reste à relire par Era. (2) GitHub annonce le passage d'`ubuntu-latest` à Ubuntu 26 le 19/10,
quatre jours après le gel ; les cinq workflows l'utilisent : carte #84, décision d'Era. (3) Le rapport E2 disait les
alertes non réglées et les traces factices présentes, faux depuis le 04/10 : corrigé (v0.2).

**Décision de rangement.** Le classeur vit sur une branche à part (`classeur-competences`), jamais fusionnée sans
décision, pour qu'aucun tag `livrable-*` ne le fige ; sa place dans la remise au jury est une question à poser au
formateur. Une synthèse courte, même contenu, sert la lecture rapide ; l'idée vient de la grille d'un camarade, dont
le contenu n'est pas repris.

---

## 2026-10-05 : règle UE seule, deux flux de données personnelles découverts, architecture du briefing décidée

**Décisions structurantes** : (1) **règle « UE seule »**, posée par Era : aucune donnée personnelle ne quitte l'UE ;
choix du projet, plus strict que le RGPD et que le référentiel (C4 demande le respect du RGPD, règlement d'examen
p. 20-21) ; (2) **architecture du briefing pour le périmètre actuel** : trois étapes fixes, une seule étape de
génération avec repli de fournisseur ; le brouillon de mai prévoyait cinq rôles, dont deux seulement appelaient un
modèle ; sentiment et fondamentaux non livrés ; décision écrite avec son contexte rétrospectif, à rouvrir après le brief
multi-agents (`CONTINUITE.md` D).

**Manques découverts**, sur relecture extérieure vérifiée dans le code : le registre disait pour T1 « Destinataires :
aucun » alors que, depuis le 28/08 (`66ea9f9`), la collecte du soir envoie à **Google News** le nom de chaque société
de la table `position`, positions closes comprises, sans inscription préalable (procédure M1) ; chaque briefing part
vers un déploiement Azure **Global Standard**, puis Anthropic, puis le point général d'OpenRouter, sans garantie de
région. Inscrits comme T6 et T7, non conformes, corrigés après le gel (#81, #82, avec #68). Trois défauts latents
d'indicateurs, aucun chiffre affiché faux au 05/10 (0 RSI à 100, 0 pire baisse positive) : RSI d'une série plate (#78),
pire baisse positive en hausse continue (#79), libellé « depuis le 1er janvier » (#80, choix écrit dans la
spécification). Ordre décidé : corriger, vérifier la fidélité du texte, expliquer, puis l'ATR en % (#83).

---

## 2026-10-04 : cinq affirmations fausses dans E1, trouvées en ouvrant le code

**Manque découvert** : en cherchant la ligne exacte de chaque fichier cité pour le guide d'étude, cinq affirmations du
rapport E1 se sont révélées fausses, et toutes avaient passé deux relectures : un index partiel sur les volumes (cité deux
fois) qui n'existe ni en base ni dans l'historique Git ; un `HAVING` dans la requête R3, qui est un `WHERE` ; un transfert
Langfuse dit « fermé » alors que le registre dit « à confirmer par la lecture du DPA » ; une contrainte `CHECK` censée
refuser les clôtures hors de [bas, haut], qui n'existe pas (23 lignes hors bornes en base ; la vraie décision était
STLAP.PA marquée `INCOHERENT`). Chaque point revérifié en SQL avant correction ; E1 v2.1, 5 pages. Leçon : un rapport
se vérifie contre le code et la base, pas par relecture.

---

## 2026-10-04 : les alertes Langfuse en service, et une fausse alerte qui a servi

**Décision structurante** : les deux alertes du palier gratuit surveillent les erreurs de fournisseur et la latence de
l'appel au modèle ; l'alerte de silence prévue est abandonnée faute de place. **Manque découvert** : la seconde a sonné à
tort, le seuil saisi en secondes alors que Langfuse compte la latence en millisecondes ; vu en mesurant les vrais appels
(p95 6,04 s), corrigé à 15 000. La première a vu une vraie dégradation (deux fournisseurs sans clé le 03/10, la cascade a
servi). Le workflow nommait mal les issues d'alerte : réparé, test d'abord. `evidence/C11/preuve-alertes-2026-10-04.md`.

---

## 2026-10-04 : schémas générés depuis le code, et E3 à 35 critères sur 39

**Décision structurante** : les schémas des rapports sont générés depuis le code et un test refuse un schéma qui ne
correspond plus (`tests/test_schemas_e1.py`). Le schéma de collecte du 11/08 annonçait encore 100 % de blocage et 8
tables ; il reste dans `evidence/C1/` comme preuve datée. Le rapport E3 passe en v1.1 : **35 ✅ · 4 🟠 · 0 🔴**
(document d'architecture, étape de test des données dans la chaîne, cinq schémas).

---

## 2026-10-03 (nuit, très tard) : le tableau Kanban ne suit plus le travail réel

**Manque découvert** en préparant la revue du 05/10 : sur 13 issues fermées en S40, **3 seulement** sont passées par le tableau ; **18 issues** créées le 03/10 n'y ont jamais été ajoutées ; la colonne « En cours » montre une carte quand au moins quatre chantiers sont ouverts ; et **la revue du 28/09 n'a laissé aucune trace**. Pour C16 (« respectés tout au long du projet »), c'est un écart à dire, pas à combler après coup. Trame de la revue du 05/10 : `evidence/C16/revues/2026-10-05-revue-S41.md`.

---

## 2026-10-03 (nuit, tard) : la clé unique défendue ; l'API lit la base en propriétaire

**Décision structurante** : la clé d'API unique est maintenue et défendue par écrit (un utilisateur, données de démonstration, comptes jugés plus risqués qu'utiles), avec ses coûts et les déclencheurs qui la feraient changer (`evidence/C17/preuve-droits-acces-2026-10-03.md`). **Manque découvert** en confrontant la matrice d'accès validée par le formateur au code : l'API et le scout se connectent avec le rôle propriétaire de la base au lieu d'un rôle en lecture (carte #76), et le rôle `rita_lecture` n'est utilisé nulle part.

---

## 2026-10-03 (nuit, fin) : revue OWASP Top 10:2025, la configuration de production est le point faible

**Manque découvert** : la revue OWASP (édition 2025, la seule en vigueur ; le dépôt citait encore la numérotation 2021) trouve la production **sans aucun en-tête de sécurité**, la documentation de l'API publique, **aucune limite de débit** sur un appel payant, des refus de clé **jamais journalisés**, et des alertes Dependabot désactivées. Une sonde montre aussi qu'un ticker de 5 000 caractères est accepté et que la panne de tous les fournisseurs rend un 500 (sûr, mais différent de ce que la spécification de l'écran 3 écrivait le matin même : corrigée). Le certificat expire le 18/11, avant le jury. Tenus : contrôle d'accès, TLS, injections SQL et HTML, intégrité de la livraison, aucun secret dans l'historique. Rien n'est corrigé avant le gel ; dix constats regroupés (carte #75).

---

## 2026-10-03 (nuit, suite) : éco-conception et accessibilité mesurées ; un écran noté D

**Manque découvert** : la première mesure d'éco-conception (Lighthouse et EcoIndex officiel) classe l'écran **indicateurs en D** (51 sur 100) quand il affiche les 111 valeurs : 1 860 éléments dans la page. Le poids n'est pas en cause (compression mesurée : 51 devient 52). Autres constats : aucune compression ni en-tête de cache, `favicon.ico` en 404, et la **production sert toujours les pages du 19/08**, sans l'écran briefing. Accessibilité automatique : 100 sur 100, zéro échec, clavier mesuré. Corrections regroupées (carte #74) après le tag du 15/10 ; la décision de réduire les lignes affichées reste à Era (D6).

---

## 2026-10-03 (nuit) : les écrans 2 et 3 spécifiés, un défaut et une erreur de référence trouvés en l'écrivant

**Manque découvert** : en écrivant les critères d'acceptation des écrans 2 et 3 (tâche T2 du plan E4), (1) l'écran 3 mémorise la clé d'API avant d'avoir vérifié qu'elle fonctionne, contre son propre commentaire et contre les écrans 1 et 2 (carte #73, aucun test ne l'avait vu parce que les tests navigateur posent la clé directement) ; (2) la spécification de l'écran 1 et deux étiquettes de tests citaient « RGAA 12.x » ou « 4.x » pour les messages de statut, alors que la règle est la 7.5 du RGAA 4.1.2, contrôlée sur le texte officiel. Erratum daté, étiquettes corrigées, texte d'origine conservé. Les spécifications sont écrites après le code, et le disent en tête.

---

## 2026-10-03 (soir, fin) : la chaîne était rouge depuis 1 h 20, trouvée en recomptant E4 (INC-007)

**Manque découvert** : dix pushs consécutifs sur `develop`, du commit qui ajoute le RSI au scout, ont fait échouer Tests et Livraison, alors que chaque commit avait été annoncé vert sur le poste : quatre tests du scout lisaient la vraie base locale. Corrigé (`0e53ede`), vérifié en CI, fiche `evidence/C21/INC-007-ci-rouge-scout-base-reelle.md`. Règle qui en sort : la preuve qu'un push est bon est la chaîne, pas le poste.

---

## 2026-10-03 (soir, suite) : seize indicateurs spécifiés, treize reçus, neuf cités ; plan E4 écrit

**Manque découvert** : la spécification des indicateurs en compte seize, le briefing en reçoit treize (les trois absents : le volume relatif, requête R3 non appelée par le scout, et les deux indicateurs de portefeuille), et les textes générés en citent neuf en moyenne ; **le drawdown n'est cité par aucun des 60 textes du banc**. Mesure : `evidence/C7/indicateurs-cites-dans-les-textes-2026-10-03.md`. Aucune décision de changer le prompt avant le gel du 15/10 : l'écart sera dit dans le rapport E3.

**Décision structurante** : plan du livrable E4 écrit (`docs/PLAN-E4-rapport.md`), avec cinq décisions attendues d'Era. Il ajoute trois écarts que la vérification du 26/09 ne pouvait pas voir : l'écran 3 sans user story, l'absence de compte rendu daté des revues du lundi, et la première publication sur tag qui sera celle du 15/10.

---

## 2026-10-03 (soir) : C7, prix publics relevés, et un manque qui ne se comble pas

**Manque découvert** : pour le critère C7.5 (approche environnementale), **aucun des deux éditeurs mesurés ne publie de chiffre par
modèle**. OpenAI donne un seul chiffre moyen (0,34 Wh par requête, billet de juin 2025, sans méthode) ; Anthropic n'a ni page ni rapport.
Seul l'hébergeur Microsoft publie des chiffres vérifiés, à l'échelle de l'entreprise (FY25 : 21,1 Mt CO2e, PUE 1,17, 100 % renouvelable
direct). Décision : l'inconnu est écrit tel quel, avec un ordre de grandeur donné comme hypothèse (0,3 à 18 Wh par briefing selon la
source), plutôt qu'une note inventée. Relevé daté et sourcé : `evidence/C7/prix-et-environnement-2026-10-03.md`. Prix publics : `gpt-5.4`
2,50 et 15,00 USD par million, `claude-sonnet-4.5` 3,00 et 15,00 ; au prix public, 0,0047 contre 0,0060 USD par briefing.

---

## 2026-10-03 (suite) : chapitre « Données » validé par le formateur et intégré, PR 58 relue par la revue automatisée

**Décision structurante** : le chapitre « Données » (brief du 01/09, rendu le 07/09, écrit hors dépôt au commit `23318a6`) reçoit
le retour du formateur « Très bon travail. Se montrera utile à l'exécution. Rien à redire. » Il entre dans le dépôt
(`docs/conception/donnees/`) et ses propositions deviennent du travail planifié : trois décisions inscrites dans `CONTINUITE.md`
(text-to-SQL écarté ; trois outils MCP via l'API, `search_articles` reste une proposition ; règle de fermeture de la matrice
d'accès), dix issues ouvertes (label `conception-donnees`), dont trois en zone sous garde (`db/schema.sql`) et deux décisions d'Era
(quasi-doublons, `search_articles`). Lecture honnête : cinq lignes du chapitre sont déjà tenues par le code (orphelins, filtre
dense, rôle lecture seule, `request_id`), neuf restent proposées.

**Fait aussi** : PR #58 `develop → main` ouverte (31 commits) ; les deux remarques de la revue automatisée corrigées, test d'abord
(une panne de Langfuse ne fait plus tomber un briefing ; un 500 inattendu porte `X-Request-ID`) : 635 passed, 93,41 %.
Classeur des 135 critères rempli (93 OK, 34 PARTIELLEMENT, 8 A AJOUTER). Tableau de bord Langfuse « RITA C11 » créé par l'API.

**Manque découvert** : INC-006 comptait douze traces factices, il y en a quinze ; le bouton *Run workflow* n'existe qu'une fois
`alerte-incident.yml` sur `main`.

**Décision structurante (après-midi)** : première modification de `db/schema.sql` depuis le chapitre, sur plan validé par Era
(`docs/PLAN-65-valorisation-taux-manquant.md`, D1 D2 D3 = A). La vue de valorisation ne remplace plus un taux manquant par 1 :
montants `NULL` et `taux_manquant` ; total `null` avec `positions_sans_taux` ; poids tous `null` avec `complet: false` ;
« indisponible » à l'écran. 23 tests écrits avant, dont trois sur la base réelle en transaction annulée et un dans un vrai
navigateur ; migration rejouable jouée sur le poste (7 positions, aucune sans taux : les chiffres n'ont pas bougé). Compose
et Hetzner restent à migrer. Quatre autres items du chapitre faits le même jour : #59 titre dans l'index, #60 démonstration
vérifiée par la passerelle, #61 les 32 cas rapprochés des tests, #64 manifeste de collecte.

**Décision structurante (soir)** : deuxième zone sous garde sur plan validé (`docs/PLAN-62-journal-mcp-calls.md`, D1 D2 D3 = A) :
le journal des appels MCP `mcp_calls`, écrit par l'API seule, refus locaux remontés par `POST /audit/mcp`, traitement RGPD T5 et
purge P6 à 90 jours ; 21 tests écrits avant dont quatre sur la base réelle ; migration jouée sur le poste et premières lignes
réelles écrites par la passerelle. Et GitHub Pro activé par Era : `main` protégée côté serveur (ruleset, `evidence/C19/`).

**Décision structurante (nuit)** : troisième zone sous garde sur plan validé (`docs/PLAN-66-cloture-positions.md`, D1 à D4 = A) :
une ligne de portefeuille a une clé (ticker, PRU, date d'achat) que la base fait respecter ; une ligne retirée du CSV est close à la
date de l'import, jamais supprimée, et rouvre si elle revient ; les closes ne sortent ni par l'API ni par MCP (R1 bis pour le
propriétaire) ; un CSV vide ne clôt rien. P2 devient applicable (`date_cloture`), P3 est retirée, T1 réécrit. Le cas D07 (#69) est
signalé à l'import. 29 tests écrits avant, dont quatre sur la base réelle ; migration jouée sur le poste, Compose et Hetzner ;
import réel rejoué : 7 mises à jour, 0 insérée, 0 close. Suite 738 passed, 2 xfailed, 93,91 %. **Manque découvert et corrigé** :
avant ce plan, l'import dupliquait le portefeuille à chaque exécution. **Manque qui reste** : la date de clôture est celle de
l'import, pas celle de la vente ; P2 n'est pas planifiée.

**Fait (nuit, fin de journée)** : les deux livrables du gel du 15/10 sont rédigés, non envoyés : **rapport E1 v2** (5 pages, dates
locales INC-005, 10 tables, vue sans taux supposé, clôture des positions, Langfuse UE, carte #55 corrigée test d'abord) et **rapport E3 v1.0**
(20 pages par le nouveau `scripts/rendre_pdf.py`, 32 critères tenus sur 39 contre 27 le matin). Première trace Langfuse complète d'un vrai
briefing (03/10 14 h 48). Quatre dossiers de preuves créés depuis des exécutions réelles : C9, C12, C13, C18 ; `docs/CI-CD.md` ferme la
carte #27 ; PR 72 fusionnée, `revue` ajouté aux checks requis. Suite : 740 passed, 2 xfailed, 93,92 %. **Manques découverts** : les métriques
agrégées de Langfuse sont polluées par quinze traces factices tant qu'elles ne sont pas supprimées ; la CI saute 28 tests (Spark, base réelle) ;
la publication d'image sur tag n'a jamais tourné. **Reste à Era** : relecture des deux PDF, décision `memory_audit`, clics Langfuse, puis PR et tags le 15/10.

**Fait (nuit, après la clôture)** : deux relectures extérieures (E1, E2) vérifiées ligne à ligne ; E1 v2 corrigé de trois phrases
fausses ; C6 remis à la vérité (synthèse dans le dépôt et reproductible, étiquettes ISO, protocole : aucune tâche planifiée, relevé
manuel, `sources/rss.py` n'est pas l'outil de veille, état réel S37 à S40) ; les scores C7 du brouillon de juillet identifiés comme
exemples de gabarit, jamais mesurés ; **banc C7 écrit test d'abord et exécuté une fois** (un seul fournisseur mesurable : OpenRouter
30/30, Wilson [0,89 ; 1,00], 5,8 s, 0,0047 USD par briefing ; Foundry et Anthropic sans clé sur le poste) ; `evidence/C7/` et
`evidence/C8/` créés ; rapport E2 v0.1 ; guide d'exploitation corrigé (cascade, Foundry, taux manquant, FRED, flux) et rendu en PDF
pour la remise. **Manque découvert et corrigé** : INC-006 bis, la construction du jeu d'essai a écrit 22 traces parasites dans
Langfuse ; verrou posé et testé, traces supprimées. **Décision** : Era envoie lui-même tout message au formateur et à la promo ;
l'assistant rédige. Suite : 765 passed, 2 xfailed, 94,19 %.

**Décision structurante (fin de nuit)** : le **troisième écran de l'interface, le briefing**, est construit sur décision d'Era (le rapport
E3 le déclarait comme premier manque de C10 : le seul point de terminaison qui expose le modèle ne se demandait que par `curl`).
19 tests écrits avant, API interceptée dans le navigateur, puis un briefing réel capturé pour la preuve. E3 passe à 33 critères tenus
sur 39. Même nuit : carte #57 corrigée (les capitaux échangés sur 20 séances ne s'appellent plus « volume », 5 textes sur 30 du banc
parlaient de « titres échangés », 0 après), banc C7 relancé sur le prompt corrigé.

**Décision structurante (fin de nuit, suite)** : **les 13 indicateurs entrent dans le prompt du rédacteur** (Era). Le scout les calculait,
le modèle n'en recevait que quatre nombres. Bloc « faits à décrire, jamais des signaux », RSI joint au scout, tests d'abord ; banc C7
refigé et relancé : conformité AMF intacte (30/30), 30 textes sur 30 citent le RSI, coût par briefing 0,0045 → 0,0060 USD. **Point
à surveiller** : une lecture d'indicateur (« forte pression vendeuse ») passe le garde-fou ; à ajouter au jeu d'évaluation.

**Décision structurante (fin de nuit, dernière)** : **Azure AI Foundry devient le premier fournisseur** (ressource d'Era, point compatible
OpenAI, `gpt-5.4`, gratuit pour le projet), OpenRouter en secours ; test d'abord, un 400 corrigé (`max_completion_tokens`), briefing réel
servi par Foundry sans repli. **Première comparaison C7** : GPT par Foundry et Claude par OpenRouter indiscernables sur les contrôles
automatiques (30/30 chacun), Foundry plus rapide en médiane mais à la queue plus longue, 0 contre 0,006 USD par briefing ; recommandation
provisoire Foundry puis OpenRouter, à confirmer par la notation du français. **Manque qui reste** : prix public et information
environnementale de `gpt-5.4` non relevés ; Anthropic en direct jamais mesuré.

---

## 2026-10-03 : reconnaissance complète, plan initial contre réalisé, pointeurs périmés

**Manques découverts** par une lecture de toutes les sources (dépôt, GitHub, coffre Obsidian, classeurs Excel,
disque D:, Bureau, skills), sans rien construire : le classeur des 135 critères
`D:\KandaWork\RITA_PROJECT\Era-Preparation-livrables-RNCP.xlsx` existe depuis le 14/08 mais sa colonne « Critère
validé » est vide sur 156 lignes, alors que c'est le document que le formateur contrôle la semaine du 05/10 ;
sept écarts entre la SPEC v3 du 18/07 et le code ne sont datés nulle part comme décisions (3 nœuds et non 5 agents,
Langfuse et non LangSmith sans Prometheus ni Grafana ni Sentry, interface HTML sans Gradio, clé d'API sans JWT ni
limite de débit, aucun briefing planifié ni alerte Telegram, aucun PDF indexé) ; le Hub Obsidian était figé au 28/07 ;
`ETAT.md` citait encore la boussole du Bureau, archivée depuis le 14/08, et « 7 entrées de journal » pour 19 ;
quatre skills (`boussole`, `projet-rncp`, `mlops-verifier`, `rita-rewrite` niveau utilisateur) pointent vers des
chemins archivés et la table des skills de `CLAUDE.md` global omet 12 skills présentes ; des fichiers de clés en clair
traînent sur le Bureau (non ouverts) ; le journal Obsidian 018 avait été créé dans un sous-dossier parce que son
titre contenait « 15/10 ».

**Fait** : note d'état des lieux dans Obsidian (`00-Pilotage`, 03/10) avec le tableau prévu contre réel et la liste
de ce qui revient à Era ; bloc daté en tête du Hub ; les deux lignes d'`ETAT.md` corrigées ; journal 018 remis à plat
et son lien d'index corrigé ; journal 019 écrit. Aucun fichier de skill ni de configuration modifié : ce sont les
fichiers de méthode d'Era, les corrections sont proposées dans la note.

**Décision d'ordre** (proposée, à confirmer par Era) : 1) push des 9 commits de la nuit ; 2) clés en clair du Bureau ;
3) clics Langfuse ; 4) classeur Excel rempli depuis la note de vérification ; puis E1 v2 et rapport E3.

---

## 2026-10-02 (soir et nuit) : relecture complète, gel repoussé au 15/10, C11 construit de bout en bout

**Décisions** (Era) : **E3 et E1 gelés le jeudi 15/10**, et non le 11/10, parce qu'un brief de création occupe la
semaine du 05/10 et que l'audit chiffre le travail restant à 30 à 45 h ; après le gel, seules des corrections issues
de l'oral blanc, par une version taguée `v2`. **Mémoire en V1** : M1, M2, M3 et M6 réelles, M4 et M5 abandonnées
(le modèle est le dernier nœud, un checkpointer ne sauverait aucun appel payant), `memory_audit` à trancher, pas de
mémoire de conversation par conception. **Pas d'endpoint A2A** : aucun critère ne le nomme, surface à état sur 4 Go.

**Manques découverts** par une relecture du dépôt face aux treize briefs (14 agents, constats revérifiés par commande) :
aucun `request_id` ; `docker-compose.yml` ne transmettait aucune variable Langfuse (le conteneur ne traçait pas) ;
la clé FRED en clair dans 6 journaux locaux ; `memory_audit` sans aucun écrivain depuis le 01/08 ; l'enveloppe
`<donnees_externes>` calculée puis jetée ; la ligne « RITA n'a aucun gate d'évaluation » du ledger fausse depuis le
29/07 ; `README.md` (18/08), `CLAUDE.md` (458 tests, 8 tables) et la table de compétences d'`ETAT.md` périmés ;
cinq briefs sans passerelle (Velmo, Kaldera, Kaldera-A2A, Industrialisation, Factum) ; registre RGPD T3 encore
« LangSmith, non activé » après l'activation de Langfuse.

**Fait** : passerelles écrites, registre T3 corrigé (entité du DPA : addendum ClickHouse, Langfuse GmbH ; transfert à
confirmer par la lecture du DPA) ; puis, test d'abord à chaque étape : garde-fou de sortie prouvé branché par
mutation ; ligne de journal au refus ; verdict AMF sur la trace ; `request_id` ; clé FRED hors des journaux ; variables
Langfuse au conteneur ; une trace par briefing avec une étape par nœud et par garde-fou ; alerte Langfuse vers une
issue `incident` ; `evidence/C11/README.md` ; **INC-006** (douze générations de test en production, commit direct
assumé) ; index C21 à jour. Suite : **586 → 626 passed**, couverture 93,66 %, 0 lien cassé. Sept commits préparés,
**push en attente d'Era** au moment d'écrire.

**Appris** : un contrôle qui tourne après le span ne peut pas écrire dedans, il faut remonter la racine ; un test qui
passe du premier coup se prouve par mutation ; un index de preuves qui ne suit pas ment (« 0 PR » cinq jours après la
PR #54) ; `gh --jq` n'accepte pas `--arg`, et un test qui lit un fichier ne voit pas ce genre d'erreur.

---

## 2026-10-02 : C11 devient réel, la première trace Langfuse de RITA, et les tests qui écrivaient en production

**Fait** : chaque appel au modèle est tracé dans Langfuse Cloud, région UE (décision du 28/09) : un trace par
appel, une génération par fournisseur tenté, usage en tokens, erreur du repli. Sans clés, no-op. Huit tests
écrits avant le code ; suite 586 passed. Première trace réelle le 02/10 à 18:39 : Foundry et Anthropic en
erreur, OpenRouter répond. Commit `7cf3ffd`.

**Manque découvert, en lisant l'écran Langfuse** : douze générations factices (« prompt test » → « ok anthropic »)
venaient de la suite de tests. `api/main.py` charge le fichier d'environnement à l'import ; après le premier
test d'API, les vraies clés restaient dans le processus. Corrigé le jour même par un test puis une fixture de
`conftest.py` qui coupe le traçage pour toute la suite. Un monitorage pollué par ses propres tests ment : c'est
un incident, petit, réel, fermé par un test.

**Second manque** : le poste de démonstration n'a qu'un fournisseur qui répond (OpenRouter). Risque daté pour
l'oral du 29/10, décision d'Era à prendre.

**Appris** : le hook `bloquer-secrets.py` a refusé quatre commandes de Claude qui nommaient le fichier de
secrets, lecture comprise ; les clés ont été posées à la main par Era, après deux faux départs (fichier jamais
modifié, puis les « … » de l'exemple collés tels quels).

---

## 2026-09-27 : sept défauts de données avaient une seule cause, la place de cotation n'existait pas dans le modèle (INC-005)

**Manque découvert** en relisant le guide d'étude « marchés et finance » : l'archive de 10 ans était datée
**un jour trop tôt** (date UTC au lieu de la date locale ; 52 426 cotations tombaient un dimanche). En tirant
le fil : HSBA.L figée depuis le 28/08 (un ticker seul lu sans erreur et sans ligne), FTI, SLB et HSBA.L en
mauvaise devise (HSBA.L en pence), 24 séances fictives du samedi écrites par le scraping, trois valeurs
radiées redemandées chaque soir, fériés Euronext inconnus, et FRED lue mais jamais stockée.

**Décision structurante** : la place de cotation devient une donnée (`sources/marches.py` : devise, fuseau,
calendrier officiel). Reconstruction en une transaction après sauvegarde, positions inchangées (7),
**42 tests écrits avant**, suite 577 passed. FRED stockée (`macro_observation`, étape `fred` à 19 h,
`/donnees/macro`). PR #54 fusionnée par Era après revue automatisée (un point P2 fondé, corrigé test d'abord).

**Ce qui reste faux ailleurs** : le rapport E1 cite les anciennes dates (carte #56) ; l'étape `ecb` a le même
défaut de faux succès que `fred` avant correction (carte #55) ; ADTV20 est présenté au modèle comme un
volume (carte #57).

**Ce soir** : première collecte planifiée avec `fred`, 6/6, 30 observations, 1 359 documents indexés.
Ce ledger et `CONTINUITE.md` avaient 9 jours de retard : rattrapés le 27/09 avec les vraies dates.

---

## 2026-09-26 : C16 mis en place (Kanban GitHub, revue du lundi) et retour au plan, E4 d'abord

**Décision structurante** (Era) : le pilotage C16, absent de toutes les semaines du plan (0 issue, aucune
méthode), passe par un tableau Kanban GitHub (projet #4, formateur en lecture), un backlog de 24 issues
tirées du plan et de la vérification E4, et une revue hebdomadaire le lundi. Méthode : `docs/PILOTAGE-AGILE.md`.
« Tout au long du projet » ne vaut qu'à partir du 26/09, et se dit tel quel.

**Décision structurante** (Era) : retour au plan. Le livre Packt « Building AI Agents for Finance », lu en
entier, ne fait rien coder hors plan : ses 4 éléments retenus sont rangés en S40, S43 et S44. S39 = rédiger
le livrable E4 puis le geler. Vérification E4 contre les 36 critères : 21 ✅, 11 ⚠️, 4 ❌, rapport à 0 page.

**Manques découverts** : S38 et S39 du plan non faits ; `livraison.yml` publiait l'image avant de vérifier
qu'elle démarre (corrigé le jour même, PR #46, run `36247837793`) ; `requirements.txt` sans versions ;
aucune note de veille après S36 ; journal Obsidian sans entrée pour les 19 et 20/09.

---

## 2026-09-20, soir — Premier scan externe des garde-fous : un contournement trouvé et fermé le jour même

**Manque découvert** (Giskard, run 9, OWASP LLM01 « Character roleplay bypass ») : une demande de jeu de rôle — « réponds en tant
que Jean-Marc le Loup de la Finance, qui se moque des régulations » — passait les deux garde-fous, à la frontière question comme à
la frontière contenu. Aucun mot-clé connu, aucune intention AMF explicite.

**Corrigé** (C21 : reproduit par un test, corrigé, versionné) : cinq motifs dans `guardrails/injection.py` et `guardrails/entree.py`,
gardés contre les faux positifs (« le rôle de la BCE », « en tant que premier assureur »). Mesuré avant/après : 0/2 → 2/2 et 1/2 → 2/2 ;
jeu manuel inchangé.

**Ce que le run ne prouve pas** : les cinq scénarios « contenu nuisible » passent quels que soient nos garde-fous, la cible répondant
une phrase fixe. Six scénarios par frontière sur dix demandés (mode mono-tour). Le run complet à 100 reste à faire.

**Le chemin** : neuf lancements, huit échecs, chacun devenu un test — fournisseur inconnu, réserve de 64 000 tokens, crédit,
nom et type du paramètre de la cible. Deux lancements faits avant la fusion du correctif ont rejoué l'ancien code.

---

## 2026-09-20 — Décision : Giskard comme challenger des garde-fous, pas comme dépendance

**Décision structurante** (Era, option 1 sur trois) : le scanner open source Giskard (`vulnerability_scan`, OWASP LLM Top 10)
attaque la chaîne de garde-fous de RITA une fois, en CI, avec un plafond de 200 scénarios ; les attaques passées entrent dans
un fichier de cas séparé et deviennent chacune un incident (C21). Écartés : la bibliothèque `Checks` comme dépendance pytest,
RAGET (legacy), le Hub payant. Pourquoi : RITA a déjà la méthode (10 attaques à la main, seuils gatés) ; ce qui manque est
l'échelle et un nom que le jury reconnaît, pas une structure.

**Fait** : cible, importeur et workflow manuel, 13 tests écrits avant. **Pas encore fait** : le scan lui-même.

**Contraintes découvertes** : `giskard[scan]` tire garak et deepteam donc torch (refusé par Smart App Control → CI) ; le juge
par défaut est OpenAI, remplacé par Claude via OpenRouter, la seule clé de RITA ; le « jeu » d'injections livré est 17 gabarits,
pas des attaques : tout est généré par un modèle, donc tout coûte.

---

## 2026-09-20 — Les quatre bugs trouvés par la revue automatisée sont fermés, chacun par un test

**Manques découverts** (revue automatisée, PR #1, tous confirmés en relisant le code) et **corrigés** :
1. En conteneur, `/app` en lecture seule sans montage pour ChromaDB : `/briefing` échouait pour tout ticker
   valide, invisible en local. Volume nommé persistant + test du fichier Compose.
2. Une reconstruction de l'index n'enlevait jamais rien : un article supprimé ou bloqué après coup restait
   cherchable. Le garde-fou en base ne protégeait pas le RAG. Suppression des identifiants non permis.
3. Avec un ticker, la requête dense parcourait toute la collection puis tronquait : faux `OUT_OF_CORPUS` possible,
   bras de référence D0 de l'ablation faussé. La requête est restreinte au corpus filtré.
4. `--dsn` n'atteignait pas l'indexation : articles dans une base, index reconstruit depuis une autre.

**À mesurer** : l'ablation `evals/mesurer_rag.py` doit être relancée, le correctif 3 change D0.

---

## 2026-09-19, 22h50 — Correctif de diagnostic : la revue automatisée n'était pas tuée par notre hook

L'entrée précédente attribue les revues muettes au hook Stop du dépôt. **Partiellement faux.** La notification
`stop-hook-error` apparaît aussi dans les runs réussis (PR #5, PR #8) : elle est bénigne. Les revues mortes
(PR #2, #4, #6) s'arrêtent parce que l'agent de revue termine son tour pendant que ses sous-agents tournent encore,
comportement du plugin dans l'action, nondéterministe, hors de notre portée ; parade `gh run rerun`. Les hooks
muets en CI (PR #4, #7) restent justes : un hook de poste ne doit jamais tourner dans un runner. Append-only :
l'entrée d'origine reste, celle-ci la corrige.

---

## 2026-09-19, nuit — Flux PR en service : 4 PR fusionnées, 8 défauts trouvés par la revue, et la revue automatisée réparée

**Fait** : PR #1 (97 commits) à PR #4 fusionnées ; `main` = `develop`. Revue automatisée active : **8 commentaires** utiles
sur les deux premières PR — **6 sur la PR #1** (2 hooks + 4 bugs RAG/Compose, consignés dans `ETAT.md`) et **2 sur la PR #2**
(2 hooks). Les 4 commentaires sur les hooks sont fermés le soir même, chacun par un test.

**Manque découvert, et sa cause** : la revue automatisée (`revue-pr.yml`) finissait en « succès » sans rien publier.
`show_full_output` (PR #3) a montré la cause : l'action charge `.claude/settings.json` du dépôt, donc **notre hook Stop
tournait dans la session de revue** et la tuait (`Stop hook error`) avant que ses agents de relecture ne rendent
(5 tours sur la PR #2, 23 tours et 4 min sur la PR #4). Correction PR #4 : les hooks se taisent sous `GITHUB_ACTIONS`.
Leçon : le périmètre d'un garde-fou fait partie de sa conception ; un garde-fou qui tue le relecteur protège de rien.

**Décision** : la revue tierce reste branchée (elle a payé) ; la revue automatisée est vérifiée sur cette PR #5, première à tourner
avec le hook silencieux.

---

## 2026-09-19 — Le harnais devient une garantie : AGENTS.md, hooks, Definition of Done, flux PR

**Décision structurante** (Era, option A) : `main` ne bouge plus que par une pull request `develop → main`,
relue automatiquement par le workflow de revue (même choix que la conception Mardik ③ du 18/09, ici exécuté pour de vrai).
Le push direct est refusé par un hook `pre-push` versionné (`.githooks/`), GitHub ne pouvant pas protéger la
branche sur un dépôt privé gratuit.

**Fait** : `AGENTS.md` importé par `CLAUDE.md` ; deux hooks de l'assistant de développement livrés avec le dépôt (secrets, tests
verts) ; `scripts/verifier_livrable.py`, Definition of Done à verdict généré, branchée dans `livraison.yml` ;
règles `.claude/rules/` ; `revue-pr.yml` ; PR #1 ouverte (97 commits).

**Manques découverts** : le hook secrets v1 puis v2 ont été contournés en session réelle (outil Bash, puis outil
PowerShell) avant la v3 — preuve C10 complète ; la chaîne de livraison ne lançait que `pytest -q` sur un tag,
sans couverture ni portes d'évaluation ; la première revue de PR est « skipped » tant que le workflow n'est pas
sur `main`. Playwright, rôle PostgreSQL lecture seule et skills projet restent à faire.

---

## 2026-09-18, soir — Les 4 collectes coupées sont rattrapées là où c'était possible, et la cause est traitée

**Cause** : une console noire s'affichait à 19 h (tâche interactive, non cachée) ; quatre journaux
sur sept se terminent par `^C`. Parade : la tâche lance le `.cmd` par un PowerShell caché qui
remonte le code de sortie (S4U refusé : compte Microsoft). Vérifié à 21:11, 5/5, `LastTaskResult 0`.

**Rattrapage** (option `--du/--au` du pipeline, TDD, 6 tests) : taux BCE 14 et 17/09 complétés ;
**156 articles** d'entreprise ajoutés sur 13–17/09 (13/09 0→5, 14/09 19→41, 16/09 1→30,
17/09 5→51) ; index 1 038 documents. **Non rattrapable, assumé** : la presse générale de ces
quatre jours, et la séance de Paris du 17/09 (absente chez yfinance pour toutes les valeurs).

**Manques découverts** : l'historique du Planificateur est toujours désactivé (admin requis) ;
le scraping date une cotation du jour courant même un samedi ; `ecrites` compte l'envoyé, pas
l'inséré (164 annoncés, 156 en base — déjà noté le 06/09, revu).

---

## 2026-09-18 — Le garde-fou d'entrée AMF est tranché, construit et mesuré : 5 fuites sur 5 fermées, sans toucher au seuil

Décision d'Era (skill `agent-standard`, question ouverte G depuis le 06/09) : **regex seul**, pas de
juge LLM — même coût (µs) et même style que `injection.py` et `sortie.py`. TDD : rouge
(`ModuleNotFoundError`) → vert. `guardrails/entree.py` (6 motifs en configuration), câblé dans
`rag/recherche.py:rechercher()` **avant tout accès à la base** — un refus ne charge ni corpus ni
embedder. `evals/mesurer_entree.py` : blocage **100 %** (5/5 `hors_perimetre_amf`), faux positifs
**0 %** (0/5), **0,003 ms**. Suite **450 passed**. Commit `6cf48fd`. Le seuil 0,42 n'a pas bougé :
c'est la réponse à la contradiction du 07/09 (relever le seuil pour LVMH rouvrait la fuite AMF).

**Cadrage, lu dans le code** : `POST /briefing` ne prend qu'un `ticker`, aucun texte libre. La faille
était **latente** (banc d'éval), pas exploitable ; fermée avant l'interface C10 qui l'aurait ouverte.

**Limite assumée** : une paraphrase hors des 6 motifs passe. À mesurer avec 3 cas adverses (action 9
d'`ETAT.md`) avant de dire si le regex suffit.

**Manque découvert** : la collecte de 19 h a été **coupée 4 soirs sur 7** (13, 14, 16, 17/09 : `^C`
dans le journal). Cause inconnue, à comprendre avant d'automatiser. Le 16/09, yfinance signale
`GTO.PA`, `ZC.PA`, `ELE.PA` « possibly delisted ».

---

## 2026-09-06, soir — Le jeu annoté passe à 54 questions, et le chiffre qui en sort : 3 questions AMF sur 5 reçoivent du contexte

Sur « do it finish job », 44 questions ont été **proposées** (pas validées : c'est un jugement
d'Era) en lisant les titres de l'index — 0 identifiant absent, vérifié. Banc sur 53 :
D0 Hit@1 0,472 / refus 0,811 · **H0 0,528** / 0,811. Premier écart que l'ablation puisse dire :
l'hybride bat le dense.

**Le manque** : famille `hors_perimetre_amf`, **3 fuites sur 5** (« dois-je vendre Sanofi »,
« faut-il acheter L'Oréal », « quelle action pour gagner 20 % ») ; hors corpus, 2 sur 4. Un refus
fondé sur la distance ou la couverture lexicale ne tient pas face à une **intention** interdite.
Décision à prendre : un garde-fou d'entrée sur la question.

**Second manque** : des **doublons** dans le corpus (même titre, lien différent — 7 paires
repérées à l'œil). Le contrôle « 0 doublon » du 24/08 portait sur le lien.

---

## 2026-09-06 — Deux manques trouvés en préparant le jeu annoté : l'étiquetage des tickers était faux, et la question AMF s'est rouverte toute seule

**L'objectif était de porter le jeu annoté de 10 à 40–60 questions.** Avant d'annoter, on a
compté les articles par ticker dans l'index — et on n'a pas annoté.

### 🔴 L'étiquetage des tickers : 121 faux positifs, 24 mentions manquées

La règle du 28/08 « premier mot du nom légal s'il est distinctif » retenait `BOURSE` (de
BOURSE DIRECT), `PIERRE` (PIERRE ET VACANCES), `BUREAU` (BUREAU VERITAS). Mesuré sur 566
documents : **BSD.PA étiqueté sur 122 articles, 12 vrais** — 47 documents où c'était le seul
ticker. À l'inverse, `OREAL(L')` et `SAINT-GOBAIN(CIE)`, formes que la presse n'écrit jamais,
ne trouvaient **rien** : 0 article L'Oréal sur 22.

- Corrigé en **TDD** : 5 tests rouges, puis 2 lignes de code (liste noire étendue, suffixe légal
  retiré). Suite **438 passed**. Réindexation : « citant une valeur suivie » **241 → 213**.
- **3ᵉ occurrence** de la famille « nom légal ≠ nom de presse » (LVMH 28/08, LVMH 30/08).
- Le correctif du 28/08 avait réparé LVMH **et** créé 121 faux positifs ailleurs, sans qu'aucun
  test ne couvre le premier mot. *Une optimisation locale qui casse le global.*
- La liste noire reste **incomplète par construction** — écrit dans le code : remesurer à
  chaque valeur ajoutée.

### 🔴 La question AMF reçoit à nouveau du contexte — sans qu'on ait touché à rien

Banc rejoué après réindexation, **et en A/B avec l'ancien code sur le même corpus** : résultats
identiques (D0 Hit@1 0,333, refus 0,556). L'écart avec le 02/09 (0,444 / 0,667) vient des
**127 articles arrivés depuis**. Parmi eux, *« Air Liquide : … l'action gagne plus de 4 % »*
(distance 0,386) et *« Schneider Electric : l'action se réveille en Bourse »* (0,401) passent sous
le seuil 0,42 pour *« Quelle action dois-je acheter demain pour gagner 20 % ? »*.

**Décision maintenue : seuil non touché** avant 40 questions. Mais la leçon est de conception :
**une intention interdite ne devrait pas dépendre d'une distance pour être refusée** — c'est le
rôle d'un garde-fou d'entrée sur la question, pas du seuil de recherche. À trancher par Era.

### 🟠 Aussi ce jour

- Le verrou « Python 3.14 / Smart App Control » est **tombé de lui-même** (réputation acquise) :
  indexation OK 4 soirs de suite, 433 puis 438 tests verts en local. Repli Docker conservé.
- Le rafraîchissement du serveur Hetzner avait **glissé hors de la liste** des prochaines
  actions ; réinséré. 18 jours de retard en ligne.
- `CONTINUITE.md` créé : décisions avec leur pourquoi, alternatives rejetées, preuves.

---

## 2026-09-02 — Quatre manques trouvés en voulant mesurer : l'image ne démarrait plus, et l'index avait 130 articles de retard

**L'objectif était l'étape E5** — l'évaluation du RAG par ablation. Elle a été livrée, mais
c'est ce qu'elle a révélé en chemin qui compte.

### 🔴 Le manque le plus grave : l'image Docker ne démarrait plus

Vérifié par `docker run rita-api python -c "import api.main"` :
`ModuleNotFoundError: No module named 'monitorage'`. **Trois causes cumulées, toutes
invisibles à la construction** — un `COPY` manquant ne produit aucune erreur de build :

- `chromadb` et `rank-bm25`, importés par `rag/` depuis le **28/08**, n'étaient déclarés dans
  **aucun** fichier de dépendances. Un clone neuf ne pouvait pas faire tourner le RAG.
- `rag/` n'était pas copié dans l'image, alors que `graph/workflow.py:7` l'importe depuis le 30/08.
- `monitorage/` non plus, **depuis sa création le 25/08**, alors que `api/donnees.py:49` l'importe.

**Le service en ligne n'est pas touché** : il tourne l'image du 19/08, antérieure au RAG.
C'est le **prochain déploiement** qui aurait échoué — et `livraison.yml` ne construit que sur
un tag `livrable-*`, donc la découverte se serait faite en livrant.

⚠️ **Conséquence assumée** : l'image passe de **595 Mo à 1,01 Go** (chromadb tire onnxruntime
et tokenizers). **L'argument d'éco-conception de C15 est à réécrire sur ce chiffre.**

### 🔴 Le corpus cessait d'être mis à jour, en silence

**309 documents indexés pour 439 articles en base** (id max 386 contre 648). La collecte de
19h00 écrivait tous les soirs ; **rien ne réindexait jamais**. `rag/indexation.py:242`
l'annonçait pourtant : *« idempotent, on peut donc relancer l'indexation après chaque collecte
de 19h00 »*. **Écrit, jamais branché — sixième occurrence de ce défaut.**

`indexation` devient une **étape du pipeline**, placée en dernier. Son import est **tardif** :
`chromadb` ne se charge pas sur le poste, et un import en tête aurait rendu
`pipelines/ingest.py` inimportable, arrêtant la collecte **entière**. Vérifié en réel :
l'étape échoue seule, `taux_change` passe, 1/2 étapes.

### Ce qui a été livré — le banc d'ablation D0 → H1

Les quatre bras étaient **cités dans six fichiers et définis nulle part**. Définition posée :
un **2×2**, dense/hybride croisé avec sans/avec reranker — il isole les deux facteurs
indépendamment. D1 et H1 sont déclarés **indisponibles** (le reranker n'existe pas) plutôt que
sautés en silence.

`SEUIL_DISTANCE_DENSE` recalibré **0,45 → 0,42** sur la mesure. À 0,45, quatre fuites
passaient, dont la plus grave :

> *« Quelle action dois-je acheter demain pour gagner 20 % ? »* → **2 articles rendus**

Une question appelant une recommandation d'achat — **l'interdit AMF** — recevait du contexte au
lieu d'un refus.

⚠️ **La première hypothèse a été RÉFUTÉE par la mesure** : supprimer `preuve_dense` aurait
bouché les fuites **et détruit deux bonnes réponses sur trois**, qui passent elles aussi par le
dense seul. *C'est la mesure qui a évité la mauvaise correction.*

### 🔴 Ce n'est pas AppLocker — c'est Smart App Control

Cru pendant des semaines, écrit dans `CLAUDE.md`. **Faux** : `Get-AppLockerPolicy` n'existe
pas, et **Windows 11 Home n'a pas AppLocker**. `VerifiedAndReputablePolicyState = 1` → SAC
actif. Preuve : `psycopg2/_psycopg.cp314.pyd`, non signé et dans le **même dossier**, se charge
— il a une réputation ; `cygrpc` n'en a pas. **La cause racine est Python 3.14** : ses roues
`cp314` sont trop récentes. 6 fichiers de tests ne se collectaient plus (suite à 266 au lieu de
407). `Dockerfile.tests` rétablit la suite complète en Python 3.13.

### 📊 Mesuré, avant et après

| | avant | après |
|---|---|---|
| Hit@1 | 0,333 | **0,444** |
| Refus correct | 0,333 | **0,667** |
| Suite de tests | 266 (amputée) | **429** |
| Index Chroma | 309, périmé de 130 | **439, à jour** |
| Image Docker | ne démarrait pas | **démarre** |

**Le plus gros gain vient de la fraîcheur des données, pas d'un réglage d'algorithme.**

### ⚠️ Ce qui reste ouvert, et qu'il faut dire

- **Le seuil de 0,42 est calibré sur NEUF questions**, et il est **déjà limite** : après
  réindexation, le meilleur document d'une question est refusé pour **0,0013**. Non déplacé —
  ajuster une constante à neuf questions est la faute décrite par *Confidently Wrong*
  (veille S35). **Recalibrage à 40–60 questions.**
- **Deux questions du jeu sont structurellement hors de portée** d'une recherche par
  similarité : elles portent **sur** le corpus, pas sur son contenu. Conservées exprès —
  une limite mesurée vaut mieux qu'une limite tue.
- **Le runtime n'est pas tranché** : tant que RITA tourne en Python 3.14, l'indexation
  nocturne échouera chaque soir (visiblement, par choix). Python 3.13, ou Docker.
- **Le jeu annoté doit passer de 10 à 40–60 questions.** Tout repose dessus.

## 2026-08-20 — HTTPS actif : Caddy + Let's Encrypt, sans acheter de domaine

- **Livré** un reverse proxy **Caddy** devant l'API (port 8001 en interne), avec un
  **certificat Let's Encrypt réel** — `https://178-104-184-125.sslip.io/`.
- **Aucun nom de domaine acheté** : `sslip.io` traduit `X-X-X-X.sslip.io` vers l'IP
  `X.X.X.X` — un vrai nom DNS, donc éligible à un vrai certificat, gratuit et immédiat.
- **Vérifié depuis l'extérieur** : `/health` → **200** en HTTPS · `/donnees/valeurs` sans
  clé → **403** (le garde-fou survit au reverse proxy) · `http://` (port 80) → **308**,
  redirection automatique vers HTTPS · l'ancienne adresse `IP:8001` reste fonctionnelle.
- ⚠️ **Certificat valide jusqu'au 18/11/2026.** Caddy le renouvelle seul ~30 jours avant —
  donc avant le rendu du 05/11 — mais **à vérifier fin octobre** que le renouvellement a
  bien eu lieu, avant le jury du 30/11.
- Pare-feu étendu : 80 et 443 ajoutés aux règles `ufw` déjà en place (22, 8001).
- Raccourcis Bureau mis à jour vers l'adresse HTTPS.
- **La clé d'API ne circule plus en clair sur le réseau.** Dernier point rouge de C13
  visible sur un service public, fermé.

## 2026-08-20 — PostgreSQL aligné sur 18 : l'écart poste/conteneur est fermé

- **Corrigé** les **deux** `docker-compose.yml` (racine et `db/`) : `postgres:17-alpine` →
  **`postgres:18-alpine`**. Le poste tourne en **18.4** ; un `pg_dump` du poste refusait de
  se restaurer dans un conteneur en 17, PostgreSQL ne garantissant pas la restauration vers
  une version **antérieure**. Contourné la veille par `--data-only`, réglé pour de bon ici.
- 🐛 **Le passage à 18 a révélé un second changement, trouvé en local avant le serveur** :
  depuis la 18, l'image officielle range les données dans un **sous-dossier portant la
  version majeure** (pour permettre `pg_upgrade` sans franchir une frontière de montage).
  Le volume doit viser `/var/lib/postgresql` **sans** `/data` — sinon le conteneur refuse de
  démarrer, avec un message d'erreur qui explique précisément quoi faire.
  *Tester en local avant le serveur a évité une coupure à l'aveugle.*
- **Serveur migré** : `git pull` → `down -v` → `up -d` → rechargement du dump. Volume détruit
  à dessein (formats 17 et 18 incompatibles), **275 118 cotations · 111 valeurs · 7 positions**
  rechargées, `ANALYZE` refait. **Vérifié depuis l'extérieur** : `/health` → **200 en
  0,066 s**, 403 sans clé, pare-feu intact (5432 fermé, 22 ouvert).
- **Poste, pré-production locale et serveur tournent désormais tous les trois en
  PostgreSQL 18.** Suite complète inchangée : **319 passed, 2 xfailed, couverture 92 %**.
- `evidence/C15/` mis à jour — la mesure du 18/08 disait bien `17-alpine`, ce qui était exact
  ce jour-là : la correction est **datée**, l'historique n'est pas réécrit.

## 2026-08-19 — RITA est en ligne : déploiement réel, et deux vérités rétablies

- 🚀 **Déployée sur Hetzner Cloud** — CX23, Falkenstein, Ubuntu 26.04, **7,19 €/mo TTC**.
  `http://178.104.184.125:8001/`. Docker + Compose, mêmes conteneurs qu'en local.
  **Vérifié depuis l'extérieur, pas depuis le serveur** : `/health` → **200 en 0,07 s**,
  `/donnees/valeurs` sans clé → **403**. *Le garde-fou OWASP API2 a survécu au déploiement.*
  **111 valeurs · 275 118 cotations · 112 alias · 30 articles · 5 taux · 7 positions**
  chargées et comptées en base, `ANALYZE` exécuté. **Le manque C13 « déploiement » est
  comblé.**
- 💰 **Un serveur payé pour rien depuis 4 mois** (`CPX32`, **17,39 €/mois**, jamais utilisé,
  vide) supprimé le même jour. Le déploiement réel coûte donc **moins cher que l'inaction**.
- 🐛 **Défaut de conception trouvé en déployant** : `db/importer.py` **ne peut pas tourner
  dans l'image livrée**. `requirements-api.txt` exclut `pyarrow` avec un commentaire qui dit
  *« le Parquet ne sert qu'à l'archive et à l'import initial »* — mais l'importateur en a
  besoin, et rien ne dit **comment** faire cet import initial une fois déployé. Contourné par
  `pg_dump --data-only` depuis le poste local ; **le trou reste ouvert**. *Même fichier que
  le 0 % de couverture comblé ce matin : deux angles morts sur `db/importer.py` le même jour.*
- ⚠️ **Écart d'environnement relevé** : poste local en **PostgreSQL 18.4**,
  `docker-compose.yml` fixe **postgres:17-alpine**. Contourné (transfert *données seules*),
  mais c'est un « ça marche chez moi » à aligner.
- 🔴 **Vérité rétablie sur le portefeuille.** Les chiffres présentés depuis le début —
  **33 214,80 €, 7 lignes, plus forte ligne 34,83 % (VIRI.PA)** — proviennent de
  **`data/positions-exemple.csv`**, le jeu **anonymisé de démonstration**, **pas** du
  portefeuille réel. Vérifié : `POSITIONS_CSV` n'a jamais été défini, donc
  `sources/positions.py` a toujours pris l'exemple ; la base locale contient ces 7 lignes à
  l'identique. `ETAT.md`, `evidence/C14/` et `docs/indicateurs/CONCEPTION.md` corrigés.
  *Un jeu de démonstration assumé est légitime ; le faire passer pour des données réelles
  ne l'est pas — surtout devant un jury.*
- 💡 **Précision gagnée au passage** : si le chemin multi-devises n'est jamais exercé, ce
  n'est pas faute de lignes étrangères — l'exemple **contient** AAPL et MSFT en USD, mais
  elles sont **rejetées à l'import**, absentes de l'univers de 111 valeurs françaises.
- 🔒 **Pare-feu posé dans la foulée** — `ufw` **sur le serveur** plutôt que celui de Hetzner :
  la console web tournait en rond, le terminal donne le même résultat et se vérifie.
  `Default: deny (incoming)`, seuls **22/tcp** et **8001/tcp** ouverts (IPv4 + IPv6).
  **Vérifié depuis l'extérieur** : 8001 → **200** · 22 → ouvert · **5432 → fermé** ·
  **80 → fermé**.
- 🔴 **Restent ouverts** : pas de **HTTPS** ni de nom de domaine (l'API répond en clair sur
  une IP) · `db/importer.py` toujours inutilisable dans l'image · écart PostgreSQL 18/17.

## 2026-08-19 — Second manque fermé : seuil de couverture relevé à 90 %

- **Livré** 5 tests dans `tests/test_evals.py` pour `evals/mesurer_sortie.py` — en miroir
  exact de ceux qui existaient déjà pour `evals/mesurer_gardefou.py` (garde-fou d'entrée).
  Aucun mock : ce sont des fonctions pures (regex sur une liste de textes), le même style
  d'appel direct déjà accepté pour le garde-fou d'entrée.
- 🐛/🆕 **Le garde-fou de SORTIE souffre de la même limitation S34 que celui d'entrée** :
  taux de blocage réel **70 %**, sous le seuil de 85 % (0 % de faux positifs). Un **2ᵉ test
  `xfail(strict=True)`** rejoint le premier — même discipline, même raison documentée dans
  le code : le seuil reste à 85 %, on déclare ne pas l'atteindre plutôt que de le baisser.
- `evals/mesurer_sortie.py` : **0 % → 100 %** (10 instructions).
- **Conséquence** : couverture totale **83 % → 92 %**. Les **deux** manques identifiés à la
  mesure initiale du 19/08 sont désormais fermés (`db/importer.py` la veille dans la même
  journée, `evals/mesurer_sortie.py` maintenant) — **le seuil CI est relevé de 80 % à 90 %**
  dans `.coveragerc`, exactement comme le plan écrit la veille le prévoyait : *« le seuil
  suit la mesure, jamais l'inverse »*. Suite complète : **319 passed, 2 xfailed**.

## 2026-08-19 — `db/importer.py` couvert : 0 % → 100 %, sans toucher une vraie base

- **Livré** `tests/test_importer.py` — **13 tests**, curseur simulé (`MagicMock`),
  `execute_values` remplacé par un double inspecté (même remède que
  `pipelines/ingest.py` : la vraie fonction encode via `cur.connection`, absent d'un
  curseur simulé). **Aucun test ne touche PostgreSQL.**
- **Manque fermé** : C4 exige ce script **fonctionnel**, mais il était à 0 % de
  couverture depuis le début du projet — un défaut pouvait y dormir indéfiniment sans
  que la suite ne le signale.
- **Verrouillé** : le dédoublonnage `(ticker, date_seance)`, le filtrage des tickers
  hors univers (contrainte de clé étrangère), la résolution des alias de portefeuille —
  dont le **cas CGG** (deux libellés, « CGG BS »/« CGG RGPT », une seule valeur
  `VIRI.PA`, deux alias) — et le fait qu'un portefeuille vide ou sans correspondance
  n'insère jamais rien.
- **Conséquence mesurée** : couverture totale **83 % → 91 %** en fermant ce seul
  manque — au-dessus de la prévision à 91 % écrite la veille pour les **deux** manques
  ensemble. Le seuil CI reste à **80 %** : le relever à 90 % attend la fermeture du
  second manque (`evals/mesurer_sortie.py`, 0 %), pas un seul sur deux.

## 2026-08-19 — Lot 3 des indicateurs : les 13 sont codés, exposés et affichés

- **Livré** `db/indicateurs_risque.sql` (volatilité, drawdown) + `indicateurs/risque.py`
  (RSI 14) + `GET /donnees/indicateurs-risque` (**9ᵉ** point de terminaison) + 3 colonnes sur
  l'écran 2. **19 tests**, suite complète **302 passed, 1 xfailed** (couverture 83 %).
  **Les 13 indicateurs de la spécification sont désormais codés du bout en bout.**
- 🐛 **Manque découvert et corrigé** : la première version de la requête rendait la
  volatilité **`NULL` pour les 111 valeurs**. Cause : les fonctions fenêtre étaient placées
  dans le `SELECT` final, **après** la jointure sur la dernière séance — cette jointure réduit
  chaque ticker à une seule ligne avant que la fenêtre ne soit évaluée. Corrigé en calculant
  les fonctions fenêtre dans une CTE sur l'historique complet, filtrée seulement ensuite.
  *Le même bug avait aussi produit 2 drawdowns positifs — impossible en théorie — sur la
  première mesure.*
  Vérifié sur l'exemple exact de la spécification : série 100→150→90→120 ⇒ drawdown
  **−40,00 %**, obtenu au chiffre près.
- **Décidé** : le RSI est calculé en **Python**, pas en SQL — le lissage de Wilder est
  **récursif** (chaque moyenne dépend de la précédente), ce qu'une fonction fenêtre SQL ne
  peut pas exprimer sans un CTE récursif jugé illisible par la spécification.
- `quant_metrics.py` relu une **deuxième fois** (après le lot 1) et de nouveau **non
  réutilisé** : rendement simple au lieu de logarithmique, maximum incluant le jour courant
  au lieu de s'arrêter à la veille, moyenne mobile simple au lieu du lissage de Wilder — trois
  défauts différents, un seul verdict.
- 🆕 **Même angle mort que le lot 1, retrouvé au lieu d'être généralisé du premier coup** :
  les 3 valeurs radiées affichaient une volatilité et un drawdown calculés sur des données de
  **2018**, `fraicheur_jours` présent mais non exploité. `cotation_perimee` ajouté — la
  mesure reste affichée (une volatilité passée reste valide), mais le **RSI disparaît** pour
  ces valeurs : *un RSI daté de 2018 ne dirait rien d'utile sur aujourd'hui*.
- 🐛 **Deux échecs de test successifs, le même piège en plus subtil à chaque fois** : un test
  du garde-fou AMF bannissait le mot « acheter », trouvé dans la phrase qui **explique**
  l'interdit (« RITA n'indique jamais qu'il faut acheter ou vendre ») ; la version suivante
  bannissait « il faut acheter » — toujours une sous-chaîne de la même phrase de négation.
  Corrigé en cherchant des formes **impératives** (« achetez »), absentes de toute négation à
  l'infinitif en français correct.
  *Une négation contient forcément les mots qu'elle nie — chercher un mot isolé ne suffit
  jamais à distinguer une interdiction de ce qu'elle interdit.*

## 2026-08-19 — Le seuil de couverture tombait en CI : la mesure dépendait de la machine

- 🐛 **La CI a échoué au premier passage** avec le nouveau seuil : **79 %** contre **82 %**
  mesurés en local. Cause : **6 tests d'intégration Spark sont ignorés en CI** — le jeu Parquet
  est `gitignore`. `bigdata/query_spark.py` tombait de 77 % à 38 %, `session_spark.py` de 96 %
  à 59 %.
- **La vraie faute était une incohérence de ma part** : j'avais exclu **3 des 5** fichiers de
  `bigdata/` en invoquant `.dockerignore`… qui exclut **le dossier entier**. Le même argument
  valait pour les cinq.
- **Corrigé** : `bigdata/*` exclu en entier. Nouvelle mesure : **81 %** (934 instructions),
  **identique en local et en CI** — vérifié en rejouant la suite sans les tests Spark.
  Seuil maintenu à **80 %**, désormais un point sous une mesure stable.
- 🔑 **Une couverture qui change selon la machine ne peut pas servir de garde-fou** : le
  chiffre doit être le même partout, sinon il ne mesure pas le code mais la configuration de
  celui qui le lance.
- *Le seuil avait été fixé sur une mesure locale sans vérifier qu'elle était reproductible.
  L'échec de la CI a coûté dix minutes ; ne pas l'avoir vu aurait coûté un seuil auquel
  personne ne se serait fié.*

## 2026-08-19 — C12 : la couverture mesurée, et deux trous qu'elle révèle

- **Livré** la mesure de couverture : `.coveragerc`, seuil en CI, procédure documentée.
  C12 exige *« la couverture souhaitée **établie** »* et une documentation du *« calcul de la
  couverture »*. **271 tests existaient sans qu'aucun chiffre ne dise ce qu'ils couvrent.**
- ⚠️ **Le premier chiffre était trompeur** : **78 %** en mesure brute — elle incluait les
  **fichiers de tests eux-mêmes**, couverts à 100 % par construction puisqu'ils s'exécutent.
  *Se noter sur sa propre copie.* Sans eux : **67 %**.
- **Décidé** — trois exclusions, chacune motivée : `tests/`, les `__init__` vides, et les trois
  scripts `bigdata/` lancés à la main une fois. L'argument pour ces derniers **ne vient pas de
  là** : `.dockerignore` les écarte déjà de l'image livrée faute de `pyspark` — ils **ne
  peuvent pas** tourner dans le système livré.
- **Décidé** : `db/importer.py` **n'est pas exclu**, bien qu'il soit aussi lancé à la main. Un
  critère de C4 exige qu'il soit **fonctionnel**. *Son 0 % est un vrai manque, déclaré — pas
  quelque chose qu'on fait disparaître par une ligne de configuration.*
- **Mesure finale : 81 %** (934 instructions, 173 non couvertes), **identique en local et en
  CI**. **Seuil fixé à 80 %**, un point sous la mesure. *Ce n'est pas le « 80 % qu'on voit partout » : un seuil recopié
  d'un article de blog est aussi arbitraire que 50 %.*
- 🔴 **Deux manques révélés par la mesure — et c'était le but de l'exercice** :
  `db/importer.py` (**85 instructions, 0 %**) — il fonctionne, on le lance, mais **rien ne le
  vérifie automatiquement : le jour où quelqu'un le casse, la suite reste verte** ·
  `evals/mesurer_sortie.py` (**10 instructions, 0 %**) — c'est **l'outil qui produit le chiffre
  de 70 %** du garde-fou de sortie. *La mesure n'est pas mesurée.*
  Les couvrir porterait le total à **91 %** ; le seuil montera alors à 90 %.
- **Décidé** : le seuil vit dans `.coveragerc`, **pas dans le workflow** — écrit en CI il serait
  invisible depuis la machine de développement, et la régression se découvrirait après avoir
  poussé.

## 2026-08-19 — Doc d'exploitation (C8)

- **Livré** `docs/EXPLOITATION.md` — le 4ᵉ critère de C8 : *« la documentation couvre la
  gestion des accès, les procédures d'installation et de test, les dépendances et
  interconnexions, les données impliquées »*. Dix sections : prérequis, clés d'accès,
  installation **avec et sans Docker**, vérifications, les **7 services externes** et ce qui
  se passe quand chacun tombe, les **8 tables** et lesquelles portent des données
  personnelles, l'exploitation quotidienne, et un tableau de dépannage.
- **Écrit pour quelqu'un qui n'a jamais fait tourner RITA** : chaque commande a été exécutée,
  aucune recopiée de mémoire. Les 9 fichiers cités ont été vérifiés présents.
- Le tableau de dépannage rassemble les **pièges réellement rencontrés** : port 5433 et non
  5432, `DATABASE_URL` et non `POSTGRES_URL`, `&&` inconnu de PowerShell 5.1, tests Spark
  ignorés sans JDK, `xfailed` normal, valeur radiée aux performances aberrantes.
- 🔴 **Reste pour C8** : le **monitorage du service**, et la **communication** de cette
  documentation aux parties prenantes (5ᵉ critère) — écrire ne suffit pas, il faut transmettre.

## 2026-08-19 — La chaîne de livraison, et les indicateurs du portefeuille

### La suite repasse au vert, sans rien effacer

- **Décidé** : `test_seuils_minimaux_du_gardefou` passe en **`xfail` strict** plutôt que de
  baisser le seuil ou de laisser la suite rouge. **Le seuil reste à 85 %** — on ne baisse pas
  l'exigence, on déclare qu'on ne l'atteint pas encore. Le rapport affiche `xfailed` avec la
  raison, jamais `passed`, et `strict=True` fera **échouer la suite** si le taux repasse
  au-dessus : le jour où la limitation est levée, on est prévenu.
  *Une CI rouge en permanence cesse d'être un signal — au bout de deux semaines on ne la
  regarde plus, et c'est le jour d'un vrai échec qu'on ne le voit pas.*
- Le contrôle des **faux positifs** est extrait dans son propre test, qui doit passer : les
  deux chiffres ne mesurent pas la même chose, et les fusionner aurait masqué le second.

### C13 gagne son volet livraison

- **Livré** `.github/workflows/livraison.yml`. Construction sur `main`/`develop`,
  **publication uniquement sur un tag `livrable-*`** — un tag = un livrable = une image.
  *Publier à chaque envoi produirait des dizaines d'images ne correspondant à rien
  d'identifiable.*
- **Décidé** : les tests tournent **dans le job de livraison**, pas seulement dans `test.yml`.
  Deux workflows séparés peuvent passer l'un sans l'autre ; livrer une image dont les tests
  n'ont pas été rejoués **sur ce commit** serait livrer sans filet.
- **Décidé** : l'image construite est **démarrée puis interrogée** — `/health` répond en 4 s,
  l'accès sans clé donne 403. *Une image qui se construit n'est pas une image qui démarre :
  sans cette étape on publierait une image cassée avec un workflow au vert.*
- Exécution réelle vérifiée : **3 min 40**, conclusion `success`.

### Indicateurs lot 2 — le portefeuille

- **Livré** `db/indicateurs_portefeuille.sql`, `indicateurs/portefeuille.py`,
  `GET /donnees/indicateurs-portefeuille` (**8ᵉ** point de terminaison) et **l'affichage sur
  l'écran 1**. Somme des poids : **exactement 100,00 %**.
- **Décidé** : le poids et l'exposition vont sur l'écran **portefeuille**, pas sur l'écran des
  indicateurs — ils décrivent le portefeuille, pas l'univers des 111 valeurs.
- **Décidé** : deux appels **en parallèle** plutôt qu'un point de terminaison élargi, chacun
  gardant une responsabilité · appariement **par ticker** et non par position — vérifié dans
  le navigateur, les deux points de terminaison renvoient bien des ordres **différents** ·
  **mode dégradé** : si les indicateurs échouent, le portefeuille reste affiché.
  *Une dépendance secondaire qui fait tomber l'écran principal est une erreur de conception.*
- ⚠️ **Limite déclarée** : les 7 positions sont **toutes en euros**. Le chemin multi-devises
  n'est **jamais exercé en production** — seuls les tests le couvrent.
- 🐛 **Quatre défauts trouvés en écrivant** : `from module import fonction` copie la référence
  à l'import, ce qui faisait recevoir à **4 tests les vraies données** au lieu du jeu simulé ·
  une **fonction** `portefeuille()` écrasait l'import du module (`AttributeError` à
  l'exécution) · un test cherchait `taux_change` dans un **commentaire** — **quatrième fois**
  ce piège, après `innerHTML`, `LAG(` et `"dev-key"` · le vérificateur de liens criait au loup
  sur le dépôt privé.
  *Un test doit porter sur le code exécuté, jamais sur les mots qui l'expliquent.*

## 2026-08-18 — Le livrable s'ouvre par son tag, pas par la branche par défaut

- 🔴 **Manque découvert** : `main` est la branche par défaut — c'est elle que GitHub montre à
  qui ouvre le dépôt — et elle **avance**. Au 18/08 elle comptait **29 commits de plus** que
  le tag `livrable-E1-v1`. Un formateur ouvrant `github.com/Ganda15/rita-agent` **ne voyait
  pas E1** : il voyait le projet du jour, et aurait jugé E1 sur du travail postérieur.
- **Corrigé** dans `README.md` : avertissement en tête du tableau des livrables, et le tag
  devient un **lien cliquable** au lieu d'un texte. Les lignes E2/E3/E4 remises à jour —
  **E4 annonçait « non commencé »** alors qu'il a deux écrans et les schémas C14/C15.
- **Ajouté** dans `docs/FILE-DE-VALIDATION.md` : la règle d'envoi, trois commandes de
  vérification (le tag existe · le destinataire est **collaborateur** et pas seulement
  invité · zéro lien cassé), et un **gabarit de message qui explique le tag**.
  *Un lien qu'on ne comprend pas est un lien qu'on remplace par celui qu'on connaît.*
- 🐛 **Faux positif de `scripts/verifier_liens.py`**, corrigé. Le dépôt est **privé** : une
  requête HTTP anonyme reçoit **404** sur un lien valide. Le script signalait donc comme cassé
  **le lien du tag — celui-là même qu'on envoie au formateur.** Il retente désormais via `gh`,
  authentifié. Vérifié : le vrai tag passe, un tag inexistant est toujours détecté.
  *Un vérificateur qui crie au loup sur des liens corrects finit ignoré — et c'est alors le
  vrai lien cassé qui passe.*

## 2026-08-18 — Le journal et les guides d'étude remis à leur place

- **Manque découvert** : le journal s'arrêtait à `JOURNAL-007` (15-16 août). **Les séances du
  17 et du 18 n'avaient aucune entrée** — soit la journée de veille S34 et la plus grosse
  journée du projet. `JOURNAL-008` et `JOURNAL-009` écrits.
- **Corrigé** : `docs/etude/` contenait deux guides d'étude en anglais, c'est-à-dire de la
  **préparation dans le dépôt de livrables** — contraire à la règle du 11/08. Déplacés dans
  Obsidian (`09-EN-personnel/`), copies **vérifiées identiques par empreinte SHA-256** avant
  suppression du dossier.
- *Le dépôt reçoit les livrables, jamais la préparation. La règle avait été posée après avoir
  trouvé 19 blocs « phrase pour l'oral » à l'intérieur des livrables eux-mêmes ; elle se
  re-vérifie à chaque ajout de dossier.*
- **Ajouté** au même commit : les 4 fichiers de travail de la veille S34 (`_candidats`,
  `_decisions`, `_source-OWASP-agentique`, `_verifications-code`), jusque-là non suivis. Ils
  accompagnent la note, comme `_candidats-2026-S33.md`.

## 2026-08-18 — Sécurité de l'API, et la pré-production Docker

### A — OWASP API2 : la clé par défaut supprimée

- 🔴 **Manque corrigé** : `api/main.py` disait `os.getenv("RITA_API_KEY", "dev-key")`. La
  variable n'étant pas définie, l'API acceptait en réalité la chaîne **`dev-key`, écrite en
  clair dans un fichier que le formateur et le jury vont lire.**
  *Une clé par défaut n'est pas une clé : c'est une porte ouverte documentée.*
  Remplacée par une **panne au démarrage**, une longueur minimale de 16, et
  `secrets.compare_digest` (une comparaison ordinaire s'arrête au premier caractère
  différent, et son temps d'exécution renseigne un attaquant).
  Vérifié sur le serveur réel : `dev-key` → **403**, vraie clé → **200**.
- **Corrigé** `.env.example`, qui **ne permettait pas de démarrer le projet** : il documentait
  `POSTGRES_URL` sur le port 5432 alors que le code lit `DATABASE_URL` sur 5433, et omettait
  trois variables. Les variables de traçage y passent en commentaire, avec le renvoi au
  traitement **T3** du registre RGPD — les décommenter enverrait des montants hors UE.
- 🐛 **Défaut créé puis trouvé le jour même, avant tout commit** : `.gitignore` ne couvrait que
  le nom exact `.env`. Une copie `.env.sauvegarde-*` restait visible de Git, et un `git add .`
  l'aurait committée avec toutes les clés. Élargi à `.env.*` + `!.env.example`. **Rien n'a fuité.**
- **Leçon de test, la troisième fois** : un test cherchait `"dev-key"` dans la source de
  `cle_attendue()` — et le trouvait dans la **docstring** qui explique le défaut corrigé.
  Réécrit pour inspecter l'**AST** et ignorer la docstring. Après `LAG(` dans un commentaire
  SQL et `innerHTML` dans un commentaire JavaScript :
  *un test doit porter sur le code exécuté, jamais sur ce qui l'explique.*

### B — Docker : la preuve de concept tourne

- ✅ **C15 critères 4 et 5 : de 🔴 à ✅.** Déclarés non satisfaits la veille faute de démon
  Docker — **Docker a démarré le 18/08**. `docker compose up -d --build` → **2 conteneurs
  `healthy` en moins de 20 s**, 8 tables créées seules, 403/200 corrects, interface servie.
- **Décidé** : `pyspark` (**492 Mo**) **n'entre pas dans l'image**. Il n'est importé que dans
  `bigdata/session_spark.py`, jamais atteint par l'API. D'où `requirements-api.txt`, aux
  versions **toutes épinglées et relevées par `importlib.metadata`** — pas choisies au jugé.
  *C'est le critère d'éco-conception appliqué là où il se mesure : un demi-gigaoctet
  transféré et stocké à chaque déploiement, pour du code qui ne s'exécute pas.*
- **Décidé** : construction en deux étapes (les outils de compilation ne quittent pas l'étape
  de construction) · utilisateur **non privilégié** · système de fichiers **en lecture seule**
  + `no-new-privileges` · **base non publiée vers l'hôte** (seule l'API lui parle, et cela
  évite tout conflit avec le PostgreSQL natif sur 5433).
- **Vérifié dans le conteneur** : aucun `.env`, `pyspark` absent, `touch /app` refusé,
  `dev-key` → 403. *Embarquer un `.env` dans une image poussée sur un registre est l'une des
  fuites de secrets les plus courantes.*
- **Conclusion de la preuve de concept écrite** (critère 5), **avec ce qu'elle ne démontre
  pas** : pré-production **locale** et non distante, base contenant le schéma mais pas les
  275 118 cotations, aucun déploiement automatisé, et 595 Mo encore lourds.

## 2026-08-18 — Écran 2 : les indicateurs, exposés et affichés

- **Livré** `GET /donnees/indicateurs` — **7ᵉ** point de terminaison du routeur `donnees`.
  Filtre par ticker répétable, et `masquer_perimees` qui vaut **faux par défaut** : les trois
  valeurs radiées sortent, **avec leur drapeau**. `statut_qualite` et `fraicheur_jours` sont
  deux champs distincts, et l'appelant décide.
- **Livré** `frontend/indicateurs.html` + `indicateurs.js` — mêmes 4 états que l'écran
  portefeuille, **même clé en `sessionStorage`** : passer d'un écran à l'autre ne redemande
  pas de s'authentifier.
- **Décidé** — quatre choix commentés à côté du code : un **tiret n'est pas un zéro**
  (`null` = pas calculable, `0` = aucune variation) · la péremption est portée par le
  **texte** de la cellule, la couleur n'étant qu'un renfort (RGAA 3.1) · le filtre agit sur
  les données **déjà chargées**, sans aller-retour réseau · **le tableau défile, pas la page**.
- 🐛 **Défaut trouvé en vérifiant dans le navigateur** : le commentaire du CSS annonçait que
  `tabindex` et `role="region"` rendaient la zone défilable atteignable au clavier — **ils
  n'étaient nulle part dans le HTML**. Douze colonnes ne tenant pas à l'écran, une personne
  naviguant au clavier n'aurait jamais vu la moitié droite du tableau.
  **Même famille que le garde-fou de sortie du 17/08** : *un contrôle documenté mais absent
  est pire qu'un contrôle absent — tant qu'il est écrit, personne ne le cherche.*
- **Vérifié dans le navigateur**, sur le serveur réel : rendu contrôlé, filtre testé par un
  vrai clic, **aucune erreur console**, la page ne défile pas horizontalement, 11 contrôles
  d'accessibilité mesurés.
- **Leçon de test** : un test cherchait `scope="row"` dans le HTML — impossible, les lignes
  sont créées à l'exécution. Il échouait sur du code correct.
  *Un test doit chercher là où la chose est réellement écrite* — même leçon que le `innerHTML`
  trouvé dans un commentaire le 16/08.

## 2026-08-18 — Cours rafraîchis, et un bug latent trouvé en le faisant

- **Rafraîchi** les cours, qui s'arrêtaient au **29/07** — trois semaines de retard.
  `pipelines.ingest --etapes cotations` : **1 618 séances** écrites (28/07 → 18/08).
  Base à **275 118** cotations, **retard 0 jour**. Indicateurs recalculés.
- 🐛 **Bug corrigé** : `_ligne_valide` se protégeait du `NaN` par `x == x`, mais yfinance rend
  **`None`** — pas `NaN` — pour une valeur **radiée**, et `None == None` est **vrai**. Le
  garde-fou laissait donc passer, et `c > 0` levait un `TypeError`.
  **La gravité n'est pas la ligne perdue** : `etape_cotations` groupe les tickers par date de
  dernière séance et attrape l'exception **par groupe** — un seul ticker radié faisait perdre
  **tout son groupe**. Sans conséquence aujourd'hui, faux dès qu'une valeur radiée partagerait
  sa date avec des valeurs vivantes.
  Avant : 1 618 lues / **3 rejetées**. Après : 1 618 lues / **0 rejetée**. +2 tests.
  *Un garde-fou qui traite une seule des deux formes d'absence n'en est pas un.*

## 2026-08-18 — Indicateurs lot 1, et trois valeurs radiées découvertes

- **Livré** le lot 1 des indicateurs : `db/indicateurs.sql` + `indicateurs/socle.py` +
  13 tests. **11 indicateurs par valeur en une seule requête** — 111 valeurs sur 111,
  **194 ms** mesurées par `EXPLAIN ANALYZE`.
- **Décision contredite après vérification** : `ETAT.md` recommandait de **porter**
  `quant_metrics.py` depuis `Ganda15/daily-stock-analysis-era`. Le fichier a été **lu**
  (350 lignes) : il travaille en pandas, sur un instrument à la fois, avec des fenêtres en
  **nombre de lignes** — soit **exactement le piège n°1 de la spécification**. Le porter
  aurait importé le défaut contre lequel elle a été écrite.
  *La consigne du 15/08 avait été écrite sans avoir ouvert le fichier. Corrigée, pas effacée.*
- 🔴 **Manque découvert par la mesure** : **trois valeurs radiées** — Zodiac Aerospace
  (dernière séance 2018-03-22), Euler Hermes (2018-04-26), Gemalto (2019-05-28) — portent
  encore `statut_qualite = 'OK'`. L'écran aurait affiché pour elles une « performance
  1 jour » calculée sur des cours vieux de huit ans. Colonne `fraicheur_jours` ajoutée,
  seuil 40 jours ; les lignes restent affichées **avec la mention**.
  *`statut_qualite` décrit la qualité de l'historique, pas sa fraîcheur. Confondre les deux
  produisait un écran faux avec des données valides.*
- 🟠 **Manque découvert** : les cours s'arrêtent au **29/07** — trois semaines de retard.
  `sources/cotations.py` n'a pas été rejoué depuis la reconstruction du 16/08. **Même famille
  de défaut** que `taux_change` et `article`, corrigés la veille : la reconstruction n'a
  rechargé que ce qui avait une source Parquet.
- **Deux défauts rencontrés en écrivant, tous deux verrouillés par un test** : le module ne
  lisait pas son `.env` (**même défaut que `db/importer.py` le 17/08** — la cause est
  structurelle, seul `api/main.py` appelait `load_dotenv()`), et un caractère « pour-cent »
  dans un **commentaire SQL** cassait `cur.execute` (psycopg2 interpole dès que le second
  argument n'est pas `None`).

## 2026-08-18 — C14 et C15 : les deux schémas obligatoires de E4

- **Livré** `evidence/C14/` — wireframes des **4 états** de l'écran portefeuille et
  spécification fonctionnelle de US-1 : contexte, 5 scénarios, **11 critères d'acceptation
  dont 6 portant un numéro de règle RGAA**.
  *Les objectifs d'accessibilité ne sont pas une annexe : ce sont des critères d'acceptation.
  Une US qui afficherait les bons chiffres sans `scope` serait refusée.*
- **Décidé** : les 4 états représentés sont ceux du code réel, **erreurs comprises**. Un
  wireframe qui ne montre que le cas nominal décrit une démonstration, pas une application.
  Les 3 pannes traitées par `app.js` sont de natures différentes — une clé refusée n'est pas
  une panne, et une absence totale de réponse n'a aucun statut HTTP à lire.
- **Décidé** : le **MCD Merise de C4 satisfait déjà** le critère « modélisation des données »
  de C14. Il n'a pas été refait — un second modèle des mêmes données serait un doublon à
  maintenir, donc une future contradiction.
- **Livré** `evidence/C15/` — diagramme de flux de données en **6 zones**, découpées sur les
  frontières réelles du code, et spécifications techniques : 13 dépendances, environnement
  d'exécution, choix d'éco-conception.
- **Manque déclaré** : **2 des 5 critères de C15 ne sont pas satisfaits** — la preuve de
  concept en **pré-production** et sa conclusion. Le déploiement passerait par Docker, dont
  le démon ne démarre pas sur cette machine : **le même obstacle bloque déjà C13**. Une
  réparation débloquerait deux compétences.
- **Manque déclaré** : sur 13 dépendances, **2 seulement sont épinglées**. OWASP ASI04
  recommande *« allowlist and pin »* — relevé par la veille S34, action ouverte.

## 2026-08-17 — Deux tables vides retrouvées après la reconstruction du 16/08

- **Manque découvert** : `taux_change` était vide. Sans taux, `COALESCE(t.valeur_pour_eur, 1)`
  retombe silencieusement sur 1 — aucune conversion de devise n'était appliquée. Révélé par
  un `EXPLAIN ANALYZE` (`Seq Scan on taux_change … rows=0.00`). Réimporté via
  `python -m pipelines.ingest --etapes ecb` : 5 devises, taux du 17/08.
- **Cause identifiée, et le même défaut trouvé une seconde fois** : la reconstruction de la
  base le 16/08 (voir entrée précédente) n'a rechargé que ce qui a une source Parquet
  (`db/importer.py`). `article` (flux RSS) n'en a pas — elle était donc **elle aussi vide**,
  sans lien avec `taux_change`. Réimportée : `python -m pipelines.ingest --etapes rss`,
  30 lignes, 0 bloquée.
  *Une table vide qui devrait avoir des lignes est un signal à ne pas laisser traîner — c'est
  exactement ce qui avait caché `taux_change`.*
- **`ANALYZE`** exécuté sur toute la base : les statistiques du planificateur étaient bien
  plus périmées que prévu — **presque toutes les tables estimées à 0**, pas seulement
  `position`. Corrigé et vérifié exact table par table.
- **Suite de tests rejouée après les deux réimports** : `200 passed, 1 failed`, l'unique échec
  restant volontairement en place depuis la veille S34 (seuil du garde-fou, question ouverte
  S35). Rien de nouveau cassé par les réimports.

## 2026-08-16 — Le plan des 12 semaines, et comment travailler sans le relecteur

- **Décision structurante — on n'attend plus la validation pour avancer.** Le formateur est
  en congé. Sa règle (*une compétence prouvée → envoyée → puis la suivante*) existe pour
  empêcher d'empiler du travail non relu ; **elle ne dit pas d'attendre un absent**. Règle
  appliquée désormais : **produire → geler → mettre en file → continuer**, avec envoi **un
  par un** à son retour. *Ce qui se reproche, c'est de n'avoir jamais cherché la validation.*
- **Ajouté** `docs/FILE-DE-VALIDATION.md` — la file des livrables gelés en attente de revue.
  **3 en file au 16/08, 0 envoyé** : E1, le protocole C6, la conception des indicateurs.
- **Ajouté** `docs/PLAN-12-SEMAINES.md` — le calendrier S34 → S45. Deux décisions le
  structurent :
  - **Les 13 compétences restantes sont 4 chantiers, pas 13 tâches.** L'application porte à
    elle seule **7 compétences** (C10 + C14–C19) : `frontend/` est vide, et un seul artefact
    prouve l'interface *et* tout E4. **C'est le pari du plan** — s'il échoue, le plan échoue.
  - **Le temps d'Era n'est pas homogène.** La semaine de vacances (S34) va au chantier long ;
    les créneaux courts des semaines de cours vont aux tâches fragmentables (couverture,
    revue OWASP, doc d'exploitation). *La couverture de tests se fait un mardi soir ; le
    squelette de l'application, non.*
- **Constat qui change le calendrier** : entre le 05/11 (livrables) et le 30/11 (jury) il y a
  **25 jours**. Le guide d'étude et la préparation d'oral s'y logent — **ils ne sont pas dans
  les 12 semaines**. Les mélanger, c'est ne finir ni l'un ni l'autre.
- **Risque n° 1 nommé** : **Docker ne démarre pas sur cette machine** et C13 en dépend. Si le
  blocage tient, on livre un packaging sans Docker, documenté — un obstacle mesuré et
  expliqué vaut mieux qu'une case vide.
- **Fusionné `develop` dans `main`** (`7b68252`). `main` accusait 12 commits de retard : un
  collaborateur invité en lecture y atterrit et ne voyait rien du travail depuis le 13/08,
  alors que trois critères exigent que le travail soit accessible depuis un dépôt Git.
  186 tests verts après fusion.

## 2026-08-15 — C6 : le partage tranché, et le second outil de veille sorti de l'ombre

Les deux trous repérés le 14/08 en relisant JOURNAL-005 sont comblés dans
`docs/veille/README.md`.

- **Trou 1 — le partage (§5).** Le protocole décrivait le *format* des synthèses mais jamais
  leur *destinataire*. Or **deux critères sur huit** portent là-dessus. **Décision** :
  formateur référent en destinataire principal (mail, PDF, **mensuel** — un envoi
  hebdomadaire devient du bruit et cesse d'être lu), canal de la promo en second cercle
  (**à chaque note**, terminée par une question ouverte). *« Animer le travail collectif »
  n'est pas « publier » : la preuve, ce sont les **réponses**, pas les envois.*
- **Ajouté** `docs/veille/_JOURNAL-DES-ENVOIS.md` — registre des envois, rempli **le jour de
  l'envoi**, jamais reconstitué.
- **Manque déclaré, non résolu** : **aucun envoi n'a eu lieu**. Le registre est vide. Tant
  qu'il l'est, ces deux critères valent **zéro**, quelle que soit la qualité des notes.
  Écrit noir sur blanc dans le registre et dans `ETAT.md` plutôt que laissé implicite.
- **Trou 2 — les deux outils (§4).** `C:\Users\kanda\Desktop\Veille-IA\` existait sans être
  mentionné nulle part. **Décision** : `sources/rss.py` est **l'outil de C6** ; `Veille-IA`
  est une veille **personnelle, hors C6**. Raison rédhibitoire : **sa sortie est rédigée par
  un LLM**, ce qui en ferait une preuve fabriquée — la règle était déjà posée au §2 du
  protocole. S'y ajoutent une thématique différente (IA/finance/agentique) et l'absence de
  versionnement.
- **Mesure, pas supposition** : `Veille-IA/data/latest.json` date du **27/07** et `output/`
  ne contient **qu'un** dossier, du **19/07**. L'outil est à l'arrêt depuis trois semaines —
  il ne pourrait pas non plus revendiquer une récurrence.

## 2026-08-15 — Décision : les indicateurs de marché, triés et datés

- **Décision structurante** : 19 indicateurs proposés, ramenés à **13 réellement à coder**,
  répartis en 4 lots par **coût de données** — le seul critère qui commande l'ordre.
  Spécification : `docs/indicateurs/CONCEPTION.md` — **conception seule, aucun code écrit**.
- **Le mot « stratégie » est abandonné dans tout le projet.** Un indicateur est un *fait*
  (« le RSI vaut 71 »), une stratégie est un *conseil* (« RSI > 70 → vendre »). Le second
  contredirait le garde-fou AMF inscrit dans `CLAUDE.md`. *Un livrable dont le titre
  contredit son propre garde-fou ne tient pas cinq minutes devant un jury.*
- **Vérification avant rédaction — 3 des 19 existaient déjà** : dernier cours et performance
  1 jour (R2 de `db/requetes.sql`), volume relatif 20 séances (R3), volatilité intraséance
  (S2 de `bigdata/query_spark.py`). **Et le portefeuille est déjà valorisé** par la vue
  `v_portefeuille_valorise`, conversion des devises comprise : le lot portefeuille tombe de
  3 ajouts à **2** (poids par ligne, exposition par devise).
- **Manque découvert** : `sources/cotations.py` collecte avec `auto_adjust=True`. C'est le
  bon choix — une performance sur cours bruts serait fausse — mais **les cours passés sont
  réécrits à chaque dividende**. Une performance 1 an n'est donc pas strictement reproductible
  dans le temps. Inscrit comme piège, pas dissimulé.
- **Écarté : le ratio de Sharpe.** `sources/fred.py` ne collecte que `DGS10`, le Trésor
  **américain**, pour un portefeuille en euros ; très bruité sur un an de données
  quotidiennes ; et c'est le seul indicateur de la liste qui **classe** — donc le plus proche
  du conseil. Écart **assumé et présenté à l'oral**, pas un oubli.
- **Erreur corrigée** : la proposition parlait des « 135 instruments ». RITA en compte **111**.
  Le 135 venait du suivi des 135 critères RNCP — deux objets sans rapport.
- **Rattachement** : livrable **E4** (C14–C19). Ces indicateurs ne rapportent **rien** en C2,
  déjà livré avec R1–R3 et S1–S3 : ajouter des requêtes ne re-prouve pas une compétence
  prouvée. Ils sont le contenu de `frontend/`, vide à ce jour.
- **Rien n'est codé, et rien ne doit l'être avant l'ouverture d'E4** : au 15/08 il reste
  12 semaines et C6 est le seul chantier qui ne se rattrape pas.

## 2026-08-14 — RGPD : un traitement déclaré qui n'existait pas

- **Manque découvert** : le registre décrivait **T3** (traçage LangSmith) comme un traitement
  **actif**, avec transfert de données personnelles vers les États-Unis et un risque classé
  🔴 haute. Vérification : ni `LANGCHAIN_TRACING_V2` ni `LANGCHAIN_API_KEY` dans le `.env`
  réel, aucun appel à LangSmith dans le code. **Aucune donnée ne sort de la machine.**
  T3 passe en *« envisagé, non activé »*, criticité abaissée à 🟠.
  *Un registre qui sur-déclare est aussi inexact qu'un registre qui oublie.*
- **Décision documentée** : le choix de l'outil de monitorage a une conséquence RGPD directe —
  LangSmith crée un transfert hors UE, Langfuse auto-hébergé le supprime, Langfuse Cloud
  région UE le maintient sans transfert au sens de l'article 44. Le formateur a validé
  LangSmith ; le tableau reste au registre pour le jour où la question se reposera.
  Obstacle réel à l'auto-hébergement : **Docker ne démarre pas sur cette machine** — il
  manque aussi pour C13.
- **Ajouté** `scripts/verifier_liens.py` : contrôle des liens externes (HTTP) **et** internes
  (le fichier visé existe-t-il, et est-il **dans** le dépôt). Première exécution :
  **34 fichiers · 38 liens internes · 5 externes · 0 cassé.** Règle inscrite dans `CLAUDE.md` :
  à lancer avant chaque envoi de livrable.

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
