# INC-010 : Azure répond 401 à la clé du serveur, briefings et questions en panne, livraisons refusées

| | |
|---|---|
| **Détecté le** | 13/11/2026, entre 19 h 16 et 19 h 20 UTC, par le **pré-test de la livraison** de #249 (refus sur `briefing` et `question`), puis à 19 h 30 UTC par l'**alerte Langfuse** « RITA : fournisseur en erreur », qui a ouvert l'issue #250 |
| **Sévérité** | P2 : briefings et questions indisponibles ; données, indicateurs et protection par clé en état de marche |
| **Durée** | service en panne du 13/11 vers 19 h UTC au 14/11 à 13 h 32 UTC (livraison de `2dd385f`, Mistral en secours) ; refus d'Azure du 13/11 vers 19 h UTC au 15/11 à 23 h 03 UTC au moins, Azure répondant de nouveau le 16/11 à 10 h 05 UTC au plus tard. **La cause, elle, n'est pas trouvée** |
| **Impact réel** | aucune donnée perdue ni faussée ; aucun texte de modèle servi à tort (une question en panne répond « indisponible ») ; toute livraison bloquée par le pré-test pendant la panne, la production restant sur `770d440` |
| **Commit du contournement** | `2dd385f` (livraison), PR #251, #254 et #256 |
| **Issue / demande de fusion** | issue #250 (ouverte par l'alerte, toujours ouverte) ; PR #251, #254, #256, puis #257 vers `main` |

## 1. Ce que j'ai vu (le symptôme, avant la cause)

Journal de l'API de production (heure UTC du serveur) :

```
2026-11-13 20:09:50,041 WARNING src.llm Fournisseur foundry indisponible pour une question : HTTPStatusError
2026-11-13 20:11:07,862 WARNING src.llm Fournisseur foundry indisponible : HTTPStatusError (HTTP 401)
2026-11-13 20:12:10,276 WARNING src.llm Fournisseur foundry indisponible : HTTPStatusError (HTTP 401)
```

La même clé, testée seule sur le serveur, hors de RITA (`curl` sur la liste des modèles d'Azure, seul le code de
réponse affiché) : **401**. Le 14/11 au matin, même test, même résultat ; et encore le 14/11 vers 17 h 20 UTC, après
l'annonce du rétablissement par Microsoft (section 4, hypothèse 5). Test du 15/11 à 23 h 03 UTC (16/11 à 0 h 03,
heure de Paris), même commande, sans que la clé ait été changée : **401**.

**Retour d'Azure, constaté le 16/11.** Un briefing réel est rédigé par Azure (`foundry`), HTTP 200, conforme au
garde-fou AMF :

```
2026-11-16 10:05:20,526 INFO src.llm Réponse obtenue via foundry
2026-11-16 10:05:21,244 INFO api.main briefing servi : request_id=97acd381f15d40a1b18978e90e6443c2 ticker='AC.PA' conforme_amf=True duree_ms=6904
```

Aucun appel au modèle entre le test du 15/11 à 23 h 03 UTC et ce briefing : l'heure exacte du retour n'est pas
connue, seulement cet intervalle. Je n'ai rien modifié côté Azure (portail, paiement, crédit, abonnement, clé).

Ce qui fonctionnait : `/health` (200), les données, les indicateurs. La vigie de 19 h 43 UTC n'a ouvert aucune issue.
Ce qu'elle regarde l'explique : elle sonde `/health`, qui n'appelle pas le modèle, puis lit les taux de `/sante`, qui
restent « inconnu » sous 5 requêtes en 15 minutes (`monitorage/seuils.json`). Je n'ai pas relevé les valeurs de
`/sante` à cette heure-là.

## 2. Cause racine : **non établie** (Azure répond de nouveau le 16/11)

Ce que je sais : un **401** veut dire que le service refuse l'authentification. Le code de RITA est hors de cause :
la clé, testée seule hors de RITA, reçoit le même refus. Ce qui reste possible se trouve côté compte Azure ou côté
Microsoft, et je n'ai pas pu le vérifier : le portail Azure ne s'ouvrait pas le 13/11 au soir.

**Une panne Microsoft le même jour, sans lien établi.** Une panne mondiale de Microsoft a commencé le jeudi 12/11 au
soir et duré jusqu'au 14/11 :

- Charente Libre, publié le 13/11 à 8 h 31 (heure de Paris), titre : panne géante chez Microsoft, Outlook
  inaccessible, ChatGPT et Claude également perturbés
  ([article](https://www.charentelibre.fr/sciences-et-technologie/web/panne-geante-chez-microsoft-outlook-inaccessible-chatgpt-et-claude-egalement-perturbes-des-milliers-d-utilisateurs-touches-31506599.php)).
  Je n'ai pu lire que son titre, sa date et son résumé.
- franceinfo, direct mis à jour le 13/11 à 23 h 34
  ([article](https://www.franceinfo.fr/internet/microsoft/direct-panne-mondiale-de-microsoft-des-resultats-positifs-en-matiere-de-stabilite-du-service-constates-par-le-geant-americain_8280665.html)) :
  services touchés Outlook, Teams et Copilot ; des erreurs de connexion ; cause donnée par Microsoft, un problème
  apparu lors d'une montée en capacité de son réseau, révélé par un changement récent, avec une forte charge dans
  plusieurs régions ; ni attaque ni lien avec l'IA selon Microsoft.
- Microsoft Q&A, fil ouvert le 12/11 à 18 h 02 UTC
  ([fil](https://learn.microsoft.com/en-us/answers/questions/6069133/is-microsoft-experiencing-an-outage)) :
  incidents Microsoft 365 MO1550821 et EX1550543 ; Exchange Online, Teams, SharePoint Online, Copilot, Defender XDR ;
  erreurs signalées : 503, délais dépassés, échecs de connexion ; « service rétabli » relayé le 14/11 par un membre de
  la communauté, pas par un employé de Microsoft.

**Pourquoi je n'en fais pas la cause** :

| Pour un lien | Contre un lien |
|---|---|
| la panne couvre la période du 401 (12/11 au soir, 14/11) | les services nommés sont ceux de **Microsoft 365** ; aucune des trois sources ne cite Azure, Azure AI Foundry, Azure OpenAI ni l'authentification par clé d'API |
| Microsoft parle d'un changement de réseau et d'une forte charge dans plusieurs régions | les erreurs décrites sont des **503**, des délais dépassés et des échecs de connexion, pas des **401** |
| | le 14/11 vers 17 h 20 UTC, après l'annonce du rétablissement, Azure refusait **encore** la clé (401) |

Le chevauchement dans le temps est réel ; le lien n'est pas prouvé, et les faits vont contre. Le test décisif est
fait : si la panne de Microsoft était la cause, la clé aurait dû répondre de nouveau une fois le service rétabli,
sans être changée. Elle reçoit toujours 401, encore le 15/11 à 23 h 03 UTC. **Je tiens donc cette hypothèse pour très peu probable** : la cause est
à chercher côté compte Azure.

**Ce que le retour du 16/11 écarte** : une clé régénérée. Le conteneur de l'API a démarré le 14/11 à 19 h 14 UTC et n'a
pas redémarré depuis (`docker inspect` : 0 redémarrage) ; il lit la clé dans son environnement, fixé au démarrage. Avec
cette clé, Azure a répondu 401 le 14/11 entre 19 h 15 et 19 h 23 UTC (quatre refus au journal, Mistral a répondu à chaque
fois), puis l'a acceptée le 16/11. Une clé régénérée ne redevient pas valide. Restent possibles l'abonnement, le crédit
ou une cause côté Microsoft, sans preuve pour l'une ou l'autre. **Ce qui trancherait encore** : (1) dans le portail Azure, le journal d'activité de la
ressource (clés régénérées ?), l'état de l'abonnement et le crédit, et Service Health pour l'abonnement ; (2) dans
Langfuse, l'heure du dernier appel réussi à Azure, que je n'ai pas relevée.

**Cause de conception, elle, établie** : RITA n'avait qu'un fournisseur pour les questions, et le pré-test de la
livraison exige un briefing et une question réels. Une panne du seul fournisseur bloquait donc à la fois le service
**et** toute livraison, y compris celle qui aurait apporté un secours.

## 3. Reproduction

En production : le test de la clé seule reproduisait le 401 à chaque essai, le 13/11, le 14/11 et le 15/11. Depuis
le 16/11, le refus ne se reproduit plus. En développement,
le refus d'Azure est simulé par les tests du secours (section 6) ; la cause, inconnue, ne peut pas l'être.

## 4. Procédure de débogage

| # | Hypothèse | Comment je l'ai testée | Résultat |
|---|---|---|---|
| 1 | Le code de RITA appelle mal Azure | la clé testée seule, hors de RITA | écartée : même 401 |
| 2 | Incident déclaré par Microsoft sur Azure | page publique d'état d'Azure, 13/11 à 20 h 40 UTC | aucun incident affiché |
| 3 | Panne passagère | nouveaux tests le 14/11 au matin et le 15/11 à 23 h 03 UTC | écartée : toujours 401 environ 52 heures après le premier refus |
| 4a | Clé régénérée | la clé du conteneur, inchangée depuis son démarrage le 14/11 à 19 h 14 UTC, refusée le 14/11, puis essayée de nouveau le 16/11 | **écartée** : acceptée le 16/11 ; une clé régénérée ne redevient pas valide |
| 4b | Abonnement suspendu ou crédit épuisé | portail Azure | **non testée** : le portail ne s'ouvrait pas le 13/11 ; rien modifié de mon côté avant le retour du 16/11 |
| 5 | Panne mondiale de Microsoft du 12 au 14/11 | trois sources lues le 14/11 (section 2), puis la clé testée de nouveau le 14/11 vers 17 h 20 UTC, après l'annonce du rétablissement | **très peu probable** : produits et types d'erreur différents, et toujours 401 une fois le service annoncé rétabli |

Le débogage n'a pas été écrit dans l'issue #250 au fil de l'eau : il l'a été dans `ETAT.md` et `CHANGELOG.md` (13/11
au soir et 14/11), puis ici le 14/11 ; complété le 16/11 avec le test du 15/11 à 23 h 03 UTC et le retour d'Azure du 16/11.

## 5. Contournement, étape par étape

La cause n'étant pas trouvée, je n'ai rien corrigé chez Azure : j'ai rendu RITA capable de servir sans lui.

1. **Mistral en secours d'Azure** (PR #251), pour les briefings et les questions, par son adresse européenne, après
   lecture de son contrat (`docs/lecture-contrat-mistral-2026-11-13.md`) et contrôle de la console (entraînement sur
   les données d'API et modèles Labs désactivés). Éteint par défaut ; allumé sur le serveur par
   `LLM_ORDRE=foundry,mistral` : Azure reste premier dès qu'il répond, sans autre livraison.
2. **Le déployeur écrit la raison d'un contrôle en échec** (PR #254) : la livraison suivante a été refusée avec une
   raison lisible, `CITATIONS_INVALIDES`, au lieu d'un échec muet.
3. **Consigne des citations précisée** (PR #256) : Mistral Large 3 omettait le numéro de l'extrait dans le texte ;
   0 réponse valide sur 6 avant, 8 sur 8 après (`evidence/C11/citations-mistral-2026-11-14/`).
4. Livraison de `2dd385f` le 14/11 à 13 h 32 UTC : pré-test, bascule et contrôle après bascule verts.

Deux obstacles sans lien avec Azure sont apparus pendant ces livraisons : le jeton du serveur pour l'image privée
avait expiré le 13/11 (renouvelé jusqu'au 31/12/2026) et le budget GitHub Packages était à 0 $ (CHANGELOG du 14/11).

## 6. Vérification et non-régression

Session de test du 14/11, juste après la livraison : 11 requêtes servies par Mistral, aucune erreur, toutes les
cartes du tableau de bord saines (`evidence/C20/session-test-2026-11-14/`).

**Tests de non-régression** :
- `tests/test_llm_mistral_secours.py::test_une_question_passe_a_mistral_quand_azure_refuse_la_cle`
- `tests/test_llm_mistral_secours.py::test_un_briefing_passe_a_mistral_quand_azure_refuse_la_cle`
- `tests/test_llm_mistral_secours.py::test_si_les_deux_refusent_la_question_est_indisponible_sans_texte`
- `tests/test_deployer_scenarios.py::test_un_refus_au_pretest_garde_la_raison_au_journal`

## 7. Ce que ça change pour la suite

- Un second fournisseur de l'UE, prêt et testé : la panne d'un seul ne bloque plus ni le service ni les livraisons.
- Le journal du déployeur dit pourquoi un contrôle échoue.
- **Limite** : la vigie n'a pas vu cette panne ; sur un trafic aussi faible, ses taux restaient « inconnu ». Ce sont
  le pré-test et l'alerte Langfuse qui l'ont vue. Je garde ce partage : une sonde qui appellerait le modèle à chaque
  passage coûterait des appels pour une information que Langfuse donne déjà.
- Azure répond de nouveau depuis le 16/11 (section 1) et reste premier ; Mistral reste en secours. Pour une demande
  servie par Azure, aucun appel de génération à Mistral n'est effectué.
- **Reste ouvert** : la cause du 401 (section 2, « ce qui trancherait encore »). L'issue #250 reste ouverte jusque-là. Pour ce critère, cet incident n'a **pas** de cause racine établie.
