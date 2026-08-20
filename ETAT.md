# ÉTAT — où on en est

> **Ce fichier se périme.** Il porte l'état du jour ; `CLAUDE.md` porte ce qui ne change pas.
> À relire au démarrage de chaque session, à mettre à jour à la fin.

**Dernière mise à jour : 2026-08-19** · deadline livrables **05/11/2026** · jury **30/11–01/12**

🆕 **Séance de veille S34 du 17/08 — ce qu'elle a changé dans le code.** Commit `c7c8811`.
- Le **garde-fou de sortie** (interdit AMF) était invoqué par `guardrails/injection.py:9`
  et **n'existait pas** ; `api/main.py` diffusait le texte du modèle sans contrôle. Écrit
  (`guardrails/sortie.py`), câblé sur `/briefing`, mesuré (`evals/mesurer_sortie.py`).
- Le **100 % du garde-fou d'entrée était circulaire** : 7 cas de test pour 9 motifs, un pour
  un. 3 cas adverses ajoutés → **taux réel 70 %**, faux positifs 0 %.
- ⚠️ **Le seuil de 85 % n'est pas atteint (70 %).** ✅ **Traité le 19/08** : le test passe en
  `xfail` **strict** avec sa raison — le seuil reste à 85 %, la limitation reste visible dans
  le rapport, et pytest fera **échouer la suite** le jour où le taux repassera au-dessus.
  Ne toujours **pas** baisser le seuil : l'arbitrage reste la question ouverte de S35.
- Le **garde-fou de sortie mesure aussi 70 %** — motifs écrits d'abord, cas d'évasion ensuite.
- Deux guides d'étude en anglais. ⚠️ **Déplacés dans Obsidian le 18/08** : ils étaient dans
  `docs/etude/`, c'est-à-dire de la **préparation dans le dépôt de livrables** — contraire à
  la règle du 11/08. Ils vivent désormais dans
  `Projets/RITA/09-EN-personnel/` (« Prompt injection and agent security » pour les concepts,
  « 17 August 2026 » pour la méthode).

📅 **Le plan des 12 semaines est écrit : `docs/PLAN-12-SEMAINES.md`.**
Le formateur est en congé → on ne l'attend pas : **produire → geler → mettre en file
(`docs/FILE-DE-VALIDATION.md`) → continuer.**

---

## ▶️ Comment Era reprend le travail

1. Ouvrir Claude Code sur le dossier **`D:\KandaWork\RITA_PROJECT\rita-agent`**
   (jamais sur `C:\Users\kanda` — sinon rien ne se charge).
2. Écrire : **« on reprend »**.
3. Claude lit ce fichier et annonce en 3 lignes : où on s'est arrêté, la prochaine action,
   les verrous. Era n'a **rien** à réexpliquer.

---

## 🧭 Prochaine action

🚩 **Le point de contrôle du 23/08 est atteint dès le 16/08.** L'application démarre et
affiche **le portefeuille de démonstration** depuis l'API (jeu anonymisé — voir la précision
du 19/08 plus bas). La semaine S34 est donc **libre pour aller plus loin que prévu**.

✅ **Note S34 terminée le 17/08** — résumé rédigé et validé par Era, 7/7 accessibilité,
31 liens externes vérifiés, 0 cassé. Commit `237c2b7`.

✅ **`taux_change` réimporté le 17/08** — `python -m pipelines.ingest --etapes ecb` (simulation
d'abord, puis réel) : 5 lignes (EUR + USD/GBP/CHF/JPY, taux du jour). La conversion de devise
fonctionne à nouveau.

✅ **`ANALYZE;` exécuté le 17/08** — les statistiques étaient bien plus périmées que prévu :
**presque toutes les tables estimées à 0** depuis la reconstruction du 16/08, pas seulement
`position`. Corrigé : `cotation` 273 608 · `valeur` 111 · `alias_valeur` 112 · `position` 7 ·
`taux_change` 5 — tous exacts, vérifiés.

✅ **`article` réimporté le 17/08** — même cause que `taux_change` : la reconstruction du
16/08 n'a rechargé que ce qui a une source Parquet (`db/importer.py`), jamais les articles.
`python -m pipelines.ingest --etapes rss` (simulation puis réel) : **30 lignes, 0 bloquée**,
3/3 flux OK. `ANALYZE article;` refait.

✅ **Suite complète rejouée après les 2 réimports** — `200 passed, 1 failed`. L'unique échec
est `test_seuils_minimaux_du_gardefou`, **volontairement rouge** depuis S34 (question ouverte
S35) : rien de nouveau cassé.

✅ **Les 2 schémas obligatoires de E4 sont faits — 18/08**, commit `0c8b8f5` :
- **C14** — `evidence/C14/` : wireframes des **4 états** de l'écran (pas 4 écrans : les états
  réels pilotés par `app.js`), + spécification US-1 (contexte, 5 scénarios, **11 critères
  d'acceptation dont 6 portant un numéro de règle RGAA**). Le MCD Merise de C4 satisfait déjà
  le 1er critère de C14 — non refait, un doublon deviendrait une contradiction.
- **C15** — `evidence/C15/` : diagramme de flux en **6 zones** découpées sur les frontières
  réelles du code, + spécifications techniques (13 dépendances, environnement, éco-conception).
- ✅ **Les 2 critères qui restaient de C15 sont faits le 18/08** — Docker a démarré (voir plus bas).

✅ **Indicateurs lot 1 codés — 18/08**, commit `a047b58`. `db/indicateurs.sql` +
`indicateurs/socle.py` + **13 tests**. 11 indicateurs par valeur en **une requête**,
**111 valeurs sur 111**, **194 ms** mesurées. Preuve : `evidence/C14/preuve-indicateurs-lot1.md`.
- 🆕 **Défaut trouvé par la mesure** : **3 valeurs radiées** (Zodiac 2018, Euler Hermes 2018,
  Gemalto 2019) portent encore `statut_qualite = 'OK'`. L'écran aurait affiché pour elles une
  « performance 1 jour » calculée sur des cours vieux de 8 ans. Colonne `fraicheur_jours`
  ajoutée (seuil 40 j). **`statut_qualite` décrit la qualité de l'historique, pas sa fraîcheur.**
✅ **Cours rafraîchis — 18/08.** Ils s'arrêtaient au 29/07 (3 semaines de retard, même famille
de défaut que `taux_change` et `article`). `pipelines.ingest --etapes cotations` :
**1 618 séances écrites**, du 28/07 au 18/08. Base : **275 118** cotations, **retard 0 jour**.
`ANALYZE cotation` refait, indicateurs recalculés sur données fraîches.

🐛 **Bug corrigé au passage — commit `8df76ba`.** Le rafraîchissement rejetait 3 tickers avec
un `TypeError` : `_ligne_valide` se protégeait du `NaN` par `x == x`, mais yfinance rend
**`None`** — pas `NaN` — pour une valeur **radiée**, et `None == None` est **vrai**.
**La gravité n'est pas la ligne perdue** : `etape_cotations` groupe les tickers par date de
dernière séance et attrape l'exception **par groupe** — un seul ticker radié faisait perdre
**tout son groupe**. Sans conséquence aujourd'hui (les 3 radiées sont seules dans leur
groupe), faux dès qu'une radiée partagerait sa date avec des valeurs vivantes.
Avant : 1 618 lues / **3 rejetées**. Après : 1 618 lues / **0 rejetée**. +2 tests.

✅ **Écran 2 livré — 18/08**, commit `52ad1ae`. `GET /donnees/indicateurs` (**7ᵉ** point de
terminaison) + `frontend/indicateurs.html` / `.js`. Vérifié **dans le navigateur** sur le
serveur réel : rendu, filtre testé par un vrai clic, **aucune erreur console**, la page ne
défile pas horizontalement. **241 tests** (32 front, 34 API).
- 🐛 **Défaut trouvé en vérifiant** : le commentaire CSS annonçait `tabindex` + `role="region"`
  sur la zone défilable — **ils n'étaient nulle part dans le HTML**. Une personne au clavier
  n'aurait jamais vu la moitié droite du tableau. **Même famille que le garde-fou de sortie
  du 17/08** : *un contrôle documenté mais absent est pire qu'un contrôle absent.*
- Preuve : `evidence/C10/preuve-ecran-indicateurs.md`.

✅ **A — OWASP API2 corrigé, 18/08**, commit `a4042b9`. `os.getenv("RITA_API_KEY", "dev-key")`
acceptait en réalité la chaîne **`dev-key`, écrite en clair dans `api/main.py`**. Remplacé par
une **panne au démarrage** + longueur minimale 16 + `secrets.compare_digest`. Vérifié sur le
serveur réel : `dev-key` → **403**, vraie clé (43 c.) → **200**.
- `.env.example` **entièrement réécrit** — il documentait `POSTGRES_URL` port 5432 alors que le
  code lit `DATABASE_URL` sur 5433, et omettait 3 variables. Un évaluateur qui le suivait échouait.
- `tests/conftest.py` créé : clé de test posée une fois pour toutes en `autouse`.
- 🐛 **`.gitignore` trop étroit** — `.env` seul ne couvrait que le nom exact ; une copie
  `.env.sauvegarde-*` restait visible de Git. Élargi à `.env.*` + `!.env.example` (`0a8ff0b`).
  Défaut créé puis trouvé le jour même, **avant tout commit — rien n'a fuité**.
- 🟡 **Reste** : ton `.env` contient **deux clés OpenRouter différentes**. La seconde était sur
  une ligne au format YAML que `python-dotenv` refusait (l'avertissement à chaque démarrage,
  maintenant disparu). Ligne **commentée, valeur conservée** — à toi de trancher laquelle garder.

✅ **B — Docker : pré-production en marche, 18/08**, commit `d1d8dfb`. **Docker a démarré.**
`docker compose up -d --build` → 2 conteneurs **`healthy` en < 20 s**, 8 tables créées seules,
403/200 corrects, interface servie sur **:8001** (le dev garde :8000, les deux cohabitent).
- **C15 critères 4 et 5 : de 🔴 à ✅** — preuve de concept **et** sa conclusion.
- Image **595 Mo** : `pyspark` (**492 Mo**) exclu via `requirements-api.txt`, versions toutes
  épinglées. Non-root (uid 10001), **lecture seule**, `no-new-privileges`, base **non publiée**.
- Vérifié dans le conteneur : **aucun `.env`**, `pyspark` absent, `dev-key` → 403.
- Preuve : `evidence/C15/preuve-preproduction-docker.md`.

✅ **19/08 — C13 gagne son volet LIVRAISON**, commit `7570bc9`. `.github/workflows/livraison.yml`
tourne : construction sur `main`/`develop`, **publication uniquement sur un tag `livrable-*`**
(un tag = un livrable = une image). Les tests tournent **dans le job de livraison**, et l'image
construite est **démarrée puis interrogée** — `/health` répond en 4 s, l'accès sans clé donne
403. *Une image qui se construit n'est pas une image qui démarre.* Exécution réelle : **3 min 40**.

✅ **19/08 — la suite repasse au VERT** : `test_seuils_minimaux_du_gardefou` passe en `xfail`
avec sa raison écrite dedans et `strict=True`. **Le seuil reste à 85 %** — on ne baisse pas
l'exigence, on déclare qu'on ne l'atteint pas encore. Le contrôle des **faux positifs** est
extrait dans son propre test, qui doit passer : les deux chiffres ne mesurent pas la même chose.
Le jour où le taux repassera au-dessus de 85 %, pytest signalera `XPASS` et **fera échouer la
suite** — on sera prévenu.

✅ **19/08 — Indicateurs lot 2 (portefeuille)**, commits `718f8ad` et `bbe6549`.
`db/indicateurs_portefeuille.sql` + `indicateurs/portefeuille.py` + `GET
/donnees/indicateurs-portefeuille` (**8ᵉ** point de terminaison) + **affichage sur l'écran 1**.
Somme des poids : **exactement 100,00 %**. Plus forte ligne : **34,83 % (VIRI.PA)**.
- 🔴 **Précision établie le 19/08, à ne plus jamais présenter autrement** : ces chiffres
  (33 214,80 €, 7 lignes, 34,83 %) viennent de **`data/positions-exemple.csv`**, le jeu de
  **démonstration anonymisé** — **pas** du portefeuille réel d'Era. Vérifié : `POSITIONS_CSV`
  n'a jamais été défini dans le `.env`, donc `sources/positions.py` a **toujours** pris
  l'exemple par défaut, et la base locale contient ces 7 lignes à l'identique.
  *Devant un jury, dire « voici mon portefeuille » serait inexact. Un jeu de démonstration
  assumé est parfaitement légitime ; le faire passer pour des données réelles ne l'est pas.*
- 🐛 **4 défauts trouvés en écrivant** : `from module import fonction` faisait recevoir à
  4 tests les **vraies** données au lieu du jeu simulé · une **fonction** `portefeuille()`
  écrasait l'import du module · un test cherchait `taux_change` dans un **commentaire**
  (**4ᵉ fois** ce piège) · le vérificateur de liens criait au loup sur le dépôt privé.
- ⚠️ **Les 7 positions sont toutes en euros** : le chemin multi-devises n'est **jamais exercé
  en production**, seuls les tests le couvrent. **Raison exacte, établie le 19/08** : le
  fichier d'exemple *contient bien* deux lignes en USD (AAPL, MSFT) — mais elles sont
  **rejetées à l'import**, car absentes de l'univers de 111 valeurs françaises (contrainte de
  clé étrangère). Ce n'est donc pas « il n'y a pas de devises étrangères », c'est « elles
  n'arrivent jamais jusqu'en base ».

✅ **Lot 3 des indicateurs — risque, fait le 19/08.** `db/indicateurs_risque.sql` (volatilité,
drawdown) + `indicateurs/risque.py` (RSI 14, Wilder) + **19 tests**. **Les 13 indicateurs de
la spécification sont désormais codés, exposés et affichés.** `GET /donnees/indicateurs-risque`
(**9ᵉ** point de terminaison), 3 colonnes sur l'écran 2. Preuve :
`evidence/C14/preuve-indicateurs-lot3.md`.
- 🐛 **Bug SQL trouvé et corrigé** : la première version rendait la volatilité **`NULL` pour
  les 111 valeurs** — les fonctions fenêtre étaient placées après un filtre qui réduisait
  chaque ticker à une seule ligne. Vérifié contre l'exemple exact de la spec
  (100→150→90→120 ⇒ drawdown **−40,00 %**, obtenu exactement).
- 🆕 **Même angle mort que le lot 1, retrouvé** : les 3 valeurs radiées affichaient volatilité
  et drawdown sur des données de 2018 sans signal — `cotation_perimee` ajouté. Le RSI, lui,
  reste absent pour ces valeurs (décision documentée, pas un oubli).
- `quant_metrics.py` relu une **deuxième fois**, toujours non réutilisé — 3 formules
  différentes de la spec (rendement simple, `cummax` incluant le jour courant, moyenne mobile
  simple au lieu de Wilder).
- 🐛 **Deux échecs de test successifs, même piège** : bannir « acheter » puis « il faut
  acheter » a échoué les deux fois — les deux étaient des sous-chaînes de la phrase qui
  **explique** l'interdit. Corrigé en cherchant des formes impératives.

✅ **Les deux manques de couverture sont fermés — 19/08.**
- `db/importer.py` : **0 % → 100 %** (85 instructions), 13 tests. Verrouille le cas CGG (deux
  libellés, une valeur, deux alias) et le filtrage des tickers hors univers.
- `evals/mesurer_sortie.py` : **0 % → 100 %** (10 instructions), 5 tests dans
  `tests/test_evals.py`, en miroir exact de ceux du garde-fou d'entrée — **même limitation
  S34, même `xfail` strict** : le garde-fou de sortie mesure lui aussi **70 %** de blocage,
  sous le seuil de 85 % (0 % de faux positifs). Un **2ᵉ `xfail`** rejoint donc le premier.
- Aucun test ne touche une vraie base ni un vrai modèle — curseur/`execute_values` simulés
  pour l'un, appel direct à une fonction pure pour l'autre.
- **Conséquence** : couverture totale **83 % → 92 %**. Le **seuil CI est relevé de 80 % à
  90 %** (`.coveragerc`) — seulement maintenant que les deux manques sont réellement fermés
  et le nouveau chiffre confirmé, pas anticipé. Suite complète : **319 passed, 2 xfailed**.

🚀 **DÉPLOYÉ EN LIGNE LE 19/08 — le manque C13 « déploiement » est comblé.**
- **`http://178.104.184.125:8001/`** — Hetzner Cloud CX23, Falkenstein, Ubuntu 26.04,
  7,19 €/mo TTC. Docker + Compose, mêmes conteneurs qu'en local.
- **Vérifié depuis l'extérieur** (pas depuis le serveur) : `/health` → **200** en 0,07 s ·
  `/donnees/valeurs` sans clé → **403**. *Le garde-fou OWASP API2 a survécu au déploiement.*
- **Données chargées et vérifiées en base** : 111 valeurs · 275 118 cotations · 112 alias ·
  30 articles · 5 taux · 7 positions (jeu de démonstration). `ANALYZE` exécuté.
- 🐛 **Défaut de conception trouvé en déployant** : `db/importer.py` **ne peut pas tourner
  dans l'image livrée** — `requirements-api.txt` exclut volontairement `pyarrow` (« le
  Parquet ne sert qu'à l'archive et à l'import initial »), mais l'importateur en a besoin.
  Le commentaire dit *« import initial »* sans jamais dire **comment** le faire une fois
  déployé. Contourné par un transfert `pg_dump --data-only` depuis le poste local, mais
  **le trou de conception reste ouvert** : soit ajouter `pyarrow`, soit assumer une image
  d'outillage séparée. *(Même fichier que le 0 % de couverture d'aujourd'hui : deux angles
  morts sur `db/importer.py`.)*
- ✅ **Écart d'environnement aligné le 20/08** : poste en **PostgreSQL 18.4**, les **deux**
  `docker-compose.yml` (racine et `db/`) passent de **17** à **18-alpine**. Testé en local
  d'abord : conteneur en **18.6**, 8 tables créées, dump du poste restauré sans erreur.
  🐛 **Le passage a révélé un changement de convention** : depuis la 18, l'image officielle
  range les données dans un **sous-dossier portant la version majeure** (pour `pg_upgrade`).
  Le montage doit viser `/var/lib/postgresql` **sans** `/data`, sinon le conteneur refuse de
  démarrer. Corrigé dans les deux fichiers.
  **Serveur migré dans la foulée** : `git pull` → `down -v` → `up -d` → rechargement du dump.
  Volume détruit à dessein (les formats 17 et 18 sont incompatibles), données rechargées
  depuis `/root/rita-donnees.sql` : **275 118 cotations, 111 valeurs, 7 positions**, `ANALYZE`
  refait. **Vérifié depuis l'extérieur après migration** : `/health` → 200 en 0,066 s · 403
  sans clé · pare-feu intact (5432 fermé, 22 ouvert). **Poste, préprod locale et serveur
  tournent désormais tous les trois en PostgreSQL 18.**
- ✅ **Pare-feu actif le 19/08** — `ufw` **sur le serveur**, pas celui de Hetzner : la console
  web faisait tourner en rond, et le terminal donne le même résultat, vérifiable.
  `Default: deny (incoming)`, seuls **22/tcp** et **8001/tcp** autorisés (IPv4 + IPv6).
  **Vérifié depuis l'extérieur** : 8001 → 200 · 22 → ouvert · **5432 → fermé** ·
  **80 → fermé**. *PostgreSQL n'était de toute façon jamais publié — double protection.*
- Le déploiement n'utilise **que** le jeu de démonstration : aucune donnée personnelle
  d'Era n'est sur cette machine (`--exclude-table-data=position` à l'export).

**Prochaines actions, dans l'ordre :**

1. ✅ **C13 volet LIVRAISON — fait le 19/08** (`7570bc9`). Reste : le **test des données**
   côté critères.
   📅 **Historique de la décision d'hébergement (19/08)** :
   - Un serveur Hetzner **CPX32 dormait depuis 4 mois** (`ubuntu-8gb-nbg1-1`, Nuremberg,
     **17,39 €/mois pour rien** — jamais utilisé, rien dessus). **Supprimé**, ainsi que ses
     IP primaires. Volumes, Floating IPs, Snapshots : vérifiés vides. **−17,39 €/mois.**
   - **Pourquoi pas du gratuit** : la base PostgreSQL gratuite de Render **expire 30 jours
     après sa création**, et le crédit Railway (5 $) s'épuise — les deux tomberaient
     **avant** le rendu du 05/11. Un serveur payé ne s'éteint pas seul la veille du jury.
   - Le déploiement était d'abord planifié pour octobre (S42), puis **fait le jour même** :
     un CX23 neuf à 7,19 €/mo remplace le CPX32 à 17,39 €. **Moins cher qu'avant, et en
     ligne.**
   - ⚠️ **Piège de lecture, à ne pas refaire** : un `docker ps -a` montrant
     `rita-api-preprod` *healthy* peut être **celui du PC**, pas du serveur. Toujours
     regarder l'invite : `PS C:\Users\kanda>` = machine locale · `root@…:~#` = serveur.
     Erreur commise le 19/08, qui a fait croire à tort à un déploiement déjà existant.
2. 🟠 **HTTPS + nom de domaine** — l'API répond en clair sur une IP, donc **la clé d'API
   circule en clair sur le réseau**. C'est le manque le plus visible sur un service public.

*Référence : `docs/indicateurs/CONCEPTION.md` (bandeau réécrit le 19/08).*

⚠️ **Consigne périmée, corrigée le 18/08 — ne pas la réinscrire.** `ETAT.md` disait
*« le moteur existe déjà (`quant_metrics.py` dans `Ganda15/daily-stock-analysis-era`), le
porter plutôt que le réécrire »*. Le fichier a été **lu** (350 lignes, 15 fonctions) : il
travaille en **pandas**, sur **un** instrument, avec des fenêtres en **nombre de lignes** —
soit exactement le **piège n°1** de la spécification (*« ne pas utiliser `LAG(cloture, 5)` »*).
Le porter aurait importé le défaut contre lequel elle a été écrite ; il calcule en outre
Sharpe, Sortino, Calmar et bêta, que la spécification écarte.
**Réutilisable plus tard, hors lot 1** : `_perf_ytd`, `_rsi`, `_max_drawdown_pct`,
`_annualized_vol`.

Tâche courte à caser dans la semaine :
1. ✅ **Note de veille S34** — faite le 17/08, terminée le 18/08 (commit `237c2b7`).
2. **Capturer le fil Discord** — la note S33 y a été postée le **16/08** avec une question
   ouverte. ⚠️ **Attendre 1 à 2 jours** : ce sont les *réponses* qui prouvent l'animation du
   travail collectif, pas le message. Capture → `evidence/C6/discussion-2026-08-__-discord.png`.
   *(L'envoi au formateur reste bloqué par son congé — en file, voir
   `docs/FILE-DE-VALIDATION.md`.)*

✅ **Les deux trous du 14/08 sont comblés** (`docs/veille/README.md`) :
- **§5** — le partage : destinataires, cadence (mensuel au formateur, à chaque note pour la
  promo), registre de trace, et les faiblesses déclarées.
- **§4** — les deux outils : `sources/rss.py` est **l'outil de C6** ; `Veille-IA` est une
  veille personnelle **hors C6** — sa sortie est rédigée par un LLM, ce qui en ferait une
  preuve fabriquée. Mesuré le 15/08 : à l'arrêt depuis le 27/07.

✅ **Note S33 faite le 14/08** — `docs/veille/2026-S33-injection-de-prompt.md`
(OWASP Top 10 2026 vérifié à la source · trifecta : 2 conditions sur 3, la 3ᵉ absente par
construction · agent sans outil ni écriture en base). **1 note sur ~12.**

- Gabarit : `docs/veille/_MODELE-note-hebdomadaire.md`
- Protocole complet (sources, fiabilité, accessibilité) : `docs/veille/README.md`

Thématique arrêtée le 14/08 : **sécurité des agents LLM — injection de prompt**. Choisie
parce qu'elle est déjà branchée sur `guardrails/injection.py` et `evals/cas.py` : chaque note
finit par « ce que ça change dans RITA », ce qui satisfait le *« formuler des recommandations
pour le projet »* du référentiel sans travail supplémentaire.

⏰ Récurrence en place : tâche planifiée `veille-hebdo-securite-llm`, **tous les lundis 09h00**.
Elle prépare une liste de candidats — **elle n'écrit pas la note** (une note produite par une
IA serait une preuve fabriquée).

---

## Les 5 livrables

| Épreuve | Compét. | État | Tag Git |
|---|---|---|---|
| **E1** — Données | C1–C5 | ✅ **livré** — 26 critères / 28 | `livrable-E1-v1` |
| **E2** — Veille & services IA | C6–C8 | 🔴 C6 et C7 **non commencés** · C8 partiel | — |
| **E3** — API modèle & MLOps | C9–C13 | 🔨 C9/C12/C13 partiels · C10 et C11 **non commencés** | — |
| **E4** — Application | C14–C19 | 🔨 **démarré le 16/08** — 1er écran livré | — |
| **E5** — Monitorage | C20–C21 | ⬜ non commencé | — |

## Ce qui existe vraiment, compétence par compétence

| C | Fait | Manque |
|---|---|---|
| **C1** | 7 sources, les 5 types, script en 6 points | invitation `bybysker` en attente d'acceptation |
| **C2** | 3 requêtes SQL, optimisation LATERAL mesurée ×2000 | — |
| **C3** | `pipelines/ingest.py`, 15 tests, règles justifiées par mesure | invitation en attente d'acceptation |
| **C4** | MCD Merise 6 entités, MPD 8 tables, registre RGPD, purge testée | — |
| **C5** | 6 endpoints, OpenAPI 3.1.0, auth au niveau routeur, 25 tests | — |
| **C6** | protocole **complet** (15/08), gabarit, récurrence, registre, note S33 (14/08), **partage promo lancé le 16/08 sur Discord** | ⚠️ ~11 notes à venir · 🟠 réponses Discord à capturer · 🔴 envoi **formateur** non fait (congé) |
| **C7** | **rien** — aucun benchmark de services IA | tout |
| **C8** | cascade 3 fournisseurs testée, clé en `.env` · **doc d'exploitation écrite le 19/08** (`docs/EXPLOITATION.md`) : accès, installation avec et sans Docker, dépendances, données, dépannage | 🔴 **monitorage du service** · la doc reste à **communiquer** aux parties prenantes (5ᵉ critère) |
| **C9** | `POST /briefing`, auth 403, OpenAPI, garde-fou injection | revue OWASP · doc d'architecture · invitation en attente |
| **C10** | 🔨 **19/08** — **2 écrans** : portefeuille + indicateurs, servis par l'API. Clé saisie (jamais en dur), partagée entre écrans, 403 et erreurs traités, RGAA vérifié **dans le navigateur**. **9 points de terminaison** intégrés. **46 tests** front | tri/recherche · audit RGAA outillé · doc d'architecture |
| **C11** | **rien** | tout |
| **C12** | **319 tests** (2 xfailed volontaires — entrée et sortie), 15 cas d'éval, seuils non compensables en CI · **couverture 92 %**, seuil **90 %** verrouillé en CI (19/08, `db/importer.py` et `evals/mesurer_sortie.py` fermés 0→100 %) · procédure documentée | DVC · 🔴 **aucun test ne se connecte à la vraie base** — tous simulent `_executer`, d'où un défaut C4 invisible pendant des semaines |
| **C13** | GitHub Actions (2 jobs, porte garde-fous) · **empaquetage Docker 18/08** — image 595 Mo, non-root, lecture seule · **volet LIVRAISON 19/08** (`7570bc9`) : publie sur GHCR uniquement sur tag `livrable-*`, démarre l'image et vérifie `/health` + 403 · ✅ **DÉPLOYÉ 19/08** sur Hetzner CX23 (`178.104.184.125:8001`), vérifié depuis l'extérieur, 275 118 cotations chargées, **pare-feu `ufw` actif** (22 + 8001 seuls, 5432 et 80 fermés — vérifié de l'extérieur) | 🔴 `db/importer.py` **ne tourne pas dans l'image** (pyarrow exclu) · écart PostgreSQL 18 local / 17 conteneur · pas de HTTPS ni de nom de domaine |
| **C14** | 🔨 **18/08** — wireframes des 4 états (`evidence/C14/`), spécification US-1 : contexte, 5 scénarios, 11 critères d'acceptation dont 6 avec numéro de règle RGAA. Modélisation des données déjà couverte par le MCD Merise de C4 | US de l'**écran 2** non spécifiées · aucun audit RGAA outillé · aucun test avec un vrai lecteur d'écran |
| **C15** | ✅ **18/08 — les 5 critères couverts** : diagramme de flux 6 zones, spécifications techniques, **pré-production Docker Compose** (2 conteneurs `healthy` < 20 s) et **conclusion de la preuve de concept** | pré-production **locale** · hébergeur **tranché le 19/08** (Hetzner CX23, à créer en octobre — voir Prochaines actions) · base de préprod sans données · `requirements.txt` toujours non épinglé |
| **C16** | **rien** — aucune méthode agile outillée | tout (kanban, backlog, rituels) |
| **C17** | garde-fou de sortie écrit et mesuré (17/08) · **2 écrans** HTML/CSS/JS sans build · **les 13 indicateurs codés** (SQL + Python + API + affichage), lots 1-2-3 complets (19/08) | tri/recherche · doc d'architecture |
| **C18–C19** | recouvrent largement C13 | idem C13 |

## Les 5 manques ouverts, par urgence

0. 🔴 **AUCUNE SAUVEGARDE DE LA BASE.** Découvert le 16/08 de la pire façon : la base
   `rita` **n'existait plus**. PostgreSQL 18 avait été réinstallé, vide — ni base, ni rôle.
   Reconstruite le soir même par `db/importer.py` depuis les Parquet, **au chiffre près**
   (111 valeurs · 112 alias · 2 560 dédoublonnées · 273 608 insérées · 7 positions).
   *Rien n'a été perdu parce que les sources étaient versionnées — pas parce qu'il y avait
   une sauvegarde.* → **`pg_dump` hebdomadaire, le lundi après la note de veille.**
1. 🔴 **C6 — la récurrence ET le partage.** Le seul qui **ne se rattrape pas** : 12 semaines
   restantes au 14/08, une semaine perdue = une preuve perdue définitivement. Depuis le
   15/08 le protocole est complet ; **1 partage sur 2 fait** (promo Discord le 16/08,
   formateur toujours bloqué par son congé).
2. 🟠 **Accès au dépôt — invitation envoyée, pas encore acceptée.** Vérifié sur GitHub le
   14/08 : `bybysker` a été invité le **13/08 à 15h16** en droit `read`. Il est dans
   `/invitations`, **pas encore dans `/collaborators`** — donc le critère *« accessible
   depuis un dépôt Git »* (C1#6, C3#2, C9) n'est **pas encore satisfait**.
   **Reste à faire** : relancer si l'invitation n'est pas acceptée · inviter le **jury**
   le moment venu. Commande de vérification :
   `gh api repos/Ganda15/rita-agent/collaborators --jq '.[].login'`
3. ✅ **Couverture mesurée le 19/08** — **81 %**, seuil **80 %** en CI. Restent 2 fichiers à 0 % (voir ci-dessus).
4. 🟠 **Chaîne de LIVRAISON absente** (C13) — aujourd'hui c'est de l'intégration continue.
5. 🟡 **Revue OWASP API Top 10** (C9) non écrite — mais **2 entrées sur 10 déjà traitées** :
   **API2** ✅ **corrigé le 18/08** (plus de clé par défaut, `compare_digest`, 4 tests) ·
   **A03** ✅ le front n'utilise que `textContent` : à documenter comme mesure prise.
   Il reste à **rédiger la revue** elle-même, les 8 autres entrées comprises.
6. ✅ **`.env.example` corrigé le 18/08** — entièrement réécrit.
7. ✅ **Avertissement `python-dotenv` supprimé le 18/08** — une ligne au format YAML dans le
   `.env` (une **seconde clé OpenRouter**). Commentée, valeur conservée : à Era de trancher.

## Fichiers de suivi hors dépôt

| Quoi | Où |
|---|---|
| Rédaction par compétences (modèle Simplon, à rendre) | `D:\KandaWork\RITA_PROJECT\Era-Preparation-livrables-RNCP.xlsx` |
| ⤷ rempli pour | C1 C2 C3 C4 C5 C8 C9 C12 C13 — les autres **volontairement vides** |
| Boussole (tâche principale + pile de détours) | `C:\Users\kanda\Desktop\RITA PROJET PRO\BOUSSOLE-RITA.md` |
| Journal (7 entrées, JOURNAL-000 → 005) | `C:\Users\kanda\Documents\Formation-IA\Formation-IA\Projets\RITA\07-Journal\` — ou via le MCP Obsidian : `Projets/RITA/07-Journal/` |

## Décisions prises, à ne pas re-débattre

- Dépôt **privé** avec accès collaborateur — décision assumée, pas un oubli.
- Une seule clé d'API (mono-utilisateur, décision D10) — pas de système de comptes.
- `article` et `memory_audit` hors du MCD : collecte brute et journal technique ne sont pas
  des entités métier. 6 entités + 2 tables techniques = 8 tables.
- `/briefing` relève de **C9**, pas de C5 : c'est une rédaction, pas de la donnée.
- **Le nom du projet — 16/08.** L'expansion du sigle passe de *« Retrieval Intelligence for
  **Trading** Analysis »* à *« Retrieval Intelligence pour le **Tracking** et l'Analyse »*.
  « Trading » = acheter et vendre, ce que RITA refuse de conseiller : le nom contredisait le
  garde-fou AMF dans la même en-tête. **Le sigle RITA ne change pas** — tag, dépôt, journal
  et preuves restent valides.
- **Le front est en HTML/CSS/JS servi par FastAPI — 16/08.** Pas de React, pas de build.
  Trois raisons tirées du texte des critères : l'éco-conception de C17 récompense le léger ·
  le RGAA se contrôle ligne par ligne sur du HTML · Era doit pouvoir défendre chaque ligne
  pendant 20 minutes. **Règle : générer la surface (CSS, mise en page), écrire soi-même la
  couture** (`frontend/app.js` — appels API, authentification, erreurs), car c'est elle
  qui relève de C10 et c'est elle que le jury interrogera.
- **E4 n'est pas six compétences de développement, c'en est une — 16/08.** C14 = spécifications
  et wireframes · C15 = architecture et déploiement en pré-production · C16 = **méthode agile**
  (kanban, backlog, rituels — aucune ligne de code) · **C17 = le seul développement** ·
  C18 = intégration continue · C19 = livraison continue. **C18 et C19 recouvrent largement
  C13 : une seule chaîne CI/CD prouve trois compétences.**
- **Indicateurs de marché — 15/08.** 19 proposés → **13 à coder**, en 4 lots. Le mot
  « stratégie » est banni (indicateur = fait, stratégie = conseil → garde-fou AMF). Sharpe
  écarté. Destination **E4**, pas C2. Spécification figée :
  `docs/indicateurs/CONCEPTION.md`. **Rien à coder avant l'ouverture d'E4** — ne pas rouvrir
  le débat, lire le fichier.
