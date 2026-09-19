# Preuve C17 — indexation RAG des actualités (étape 2)

**Date : 28/08/2026** · Compétences : **C17** (composants métier), **C15** (cadre technique).
Consigne formateur du 28/08 : le **RAG est obligatoire**. Plan : `docs/PLAN-RAG-MCP.md`.

---

## 1. Ce qui a été construit

| Fichier | Rôle |
|---|---|
| `rag/indexation.py` | construit l'index à partir de la table `article` |
| `tests/test_rag_indexation.py` | **15 tests** |
| `.gitignore` | `data/chroma/` exclu — l'index se reconstruit depuis la base |

**Pile retenue** : ChromaDB (persistant, local) + embeddings `all-MiniLM-L6-v2`
**384 dimensions**, exécutés par **ONNX**.

**Pourquoi ONNX et pas PyTorch** : l'image Docker fait déjà 595 Mo et `pyspark` (492 Mo)
en a été volontairement exclu. PyTorch aurait ajouté plusieurs centaines de mégaoctets
pour le même résultat. ONNX charge un modèle de **79 Mo**, une seule fois, en cache.
Le modèle tourne **hors ligne, sans clé, sans coût par appel** — et c'est **le même que
celui du brief Sorabel**, ce qui rend les deux travaux comparables.

## 2. Trois décisions, chacune fondée sur une mesure

### Un article = un morceau, sans découpage

Mesuré sur le corpus le 28/08 :

```
163 articles · titre 92 caracteres en moyenne
              resume 283 en moyenne, 915 au maximum
              0 article sans resume
```

Un article tient en ~1 000 caractères. Le découper produirait des fragments
incompréhensibles seuls. Règle du brief Sorabel appliquée telle quelle : *« garder une
fiche courte entière ; ne découper qu'un document long »*.

⚠️ **Limite assumée** : le modèle tronque au-delà de ~256 unités lexicales. Les rares
résumés les plus longs perdent leur fin. Acceptable pour de la dépêche, écrite en
**pyramide inversée** — l'essentiel est dans les premières phrases. Inacceptable pour
un mode d'emploi ; c'est pourquoi la règle est écrite avec sa condition de validité.

### Le titre est indexé avec le résumé

Un titre de presse est une reformulation dense du contenu : le meilleur signal
disponible par caractère.

### Un article bloqué n'entre JAMAIS dans l'index

`bloque_injection = TRUE` marque une tentative d'injection de prompt. `api/donnees.py`
l'exclut déjà de l'API — **l'index doit l'exclure aussi**. Sinon le contenu hostile
revient par la porte de derrière, directement dans le contexte du modèle.

*C'est la règle Sorabel : « appliquer le filtre AVANT la recherche ; le contenu interdit
ne doit jamais atteindre le LLM ni le reranker ». Un contenu écarté d'un côté mais indexé
de l'autre est pire que rien : on se croit protégé.*

Au 28/08 : **0 article bloqué sur 163**. Le filtre ne sert à rien aujourd'hui — il servira
le jour où il servira, et ce jour-là il sera déjà en place.

## 3. Exécution réelle — 28/08/2026

```
163 lus | 163 indexes | 0 bloques ecartes | 22 citant une valeur suivie
```

### 🔴 Le chiffre qui compte : 22 sur 163

**Seuls 13 % des articles citent une des 111 valeurs suivies.** Ce n'est pas un défaut
d'indexation : les trois flux sont des flux d'**économie générale** — BFM éco (60),
Le Monde éco (53), La Tribune (50) — et non des flux d'actualité d'entreprise.

**Conséquence, mesurée et non supposée** :

```
requete « resultats d'une entreprise du luxe »
   0.489  « Quand la peniche prend l'eau... »          AUCUN RAPPORT
   0.519  « Dette grecque : Athenes veut solder... »   AUCUN RAPPORT
```

Il n'existe aucun article sur le luxe dans le corpus. La recherche dense rend alors le
**moins mauvais** résultat, pas un bon — et sans seuil de refus, cet article partirait
enrichir un briefing sur LVMH.

👉 **Cela démontre que le refus `OUT_OF_CORPUS` de l'étape 3 n'est pas un raffinement,
c'est une sécurité.** À comparer avec une requête couverte par le corpus :

```
requete « inflation et taux de la BCE »
   0.435  « Aux Etats-Unis, l'inflation stagne a 3,7 %... »   PERTINENT
```

⚠️ **L'écart est faible** : 0,435 pour un résultat pertinent contre 0,489 pour un
résultat sans rapport. **Le seuil devra être calibré sur des cas annotés, pas choisi à
vue** — et c'est exactement la question ouverte de la veille S35
(*Confidently Wrong*, arXiv 2606.22659 : un seuil calibré puis transporté voit son taux
d'échec passer de 0,01 à 0,97).

### Deux pistes pour le corpus, à trancher avec le formateur

1. **Assumer un corpus macro** : le RAG apporte le contexte économique du briefing
   (inflation, taux, conjoncture) plutôt que l'actualité d'une valeur précise.
2. **Ajouter des flux par entreprise** : `sources/rss.py` sait déjà lire un flux ;
   ajouter un flux Google News par ticker rendrait le corpus spécifique. Coût faible,
   volume multiplié.

## 4. Tests — 15 cas

Les deux tests centraux :

| Test | Ce qu'il protège |
|---|---|
| `test_un_article_bloque_n_entre_JAMAIS_dans_l_index` | le filtre de sécurité |
| `test_un_nom_a_l_interieur_d_un_mot_n_est_PAS_detecte` | « ACCOR » ne doit pas être trouvé dans « raccorder » — sinon l'article partirait enrichir le briefing d'Accor |

🐛 **Défaut trouvé et corrigé pendant l'écriture des tests** : le simulacre de base
reconnaissait la requête par la chaîne `"FROM article"`, alors que le SQL réel écrit
`FROM   article` avec plusieurs espaces d'alignement. **Le test passait donc au vert sur
un corpus vide — il ne testait rien.**

*C'est exactement le « 100 % circulaire » de la note de veille S34* : un test qui mesure
son propre simulacre plutôt que le code. Corrigé en reconnaissant les **colonnes**
(`bloque_injection`, `nom_officiel`) plutôt que la mise en forme du SQL.

**Suite complète** : `370 passed, 2 xfailed` · couverture **92,28 %** (seuil CI 90 %).

## 5. Correction de cause racine, faite au passage

En interrogeant la base pour mesurer le corpus, la connexion a échoué sur le port
**5432** au lieu de **5433** — **quatrième occurrence** du même défaut après
`db/importer.py` (17/08), `indicateurs/socle.py` et `monitorage/fraicheur.py` (25/08).

**La cause était architecturale** : `sources/database.py`, le module qui **ouvre** la
connexion, ne chargeait pas le `.env`. **Six modules le chargeaient à sa place** — et
chaque nouvel appelant devait y penser.

> *Le module qui a besoin d'une configuration doit la charger lui-même, pas compter sur
> ses appelants.*

`load_dotenv` déplacé dans `sources/database.py`. Les six appels existants restent
inoffensifs (`load_dotenv` est idempotent et ne remplace pas une variable déjà posée,
donc l'environnement du conteneur Docker garde la priorité).

**Corriger le quatrième symptôme aurait garanti un cinquième.**

## 6. Ce qui reste

⬜ **E3** — recherche hybride dense + BM25, fusion RRF, et le **seuil de refus**
(`rank_bm25` est déjà installé) · ⬜ **E4** — branchement au briefing ·
⬜ **E5** — évaluation par ablation · ⬜ le 5ᵉ outil MCP `search_articles`.

---

# Étape 3 — recherche hybride, ajoutée le 28/08/2026

`rag/recherche.py` · **13 tests** · suite complète **383 passed, 2 xfailed** ·
couverture **92,17 %**.

## 1. La mesure qui a décidé de l'hybride

L'index contenait **2 articles citant « TotalEnergies »**. Interrogé sur ce mot exact,
le moteur **dense seul** a rendu :

```
0.648  TotalEnergies reduit son exposition au gaz russe   <- bon, score mediocre
0.767  Sanofi penalise en Bourse...                       <- FAUX, classe 2e
0.777  ...le PDG de TotalEnergies                         <- bon, classe 3e DERRIERE Sanofi
```

**Un moteur qui place Sanofi devant TotalEnergies quand on cherche « TotalEnergies »
n'est pas utilisable pour un briefing financier.** `all-MiniLM-L6-v2` est entraîné
majoritairement sur de l'anglais ; le français financier n'est pas son terrain.

BM25 règle ce cas trivialement : « TotalEnergies » est un mot rare, donc lourdement
pondéré. **Après fusion**, les deux articles remontent — le second était `dense#2`
mais `lex#0`.

## 2. Pourquoi RRF et pas une moyenne de scores

| Requête | Résultat | Distance |
|---|---|---|
| « résultats d'une entreprise du luxe » | **hors sujet** (une péniche) | **0,489** |
| « TotalEnergies » | **pertinent** | **0,648** |

**Un hors-sujet obtient une meilleure distance qu'un bon résultat sur une autre
requête.** Les distances ne sont donc pas comparables d'une requête à l'autre, et toute
moyenne pondérée mélangerait deux échelles sans commune mesure. **RRF fusionne les
rangs**, pas les scores : le problème disparaît par construction.

⚠️ **Conséquence directe pour la veille S35** : cette mesure confirme sur nos propres
données ce que dit *Confidently Wrong* (arXiv 2606.22659) — un seuil de distance
calibré sur un jeu figé ne se transporte pas.

## 3. Le refus — deux versions, et pourquoi la première était fausse

| Version | Règle | Résultat mesuré |
|---|---|---|
| 1 | score BM25 > 0 | ❌ « **recette** de la tarte aux pommes » acceptée (score 4,94) — *« recette »* veut aussi dire *recettes fiscales* |
| 2 | **la moitié des mots significatifs** de la question doit figurer dans le document | ✅ refusée |

**Un seul mot commun ne fait pas une réponse.** La couverture est une proportion, donc
**comparable d'une question à l'autre** — contrairement aux distances.

⚠️ **Faux négatif mesuré et assumé** : « résultats d'une entreprise du luxe » (3 mots
significatifs, 2 exigés) est **refusée** alors qu'un article LVMH pertinent existe.
Reformulée en « actualité du luxe LVMH », elle passe. **C'est l'arbitrage
précision/rappel, et il ne se tranche pas à vue** — c'est l'objet de l'étape 5
(ablation sur cas annotés).

## 4. Corpus enrichi — flux par entreprise

Le corpus ne parlait pas des valeurs suivies (22 articles sur 163). Ajout d'un **flux
Google News par entreprise détenue**, construit depuis la table `position` :

```
163 -> 263 articles      22 -> 109 citant une valeur suivie  (13 % -> 41 %)
```

**Pourquoi Google News** : Boursorama, Les Échos et Zonebourse renvoient un **403** en
accès direct (documenté dans `sources/rss.py` depuis le 31/07). Google News les agrège —
on obtient leur contenu **par une porte ouverte**, sans rien contourner. Vérifié : les
articles rendus viennent de Boursier.com, Boursorama et Zonebourse.

**Un flux par valeur détenue, pas par valeur suivie** : 111 flux, ce seraient 111
requêtes chaque soir pour des titres sur lesquels RITA ne rédige jamais.

⚠️ Un flux échoue : `ent_cgg_bs`. La raison sociale en base vaut **« CGG BS »**, une
dénomination tronquée qui ne correspond à aucune recherche. La dégradation est propre —
ce flux est ignoré, les 9 autres continuent.

## 5. Deux défauts trouvés par les tests, et corrigés

**a) La détection de valeurs ratait LVMH.** Elle comparait au nom **légal**
« LVMH MOET VUITTON », que la presse n'écrit jamais. Le filtre `MC.PA` ne trouvait
**aucun** article sur un corpus qui en contenait dix.

Correctif : ajouter le **premier mot** du nom légal quand il est distinctif.
⚠️ Un critère de longueur ne suffit pas — à 6 caractères minimum, « LVMH » (4) était
rejeté ; à 4, « CREDIT » de « CREDIT AGRICOLE » aurait étiqueté ACA.PA tout article
parlant de crédit. **C'est le sens du mot qui compte, pas sa taille** : d'où une liste
de mots trop génériques (CREDIT, BANQUE, SOCIETE, GROUPE, FRANCE…).

**b) Plantage quand le filtre par ticker est actif.** La recherche dense interroge
**toute** la collection — ChromaDB ne sait pas la restreindre à une sous-liste
d'identifiants. Elle rendait donc des documents écartés par le filtre, et la suite
plantait sur `list.index(x): x not in list`. Correctif : intersection explicite, et
un test dédié.

## 6. Ce qui reste

⬜ **E4** — brancher la recherche au briefing · ⬜ **E5** — ablation D0 → H1 sur cas
annotés, qui tranchera le seuil · ⬜ 4ᵉ outil MCP `search_articles` ·
⬜ le **reranker**, non implémenté : à décider après l'ablation, quand on saura ce
qu'il apporterait.
