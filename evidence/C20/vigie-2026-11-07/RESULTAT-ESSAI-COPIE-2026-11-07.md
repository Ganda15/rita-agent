# C20.5 : essai de disponibilite sur copie, 07/11/2026

## Resultat

**Essai reussi : indisponibilite locale → alerte GitHub → service retabli → cloture par la vigie.**

Incident : https://github.com/Ganda15/rita-agent/issues/230

| Etape | Heure de Paris | Constat conserve |
|---|---|---|
| Depart | 21:53:50 | `/health` et `/sante` repondent 200 ; aucun exercice actif |
| Arret de la copie | 21:53:51 | Seul `rita-api-c20-20261107` est arrete |
| Deux sondes en echec | 21:53:56 puis 21:54:10 | Regle du signal service : 2 essais, attente de 10 secondes entre les essais ; les temps de connexion s'ajoutent |
| Alerte | 21:54:11 | Issue #230 ouverte par la vigie, sortie 1 attendue |
| Redemarrage | 21:54:13 | Le conteneur local est redemarre |
| Retour constate | 21:55:14 puis 21:55:17 | `/health` repond 200 avec le commit attendu |
| Cloture | 21:55:22 | La vigie ferme #230 avec un commentaire « Retour a la normale » ; `/sante` repond 200 ; sortie 0 |

L'accueil de `http://localhost:8011/` repond aussi 200 apres l'essai. Cette copie technique a une base neuve et aucune cle de fournisseur : elle sert au test de disponibilite, pas a une demonstration de generation de briefing.

## Version et isolation

- Commit de production constate : `6f428d61511019d7b6013fb007e290c133d48c2e`.
- Meme image Docker : `sha256:1b262b59308ac70f18a06c195f2c4e5ce2e63571285496adff15870e77064f6a`, copiee du serveur sans reconstruction.
- Projet local distinct : `rita-c20-20261107`, conteneurs et volumes neufs ; les anciennes piles locales sont conservees.
- Publication du port : `127.0.0.1:8011` seulement.
- Cles API et exercice locales generees pour cette copie ; configuration privee dans Temp, hors de ce dossier de preuves.
- Aucun identifiant de fournisseur Azure, Anthropic ou OpenRouter dans la copie ; Langfuse desactive.
- Aucun appel au modele. Aucune panne ni modification de configuration en production.
- Verification finale : `/health` de production repond toujours 200 avec le meme commit.
- #77 et #132 restent ouverts avec leurs dates de mise a jour anterieures a cet essai.

## Methode et limites

La fonction reelle `monitorage.vigie.passage` et les seuils de la version ci-dessus ont ete utilises sans modification. La sonde HTTP et les operations GitHub sont reelles. Un adaptateur du banc limite les operations GitHub au seul titre **Incident : vigie (prototype local) « service »**, pour ne pas clore les anciens incidents a partir des compteurs vides de cette nouvelle copie.

Ce n'est pas une execution de la CLI complete sur copie : c'est un essai reel du signal `service` et de sa chaine d'alerte/retablissement. Il ne mesure pas le scenario de cinq erreurs du fournisseur sur quinze minutes. Le critere de retablissement du signal service est le retour HTTP 200 ; aucun seuil n'a ete abaisse.

Le premier controle immediat du banc n'a pas retrouve l'issue juste apres sa creation : il a rendu une assertion en echec et redemarre la copie par securite. Le journal conserve cet evenement. La liste GitHub a ensuite permis de retrouver #230 ; la phase de retablissement a repris sur **cette meme issue**, qui a ete fermee par la vigie. Aucun historique n'a ete efface ni reconstitue.

Un code 0 signifie qu'aucun verdict `probleme` n'a ete constate. Les autres signaux de la copie, sans trafic ni donnees, peuvent rester `inconnu`.

## Pieces

- `essai-service.json` : journal horodate de l'essai, y compris l'assertion du banc puis la reprise.
- `issue-essai-service.json` : etat final et commentaire de cloture de #230.
- `copie-baseline-health.json` et `copie-baseline-sante.json` : etat initial reel.
- `copie-state.json` : version et description de l'isolation, sans cle.
- `essai_disponibilite.py` : banc de verification et restriction des incidents.
- `RESULTAT-VIGIE-2026-11-07.md` et `verification-secret.json` : correction anterieure du secret et passage manuel de production reussi.

## Encore a constater pour C20.5

Au dernier controle de cette session, le dernier passage reussi de production reste le run manuel **42411132337, tentative 2**. L'execution `schedule` prevue a **21:17 UTC, soit 22:17 a Paris**, n'est pas encore observee. Le demarrage peut etre retarde par GitHub. Conserver son URL, son evenement `schedule`, son commit, son resultat et sa ligne de sortie avant de conclure sur l'execution automatique en production.

Le rapport E5 et la grille n'ont pas ete modifies par cette intervention.
