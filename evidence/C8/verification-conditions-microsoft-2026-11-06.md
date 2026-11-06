# Conditions de Microsoft relues pour le service retenu (C8.2), 6 novembre 2026

**Pourquoi cette preuve.** Le registre RGPD laissait trois points ouverts sur Azure (`db/RGPD-registre-des-traitements.md`,
§ 5, lignes 6, 8 et 12) : relire les conditions de Microsoft, lire les cas de transfert hors de la frontière de données de
l'Union européenne, connaître la conservation de l'échantillon gardé pour la surveillance des abus. La règle du projet
est « aucune donnée personnelle hors de l'Union européenne » (registre, § 0). Cette note dit ce que Microsoft écrit, page
par page, et ce que cela change pour RITA. Elle ne remplace pas une lecture juridique complète du contrat.

**Ce qui a été lu, le 06/11/2026** (liens vérifiés, réponse 200) :

| Page de Microsoft | Date de la page | Lien |
|---|---|---|
| Données, confidentialité et sécurité des modèles vendus par Azure dans Foundry | 18/05/2026 | <https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy> |
| Surveillance des abus des modèles vendus par Azure | 13/05/2026 | <https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/abuse-monitoring> |
| Qu'est-ce que l'EU Data Boundary ? | 21/07/2026 | <https://learn.microsoft.com/en-us/privacy/eudb/eu-data-boundary-learn> |
| Transferts maintenus pour tous les services de l'EU Data Boundary | 04/11/2026 | <https://learn.microsoft.com/en-us/privacy/eudb/eu-data-boundary-transfers-for-all-services> |

**Ce qui n'a pas été lu en entier** : l'addendum de protection des données (DPA) et les conditions des produits de
Microsoft, auxquels la première page renvoie. Les constats ci-dessous viennent des pages de documentation, pas du contrat.

## Ce que Microsoft écrit, question par question

| Question | Ce que dit Microsoft | Page |
|---|---|---|
| Les requêtes servent-elles à entraîner un modèle ? | Non : ni à entraîner ni à améliorer les modèles de base, ni transmises à OpenAI ou à d'autres clients | données et confidentialité |
| Où sont traitées les requêtes d'un déploiement « DataZone » ? | Pour une ressource située dans un État membre de l'Union, dans cet État ou dans un autre État membre | données et confidentialité |
| Où sont stockées les données au repos ? | Dans la géographie choisie par le client, y compris l'échantillon de la surveillance des abus | données et confidentialité |
| Qui peut relire un échantillon signalé ? | Des employés autorisés de Microsoft, seulement sur un contenu signalé ; pour un déploiement dans l'Espace économique européen, ces employés sont situés dans l'Espace économique européen | surveillance des abus |
| Combien de temps l'échantillon est-il gardé ? | **Non indiqué** sur les deux pages relues | surveillance des abus, données et confidentialité |
| Peut-on supprimer ce stockage ? | Oui, sur demande acceptée (« surveillance modifiée »), réservée aux clients qui remplissent des critères d'accès limité ; **non demandée** pour RITA | surveillance des abus |
| Des données sortent-elles quand même de la frontière européenne ? | **Oui, dans des cas que Microsoft décrit** : accès à distance de son personnel depuis l'extérieur, rare et contrôlé, que Microsoft qualifie lui-même de transfert au sens du droit européen ; opérations de sécurité, sur des journaux pseudonymisés et, rarement, des données client ; acheminement réseau qui peut passer par l'extérieur | transferts maintenus |
| Peut-on encadrer l'accès du personnel ? | Microsoft cite le Customer Lockbox, qui demande l'accord explicite du client avant un accès aux données ; **non configuré pour RITA**, et son coût et ses conditions ne sont pas vérifiés | transferts maintenus |

## Ce que cela change pour RITA

**Ce qui dépend de RITA est conforme à la règle.** Le déploiement est en DataZoneStandard sur une ressource en Suède
(capture du portail du 06/11 : emplacement `swedencentral`), trois appels du 09/10 ont été servis en Sweden Central
(`evidence/C8/preuve-deploiement-zone-eu-2026-10-09.md`), et depuis le 31/10 aucun repli hors de l'Union n'est appelé
par défaut (`src/llm.py`, ordre `foundry`).

**Ce que le fournisseur se réserve ne l'est pas entièrement.** Microsoft documente lui-même des cas rares de sortie de
la frontière européenne, dont l'accès à distance de son personnel, qu'il qualifie de transfert. Le CEPD retient la même
lecture (lignes directrices 05/2021, § 9, cité au registre). La règle « UE seule », appliquée à la lettre, n'est donc pas
garantie par Azure : c'est un écart résiduel, du côté du fournisseur, documenté par lui.

**Les options, à décider par Era** : accepter cet écart résiduel en l'écrivant, jusqu'à l'arrêt d'Azure prévu après le
02/12 ; étudier le Customer Lockbox ; ou retenir un autre fournisseur, dont le contrat serait lu de la même façon.

**Restent ouverts** : la durée de conservation de l'échantillon des abus ; la lecture complète du DPA.

## 📖 Glossaire

- **DataZoneStandard** : type de déploiement d'Azure dont les requêtes sont traitées dans une zone de données (ici
  l'Union européenne), sans sortir de cette zone pour le traitement.
- **EU Data Boundary** (frontière de données de l'Union européenne) : engagement de Microsoft de stocker et de traiter
  les données de ses services en ligne dans les pays de l'Union et de l'AELE, sauf exceptions qu'il publie.
- **Surveillance des abus** : contrôle par Microsoft des usages contraires à son code de conduite ; un échantillon
  signalé peut être gardé et relu.
- **Surveillance modifiée** : régime sur demande où Microsoft ne garde pas cet échantillon et ne le fait pas relire.
- **Customer Lockbox** : service de Microsoft qui demande l'accord du client avant tout accès de son personnel aux
  données.
- **DPA** (Data Protection Addendum) : l'avenant contractuel de Microsoft sur la protection des données.
- **Transfert** : au sens du RGPD et du CEPD, toute mise à disposition de données hors de l'Union, y compris un accès à
  distance depuis un pays tiers.
