# Schémas du rapport E2

Trois schémas, un par compétence, montrés dans l'annexe du rapport (`docs/rapports/E2/annexe-schemas-E2.md`, A1 à A3).
Ils ont été dessinés le 01/11/2026 pour le rapport, à partir des preuves qu'il cite : ce sont des figures de synthèse,
pas des documents de conception d'époque. Leurs textes viennent d'une seule description, `generer_schemas.py`, qui
écrit le `.drawio` (éditable dans draw.io) et le `.svg` : c'est là qu'on corrige un texte. Le dessin reprend le moteur
des schémas d'E3 (`docs/rapports/E3/schemas/generer_schemas.py`), pour garder la même charte.
`tests/test_schemas_e2.py` vérifie qu'aucun texte ne déborde de sa boîte et que les fichiers publiés sont ceux que le
générateur écrit.

| Fichier | Contenu | Annexe | Taille de rendu |
|---|---|---|---|
| `E2-veille` | la veille : chercher et trier, qualifier et écrire, utiliser et partager, puis ses limites | A1 (C6) | 1400,716 |
| `E2-banc-decision` | le banc du 03/10, puis les décisions datées du 05/10 au 31/10 | A2 (C7) | 1400,692 |
| `E2-service-aujourdhui` | l'appel d'un briefing, sa surveillance, le guide, et ce qui manque | A3 (C8) | 1400,846 |

## Régénérer

```
cd D:\KandaWork\RITA_PROJECT\rita-agent
```
```
C:\Python314\python.exe -X utf8 docs\rapports\E2\schemas\generer_schemas.py
```

Le PNG se rend depuis le `.svg`, un schéma à la fois, en double résolution, avec la hauteur de la colonne « Taille de
rendu » (Chrome exige un `--user-data-dir`) :

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 --user-data-dir=%TEMP%\chrome-rendu-e2 --window-size=1400,716 --screenshot=docs\rapports\E2\schemas\E2-veille.png file:///D:/KandaWork/RITA_PROJECT/rita-agent/docs/rapports/E2/schemas/E2-veille.svg
```

Chaque PNG a été regardé avant d'être rangé, le 01/11/2026 : aucune flèche ne traverse une boîte ni un titre, aucun
texte n'est coupé.
