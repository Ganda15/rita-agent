# Registre des traitements de données personnelles — RITA

**Compétence C4**, trois critères :
> « Le registre des traitements de données personnelles intègre l'ensemble des traitements
> de données personnelles impliqués dans la base de données. »
> « Les procédures de tri des données personnelles pour la mise en conformité de la base de
> données avec le RGPD sont rédigées. »
> « Les procédures de tri détaillent les traitements de conformité (automatisés ou non) à
> appliquer ainsi que leur fréquence d'exécution. »

**Base réglementaire** : RGPD (Règlement Général sur la Protection des Données,
UE 2016/679), **article 30** — registre des activités de traitement.

**Dernière mise à jour** : 2026-08-14 *(correction de T3 — voir §1)*

---

## 0. Le cadre, dit honnêtement

RITA est un **projet personnel mono-utilisateur**. Era est à la fois :

- le **responsable de traitement** — celui qui décide pourquoi et comment les données sont traitées ;
- la **personne concernée** — celui dont les données sont traitées.

Cette situation **n'exonère de rien** : dès qu'un traitement automatisé porte sur des
données personnelles, le RGPD s'applique. Mais elle simplifie beaucoup de choses — pas de
sous-traitant à encadrer, pas de demande d'accès d'un tiers à instruire.

> ⚠️ **Ce que ça change si RITA devient multi-utilisateur** : il faudra une base légale
> explicite (le consentement), une information des utilisateurs, une procédure de réponse
> aux demandes d'accès, et une analyse d'impact (AIPD) — les données financières sont
> considérées à risque élevé. **Aujourd'hui, aucun de ces éléments n'est en place, et c'est
> assumé.**

**Précision utile** : les données financières **ne sont pas** des « données sensibles » au
sens de l'**article 9** du RGPD (qui vise l'origine ethnique, les opinions politiques, la
santé, l'orientation sexuelle…). Ce sont des données personnelles ordinaires — mais dont la
divulgation cause un préjudice réel, donc à protéger sérieusement.

---

## 1. Les traitements recensés

### T1 — Stockage du portefeuille

| Rubrique | Contenu |
|---|---|
| **Finalité** | Calculer la valorisation et la performance du portefeuille pour produire le briefing quotidien |
| **Base légale** (art. 6) | **Intérêt légitime** de la personne concernée, qui est l'utilisateur lui-même et l'unique destinataire |
| **Personnes concernées** | 1 — l'utilisateur |
| **Catégories de données** | Ticker détenu · quantité · prix de revient unitaire (PRU) · date d'achat · devise |
| **Ce que ça révèle** | La **situation financière** : composition du patrimoine, montants investis, plus ou moins-values |
| **Support** | Table `position` (PostgreSQL) · fichier CSV source |
| **Destinataires** | Aucun. Données locales. |
| **Transfert hors UE** | Non |
| **Durée de conservation** | Position **active** : tant qu'elle est détenue · position **soldée** : 3 ans (utile aux comparaisons de performance), puis suppression |
| **Sécurité** (art. 32) | Fichier source **jamais versionné** (`.gitignore`, vérifié par `git check-ignore`) · base non exposée au réseau · chemin par variable d'environnement `POSITIONS_CSV` |

### T2 — Journal des accès à la mémoire des agents

| Rubrique | Contenu |
|---|---|
| **Finalité** | Déboguer et auditer le comportement des agents (exigence du standard Velmo 2.0) |
| **Base légale** | Intérêt légitime — sans trace, un agent n'est ni débogable ni explicable |
| **Catégories de données** | Nom de l'agent · type de mémoire · opération · clé · **résumé du contenu** |
| **⚠️ Risque** | Le champ `resume` **peut contenir des éléments du portefeuille** (un ticker détenu, un montant) selon ce que l'agent manipule |
| **Support** | Table `memory_audit` |
| **Durée de conservation** | **90 jours** — au-delà, un log de débogage n'a plus d'utilité |
| **Sécurité** | Purge automatisée (voir §2) |

### T3 — Traces d'exécution LangSmith — ⏸ **ENVISAGÉ, NON ACTIVÉ**

> ## ⚠️ Correction du 2026-08-14 — ce traitement n'a **jamais eu lieu**
>
> Ce registre décrivait T3 comme un traitement **actif**, avec transfert de données
> personnelles vers les États-Unis et un risque classé 🔴 haute. **Vérification faite :
> c'est faux.**
>
> | Contrôle | Constat |
> |---|---|
> | `LANGCHAIN_TRACING_V2` dans le `.env` réel | **absent** |
> | `LANGCHAIN_API_KEY` dans le `.env` réel | **absent** |
> | Appel à LangSmith dans le code (`grep`) | **aucun** |
> | `langsmith` installé | oui — **dépendance transitive** de `langchain-core`, jamais activée |
>
> Les deux variables n'existent que dans `.env.example`, à titre d'exemple.
> **Sans drapeau ni clé, aucune trace ne quitte la machine.**
>
> 🔑 **La leçon** : un registre qui **sur-déclare** est aussi inexact qu'un registre qui
> oublie. Déclarer un transfert hors UE qui n'existe pas, c'est se décrire moins protecteur
> qu'on ne l'est — et rendre invérifiable tout le reste du document.

**Le jour où le traçage sera activé**, ce traitement redeviendra réel et les rubriques
ci-dessous s'appliqueront telles quelles. Elles sont conservées pour cette raison.

| Rubrique | Contenu *(applicable seulement après activation)* |
|---|---|
| **Finalité** | Monitorage des agents : latence, coût, qualité des réponses (C11/C20) |
| **Base légale** | Intérêt légitime |
| **Catégories de données** | Prompts et réponses des agents — **donc potentiellement des tickers détenus et des montants** |
| **⚠️ Destinataire** | **LangChain Inc. (États-Unis)** — sous-traitant |
| **⚠️ Transfert hors UE** | **OUI** — encadré par les clauses contractuelles types (CCT) et le *Data Privacy Framework* UE–États-Unis |
| **Durée de conservation** | Selon la politique LangSmith (non maîtrisée par nous) |
| **Mesure de réduction** | ⬜ masquer les montants dans les prompts tracés, ou désactiver le traçage sur les nœuds manipulant le portefeuille |

#### Décision à prendre **avant** d'activer le traçage

L'outil de monitorage n'est pas encore arrêté, et le choix a une conséquence RGPD directe :

| Option | Sous-traitant | Transfert hors UE | Conséquence pour ce registre |
|---|---|---|---|
| **LangSmith** | LangChain Inc. (États-Unis) | **oui** | T3 devient actif, CCT / *Data Privacy Framework* à invoquer |
| **Langfuse auto-hébergé** (cœur sous licence MIT) | **aucun** | **non** | **T3 disparaît** — les données ne quittent pas la machine |
| **Langfuse Cloud, région UE** (Irlande) | Langfuse | **non** | T3 reste, mais sans transfert au titre de l'article 44 |

> 💡 **Le meilleur traitement de données personnelles est celui qu'on ne fait pas.**
> L'auto-hébergement supprime le sous-traitant, le transfert, et les clauses à justifier.
> ⚠️ Il exige Docker — **aujourd'hui le démon ne démarre pas sur la machine d'Era**, c'est
> le vrai obstacle, et il vaut aussi pour C13 (empaquetage, livraison continue).

#### Décision du 2026-09-28 : **Langfuse Cloud, région UE** (option 3), activation prévue en S43 (carte #39)

Décision d'Era, après la règle donnée par le formateur le 28/09 (« la condition, c'est la sensibilité
des données ») et une mesure dans le code plutôt qu'une supposition :

| Ce qui a été mesuré | Résultat | Où |
|---|---|---|
| Le prompt envoyé au modèle contient-il une donnée personnelle ? | **Non** : ticker, cours, variation, ADTV20, devise, fraîcheur, passages de presse. Aucune position, aucun PRU, aucune quantité | `agents/analyst.py`, `generate_briefing()` ; `grep` sur `agents/`, `graph/` : zéro |
| Ce qu'une trace révèle malgré tout | les tickers demandés, donc les valeurs détenues, par effet de bord | ce registre, ligne « catégories » |
| Auto-hébergement possible sur le serveur ? | **Non** : Langfuse v3 = six composants (web, worker, Postgres, ClickHouse, Redis, S3) ; le CX23 a 4 Go partagés, déjà occupés par l'API, PostgreSQL et Chroma | doc Langfuse « self-hosting » ; spécification CX23 |
| Région UE de Langfuse Cloud | Irlande, AWS `eu-west-1`, `cloud.langfuse.com` ; palier gratuit : 50 000 unités/mois, 30 jours de rétention, 2 alertes | doc Langfuse « cloud data regions », « pricing » |
| LangSmith aurait-il convenu ? | région UE disponible (GCP), mais l'éditeur déclare **aucune entité juridique en UE** pour contracter, et l'auto-hébergement est réservé au plan Enterprise : pas de porte de sortie | doc LangSmith « regions FAQ », page des tarifs |

**Conséquences pour ce registre, à appliquer le jour de l'activation (S43)** :

- Destinataire : **Langfuse**, région UE. ⚠️ La page RGPD de Langfuse renvoie à `privacy@clickhouse.com` :
  **l'entité qui traite peut être ClickHouse Inc. (États-Unis)** même pour la région UE. Une région n'est
  pas une personne morale. **Lire le DPA à la création du compte** et inscrire ici le nom exact du
  sous-traitant et sa juridiction. Tant que ce n'est pas fait, T3 reste « envisagé ».
- Transfert hors UE : **non** au titre de la localisation des données ; à confirmer au titre de l'entité
  (point ci-dessus).
- Durée de conservation : 30 jours (palier gratuit), inférieure aux 90 jours de T2.
- Mesure de réduction : rien à masquer aujourd'hui (aucune donnée personnelle dans le prompt). **Condition
  écrite** : si une position, un PRU ou une quantité entre un jour dans le prompt, brancher la fonction de
  masquage du SDK Langfuse avant d'activer la trace correspondante.
- Alternative écartée et pourquoi : auto-hébergement (mesuré impossible sur 4 Go, coût d'entretien décrit par
  le formateur) ; LangSmith (pas de porte de sortie open source, entité UE absente).

### T4 — Fichier CSV source du portefeuille

| Rubrique | Contenu |
|---|---|
| **Finalité** | Alimenter T1 |
| **Support** | Fichier local, hors du dépôt Git |
| **Sécurité** | `.gitignore` : `data/positions.csv`, `*bourse*.xlsm`, `*portefeuille*.csv` — **vérifié** par `git check-ignore` |
| **Durée** | Conservé tant qu'il est la source de vérité du portefeuille |

### Ce qui **n'est pas** un traitement de données personnelles

| Donnée | Pourquoi |
|---|---|
| `cotation`, `valeur`, `alias_valeur` | Cours de bourse — **données publiques**, aucune personne identifiable |
| `taux_change` | Taux BCE — donnée publique |
| `article` | Presse publique. ⚠️ *Peut* citer des personnes, mais on ne les traite pas en tant que personnes |

---

## 2. Procédures de tri — automatisées

**Script** : `db/rgpd_purge.py` · **Exécution** : `python -m db.rgpd_purge --appliquer`

| # | Procédure | Fréquence | Automatisé |
|---|---|---|---|
| **P1** | Purger `memory_audit` au-delà de **90 jours** | **Hebdomadaire** (lundi 03 h 00, APScheduler) | ✅ oui |
| **P2** | Supprimer les positions **soldées depuis plus de 3 ans** | **Mensuelle** (1er du mois) | ✅ oui |
| **P3** | Détecter les **doublons de positions** (même ticker, même date d'achat, même PRU) | Mensuelle | ✅ détection ; ⚠️ suppression **manuelle** — un doublon peut être un vrai second achat |
| **P4** | Vérifier qu'**aucun fichier personnel n'est suivi par Git** | **À chaque commit** (hook pre-commit) | ⬜ **à mettre en place** |
| **P5** | Revoir le champ `resume` de `memory_audit` : contient-il des montants ? | Trimestrielle | ❌ **manuelle** — jugement humain requis |

**Mode par défaut du script : simulation.** Il affiche ce qu'il supprimerait sans rien
supprimer. Le drapeau `--appliquer` est obligatoire pour agir. *Une purge qui s'exécute par
accident est une perte de données irréversible.*

## 3. Procédures de tri — manuelles

| # | Procédure | Fréquence | Pourquoi pas automatique |
|---|---|---|---|
| **M1** | Relire le registre ci-dessus | À chaque nouvelle source de données | Un nouveau traitement doit être inscrit **avant** d'être codé |
| **M2** | Vérifier que le dépôt public ne contient aucune donnée personnelle | **Avant chaque passage en public** | ⚠️ Le dépôt doit s'ouvrir avant le 05/11 |
| **M3** | Décider du sort des doublons détectés par P3 | Mensuelle | Deux achats identiques le même jour sont possibles |
| **M4** | Réévaluer le traçage LangSmith (T3) | Trimestrielle | Arbitrage entre valeur du monitorage et exposition des données |

---

## 4. Exercice des droits (art. 15 à 22)

Era étant la personne concernée, les droits s'exercent par simple accès à la base. Les
commandes sont néanmoins documentées — elles seraient nécessaires dès le deuxième
utilisateur.

| Droit | Article | Comment l'exercer aujourd'hui |
|---|---|---|
| **Accès** | 15 | `SELECT * FROM position;` |
| **Rectification** | 16 | `UPDATE position SET quantite = ... WHERE id = ...;` |
| **Effacement** | 17 | `DELETE FROM position WHERE id = ...;` puis purge du CSV source |
| **Portabilité** | 20 | `\copy (SELECT * FROM position) TO 'export.csv' CSV HEADER` — format ouvert |
| **Limitation** | 18 | Sans objet : traitement local, aucun destinataire |
| **Opposition** | 21 | Sans objet : la personne concernée est le responsable de traitement |

---

## 5. Ce qui reste à faire — dit franchement

| # | Action | Criticité |
|---|---|---|
| 1 | **Choisir l'outil de monitorage AVANT d'activer le traçage** (T3) — l'auto-hébergement supprime le transfert hors UE ; LangSmith le crée | 🟠 moyenne *(abaissée le 14/08 : le traçage n'est pas activé, donc aucune donnée ne sort aujourd'hui)* |
| 2 | **Hook Git `pre-commit`** interdisant l'ajout d'un fichier personnel (P4) | 🟠 moyenne |
| 3 | Brancher P1 et P2 sur APScheduler (aujourd'hui : lancement manuel) | 🟠 moyenne |
| 4 | Chiffrer la sauvegarde de la base si elle sort de la machine | 🟡 basse tant que tout est local |

> Un registre qui ne signale aucune faiblesse n'est pas crédible. Ces quatre points sont
> ouverts, et ils seront présentés comme tels.

---

## 6. 📖 Glossaire

| Terme | En clair | Pourquoi ça compte ici |
|---|---|---|
| **RGPD** | *Règlement Général sur la Protection des Données* — loi européenne de 2016 sur les données personnelles | Exigé par C4 |
| **GDPR** | Le même, en anglais (*General Data Protection Regulation*) | La doc technique dit « GDPR » |
| **Donnée personnelle** | Toute information se rapportant à une personne identifiée ou identifiable | Tes positions en sont |
| **Traitement** | Toute opération sur une donnée : collecte, stockage, consultation, suppression | Même *lire* est un traitement |
| **Responsable de traitement** | Celui qui décide **pourquoi** et **comment** on traite | Era |
| **Personne concernée** | Celui **dont** on traite les données | Era aussi, ici |
| **Sous-traitant** | Un tiers qui traite pour le compte du responsable | LangSmith / LangChain Inc. |
| **Base légale** (art. 6) | La justification juridique du traitement — il en faut **une** parmi six | Ici : intérêt légitime |
| **Intérêt légitime** | Base légale : le traitement sert un intérêt réel sans léser la personne | Celle retenue pour RITA |
| **Registre des traitements** (art. 30) | La liste écrite de tous les traitements | Ce document |
| **Minimisation** (art. 5) | Ne collecter que le strict nécessaire | On ne stocke ni nom ni adresse |
| **Limitation de conservation** (art. 5) | Ne pas garder indéfiniment | D'où les durées du §1 |
| **Données sensibles** (art. 9) | Catégories particulières : santé, opinions, origine… | Les données financières **n'en font pas partie** |
| **AIPD / DPIA** | *Analyse d'Impact relative à la Protection des Données* — étude obligatoire si risque élevé | Non requise en mono-utilisateur |
| **CCT / SCC** | *Clauses Contractuelles Types* — contrat encadrant un transfert hors UE | Couvre le transfert vers LangSmith |
| **Data Privacy Framework** | Accord UE–États-Unis autorisant certains transferts (2023) | Base du transfert T3 |
| **Purge** | Suppression programmée des données trop anciennes | P1 et P2 |
| **Mode simulation** (*dry-run*) | Le script montre ce qu'il ferait, sans le faire | Comportement par défaut de `rgpd_purge.py` |
| **Hook pre-commit** | Script Git qui s'exécute **avant** d'enregistrer un commit | Empêcherait d'ajouter un fichier personnel |
| **PRU** | *Prix de Revient Unitaire* — prix moyen d'achat d'un titre | Donnée personnelle : révèle la plus-value |
