# Schémas du rapport E3

Deux schémas, générés depuis une seule description par `generer_schemas.py` : le `.drawio` (éditable
dans draw.io) et le `.svg` sortent du même script, le `.png` est rendu depuis le `.svg` par Chrome
sans fenêtre. Règle du dépôt : un `.drawio` pour corriger, une image pour voir.

| Fichier | Contenu | Section du rapport |
|---|---|---|
| `E3-architecture` | le chemin d'un briefing : clients, API, graphe, garde-fous, réserves, observabilité | 2 |
| `E3-chaine-livraison` | les cinq workflows, le poste, le serveur, ce qui est conçu et non construit | 7 |

## Régénérer

```
cd D:\KandaWork\RITA_PROJECT\rita-agent
```
```
C:\Python314\python.exe -X utf8 docs\rapports\E3\schemas\generer_schemas.py
```

Puis le rendu PNG (Chrome exige un `--user-data-dir`, sinon il échoue sans message) :

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --hide-scrollbars --user-data-dir=%TEMP%\chrome-rendu --window-size=1500,900 --screenshot=docs\rapports\E3\schemas\E3-architecture.png file:///D:/KandaWork/RITA_PROJECT/rita-agent/docs/rapports/E3/schemas/E3-architecture.svg
```

Même commande pour `E3-chaine-livraison` avec `--window-size=1400,760`. Les deux PNG ont été regardés
avant d'être rangés (03/10/2026) : aucune flèche ne traverse une boîte, aucun texte n'est coupé.
