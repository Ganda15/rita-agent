# C8.5 : contrôle d'accessibilité du guide d'exploitation en PDF (31/10/2026)

Ce que le critère demande (référentiel, p. 9) : la documentation « est communiquée aux parties prenantes dans un
format qui respecte les recommandations d'accessibilité ». Ce fichier prouve le **format** ; l'**envoi** n'est pas fait
au moment où il est écrit.

## Le document

- Source : `docs/exploitation.md`, mise à jour du 31/10/2026.
- PDF : `docs/EXPLOITATION.pdf`, 35 pages, rendu le 31/10/2026 par
  `C:\Python314\python.exe -X utf8 scripts\rendre_pdf.py docs\exploitation.md --lisible`.
- L'ancien PDF datait du 11/10 et ne reflétait plus le guide.

## Les règles appliquées, et d'où elles viennent

| Règle | Source |
|---|---|
| Un seul titre de premier niveau, aucun niveau de titre sauté | règles du projet, `docs/veille/README.md`, § 5.4 |
| Texte des liens explicite, aucune URL nue dans le texte courant | idem |
| Texte alternatif sur chaque image | idem (le guide n'a pas d'image) |
| Tableaux avec une ligne d'en-tête, sans cellule fusionnée | idem |
| Aucune information portée par la seule couleur | idem |
| PDF balisé, titre, langue, signets tirés des titres | guides AcceDe d'Atalan sur les PDF accessibles |
| Texte d'au moins 12 pt, police sans empattement, fort contraste | pratique couramment citée pour un document texte ; aucun document officiel de l'association Valentin Haüy n'a été trouvé le 31/10 |

## Ce qui a été corrigé pour ce rendu

- Le rendu des rapports met le texte à 10 pt, le code et les tableaux sous 9,5 pt, et ne distingue les liens que par
  leur couleur. L'option `--lisible` de `scripts/rendre_pdf.py` (test d'abord, `tests/test_rendre_pdf_lisible.py`) met
  le texte et les tableaux à 12 pt, le code à 11 pt, les titres sans empattement, et souligne les liens.
- Le PDF n'avait aucun signet : Chrome les tire maintenant des titres (`--generate-pdf-document-outline`).
- Quatre liens relatifs du guide devenaient, une fois imprimés, des adresses de fichier du poste
  (`/C:/Users/...`) : morts pour le lecteur, et ils exposaient un chemin local. Ils sont rendus comme du texte.

## Corrections de fond, après une seconde relecture (31/10/2026)

Une relecture du PDF a relevé des erreurs de sens, vérifiées une à une dans le code avant d'être corrigées dans
`docs/exploitation.md` (aucun changement du fonctionnement de l'application) :

| Passage | Erreur | Vérifié dans |
|---|---|---|
| Alerte de temps de réponse | « 95 % des réponses mettent plus de 10 s » : c'est l'inverse d'un p95 | `monitorage/seuils.json`, `monitorage/seuils.py` (seuils atteints à partir de 10 s et 20 s, au moins 5 requêtes, 15 min) |
| Diagnostic | la trace « dont l'identifiant est le `request_id` » : l'identifiant en est dérivé | `src/traces.py` (`create_trace_id(seed=request_id)`, `request_id` en métadonnée) |
| Diagnostic | « aucune ligne : ce n'est pas une vraie panne » : une absence ne prouve rien | (raisonnement) |
| Vigie | « code 0 : tout est sain » : un signal peut rester en ATTENTION ou INCONNU | `monitorage/vigie.py` (code 1 seulement pour un signal en problème) |
| Vigie | une planification laissée entendre ; aucune n'est consignée | `.github/workflows/` (aucune tâche de vigie) |
| Exercices | « panne et dérive simulées coupées en production » : seule la panne l'est | `api/exercice.py`, `monitorage/exercer.py` (la dérive utilise la clé ordinaire) |
| Couverture | 94,70 % puis « mesure réelle actuelle : 92 % » ; périmètre non dit | CI du 31/10 (96,32 %), `.coveragerc` (`source`) |
| Données | `article` marqué « non » personnel ; parcours Question absent | registre RGPD (corpus d'articles, T8) |
| Installation | une vérification « prévue après le gel du 15/10 » | état au 31/10 : toujours pas consignée |
| Fournisseurs | Mistral et le coût d'Azure | `CONTINUITE.md` (11/10) ; rapport E2 |

Une table « Lire ce guide » a été ajoutée en tête : la copie locale des exercices du sprint 5, RITA livrée en
production, et l'installation locale, avec pour chacune où elle s'exécute et ce qu'elle touche.

## Mesures sur le PDF final (31/10/2026)

Lues avec `pikepdf` et `PyMuPDF` :

| Contrôle | Résultat |
|---|---|
| PDF balisé (`/MarkInfo /Marked`) et arbre de structure (`/StructTreeRoot`) | oui, oui |
| Langue du document (`/Lang`) | `fr` |
| Titre du document, affiché à l'ouverture (`/Title`, `/DisplayDocTitle`) | « Exploitation de RITA : déployer, diagnostiquer une panne, revenir en arrière », oui |
| Signets | 66, tirés des titres |
| Texte extractible | oui (5 675 caractères sur les trois premières pages) |
| Taille du texte | 76 % du texte à 12 pt, 20 % à 11 pt (code), le reste en titres plus grands ; numéros de page à 10 pt |
| Liens vers un fichier local | 0 |
| Liens web | deux adresses publiques, HTTP 200 le 31/10 (`https://178-104-184-125.sslip.io/tableau-de-bord.html`, `https://www.postgresql.org/docs/17/ddl-schemas.html`) ; trois adresses `localhost` de la copie locale, utilisées par les procédures |

Sur la source : un seul titre de premier niveau, aucun niveau sauté, 34 liens Markdown dont aucun au texte vague
(« ici », « lien »), aucune image, aucune information donnée par la seule couleur. Rendu regardé page par page sur
quatre pages (première page, table des clés, services externes, commandes) : accents, tableaux, gras et code lisibles.

## Les limites, dites franchement

- **Ce n'est pas un audit PDF/UA complet.** Aucun outil de référence (PAC, veraPDF) n'a été lancé : l'ordre de lecture
  et la qualité du balisage produit par Chrome ne sont pas vérifiés par un tel outil, ni par un lecteur d'écran.
- **Le contraste des couleurs** n'est pas mesuré outil en main ; le texte courant est sombre sur fond blanc.
- **Un signet** (le titre principal) perd une espace à la coupure de ligne : « unepanne ».
- **Le code reste à 11 pt**, sous les 12 pt du texte.
- **La remise aux parties prenantes** n'est pas faite : décision du 31/10, le guide part avec les livrables du 05/11,
  et cet envoi reste à prouver par une trace datée.
