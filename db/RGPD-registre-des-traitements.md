# Registre des traitements de données personnelles — RITA

**Compétence C4**, trois critères :
> « Le registre des traitements de données personnelles intègre l'ensemble des traitements
> de données personnelles impliqués dans la base de données. »
> « Les procédures de tri des données personnelles pour la mise en conformité de la base de
> données avec le RGPD sont rédigées. »
> « Les procédures de tri détaillent les traitements de conformité (automatisés ou non) à
> appliquer ainsi que leur fréquence d'exécution. »

**Base réglementaire** : RGPD (Règlement Général sur la Protection des Données,
UE 2016/679), **article 30** — registre des activités de traitement.

**Dernière mise à jour** : 2026-10-10 *(glossaire et suites du 02/10 alignés sur la lecture des contrats du 05/10 : clauses contractuelles types prévues, Data Privacy Framework non vérifié ; avant, le 2026-10-09 : Azure AI Foundry passé en Data Zone Standard EU par Era, région mesurée
Sweden Central sur trois appels réels, T6 partiellement corrigé ; avant, le 2026-10-05 : règle « UE seule » posée par Era ; T1 corrigé : les noms des sociétés détenues partent vers Google News ; T6, fournisseurs du modèle, et T7, requêtes Google News, inscrits ; traces de test supprimées le 04/10 ; le même jour, garanties contractuelles des destinataires relues : identifiées,
vérification propre à RITA incomplète, voir § 5)*

*Mise à jour précédente : 2026-10-02 (T3 devient un traitement actif : Langfuse Cloud, région UE ; P1 et P2 corrigées ; état de `memory_audit` ajouté à T2).*

---

## 0. Le cadre, dit honnêtement

RITA est un **projet personnel mono-utilisateur**. Era est à la fois :

- le **responsable de traitement** — celui qui décide pourquoi et comment les données sont traitées ;
- la **personne concernée** — celui dont les données sont traitées.

Cette situation **n'exonère de rien** : dès qu'un traitement automatisé porte sur des
données personnelles, le RGPD s'applique. Elle simplifie une chose : il n'y a pas de demande
d'accès d'un tiers à instruire. Elle ne dispense pas d'encadrer les destinataires extérieurs
(Langfuse en T3, les fournisseurs du modèle en T6, Google en T7).

> 🇪🇺 **Règle du projet, posée par Era le 2026-10-05 : aucune donnée personnelle ne quitte l'Union
> européenne.** C'est un **choix du projet**, pas une exigence du référentiel : C4 demande une base
> « dans le respect du RGPD », un registre complet et des procédures de tri (règlement d'examen, p. 20-21).
> Elle est plus stricte que le RGPD, qui autorise des transferts encadrés (clauses contractuelles
> types, Data Privacy Framework) : un transfert licite peut quand même la violer. Choisie, elle doit
> être prouvée, et elle pèse sur le choix des services d'IA (C7). Une
> région « UE » n'est pas une personne morale : il faut vérifier qui traite, où, et avec quels
> sous-traitants. **Au 2026-10-05, trois traitements ne la respectent pas ou pas de façon prouvée** :
> T6 (fournisseurs du modèle : depuis le 09/10, Azure, premier de la cascade, traite en Data Zone EU, mais les replis
> Anthropic et OpenRouter restent sans garantie de région), T7 (Google News), et T3 : le contrat de Langfuse lui-même permet un traitement hors de
> la région choisie (DPA ClickHouse, § 6.1).
> Corrections après le gel du 15/10 (§ 5).

> ⚠️ **Ce que ça change si RITA devient multi-utilisateur** : il faudra une base légale
> explicite (le consentement), une information des utilisateurs, une procédure de réponse
> aux demandes d'accès, et une analyse d'impact (AIPD) — les données financières sont
> considérées à risque élevé. **Aujourd'hui, aucun de ces éléments n'est en place, et c'est
> assumé.**

**Précision utile** : les données financières **ne sont pas** des « données sensibles » au
sens de l'**article 9** du RGPD (qui vise l'origine ethnique, les opinions politiques, la
santé, l'orientation sexuelle…). Ce sont des données personnelles ordinaires — mais dont la
divulgation cause un préjudice réel, donc à protéger sérieusement.

---

## 1. Les traitements recensés

### T1 — Stockage du portefeuille

| Rubrique | Contenu |
|---|---|
| **Finalité** | Calculer la valorisation et la performance du portefeuille pour produire le briefing quotidien |
| **Base légale** (art. 6) | **Intérêt légitime** de la personne concernée, qui est l'utilisateur lui-même et l'unique destinataire |
| **Personnes concernées** | 1 — l'utilisateur |
| **Catégories de données** | Ticker détenu · quantité · prix de revient unitaire (PRU) · date d'achat · devise |
| **Ce que ça révèle** | La **situation financière** : composition du patrimoine, montants investis, plus ou moins-values |
| **Support** | Table `position` (PostgreSQL) · fichier CSV source |
| **Destinataires** | Aucun pour les quantités, PRU et dates : elles restent locales. **Les noms des sociétés détenues, eux, partent chaque soir vers Google News** (T7, relevé le 2026-10-05 ; ce registre disait « aucun » à tort) |
| **Transfert hors UE** | Table et fichier : non. Noms des sociétés détenues : **probable**, voir T7 |
| **Durée de conservation** | Position **active** : tant que sa ligne est dans le CSV · position **soldée** : **3 ans après `date_cloture`**, puis suppression (P2). **Depuis le 03/10/2026 (plan 66)** : une ligne retirée du CSV **est** l'acte de vente ; l'import la clôt à la date du jour (la seule date de vente que le projet connaisse, donc en retard du délai entre la vente et l'import suivant) ; une ligne revenue rouvre la même position ; un CSV vide ne clôt rien |
| **Sécurité** (art. 32) | Fichier source **jamais versionné** (`.gitignore`, vérifié par `git check-ignore`) · base non exposée au réseau · chemin par variable d'environnement `POSITIONS_CSV` |

### T2 — Journal des accès à la mémoire des agents

| Rubrique | Contenu |
|---|---|
| **Finalité** | Déboguer et auditer le comportement des agents (exigence du standard Velmo 2.0) |
| **Base légale** | Intérêt légitime — sans trace, un agent n'est ni débogable ni explicable |
| **Catégories de données** | Nom de l'agent · type de mémoire · opération · clé · **résumé du contenu** |
| **⚠️ Risque** | Le champ `resume` **peut contenir des éléments du portefeuille** (un ticker détenu, un montant) selon ce que l'agent manipule |
| **Support** | Table `memory_audit` |
| **Durée de conservation** | **90 jours** — au-delà, un log de débogage n'a plus d'utilité |
| **Sécurité** | Purge automatisée (voir §2) |
| **État au 2026-10-02** | **Aucun code n'écrit dans cette table** (`grep -rn "INTO memory_audit"` : aucun résultat). Le risque ci-dessus est donc théorique aujourd'hui. Décision en attente : un écrivain qui ne stocke que des empreintes SHA-256, ou le retrait de la table avec T2, P1 et P5 (`CONTINUITE.md` D, 02/10) |

### T3 : Traces d'exécution Langfuse Cloud, région UE : ✅ **ACTIF depuis le 2026-10-02**

> ## ✅ Mise à jour du 2026-10-02 : ce traitement est maintenant réel
>
> Le traçage est activé depuis le 02/10 : `src/traces.py` envoie à **Langfuse Cloud, région UE (Irlande)** un trace par appel
> au modèle, avec une génération par fournisseur essayé. L'outil retenu le 28/09 est Langfuse, **pas LangSmith** :
> LangSmith n'a jamais été activé ici et reste dans ce registre seulement comme l'option comparée et écartée.
> Sans clés Langfuse dans l'environnement, rien ne part (le module ne fait alors rien). La suite de tests coupe le traçage
> pour tous les tests depuis le 02/10 (douze lignes de test avaient atteint la production, voir plus bas).


> ## ⚠️ Correction du 2026-08-14 — ce traitement n'a **jamais eu lieu**
>
> Ce registre décrivait T3 comme un traitement **actif**, avec transfert de données
> personnelles vers les États-Unis et un risque classé 🔴 haute. **Vérification faite :
> c'est faux.**
>
> | Contrôle | Constat |
> |---|---|
> | `LANGCHAIN_TRACING_V2` dans le `.env` réel | **absent** |
> | `LANGCHAIN_API_KEY` dans le `.env` réel | **absent** |
> | Appel à LangSmith dans le code (`grep`) | **aucun** |
> | `langsmith` installé | oui — **dépendance transitive** de `langchain-core`, jamais activée |
>
> Les deux variables n'existent que dans `.env.example`, à titre d'exemple.
> **Sans drapeau ni clé, aucune trace ne quitte la machine.**
>
> 🔑 **La leçon** : un registre qui **sur-déclare** est aussi inexact qu'un registre qui
> oublie. Déclarer un transfert hors UE qui n'existe pas, c'est se décrire moins protecteur
> qu'on ne l'est — et rendre invérifiable tout le reste du document.

Ce traitement est réel depuis le 02/10/2026 ; les rubriques ci-dessous décrivent **Langfuse** (elles décrivaient LangSmith
avant le 28/09).

| Rubrique | Contenu (état au 2026-10-02) |
|---|---|
| **Finalité** | Monitorage du modèle : latence, coût, jetons, erreurs de repli entre fournisseurs (C11, C20) |
| **Base légale** | Intérêt légitime |
| **Catégories de données** | Le prompt envoyé au modèle et sa réponse : ticker, cours, variation, ADTV20, devise, fraîcheur, passages de presse. **Aucune position, aucun PRU, aucune quantité** (mesuré le 28/09 dans `agents/analyst.py`). Malgré cela, les tickers demandés révèlent les valeurs d'intérêt de l'utilisateur. S'y ajoutent le modèle, le fournisseur, l'usage en jetons et le message d'erreur (tronqué à 300 caractères) |
| **Destinataire** | **Langfuse GmbH** (Allemagne), sous-traitant, au sein du groupe ClickHouse. L'addendum applicable est le « ClickHouse Customer Data Processing Addendum » (en vigueur le 10/04/2026) ; contact : privacy@clickhouse.com. Hébergement : AWS `eu-west-1` (Irlande) |
| **Sous-traitants ultérieurs** | Selon la liste publiée par l'éditeur (en vigueur le 10/08/2026) : ClickHouse GmbH (Allemagne), ClickHouse BV (Pays-Bas) et **ClickHouse, Inc. (États-Unis)** |
| **Transfert hors UE** | Les données sont hébergées dans l'UE. **Une entité américaine figure parmi les sous-traitants du groupe.** Relu le 2026-10-05 dans le DPA (https://clickhouse.com/legal/agreements/data-processing-addendum) : **§ 6.1**, pour Langfuse Cloud, les données restent dans la région choisie « except as reasonably necessary to provide the Services or as necessary to comply with the law » ; **§ 6.2**, un transfert hors de l'EEE sans décision d'adéquation est encadré par les clauses contractuelles types. Donc : garantie contractuelle identifiée, **transfert possible par contrat**, conformité RGPD de ce transfert **non vérifiée** (AITD non faite, § 5) ; **non conforme à la règle UE seule** (§ 0), par contrat |
| **Durée de conservation** | 30 jours (palier gratuit), moins que les 90 jours de T2. Suppression possible à la demande par l'interface ou par l'API (quelques minutes selon l'éditeur) |
| **Mesure de réduction** | Rien à masquer aujourd'hui. **Condition écrite** : si une position, un PRU ou une quantité entre un jour dans le prompt, brancher la fonction de masquage du SDK Langfuse avant de tracer le nœud concerné |
| **Incident du 2026-10-02** | Des générations de test (texte « prompt test ») ont été écrites dans le projet de production par la suite de tests. Aucune donnée personnelle dedans. Cause corrigée le jour même ; **traces supprimées le 2026-10-04** (relecture par l'API : 0 « prompt test ») |

#### Décision prise avant l'activation (historique du 14/08 et du 28/09)

Au 14/08, l'outil de monitorage n'était pas arrêté, et le choix avait une conséquence RGPD directe :

| Option | Sous-traitant | Transfert hors UE | Conséquence pour ce registre |
|---|---|---|---|
| **LangSmith** | LangChain Inc. (États-Unis) | **oui** | T3 devient actif, CCT / *Data Privacy Framework* à invoquer |
| **Langfuse auto-hébergé** (cœur sous licence MIT) | **aucun** | **non** | **T3 disparaît** — les données ne quittent pas la machine |
| **Langfuse Cloud, région UE** (Irlande) | Langfuse | **non** | T3 reste, mais sans transfert au titre de l'article 44 |

> 💡 **Le meilleur traitement de données personnelles est celui qu'on ne fait pas.**
> L'auto-hébergement supprime le sous-traitant, le transfert, et les clauses à justifier.
> ⚠️ Il exige Docker — **aujourd'hui le démon ne démarre pas sur la machine d'Era**, c'est
> le vrai obstacle, et il vaut aussi pour C13 (empaquetage, livraison continue).

#### Décision du 2026-09-28 : **Langfuse Cloud, région UE** (option 3), activée le 2026-10-02 (carte #39)

Décision d'Era, après la règle donnée par le formateur le 28/09 (« la condition, c'est la sensibilité
des données ») et une mesure dans le code plutôt qu'une supposition :

| Ce qui a été mesuré | Résultat | Où |
|---|---|---|
| Le prompt envoyé au modèle contient-il une donnée personnelle ? | **Non** : ticker, cours, variation, ADTV20, devise, fraîcheur, passages de presse. Aucune position, aucun PRU, aucune quantité | `agents/analyst.py`, `generate_briefing()` ; `grep` sur `agents/`, `graph/` : zéro |
| Ce qu'une trace révèle malgré tout | les tickers demandés, donc les valeurs détenues, par effet de bord | ce registre, ligne « catégories » |
| Auto-hébergement possible sur le serveur ? | **Non** : Langfuse v3 = six composants (web, worker, Postgres, ClickHouse, Redis, S3) ; le CX23 a 4 Go partagés, déjà occupés par l'API, PostgreSQL et Chroma | doc Langfuse « self-hosting » ; spécification CX23 |
| Région UE de Langfuse Cloud | Irlande, AWS `eu-west-1`, `cloud.langfuse.com` ; palier gratuit : 50 000 unités/mois, 30 jours de rétention, 2 alertes | doc Langfuse « cloud data regions », « pricing » |
| LangSmith aurait-il convenu ? | région UE disponible (GCP), mais l'éditeur déclare **aucune entité juridique en UE** pour contracter, et l'auto-hébergement est réservé au plan Enterprise : pas de porte de sortie | doc LangSmith « regions FAQ », page des tarifs |

**Conséquences pour ce registre, appliquées le 2026-10-02 (voir le tableau de T3 plus haut)** :

- Destinataire : **Langfuse**, région UE. ⚠️ La page RGPD de Langfuse renvoie à `privacy@clickhouse.com` :
  **l'entité qui traite peut être ClickHouse Inc. (États-Unis)** même pour la région UE. Une région n'est
  pas une personne morale. Relevé le 02/10 par recherche : le contrat est le « ClickHouse Customer Data Processing
  Addendum », avec Langfuse GmbH (Allemagne) comme sous-traitant et ClickHouse, Inc. (États-Unis) parmi les entités
  du groupe. **Reste à faire par Era : lire ce DPA** et confirmer si un transfert vers les États-Unis est encadré
  (clauses contractuelles types ou Data Privacy Framework). Le registre ne dit pas « aucun transfert » avant cela.
  **Fait le 2026-10-05** : DPA lu, § 6.2 (clauses contractuelles types), voir la ligne « Transfert hors UE » de T3.
- Transfert hors UE : **non** au titre de la localisation des données ; à confirmer au titre de l'entité
  (point ci-dessus). **Depuis le 2026-10-05** : transfert possible par contrat, encadré par les clauses types (T3).
- Durée de conservation : 30 jours (palier gratuit), inférieure aux 90 jours de T2.
- Mesure de réduction : rien à masquer aujourd'hui (aucune donnée personnelle dans le prompt). **Condition
  écrite** : si une position, un PRU ou une quantité entre un jour dans le prompt, brancher la fonction de
  masquage du SDK Langfuse avant d'activer la trace correspondante.
- Alternative écartée et pourquoi : auto-hébergement (mesuré impossible sur 4 Go, coût d'entretien décrit par
  le formateur) ; LangSmith (pas de porte de sortie open source, entité UE absente).

### T4 — Fichier CSV source du portefeuille

| Rubrique | Contenu |
|---|---|
| **Finalité** | Alimenter T1 |
| **Support** | Fichier local, hors du dépôt Git |
| **Sécurité** | `.gitignore` : `data/positions.csv`, `*bourse*.xlsm`, `*portefeuille*.csv` — **vérifié** par `git check-ignore` |
| **Durée** | Conservé tant qu'il est la source de vérité du portefeuille |

### T5 : Journal des appels MCP (table `mcp_calls`) : ✅ **ACTIF depuis le 2026-10-03** (plan 62)

| Rubrique | Contenu |
|---|---|
| **Finalité** | Sécurité et surveillance des accès par un client automatique (la passerelle MCP) : qui a demandé quel outil, avec quel résultat, quand ; les refus compris (C20, chapitre « Données » §3.7) |
| **Base légale** | Intérêt légitime du responsable : sécurité du service ; sans journal des refus, la règle de fermeture de la matrice d'accès est invérifiable |
| **Catégories de données** | identifiant de requête · identité technique du client (`passerelle-mcp`) · nom de l'outil · statut (succès, refusé, erreur) · code d'erreur typé · durée · version de la politique d'accès · horodatage. **Jamais** : paramètres de l'appel, prompt, clé, positions ou totaux |
| **⚠️ Pourquoi c'est personnel** | il n'y a qu'un utilisateur : un horodatage et un identifiant de requête disent quand le propriétaire a consulté quoi |
| **Support** | Table `mcp_calls`, écrite par l'API seule (`db/audit_mcp.py`) ; la passerelle remonte ses refus par `POST /audit/mcp`, jamais par SQL |
| **Durée de conservation** | **90 jours** (comme T2) : au-delà, un refus ancien n'aide plus un diagnostic |
| **Sécurité** | rôle `rita_lecture` en lecture seule ; purge automatisée P6 (§2) ; une panne d'écriture est comptée et exposée par `/donnees/fraicheur` |
| **Droits** | effacement sur demande par `request_id` ; accès : le propriétaire lit la table |

### T6 : Rédaction du briefing par un modèle fourni : ✅ **ACTIF**, inscrit le 2026-10-05 (non conforme à la règle UE seule ; premier fournisseur en zone UE depuis le 2026-10-09)

| Rubrique | Contenu (état relu dans le code le 2026-10-05) |
|---|---|
| **Finalité** | Rédiger en français le briefing d'une valeur demandée par l'utilisateur (`POST /briefing`) |
| **Base légale** | Intérêt légitime |
| **Catégories de données** | Le prompt : ticker demandé, cours, variation, ADTV20, devise, fraîcheur, les 13 indicateurs, passages de presse (`agents/analyst.py`). **Aucune position, aucun PRU, aucune quantité.** Ce qui est personnel malgré tout : **la valeur demandée et l'heure de la demande** disent ce qui intéresse l'unique utilisateur, et chaque appel est rattaché à son compte chez le fournisseur |
| **Destinataires** | Dans l'ordre de la cascade (`src/llm.py`, `LLM_ORDRE`) : 1. **Microsoft Azure AI Foundry**, déploiement **`gpt-5.4-dzs-eu`, Data Zone Standard, zone EUR**, depuis le 2026-10-09 (créé par Era dans le portail ; même modèle `gpt-5.4`) : les appels sont traités dans la zone de données de l'UE ; région mesurée sur trois appels réels faits par le code de RITA : Sweden Central (`evidence/C8/preuve-deploiement-zone-eu-2026-10-09.md`). Jusqu'au 09/10, déploiement **Global Standard** (lu dans le portail le 03/10, `evidence/C7/prix-et-environnement-2026-10-03.md`), qui pouvait traiter un appel dans n'importe quelle région Azure ; 2. **Anthropic** (API directe), société établie aux États-Unis ; 3. **OpenRouter**, point d'entrée général `https://openrouter.ai/api/v1/chat/completions` (`src/llm.py:24`), sans garantie de région |
| **Transfert hors UE** | **Azure : traitement dans la zone UE** depuis le 2026-10-09 (Data Zone Standard EU ; Microsoft reste une société américaine, contrat non relu en détail). **Probable** pour Anthropic et OpenRouter, appelés seulement si Azure échoue. **Toujours non conforme à la règle UE seule** (§ 0) tant que ces deux replis existent |
| **Garanties contractuelles** (relues le 2026-10-05) | **OpenRouter** (https://openrouter.ai/data-processing-agreement) : § 13.2, clauses contractuelles types, module 2 ; l'option « EU-only » (annexe A) ne s'applique **que si elle est choisie** et passe par l'« EU API », et ne couvre que les « API Payloads » (prompts, réponses), **pas** les données de compte, de facturation ni d'authentification : elle ne suffit donc pas à la règle UE seule. **Microsoft** : clauses contractuelles types proposées par son DPA pour Azure, selon la page officielle (https://learn.microsoft.com/en-us/compliance/regulatory/offering-eu-model-clauses), non relue en détail. **Anthropic** : DPA avec clauses types intégré à ses conditions commerciales pour l'API, selon sa page officielle (https://privacy.claude.com/en/articles/7996862-how-do-i-view-and-sign-your-data-processing-addendum-dpa), non relue en détail. **Vérification propre à RITA incomplète** (§ 5) |
| **Durée de conservation** | Selon chaque fournisseur, **non vérifiée** |
| **Lien avec T3** | Le même prompt et la même réponse sont tracés dans Langfuse (T3) |
| **Inventaire champ par champ** | À faire : carte #68 (tableau champ, origine, destinataire, durée, et un test qui échoue si le prompt contient un champ hors liste) |
| **Correction prévue** (après le gel du 15/10, carte #82) | Ne garder que des fournisseurs approuvés : déploiement Azure limité à l'UE (zone de données ou région, à vérifier dans le portail et le contrat), routage UE d'OpenRouter (éligibilité et contrat à vérifier) ou modèle local. **Aucun repli vers un fournisseur non approuvé** : sans fournisseur approuvé, l'écran montre les faits et dit « briefing indisponible » (réponse 503 `AUCUN_FOURNISSEUR` prévue par `docs/conception/frontend/refonte-2026-10.md`, § 6) |

### T7 : Recherche d'actualités sur les valeurs détenues (Google News) : ✅ **ACTIF depuis le 2026-08-28**, inscrit le 2026-10-05 (non conforme à la règle UE seule)

| Rubrique | Contenu (état relu dans le code le 2026-10-05) |
|---|---|
| **Finalité** | Collecter chaque soir les articles de presse sur les sociétés du portefeuille |
| **Base légale** | Intérêt légitime |
| **Catégories de données** | **Le nom de chaque société présente dans la table `position`** (positions closes comprises : `SELECT DISTINCT v.nom_officiel FROM position p JOIN valeur v`, `pipelines/ingest.py:283-289`), placé dans l'adresse d'une requête Google News avec le mot « bourse » et une fenêtre de dates (`sources/rss.py:56-89`) ; l'adresse IP du poste |
| **Ce que ça révèle** | **La composition du portefeuille**, sans les quantités ni les montants |
| **Destinataire** | Google, service Google News (`news.google.com`) ; entité qui traite et lieu de traitement **non vérifiés** |
| **Transfert hors UE** | **Probable, non vérifié. Non conforme à la règle UE seule** (§ 0) |
| **Fréquence** | Chaque soir à 19 h (collecte planifiée) : une requête par société détenue (10 flux le 03/10 : 3 généraux et 7 par société) |
| **Écart de méthode** | Codé le 28/08 (commit `66ea9f9`) **sans inscription préalable** dans ce registre, alors que la procédure M1 demande d'inscrire un traitement **avant** de le coder. Relevé le 05/10 par une relecture extérieure, confirmé dans le code |
| **Correction prévue** (après le gel du 15/10, carte #81) | Remplacer les requêtes dérivées des positions par une liste de veille qui n'en dépend pas (par exemple les 111 valeurs suivies), interrogée auprès de sources approuvées ; à défaut, supprimer ces flux |

### Ce qui **n'est pas** un traitement de données personnelles

| Donnée | Pourquoi |
|---|---|
| `cotation`, `valeur`, `alias_valeur` | Cours de bourse — **données publiques**, aucune personne identifiable |
| `taux_change` | Taux BCE — donnée publique |
| `article` | Presse publique. ⚠️ *Peut* citer des personnes, mais on ne les traite pas en tant que personnes |

---

## 2. Procédures de tri — automatisées

**Script** : `db/rgpd_purge.py` · **Exécution** : `python -m db.rgpd_purge --appliquer`

| # | Procédure | Fréquence | Automatisé |
|---|---|---|---|
| **P1** | Purger `memory_audit` au-delà de **90 jours** | Prévue hebdomadaire ; **lancement manuel aujourd'hui** (aucun planificateur : APScheduler n'est dans aucun fichier de dépendances). La table étant vide, la purge ne supprime rien | ⚠️ script prêt et testé, planification absente |
| **P2** | Supprimer les positions **closes depuis plus de 3 ans** (`date_cloture`, plan 66) | Prévue mensuelle ; **lancement manuel aujourd'hui** | ✅ **applicable depuis le 03/10/2026** (avant : visait `quantite = 0`, interdit par le schéma) ; planification absente |
| **P3** | ~~Détecter les doublons de positions~~ **retirée le 03/10/2026** : l'index unique `uq_position_ligne` (ticker, PRU, date d'achat) les refuse à l'écriture | sans objet | ✅ remplacée par une contrainte de la base |
| **P4** | Vérifier qu'**aucun fichier personnel n'est suivi par Git** | **À chaque commit** (hook pre-commit) | ⬜ **à mettre en place** |
| **P5** | Revoir le champ `resume` de `memory_audit` : contient-il des montants ? | Trimestrielle | ❌ **manuelle** — jugement humain requis |
| **P6** | Purger `mcp_calls` au-delà de **90 jours** (T5) | Prévue hebdomadaire avec P1 ; lancement manuel aujourd'hui | ✅ script `db/rgpd_purge.py` (03/10/2026), même planification que P1 |

**Mode par défaut du script : simulation.** Il affiche ce qu'il supprimerait sans rien
supprimer. Le drapeau `--appliquer` est obligatoire pour agir. *Une purge qui s'exécute par
accident est une perte de données irréversible.*

## 3. Procédures de tri — manuelles

| # | Procédure | Fréquence | Pourquoi pas automatique |
|---|---|---|---|
| **M1** | Relire le registre ci-dessus | À chaque nouvelle source de données | Un nouveau traitement doit être inscrit **avant** d'être codé |
| **M2** | Vérifier que le dépôt public ne contient aucune donnée personnelle | **Avant chaque passage en public** | ⚠️ Le dépôt doit s'ouvrir avant le 05/11 |
| **M3** | Décider du sort des doublons détectés par P3 | Mensuelle | Deux achats identiques le même jour sont possibles |
| **M4** | Réévaluer le traçage Langfuse (T3) | Trimestrielle | Arbitrage entre valeur du monitorage et exposition des données |

---

## 4. Exercice des droits (art. 15 à 22)

Era étant la personne concernée, les droits s'exercent par simple accès à la base. Les
commandes sont néanmoins documentées — elles seraient nécessaires dès le deuxième
utilisateur.

| Droit | Article | Comment l'exercer aujourd'hui |
|---|---|---|
| **Accès** | 15 | `SELECT * FROM position;` |
| **Rectification** | 16 | `UPDATE position SET quantite = ... WHERE id = ...;` |
| **Effacement** | 17 | `DELETE FROM position WHERE id = ...;` puis purge du CSV source |
| **Portabilité** | 20 | `\copy (SELECT * FROM position) TO 'export.csv' CSV HEADER` — format ouvert |
| **Limitation** | 18 | Sans objet tant que la personne concernée est le responsable ; les destinataires extérieurs sont listés en T3, T6 et T7 |
| **Opposition** | 21 | Sans objet : la personne concernée est le responsable de traitement |

---

## 5. Ce qui reste à faire — dit franchement

| # | Action | Criticité |
|---|---|---|
| 1 | ~~Choisir l'outil de monitorage avant d'activer le traçage (T3)~~ **Fait : Langfuse Cloud UE choisi le 28/09, activé le 02/10 ; traces de test supprimées le 04/10 ; DPA relu le 05/10 (§ 6.1 et § 6.2).** Reste : décider si T3 est gardé malgré la règle UE seule (le contrat permet un traitement hors région), ou remplacé (auto-hébergement, autre outil) | 🟠 moyenne |
| 2 | **Hook Git `pre-commit`** interdisant l'ajout d'un fichier personnel (P4) | 🟠 moyenne |
| 3 | Brancher P1 et P2 sur APScheduler (aujourd'hui : lancement manuel) | 🟠 moyenne |
| 4 | Chiffrer la sauvegarde de la base si elle sort de la machine | 🟡 basse tant que tout est local |
| 5 | **T7 (carte #81) : arrêter d'envoyer à Google News les noms des sociétés détenues** (liste de veille indépendante des positions, sources approuvées) | 🔴 haute : révèle chaque soir la composition du portefeuille hors de l'UE |
| 6 | **T6 (cartes #82 et #68) : n'appeler que des fournisseurs de modèle approuvés UE**, sans repli vers un fournisseur non approuvé ; **fait le 2026-10-09 pour le premier fournisseur** (Azure en Data Zone EU, région mesurée) ; reste : retirer les replis Anthropic et OpenRouter (`LLM_ORDRE=foundry`, test et réponse 503 déjà spécifiés), relire en entier le contrat de Microsoft | 🟠 moyenne : un briefing ne sort de l'UE que si Azure échoue |
| 7 | **Transferts hors UE (T3, T6)** : pour chaque destinataire, vérifier la certification au Data Privacy Framework ; à défaut, faire l'**analyse d'impact du transfert (AITD)** exigée par la CNIL pour les clauses types ; documenter contrats applicables, données envoyées, sous-traitants, lieux et durées | 🟠 moyenne pour le RGPD ; sans effet sur la règle UE seule, qui interdit le transfert de toute façon |
| 8 | **T6, Azure** : Microsoft documente des cas limités de transfert hors de son EU Data Boundary, dont l'accès à distance de son personnel (https://learn.microsoft.com/en-us/privacy/eudb/eu-data-boundary-learn) ; un accès à distance depuis un pays tiers est un transfert (CEPD, lignes directrices 05/2021, § 9). Lire ces cas avant de dire T6 conforme à la règle UE seule | 🟠 moyenne |
| 9 | **T1, jeu de démonstration** : la base contient des positions inventées sur des sociétés réellement cotées (déclaration d'Era du 2026-10-10 : il ne détient pas ces titres) ; aligner la fiche T1 et la description du fichier réel `data/positions.csv` | 🟡 basse |
| 10 | **yfinance (Yahoo, États-Unis)** : la requête du soir envoie les 111 tickers suivis et l'adresse IP du poste ; elle ne révèle pas les positions ; à inscrire (ce qui part, où, sous quelle lecture du CEPD) | 🟡 basse |

> 🟠 **Statut des transferts au 2026-10-05 : garanties contractuelles identifiées ; vérification propre à RITA
> incomplète.** Trouver une clause (DPA, clauses contractuelles types) montre qu'une garantie existe, pas que la
> configuration de RITA, ses données réellement envoyées, ses destinataires et leurs sous-traitants, les lieux et les
> durées de traitement la respectent. Avant de conclure qu'un transfert est conforme au RGPD, il faut documenter : les
> contrats qui s'appliquent réellement, les données envoyées (carte #68), les destinataires et sous-traitants, les lieux,
> les durées, et **l'analyse d'impact du transfert (AITD)** quand il repose sur des clauses types : la CNIL l'exige
> dans ce cas (guide AITD, p. 7 : https://www.cnil.fr/sites/cnil/files/2025-02/guide_aitd_pdf.pdf). Exception : un
> destinataire américain **certifié** au Data Privacy Framework relève de la décision d'adéquation (art. 45), sans
> AITD ; la certification se vérifie, elle ne se suppose pas. **Et un transfert licite au regard du RGPD violerait
> quand même la règle UE seule du projet.**

> Un registre qui ne signale aucune faiblesse n'est pas crédible. Ces points (le premier est fait) sont
> ouverts, et ils seront présentés comme tels.

---

## 6. 📖 Glossaire

| Terme | En clair | Pourquoi ça compte ici |
|---|---|---|
| **RGPD** | *Règlement Général sur la Protection des Données* — loi européenne de 2016 sur les données personnelles | Exigé par C4 |
| **GDPR** | Le même, en anglais (*General Data Protection Regulation*) | La doc technique dit « GDPR » |
| **Donnée personnelle** | Toute information se rapportant à une personne identifiée ou identifiable | Tes positions en sont |
| **Traitement** | Toute opération sur une donnée : collecte, stockage, consultation, suppression | Même *lire* est un traitement |
| **Responsable de traitement** | Celui qui décide **pourquoi** et **comment** on traite | Era |
| **Personne concernée** | Celui **dont** on traite les données | Era aussi, ici |
| **Sous-traitant** | Un tiers qui traite pour le compte du responsable | Langfuse GmbH et le groupe ClickHouse (T3) |
| **Base légale** (art. 6) | La justification juridique du traitement — il en faut **une** parmi six | Ici : intérêt légitime |
| **Intérêt légitime** | Base légale : le traitement sert un intérêt réel sans léser la personne | Celle retenue pour RITA |
| **Registre des traitements** (art. 30) | La liste écrite de tous les traitements | Ce document |
| **Minimisation** (art. 5) | Ne collecter que le strict nécessaire | On ne stocke ni nom ni adresse |
| **Limitation de conservation** (art. 5) | Ne pas garder indéfiniment | D'où les durées du §1 |
| **Données sensibles** (art. 9) | Catégories particulières : santé, opinions, origine… | Les données financières **n'en font pas partie** |
| **AIPD / DPIA** | *Analyse d'Impact relative à la Protection des Données* — étude obligatoire si risque élevé | Non requise en mono-utilisateur |
| **CCT / SCC** | *Clauses Contractuelles Types* : contrat modèle de la Commission européenne qui encadre un transfert hors UE | Prévues par le DPA de Langfuse (§ 6.2, T3) et par celui d'OpenRouter (§ 13.2, module 2, T6), relus le 2026-10-05 ; elles exigent une AITD, non faite (§ 5) |
| **AITD** (analyse d'impact des transferts) | Étude écrite des lois du pays de destination et des protections à ajouter | Exigée par la CNIL quand un transfert repose sur des clauses types (T3, T6) |
| **Data Privacy Framework** | Accord UE–États-Unis autorisant certains transferts (2023) | Base possible du transfert T3 si ClickHouse, Inc. est certifiée (le DPF vaut alors décision d'adéquation) ; certification non vérifiée (§ 5, point 7) ; à défaut, ce sont les clauses types du DPA (§ 6.2) |
| **Purge** | Suppression programmée des données trop anciennes | P1 et P2 |
| **Mode simulation** (*dry-run*) | Le script montre ce qu'il ferait, sans le faire | Comportement par défaut de `rgpd_purge.py` |
| **Hook pre-commit** | Script Git qui s'exécute **avant** d'enregistrer un commit | Empêcherait d'ajouter un fichier personnel |
| **PRU** | *Prix de Revient Unitaire* — prix moyen d'achat d'un titre | Donnée personnelle : révèle la plus-value |
| **Règle UE seule** | Aucune donnée personnelle hors de l'Union européenne, même encadrée | Règle d'Era (05/10), plus stricte que le RGPD |
| **Global Standard** (Azure) | Type de déploiement qui peut traiter un appel dans n'importe quelle région Azure | Celui du déploiement Foundry de RITA jusqu'au 09/10 (T6) |
| **Data Zone Standard** (Azure) | Type de déploiement qui traite les appels dans une zone de données, ici l'UE | Celui de RITA depuis le 09/10, `gpt-5.4-dzs-eu` (T6) |
