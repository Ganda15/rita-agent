# Schémas du rapport E1

Quatre schémas, générés depuis le code par `generer_schemas.py` : le `.drawio` (éditable dans draw.io) et
le `.svg` sortent du même script. Le `.png` remis au jury est rendu par Chrome sans fenêtre depuis la mise en forme
illustrée (`<nom>-illustre.html`). Les couleurs viennent du module des schémas E3 (`../../E3/schemas/generer_schemas.py`).

| Fichier | Contenu | Critère | Section du rapport | Taille du PNG |
|---|---|---|---|---|
| `E1-collecte` | les sources par type exigé, la collecte du soir, le garde-fou d'injection, l'import, la base et le RGPD | C1 | 3 | 1920,1358 |
| `E1-nettoyage` | chaque défaut mesuré à l'analyse exploratoire, la décision prise et le fichier qui l'applique | C3 | 4 | 1920,1318 |
| `E1-requetes` | les deux systèmes (PostgreSQL, Parquet), les requêtes de chacun dans son langage, le coût mesuré (EXPLAIN ANALYZE, partitions lues) | C2 | 6 | 1920,1101 |
| `E1-api` | les clients du jeu de données, la clé posée sur tout le routeur, les 12 points de terminaison, le contrat OpenAPI et les tests | C5 | 7 | 1920,1114 |

C4 a son schéma dans le rapport (le MCD, `../images/mcd-recadre.png`). Le MCD du 01/08 rangé dans
`../../../../evidence/C4/` est une preuve datée, et les deux schémas de `../../../../bigdata/schemas/` (août) restent
où ils sont : ils sont cités par `bigdata/`. Les chiffres de ce dossier-ci sont ceux du 27/10.

## Pourquoi un générateur

Le schéma de collecte du 11/08 (`evidence/C1/SCHEMA-C1-collecte-multisource`, gardé tel quel comme preuve
datée) annonçait encore, le 4 octobre, 8 tables et un garde-fou d'injection bloquant tout, alors que la base
compte 10 tables et que la mesure donne 70 %. Ici, les chiffres qui suivent le code sont lus dans le code
à la génération (fonction `faits()` : tables, vue et contraintes CHECK de `db/schema.sql`, motifs du
garde-fou, taux mesuré par `evals/mesurer_gardefou.py`, flux RSS, étapes de `pipelines/ingest.py`,
devises suivies, traitements et procédures du registre RGPD). Les chiffres datés (analyse de juillet 2026,
comptages du 02/10) restent écrits avec leur date.

`tests/test_schemas_e1.py` vérifie que chaque schéma existe en trois formats, que ses chiffres
sont ceux du code, et que les fichiers rangés sont exactement ce que le générateur produit aujourd'hui. Un
schéma retouché à la main, ou du code qui change sans régénération, fait tomber la suite (essayé le
04/10/2026 : « 10 tables » remplacé par « 8 tables » dans le `.svg`, 1 test rouge ; régénéré, 12 verts).

**Depuis le 27/10/2026** : C2 lit dans `bigdata/query_spark.py` les années filtrées par S2 et S3, et en déduit les
partitions et les lignes lues ; chaque durée PostgreSQL affichée doit être écrite dans `db/requetes.sql`. Le nombre
de lignes par partition est un comptage daté (27/10, métadonnées Parquet) : l'archive n'est pas dans le dépôt, et
le test qui le compare à l'archive ne tourne que là où elle est. C5 lit les routes dans `api/donnees.py` et le
contrat dans l'application (`app.openapi()`). Un dernier test estime, boîte par boîte, que le texte tient dans sa
hauteur ; la vraie mesure s'est faite dans Chrome (aucun texte ne dépasse de sa boîte, le 27/10).

## Régénérer

```
cd D:\KandaWork\RITA_PROJECT\rita-agent
```
```
C:\Python314\python.exe -X utf8 docs\rapports\E1\schemas\generer_schemas.py
```

Puis le rendu PNG, un schéma à la fois (Chrome exige un `--user-data-dir`, sinon il échoue sans message) :

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --hide-scrollbars --user-data-dir=%TEMP%\chrome-rendu --window-size=1920,1358 --screenshot=docs\rapports\E1\schemas\E1-collecte.png file:///D:/KandaWork/RITA_PROJECT/rita-agent/docs/rapports/E1/schemas/E1-collecte-illustre.html
```

Même commande pour les trois autres, chacun depuis son `-illustre.html` et à la taille du tableau ci-dessus
(`E1-nettoyage` : `--window-size=1920,1318`). Les trois PNG du 27/10 ont été regardés le soir même.
Les deux PNG du 4 octobre (collecte et nettoyage, dans leur version d'alors) ont été regardés le
04/10/2026 au soir, après la refonte de la charte : aucune flèche ne traverse une boîte ni un titre, aucun texte n'est coupé.
**Collecte, depuis le 24/10/2026 (à ma demande)** : le PNG remis au jury est rendu depuis
`E1-collecte-illustre.html`, une mise en forme illustrée que j'ai fournie (icônes, formes de base de données). Les
sources `E1-collecte.svg` et `.drawio` restent générées et modifiables (bandeaux de colonne pleins, flèches à angle
droit, étiquettes en pastille). Le test `test_le_schema_illustre_dit_exactement_ce_que_dit_le_schema_genere` vérifie que
l'illustration porte les mêmes textes que le schéma généré : il a d'abord échoué sur deux textes de la maquette
(« cours du jour » sur un bus qui porte aussi BCE, FRED et RSS ; un pied qui la disait générée), corrigés. Quand un
chiffre change, régénérer le `.svg`, reporter le texte dans le `.html`, relancer le test, puis le rendu PNG.
**Nettoyage, requêtes et API, depuis le 27/10/2026 (à ma demande)** : même mise en forme, mais produite par le
générateur (`illustre`), avec les positions du schéma généré multipliées par 1,28. Régénérer suffit donc : le `.html`
suit, et un test refuse une illustration qui ne serait plus celle du générateur. Le nettoyage est passé au tracé de la
collecte (trois colonnes à bandeau).
**Relecture croisée du 28/10/2026** (faite par un second assistant de code ; chaque remarque a été vérifiée contre le code avant correction) : le
nettoyage disait que « les requêtes ne lisent que 'OK' » (R1, le portefeuille, ne filtre pas : `db/requetes.sql`) et
dédoublonnait « sur (ticker, date_seance) » (le code : `(ticker, date)`, `db/importer.py`) ; il dit maintenant la limite
des libellés CGG (addendum C3 du 26/10). L'API se disait « en lecture seule » alors qu'un appel de la passerelle MCP,
`/donnees` compris, écrit une ligne dans `mcp_calls`, et promettait le « jeu complet » sans route pour les taux de
change. Le plan Spark montre des partitions écartées, pas « des fichiers jamais ouverts ». Cinq tests tiennent ces
corrections ; ils ont échoué avant elles.
**Charte (refaite le 04/10/2026, à ma demande)** : texte presque noir et plus grand, traits épais ; une couleur
par rôle de boîte (bande à gauche) et par sens de flèche ; une légende dessinée en bas de chaque schéma, qui ne montre
que les couleurs employées et ce qu'elles veulent dire dans ce schéma. Le 04/10, le texte de chaque boîte a été
mesuré dans Chrome (largeur réelle de chaque ligne) : aucun ne dépasse de sa boîte.

Corrigé le 03/11/2026 (livret E1 v6, avant le tag) : la collecte et le nettoyage disaient « 11 partitions par année » ;
le Parquet a 11 partitions en tout, une par année (`annee=2016` à `annee=2026`). Collecte : « 11 partitions au total, une
par année » ; nettoyage : « 11 partitions, une par année » (la forme longue passait sur deux lignes dans sa boîte, vu au
rendu). Test d'abord (`test_les_partitions_se_comptent_au_total_une_par_annee`, 2 échecs), puis générateur, texte de
l'illustration de la collecte, rendu PNG, et les deux images remplacées dans les pages 7 et 9 du PDF avec annexes.

Corrigé le 02/11/2026 (livret E1 v5) : dans `../images/mcd-recadre.png`, la cardinalité côté VALEUR de « est cotée lors » passe de `1,n` à `0,n` (ma décision, `evidence/C4/preuve-mcd-merise.md`, section 5 bis) ; seul ce chiffre a été redessiné, le reste de la figure est inchangé.
