# Le diagramme de flux de données, version du 02/11/2026 (C15.3)

Relevé sur le code du commit `dd3c065`, flux par flux (`evidence/C15/preuve-flux-donnees-2026-11-02.md`). L'ancienne
version, du 18/08, est gardée : `evidence/C15/FLUX-DONNEES-C15-application-RITA.png`. Le texte vient d'une seule
description, `generer_flux.py`, qui écrit le `.drawio` (éditable dans draw.io) et le `.svg` ; c'est là qu'on corrige un
texte. Le dessin reprend le moteur des schémas d'E3. `tests/test_flux_c15.py` vérifie qu'aucun texte ne déborde, que
les fichiers publiés sont ceux du générateur, que les flux de données personnelles sont marqués, et que l'ancienne
version est toujours là.

| Fichier | Taille de rendu |
|---|---|
| `FLUX-DONNEES-C15-application-RITA-2026-11-02` | 1750,886 |

## Régénérer

```
cd D:\KandaWork\RITA_PROJECT\rita-agent
```
```
C:\Python314\python.exe -X utf8 evidence\C15\flux\generer_flux.py
```

Le PNG se rend depuis le `.svg`, en double résolution (Chrome exige un `--user-data-dir`) :

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 --user-data-dir=%TEMP%\chrome-rendu-c15 --window-size=1750,886 --screenshot=evidence\C15\flux\FLUX-DONNEES-C15-application-RITA-2026-11-02.png file:///D:/KandaWork/RITA_PROJECT/rita-agent/evidence/C15/flux/FLUX-DONNEES-C15-application-RITA-2026-11-02.svg
```
