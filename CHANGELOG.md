# Journal des livrables et décisions — RITA

> **Append-only** : on ajoute en haut, on ne réécrit **jamais** une entrée passée.
> Le présent est dans `ETAT.md` · le pourquoi détaillé dans le journal Obsidian ·
> le détail technique dans `git log`.
>
> **Une entrée = un livrable envoyé, une décision structurante, ou un manque découvert.**
> Pas les commits de code : Git les garde mieux, horodatés et infalsifiables.

---

## 2026-08-19 — RITA est en ligne : déploiement réel, et deux vérités rétablies

- 🚀 **Déployée sur Hetzner Cloud** — CX23, Falkenstein, Ubuntu 26.04, **7,19 €/mo TTC**.
  `http://178.104.184.125:8001/`. Docker + Compose, mêmes conteneurs qu'en local.
  **Vérifié depuis l'extérieur, pas depuis le serveur** : `/health` → **200 en 0,07 s**,
  `/donnees/valeurs` sans clé → **403**. *Le garde-fou OWASP API2 a survécu au déploiement.*
  **111 valeurs · 275 118 cotations · 112 alias · 30 articles · 5 taux · 7 positions**
  chargées et comptées en base, `ANALYZE` exécuté. **Le manque C13 « déploiement » est
  comblé.**
- 💰 **Un serveur payé pour rien depuis 4 mois** (`CPX32`, **17,39 €/mois**, jamais utilisé,
  vide) supprimé le même jour. Le déploiement réel coûte donc **moins cher que l'inaction**.
- 🐛 **Défaut de conception trouvé en déployant** : `db/importer.py` **ne peut pas tourner
  dans l'image livrée**. `requirements-api.txt` exclut `pyarrow` avec un commentaire qui dit
  *« le Parquet ne sert qu'à l'archive et à l'import initial »* — mais l'importateur en a
  besoin, et rien ne dit **comment** faire cet import initial une fois déployé. Contourné par
  `pg_dump --data-only` depuis le poste local ; **le trou reste ouvert**. *Même fichier que
  le 0 % de couverture comblé ce matin : deux angles morts sur `db/importer.py` le même jour.*
- ⚠️ **Écart d'environnement relevé** : poste local en **PostgreSQL 18.4**,
  `docker-compose.yml` fixe **postgres:17-alpine**. Contourné (transfert *données seules*),
  mais c'est un « ça marche chez moi » à aligner.
- 🔴 **Vérité rétablie sur le portefeuille.** Les chiffres présentés depuis le début —
  **33 214,80 €, 7 lignes, plus forte ligne 34,83 % (VIRI.PA)** — proviennent de
  **`data/positions-exemple.csv`**, le jeu **anonymisé de démonstration**, **pas** du
  portefeuille réel. Vérifié : `POSITIONS_CSV` n'a jamais été défini, donc
  `sources/positions.py` a toujours pris l'exemple ; la base locale contient ces 7 lignes à
  l'identique. `ETAT.md`, `evidence/C14/` et `docs/indicateurs/CONCEPTION.md` corrigés.
  *Un jeu de démonstration assumé est légitime ; le faire passer pour des données réelles
  ne l'est pas — surtout devant un jury.*
- 💡 **Précision gagnée au passage** : si le chemin multi-devises n'est jamais exercé, ce
  n'est pas faute de lignes étrangères — l'exemple **contient** AAPL et MSFT en USD, mais
  elles sont **rejetées à l'import**, absentes de l'univers de 111 valeurs françaises.
- 🔴 **Reste à faire** : le **pare-feu Hetzner n'est pas configuré** — aucun n'est attaché,
  donc tous les ports sont ouverts. À restreindre à 22 + 8001.

## 2026-08-19 — Second manque fermé : seuil de couverture relevé à 90 %

- **Livré** 5 tests dans `tests/test_evals.py` pour `evals/mesurer_sortie.py` — en miroir
  exact de ceux qui existaient déjà pour `evals/mesurer_gardefou.py` (garde-fou d'entrée).
  Aucun mock : ce sont des fonctions pures (regex sur une liste de textes), le même style
  d'appel direct déjà accepté pour le garde-fou d'entrée.
- 🐛/🆕 **Le garde-fou de SORTIE souffre de la même limitation S34 que celui d'entrée** :
  taux de blocage réel **70 %**, sous le seuil de 85 % (0 % de faux positifs). Un **2ᵉ test
  `xfail(strict=True)`** rejoint le premier — même discipline, même raison documentée dans
  le code : le seuil reste à 85 %, on déclare ne pas l'atteindre plutôt que de le baisser.
- `evals/mesurer_sortie.py` : **0 % → 100 %** (10 instructions).
- **Conséquence** : couverture totale **83 % → 92 %**. Les **deux** manques identifiés à la
  mesure initiale du 19/08 sont désormais fermés (`db/importer.py` la veille dans la même
  journée, `evals/mesurer_sortie.py` maintenant) — **le seuil CI est relevé de 80 % à 90 %**
  dans `.coveragerc`, exactement comme le plan écrit la veille le prévoyait : *« le seuil
  suit la mesure, jamais l'inverse »*. Suite complète : **319 passed, 2 xfailed**.

## 2026-08-19 — `db/importer.py` couvert : 0 % → 100 %, sans toucher une vraie base

- **Livré** `tests/test_importer.py` — **13 tests**, curseur simulé (`MagicMock`),
  `execute_values` remplacé par un double inspecté (même remède que
  `pipelines/ingest.py` : la vraie fonction encode via `cur.connection`, absent d'un
  curseur simulé). **Aucun test ne touche PostgreSQL.**
- **Manque fermé** : C4 exige ce script **fonctionnel**, mais il était à 0 % de
  couverture depuis le début du projet — un défaut pouvait y dormir indéfiniment sans
  que la suite ne le signale.
- **Verrouillé** : le dédoublonnage `(ticker, date_seance)`, le filtrage des tickers
  hors univers (contrainte de clé étrangère), la résolution des alias de portefeuille —
  dont le **cas CGG** (deux libellés, « CGG BS »/« CGG RGPT », une seule valeur
  `VIRI.PA`, deux alias) — et le fait qu'un portefeuille vide ou sans correspondance
  n'insère jamais rien.
- **Conséquence mesurée** : couverture totale **83 % → 91 %** en fermant ce seul
  manque — au-dessus de la prévision à 91 % écrite la veille pour les **deux** manques
  ensemble. Le seuil CI reste à **80 %** : le relever à 90 % attend la fermeture du
  second manque (`evals/mesurer_sortie.py`, 0 %), pas un seul sur deux.

## 2026-08-19 — Lot 3 des indicateurs : les 13 sont codés, exposés et affichés

- **Livré** `db/indicateurs_risque.sql` (volatilité, drawdown) + `indicateurs/risque.py`
  (RSI 14) + `GET /donnees/indicateurs-risque` (**9ᵉ** point de terminaison) + 3 colonnes sur
  l'écran 2. **19 tests**, suite complète **302 passed, 1 xfailed** (couverture 83 %).
  **Les 13 indicateurs de la spécification sont désormais codés du bout en bout.**
- 🐛 **Manque découvert et corrigé** : la première version de la requête rendait la
  volatilité **`NULL` pour les 111 valeurs**. Cause : les fonctions fenêtre étaient placées
  dans le `SELECT` final, **après** la jointure sur la dernière séance — cette jointure réduit
  chaque ticker à une seule ligne avant que la fenêtre ne soit évaluée. Corrigé en calculant
  les fonctions fenêtre dans une CTE sur l'historique complet, filtrée seulement ensuite.
  *Le même bug avait aussi produit 2 drawdowns positifs — impossible en théorie — sur la
  première mesure.*
  Vérifié sur l'exemple exact de la spécification : série 100→150→90→120 ⇒ drawdown
  **−40,00 %**, obtenu au chiffre près.
- **Décidé** : le RSI est calculé en **Python**, pas en SQL — le lissage de Wilder est
  **récursif** (chaque moyenne dépend de la précédente), ce qu'une fonction fenêtre SQL ne
  peut pas exprimer sans un CTE récursif jugé illisible par la spécification.
- `quant_metrics.py` relu une **deuxième fois** (après le lot 1) et de nouveau **non
  réutilisé** : rendement simple au lieu de logarithmique, maximum incluant le jour courant
  au lieu de s'arrêter à la veille, moyenne mobile simple au lieu du lissage de Wilder — trois
  défauts différents, un seul verdict.
- 🆕 **Même angle mort que le lot 1, retrouvé au lieu d'être généralisé du premier coup** :
  les 3 valeurs radiées affichaient une volatilité et un drawdown calculés sur des données de
  **2018**, `fraicheur_jours` présent mais non exploité. `cotation_perimee` ajouté — la
  mesure reste affichée (une volatilité passée reste valide), mais le **RSI disparaît** pour
  ces valeurs : *un RSI daté de 2018 ne dirait rien d'utile sur aujourd'hui*.
- 🐛 **Deux échecs de test successifs, le même piège en plus subtil à chaque fois** : un test
  du garde-fou AMF bannissait le mot « acheter », trouvé dans la phrase qui **explique**
  l'interdit (« RITA n'indique jamais qu'il faut acheter ou vendre ») ; la version suivante
  bannissait « il faut acheter » — toujours une sous-chaîne de la même phrase de négation.
  Corrigé en cherchant des formes **impératives** (« achetez »), absentes de toute négation à
  l'infinitif en français correct.
  *Une négation contient forcément les mots qu'elle nie — chercher un mot isolé ne suffit
  jamais à distinguer une interdiction de ce qu'elle interdit.*

## 2026-08-19 — Le seuil de couverture tombait en CI : la mesure dépendait de la machine

- 🐛 **La CI a échoué au premier passage** avec le nouveau seuil : **79 %** contre **82 %**
  mesurés en local. Cause : **6 tests d'intégration Spark sont ignorés en CI** — le jeu Parquet
  est `gitignore`. `bigdata/query_spark.py` tombait de 77 % à 38 %, `session_spark.py` de 96 %
  à 59 %.
- **La vraie faute était une incohérence de ma part** : j'avais exclu **3 des 5** fichiers de
  `bigdata/` en invoquant `.dockerignore`… qui exclut **le dossier entier**. Le même argument
  valait pour les cinq.
- **Corrigé** : `bigdata/*` exclu en entier. Nouvelle mesure : **81 %** (934 instructions),
  **identique en local et en CI** — vérifié en rejouant la suite sans les tests Spark.
  Seuil maintenu à **80 %**, désormais un point sous une mesure stable.
- 🔑 **Une couverture qui change selon la machine ne peut pas servir de garde-fou** : le
  chiffre doit être le même partout, sinon il ne mesure pas le code mais la configuration de
  celui qui le lance.
- *Le seuil avait été fixé sur une mesure locale sans vérifier qu'elle était reproductible.
  L'échec de la CI a coûté dix minutes ; ne pas l'avoir vu aurait coûté un seuil auquel
  personne ne se serait fié.*

## 2026-08-19 — C12 : la couverture mesurée, et deux trous qu'elle révèle

- **Livré** la mesure de couverture : `.coveragerc`, seuil en CI, procédure documentée.
  C12 exige *« la couverture souhaitée **établie** »* et une documentation du *« calcul de la
  couverture »*. **271 tests existaient sans qu'aucun chiffre ne dise ce qu'ils couvrent.**
- ⚠️ **Le premier chiffre était trompeur** : **78 %** en mesure brute — elle incluait les
  **fichiers de tests eux-mêmes**, couverts à 100 % par construction puisqu'ils s'exécutent.
  *Se noter sur sa propre copie.* Sans eux : **67 %**.
- **Décidé** — trois exclusions, chacune motivée : `tests/`, les `__init__` vides, et les trois
  scripts `bigdata/` lancés à la main une fois. L'argument pour ces derniers **ne vient pas de
  là** : `.dockerignore` les écarte déjà de l'image livrée faute de `pyspark` — ils **ne
  peuvent pas** tourner dans le système livré.
- **Décidé** : `db/importer.py` **n'est pas exclu**, bien qu'il soit aussi lancé à la main. Un
  critère de C4 exige qu'il soit **fonctionnel**. *Son 0 % est un vrai manque, déclaré — pas
  quelque chose qu'on fait disparaître par une ligne de configuration.*
- **Mesure finale : 81 %** (934 instructions, 173 non couvertes), **identique en local et en
  CI**. **Seuil fixé à 80 %**, un point sous la mesure. *Ce n'est pas le « 80 % qu'on voit partout » : un seuil recopié
  d'un article de blog est aussi arbitraire que 50 %.*
- 🔴 **Deux manques révélés par la mesure — et c'était le but de l'exercice** :
  `db/importer.py` (**85 instructions, 0 %**) — il fonctionne, on le lance, mais **rien ne le
  vérifie automatiquement : le jour où quelqu'un le casse, la suite reste verte** ·
  `evals/mesurer_sortie.py` (**10 instructions, 0 %**) — c'est **l'outil qui produit le chiffre
  de 70 %** du garde-fou de sortie. *La mesure n'est pas mesurée.*
  Les couvrir porterait le total à **91 %** ; le seuil montera alors à 90 %.
- **Décidé** : le seuil vit dans `.coveragerc`, **pas dans le workflow** — écrit en CI il serait
  invisible depuis la machine de développement, et la régression se découvrirait après avoir
  poussé.

## 2026-08-19 — Doc d'exploitation (C8)

- **Livré** `docs/EXPLOITATION.md` — le 4ᵉ critère de C8 : *« la documentation couvre la
  gestion des accès, les procédures d'installation et de test, les dépendances et
  interconnexions, les données impliquées »*. Dix sections : prérequis, clés d'accès,
  installation **avec et sans Docker**, vérifications, les **7 services externes** et ce qui
  se passe quand chacun tombe, les **8 tables** et lesquelles portent des données
  personnelles, l'exploitation quotidienne, et un tableau de dépannage.
- **Écrit pour quelqu'un qui n'a jamais fait tourner RITA** : chaque commande a été exécutée,
  aucune recopiée de mémoire. Les 9 fichiers cités ont été vérifiés présents.
- Le tableau de dépannage rassemble les **pièges réellement rencontrés** : port 5433 et non
  5432, `DATABASE_URL` et non `POSTGRES_URL`, `&&` inconnu de PowerShell 5.1, tests Spark
  ignorés sans JDK, `xfailed` normal, valeur radiée aux performances aberrantes.
- 🔴 **Reste pour C8** : le **monitorage du service**, et la **communication** de cette
  documentation aux parties prenantes (5ᵉ critère) — écrire ne suffit pas, il faut transmettre.

## 2026-08-19 — La chaîne de livraison, et les indicateurs du portefeuille

### La suite repasse au vert, sans rien effacer

- **Décidé** : `test_seuils_minimaux_du_gardefou` passe en **`xfail` strict** plutôt que de
  baisser le seuil ou de laisser la suite rouge. **Le seuil reste à 85 %** — on ne baisse pas
  l'exigence, on déclare qu'on ne l'atteint pas encore. Le rapport affiche `xfailed` avec la
  raison, jamais `passed`, et `strict=True` fera **échouer la suite** si le taux repasse
  au-dessus : le jour où la limitation est levée, on est prévenu.
  *Une CI rouge en permanence cesse d'être un signal — au bout de deux semaines on ne la
  regarde plus, et c'est le jour d'un vrai échec qu'on ne le voit pas.*
- Le contrôle des **faux positifs** est extrait dans son propre test, qui doit passer : les
  deux chiffres ne mesurent pas la même chose, et les fusionner aurait masqué le second.

### C13 gagne son volet livraison

- **Livré** `.github/workflows/livraison.yml`. Construction sur `main`/`develop`,
  **publication uniquement sur un tag `livrable-*`** — un tag = un livrable = une image.
  *Publier à chaque envoi produirait des dizaines d'images ne correspondant à rien
  d'identifiable.*
- **Décidé** : les tests tournent **dans le job de livraison**, pas seulement dans `test.yml`.
  Deux workflows séparés peuvent passer l'un sans l'autre ; livrer une image dont les tests
  n'ont pas été rejoués **sur ce commit** serait livrer sans filet.
- **Décidé** : l'image construite est **démarrée puis interrogée** — `/health` répond en 4 s,
  l'accès sans clé donne 403. *Une image qui se construit n'est pas une image qui démarre :
  sans cette étape on publierait une image cassée avec un workflow au vert.*
- Exécution réelle vérifiée : **3 min 40**, conclusion `success`.

### Indicateurs lot 2 — le portefeuille

- **Livré** `db/indicateurs_portefeuille.sql`, `indicateurs/portefeuille.py`,
  `GET /donnees/indicateurs-portefeuille` (**8ᵉ** point de terminaison) et **l'affichage sur
  l'écran 1**. Somme des poids : **exactement 100,00 %**.
- **Décidé** : le poids et l'exposition vont sur l'écran **portefeuille**, pas sur l'écran des
  indicateurs — ils décrivent le portefeuille, pas l'univers des 111 valeurs.
- **Décidé** : deux appels **en parallèle** plutôt qu'un point de terminaison élargi, chacun
  gardant une responsabilité · appariement **par ticker** et non par position — vérifié dans
  le navigateur, les deux points de terminaison renvoient bien des ordres **différents** ·
  **mode dégradé** : si les indicateurs échouent, le portefeuille reste affiché.
  *Une dépendance secondaire qui fait tomber l'écran principal est une erreur de conception.*
- ⚠️ **Limite déclarée** : les 7 positions sont **toutes en euros**. Le chemin multi-devises
  n'est **jamais exercé en production** — seuls les tests le couvrent.
- 🐛 **Quatre défauts trouvés en écrivant** : `from module import fonction` copie la référence
  à l'import, ce qui faisait recevoir à **4 tests les vraies données** au lieu du jeu simulé ·
  une **fonction** `portefeuille()` écrasait l'import du module (`AttributeError` à
  l'exécution) · un test cherchait `taux_change` dans un **commentaire** — **quatrième fois**
  ce piège, après `innerHTML`, `LAG(` et `"dev-key"` · le vérificateur de liens criait au loup
  sur le dépôt privé.
  *Un test doit porter sur le code exécuté, jamais sur les mots qui l'expliquent.*

## 2026-08-18 — Le livrable s'ouvre par son tag, pas par la branche par défaut

- 🔴 **Manque découvert** : `main` est la branche par défaut — c'est elle que GitHub montre à
  qui ouvre le dépôt — et elle **avance**. Au 18/08 elle comptait **29 commits de plus** que
  le tag `livrable-E1-v1`. Un formateur ouvrant `github.com/Ganda15/rita-agent` **ne voyait
  pas E1** : il voyait le projet du jour, et aurait jugé E1 sur du travail postérieur.
- **Corrigé** dans `README.md` : avertissement en tête du tableau des livrables, et le tag
  devient un **lien cliquable** au lieu d'un texte. Les lignes E2/E3/E4 remises à jour —
  **E4 annonçait « non commencé »** alors qu'il a deux écrans et les schémas C14/C15.
- **Ajouté** dans `docs/FILE-DE-VALIDATION.md` : la règle d'envoi, trois commandes de
  vérification (le tag existe · le destinataire est **collaborateur** et pas seulement
  invité · zéro lien cassé), et un **gabarit de message qui explique le tag**.
  *Un lien qu'on ne comprend pas est un lien qu'on remplace par celui qu'on connaît.*
- 🐛 **Faux positif de `scripts/verifier_liens.py`**, corrigé. Le dépôt est **privé** : une
  requête HTTP anonyme reçoit **404** sur un lien valide. Le script signalait donc comme cassé
  **le lien du tag — celui-là même qu'on envoie au formateur.** Il retente désormais via `gh`,
  authentifié. Vérifié : le vrai tag passe, un tag inexistant est toujours détecté.
  *Un vérificateur qui crie au loup sur des liens corrects finit ignoré — et c'est alors le
  vrai lien cassé qui passe.*

## 2026-08-18 — Le journal et les guides d'étude remis à leur place

- **Manque découvert** : le journal s'arrêtait à `JOURNAL-007` (15-16 août). **Les séances du
  17 et du 18 n'avaient aucune entrée** — soit la journée de veille S34 et la plus grosse
  journée du projet. `JOURNAL-008` et `JOURNAL-009` écrits.
- **Corrigé** : `docs/etude/` contenait deux guides d'étude en anglais, c'est-à-dire de la
  **préparation dans le dépôt de livrables** — contraire à la règle du 11/08. Déplacés dans
  Obsidian (`09-EN-personnel/`), copies **vérifiées identiques par empreinte SHA-256** avant
  suppression du dossier.
- *Le dépôt reçoit les livrables, jamais la préparation. La règle avait été posée après avoir
  trouvé 19 blocs « phrase pour l'oral » à l'intérieur des livrables eux-mêmes ; elle se
  re-vérifie à chaque ajout de dossier.*
- **Ajouté** au même commit : les 4 fichiers de travail de la veille S34 (`_candidats`,
  `_decisions`, `_source-OWASP-agentique`, `_verifications-code`), jusque-là non suivis. Ils
  accompagnent la note, comme `_candidats-2026-S33.md`.

## 2026-08-18 — Sécurité de l'API, et la pré-production Docker

### A — OWASP API2 : la clé par défaut supprimée

- 🔴 **Manque corrigé** : `api/main.py` disait `os.getenv("RITA_API_KEY", "dev-key")`. La
  variable n'étant pas définie, l'API acceptait en réalité la chaîne **`dev-key`, écrite en
  clair dans un fichier que le formateur et le jury vont lire.**
  *Une clé par défaut n'est pas une clé : c'est une porte ouverte documentée.*
  Remplacée par une **panne au démarrage**, une longueur minimale de 16, et
  `secrets.compare_digest` (une comparaison ordinaire s'arrête au premier caractère
  différent, et son temps d'exécution renseigne un attaquant).
  Vérifié sur le serveur réel : `dev-key` → **403**, vraie clé → **200**.
- **Corrigé** `.env.example`, qui **ne permettait pas de démarrer le projet** : il documentait
  `POSTGRES_URL` sur le port 5432 alors que le code lit `DATABASE_URL` sur 5433, et omettait
  trois variables. Les variables de traçage y passent en commentaire, avec le renvoi au
  traitement **T3** du registre RGPD — les décommenter enverrait des montants hors UE.
- 🐛 **Défaut créé puis trouvé le jour même, avant tout commit** : `.gitignore` ne couvrait que
  le nom exact `.env`. Une copie `.env.sauvegarde-*` restait visible de Git, et un `git add .`
  l'aurait committée avec toutes les clés. Élargi à `.env.*` + `!.env.example`. **Rien n'a fuité.**
- **Leçon de test, la troisième fois** : un test cherchait `"dev-key"` dans la source de
  `cle_attendue()` — et le trouvait dans la **docstring** qui explique le défaut corrigé.
  Réécrit pour inspecter l'**AST** et ignorer la docstring. Après `LAG(` dans un commentaire
  SQL et `innerHTML` dans un commentaire JavaScript :
  *un test doit porter sur le code exécuté, jamais sur ce qui l'explique.*

### B — Docker : la preuve de concept tourne

- ✅ **C15 critères 4 et 5 : de 🔴 à ✅.** Déclarés non satisfaits la veille faute de démon
  Docker — **Docker a démarré le 18/08**. `docker compose up -d --build` → **2 conteneurs
  `healthy` en moins de 20 s**, 8 tables créées seules, 403/200 corrects, interface servie.
- **Décidé** : `pyspark` (**492 Mo**) **n'entre pas dans l'image**. Il n'est importé que dans
  `bigdata/session_spark.py`, jamais atteint par l'API. D'où `requirements-api.txt`, aux
  versions **toutes épinglées et relevées par `importlib.metadata`** — pas choisies au jugé.
  *C'est le critère d'éco-conception appliqué là où il se mesure : un demi-gigaoctet
  transféré et stocké à chaque déploiement, pour du code qui ne s'exécute pas.*
- **Décidé** : construction en deux étapes (les outils de compilation ne quittent pas l'étape
  de construction) · utilisateur **non privilégié** · système de fichiers **en lecture seule**
  + `no-new-privileges` · **base non publiée vers l'hôte** (seule l'API lui parle, et cela
  évite tout conflit avec le PostgreSQL natif sur 5433).
- **Vérifié dans le conteneur** : aucun `.env`, `pyspark` absent, `touch /app` refusé,
  `dev-key` → 403. *Embarquer un `.env` dans une image poussée sur un registre est l'une des
  fuites de secrets les plus courantes.*
- **Conclusion de la preuve de concept écrite** (critère 5), **avec ce qu'elle ne démontre
  pas** : pré-production **locale** et non distante, base contenant le schéma mais pas les
  275 118 cotations, aucun déploiement automatisé, et 595 Mo encore lourds.

## 2026-08-18 — Écran 2 : les indicateurs, exposés et affichés

- **Livré** `GET /donnees/indicateurs` — **7ᵉ** point de terminaison du routeur `donnees`.
  Filtre par ticker répétable, et `masquer_perimees` qui vaut **faux par défaut** : les trois
  valeurs radiées sortent, **avec leur drapeau**. `statut_qualite` et `fraicheur_jours` sont
  deux champs distincts, et l'appelant décide.
- **Livré** `frontend/indicateurs.html` + `indicateurs.js` — mêmes 4 états que l'écran
  portefeuille, **même clé en `sessionStorage`** : passer d'un écran à l'autre ne redemande
  pas de s'authentifier.
- **Décidé** — quatre choix commentés à côté du code : un **tiret n'est pas un zéro**
  (`null` = pas calculable, `0` = aucune variation) · la péremption est portée par le
  **texte** de la cellule, la couleur n'étant qu'un renfort (RGAA 3.1) · le filtre agit sur
  les données **déjà chargées**, sans aller-retour réseau · **le tableau défile, pas la page**.
- 🐛 **Défaut trouvé en vérifiant dans le navigateur** : le commentaire du CSS annonçait que
  `tabindex` et `role="region"` rendaient la zone défilable atteignable au clavier — **ils
  n'étaient nulle part dans le HTML**. Douze colonnes ne tenant pas à l'écran, une personne
  naviguant au clavier n'aurait jamais vu la moitié droite du tableau.
  **Même famille que le garde-fou de sortie du 17/08** : *un contrôle documenté mais absent
  est pire qu'un contrôle absent — tant qu'il est écrit, personne ne le cherche.*
- **Vérifié dans le navigateur**, sur le serveur réel : rendu contrôlé, filtre testé par un
  vrai clic, **aucune erreur console**, la page ne défile pas horizontalement, 11 contrôles
  d'accessibilité mesurés.
- **Leçon de test** : un test cherchait `scope="row"` dans le HTML — impossible, les lignes
  sont créées à l'exécution. Il échouait sur du code correct.
  *Un test doit chercher là où la chose est réellement écrite* — même leçon que le `innerHTML`
  trouvé dans un commentaire le 16/08.

## 2026-08-18 — Cours rafraîchis, et un bug latent trouvé en le faisant

- **Rafraîchi** les cours, qui s'arrêtaient au **29/07** — trois semaines de retard.
  `pipelines.ingest --etapes cotations` : **1 618 séances** écrites (28/07 → 18/08).
  Base à **275 118** cotations, **retard 0 jour**. Indicateurs recalculés.
- 🐛 **Bug corrigé** : `_ligne_valide` se protégeait du `NaN` par `x == x`, mais yfinance rend
  **`None`** — pas `NaN` — pour une valeur **radiée**, et `None == None` est **vrai**. Le
  garde-fou laissait donc passer, et `c > 0` levait un `TypeError`.
  **La gravité n'est pas la ligne perdue** : `etape_cotations` groupe les tickers par date de
  dernière séance et attrape l'exception **par groupe** — un seul ticker radié faisait perdre
  **tout son groupe**. Sans conséquence aujourd'hui, faux dès qu'une valeur radiée partagerait
  sa date avec des valeurs vivantes.
  Avant : 1 618 lues / **3 rejetées**. Après : 1 618 lues / **0 rejetée**. +2 tests.
  *Un garde-fou qui traite une seule des deux formes d'absence n'en est pas un.*

## 2026-08-18 — Indicateurs lot 1, et trois valeurs radiées découvertes

- **Livré** le lot 1 des indicateurs : `db/indicateurs.sql` + `indicateurs/socle.py` +
  13 tests. **11 indicateurs par valeur en une seule requête** — 111 valeurs sur 111,
  **194 ms** mesurées par `EXPLAIN ANALYZE`.
- **Décision contredite après vérification** : `ETAT.md` recommandait de **porter**
  `quant_metrics.py` depuis `Ganda15/daily-stock-analysis-era`. Le fichier a été **lu**
  (350 lignes) : il travaille en pandas, sur un instrument à la fois, avec des fenêtres en
  **nombre de lignes** — soit **exactement le piège n°1 de la spécification**. Le porter
  aurait importé le défaut contre lequel elle a été écrite.
  *La consigne du 15/08 avait été écrite sans avoir ouvert le fichier. Corrigée, pas effacée.*
- 🔴 **Manque découvert par la mesure** : **trois valeurs radiées** — Zodiac Aerospace
  (dernière séance 2018-03-22), Euler Hermes (2018-04-26), Gemalto (2019-05-28) — portent
  encore `statut_qualite = 'OK'`. L'écran aurait affiché pour elles une « performance
  1 jour » calculée sur des cours vieux de huit ans. Colonne `fraicheur_jours` ajoutée,
  seuil 40 jours ; les lignes restent affichées **avec la mention**.
  *`statut_qualite` décrit la qualité de l'historique, pas sa fraîcheur. Confondre les deux
  produisait un écran faux avec des données valides.*
- 🟠 **Manque découvert** : les cours s'arrêtent au **29/07** — trois semaines de retard.
  `sources/cotations.py` n'a pas été rejoué depuis la reconstruction du 16/08. **Même famille
  de défaut** que `taux_change` et `article`, corrigés la veille : la reconstruction n'a
  rechargé que ce qui avait une source Parquet.
- **Deux défauts rencontrés en écrivant, tous deux verrouillés par un test** : le module ne
  lisait pas son `.env` (**même défaut que `db/importer.py` le 17/08** — la cause est
  structurelle, seul `api/main.py` appelait `load_dotenv()`), et un caractère « pour-cent »
  dans un **commentaire SQL** cassait `cur.execute` (psycopg2 interpole dès que le second
  argument n'est pas `None`).

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
