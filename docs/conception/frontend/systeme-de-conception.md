# Le système de conception de RITA

> Écrit le 06/11/2026 pour le critère C17.2 (rapport E4, § 4.3). **Ce document est écrit après le code** : il décrit le
> système que les cinq écrans partagent depuis la refonte livrée le 04/11 (`8ecc5a7`), il ne l'a pas précédé. Ses sources
> sont `frontend/style.css`, les choix validés le 04/10 ([`refonte-2026-10.md`](refonte-2026-10.md), § 3 et § 8) et la
> décision d'Era du 04/11 (thème sombre par défaut, spécification 001, § 7). Pour Portefeuille, Indicateurs et Briefing,
> les maquettes du 04/10 ont précédé le code. Pour **Question** et **Tableau de bord**, qui n'ont pas de maquette, ce
> système est la référence de conformité, comme le formateur l'a accepté le 03/11 (un système de conception suffit).

## 1. Les principes

| Principe | Ce qu'il impose | Où il est vérifié |
|---|---|---|
| Une couleur par écran | Portefeuille vert, Indicateurs indigo, Briefing ambre, Question et Tableau de bord bleu « service » ; le reste de la page lit `--couleur-ecran` et `--teinte-ecran`, posés selon `body[data-ecran]` | `frontend/style.css`, lignes 89 à 95 |
| Deux thèmes | sombre par défaut (style B des maquettes), clair au choix (style A), basculés par `theme.js` sur `<html data-theme="clair">` | `tests/test_theme_ui.py` |
| Contraste | chaque couleur de texte a au moins 4,5:1 sur son fond, dans les deux thèmes | `tests/test_entete_commun.py` (le calcul est un test) |
| L'état se dit en mots | un verdict, une fraîcheur, une donnée suspecte s'écrivent en texte, jamais par la seule couleur | recette du 02/11 (`evidence/C17/recette-2026-11-02/`) |
| Rien de tiers | polices installées, aucune bibliothèque, aucune image téléchargée hors du logo ; graphiques en SVG construits à la main | politique de contenu `default-src 'self'` (carte #75, `tests/test_entetes_securite.py`) |
| Couleurs par jetons seulement | aucune couleur écrite en dur hors des jetons, aucune dans les scripts | `tests/test_systeme_de_conception.py` |
| Clavier et mouvement | focus visible partout (RGAA 10.7) ; animations réduites si le système le demande (WCAG 2.3.3) | `tests/test_recette_clavier.py` |

## 2. Les jetons

Valeurs lues dans `frontend/style.css` le 06/11/2026. Un jeton absent de ce tableau fait échouer
`tests/test_systeme_de_conception.py`.

| Jeton | Rôle | Thème sombre (défaut) | Thème clair |
|---|---|---|---|
| `--police-texte` | le texte courant : polices déjà installées (Segoe UI Variable, SF Pro), rien n'est téléchargé | `"Segoe UI Variable Text", "Sego…` | le même |
| `--police-titres` | les titres | `"Segoe UI Variable Display", "S…` | le même |
| `--police-chiffres` | les chiffres, à chasse fixe et alignés en colonnes (Cascadia Mono, SF Mono) | `"Cascadia Mono", "SF Mono", ui-…` | le même |
| `--fond` | le fond de la page | `#0b2a4d` | `#f0f4f9` |
| `--surface` | le fond d'une carte | `#0f2643` | `#ffffff` |
| `--fond-alt` | un fond secondaire (champ, ligne d'en-tête) | `#163256` | `#eef0f3` |
| `--bord` | les bordures | `#2b4a72` | `#d0d0d0` |
| `--texte` | le texte principal | `#f5f8fc` | `#1a1a1a` |
| `--texte-doux` | le texte secondaire (aide, précision) | `#c5d3e4` | `#4a4a4a` |
| `--texte-sur-couleur` | le texte posé sur une couleur d'écran (bouton, page courante) | `#0b1a2e` | `#ffffff` |
| `--alerte` | un message d'erreur | `#ff9a8c` | `#8a1f11` |
| `--frais-ok` | des données fraîches | `#5fd394` | `#145a32` |
| `--frais-attention` | des données à surveiller | `#f0b54d` | `#7a4f00` |
| `--perimee` | une cotation périmée | `#3a2f12` | `#fdf6e3` |
| `--perimee-survol` | la même, au survol | `#45381a` | `#f8edd0` |
| `--couleur-portefeuille` | l'écran Portefeuille (vert) | `#4ccb8a` | `#1e7b45` |
| `--teinte-portefeuille` | sa teinte de fond | `#12382a` | `#f1f8f4` |
| `--couleur-indicateurs` | l'écran Indicateurs (indigo) | `#a5a8ff` | `#3f3fa8` |
| `--teinte-indicateurs` | sa teinte de fond | `#25295a` | `#f1f1fa` |
| `--couleur-briefing` | l'écran Briefing (ambre) | `#f2a93b` | `#a35a00` |
| `--teinte-briefing` | sa teinte de fond | `#40300f` | `#fcf5ec` |
| `--couleur-service` | les écrans Question et Tableau de bord (bleu « service ») | `#6cb8ea` | `#12507a` |
| `--teinte-service` | leur teinte de fond | `#123a5c` | `#eef4f9` |
| `--fond-hausse` | une case en hausse (carte des performances) | `#133a28` | `#e4f4ea` |
| `--fond-baisse` | une case en baisse | `#47201d` | `#fbe5e2` |
| `--teinte-colonne` | une colonne sur deux d'un tableau, posée par-dessus le fond | `rgba(255, 255, 255, 0.08)` | `rgba(11, 42, 77, 0.07)` |
| `--degrade-debut` | le dégradé du fond, début | `#061527` | `#e6eef7` |
| `--degrade-milieu` | le dégradé, milieu | `#0b2a4d` | `#f0f4f9` |
| `--degrade-fin` | le dégradé, fin | `#14507f` | `#fafbfd` |
| `--degrade` | le fond de la page : du bleu nuit au bleu, avec une lueur teal en haut à droite (CSS, aucune image) | `radial-gradient(circle at 88% 0…` | le même |
| `--couleur-marque` | la couleur du logo (teal en sombre, bleu nuit en clair) | `#45d3c1` | `#12395e` |
| `--logo` | le logo officiel, une version par thème | `url("logo-rita-sombre.png")` | `url("logo-rita-clair.png")` |

## 3. Les composants partagés

| Composant | Classes ou éléments | Ce qu'il porte | Écrans |
|---|---|---|---|
| En-tête commun | `.entete`, `.entete-ligne`, `.marque`, `.logo`, `.devise`, `.entete-actions` | le logo décoratif suivi du mot « RITA », la devise, les boutons « Mode simulation » (`.bascule-simulation`) et « Thème clair » (`.bascule-theme`) | les cinq |
| Navigation | les cinq liens de l'en-tête | la page courante n'est pas un lien ; elle prend la couleur de l'écran | les cinq |
| Avertissement | `.avertissement` | « Aide à la lecture. Aucune recommandation d'achat ou de vente. » (contrainte AMF) | les cinq |
| Carte de contenu | `main` | le contenu de l'écran, sur le fond de la page | les cinq |
| Connexion | `#connexion`, `#form-cle`, `#cle` | la clé d'API, masquée à la saisie, gardée après un appel réussi seulement | les cinq |
| Bouton principal | `button` | fond à la couleur de l'écran, texte `--texte-sur-couleur` ; le survol l'assombrit d'un voile noir à 12 % (la seule couleur hors jetons) | les cinq |
| Statut | `#statut` | chargement, refus, erreur, annoncés par `aria-live` | les cinq |
| Précision | `.precision` | une phrase d'aide sous un champ ou un résultat, en `--texte-doux` | Question et les écrans de données |
| Fraîcheur des données | `.fraicheur-orange`, `.fraicheur-rouge` | l'âge des données, en mots et en couleur | Question et les écrans de données |
| Tableau | `table` | colonnes de texte à gauche, chiffres à droite en `--police-chiffres`, une colonne sur deux teintée | Portefeuille, Indicateurs |
| Cartes de signaux | `.cartes`, `.resume`, `.horodatages`, `.barre-outils`, `.chapeau` | un signal par carte, son verdict en mots contre un seuil écrit | Tableau de bord |
| Bandeau d'exercice | `.bandeau-exercice` | une panne simulée en cours, impossible à manquer | Tableau de bord |
| Mention de simulation | `#mention-simulation` | « Simulation » sur chaque écran quand le mode est choisi | les cinq |

## 4. Comment la conformité se vérifie

1. **Par le code** (`tests/test_systeme_de_conception.py`) : aucune couleur hors jetons ; aucun script n'écrit de
   couleur ; Question et Tableau de bord n'utilisent que des classes définies par la feuille commune ; chaque jeton est
   décrit ici.
2. **À l'œil** : le système à côté des écrans livrés, en annexe A7 du rapport E4.

## 5. Limites

- Écrit après le code : ce document constate un système, il ne l'a pas conçu à l'avance pour Question et Tableau de bord.
- Aucun test avec un lecteur d'écran ; le contraste est calculé, pas mesuré sur un écran réel.
- Les composants propres à un seul écran (graphiques, carte des performances) ne sont décrits que par leur feuille de style.

## 📖 Glossaire

- **Système de conception** (*design system*) : l'ensemble des règles, des couleurs, des polices et des composants qu'un
  produit réutilise partout, pour que ses écrans se ressemblent et se comprennent de la même façon.
- **Jeton** (*design token*) : une valeur nommée (une couleur, une police) que tout le reste lit par son nom, ici une
  variable CSS comme `--couleur-ecran`.
- **Thème** : un jeu de valeurs pour les mêmes jetons (sombre, clair).
- **Composant** : un élément d'interface réutilisé tel quel (en-tête, bouton, carte).
- **Contraste** : rapport de luminosité entre un texte et son fond ; 4,5:1 est le minimum du WCAG pour un texte courant.
- **RGAA**, **WCAG** : le référentiel français et la norme internationale d'accessibilité des contenus web.
