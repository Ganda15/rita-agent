# C17.11, C18.6, C19 : contrôle d'accessibilité de deux documents techniques (01/11/2026)

Ce que les critères demandent (référentiel, C17 à C19) : la documentation technique est communiquée dans un format qui
respecte les recommandations d'accessibilité. Ce fichier contrôle le **format** de deux documents ; il ne prouve pas
leur **communication**, qui reste à faire et à prouver.

## Les documents

| Document | Dernier changement | Lu comment |
|---|---|---|
| `docs/ARCHITECTURE.md` | commit `2cca958`, 31/10/2026 | en Markdown, tel que GitHub l'affiche |
| `docs/CI-CD.md` | commit `515c214`, 24/10/2026, puis une ligne ajoutée au § 6 le 01/11/2026 (vérifier qu'un tag publie son image) ; mesures refaites après cet ajout | en Markdown, tel que GitHub l'affiche |

Aucun PDF n'est produit pour ces deux documents : ils se lisent dans le dépôt.

## Les règles appliquées

Celles du protocole de veille (`docs/veille/README.md`, § 5.4), déjà appliquées au guide d'exploitation le 31/10
(`evidence/C8/controle-accessibilite-guide-2026-10-31.md`) et à la synthèse de veille le 01/11
(`evidence/C6/controle-accessibilite-synthese-2026-11-01.md`).

## Mesures

Lecture de la source, blocs de code exclus, le 01/11/2026.

| Règle | `docs/ARCHITECTURE.md` | `docs/CI-CD.md` |
|---|---|---|
| Un seul titre de premier niveau | oui (11 titres) | oui (17 titres) |
| Aucun niveau de titre sauté | oui | oui |
| Texte de lien explicite, jamais une URL ni « ici » | oui (1 lien) | oui (5 liens) |
| Aucune URL nue dans le texte courant | oui | oui ; la seule adresse fait partie d'une commande, dans du code en ligne (§ 6) |
| Texte alternatif sur chaque image | oui (1 image) | sans objet : aucune image |
| Tableaux avec une ligne d'en-tête | oui (6 tableaux) | oui (5 tableaux) |
| Aucune information portée par la seule couleur | aucune mention trouvée | aucune mention trouvée |

## Limites

- Le texte alternatif du schéma d'`ARCHITECTURE.md` est court (« Le chemin d'un briefing ») : le schéma montre aussi
  le chemin d'une question et la surveillance.
- Le rendu de GitHub n'a pas été audité, et aucun lecteur d'écran n'a été passé.
- La communication n'est pas faite : un document présent dans le dépôt n'est pas un document communiqué.
