# C5 · Preuve — API REST de mise à disposition du jeu de données

**Compétence C5** : « Développer une API mettant à disposition **le jeu de données** en
utilisant l'architecture REST afin de permettre l'exploitation du jeu de données par les
autres composants du projet. »

**Fichiers** : `api/donnees.py` · `api/main.py` · **Tests** : `tests/test_api_donnees.py` (25)
**Date** : 2026-08-01

## La distinction qui a motivé ce travail

L'API existante exposait `/briefing` — **un texte rédigé par un modèle**. C'est **C9**
(exposer un modèle d'IA), pas C5. C5 demande le **jeu de données** lui-même.

```
/donnees/*    la donnee brute, filtrable        -> C5
/briefing     un texte redige par un modele     -> C9
```

## Les 6 points de terminaison

| Route | Ce qu'elle expose |
|---|---|
| `GET /donnees/valeurs` | l'univers suivi, avec `statut_qualite` |
| `GET /donnees/cotations?ticker=&depuis=` | l'historique d'une valeur |
| `GET /donnees/portefeuille` | ⚠️ positions valorisées en euros (RGPD) |
| `GET /donnees/mouvements` | plus fortes variations |
| `GET /donnees/volumes-anormaux` | signal de volume |
| `GET /donnees/articles` | actualités RSS |

## Les 5 critères de C5

| Critère | État | Preuve |
|---|---|---|
| Doc technique couvre **tous** les points de terminaison | ✅ | test `test_chaque_route_a_un_resume_documente` |
| Doc couvre les règles d'**authentification / autorisation** | ✅ | `securitySchemes` dans OpenAPI |
| Doc respecte un **standard** (OpenAPI) | ✅ | **OpenAPI 3.1.0**, 8 chemins documentés |
| API **restreint** l'accès par autorisation | ✅ | 403 sur les 6 routes sans clé |
| API permet de récupérer **l'ensemble** des données | ✅ | 4 tables du jeu couvertes |

## Sortie réelle

```
=== 1. Sans cle : l'acces doit etre REFUSE ===
  /donnees/valeurs             -> 403 OK refuse
  /donnees/portefeuille        -> 403 OK refuse
  /donnees/articles            -> 403 OK refuse

=== 2. /health reste public ===
  /health -> 200 {'status': 'ok', 'project': 'RITA'}

=== 3. Avec cle : les donnees sortent ===
  /donnees/valeurs?limite=3                 -> 200  nb=3
  /donnees/portefeuille                     -> 200  nb=7  total=31,264.10 EUR
  /donnees/mouvements?limite=3              -> 200  nb=3
  /donnees/volumes-anormaux                 -> 200  nb=4
  /donnees/articles?limite=2                -> 200  nb=2
  /donnees/cotations?ticker=MC.PA&limite=2  -> 200  nb=2

=== 4. Ticker inexistant -> 404 ===
  -> 404

=== 5. Contrat OpenAPI ===
  version OpenAPI : 3.1.0
  points de terminaison documentes : 8
```

## 💎 Trois choix de conception à défendre

### 1. La protection est posée sur le ROUTEUR, pas sur chaque route

```python
app.include_router(routeur_donnees, dependencies=[Depends(verify_api_key)])
```

**Pourquoi** : un point de terminaison ajouté plus tard est protégé **d'office**. Poser la
dépendance route par route revient à parier sur la discipline du développeur — **un
garde-fou de conception vaut mieux qu'un garde-fou de vigilance.**

Vérifié par test : `test_toute_route_donnees_est_protegee` parcourt les routes déclarées et
échoue si l'une répond autre chose que 403 sans clé.

### 2. La pagination est plafonnée **côté serveur**

`cotation` compte 273 611 lignes. Un `GET` sans limite renverrait des dizaines de mégaoctets
et ferait tomber le client comme le serveur.

```python
limite: int = Query(250, ge=1, le=LIMITE_MAX)   # LIMITE_MAX = 1000
```

Un client qui demande 99 999 reçoit **422**, pas 273 611 lignes. Testé sur 3 routes.

### 3. `bloque_injection = FALSE` est **codé en dur**

Un article porteur d'injection ne doit **jamais** sortir de l'API, même si un appelant le
demande explicitement. Il reste consultable en base pour audit — pas ici.

Testé : `test_les_articles_bloques_ne_sortent_jamais` inspecte le SQL réellement envoyé.

## Limite assumée : une seule clé d'API

RITA est mono-utilisateur (décision D10). Un système de comptes serait de la complexité sans
besoin. **La contrepartie est réelle** : pas de révocation partielle, pas de traçabilité par
appelant. Documenté dans la docstring de `verify_api_key`.

## Tests

```
C:\Python314\python.exe -m pytest tests/test_api_donnees.py -q
→ 25 passed
```

**12 des 25 tests portent sur l'autorisation** — le critère central de C5. Chaque route est
testée **sans clé** et **avec une mauvaise clé** : un contrôle d'accès qui protège 5 routes
sur 6 ne protège rien.

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **API REST** | Interface web où chaque URL représente une ressource |
| **Point de terminaison** (*endpoint*) | Une URL de l'API — ex. `/donnees/valeurs` |
| **OpenAPI** | Norme décrivant une API REST, lisible par machine |
| **`/openapi.json`** | Le contrat de l'API, généré automatiquement par FastAPI |
| **`/docs`** | Documentation interactive générée depuis l'OpenAPI |
| **Routeur** (*router*) | Groupe de routes partageant préfixe et règles |
| **Dépendance** (*dependency*) | Fonction exécutée avant la route — ici l'autorisation |
| **HTTP 403** | Interdit — la clé est absente ou invalide |
| **HTTP 404** | Ressource introuvable — ticker inexistant |
| **HTTP 422** | Paramètre invalide — limite hors bornes |
| **Pagination** | Découper un gros résultat en pages |
| **RGPD** | Règlement européen sur les données personnelles |
