# C17.11 : contrôle de `README.md`, format et contenu (02/11/2026)

Ce que le critère demande (référentiel, C17) : la documentation technique couvre l'installation, l'architecture, les
dépendances et l'exécution des tests, et elle est communiquée dans un format qui respecte les recommandations
d'accessibilité. Ce fichier contrôle le **format** et le **contenu** de `README.md`, la porte d'entrée du dépôt ; il ne
prouve pas sa **communication**, qui reste à faire et à prouver. `docs/ARCHITECTURE.md` et `docs/CI-CD.md`, contrôlés le
01/11 (`controle-accessibilite-architecture-et-ci-cd-2026-11-01.md`), sont remesurés ici : ils ont changé depuis.

## Les documents

| Document | Dernier changement | Lu comment |
|---|---|---|
| `README.md` | commit `2cca958`, 31/10/2026 | en Markdown, tel que GitHub l'affiche |
| `docs/ARCHITECTURE.md` | commit `afa741d`, 01/11/2026 (« six » checks devenus « sept ») | idem |
| `docs/CI-CD.md` | commit `8ff64bf`, 02/11/2026 (job `base`, marqueur, Playwright) | idem |

## Les règles appliquées, mesurées par script

Celles du protocole de veille (`docs/veille/README.md`, § 5.4), comme pour les contrôles du 31/10 et du 01/11. Blocs de
code exclus, le 02/11/2026.

| Règle | `README.md` | `docs/ARCHITECTURE.md` | `docs/CI-CD.md` |
|---|---|---|---|
| Un seul titre de premier niveau | oui (10 titres) | oui (11 titres) | oui (17 titres) |
| Aucun niveau de titre sauté | oui | oui | oui |
| Texte de lien explicite, jamais une URL ni « ici » | oui (21 liens ; six ont pour texte un chemin de fichier en code, qui dit ce qu'ils ouvrent) | oui (1 lien) | oui (5 liens) |
| Aucune URL nue dans le texte courant | oui ; les adresses locales de l'API sont dans du code en ligne | oui | oui |
| Texte alternatif sur chaque image | sans objet : aucune image | oui (1 image) | sans objet |
| Tableaux avec une ligne d'en-tête | oui (3 tableaux) | oui (6 tableaux) | oui (5 tableaux) |
| Aucune information portée par la seule couleur | aucune mention trouvée ; les états du tableau des livrables ont un mot à côté de l'émoji | aucune | aucune |

## Le contenu, contre le critère

| Ce que le critère demande | Dans `README.md` | Écart |
|---|---|---|
| Installation | « Lancer le projet » : environnement, dépendances, fichier de configuration, serveur | la création d'environnement bloquée est attribuée à « AppLocker » : faux, c'est Smart App Control (diagnostic corrigé le 02/09/2026) |
| Architecture | « Structure » (dossiers) ; le schéma est dans `docs/ARCHITECTURE.md` | aucun lien vers `docs/ARCHITECTURE.md` dans tout le README (vérifié par recherche du nom) |
| Dépendances | « Stack » et `requirements.txt` | aucun |
| Exécution des tests | « Lancer les tests » : `pytest -q` | chiffres du 10/10 (836 collectés ; 1 926 aujourd'hui) ; les tests PostgreSQL (base de test déclarée, marqueur `postgresql`) ne sont décrits que dans `docs/CI-CD.md` |
| (état du projet) | tableau des livrables « État au 10/10/2026 » | daté, donc honnête, mais périmé : E1 v3 et E3 v2 livrés et tagués, E2, E4 et E5 rédigés depuis |

## Limites

- Le rendu de GitHub n'a pas été audité, et aucun lecteur d'écran n'a été passé.
- Les écarts de contenu ne sont pas corrigés ici : la mise à jour de `README.md` attend la décision d'Era.
- La communication n'est pas faite : un document présent dans le dépôt n'est pas un document communiqué.
