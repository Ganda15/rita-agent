# Sprint 3 : les données et l'ancrage

Document d'entrée du sprint 3 du fil rouge RITA. Il dit où voir chaque critère de la grille de l'atelier 3, ce qui a
été livré et mesuré, et ce qui n'est pas fait.

- **Production** : <https://178-104-184-125.sslip.io> (serveur Hetzner). `/health` annonce le commit servi et
  l'identité de l'index (nombre d'articles, identifiant maximal, empreinte du contenu, identifiant de construction).
  L'écran de question est `/question.html` ; il demande la clé d'API.
- **Conception** : la spec `docs/sprint-3/SPEC.md` et le plan de travail `docs/sprint-3/PLAN-TRAVAIL.md`.
- **Preuves** : index dans `evidence/sprint-3/README.md` ; récit des livraisons et de l'ingestion du 16/10 dans
  `docs/sprint-3/COMPTE-RENDU-N5-2026-10-16.md`.
- **Registre RGPD** : `db/RGPD-registre-des-traitements.md` (T7 arrêté, T8 inscrit, corpus d'articles examiné).

## Ce que la grille demande, et où le voir

| Critère | Où le voir |
|---|---|
| 1. Sources licites | Registre RGPD : section « Corpus d'articles de presse » (les sources, leurs champs, la minimisation) ; fiche T7 (Google News arrêté le 16/10, date vérifiée sur le serveur et sur le poste) ; fiche T8 (le texte des questions n'est jamais conservé). Décisions D2 et D3 dans la spec |
| 2. Traçabilité | `POST /question` rend la réponse et ses références (titre, éditeur, date, lien, extrait transmis au modèle), construites depuis les données stockées et jamais depuis le texte du modèle (`agents/question.py`) ; la fiche d'une source, `GET /donnees/articles/{id}` (`api/donnees.py`) ; l'écran `frontend/question.html`. Évaluation en production : `evidence/sprint-3/evaluation-production-2026-10-16-relecture.md` |
| 3. Refus hors corpus | Règle de pertinence de la recherche (`rag/recherche.py`) ; refus sans appel au modèle pour une question hors corpus ou une demande de conseil d'achat, abstention quand les passages ne suffisent pas, citations contrôlées (`agents/question.py`) ; questions Q6 à Q8 du jeu, refusées en production |
| 4. Pipeline rejouable | Bouton « Ingestion » (`.github/workflows/ingestion.yml`) et ordre `ingerer` du script du serveur (`deploy/deployer.py`) : collecte, nouvel index à part, pré-test, rejeu des questions, bascule, identité vérifiée. Relancée le 16/10, la collecte relit les mêmes 30 articles et n'en écrit aucun : `evidence/sprint-3/manifeste-2026-10-16-192124.json`. Mode d'emploi : `docs/EXPLOITATION.md`, § 8 |
| 5. En production | Livraisons N5 et N6, deux ingestions, évaluation : tout sur l'adresse déployée, version lue dans `/health` (captures et journaux dans `evidence/sprint-3/`) |
| Livrable : questions de démonstration | `rag/questions_demo.json` (version 2) et son rejeu `rag/controle_questions.py` ; rapports de rejeu dans `evidence/sprint-3/` |
| Journal des retours | Livrable, § 8 ; retours de l'atelier 3 (19/10, oraux, grille non remplie) : `eval/ateliers/sprint-3-grille.md` |

## Les livraisons du sprint (16 au 19/10/2026, mesurées)

- **N5** (PR #101, commit `41b1763`) : livrée à 18:59 ; rejeu des 8 questions sans écart avant la bascule ; index
  servi `d2d029d7…`, 2052 articles.
- **Première ingestion** : arrêtée à la collecte sur `FeatureNotFound: lxml` (bibliothèque présente sur le poste,
  absente de l'image). Aucun article écrit, index servi inchangé : le garde-fou a joué son rôle.
- **N6** (PR #103, commit `72dba4d`) : collecte sans `lxml`, essai du nettoyage RSS dans l'image avant publication,
  fiche qui nomme la même source que la référence, repères complets dans le jeu, dates en UTC dans l'empreinte de
  l'index. Première tentative arrêtée avant le serveur par un 429 du registre d'images, seconde livrée à 21:05 ;
  index reconstruit avec la même empreinte de contenu que celui de N5.
- **Ingestions** : à 21:08, 29 articles écrits (2052 à 2081) ; à 21:21, aucun (dédoublonnage). Rejeux sans écart.
- **Évaluation en production** : sur ce passage, 8 sur 8 conformes aux contrôles du jeu ; 3 faits sur 9 retrouvés
  automatiquement ; aucune affirmation non soutenue selon la relecture d'Era.
- **Collecte du poste** : reprise sur le code de N6, sans Google News (première collecte à 22:01, 6 étapes sur 6).
- **N7** (PR #105, commit `66963da`) : les caractères de contrôle du texte du modèle remplacés par une espace (relevé
  par l'évaluation en production), avec les documents de fin de sprint ; livrée à 22:10 UTC, vert du premier coup,
  même empreinte d'index.
- **N8** (PR #107, commit `7f2a855`) : le livrable version 1 ; en production 40 min 31 s après la fusion, trois
  tentatives arrêtées par un 429. Tag `livrable-sprint-3-v1` posé le 18/10 sur ce commit.
- **Ingestions du 18 et du 19/10** (passages `39115076808` et `39265862974`) : réussies ; la seconde lancée en direct
  pendant l'atelier, 2110 puis 2140 articles.
- **Livrable** : `docs/sprint-3/livrable/livrable-sprint-3.pdf`, version 2 (16 pages, après l'atelier du 19/10) ; la
  version 1 (10 pages, validée par Era le 17/10) reste au tag `livrable-sprint-3-v1`. Quatre captures de
  production : `evidence/sprint-3/captures/`.

## Ce qui n'est pas fait

- **Atelier 3 sans grille** : la grille n'a pas été remplie ; les retours, oraux, et leur suite sont dans
  `eval/ateliers/sprint-3-grille.md`.
- **Aucune capture du refus d'une demande de conseil d'achat** (`INTENTION_INTERDITE`) : ce refus est prouvé par
  l'évaluation en production du 16/10 ; les captures du 17/10 montrent une réponse citée, sa fiche et un refus hors
  corpus.
- **Construction de l'image fragile** : l'image de base est téléchargée sans authentification depuis
  `public.ecr.aws` ; onze constructions ont échoué sur un 429 du 16 au 18/10, chaque fois relancées à la main.
- **Le manifeste écrit sur le serveur ne porte pas le commit** (`"commit": null`, Git n'est pas dans l'image).
- **L'outil d'évaluation charge la clé locale** : ses imports lisent le `.env` du poste ; sans `RITA_API_KEY` dans
  la session, la clé locale part vers l'adresse donnée en argument. Relevé le 16/10, non corrigé.
- **Corpus** : aucune durée de conservation ; les 675 anciens articles Google News ont une source au nom d'une
  société du portefeuille (simulé), que le champ `flux` de la fiche montre ; le comptage des articles Google News
  collectés après le 16/10 n'est fait que sur le poste, pas dans la base de production (registre, § 5).
- **T8** : la durée pendant laquelle Microsoft garde un échantillon pour la revue des abus n'est pas documentée ; le
  journal du serveur web n'est pas relu ; la présence des clés Langfuse sur le serveur, donc des traces de
  métadonnées en production, n'est pas revérifiée (aucune clé au sprint 2).
- **Le jeu de questions reste lié à l'index local** sur lequel il a été mesuré (`18c122a9…`, empreinte calculée
  avant la correction du fuseau).
- **Le seuil de pertinence (0,42)** reste calibré sur 9 questions.
- **Faits retrouvés automatiquement : 3 sur 9 en production.** Les réponses donnent le fait principal et omettent des
  détails ; la fidélité est jugée par la relecture, pas par ce comptage.
- `sources/scraper.py` utilise encore `lxml` ; l'ingestion du serveur ne l'appelle pas.
- Le schéma `docs/rapports/E1/schemas/E1-collecte` garde un texte daté du 4 octobre qui décrit encore les flux Google
  News (rapport E1 déjà rendu).
- Le livrable du sprint 2 contient 12 liens vers le dépôt, privé, qui répondent 404 sans connexion.
