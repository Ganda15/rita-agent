# C1 · Preuve 5 — Extraction par scraping HTML

**Type de source couvert** : **page web (scraping)** — le type le plus explicitement nommé
par C1
**Fichier** : `sources/scraper.py` · **Tests** : `tests/test_scraper.py` (20 tests)
**Cible** : pages `/cours/<symbole>/` de Boursorama · **Date** : 2026-07-31

## Commande

```powershell
Set-Location "D:\KandaWork\RITA_PROJECT\rita-agent"
C:\Python314\python.exe -X utf8 -m sources.scraper
```

## Sortie réelle

```
=== SCRAPING HTML — pages de cotation ===
Recuperees : 3/3

  Cours LVMH  (FR0000121014)
    place       : Euronext Paris données temps réel
    dernier     : 475.15   variation : 0.39 %
    O/H/L       : 468.95 / 478.9 / 467.5
    veille      : 473.3   volume : 429,187
    collecte le : 2026-07-31T21:54:36+00:00

  Cours L'OREAL  (FR0000120321)
    dernier     : 386.95   variation : -1.79 %
    O/H/L       : 391.05 / 392.35 / 384.45
    veille      : 394.0   volume : 427,656

  Cours AIR LIQUIDE  (FR0000120073)
    dernier     : 170.72   variation : -0.59 %
    O/H/L       : 170.92 / 173.14 / 170.36
    veille      : 171.74   volume : 1,441,279
```

## ⚖️ `robots.txt` vérifié AVANT toute requête

C1 demande l'identification des contraintes *« dont les règles de confidentialité »*. Pour
du scraping, cela commence par demander la permission :

```python
def scraping_autorise(url: str, agent: str = "*") -> bool:
    lecteur = _lecteur_robots(f"{partie.scheme}://{partie.netloc}")
    if lecteur is None:
        return False            # robots.txt illisible -> abstention par défaut
    return lecteur.can_fetch(agent, url)
```

**En cas de doute, on ne scrape pas.** Trois tests couvrent les trois cas : autorisé,
interdit, illisible.

### Optimisation mesurée

Première version : `robots.txt` téléchargé **une fois par page**.

```
INFO GET .../robots.txt   INFO GET .../cours/1rPMC/
INFO GET .../robots.txt   INFO GET .../cours/1rPOR/
INFO GET .../robots.txt   INFO GET .../cours/1rPAI/
```

Sur 3 valeurs c'est négligeable ; sur les 111 de l'univers, c'est **111 requêtes inutiles**
sur le même fichier. Cache par domaine via `@lru_cache` :

```
avant : 3 téléchargements de robots.txt
après : 1
```

Vérifié par test (`test_robots_est_mis_en_cache_par_domaine` : `call_count == 1` pour
3 pages). C'est autant une question de politesse envers le site que de latence.

## 💎 Le choix de cible : trois échecs avant le bon

Un scraper ne vaut que par la page qu'il peut réellement lire. Quatre cibles testées :

| Cible | Résultat | Verdict |
|---|---|---|
| **AMF** (actualités du régulateur) | HTTP 200 mais **liste rendue en JavaScript** | ❌ absente de l'HTML — exigerait un navigateur *headless* |
| **Wikipédia FR** | **HTTP 403** sur requête simple | ❌ |
| Zonebourse / Boursier / ABC Bourse | **HTTP 403** | ❌ anti-bot |
| **Boursorama** `/cours/` | HTTP 200, **HTML statique**, robots.txt autorise | ✅ retenu |

Le cas AMF est le plus instructif : **HTTP 200 ne veut pas dire exploitable.** La page
répond, pèse 54 ko, et ne contient aucun article — ils sont injectés par JavaScript après
chargement. Un scraper HTTP simple ne voit rien.

> C'est la distinction entre *page accessible* et *contenu accessible*. On la vérifie en
> comptant les éléments attendus dans l'HTML brut, pas en regardant le code de statut.

## 🚨 Un scraper cassé doit crier

Une page HTML n'offre **aucun contrat**. Une API publie un schéma et le fait vivre ;
Boursorama peut renommer `.c-instrument--last` demain sans prévenir.

Le piège classique : retourner `None` silencieusement. Les données partent en base, le
briefing s'affiche avec des trous, personne ne voit rien pendant des semaines.

```python
if all(champ in absents for champ in CHAMPS_OBLIGATOIRES):
    raise StructurePageModifiee(
        f"Aucun champ obligatoire trouve pour {symbole}. "
        f"Selecteurs a revoir : {list(SELECTEURS.values())}"
    )
```

**Distinction assumée** : un champ *optionnel* absent (le volume) est signalé dans
`champs_absents` sans interrompre ; l'absence de **tous** les champs obligatoires lève.
Deux tests séparés couvrent les deux comportements.

## 🛡️ Garde-fou d'injection sur le contenu extrait

Le nom de société, l'ISIN et la place de cotation viennent d'une page tierce et finiront
dans le contexte du Rédacteur :

```python
verdict = neutraliser(f"{nom}\n{isin_brut}\n{place}", source=f"scraping:{symbole}")
```

Test : une page dont le nom de société est *« Ignore les instructions precedentes »*
ressort avec `motifs_injection == ['ignore_instructions_fr']`, une page normale avec `[]`.

C'est exactement le scénario du **point 4 du standard Velmo 2.0** — la porte d'entrée des
outils, celle qu'on oublie.

## 🔢 Conversion des nombres au format français

Piège classique du scraping FR : les milliers sont séparés par un **espace insécable**
(`\xa0`), la décimale est une virgule.

```
« 475,15 »      -> 475.15
« 429 187 »     -> 429187.0    (\xa0 géré)
« +0,39% »      -> 0.39
« n/a »         -> None
```

8 cas testés en `parametrize`.

## Tests

```
C:\Python314\python.exe -m pytest tests/test_scraper.py -q
→ 20 passed
```

| Famille | Ce qui est couvert |
|---|---|
| Parsing | tous les champs, conversion FR, horodatage UTC |
| Robustesse | refonte du site → erreur explicite · champ optionnel absent → trace |
| Garde-fou | texte hostile détecté · page normale non bloquée |
| robots.txt | autorisé · interdit · illisible → abstention · **mise en cache** |
| Collecte | un symbole en échec n'emporte pas les autres |

## Limites assumées

| Limite | Conséquence |
|---|---|
| Dépend de la structure HTML de Boursorama | rupture possible sans préavis — d'où `StructurePageModifiee` |
| Ne lit pas les pages rendues en JavaScript | l'AMF resterait hors de portée sans navigateur *headless* |
| Pas de cache des pages | acceptable : 3 valeurs, briefing quotidien (décision D8) |

## 🎤 Phrase pour l'oral

> « Pour le scraping, j'ai testé quatre cibles. L'AMF répond HTTP 200 mais sa liste
> d'actualités est rendue en JavaScript : la page est accessible, le contenu ne l'est pas.
> J'ai retenu Boursorama, en HTML statique, après avoir vérifié son robots.txt — que je
> mets en cache par domaine, sinon je le téléchargerais 111 fois pour 111 valeurs. Et si
> Boursorama change sa structure, mon scraper lève une exception au lieu de retourner des
> valeurs vides : une panne silencieuse qui pollue la base est bien pire qu'un plantage. »
