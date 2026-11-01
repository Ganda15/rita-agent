# INC-009 : un message de retour à la normale a ouvert un nouveau ticket d'incident

| | |
|---|---|
| **Détecté le** | 31/10/2026, au soir, en préparant le rapport E5 : relecture des issues `incident` restées ouvertes. #137 portait « Gravité OK » et « recovered ». Le défaut n'a pas été signalé par une alerte : c'est la chaîne d'alerte elle-même qui l'a produit |
| **Sévérité** | **P3** : aucun effet sur le service ni sur les données. Un faux ticket d'incident, qui brouille le suivi et pouvait faire croire à une nouvelle panne de fournisseur |
| **Durée** | du 24/10, 08:30 UTC (création de #137), au 31/10, 22:48 (correctif vérifié sur le poste). Le correctif ne s'applique aux vraies alertes qu'une fois sur `main` : pas encore fait |
| **Impact réel** | une issue (#137) ouverte à tort, restée sans traitement sept jours ; aucune alerte réelle perdue |
| **Commit du correctif** | `a57dccb` (branche `fix/137-retour-a-la-normale`) |
| **Issue / demande de fusion** | issue [#137](https://github.com/Ganda15/rita-agent/issues/137), débogage écrit dans l'issue le 31/10 ; PR [#171](https://github.com/Ganda15/rita-agent/pull/171) vers `develop` |

## 1. Ce qu'on a vu *(critère 1 : le symptôme, avant la cause)*

Issue #137, ouverte le 24/10/2026 à 08:30 UTC par le workflow `alerte-incident.yml`, titre
« Incident : alerte Langfuse « RITA : fournisseur en erreur » », aucun commentaire. Son tableau :

```
| Gravité | OK |
| Détail | `count(observations.count)` recovered |
```

Dans la charge utile envoyée par Langfuse : `"title": "[OK] RITA : fournisseur en erreur"`, `"severity": "OK"`,
fenêtre du 23/10 08:30 au 24/10 08:30 UTC. La veille, l'issue #130 de la même alerte avait été ouverte à 08:30 UTC,
puis fermée à la main à 09:48 : fausse alerte qualifiée (les erreurs venaient de l'exercice de panne simulée de la
copie locale, qui envoyait alors ses traces au projet Langfuse de la production).

## 2. Cause racine *(critère 1)*

**Cause technique** (`.github/workflows/alerte-incident.yml`, version du commit `4be89d0`) :

- ligne 67 : la gravité est retirée du titre (« [OK] », « [ALERT] »), volontairement, pour garder un titre stable
  par alerte ;
- ligne 68 : la gravité est lue, mais seulement affichée dans le corps de l'issue ;
- lignes 119 à 125 : sans issue ouverte du même titre, une issue est créée, quelle que soit la gravité.

**Cause de conception.** La chaîne a été pensée le 02/10 pour des alertes. Le 04/10, le titre a été corrigé après
#77 ; les retours à OK de cette époque arrivaient sur une issue restée ouverte et devenaient des commentaires,
sans dommage. La conception supposait donc qu'un incident reste ouvert jusqu'à son retour à OK. Le défaut n'apparaît
que si l'incident est fermé avant, c'est-à-dire quand la fermeture est faite pour une bonne raison (ici, une fausse
alerte qualifiée). Les tests du 04/10 vérifiaient le titre, pas la décision « ouvrir ou commenter » selon la gravité.

**Pourquoi il est passé inaperçu.** #137 ressemblait à un vrai incident, et aucune routine ne relit les issues
`incident` ouvertes : #137 est resté sept jours sans traitement, #77 quatre semaines.

## 3. Reproduction en développement *(critère 2)*

Les deux étapes du workflow, rejouées telles qu'elles sont écrites dans le fichier, avec la charge utile de #137 et
un faux `gh` qui note les appels au lieu de les faire. Le poste n'a pas `jq` : conteneur jetable de l'image
`rita-tests` (Debian 13, Python 3.13.15, pytest 9.1.1), `jq` 1.7.1 téléchargé dans le conteneur seulement, avec
l'accord d'Era. Trois fichiers montés en lecture seule (le workflow, les tests, le guide d'exploitation) ; aucun
`.env`, aucune variable `GH_` ou `GITHUB_`, pas de vrai `gh` ; conteneur supprimé après l'exécution.

```
docker run --rm --pull=never -v <workflow>:ro -v <tests>:ro -v <guide>:ro rita-tests:latest \
  bash -c "apt-get install jq ; python -m pytest -v tests/test_alerte_incident.py"

AssertionError: un retour à OK a créé une issue :
 ['issue list --label incident --state open --search "Incident : alerte Langfuse « RITA : fournisseur en erreur »" in:title --json number,title',
  'issue create --title Incident : alerte Langfuse « RITA : fournisseur en erreur » --label incident --body-file corps.md']
1 failed, 13 passed
```

Workflow testé : commit `4be89d0`, sans modification locale, sha256 `f3f85f72…e7d1d1`. Journaux complets :
[`INC-009-reproduction/pytest-avant.txt`](INC-009-reproduction/pytest-avant.txt),
[`versions-hote-avant.txt`](INC-009-reproduction/versions-hote-avant.txt),
[`versions-conteneur-avant.txt`](INC-009-reproduction/versions-conteneur-avant.txt).

## 4. Procédure de débogage *(critère 3)*

Écrite dans l'outil de suivi : [commentaire du 31/10 sur #137](https://github.com/Ganda15/rita-agent/issues/137#issuecomment-6549650079).

| # | Hypothèse | Comment elle a été testée | Résultat |
|---|---|---|---|
| 1 | Une nouvelle panne de fournisseur les 23 et 24/10 | Lecture de #137 : gravité `OK`, message « recovered » | écartée : c'est un retour à la normale |
| 2 | Langfuse a envoyé l'alerte en double | Identifiant de la charge utile (`57467bab…`), différent de celui de #130 ; gravité différente | écartée : deux messages distincts, une alerte puis son retour à OK |
| 3 | Le workflow ne distingue pas un retour à OK d'une alerte | Lecture des lignes 67, 68 et 119 à 125 | confirmée : la gravité est affichée, jamais utilisée pour décider |
| 4 | Il faut réécrire la logique en Python pour la tester sur le poste, faute de `jq` | Relecture d'Era : ce serait tester un autre code que celui qui tourne | **fausse piste de méthode**, abandonnée : on rejoue le vrai script, dans un conteneur qui a `jq` |
| 5 | Le défaut se reproduit sur le code actuel | Test rejoué sur le workflow de `4be89d0` (section 3) | confirmée : `issue create` demandé pour un message OK |

## 5. Correction, étape par étape *(critère 4)*

1. **Repérer le retour à la normale avant de retirer la gravité du titre** : `retablie=oui` si `.payload.severity`
   vaut `OK`, ou si le titre commence par « [OK] » (au cas où la gravité manquerait). Sortie `retablie` de l'étape.
2. **Décider selon la gravité** : une issue ouverte pour cette alerte est commentée, comme avant ; sans issue ouverte,
   un retour à OK ne crée rien et l'écrit dans le journal de l'exécution ; une alerte crée l'issue, comme avant.
3. **Ne rien fermer automatiquement.** Un retour à OK dit que la condition d'alerte n'est plus remplie au moment du
   calcul, pas que le défaut est corrigé : le commentaire le dit, et la fermeture reste une décision humaine,
   justifiée (résolution vérifiée, fausse alerte qualifiée ou exercice terminé).

**Pourquoi ce choix.** Le plus petit changement qui corrige la décision, dans le langage du workflow : le code testé
est celui qui tourne sur GitHub. Fermer automatiquement à la réception d'un OK aurait effacé un incident avant son
diagnostic.

## 6. Vérification et non-régression *(critères 2 et 5)*

Même image, mêmes montages, même fichier de tests (dernière modification le 31/10 à 22:39:44, avant les deux
exécutions), workflow corrigé, sha256 `e1bd611e…c0b284` :

```
14 passed in 0.21s
```

Journaux : [`pytest-apres.txt`](INC-009-reproduction/pytest-apres.txt),
[`versions-hote-apres.txt`](INC-009-reproduction/versions-hote-apres.txt),
[`versions-conteneur-apres.txt`](INC-009-reproduction/versions-conteneur-apres.txt). Les alertes `ALERT` se
comportent comme avant : création sans issue ouverte, commentaire sinon.

**Tests de non-régression** (`tests/test_alerte_incident.py`, exécutés aussi par le runner GitHub, qui a `jq`) :

- `test_un_retour_a_la_normale_sans_issue_ouverte_ne_cree_aucune_issue` : le cas de #137 ;
- `test_un_retour_a_la_normale_commente_l_issue_ouverte_sans_la_fermer` ;
- `test_une_alerte_sans_issue_ouverte_cree_une_issue` et `test_une_alerte_repetee_commente_l_issue_ouverte`.

## 7. Ce que ça change pour la suite

- **Activer le correctif** : `repository_dispatch` exécute le workflow de la branche par défaut ; tant que la PR n'est
  pas arrivée sur `main`, une vraie alerte suit encore l'ancien code.
- **Relire les issues `incident` ouvertes** : #137 est resté sept jours sans traitement, #77 quatre semaines. Aucune
  routine n'est fixée ; la décision revient à Era.
- **Séparer exercice et production dans Langfuse** : le mélange a provoqué la fausse alerte de #130 (et l'INC-006).
  Le guide d'exploitation demande déjà un projet distinct pour la copie locale ; la séparation effective des
  configurations actuelles reste à vérifier.
- **Non fait** : le bouton « Run workflow » ne peut pas envoyer un retour à OK ; le chemin « OK » n'est donc prouvé
  que par les tests, pas par une exécution sur GitHub.

## 📖 Glossaire

- **Retour à la normale (OK, « recovered »)** : message de Langfuse qui dit que la condition d'une alerte n'est plus
  remplie au moment du calcul.
- **Charge utile** : le contenu JSON envoyé par Langfuse au dépôt, avec le nom de l'alerte et sa gravité.
- **`jq`** : outil en ligne de commande qui lit et filtre du JSON ; le workflow s'en sert.
- **Faux `gh`** : petit programme du test, nommé comme l'outil GitHub, qui note les appels au lieu de les faire.
- **Conteneur jetable** : environnement isolé, créé pour une exécution puis supprimé.
