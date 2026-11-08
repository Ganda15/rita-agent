# Rattrapage des cours et des taux en production, 08/11/2026

Preuve constituée le soir même, à partir de la sortie du serveur : `sortie-serveur-2026-11-08.txt`.

## Le constat

Le 08/11 vers 18 h 50 (heure de Paris), l'écran Mon portefeuille de la production annonçait « 2 jours ouvrés de
retard », dernière séance du 04/11/2026, et l'écran Indicateurs « cours du 04/11/2026 ».

Ce n'était pas une collecte arrêtée :

- la tâche planifiée du poste a tourné chaque soir (`logs/collecte-2026-11-03.log` à `collecte-2026-11-07.log` :
  6 étapes sur 6, code de sortie 0, séances jusqu'au 06/11), mais elle écrit dans la base **du poste** ;
- sur le serveur, aucune collecte planifiée des cours (constat du 04/11, `ETAT.md`) : les cours de production ne
  changent que par le rattrapage à la main ; le précédent datait du 04/11, 22 h 17 ;
- `/health` de la production annonçait le commit `770d440`, celui de la livraison du 08/11.

## Le premier passage à blanc a échoué, sans rien écrire

L'étape 3 du guide lisait l'adresse de la base dans le conteneur de l'API. Depuis la carte #76 (en production le 07/11),
ce conteneur ne l'a plus : l'API lit la base avec `rita_api`, et le guide lui-même attend `absente` à cette question
(`docs/exploitation.md`, « Le rôle de l'API en production »). La variable est revenue vide (`utilisateur=` à l'étape 4),
la collecte a visé la base locale par défaut et s'est arrêtée sur `psycopg2.OperationalError`. Aucune ligne écrite :
la dernière séance est restée au 04/11 jusqu'au passage suivant.

## La correction, puis le rattrapage

- Adresse au format clé=valeur, sans mot de passe : `host=postgres port=5432 dbname=rita user=rita`.
- Mot de passe du propriétaire dans `PGPASSWORD`, lu dans le conteneur de la base (la valeur que Compose y a mise),
  jamais affiché : la vérification n'en montre que la présence (`mot_de_passe=present`).
- Passage à blanc : 2 étapes sur 2, 325 cotations lues, 0 écrite. Puis écriture avec `--strict` (manifeste
  `manifeste-2026-11-08-181207.json`, 18 h 12 UTC, soit 19 h 12 à Paris).

| Mesure | Avant | Après |
|---|---|---|
| Dernière séance | 2026-11-04 | 2026-11-06 |
| Lignes de `cotation` | 281 166 | 281 383 (+217) |
| Cotations du passage | | 325 écrites, 0 rejetée ; 108 séances déjà présentes réécrites (325 - 217) |
| Taux de change | cinq devises au 04/11 | cinq devises au 06/11 ; 15 écrits (4 devises sur 3 jours, plus l'euro à 1 chaque jour) |
| Statistiques | | `ANALYZE` sur `cotation` et `taux_change` |
| Variables de session | | effacées, mot de passe compris |

Pourquoi le 06/11 et pas le 08/11 : les 07 et 08/11 sont un samedi et un dimanche, sans séance ; la BCE ne publie pas
de taux ces jours-là.

## Ce qui a été retiré de la sortie

La bannière de connexion du serveur et la ligne « Last login », qui porte l'adresse IP de connexion (une donnée
personnelle). Rien d'autre : les commandes et les résultats sont ceux du terminal. Aucun mot de passe n'apparaît, ni
à l'écran ni dans les commandes.

## Limites

- Toujours aucune collecte planifiée des cours en production : ils vieillissent de nouveau dès la clôture du lundi
  09/11. Prochains rattrapages utiles : la veille de l'oral blanc et la veille du jury, après 17 h 35.
- Le bandeau de fraîcheur conseille « Vérifier la collecte de 19h00 » : cette collecte ne concerne que le poste. En
  production, la formulation envoie au mauvais endroit ; correction à faire plus tard, test d'abord.
- La décision du 06/11 (aucune écriture en production avant l'oral blanc) a été levée le 08/11 pour ce rattrapage.
- Contrôle à l'écran avec la clé, après le rattrapage : pas fait au moment où cette preuve est écrite.

Guide corrigé : `docs/exploitation.md`, section « Rattraper les cours et les taux en production, à la main », étapes
3 et 4 ; tests : `tests/test_exploitation_doc.py`.
