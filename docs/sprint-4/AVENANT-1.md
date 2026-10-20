# Avenant n°1 au dossier du sprint 1 : le parcours des questions entre dans la composante agentique

> Décidé par Era le 18/10/2026 (option A de la réception du brief du sprint 4), écrit le 19/10/2026. **À présenter au
> formateur** pour validation : la grille de l'atelier 4 demande qu'un écart au dossier du sprint 1 soit « un avenant
> validé, pas une dérive silencieuse ». Qui valide l'avenant n'est pas précisé par le brief : À CLARIFIER.

## 1. Ce que disait le dossier du sprint 1

`docs/CADRAGE-V1.md`, § 3 : la composante agentique est le **graphe du briefing**, trois étapes fixes (`scout`, `rag`,
`redacteur`) derrière `POST /briefing`, avec des garde-fous en entrée, sur les articles et en sortie. L'entrée est une
valeur cotée (un ticker). Le § 1 met hors périmètre de la V1 « pas de nouvel agent ».

## 2. Ce qui a changé depuis, et pourquoi

- **Le brief du sprint 3** a demandé que l'application réponde à partir de ses données en citant ses sources, et
  qu'elle refuse ce qui sort de son corpus. RITA a donc reçu un second parcours, `POST /question` : une question libre
  en français, une réponse citée ou un refus motivé. Il est en production depuis la livraison N5 (16/10/2026).
- **Le brief du sprint 4** demande des garde-fous contre des contenus hostiles, des injections et des tentatives
  d'extraction, que l'évaluateur tire lui-même en direct. Ces attaques sont du texte libre. `POST /briefing` ne reçoit
  qu'un ticker : elles ne peuvent viser que le parcours des questions.

Sans avenant, la composante annoncée au sprint 1 ne contiendrait pas la seule partie de RITA qui reçoit du texte
libre, et les critères 2 à 4 de la grille ne pourraient pas se démontrer sur elle.

## 3. Ce que dit l'avenant

La composante agentique de RITA comprend **deux parcours** :

1. **Le briefing**, inchangé : le graphe à trois étapes fixes, sur une valeur cotée.
2. **Le parcours des questions** : recherche dans le corpus, refus sans appel au modèle si aucun passage n'est assez
   proche, un appel au modèle sous un format imposé, puis des contrôles (citations, garde-fou de sortie) ; les
   références sont construites à partir des passages retrouvés.

Les garde-fous du sprint 4 portent sur les deux parcours, et d'abord sur le parcours des questions, qui reçoit du texte
libre.

## 4. Ce qui ne change pas

- **Pas d'agent qui choisit ses outils.** Les deux parcours ont des étapes fixes, pour la même raison qu'au sprint 1 :
  en finance, chaque texte doit pouvoir être relu et expliqué.
- **Pas de nouvel agent au sens du sprint 1.** Le parcours des questions est une chaîne fixe, sans choix d'outil et sans
  mémoire. L'avenant le déclare comme une partie de la composante plutôt que de le laisser hors du dossier.
- **Lecture seule.** RITA lit et rédige ; elle n'écrit dans aucun système extérieur et n'envoie rien.
- **Les engagements du sprint 3 restent** : Azure, zone de données de l'UE, seul fournisseur du parcours des
  questions ; le texte des questions n'est jamais conservé.
- **Le contrat personnel du § 6** n'est pas modifié par cet avenant. Son état critère par critère est suivi à part
  (`docs/sprint-4/CONTRAT.md`, à écrire au sprint 4).
