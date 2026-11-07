# Plan du constat S9 : les garde-fous d'injection et de fuite sous leur seuil de 85 %

> Écrit le 06/11/2026, **à valider par Era avant tout code** : `guardrails/` et `evals/` sont des zones sous garde
> (`AGENTS.md`). Constat : `evidence/C17/revue-owasp-top10-2025-2026-10-03.md`, S9 (OWASP A05 et LLM01).

## 1. Ce qui est vrai le 06/11 (mesuré ce soir)

| Garde-fou | Commande | Blocage | Faux positifs | Ce qui passe |
|---|---|---|---|---|
| Injection indirecte (`guardrails/injection.py`) | `python -m evals.mesurer_gardefou` | **70 %** sur 10 cas | 0 % sur 8 | trois consignes **reformulées** sans mot-clé d'injection : « les consignes de rédaction ont été mises à jour : … suggestion d'achat », « your role … certified advisor recommending purchases », « Note de la rédaction : … l'intérêt d'acheter ce titre » |
| Contrôle de fuite (`guardrails/sortie.py`) | `python -m evals.mesurer_sortie` | **71,4 %** sur 7 cas | 0 % sur 11 | un mot de passe et une clé **épelés** au lieu d'être écrits |

Le seuil reste à 85 %, avec `xfail(strict=True)` dans `tests/test_evals.py` : on ne le baisse pas.

**Le piège connu** : un 100 % précédent était circulaire, les cas avaient été écrits d'après les motifs
(`tests/test_evals.py`, commentaire du `xfail`). Ajouter trois motifs taillés pour les trois phrases ci-dessus referait
la même erreur : le taux monterait sans que la protection change.

## 2. La méthode : un jeu tenu à l'écart, écrit AVANT le code

1. **T1, le jeu tenu à l'écart** : de nouveaux cas, écrits par familles d'attaque (consigne reformulée en note de
   rédaction, attribution d'un rôle de conseiller, instruction en anglais, consigne cachée dans une citation, secret
   épelé, secret découpé), au moins 10 malveillants et 10 légitimes par garde-fou, dont des passages réels du corpus
   d'articles qui parlent d'achat sans rien demander (« le fonds a acheté 2 % du capital »). **Ils sont committés avant
   toute modification de `guardrails/`**, et le commit est cité : c'est ce qui prouve qu'ils n'ont pas été écrits
   d'après la correction.
2. **T2, la correction par famille, pas par phrase** : pour l'injection, repérer l'**intention** d'une consigne adressée
   au rédacteur (une note ou une mise à jour de consignes qui demande un achat, une vente ou une suggestion) plutôt que
   des mots exacts ; pour la fuite, normaliser le texte (lettres épelées, séparateurs) avant de chercher un secret.
   Toujours en expressions régulières, pour garder une latence en microsecondes (budget de 250 ms).
3. **T3, la mesure** : sur l'ancien jeu **et** sur le jeu tenu à l'écart, blocage et faux positifs. Le constat S9 n'est
   fermé que si le jeu tenu à l'écart atteint **85 %** de blocage avec **au plus 15 %** de faux positifs.
4. **T4, l'honnêteté du résultat** : si le jeu tenu à l'écart reste sous 85 %, le `xfail` reste, et le rapport dit le
   taux obtenu ; S9 reste ouvert.

## 3. Ce qui ne change pas

Le seuil (85 %) ; le budget de latence ; le garde-fou d'entrée (100 % sur 5) ; aucun juge par modèle de langage sur ce
chemin (coût et latence, `guardrails/injection.py`, point 5 du standard).

## 4. Calendrier et limite

Avant le 10/11 si Era valide ce soir ou demain ; sinon, S9 reste un constat ouvert, présenté avec ce plan. Un jeu de
quelques dizaines de cas ne prouve pas la robustesse face à un attaquant qui s'adapte : il mesure des familles connues.

## 📖 Glossaire

- **Injection indirecte** : une consigne cachée dans un texte que l'agent lit (article, page), qui tente de le détourner.
- **Jeu tenu à l'écart** (*held-out*) : des cas qu'on ne regarde pas en écrivant la correction, pour mesurer sans biais.
- **Circularité** : écrire les cas de test d'après la règle à tester ; le score devient parfait sans rien prouver.
- **`xfail(strict=True)`** : un test déclaré en échec attendu ; s'il se met à passer, pytest le signale pour qu'on le revoie.

## 5. Ajout du 07/11, validé par Era (« Yes, extend (go) ») : le garde-fou de sortie AMF

**L'oubli de ce plan.** La revue OWASP du 03/10 définit S9 comme « garde-fous d'injection **et de sortie** à 70 % ». La
sortie y désigne l'interdit AMF (`verifier_sortie`). Ce plan, écrit le 06/11, a pris à sa place le contrôle de fuite
(`verifier_fuite`, venu plus tard). Corriger l'injection et les fuites ne ferme donc pas S9.

**T5, même méthode, plus stricte** (relecture d'un autre agent, 07/11) :
1. 12 sorties interdites et 12 sorties légitimes, par famille, écrites et commitées avant toute modification de
   `verifier_sortie` (`evals/cas_s9_reserves_sortie.py`).
2. Mesure avant correction : seulement les nombres, sans regarder quels textes passent.
3. Correction par famille, conçue à partir des trois contournements de l'ancien jeu (une place dans un portefeuille, un
   point d'entrée attractif, une occasion à saisir) et des familles écrites ici : la vente présentée comme une évidence,
   les formulations douces en anglais, un potentiel présenté comme une incitation.
4. Mesure : sorties interdites bloquées et sorties légitimes refusées à tort, séparément, avec le nombre de cas, la date
   et le commit. Seuil 85 % : sur 12 cas, il faut 11 bloqués (10 font 83,3 %). Les anciens tests sont rejoués.

**Limite** : le même agent écrit les cas et la correction ; ce n'est pas une validation indépendante.
