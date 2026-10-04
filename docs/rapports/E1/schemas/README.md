# Schémas du rapport E1

Deux schémas, générés depuis le code par `generer_schemas.py` : le `.drawio` (éditable dans draw.io) et
le `.svg` sortent du même script, le `.png` est rendu depuis le `.svg` par Chrome sans fenêtre. Le dessin
est celui des schémas E3 (`../../E3/schemas/generer_schemas.py`, même module importé).

| Fichier | Contenu | Critère | Section du rapport | Taille de rendu |
|---|---|---|---|---|
| `E1-collecte` | les sources par type exigé, la collecte du soir, le garde-fou d'injection, l'import, la base et le RGPD | C1 | 3 | 1500,964 |
| `E1-nettoyage` | chaque défaut mesuré à l'analyse exploratoire, la décision prise et le fichier qui l'applique | C3 | 4 | 1500,876 |

Les autres critères d'E1 ont déjà leur schéma : C2 dans `../../../../bigdata/schemas/` (les trois requêtes
Spark SQL, l'élagage des partitions), C4 dans le rapport (MCD) et dans `../../../../evidence/C4/`
(`MCD-MERISE-RITA.drawio`), C5 dans les schémas E3 (`E3-architecture`).

## Pourquoi un générateur

Le schéma de collecte du 11/08 (`evidence/C1/SCHEMA-C1-collecte-multisource`, gardé tel quel comme preuve
datée) annonçait encore, le 4 octobre, 8 tables et un garde-fou d'injection bloquant tout, alors que la base
compte 10 tables et que la mesure donne 70 %. Ici, les chiffres qui suivent le code sont lus dans le code
à la génération (fonction `faits()` : tables, vue et contraintes CHECK de `db/schema.sql`, motifs du
garde-fou, taux mesuré par `evals/mesurer_gardefou.py`, flux RSS, étapes de `pipelines/ingest.py`,
devises suivies, traitements et procédures du registre RGPD). Les chiffres datés (analyse de juillet 2026,
comptages du 02/10) restent écrits avec leur date.

`tests/test_schemas_e1.py` (12 tests) vérifie que chaque schéma existe en trois formats, que ses chiffres
sont ceux du code, et que les fichiers rangés sont exactement ce que le générateur produit aujourd'hui. Un
schéma retouché à la main, ou du code qui change sans régénération, fait tomber la suite (essayé le
04/10/2026 : « 10 tables » remplacé par « 8 tables » dans le `.svg`, 1 test rouge ; régénéré, 12 verts).

## Régénérer

```
cd D:\KandaWork\RITA_PROJECT\rita-agent
```
```
C:\Python314\python.exe -X utf8 docs\rapports\E1\schemas\generer_schemas.py
```

Puis le rendu PNG, un schéma à la fois (Chrome exige un `--user-data-dir`, sinon il échoue sans message) :

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --hide-scrollbars --user-data-dir=%TEMP%\chrome-rendu --window-size=1500,964 --screenshot=docs\rapports\E1\schemas\E1-collecte.png file:///D:/KandaWork/RITA_PROJECT/rita-agent/docs/rapports/E1/schemas/E1-collecte.svg
```

Même commande pour `E1-nettoyage` avec `--window-size=1500,876`. Les deux PNG ont été regardés le
04/10/2026 au soir, après la refonte de la charte : aucune flèche ne traverse une boîte ni un titre, aucun texte n'est coupé.
**Charte (refaite le 04/10/2026, à la demande d'Era)** : texte presque noir et plus grand, traits épais ; une couleur
par rôle de boîte (bande à gauche) et par sens de flèche ; une légende dessinée en bas de chaque schéma, qui ne montre
que les couleurs employées et ce qu'elles veulent dire dans ce schéma. Le 04/10, le texte de chaque boîte a été
mesuré dans Chrome (largeur réelle de chaque ligne) : aucun ne dépasse de sa boîte.

