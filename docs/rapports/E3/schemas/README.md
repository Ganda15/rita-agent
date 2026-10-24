# Schémas du rapport E3

Cinq schémas. Leurs textes viennent d'une seule description, `generer_schemas.py`, qui écrit le `.drawio` (éditable
dans draw.io) et le `.svg` : c'est là qu'on corrige un texte. L'image publiée dans le rapport est la **mise en forme
d'Era** (`E3-<nom>-illustre.svg`, 24/10/2026), rendue en `.png` par Chrome sans fenêtre. `tests/test_schemas_e3.py`
compare chaque texte de la mise en forme à ceux du générateur : un texte changé d'un côté seulement fait tomber le
test. Règle du dépôt : un `.drawio` pour corriger, une image pour voir.

| Fichier | Contenu | Section du rapport | Taille de rendu |
|---|---|---|---|
| `E3-architecture` | les deux chemins vers le modèle (briefing, question) : clients, API, garde-fous avant et après, réserves, surveillance | 2 (C9) | 1400,946 |
| `E3-integration-briefing` | une demande de briefing depuis l'écran, et ce que l'écran fait des réponses qui ne sont pas un briefing (403, 422, 429, 502, 500) | 4 (C10) | 1400,716 |
| `E3-monitorage` | collecte des traces et des compteurs, Langfuse, les deux tableaux de bord, les deux alertes vers GitHub, ce qui manque | 5 (C11) | 1400,826 |
| `E3-strategie-tests` | les 1 751 tests par ce qu'ils protègent, et où ils tournent (poste, CI, à la main) | 6 (C12) | 1400,716 |
| `E3-chaine-livraison` | les sept workflows, le ruleset, le serveur, le déploiement et le retour arrière | 7 (C13) | 1400,886 |

## Régénérer

```
cd D:\KandaWork\RITA_PROJECT\rita-agent
```
```
C:\Python314\python.exe -X utf8 docs\rapports\E3\schemas\generer_schemas.py
```

Le script refuse d'écrire si une ligne ne tient plus dans sa boîte (contrôle `debordements`, 24/10/2026) : il nomme
la boîte et la ligne à raccourcir.

Le PNG publié se rend depuis la mise en forme, un schéma à la fois, en double résolution (Chrome exige un
`--user-data-dir`, sinon il échoue sans message ; police Noto Sans, installée sur le poste) :

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 --user-data-dir=%TEMP%\chrome-rendu --window-size=1440,1022 --screenshot=docs\rapports\E3\schemas\E3-architecture.png file:///D:/KandaWork/RITA_PROJECT/rita-agent/docs/rapports/E3/schemas/E3-architecture-illustre.svg
```

Même commande pour les quatre autres, même taille (1440,1022 ; la colonne « Taille de rendu » du tableau
est celle du `.svg` généré). Chaque PNG est regardé avant
d'être rangé : aucune flèche ne traverse une boîte ni un titre, aucun texte n'est coupé (les cinq le 24/10/2026,
après la remise à jour).

**Charte (refaite le 04/10/2026, à la demande d'Era)** : texte presque noir et plus grand, traits épais ; une couleur
par rôle de boîte (bande à gauche) et par sens de flèche ; une légende dessinée en bas de chaque schéma, qui ne montre
que les couleurs employées et ce qu'elles veulent dire dans ce schéma.

**Remise à jour du 24/10/2026 (E3 v1.5)** : les cinq schémas disaient l'état du 4 octobre. Le texte des boîtes,
11,5 px dans un schéma réduit à 516 points de large, passait à environ 4 points une fois imprimé : il est passé à
15,5 px (environ 5,7 points), les textes ont été raccourcis, et les explications sont dans le corps du rapport.

**Mise en forme d'Era (24/10/2026)** : une première version, faite à partir d'un rendu intermédiaire, disait
« 6 h à 9 h » pour le créneau du matin et deux textes déjà corrigés ; la seconde, faite depuis
`TEXTES-EXACTS`, a les textes du générateur mot pour mot (comparaison automatique : 0 absent, 0 en plus
hors trois étiquettes de flèche vérifiées) et un texte courant de 6 à 6,9 points une fois imprimé (5 au
plus petit). Le test l'a prouvé en retrouvant l'erreur « 6 h » réintroduite exprès.
