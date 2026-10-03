# Preuve C17 : éco-conception et accessibilité des trois écrans, mesurées le 03/10/2026

> **Critères visés** (livrable E4) : C17, *« Éco-conception »* (jusqu'ici « aucune mesure », voir `docs/rapports/E4/recomptage-criteres-2026-10-03.md`) ;
> C14, accessibilité *« formulée en s'appuyant sur un standard »*, dont la spécification de l'écran 1 disait *« Aucun audit RGAA outillé n'a été passé »*.
> Tâche T3 du plan E4 ([`../../docs/PLAN-E4-rapport.md`](../../docs/PLAN-E4-rapport.md)), carte #25, décision D2 d'Era : Lighthouse.

## 1. Le verdict, en six lignes

| | |
|---|---|
| **Accessibilité automatique** | **100 sur 100 et zéro échec** aux 10 étapes mesurées (3 écrans, 4 états), en mode bureau comme en mode mobile |
| **Clavier, mesuré** | ordre de tabulation logique sur les trois écrans, contour de focus de 2 à 3 pixels sur chaque élément, aucun piège, focus placé sur le résultat à l'arrivée du briefing |
| **Poids** | 20 à 25 Ko pour un écran vide, 3 ou 4 requêtes, aucune ressource externe |
| **EcoIndex** | **A** pour le portefeuille (90) et le briefing (90), **D pour l'écran indicateurs avec ses 111 lignes (51)** |
| **Cause du D** | le nombre d'éléments de la page (1 860), pas son poids : la compression ne le fait passer que de 51 à 52 |
| **Ce qui manque à la chaîne** | aucune compression, aucun en-tête de cache, un `favicon.ico` introuvable ; corrections à faire **après** le tag du 15/10 (carte à ouvrir, §6) |

## 2. Ce qui a été mesuré, et comment

| Élément | Valeur |
|---|---|
| Outil d'audit | **Lighthouse 13.5.0** (Google, licence Apache-2.0), installé depuis le registre npm dans un dossier temporaire, hors du dépôt, avec l'accord d'Era (D2) |
| Navigateur | HeadlessChrome 154.0.0.0 ; mesures prises le 03/10/2026 à 19 h 15 UTC |
| Modes | **bureau** (1 350 × 940, sans ralentissement) et **mobile** (412 × 823, ralentissement standard de Lighthouse) |
| Méthode | le « mode flux » de Lighthouse : une navigation par état, puis un instantané de la page affichée, ce qui permet de mesurer aussi l'écran **avec ses données**, pas seulement la page de connexion |
| Application mesurée | le dépôt à l'état du 03/10, servi **en local** (port 8001), base locale réelle (111 valeurs) |
| Précautions | clé d'API **jetable**, fournie par une variable d'environnement et jamais écrite dans un fichier ; **traçage Langfuse coupé** pour ne rien écrire en production (leçon d'INC-006) ; l'appel payant au modèle remplacé, pour l'écran 3, par **un vrai texte produit par le modèle le 03/10** (banc C7) |
| Calcul EcoIndex | **code et tables officiels** du dépôt `cnumr/ecoindex_python` (fichiers `compute/ecoindex.py`, `data/quantiles.py`, `data/grades.py`, lus le 03/10/2026), recopiés sans modification ; entrées : éléments du DOM, taille en Ko, nombre de requêtes |
| Compression | **mesurée**, pas estimée : chaque fichier et chaque réponse de l'API compressés en gzip niveau 9, ce que fait par défaut le composant de compression de FastAPI |

Fichiers dans [`mesures-2026-10-03/`](mesures-2026-10-03/) :

| Fichier | Contenu |
|---|---|
| [`resume-bureau.json`](mesures-2026-10-03/resume-bureau.json), [`resume-mobile.json`](mesures-2026-10-03/resume-mobile.json) | par étape : scores, poids, requêtes, éléments du DOM, métriques, audits d'accessibilité en échec |
| [`flux-portefeuille-bureau.html`](mesures-2026-10-03/flux-portefeuille-bureau.html), [`flux-indicateurs-bureau.html`](mesures-2026-10-03/flux-indicateurs-bureau.html), [`flux-briefing-bureau.html`](mesures-2026-10-03/flux-briefing-bureau.html) | les rapports Lighthouse complets, à ouvrir dans un navigateur |
| [`clavier.json`](mesures-2026-10-03/clavier.json) | le parcours au clavier de chaque écran |
| [`ecoindex-resume.json`](mesures-2026-10-03/ecoindex-resume.json) | l'EcoIndex avant et après compression, par écran et par état |
| [`entrees/`](mesures-2026-10-03/entrees/) | les pages et les réponses de l'API **telles que mesurées**, pour rejouer le calcul |
| [`outils/`](mesures-2026-10-03/outils/) | les quatre scripts (§7) |

## 3. Accessibilité

### 3.1 L'audit automatique

| Écran | Étape | Accessibilité (bureau / mobile) | Contrôles réussis | Échecs |
|---|---|---|---|---|
| Portefeuille | sans clé / avec données | 100 / 100 | 21 / 24 | 0 |
| Indicateurs | sans clé / avec données | 100 / 100 | 21 / 23 | 0 |
| Briefing | sans clé / demande / texte affiché | 100 / 100 | 21 / 21 / 22 | 0 |

Lighthouse exécute les contrôles automatiques de la bibliothèque axe-core : ils couvrent une **partie** des critères du RGAA, pas le référentiel entier.
Dix contrôles qu'il ne peut pas faire seul sont listés « à vérifier à la main » à chaque étape : champs cliquables atteignables au clavier, ordre de tabulation, ordre
visuel, piège du focus, focus dirigé vers un nouveau contenu, repères HTML5, contenu hors écran, étiquettes et rôles des contrôles personnalisés. Le §3.2 en traite quatre par une mesure ;
le reste n'est pas fait.

### 3.2 Le clavier, mesuré ([`clavier.json`](mesures-2026-10-03/clavier.json))

Une personne parcourt chaque écran avec la touche Tabulation, à partir du haut de la page :

| Écran | Ordre mesuré | Contour du focus |
|---|---|---|
| Sans clé (les trois) | le focus arrive d'emblée sur le champ de la clé | 3 px |
| Portefeuille | lien « Indicateurs », lien « Briefing », « Comment lire ce tableau ? » | 3 px |
| Indicateurs | « Mon portefeuille », « Briefing », case « Masquer les cotations périmées », **la zone de défilement du tableau** (région nommée), « Comment lire ce tableau ? » | 3 px, **2 px sur la région** |
| Briefing | « Mon portefeuille », « Indicateurs », champ du code, bouton « Rédiger le briefing » ; après l'envoi **au clavier**, le focus est sur la région « Briefing » (`#resultat`) | 3 px |

Cela fait passer de « lecture du code » à « mesuré » : l'ordre de tabulation suit l'ordre de la page, la zone qui défile est atteignable (RGAA 7.3, WCAG 2.1.1),
le focus est visible (RGAA 10.7), et le focus est déplacé sur le résultat (WCAG 2.4.3), critère R11 de [`../C14/preuve-specifications-ecrans-2-et-3.md`](../C14/preuve-specifications-ecrans-2-et-3.md).
Aucun piège : la tabulation sort de la page après le dernier élément.

### 3.3 Ce que cela ne prouve pas

- Pas de **lecteur d'écran réel** (NVDA, VoiceOver) : le rendu vocal de `aria-live` reste non observé.
- Pas de revue **humaine** de l'ensemble des critères du RGAA : un score de 100 sur 100 n'est pas une déclaration de conformité.
- L'ordre **visuel** (par rapport à l'ordre du code), les repères HTML5 et le contenu masqué aux technologies d'assistance n'ont été relus que dans le code.
- L'écran 3 a été mesuré avec une réponse enregistrée : le temps d'attente du modèle (5 à 15 s, dit à l'écran) n'est pas dans ces chiffres.

## 4. Éco-conception

### 4.1 Les chiffres

Poids en kilo-octets de corps de réponse (les en-têtes ajoutent environ 3 % dans les mesures de transfert de Lighthouse) ; « données » = écran affiché avec ses réponses d'API.

| Écran | État | Éléments du DOM | Requêtes | Poids actuel | **EcoIndex** | gCO2e / eau (cl) par page |
|---|---|---|---|---|---|---|
| Portefeuille | sans clé | 65 | 4 | 24,9 Ko | **93, A** | 1,14 / 1,71 |
| Portefeuille | données | 138 | 7 | 28,4 Ko | **90, A** | 1,20 / 1,80 |
| Indicateurs | sans clé | 84 | 3 | 22,9 Ko | **92, A** | 1,16 / 1,74 |
| Indicateurs | **données (111 valeurs)** | **1 860** | 5 | 86,6 Ko | **51, D** | 1,98 / 2,97 |
| Briefing | sans clé | 46 | 3 | 20,5 Ko | **95, A** | 1,10 / 1,65 |
| Briefing | données (liste de l'univers) | 157 | 4 | 38,3 Ko | **90, A** | 1,20 / 1,80 |

Les « gCO2e » et les centilitres d'eau sont ceux que la méthode EcoIndex associe à chaque score : une **modélisation** de la méthode, pas une mesure de l'électricité réellement consommée.
Le nombre de requêtes du portefeuille compte la demande de `favicon.ico`, qui échoue. L'état « données » du briefing est mesuré avant l'arrivée du texte (quelques éléments de plus ensuite).

Performance (Lighthouse, première visite, bureau) : premier affichage **247 à 257 ms**, aucun blocage du fil principal, décalage de mise en page 0 à 0,007. En mobile avec ralentissement :
905 à 957 ms. Les étapes « avec clé » sont mesurées avec les fichiers déjà en cache du navigateur : leurs temps ne sont pas comparables et ne sont pas cités.

### 4.2 Ce que montrent les chiffres

- **Le poids n'est pas le problème.** Un écran vide pèse de 20 à 25 Ko, sans image, sans police téléchargée, sans bibliothèque ni service extérieur : c'est le résultat des choix documentés en C15 (pas de chaîne de build, mise en forme des nombres par le navigateur).
- **Le nombre d'éléments l'est, sur un seul écran.** La page indicateurs ajoute 16 éléments par valeur (une ligne, un en-tête de ligne, 14 cellules) : 111 valeurs font 1 860 éléments. Dans la méthode EcoIndex, le DOM pèse trois fois plus que la taille ; c'est lui qui fait passer l'écran de A à D.
- **La compression ne suffit pas à elle seule** : elle divise le poids statique par 2,6 et celui du JSON des indicateurs par 6, et le score de cet écran ne gagne qu'un point (51 vers 52). Elle est utile (moins de données transférées à chaque visite), mais elle ne change pas la note.

## 5. Les constats, chiffrés

| # | Constat | Mesure | Piste | Gain mesuré ou projeté |
|---|---|---|---|---|
| F1 | **Aucune compression**, ni en local ni sur le serveur de production (en-têtes lus : pas de `Content-Encoding`, serveur `uvicorn` directement exposé) | Lighthouse : « No compression applied » aux 3 pages | composant de compression de FastAPI | **mesuré** (gzip niveau 9) : statique 25 542 vers 9 724 o (−62 %), JSON des indicateurs 65 205 vers 10 632 o (−84 %), liste de l'univers 18 218 vers 1 664 o (−91 %) |
| F2 | **Aucun en-tête de cache** : durée de vie 0 pour la feuille de style et le script de chaque écran | Lighthouse : « Use efficient cache lifetimes », 17 à 20 Kio signalés | `Cache-Control` sur les fichiers statiques | **estimation de Lighthouse**, non mesurée : l'ETag et la date de modification présents limitent le coût réel d'une revisite |
| F3 | `favicon.ico` **répond 404** (local et production) | une erreur console à la première page ouverte (le portefeuille) : Bonnes pratiques à 96 au lieu de 100, en bureau et en mobile | une icône, ou une ligne `<link rel="icon">` vide | 1 requête de moins, 96 vers 100 |
| F4 | **1 860 éléments** sur l'écran indicateurs | EcoIndex D (51) | n'afficher d'abord qu'une partie des 111 lignes (pagination ou « afficher plus ») | **projection, pas une mesure** : environ 480 éléments pour 25 lignes, EcoIndex ≈ 77 (B) ; 884 éléments pour 50 lignes, ≈ 64 (C). Décision de produit, voir §8 |
| F5 | Feuille de style et script **bloquent le premier affichage** | Lighthouse : 70 à 90 ms en bureau, 260 à 350 ms en mobile ralenti | attribut `defer` sur les scripts | faible |
| F6 | CSS et JavaScript **non minifiés** | Lighthouse : 4 à 6 Kio | une minification | **faible une fois compressé** ; c'est le prix du choix « pas de chaîne de build », à garder ou non |
| F7 | Pas de `meta description` | SEO à 90 | une ligne | sans objet pour un outil derrière une clé ; noté, pas à faire |

Rien de F1 à F5 n'est corrigé : **aucun code d'application avant le tag du 15/10** (plan E4, §9). Le §6 dit ce qui sera fait et remesuré.

## 6. Production : ce qui a été relevé, et ce qui ne l'a pas été

Relevé par `curl` le 03/10/2026 sur le serveur de production : réponse `HTTP/1.1 200`, `Server: uvicorn`, **pas de `Content-Encoding`, pas de `Cache-Control`**,
`favicon.ico` en 404. Ses fichiers datent du **19/08/2026** (en-tête `Last-Modified`) : la feuille de style fait 6 394 octets contre 7 906 en local, et **l'écran 3 n'y existe pas**
(`/briefing.html` répond 404). La production n'a donc **pas** été auditée par Lighthouse : ses chiffres seraient ceux d'un état périmé. Elle le sera après le déploiement qui suit le tag du 15/10.

**Après le 15/10, dans l'ordre :** (1) F1, F3, F2 (trois changements de quelques lignes, test d'abord) ; (2) remesure complète avec les mêmes scripts, ce qui donne le **tableau avant/après** que le plan E4 prévoyait ;
(3) F4 seulement si Era le décide (§8) ; (4) mesure de la production une fois déployée.

## 7. Rejouer la mesure

Pré-requis : Node, Chrome, et `npm install lighthouse@13.5.0` dans un dossier temporaire. Le serveur de mesure démarre sur un autre port que celui d'usage, avec une clé jetable :

1. Définir `LH_CLE` (une chaîne jetable de 32 caractères) et démarrer l'API sur le port 8001 avec `RITA_API_KEY` égal à cette valeur et `LANGFUSE_TRACING_ENABLED=false`.
2. `node audit-rita.mjs <dossier> bureau`, puis `... mobile`, avec la variable `RESULTATS` pointant sur `evidence/C7/resultats-2026-10-03.jsonl` (texte du briefing enregistré).
3. `node clavier.mjs <fichier.json>`.
4. `python calcul-ecoindex.py entrees mesures-2026-10-03` recalcule l'EcoIndex depuis les pages et les réponses archivées, sans réseau.

Scripts : [`outils/audit-rita.mjs`](mesures-2026-10-03/outils/audit-rita.mjs), [`outils/clavier.mjs`](mesures-2026-10-03/outils/clavier.mjs), [`outils/analyse-audits.py`](mesures-2026-10-03/outils/analyse-audits.py), [`outils/calcul-ecoindex.py`](mesures-2026-10-03/outils/calcul-ecoindex.py).

## 8. Ce qui reste, dit franchement

| Manque | Conséquence |
|---|---|
| **Une seule exécution par état** | les scores de Lighthouse varient légèrement d'une exécution à l'autre ; aucune moyenne n'a été faite |
| **Mesure en local, pas en production** | voir §6 |
| **EcoIndex modélisé** | il classe une page sur trois grandeurs ; il ne mesure ni l'énergie réelle du serveur ni celle du modèle de langage (voir `evidence/C7/prix-et-environnement-2026-10-03.md` pour ce qu'on sait de lui) |
| **Pas de lecteur d'écran réel, pas de test avec un utilisateur** | §3.3 |
| **Décision D6 d'Era** | faut-il réduire le nombre de lignes affichées d'emblée sur l'écran indicateurs ? C'est le seul levier qui change la note (D vers C ou B), au prix de l'affichage des 111 valeurs en une page. Recommandation : **ne pas décider avant le gel**, mesurer d'abord F1 à F3 |

*Un document qui ne signale aucune faiblesse n'est pas crédible devant un jury.*

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Lighthouse** | outil libre de Google qui audite une page : performance, accessibilité, bonnes pratiques, référencement |
| **axe-core** | bibliothèque de tests d'accessibilité automatiques, utilisée par Lighthouse |
| **EcoIndex** | note de A à G (et score sur 100) d'une page web, calculée depuis le nombre d'éléments du DOM, le nombre de requêtes et la taille transférée |
| **DOM** | l'arbre des éléments d'une page, tel que le navigateur le construit ; plus il est gros, plus la page est lourde à afficher |
| **Compression gzip** | réduction de la taille des fichiers texte avant l'envoi, défaite par le navigateur |
| **Cache** | copie gardée par le navigateur pour ne pas retélécharger un fichier ; `Cache-Control` en fixe la durée |
| **ETag** | empreinte d'un fichier : le navigateur demande « a-t-il changé ? » et reçoit une réponse très courte si non |
| **TBT, CLS, FCP, LCP** | durée de blocage du navigateur, décalage visuel, premier et plus grand affichage : les métriques de performance de Lighthouse |
| **Mode flux (user flow)** | façon de piloter Lighthouse pas à pas, avec des clics et des saisies, pour mesurer un écran dans un état précis |
| **Piège du focus** | zone dont on ne peut sortir au clavier |
| **Instantané (snapshot)** | audit de la page telle qu'elle est affichée, sans la recharger |
