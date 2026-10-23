# Sprint 5, étape 11 : les preuves sur la copie en marche (22/10/2026, 18 h 56 - 19 h 34)

Prototype local du sprint 5 (projet Docker `rita-s5`, `http://localhost:8011`). Commandes lancées par Claude pour Era
(option A, accord d'Era du 22/10 : création d'issues autorisée, plafond Azure 0,10 €), depuis
`D:\KandaWork\RITA_PROJECT\rita-agent-sprint-5`. Les programmes lisent les clés depuis `.env` ; les commandes ne les
affichent pas et ce fichier n'en recopie aucune. Aucun texte de question n'apparaît dans les sorties. Le journal brut,
commande par commande, est dans `preuves-copie-2026-10-22-journal.txt`.

## 1. Les commandes, l'attendu écrit avant, l'observé

| # | Heure | Commande | Code | Attendu | Observé | Verdict |
|---|---|---|---|---|---|---|
| 0 | 18:56:43 | contrôle préalable | | aucune issue de la vigie ouverte ; arbre propre ; commit `699e479` | `issues de la vigie ouvertes : {}` ; 0 fichier modifié ; `/health` `f8b13c8245f2` | conforme |
| 1 | 18:56:52 | `scripts\copie_sprint5.py deployer` | 0 | `/health` annonce `699e479` ; précédente `f8b13c8` | `déployée, /health annonce 699e479adc46 ; version précédente gardée : f8b13c8245f2` (14 s) | conforme |
| 2 | 18:57:16 | `scripts\copie_sprint5.py revenir` | 0 | `/health` annonce `f8b13c8` ; image vérifiée ; précédente aucune | `revenue à f8b13c8245f2 ; /health l'annonce, image vérifiée (sha256:422925e5…)` ; image du conteneur = image `rita-api:s5-f8b13c8245f2` ; `construit_le` revenu à 18:11:20 (pas de reconstruction) ; 6 s | conforme |
| 2 bis | 18:57:34 | `revenir` une seconde fois | 1 | refusé | `retour arrière refusé : aucune version précédente` | conforme |
| 3 | 18:57:35 | `deployer` | 0 | courante `699e479`, précédente `f8b13c8` | `version courante : 699e479adc46` ; `version precedente : f8b13c8245f2` | conforme |
| 4 | 18:57:58 | `python -m monitorage.vigie` (à blanc) | 0 | rien à ouvrir | `passage terminé, code 0` | conforme |
| 5a | 18:58:13 | `python -m monitorage.exercer panne` | 0 | panne posée | `panne simulée posée par Claude pour Era, fin au plus tard à 17:18` : heure du conteneur en UTC (anomalie 1, § 3) | conforme, avec anomalie |
| 5b | 18:58:16 | `python -m monitorage.exercer appels` | 0 | 5 × HTTP 503 `FOURNISSEUR_INDISPONIBLE` | 5 × `HTTP 503 erreur FOURNISSEUR_INDISPONIBLE`, vérifié ligne à ligne | conforme |
| 5c | 18:58:19 | `python -m monitorage.vigie --github` | 1 | issue `erreurs_techniques` ouverte | `ouverte : Incident : vigie (prototype local) « erreurs_techniques »` : [#127](https://github.com/Ganda15/rita-agent/issues/127), étiquettes `E5`, `incident` | conforme |
| 6 | 19:00:07 | diagnostic selon `docs/exploitation.md` | 0 | motif trouvé, exercice trouvé, panne retirée | `/health` `status ok` ; 5 lignes `question servie … statut=erreur motif=FOURNISSEUR_INDISPONIBLE` avec leur `request_id` ; `/sante` : exercice « Claude pour Era : preuves étape 11 » ; `exercer fin` : `exercice terminé` | conforme |
| 7a | 19:00:25 | `exercer appels` (questions réelles vers Azure) | 0 | 5 × HTTP 200 | `HTTP 200 reponse OK` × 3, `HTTP 200 refus ABSTENTION` × 2, vérifié ligne à ligne | conforme |
| 7b | 19:00:40 | `vigie --github` | 1 | commentaire « Service rétabli », issue non fermée | `commentée : … « erreurs_techniques » (service rétabli)` ; commentaire « Service rétabli à 19:00 … L'alerte de taux reste ouverte jusqu'à 19:13 environ » ; taux 5 sur 10 (50 %), PROBLÈME | conforme |
| 7c | 19:00:44 | lecture de `/sante` | 0 | coût sous le plafond (0,10 €) | `cout_24h : 0.009486 EUR` (2 420 jetons d'entrée, 250 de sortie) | conforme |
| 8 | 19:14:25 | `vigie --github` (19:13 + 60 s de marge) | 0 | issue #127 fermée | `fermée : … « erreurs_techniques »` ; #127 CLOSED à 19:14 ; « Retour à la normale le 22/10/2026 19:14 … Valeur actuelle : 0,0 % (0 sur 5 résultats) » | conforme |
| 9a | 19:15:03 | `python -m monitorage.exercer derive` | 0 | 12 × refus `TENTATIVE_DETOURNEMENT`, 0 jeton | 12 × `HTTP 200 refus TENTATIVE_DETOURNEMENT`, vérifié ligne à ligne ; `jetons ajoutés : 0` ; 87 s | conforme |
| 9b | 19:16:30 | `vigie --github` | 1 | issue `refus_securite` ouverte | `ouverte : … « refus_securite »` : [#128](https://github.com/Ganda15/rita-agent/issues/128) | conforme |
| 10a | 19:17:11 | action de la doc : lire les refus | 0 | des refus de prompts hostiles connus | 12 lignes `statut=refus motif=TENTATIVE_DETOURNEMENT`, durée 0 à 12 ms (refus avant le modèle) ; lecture : exercice de dérive, rien à corriger | conforme |
| 10b | 19:32:33 | `vigie --github` (dernier refus 19:16:30 + 15 min + 60 s) | 0 | issue #128 fermée | `fermée : … « refus_securite »` ; #128 CLOSED à 19:32 | conforme |
| 11a | 19:33:10 | `deployer` (correctif `d43a01e`, § 3) | 0 | courante `d43a01e`, précédente `699e479` | `version courante : d43a01e64b93` ; `version precedente : 699e479adc46` | conforme |
| 11b | 19:33:31 | `exercer panne --duree-min 1`, puis `fin`, sans appel | 0 | heure locale | `fin au plus tard à 19:34` (heure de Paris) ; `exercice terminé` | conforme |

## 2. Les captures du tableau de bord (prises par Era)

| Fichier | Moment | Ce qu'elle montre |
|---|---|---|
| `captures/copie-0-redemarrage-pendant-le-retour-arriere.webp` | 18:57:19, pendant le retour arrière | panne partielle : « Le service ne répond pas » en PROBLÈME, les autres cartes INCONNU, « le tableau de bord n'a pas pu lire les mesures » |
| `captures/copie-1-panne-en-cours.webp` | 18:58:49 | bandeau « Exercice de panne en cours depuis 18:58 … fin au plus tard à 19:18 » ; « Réponses en erreur » PROBLÈME, 5 sur 5 (100 %) |
| `captures/copie-2-service-retabli-alerte-ouverte.webp` | 19:00:49 | plus de bandeau ; « Réponses en erreur » encore PROBLÈME, 5 sur 10 (50 %) : service rétabli, alerte pas encore résolue |
| `captures/copie-3-derive-refus-securite.webp` | 19:19:19 | « Refus de sécurité » PROBLÈME, 12 sur 12 (100 %), avec sa consigne ; « Réponses en erreur » SAIN |

## 3. Les anomalies relevées

1. **Heures en UTC hors du tableau de bord.** Le conteneur tourne en UTC : la commande affichait « fin au plus tard
   à 17:18 » pour 19:18 heure de Paris, et l'issue #127 disait « Exercice … depuis 16:58 » sous un titre « 18:58 (heure
   du poste) ». Le tableau de bord convertissait déjà correctement. **Corrigé** (commit `d43a01e`, tests rouges puis
   verts) et **vérifié sur la copie** (étape 11b : « 19:34 »). Le corps de l'issue #127, déjà publié, garde l'heure UTC.
2. **Délai d'indexation de GitHub.** Juste après l'ouverture de #127, la liste des issues de la vigie était vide
   (`{}`) ; quelques secondes plus tard, #127 y figurait avec ses étiquettes. Un second passage de la vigie lancé dans
   ces secondes-là pourrait ouvrir un doublon. En pratique, les passages sont espacés de plusieurs minutes. Limite
   écrite : laisser au moins 30 s entre deux passages.

## 4. Les limites relevées pendant les preuves

- La commande `exercer appels` rend toujours le code 0, quels que soient les statuts : la preuve repose sur la
  vérification de chaque ligne, faite ci-dessus.
- Pour des refus instantanés, le tableau de bord affiche « 95 % des réponses en moins de 0,0 s » : exact, mais peu
  lisible ; « moins de 0,1 s » serait plus clair.
- Deux des cinq questions de test reçoivent une abstention (`ABSTENTION`) : le corpus de démonstration n'a que
  6 articles synthétiques. Les questions de la démo (étape 13) seront choisies parmi celles qui reçoivent une réponse.

## 5. Le contrôle final (19:33:37)

| Contrôle | Attendu | Observé |
|---|---|---|
| `/health` | la dernière version | `d43a01e64b93` (le correctif, déployé après les preuves) |
| Version précédente | un retour arrière encore possible | `699e479adc46` |
| Exercice en cours | aucun | `None` |
| Issues de la vigie ouvertes | aucune | `{}` ; #127 et #128 fermées par la vigie |
| Questions réelles envoyées à Azure | 5 | 5 (étape 7a) |
| Jetons de la dérive | 0 | 0 |
| Coût estimé de l'exercice | au plus 0,10 € | 0,009486 € |
| Image de la pile locale | inchangée | `rita-api:local` `sha256:cd6be8374a7f` |

L'écart avec le plan écrit avant (version finale `699e479`, précédente `f8b13c8`) vient du correctif de
l'anomalie 1, déployé à la fin : la version finale est `d43a01e`, la précédente `699e479`.
