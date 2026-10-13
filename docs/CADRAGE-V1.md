# RITA : cadrage V1 (fil rouge, sprint 1)

> Ce dossier consolide l'existant ; il ne le réécrit pas. Le détail vit dans
> [ARCHITECTURE.md](ARCHITECTURE.md) et [EXPLOITATION.md](EXPLOITATION.md).

## 1. Le besoin

**Pour qui.** Un investisseur particulier qui suit seul son portefeuille d'actions
et n'a pas le temps de tout relire chaque soir.

**Parcours principal.** L'utilisateur choisit une valeur ; RITA rédige en français
un briefing court à partir des données collectées la veille (cours, indicateurs,
extraits d'articles). Un garde-fou retient tout texte qui recommande d'acheter ou
de vendre (contrainte AMF). RITA aide à lire le marché, elle ne conseille pas.

**Hors périmètre V1.** Aucun conseil ni ordre de bourse. Un seul utilisateur, une
seule clé. Pas de temps réel. Pas de nouvel agent. Aucun entraînement de modèle.

## 2. Périmètre V1 : l'existant, durci en six jours

Le parcours principal existe et est testé. La V1 ferme les manques déjà relevés
([ARCHITECTURE.md § 9](ARCHITECTURE.md#9-ce-que-cette-architecture-ne-fait-pas),
[revue OWASP du 03/10](../evidence/C17/revue-owasp-top10-2025-2026-10-03.md)).

| Jour | Travail |
|---|---|
| 1 | Déployer le code gelé du 15/10 ; `/health` annonce la version servie |
| 2 | Retour arrière outillé, écrit dans `EXPLOITATION.md` |
| 3 | Valeur inconnue ou trop longue : réponse 422, sans appel au modèle |
| 4 | Limite de débit sur `POST /briefing` |
| 5 | Refus de clé journalisés avec leur `request_id` |
| 6 | Marge : tests et documentation |

À couper en premier si le temps manque : le jour 4, gardé comme limite connue, car aucun critère du contrat n'en
dépend. Le jour 5 reste : le critère 4 exige la ligne de refus.

**Ce que la V1 reprend du chapitre « Industrialisation » (brief du 15/09).** Le
manifeste de version (jour 1), le retour arrière (jour 2) et le 422 pour une valeur
inconnue (jour 3) y étaient déjà conçus. Restent hors V1, bien que conçus : la route
`/v1` avec son refus en 401, les alertes Telegram, la porte d'évaluation sur le vrai
modèle.

## 3. Composante agentique

Graphe LangGraph à trois étapes fixes (`scout`, `rag`, `redacteur`), garde-fous
en entrée, sur les articles et en sortie. **Pourquoi :** un briefing financier doit
pouvoir être relu et rejoué ; des arêtes fixes le rendent traçable, et le risque
principal (une phrase qui conseille) est bloqué par un contrôle après le modèle.

**Pourquoi pas un agent qui choisit ses outils.** Il serait plus souple, mais imprévisible
et difficile à auditer ; en finance, chaque texte doit pouvoir s'expliquer. Le menu du
dispositif est demandé au formateur pour confronter ce choix.

## 4. Stack

| Outil | Rôle et raison |
|---|---|
| Python | le langage des données et de l'IA ; LangGraph, FastAPI et les clients des modèles y existent |
| FastAPI | l'API : paramètres typés et vérifiés, documentation OpenAPI générée |
| PostgreSQL | les cours et les indicateurs en SQL ; des règles CHECK refusent un cours impossible |
| ChromaDB | la recherche dans les articles : base de vecteurs locale, dans un dossier, sans service à part |
| LangGraph | un état partagé entre les trois étapes, chaque étape tracée ; prêt pour un embranchement plus tard. Limite : à trois étapes fixes, il sert surtout à structurer |
| Langfuse | la trace de chaque briefing (consigne, réponse, jetons, durée) et les alertes ; région UE |
| Docker | la même application sur le poste, en CI et sur le serveur |
| GitHub Actions | les contrôles à chaque envoi, sans serveur à gérer |
| Azure AI Foundry, zone UE | le modèle, sans entraînement ; données gardées en Europe (`LLM_ORDRE=foundry` depuis le 11/10) |

Élément hors socle : [À CONFIRMER].

## 5. Schémas

**Le système complet.** Chaque soir, la collecte lit ses sources (cours, taux de la
BCE, séries FRED, flux RSS, pages scrapées) en six étapes indépendantes et range tout
dans PostgreSQL ; les articles admis sont aussi indexés dans ChromaDB. Le fichier de
positions et l'archive de cours sont importés à part (`db/importer.py`). À la demande,
l'interface (trois écrans) ou un assistant passant par la passerelle MCP appelle
l'API FastAPI, protégée par une clé. Pour un briefing, le graphe enchaîne `scout`,
`rag` et `redacteur`, le modèle Azure (zone UE) rédige, et le garde-fou de sortie
relit le texte avant la réponse. Autour, GitHub Actions teste chaque changement, la
production tourne en conteneur derrière Caddy, Langfuse trace chaque briefing, et
deux alertes ouvrent une issue « incident ».

**La passerelle MCP.** Elle tourne sur le poste de l'utilisateur, lancée par l'assistant
(Claude Desktop), sans port réseau (transport stdio, `passerelle_mcp/serveur.py`). Elle offre
trois outils en lecture seule (`rita_fraicheur`, `rita_portefeuille`, `rita_indicateurs`),
appelle l'API en HTTP avec la clé et n'a aucun accès au briefing ; ses refus sont journalisés
par `POST /audit/mcp`.

- **Architecture complète de la V1** (données, agent et garde-fous, interface, API, puis le pilotage ; les ajouts des
  six jours en pointillé rouge) : [CADRAGE-architecture-v1.png](cadrage/CADRAGE-architecture-v1.png), éditable en
  [CADRAGE-architecture-v1.drawio](cadrage/CADRAGE-architecture-v1.drawio)
- Architecture, état du code au 04/10 : [E3-architecture.png](rapports/E3/schemas/E3-architecture.png)
- Pilotage (chaîne CI/CD, environnements, signaux) : [E3-chaine-livraison.png](rapports/E3/schemas/E3-chaine-livraison.png)
  et [E3-monitorage.png](rapports/E3/schemas/E3-monitorage.png)
- Interface, de l'écran au modèle et ses erreurs : [E3-integration-briefing.png](rapports/E3/schemas/E3-integration-briefing.png)
  et un vrai briefing à l'écran : [ecran-briefing-2026-10-03.png](../evidence/C10/ecran-briefing-2026-10-03.png)

Le schéma de la V1 est daté du 12/10 ; les schémas E3 sont datés du 04/10. Depuis le 11/10, le poste n'appelle plus qu'Azure
(`LLM_ORDRE=foundry`, règle UE seule) : la cascade dessinée reste dans le code, sans
secours configuré. Dans le schéma de livraison, les cases rouges en pointillé
reprennent l'esquisse de la chaîne du chapitre « Industrialisation » ; la V1 en
construit deux, le manifeste de version et le retour arrière.

## 6. Contrat personnel

1. **Étant donné** une clé valide et une valeur cotée il y a moins de 5 jours
   ouvrés, **quand** j'appelle `POST /briefing?ticker=OR.PA`, **alors** je reçois
   un 200, un texte en français et un en-tête `X-Request-ID`.
2. **Étant donné** un texte du modèle qui recommande d'acheter, **quand** le
   garde-fou de sortie le relit, **alors** la réponse porte `conforme_amf: false`
   et le texte d'origine n'est pas servi.
3. **Étant donné** une valeur inconnue ou de plus de 20 caractères, **quand** je
   demande un briefing, **alors** je reçois un 422 et le modèle n'est pas appelé.
4. **Étant donné** une fausse clé, **quand** j'appelle une route de données,
   **alors** je reçois un 403 et le journal garde une ligne de refus.
5. **Étant donné** la version N en production et N-1 taguée, **quand** un tiers
   suit la procédure de retour arrière, **alors** `/health` annonce N-1 en moins
   de 10 minutes.

**La preuve de chaque critère.**

| Critère | Preuve |
|---|---|
| 1 | l'en-tête : `tests/test_request_id.py` (l. 46) ; le 200 et le texte : démonstration du 13/10 |
| 2 | `tests/test_health.py` (l. 126) |
| 3 | test à écrire au jour 3, avec une doublure du modèle appelée zéro fois |
| 4 | le 403 : `tests/test_api_donnees.py` (l. 77) ; la ligne de refus : test à écrire au jour 5 |
| 5 | vérification chronométrée au jour 2, par un tiers |

## 7. Sprints 2 à 5

| Sprint | Quoi | Risque |
|---|---|---|
| 2 | Déploiement, version servie, retour arrière | déploiement encore manuel |
| 3 | Validation des entrées, collecte robuste | une source change de format |
| 4 | Débit, refus journalisés | régression d'un garde-fou |
| 5 | Métriques, tableau, alertes, démo | alertes Langfuse lentes à sonner |