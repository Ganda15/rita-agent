# Schémas de parcours des écrans 4 et 5 (C14.2)

Deux schémas fonctionnels, **relevés le 02/11/2026 sur la version actuelle** (commit `12cc00c`) : ce ne sont pas des
maquettes initiales, et la note en bas de chaque schéma le dit. Ils suivent les scénarios de
`evidence/C14/preuve-specifications-ecrans-4-et-5.md` et sont montrés dans son § 7. Leurs textes viennent d'une seule
description, `generer_parcours.py`, qui écrit le `.drawio` (éditable dans draw.io) et le `.svg` ; c'est là qu'on corrige
un texte. Le dessin reprend le moteur des schémas d'E3 (`docs/rapports/E3/schemas/generer_schemas.py`).
`tests/test_parcours_c14.py` vérifie qu'aucun texte ne déborde, que les fichiers publiés sont ceux que le générateur
écrit, et que la preuve C14 les montre.

| Fichier | Contenu | Taille de rendu |
|---|---|---|
| `PARCOURS-C14-ecran-question` | entrer, demander, répondre ou refuser, remonter à la source | 1400,756 |
| `PARCOURS-C14-ecran-tableau-de-bord` | entrer, lire, montrer, laisser lire (dont la suspension de l'actualisation) | 1400,756 |

## Régénérer

```
cd D:\KandaWork\RITA_PROJECT\rita-agent
```
```
C:\Python314\python.exe -X utf8 evidence\C14\parcours\generer_parcours.py
```

Le PNG se rend depuis le `.svg`, un schéma à la fois, en double résolution (Chrome exige un `--user-data-dir`) :

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 --user-data-dir=%TEMP%\chrome-rendu-c14 --window-size=1400,756 --screenshot=evidence\C14\parcours\PARCOURS-C14-ecran-question.png file:///D:/KandaWork/RITA_PROJECT/rita-agent/evidence/C14/parcours/PARCOURS-C14-ecran-question.svg
```
