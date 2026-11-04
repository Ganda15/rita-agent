# C3 · Preuve : Viridien en production (commencée le 04/11/2026, écrite au fil de l'opération)

Plan suivi : [`docs/PLAN-VIRIDIEN-PRODUCTION.md`](../../docs/PLAN-VIRIDIEN-PRODUCTION.md). Correction locale :
[`preuve-correction-viridien-2026-11-04.md`](preuve-correction-viridien-2026-11-04.md).

| Statut | État au 04/11/2026, 21 h 50 (heure de Paris) |
|---|---|
| Testé en local | **oui** : base locale corrigée et vérifiée cellule par cellule et sur l'écran ; mode `--corrections-seulement` et ses portes testés sur des copies (id 8 à 14) ; suite complète 2 180 réussis, 60 sautés, 2 xfailed, deux fois (la seconde avec Azure injoignable) ; **répétition sur la sauvegarde S1 de la production : 0 contrôle en échec** (§ 4) |
| Déployé | **oui** (04/11, 20 h 22 UTC) : `8ecc5a7`, image `rita-api@sha256:9f6f5654…`, § 7 |
| Vérifié en production | **oui** : fichiers servis 63 sur 63 ; B2 puis S2 comparée à S1, exactement 4 cellules ; API et MCP avec la clé, 0 échec ; écrans Portefeuille et Indicateurs et leurs deux graphiques, captures d'Era (§ 7 et 8). Cours de production toujours au 27/10 : la fraîcheur est hors de cette correction |

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

## 5. L'intervention A et B (accord d'Era : « go a+b », 04/11/2026 vers 19 h 48, heure de Paris)

Accord donné sur la demande regroupée (plan, § 0). Décisions lues dans cet accord : l'exception gitleaks de la clé de test
simulée fait partie de A, donc acceptée avec A ; le correctif de la passerelle MCP n'a pas été demandé, il n'est **pas**
livré (proposition gardée sur une branche locale, `db3c709`) ; la lecture L3 des journaux du serveur n'a pas été demandée,
elle n'est pas faite.

**Départ** : production à `2310f87` ; PR #179 (`refonte-interface` vers `develop`, 6 contrôles sur 6) fusionnée par l'agent
après l'accord : `develop` à `55b9687`, arbre `ba74608177faac9676ea01aa2ade848bb4d9f001`, celui du commit relu `5318d11`.
PR #180 (`develop` vers `main`) ouverte : 96 fichiers (les 93 comptés plus les 3 du correctif gitleaks).

**Correctif MCP** (décision d'Era, après la fusion de #179) : PR #181 (`proposition-passerelle-nombres` vers `develop`,
2 fichiers, hors image), puis #180 se met à jour et rejoue sa CI et sa revue sur le commit qui contient le correctif.

**Revue automatique de #180 sur `55b9687`** : une trouvaille P2 (Codex), `frontend/commun.js:99` : une page restaurée par le
cache de navigation (bouton Retour) ne relit pas le mode simulation activé entre-temps sur un autre écran. Évaluée : chaque
page affiche son propre mode par sa mention ; aucune donnée fausse, aucune fuite ; décision laissée à Era.

## 6. Fraîcheur : lecture L3 du serveur (accord d'Era, lecture seule, 04/11/2026 à 18 h 51 UTC)

Gardes vérifiées en tête : `lecture_seule=on role=rita_lecture`. Constats, lus sur le serveur et non déduits :
dernière séance 27/10 pour les 7 positions ouvertes et dernier taux 27/10 pour les 5 devises (280 518 cotations) ; dernière
collecte d'articles le 27/10 à 15 h 46 UTC ; **9 manifestes** en tout dans `/root/rita-deploy/rapports` : les ingestions
d'articles lancées par GitHub, et **un seul rattrapage des cours et des taux, le 27/10 à 15 h 43 UTC** (simulation, puis
5 508 cotations et 255 taux écrits) ; **aucun manifeste depuis le 27/10 à 15 h 45 UTC** ; **aucune tâche planifiée de
collecte** (aucun fichier cron ne la nomme ; les minuteries systemd sont celles du système) ; journal des opérations : dernière
ingestion le 27/10 à 16 h 50 (heure de Paris, passage 40534178721), dernière livraison le 03/11 à 22 h 40 (`f36dda84…`).
Petit défaut du script de lecture : l'`awk` de la liste des minuteries a échoué sur la ligne de résumé finale de
`systemctl`. **Lecture corrigée** (même accord, 04/11 à 19 h 17 UTC, `lecture-L3-planification-production-2026-11-04.txt`) :
18 minuteries systemd, toutes du système (apt, logrotate, sysstat...), aucune unité dont le nom contient « rita » ; aucun
fichier cron qui cite la collecte ou RITA, crontab de root sans ligne active, aucun travail `at` ; conteneurs : `rita-api-preprod`
(depuis le 03/11) et `rita-postgres-preprod` (depuis le 20/08), les autres appartiennent à d'autres projets, aucun ne collecte.
Période couverte par les journaux de RITA sur le serveur : journal des opérations du 14/10 au 03/11 (47 lignes : 39
livraisons, 2 retours arrière, 6 ingestions) ; manifestes de collecte du 16/10 au 27/10 (dossier des rapports créé le 16/10).
**Conclusion, sans aller au-delà des preuves** : au 04/11, aucune planification de collecte n'est trouvée sur le serveur ; sur
la période couverte par les journaux (depuis le 14/10), les cours n'y sont arrivés qu'une fois, par le rattrapage à la main du
27/10 ; avant le 14/10, aucun journal du serveur ne permet de dire ce qui a tourné. La phrase « La collecte ne tourne plus »
du bandeau est une déduction du code (`monitorage/fraicheur.py`), pas une lecture de journal.

## 7. A puis B, exécutés (04/11/2026, plan validé par Era ; sorties brutes dans `sorties-production-2026-11-04/`)

**Correctifs intégrés avant la livraison**, chacun sur sa PR vers `develop`, fusionnée par Era : #181 (passerelle MCP),
#182 (mode simulation au retour par le cache d'aller-retour, plus l'attente corrigée d'un test du briefing), #183 (sonde du
cache sur une page témoin). CI de #180 sur son contenu final `91b2971` : tous les contrôles verts, les huit tests du cache
exécutés et réussis ; revue Claude verte sans nouvelle trouvaille ; **revue Codex non relancée sur cette version** (sa
dernière revue de #180 porte sur `55b9687` ; #181, #182 et #183 ont chacune la leur, sans trouvaille).

**A, interface déployée : réussi.** Fusion de #180 par Era (20 h 12 UTC) : commit `8ecc5a7`, arbre
`19e38f035abbfe5a78c6d10e7bf88b9dd9e7cc2d`, identique à l'arbre relu. Livraison verte (passage 41904329612, `deployer` de
20 h 18 à 20 h 22 UTC) ; image publiée `ghcr.io/ganda15/rita-api@sha256:9f6f56547c74af86b5e32afec192e6a8cb883d8ee43337cd300d2277e96eb2a9`,
celle du conteneur en service (lue sur le serveur avant B1) ; `/health` annonce `8ecc5a7`, construit à 20 h 16 UTC.
Fichiers réellement servis par l'adresse de production : **63 contrôles réussis, 0 échec** (avant : 11 réussis, 16 échecs) ;
`Cache-Control: no-cache`, chaque script appelé avec sa version, chaque fichier servi identique à celui de `8ecc5a7`.

**Avant B1 : données inchangées depuis S1.** Empreinte de chaque table (nombre de lignes et empreinte des lignes triées par
clé, en UTC), même requête sur la production et sur S1 restaurée : 13 lignes sur 13 identiques. Valeurs des quatre cellules
avant : `quantite` 120,0000 ; `pru` 1,8500 ; `importe_le` 2026-08-20 11:03:00.621572 UTC ; `nom_officiel` CGG BS.

**B1, à blanc : réussi.** Image du conteneur vérifiée (celle de A), utilisateur `rita`, bilan 1 et 1, tout annulé ; relecture
des empreintes après B1 : 13 sur 13 identiques à S1, rien n'a été écrit.

**B2, réel : réussi.** 20 h 27 min 37 s à 20 h 27 min 39 s UTC, compteurs exigés 1 et 1, code 0.

**S2 et comparaison : réussi.** Sauvegarde `rita-prod-S2-apres-correction-2026-11-04-212755.dump` (5 591 689 octets, SHA-256
`453e47888d3dde4e16bf531c31784377723c72b75ad372ee00781d6377740fc6`), mêmes contrôles que S1. S1 et S2 restaurées et comparées
cellule par cellule : **exactement 4 différences** (`quantite` 120 → 1, `pru` 1,85 → 185, `importe_le` → 2026-11-04 20:27:39 UTC,
`nom_officiel` CGG BS → VIRIDIEN) ; toutes les autres tables identiques, dont 280 518 cotations, 2 166 articles et les journaux.
Vue recalculée avec les cours présents en production (tous du 27/10) : VIRIDIEN 1 × 185, cours 96,15 €, valorisation 96,15 €,
**-48,03 %**, poids **0,46 %** ; **total 20 835,20 € sur 7 lignes** ; les six autres lignes gardent quantités, prix de revient,
cours, valorisations et performances ; seuls leurs poids changent (AI.PA 33,69 %, MC.PA 22,33 %, OR.PA 16,59 %, SU.PA 11,65 %,
SAN.PA 9,03 %, BNP.PA 6,24 %).

**Non vérifié par l'agent, à faire par Era avec sa clé** : les écrans Portefeuille et Indicateurs (dont les deux graphiques)
et la passerelle MCP contre la production. **Collecte : non actualisée** par A ni par B ; les cours de production restent au 27/10.

**MCP et API avec la clé, contre la production : réussi** (Era, 04/11/2026 à 21 h 36, heure de Paris ; `verifier_mcp_production.py`,
passerelle de `main` `8ecc5a7`, clé saisie sans écho). Les trois routes appelées en HTTPS sur l'adresse de production répondent
200 : `rita_fraicheur` OK, statut rouge, dernière séance 2026-10-27 ; `rita_portefeuille` OK, **verrou de démonstration accepté**
(le défaut de #152, corrigé par #181, est levé en production), 7 positions, total 20 835,20 € ; VIRI.PA VIRIDIEN 1,0000 × 185,0000,
cours 96,15 du 27/10, valorisation 96,15, -48,03 % ; les six autres lignes identiques à la vue de S2 ; `rita_indicateurs` OK
(VIRI.PA) ; 0 échec. Ces appels ont laissé des lignes dans `mcp_calls`, comme prévu.

**Reste à vérifier par Era** : les écrans Portefeuille et Indicateurs de la production et leurs deux graphiques.

## 8. Écrans de la production vérifiés par Era avec sa clé (04/11/2026, 21 h 41 à 21 h 48, heure de Paris)

Captures dans `captures-viridien-production/` :

- **21 h 41, Portefeuille resté sur « Chargement du portefeuille… »** (`2-portefeuille-chargement-transitoire-2026-11-04.webp`).
  Diagnostic, sans toucher au serveur : les journaux de l'API depuis la livraison ne montrent aucune erreur, et tous les appels
  de la page ont reçu 200 (`/donnees/portefeuille` 8 fois, `/donnees/indicateurs-portefeuille` 7, `/donnees/fraicheur` 8) ; les
  trois routes répondent en moins de 0,2 s ; mêmes en-têtes et mêmes scripts servis que sur le poste, aucune politique CSP. Le
  code livré, lancé sur le poste contre S2 restaurée, affiche le portefeuille sans erreur JavaScript. Après un rechargement, la
  page s'affiche (capture de 21 h 48). État transitoire, **non reproduit** ; sa cause n'est pas établie.
- **21 h 46, Indicateurs** (`3-indicateurs-apres-2026-11-04.webp`) : nouvelle interface, 108 valeurs, 3 cotations périmées
  masquées, recherche, tri, carte des performances au cours du 27/10/2026.
- **21 h 48, Portefeuille** (`4-portefeuille-apres-2026-11-04.webp`) : nouvelle interface ; valeur totale **20 835,20 €**,
  7 lignes ouvertes, 0 ligne sans taux, 0 position close ; **les deux graphiques lisibles** : anneau des poids (AIR LIQUIDE
  33,7 %, LVMH 22,3 %, OREAL 16,6 %, conformes aux poids attendus) et barres des gains et pertes (VIRIDIEN -48,03 %, qui n'écrase
  plus les autres lignes) ; aucune alerte « performance hors du commun » ; bandeau rouge de fraîcheur toujours présent, attendu.

**Statuts finaux** : testé en local, oui ; déployé, oui (`8ecc5a7`) ; vérifié en production, oui (fichiers servis, base,
API et MCP avec la clé, écrans). **La fraîcheur des cours reste à traiter à part** : dernière cotation de production le
27/10/2026 ; un rattrapage, ou une collecte planifiée sur le serveur, est une décision d'Era, non prise ce soir.
