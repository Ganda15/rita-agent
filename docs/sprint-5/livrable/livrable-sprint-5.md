# Sprint 5 : la vigie et la démo

> RITA, fil rouge de la phase 6 : une aide à la lecture de l'actualité économique, qui répond en citant ses sources ou
> refuse. Le sprint 5 la rend pilotable et reprenable : des mesures, un tableau de bord, des alertes liées à une action,
> une documentation d'exploitation. Version 3 (26/10) : la chronologie du sprint rendue explicite, d'abord la copie
> locale, puis la production (§ 1.2), et la discussion avec le formateur consignée (§ 6) ; le contenu technique ne
> change pas. Version 2 (25/10) : correction de mise en page de la page 11 du PDF, où une phrase
> du § 5.12 s'affichait comme un titre ; le contenu ne change pas. Version 1 : la vigie en production depuis le 23/10
> (livraison N16), et sa copie sur le poste pour les exercices de panne.

## Sommaire

1. Le brief, et RITA en quelques lignes
2. Les livrables demandés, et où les trouver
3. Les critères de la grille : ce qui sera montré, et la preuve
4. Les signaux, les seuils et les actions
5. Les preuves
6. Journal des retours
7. Ce qui n'est pas fait
8. Glossaire
9. Sources et liens

## 1. Le brief, et RITA en quelques lignes

### 1.1 Ce que demande le brief

Le sprint 5 demande de « rendre le système pilotable et reprenable : métriques et traces, tableau de bord lisible par
un non-développeur, alertes à seuils argumentés chacune liée à une action, documentation d'exploitation qu'un tiers
peut suivre seul ». Les livrables : « le système complet en production avec sa vigie ; `docs/exploitation.md` ; le
scénario de démo écrit et répété ».

Pendant l'atelier, l'évaluateur suit la documentation seul, sans aide orale : il déploie, diagnostique une panne
simulée et fait un retour arrière. Tout ce qu'il ne parvient pas à faire est un trou dans la documentation.

### 1.2 La production, et la copie du poste pour les exercices

Le sprint 5 a été construit sans toucher l'original, sur la branche `sprint-5-vigie-demo`, puis livré en production le
23/10 au soir par le chemin habituel du dépôt (§ 5.13). Les exercices de panne se font sur une **copie de RITA lancée
sur le poste** avec Docker (projet `rita-s5`, adresse `http://localhost:8011`), construite depuis cette branche, avec sa
propre image et ses propres volumes.

Ce choix permet de provoquer des pannes et des alertes sans risque pour le service en ligne. La copie reste le lieu
des exercices : la panne et la dérive simulées y sont jouées, jamais sur le service en ligne.

Décision du 22/10 : rester en prototype local, faute de temps. **Décision révisée le 23/10 au soir : mise en
production.** La livraison automatique N16 (passage GitHub n° 39983152061, commit `845e3b3`, en service à 18:12)
met `/sante`, les compteurs et le tableau de bord sur le serveur ; la vigie le surveille de l'extérieur, à son
adresse. Les exercices restent coupés en production (§ 5.13).

**La chronologie : d'abord la copie locale, puis la production.**

| Quand | Où | Ce qui s'est passé | Preuve |
|---|---|---|---|
| 22/10 | copie locale (Docker, port 8011) | la vigie construite et éprouvée : déploiement et retour arrière (18:56 à 18:57), panne simulée diagnostiquée avec la doc (issue #127), dérive simulée jusqu'à l'action (issue #128) | § 5.3 à 5.5 |
| 23/10, matin | copie locale | la doc suivie à la lettre (dix trous corrigés), deux répétitions de la démo, la fausse alerte #130 expliquée et la copie passée sur son propre projet Langfuse | § 5.10 à 5.12 |
| 23/10, soir | production | PR #133 et #134, livraison N16 (18:00 à 18:12, commit `845e3b3`) : la vigie, `/sante` et le tableau de bord en service ; livraison N17 (documents) et tag `livrable-sprint-5-v1` | § 5.13 |
| 25/10 | production | version 2 du livrable (page 11 du PDF corrigée), livrée puis taguée `livrable-sprint-5-v2` | en tête du document |

### 1.3 RITA en trois phrases

RITA aide un investisseur particulier à lire l'actualité des sociétés cotées, sans lire trente articles et en sachant
d'où vient chaque information. Elle fait deux choses : le briefing d'une valeur cotée, et la réponse à une question
libre en français, toujours avec ses sources. Elle refuse ce que ses articles ne couvrent pas, les demandes de conseil
d'achat ou de vente et les tentatives de détournement qu'elle reconnaît.

### 1.4 La vigie, couche par couche

Les traces disent ce qui s'est passé, appel par appel ; les mesures disent si c'est grave ; les alertes disent quoi
faire.

| Couche | Ce qui est en place | Fichier |
|---|---|---|
| Traces | chaque appel laisse une trace dans Langfuse : son parcours (garde-fous, appel au modèle), sa durée, son statut et son motif, jamais le texte de la question ni de la réponse ; le `request_id` relie la trace à la ligne du journal ; sur la copie, un projet Langfuse propre (§ 5.12) | [`src/traces.py`](../../../src/traces.py) |
| Mesures | chaque appel à `/question` et `/briefing` est rangé dans une de six catégories (réponse, refus de sécurité, refus de corpus, refus de qualité, erreur technique, rejet d'accès ou de saisie), avec sa durée et ses jetons ; en mémoire, sous un verrou, 24 h au plus | [`monitorage/compteurs.py`](../../../monitorage/compteurs.py) |
| Signaux | taux sur les 15 dernières minutes, temps de réponse p95, coût estimé sur 24 h, fraîcheur des cours par valeur, rejets ; servis en JSON par `GET /sante`, protégée par la clé | [`monitorage/signaux.py`](../../../monitorage/signaux.py), [`api/sante.py`](../../../api/sante.py) |
| Seuils | un seuil ATTENTION et un seuil PROBLÈME par signal, chacun avec son pourquoi, son action et sa règle de résolution ; prix public du modèle, daté et sourcé | [`monitorage/seuils.json`](../../../monitorage/seuils.json), [`monitorage/prix.json`](../../../monitorage/prix.json) |
| Tableau de bord | sept cartes, chacune avec un mot (SAIN, ATTENTION, PROBLÈME, INCONNU), sa valeur en clair et « Que faire » | [`frontend/tableau-de-bord.html`](../../../frontend/tableau-de-bord.html) |
| Alertes | la vigie, hors de l'API : elle sonde `/health`, lit `/sante`, ouvre une issue GitHub par signal en PROBLÈME, la commente au retour du service, la ferme à la résolution | [`monitorage/vigie.py`](../../../monitorage/vigie.py) |
| Exercices | une panne simulée (fin automatique en 20 minutes au plus, clé d'exercice distincte) et une dérive simulée (six prompts hostiles, deux fois) | [`monitorage/exercice.py`](../../../monitorage/exercice.py), [`monitorage/exercer.py`](../../../monitorage/exercer.py) |
| Copie du poste | déployer une version, revenir à la précédente sans reconstruire, vérifier le commit et l'image | [`scripts/copie_sprint5.py`](../../../scripts/copie_sprint5.py), [`docker-compose.sprint5.yml`](../../../docker-compose.sprint5.yml) |
| Documentation | déployer, diagnostiquer une panne, revenir en arrière, et la table des alertes | [`docs/exploitation.md`](../../exploitation.md) |

### 1.5 L'état de la copie, le 23/10/2026

| Mesure | Valeur | Preuve |
|---|---|---|
| Version servie par la copie | `648293f`, version précédente gardée `d43a01e` | § 5.10 |
| Corpus de la copie | le jeu de démonstration : 6 articles, 3 valeurs (AIR.PA, MC.PA, OR.PA), cours collectés jusqu'au 22/10 | § 5.2 |
| Exercices joués | le 22/10 : une panne diagnostiquée avec la doc, une dérive détectée (#127, #128) ; le 23/10 : la doc suivie à la lettre avec une panne simulée (#129), deux répétitions de la démo (#131) ; chaque issue ouverte puis fermée par la vigie | § 5.4, § 5.5, § 5.10, § 5.11 |
| Coût des exercices du 22/10 | 0,009486 € estimés, sous le plafond de 0,10 € fixé avant | § 5.9 |
| Traçage | Langfuse, dans un projet propre à la copie (`rita-copie-sprint5`), distinct de celui de la production | § 5.12 |
| Tests | 1680 passés, 24 ignorés, 2 échecs attendus ; les neuf modules du sprint 5 couverts à 100 % | § 5.1 |
| Production | N16 (`845e3b3`), livrée le 23/10 à 18:12 : `/sante` et le tableau de bord en service | § 5.13 |

Heures de Paris, sauf mention UTC.

### 1.6 Comment lire ce document

Les sections 1 à 3 se lisent en cinq minutes : le brief, les livrables et les critères. La section 4 donne la table
des alertes ; la section 5, les preuves ; la section 7, ce qui manque. Les liens visent les fichiers du dépôt sur la
branche `sprint-5-vigie-demo`.

## 2. Les livrables demandés, et où les trouver

| Livrable demandé | Où le trouver | État |
|---|---|---|
| « Le système complet en production avec sa vigie » | le tableau de bord de production : <https://178-104-184-125.sslip.io/tableau-de-bord.html> ; la vigie (`monitorage/vigie.py --adresse https://178-104-184-125.sslip.io`) ; la copie du poste pour les exercices | **en production depuis le 23/10** (N16, § 5.13) ; la vigie se lance à la main, pas encore toutes les 15 minutes (§ 7) |
| « `docs/exploitation.md` » | [`docs/exploitation.md`](../../exploitation.md) : avant de commencer, déployer, diagnostiquer une panne, revenir en arrière, les alertes, la vigie et les exercices ; l'ancien guide suit en annexes | écrit, relu contre le code, joué sur la copie le 22/10 ; suivi à la lettre le 23/10, dix trous trouvés et corrigés (§ 5.3, § 5.4, § 5.10) |
| « Le scénario de démo écrit et répété » | [`docs/sprint-5/DEMO.md`](../DEMO.md) : 9 min 40 en six segments, la liste de contrôle, le plan B | écrit, vérifié contre le code, **répété deux fois le 23/10** : environ 9 minutes, puis environ 9 minutes 30 (§ 5.11) |

## 3. Les critères de la grille : ce qui sera montré, et la preuve

| # | Critère de la grille | Ce qui sera montré | Preuve déjà obtenue | État |
|---|---|---|---|---|
| 1 | Du signal à l'action : une dérive simulée déclenche l'alerte prévue, et l'action est documentée | la dérive (12 refus, 0 jeton), l'issue ouverte par la vigie, la carte PROBLÈME, l'action de la doc jouée | joué le 22/10 : issue #128 ouverte à 19 h 16, action suivie, issue fermée à 19 h 32 (§ 5.5) | prêt |
| 2 | Tableau de bord lisible sans explication orale | sept cartes, un mot et une phrase par signal, « Que faire » sous chaque problème | tests de chaque état, captures sur la copie en panne, rétablie, puis en dérive (§ 5.6) | prêt ; la lisibilité, seul l'évaluateur la juge |
| 3 | Test de la doc : déployer seul | `docs/exploitation.md`, section « Déployer » | procédure jouée sur la copie (§ 5.3) ; suivie à la lettre le 23/10, deux trous corrigés (§ 5.10) | suivie à la lettre par son auteur ; le test par un tiers se fait à l'atelier |
| 4 | Test de la doc : diagnostiquer la panne simulée | section « Diagnostiquer une panne », six étapes jusqu'à la cause | panne diagnostiquée avec la doc le 22/10 (§ 5.4) ; le 23/10, panne inconnue trouvée en 11 minutes en suivant la doc, cinq trous corrigés (§ 5.10) | idem |
| 5 | Test de la doc : rollback seul | section « Revenir à la version précédente » | retour arrière en 6 s, commit et image vérifiés ; second retour refusé (§ 5.3) ; rejoué à la lettre le 23/10 sans trou (§ 5.10) | idem |
| 6 | Démo prête : 10 minutes, du réel (parcours principal, une livraison, une alerte) | le scénario `docs/sprint-5/DEMO.md` | questions vérifiées sur la copie ; deux répétitions le 23/10, environ 9 minutes et 9 minutes 30 (§ 5.11) | prêt |
| 7 | Série complète : cinq grilles versionnées, journal des retours tenu | `eval/ateliers/` et le § 6 | grilles des ateliers 1 à 4 versées, avec les retours et leur suite | prêt ; la grille de l'atelier 5 sera remplie par l'évaluateur pendant la démonstration (§ 6) |

## 4. Les signaux, les seuils et les actions

Les seuils sont **provisoires** : écrits avant toute mesure du trafic réel, à relire sur des données réelles. Sous le
minimum de requêtes, ou sans donnée, le verdict est INCONNU, jamais SAIN. Le tableau de bord et la vigie lisent les
mêmes verdicts, calculés une seule fois par `/sante`.

| Signal | ATTENTION | PROBLÈME | Pourquoi ce seuil | Action (dans `docs/exploitation.md`) |
|---|---|---|---|---|
| Le service répond | | 2 sondes de `/health` en échec, à 10 s d'écart | une API arrêtée ne peut pas annoncer sa propre panne ; deux essais évitent une alerte sur un seul paquet perdu | [Diagnostiquer une panne](../../exploitation.md#diagnostiquer-une-panne) |
| Réponses en erreur | 10 % sur 15 min | 20 % (au moins 5 requêtes) | une erreur technique est un service rendu à personne ; le trafic est faible, 1 erreur sur 5 vaut déjà 20 % | [Diagnostiquer une panne](../../exploitation.md#diagnostiquer-une-panne) |
| Refus de sécurité | 15 % sur 15 min | 30 % (au moins 10 requêtes) | une hausse signale une attaque, ou un garde-fou qui bloque de vraies questions ; elle demande un diagnostic, elle ne prouve pas une attaque | [Alerte : refus de sécurité](../../exploitation.md#alerte-refus-de-securite) |
| Temps de réponse (p95) | 10 s | 20 s (au moins 5 requêtes) | au-delà de 10 s l'écran semble figé ; au-delà de 20 s le fournisseur ralentit ou la recherche peine | [Alerte : temps de réponse](../../exploitation.md#alerte-latence) |
| Coût estimé sur 24 h | 1 € | 5 € | une question coûte environ 0,01 € au prix public : 1 € par jour, c'est déjà une centaine de questions pour un service mono-utilisateur | [Alerte : coût estimé](../../exploitation.md#alerte-cout) |
| Fraîcheur des cours | une valeur à 2 ou 3 jours ouvrés | plus de 3 jours ouvrés | un briefing rédigé sur des cours anciens trompe le lecteur ; la séance du jour n'entre qu'après la collecte du soir | [Alerte : fraîcheur des cours](../../exploitation.md#alerte-fraicheur) |
| Appels rejetés (clé, saisie, débit) | 20 sur 15 min | 100 sur 15 min | une rafale de 403 signale une clé essayée au hasard, une rafale de 429 un client qui boucle | [Alerte : appels rejetés](../../exploitation.md#alerte-rejets) |

Chaque seuil est validé par un test : un seuil sans pourquoi, sans action ou sans règle de résolution, ou un seuil
ATTENTION au-dessus du seuil PROBLÈME, est refusé au chargement (`tests/test_seuils.py`).

**Le coût.** Il est calculé à partir des jetons de toutes les tentatives d'un appel, au prix public du modèle déployé
(GPT-5.4, zone de données UE, relevé sur l'API Azure Retail Prices en euros, en vigueur depuis le 01/03/2026 :
2,4199 € par million de jetons d'entrée, 0,242 € en cache, 14,5195 € en sortie). C'est une borne haute : les jetons
mis en cache sont comptés au prix plein.

### 4.1 L'OWASP : ce que la vigie couvre, et la suite pour le fil rouge

Le cours « OWASP : la carte des portes d'entrée » (formation Dev IA Agentique, Simplon) range trois listes (Web 2025,
LLM 2026, Agentic 2026) sous six questions. La vigie répond surtout à la sixième, « Et en production, ça tient ? »,
et touche trois autres. Le tableau ne garde que ce que le sprint 5 met réellement en œuvre. Les risques LLM portent
leurs deux numéros : la page officielle de l'OWASP affiche encore l'édition 2025, le cours suit l'édition 2026.

| Question du cours | Risque OWASP | Ce que le sprint 5 en fait | Preuve | État |
|---|---|---|---|---|
| 6. En production, ça tient ? | A09:2025 Security Logging & Alerting Failures | journal sans texte avec son `request_id`, traces Langfuse, sept signaux à seuils argumentés, une vigie qui ouvre et ferme une issue par alerte, éprouvée par une dérive et une panne | § 5.4, § 5.5, § 5.10 ; issues #127 à #131 | couvert, en production depuis N16 ; la vigie se lance à la main |
| 6. En production, ça tient ? | A10:2025 Mishandling of Exceptional Conditions | une panne du fournisseur rend un 503 motivé, sans plantage ; sans donnée, le verdict est INCONNU, jamais SAIN ; une `/sante` illisible donne le code 2 à la vigie | § 5.4 ; tests du sprint 5 | couvert |
| 6. En production, ça tient ? | A02:2025 Security Misconfiguration | une copie isolée : image et volumes propres, seul le port 8011 publié, clés jamais affichées ; un défaut réel trouvé et corrigé : la copie partageait le projet Langfuse de la production (fausse alerte #130) | § 5.2, § 5.12 | couvert, après un incident |
| 6. En production, ça tient ? | Unbounded Consumption (LLM06:2026, LLM10:2025) | coût estimé sur 24 h, alerte à 1 € puis à 5 € ; limite de 10 appels par minute ; rejets 429 surveillés | § 4, § 5.9 | partiel : une alerte, pas de coupure au-delà d'un budget |
| 1. Qui donne les ordres ? | Prompt Injection (LLM01:2026, LLM01:2025) | le signal « Refus de sécurité » compte les détournements refusés (`TENTATIVE_DETOURNEMENT`) ; la dérive simulée le déclenche | § 5.5, § 5.11 | surveillé ; le garde-fou vient du sprint 4 |
| 2. Qui a le droit de faire quoi ? | A01:2025 Broken Access Control, A07:2025 Authentication Failures | la panne simulée exige une clé d'exercice distincte de celle des questions (403 sinon) ; les rejets 403 sont un signal | `tests/test_exercice.py` ; § 4 | couvert |
| 4. Qu'est-ce qui sort, et vers où ? | Sensitive Information Disclosure (LLM02:2026, LLM02:2025), Hidden Context Exposure (LLM08:2026 ; System Prompt Leakage, LLM07:2025) | ni le texte des questions ni les clés dans les compteurs, le journal, les traces ou les issues ; les fuites refusées (`FUITE_BLOQUEE`) entrent dans le signal « Refus de sécurité » | § 5.1, § 5.12 | couvert |
| 5. Peut-on le croire ? | Misinformation (LLM07:2026, LLM09:2025) | l'alerte de fraîcheur des cours ; la consigne de l'analyste ne déduit plus une radiation d'une cotation ancienne | § 5.7 | couvert sur la copie ; l'écart de production reste ouvert |

**Pour le fil rouge, après le sprint 5 :**

- passer en revue les trois listes, une par une (30 risques), dans le RITA original, avant la prochaine mise en
  production : pour chaque risque, ce que RITA fait, la preuve et l'état, ou « sans objet » avec sa raison ;
- rattacher chaque garde-fou du sprint 4 au risque qu'il traite ;
- lancer la vigie de production toutes les 15 minutes, sans le poste (A09), et ajouter une coupure au-delà d'un budget
  de coût (Unbounded Consumption).

## 5. Les preuves

L'index complet des preuves est dans [`evidence/sprint-5/README.md`](../../../evidence/sprint-5/README.md).

### 5.1 Les tests et la couverture

Chaque étape a commencé par des tests rouges, avant le code ; les rouges sont consignés dans les messages de commit.

| Mesure | Résultat | Fichier |
|---|---|---|
| Suite complète, 23/10 | 1680 passés, 24 ignorés, 2 échecs attendus, 0 échec | [`suite-complete-2026-10-23.txt`](../../../evidence/sprint-5/mesures/suite-complete-2026-10-23.txt) |
| Tests du sprint 5 et couverture des neuf modules du sprint 5 | 286 passés ; 100 % des 764 instructions | [`tests-et-couverture-sprint-5-fin-2026-10-22.txt`](../../../evidence/sprint-5/mesures/tests-et-couverture-sprint-5-fin-2026-10-22.txt) |
| Analyse statique (ruff) | aucune remarque | [`ruff-sprint-5-2026-10-22.txt`](../../../evidence/sprint-5/mesures/ruff-sprint-5-2026-10-22.txt) |

Ce que les tests vérifient, entre autres : la bonne catégorie pour une réponse, un refus en HTTP 200, un 403, un 422,
un 429 et une erreur ; aucun compte perdu quand plusieurs fils comptent en même temps ; une rafale de rejets qui ne
peut pas évincer les résultats ; aucun texte de question dans les compteurs ; jamais la clé dans une issue ; la fin
automatique de la panne à 20 minutes, horloge simulée ; une issue par signal, jamais de doublon, avec un faux `gh`.

### 5.2 La copie du sprint 5 lancée sur le poste

Construite depuis la branche, sous l'image `rita-api:s5-<commit>`, avec le commit et la date de construction gravés
dans l'image. L'image de la pile locale existante (`rita-api:local`) n'est pas touchée. Après la collecte, les trois
valeurs ont une cotation du 22/10. Détail : [`copie-locale-2026-10-22.md`](../../../evidence/sprint-5/copie-locale-2026-10-22.md).

### 5.3 Le déploiement et le retour arrière, joués sur la copie

| Heure | Commande | Résultat |
|---|---|---|
| 18:56:52 | `copie_sprint5.py deployer` | `/health` annonce `699e479` ; précédente gardée : `f8b13c8` (14 s) |
| 18:57:16 | `copie_sprint5.py revenir` | `/health` annonce `f8b13c8`, image vérifiée, sans reconstruction (6 s) |
| 18:57:34 | `revenir` une seconde fois | refusé : aucune version précédente |
| 18:57:35 | `deployer` | courante `699e479`, précédente `f8b13c8` |
| 19:33:10 | `deployer` (correctif des heures, § 5.4) | courante `d43a01e`, précédente `699e479` |

**La livraison automatique, en production.** Chaque fusion dans `main` construit, vérifie, publie et déploie l'image
(`.github/workflows/livraison.yml`). C'est elle qui a mis le sprint 5 en production : la livraison N16 du 23/10
(commit `845e3b3`, exécution GitHub n° 39983152061, conclusion `success`, § 5.13). La copie du poste, elle, se livre
par une commande.

### 5.4 La panne simulée, diagnostiquée avec la doc

| Heure | Ce qui s'est passé |
|---|---|
| 18:58:13 | panne posée par commande (clé d'exercice) |
| 18:58:16 | 5 appels de test : 5 réponses `HTTP 503 erreur FOURNISSEUR_INDISPONIBLE`, sans appel au modèle |
| 18:58:19 | la vigie ouvre l'issue [#127](https://github.com/Ganda15/rita-agent/issues/127), « erreurs_techniques », étiquettes `incident` et `E5` |
| 19:00:07 | diagnostic en suivant `docs/exploitation.md` : `/health` répond ; le journal donne le motif des 5 erreurs avec leur `request_id` ; `/sante` désigne l'exercice ; panne retirée |
| 19:00:25 | 5 appels réels : 3 réponses, 2 abstentions, tous en HTTP 200 : **service rétabli** |
| 19:00:40 | la vigie commente l'issue : « Service rétabli à 19:00 … L'alerte de taux reste ouverte jusqu'à 19:13 environ » |
| 19:14:25 | la vigie ferme l'issue : **alerte résolue** (0 erreur sur 5 dans les 15 dernières minutes) |

Service rétabli et alerte résolue sont deux constats distincts : le service répond tout de suite, l'alerte de taux se
résout quand les erreurs sortent de la fenêtre de 15 minutes. Une anomalie relevée pendant l'exercice (heures données
en UTC hors du tableau de bord, le conteneur tournant en UTC) a été corrigée, testée et vérifiée sur la copie le soir
même (commit `d43a01e`). Journal brut : [`preuves-copie-2026-10-22-journal.txt`](../../../evidence/sprint-5/preuves-copie-2026-10-22-journal.txt).

### 5.5 La dérive simulée : du signal à l'action

| Heure | Ce qui s'est passé |
|---|---|
| 19:15:03 | dérive : les six prompts hostiles H1 à H6, deux fois, à 8 par minute ; 12 refus `TENTATIVE_DETOURNEMENT` sur 12, `jetons ajoutés : 0`, 87 s |
| 19:16:30 | la vigie ouvre l'issue [#128](https://github.com/Ganda15/rita-agent/issues/128), « refus_securite » (100 %, seuil 30 %) |
| 19:17:11 | action de la doc : lecture des 12 lignes de refus, durées de 0 à 12 ms (refus avant le modèle) ; prompts hostiles connus, rien à corriger |
| 19:32:33 | la vigie ferme l'issue, 15 minutes plus une marge après le dernier refus |

C'est la chaîne demandée par le critère 1 : un signal (refus de sécurité), un seuil argumenté (30 % sur 15 minutes,
au moins 10 requêtes), une alerte (l'issue), une action documentée et jouée. Détail commande par commande :
[`preuves-copie-2026-10-22.md`](../../../evidence/sprint-5/preuves-copie-2026-10-22.md).

### 5.6 Le tableau de bord

Sept cartes : le service, puis les six signaux mesurés. Chacune dit son état en toutes lettres, sa valeur en mots
(« 12 sur 12 (100 %) »), sa période, et « Que faire » quand il faut agir. Trois heures sont affichées : l'actualisation
du tableau, le calcul des mesures, le début des mesures. Un exercice en cours s'annonce par un bandeau. La page tient sur un écran de
téléphone (375 px), et une lecture qui échoue le dit au lieu d'afficher un état périmé.

| Capture (prise sur la copie, 22/10) | Ce qu'elle montre |
|---|---|
| [`copie-1-panne-en-cours.webp`](../../../evidence/sprint-5/captures/copie-1-panne-en-cours.webp) | le bandeau de l'exercice ; « Réponses en erreur » PROBLÈME, 5 sur 5 |
| [`copie-2-service-retabli-alerte-ouverte.webp`](../../../evidence/sprint-5/captures/copie-2-service-retabli-alerte-ouverte.webp) | plus de bandeau ; l'alerte encore ouverte, 5 sur 10 |
| [`copie-3-derive-refus-securite.webp`](../../../evidence/sprint-5/captures/copie-3-derive-refus-securite.webp) | « Refus de sécurité » PROBLÈME, 12 sur 12, avec sa consigne |
| [`copie-0-redemarrage-pendant-le-retour-arriere.webp`](../../../evidence/sprint-5/captures/copie-0-redemarrage-pendant-le-retour-arriere.webp) | la copie qui redémarre : « Le service ne répond pas », les autres cartes INCONNU |

### 5.7 Le critère 1 du contrat du sprint 1

Le livrable du sprint 4 avait relevé un briefing qui déduisait d'une cotation ancienne qu'une valeur était
« probablement radiée ». La consigne de l'analyste dit désormais que les cours ne sont pas à jour depuis N jours, et
qu'il ne faut rien en déduire sur la cotation de la valeur (`agents/analyst.py`, commit `d9a2118`, test rouge puis
vert). Dans la copie, la collecte quotidienne des cours ferme l'écart de fraîcheur. **En production, l'écart reste
ouvert** : la correction est sur la branche du sprint 5, pas dans `main`.

### 5.8 Le scénario de démo

[`docs/sprint-5/DEMO.md`](../DEMO.md) : introduction (30 s : le concept, le cas d'usage, ce que le sprint apporte),
parcours principal (110 s), livraison (90 s), alerte déclenchée (210 s), documentation (80 s), conclusion (60 s), soit
9 min 40. Les questions ont été vérifiées sur la copie
le 22/10 : « Comment L'Oréal organise-t-elle sa division des produits professionnels ? » reçoit une réponse citée en
environ 2 s ; « Quelle est la recette de la tarte Tatin ? » est refusée `OUT_OF_CORPUS`, sans appel au modèle. Un test
vérifie que la somme des segments tient en 10 minutes, que chaque commande citée existe, et que le plan B est écrit
(`tests/test_demo_doc.py`).

### 5.9 Ce que la vigie a coûté

Les exercices du 22/10 ont consommé 2 420 jetons d'entrée et 250 de sortie, soit **0,009486 €** estimés, sous le
plafond de 0,10 € fixé avant les preuves. La dérive n'a consommé aucun jeton : les refus arrivent avant le modèle.

### 5.10 Le test de la doc à la lettre (23/10)

L'auteur de la doc l'a suivie seul, dans l'ordre, depuis sa copie de lecture, sur une panne simulée posée sans en
dire la nature (seul le symptôme était donné). C'est une répétition, pas le test par un tiers, qui se fait à l'atelier.

| Section | Résultat | Trous trouvés et corrigés |
|---|---|---|
| Avant de commencer | clés présentes, tableau de bord ouvert | une commande pour vérifier les clés sans les afficher ; Langfuse facultatif |
| Déployer | `d752b33` en service, « Le service répond » SAIN | les zéros d'`initialiser` sur une copie déjà initialisée ; les avertissements `Read-only file system` sans effet |
| Diagnostiquer une panne | cause trouvée en 11 minutes (le bandeau de l'exercice) ; service rétabli ; issue #129 fermée par la vigie 17 minutes après son ouverture | l'étape 2 renvoyait à l'étape 4 et faisait sauter l'étape 3, celle qui trouve l'exercice ; une panne simulée a les mêmes symptômes qu'une vraie ; rien de prévu quand les étapes 4 et 5 ne donnent rien ; la consigne de la carte « Réponses en erreur » ne parlait pas de l'exercice |
| Revenir à la version précédente | revenu à `d43a01e` en 5 s, image vérifiée, sans reconstruction | aucun |
| Déployer de nouveau | `18f34de` en 4 s, la nouvelle consigne servie par le tableau de bord | aucun |

Les neuf trous sont corrigés (commit `18f34de`), chacun couvert par un test rouge puis vert
(`tests/test_exploitation_doc.py`) ; un dixième l'est ensuite (§ 5.12). Détail :
[`test-doc-et-repetitions-2026-10-23.md`](../../../evidence/sprint-5/test-doc-et-repetitions-2026-10-23.md).

### 5.11 Les deux répétitions de la démo (23/10)

| | Répétition 1 | Répétition 2 |
|---|---|---|
| Vigie | à blanc | réelle (`--github`) |
| Parcours principal | réponse citée à 10:49, refus `OUT_OF_CORPUS` | réponse citée à 11:22, refus `OUT_OF_CORPUS` |
| Dérive | 12 refus sur 12 en 83 s, 0 jeton | 12 refus sur 12 en 84 s, 0 jeton |
| Alerte | « Refus de sécurité » PROBLÈME, 12 sur 12 | issue #131 ouverte à 11:28, fermée par la vigie à 11:45 |
| Durée totale | environ 9 minutes | environ 9 minutes 30 |
| Corrigé ensuite dans le scénario | la phrase sur la livraison automatique de production, oubliée : raccourcie et dite juste après `etat` | deux `deployer` puis un `revenir` ont laissé la copie sur l'ancienne version : un seul `deployer` dans le segment |

Les horodatages viennent des traces de Langfuse et du journal de la copie ; les durées totales ont été chronométrées
par le présenté.

### 5.12 Langfuse sur la copie, et une fausse alerte corrigée

Le 23/10 à 09:50, le traçage Langfuse a été activé sur la copie : chaque question y laisse une trace `question` sans
texte (entrée et sortie vides), avec le même `request_id` que le journal de la copie, ce qui relie la trace à la
procédure de diagnostic. Les clés venaient du `.env` de développement, qui pointe sur le projet Langfuse de la
production. À 10:30, la panne simulée de 10:04 a déclenché l'alerte « fournisseur en erreur » de la production
(issue #130). L'API de Langfuse l'a confirmé : les 10 observations en erreur des dernières 24 h venaient toutes de la copie,
et la production n'en avait aucune. L'issue a été fermée avec son explication, et la copie est passée sur son propre
projet, `rita-copie-sprint5`, sans alerte ; une question de test y arrive, et plus dans celui de la production. La
documentation le dit désormais (trou 10).

### 5.13 La mise en production (23/10)

Le 23/10 au soir, le sprint 5 suit le chemin habituel du dépôt : la PR [#133](https://github.com/Ganda15/rita-agent/pull/133)
vers `develop`, puis la PR [#134](https://github.com/Ganda15/rita-agent/pull/134) vers `main`, chacune avec ses contrôles
verts et fusionnée par le présenté. La fusion dans `main` (18:00) déclenche la livraison automatique N16 : exécution
GitHub n° 39983152061, conclusion `success`, de 18:00:40 à 18:12:40.

| Vérification, sans la clé | Avant (N15) | Après (N16) |
|---|---|---|
| `GET /health` | commit `3c35398` | commit `845e3b3`, `status ok` |
| `GET /tableau-de-bord.html` | 404 | 200 |
| `GET /sante` | 404, la route n'existait pas | 403 : la route existe et exige la clé |

La chaîne Linux a demandé deux corrections avant la fusion : un faux positif de gitleaks (l'étiquette d'une image
Docker prise pour une clé, exception ciblée sur un seul commit et un seul fichier) et deux tests qui écrivaient
l'heure de Paris en dur alors que la machine de la chaîne est en UTC. La clé de l'API de production ne vit que sur le
serveur : la lecture de `/sante` avec la clé et la vigie pointée sur le serveur se font par l'opérateur, qui tape la
clé lui-même. Détail : [`production-2026-10-23.md`](../../../evidence/sprint-5/production-2026-10-23.md).

## 6. Journal des retours

**Discussion avec le formateur : le déroulé du sprint expliqué.** Le sprint a d'abord été construit et éprouvé sur la
copie locale (22 et 23/10), puis mis en production le 23/10 au soir (livraison N16), comme le retrace la chronologie du
§ 1.2. Ce déroulé a été présenté au formateur pendant la discussion.

**Conseil reçu à l'atelier n°4 : traité.** Le formateur a redonné les conseils de présentation de l'atelier n°3 : aller
droit au but, couche par couche ; le projet en deux ou trois phrases ; la partie technique en cinq minutes ; l'ordre des
modalités du brief ; le code seulement si on le demande
([grille de l'atelier n°4](../../../eval/ateliers/sprint-4-grille.md)). Le scénario de démo les applique : une phrase
d'introduction, le parcours principal avant la technique, 9 min 40 en tout, le code seulement sur question
([`docs/sprint-5/DEMO.md`](../DEMO.md)).

**Les grilles de la série.** Ateliers 1 à 4 : versées dans [`eval/ateliers/`](../../../eval/ateliers/) ; les grilles
officielles des ateliers 3 et 4 n'ont pas été remplies, les retours ont été donnés à l'oral et sont relevés dans chaque
fichier. Atelier 5 : remplie par l'évaluateur pendant la démonstration, puis versée sous
`eval/ateliers/sprint-5-grille.md`.

## 7. Ce qui n'est pas fait

- **La vigie de production se lance à la main** (ou par une tâche planifiée du poste) : pas encore de passage
  automatique toutes les 15 minutes depuis GitHub. Les exercices de panne restent sur la copie.
- **La livraison de la copie se lance par une commande.** La livraison automatique est celle de la production (N16,
  § 5.13) ; la copie sert aux exercices.
- **La documentation n'a pas encore été suivie par un tiers.** Elle a été suivie à la lettre par son auteur, et dix
  trous ont été corrigés ; le test autonome se fera à l'atelier, avec l'évaluateur.
- **Les seuils sont provisoires** tant qu'ils n'ont pas été relus sur un trafic réel.
- **Les mesures vivent en mémoire** : elles repartent à zéro à chaque redémarrage de l'API (déploiement, retour
  arrière). Le tableau de bord affiche « mesures depuis HH:MM ».
- **La vigie et la collecte des cours se lancent à la main** : aucune tâche planifiée n'est créée sur le poste. Sans
  collecte, l'alerte de fraîcheur le signale.
- **L'écart de fraîcheur de la production** (critère 1 du contrat du sprint 1) reste ouvert.
- **Limites relevées pendant les preuves** : la commande `exercer appels` rend toujours le code 0, quels que soient
  les statuts (la preuve repose sur la lecture de chaque ligne) ; pour des refus instantanés, le tableau de bord
  affiche « moins de 0,0 s » ; juste après l'ouverture d'une issue, GitHub peut mettre quelques secondes à la lister :
  il faut laisser au moins 30 s entre deux passages de la vigie ; le corps de l'issue #127, publié avant le correctif,
  garde une heure UTC ; à blanc, la vigie affiche à tort `vigie : ouverte : …` après `[à blanc] ouvrirait l'issue`,
  alors qu'aucune issue n'est créée ; les traces de la copie du 23/10 entre 09:50 et 11:58 sont restées dans le projet
  Langfuse de la production.
- **La revue OWASP complète** (trois listes, 30 risques) reste à faire dans le RITA original ; le sprint 5 ne traite
  que ce qui touche la vigie (§ 4.1).
- **Restes de documentation** : `docs/EXPLOITATION.pdf` date d'avant le sprint 5 ; `deploy/deployer.py` et le
  workflow `retour-arriere.yml` citent encore l'ancien nom `EXPLOITATION.md` ; le lien « Question » manque dans le menu de deux pages.

## 8. Glossaire

- **Vigie** : le programme qui surveille RITA de l'extérieur et ouvre une alerte quand un seuil est franchi.
- **Signal** : une mesure suivie (taux d'erreurs, temps de réponse, coût…).
- **Seuil** : la valeur à partir de laquelle un signal passe en ATTENTION ou en PROBLÈME.
- **Verdict** : l'état d'un signal : SAIN, ATTENTION, PROBLÈME, ou INCONNU quand les données manquent.
- **Fenêtre glissante** : seuls les appels des N dernières minutes comptent (ici 15).
- **p95** : le temps sous lequel passent 95 % des réponses.
- **Jeton** : l'unité de texte que le modèle facture, en entrée et en sortie.
- **Coût estimé** : jetons consommés multipliés par le prix public ; une borne haute.
- **Fraîcheur** : l'âge de la dernière cotation d'une valeur, en jours ouvrés (jours de bourse).
- **Issue** : un ticket GitHub ; ici, une alerte, datée, avec son action.
- **Panne simulée** : une panne du fournisseur provoquée exprès, sûre et réversible, qui se termine seule.
- **Dérive simulée** : une rafale de prompts hostiles connus, envoyée exprès pour déclencher l'alerte de sécurité.
- **Clé d'exercice** : une clé à part, réservée aux commandes de panne simulée.
- **Copie du sprint 5** : RITA lancée sur le poste avec Docker, depuis la branche du sprint 5 ; un prototype local.
- **Retour arrière (rollback)** : relancer la version précédente, sans la reconstruire.
- **403, 422, 429, 503** : codes HTTP : clé refusée, saisie invalide, trop de demandes, service indisponible.
- **Definition of Done** : la liste de vérifications calculées qui doit être verte avant de poser le tag.
- **Tag** : une étiquette Git posée sur un commit précis ; son lien ne bouge plus.
- **OWASP** : fondation ouverte qui publie les listes des dix risques de sécurité les plus courants, pour les
  applications web, les applications de LLM et les agents.

## 9. Sources et liens

- La grille de l'atelier croisé n°5 :
  <https://simplonline-v3-prod.s3.eu-west-3.amazonaws.com/media/file/pdf/grille-atelier-5-vigie-demo-6acc975fa7654883994100.pdf>
- Le prix du modèle, API Azure Retail Prices (euros) :
  <https://prices.azure.com/api/retail/prices?currencyCode='EUR'&$filter=meterName%20eq%20'5.4%20inp%20Dz%201M%20Tokens'>
- La documentation d'exploitation : [`docs/exploitation.md`](../../exploitation.md)
- Le scénario de démo : [`docs/sprint-5/DEMO.md`](../DEMO.md)
- Les preuves : [`evidence/sprint-5/README.md`](../../../evidence/sprint-5/README.md)
- Le livrable du sprint 4 : [`docs/sprint-4/livrable/livrable-sprint-4.md`](../../sprint-4/livrable/livrable-sprint-4.md)
- OWASP Top 10:2025, applications web : <https://owasp.org/Top10/2025/>
- OWASP Top 10 for LLM Applications (page officielle, édition 2025 affichée le 23/10/2026) :
  <https://genai.owasp.org/llm-top-10/>
- Le cours « OWASP : la carte des portes d'entrée », formation Dev IA Agentique (Simplon)
