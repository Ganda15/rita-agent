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

À couper en premier si le temps manque : le jour 5, gardé comme limite connue.

## 3. Composante agentique

Graphe LangGraph à trois étapes fixes (`scout`, `rag`, `redacteur`), garde-fous
en entrée, sur les articles et en sortie. **Pourquoi :** un briefing financier doit
pouvoir être relu et rejoué ; des arêtes fixes le rendent traçable, et le risque
principal (une phrase qui conseille) est bloqué par un contrôle après le modèle.

## 4. Stack

Python, FastAPI, PostgreSQL, ChromaDB, LangGraph, Langfuse, Docker, GitHub Actions,
modèle Azure AI Foundry en zone UE. Élément hors socle : [À CONFIRMER].

## 5. Schémas

**Le système complet.** Chaque soir, la collecte lit six sources (cours, taux de la
BCE, séries FRED, flux RSS, pages scrapées, fichier de positions) et range tout
dans PostgreSQL ; les articles sont aussi indexés dans ChromaDB. À la demande,
l'interface (trois écrans) ou un assistant passant par la passerelle MCP appelle
l'API FastAPI, protégée par une clé. Pour un briefing, le graphe enchaîne `scout`,
`rag` et `redacteur`, le modèle Azure (zone UE) rédige, et le garde-fou de sortie
relit le texte avant la réponse. Autour, GitHub Actions teste chaque changement, la
production tourne en conteneur derrière Caddy, Langfuse trace chaque briefing, et
deux alertes ouvrent une issue « incident ».

- Architecture : [E3-architecture.png](rapports/E3/schemas/E3-architecture.png)
- Pilotage (chaîne CI/CD, environnements, signaux) : [E3-chaine-livraison.png](rapports/E3/schemas/E3-chaine-livraison.png)
  et [E3-monitorage.png](rapports/E3/schemas/E3-monitorage.png)

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

## 7. Sprints 2 à 5

| Sprint | Quoi | Risque |
|---|---|---|
| 2 | Déploiement, version servie, retour arrière | déploiement encore manuel |
| 3 | Validation des entrées, collecte robuste | une source change de format |
| 4 | Débit, refus journalisés | régression d'un garde-fou |
| 5 | Métriques, tableau, alertes, démo | alertes Langfuse lentes à sonner |