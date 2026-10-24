# Preuve C4 — MCD Merise : lecture et justification

> **Compétence visée — C4** : *« Les modélisation**s** des données respectent la méthode et le
> formalisme Merise. »* Le pluriel vise le **conceptuel** (ce document) **et** le **physique**
> (`db/schema.sql`).

📎 **Fichiers de cette preuve** :

| Fichier | Rôle |
|---|---|
| [`MCD-MERISE-RITA.png`](MCD-MERISE-RITA.png) | Le modèle conceptuel — à regarder |
| [`MCD-MERISE-RITA.drawio`](MCD-MERISE-RITA.drawio) | La source, éditable (app.diagrams.net) |
| `../../db/schema.sql` | Le modèle **physique** qui en découle |
| `../../db/README.md` | Procédure d'installation et de vérification |

> **MCD** = *Modèle Conceptuel de Données* — le schéma qui décrit **le métier**, sans aucune
> technologie. Pas de type de colonne, pas de clé étrangère, pas de SQL.

---

## 1. Comment lire le schéma

Trois symboles, pas un de plus :

| Symbole | Nom | Ce que c'est |
|---|---|---|
| **Rectangle** | **Entité** | Une « chose » du métier. L'**identifiant** est souligné. |
| **Ellipse** | **Association** | Le lien entre deux entités. **Toujours un verbe.** |
| `1,1` `1,n` `0,n` | **Cardinalité** | Combien de fois une entité participe au lien : **min,max** |

**La cardinalité se lit du côté de l'entité, en partant d'elle** :

> `VALEUR ──1,n──( est cotée lors )──1,1── COTATION`
>
> - côté VALEUR : *« **une** valeur est cotée lors d'**au moins une** et **plusieurs** séances »* → `1,n`
> - côté COTATION : *« **une** cotation concerne **exactement une** valeur »* → `1,1`

---

## 2. Les 6 entités, et pourquoi chacune existe

| Entité | Ce qu'elle représente | Pourquoi elle est là |
|---|---|---|
| **VALEUR** | Une société cotée en bourse | Le pivot du modèle |
| **ALIAS** | Un libellé de portefeuille désignant une valeur | ⭐ **résout le cas CGG** — voir §3 |
| **COTATION** | Une séance de bourse pour une valeur | Les prix, cœur du produit |
| **POSITION** | Une ligne détenue par l'utilisateur | ⚠️ **données personnelles (RGPD)** |
| **DEVISE** | Une monnaie (EUR, USD…) | Le portefeuille est multi-devises |
| **TAUX_CHANGE** | Le cours d'une devise un jour donné | Sans lui, le total du portefeuille est faux |

---

## 3. ⭐ Chaque cardinalité, justifiée par un fait mesuré

Aucune de ces cardinalités n'est une intuition : chacune vient d'un constat de l'analyse
exploratoire du 31/07 (`bigdata/explorer.py`, preuve `../C1/preuve-09-analyse-exploratoire.md`).

### `VALEUR 1,n ── est nommée ── 1,1 ALIAS`

> Une valeur peut porter **plusieurs libellés** dans le portefeuille ; un libellé désigne
> **une seule** valeur.

**Le fait mesuré** : l'univers contient **112 libellés pour 111 tickers**. « CGG BS » (bons
de souscription) et « CGG RGPT » (regroupement d'actions) pointent tous deux vers
`VIRI.PA` — Viridien, ex-CGG.

**Si on avait écrit `1,1` de ce côté** — une valeur, un seul nom — on reproduisait le bug :
2 560 lignes en double et un `INSERT` qui échoue sur la clé primaire.

> 💡 Une cardinalité mal posée n'est pas une erreur de dessin : c'est **un bug de données**.

### `VALEUR 1,n ── est cotée lors ── 1,1 COTATION`

> Une valeur a **au moins une** cotation ; une cotation appartient à **une seule** valeur.

**Le fait mesuré** : 273 608 cotations distinctes pour 111 valeurs, soit de **286 à 2 560
séances** selon la valeur. Le `1` du minimum dit qu'**une valeur sans aucune cotation
n'existe pas** dans notre modèle — c'est une valeur qu'on n'a pas su télécharger, donc
qu'on écarte en amont.

### `VALEUR 0,n ── est détenue ── 1,1 POSITION`

> ⚠️ **Le `0` est volontaire et important.**

Une valeur peut n'être détenue par **personne** — l'univers de suivi (111 valeurs) est plus
large que le portefeuille. RITA surveille des valeurs qui ne sont pas détenues.

**Si on avait écrit `1,n`**, on aurait interdit de suivre une valeur sans l'acheter — ce qui
casse la fonction de veille du produit.

### `VALEUR 1,1 ── est cotée en ── 0,n DEVISE`

> Une valeur est cotée dans **exactement une** devise ; une devise peut concerner **zéro ou
> plusieurs** valeurs.

Le `0` côté DEVISE permet d'enregistrer une devise **avant** d'avoir une valeur qui l'utilise
(par exemple pour stocker un taux de change à l'avance).

### `POSITION 1,1 ── est libellée en ── 0,n DEVISE`

> Une position est libellée dans **une seule** devise.

**Le fait mesuré** : `sources/positions.py` a détecté **2 devises** (EUR, USD) et signalé que
le total brut de 26 700,95 **n'a aucun sens** tant qu'on ne convertit pas.

### `DEVISE 1,n ── a pour cours ── 1,1 TAUX_CHANGE`

> Une devise a **plusieurs** cours dans le temps (un par jour) ; un cours concerne **une
> seule** devise à **une seule** date.

C'est ce qui rend la valorisation **historique** possible : valoriser une position au taux
du jour de l'achat, pas au taux d'aujourd'hui.

---

## 4. Ce qui n'est **pas** dans le MCD — et pourquoi

Le modèle physique (`db/schema.sql`) compte **8 tables**, le MCD **6 entités**. L'écart est
volontaire et se défend :

| Table du MPD | Absente du MCD ? | Raison |
|---|---|---|
| `article` (flux RSS) | ⚠️ oui | Collecte **brute**, pas encore rattachée aux valeurs. Elle entrera au MCD quand l'association `ARTICLE ── mentionne ── VALEUR` sera implémentée (Q3). |
| `memory_audit` | ✅ oui, exclue | **Journal technique**, pas une entité métier. Un MCD décrit le métier ; les logs n'en font pas partie. |

**6 entités + 2 tables techniques = 8 tables.** Le compte tombe juste.

> ⚠️ **Corrigé le 10/08/2026.** Ce paragraphe annonçait **7 tables** — il était en contradiction
> avec son propre tableau (6 + 2 = 8). Vérifié en rejouant `db/schema.sql` sur une instance
> neuve : `SELECT count(*) FROM information_schema.tables WHERE table_type='BASE TABLE'` → **8**.
> `db/README.md` portait la même erreur, corrigée par le commit `45f3aaf`.

---

## 5. Comment on passe du MCD au MPD

Merise a des **règles mécaniques** de traduction. C'est ce qui explique que
`db/schema.sql` ressemble au schéma ci-dessus :

| Règle Merise | Application dans RITA |
|---|---|
| Une **entité** devient une **table** | `VALEUR` → table `valeur` |
| Son **identifiant** devient la **clé primaire** | `ticker` → `PRIMARY KEY` |
| Association **1,n ↔ 1,1** → la clé migre du côté `1,1` | `cotation.ticker` devient **clé étrangère** |
| Association **0,n ↔ 1,1** → idem, mais la colonne peut être vide | `position.ticker` |
| Association **n,n des deux côtés** → **table intermédiaire** | *aucune dans RITA* — c'est un signe de modèle simple |

> **Erratum du 24/10/2026** (la ligne d'origine est gardée telle quelle : une preuve datée ne se réécrit pas). La règle
> « 0,n ↔ 1,1 → idem, mais la colonne peut être vide » est fausse. Le `1,1` du côté de POSITION impose que chaque
> position appartienne à une valeur : la clé étrangère `position.ticker` est **obligatoire**, et `db/schema.sql` la
> déclare bien `NOT NULL`. Le `0` de `0,n` dit seulement qu'une valeur peut n'avoir aucune position. Une clé étrangère
> ne peut être vide que pour une cardinalité `0,1`.

> Le fait qu'**aucune association ne soit `n,n` des deux côtés** est un bon signal : le
> modèle est simple, sans table de liaison à justifier.

---

## 6. 📖 Glossaire

| Terme | En clair | Pourquoi ça compte ici |
|---|---|---|
| **Merise** | Méthode française de conception de bases de données (1979) | Imposée par le critère C4 |
| **MCD** | *Modèle Conceptuel de Données* — le métier, sans technique | Ce document |
| **MLD** | *Modèle Logique* — l'étape intermédiaire, on choisit le relationnel | Souvent sautée, tolérée |
| **MPD** | *Modèle Physique* — le SQL réel, avec les types | `db/schema.sql` |
| **Entité** | Une « chose » du métier | Un rectangle |
| **Association** | Le lien entre deux entités, toujours un verbe | Une ellipse |
| **Cardinalité** | `min,max` — combien de fois l'entité participe au lien | Le cœur du MCD |
| **Identifiant** | L'attribut qui distingue une occurrence des autres | Souligné dans le rectangle |
| **Occurrence** | Un exemplaire concret d'une entité | `MC.PA` est une occurrence de VALEUR |
| **Clé primaire** (*primary key*) | La colonne qui identifie une ligne, en base | Traduction de l'identifiant |
| **Clé étrangère** (*foreign key*) | Colonne qui pointe vers la clé primaire d'une autre table | Naît des cardinalités |
| **Table de liaison** | Table créée pour une association `n,n` | Aucune dans RITA |
| **PRU** | *Prix de Revient Unitaire* — le prix moyen d'achat d'un titre | Attribut de `POSITION` |
| **ISIN** | Code international à 12 caractères d'un titre (`FR0000121014`) | Identifiant officiel, stable |
| **Ticker** | Code court d'une valeur (`MC.PA` = LVMH) | Identifiant technique, propre à la source |
| **Bons de souscription** (*warrants*) | Droit d'acheter une action plus tard à un prix fixé | Une des deux lignes CGG |
| **Regroupement d'actions** (*reverse split*) | 10 anciennes actions → 1 nouvelle, prix ×10 | L'autre ligne CGG |
| **Séance** | Une journée de bourse pour une valeur | Une occurrence de `COTATION` |
| **OHLCV** | *Open, High, Low, Close, Volume* | Les 5 mesures d'une séance |
| **RGPD** | Règlement européen sur les données personnelles | `POSITION` est concernée |
