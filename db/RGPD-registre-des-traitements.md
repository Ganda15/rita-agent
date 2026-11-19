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

**Dernière mise à jour** : 2026-11-19 *(T9 corrigé sur le code relu : la fenêtre de 15 minutes sert à compter les clés refusées, elle ne borne pas la conservation ; une adresse n'est oubliée qu'à son prochain appel après la fenêtre, au-delà de 10 000 adresses suivies ou au redémarrage de l'API ; T9 actif depuis le 2026-11-07)* ; avant : 2026-11-07 *(T9 inscrit avant sa mise en service : l'adresse IP gardée 15 minutes en mémoire par le frein des essais de clé, constat S3)* ; avant : 2026-11-06 *(règle UE précisée par décision d'Era (§ 0) ; T3 décrit aux métadonnées de D9 ; transferts de T3, T6 et T8 vérifiés sur les contrats et sur la liste officielle du Data Privacy Framework)* ; avant : 2026-10-31 *(T6 : la production tournait encore avec `foundry,anthropic,openrouter`, lu dans le conteneur ; ordre par défaut passé à `foundry` (`d1cbb7b`), livré et relu en production : Anthropic et OpenRouter ne sont plus appelés par défaut ; avant, le 2026-10-21 : sprint 4 : T3 actif aussi en production depuis la livraison N12 du 21/10, clés posées par Era, une trace de briefing vérifiée sans prompt ni réponse ; depuis la décision D9 du 20/10, une trace ne garde que des métadonnées, dont la valeur demandée ; T6 et T8 alignés ; avant, le 2026-10-20 : sprint 4, tâche D2 : l'exception dédiée à l'évaluation de T8 nomme aussi `evals/mesurer_question.py` et ses rapports ; avant, le 2026-10-16 : sprint 3, tâche C1 : T7 arrêté (décision D3), date de prise d'effet vérifiée sur le serveur et sur le poste ; corpus d'articles de presse examiné et inscrit ; T8, questions posées dans l'écran de question, inscrit ; avant, le 2026-10-11 : exemption domestique de l'article 2.2.c ajoutée au § 0, à examiner ; intérêt légitime de T1 retenu à titre provisoire, justification à documenter ; avant, le 2026-10-10 : glossaire et suites du 02/10 alignés sur la lecture des contrats du 05/10 : clauses contractuelles types prévues, Data Privacy Framework non vérifié ; avant, le 2026-10-09 : Azure AI Foundry passé en Data Zone Standard EU par Era, région mesurée
Sweden Central sur trois appels réels, T6 partiellement corrigé ; avant, le 2026-10-05 : règle « UE seule » posée par Era ; T1 corrigé : les noms des sociétés détenues partent vers Google News ; T6, fournisseurs du modèle, et T7, requêtes Google News, inscrits ; traces de test supprimées le 04/10 ; le même jour, garanties contractuelles des destinataires relues : identifiées,
vérification propre à RITA incomplète, voir § 5)*

*Mise à jour précédente : 2026-10-02 (T3 devient un traitement actif : Langfuse Cloud, région UE ; P1 et P2 corrigées ; état de `memory_audit` ajouté à T2).*

---

## 0. Le cadre, dit honnêtement

RITA est un **projet personnel mono-utilisateur**. Era est à la fois :

- le **responsable de traitement** — celui qui décide pourquoi et comment les données sont traitées ;
- la **personne concernée** — celui dont les données sont traitées.

Cette situation **n'exonère de rien d'office** : le RGPD s'applique à tout traitement automatisé de
données personnelles, sauf l'exemption de l'**article 2.2.c** (activité « strictement personnelle ou domestique »).
Précision du 11/10 : cette exemption n'est pas invoquée sans avoir été examinée (RITA sert aussi une certification,
présentée à un jury, et s'appuie sur des sous-traitants) ; en attendant, ce registre est tenu comme si le RGPD
s'appliquait. La situation simplifie une chose : il n'y a pas de demande
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
> Corrections après le gel du 15/10 (§ 5). Au 2026-10-16, T7 est arrêté (fiche T7) ; T6 et T3 restent ouverts.
> Au 2026-10-31, les replis de T6 (Anthropic, OpenRouter) sont retirés de l'ordre par défaut et de la production
> (conteneur relu) ; T6 reste ouvert sur le contrat de Microsoft.

> 🇪🇺 **Règle précisée par décision d'Era du 2026-11-06** (`evidence/C8/regle-ue-2026-11-06/README.md`). RITA utilise des services configurés dans leurs
> régions de l'Union européenne. Elle ne promet plus l'absence absolue de transfert hors de l'Union : pour chaque
> sous-traitant, les exceptions prévues par son contrat sont identifiées, leurs garanties vérifiées, et les données
> envoyées limitées au nécessaire. **Pourquoi** : aucun des deux sous-traitants (Microsoft, ClickHouse pour Langfuse) ne
> garantit la lettre de la règle du 05/10, leurs contrats prévoyant des sorties de la région ; une promesse que le contrat
> dément ne protège personne. La règle reste un choix du projet, plus précis que l'exigence du référentiel. Elle ne
> rend aucun critère vert : chaque traitement est vérifié à part (T3, T6, T8 ci-dessous).

> ⚠️ **Ce que ça change si RITA devient multi-utilisateur** : il faudra déterminer et
> documenter la base légale de chaque traitement (le consentement n'est qu'une des possibilités ;
> précision du 11/10), une information des utilisateurs, une procédure de réponse
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
| **Base légale** (art. 6) | **Intérêt légitime** (art. 6.1.f), retenu **à titre provisoire** si le RGPD s'applique (exemption domestique de l'art. 2.2.c à examiner, § 0) : l'intérêt du responsable, qui est aussi l'utilisateur et l'unique destinataire. Sa justification (intérêt, nécessité, mise en balance) reste à documenter (précision du 11/10) |
| **Personnes concernées** | 1 — l'utilisateur |
| **Catégories de données** | Ticker détenu · quantité · prix de revient unitaire (PRU) · date d'achat · devise |
| **Ce que ça révèle** | La **situation financière** : composition du patrimoine, montants investis, plus ou moins-values (précision du 10/10 : au 10/10, la base de développement et de preuve contient uniquement des positions inventées ; quantités et PRU ne décrivent aucun patrimoine réel ; T1 devient un traitement de portefeuille personnel dès le chargement d'un CSV réel) |
| **Support** | Table `position` (PostgreSQL) · fichier CSV source |
| **Destinataires** | Aucun pour les quantités, PRU et dates : elles restent locales. **Jusqu'au 2026-10-15, les noms des sociétés détenues partaient chaque soir vers Google News** (T7, relevé le 2026-10-05 ; ce registre disait « aucun » à tort). T7 est arrêté depuis le 2026-10-16 : plus aucun nom ne sort |
| **Transfert hors UE** | Table et fichier : non. Noms des sociétés détenues : **probable jusqu'au 2026-10-15**, voir T7 (arrêté) |
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

### T3 : Traces d'exécution Langfuse Cloud, région UE : ✅ **ACTIF depuis le 2026-10-02** sur le poste de développement, **et en production depuis le 2026-10-21** (livraison N12)

> ## Mise à jour du 2026-10-21 : où le traçage tourne, et ce qu'il garde
>
> - **Sur le poste depuis le 02/10, en production depuis le 21/10.** Jusqu'au 21/10, le serveur de production n'avait
>   aucune clé Langfuse (manque connu depuis le sprint 2, `docs/sprint-2/README.md`, mesuré le 21/10) : les traces
>   citées depuis le 02/10 viennent du poste. Era a posé les clés le 21/10 ; elles sont actives depuis la livraison N12,
>   et une trace de briefing de production a été ouverte : ni prompt ni réponse (`evidence/sprint-4/README.md`,
>   section « La livraison N12 »).
> - **Métadonnées seules depuis le 20/10** (décision D9 du sprint 4, `docs/sprint-4/SPEC.md`) : une trace ne garde plus
>   ni le prompt ni la réponse du modèle. Restent l'identifiant de requête, **la valeur demandée (le ticker) pour un
>   briefing**, qui peut révéler les valeurs d'intérêt de l'utilisateur, le modèle, le fournisseur, la tentative, les
>   jetons, la durée, le type d'une erreur (jamais son message) et le verdict des garde-fous (`src/traces.py`). La rubrique « Catégories de
>   données » ci-dessous décrit l'état du 02/10.
> - Depuis la livraison N12 (21/10), ces métadonnées partent aussi de la production.

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
| **Catégories de données** | **Depuis le 2026-10-20 (décision D9), des métadonnées seules** : identifiant de requête, valeur demandée pour un briefing, verdict des garde-fous, noms et durées des étapes, fournisseur, modèle, tentative, jetons, type d'une erreur (jamais son message) ; pour une question : statut, motif, longueur et identifiants des articles cités ; attributs techniques du SDK (nom du service, identifiant d'instance) ; jamais le prompt ni le texte produit (`src/traces.py`). **Des métadonnées ne sont pas des données anonymes** : la valeur demandée et l'heure disent ce qui intéresse l'utilisateur, et l'identifiant de requête relie la trace aux journaux du serveur. *Précision du 2026-11-06.* **Du 02/10 au 20/10** : Le prompt envoyé au modèle et sa réponse : ticker, cours, variation, ADTV20, devise, fraîcheur, passages de presse. **Aucune position, aucun PRU, aucune quantité** (mesuré le 28/09 dans `agents/analyst.py`). Malgré cela, les tickers demandés révèlent les valeurs d'intérêt de l'utilisateur. S'y ajoutent le modèle, le fournisseur, l'usage en jetons et le message d'erreur (tronqué à 300 caractères) |
| **Destinataire** | **Langfuse GmbH** (Allemagne), sous-traitant, au sein du groupe ClickHouse. L'addendum applicable est le « ClickHouse Customer Data Processing Addendum » (en vigueur le 10/04/2026) ; contact : privacy@clickhouse.com. Hébergement : AWS `eu-west-1` (Irlande) |
| **Sous-traitants ultérieurs** | Selon la liste publiée par l'éditeur (en vigueur le 10/08/2026) : ClickHouse GmbH (Allemagne), ClickHouse BV (Pays-Bas) et **ClickHouse, Inc. (États-Unis)** |
| **Transfert hors UE** | Les données sont hébergées dans l'UE. **Une entité américaine figure parmi les sous-traitants du groupe.** Relu le 2026-10-05 dans le DPA (https://clickhouse.com/legal/agreements/data-processing-addendum) : **§ 6.1**, pour Langfuse Cloud, les données restent dans la région choisie « except as reasonably necessary to provide the Services or as necessary to comply with the law » ; **§ 6.2**, un transfert hors de l'EEE sans décision d'adéquation est encadré par les clauses contractuelles types. Donc : garantie contractuelle identifiée, **transfert possible par contrat**, conformité RGPD de ce transfert **non vérifiée** (AITD non faite, § 5) ; **non conforme à la règle UE seule** (§ 0), par contrat **Vérifié le 2026-11-06** (`evidence/C8/regle-ue-2026-11-06/README.md`) : DPA en vigueur le 10/04/2026 relu (§ 6.1, 6.2, 6.5) ; **ClickHouse, Inc. est active au Data Privacy Framework** sur la liste officielle (certification du 09/05/2024, échéance du 11/04/2027, données hors RH) : un transfert vers elle relève de la décision d'adéquation (art. 45), sans AITD. Restent : l'exception du § 6.1, non chiffrée ; aucune clause sur l'accès à distance du personnel. Conforme à la règle précisée du 06/11 (§ 0), sous réserve du double contrôle |
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

### T6 : Rédaction du briefing par un modèle fourni : ✅ **ACTIF**, inscrit le 2026-10-05 (premier fournisseur en zone UE depuis le 2026-10-09 ; replis hors UE retirés le 2026-10-31 ; pas encore déclaré conforme à la règle UE seule, contrat de Microsoft à relire)

| Rubrique | Contenu (état relu dans le code le 2026-10-05) |
|---|---|
| **Finalité** | Rédiger en français le briefing d'une valeur demandée par l'utilisateur (`POST /briefing`) |
| **Base légale** | Intérêt légitime |
| **Catégories de données** | Le prompt : ticker demandé, cours, variation, ADTV20, devise, fraîcheur, les 13 indicateurs, passages de presse (`agents/analyst.py`). **Aucune position, aucun PRU, aucune quantité.** Ce qui est personnel malgré tout : **la valeur demandée et l'heure de la demande** disent ce qui intéresse l'unique utilisateur, et chaque appel est rattaché à son compte chez le fournisseur |
| **Destinataires** | **Depuis le 2026-11-14, Azure d'abord, puis Mistral** (adresse européenne, `mistral-large-2512`) si Azure échoue (`LLM_ORDRE=foundry,mistral` sur le serveur ; fiche `docs/lecture-contrat-mistral-2026-11-13.md`). **Du 2026-10-31 au 13/11, Azure seul par défaut** (`LLM_ORDRE=foundry` dans `src/llm.py` et `docker-compose.yml` ; valeur lue dans le conteneur de production après la livraison du 31/10). Jusqu'à cette date, en production, dans l'ordre de la cascade (`src/llm.py`, `LLM_ORDRE`) : 1. **Microsoft Azure AI Foundry**, déploiement **`gpt-5.4-dzs-eu`, Data Zone Standard, zone EUR**, depuis le 2026-10-09 (créé par Era dans le portail ; même modèle `gpt-5.4`) : les appels sont traités dans la zone de données de l'UE ; région mesurée sur trois appels réels faits par le code de RITA : Sweden Central (`evidence/C8/preuve-deploiement-zone-eu-2026-10-09.md`). Jusqu'au 09/10, déploiement **Global Standard** (lu dans le portail le 03/10, `evidence/C7/prix-et-environnement-2026-10-03.md`), qui pouvait traiter un appel dans n'importe quelle région Azure ; 2. **Anthropic** (API directe), société établie aux États-Unis ; 3. **OpenRouter**, point d'entrée général `https://openrouter.ai/api/v1/chat/completions` (`src/llm.py:24`), sans garantie de région |
| **Transfert hors UE** | **Azure : traitement dans la zone UE** depuis le 2026-10-09 (Data Zone Standard EU ; Microsoft reste une société américaine, contrat non relu en détail). **Probable** pour Anthropic et OpenRouter tant qu'ils étaient appelés quand Azure échouait : c'était le cas en production jusqu'au 2026-10-31 (valeur `foundry,anthropic,openrouter` lue dans le conteneur). Depuis, ils ne sont plus dans l'ordre par défaut. **T6 n'est pas encore déclaré conforme à la règle UE seule** (§ 0) : le contrat de Microsoft n'est pas relu en entier (§ 5, point 6) **Vérifié le 2026-11-06** (`evidence/C8/regle-ue-2026-11-06/README.md`) : DPA de Microsoft du 01/11/2026 relu sur les transferts (clauses types de 2021), la localisation, l'usage, les sous-traitants et la conservation ; **Microsoft Corporation est active au Data Privacy Framework** sur la liste officielle (échéance du 31/08/2027). Pour le briefing, aucune position, aucun PRU ni aucune quantité n'est envoyé ; la valeur demandée et l'heure restent personnelles (rubrique « Catégories de données »). Reste : la durée de conservation de l'échantillon des abus. **Mistral, secours depuis le 2026-11-14** : inférence en UE et AELE par l'adresse européenne ; plan de contrôle (compte, clés, facturation) possible hors de la zone ; transferts permis par clauses contractuelles types (DPA, § 8.1) ; fiche `docs/lecture-contrat-mistral-2026-11-13.md` |
| **Garanties contractuelles** (relues le 2026-10-05) | **OpenRouter** (https://openrouter.ai/data-processing-agreement) : § 13.2, clauses contractuelles types, module 2 ; l'option « EU-only » (annexe A) ne s'applique **que si elle est choisie** et passe par l'« EU API », et ne couvre que les « API Payloads » (prompts, réponses), **pas** les données de compte, de facturation ni d'authentification : elle ne suffit donc pas à la règle UE seule. **Microsoft** : clauses contractuelles types proposées par son DPA pour Azure, selon la page officielle (https://learn.microsoft.com/en-us/compliance/regulatory/offering-eu-model-clauses), non relue en détail. **Anthropic** : DPA avec clauses types intégré à ses conditions commerciales pour l'API, selon sa page officielle (https://privacy.claude.com/en/articles/7996862-how-do-i-view-and-sign-your-data-processing-addendum-dpa), non relue en détail. **Vérification propre à RITA incomplète** (§ 5) |
| **Durée de conservation** | Selon chaque fournisseur, **non vérifiée** ; Mistral : 30 jours pour la modération des abus, d'après des résumés tiers (fiche du 13/11), pas encore lue dans le texte |
| **Lien avec T3** | Jusqu'au 20/10, le même prompt et la même réponse étaient tracés dans Langfuse (T3), depuis le poste ; depuis la décision D9 (20/10), seules des métadonnées ; depuis la livraison N12 (21/10), elles partent aussi de la production |
| **Inventaire champ par champ** | À faire : carte #68 (tableau champ, origine, destinataire, durée, et un test qui échoue si le prompt contient un champ hors liste) |
| **Correction prévue** (après le gel du 15/10, carte #82) | Ne garder que des fournisseurs approuvés (plan au 10/10, branche `mistral-ue`, PR #88) : Azure AI Foundry en Data Zone Standard EU en premier ; Mistral Large 4 par son adresse européenne en secours, à confirmer par la lecture de son contrat et par le banc C7 ; Anthropic et OpenRouter retirés de la cascade. **Aucun repli vers un fournisseur non approuvé** : sans fournisseur approuvé, l'écran montre les faits et dit « briefing indisponible » (réponse 503 `AUCUN_FOURNISSEUR` prévue par `docs/conception/frontend/refonte-2026-10.md`, § 6). **Fait le 2026-10-31 pour le retrait** : Anthropic et OpenRouter sortis de l'ordre par défaut (commit `d1cbb7b`), production relue ; restent Mistral (contrat, banc C7, PR #88) et la réponse 503, encore 500 au 31/10 (503 `AUCUN_FOURNISSEUR` depuis le 04/11). **14/11/2026** : Mistral codé en secours (Large 3, `mistral-large-2512`, adresse européenne écrite dans le code), **éteint par défaut**, allumé seulement par `LLM_ORDRE=foundry,mistral` sur le serveur, après le refus de la clé Azure (HTTP 401) le 13/11. Contrat lu le 13/11 (`docs/lecture-contrat-mistral-2026-11-13.md`) : inférence en UE et AELE ; plan de contrôle (compte, clés, facturation) possible hors de la zone ; Mistral responsable de traitement pour la modération des abus (DPA, § 2.3) ; conservation 30 jours sans rétention zéro, d'après des résumés tiers, non lue dans le texte (ligne « Durée de conservation ») ; transferts permis par clauses contractuelles types (DPA, § 8.1). Avant l'allumage, quatre vérifications par Era (fiche, « Verdict proposé ») |

### T7 : Recherche d'actualités sur les valeurs détenues (Google News) : ⛔ **ARRÊTÉ le 2026-10-16** (décision D3), en service du 2026-08-28 au 2026-10-15, inscrit le 2026-10-05

| Rubrique | Contenu (état relu dans le code le 2026-10-05 ; arrêt ajouté le 2026-10-16) |
|---|---|
| **Arrêt et raison** | Décision D3 du sprint 3 : le nom des sociétés du portefeuille ne doit plus sortir vers Google, et T7 ne respectait pas la règle UE seule (§ 0). Code (sprint 3, tâche B1) : la collecte ne lit plus que les trois flux généraux de `FLUX` (`sources/rss.py`) et ne lit plus la table `position` ; au commit `72dba4d`, `git grep "news.google.com" -- sources pipelines` ne rend rien. Les flux généraux restent (voir « Corpus d'articles de presse ») |
| **Prise d'effet sur le poste** | La tâche planifiée « RITA - collecte quotidienne » exécute le dossier `D:\KandaWork\RITA_PROJECT\rita-agent`. Dernière collecte avec Google News : 2026-10-15 à 19:00 (manifeste du poste, commit `b586072`, « flux OK 9/10 (dont 7 par entreprise) »). Tâche suspendue le 2026-10-16 au matin (`evidence/sprint-3/suspension-collecte-2026-10-16.txt`), dossier passé au commit `72dba4d` le 2026-10-16 à 21:58, tâche réactivée, première collecte le 2026-10-16 à 22:01:39 : `evidence/sprint-3/manifeste-poste-2026-10-16-220139.json` (commit `72dba4d`, « flux OK 3/3 »), preuve complète dans `evidence/sprint-3/reprise-collecte-2026-10-16.txt`. Complément : dans la base locale `rita`, 0 article `ent_%` collecté à partir du 2026-10-16 ; le dernier date du 2026-10-15 à 19:00:37 (requête en lecture, compte `rita`) |
| **Prise d'effet sur le serveur** | L'ordre `ingerer` existe depuis la livraison N5 (2026-10-16, 18:59, commit `41b1763`), dont le code est déjà sans Google News. D'après le journal des opérations du serveur (`evidence/sprint-3/journal-serveur-2026-10-16.jsonl`), la première ingestion date du 2026-10-16 à 19:04 ; elle s'est arrêtée avant d'écrire (`manifeste-2026-10-16-170439.json`, `FeatureNotFound: lxml`). Première collecte réussie : 2026-10-16 à 21:08, `evidence/sprint-3/manifeste-2026-10-16-190839.json` (« flux OK 3/3 », 29 articles écrits), sur l'image de la livraison N6 (commit `72dba4d`, relevé par `/health` ; le manifeste écrit dans l'image ne porte pas de commit, Git n'y étant pas). Le comptage des articles `ent_%` dans la base de production n'a pas été fait |
| **Sort des articles déjà collectés** | Ils sont conservés dans le corpus, avec leur origine notée : `source` vaut `ent_<société>` et le lien pointe vers `news.google.com`. 675 articles sur 2052 dans la copie de production du 2026-10-16 (voir « Corpus d'articles de presse ») |
| **Finalité** | Collecter chaque soir les articles de presse sur les sociétés du portefeuille |
| **Base légale** | Intérêt légitime |
| **Catégories de données** | **Le nom de chaque société présente dans la table `position`** (positions closes comprises : `SELECT DISTINCT v.nom_officiel FROM position p JOIN valeur v`, `pipelines/ingest.py:283-289`), placé dans l'adresse d'une requête Google News avec le mot « bourse » et une fenêtre de dates (`sources/rss.py:56-89`) ; l'adresse IP du poste |
| **Ce que ça révèle** | **La composition du portefeuille**, sans les quantités ni les montants (précision du 10/10 : la base ne contient aujourd'hui que des positions simulées sur des sociétés cotées ; Google reçoit ces noms et l'adresse IP, et recevrait la composition d'un vrai portefeuille dès qu'il serait chargé) |
| **Destinataire** | Google, service Google News (`news.google.com`) ; entité qui traite et lieu de traitement **non vérifiés** |
| **Transfert hors UE** | **Probable, non vérifié. Non conforme à la règle UE seule** (§ 0) |
| **Fréquence** (jusqu'au 2026-10-15) | Chaque soir à 19 h (collecte planifiée) : une requête par société détenue (10 flux le 03/10 : 3 généraux et 7 par société) |
| **Écart de méthode** | Codé le 28/08 (commit `66ea9f9`) **sans inscription préalable** dans ce registre, alors que la procédure M1 demande d'inscrire un traitement **avant** de le coder. Relevé le 05/10 par une relecture extérieure, confirmé dans le code |
| **Correction faite** (carte #81, sprint 3) | Les requêtes dérivées des positions sont **supprimées**, sans liste de veille de remplacement : la collecte garde les trois flux généraux. Une liste de veille indépendante des positions reste possible plus tard, auprès de sources approuvées |

### T8 : Questions posées dans l'écran de question (`POST /question`) : ✅ **ACTIF depuis le 2026-10-16** (livraison N5), inscrit le 2026-10-16

| Rubrique | Contenu (état relu dans le code le 2026-10-16, commit `72dba4d`) |
|---|---|
| **Finalité** | Répondre à une question libre à partir du corpus d'articles, avec les références des articles cités, ou refuser de répondre (écran `question.html`, route `POST /question`) |
| **Base légale** | Intérêt légitime, retenu à titre provisoire comme pour T1 (§ 0) |
| **Personnes concernées** | Qui pose une question avec la clé d'API : Era, et les personnes à qui il la confie (évaluateurs) |
| **Catégories de données** | Le texte de la question, qui peut contenir ce que le visiteur choisit d'y écrire, y compris une donnée personnelle ; les passages d'articles transmis au modèle ; la réponse générée ; l'adresse IP et l'heure de la requête, comme pour toute requête HTTP (journal du serveur web non relu) |
| **Ce que RITA conserve** | Pour le parcours `/question`, le texte de la question et celui de la réponse : **jamais conservé** par RITA dans ses stockages et ses traces applicatifs, ni en base, ni dans ses journaux, ni dans ses traces, y compris en cas d'erreur (spec du sprint 3, CA4.3, décision D2 ; prouvé par `tests/test_api_question.py` et `tests/test_traces_question.py`). Ce qui est gardé : dans le journal de l'API, une ligne par question avec l'identifiant de la requête, le statut, le motif, la longueur de la question, les identifiants des articles cités, la durée et l'heure ; dans les traces (T3), les mêmes métadonnées (statut, motif, longueur, identifiants), le texte étant masqué ; en production, ces traces ne partent que si les clés Langfuse sont posées sur le serveur (aucune au sprint 2, non revérifié le 2026-10-16). **Exception dédiée à l'évaluation** : les outils `evals/evaluer_reponses.py` (sprint 3) et `evals/mesurer_question.py` (sprint 4, jeu élargi aux questions hostiles, aux questions légitimes et aux reformulations réservées), lancés volontairement par Era sur le jeu de questions de démonstration, enregistrent les questions et les réponses dans des rapports JSON, pour la relecture ; les rapports retenus sont conservés et versionnés dans `evidence/` (au 2026-10-16 : `evidence/sprint-3/evaluation-2026-10-16-*.json` ; au 2026-10-20 : `evidence/sprint-4/mesure-question-niveau2-2026-10-20-*.json`) |
| **Destinataire** | Microsoft Azure AI Foundry, déploiement `gpt-5.4-dzs-eu` en Data Zone Standard, zone UE, premier fournisseur de ce parcours. Jusqu'au 13/11, seul, sans repli (spec CA2.4) ; depuis le 14/11, **Mistral** (adresse européenne) peut répondre si Azure échoue, seulement si `LLM_ORDRE` le nomme (même conditions que T6) ; Anthropic et OpenRouter ne répondent jamais à une question (`src/llm.py`, `FOURNISSEURS_DES_QUESTIONS`). Langfuse Cloud, région UE, pour les métadonnées (T3), actif en production depuis la livraison N12 (21/10) |
| **Transfert hors UE** | Traitement dans la zone de données de l'UE. Microsoft reste une société américaine : même réserve que T6 (§ 5, point 8). **Vérifié le 2026-11-06** (`evidence/C8/regle-ue-2026-11-06/README.md`) : mêmes garanties que T6 (DPA du 01/11/2026, Microsoft active au Data Privacy Framework). **Reste un écart à la règle précisée** : l'écran Question ne demande pas de taire les données personnelles, et le texte libre part tel quel vers Azure : les données envoyées ne sont pas limitées au nécessaire pour ce parcours (§ 5, point 13). **Mistral, secours depuis le 2026-11-14** (seulement si `LLM_ORDRE` le nomme) : mêmes réserves que T6, inférence en UE et AELE, plan de contrôle possible hors de la zone |
| **Ce que Microsoft conserve** (documentation relue le 2026-10-16 : https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy et la page « abuse monitoring » qu'elle cite) | Le modèle ne garde pas les questions ni les réponses, et elles ne servent pas à l'entraîner. RITA n'utilise aucune fonction de stockage d'Azure : le paramètre `store` n'est jamais envoyé (`src/llm.py`), ni l'API Responses ni les assistants ne sont appelés. En zone de données UE, le traitement peut avoir lieu dans tout État membre. **Surveillance des abus** : une revue automatique, sans stockage ; un échantillon signalé peut être conservé pour une revue humaine, « stored in the Azure geography where the customer's Foundry resource is deployed » (ici en Europe : la même page réserve le déploiement en zone de données UE aux ressources situées dans un État membre ; région exacte de la ressource non relue, région de traitement mesurée Sweden Central, T6), et relu par des employés de Microsoft situés dans l'Espace économique européen pour un déploiement dans l'EEE. **La durée de cette conservation n'est pas donnée par les deux pages relues.** Une surveillance modifiée, sans stockage ni revue humaine, existe sur demande et sous conditions d'accès ; RITA ne l'a pas demandée |
| **Durée de conservation** | Texte, parcours `/question` : aucune chez RITA. Rapports d'évaluation (exception ci-dessus) : versionnés dans `evidence/`, gardés aussi longtemps que le dépôt. Journal de l'API : tant que le conteneur existe ; il est remplacé à chaque livraison et à chaque ingestion (`docker compose up`), et aucune rotation n'est réglée dans les fichiers Compose du dépôt (réglage du démon Docker du serveur non vérifié). Traces : 30 jours (Langfuse, palier gratuit, T3). Chez Microsoft : voir la ligne précédente. Chez Mistral (secours depuis le 2026-11-14) : 30 jours sans rétention zéro d'après des résumés tiers, non vérifiés dans le texte (T6) |
| **Sécurité** | Route protégée par la clé d'API (403 sans clé) ; texte retiré des journaux et des traces par construction, vérifié par les tests cités |
| **Droits** | Pour le parcours `/question`, le texte n'étant pas conservé, il n'y a rien à rendre ni à effacer chez RITA ; un rapport d'évaluation se retire de `evidence/` par un commit (il reste dans l'historique Git) ; les métadonnées se retrouvent par l'identifiant de la requête (journaux) ou dans Langfuse (T3) quand le traçage est actif |

### T9 : Frein des essais de clé (adresse IP en mémoire) : inscrit le 2026-11-07 avant sa mise en service, **actif depuis le 2026-11-07** (constat S3, plan validé par Era le 07/11 ; vérifié en production le 07/11, `evidence/C17/verification-production-2026-11-07/`)

| Rubrique | Contenu (état écrit dans le code le 2026-11-07, `api/limiteur.py`, `FreinDesEssais` ; relu le 2026-11-19) |
|---|---|
| **Finalité** | Sécurité du service : au-delà de 10 clés d'API refusées en 15 minutes depuis une même adresse, l'API répond 429 à cette adresse au lieu de comparer la clé (OWASP API4:2023) |
| **Base légale** | Intérêt légitime du responsable : la sécurité du service ; un compteur unique pour tous laisserait n'importe qui bloquer le service en envoyant de fausses clés |
| **Personnes concernées** | Qui envoie une clé d'API fausse : un visiteur qui se trompe, Era compris, ou un tiers qui essaie des clés |
| **Catégories de données** | L'adresse IP vue par l'API (celle que Caddy écrit dans `X-Forwarded-For`) et l'heure de chaque clé refusée. Une clé absente ou juste ne laisse rien. **Jamais** : la clé envoyée, ni un morceau |
| **Support** | La mémoire du processus de l'API seulement : aucune table, aucun fichier ; la ligne de journal d'un blocage n'écrit ni l'adresse ni la clé (test `tests/test_essais_de_cle.py`) |
| **Durée de conservation** | En mémoire seulement ; les clés refusées sont comptées sur une fenêtre de 15 minutes ; une adresse est oubliée à son prochain appel après la fenêtre, au-delà de 10 000 adresses suivies (la plus anciennement vue d'abord), ou au redémarrage de l'API. **Limite** : une adresse qui ne rappelle pas reste en mémoire jusqu'au redémarrage ou jusqu'à ce que 10 000 autres la poussent dehors ; il n'y a pas de durée maximale garantie (`api/limiteur.py`, `_recents`, lignes 108 à 118) |
| **Destinataire** | Aucun ; rien ne sort du serveur |
| **Transfert hors UE** | Aucun : serveur Hetzner à Falkenstein, en Allemagne (centre `fsn1`, lu dans le nom de la machine le 2026-11-07) |
| **Droits** | Rien n'est écrit sur disque ni dans le journal, donc rien à rendre ; l'effacement immédiat se fait en redémarrant l'API ; sans redémarrage, l'adresse est oubliée à son prochain appel une fois la fenêtre de 15 minutes passée |

### Corpus d'articles de presse (table `article`) : examiné le 2026-10-16, inscrit comme traitement accessoire

Examen fait sur la copie locale de la production du 2026-10-16 (base `rita_sprint3`, compte en lecture seule
`rita_lecture`), qui contient les 2052 articles servis avant la première ingestion ; l'ingestion du 16/10 en a ajouté 29,
tous venus des trois flux généraux.

**Les sources** (spec CA4.1) :

| Source | Nature | Finalité | Ce qui rend l'usage licite | Articles au 2026-10-16 |
|---|---|---|---|---|
| `bfm_eco` | Flux RSS public de BFM, rubrique économie (https://www.bfmtv.com/rss/economie/) | Actualité économique générale, citée dans les réponses | Flux publié par l'éditeur pour être repris par des lecteurs de flux ; RITA ne garde que le titre, le résumé du flux, le lien et la date, et chaque citation renvoie à l'article de l'éditeur | 442 |
| `latribune` | Flux RSS public de La Tribune (https://www.latribune.fr/feed.xml) | Idem | Idem | 474 |
| `lemonde_eco` | Flux RSS public du Monde, rubrique économie (https://www.lemonde.fr/economie/rss_full.xml) | Idem | Idem | 461 |
| `ent_<société>` | Anciennes requêtes Google News par société (T7, arrêté le 2026-10-16) ; liens `news.google.com`, éditeur réel noté à la fin du titre | Actualité des sociétés suivies | Mêmes champs que ci-dessus ; plus aucune collecte depuis l'arrêt de T7 ; conservés, origine notée | 675 |

Limite : les conditions de réutilisation propres à chaque éditeur ne sont pas relues (§ 5).

**Les champs réellement indexés** (spec CA4.2) : le texte vectorisé est le titre puis le résumé du flux
(`texte_indexable`, `rag/indexation.py`) ; les métadonnées gardées avec lui sont la source (l'éditeur), le titre, le
flux, le lien, la date de publication et les valeurs suivies citées. La table `article` n'a pas de colonne d'auteur :
**aucun auteur n'est collecté**, ni l'article complet.

**Les personnes qui peuvent y être nommées** : dirigeants d'entreprise, responsables politiques, banquiers centraux,
économistes ou analystes cités dans un titre ou un résumé. Mesure du 2026-10-16 : 305 des 2052 articles citent une
fonction de personne (PDG, président, ministre, directeur, économiste, analyste, « M. », « Mme »…) dans leur titre ou
leur résumé. C'est un repérage par mots-clés, une indication et non un décompte des personnes. Des données publiées
dans la presse restent des données personnelles, et leur réutilisation reste soumise au RGPD (CNIL,
https://www.cnil.fr/fr/recommandations-reutilisateurs-donnees-internet) : la non-applicabilité n'est donc pas
retenue, et le corpus est inscrit ici comme un traitement accessoire.

**Nécessité** : le nom fait partie du fait rapporté (« le PDG annonce… ») ; le retirer déformerait l'information citée.
RITA ne s'en sert pas pour décrire une personne : aucune recherche par personne, aucune fiche, aucun croisement.

**Mesures de minimisation** : aucun champ de personne ; aucun auteur ; aucun enrichissement ; seul le résumé publié dans
le flux, jamais l'article complet ; les articles bloqués par le garde-fou d'injection (`bloque_injection`) ne sont jamais
indexés (aucun dans la copie du 2026-10-16) ; le texte des questions n'est pas conservé (T8).

**Ce que les anciens articles Google News révèlent** : leur `source` porte le nom d'une société de la table `position`
(`ent_<société>`). Le corpus laisse donc deviner la composition du portefeuille, aujourd'hui simulé (T1). Depuis la
livraison N6, la fiche d'un article (`GET /donnees/articles/{id}`, protégée par la clé) montre ce nom dans le champ
`flux`.

**Base légale** : intérêt légitime (information économique des réponses), retenu à titre provisoire (§ 0).

**Durée de conservation** : **aucune limite aujourd'hui**. Aucune purge ne vise la table `article` (§ 2) : les articles
restent tant que la base existe. Ce point est ouvert (§ 5).

### Ce qui **n'est pas** un traitement de données personnelles

| Donnée | Pourquoi |
|---|---|
| `cotation`, `valeur`, `alias_valeur` | Cours de bourse — **données publiques**, aucune personne identifiable |
| `taux_change` | Taux BCE — donnée publique |

La table `article` figurait ici jusqu'au 2026-10-16 ; elle est examinée et inscrite dans « Corpus d'articles de presse »
ci-dessus.

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
| **M2** | Vérifier que le dépôt public ne contient aucune donnée personnelle | **Avant chaque passage en public** | ⚠️ Au 16/11 : publication prévue le 23/11. Contrôle en lecture seule du 16/11 : aucune adresse de courriel personnelle ni numéro de téléphone dans les fichiers suivis. Audit en lecture seule du 13/11 (`ETAT.md`) : seuls secrets, les deux clés révoquées d'INC-008 ; restent visibles l'historique d'avant le 27/10 et l'adresse d'auteur des commits ; noms de personnes tierces remplacés par leur rôle dans les documents de l'état actuel le 16/11, gardés dans les preuves datées |
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
| **Limitation** | 18 | Sans objet tant que la personne concernée est le responsable ; les destinataires extérieurs sont listés en T3, T6, T7 (arrêté) et T8 |
| **Opposition** | 21 | Sans objet : la personne concernée est le responsable de traitement |

---

## 5. Ce qui reste à faire — dit franchement

| # | Action | Criticité |
|---|---|---|
| 1 | ~~Choisir l'outil de monitorage avant d'activer le traçage (T3)~~ **Fait : Langfuse Cloud UE choisi le 28/09, activé le 02/10 ; traces de test supprimées le 04/10 ; DPA relu le 05/10 (§ 6.1 et § 6.2).** Reste : décider si T3 est gardé malgré la règle UE seule (le contrat permet un traitement hors région), ou remplacé (auto-hébergement, autre outil) | 🟠 moyenne |
| 2 | **Hook Git `pre-commit`** interdisant l'ajout d'un fichier personnel (P4) | 🟠 moyenne |
| 3 | Brancher P1 et P2 sur APScheduler (aujourd'hui : lancement manuel) | 🟠 moyenne |
| 4 | Chiffrer la sauvegarde de la base si elle sort de la machine | 🟡 basse tant que tout est local |
| 5 | ~~**T7 (carte #81) : arrêter d'envoyer à Google News les noms des sociétés détenues**~~ **Fait le 2026-10-16** (sprint 3, décision D3) : requêtes par société supprimées, prise d'effet vérifiée sur le poste et sur le serveur (fiche T7). Reste : compter les articles `ent_%` collectés après le 2026-10-16 dans la base de production | ✅ fait ; 🟡 basse pour le comptage |
| 6 | **T6 (cartes #82 et #68) : n'appeler que des fournisseurs de modèle approuvés UE**, sans repli vers un fournisseur non approuvé ; **fait le 2026-10-09 pour le premier fournisseur** (Azure en Data Zone EU, région mesurée) ; replis Anthropic et OpenRouter **retirés le 2026-10-31** (ordre par défaut `foundry`, production relue) ; reste : Mistral en second (plan du 10/10 : `LLM_ORDRE=foundry,mistral` sur la branche `mistral-ue`, Mistral Large 4 après lecture de son contrat et banc C7 ; test et réponse 503 déjà spécifiés), relire en entier le contrat de Microsoft | 🟠 moyenne : depuis le 31/10, aucun repli hors UE par défaut ; reste le contrat de Microsoft |
| 7 | **Transferts hors UE (T3, T6)** : pour chaque destinataire, vérifier la certification au Data Privacy Framework ; à défaut, faire l'**analyse d'impact du transfert (AITD)** exigée par la CNIL pour les clauses types ; documenter contrats applicables, données envoyées, sous-traitants, lieux et durées | 🟠 moyenne pour le RGPD ; sans effet sur la règle UE seule, qui interdit le transfert de toute façon |
| 8 | **T6, Azure** : Microsoft documente des cas limités de transfert hors de son EU Data Boundary, dont l'accès à distance de son personnel (https://learn.microsoft.com/en-us/privacy/eudb/eu-data-boundary-learn) ; un accès à distance depuis un pays tiers est un transfert (CEPD, lignes directrices 05/2021, § 9). Lire ces cas avant de dire T6 conforme à la règle UE seule | 🟠 moyenne |
| 9 | **T1, jeu de démonstration** : la base contient des positions inventées sur des sociétés réellement cotées (déclaration d'Era du 2026-10-10 : il ne détient pas ces titres) ; 12 lignes dans le fichier d'exemple, 10 gardées par le lecteur, 7 importées (3 hors univers) ; T1 aligné le 10/10 ; reste à documenter comment le fichier local non versionné `data/positions.csv` a été constitué | 🟡 basse |
| 10 | **yfinance (Yahoo, États-Unis)** : la requête du soir envoie les 108 valeurs encore cotées (les 3 radiées ne sont plus demandées) et l'adresse IP du poste ; elle ne révèle pas les positions ; à inscrire (ce qui part, où, sous quelle lecture du CEPD) | 🟡 basse |
| 11 | **Corpus d'articles** : fixer une durée de conservation et la purge qui l'applique (aucune limite aujourd'hui) ; décider du sort des 675 articles `ent_%`, dont la source laisse deviner la composition du portefeuille ; relire les conditions de réutilisation de chaque flux | 🟠 moyenne |
| 12 | **T8, Azure** : la durée de conservation de l'échantillon gardé pour la revue humaine des abus n'est pas donnée par la documentation relue le 2026-10-16 ; la surveillance modifiée (sans stockage) n'est pas demandée ; le journal du serveur web (adresse IP, heure) n'est pas relu | 🟡 basse : seul un échantillon signalé est gardé, dans la géographie de la ressource |
| 13 | **T8, écran Question** : écrire sous le champ de la question de ne pas y mettre de donnée personnelle (nom, adresse, numéro), puisque le texte part vers Azure ; test d'abord. Seul écart restant de T8 à la règle précisée du 06/11 (`evidence/C8/regle-ue-2026-11-06/README.md`) | 🟠 moyenne |

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
| **Base légale** (art. 6) | La justification juridique du traitement — il en faut **une** parmi six | Ici : intérêt légitime, retenu à titre provisoire (§ 0, T1) |
| **Intérêt légitime** | Base légale (art. 6.1.f) : un intérêt réel du responsable ou d'un tiers, un traitement nécessaire, et une mise en balance qui ne lèse pas la personne | Retenue à titre provisoire pour RITA ; justification à documenter |
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
