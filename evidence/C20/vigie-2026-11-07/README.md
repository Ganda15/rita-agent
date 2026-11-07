# C20.5 : les alertes, configurées et en état de marche selon des seuils définis à l'avance (07/11/2026)

Critère : « Les alertes sont configurées et en état de marche, en fonction des seuils préalablement définis. » Le
registre des partiels (`docs/recette/registre-des-partiels.md`, ligne C20.5) attendait : la vigie planifiée, une alerte
et un retour à la normale testés hors production, l'exécution planifiée constatée. Heures en UTC ; une heure de plus à
Paris.

Les fichiers de ce dossier sont les sorties originales des opérations du 07/11, copiées sans modification depuis le
dossier de travail de l'autre agent qui les a menées avec Era, sauf ce README. Aucun ne contient de clé ; la
configuration privée de la copie est restée hors du dépôt. Les trois fichiers du passage planifié (section 4) ont été relevés
par `gh` le 07/11 à 21 h 55, sans modification.

## 1. Les seuils, définis à l'avance

`monitorage/seuils.json` (sprint 5, étape 3, « seuils argumentés ») porte, pour chaque signal, la fenêtre, le minimum
de requêtes, les seuils orange et rouge, et pour le signal `service` le nombre d'essais (2) et leur intervalle (10 s).
**Aucune de ces valeurs n'a changé** entre le commit `699e479` (22/10, 16 h 45) et le commit de production `6f428d6` :
`git diff 699e479 6f428d6 -- monitorage/seuils.json` ne touche aucune ligne `orange`, `rouge`, `fenetre_min`,
`minimum_requetes`, `essais` ou `intervalle_s` (les deux commits suivants ne changent que des phrases d'explication).

## 2. La configuration

- La vigie (`.github/workflows/vigie.yml`) tourne toutes les trois heures (`17 */3 * * *`) contre la production, avec le
  secret `RITA_API_KEY_VIGIE`. Le secret manquait jusqu'au 07/11 : la vigie échouait à chaque passage.
- Le 07/11, le secret a d'abord reçu une clé refusée (HTTP 403, passages 42410636772 et 42411132337 première tentative).
  Era a fait lire la seule clé de l'API active sur le serveur, l'a vérifiée (`/sante` 200), puis l'a transmise au secret
  par l'entrée standard, sans affichage ([`RESULTAT-VIGIE-2026-11-07.md`](RESULTAT-VIGIE-2026-11-07.md),
  [`verification-secret.json`](verification-secret.json), [`corriger_secret_vigie.py`](corriger_secret_vigie.py)).
  Secret enregistré à 20 h 33 07 s.
- Relance manuelle (42411132337, tentative 2) : succès, « vigie : passage terminé, code 0 ». Le code 0 veut dire
  qu'aucun verdict « problème » n'a été relevé ; des verdicts « attention » ou « inconnu » peuvent subsister.
- Les alertes Langfuse (`.github/workflows/alerte-incident.yml`) ouvrent des issues `incident` depuis le 03/10 (#71,
  essai manuel de la chaîne ; puis #130, #137).

## 3. L'alerte et le retour à la normale, sur copie (aucune panne en production)

**#230 vérifie l'ouverture et la clôture de l'alerte `service` avec le code actuellement en production, exécuté sur
copie. Les essais des 22-23/10 documentent les signaux en taux avec les mêmes valeurs de seuils, mais sur une version
antérieure.**

L'essai du 07/11 ([`RESULTAT-ESSAI-COPIE-2026-11-07.md`](RESULTAT-ESSAI-COPIE-2026-11-07.md),
[`essai-service.json`](essai-service.json), [`issue-essai-service.json`](issue-essai-service.json)) :

| Étape | Heure | Constat |
|---|---|---|
| Départ | 20 h 53 50 | `/health` et `/sante` de la copie répondent 200 |
| Arrêt de la copie | 20 h 53 51 | seul le conteneur de la copie est arrêté |
| Deux sondes en échec | 20 h 53 56, 20 h 54 10 | règle du signal `service` : 2 essais à 10 s d'écart |
| Alerte | 20 h 54 11 | issue [#230](https://github.com/Ganda15/rita-agent/issues/230) ouverte par la vigie, « Incident : vigie (prototype local) « service » » |
| Redémarrage | 20 h 54 13 | conteneur de la copie redémarré |
| Clôture | 20 h 55 19 | la vigie ferme #230 : « Retour à la normale le 07/11/2026 21:55 : /health répond de nouveau 200. » |

- Copie : même image Docker que la production (`sha256:1b262b59…`, commit `6f428d6`), copiée du serveur sans
  reconstruction, port publié sur `127.0.0.1:8011` seulement, base neuve, aucune clé de fournisseur, Langfuse coupé
  ([`copie-state.json`](copie-state.json), [`verification-isolation-finale.json`](verification-isolation-finale.json)).
- La fonction réelle `monitorage.vigie.passage` et les seuils de cette version ont servi sans modification. Un
  adaptateur du banc ([`essai_disponibilite.py`](essai_disponibilite.py)) limite les opérations GitHub au seul titre du
  signal `service` : sans lui, les compteurs vides de la copie auraient fermé l'ancien incident #132.
- Le journal garde un incident du banc : le premier contrôle, juste après la création, n'a pas retrouvé l'issue
  (assertion en échec, copie redémarrée par sécurité) ; la liste GitHub l'a ensuite retrouvée, et le rétablissement a
  repris sur **la même issue #230**. Rien n'a été effacé ni reconstitué.
- #77 et #132 n'ont pas été touchés (dernières mises à jour au 11/10 et au 23/10).

Les essais des 22-23/10, sur la copie du sprint 5 (`evidence/sprint-5/preuves-copie-2026-10-22.md`) : #127, #129
(`erreurs_techniques`), #128, #131 (`refus_securite`), chacun ouvert puis fermé par la vigie en un quart d'heure
environ. Mêmes valeurs de seuils qu'aujourd'hui ; code de la vigie antérieur au commit `04d5b93` (23/10, 15 h 12) qui
l'a préparée pour la production.

## 4. Le passage automatique en production

**Constaté le 07/11 à 21 h 52** : passage [42417908976](https://github.com/Ganda15/rita-agent/actions/runs/42417908976), événement `schedule` (déclenché par GitHub, pas à
la main), branche `main`, commit `6f428d6` (celui de la production), conclusion `success`. Il était prévu à 21 h 17 :
GitHub l'a lancé avec 35 minutes de retard. Sortie de la vigie, contre `https://178-104-184-125.sslip.io` avec
`--github` :

```
vigie : passage terminé, code 0 (0 sain, 1 problème, 2 /sante illisible)
```

Le code 0 veut dire que `/sante` a été lu avec la clé (sinon : code 2) et qu'aucun signal n'était en « problème ».
Aucune issue n'a été ouverte ni fermée : la liste des issues `incident` relevée à 21 h 55 ne contient aucun titre
« vigie (production) », et #77 et #132 restent ouvertes, inchangées.

Fichiers : [`passage-planifie-42417908976.json`](passage-planifie-42417908976.json) (métadonnées du passage),
[`passage-planifie-42417908976.txt`](passage-planifie-42417908976.txt) (journal complet, secrets masqués par
GitHub), [`issues-incident-2026-11-07-2155.json`](issues-incident-2026-11-07-2155.json).

Les passages planifiés de la journée, depuis l'arrivée du workflow sur `main` (#221, `a68f2cf`, 1 h 49) : sept
créneaux, trois passages `schedule`. 10 h 13 (42363054393) et 17 h 44 (42397820857) ont échoué, « Secret
RITA_API_KEY_VIGIE absent » ; 21 h 52 a réussi. Les autres créneaux n'ont donné aucun passage.

Le calcul des verdicts n'a pas changé depuis les essais des 22-23/10 : `git diff --stat 699e479 6f428d6` ne touche ni
`api/sante.py`, ni `monitorage/seuils.py`, `signaux.py` ou `compteurs.py`. Dans `monitorage/vigie.py`, les
changements portent sur le titre des issues (« production » ou « prototype local » selon l'adresse), la branche des
liens, l'heure dite dans le corps et le filtre de la liste des issues.

## 5. La réévaluation de C20.5

Élément par élément, sur les preuves de ce dossier :

| Élément du critère | Preuve |
|---|---|
| alertes configurées | `vigie.yml` sur `main` depuis le 07/11 (planification, secret) ; passage `schedule` 42417908976 ; alertes Langfuse (`alerte-incident.yml`) depuis le 03/10 |
| en état de marche | passage planifié réussi en production (section 4) ; ouverture et fermeture d'une alerte par la vigie, code de production, sur copie (#230) ; signaux en taux les 22-23/10 (#127 à #131), même calcul des verdicts ; chaîne Langfuse : #130, #137 |
| selon des seuils définis à l'avance | `monitorage/seuils.json`, valeurs inchangées depuis le 22/10 (section 1) |

Proposition : ✅ avec les limites ci-dessous, à valider par Era (règle 4 du registre des partiels).

## 6. Les limites

- L'essai sur copie couvre le signal `service` (la disponibilité) ; il ne refait pas aujourd'hui le scénario des
  signaux en taux (par exemple cinq erreurs du fournisseur en quinze minutes), documenté le 22-23/10 sur une version
  antérieure de la vigie.
- Aucune alerte n'a encore été émise par la vigie **de production** elle-même : la production était saine.
- Le déclenchement planifié dépend de GitHub, qui peut retarder ou sauter un passage : le 07/11, trois passages pour
  sept créneaux, le dernier avec 35 minutes de retard. Une panne peut donc attendre plus de trois heures son alerte.
- Deux incidents anciens restent ouverts (#77, alerte Langfuse du 04/10 ; #132, prototype local du 23/10) : ils ne
  sont fermés que si leur résolution est prouvée.
