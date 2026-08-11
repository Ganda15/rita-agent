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

**Dernière mise à jour** : 2026-08-01

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

### T3 — Traces d'exécution LangSmith

| Rubrique | Contenu |
|---|---|
| **Finalité** | Monitorage des agents : latence, coût, qualité des réponses (C11/C20) |
| **Base légale** | Intérêt légitime |
| **Catégories de données** | Prompts et réponses des agents — **donc potentiellement des tickers détenus et des montants** |
| **⚠️ Destinataire** | **LangChain Inc. (États-Unis)** — sous-traitant |
| **⚠️ Transfert hors UE** | **OUI** — encadré par les clauses contractuelles types (CCT) et le *Data Privacy Framework* UE–États-Unis |
| **Durée de conservation** | Selon la politique LangSmith (non maîtrisée par nous) |
| **Mesure de réduction** | ⬜ **À FAIRE** : masquer les montants dans les prompts tracés, ou désactiver le traçage sur les nœuds manipulant le portefeuille |

> 🔴 **T3 est le point faible du dispositif et il est signalé comme tel.** Envoyer des
> montants de portefeuille à un service américain est une décision qui doit être consciente.
> **Ce n'est pas encore corrigé** — c'est une action ouverte, pas un acquis.

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
| 1 | **Masquer les montants dans les traces LangSmith** (T3) | 🔴 haute |
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
