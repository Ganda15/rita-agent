# Journal des envois — la trace du partage de veille (C6)

> **Deux critères de C6 sur huit** ne portent ni sur la qualité des notes ni sur les sources :
> ils demandent que les synthèses soient *« communiquées aux parties prenantes »* et que la
> veille soit menée *« en animant le travail collectif »*. Ce registre est **la seule preuve**
> que ces deux-là sont satisfaits.
>
> Protocole : `README.md` §5. Créé le **2026-08-15**.

## Comment on le remplit

- **Une ligne par envoi**, écrite **le jour de l'envoi**.
- ⚠️ **Jamais reconstitué après coup.** Un registre rempli d'un bloc la veille du rendu se
  repère immédiatement : les dates ne collent plus avec les notes qu'il prétend accompagner.
- La colonne **Retour reçu** est celle qui compte pour *« animer le travail collectif »* :
  un message sans réponse prouve qu'on a publié, pas qu'on a animé. **Si elle reste vide
  deux fois de suite, changer de canal** — ne pas continuer à publier dans le vide.
- Preuve conservée : capture d'écran ou export du mail, dans `evidence/C6/` — **ce dossier
  n'existe pas encore au 15/08/2026**, il est à créer au premier envoi.

---

## Les envois

| # | Date | Destinataire | Canal | Notes couvertes | Retour reçu | Preuve |
|---|---|---|---|---|---|---|
| **1** | **2026-08-16** | **la promo** | **Discord** — canal général | **S33** — injection de prompt | ⬜ en attente | ⬜ capture à faire **après** les réponses |
| 2 | ⬜ | le formateur référent | mail + PDF | S33 | ⬜ | ⬜ — bloqué : congé |
| 3 | 2026-10-11 | la promo | Discord, canal #veille (20 h 04) | S41 : les détecteurs d'injection réussissent le test sur lequel ils sont entraînés | ✅ 1 réponse, relevée le 09/11 : un étudiant de la promotion, 13/10 à 07 h 18, lien Nielsen Norman Group sur les temps de réponse (sujet UX, pas la question posée) ; 2 réactions 👍 | ✅ message posté : `evidence/C6/envoi-2026-10-11-promo-discord-veille.png` · ✅ [capture du retour prise le 09/11](../../evidence/C6/retour-S41-capture-2026-11-09.jpg) · [réponse dans Discord (compte membre requis)](https://discordapp.com/channels/1501232309775634546/1501233243238699060/1559435233647132712) |
| 4 | 2026-11-09 | la promo | Discord, canal #veille (11 h 41) | S46 : les motifs de texte ne vérifient pas l’autorité d’une source | ⬜ en attente | ✅ message posté : [evidence/C6/envoi-2026-11-09-promo-discord.png](../../evidence/C6/envoi-2026-11-09-promo-discord.png) · ⬜ fil après les réponses |

> **Contrôle du 09/11/2026** : une réponse directe au message S41 du 11/10 est visible dans Discord, datée du 13/10 à 07 h 18. La capture a été prise le 09/11, sans reconstituer un envoi passé. Le cas de deux envois consécutifs sans aucun retour n’est donc pas établi. Ce retour porte sur l’UX et ne résout pas la question des faux positifs. S33 n’a pas été revérifié lors de ce contrôle. La synthèse S46 a ensuite été publiée dans #veille le 09/11 à 11 h 41 ; son retour est en attente. Le message YouTube du formateur du 15/10 n’est pas compté comme une réponse à S41.

> **Accès aux preuves** : le lien Discord demande un compte membre du serveur. Les captures locales permettent de consulter les messages sans cet accès ; un code HTTP 200 ne prouve pas que le message est visible par un évaluateur extérieur.

> **Au 2026-08-16 : 1 partage effectué sur 2.**
> ✅ La note S33 a été **postée dans le canal Discord de la promo le 16/08**, terminée par une
> question ouverte — le critère *« en animant le travail collectif »* est **lancé**.
> ⬜ Il n'est **pas encore prouvé** : ce sont les **réponses** qui font la preuve, pas le
> message. La capture est à faire dans un ou deux jours, une fois le fil nourri.
> 🔴 L'envoi au **formateur** reste à faire — bloqué par son congé, en file
> (`../FILE-DE-VALIDATION.md`, ligne 4).

> **Au 2026-10-11 : 2 partages à la promo effectués (S33 le 16/08, S41 le 11/10), 0 au formateur.**
> ✅ La note S41 (`2026-S41-mesurer-le-gardefou.md`) a été **postée dans le canal #veille du Discord de la promo le
> 11/10 à 20 h 04**, terminée par une question ouverte (capture du message : `evidence/C6/`). ⬜ Les **réponses** font
> la preuve : capture du fil à faire une fois qu'il y en a, rangée dans `evidence/C6/`. La capture du partage S33 (16/08) n'a toujours pas été faite. 🔴 L'envoi au formateur
> reste en file.

**Le message S41 tel que posté le 11/10 à 20 h 04** (texte relevé sur la capture du message) :

> sécurité des agents LLM
>
> Un détecteur d'injections peut être excellent sur un benchmark et rater presque tout sur un autre. Un article
> d'octobre a retesté 15 détecteurs sur trois jeux d'essai : le classement ne se transfère pas d'un jeu à l'autre.
> PIGuard, par exemple, détecte 95,1 % des injections de la moitié test de BIPIA, et seulement 2,1 % de celles
> d'AgentDojo, au même seuil. Pour les deux détecteurs dont les données d'entraînement sont publiques, la cause est
> claire : ils ont été entraînés sur des données qui ressemblent au test. Et l'auteur le reconnaît : il règle son
> seuil sur les données de test elles-mêmes, ce qui avantage tous les détecteurs.
>
> Ça me concerne directement : mon filtre d'injection et ses premiers cas de test ont été écrits le même jour, et
> j'avais obtenu 100 % de blocage le 29/07, sur 7 cas calqués sur les motifs. Les 3 cas écrits après coup contre les
> motifs sont exactement les 3 qu'il rate (7 sur 10).
>
> Ma question ouverte : pour mesurer les faux positifs là où le filtre est vraiment branché, il faudrait un lot de
> contenus sains représentatifs de mes vraies sources (articles RSS, champs extraits des pages par scraping). Vous
> feriez comment pour constituer ce lot ?
>
> Lien : https://arxiv.org/abs/2610.03448

### ⚠️ Le formateur est bloqué. La promo ne l'est pas.

Les deux critères ne visent pas le même destinataire :

| Critère | Destinataire | Bloqué par le congé ? |
|---|---|---|
| *« communiquées aux parties prenantes »* | le **formateur** | ✅ oui — attendre son retour est légitime |
| *« en animant le travail collectif »* | la **promo** | ❌ **non** — le canal de classe est disponible aujourd'hui |

**Attendre le formateur pour les deux, c'est laisser à zéro un critère qui n'a jamais dépendu
de lui.** Et l'animation du travail collectif est le plus lent des deux à produire : il faut
que d'autres personnes répondent, ce qui prend des jours. Plus il démarre tard, moins il a de
chances d'aboutir avant le 05/11.

---

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Partie prenante** | Toute personne concernée par le projet : formateur, camarades de promo, jury |
| **Animer le travail collectif** | Provoquer des échanges autour de la veille — pas seulement publier. La preuve, ce sont les **réponses**, pas les envois |
| **Registre** | Tableau tenu au fil de l'eau, dont la valeur vient précisément du fait qu'il n'a pas été écrit d'un bloc |
