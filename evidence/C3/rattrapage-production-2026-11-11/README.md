# Rattrapage des cours et des taux en production, 11/11/2026

Preuve constituée le soir même, à partir de la sortie du serveur : `sortie-serveur-2026-11-11.txt` (cinq connexions,
dans l'ordre), et de deux captures d'écran de la production.

## Le constat du matin

Le 11/11 à 08 h 43 UTC, avant tout rattrapage, la base de production était restée au 06/11 :

- les 106 valeurs au statut `OK` avaient toutes leur dernière séance le 2026-11-06 (liste complète, session 2) ;
- aucune cotation du 2026-11-11 ; dernière séance 2026-11-06, 281 383 lignes dans `cotation` ;
- les cinq devises (CHF, EUR, GBP, JPY, USD) au 2026-11-06.

Ce n'était pas une panne : le serveur n'a toujours aucune collecte planifiée des cours, ils ne changent que par ce
rattrapage à la main (constat du 08/11, `../rattrapage-production-2026-11-08/README.md`). La vigie n'avait pas encore
alerté : le 11/11, le retard était de 3 jours ouvrés, dans la zone orange ; le rouge commence à 4
(`monitorage/fraicheur.py`).

## Deux essais sans rien écrire

À 08 h 28 UTC (session 1), puis à 17 h 33 UTC (session 3), la ligne qui garde le nom du réseau Docker dans `RESEAU`
n'a pas été passée. La vérification l'a montré (`reseau=` vide), puis Docker a refusé de démarrer le conteneur :
`docker: no name set for network`. Rien n'a été écrit : dernière séance et nombre de lignes identiques avant et après
(`2026-11-06|281383`), cinq devises toujours au 06/11.

La correction : je n'utilise plus de variable pour le réseau. Son nom, `rita-agent_default`, est le même le 08/11 et le
11/11 ; il est écrit en clair dans la commande, et une lecture juste avant (`docker inspect`) vérifie qu'il n'a pas
changé.

## Premier passage, à 18 h 39 à Paris (session 4)

- Passage à blanc : 2 étapes sur 2, 431 cotations lues, 0 écrite.
- Écriture avec `--strict` : 431 écrites, 0 rejetée ; taux : 16 lus, 20 écrits. Manifeste
  `manifeste-2026-11-11-173953.json` (17 h 39 UTC).

| Mesure | Avant | Après |
|---|---|---|
| Dernière séance | 2026-11-06 | 2026-11-11 |
| Lignes de `cotation` | 281 383 | 281 706 (+323) |
| Cotations du passage | | 431 écrites, 0 rejetée |
| Taux de change | cinq devises au 06/11 | cinq devises au 11/11 |

Les chiffres se recoupent. 108 valeurs non radiées sur 4 séances (06, 09, 10 et 11/11) donnent 432 lignes ; il en
manque une, CRI.PA au 11/11, d'où 431. Les nouvelles lignes : 108 × 3 − 1 = 323, exactement l'écart du total. Les 108
lignes du 06/11 sont relues exprès : la borne de départ est inclusive, pour écraser une séance capturée avant la clôture
(`pipelines/ingest.py:183-187`). Taux : 4 devises sur 4 jours, plus l'euro à 1 chaque jour (`pipelines/ingest.py:113`),
la même règle que le 08/11 (12 lus, 15 écrits).

Contrôle par statut, pour les valeurs non radiées, au 11/11 :

| Statut | Attendues | Présentes | Manquantes |
|---|---|---|---|
| INCOHERENT | 2 | 2 | 0 |
| OK | 106 | 105 | 1 (CRI.PA) |

**Ce que l'heure changeait.** À 18 h 39 à Paris, New York était ouvert jusqu'à 22 h. Les lignes du 11/11 de FTI et SLB
étaient donc un cours de mi-séance : volumes de 1 040 115 et 2 816 517 titres, environ 30 % des deux séances
précédentes (session 4, suite). Le conseil « après 17 h 35 » de la preuve du 08/11 et de `ETAT.md` ne vaut que pour les
places européennes. Avec FTI et SLB dans l'univers, le rattrapage se fait après 22 h 05, heure de Paris.

## Second passage, à 22 h 04 à Paris (session 5)

- Passage à blanc : 2 étapes sur 2, 108 cotations lues, 0 écrite. 108, c'est 107 valeurs relues au 11/11 plus CRI.PA
  relue depuis le 10/11, d'où « seances du 2026-11-10 au 2026-11-11 ».
- Écriture avec `--strict` : 108 écrites, 0 rejetée ; taux : 16 lus, 20 écrits. Manifeste
  `manifeste-2026-11-11-210436.json` (21 h 04 UTC).
- Total inchangé : 281 706 lignes. Les 108 lignes écrites ont remplacé des lignes déjà là ; la clé primaire
  `(ticker, date_seance)` interdit le doublon et l'insertion met la ligne à jour (`ON CONFLICT DO UPDATE`,
  `pipelines/ingest.py:248-253`).

| Valeur | Clôture du 11/11, 18 h 39 | Clôture du 11/11, 22 h 04 | Volume du 11/11, 18 h 39 | Volume du 11/11, 22 h 04 | Volumes du 09 et du 10/11 |
|---|---|---|---|---|---|
| FTI | 65,50 | 65,39 | 1 040 115 | 2 120 215 | 3 551 800 et 3 435 800 |
| SLB | 51,01 | 50,95 | 2 816 517 | 5 689 273 | 9 652 500 et 9 370 600 |

Ce qui est prouvé : les lignes de mi-séance ont été remplacées, sur la même ligne, sans doublon. Ce qui ne l'est pas :
que ces chiffres soient définitifs. Les volumes du 11/11 restent autour de 60 % des deux séances précédentes et ne sont
pas arrondis à la centaine, contrairement aux séances complètes de ce tableau. Deux explications tiennent : une séance
plus calme (le 11/11 est un jour férié aux États-Unis où la bourse est ouverte et le marché obligataire fermé), ou un
volume que le fournisseur n'avait pas encore consolidé quatre minutes après la clôture. Le prochain rattrapage relira
le 11/11 (borne inclusive) et tranchera, sans manipulation de plus.

## CRI.PA, sans cotation du 11/11

À 22 h 04, soit 4 h 30 après la clôture de Paris, le fournisseur ne donnait toujours pas de séance du 11/11 pour CRI.PA.
Ses volumes des 09 et 10/11 sont faibles (4 522 et 13 359 titres) ; l'écran de détail annonce « échangé par jour
(20 séances) : 75,5 k EUR », soit environ 10 000 titres par jour au cours de 7,68 EUR. Une journée sans aucun échange
paraît donc peu probable, et une publication tardive du fournisseur plus probable. Ce n'est pas prouvé. Le prochain
passage repartira du 10/11, dernière séance de CRI.PA, et prendra le 11/11 s'il existe.

## Les deux valeurs INCOHERENT

L'écart entre les 106 valeurs `OK` et les 108 valeurs collectées, ce sont ALJXR.PA et STLAP.PA (session 4, suite). Leur
collecte est voulue : « Exclure sans supprimer », elles sont « conservées avec leur cause » (`db/schema.sql:62-64`),
causes mesurées dans `db/importer.py:57-60` (STLAP.PA : 1 142 clôtures hors bornes ; ALJXR.PA : cours maximal de
7 156 748, un regroupement d'actions rétro-ajusté par le fournisseur, `../preuve-artefact-reverse-split.md`). La collecte
n'écarte que les valeurs radiées (`pipelines/ingest.py:208`).

La limite est ailleurs : la vigie ne surveille que les valeurs au statut `OK` (`db/fraicheur_par_valeur.sql`), alors que
la valorisation du portefeuille ne filtre pas sur le statut (`db/requetes.sql:48-50`). Si le cours d'une valeur
`INCOHERENT` cessait d'arriver, rien ne m'alerterait. Le 11/11, les deux ont leur séance du jour ; je le contrôle à la
main après chaque rattrapage, avec la requête par statut ci-dessus.

## Le contrôle à l'écran

Après le second passage, écran Indicateurs de la production, avec ma clé :

- `capture-indicateurs-2026-11-11.png` : « Carte des performances : cours du 11/11/2026 », « 108 valeurs · 3 cotations
  périmées masquées ». Les trois masquées sont les valeurs radiées (ELE.PA, GTO.PA, ZC.PA, derniers cours en 2018 et
  2019) : une cotation est dite périmée au-delà de 40 jours (`indicateurs/socle.py:42`). Le message « Vous êtes trop
  près de votre écran. », en bas de l'image, vient du système de mon poste, pas de RITA ; il cache une partie de la
  ligne AKW.PA.
- `capture-detail-cri-2026-11-11.png` : le détail de CRI.PA annonce « cours du 10/11/2026 : 7,68 EUR », la valeur de la
  base (clôture du 10/11 : 7,6800).

Ce que montrent les deux captures ensemble : la date du titre est celle de la séance la plus récente. Une ligne du
tableau ne porte pas sa propre date ; CRI.PA y figure avec son cours du 10/11, sous un titre au 11/11, sans être
signalée (un jour de retard est loin du seuil de 40 jours, pensé pour les valeurs radiées). Le détail de la valeur, lui,
donne la vraie date.

## Ce qui a été retiré de la sortie

La bannière de connexion du serveur et les cinq lignes « Last login », qui portent l'adresse IP de connexion (une donnée
personnelle). Rien d'autre : les commandes et les résultats sont ceux du terminal, doublons compris (la requête sur FTI,
SLB et CRI.PA a été lancée deux fois à la session 5). Aucun mot de passe n'apparaît : la vérification n'en montre que la
présence (`mot_de_passe=present`).

## Limites

- Toujours aucune collecte planifiée des cours en production. Prochain rattrapage utile : la veille du jury (01/12),
  après 22 h 05 à Paris.
- Le guide (`docs/exploitation.md`, section « Rattraper les cours et les taux en production, à la main ») a le même
  piège que ce matin : les étapes 6 et 7 utilisent `"$RESEAU"`, et l'étape 4 ne dit de s'arrêter que si le mot de passe
  est absent, pas si le réseau est vide. Correction après l'oral blanc, test d'abord.
- Chiffres du 11/11 de FTI et SLB non prouvés définitifs ; CRI.PA sans séance du 11/11 (voir plus haut).
- La vigie ne surveille pas les deux valeurs `INCOHERENT`, qui comptent dans la valorisation.
- Le bandeau de fraîcheur conseille toujours « Vérifier la collecte de 19h00 », qui ne concerne que le poste
  (limite déjà notée le 08/11).
