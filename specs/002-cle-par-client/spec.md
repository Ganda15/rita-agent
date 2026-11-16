# Spécification 002 : une clé d'accès par client

| | |
|---|---|
| **Statut** | **Implémentation reportée après l'oral blanc des 12-13/11, réévaluation le 14/11** (décision d'Era du 06/11) ; d'ici là, la clé partagée est présentée comme une limite, avec cette solution et son estimation. **Validée par Era le 05/11/2026** : les sept réponses du § 7 confirmées, avec trois précisions (audit différé ou direct, `/audit/mcp` réservé à la passerelle, secours compatible dès la première bascule) ; deux relectures du 05/11 intégrées ; le plan et les tâches viennent ensuite, aucune ligne de code avant leur validation |
| **Décision d'origine** | retour écrit du formateur du 03/11 : « faire une clé par client avant le jury » (C5) ; ordre retenu le 05/11 : clé par client, puis collecte sur le serveur, puis briefing du matin |
| **Ce qui fait foi** | `docs/BUDGET.md`, « L'évolution prévue avant le jury : une clé par client (C5) » : test d'acceptation et estimation |
| **Ce que ce document dit** | **quoi** et **pourquoi** ; le **comment** (où vivent les empreintes, comment la révocation se propage) ira dans `plan.md`, après validation |

## 1. Pourquoi

Aujourd'hui, tout le monde ouvre RITA avec la même clé. Retirer l'accès à une personne oblige à changer la clé de
tous, et le journal ne peut pas dire qui a fait un appel. Avant le jury, chaque accès utile (Era, le formateur, le jury,
la passerelle MCP) doit avoir sa clé, retirable seule, et chaque appel protégé doit être rattaché à la clé qui l'a
ouvert. Une clé identifie un **accès attribué**, pas la personne qui tient le clavier : si le jury partage une clé, le
journal identifie le groupe.

## 2. Ce qui existe au 05/11/2026 (relu dans le code)

- **Une seule clé** : `X-API-Key` comparée à `RITA_API_KEY` à temps constant (`api/main.py`, ligne 207) ; 403 sans elle ;
  16 caractères au minimum (ligne 164). La docstring assume la limite : « pas de révocation partielle, pas de
  traçabilité par appelant ».
- **La clé est vérifiée avant le quota** (`api/main.py`, lignes 273 et 408) : une clé invalide reçoit 403 sans consommer
  les 10 appels par minute partagés par `/briefing` et `/question` (`api/limiteur.py`).
- **L'identité de l'appelant est déclarée, pas prouvée**, à deux endroits : le middleware lit `X-Client-Id` (ligne 153)
  et la route `POST /audit/mcp` le relit (ligne 237). Seule la passerelle MCP l'envoie (`passerelle_mcp/serveur.py`,
  ligne 300), avec la même clé que le navigateur. Le corps de `/audit/mcp` refuse déjà tout champ inconnu.
- **Deux façons d'écrire l'audit** : le middleware écrit dans `mcp_calls` **après** la réponse (tâche de fond, lignes
  156 à 160) ; la route `POST /audit/mcp` écrit **avant** de répondre (`audit_mcp.enregistrer`, puis `{"enregistre": ok}`,
  lignes 235 à 240). Une panne d'écriture donne une ligne WARNING et un compteur (`db/audit_mcp.py`), sans interrompre
  l'appel métier.
- **Le déployeur contrôle un retour arrière avec la clé de la version visée** : il la lit dans la copie du `.env` de
  cette version (`deploy/deployer.py`, ligne 666).
- **Chaque livraison garde sa propre copie du `.env`**, et le retour arrière reprend la configuration de la version
  précédente (`deploy/deployer.py`, lignes 558 et 892). Une clé révoquée qui vivrait dans `.env` pourrait revenir.
- **Les livraisons sont différées entre 7 h 30 et 9 h** (créneau protégé de 8 h à 9 h, marge de 30 minutes,
  `.github/workflows/livraison.yml`, ligne 325).
- **Purge** : P6 purge `mcp_calls` au-delà de 90 jours, script prêt, **lancement manuel aujourd'hui** (registre RGPD,
  ligne 343). Le même registre dit « purge automatisée P6 » à la ligne 221 : incohérence à corriger dans ce lot.

## 3. Les histoires

### R1. Retirer l'accès d'un client sans couper les autres (priorité 1)

En tant qu'exploitant, je veux retirer l'accès d'un client, afin que les autres continuent de travailler.

- Après la révocation de la clé A, A reçoit **403** et B reçoit **200** sur la même route protégée, **sans appel
  payant au modèle** pour ce test.
- La révocation agit **sans redémarrage** : dès qu'elle est confirmée, la prochaine vérification refuse la clé. Un appel
  déjà accepté n'est pas annulé après coup.
- Une clé révoquée **reste révoquée** après redémarrage, redéploiement et **retour arrière** ; si un retour arrière vers
  une version qui ne connaît pas les clés par client rendrait l'ancienne clé commune valable, ce retour est empêché.
- Si la liste des clés est absente, illisible ou invalide, **aucun accès n'est accordé** par une clé de secours, et
  l'erreur ne contient aucun secret.
- **Un secours compatible existe dès la première bascule** : si la nouvelle version échoue, le service peut être rétabli
  sans réactiver une clé révoquée. Le plan dit comment, étape par étape.

### R2. Rattacher chaque appel protégé à la clé qui l'a ouvert (priorité 1)

En tant qu'exploitant, je veux que le journal dise qui a appelé d'après la clé acceptée, jamais d'après ce que
l'appelant déclare.

- **Portée** : chaque requête protégée authentifiée laisse dans le journal de l'API le pseudonyme de la clé, la
  référence de requête, la route et le résultat. Une requête publique, sans clé ou avec une clé inconnue n'obtient
  l'identité d'aucun client ; une clé révoquée est journalisée « refusée », jamais « authentifiée ».
- **`X-Client-Id` est ignoré** pour l'attribution, **sur les deux chemins** : le middleware et `POST /audit/mcp`. Une
  clé A envoyée avec un en-tête B est attribuée à A ; un en-tête absent ne supprime pas l'audit prévu.
- `mcp_calls` reste le journal des **événements MCP** ; les appels du navigateur n'y entrent pas. Un appel est MCP parce
  que la clé acceptée est celle de la passerelle, pas parce qu'un en-tête libre le dit. Où vont les autres journaux, et
  combien de temps : à écrire dans le plan.
- `/audit/mcp` est **réservé à la clé de la passerelle** : une clé d'utilisateur valide reçoit 403 et n'écrit aucune
  ligne. Pas de double ligne pour un même événement ; un `client_id` glissé dans le JSON reste refusé. La clé prouve qui
  envoie un signalement, pas que le signalement décrit un événement réel.
- La différence entre les deux écritures reste dite : le middleware écrit après la réponse (une panne n'est vue qu'au
  journal et au compteur), `/audit/mcp` écrit avant de répondre et renvoie `enregistre: false` en cas d'échec.
- Si un refus local de la passerelle ne peut plus être journalisé (clé de la passerelle révoquée, audit en panne),
  l'échec est visible sans secret, et le refus métier reste un refus. On ne promet pas un journal durable exhaustif :
  l'audit reste différé, ses échecs comptés.

### R3. Donner un accès à une personne invitée (priorité 1)

En tant qu'exploitant, je veux créer l'accès d'un nouveau client sans toucher au code, afin de préparer le jury.

- Les clés sont **générées au hasard**, de façon imprévisible ; la longueur de 16 caractères ne suffit pas à le prouver.
- Le serveur garde des **empreintes**, pas des clés utilisables : une copie volée de cette liste n'ouvre rien.
- La clé est montrée **une seule fois**, à son destinataire, au moment de sa remise (seule exception à « aucune clé
  dans une réponse », qui vise les réponses métier). Une clé oubliée est **remplacée**, jamais réaffichée.
- Le guide d'exploitation décrit la création, la remise, la révocation et le remplacement, pas à pas.

### R4. Changer de clés sans casser ce qui marche (priorité 1)

En tant qu'utilisateur, je veux saisir ma clé comme aujourd'hui ; en tant qu'exploitant, je veux une bascule préparée.

- Les cinq écrans fonctionnent avec la clé de chaque client, saisie comme aujourd'hui.
- **Bascule** : de nouvelles clés sont émises pour chaque consommateur réellement présent (navigateur, passerelle MCP,
  outils de contrôle et de déploiement, scripts, vigie : inventaire dans le plan), puis la clé commune est retirée. Elle
  ne devient pas la clé d'Era : un accès partagé ne doit pas devenir une identité personnelle.
- Les **clés d'essai A et B** sont distinctes des clés utiles et ne les remplacent jamais.

### R5. Le jury peut vérifier (priorité 2)

- Un test automatique, en CI, prouve R1 et R2 (§ 8).
- Une **preuve datée en production**, sur une route protégée, sans appel au modèle et sans clé visible.
- À l'oral, une révocation en direct reste facultative, **uniquement avec une clé d'essai**.
- Le registre RGPD dit ce que deviennent les pseudonymes et les empreintes, et sa durée de conservation réelle.

## 4. Exigences transverses

- Aucune clé ni fragment de clé dans le dépôt, un journal ou une réponse métier ; comparaison à temps constant gardée.
- **Quota** : le plafond global de 10 appels par minute, partagé par `/briefing` et `/question`, reste tel quel ; il
  n'est pas multiplié par le nombre de clients. Limite écrite : il protège le coût total, sans garantir un quota
  indépendant à chacun. Une clé invalide ne consomme toujours pas le quota.
- Deux clients simultanés : aucune contamination des identités entre requêtes.
- Test d'abord ; aucun test existant désactivé ni affaibli.
- Si les empreintes vivent dans la base, `db/schema.sql` est une zone sous garde : plan écrit et validé avant.
- **Conservation** : décrire les durées réelles des supports utilisés ; ne pas annoncer une purge automatique qui
  n'existe pas ; corriger la ligne 221 du registre.

## 5. Hors périmètre

- **#76, le rôle de la base** (l'API et le scout lisent la base avec le rôle propriétaire) : **lot distinct, prioritaire
  avant le jury**. Une clé par client ne corrige pas les droits de la base et ne clôt pas seule C17.5 ; le rôle de
  l'API doit aussi pouvoir écrire son audit, le rôle de lecture seul ne suffit pas.
- L'historique des briefings, le briefing du matin et ses notifications : lot à venir.
- Comptes, mots de passe, interface d'administration, expiration automatique des clés.

## 6. Calendrier

Spécification validée par Era → plan → tâches → code, test d'abord → PR vers `develop` puis `main` → déploiement **au
créneau autorisé par la chaîne actuelle** (jamais entre 7 h 30 et 9 h) → preuve datée en production. Visé : avant
l'oral blanc des 12-13/11 ; au plus tard avant le gel de l'application (vers le 24/11, date à fixer par Era).
L'estimation de `docs/BUDGET.md` (1 à 2 journées) reste une hypothèse à confronter au plan, notamment pour la
migration, la révocation sans redémarrage et le retour arrière. À l'oral : « depuis la version figée au tag …, le …,
commit … ».

## 7. Questions pour Era : réponses confirmées le 05/11

| Question | Réponse confirmée par Era |
|---|---|
| **Q1. Les clients** | Era, le formateur, un accès jury, la passerelle MCP ; plus deux clés d'essai A et B. Un pseudonyme chacun. |
| **Q2. La révocation** | Sans redémarrage. |
| **Q3. La clé actuelle** | Remplacée par une bascule préparée ; elle ne devient pas la clé d'Era. |
| **Q4. `X-Client-Id`** | Ignoré pour l'attribution ; l'identité vient de la clé validée. |
| **Q5. #76** | Lot distinct, prioritaire avant le jury. |
| **Q6. Le quota** | Global, 10 par minute, inchangé. |
| **Q7. À l'oral** | Test automatique et preuve datée ; révocation en direct facultative, clé d'essai seulement. |

## 8. Vérifications d'acceptation

| Cas | Attendu |
|---|---|
| Deux clés A et B actives | Toutes deux acceptées sur une même route protégée. |
| A révoquée, B active | A → 403 ; B → 200 ; sans appel payant au modèle. |
| A valide, en-tête B ou absent | L'appel est attribué à A. |
| Clé inconnue, en-tête d'un client existant | Refus, sans attribuer l'appel à ce client. |
| Signalement `/audit/mcp` par la passerelle | Identité issue de la clé ; pas de double ligne ; `client_id` dans le JSON refusé. |
| Signalement `/audit/mcp` avec une clé d'utilisateur valide | 403 ; aucune ligne écrite. |
| Première bascule, nouvelle version en échec | Service rétabli par le secours prévu ; aucune clé révoquée réactivée. |
| Deux clients simultanés | Aucune contamination des identités. |
| Redémarrage et redéploiement | La révocation persiste ; la clé commune n'est pas réactivée. |
| Retour arrière | L'accès révoqué reste interdit, ou le retour vers une version incompatible est empêché. |
| Liste des clés absente ou invalide | Aucun accès par défaut ; erreur sans secret. |
| Refus local MCP, audit en échec | Avertissement visible sans clé ; refus métier conservé. |
| Clé invalide sur une route du modèle | Ne consomme pas le quota des clients valides. |
| Journaux et réponses | Aucun secret ni fragment de clé ; pseudonyme, références et motifs seulement. |

## 9. Traçabilité

| Exigence | D'où elle vient |
|---|---|
| R1, R3 | retour du formateur du 03/11 (C5) ; `docs/BUDGET.md`, test d'acceptation |
| R2 | `api/main.py`, lignes 153 et 237 (identité déclarée) ; relecture du 05/11 |
| R1 (retour arrière) | `deploy/deployer.py`, lignes 558 et 892 |
| R4 | `passerelle_mcp/serveur.py`, ligne 300 ; écrans existants |
| R5 | C5 d'abord ; contribue à C17.5 (« à consolider » dans E4 v1.5) sans le clore (#76) ; registre RGPD, T5 et P6 |
| § 4 | OWASP, *Secrets Management Cheat Sheet* (cycle de vie, révocation, rotation) |

## 📖 Glossaire

- **Clé d'API** : le secret que l'écran ou un programme envoie avec chaque demande pour être accepté.
- **Révocation** : le retrait d'une clé ; elle n'ouvre plus rien, les autres continuent de marcher.
- **Empreinte** : un résumé calculé à partir de la clé, qui permet de la reconnaître sans la garder ; on ne peut pas
  retrouver la clé depuis l'empreinte.
- **Pseudonyme** : un identifiant qui ne donne pas le nom de la personne (« client-02 »).
- **Bascule** : le moment préparé où les nouvelles clés remplacent l'ancienne, pour tous les consommateurs à la fois.
- **Retour arrière** : la remise en service de la version précédente de l'application, avec sa configuration.
- **403** : la réponse « accès refusé ».
- **Comparaison à temps constant** : une vérification qui prend le même temps que la clé soit presque juste ou très
  fausse, pour ne rien apprendre à un attaquant.
- **Passerelle MCP** : le programme qui permet à un assistant IA d'interroger RITA en lecture, avec sa propre clé.
