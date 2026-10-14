# Preuve C10 : le troisième écran, le briefing, appelle le modèle par l'API (03/10/2026)

> Livrables E3 (C10, intégrer l'API dans une application) et E4 (C17, composants et interfaces). Jusqu'au 03/10 au
> soir, `/briefing`, le seul point de terminaison qui expose le modèle (C9), ne se demandait que par `curl`, la
> passerelle MCP ou la documentation interactive : le rapport E3 v1.0 le déclarait comme premier manque de C10.
> Décision d'Era le 03/10 (« do it »), construit test d'abord dans la nuit.

## 1. Le récit utilisateur (US-3), tel qu'il a guidé l'écran

*En tant qu'investisseur particulier qui suit sept positions, je veux demander un briefing rédigé sur une valeur en
tapant son code, pour lire en français ce qu'elle a fait et ce qu'en disent les articles, sans jamais recevoir de
conseil d'achat ou de vente.*

Critères d'acceptation, chacun tenu par un test nommé :

| Critère | Test |
|---|---|
| Je saisis ma clé une fois ; elle vaut pour les trois écrans et disparaît à la fermeture de l'onglet | `test_aucune_cle_d_api_dans_le_code_de_l_ecran_briefing`, `test_la_cle_n_est_pas_stockee_durablement` |
| Je choisis la valeur dans la liste de l'univers suivi, ou je tape son code | liste `datalist` remplie depuis `/donnees/valeurs` (111 valeurs le 03/10) ; saisie libre conservée |
| Pendant la rédaction, l'écran me dit qu'il travaille et combien de temps | `test_l_ecran_briefing_dit_que_la_redaction_prend_du_temps` (zone `aria-live`) |
| Le texte s'affiche en paragraphes lisibles, sans code venu du modèle | `test_le_texte_du_modele_est_rendu_en_paragraphes_sans_html`, `test_l_ecran_briefing_n_utilise_jamais_innerhtml` |
| Je vois si le garde-fou a retenu le texte, en mots, pas seulement en couleur | `test_le_verdict_du_garde_fou_est_dit_en_texte_pas_seulement_en_couleur` |
| Un code inconnu est dit introuvable ; une clé refusée est redemandée | `test_un_ticker_inconnu_est_dit_en_clair_et_une_cle_refusee_est_oubliee`, `test_l_ecran_briefing_dit_quand_le_ticker_est_introuvable` (navigateur) |
| Je peux citer une référence si quelque chose cloche | `test_l_identifiant_de_requete_est_montre_pour_le_support` (`X-Request-ID`, le même que dans le journal et la trace) |
| Les trois écrans se relient, la page courante est marquée | `test_les_trois_ecrans_se_relient`, marqueurs RGAA |

Quatre états, comme les deux autres écrans : connexion, demande, chargement ou erreur, résultat. Le résultat reçoit
le focus à l'arrivée du texte : une personne au clavier ou au lecteur d'écran sait que c'est prêt.

## 2. Test d'abord, puis le code

17 tests statiques (`tests/test_frontend.py`) et 2 tests dans un vrai navigateur (`tests/test_smoke_ui.py`, Chrome,
`/briefing` intercepté par Playwright : **aucun appel payant** dans la suite). Rouges d'abord, les fichiers
n'existant pas ; puis `frontend/briefing.html`, `frontend/briefing.js` et un lien dans les deux autres écrans.

```
tests/test_frontend.py : 72 passed      (55 avant l'écran 3)
tests/test_smoke_ui.py : 7 passed       (5 avant)
```

Un accroc d'outillage, pas de code : le motif d'interception `**/briefing*` attrapait aussi `briefing.html` et
`briefing.js`, et la page recevait du JSON à leur place ; motif resserré à `**/briefing?ticker=*`.

## 3. Un briefing réel à l'écran

API réelle démarrée sur le poste, clé lue par l'application, Chrome piloté par Playwright, MC.PA demandé :

```
options de la liste deroulante : 111
briefing affiche en 11.2 s | paragraphes : 3
donnees : MC.PA — cours 378,55 EUR, variation sur une séance -0,25 %
verdict : Texte conforme : aucune recommandation d'achat ou de vente détectée.
reference : Référence de la requête : 6633e3f970384737a5c753deb2ef5cec
focus sur le resultat : resultat
erreurs JS : []
```

Capture : `ecran-briefing-2026-10-03.png`. La référence affichée est celle de la trace Langfuse et de la ligne de
journal de la même requête : c'est le chemin de la démonstration de l'oral E3 (l'écran, puis la trace par sa référence).

## 4. Ce que l'écran ne fait pas, dit tel quel

- Il ne met rien en cache : chaque demande est un appel payant au modèle (de l'ordre de 0,005 USD, banc C7).
- Il ne propose pas d'historique des briefings : la mémoire M4 est abandonnée pour la V1 (décision du 02/10).
- La passerelle MCP n'a pas d'outil de briefing : ses trois outils restent en lecture seule sur les données, par
  choix, tant qu'aucune politique de coût n'encadre un outil qui déclenche un appel payant.
- Sur le poste de démonstration, un seul fournisseur de modèle répond ; s'il tombe, l'écran dit « aucun fournisseur
  ne répond », il ne ment pas.
- Le récit utilisateur ci-dessus a été écrit avec l'écran, pas avant lui ; l'écran 2 n'en a toujours pas (carte #24).
