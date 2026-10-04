# C11 et C20 : les deux alertes Langfuse, réglées et mises à l'épreuve le 04/10/2026

**Écrit le 04/10/2026.** Ce document prouve trois choses : les traces factices d'INC-006 sont parties, les deux
alertes du palier gratuit sont en place et branchées sur GitHub, et chacune a sonné pour de vrai. La seconde a
d'abord sonné à tort, et c'est la mesure qui l'a montré. Toutes les lectures de Langfuse ci-dessous sont faites
par l'API publique, en lecture seule, avec les clés du projet chargées par l'application et jamais affichées.

## 1. Les traces factices d'INC-006 sont supprimées

| Quand | Quoi | Preuve |
|---|---|---|
| 03/10, 00:17 UTC | Export des 15 traces factices (entrée `prompt test`, écrites par la suite de tests le 02/10) avant toute suppression | `inc-006-traces-factices-avant-suppression-2026-10-03.json` (`"nombre": 15`) |
| 04/10, matin | Era les sélectionne dans Tracing et lance « Delete Traces » ; Langfuse prévient que la suppression peut prendre jusqu'à 15 minutes | captures d'Era (sélection de 15 lignes) |
| 04/10, 11:44:47 (heure de Paris) | Relecture par l'API de la fenêtre du 02/10, 18:20 à 19:15 : **7 traces, 0 « prompt test »** | sortie du script de lecture, ci-dessous |

```
11:44:47 traces: 7 prompt test: 0
SUPPRESSION CONSTATEE
```

Les 7 traces qui restent sont les vrais briefings de ce soir-là. La suppression a été faite par Era : la session de
l'assistant n'a pas le droit de supprimer définitivement des données.

## 2. Le canal : Langfuse appelle GitHub, GitHub ouvre une issue

Automatisation Langfuse de type « GitHub Dispatch » : adresse de dispatch du dépôt, type d'événement
`alerte-langfuse`, jeton personnel (droit `repo`) saisi par Era dans Langfuse seulement. Côté dépôt,
`.github/workflows/alerte-incident.yml` reçoit l'événement et ouvre une issue `incident`, ou commente celle déjà
ouverte pour la même alerte. Tests : `tests/test_alerte_incident.py` (10 tests depuis le 04/10, dont deux qui
exécutent le vrai script de l'étape sur la charge utile reçue ; ils tournent sur le runner GitHub, où `jq` existe).

## 3. Alerte 1 : « RITA : fournisseur en erreur »

| Réglage | Valeur |
|---|---|
| Vue, mesure, agrégation | Observations, nombre d'observations |
| Filtre | niveau `ERROR` (l'interface l'appelle « Status » ; la charge utile dit `"column": "level"`) |
| Condition | au-dessus de 0, sur 1 jour |

**Elle a sonné le 04/10 à 10:07 UTC** : exécution GitHub `37194357268`, issue
[#77](https://github.com/Ganda15/rita-agent/issues/77). Charge utile reçue :
`count(observations.count) is above 0 over the last 1d`, titre `[ALERT] RITA : fournisseur en erreur`.

**Était-ce une vraie erreur ?** Oui. Lecture par l'API des observations de niveau ERROR entre le 03/10 10:07 UTC et
le 04/10 10:08 UTC :

| Heure (UTC) | Observation | Message |
|---|---|---|
| 03/10 12:48:21 | `llm-foundry` | `KeyError: 'AZURE_FOUNDRY_API_KEY'` |
| 03/10 12:48:21 | `llm-anthropic` | `TypeError: "Could not resolve authentication method...` |
| 03/10 15:18:22 | `llm-foundry` | `KeyError: 'AZURE_FOUNDRY_API_KEY'` |
| 03/10 15:18:22 | `llm-anthropic` | `TypeError: "Could not resolve authentication method...` |

À ces heures (14 h 48 et 17 h 18 à Paris), la clé Foundry n'était pas encore configurée sur le poste : le commit
`a24375c` (16 h 07) note « Foundry et Anthropic indisponibles faute de clés ». La cascade a fait son travail :
OpenRouter a répondu les deux fois (5,82 s et 6,07 s, section 4). L'alerte a donc vu une dégradation réelle, sans
panne pour l'utilisateur. Le briefing de 17:28 UTC passe par Foundry sans erreur.

**Prévision à vérifier** (pas encore constatée) : sans nouvelle erreur, l'alerte repasse à OK quand l'erreur de
15:18 UTC sort de la fenêtre d'un jour, soit après le 04/10 vers 15:18 UTC.

## 4. Alerte 2 : « RITA : appel au modèle trop lent », et la fausse alerte

| Réglage | Valeur |
|---|---|
| Vue, mesure, agrégation | Observations, latence, p95 |
| Filtre | nom de l'observation = `briefing-llm` (l'appel au modèle, cascade comprise) |
| Condition | au-dessus de **15000**, sur 1 jour (réglé d'abord à 15, voir plus bas) |

**Ce qui s'est passé.** Créée avec le seuil `15` en pensant à des secondes, elle a sonné dès sa création, le 04/10 à
10:17 UTC (exécution `37194875460`, commentaire sur #77) : `p95(observations.latency) is above 15 over the last 1d`.

**La mesure qui l'a montré.** Les vrais appels de la fenêtre, lus par l'API :

```
2026-10-03T12:48:21 | DEFAULT | 5.82 s
2026-10-03T15:18:22 | DEFAULT | 6.07 s
2026-10-03T17:28:15 | DEFAULT | 2.78 s
nombre : 3
min 2.78 max 6.07 mediane 5.82
p95 (quantiles inclusifs) 6.04
```

Un p95 de 6 secondes ne dépasse pas 15 secondes. La documentation de l'API de métriques de Langfuse définit la
mesure `latency` comme « Observation latency (milliseconds) » : l'alerte comparait 6 040 ms à 15.

**La correction.** Seuil passé à `15000` par Era le 04/10. L'aperçu de l'alerte trace alors la ligne de seuil à 15 s
et la courbe réelle autour de 6 s, en dessous : `capture-2026-10-04-alerte-latence-seuil-15000.webp`.

**Pourquoi 15 secondes.** Les briefings mesurés durent de 2,8 à 6,1 s ; le banc C7 donne une médiane de 5,8 s par
OpenRouter. Quinze secondes, c'est plus du double du pire cas observé : l'alerte ne sonne que si le service se
dégrade vraiment. Ce seuil sera revu après une semaine de traces, comme prévu dans `docs/EXPLOITATION.md`.

## 5. Ce que la chaîne a révélé, et ce qui a été corrigé

| Défaut | Correction | Preuve |
|---|---|---|
| Seuil de latence en secondes au lieu de millisecondes | seuil 15000 | section 4, capture |
| Les issues portaient le nom générique « alerte Langfuse » : le workflow cherchait le nom dans `.name` ou `.title`, Langfuse l'envoie dans `.payload.message.title` | nom lu au bon endroit, gravité `[ALERT]` retirée pour garder un titre stable, gravité et message ajoutés au corps ; test écrit avant (rouge sur l'ancien workflow, vert sur le nouveau) | commit `f42697d`, CI `37195380776` : 781 passed, 29 skipped, 2 xfailed |

Effet de la seconde correction : à partir de la prochaine alerte, chacune ouvre sa propre issue
(« Incident : alerte Langfuse « RITA : appel au modèle trop lent » »). L'issue #77 reste telle quelle, comme trace
de l'avant.

## 6. Ce qui reste ouvert

- Constater le retour à OK des deux alertes (section 3 pour l'alerte 1 ; pour l'alerte 2, à la prochaine évaluation).
- La capture du tableau de bord « RITA C11 » (Era).
- Le serveur Hetzner n'envoie toujours aucune trace : il sert le code du 19/08, sans les variables Langfuse.
- Le palier gratuit n'offre que deux alertes : il n'y a pas d'alerte « aucune trace depuis 24 h » (silence du service).
  Ce manque est assumé et écrit ici.

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Alerte (Langfuse)** | une règle qui compare une mesure à un seuil sur une fenêtre de temps, et prévient quand elle est franchie |
| **Fenêtre** | la période sur laquelle la mesure est calculée, ici le dernier jour glissant |
| **p95** | la valeur sous laquelle tombent 95 % des mesures |
| **Faux positif** | une alerte qui sonne alors que rien ne va mal ; ici, une erreur d'unité |
| **Repository dispatch** | un appel d'un service extérieur qui déclenche un workflow GitHub Actions |
| **Charge utile** | le contenu JSON envoyé avec l'appel, ici par Langfuse |
| **Cascade** | l'ordre des fournisseurs de modèle : si l'un échoue, le suivant est essayé |
