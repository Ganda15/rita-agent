# Journal des livrables et décisions — RITA

> **Append-only** : on ajoute en haut, on ne réécrit **jamais** une entrée passée.
> Le présent est dans `ETAT.md` · le pourquoi détaillé dans le journal Obsidian ·
> le détail technique dans `git log`.
>
> **Une entrée = un livrable envoyé, une décision structurante, ou un manque découvert.**
> Pas les commits de code : Git les garde mieux, horodatés et infalsifiables.

---

## 2026-08-16 — Le plan des 12 semaines, et comment travailler sans le relecteur

- **Décision structurante — on n'attend plus la validation pour avancer.** Le formateur est
  en congé. Sa règle (*une compétence prouvée → envoyée → puis la suivante*) existe pour
  empêcher d'empiler du travail non relu ; **elle ne dit pas d'attendre un absent**. Règle
  appliquée désormais : **produire → geler → mettre en file → continuer**, avec envoi **un
  par un** à son retour. *Ce qui se reproche, c'est de n'avoir jamais cherché la validation.*
- **Ajouté** `docs/FILE-DE-VALIDATION.md` — la file des livrables gelés en attente de revue.
  **3 en file au 16/08, 0 envoyé** : E1, le protocole C6, la conception des indicateurs.
- **Ajouté** `docs/PLAN-12-SEMAINES.md` — le calendrier S34 → S45. Deux décisions le
  structurent :
  - **Les 13 compétences restantes sont 4 chantiers, pas 13 tâches.** L'application porte à
    elle seule **7 compétences** (C10 + C14–C19) : `frontend/` est vide, et un seul artefact
    prouve l'interface *et* tout E4. **C'est le pari du plan** — s'il échoue, le plan échoue.
  - **Le temps d'Era n'est pas homogène.** La semaine de vacances (S34) va au chantier long ;
    les créneaux courts des semaines de cours vont aux tâches fragmentables (couverture,
    revue OWASP, doc d'exploitation). *La couverture de tests se fait un mardi soir ; le
    squelette de l'application, non.*
- **Constat qui change le calendrier** : entre le 05/11 (livrables) et le 30/11 (jury) il y a
  **25 jours**. Le guide d'étude et la préparation d'oral s'y logent — **ils ne sont pas dans
  les 12 semaines**. Les mélanger, c'est ne finir ni l'un ni l'autre.
- **Risque n° 1 nommé** : **Docker ne démarre pas sur cette machine** et C13 en dépend. Si le
  blocage tient, on livre un packaging sans Docker, documenté — un obstacle mesuré et
  expliqué vaut mieux qu'une case vide.
- **Fusionné `develop` dans `main`** (`7b68252`). `main` accusait 12 commits de retard : un
  collaborateur invité en lecture y atterrit et ne voyait rien du travail depuis le 13/08,
  alors que trois critères exigent que le travail soit accessible depuis un dépôt Git.
  186 tests verts après fusion.

## 2026-08-15 — C6 : le partage tranché, et le second outil de veille sorti de l'ombre

Les deux trous repérés le 14/08 en relisant JOURNAL-005 sont comblés dans
`docs/veille/README.md`.

- **Trou 1 — le partage (§5).** Le protocole décrivait le *format* des synthèses mais jamais
  leur *destinataire*. Or **deux critères sur huit** portent là-dessus. **Décision** :
  formateur référent en destinataire principal (mail, PDF, **mensuel** — un envoi
  hebdomadaire devient du bruit et cesse d'être lu), canal de la promo en second cercle
  (**à chaque note**, terminée par une question ouverte). *« Animer le travail collectif »
  n'est pas « publier » : la preuve, ce sont les **réponses**, pas les envois.*
- **Ajouté** `docs/veille/_JOURNAL-DES-ENVOIS.md` — registre des envois, rempli **le jour de
  l'envoi**, jamais reconstitué.
- **Manque déclaré, non résolu** : **aucun envoi n'a eu lieu**. Le registre est vide. Tant
  qu'il l'est, ces deux critères valent **zéro**, quelle que soit la qualité des notes.
  Écrit noir sur blanc dans le registre et dans `ETAT.md` plutôt que laissé implicite.
- **Trou 2 — les deux outils (§4).** `C:\Users\kanda\Desktop\Veille-IA\` existait sans être
  mentionné nulle part. **Décision** : `sources/rss.py` est **l'outil de C6** ; `Veille-IA`
  est une veille **personnelle, hors C6**. Raison rédhibitoire : **sa sortie est rédigée par
  un LLM**, ce qui en ferait une preuve fabriquée — la règle était déjà posée au §2 du
  protocole. S'y ajoutent une thématique différente (IA/finance/agentique) et l'absence de
  versionnement.
- **Mesure, pas supposition** : `Veille-IA/data/latest.json` date du **27/07** et `output/`
  ne contient **qu'un** dossier, du **19/07**. L'outil est à l'arrêt depuis trois semaines —
  il ne pourrait pas non plus revendiquer une récurrence.

## 2026-08-15 — Décision : les indicateurs de marché, triés et datés

- **Décision structurante** : 19 indicateurs proposés, ramenés à **13 réellement à coder**,
  répartis en 4 lots par **coût de données** — le seul critère qui commande l'ordre.
  Spécification : `docs/indicateurs/CONCEPTION.md` — **conception seule, aucun code écrit**.
- **Le mot « stratégie » est abandonné dans tout le projet.** Un indicateur est un *fait*
  (« le RSI vaut 71 »), une stratégie est un *conseil* (« RSI > 70 → vendre »). Le second
  contredirait le garde-fou AMF inscrit dans `CLAUDE.md`. *Un livrable dont le titre
  contredit son propre garde-fou ne tient pas cinq minutes devant un jury.*
- **Vérification avant rédaction — 3 des 19 existaient déjà** : dernier cours et performance
  1 jour (R2 de `db/requetes.sql`), volume relatif 20 séances (R3), volatilité intraséance
  (S2 de `bigdata/query_spark.py`). **Et le portefeuille est déjà valorisé** par la vue
  `v_portefeuille_valorise`, conversion des devises comprise : le lot portefeuille tombe de
  3 ajouts à **2** (poids par ligne, exposition par devise).
- **Manque découvert** : `sources/cotations.py` collecte avec `auto_adjust=True`. C'est le
  bon choix — une performance sur cours bruts serait fausse — mais **les cours passés sont
  réécrits à chaque dividende**. Une performance 1 an n'est donc pas strictement reproductible
  dans le temps. Inscrit comme piège, pas dissimulé.
- **Écarté : le ratio de Sharpe.** `sources/fred.py` ne collecte que `DGS10`, le Trésor
  **américain**, pour un portefeuille en euros ; très bruité sur un an de données
  quotidiennes ; et c'est le seul indicateur de la liste qui **classe** — donc le plus proche
  du conseil. Écart **assumé et présenté à l'oral**, pas un oubli.
- **Erreur corrigée** : la proposition parlait des « 135 instruments ». RITA en compte **111**.
  Le 135 venait du suivi des 135 critères RNCP — deux objets sans rapport.
- **Rattachement** : livrable **E4** (C14–C19). Ces indicateurs ne rapportent **rien** en C2,
  déjà livré avec R1–R3 et S1–S3 : ajouter des requêtes ne re-prouve pas une compétence
  prouvée. Ils sont le contenu de `frontend/`, vide à ce jour.
- **Rien n'est codé, et rien ne doit l'être avant l'ouverture d'E4** : au 15/08 il reste
  12 semaines et C6 est le seul chantier qui ne se rattrape pas.

## 2026-08-18 — C14 et C15 : les deux schémas obligatoires de E4

- **Livré** `evidence/C14/` — wireframes des **4 états** de l'écran portefeuille et
  spécification fonctionnelle de US-1 : contexte, 5 scénarios, **11 critères d'acceptation
  dont 6 portant un numéro de règle RGAA**.
  *Les objectifs d'accessibilité ne sont pas une annexe : ce sont des critères d'acceptation.
  Une US qui afficherait les bons chiffres sans `scope` serait refusée.*
- **Décidé** : les 4 états représentés sont ceux du code réel, **erreurs comprises**. Un
  wireframe qui ne montre que le cas nominal décrit une démonstration, pas une application.
  Les 3 pannes traitées par `app.js` sont de natures différentes — une clé refusée n'est pas
  une panne, et une absence totale de réponse n'a aucun statut HTTP à lire.
- **Décidé** : le **MCD Merise de C4 satisfait déjà** le critère « modélisation des données »
  de C14. Il n'a pas été refait — un second modèle des mêmes données serait un doublon à
  maintenir, donc une future contradiction.
- **Livré** `evidence/C15/` — diagramme de flux de données en **6 zones**, découpées sur les
  frontières réelles du code, et spécifications techniques : 13 dépendances, environnement
  d'exécution, choix d'éco-conception.
- **Manque déclaré** : **2 des 5 critères de C15 ne sont pas satisfaits** — la preuve de
  concept en **pré-production** et sa conclusion. Le déploiement passerait par Docker, dont
  le démon ne démarre pas sur cette machine : **le même obstacle bloque déjà C13**. Une
  réparation débloquerait deux compétences.
- **Manque déclaré** : sur 13 dépendances, **2 seulement sont épinglées**. OWASP ASI04
  recommande *« allowlist and pin »* — relevé par la veille S34, action ouverte.

## 2026-08-17 — Deux tables vides retrouvées après la reconstruction du 16/08

- **Manque découvert** : `taux_change` était vide. Sans taux, `COALESCE(t.valeur_pour_eur, 1)`
  retombe silencieusement sur 1 — aucune conversion de devise n'était appliquée. Révélé par
  un `EXPLAIN ANALYZE` (`Seq Scan on taux_change … rows=0.00`). Réimporté via
  `python -m pipelines.ingest --etapes ecb` : 5 devises, taux du 17/08.
- **Cause identifiée, et le même défaut trouvé une seconde fois** : la reconstruction de la
  base le 16/08 (voir entrée précédente) n'a rechargé que ce qui a une source Parquet
  (`db/importer.py`). `article` (flux RSS) n'en a pas — elle était donc **elle aussi vide**,
  sans lien avec `taux_change`. Réimportée : `python -m pipelines.ingest --etapes rss`,
  30 lignes, 0 bloquée.
  *Une table vide qui devrait avoir des lignes est un signal à ne pas laisser traîner — c'est
  exactement ce qui avait caché `taux_change`.*
- **`ANALYZE`** exécuté sur toute la base : les statistiques du planificateur étaient bien
  plus périmées que prévu — **presque toutes les tables estimées à 0**, pas seulement
  `position`. Corrigé et vérifié exact table par table.
- **Suite de tests rejouée après les deux réimports** : `200 passed, 1 failed`, l'unique échec
  restant volontairement en place depuis la veille S34 (seuil du garde-fou, question ouverte
  S35). Rien de nouveau cassé par les réimports.

## 2026-08-14 — RGPD : un traitement déclaré qui n'existait pas

- **Manque découvert** : le registre décrivait **T3** (traçage LangSmith) comme un traitement
  **actif**, avec transfert de données personnelles vers les États-Unis et un risque classé
  🔴 haute. Vérification : ni `LANGCHAIN_TRACING_V2` ni `LANGCHAIN_API_KEY` dans le `.env`
  réel, aucun appel à LangSmith dans le code. **Aucune donnée ne sort de la machine.**
  T3 passe en *« envisagé, non activé »*, criticité abaissée à 🟠.
  *Un registre qui sur-déclare est aussi inexact qu'un registre qui oublie.*
- **Décision documentée** : le choix de l'outil de monitorage a une conséquence RGPD directe —
  LangSmith crée un transfert hors UE, Langfuse auto-hébergé le supprime, Langfuse Cloud
  région UE le maintient sans transfert au sens de l'article 44. Le formateur a validé
  LangSmith ; le tableau reste au registre pour le jour où la question se reposera.
  Obstacle réel à l'auto-hébergement : **Docker ne démarre pas sur cette machine** — il
  manque aussi pour C13.
- **Ajouté** `scripts/verifier_liens.py` : contrôle des liens externes (HTTP) **et** internes
  (le fichier visé existe-t-il, et est-il **dans** le dépôt). Première exécution :
  **34 fichiers · 38 liens internes · 5 externes · 0 cassé.** Règle inscrite dans `CLAUDE.md` :
  à lancer avant chaque envoi de livrable.

## 2026-08-14 — C6 : la veille est lancée

- **Thématique arrêtée** : **sécurité des agents LLM — l'injection de prompt**. Retenue parce
  qu'elle porte sur un risque **réel** du projet (RITA lit des pages et des flux écrits par des
  tiers) et sur un outil qu'il possède déjà (`guardrails/injection.py`), pas sur un sujet
  choisi pour l'exercice.
- **Ajouté** `docs/veille/README.md` — le protocole : 7 sources **pesées une par une** sur les
  critères de fiabilité du référentiel (auteur identifié, notoriété, intérêts), dont deux
  gardées **sous condition** (éditeurs de modèles = intérêt commercial ; arXiv = non relu par
  les pairs), trois écartées avec motif. Outil d'agrégation : **RSS via `sources/rss.py`**, le
  code que le projet possède déjà — **budget 0 €**. Plus les 7 règles d'accessibilité
  appliquées à chaque note.
- **Ajouté** `docs/veille/_MODELE-note-hebdomadaire.md`, avec la section obligatoire
  **« Ce que ça change dans RITA »** et une liste de contrôle d'accessibilité.
- **Récurrence en place** : tâche planifiée `veille-hebdo-securite-llm`, **lundi 09h00**.
- **Décidé** : la tâche planifiée **prépare** une liste de candidats, elle **n'écrit pas la
  note**. *Une note de veille produite par une IA serait une preuve fabriquée devant le jury —
  et ne prouverait aucune compétence.*
- **Reste** : les notes elles-mêmes. **0 écrite à ce jour.**

## 2026-08-14 — Continuité entre sessions

- **Ajouté** `CLAUDE.md` (identité du projet, invariante) et `ETAT.md` (état du jour) à la
  racine du dépôt, plus ce `CHANGELOG.md`. Le rituel début/fin de session est inscrit en
  tête de `CLAUDE.md`.
- **Décidé** : `ETAT.md` devient la **source unique** de l'état. `BOUSSOLE-RITA.md` (Bureau)
  passe en archive — elle vivait hors du dépôt, ne se chargeait que si on pensait à
  l'ouvrir, et s'est retrouvée fausse sur 3 points le 13/08.
  *Deux fichiers pour un même rôle finissent toujours par se contredire.*
- **Ajouté** `C:\Users\kanda\.claude\CLAUDE.md` — règles de travail valables dans tous les
  projets, pour ne plus dépendre de la mémoire rangée par dossier.
- **Découvert** : le vrai vault Obsidian est
  `C:\Users\kanda\Documents\Formation-IA\Formation-IA\`. Les deux dossiers de `D:\` qui
  ressemblent à des vaults sont des **leurres vides** datés de mai 2026. Le journal RITA
  n'avait jamais bougé — c'est la méthode de recherche qui était mauvaise (`find` sur le
  disque au lieu du MCP Obsidian).
- **Rédigé** dans le modèle Simplon (`D:\KandaWork\RITA_PROJECT\Era-Preparation-livrables-RNCP.xlsx`) :
  C1 C2 C3 C4 C5 C8 C9 C12 C13. **C6, C7, C10 et C11 laissés délibérément vides — rien n'est
  fait.** Une cellule vide se rattrape ; une affirmation fausse devant le jury, non.
- **Vérifié sur GitHub** (`gh api`) l'état réel de l'accès au dépôt, au lieu de le supposer :
  dépôt `PRIVATE`, un seul collaborateur (`Ganda15`, admin), et **une invitation envoyée le
  13/08 à 15h16 à `bybysker` en droit `read`, toujours en attente d'acceptation**.
  L'action a donc bien été faite le 13/08 — mais tant que l'invitation n'est pas acceptée,
  le critère *« accessible depuis un dépôt Git »* n'est pas satisfait.
  *Une invitation envoyée n'est pas un accès donné.*
- **Manque confirmé, le plus urgent** : C6 exige *« à minima une récurrence d'une heure
  hebdomadaire »*. `docs/veille/` ne contient que `.gitkeep`. **12 semaines avant la
  deadline** — c'est le seul critère qui ne se rattrape pas rétroactivement.

## 2026-08-13 — Livrable E1 envoyé · tag `livrable-E1-v1`

- **Livré** E1 (C1–C5) — **26 critères sur 28**.
- **Restent** C1#6 et C3#2 : *« accessible depuis un dépôt Git »*. Le dépôt est privé —
  c'est un **accès à donner** (invitation en collaborateur), pas du travail à produire.
- **Décidé** : le dépôt **reste privé**, accès par invitation. Décision assumée, pas un oubli.
- **Corrigé** le `README.md` : retrait de Prometheus, Grafana, Docker et d'une version de
  Python — tous annoncés alors qu'ils n'existent pas dans le projet.
  *Un README qui promet ce qui n'existe pas est un mensonge au jury.*
- **Bascule** de la tâche principale : **E1 → E3**.

## 2026-08-11 — Preuves C4 remises dans le dépôt

- **Découvert** que `evidence/C4/` était **vide** alors que le MCD Merise existait depuis le
  01/08 : il n'avait jamais été copié dans le dépôt. Corrigé le jour même
  (`.png`, `.drawio`, `preuve-mcd-merise.md`).
- **Corrigé** `evidence/README.md`, qui annonçait encore l'état du 28/07 — soit le premier
  fichier qu'un évaluateur ouvre.
  *Un document d'état daté reste faux tant que personne ne lit la date.*
- **Corrigé** le compte de tables : le texte annonçait 7 tables en se contredisant avec son
  propre tableau (6 entités + 2 tables techniques = **8**). Vérifié en rejouant
  `db/schema.sql` sur une instance neuve.
