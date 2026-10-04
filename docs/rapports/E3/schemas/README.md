# Schémas du rapport E3

Cinq schémas, générés depuis une seule description par `generer_schemas.py` : le `.drawio` (éditable
dans draw.io) et le `.svg` sortent du même script, le `.png` est rendu depuis le `.svg` par Chrome
sans fenêtre. Règle du dépôt : un `.drawio` pour corriger, une image pour voir.

| Fichier | Contenu | Section du rapport | Taille de rendu |
|---|---|---|---|
| `E3-architecture` | le chemin d'un briefing : clients, API, graphe, garde-fous, réserves, observabilité | 2 (C9) | 1500,900 |
| `E3-integration-briefing` | une demande de briefing depuis l'écran 3, et ce que l'écran fait des réponses qui ne sont pas un briefing | 4 (C10) | 1400,560 |
| `E3-monitorage` | collecte des traces, Langfuse, restitution, les deux alertes vers GitHub | 5 (C11) | 1400,560 |
| `E3-strategie-tests` | ce qui est testé, par quoi, et où ça tourne (poste, CI, manuel) | 6 (C12) | 1400,560 |
| `E3-chaine-livraison` | les cinq workflows, le poste, le serveur, ce qui est conçu et non construit | 7 (C13) | 1400,760 |

## Régénérer

```
cd D:\KandaWork\RITA_PROJECT\rita-agent
```
```
C:\Python314\python.exe -X utf8 docs\rapports\E3\schemas\generer_schemas.py
```

Puis le rendu PNG, un schéma à la fois (Chrome exige un `--user-data-dir`, sinon il échoue sans message) :

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --hide-scrollbars --user-data-dir=%TEMP%\chrome-rendu --window-size=1500,900 --screenshot=docs\rapports\E3\schemas\E3-architecture.png file:///D:/KandaWork/RITA_PROJECT/rita-agent/docs/rapports/E3/schemas/E3-architecture.svg
```

Même commande pour les quatre autres, avec la taille de rendu du tableau. Chaque PNG est regardé avant
d'être rangé : aucune flèche ne traverse une boîte, aucun texte n'est coupé (architecture et chaîne le
03/10, les trois autres et la mise à jour des alertes le 04/10/2026).
