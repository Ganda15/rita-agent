# C21 : Résoudre les incidents techniques

Créé le 25/08/2026. Livrable E5.

---

## Les 5 critères officiels, et où RITA en est

| # | Critère (texte officiel) | État | Pourquoi |
|---|---|---|---|
| 1 | Les causes du problème sont identifiées correctement | ✅ | chaque incident ci-dessous a une cause racine établie, pas une hypothèse, **sauf INC-010** (14/11) : la cause du 401 d'Azure n'est pas trouvée, la fiche le dit et liste ce qui trancherait |
| 2 | Le problème est reproduit en environnement de développement | ✅ | reproduit pour INC-001, 002 et 004 ; INC-003 s'est produit *en* développement |
| 3 | La procédure de débogage est documentée depuis l'outil de suivi | ✅ depuis le 27/09 | INC-005 : issues #47 à #53, débogage écrit au fil de l'eau. Avant : aucune issue (25/08). INC-006 (02/10) : pas d'issue, dit dans la fiche |
| 4 | La solution documentée explicite chaque étape de résolution | ✅ | c'est l'objet des fiches ci-dessous |
| 5 | La solution est versionnée Git (merge request) | ✅ depuis le 27/09 | INC-005 : PR #54 relue, fusionnée. Avant : commits directs (25/08). INC-006 : commit direct `7cf3ffd`, dit dans la fiche |

Bilan au 25/08 : 3 critères sur 5. Les deux manquants ne portaient pas sur la qualité de la
correction, mais sur le processus : tracer l'incident dans un outil, et faire passer le
correctif par une demande de fusion relue.

Bilan au 02/10 : 5 critères sur 5, une fois. INC-005 (27/09) a traversé toute la chaîne :
issues, branche, PR #54, post-mortem. INC-006 (02/10), trouvé et corrigé dans la même heure, est
passé en commit direct : la chaîne a été sautée, la fiche le dit. Un critère tenu une fois n'est pas
un critère acquis ; c'est la régularité qui prouve.

## Ce que je ne ferai pas : fabriquer la trace après coup

Il serait techniquement possible d'ouvrir aujourd'hui cinq issues et cinq pull requests datées
d'aujourd'hui pour des incidents d'août. Je ne le fais pas.

C'est exactement la faute que ce dépôt refuse ailleurs, mot pour mot :

> *« ⚠️ Jamais reconstitué après coup. Un registre rempli d'un bloc la veille du rendu se repère
> immédiatement : les dates ne collent plus avec les notes qu'il prétend accompagner. »*
> Source : `docs/veille/_JOURNAL-DES-ENVOIS.md`

Une issue ouverte et fermée dans la même minute, deux mois après le fait, ne trompe personne et
détruit la crédibilité du reste du dossier. Les fiches ci-dessous disent donc la vérité : les
incidents sont réels et vérifiables dans Git, le processus de suivi ne l'était pas.

## Ce qui rend C21 complet : à installer maintenant, sans attendre octobre

Le prochain incident (il y en aura un) doit suivre la chaîne complète :

```
1. Ouvrir une ISSUE GitHub dès la détection
   -> titre = le symptôme observé, pas la cause supposée
   -> y écrire le déroulé du débogage AU FIL DE L'EAU (critère 3)
2. Créer une BRANCHE  fix/<numero-issue>-<mot-cle>
3. Corriger + ajouter le TEST DE NON-RÉGRESSION dans la même branche
4. Ouvrir une PULL REQUEST qui referme l'issue (« Closes #12 »)  (critère 5)
5. Fusionner, puis remplir la fiche de post-mortem ici
```

Pourquoi l'installer tout de suite : ce critère ne se rattrape pas en le décidant, il faut
qu'un vrai incident traverse la chaîne. Plus la chaîne est posée tard, moins il reste
d'occasions qu'un incident réel survienne pour la remplir. *Même logique que C6 : c'est la
régularité qui prouve.*

## Les fiches

| Fiche | Incident | Commit | Nature |
|---|---|---|---|
| [INC-001](INC-001-cle-par-defaut.md) | Une clé d'API par défaut acceptait n'importe qui | `a4042b9` | Sécurité : OWASP API2 |
| [INC-002](INC-002-valeur-radiee.md) | Une valeur radiée faisait perdre tout son groupe d'import | `8df76ba` | Logique métier : `None` ≠ `NaN` |
| [INC-003](INC-003-base-perdue.md) | La base de données a disparu | *(reconstruction 16/08)* | Exploitation : perte de données |
| [INC-004](INC-004-controle-documente-mais-absent.md) | Des contrôles décrits dans la doc n'existaient pas dans le code | `c7c8811`, `a7a3dba` | Défaut récurrent : 5 occurrences |
| [INC-005](INC-005-archive-decalee-d-un-jour.md) | Dix ans de cotations datées un jour trop tôt, quatre défauts de place de cotation | `af783d7`, PR #54 | Qualité des données : première chaîne complète issue, PR, post-mortem |
| [INC-007](INC-007-ci-rouge-scout-base-reelle.md) | Dix pushs de suite avec la chaîne rouge, la suite étant verte sur le poste | `0e53ede` | Intégration continue : trouvé en recomptant les critères E4, pas par une alerte ; test qui dépendait de la machine ; commit direct |
| [INC-006](INC-006-tests-ecrivaient-en-production.md) | Douze générations de test dans le projet Langfuse de production | `7cf3ffd` | Observabilité : trouvé dans l'outil de surveillance, pas dans le code ; commit direct |
| [INC-008](INC-008-cles-mistral-dans-l-historique.md) | Deux vraies clés Mistral dans l'historique de `.env.example` (branche `mistral-ue`) | sprint 2, tâche 3 | Sécurité : trouvé par la première analyse de l'historique (gitleaks) ; clés révoquées, historique gardé, exceptions documentées |
| [INC-009](INC-009-retour-a-la-normale-ouvre-un-incident.md) | Un message de retour à la normale de Langfuse a ouvert un nouveau ticket d'incident (#137) | `a57dccb`, PR #171 | Chaîne d'alerte : trouvé en relisant les issues ouvertes pour E5 ; reproduit avant correctif dans un conteneur jetable (1 test rouge), 14 tests verts après ; débogage écrit dans l'issue |
| [INC-010](INC-010-azure-repond-401.md) | Azure répond 401 à la clé du serveur : briefings et questions en panne, livraisons refusées (#250) | `2dd385f`, PR #251, #254, #256 | Fournisseur du modèle : vu par le pré-test et l'alerte Langfuse, pas par la vigie ; contourné par Mistral en secours ; **cause non établie** (une panne mondiale de Microsoft 365 du 12 au 14/11 coïncide, mais la clé reçoit toujours 401 après l'annonce du rétablissement : hypothèse très peu probable) |

INC-004 est le plus important des quatre devant un jury. Ce n'est pas un simple bug : c'est un
mode de défaillance du projet lui-même, repéré dans le projet, avec une contre-mesure.

## Glossaire

| Terme | En clair |
|---|---|
| **Post-mortem** | Fiche écrite *après* un incident : ce qui s'est passé, pourquoi, comment on a corrigé, comment on empêche le retour |
| **Cause racine** (*root cause*) | La vraie origine, pas le symptôme. « L'API renvoie 500 » est un symptôme ; « la clé était absente » est une cause |
| **Test de non-régression** | Test écrit *pour* le bug corrigé : il échouerait si le bug revenait. C'est ce qui distingue une correction d'un rustinage |
| **Demande de fusion** (*merge request* / *pull request*) | Proposition de fusionner une branche, relisible et commentable avant intégration |
| **Outil de suivi** (*issue tracker*) | Registre des incidents (ici GitHub Issues) |
