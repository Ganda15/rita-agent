# INC-003 — La base de données `rita` n'existait plus

| | |
|---|---|
| **Détecté le** | **16/08/2026**, de la pire façon : une commande banale échoue, la base n'existe pas — **ni la base, ni le rôle** |
| **Sévérité** | **P1** — perte totale de la couche de données |
| **Durée** | reconstruite le soir même |
| **Impact réel** | **aucune donnée définitivement perdue.** ⚠️ **Mais pas grâce à une sauvegarde** — voir §7, c'est tout l'enjeu de cette fiche |
| **Cause immédiate** | PostgreSQL **18 réinstallé**, base vide |
| **Issue / demande de fusion** | **aucune — commit direct sur `develop`** |

## 1. Ce qu'on a vu

La base `rita` avait disparu du serveur PostgreSQL local. Pas corrompue, pas vide :
**inexistante**. Le rôle non plus.

## 2. Cause racine

**Cause technique** : une réinstallation de PostgreSQL en version 18 a créé une instance
neuve. Les données de l'ancienne instance n'ont pas été reprises — le nouveau serveur ne les
voyait tout simplement pas.

**Cause de conception — et c'est la seule qui compte ici** : *il n'existait aucune sauvegarde.*
Le projet avait 3 mois, 275 000 lignes de cotations, et **zéro copie de sa base**.

> **Rien n'a été perdu parce que les sources étaient versionnées — pas parce qu'il y avait une
> sauvegarde.** La différence entre les deux est exactement l'objet de cet incident.

Le projet a survécu par **chance structurelle** : les données brutes étaient conservées en
Parquet, et `db/importer.py` savait les rejouer. Si l'ingestion avait été destructrice, ou si
les Parquet avaient vécu sur le même disque perdu, l'incident était terminal à 80 jours du
rendu.

## 3. Reproduction en développement

⚠️ **Non reproduit, et volontairement.** Reproduire cet incident signifie détruire une base de
production locale : le coût du test dépasse ce qu'il apprendrait, la cause étant déjà certaine.

**Ce qui a été vérifié à la place** : que la **procédure de reconstruction** fonctionne — ce qui
est la question utile. Elle a été exécutée en vrai, avec des chiffres contrôlés un à un (§6).

*Écrit tel quel plutôt que masqué : le critère demande une reproduction, elle n'a pas eu lieu,
et la raison est défendable.*

## 4. Procédure de débogage

| # | Hypothèse | Comment elle a été testée | Résultat |
|---|---|---|---|
| 1 | Mauvais port de connexion (5432 au lieu de 5433) | connexion explicite sur 5433 | ❌ le serveur répond, mais **pas de base `rita`** |
| 2 | La base existe sous un autre rôle | liste des bases et des rôles de l'instance | ❌ **ni base, ni rôle** |
| 3 | Les données sources sont-elles, elles, intactes ? | inventaire des fichiers Parquet | ✅ **intacts** — la reconstruction est possible |

L'hypothèse 3 a transformé un incident terminal en incident réparable. **C'est la première
question à poser dans toute perte de données : que reste-t-il en amont ?**

## 5. Correction, étape par étape

1. **Recréation** de la base et du rôle.
2. **Rejeu de `db/importer.py`** depuis les Parquet versionnés.
3. **Contrôle chiffré de chaque table**, pas un « ça a l'air bon » :
   111 valeurs · 112 alias · **2 560 lignes dédoublonnées** · **273 608 cotations insérées** ·
   7 positions.
4. **`ANALYZE`** exécuté — et c'est là qu'un second défaut est apparu (§7).

## 6. Vérification et non-régression

Chiffres relevés après reconstruction, table par table, et comparés à l'état attendu :

```
cotation 273 608 · valeur 111 · alias_valeur 112 · position 7
```

⚠️ **La vérification a révélé deux tables oubliées** : la reconstruction n'a rechargé que ce
qui a une **source Parquet**. `taux_change` et `article` n'en ont pas — ils sont restés
**vides pendant un jour**, sans que rien ne le signale. Réimportés le 17/08
(`--etapes ecb` puis `--etapes rss`) : 5 taux, 30 articles, 0 bloqué.

**Il n'y a pas de test de non-régression possible** pour cet incident — on ne teste pas
automatiquement « la base existe encore ». La contre-mesure est opérationnelle, pas logicielle
(§7).

## 7. Ce que ça change pour la suite

- 🔴 **La contre-mesure décidée le 16/08 — `pg_dump` hebdomadaire — n'a été appliquée que le
  24/08.** Huit jours de décision non tenue, écrits ici tels quels. La première sauvegarde
  réelle date du **24/08** : `sauvegardes/rita-2026-08-24.dump`, 4,7 Mo, **vérifiée par
  `pg_restore --list`** (8 tables listées).
  *Un fichier qui existe n'est pas une sauvegarde qui restaure — c'est pourquoi la vérification
  fait partie de la contre-mesure, pas de son commentaire.*
- ⬜ **Ce qui manque encore** : la récurrence n'est **pas automatisée** (sauvegarde faite à la
  main), et **aucune restauration n'a été testée**. *Une sauvegarde jamais restaurée n'est
  qu'un fichier.* Prochaine étape : restaurer le dump dans une base jetable, une fois.
- **Second défaut mis au jour par `ANALYZE`** : les statistiques du planificateur étaient
  périmées au point que **presque toutes les tables étaient estimées à 0 lignes** alors
  qu'elles étaient pleines. C'est la raison pour laquelle la requête de fraîcheur du 25/08
  utilise un `COUNT(*)` **exact** et non l'estimation `reltuples` — *une jauge de santé qui
  ment est pire qu'une jauge absente* (`db/fraicheur.sql`).
- **Leçon transposable** : la question « qu'est-ce qui me sauverait si ceci disparaissait ? »
  doit être posée **avant** que ça disparaisse. Elle l'a été après.
