# Atelier croisé n°3 : Les données et l'ancrage

Phase 6, fil rouge. Grille prévue pour être remplie par l'évaluateur pendant la démonstration, puis versée dans le
dépôt du présenté.

| Présenté | Évaluateur | Date | Projet |
|---|---|---|---|
| Eramalingam GANDAKUMAR | le formateur | 19/10/2026 | RITA, document d'entrée [`docs/sprint-3/README.md`](../../docs/sprint-3/README.md) |

**Grille non remplie.** L'atelier s'est tenu avec le formateur, en direct sur l'adresse de production. La
[grille officielle](https://simplonline-v3-prod.s3.eu-west-3.amazonaws.com/media/file/pdf/grille-atelier-3-donnees-ancrage-6acc9234d3abb849233977.pdf)
n'a pas été remplie : aucun critère n'a été noté ✓, ~ ou ✗, et aucun point fort ni conseil prioritaire n'a été écrit.
Les retours ont été donnés à l'oral ; ils sont relevés ci-dessous depuis les notes de séance du 19/10/2026.

**Journal des retours.** Conseil reçu à l'atelier n°2 : « RAS » ([grille de l'atelier n°2](sprint-2-grille.md)) ;
rien à traiter.

| # | Critère | ✓ / ~ / ✗ | Preuve observée, remarque |
|---|---|---|---|
| 1 | **Sources licites.** Les données sont identifiées. La minimisation RGPD est appliquée, ou sa non-applicabilité est argumentée. | non noté | grille non remplie |
| 2 | **Traçabilité.** À ma question, la réponse cite sa source et j'ai pu remonter jusqu'à elle (document, table, identifiant, date). | non noté | grille non remplie |
| 3 | **Refus hors corpus.** À ma question hors sujet, l'application refuse proprement au lieu d'inventer. | non noté | grille non remplie |
| 4 | **Pipeline rejouable.** L'ingestion se relance par une commande, pas par une suite de manipulations. | non noté | grille non remplie ; ingestion lancée en direct, passage `39265862974`, réussi |
| 5 | **En production.** Tout ce qui précède est visible sur l'environnement déployé, pas dans un notebook. | non noté | grille non remplie |

## Les retours oraux du formateur

- La présentation est trop dense et non linéaire : difficile à suivre, même en connaissant le projet.
- Aller droit au but, couche par couche : d'abord le projet en deux ou trois phrases, puis les sources de données, le
  stockage et la fréquence d'ingestion ; creuser un niveau seulement si la personne le demande.
- Ne pas noyer l'auditoire : une présentation technique tient en cinq minutes.
- Les schémas ont déjà été vus la dernière fois : les montrer vite, sans s'y attarder.
- Point positif : un travail réel, et une évolution visible depuis la dernière fois.

Quatre retours de la même séance manquaient à ces notes. Ils ont été relevés le 21/10/2026 dans la transcription de la
séance :

- Les points n'ont pas suivi l'ordre des « modalités pédagogiques » du brief : les présenter dans cet ordre, comme une
  liste à cocher.
- La partie données a été présentée comme le cadrage du sprint 1 : montrer ce qui est construit (la collecte, sa mise
  en œuvre), sans redire le cadrage.
- Trop de temps sur ce qui n'est pas attendu, comme la démonstration des sources (« c'est pas attendu ») et les
  livrables.
- Le code en dernier, et seulement si on le demande : « tel fichier qui permet de faire ça ».

---

## Suite donnée par le présenté

Pour chaque retour : traité (commit), reporté (sprint et raison) ou écarté (raison).

| Retour | Suite | Commit ou raison |
|---|---|---|
| Présentation trop dense et non linéaire | reporté au sprint 4 | l'oral de l'atelier n°4 sera court et linéaire |
| Couche par couche : le projet, puis les sources, le stockage, la fréquence d'ingestion | traité dans le livrable ; reporté au sprint 4 pour l'oral | livrable du sprint 3, version 2, § 1.2 et 1.3 |
| Une présentation technique tient en cinq minutes | reporté au sprint 4 | partie technique limitée à cinq minutes, le détail gardé pour les questions |
| Schémas déjà vus : les montrer vite | reporté au sprint 4 | un schéma déjà présenté n'est plus commenté, sauf question |
| Suivre l'ordre des modalités pédagogiques, comme une liste | reporté au sprint 4 | l'oral de l'atelier n°4 présente les six points des modalités, dans leur ordre |
| Montrer ce qui est construit, pas le cadrage du sprint 1 | reporté au sprint 4 | l'oral montre les garde-fous construits et les fait jouer en production ; le cadrage n'est pas redit |
| Pas de temps sur ce qui n'est pas attendu | reporté au sprint 4 | ni démonstration des sources ni présentation des livrables pendant l'oral |
| Le code en dernier, seulement si on le demande | reporté au sprint 4 | l'oral ne montre le code que sur question, fichier par fichier |
| Point positif | rien à faire | point positif |
| Grille non remplie | traité | signalé au § 8.1 du livrable du sprint 4 |
