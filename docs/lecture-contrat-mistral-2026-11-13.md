# Lecture du contrat de Mistral AI : peut-il être le second fournisseur du modèle ?

13/11/2026, soir. Décision d'Era le 14/11 au matin : Mistral en secours d'Azure, briefings et questions (Azure toujours 401). Le code le permet, éteint par défaut ; les quatre vérifications du verdict restent à faire avant de l'allumer sur le serveur.

## Pourquoi maintenant

Le 13/11 vers 20 h, Azure a refusé l'authentification (HTTP 401) : briefings et questions en panne en production, et
livraison refusée au pré-test. Le plan B retenu par Era : Mistral en second fournisseur, Azure restant le premier.
Mistral est déjà codé (adresse européenne `api.eu.mistral.ai`, écrite dans le code), mais tenu hors de la cascade
« tant que son contrat n'est pas lu » (`src/llm.py:30`, PR #88). Cette fiche fait cette lecture.

La règle à respecter est le § 0 du registre (`db/RGPD-registre-des-traitements.md`, version du 06/11) : pour chaque
sous-traitant, identifier les exceptions de son contrat, vérifier leurs garanties, limiter les données envoyées.

## Ce que RITA enverrait à Mistral

- **Briefing (T6)** : le ticker demandé, le cours, la variation, les indicateurs, des passages de presse. Aucune
  position, aucun PRU, aucune quantité. Donnée personnelle possible : la valeur demandée, qui révèle un intérêt.
- **Question (T8)** : le texte tapé par l'utilisateur et des passages d'articles. Le texte libre peut contenir une
  donnée personnelle si l'utilisateur en écrit une.

## Ce que disent les textes de Mistral

| Point | Ce que disent les textes | Conséquence pour RITA |
|---|---|---|
| **Entraînement** | Conditions commerciales, § 4.2 (en vigueur le 25/09/2026) : pas d'entraînement sur les données ni les réponses du client, sauf exceptions : produit dont l'entraînement est activé par défaut et non désactivé, retours (« Feedback »), bon de commande, et **modèles Labs ou Preview** (§ 4.3, où ni le refus d'entraînement ni la rétention zéro ne s'appliquent). La page de l'inférence dit que les données envoyées par l'API ne servent pas à l'entraînement. Le centre d'aide (mis à jour le 03/09/2026) décrit pour l'API un interrupteur « Anonymous improvement data », dans le menu Privacy de la console d'administration, distinct de celui de Vibe ; la valeur par défaut pour l'API n'y est pas écrite. | Vérifier l'interrupteur dans la console, et n'utiliser qu'un modèle de production, jamais Labs ou Preview |
| **Rôle de Mistral** | Conditions commerciales, § 12 : Mistral est sous-traitant ; l'accord de traitement des données (DPA, en vigueur le 27/07/2026) s'applique, intégré par renvoi (§ 11.2), sans signature séparée. Mais le DPA, § 2.3, fait de Mistral un **responsable de traitement pour la modération automatique et la surveillance des abus** de ses API, sauf rétention zéro. | Une exception à inscrire au registre : pour la modération, Mistral décide seul |
| **Lieu du traitement** | Avec `api.eu.mistral.ai`, l'inférence se fait dans des centres de données de l'UE et de l'AELE, au tarif catalogue majoré de 10 %. Le **plan de contrôle** (compte, clés, facturation, analyses d'usage) peut être traité hors de la zone, et le stockage régional n'est pas garanti pour toutes les données. Les modèles disponibles varient selon la région. | Les prompts restent dans l'UE et l'AELE pour l'inférence ; les données de compte peuvent sortir |
| **Transferts hors UE** | DPA, § 8.1 : transferts permis vers un pays adéquat, avec des garanties appropriées ou par les clauses contractuelles types ; le Data Privacy Framework n'est pas cité. Open Terms Archive (10/02/2025) : le DPA a ajouté les **États-Unis** aux lieux de traitement sur Google Cloud (avant : l'Irlande seule), et restreint la notification aux ajouts et remplacements de sous-traitants. DPA, § 7 : liste des sous-traitants sur le Trust Center, alertes par courriel, 10 jours pour s'opposer. | La liste des sous-traitants est à lire avant de conclure |
| **Conservation** | Sans rétention zéro, entrées et réponses de l'API gardées **30 jours** pour la surveillance des abus (politique de confidentialité, selon des résumés tiers ; DPA, § 10.1 : données rendues inaccessibles 30 jours après la fin de l'accès). La rétention zéro : plans payants seulement, sur demande motivée, refusable, hors modèles Labs. | Une durée de 30 jours à inscrire au registre |
| **Droit applicable** | Conditions commerciales, § 14.10 : droit français et tribunaux de Paris pour un client hors Amériques et Asie-Pacifique. | Rien à faire |

## Verdict proposé (Era décide)

Mistral est **compatible avec la règle § 0 comme second fournisseur**, si quatre conditions sont vérifiées par Era :

1. L'interrupteur d'amélioration de l'API est **désactivé** dans la console d'administration de Mistral.
2. Le modèle utilisé (`mistral-large-2512`, Large 3) est un **modèle de production**, pas Labs ni Preview.
3. La **liste des sous-traitants** est lue : aucun hors de l'UE pour l'inférence européenne, ou chaque exception notée.
4. Le registre est **mis à jour** (T6 et T8) : Mistral destinataire, 30 jours de conservation, rôle de responsable
   pour la modération, plan de contrôle possible hors de la zone.

Il n'est **pas** compatible avec deux promesses : « aucune donnée ne quitte l'UE » (le plan de contrôle et la
modération y échappent) et « aucune conservation » (30 jours sans rétention zéro).

## Ce que je n'ai pas pu vérifier

- La liste des sous-traitants : la page du Trust Center se construit en JavaScript, sa lecture automatique est vide.
- Le plan du compte Mistral d'Era (gratuit ou payant), dont dépend l'accès à la rétention zéro.
- Le statut de `mistral-large-2512` (production, ou Labs ou Preview) : aucune source officielle lue.
- La durée de 30 jours vient de résumés tiers de la politique de confidentialité, pas du texte lu par moi.

## Sources (vérifiées le 13/11/2026, HTTP 200)

- [Conditions commerciales de Mistral AI](https://legal.mistral.ai/terms/commercial-terms-of-service)
- [Accord de traitement des données (DPA)](https://legal.mistral.ai/terms/data-processing-addendum)
- [Centre d'aide : refuser l'usage des données pour l'entraînement](https://help.mistral.ai/en/articles/455207-can-i-opt-out-of-my-input-or-output-data-being-used-for-training)
- [Rétention zéro des données](https://docs.mistral.ai/admin/monitor-comply/zero-data-retention)
- [Inférence régionale](https://docs.mistral.ai/fr/studio-api/regional-inference)
- [Page de l'inférence de Mistral](https://mistral.ai/cloud/inference/)
- [Trust Center : sous-traitants](https://trust.mistral.ai/subprocessors) (à ouvrir dans un navigateur)
- [Open Terms Archive : traitement aux États-Unis](https://opentermsarchive.org/en/memos/mistral-operates-usa-no-notification/)

## 📖 Glossaire

- **DPA** (Data Processing Agreement) : le contrat qui fixe ce qu'un sous-traitant peut faire des données personnelles.
- **Sous-traitant / responsable de traitement** : le premier traite pour le compte d'un autre ; le second décide du
  pourquoi et du comment.
- **Clauses contractuelles types** : modèle de contrat de la Commission européenne pour encadrer un transfert hors UE.
- **AELE** : Islande, Liechtenstein, Norvège (dans l'Espace économique européen) et Suisse (reconnue adéquate).
- **Plan de contrôle** : la partie du service qui gère le compte, les clés et la facturation, pas les requêtes.
- **Rétention zéro** : option où le fournisseur ne garde rien après la réponse.
- **Labs / Preview** : modèles expérimentaux de Mistral, soumis à des règles d'entraînement différentes.
