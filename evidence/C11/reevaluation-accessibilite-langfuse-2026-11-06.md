# C11 · Réévaluation de l'outil de monitorage au regard de l'accessibilité, 6 novembre 2026

**Le critère** (C11) : l'accessibilité est prise en compte dans le choix de l'outil de monitorage.

**Pourquoi cette preuve.** Langfuse a été choisi le 03/10 pour tracer chaque appel au modèle ; son accessibilité n'a été
examinée qu'après ce choix (rapport E3, § 5.6), sans déclaration de l'éditeur ni mesure. Le 06/11, après le retour du
formateur, le choix est **réévalué avec ce critère**, et une règle est écrite pour l'outil suivant. Le choix du 03/10
n'est pas réécrit : la réévaluation est datée.

## Ce qui a été relevé le 06/11/2026

| Question | Relevé | Source |
|---|---|---|
| Langfuse publie-t-il une déclaration d'accessibilité ? | aucune trouvée | recherche web du 06/11 (aucun résultat sur Langfuse lui-même) |
| Que mesure un audit automatique sur une page publique ? | page de connexion `https://cloud.langfuse.com/auth/sign-in` : **94/100** en accessibilité | Lighthouse 13.5.0, HeadlessChrome 156, le 06/11 à 20 h 40 UTC ([`lighthouse-langfuse-connexion-2026-11-06.json`](lighthouse-langfuse-connexion-2026-11-06.json)) |
| Quels audits échouent ? | `meta-viewport` : la page interdit l'agrandissement sur mobile (`user-scalable=no`), un vrai obstacle pour une personne malvoyante ; `svg-img-alt` : une image SVG sans texte de remplacement | même fichier |
| L'éditeur corrige-t-il des défauts d'accessibilité ? | une correction trouvée sur son dépôt public : #18361 (« a11y: add missing DialogTitle to four dialog surfaces »), close le 06/10/2026 | `gh search issues --repo langfuse/langfuse accessibility` |

Les pages de traces et de tableaux de bord demandent une connexion : elles ne sont pas auditées ici.

## La décision du 06/11

- **Langfuse reste l'outil de l'exploitant** (traces, coûts, latences). Il n'est pas la restitution destinée aux autres
  lecteurs du projet.
- **La restitution accessible est le tableau de bord de RITA** (`frontend/tableau-de-bord.html`, en production depuis le
  23/10) : verdict de chaque signal en mots et pas seulement en couleur, marqueurs RGAA testés dans un vrai navigateur, et
  accessibilité 100/100 à Lighthouse sur les cinq écrans de RITA le 06/11 (`evidence/C17/mesures-2026-11-06/`).
- **Règle pour l'outil suivant** : l'accessibilité est un critère écrit **avant** le choix ; un outil qui ne publie rien
  est audité sur ses pages publiques, et un obstacle bloquant (zoom interdit, contenu sans texte) est noté contre lui.

## Ce que cette réévaluation ne prouve pas

- Le choix du 03/10 n'a pas été fait sur ce critère.
- Aucun test avec un lecteur d'écran, ni sur Langfuse ni sur RITA.
- Un audit automatique ne voit qu'une partie des obstacles ; une seule page publique de Langfuse est mesurée.

## 📖 Glossaire

- **Accessibilité** : possibilité d'utiliser un service quel que soit son handicap (vue, motricité, audition, cognition).
- **Lighthouse** : outil libre de Google qui audite une page, dont son accessibilité, sur 100.
- **RGAA** : référentiel général d'amélioration de l'accessibilité, la norme française pour les services numériques.
- **Lecteur d'écran** : logiciel qui lit à voix haute le contenu d'une page pour une personne aveugle ou malvoyante.
