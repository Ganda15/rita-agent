# Preuve C17 — indexation RAG des actualités (étape E2)

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

👉 **Cela démontre que le refus `OUT_OF_CORPUS` de l'étape E3 n'est pas un raffinement,
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
