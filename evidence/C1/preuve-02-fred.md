# C1 · Preuve — source FRED (indicateurs macro-économiques US)

**Compétence C1** : « Automatiser l'extraction de données depuis **un service web**, une page
web (scraping), un fichier de données, une base de données et un système big data en
programmant le script adapté afin de pérenniser la collecte des données nécessaires au projet. »

**Fichier** : `sources/fred.py` · **Tests** : `tests/test_fred.py` (9) · **Date** : 2026-08-02

---

## 1. Pourquoi cette source existe

RITA disposait déjà de six sources. Aucune ne répondait à la question **« pourquoi »**.

| Sans FRED | Avec FRED |
|---|---|
| « MC.PA a baissé de 3 % hier. » | « MC.PA a baissé de 3 % le jour où le 10 ans américain a pris 12 points de base. » |
| un **constat** | un **contexte** |

Aucune autre source ne peut produire la seconde phrase : la BCE donne des taux de change,
Boursorama des cours, le RSS des titres d'articles. **Personne ne donne le climat de marché.**

Les taux américains pilotent les marchés mondiaux, y compris les actions européennes que RITA
suit. C'est la raison d'être de cette source — **pas** un critère supplémentaire.

## 2. ⚠️ Ce que cette source n'apporte PAS, dit franchement

FRED est de type **service web**, exactement comme la BCE. Elle **ne fait gagner aucun critère
C1** : le référentiel raisonne en *types* de sources, et ce type était déjà couvert.

Elle a été codée pour une raison **produit**, pas pour une raison de grille. Le dire au jury
avant qu'il ne pose la question vaut mieux que de le défendre après.

## 3. Les trois séries retenues

| Code | Ce que c'est | Pourquoi pour un portefeuille européen |
|---|---|---|
| `DGS10` | Rendement du Trésor américain à 10 ans | le taux de référence mondial ; quand il monte, les actions souffrent |
| `CPIAUCSL` | Indice des prix à la consommation US | pilote les décisions de la Réserve fédérale |
| `DFF` | Taux directeur effectif de la Fed | l'outil de la Fed, effet direct sur les marchés |

## 4. Sortie réelle

```
PREUVE REELLE — sources/fred.py
==============================================================
  DGS10      2026-07-30          4.68   Rendement du Tresor americain a 10 ans
  CPIAUCSL   2026-06-01        332.57   Indice des prix a la consommation (inflation US)
  DFF        2026-07-30          3.63   Taux directeur effectif de la Reserve federale

  DGS10 sur 400 observations demandees -> 383 retenues
  17 ecartees (valeur '.') = jours feries federaux US
```

## 5. 💎 Deux particularités **mesurées**, pas supposées

La structure de la réponse a été relevée en direct avant d'écrire une ligne de code — la même
méthode que pour la BCE.

### 5.1 `value` est une chaîne, jamais un nombre

```
decimales renvoyees : '4.6800000000' -> float = 4.68
```

FRED renvoie **du texte à 10 décimales**. Sans `float()`, la première moyenne calculée
échouerait.

### 5.2 Une valeur manquante s'écrit `"."`

Mesuré sur **400 observations réelles** de `DGS10` :

```
observations recues : 400
valeurs manquantes  : 17   (chaine ".", pas null)
    2026-07-03  '.'
    2026-06-19  '.'
    2026-05-25  '.'
    2026-02-16  '.'
    2026-01-19  '.'
```

**Ces dates ne sont pas aléatoires** : 4 juillet (Independence Day, observé le 3), 19 juin
(Juneteenth), 25 mai (Memorial Day), 16 février (Presidents' Day), 19 janvier (Martin Luther
King Day). Ce sont les **jours fériés fédéraux américains** — le marché obligataire est fermé.

**4,3 % des observations.** Sans le filtre `if obs["value"] != "."`, la collecte s'interrompt
sur `ValueError: could not convert string to float: '.'` environ **une fois sur vingt-cinq**.

## 6. 🔒 La première source de RITA qui manipule un secret

BCE, RSS, Boursorama, CSV : aucune clé. **FRED en exige une.** C'est donc le premier module où
la question « où vit le secret » se pose concrètement.

```python
params={
    "series_id": series_id,
    # La clé passe en PARAMÈTRE, jamais concaténée dans l'URL.
    "api_key": _cle(),
    ...
}
```

**Pourquoi ce n'est pas un détail** : les serveurs web journalisent les **URL complètes**, pas
les paramètres de requête. Une clé collée dans l'URL se retrouve en clair dans les journaux de
FRED, dans ceux de tout intermédiaire, et dans l'historique du navigateur si elle transite par
là. En paramètre, elle reste dans le corps de la requête.

**C'est verrouillé par un test** — et c'est celui dont je suis le plus satisfait :

```python
def test_la_cle_ne_se_retrouve_jamais_dans_l_url(monkeypatch):
    ...
    assert "cle-de-test" not in appel.call_args.args[0]
    assert appel.call_args.kwargs["params"]["api_key"] == "cle-de-test"
```

Il ne vérifie pas ce que la fonction **renvoie**, mais ce qu'elle **ne fait pas**. Si quelqu'un
« simplifie » un jour en concaténant la clé dans l'URL, le test casse. **Un garde-fou de
conception, pas un garde-fou de vigilance** — même principe que l'authentification posée sur le
routeur entier de l'API (C5).

## 7. Une erreur qui porte son remède

```python
raise CleFredAbsente(
    "FRED_API_KEY absente. Ajouter FRED_API_KEY=<cle> dans .env "
    "(cle gratuite sur https://fredaccount.stlouisfed.org/apikeys)."
)
```

`os.environ["FRED_API_KEY"]` aurait levé un `KeyError: 'FRED_API_KEY'` — exact, mais muet.
Ici l'erreur dit **quoi faire**. Même principe que `StructurePageModifiee` dans le scraper :
une panne doit se **nommer**, pas se deviner.

Deux tests le garantissent, dont un vérifie que l'erreur tombe **avant** la requête réseau —
pas après un aller-retour inutile.

## 8. Tests — 9, aucun appel réseau

```
C:\Python314\python.exe -m pytest tests/test_fred.py -v
→ 9 passed in 0.19s
```

| Test | Ce qu'il protège |
|---|---|
| `test_retourne_date_et_valeur` | le contrat de sortie |
| `test_la_valeur_est_un_nombre_pas_une_chaine` | la conversion depuis le texte FRED |
| `test_ignore_les_observations_manquantes` | le filtre `"."` — sur une vraie date fériée |
| **`test_la_cle_ne_se_retrouve_jamais_dans_l_url`** | **le secret ne fuit pas** |
| `test_la_plus_recente_est_demandee_en_premier` | `sort_order=desc` — sinon on lit 1962 |
| `test_sans_cle_erreur_explicite` | le message porte le remède |
| `test_aucun_appel_reseau_sans_cle` | pas de tour de réseau inutile |
| `test_une_cle_vide_est_traitee_comme_absente` | une ligne `FRED_API_KEY=` vide dans `.env` |
| `test_les_series_retenues_sont_documentees` | un code seul ne dit rien |

`httpx.get` est remplacé par un double : les tests tournent **sans clé, sans internet, et sans
consommer le quota**. Un test qui dépend du réseau échoue un jour pour une raison qui n'a rien
à voir avec le code.

**Suite complète du projet : 176 tests verts** (167 avant cette source) — soit **+9 apportés
par FRED**.

> ℹ️ Chiffre **daté du 02/08/2026**, laissé tel quel volontairement : c'est la mesure qui
> établit l'apport de cette source. Le projet en compte **186** depuis le 03/08 (commit
> `d87e850`, rafraîchissement quotidien des cotations). Les deux chiffres sont justes, ils
> ne datent simplement pas du même jour.

## 9. Ce qui reste à faire

Ce module **récupère** les données ; il ne les **stocke** pas encore.

| Étape suivante | Ce qu'elle demande |
|---|---|
| Table `indicateur_macro` | une table dans `db/schema.sql`, sur le modèle de `taux_change` |
| 7ᵉ étape dans `pipelines/ingest.py` | `etape_indicateurs_macro`, à côté des taux BCE |
| Point de terminaison `/donnees/macro` | extension de l'API (C5) |
| §3 du rapport E1 | mentionner la source, et re-vérifier les 5 pages |

Décision assumée : ces étapes viennent **après** la remise du Bloc 1. Le module existe, il est
testé, il fonctionne sur données réelles — l'intégration en base touche un livrable déjà finalisé.

## 🎤 Phrase pour l'oral

> « FRED est ma seule source qui exige une clé. Ça m'a obligé à me poser une question que les
> autres ne posaient pas : où vit le secret ? La clé est dans un `.env` exclu de Git, et elle
> passe en paramètre de requête, jamais dans l'URL — parce que les serveurs journalisent les URL
> complètes. J'ai verrouillé ça par un test qui vérifie que la clé n'apparaît pas dans l'URL
> appelée. Et je suis franc sur un point : FRED ne me fait gagner aucun critère, c'est un
> service web comme la BCE. Je l'ai codée parce qu'elle apporte le contexte macro qui manquait
> au briefing, pas pour remplir une case. »

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **FRED** | *Federal Reserve Economic Data*, base de la Fed de Saint-Louis |
| **Série macroéconomique** | Une mesure suivie dans le temps (l'inflation mois par mois) |
| **Observation** | Un couple (date, valeur) dans une série |
| **`DGS10`** | *Daily Treasury Yield, 10-Year* — ce que rapporte un prêt à l'État américain sur 10 ans |
| **Point de base** | Un centième de pourcent ; 12 points de base = 0,12 % |
| **Taux directeur** | Le taux auquel la banque centrale prête aux banques |
| **Paramètre de requête** | Ce qui suit le `?` dans une URL ; `httpx` l'encode et ne le journalise pas |
| **Double de test** (*mock*) | Faux objet imitant le vrai, pour tester sans réseau |
| **`monkeypatch`** | Outil pytest qui modifie l'environnement le temps d'un test |
| **Quota d'API** | Nombre d'appels autorisés par période |
