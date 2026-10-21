# Le schéma de la composante agentique du sprint 4

`SPRINT4-composante-garde-fous` : les deux parcours de la composante (les questions, entrées par l'avenant n°1, et le
briefing), chaque garde-fou à sa place, et le code qui le fait (fichier, fonction, ligne, tests). Vert : codé au
sprint 4 ; orange : garde-fou déjà là ; [S1], [S3], [S4] : le sprint du code. Numéros de ligne du 21/10/2026.

| Fichier | Rôle |
|---|---|
| `generer_schema_composante.py` | le schéma décrit en Python, avec la charte de `docs/rapports/E3/schemas/generer_schemas.py` |
| `SPRINT4-composante-garde-fous.drawio` | la version modifiable (diagrams.net) |
| `SPRINT4-composante-garde-fous.svg` | la version vectorielle, source du `.png` |
| `SPRINT4-composante-garde-fous.png` | l'image, pour les documents et l'oral |

Régénérer, depuis la racine du dépôt :

```
C:/Python314/python.exe -X utf8 docs/sprint-4/schemas/generer_schema_composante.py
```

Rendre le `.png` depuis le `.svg` (Chrome sans fenêtre, à la taille annoncée par le script) :

```
"C:/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --hide-scrollbars --window-size=2000,1346 --screenshot=docs/sprint-4/schemas/SPRINT4-composante-garde-fous.png file:///D:/KandaWork/RITA_PROJECT/rita-agent-sprint-4/docs/sprint-4/schemas/SPRINT4-composante-garde-fous.svg
```
