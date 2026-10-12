# Schéma du cadrage V1 (sprint 1)

Un schéma, généré par `generer_schema_architecture_v1.py` avec la charte des schémas E3
(`../rapports/E3/schemas/generer_schemas.py`, réutilisée telle quelle) : le `.drawio` (éditable dans draw.io) et le
`.svg` sortent du même script, le `.png` est rendu depuis le `.svg` par Chrome sans fenêtre.

| Fichier | Contenu | Taille de rendu |
|---|---|---|
| `CADRAGE-architecture-v1` | l'architecture complète de la V1, dans l'ordre du brief : 1 données, 2 agent et garde-fous, 3 interface, 4 API, puis le pilotage autour ; les ajouts des six jours en pointillé rouge | 1500,1144 |

Pourquoi ce schéma en plus d'`E3-architecture` : celui-ci montre l'état du code au 04/10 (cascade de trois fournisseurs,
rien des six jours de la V1) ; le brief du sprint 1 demande l'architecture complète du système fini.

## Régénérer

```
cd D:\KandaWork\RITA_PROJECT\rita-agent
```
```
C:\Python314\python.exe -X utf8 docs\cadrage\generer_schema_architecture_v1.py
```

Puis le rendu PNG (Chrome exige un `--user-data-dir`, sinon il échoue sans message) :

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --hide-scrollbars --user-data-dir=%TEMP%\chrome-rendu --window-size=1500,1144 --screenshot=docs\cadrage\CADRAGE-architecture-v1.png file:///D:/KandaWork/RITA_PROJECT/rita-agent/docs/cadrage/CADRAGE-architecture-v1.svg
```

Le PNG du 12/10/2026 a été regardé avant d'être rangé : aucune flèche ne traverse une boîte ni un titre, aucun texte
ne dépasse de sa boîte. Le `.drawio` et le `.svg` se lisent comme du XML valide (99 et 218 éléments).
