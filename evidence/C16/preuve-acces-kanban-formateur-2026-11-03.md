# Preuve C16.4 : le formateur ouvre le tableau Kanban (03/11/2026)

> **C16.4** : « Les éléments de pilotage sont rendus accessibles à toutes les parties du projet et ce tout au long du
> projet… » (texte repris dans `docs/recette/registre-des-partiels.md`, ligne C16.4).
> Écart noté avant cette preuve : « accès au tableau non revérifié » (rapport E4 v1.1, tableau d'auto-évaluation).

## 1. L'échange, daté

| Quand (heure de Paris) | Qui | Quoi |
|---|---|---|
| 03/11, 11 h 27 | Era | courriel au formateur : le tableau est un projet GitHub privé, séparé du dépôt (être collaborateur du dépôt ne suffit pas pour le voir) ; lien `https://github.com/users/Ganda15/projects/4` ; demande de confirmation depuis le compte `bybysker`. Avant l'envoi, Era a ouvert la gestion des accès du tableau : `bybysker` y figurait déjà (constat d'Era) |
| 03/11, 11 h 55 | Elbby, formateur | réponse écrite, texte original : **« Bonjour Era, oui j'ai bien accès au projet »** |

**Source** : la messagerie d'Era, fil « Objet : RITA : six questions avant la remise des livrables », réponse du
formateur horodatée 10:55:50 UTC, lue le 03/11 par le connecteur Gmail de la session de travail. Era a fourni le même
jour deux captures d'écran de l'échange : l'une affiche le texte original en français, identique à la citation
ci-dessus ; l'autre, la traduction automatique de Gmail en anglais (« Hello Era, yes I do have access to the project »).
Le texte qui fait foi est l'original en français. Les adresses électroniques ne sont pas recopiées ici (données
personnelles).

## 2. Le tableau, vérifié le même jour

```
gh project view 4 --owner Ganda15 --format json --jq '{title, public, closed, items: .items.totalCount, url}'
{"closed":false,"items":34,"public":false,"title":"RITA - Pilotage Kanban (livrables E2-E5)","url":"https://github.com/users/Ganda15/projects/4"}
```

Le tableau est privé (`public: false`) : l'accès du formateur passe par une invitation, pas par le lien seul.

## 3. Ce que cette preuve établit, et ce qu'elle n'établit pas

- **Établi** : le 03/11, le formateur, partie prenante du projet, ouvre le tableau de pilotage depuis son propre compte
  et le confirme par écrit.
- **Le dépôt, où vivent le backlog (les issues), la méthode et les revues, est ouvert au formateur depuis août** :
  invitation envoyée le 13/08 à 15 h 16 et vérifiée le 14/08, encore en attente (commit `4e92bde`) ; acceptation
  constatée le 24/08 (commit `959f098` ; `docs/FILE-DE-VALIDATION.md`, « `bybysker (read)` dans `/collaborators` ») ;
  accès vérifié de nouveau le 30/10 et le 03/11
  (`gh api repos/Ganda15/rita-agent/collaborators/bybysker/permission` : `read`). Le backlog, créé le 26/09, lui a donc
  été lisible dès sa création. Selon Era, le formateur a aussi confirmé oralement son accès GitHub le 26/09 ; cette
  confirmation orale n'a pas de trace écrite.
- **Le tableau** est lié au dépôt (projet n° 4, privé, `repository.projectsV2` le 03/11), mais un projet privé demande
  son propre accès : donné le 26/09 ([`preuve-mise-en-place-kanban.md`](preuve-mise-en-place-kanban.md), mutation
  `updateProjectV2Collaborators`, réponse `bybysker`) ; toujours en place le 03/11, puisque `bybysker` figurait déjà
  dans la gestion des accès du tableau (constat d'Era) ; confirmé par écrit par le formateur le même jour. L'accès du
  formateur au tableau est donc établi du 26/09 au 03/11. Le tableau n'a plus bougé après le 14/10 (registre, ligne
  C16.1).
- **Le jury** : pas encore invité ; le retour du formateur du 03/11 (point 8) prévoit d'ouvrir le dépôt aux
  examinateurs le jour de l'examen, puis de le refermer.

Le statut de C16.4 ne change pas dans ce fichier : il se décide par Era, critère par critère.
