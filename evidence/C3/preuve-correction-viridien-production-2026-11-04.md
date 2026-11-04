# C3 · Preuve : Viridien en production (commencée le 04/11/2026, écrite au fil de l'opération)

Plan suivi : [`docs/PLAN-VIRIDIEN-PRODUCTION.md`](../../docs/PLAN-VIRIDIEN-PRODUCTION.md). Correction locale :
[`preuve-correction-viridien-2026-11-04.md`](preuve-correction-viridien-2026-11-04.md).

| Statut | État au 04/11/2026, 19 h 30 (heure de Paris) |
|---|---|
| Testé en local | **oui** : base locale corrigée et vérifiée cellule par cellule et sur l'écran ; mode `--corrections-seulement` et ses portes testés sur des copies (id 8 à 14) ; suite complète 2 180 réussis, 60 sautés, 2 xfailed, deux fois (la seconde avec Azure injoignable) ; **répétition sur la sauvegarde S1 de la production : 0 contrôle en échec** (§ 4) |
| Déployé | **non** : la production sert le commit `2310f87` ; le code de la correction est commité (`1dd8572`) et poussé sur `refonte-interface`, le plan l'est en `ca5b4f8`, rien n'est fusionné dans `main` |
| Vérifié en production | **non** : aucune écriture faite ni autorisée ; seule la lecture S1 a été faite, sur l'accord d'Era |

## 1. Avant (lecture seule et écran public)

**Diagnostic en lecture seule, 04/11/2026 vers 17 h UTC** (une session SSH, `SELECT` en session lecture seule) : la ligne
`VIRI.PA` a l'id 14, 120 × 1,85, achat du 14/10/2021, ouverte, `importe_le` du 20/08/2026 11 h 03 UTC ; la valeur s'appelle
`CGG BS` ; la vue rend Viridien à 96,15 € (27/10/2026), +5 097,30 %, 11 538,00 €, total 32 277,05 € sur 7 lignes.

**Écran public, capture d'Era du 04/11/2026 au soir** (`https://178-104-184-125.sslip.io/index.html`, ancienne interface, avec sa
clé) : « Total du portefeuille : 32 277,05 € · 7 lignes » ; « Portefeuille valorisé, cours du 2026-10-27 » ; ligne VIRI.PA « CGG BS »,
120, 1,85, cours 96,15, investi 222,00 €, valorisation 11 538,00 €, **+5 097,30 %**, poids **35,75 %** ; bandeau rouge « 6 jours
ouvrés de retard, dernière séance du 27/10/2026. La collecte ne tourne plus. » Les sept lignes égalent celles du diagnostic.
Fichier de la capture : à déposer par Era dans `captures-viridien-production/1-avant-production-2026-11-04.png` (l'agent n'y a pas
accès ; une première copie faite par erreur depuis une autre capture, celle du port 8000 local, a été supprimée aussitôt).

Le retard des cours et l'archive décalée d'un jour (plan § 7) sont hors de cette correction.

## 2. Préparé le 04/11 au soir, sans contact en écriture avec le serveur

Le plan est réécrit en trois opérations séparées (livraison du code, correction de Viridien, diagnostic de fraîcheur). Fichiers
servis par la production, lus sans clé : 11 contrôles réussis, 16 en échec (aucun `Cache-Control`, scripts sans `?v=`, phrase
témoin absente), l'état « avant » de la livraison. Répétition sur une copie représentative de la production (base jetable) :
0 contrôle en échec, exactement 4 cellules changées, total 20 835,20 € sur 7 lignes, Viridien -48,03 %, poids 0,46 %, rejeu
refusé, retour arrière à l'identique. La lecture complémentaire `lecture_prod_4.sh` est abandonnée : la sauvegarde S1 la remplace.

## 3. À venir, dans l'ordre du plan

Sauvegarde S1 et répétition sur elle : faites le 04/11 (§ 4). Restent, chacune sur son accord : seconde copie protégée de S1 ;
livraison du code (accord A) et vérification des fichiers servis ; passage à blanc puis vrai passage avec compteurs attendus
(accords B1, B2) ; sauvegarde S2 et comparaison cellule par cellule avec S1 ; vérifications API et écran ; captures après.

## 4. S1 : la sauvegarde d'avant correction, et sa répétition (04/11/2026, accord d'Era : « go S1 », S1 seulement)

**Commande sécurisée, essayée d'abord sur le poste** (conteneur jetable, lignes factices, aucun contact avec le serveur) :
nom unique horodaté à la seconde et refus si le nom existe ; dump reçu dans un fichier `.partiel`, renommé seulement si
tout passe ; contrôles et erreurs dans un journal séparé ; empreinte SHA-256 ; fichier en lecture seule, accès limité au
compte Windows d'Era. Cinq essais : cas normal réussi ; même nom refusé, fichier intact ; source absente, échec sans
fichier final ; droit d'écriture ajouté au compte de lecture (sur le conteneur d'essai), arrêt avant le dump, aucun droit
modifié ; restauration complète du dump d'essai, 10 tables identiques. Deux pièges trouvés en chemin : les scripts écrits
sur le poste avaient des fins de ligne Windows (CRLF), que le bash du serveur aurait refusées, convertis et vérifiés
(0 octet CR) ; `sed` sous Git Bash les remettait en place, d'où une conversion octet par octet.

**Le passage** : 04/11/2026, dump de 18 h 16 min 39 s à 18 h 16 min 41 s UTC, une session SSH, lecture seule. Contrôles
faits sur le serveur avant toute lecture de données, sans rien modifier : compte `rita_lecture`, session en lecture seule ;
ni superutilisateur, ni création de rôles ou de bases, ni contournement des règles de lignes ; 15 objets dans le schéma
public, 0 illisible, 0 où le compte pourrait écrire. Résultat : code 0 ;
`D:\KandaWork\RITA_PROJECT\sauvegardes\rita-prod-S1-avant-correction-2026-11-04-191640.dump` (hors du dépôt), 5 591 673
octets, 10 blocs de données, SHA-256 `cb3cd2aee247881d6a4919da1e08dea1e6c4e2604e0f7271a43951792a7bae9a`, lecture seule,
accès limité à `ERAMALINGAM\kanda`. Le disque D: est un disque externe USB (Toshiba) : **seconde copie** faite le même soir
sur le disque interne (C:, SSD NVMe), dans `C:\Users\kanda\RITA-sauvegardes\`, hors OneDrive et hors Git, protégée de la même
façon ; empreinte identique, et conforme à celle notée au moment du dump.

**Restauration complète dans une base jetable** (`postgres:18-alpine`, sur le poste, supprimée ensuite) : code 0. Lignes :
devise 5, valeur 111, alias_valeur 112, position 7, cotation 280 518, taux_change 260, macro_observation 0, article 2 166,
memory_audit 0, mcp_calls 0. Recoupements indépendants : la vue donne 32 277,05 € sur 7 lignes (l'écran de production) ;
280 518 cotations (le chiffre noté après le rattrapage du 27/10, `docs/exploitation.md`) ; 2 166 articles (`/health` de la
production) ; dernière collecte d'articles le 27/10 à 15 h 46 UTC (l'ingestion GitHub du 27/10) ; droits restaurés
conformes à `db/roles.sql`.

**Répétition sur cette restauration** : ligne `VIRI.PA` id 14, 120 × 1,85, `importe_le` 2026-08-20 11:03:00.621572 UTC,
nom `CGG BS`. Instantané de 10 tables sur 10. À blanc : bilan 1 et 1, puis 0 différence. Vrai passage, compteurs exigés
1 et 1 : **exactement 4 cellules** (`quantite` 120 → 1, `pru` 1,85 → 185, `importe_le` de cette ligne ; `nom_officiel`
CGG BS → VIRIDIEN). Vue après : Viridien 96,15 €, -48,03 %, **total 20 835,20 € sur 7 lignes, poids 0,46 %**. Rejeu
refusé (`obtenu (0, 0)`, code 1). Retour arrière gardé : 0 différence sur les 10 tables. **Bilan : 0 contrôle en échec.**

Différences avec la répétition sur la copie représentative : seulement l'`importe_le` de départ (03/10 dans la copie,
20/08 en production) et le nombre de cotations (18 354 contre 280 518, la copie ne gardant que les valeurs détenues) ;
mêmes cellules changées, mêmes chiffres après correction.

Cet accord n'autorise ni la livraison (A), ni la correction (B1, B2), ni aucune restauration dans la base de production.
