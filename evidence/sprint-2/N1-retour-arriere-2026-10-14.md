# Preuve sprint 2 : livraison N1, retour arrière N1 vers N0, relivraison de N1 (14/10/2026)

> Suite de `N0-premiere-livraison-2026-10-14.md`. Une deuxième version (N1) donne au script du serveur une version
> précédente : le retour arrière devient possible. Il a été répété une fois, en une seule opération, puis N1 a été
> relivrée pour que la production corresponde de nouveau à `main`.

| Étape | Déclencheur | Côté serveur (UTC) | Résultat |
|---|---|---|---|
| Livraison N1 | fusion de la PR #92 (commit `e06cd17`), passage `38636271353` | 21:02:05 à 21:05:50 (225 s) | `livree`, de N0 vers N1 |
| Retour arrière | `gh workflow run retour-arriere.yml`, passage `38637911060` | 21:08:46 à 21:09:02 (16 s) | `retour arriere`, de N1 vers N0 |
| Relivraison N1 | relance du travail `deployer` du passage `38636271353` (tentative 2) | 21:10:37 à 21:14:20 (223 s) | `livree`, de N0 vers N1 |

Les deux versions :

| Version | Commit | Image |
|---|---|---|
| N0 | `48196272fb5e4aaaf4f62712253a9d6b14912af8` | `ghcr.io/ganda15/rita-api@sha256:d181f9ad9402cd732fb9badfd8f5bd755470a07876849d9e4671c9772c8ee284` |
| N1 | `e06cd17ef9b8d25635d311939ec6ded7880a66a4` | `ghcr.io/ganda15/rita-api@sha256:75cbf7894c00815a3df2df66e51e7fccb53d10bb1f8e2401df83f5113f31581b` |

## Livraison N1 : de la fusion à la production sans intervention

La PR #92 ne contenait que de la documentation ; ses six contrôles exigés sont passés (`lint` 9 s, `revue` 44 s,
`secrets` 57 s, `evals` 1 min 31, `pytest` 2 min 26, `construire-et-publier` 3 min 14). Sa fusion a lancé le passage
`38636271353` à 20:56:26 UTC :

```
✓ secrets in 32s
✓ lint in 14s
✓ construire-et-publier in 4m43s
✓ attendre-creneau in 8s
✓ deployer in 3m53s
- attendre-reprise
- deployer-reprise
✓ Run Livraison (38636271353) completed with 'success'
```

Journal du travail `deployer` :

```
script du serveur identique au depot (85c460468dfbb16fe84d3d345c2cc74e08b76e983cad754e221dd21e210a5b6e)
code rendu par le serveur : 0
```

**De la fusion à la production : 9 min 24 s** (20:56:26 à 21:05:50 UTC). `/health` vu de l'extérieur ensuite :

```
{"status":"ok","project":"RITA","commit":"e06cd17ef9b8d25635d311939ec6ded7880a66a4","construit_le":"2026-10-14T20:59:55Z"}
```

## Retour arrière : une opération

Commande lancée depuis le poste (équivalent du bouton *Run workflow* de l'onglet Actions) :

```
gh workflow run retour-arriere.yml --repo Ganda15/rita-agent --ref main -f acteur=Era -f "motif=Repetition du retour arriere N1 vers N0 (sprint 2)"
```

Journal du passage `38637911060` (le nom et le motif restent dans GitHub ; le serveur ne reçoit que le numéro du
passage) :

```
ACTEUR: Era
MOTIF: Repetition du retour arriere N1 vers N0 (sprint 2)
script du serveur identique au depot (85c460468dfbb16fe84d3d345c2cc74e08b76e983cad754e221dd21e210a5b6e)
ORDRE: revenir
ARGUMENT: 38637911060
code rendu par le serveur : 0
```

Passage créé à 21:08:37, terminé avec succès à 21:09:05 UTC : **28 s de bout en bout, 16 s côté serveur**.

Mesure faite pendant le retour, depuis le poste : `/health` interrogé toutes les 2 s, une ligne à chaque changement.

```
debut de la mesure : 21:07:42 UTC
21:07:42 UTC  code=200 commit=e06cd17
21:08:49 UTC  code=502 commit=
21:08:56 UTC  code=200 commit=4819627
fin de la mesure : 21:09:01 UTC
```

N0 est servie **19 s après le lancement**. Pendant la bascule, la production a répondu **502 pendant environ 7 s**
(précision de la mesure : 2 s).

## Relivraison de N1

Relance du travail `deployer` du passage N1 (`gh run rerun`), avec l'image déjà publiée et vérifiée, sans
reconstruction : tentative 2, travail de 21:10:32 à 21:14:22 UTC, `code rendu par le serveur : 0`.

## État final sur le serveur

Journal (`/root/rita-deploy/journal.jsonl`), quatre dernières lignes :

```
{"date": "2026-10-14T22:37:31+02:00", "operation": "livrer", "vers": "ghcr.io/ganda15/rita-api@sha256:d181f9ad9402cd732fb9badfd8f5bd755470a07876849d9e4671c9772c8ee284", "de": null, "resultat": "livree"}
{"date": "2026-10-14T23:05:50+02:00", "operation": "livrer", "vers": "ghcr.io/ganda15/rita-api@sha256:75cbf7894c00815a3df2df66e51e7fccb53d10bb1f8e2401df83f5113f31581b", "de": "ghcr.io/ganda15/rita-api@sha256:d181f9ad9402cd732fb9badfd8f5bd755470a07876849d9e4671c9772c8ee284", "resultat": "livree"}
{"date": "2026-10-14T23:09:02+02:00", "operation": "revenir", "passage": "38637911060", "de": "ghcr.io/ganda15/rita-api@sha256:75cbf7894c00815a3df2df66e51e7fccb53d10bb1f8e2401df83f5113f31581b", "vers": "ghcr.io/ganda15/rita-api@sha256:d181f9ad9402cd732fb9badfd8f5bd755470a07876849d9e4671c9772c8ee284", "resultat": "retour arriere"}
{"date": "2026-10-14T23:14:20+02:00", "operation": "livrer", "vers": "ghcr.io/ganda15/rita-api@sha256:75cbf7894c00815a3df2df66e51e7fccb53d10bb1f8e2401df83f5113f31581b", "de": "ghcr.io/ganda15/rita-api@sha256:d181f9ad9402cd732fb9badfd8f5bd755470a07876849d9e4671c9772c8ee284", "resultat": "livree"}
```

`/root/rita-deploy/etat.json` :

```
{
  "active": {
    "image": "ghcr.io/ganda15/rita-api@sha256:75cbf7894c00815a3df2df66e51e7fccb53d10bb1f8e2401df83f5113f31581b",
    "config": "/root/rita-deploy/configs/20261014-231039-75cbf7894c00",
    "profil": "complet",
    "index": "rita-index-20261014-231039-75cbf7894c00"
  },
  "precedente": {
    "image": "ghcr.io/ganda15/rita-api@sha256:d181f9ad9402cd732fb9badfd8f5bd755470a07876849d9e4671c9772c8ee284",
    "config": "/root/rita-deploy/configs/20261014-223353-d181f9ad9402",
    "profil": "complet",
    "index": "rita-index-20261014-223353-d181f9ad9402"
  },
  "observee": "ghcr.io/ganda15/rita-api@sha256:75cbf7894c00815a3df2df66e51e7fccb53d10bb1f8e2401df83f5113f31581b",
  "sante": "sain"
}
```

Index présents :

```
rita-index-20261014-223353-d181f9ad9402
rita-index-20261014-230209-75cbf7894c00
rita-index-20261014-231039-75cbf7894c00
```

Commandes rejouables :

```
ssh root@178.104.184.125 "tail -n 4 /root/rita-deploy/journal.jsonl; cat /root/rita-deploy/etat.json"
```

```
gh run view 38637911060 --repo Ganda15/rita-agent
```

## Ce que cela prouve, et ce que cela ne prouve pas

**Prouvé** : une fusion sur `main` arrive seule en production (N1, premier essai) ; le retour à la version précédente
validée tient en une opération et moins d'une demi-minute ; il est tracé des deux côtés (nom et motif dans GitHub,
numéro du passage dans le journal du serveur) ; la version revenue est contrôlée avec sa propre configuration et son
propre index, gardés depuis sa livraison ; la production revient ensuite à `main` par la même chaîne.

**Pas prouvé** : le retour automatique après une bascule ratée (aucune bascule n'a échoué) ; le retour quand GitHub
est indisponible (procédure de secours sur le serveur, non exercée) ; le report de 8 h et la reprise de 9 h en
conditions réelles.

## Manques relevés

- **La bascule n'est pas sans coupure** : environ 7 s de 502 pendant le retour, parce que le conteneur de l'API est
  remplacé. Les livraisons basculent de la même façon. Non mesuré pour elles.
- **Un index ne sert plus** : `rita-index-20261014-230209-75cbf7894c00`, celui de la première livraison de N1. Ni la
  version active ni la précédente ne l'utilisent. Le ménage des anciens index se fait à la main.
