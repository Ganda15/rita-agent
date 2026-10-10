# Preuve C8 : premiers vrais briefings servis par Mistral, choix du modèle (10/10/2026)

Branche `mistral-ue` (carte #82, PR #88). Constituée le soir même, au fil de l'eau.

## Pourquoi cette mesure

Jusqu'ici, Mistral n'avait répondu qu'à deux sondes d'un mot (« OK », 0,53 s le matin, 0,61 s le soir avec la clé
neuve). Les tests de `tests/test_llm.py` remplacent le réseau par une doublure : ils prouvent la logique de la cascade,
pas la qualité du texte. Il fallait voir de vrais briefings de Mistral avant de fusionner la PR #88, et savoir si le
modèle du code (`mistral-large-2512`, Large 3) convient. Décision d'Era : GPT-5.4 (Azure, gratuit pour le projet) sert
aux essais de tous les jours ; Mistral sert quand une preuve de qualité, de coût, de latence et de traçage est utile.

## Méthode

- Route réelle `POST /briefing?ticker=MC.PA`, appelée dans le processus par le client de test de FastAPI : clé d'API,
  garde-fou d'entrée, graphe scout, rag, rédacteur, garde-fou AMF de sortie, trace Langfuse.
- Un seul fournisseur par passage (`LLM_ORDRE=mistral` ou `foundry`) : aucun repli ne peut masquer un échec.
- Pour essayer un autre modèle Mistral, seule la variable `MISTRAL_MODEL` change, le temps du passage.
- Un espion autour de `_appel_<fournisseur>` relève les jetons, la durée de l'appel, le modèle et l'origine.
- Même valeur, mêmes données, dans la même heure : le prompt d'Azure et celui du dernier passage Mistral sont
  identiques octet pour octet (`cmp`). Le prompt complet est en annexe.
- Pour Large 4, deux appels directs (hors RITA, même prompt, même limite de 500 jetons) ont d'abord testé le réglage
  `reasoning_effort` documenté par Mistral ; puis le code a été changé, test d'abord, et un briefing a été servi par la
  route avec le nouveau code.
- Valeur de démonstration du projet (MC.PA). Les deux fournisseurs sont dans l'UE : Mistral par `api.eu.mistral.ai`,
  Azure en Data Zone EU (origine mesurée : Sweden Central).

## Résultats

| Passage | HTTP | Appel au modèle | Route entière | Jetons entrée / sortie | Coût du briefing | Garde-fou AMF |
|---|---|---|---|---|---|---|
| Large 3 `mistral-large-2512`, par la route | 200 | 4,04 s | 7,93 s | 837 / 248 | 0,079 centime ; **0 dans Langfuse** | conforme |
| Azure `gpt-5.4`, par la route (référence) | 200 | 2,99 s | 5,44 s | 768 / 209 | 0,51 centime au prix catalogue (Langfuse) ; 0 € pour le projet | conforme |
| Medium 3.5 `mistral-medium-2604`, par la route | 200 | **1,31 s** | 3,51 s | 849 / 155 | 0,24 centime | conforme |
| Large 4 `mistral-large-4`, réglage par défaut, par la route | **500** | 20,48 s | 25,38 s | 749 / 500 (limite atteinte) | non calculé | non atteint |
| Large 4 `mistral-large-4-0`, réflexion coupée, appel direct 1 | 200 | 2,63 s | sans objet | 749 / 178 | 0,088 centime | conforme |
| Large 4 `mistral-large-4-0`, réflexion coupée, appel direct 2 | 200 | 3,73 s | sans objet | 749 / 232 | 0,099 centime | conforme |
| **Large 4, nouveau code, par la route** | 200 | **3,09 s** | 5,50 s | 749 / 237 | **0,10 centime** ; **0 dans Langfuse** | conforme |

Prix officiels lus le 10/10/2026 sur https://docs.mistral.ai/models/pricing, en dollars par million de jetons
(entrée / sortie) : Large 4 `mistral-large-4-0` 0,68 / 2,09 (prix soldé, prix normal 1,36 / 4,18, aucune date de fin
indiquée), Large 3 0,5 / 1,5, Medium 3.5 1,5 / 7,5, Small 4 0,15 / 0,6. Les coûts du tableau sont calculés avec ces prix et
les jetons mesurés ; au prix normal, un briefing Large 4 coûterait environ 0,2 centime.

Identifiants (journal et Langfuse) : Large 3 `d5cf1ebfb8414645903533dca70fce90` (trace `8d0c9d90817055dd13a74f88bf732932`),
Azure `f8fab692968042f39320a262df607a81` (trace `925db5adc04dc2c9cf8f09d350330b01`), Medium 3.5
`b2104ffafd0843b3b0e80c112b319379`, Large 4 par défaut `0f2da6f3bf8f4990bfbecb7731512e36`, Large 4 nouveau code
`223384bb05af492c81d4c14a034a60f2` (trace `e55c13e2151b647bec57bea094cc2863`). L'identifiant de trace est dérivé de celui
de la requête (`src/traces.py`, `create_trace_id(seed=request_id)`).

## Les textes, relus contre les règles du prompt

**Large 3** (texte rendu tel quel) :

> **Briefing sur LVMH (MC.PA) – Séance du 27 septembre 2026**
>
> L'action LVMH a clôturé en léger repli à 380,00 €, enregistrant une baisse modérée de 0,24 % sur la séance. La
> performance récente reste contrastée, avec une progression de 0,38 % sur une semaine, mais un recul marqué de 7,60 % sur
> un mois et de près de 40 % depuis le début de l'année. Le titre évolue sous ses moyennes mobiles à 20 séances
> (395,43 €) et 50 séances (430,54 €), tandis que le RSI 14 à 30,5 suggère une dynamique technique affaiblie.
>
> À surveiller pour la prochaine séance : l'impact potentiel des récentes tensions sur la demande chinoise, évoquées dans
> une analyse de *BFM Bourse* (28 juillet 2026), qui pèsent sur le segment mode et maroquinerie. Aucune actualité récente
> ne contredit cette tendance.

- ❌ **Date inventée** : le prompt ne donne aucune date de séance (seulement « Fraîcheur de la donnée : 1 jour(s) »).
  Le 27/09/2026 est un dimanche. Règle enfreinte : « Pas d'invention de chiffres ou d'événements non fournis ».
- ❌ Un article du 28/07 devient des « récentes tensions » : le prompt interdit de présenter une dépêche ancienne comme
  une actualité.
- ❌ « Aucune actualité récente ne contredit cette tendance » n'est soutenu par aucun article, et l'article le plus
  récent (24/09, Christian Dior +16 %) est ignoré.
- ⚠️ « Baisse modérée » pour -0,24 % ; le RSI est interprété (« dynamique affaiblie ») alors que le prompt demande de le
  citer comme une mesure. Ce n'est pas une recommandation : le garde-fou AMF passe.
- ✅ Tous les chiffres repris sont exacts ; la source et la date de l'article sont citées.

**Medium 3.5** :

> **Briefing MC.PA (LVMH) – 24/09/2026**
>
> L'action LVMH (MC.PA) a clôturé à 380,00 €, en léger recul de -0,24 % sur la séance, une variation modérée. Sur un an,
> la performance reste négative (-30,34 %), avec un drawdown maximal de -41,00 %. À surveiller : l'impact potentiel de
> l'annonce récente concernant le changement de structure technique du groupe (source : *tradingsat.com*, 24/09/2026), qui
> avait déjà suscité une forte réaction sur Christian Dior (+16 %).

- ❌ La date du titre est celle de l'article 3, pas celle de la séance (fraîcheur 1 jour, donc la séance du 09/10).
- ⚠️ « Variation modérée » pour -0,24 % ; un article vieux de 16 jours appelé « annonce récente ».
- ✅ Chiffres exacts, source et date citées, l'article le plus récent est celui retenu ; le plus rapide, mais trois fois
  plus cher que Large 4.

**Large 4, réflexion coupée, nouveau code, par la route** :

> **Briefing LVMH (MC.PA) — Séance du jour**
>
> L'action LVMH a clôturé à 380,00 EUR, en repli de 0,24 % sur la séance, une variation que l'on peut qualifier de
> faible. Sur le plan technique, le titre évolue sous ses moyennes mobiles 20 séances (395,43 EUR) et 50 séances
> (430,54 EUR), avec un RSI 14 à 30,5, ce qui traduit une pression vendeuse persistante depuis plusieurs semaines. La
> performance depuis le début de l'année s'établit à -39,83 %, dans un contexte de volatilité annualisée de 21,34 %.
>
> **Point à surveiller :** le comportement du titre autour du seuil des 380 EUR, niveau de clôture du jour, alors que la
> dernière actualité sectorielle citée — un article de BFM Bourse du 28 juillet 2026 évoquant des marges surprenantes mais
> une croissance de la mode-maroquinerie jugée insuffisante et une demande chinoise stagnante — date de plusieurs mois et
> ne reflète pas nécessairement les anticipations actuelles du marché.

- ✅ Aucune date inventée, niveau de variation juste (« faible »), chiffres exacts, et l'article de juillet est dit
  « daté de plusieurs mois » : la règle sur les dépêches anciennes est respectée.
- ⚠️ L'article le plus récent (24/09) est ignoré ; le RSI est interprété (« pression vendeuse persistante depuis
  plusieurs semaines ») ; « séance du jour » alors que la donnée a un jour.

**Azure GPT-5.4** (référence) :

> MC.PA a clôturé à 380,0 EUR, en baisse de 0,24% sur la dernière séance, un repli de faible ampleur dans un contexte où
> le titre reste nettement en retrait sur des horizons plus longs (-7,60% sur un mois, -39,83% depuis le 1er janvier). Les
> capitaux échangés en moyenne sur 20 séances atteignent 248,1 M EUR, ce qui témoigne d'une activité de marché soutenue
> sans préjuger de la séance du jour. D'un point de vue factuel, le cours demeure sous ses moyennes mobiles à 20 séances
> (395,43 EUR) et 50 séances (430,54 EUR), tandis que le RSI 14 s'établit à 30,5. Pour la prochaine séance, le point à
> surveiller sera la capacité du titre à se maintenir autour de 380 EUR, dans un environnement où la valeur reste proche
> de ses plus bas relatifs sur un an.

- ✅ Aucune date inventée, niveau de variation juste, chiffres exacts, capitaux moyens présentés comme une moyenne.
- ⚠️ Aucun des trois articles n'est utilisé ; « activité soutenue » est une interprétation légère.

**Large 4 avec son réglage par défaut** : modèle à raisonnement. Sa réponse est une liste de blocs dont le premier est
une réflexion ; avec la limite de 500 jetons du rédacteur, la réflexion consomme tout et il n'y a pas de texte. La liste
faisait échouer le garde-fou : 500, sans repli vers le fournisseur suivant. Relancé seul avec 1 500 jetons : 23,2 s,
arrêt sur la limite, une réflexion de 5 480 caractères, toujours aucun texte. Avec `reasoning_effort: "none"` (page
officielle https://docs.mistral.ai/en/studio-api/conversations/reasoning : `mistral-large-4-0` accepte ce réglage, la
réponse redevient une chaîne), il répond en 2,6 à 3,7 s.

## Ce qui a changé dans le code, test d'abord

- `src/llm.py` : modèle Mistral par défaut `mistral-large-4-0` ; l'appel envoie `reasoning_effort: "none"` ; une réponse
  en blocs ne garde que les blocs de texte, et sans texte lève `ValueError`, ce qui fait passer la cascade au suivant au
  lieu d'un 500 dans le garde-fou (`_texte_mistral`).
- `tests/test_llm.py` : trois tests nouveaux (réflexion coupée demandée, blocs réduits au texte, réponse sans texte =
  indisponibilité), deux tests mis au nouveau modèle par défaut. Rouges d'abord (5 échecs pour la raison attendue), puis
  verts.
- `evals/benchmark_fournisseurs.py` : prix cité de Large 4, test mis à jour d'abord.
- Suite complète : **847 passed**, 2 skipped, 2 xfailed (844 avant les trois tests nouveaux).

## Ce que la mesure apprend

1. **Large 4 sans réflexion remplace Large 3** (décision d'Era, 10/10) : sur ce passage, il n'invente pas de date et
   nomme bien le niveau de variation, pour un coût voisin (0,10 contre 0,08 centime). Medium 3.5 est plus rapide mais
   trois fois plus cher, avec le même défaut de date que Large 3.
2. **Le prompt ne donne pas la date de la séance**, et deux modèles Mistral sur quatre en ont mis une, fausse, dans le
   titre. Donner la date dans le prompt (`agents/analyst.py`) ôte la tentation à tous les modèles. Après le gel, test
   d'abord.
3. **Langfuse compte 0 $ pour Mistral** (Large 3 comme Large 4) : il ne connaît pas leur prix. Le même manque existait
   pour OpenRouter. À déclarer dans Langfuse avec le prix cité (C11, C20).
4. **Aucun modèle n'utilise bien les trois articles** : l'article le plus récent (24/09) n'est repris que par Medium 3.5.

## Limites

Une valeur, un à deux passages par modèle, dans la même heure : ce n'est pas une mesure statistique. La qualité est
relue à la main contre les règles du prompt, pas notée par une grille. Le prix de Large 4 est un prix soldé sans date de
fin. Le banc C7 (10 valeurs, notes de français, indicateurs cités, même grille que le 03/10) reste à passer.

## Suite proposée

Après le gel du 15/10 : date de séance dans le prompt (test d'abord), prix de Mistral déclaré dans Langfuse, banc C7
entre Azure et Large 4 (et Medium 3.5 ou Small 4 si utile), puis la question de l'ordre de la cascade (Azure d'abord,
gratuit, ou Mistral d'abord) tranchée sur ces chiffres.

## Annexe : le prompt reçu par les modèles qui ont répondu

```
Tu es un analyste financier français qui rédige des briefings courts pour des investisseurs particuliers.

Données de la dernière séance collectée :
- Action : MC.PA
- Cours de clôture : 380.0 EUR
- Variation sur 1 jour : -0.24% (baisse)
- Capitaux échangés en moyenne par séance sur 20 séances : 248,142,373 EUR
- Fraîcheur de la donnée : 1 jour(s)

Indicateurs calculés sur l'historique, à la dernière séance collectée (10 autres ; avec le cours, la variation du jour et les capitaux moyens, les 13 calculés par RITA) :
- Performance sur 1 semaine : +0,38 %
- Performance sur 1 mois : -7,60 %
- Performance depuis le 1er janvier : -39,83 %
- Performance sur 1 an : -30,34 %
- Moyenne mobile 20 séances : 395.43 EUR
- Moyenne mobile 50 séances : 430.54 EUR
- Distance au plus haut sur 1 an : -40,98 %
- Volatilité annualisée : 21,34 %
- Drawdown maximal sur 1 an : -41,00 %
- RSI 14 : 30.5
Ces indicateurs sont des faits à décrire, jamais des signaux : ne tire d'aucun d'eux une recommandation d'achat ou de vente, ni un pronostic ; un RSI ou une moyenne mobile se citent comme des mesures, sans dire ce qu'il faudrait faire.

Articles retrouvés (3) — classés par PERTINENCE, pas par date : vérifie leur date avant de t'en servir, et ne présente jamais une dépêche ancienne comme une actualité du jour. Quand tu t'appuies sur l'un d'eux, cite la source et la date. Chaque affirmation tirée des articles doit être soutenue par l'un des articles ci-dessous ; si deux articles se contredisent, dis-le au lieu de choisir en silence :
1. [BFM Bourse, 2026-01-28T09:00:00+01:00] Lvmh : L'activité de la mode et maroquinerie de LVMH laisse la Bourse sur sa faim, l'action chute de 7% - BFM Bourse
2. [BFM Bourse, 2026-07-28T09:00:00+02:00] Lvmh : Les marges de LVMH surprennent mais la croissance de la mode et maroquinerie est trop juste et la demande chinoise stagne, l'action est dans le rouge - BFM Bourse
3. [tradingsat.com, 2026-09-24T12:21:06+02:00] Lvmh : Christian Dior s'envole de 16%, pourquoi la Bourse s'enflamme pour le changement de structure très technique de LVMH - tradingsat.com

Rédige un briefing de 3 à 5 phrases en français qui :
1. Résume la performance du jour avec un ton factuel
2. Indique le niveau de variation (faible / modérée / forte)
3. Signale un point à surveiller pour la séance suivante

Règles strictes :
- AUCUNE recommandation d'achat ou de vente
- Pas d'invention de chiffres ou d'événements non fournis
- Ne présente JAMAIS ces capitaux moyens ni comme un volume du jour, ni comme un nombre de titres
- Ton neutre, professionnel, accessible
```

## 📖 Glossaire

- **Jeton** : unité de texte comptée par le fournisseur (environ trois quarts de mot) ; le prix se calcule en jetons.
- **Latence** : temps entre la demande et la réponse. « Appel au modèle » : le seul échange avec le fournisseur ;
  « route entière » : tout le briefing, données et garde-fous compris.
- **Trace** : l'enregistrement d'un briefing dans Langfuse, avec ses étapes, ses jetons et son coût.
- **Garde-fou AMF** : contrôle de sortie qui refuse tout texte ressemblant à une recommandation d'achat ou de vente.
- **Modèle à raisonnement** : modèle qui écrit d'abord une réflexion avant sa réponse ; plus lent, plus coûteux.
- **`reasoning_effort`** : réglage de Mistral qui fixe la part de réflexion ; `"none"` la coupe presque entièrement.
- **Repli (cascade)** : si un fournisseur échoue, la cascade passe au suivant.
- **Doublure** : fausse fonction utilisée par un test à la place du réseau, pour tester la logique sans appel réel.
- **Fraîcheur de la donnée** : âge, en jours, de la dernière cotation collectée.
