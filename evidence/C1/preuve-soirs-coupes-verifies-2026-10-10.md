# Preuve C1 : les 7 soirs de collecte coupés, vérifiés en base, et le taux BCE du 03/09 rattrapé (10 octobre 2026)

## Pourquoi

Le rapport E1 (§ 3, version 2.2) disait : « 40 journaux du 24/08 au 02/10, 33 terminés avec le code 0, les 7 autres
interrompus par l'arrêt du poste **et rattrapés** par les plages de dates que chaque étape accepte ». En relisant E1, Era
a demandé ce qui s'était passé après les coupures. Le rattrapage du 18/09 n'était documenté que pour quatre soirs
(13, 14, 16 et 17/09). Avant le gel, on a vérifié les sept dans la base.

## Les sept journaux sans code de sortie

Relevé dans `logs/collecte-2026-*.log` (24/08 au 02/10) : 40 journaux, 33 avec `Code de sortie : 0`, 7 sans code, tous
terminés par `^C` (console fermée à l'arrêt du poste).

| Soir | Où la collecte s'est arrêtée (d'après le journal) |
|---|---|
| 02/09 | taux BCE lus, coupé pendant les flux RSS (3 flux lus) |
| 03/09 | coupé à 19:00:06, avant la première étape |
| 08/09 | taux et flux RSS faits, coupé pendant le scraping (4 pages Boursorama) |
| 13/09, 14/09, 16/09, 17/09 | rattrapés le 18/09 (`--etapes ecb,rss,indexation --du 2026-09-12 --au 2026-09-18`, voir `ETAT.md`, ligne du 18/09) |

## Vérification en base, lecture seule (10/10, avant rattrapage)

Requête lancée par Era sur la base du poste, dans une transaction `READ ONLY` terminée par `ROLLBACK` (fichier hors
dépôt `D:\KandaWork\RITA_PROJECT\verif-soirs-coupes.sql`, aucune instruction d'écriture). L'agent n'a pas lu la base
lui-même : le rôle `rita_lecture` n'a ni mot de passe ni chaîne de connexion sur ce poste (`RITA_DSN_LECTURE` vide), et
`AGENTS.md` lui interdit `DATABASE_URL`.

| Soir coupé | Taux BCE (devises) | Cours (valeurs) | Articles publiés ce jour | Constat |
|---|---|---|---|---|
| 02/09 (mer.) | 5 | 108 | **4** (voisins : 49 le 01/09, 39 le 04/09) | articles perdus |
| 03/09 (jeu.) | **aucune ligne** | 108 (rempli par la collecte suivante) | **6** | taux et articles perdus |
| 08/09 (mar.) | 5 | 108 | 35 | rien de perdu |
| 13/09 (dim.) | sans objet | sans objet | 5 | rattrapé le 18/09 |
| 14/09 (lun.) | 5 | 108 | 41 | rattrapé le 18/09 |
| 16/09 (mer.) | 5 | 108 | 32 | rattrapé le 18/09 |
| 17/09 (jeu.) | 5 | **4** | 54 | rattrapé le 18/09, sauf la séance des valeurs de Paris (déclaré le 18/09 : Yahoo ne l'a pas) |

108 valeurs est le niveau des jours ouvrés de la période (106 le 07/09), pas un manque propre aux soirs coupés. Les articles de flux RSS ne se
rattrapent pas : un flux ne garde que ses 20 à 30 derniers éléments (même limite que le 18/09).

## Rattrapage du taux BCE du 03/09 (10/10, par Era)

La BCE garde l'historique et l'étape `ecb` accepte une plage de jours (`startPeriod`, `endPeriod`) ; l'écriture est un
`INSERT ... ON CONFLICT (devise, date_taux) DO UPDATE`, rejouable.

```
C:\Python314\python.exe -X utf8 -m pipelines.ingest --etapes ecb --du 2026-09-03 --au 2026-09-03 --simulation
  taux_change (BCE)            lues    4 | ecrites    0 | rejetees   0
  Etapes reussies : 1/1   Duree : 1.6 s

C:\Python314\python.exe -X utf8 -m pipelines.ingest --etapes ecb --du 2026-09-03 --au 2026-09-03
  taux_change (BCE)            lues    4 | ecrites    5 | rejetees   0
  Etapes reussies : 1/1   Duree : 0.6 s
```

Manifeste `logs/manifeste-2026-10-10-151156.json` (dossier ignoré par Git, sur le poste) : mode `execution`, période
`2026-09-03` à `2026-09-03`, étape `ecb`, 4 lues, 5 écrites (4 devises et l'euro), 0 rejetée, code au commit `63afa2e`.

## Contrôle en base après rattrapage

Requête en lecture seule lancée par Era (`D:\KandaWork\RITA_PROJECT\verif-taux-03-09.sql`, `BEGIN TRANSACTION READ
ONLY` puis `ROLLBACK`) :

```
=== Taux du 03/09 (attendu : 5 devises)
 devise | date_taux  | valeur_pour_eur
--------+------------+-----------------
 CHF    | 2026-09-03 |        0.939000
 EUR    | 2026-09-03 |        1.000000
 GBP    | 2026-09-03 |        0.860550
 JPY    | 2026-09-03 |      181.210000
 USD    | 2026-09-03 |        1.161500
(5 lignes)

=== Taux par jour du 01/09 au 05/09
    jour    |  j  | devises
------------+-----+---------
 2026-09-01 | Tue |       5
 2026-09-02 | Wed |       5
 2026-09-03 | Thu |       5
 2026-09-04 | Fri |       5
(4 lignes)
```

Le 03/09 a maintenant ses cinq taux, entre le 02/09 et le 04/09. **Rejouable, vérifié** : Era a relancé la simulation
puis l'exécution à 15:14 (manifestes `manifeste-2026-10-10-151423.json` et `-151438.json`), même résultat (4 lues,
5 écrites) et toujours cinq lignes : l'écriture met à jour, elle ne double pas.

## Ce que dit E1 depuis (§ 3, version 2.2)

« …les 7 autres interrompus par l'arrêt du poste. Vérifié en base le 10/10 : quatre rattrapés le 18/09 par les plages de
dates que chaque étape accepte (sauf la séance parisienne du 17/09), un sans perte, deux incomplets (articles des 02 et
03/09 perdus ; taux BCE du 03/09 rattrapé le 10/10). »

## Ce qui reste, dit franchement

- Les articles des 02 et 03/09 sont perdus et le restent.
- La séance du 17/09 manque pour les valeurs de Paris.
- Le poste qui s'éteint coupe la collecte : la tâche planifiée ne reprend pas seule une exécution interrompue.
- Le rôle `rita_lecture` n'est pas utilisable par un agent sur ce poste tant qu'il n'a ni mot de passe ni
  `RITA_DSN_LECTURE` : à régler après le gel.
