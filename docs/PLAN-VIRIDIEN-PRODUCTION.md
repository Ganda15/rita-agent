# Plan : trois opérations en production, séparées (interface, Viridien, fraîcheur des données)

**Statut au 16/11** : réalisé en production le 04/11 (voir `ETAT.md`, 04/11). **Statut d'origine** : à valider par Era. **Aucune écriture sur le serveur avant son accord**, donné séparément pour chaque
opération, et pour chaque étape notée « accord ». Première version le 04/11/2026 (Viridien seul), réécrite le même soir
en trois opérations à la demande de la revue : « Ne mélange pas correction de position et actualisation des cours. »
Preuve de la correction locale : [`evidence/C3/preuve-correction-viridien-2026-11-04.md`](../evidence/C3/preuve-correction-viridien-2026-11-04.md) ;
preuve en production, écrite au fil de l'opération : [`evidence/C3/preuve-correction-viridien-production-2026-11-04.md`](../evidence/C3/preuve-correction-viridien-production-2026-11-04.md).

## 0. La demande de validation regroupée (A et B), 04/11/2026 au soir

Objectif fixé par Era : une seule validation avant les changements en production. Ce paragraphe la résume ; le détail suit.

**Ce qui est déployé (A).** Le contenu de `refonte-interface`, porté par la PR `develop` vers `main`. Dans l'image, par rapport
à la production (`2310f87`) : 7 fichiers Python (`api/main.py`, `agents/analyst.py`, `graph/state.py`, `graph/workflow.py`,
`sources/marches.py`, `src/llm.py`, `db/importer.py`) et 16 fichiers de l'interface ; rien d'autre (§ 1.1). Changements de
comportement : `/briefing` ajoute un bloc `diagnostic` et répond 503 au lieu de 500 quand aucun fournisseur ne répond ;
l'interface est servie en `no-cache` ; le prompt du rédacteur, l'ordre des fournisseurs, le schéma et les rôles ne changent pas.
L'image est construite par la CI à partir du commit de fusion, publiée sous `ghcr.io/ganda15/rita-api:sha-<fusion>` et
transmise au serveur par son empreinte `@sha256` ; contrôle : l'arbre du commit de fusion doit être celui du commit relu.
Le code n'a pas changé depuis la suite complète (2 180 réussis, deux fois, à `6f6e94e`) : seuls quatre documents ont changé.
Contrôle des secrets : la PR #179 était rouge sur `secrets` (gitleaks, 1 trouvaille) ; c'est un faux positif, la clé périmée
simulée `cle-perimee-0123456789` de `tests/test_commun_ui.py` (requêtes interceptées par Playwright), ajoutée aux exceptions
exactes et ancrées de `.gitleaks.toml` selon la convention du dépôt, test d'abord (`tests/test_gitleaks_config.py`, rouge
puis vert) ; gitleaks rejoué sur tout l'historique comme la CI : 695 commits, aucune fuite. **À valider par Era avec A.**

**Ce qui change en base (B).** Exactement 4 cellules (§ 2.1), répétées sur S1, la vraie copie de la production. Chiffres
attendus, calculés avec les cours présents en production (ceux du 27/10), jamais avec le total local :

| Ligne | Valorisation | Poids avant | Poids après |
|---|---|---|---|
| VIRI.PA (VIRIDIEN, 1 × 185,00, cours 96,15, -48,03 %) | 11 538,00 € → 96,15 € | 35,75 % | 0,46 % |
| BNP.PA | 1 300,95 € | 4,03 % | 6,24 % |
| SU.PA | 2 428,00 € | 7,52 % | 11,65 % |
| AI.PA | 7 020,00 € | 21,75 % | 33,69 % |
| OR.PA | 3 455,60 € | 10,71 % | 16,59 % |
| SAN.PA | 1 881,50 € | 5,83 % | 9,03 % |
| MC.PA | 4 653,00 € | 14,42 % | 22,33 % |
| **Total** | **32 277,05 € → 20 835,20 €** | | |

Les poids « avant » sont ceux de l'écran de production, ce qui valide le calcul ; les six autres lignes ne changent pas.

**La fenêtre.** Hors du créneau protégé (7 h 30 à 9 h). Mesuré le 03/11 : 13 minutes de la fusion à la fin du déploiement ;
puis B1 et B2, deux minutes ; puis S2 et les vérifications. Pendant la bascule, la production a déjà répondu 502 environ
7 secondes (14/10). Entre la fin de A et B2, quelques minutes : la nouvelle interface montre encore Viridien à 120 × 1,85.

**Le risque pour MCP.** La passerelle MCP n'est pas dans l'image (aucun `COPY` dans le `Dockerfile`) et aucun client MCP
configuré ne la lance ; chaque appel qu'elle fait à l'API laisse une ligne dans `mcp_calls`, et S1 en compte **0** : elle n'a
jamais appelé la production. A et B ne changent donc rien pour MCP. **Défaut antérieur trouvé le 04/11 en préparant le
contrôle MCP** : `rita_portefeuille` refuse aussi la base locale déjà corrigée. L'API sert les quantités, prix de revient,
cours et montants comme des **textes** (des `Decimal` sérialisés par Pydantic 2 : `"quantite":"15.0000"`), et le contrôle
de cohérence de la passerelle exige des nombres JSON (`_nombre_json`, `passerelle_mcp/serveur.py:156`) ; ses tests lui
donnent des réponses écrites à la main, en nombres, jamais une vraie réponse de l'API. Le défaut date de la recette #152
(`c0ce2b9`, 01/11) et il est déjà dans le code de production : avant comme après A et B, `rita_portefeuille` refuse, sans
rendre aucune donnée (le refus est sûr, pas une fuite). `rita_fraicheur` et `rita_indicateurs` fonctionnent. Le corriger est
une décision d'Era (§ 4) : un changement de la passerelle seule, hors de l'image, test d'abord.

**Les conditions d'arrêt.** Une case rouge sur la PR : pas de fusion. Arbre du commit de fusion différent de celui relu :
arrêt. Déploiement en échec : le serveur remet lui-même l'ancienne image ; arrêt, B n'est pas lancé. Après A, `/health` ou
fichiers servis non conformes : retour arrière de A, B n'est pas lancé. B1 ou B2 sans le bilan exact 1 et 1 : rien n'est
validé, arrêt. S2 différente de S1 par autre chose que les 4 cellules (hors ajouts permis) : retour arrière de B.

**Le retour arrière, sans effacer de données légitimes.** B : le bloc `DO` gardé (§ 2.7), qui ne vise que les deux lignes
par leurs valeurs et remet la valeur d'origine lue dans S1 ; répété sur S1 : retour exact. A : le workflow « Retour arrière »,
qui remet l'image précédente sans toucher aux données. Restaurer S1 en entier est exclu. Sauvegardes : S1 sur le disque USB
(D:) et une copie sur le disque interne (C:), même empreinte.

**Ce que l'accord couvre** : fusion de la PR vers `main` (A), lecture de l'empreinte de l'image sur le serveur, B1 puis B2,
S2 et sa comparaison avec S1, vérifications. Era vérifie l'écran et l'API avec sa clé, et la passerelle MCP s'il le souhaite.
Hors accord : toute collecte ou synchronisation des cours (§ 3) ; la lecture L3 reste à part.

| Opération | Ce qu'elle change | Accords | Dépend de |
|---|---|---|---|
| 1. Livrer la nouvelle interface | le code servi (image, écrans, API, importateur) ; aucune donnée | **A** (fusion) | rien |
| 2. Corriger Viridien | 4 cellules de la base, rien d'autre | **S1** (sauvegarde avant), **B1** (à blanc), **B2** (vrai passage), **S2** (sauvegarde après) | 1 vérifiée |
| 3. Diagnostiquer la fraîcheur | rien : lecture seule | **L3** (lecture du serveur) | rien |

Ordre proposé : 3 quand Era veut (indépendante) ; puis S1 et la répétition sur le poste ; puis A ; puis B1 et B2 juste
après A (voir § 2.6) ; puis S2 et les vérifications. **Aucun rattrapage des cours entre S1 et S2** : il changerait les
chiffres attendus et mêlerait les deux sujets.

## 1. Opération 1 : livrer la nouvelle interface, et vérifier ce qui est réellement servi

### 1.1 Ce qui part, mesuré le 04/11 au soir

- **Version** : `refonte-interface` à `5398331`, identique sur le poste et sur GitHub. La production sert `2310f87` (tête de
  `main`, PR #178), image construite le 03/11 à 21 h 33 UTC (`/health`, lu sans clé).
- **Contenu** : `git diff --stat 2310f87 5398331` : 93 fichiers, 27 539 lignes ajoutées, 543 retirées. Par dossier : 30 dans
  `evidence/`, 29 dans `tests/`, 16 dans `frontend/`, 3 dans `specs/`, 3 à la racine (`ETAT.md`, `CONTINUITE.md`, `README.md`),
  et 10 fichiers de code hors de l'interface, chacun relié à sa tâche :

| Fichier | Tâche | Effet |
|---|---|---|
| `src/llm.py` | refonte, tâche 1 | la cascade dit quel fournisseur a répondu |
| `agents/analyst.py`, `graph/state.py`, `graph/workflow.py` | tâche 2 | le graphe garde qui a rédigé le briefing |
| `api/main.py`, `sources/marches.py` | tâches 3 et 5 | `/briefing` renvoie un bloc `diagnostic` et un 503 si aucun fournisseur ne répond ; l'interface est servie en `no-cache` ; la place de cotation est nommée |
| `scripts/versionner_interface.py` | tâche 5 | écrit l'empreinte de chaque script et feuille de style dans les pages |
| `db/importer.py`, `data/positions-exemple.csv`, `passerelle_mcp/jeu_demo_attendu.csv` | Viridien | modes ciblés et leurs portes, ligne d'exemple corrigée, jeu attendu de la passerelle aligné |

- **Rien d'autre** : `git diff --name-only 2310f87 5398331` ne liste aucun `Dockerfile`, `docker-compose.yml`, fichier de
  dépendances, `db/schema.sql`, `db/roles.sql`, fichier `.sql`, `.github/` ni `deploy/`. Aucune migration de base.
- **Fusion** : `git merge-tree` de `main` et `refonte-interface` : aucun conflit. `develop` n'a aucun commit absent de la
  branche ; `main` n'a, par rapport à `develop`, que des commits de fusion.
- **Ce qui ne part pas** : les tâches 10 (simulation) et 11 de la refonte. Aucune page ne pointe vers une page absente :
  les cinq pages existent et leurs liens de navigation visent ces cinq pages. **Écart au plan** : la refonte prévoyait la
  production à la tâche 12 ([`plan.md`](../specs/001-refonte-interface/plan.md)) ; livrer maintenant est une décision d'Era (§ 4).

### 1.2 Les étapes

1. PR `refonte-interface` vers `develop`, puis PR `develop` vers `main` : sept contrôles exigés, dont `pytest`, `evals` et la revue.
2. **Accord A** : fusion par Era. **Toute fusion dans `main` redéploie la production.**
3. Le job `deployer` attend la fin du créneau protégé (7 h 30 à 9 h) s'il y tombe, puis déploie. Lire la CI et garder le lien de l'exécution.
4. Retour arrière si besoin : [Revenir à la version précédente en production](exploitation.md#rollback-production).

### 1.3 Vérifier les fichiers réellement servis

Un script de vérification, en lecture seule (des GET publics, sans clé), contrôle pour chacune des cinq pages : statut 200,
en-tête `Cache-Control: no-cache`, chaque script et feuille de style appelé avec `?v=<version>`, fichier servi à cette adresse
d'empreinte égale à la version annoncée (même calcul que `scripts/versionner_interface.py`), et identique au fichier du
commit attendu ; puis `/health` annonce ce commit, et la page Indicateurs contient « Volatilité annualisée (20 séances) ».

| Cible, 04/11/2026 au soir | Résultat |
|---|---|
| production actuelle, comparée à `2310f87` | **11 contrôles réussis, 16 en échec** : commit et cinq pages identiques à `2310f87` ; cinq pages sans `Cache-Control`, dix liens de script sans `?v=`, phrase témoin absente. C'est l'état « avant » |
| serveur local de la nouvelle interface, comparé à `5398331` | tout réussit, sauf `/health`, qui répond `inconnu` : un serveur lancé à la main n'est pas une image construite par la CI |

**Attendu après A** : zéro échec contre le commit de fusion. Le script distingue donc l'ancienne version de la nouvelle.

## 2. Opération 2 : corriger Viridien, avec sauvegarde et répétition

### 2.1 Les changements exacts en base

| Table | Ligne | Champ | Avant | Après |
|---|---|---|---|---|
| `position` | `VIRI.PA` achetée le 14/10/2021 (id 14 en production) | `quantite` | 120,0000 | 1,0000 |
| | | `pru` | 1,8500 | 185,0000 |
| | | `importe_le` (cette ligne seulement) | 20/08/2026 11 h 03 UTC | l'heure de la correction |
| `valeur` | `VIRI.PA` | `nom_officiel` | CGG BS | VIRIDIEN |

Rien d'autre, dans aucune table : aucune cotation, aucun taux, aucune autre position, aucun alias, aucune clôture.

**Chiffres attendus**, avec les cours de production du 27/10 (relevés de 16 h 43, pas des clôtures) : Viridien `VIRIDIEN`,
1 × 185,00, cours 96,15 €, valorisation 96,15 €, **-48,03 %**, poids **0,46 %** ; total **20 835,20 €** sur 7 lignes
(32 277,05 € de l'écran actuel, moins 11 538,00 €, plus 96,15 €). Ils diffèrent du local (21 409,85 €, -50,43 %) parce que
les cours diffèrent, pas la correction.

### 2.2 S1 et S2 : les sauvegardes (accords S1 et S2, des lectures de la production)

**S1 est faite** (04/11/2026, 18 h 16 UTC, accord d'Era) : résultats dans la preuve, § 4. S2 suit la même procédure, après B2.

💻 Sur le poste, une commande par sauvegarde, `-Etape S1` (avant correction) ou `-Etape S2` (après correction) :
`sauvegarde_production.ps1`, avec sa partie distante `sauvegarde_distante.sh`, envoyée au serveur par `ssh ... bash -s`.

- **Deux noms distincts, jamais d'écrasement** : `rita-prod-S1-avant-correction-<date>-<heure à la seconde>.dump` et
  `rita-prod-S2-apres-correction-<...>.dump`, dans `D:\KandaWork\RITA_PROJECT\sauvegardes\`, hors du dépôt. Refus si un fichier
  du même nom existe ; le dump arrive dans un fichier `.partiel`, renommé seulement si tous les contrôles passent, sans
  `-Force` (le renommage refuse aussi une cible existante).
- **Le compte et ses droits, vérifiés sans être modifiés** : connexion directe avec le compte de lecture `rita_lecture`
  (`db/roles.sql`, SELECT seul), session en lecture seule ; avant toute lecture de données, le script vérifie sur le serveur
  que le compte n'est ni superutilisateur, ni créateur de rôles ou de bases, qu'il lit tous les objets du schéma public et
  qu'il ne peut écrire dans aucune table. Sinon, arrêt sans sauvegarde : aucun droit n'est jamais accordé pour « que ça passe ».
- **La réussite de l'export et du transfert** : code de sortie de `pg_dump` remonté par `ssh` puis par `cmd` ; fichier non vide
  et signé `PGDMP` ; table des matières lue par `pg_restore` (version 18, celle de la production) ; empreinte SHA-256 écrite à
  côté. Contrôles et erreurs dans un journal séparé (`.journal.txt`), jamais dans le dump. Puis **restauration complète** dans
  une base jetable (§ 2.3), la seule preuve qu'une sauvegarde sert.
- **Protection** : fichiers en lecture seule, accès limité au compte Windows d'Era (`icacls`, héritage retiré) ; **seconde copie
  protégée avant toute écriture en production**, sur un disque choisi par Era, jamais sur un service hors de l'Union
  européenne (OneDrive compris, tant que sa région n'est pas prouvée).
- **Pourquoi passer par `cmd`** : mesuré le 04/11 sur une base jetable aux lignes factices. Redirigé par le `>` de PowerShell
  5.1, le dump gagne 790 octets (réencodé) et `pg_restore` le refuse ; redirigé par `cmd`, il se restaure à l'identique.
- **Essayée sur le poste avant S1**, sans le serveur : cas normal, même nom (refusé), source absente (échec sans fichier
  final), droit d'écriture ajouté au compte sur le conteneur d'essai (arrêt avant le dump), restauration complète identique.

### 2.3 La répétition sur la sauvegarde elle-même (sur le poste, sans contact avec le serveur)

La sauvegarde **est** la vraie copie de la production : la répétition se fait dessus, ce qui remplace la lecture
complémentaire préparée plus tôt (`lecture_prod_4.sh`, abandonnée). Elle est restaurée dans une base jetable
(`postgres:18-alpine`, l'image de la production, publiée sur 127.0.0.1 seulement, supprimée à la fin) ; **rien n'est écrit
dans la base locale du poste (port 5433)**. Contrôles, chacun vérifié par le script lui-même :

1. restauration, code 0 ; instantané de **toutes** les tables (autant de tables dans l'instantané que dans la base) ;
2. passage à blanc : `Positions regroupees : 1`, `Noms officiels : 1`, puis **0 différence** ;
3. vrai passage avec `--attendu-corrigees 1 --attendu-noms 1` : **exactement 4 cellules**, celles du § 2.1 ;
4. chiffres de la vue : ceux du § 2.1 ;
5. rejeu : refusé (`obtenu (0, 0)`), code 1 ;
6. retour arrière gardé (§ 2.7) : **0 différence** avec l'instantané de départ.

**Répétition faite le 04/11 sur une copie représentative de la production**, sans contact avec le serveur : la sauvegarde
locale prise le matin avant la correction locale (111 valeurs, 112 alias), les sept positions renumérotées aux id de la
production (8 à 14), les cours jusqu'au 26/10 et, pour le 27/10, les sept cours que la production affiche. Avant correction,
cette copie donne l'écran de production au centime : 32 277,05 € sur 7 lignes, Viridien 11 538,00 €, +5 097,30 %, poids
35,75 %. Résultat : **0 contrôle en échec**. À blanc, 0 différence ; vrai passage, exactement les 4 cellules (ligne id 14 et
nom de la valeur) ; vue après correction : Viridien 96,15 €, -48,03 %, **total 20 835,20 € sur 7 lignes, poids 0,46 %** ;
rejeu refusé, code 1 ; retour arrière : 0 différence sur les 10 tables. Elle sera rejouée sur S1 avant B1 : seule S1 contient
tout ce que la production contient (articles, journaux, archive des cours).

Le script a d'abord été essayé sur une sauvegarde factice aux mêmes lignes Viridien. **Raté en chemin** : le premier essai ne
comparait qu'une table sur dix (une boucle de lecture dont `docker exec -i` avalait la suite de la liste) et concluait
« 0 différence » après la correction ; corrigé, et le script vérifie désormais le nombre de tables et le nombre de
différences attendu à chaque étape.

**La commande exacte de la production a aussi été jouée dans l'image** construite depuis `5398331`, sur une base jetable
reliée par un réseau Docker : à blanc, la ligne reste 120 × 1,85 « CGG BS » ; vrai passage, 1 × 185 « VIRIDIEN » ; rejeu
refusé, code 1. L'image n'a aucun fichier de données dans `/app/data` (seulement le point de montage de l'index,
`/app/data/chroma`, `Dockerfile:83`) : ce mode n'en lit aucun.

### 2.4 B1 et B2 : la correction en production (après A vérifiée)

🖧 Sur le serveur (`ssh root@178.104.184.125`), depuis `/root/rita-agent` : d'abord les étapes 1 à 4 du
[rattrapage à la main](exploitation.md#rattrapage-cours-production) (image, réseau et adresse de la base gardés en mémoire,
rien n'est affiché ; attendu `utilisateur=rita`). L'image est alors celle livrée par A.

**Accord B1**, passage à blanc, sous le verrou du serveur (le même que la livraison) :

```bash
flock -w 600 /root/rita-deploy/verrou docker run --rm --network "$RESEAU" -e DATABASE_URL "$IMAGE" python -m db.importer --corrections-seulement --a-blanc
```

Attendu : `A BLANC, TOUT EST ANNULE`, `Positions regroupees : 1`, `Noms officiels : 1`, code 0. Sinon, s'arrêter.

**Accord B2**, vrai passage, compteurs exigés :

```bash
flock -w 600 /root/rita-deploy/verrou docker run --rm --network "$RESEAU" -e DATABASE_URL "$IMAGE" python -m db.importer --corrections-seulement --attendu-corrigees 1 --attendu-noms 1
```

Attendu : les mêmes compteurs, code 0. Si un compteur diffère, tout est annulé et la commande sort en code 1. Puis :

```bash
unset DATABASE_URL IMAGE RESEAU
```

### 2.5 S2 et les vérifications, dans l'ordre base, API, écran

| Quoi | Qui | Attendu |
|---|---|---|
| Base : sauvegarde S2 (§ 2.2, `-Etape S2`, accord S2), puis S1 et S2 restaurées dans deux bases jetables et comparées cellule par cellule, toutes tables | l'agent, sur le poste | **exactement les 4 cellules du § 2.1** ; `article`, `memory_audit` et `mcp_calls` peuvent seulement gagner des lignes (ingestion, journaux), une ligne modifiée ou retirée y compte. Essayé sur des sauvegardes factices : 4 différences, réussite ; contre-essai avec une autre position modifiée et un article retiré : échec, 6 différences, code 1 |
| `/health` et fichiers servis | l'agent, sans clé | le commit de la fusion ; le script du § 1.3 sans échec |
| API `/donnees/portefeuille` et `/donnees/indicateurs-portefeuille` | Era, avec la clé de production | les chiffres du § 2.1 |
| Écran public, Portefeuille et Indicateurs | Era, avec la clé | les mêmes chiffres ; plus d'alerte « performance hors du commun » sur Viridien ; deux graphiques lisibles ; rechargement normal, sans Ctrl+F5 |

Le bandeau de fraîcheur restera rouge : les cours s'arrêtent toujours au 27/10. C'est l'objet de l'opération 3, pas de celle-ci.

### 2.6 Entre A et B

La passerelle MCP compare l'API à `passerelle_mcp/jeu_demo_attendu.csv`, qui passe à Viridien corrigé avec A : entre A et
B2, elle refuserait la production. B suit donc A sans attendre.

### 2.7 Le retour arrière

Un bloc `DO` exécuté en une transaction, qui lève une erreur, donc annule tout, si un compteur n'est pas exactement 1 :
remettre `nom_officiel` à `CGG BS`, puis la ligne `VIRI.PA` du 14/10/2021 à 120 × 1,85 avec son `importe_le` d'origine (lu
dans S1), en ne visant la ligne que par ticker, date, quantité et prix de revient, jamais par id. Répété le 04/11 sur des
copies : retour à l'empreinte de départ ; rejoué, il refuse (`obtenu 0`). C'est une exception à la règle « écriture en base
par l'importateur seulement » : elle ne servirait qu'en incident, avec l'accord d'Era. **Restaurer S1 en entier est exclu** :
cela effacerait tout ce qui a été écrit depuis S1 (articles d'une ingestion, journaux d'usage). S1 sert à relire la valeur
exacte d'origine (`importe_le` 2026-08-20 11:03:00.621572 UTC, mesuré sur S1) et à prouver le retour, jamais à écraser la base.

## 3. Opération 3 : diagnostiquer la fraîcheur des données (lecture seule)

### 3.1 Ce que le bandeau affirme, et d'où vient la phrase

Le bandeau rouge de la production dit « 6 jours ouvrés de retard, dernière séance du 27/10/2026. La collecte ne tourne
plus. » Cette phrase n'est lue dans aucun journal : [`monitorage/fraicheur.py`](../monitorage/fraicheur.py) (lignes 149 à 152)
l'écrit dès que la dernière séance en base a plus de 3 jours ouvrés de retard (`SEUIL_ORANGE_JOURS_OUVRES = 3`). En orange,
il conseille « Vérifier la collecte de 19h00 », qui est la tâche planifiée du poste. C'est une déduction écrite comme un fait,
et la livraison A ne la change pas (le texte est le même dans `5398331`).

### 3.2 Constaté le 04/11, sans toucher au serveur

| Question | Réponse | Preuve |
|---|---|---|
| Où tourne la collecte planifiée ? | sur le **poste** : tâche Windows « RITA - collecte quotidienne », chaque jour à 19 h, qui écrit dans la **base du poste** | `Get-ScheduledTask` ; [`scripts/collecte-quotidienne.cmd`](../scripts/collecte-quotidienne.cmd) ; [`exploitation.md`](exploitation.md), « La collecte ci-dessus, comme la tâche planifiée du soir, écrit dans la base du poste » |
| Dernière collecte réussie sur le poste | 03/11/2026 à 19 h 00, code 0, 6 étapes sur 6 ; cotations 216 lues, 216 écrites, séances du 30/10 au 03/11 | `Get-ScheduledTaskInfo` ; `logs/manifeste-2026-11-03-190004.json` ; fin de `logs/collecte-2026-11-03.log` |
| Ce qui alimente la production | l'**ingestion** lancée par GitHub, qui ne collecte **que les articles** ; dernier passage le 27/10/2026 à 15 h 45 UTC, réussi | [`exploitation.md`](exploitation.md#rattrapage-cours-production) ; `gh run list --workflow ingestion.yml` (passage 40534178721) |
| Les cours et les taux en production | aucun envoi automatique : un seul **rattrapage à la main**, le 27/10 vers 16 h 43 (heure de Paris), avant la clôture d'Euronext (17 h 35), donc des cours de séance et non des clôtures ; « Une collecte planifiée des cours sur le serveur reste à faire » | [`exploitation.md`](exploitation.md#rattrapage-cours-production) |

**Ce qui en découle, à confirmer par les journaux du serveur** : en production, aucune collecte des cours n'a jamais tourné
seule ; elle ne s'est donc pas « arrêtée ». Les cours y sont simplement restés ceux du rattrapage du 27/10, pendant que le
poste collectait chaque soir pour lui-même.

### 3.3 L3 : la lecture du serveur (accord L3)

Un script en lecture seule, lancé par une seule session SSH : la base est lue en session lecture seule **et** avec le rôle
`rita_lecture`, sinon il s'arrête. Il donne : la dernière séance et le nombre de cotations, la dernière séance de chaque
position ouverte, la dernière date de chaque taux, la dernière collecte d'articles ; les douze derniers manifestes du serveur
(nom, mode, et pour chaque étape seulement nom, réussite, lues, écrites, rejetées) ; les tâches planifiées du serveur qui
parlent de collecte (noms de fichiers seulement) ; les vingt dernières lignes du journal des opérations, limitées à une liste
blanche de clés (date, opération, résultat, passage, de, vers, manifeste, bascule), jamais le champ libre `message`. Aucune
variable d'environnement, aucun contenu de crontab. Ses deux lecteurs ont été essayés sur le poste : le manifeste du 03/11 est
lu correctement, et une fausse ligne de journal perd bien son `message`.

### 3.4 Ce que l'opération 3 ne fait pas

Elle ne rattrape aucun cours. Un rattrapage (la procédure à la main existe) ou une collecte planifiée sur le serveur sont des
décisions séparées, à prendre après ce diagnostic et **jamais entre S1 et S2**. Corriger la phrase du bandeau est un
changement de code (test d'abord), noté comme défaut de monitorage (C20), hors de ce plan.

## 4. Les décisions d'Era

1. **Opération 1 maintenant** (tâches 0 à 9 livrées, 10 et 11 dans une seconde livraison avant le 12/11) **ou à la tâche 12**.
   Recommandation : maintenant, parce que la correction de Viridien en production exige l'importateur livré et que la revue
   demande le code d'abord ; la suite a passé 2 180 tests, deux fois, la seconde avec Azure injoignable.
2. L3 : lancée par l'agent après l'accord, ou par Era lui-même.
3. Le disque de la seconde copie des sauvegardes.
4. Un accord explicite pour chaque étape : A, B1, B2, S2 (S1 accordée et faite le 04/11).
5. **Avant A, demandé par la revue** : l'examen complet des 93 fichiers livrés et de leurs changements de comportement, avec
   les contrôles relus sur le commit final ; la fenêtre où la passerelle MCP refuserait la production (entre A et B2) et ce
   qu'on fait si B échoue ; le retour arrière sans perte des données écrites depuis S1 (§ 2.7).
6. **La passerelle MCP** (§ 0) : corriger maintenant son contrôle de types (changement de la passerelle seule, hors image,
   test d'abord avec une vraie réponse de l'API), ou après la livraison ; sans correction, le contrôle MCP final ne porte que
   sur `rita_fraicheur` et `rita_indicateurs`, et `rita_portefeuille` reste refusé comme aujourd'hui.
7. **L'exception gitleaks** de la clé périmée simulée (§ 0), à accepter ou à refuser avec A.
8. Les scripts de préparation (sauvegarde S1 et S2, vérification des fichiers servis, répétition, comparaison cellule par
   cellule, lecture L3) sont sur le poste, hors du dépôt : les verser dans `scripts/` avec leurs tests, ou les garder comme outils de cette opération.

## 📖 Glossaire

- **PR (pull request)** : demande de fusion d'une branche dans une autre, relue et contrôlée avant d'être acceptée.
- **Fusion** : intégration d'une branche dans une autre ; ici, dans `main`, elle déclenche le déploiement.
- **Job `deployer`** : étape de la CI qui installe la nouvelle image sur le serveur.
- **Créneau protégé** : plage du matin (7 h 30 à 9 h pour la livraison) pendant laquelle rien ne bascule en production.
- **Empreinte (SHA-256)** : résumé calculé d'un contenu ; deux contenus d'empreinte égale sont identiques.
- **`Cache-Control: no-cache`** : en-tête qui oblige le navigateur à redemander la page au lieu de reprendre une copie gardée.
- **`pg_dump -Fc` / `pg_restore`** : sauvegarde d'une base PostgreSQL au format compressé, et sa restauration.
- **Base jetable** : base créée pour un essai sur le poste, puis supprimée.
- **Passage à blanc** : exécution complète dont tout l'effet est annulé à la fin ; sert à lire le bilan sans rien écrire.
- **Verrou (`flock`)** : fichier que deux opérations ne peuvent pas tenir en même temps ; empêche une livraison pendant la correction.
- **Bloc `DO`** : petit programme SQL exécuté d'un seul tenant ; une erreur annule tout ce qu'il a fait.
- **Manifeste** : fichier écrit à chaque collecte, qui compte par étape les lignes lues, écrites et rejetées.
- **Ingestion** : collecte des articles en production, lancée depuis GitHub.
- **Rattrapage** : collecte des cours et des taux lancée à la main sur le serveur.
- **Jour ouvré** : jour de semaine ; le samedi et le dimanche ne comptent pas dans le retard.
- **Liste blanche** : liste des seuls champs autorisés à l'affichage ; tout le reste est ignoré.
- **PRU (prix de revient unitaire)** : prix moyen payé pour une action, frais compris.
