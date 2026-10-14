# Preuve sprint 2 : première livraison N0 par la chaîne (14/10/2026)

> La fusion de la PR #91 sur `main` (commit `48196272fb5e4aaaf4f62712253a9d6b14912af8`) a déclenché le workflow
> `Livraison` (`.github/workflows/livraison.yml`, exécution `38627837851`, événement `push`, 19:56:22 UTC).
> `lint`, `secrets` et `construire-et-publier` sont passés au premier essai ; l'image a été publiée sous l'empreinte
> `ghcr.io/ganda15/rita-api@sha256:d181f9ad9402cd732fb9badfd8f5bd755470a07876849d9e4671c9772c8ee284`.
> Le travail `deployer` a été lancé trois fois. Les deux premiers essais ont été refusés **sans toucher à la
> production** ; le troisième a livré.

| Essai | Travail `deployer` (UTC) | Résultat | Cause | Production |
|---|---|---|---|---|
| 1 | 20:04:06 à 20:04:12 | refusé avant toute connexion | empreinte du serveur enregistrée vide | inchangée |
| 2 | 20:22:04 à 20:26:06 | refusé au pré-test | adresse du modèle collée deux fois dans le `.env` du serveur | inchangée |
| 3 | 20:33:44 à 20:37:33 | livré | | N0 en service |

Relevé rejouable des horaires :

```
gh api repos/Ganda15/rita-agent/actions/runs/38627837851/attempts/3/jobs --jq '.jobs[] | .name + " " + .conclusion'
```

## Essai 1 : SSH refuse un serveur qu'il ne sait pas reconnaître

Journal du travail, étape « Comparer le script du serveur à celui du dépôt » :

```
Host key verification failed.
##[error]Process completed with exit code 255.
```

**Cause.** Le secret `DEPLOY_KNOWN_HOSTS` avait été posé par
`cmd /c "ssh-keyscan -t ed25519 178.104.184.125 2>nul | gh secret set DEPLOY_KNOWN_HOSTS ..."`. Sur le poste, le
`ssh-keyscan` trouvé en premier est celui de Windows (`C:\Windows\System32\OpenSSH\`). Face au serveur
(`SSH-2.0-OpenSSH_10.2p1 Ubuntu-2ubuntu3.6`), il échoue avec le code 1 :

```
choose_kex: unsupported KEX method sntrup761x25519-sha512@openssh.com
```

`2>nul` masquait ce message ; `gh` a reçu une entrée vide et a enregistré un secret vide. Le travail a écrit un
`known_hosts` vide, et `StrictHostKeyChecking=yes` a refusé la connexion. Le serveur n'a reçu aucun ordre.

**Correction.** La ligne de clé publique relue avec le `ssh-keyscan` de Git, empreinte
`SHA256:1ArXtdtqdPTz9MHwb5J2Wq8HQ2W3olUexUOYMgi5us8`, identique à celle que donne le serveur lui-même
(`ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`), posée sans pipe :

```
gh secret set DEPLOY_KNOWN_HOSTS --env production --repo Ganda15/rita-agent --body "178.104.184.125 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIK57l8G2igKdRJbcCatHoLu64YU543kByI1s0KwsSsfn"
```

Puis `gh run rerun 38627837851 --failed` : seul `deployer` est relancé, l'image publiée est réutilisée.

## Essai 2 : le pré-test refuse une version qui ne produit pas de briefing

Journal du travail :

```
script du serveur identique au depot (85c460468dfbb16fe84d3d345c2cc74e08b76e983cad754e221dd21e210a5b6e)
operation refusee ou en echec : voir journal.jsonl sur le serveur
code rendu par le serveur : 1
```

Journal du serveur (`/root/rita-deploy/journal.jsonl`) :

```
{"date": "2026-10-14T22:26:04+02:00", "operation": "livrer", "vers": "ghcr.io/ganda15/rita-api@sha256:d181f9ad9402cd732fb9badfd8f5bd755470a07876849d9e4671c9772c8ee284", "resultat": "refusee au pre-test", "echecs": ["briefing"]}
```

État juste après : l'API de production toujours sur l'ancienne image (`rita-api-preprod rita-api:local Up 7 weeks
(healthy)`), aucun volume `rita-index-*` restant (l'index de la candidate a été supprimé), `/health` sans champ
`commit` (ancienne version).

**Cause.** Comparaison des longueurs, jamais des valeurs : `AZURE_FOUNDRY_ENDPOINT` faisait 68 caractères sur le
poste et 136 sur le serveur. Vérification sur le serveur, sans afficher la valeur :

```
longueur 136
finit par /openai/v1
DOUBLON : les deux moities sont identiques
```

L'adresse était collée deux fois. La cascade de modèles (`foundry`, `anthropic`, `openrouter`) n'a de clé que pour
Azure sur le serveur : l'appel échouait, `/briefing` répondait en erreur, et le contrôle `briefing` du pré-test a
refusé la version avant la bascule.

**Correction** (sur le serveur, copie du `.env` faite avant, puis supprimée après la livraison) : la ligne réécrite
avec sa première moitié seulement. Contrôles :

```
longueur 68
finit par /openai/v1
pas de doublon
```

Aucune autre variable du `.env` n'a deux moitiés identiques ; droits du `.env` : `600 root`. Un appel réel à Azure
depuis le serveur (clé passée par `curl -K -`, seul le code affiché) répond `200`.

## Essai 3 : livré

Journal du travail :

```
script du serveur identique au depot (85c460468dfbb16fe84d3d345c2cc74e08b76e983cad754e221dd21e210a5b6e)
code rendu par le serveur : 0
```

**Durée mesurée** : ordre envoyé à 20:33:50, code 0 à 20:37:31, soit **221 s** pour le tirage de l'image, la
construction d'un index neuf, le pré-test sur `127.0.0.1:8003` avec le compte `rita_lecture`, la bascule et les
contrôles complets. Maximum calculé par le script : `DUREE_MAX_LIVRER` = 4 161 s.

Journal du serveur :

```
{"date": "2026-10-14T22:37:31+02:00", "operation": "livrer", "vers": "ghcr.io/ganda15/rita-api@sha256:d181f9ad9402cd732fb9badfd8f5bd755470a07876849d9e4671c9772c8ee284", "de": null, "resultat": "livree"}
```

`/root/rita-deploy/etat.json` (aucun secret) :

```
{
  "active": {
    "image": "ghcr.io/ganda15/rita-api@sha256:d181f9ad9402cd732fb9badfd8f5bd755470a07876849d9e4671c9772c8ee284",
    "config": "/root/rita-deploy/configs/20261014-223353-d181f9ad9402",
    "profil": "complet",
    "index": "rita-index-20261014-223353-d181f9ad9402"
  },
  "precedente": null,
  "observee": "ghcr.io/ganda15/rita-api@sha256:d181f9ad9402cd732fb9badfd8f5bd755470a07876849d9e4671c9772c8ee284",
  "sante": "sain"
}
```

Conteneurs et index :

```
rita-api-preprod d181f9ad9402 Up 6 minutes (healthy)
rita-postgres-preprod postgres:18-alpine Up 7 weeks (healthy)
rita-index-20261014-223353-d181f9ad9402
```

Contrôle de l'extérieur, depuis le poste :

```
/health                  : {"status":"ok","project":"RITA","commit":"48196272fb5e4aaaf4f62712253a9d6b14912af8","construit_le":"2026-10-14T19:59:58Z"}
/briefing.html           : 200
/donnees/valeurs sans clé : 403
origin/main              : 48196272fb5e4aaaf4f62712253a9d6b14912af8
```

Commandes rejouables :

```
curl -s https://178-104-184-125.sslip.io/health
```

```
ssh root@178.104.184.125 "tail -n 1 /root/rita-deploy/journal.jsonl; cat /root/rita-deploy/etat.json"
```

## Ce que cette livraison prouve, et ce qu'elle ne prouve pas

**Prouvé** : une fusion sur `main` part seule jusqu'à la production (lint, recherche de secrets, construction,
publication, livraison) ; le serveur n'exécute qu'un script identique au dépôt ; un serveur non reconnu bloque tout
avant la connexion ; une version qui ne produit pas de briefing est refusée au pré-test, avant la bascule ; un refus
laisse la production intacte et retire l'index de la candidate.

**Pas encore prouvé** : le retour arrière (`"precedente": null`, il faut une deuxième livraison, N1) ; le retour
automatique après une bascule ratée ; le report de 8 h et la reprise de 9 h en conditions réelles (prouvés par les
tests seulement) ; le secours dégradé vers la version d'avant la chaîne, jamais exercé.

## Manques relevés pendant cette livraison

- Le journal du serveur nomme le contrôle en échec (`briefing`) sans son code HTTP, et le conteneur du pré-test est
  supprimé avec ses journaux : il a fallu une enquête pour trouver la cause. Le code HTTP ne contient aucun secret ; à
  ajouter au journal après l'atelier (modification de `deploy/deployer.py`, donc réinstallation du script).
- Les contrôles de la tâche 10 vérifiaient la présence et la longueur des valeurs du `.env`, pas leur justesse : le
  doublon est passé. Le contrôle juste est un appel réel au modèle depuis le serveur.
- Le secret `DEPLOY_KNOWN_HOSTS` n'est pas relisible (GitHub ne rend jamais la valeur d'un secret) : seul un essai de
  connexion prouve qu'il est bon.
