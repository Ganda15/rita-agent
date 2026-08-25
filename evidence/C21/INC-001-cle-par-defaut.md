# INC-001 — L'API acceptait une clé écrite en clair dans son propre code source

| | |
|---|---|
| **Détecté le** | **18/08/2026**, par **relecture de code** dans le cadre de la revue OWASP API Top 10 — aucune alerte, aucun test rouge, aucun symptôme visible |
| **Sévérité** | **P1** — contournement complet de l'authentification |
| **Durée** | détection et correction le même jour |
| **Impact réel** | **aucune fuite constatée** : le dépôt était privé et l'API n'était pas encore déployée le 18/08. Le déploiement a eu lieu le **19/08 — le lendemain**. Sans cette relecture, la faille partait en production |
| **Commit du correctif** | `a4042b9` — *« OWASP API2 : supprime la cle par defaut devinable »* |
| **Issue / demande de fusion** | **aucune — commit direct sur `develop`** *(voir `README.md` : le critère 5 n'est pas satisfait pour cet incident, et on ne fabrique pas la trace après coup)* |

## 1. Ce qu'on a vu

Une ligne, dans `api/main.py` :

```python
os.getenv("RITA_API_KEY", "dev-key")
```

Rien ne clochait à l'exécution. Les tests passaient. L'API répondait 403 aux mauvaises clés et
200 à la bonne. **Le défaut était invisible à tout ce qui était en place pour le voir.**

## 2. Cause racine

**Cause technique** : `os.getenv(nom, defaut)` rend le second argument quand la variable est
absente. `RITA_API_KEY` n'étant pas définie dans l'environnement, la clé réellement attendue par
l'API était la chaîne **`dev-key`** — écrite en clair dans un fichier versionné, destiné à être
lu par le formateur puis par le jury.

> *Une clé par défaut n'est pas une clé : c'est une porte ouverte documentée.*

**Cause de conception — la vraie leçon** : la valeur par défaut existait pour du **confort de
développement**, afin que l'API démarre sans configuration. Ce confort a créé un mode de
fonctionnement dégradé **indiscernable du mode normal** : rien, ni au démarrage, ni dans les
journaux, ni dans les tests, ne signalait qu'on tournait sur la clé de secours.

C'est le point qui compte : **le défaut n'est pas la ligne, c'est le silence.**

## 3. Reproduction en développement

Reproduit immédiatement, en interrogeant l'API avec la chaîne écrite dans le code :

```
curl -H "X-API-Key: dev-key" http://127.0.0.1:8000/donnees/valeurs
-> 200 OK  (accès accordé)
```

Après correction, sur le serveur réel :

```
dev-key            -> 403
vraie clé (43 c.)  -> 200
```

## 4. Procédure de débogage

⚠️ Il n'y a pas eu de débogage au sens strict — **le défaut a été trouvé par lecture, pas par
symptôme**. C'est en soi une information : aucun des dispositifs de détection en place (tests,
journaux, revue de dépendances) ne pouvait l'attraper.

| # | Hypothèse | Comment elle a été testée | Résultat |
|---|---|---|---|
| 1 | La clé est bien lue depuis l'environnement | lecture de `api/main.py`, ligne par ligne, contre la liste OWASP API2 | ❌ **une valeur par défaut est présente** |
| 2 | La variable est peut-être définie ailleurs, rendant le défaut inerte | recherche de `RITA_API_KEY` dans `.env` | ❌ **absente du `.env`** — donc c'est bien `dev-key` qui servait |
| 3 | Le `.env.example` documente-t-il correctement la variable ? | lecture du fichier | ❌ **il documentait `POSTGRES_URL` port 5432** alors que le code lit `DATABASE_URL` sur **5433**, et omettait 3 variables — *un évaluateur qui suivait ce fichier échouait à démarrer le projet* |

L'hypothèse 3 est une **découverte annexe** : chercher une chose en révèle une autre. Elle est
consignée ici plutôt que traitée en silence.

## 5. Correction, étape par étape

1. **Suppression de la valeur par défaut**, remplacée par une **panne au démarrage**.
   *Choix assumé* : mieux vaut une API qui refuse de servir qu'une API qui sert n'importe qui.
2. **Message d'erreur qui dit quoi faire** — la commande de génération d'une clé y figure.
   *Raison* : un garde-fou qui bloque sans expliquer finit contourné par celui qu'il protège.
3. **Longueur minimale de 16 caractères** — une clé courte se devine ou se force.
4. **Comparaison par `secrets.compare_digest`** au lieu de `==`.
   *Raison* : l'égalité de chaînes s'arrête au premier caractère différent, ce qui laisse fuir
   de l'information par le temps de réponse (attaque temporelle).
5. **`tests/conftest.py` créé** : la clé de test est posée une fois pour toutes en `autouse`,
   pour que la suite ne dépende pas de l'environnement de la machine.
6. **`.env.example` entièrement réécrit** (découverte annexe, hypothèse 3).

## 6. Vérification et non-régression

Vérifié **sur le serveur réel**, pas seulement en test : `dev-key` → **403**, vraie clé de
43 caractères → **200**.

Le correctif ajoute **+216 lignes sur 5 fichiers**, dont **85 dans `tests/test_health.py`** et
42 dans `tests/conftest.py` : *le volume de test dépasse le volume de correction*, ce qui est
attendu pour un défaut de sécurité.

**Tests de non-régression** : `tests/test_health.py` (démarrage refusé sans clé, refusé si clé
trop courte) et `tests/test_api_donnees.py::test_toute_route_donnees_est_protegee` — ce dernier
énumère **dynamiquement** toutes les routes `/donnees` et vérifie qu'aucune ne répond sans clé.
*Il a d'ailleurs validé automatiquement le point de terminaison `/donnees/fraicheur` ajouté le
25/08, sans qu'on ait à y penser.*

## 7. Ce que ça change pour la suite

- **Règle adoptée** : aucun secret n'a de valeur par défaut. L'absence de configuration doit
  provoquer un **arrêt bruyant**, jamais un fonctionnement dégradé silencieux.
- **Découverte associée le même jour** : le `.gitignore` ne couvrait que le nom exact `.env` ;
  une copie `.env.sauvegarde-*` restait visible de Git. Élargi à `.env.*` avec exception pour
  `.env.example` (commit `0a8ff0b`). **Défaut créé puis trouvé le jour même, avant tout
  commit — rien n'a fuité.**
- **Ce que ça dit du dispositif de détection** : ce défaut est passé sous 300 tests et une
  intégration continue. Il n'a été vu que par une **relecture humaine dirigée par une liste**
  (OWASP API Top 10). Les tests vérifient ce qu'on a pensé à vérifier ; une liste de contrôle
  externe apporte ce à quoi on n'a pas pensé.
