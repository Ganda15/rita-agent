# C7 : prix publics et information environnementale des services comparés, relevés le 03/10/2026

> **Ce que ce fichier est** : le relevé, daté et sourcé, de ce que chaque service publie sur son prix et sur son
> empreinte, pour les deux fournisseurs mesurés par le banc du 03/10 (`preuve-benchmark-2026-10-03.md`, §9).
> Règle du plan C7 (§5) : un chiffre n'entre ici que s'il est publié par le fournisseur ou son hébergeur, avec sa date
> et son lien ; sinon on écrit **inconnu**. Aucune note d'éco-responsabilité n'est inventée.
>
> Chaque lien a été contrôlé le 03/10/2026 (`curl`, code 200). Les prix sont en dollars américains (USD) par million
> de jetons, tels que les fournisseurs les publient.

## 1. Les prix publics

| Service, modèle | Entrée | Entrée en cache | Sortie | Source, date |
|---|---|---|---|---|
| **Azure AI Foundry**, `gpt-5.4` (déploiement Standard Global, contexte jusqu'à 272 000 jetons) | **2,50** | 0,25 | **15,00** | billet Microsoft « Introducing GPT-5.4 in Microsoft Foundry », publié le 05/03/2026, modifié le 10/03/2026 : https://azure.microsoft.com/en-us/blog/introducing-gpt-5-4-in-microsoft-foundry/ ; réponse d'un modérateur Microsoft Q&A du 06/04/2026 : https://learn.microsoft.com/en-us/answers/questions/5841927/pricing-for-gpt-5-4-5-4-mini-5-4-nano |
| Azure AI Foundry, `gpt-5.4`, contexte au-delà de 272 000 jetons | 5,00 | 0,50 | 22,50 | même réponse Q&A du 06/04/2026 (sans objet pour RITA : 644 jetons d'entrée en moyenne) |
| OpenAI en direct, `gpt-5.4` (instantané par défaut `gpt-5.4-2026-03-05`, le même nom que celui renvoyé au banc) | 2,50 | 0,25 | 15,00 | fiche du modèle, lue le 03/10/2026 : https://developers.openai.com/api/docs/models/gpt-5.4 (fenêtre de 1 050 000 jetons, connaissances arrêtées au 31/08/2025) |
| **OpenRouter**, `anthropic/claude-sonnet-4.5` | **3,00** | non publié par l'API | **15,00** | API publique lue le 03/10/2026 : https://openrouter.ai/api/v1/models (le banc lit ce prix à chaque passage) ; page : https://openrouter.ai/anthropic/claude-sonnet-4.5 |
| OpenRouter, `openai/gpt-5.4` (non mesuré, pour situer) | 2,50 | | 15,00 | même API, même date ; page : https://openrouter.ai/openai/gpt-5.4 |

Deux observations à garder :

- La page de tarifs Azure OpenAI (https://azure.microsoft.com/en-us/pricing/details/azure-openai/) affichait le
  03/10/2026 une section « GPT 5.4 Series » avec des cases à `$-`, sans montant, et la mention que les prix sont des
  estimations en dollars. Le prix retenu vient donc du billet de lancement et de la réponse Q&A, pas de la page de tarifs.
- Sur OpenRouter, `claude-sonnet-4.5` est servi par sept points de sortie (Anthropic, Claude sur AWS, Amazon Bedrock,
  Azure global, Google Vertex global à 3,00 et 15,00 ; Bedrock `eu-west-1` et Vertex `us-east5` à 3,30 et 16,50), lus
  dans https://openrouter.ai/api/v1/models/anthropic/claude-sonnet-4.5/endpoints le 03/10/2026. Le script du banc ne
  conservait pas le point de sortie qui a servi chaque appel : le quatrième passage (30 appels) n'a pas d'origine. Depuis
  le soir du 03/10 le banc la journalise : sur 10 appels, **Amazon Bedrock** les a tous servis (preuve §10), région non nommée.

### Ce que ça donne pour le banc du 03/10, au prix public

Recalculé depuis les jetons bruts de `resultats-2026-10-03.jsonl` (30 appels par service) :

| Service | Jetons d'entrée | Jetons de sortie | Coût du passage au prix public | Coût d'un briefing | Facturé au projet |
|---|---|---|---|---|---|
| Foundry, `gpt-5.4` | 19 314 | 6 115 | **0,14 USD** | **0,0047 USD** | 0 (ressource d'Era) |
| OpenRouter, `claude-sonnet-4.5` | 23 904 | 7 302 | **0,18 USD** | **0,0060 USD** | 0,18 USD |

Lecture : au prix public, un briefing par `gpt-5.4` coûte environ 22 % de moins qu'un briefing par `claude-sonnet-4.5`.
L'écart vient surtout des jetons (deux découpages différents, et des textes un peu plus courts côté GPT), un peu du prix
d'entrée (2,50 contre 3,00) ; le prix de sortie est le même. Ce que le projet paie réellement est autre chose : la
ressource Foundry d'Era ne lui est pas facturée (ce qu'il a dit le 03/10 ; la nature de cette gratuité, crédits ou
offre, n'est pas écrite ici, Era la précisera). La recommandation de la preuve §9 repose sur le prix public, pas sur
la gratuité, pour rester vraie si elle s'arrête.

## 2. L'information environnementale, service par service

### 2.1 OpenAI, éditeur de `gpt-5.4` : un seul chiffre public, et pas pour ce modèle

OpenAI ne publie **aucune donnée par modèle** : rien pour `gpt-5.4` sur sa fiche, pas de rapport d'émissions. Le seul
chiffre public vient d'un billet de son dirigeant, « The Gentle Singularity » (https://blog.samaltman.com/the-gentle-singularity,
juin 2025 ; la page n'affiche pas de date) : une requête ChatGPT moyenne consommerait « environ 0,34 wattheure » et
« environ 0,000085 gallon d'eau » (0,32 millilitre). Sans méthode, sans modèle nommé, sans date de mesure. Ce chiffre
ne s'applique pas tel quel à un briefing RITA (environ 850 jetons, modèle de 2026).

Des estimations indépendantes vont beaucoup plus haut pour GPT-5 : un laboratoire universitaire (University of Rhode
Island, août 2025, rapporté par Tom's Hardware :
https://www.tomshardware.com/tech-industry/artificial-intelligence/chatgpt-5-power-consumption-could-be-as-much-as-eight-times-higher-than-gpt-4-research-institute-estimates-medium-sized-gpt-5-response-can-consume-up-to-40-watt-hours-of-electricity)
estime une réponse GPT-5 de taille moyenne à environ 18 Wh, jusqu'à 40 Wh. C'est une **estimation** (temps de
réponse multiplié par la puissance d'un serveur type), pas une mesure du fournisseur, et pas `gpt-5.4`.

**Verdict pour le critère : inconnu par modèle.** Ce qui existe est un ordre de grandeur contradictoire (0,34 à 18 Wh
par requête), à présenter comme tel.

### 2.2 Microsoft, hébergeur de Foundry : des chiffres d'entreprise datés, rien par requête

Microsoft publie un rapport environnemental annuel et une fiche de données vérifiée par un cabinet d'audit. Chiffres de
l'exercice FY25 (juillet 2024 à juin 2025), lus le 03/10/2026 dans la fiche
https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/msc/documents/presentations/CSR/2026-Microsoft-Environmental-Data-Fact-Sheet-PDF.pdf
et le rapport
https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/msc/documents/presentations/CSR/2026-Microsoft-Environmental-Sustainability-Report-PDF.pdf :

| Indicateur | FY20 (référence) | FY25 | Source |
|---|---|---|---|
| Émissions totales, scopes 1 + 2 + 3 (tonnes équivalent CO2, méthode GHG Protocol) | 13 061 000 | **21 121 000** (+62 %) | fiche, table 1A |
| Même total, « critères de la direction » (celui du suivi de l'objectif 2030) | 12 881 000 | 20 290 000 (+58 %) | fiche, table 1B |
| Électricité consommée (MWh), dont Europe, Moyen-Orient, Afrique | 10 770 714 (2 236 689) | 37 026 353 (9 975 755) | fiche, table 13 |
| Part d'électricité renouvelable directe | non suivi | **100 %** | fiche, table 6 |
| PUE moyen mondial des centres de données | | **1,17** | rapport, section efficacité |
| WUE moyen mondial | | 0,27 L/kWh | rapport, section eau |
| Objectif | | carbone négatif en 2030 | rapport |

Le rapport affirme aussi, sans nommer de modèle ni de méthode : « une inférence d'IA optimisée à grande échelle peut
consommer moins d'un wattheure par requête ». À lire comme une communication, pas comme une mesure de `gpt-5.4`.

**Le lieu de traitement, mesuré le 03/10 au soir : Sweden Central.** Chaque réponse d'Azure OpenAI porte un en-tête
`x-ms-region` qui nomme la région qui a traité l'appel. Une sonde (un appel de 5 jetons, même clé, même point que le
banc, clé jamais affichée) a renvoyé :

```
statut 200
x-ms-region = Sweden Central
x-ratelimit-limit-requests = 2500
x-ratelimit-limit-tokens = 250000
modele gpt-5.4-2026-03-05 | usage 11 4
```

Era situait sa ressource « France Central, Sweden Central ou West Europe » ; la mesure tranche pour la sonde. Les
30 appels du quatrième passage n'ont pas journalisé cet en-tête (le script ne le lisait pas). **Depuis, il le journalise** :
un passage séparé de 10 appels a donné `Sweden Central` 10 fois sur 10 (preuve §10), ce qui confirme la sonde sans
rien dire du quatrième passage, ni de demain. La fiche du modèle dans le portail (collée par Era le 03/10) donne
les limites du modèle : fenêtre de 1 050 000 jetons, entrée jusqu'à 922 000, **sortie jusqu'à 128 000**, cycle de vie
« Generally Available », entrées texte et image. Limites de débit de la ressource, lues dans les en-têtes : 2 500
requêtes et 250 000 jetons par fenêtre (l'en-tête ne dit pas la durée de la fenêtre ; la documentation Azure parle de
quotas par minute).

**Type de déploiement, lu par Era dans le portail Foundry le 03/10 au soir : Global Standard.** D'après la documentation
Microsoft (https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types, mise à jour du
12/08/2026), un déploiement **Global Standard** « peut être traité dans n'importe quelle région Azure » : Sweden Central
pour la sonde du 03/10, une autre région possible demain, au choix d'Azure. Conséquence pour la preuve : la région
n'est pas une propriété de la ressource, c'est le résultat d'un appel, et elle ne peut être connue que si le banc
journalise `x-ms-region` à chaque appel. Conséquence pour les données : les prompts (cours, indicateurs, extraits
d'actualité, aucune donnée personnelle) peuvent être traités hors de l'Union européenne ; un déploiement **Data Zone
EU** les garderait dans la frontière de données européenne, pour un prix publié plus élevé, et `gpt-5.4` n'a été lancé
qu'en Global Standard et Data Zone US. Sur l'énergie de la région suédoise, Microsoft communique sur une alimentation
en électricité sans carbone, mais ses pages régionales refusent la lecture automatique (code 403 le 03/10) : **aucun
chiffre régional n'est cité ici**, seuls les chiffres d'entreprise du tableau ci-dessus le sont.

### 2.3 Anthropic, éditeur de `claude-sonnet-4.5` : rien de publié

Vérifié le 03/10/2026 : https://www.anthropic.com/sustainability répond 404 ; la page de transparence
(https://www.anthropic.com/transparency) ne contient aucun chiffre d'énergie, d'eau ou d'émissions ; aucune recherche
web n'a trouvé de rapport d'émissions ni de chiffre par requête. **Inconnu.**

### 2.4 OpenRouter, fournisseur : un routeur, pas un hébergeur

OpenRouter ne publie rien sur l'environnement, et pour cause : il route vers sept points de sortie (§1). L'empreinte
d'un appel est celle de l'hébergeur qui l'a servi. Le banc le journalise depuis le 03/10 au soir : **Amazon Bedrock** sur
10 appels sur 10 (preuve §10), sans région. Les données d'Amazon (AWS) n'ont pas été relevées ici : **Inconnu**, à relever
si le jury demande l'empreinte du Claude d'OpenRouter.

## 3. Un ordre de grandeur, écrit comme une hypothèse

Pour donner une échelle au jury, pas une mesure : le banc du 03/10 a fait 60 appels. Avec le chiffre d'OpenAI pour une
requête moyenne (0,34 Wh), le passage pèse environ 20 Wh ; avec l'estimation universitaire pour GPT-5 (18 Wh), environ
1,1 kWh. Un briefing RITA se situe donc, selon l'hypothèse, entre un tiers de wattheure et une vingtaine de wattheures,
un facteur 50 d'incertitude. Aucun des deux fournisseurs ne permet de faire mieux aujourd'hui, et le fichier le dit
plutôt que de choisir un chiffre.

## 4. Ce que ça change pour C7

- **C7.5 (approche environnementale)** passe de « aucune donnée vérifiée » à « données d'hébergeur datées pour
  Microsoft ; rien par modèle chez les deux éditeurs, écrit comme inconnu ». Ce n'est pas un ✅ : le critère demande une
  approche, et l'approche honnête ici consiste à montrer l'absence de donnée et l'ordre de grandeur contradictoire.
- **Le coût (C7.4)** a maintenant un prix public pour les deux modèles ; la recommandation provisoire de la preuve §9
  (Foundry d'abord, OpenRouter en secours) tient au prix public comme en gratuité.
- **Fait le 03/10 au soir** : le banc journalise l'origine de chaque appel (région Azure, hébergeur OpenRouter), test
  d'abord ; première mesure : Sweden Central 10 sur 10 pour Foundry, Amazon Bedrock 10 sur 10 pour OpenRouter (preuve §10).
- **Restent inconnus**, et dits tels : l'origine des 60 appels du quatrième passage (non journalisée à l'époque), la région
  d'Amazon Bedrock, la variation de région dans le temps (déploiement Global Standard : un journal sur plusieurs jours),
  les limites de débit d'OpenRouter (non relevées), les données environnementales d'AWS, et toute empreinte par modèle.

## 📖 Glossaire

- **Jeton (token)** : unité de découpage du texte facturée par les fournisseurs ; un mot français fait souvent deux ou trois jetons.
- **Entrée en cache** : partie du prompt déjà vue par le fournisseur, facturée moins cher quand il la reconnaît.
- **Standard Global / Data Zone** : types de déploiement Azure ; le premier peut traiter la requête dans n'importe quelle région du monde, le second dans une zone (Union européenne, États-Unis, Asie-Pacifique).
- **Scopes 1, 2, 3** : catégories du protocole GHG ; émissions directes, émissions de l'électricité achetée, et tout le reste de la chaîne (fournisseurs, construction, usage).
- **PUE (Power Usage Effectiveness)** : énergie totale d'un centre de données divisée par l'énergie des serveurs ; 1,0 serait parfait.
- **WUE (Water Usage Effectiveness)** : litres d'eau consommés par kilowattheure de serveurs.
- **Wh (wattheure)** : énergie d'une puissance d'un watt pendant une heure ; un téléphone se recharge avec 10 à 20 Wh.
- **Point de sortie (endpoint)** : chez OpenRouter, l'hébergeur et la région qui exécutent réellement le modèle demandé.
