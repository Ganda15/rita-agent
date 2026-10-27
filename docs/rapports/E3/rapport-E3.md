<style>
.logo{ float:right; width:15mm; margin:7pt 0 2pt 12pt; }
.identite{ color:var(--ink-soft); font-size:9.4pt; }
.sommaire{ margin:9pt 0 2pt; padding:6pt 10pt 5pt; border:.5pt solid var(--rule); border-radius:2pt; }
.sommaire-titre{ font-family:Georgia,"Times New Roman",serif; font-weight:600; font-size:11pt; margin:0 0 4pt; }
.sommaire ol{ list-style:none; padding:0; margin:0; columns:2; column-gap:22pt; }
.sommaire li{ display:flex; justify-content:space-between; gap:8pt; margin:0 0 2pt; break-inside:avoid; font-size:9.4pt; }
.sommaire li a{ color:var(--ink); }
.sommaire li span{ color:var(--accent); font-weight:600; }
</style>

<div><img class="logo" src="logo/rita-logo-marque.png" alt="Logo de RITA"></div>

# Rapport E3 : l'API du modèle, son intégration, son monitorage, ses tests et sa chaîne de livraison

Projet fil rouge **RITA** · **Eramalingam Gandakumar** · Développeur en intelligence artificielle, RNCP 37827 · Simplon × Wild Code School · bloc de compétences 2, compétences C9 à C13 · version 1.9, 27 octobre 2026 ; état décrit : 24 octobre 2026 · code : [`Ganda15/rita-agent`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2), [tag du livrable](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/jury/README.md) (dépôt privé, formateur et jury invités)
{: .identite }

> **En une minute.** RITA aide un investisseur particulier à comprendre les informations disponibles sur une action : il demande un briefing pour une valeur, ou il pose une question sur les articles collectés. Les deux textes sont rédigés par un modèle de langage fourni, que je n'entraîne pas. Ce rapport montre ce qui entoure ce modèle : l'API qui l'expose (C9), l'application qui l'utilise (C10), sa surveillance (C11), ses tests (C12) et sa livraison continue (C13).

<div class="sommaire" role="navigation" aria-label="Sommaire">
<p class="sommaire-titre">Sommaire</p>
<ol>
<li><a href="#usages">Les deux usages, et comment lire ce rapport</a><span>p. 1</span></li>
<li><a href="#s1">1. Le contexte, une seule fois</a><span>p. 1</span></li>
<li><a href="#s2">2. L'architecture autour du modèle</a><span>p. 2</span></li>
<li><a href="#c9">3. C9 : l'API qui expose le modèle</a><span>p. 3</span></li>
<li><a href="#c10">4. C10 : intégrer l'API dans une application</a><span>p. 5</span></li>
<li><a href="#c11">5. C11 : monitorer le modèle</a><span>p. 7</span></li>
<li><a href="#c12">6. C12 : les tests automatisés</a><span>p. 10</span></li>
<li><a href="#c13">7. C13 : la chaîne de livraison continue</a><span>p. 14</span></li>
<li><a href="#s8">8. Ce que les briefs de la formation ont apporté</a><span>p. 16</span></li>
<li><a href="#s9">9. Reproduire : commandes, versions, commits</a><span>p. 16</span></li>
<li><a href="#s10">10. Les 44 critères, regroupés en 39 lignes</a><span>p. 17</span></li>
<li><a href="#s11">11. Ce qui n'est pas fait, et les risques</a><span>p. 19</span></li>
<li><a href="#glossaire">Glossaire</a><span>p. 20</span></li>
</ol>
</div>

## Les deux usages, et comment lire ce rapport {: #usages }

| Usage | Ce que fait l'utilisateur | Ce qu'il voit |
|---|---|---|
| Briefing | il choisit une valeur et demande une synthèse | un texte court, le verdict du garde-fou écrit en mots, la référence de la requête |
| Question | il pose une question sur l'actualité collectée | une réponse avec ses sources citées, ou un refus expliqué |

Chaque compétence part de son cas d'usage, passe ensuite à la technique et finit par « Ce qui manque ». Un chiffre se cite mesuré et daté, avec sa commande ; une preuve est un fichier du dépôt ou une sortie de commande ; ce qui n'existe pas est écrit comme tel. Versions, commits et production : section 9 ; termes techniques : glossaire final.

---

## 1. Le contexte, une seule fois {: #s1 }

**RITA** (*Retrieval Intelligence pour le Tracking et l'Analyse*) est un assistant qui collecte des données boursières et macroéconomiques, les stocke dans une base PostgreSQL conçue selon la méthode Merise, les expose par une API REST, et fait rédiger en français les deux textes présentés plus haut : le **briefing** (ce que la valeur a fait, avec quelles actualités autour) et la **réponse à une question libre**, avec ses sources. L'utilisateur est unique : un investisseur particulier qui suit 111 valeurs ; la démonstration ne porte que sur des positions inventées.

**La contrainte qui structure tout** : RITA est conçue pour informer, sans fournir de recommandation d'achat ou de vente. C'est l'interdit du conseil en investissement non agréé, posé par l'**AMF** (Autorité des marchés financiers). Il est écrit dans les consignes du modèle, et des garde-fous relisent la question, les articles et le texte produit : ils réduisent ce risque, sans garantir son élimination (en sortie, 7 recommandations arrêtées sur 10 cas préparés, section 6.3).

**Le modèle est fourni, pas entraîné.** RITA appelle un modèle de langage déjà entraîné, par une API. Pour le briefing, une **cascade** de fournisseurs : Azure AI Foundry (`gpt-5.4`, déploiement en zone de données UE), puis Anthropic, puis OpenRouter ; c'est l'ordre par défaut du code, et depuis le 11 octobre le poste n'appelle qu'Azure (`LLM_ORDRE=foundry`). Pour la question, Azure seul, avec une réponse au format JSON imposé ([`src/llm.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/src/llm.py), `generer_json`). Il n'y a ni jeu d'entraînement, ni poids, ni réglage fin. Ce que ce rapport mesure n'est donc pas une métrique d'apprentissage, mais le **comportement du système autour du modèle** : ce qu'on lui donne, ce qu'on accepte de lui, ce qu'on refuse, et comment on le voit fonctionner. Une consigne écrite de la chef de projet, le 7 septembre 2026, va dans ce sens ; donnée en réponse à la question d'un camarade, elle ne porte pas sur RITA en particulier (citée dans [`docs/LLMOPS.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/LLMOPS.md)) : des tests sur l'évaluation des réponses et la validation des formats, plus la description des pratiques LLMOps mises en place, suffisent. Absence d'entraînement ne veut pas dire absence d'évaluation : la section 6 mesure chaque garde-fou.

**Ce que le livrable E1 a posé** (version 1 envoyée le 13 août 2026, tag `livrable-E1-v1` ; version 2.6 du 24 octobre, gelée avec ce rapport) : la collecte depuis cinq types de sources, la base de dix tables et une vue, les requêtes, le registre RGPD, l'API de données `/donnees/*`. Ce rapport E3 commence là où E1 s'arrête : le modèle.

---

## 2. L'architecture autour du modèle {: #s2 }

![Deux chemins vers le modèle, et ce qui les surveille](schemas/E3-architecture.png){: style="width:85%" }

*Figure 1. Les deux chemins vers le modèle et ce qui les surveille (état du code au 24 octobre 2026, `develop`, `9683f04`). Source éditable : [`schemas/E3-architecture.drawio`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/rapports/E3/schemas/E3-architecture.drawio). Le même ensemble, brique par brique avec les tests de chacune, est le document d'architecture [`docs/ARCHITECTURE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/ARCHITECTURE.md).*

En texte : un appel passe par l'API (identifiant de requête, clé, valeur connue, quota), puis par l'un des deux parcours. Le briefing suit un graphe à trois nœuds (le scout lit la base, le nœud `rag` cherche les articles, le rédacteur écrit) ; la question passe par ses garde-fous, la recherche, puis le modèle en JSON imposé. Les articles trouvés sont revérifiés avant le prompt, le texte produit est relu, et la réponse part avec son identifiant, une trace sans texte et une ligne de journal.

Cinq contrôles, à trois positions, chacun testé et mesuré (section 6) : sur la **question**, l'intention AMF ([`guardrails/entree.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/guardrails/entree.py)) et le détournement, injection ou extraction ([`guardrails/detournement.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/guardrails/detournement.py)) ; sur les **articles collectés**, l'injection ([`guardrails/injection.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/guardrails/injection.py)), appliquée à la collecte puis de nouveau avant chaque prompt ; sur le **texte produit**, la recommandation et la fuite ([`guardrails/sortie.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/guardrails/sortie.py)), et pour une réponse, les nombres ([`guardrails/nombres.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/guardrails/nombres.py)). Le graphe est linéaire : l'ordre des étapes est connu, donc aucun choix de routage n'est confié au modèle. C'est la leçon du brief Kaldera : quand l'ordre est connu, un superviseur déterministe vaut mieux qu'un modèle qui choisit.

---

## 3. C9 : l'API qui expose le modèle {: #c9 }

**Le cas d'usage** : l'utilisateur demande le briefing de MC.PA ; sans clé, ou pour une valeur inconnue, la demande s'arrête avant le modèle. Comment l'API expose-t-elle ce modèle, et à qui ?

### 3.1 Les points de terminaison

L'API publie son contrat OpenAPI 3.1.0 sur `/openapi.json`, avec la documentation interactive sur `/docs`. **Dix-neuf chemins** le 24 octobre 2026 (`app.openapi()`), dont douze sous `/donnees` :

| Route | Rôle | Clé |
|---|---|---|
| `GET /health` | le service répond ; il annonce le commit, la date de construction et l'index servis | aucune |
| `POST /briefing?ticker=` | **le modèle** : un briefing rédigé pour une valeur | `X-API-Key` |
| `POST /question` | **le modèle** : une réponse tirée des articles, avec ses sources, ou un refus | `X-API-Key` |
| `GET /donnees/valeurs`, `/cotations`, `/macro`, `/portefeuille`, `/mouvements`, `/volumes-anormaux`, `/articles`, `/articles/{article_id}`, `/indicateurs`, `/indicateurs-portefeuille`, `/indicateurs-risque`, `/fraicheur` | le jeu de données (E1, C5) | `X-API-Key` |
| `GET /sante` | les signaux de la vigie et leurs verdicts | `X-API-Key` |
| `POST /exercice/panne`, `/exercice/fin` | poser ou retirer une panne simulée ; coupées en production | `X-Cle-Exercice` |
| `POST /audit/mcp` | la passerelle MCP y dépose ses refus locaux | `X-API-Key` |

La distinction entre C5 et C9 est celle du référentiel : `/donnees/*` sert de la donnée, `/briefing` et `/question` servent une rédaction produite par un modèle.

### 3.2 L'authentification

Deux clés, chacune dans son en-tête, jamais l'une pour l'autre. Les pages de l'interface et `/health` sont publiques, sans donnée métier. Quatre décisions, chacune née d'un incident ou d'une revue :

- **Aucune clé par défaut.** Le code acceptait `dev-key` écrite en clair quand la variable manquait ; corrigé le 18 août 2026 (INC-001, OWASP API2). Une clé absente ou trop courte (16 caractères minimum) est détectée à l'authentification (`cle_attendue()`), avec un message qui dit comment en générer une.
- **Comparaison à temps constant** (`secrets.compare_digest`) : une comparaison ordinaire s'arrête au premier caractère différent et laisse mesurer la clé par le temps de réponse.
- **Une dépendance par routeur** (données, question, santé) : une route ajoutée à l'un de ces routeurs hérite de la clé. `/briefing` et `/audit/mcp`, posées directement sur l'application, déclarent la leur, chacune avec son test de refus sans clé ([`tests/test_health.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_health.py), [`tests/test_audit_mcp.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_audit_mcp.py)). Une route posée hors de ces routeurs doit déclarer sa protection ; seul `/donnees` a un test qui parcourt toutes ses routes ([`tests/test_api_donnees.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_api_donnees.py)).
- **Un refus laisse une ligne de journal** (identifiant de requête, route, motif), jamais la clé ni sa longueur ([`tests/test_refus_cle_journal.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_refus_cle_journal.py), 5 tests). La clé d'exercice (`X-Cle-Exercice`, variable `RITA_CLE_EXERCICE`) ne sert qu'aux exercices ; sans elle, ces routes répondent 503.

Jusqu'au 24 octobre, le contrat publié se trompait sur ce dernier point : les deux clés portaient le même nom de schéma par défaut, et `/docs` annonçait `X-API-Key` sur `/exercice/*`. Corrigé, avec un test qui lit le contrat ([`tests/test_exercice.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_exercice.py)).

### 3.3 Les recommandations OWASP appliquées

Le top 10 OWASP des API (2023) et celui des applications de modèles de langage (2025) ont servi de grilles. Ce qui est appliqué, et ce qui ne l'est pas :

| Risque OWASP | Dans RITA | État |
|---|---|---|
| API2, authentification défaillante | clé obligatoire, longueur minimale, temps constant, aucune valeur par défaut, refus journalisés | appliqué |
| API4, consommation de ressources non limitée | 10 appels par minute (`RITA_QUOTA_PAR_MINUTE`), partagés par les deux routes du modèle, 429 et `Retry-After` au-delà ([`api/limiteur.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/api/limiteur.py), depuis le 20 octobre) ; compteur en mémoire d'un seul processus, remis à zéro au redémarrage ; pas un plafond de dépense | **partiel** |
| API8, mauvaise configuration | conteneur non-root (UID 10001), système de fichiers en lecture seule, `no-new-privileges`, aucun port de base publié ; **mais aucun en-tête de sécurité en production**, et `Server` et `Via` annoncés (mesuré le 24 octobre, 14 h 54 UTC) | **partiel** |
| A05:2025 (OWASP web), injection | l'interface n'utilise jamais `innerHTML` ; tout texte passe par `textContent` | appliqué |
| LLM01:2025, injection de prompt | garde-fous de la question et des articles, mesurés ; scan Giskard du 20 septembre | appliqué, limites mesurées (section 6) |
| LLM02 et LLM07:2025, divulgation, fuite des consignes | contrôle de fuite après le modèle, sur les deux parcours | appliqué, 71,4 % mesuré (section 6) |

La revue entrée par entrée, sur l'édition **OWASP Top 10:2025**, date du 3 octobre : [`evidence/C17/revue-owasp-top10-2025-2026-10-03.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C17/revue-owasp-top10-2025-2026-10-03.md). Ses corrections suivent la carte #75 : la longueur du ticker est bornée, les refus de clé sont journalisés, la limite de débit existe ; restent les en-têtes de sécurité et le message d'une panne totale des fournisseurs. Le certificat de production, dont la carte #75 notait l'échéance du 18 novembre, avant le jury, a été renouvelé seul le 19 octobre (valable jusqu'au 17 janvier 2027, lu le 24 octobre).

### 3.4 Versionnage et tests

Les sources sont sur GitHub, `Ganda15/rita-agent` : `develop` pour le travail, `main` pour les versions, qui ne bouge que par une pull request relue (section 7). Les tests de l'API, collectés le 24 octobre : [`tests/test_health.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_health.py) (12 : vivacité, 403, substitution AMF prouvée par mutation), [`tests/test_briefing_422.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_briefing_422.py) (5), [`tests/test_limiteur.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_limiteur.py) (7), [`tests/test_request_id.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_request_id.py) (12 : l'identifiant sur toute réponse, 500 compris), [`tests/test_traces_robustesse.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_traces_robustesse.py) (8 : une panne du traçage ne fait jamais tomber un briefing), [`tests/test_api_donnees.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_api_donnees.py) (63), [`tests/test_api_question.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_api_question.py) (19), [`tests/test_exercice.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_exercice.py) (23). La documentation tient en trois fichiers, mis à jour le 24 octobre : [`docs/ARCHITECTURE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/ARCHITECTURE.md) (chaque brique et ses tests, les 19 chemins, les deux clés, les règles d'accès), [`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/exploitation.md) (installer, déployer, diagnostiquer, revenir en arrière), [`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/CI-CD.md) (la chaîne). Le détail de chaque route est le contrat OpenAPI. Un appel réel du 3 octobre est rangé dans [`evidence/C9/preuve-api-modele-2026-10-03.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C9/preuve-api-modele-2026-10-03.md).

### 3.5 Ce qui manque, C9

- Le contrat n'est pas versionné dans l'adresse (`/v1`), et sa version déclarée (`1.1.0`, du 1er août) n'a pas suivi l'ajout de `/question`, `/sante` et `/exercice`.
- Un briefing dont le graphe échoue répond 502 ; une panne de tous les fournisseurs, 500 générique, sans fuite (carte #75).
- Le format des erreurs n'est pas celui de la RFC 9457 (format JSON normalisé des erreurs).
- Aucun en-tête de sécurité en production ; la limite de débit n'est ni par adresse ni par clé.
- Le dépôt est privé : le jury doit y être invité avant l'envoi.

---

## 4. C10 : intégrer l'API dans une application {: #c10 }

**Le cas d'usage** : l'utilisateur choisit une valeur ou pose une question ; il voit le texte, le verdict du garde-fou en mots et la référence de sa requête, ou un message d'erreur. Comment l'écran appelle-t-il l'API ?

### 4.1 Les clients, un seul chemin

L'API a deux clients dans le dépôt, et tous deux passent par HTTP avec la clé, jamais par les modules Python en direct.

**L'interface web** ([`frontend/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/frontend), HTML, CSS et JavaScript sans outil de construction) : cinq écrans, le portefeuille valorisé, les indicateurs de marché, le briefing, les questions et le tableau de bord de la vigie. Ils appellent onze chemins : sept routes de données (`/donnees/valeurs`, `/portefeuille`, `/indicateurs`, `/indicateurs-portefeuille`, `/indicateurs-risque`, `/fraicheur`, `/articles/{article_id}`), `/briefing`, `/question`, `/health` et `/sante` ; les autres routes de données servent la passerelle ou un appel direct. La clé est saisie par l'utilisateur, gardée en `sessionStorage` (mémoire de l'onglet, effacée à sa fermeture), jamais écrite dans le code. La figure 2 suit le parcours du briefing : valeur choisie dans l'univers suivi, `POST /briefing` avec la clé, texte rendu par `textContent`, **verdict du garde-fou écrit en mots**, identifiant de requête affiché pour le support, et un message propre à chaque refus. Preuve de l'écran avec un briefing réel : [`evidence/C10/preuve-ecran-briefing.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C10/preuve-ecran-briefing.md). La preuve principale de C10 est cette interface, qui intègre `/briefing` et `/question` ; la passerelle MCP ci-dessous est un client complémentaire des données.

![Une demande de briefing, de l'écran au modèle et retour](schemas/E3-integration-briefing.png){: style="width:85%" }

*Figure 2. Une demande de briefing depuis l'écran, en cinq temps, et ce que l'écran fait de chaque réponse qui n'est pas un briefing (aucune réponse, 403, 422, 429, 502 et 500). En pointillé, les écarts connus : le message générique d'une panne totale (#75) et la clé gardée trop tôt (#73). Source éditable : [`schemas/E3-integration-briefing.drawio`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/rapports/E3/schemas/E3-integration-briefing.drawio).*

**La passerelle MCP** ([`passerelle_mcp/serveur.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/passerelle_mcp/serveur.py)) : MCP (*Model Context Protocol*) est le protocole qui décrit des outils à un modèle de langage. La passerelle expose trois outils en lecture seule (`rita_fraicheur`, `rita_portefeuille`, `rita_indicateurs`), avec l'annotation `read_only_hint`, et appelle l'API REST par HTTP avec `X-API-Key`. Passer par HTTP plutôt que par les modules fait de la passerelle un vrai client, soumis au refus 403, et évite deux chemins d'accès aux données qui divergeraient. Le formateur a rendu le MCP obligatoire le 28 août 2026. Preuve : [`evidence/C10/preuve-passerelle-mcp.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C10/preuve-passerelle-mcp.md). `rita_portefeuille` exige le mode démonstration et compare les couples (ticker, quantité) servis à ceux du jeu d'exemple ; sinon il refuse (`NOT_AUTHORIZED`) sans exposer les données. **Défaut connu (#152, ouvert)** : l'import écarte les valeurs hors de l'univers suivi, si bien que 7 positions arrivent en base contre 10 lignes gardées dans le fichier d'exemple ; le verrou refuse donc aussi le jeu de démonstration importé. Il échoue fermé : aucune donnée ne sort, mais l'outil ne rend pas ce portefeuille. Les tests passaient parce qu'ils simulent la réponse de l'API. Chaque appel d'outil déclaré est journalisé dans la table `mcp_calls` (statut, code d'erreur, durée, jamais le contenu) ; si la base ne répond pas, l'appel n'est pas bloqué et l'échec d'écriture est compté ([`db/audit_mcp.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/db/audit_mcp.py)). Les refus pris dans la passerelle sont déposés par `POST /audit/mcp`.

### 4.2 Les tests d'intégration

| Fichier | Tests | Ce qu'il prouve |
|---|---|---|
| [`tests/test_frontend.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_frontend.py) | 92 | aucune clé dans le code servi, gestion du 403, verdict en mots, paragraphes sans HTML, attributs d'accessibilité, écrans reliés |
| [`tests/test_smoke_ui.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_smoke_ui.py) | 13 | un vrai navigateur (Playwright) : zéro erreur JavaScript, mauvaise clé refusée, valeur inconnue (422) et quota atteint (429) dits à l'écran, briefing affiché avec son verdict et sa référence (API interceptée : aucun appel payant) |
| [`tests/test_tableau_de_bord.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_tableau_de_bord.py), [`tests/test_smoke_tableau_de_bord.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_smoke_tableau_de_bord.py) | 18 + 14 | le tableau de bord : marqueurs RGAA, état écrit en mots, écran de 375 px sans défilement horizontal, vrai navigateur |
| [`tests/test_passerelle_mcp.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_passerelle_mcp.py) | 19 | les trois outils, leurs erreurs typées, l'appel HTTP avec clé, le verrou de démonstration, le dépôt des refus |
| [`tests/test_audit_mcp.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_audit_mcp.py), [`tests/test_audit_mcp_base.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_audit_mcp_base.py) | 22 + 4 | le journal des appels ; sur la base réelle en transaction annulée, le rôle lecture seule lit sans pouvoir écrire |

Deux hooks de l'assistant de développement ([`.claude/hooks/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/.claude/hooks)) gardent le développement lui-même : l'un refuse toute commande qui nomme le fichier de secrets, l'autre refuse de conclure sans une sortie de tests ; neuf tests les couvrent, sautés hors Windows (donc en CI).

### 4.3 Ce qui manque, C10

- **La clé est gardée avant d'avoir servi (#73), non corrigé** : les écrans du briefing et des questions la mémorisent dès l'envoi du formulaire ; le tableau de bord la garde après une panne réseau ou une erreur 500. Le portefeuille et les indicateurs attendent un appel réussi. Aucun contournement de l'authentification du serveur : c'est un écart au parcours spécifié.
- **Le verrou de `rita_portefeuille` refuse aussi le jeu de démonstration importé (#152), non corrigé** : un défaut de disponibilité, pas un accès indu aux données ; à corriger avec un test sur les positions réellement importées.
- Les trois premiers écrans ont leurs spécifications et maquettes ([`evidence/C14/preuve-specifications-ecrans-2-et-3.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C14/preuve-specifications-ecrans-2-et-3.md)) ; l'écran des questions suit les critères de [`docs/sprint-3/SPEC.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/sprint-3/SPEC.md) ; le tableau de bord n'a pas de spécification écrite dans le dépôt.
- La passerelle MCP n'offre pas d'outil de briefing, par choix (un outil qui déclenche un appel payant demande une politique de coût d'abord) ; le quatrième outil du chapitre « Données », `search_articles`, n'existe pas.

---

## 5. C11 : monitorer le modèle {: #c11 }

**Le cas d'usage** : sans que l'utilisateur le voie, chacune de ses demandes laisse une trace sans texte (étapes, durées, fournisseur, jetons) ; un seuil franchi déclenche une alerte. Comment voit-on que le modèle fonctionne ?

### 5.1 L'outil, et pourquoi lui

Le monitorage d'un modèle fourni par API consiste à voir chaque appel : combien de temps, combien de jetons, quel fournisseur a répondu, et si un garde-fou a dû intervenir. L'outil retenu est **Langfuse Cloud, région Union européenne**, palier gratuit : 50 000 unités par mois, 30 jours de conservation, deux alertes. Décision du 28 septembre 2026, prise sur une règle donnée par le formateur, « la condition, c'est la sensibilité des données », et sur une mesure dans le code : le prompt du briefing ne contient ni position, ni quantité, ni prix de revient (ticker, cours, variation, volume, passages de presse). Le ticker demandé peut toutefois révéler un intérêt de l'utilisateur, et une question libre peut contenir une donnée personnelle (registre RGPD, T8). Depuis le 20 octobre, ni prompt ni réponse ne sont gardés dans les traces. Trois options comparées dans le registre RGPD (§T3) :

| Option | Sous-traitant | Transfert hors UE | Retenue ? |
|---|---|---|---|
| LangSmith | éditeur sans entité juridique en UE, auto-hébergement réservé au plan Enterprise | oui | non |
| Langfuse auto-hébergé | aucun | non | non : six composants (web, worker, PostgreSQL, ClickHouse, Redis, S3) sur un serveur de 4 Go déjà occupé |
| **Langfuse Cloud, région UE** | Langfuse GmbH (Allemagne), groupe ClickHouse | hébergement UE ; le contrat permet un traitement hors de la région choisie si le service l'exige, avec des clauses types ; **vérification propre à RITA incomplète** (registre RGPD, T3) | **oui** |

Deux contraintes techniques ont pesé : le SDK Langfuse exporte en OpenTelemetry sur HTTP sans gRPC, or gRPC est refusé par la sécurité du poste de développement (Smart App Control) ; et un auto-hébergement était impossible sur le serveur.

### 5.2 Ce qu'une trace montre

Chaque appel à `/briefing` produit une trace à racine `briefing`, puis une étape par nœud et par garde-fou ; chaque appel à `/question`, une racine `question` (statut, motif, longueur, identifiants des sources citées) et la génération du modèle :

```
briefing                         racine : request_id, verdict AMF, note conforme_amf (1 ou 0)
├── scout                        ticker, fraîcheur en jours, cotation périmée, erreur éventuelle
├── rag            (retriever)   motif (OK, OUT_OF_CORPUS), nombre de passages, noms des sources
│   ├── garde-fou-detournement   bloqué ou non, motifs ; niveau WARNING si bloqué
│   └── garde-fou-entree         bloqué ou non, motifs
├── redacteur                    longueur du texte
│   └── briefing-llm             la cascade
│       └── llm-<fournisseur>    une génération par fournisseur essayé : modèle, jetons, erreur
└── garde-fou-sortie             bloqué ou non, motifs ; niveau WARNING si bloqué
```

Une règle tenue partout : la sortie d'une étape est un résumé (compte, motif, durée), jamais le contenu. **Depuis le 20 octobre, aucune étape ne garde de texte**, ni le prompt ni la réponse, sur la racine comme sur les générations ([`src/traces.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/src/traces.py), [`tests/test_traces_briefing_sans_texte.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_traces_briefing_sans_texte.py)).

**Deux traces réelles relues.** La première trace complète d'un briefing, le 3 octobre à 14 h 48, sur le poste : racine de 12,33 s, dont 5,07 s de recherche documentaire, 5,64 s pour le fournisseur qui a répondu (OpenRouter, 616 jetons en entrée et 210 en sortie) et deux générations en erreur avant lui (clés absentes du poste) ; dix observations dans l'ordre attendu par [`tests/test_trace_chemin.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_trace_chemin.py), et le même `request_id` dans l'en-tête de la réponse, la ligne de journal et la trace ([`evidence/C11/preuve-langfuse-2026-10-03.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C11/preuve-langfuse-2026-10-03.md)). La première trace de **production**, le 21 octobre à 12 h 51, ouverte dans Langfuse :

| Observation | Entrée et sortie | Ce qui est gardé |
|---|---|---|
| racine `briefing`, 6,88 s | aucune | verdict `conforme_amf: True`, coût et jetons agrégés |
| génération `llm-foundry`, 4,69 s | aucune | modèle `gpt-5.4-2026-03-05`, environ 1 000 jetons, 0,006 $ |
| étape `rag` | motif `OK`, 3 passages, noms des sources | aucun texte d'article |

Preuves : [`evidence/sprint-4/README.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/sprint-4/README.md) et deux captures dans [`evidence/sprint-4/captures/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/evidence/sprint-4/captures). Limite : une seule trace de production relue.

![Surveiller le modèle : collecte, alerte et restitution](schemas/E3-monitorage.png){: style="width:85%" }

*Figure 3. La chaîne de monitorage au 24 octobre 2026 : ce qui est collecté à chaque requête, ce que Langfuse en fait, les deux restitutions, comment une alerte devient une issue GitHub, et ce qui manque. Source éditable : [`schemas/E3-monitorage.drawio`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/rapports/E3/schemas/E3-monitorage.drawio).*

### 5.3 Les métriques, et ce qu'elles veulent dire

| Métrique | Où elle se lit | Ce qu'elle dit, et ce qu'elle ne dit pas |
|---|---|---|
| **Latence par étape**, et p95 de l'appel au modèle | durée de chaque étape ; p95 = la valeur sous laquelle tombent 95 % des appels | où passe le temps ; le p95 se lit sur `briefing-llm`, pas sur la racine, pour comparer des grandeurs de même nature |
| **Jetons et coût** par génération | jetons de chaque génération, coût déduit par Langfuse ; coût estimé en euros par `/sante` ([`monitorage/prix.json`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/monitorage/prix.json)) | le budget, pas la qualité |
| **Erreurs de repli** | niveau ERROR sur la génération du fournisseur en panne | une dégradation (un fournisseur tombe, la cascade compense), pas une panne : la panne est la racine en erreur, le briefing non servi |
| **Verdict AMF** | métadonnée et note `conforme_amf` sur la racine ; niveau WARNING si refus | combien de textes ont dû être retenus ; un taux élevé dirait « le modèle produit souvent des formules interdites », et c'est le prompt qu'il faudrait regarder |
| **Fraîcheur des données** | `GET /donnees/fraicheur`, bandeau de l'écran 1, signal de `/sante` | un service qui répond mais sert des cours vieux de trois mois est en panne silencieuse |

**Le coût, d'une trace à l'autre.** Le 3 octobre, le coût de la génération OpenRouter valait zéro dans Langfuse : le nom de modèle reçu, `anthropic/claude-sonnet-4.5`, n'était pas dans sa grille de prix. La métrique était fausse, pas absente. Le 21 octobre, la génération Azure de production affiche 0,006 $ pour environ 1 000 jetons : Langfuse connaît ce modèle. Pour `/question`, les jetons partent en métadonnées (`jetons_entree`, `jetons_sortie`) et non dans le champ d'usage de la génération : Langfuse n'en déduit pas de coût. Les coûts des deux parcours restent donc à distinguer ; le coût de `/sante` est une estimation à partir d'une grille écrite, remise à zéro au redémarrage.

**Les erreurs de repli.** Sur la trace du 3 octobre, deux générations sur trois portent le niveau ERROR : deux clés absentes du poste. Un taux d'erreur calculé sur toutes les générations serait trompeur (67 %, alors que le briefing a été servi) ; c'est pourquoi la première alerte s'appelle « fournisseur en erreur » et non « panne ».

Un **identifiant de requête** (`request_id`) relie tout : il est dans l'en-tête `X-Request-ID` de chaque réponse, erreurs comprises, dans chaque ligne de journal, et il sert de graine à l'identifiant de trace. Un identifiant fourni par le client n'est repris que s'il est sain (8 à 64 caractères, lettres, chiffres, tiret, souligné).

### 5.4 Le bac à sable avant la production

La chaîne a été testée hors production avant d'être branchée, et deux incidents l'ont imposé. Le 2 octobre, quinze générations « prompt test » sont apparues dans le projet de production : les tests chargeaient les vraies clés. Corrigé le jour même, test d'abord, par une règle de [`tests/conftest.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/conftest.py) qui coupe le traçage pour toute la suite ; les tests utilisent depuis des doubles de client Langfuse, sans réseau ([`evidence/C21/INC-006-tests-ecrivaient-en-production.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C21/INC-006-tests-ecrivaient-en-production.md)). Le 23 octobre, une panne simulée sur la copie du poste a fait sonner l'alerte de production (issue #130) : la copie écrivait dans le même projet Langfuse. Elle a depuis son propre projet, sans alerte.

### 5.5 Alerter

Le palier gratuit offre deux alertes. Le canal retenu est GitHub Actions, parce que le dépôt est déjà l'endroit où vivent les incidents : [`.github/workflows/alerte-incident.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/.github/workflows/alerte-incident.yml) ouvre une issue avec le label `incident` (titre stable par alerte, charge utile jointe, étapes de post-mortem à cocher), ou commente l'issue déjà ouverte. Exécuté à la main le 3 octobre (issue #71).

| Alerte | Règle | Ce qui s'est passé |
|---|---|---|
| « RITA : fournisseur en erreur » | au moins une observation ERROR sur un jour | 4 octobre (#77) : **vraie alerte**, quatre erreurs réelles de fournisseurs sans clé, la cascade a servi. 23 octobre (#130) : **fausse alerte**, venue de la copie du poste, cause établie en 77 minutes par l'API de Langfuse |
| « RITA : appel au modèle trop lent » | p95 de `briefing-llm` au-dessus de 15 000 ms sur un jour | 4 octobre : a sonné **à tort**, seuil saisi à 15 en pensant à des secondes ; corrigé à 15 000 le jour même |

Ces alertes ont aussi révélé un défaut du workflow (deux alertes sous un même nom générique), corrigé test d'abord : une issue par alerte, nommée d'après la charge utile ([`tests/test_alerte_incident.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_alerte_incident.py), 10 tests). Preuves : [`evidence/C11/preuve-alertes-2026-10-04.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C11/preuve-alertes-2026-10-04.md).

### 5.6 Restitution et documentation

Deux restitutions en temps réel. Le tableau de bord Langfuse « RITA C11 », construit le 3 octobre par l'API ([`evidence/C11/dashboard-rita-c11-2026-10-03.json`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C11/dashboard-rita-c11-2026-10-03.json)) : tentatives d'appel par fournisseur, échecs compris, p95 de l'appel au modèle, observations en erreur ou en avertissement. Et, depuis le 23 octobre en production, le tableau de bord de RITA ([`frontend/tableau-de-bord.html`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/frontend/tableau-de-bord.html)) qui lit `/sante` : le verdict de chaque signal contre un seuil écrit ([`monitorage/seuils.json`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/monitorage/seuils.json)), en mots et pas seulement en couleur, testé dans un vrai navigateur. Utilisation et réglage des alertes : [`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/exploitation.md). Accessibilité : l'interface Langfuse est faite de texte et de tableaux, navigable au clavier, chaque tuile s'exporte en CSV ; le tableau de bord de RITA porte des marqueurs RGAA testés et un état lisible sans la couleur. Le critère reste partiel : l'accessibilité de Langfuse a été examinée après son choix, sans déclaration de l'éditeur ni test au lecteur d'écran.

### 5.7 Ce qui manque, C11

- **La capture du tableau Langfuse** n'est pas rangée dans [`evidence/C11/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/evidence/C11) : sa définition y est en JSON. Les captures du tableau de RITA ([`evidence/sprint-5/captures/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/evidence/sprint-5/captures)) portent sur des données fabriquées.
- Le coût de `/question` n'est pas calculé par Langfuse, et une seule trace de production a été relue.
- Pas d'alerte de silence (aucune trace depuis 24 heures) : les deux alertes du palier gratuit sont prises.
- Les compteurs de `/sante` vivent en mémoire et repartent à zéro à chaque redémarrage ; les journaux sont du texte, pas du JSON.

---

## 6. C12 : les tests automatisés {: #c12 }

**Le cas d'usage** : une version ne sert des briefings qu'après des tests, dont ceux-ci : une recommandation d'achat est retenue, une demande sans clé est refusée. Qu'est-ce qui est testé, et qu'est-ce qui ne l'est pas ?

### 6.1 La stratégie

Le modèle n'est pas entraîné : il n'y a ni test de préparation de données d'entraînement ni évaluation d'un apprentissage. Ce qui est testé, par niveau :

| Niveau | Ce qu'il vérifie | Exemples de fichiers |
|---|---|---|
| **Unitaire** | une fonction, sans réseau ni base | `test_entree`, `test_garde_fou_question`, `test_controle_nombres`, `test_indicateurs_*`, `test_limiteur` |
| **Intégration** | l'API par un client de test, le graphe, la base réelle en transaction annulée | `test_health`, `test_api_question`, `test_workflow`, `test_role_lecture`, `test_audit_mcp_base` |
| **Contrat** | un fichier (déploiement, documentation, contrat OpenAPI) lu comme du code | `test_docker_compose`, `test_workflows_livraison`, `test_exploitation_doc`, `test_alerte_incident` |
| **Trace** | qui a tourné, dans quel ordre, combien de fois, sans texte | `test_trace_chemin`, `test_traces_briefing_sans_texte`, `test_request_id` |
| **Portes d'évaluation** | les mesures des garde-fous deviennent des conditions de fusion | `test_evals` |
| **Fumée** | un vrai navigateur, une vraie image Docker | `test_smoke_ui`, `test_smoke_tableau_de_bord`, `livraison.yml` |

**Mesure de la CI du 24 octobre 2026**, branche `develop`, commit `9683f04`, passage `40101793487`, commande `pytest -v --cov --cov-report=term-missing` :

```
TOTAL                              3506    129    96%
Required test coverage of 90.0% reached. Total coverage: 96.32%
===== 1719 passed, 30 skipped, 2 xfailed, 17 warnings in 83.63s (0:01:23) ======
```

1 751 tests collectés dans 100 fichiers (`pytest --collect-only -q`, même commit). Le même jour, `main` (`b547cbf`, celui de la production) donnait 1 700 réussis, 30 sautés, 2 `xfailed`, 96,32 % (passage `40083432858`) ; les 19 tests de plus de `develop` sont ceux du vérificateur de liens, du contrat OpenAPI et d'un schéma d'E1. Les 30 sautés, relus dans le journal : 16 exigent la base réelle, 9 les hooks Windows de l'assistant, 5 un JDK, conditions absentes de la CI. Le passage local du même jour (1 709 réussis, 40 sautés) ne prouve pas qu'ils y ont tous tourné : ses 40 sautés ne sont pas détaillés. Historique : 440 tests le 7 septembre (92,23 %), 742 le 3 octobre, 1 719 réussis en CI le 24 octobre. Sortie rangée le jour même : [`evidence/C12/preuve-ci-develop-2026-10-24.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C12/preuve-ci-develop-2026-10-24.md). **Au commit du tag** `livrable-E3-v1` (`312056a`), la CI a collecté 1 792 tests : 1 760 réussis, 30 sautés, 2 `xfailed`, couverture 96,32 % (passage `40112605735`) ; la différence avec `9683f04` vient du seul fichier de tests ajouté entre les deux, [`tests/test_schemas_e3.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_schemas_e3.py).

![Ce qui est testé, par quoi, et où](schemas/E3-strategie-tests.png){: style="width:85%" }

*Figure 4. Les 1 751 tests regroupés par ce qu'ils protègent (en bleu, le comportement du modèle ; en blanc, l'application autour), chaque fichier dans un seul groupe, puis les endroits où ils tournent. Source éditable : [`schemas/E3-strategie-tests.drawio`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/rapports/E3/schemas/E3-strategie-tests.drawio).*

Trois extraits réels, lus dans le dépôt le 24 octobre 2026, et ce qu'il faut y voir.

#### 6.1.1 Intégration : l'API par un client de test, le modèle simulé

```python
# tests/test_health.py
def test_briefing_interdit_est_remplace_par_le_message_de_refus():
    from guardrails.sortie import MESSAGE_REFUS

    resultat_simule = {"ticker": "MC.PA", "price": 457.5, "change_pct": -1.99,
                        "currency": "EUR", "error": "",
                        "briefing": "Nous recommandons l'achat de cette valeur."}
    with patch("api.main.generer_briefing_complet", return_value=resultat_simule):
        response = client.post("/briefing?ticker=MC.PA", headers={"X-API-Key": CLE_DE_TEST})

    assert response.status_code == 200          # un refus n'est pas une panne
```

`patch` remplace, le temps du test, la fonction qui appelle le modèle par une réponse fixe : on lui fait produire une recommandation d'achat, et on vérifie que l'API ne la diffuse pas. Le `client` est le `TestClient` de FastAPI, qui parle à l'application sans serveur ni port. Le code 200 est une décision de conception fixée par le test : un refus du garde-fou est le garde-fou qui fait son travail, pas une erreur du serveur. Les assertions suivantes vérifient `conforme_amf is False` et que le mot interdit ne fuit nulle part.

#### 6.1.2 Trace : qui a tourné, dans quel ordre, combien de fois

```python
# tests/test_trace_chemin.py
# Sprint 4 (tâche A3) : toute recherche passe d'abord par le garde-fou de détournement, celle du briefing comprise.
ORDRE_ATTENDU = ["briefing", "scout", "rag", "garde-fou-detournement", "garde-fou-entree", "redacteur",
                 "briefing-llm", "llm-anthropic", "garde-fou-sortie"]
```

Le texte d'un modèle change à chaque appel ; la trace, elle, ne change pas. Ce test remplace le client Langfuse par un double qui note chaque étape ouverte, et compare la liste à l'ordre attendu, chaque nom une fois. Il attrape un nœud dupliqué, oublié ou déplacé, ce qu'aucun test sur le texte ne peut faire. Quand le garde-fou de détournement a été ajouté au sprint 4, c'est ce test qui a dû changer, et le commentaire dit pourquoi. C'est la leçon du brief Kaldera : tester la trace, pas le texte.

#### 6.1.3 Portes d'évaluation : la mesure devient une condition de fusion

```python
# tests/test_evals.py
SEUIL_BLOCAGE = 85.0
SEUIL_FAUX_POSITIFS = 15.0

@pytest.mark.xfail(
    reason=(
        "Limitation connue depuis la veille S34 (17/08/2026) : le taux de blocage reel est "
        "de 70 %, sous le seuil de 85 %. [...] LE SEUIL RESTE A 85 % : on ne baisse pas "
        "l'exigence, on declare qu'on ne l'atteint pas encore. [...]"
    ),
    strict=True,
)
def test_seuils_minimaux_du_gardefou():
```

Le marqueur `xfail` dit « cet échec est attendu, et voici pourquoi » : pytest affiche `xfailed` avec la raison, jamais `passed`. `strict=True` est le point qui compte : si le taux repassait au-dessus de 85 %, pytest signalerait `XPASS` et la suite échouerait, ce qui oblige à retirer le marqueur le jour où la limite est levée. Les portes des faux positifs et de la latence, elles, bloquent la fusion : en CI le 24 octobre, 16 tests verts et les 2 `xfail` attendus. Une CI verte ne dit donc pas que tous les objectifs de qualité sont atteints : deux ne le sont pas, ils sont déclarés, et ils n'empêchent pas la livraison.

### 6.2 La couverture : un seuil établi, pas décrété

Le seuil vit dans un seul fichier, [`.coveragerc`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/.coveragerc) (`fail_under = 90`), lu en local comme en CI ; la commande de la CI porte bien `--cov`, sans quoi le seuil ne serait jamais appliqué (leçon de l'exercice Factum du 2 octobre). Son historique est écrit dans le fichier : 80 % le 19 août à la première mesure, relevé à 90 % le même jour une fois deux manques fermés. **Le seuil suit la mesure, jamais l'inverse.** Les fichiers de tests et [`bigdata/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/bigdata) (absent de l'image livrée) sont exclus, avec le pourquoi dans le fichier. **Limite trouvée le 24 octobre** : [`rag/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/rag), [`monitorage/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/monitorage) et [`passerelle_mcp/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/passerelle_mcp) ne sont pas dans la liste `source` du fichier, et les 96,32 % ne les comptent pas. Mesurés à part sur le poste le même jour, sans toucher au fichier : 98 % (1 060 instructions, 20 non couvertes ; la passerelle seule, 88 %).

### 6.3 Les garde-fous, mesurés, et le choix de ne pas baisser le seuil

Chaque garde-fou se mesure par deux chiffres, toujours ensemble : un garde-fou qui bloque tout affiche 100 % et rend le produit inutilisable. **Mesures du 24 octobre 2026** sur `9683f04` (harnais lancés à la main, sans modèle ni réseau ; le contrôle des nombres, lui, a été relu sur une exécution réelle) :

| Contrôle | Commande | Blocage | Faux positifs | Limite à garder |
|---|---|---|---|---|
| Intention AMF (question) | `python -m evals.mesurer_entree` | 100 % (5 cas) | 0 % (5) | 5 cas seulement |
| Détournement (question) | `python -m evals.mesurer_entree` | 100 % (6 attaques) | 0 % (17) | **0 des 8 reformulations réservées** reconnue par ce garde-fou seul |
| Injection (articles) | `python -m evals.mesurer_gardefou` | 70 % (10) | 0 % (8) | 3 injections non détectées : deux fausses consignes de la rédaction, un changement de rôle |
| Recommandation (sortie) | `python -m evals.mesurer_sortie` | 70 % (10) | 0 % (6) | 3 formules allusives (« le point d'entrée paraît attractif ») |
| Fuite (sortie) | `python -m evals.mesurer_sortie` | 71,4 % (7) | 0 % (11) | 2 contournements non détectés |
| Nombres (réponse) | relecture du 21 octobre, niveau 2 | 8 réponses, chaque nombre dans un article cité | sans objet | contrôle de présence, pas du sens, de l'unité ni de l'attribution |

La limite est structurelle : des motifs lexicaux ne reconnaissent pas une intention. [`tests/test_evals.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_evals.py) transforme ces mesures en conditions de fusion : blocage attendu à 85 %, faux positifs au plus 15 %, latence sous 250 ms. Le blocage à 85 % n'est pas atteint sur deux garde-fous : **ces tests sont marqués `xfail` strict plutôt que de baisser le seuil** (6.1.3). Faux positifs et latence bloquent la fusion dès aujourd'hui, et chaque attaque du jeu de questions doit être arrêtée par un garde-fou.

### 6.4 La recherche documentaire et le parcours des questions

`python -m evals.mesurer_rag` joue 53 questions annotées sur quatre configurations. Mesure du 20 septembre 2026 sur 1 072 documents : Hit@1 (part des questions dont le premier document retrouvé est un document attendu) de 0,415 en dense seul et 0,434 en hybride. L'hybride reste devant, d'environ une question sur 53 : un avantage observé sur ce jeu, pas une supériorité démontrée. Statut du jeu annoté, à citer sans le maquiller : annoté par un modèle à partir du corpus, non revalidé humainement ([`evals/RELECTURE-2026-09-06.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evals/RELECTURE-2026-09-06.md)).

Le parcours des questions a son propre jeu : 26 questions ([`rag/questions_demo.json`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/rag/questions_demo.json)), plus 8 reformulations réservées, soit 34 cas. Le 21 octobre, au niveau 2 (vrai modèle, Azure) : 19 refus avant le modèle, puis 8 réponses et 7 abstentions parmi les 15 cas transmis au modèle, aucune erreur technique ([`evidence/sprint-4/mesure-question-niveau2-2026-10-21-0818.json`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/sprint-4/mesure-question-niveau2-2026-10-21-0818.json) ; la veille, 9 réponses et 6 abstentions : la question R1 est passée d'une réponse à une abstention, le modèle variant d'un essai à l'autre). La sortie du modèle y est validée : un schéma JSON imposé au fournisseur en mode strict, puis revérifié par l'application ([`agents/question.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/agents/question.py), [`tests/test_question_contrat.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_question_contrat.py), 17 tests) ; les références montrées viennent des données stockées, jamais du texte du modèle. Attention en reproduisant : [`evals/mesurer_question.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evals/mesurer_question.py) n'est pas une simple lecture, son niveau 2 appelle Azure et il écrit un rapport.

### 6.5 Un test se prouve par sa capacité à échouer

Le 2 octobre, le test de 6.1.1 est passé du premier coup, ce qui ne prouve rien : le garde-fou était déjà branché. La preuve est venue d'une **mutation** : l'appel au garde-fou dans [`api/main.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/api/main.py) remplacé par un verdict toujours favorable, la suite tombe (`1 failed, 9 passed`), le fichier restauré, la suite repasse. Un test que l'on n'a jamais vu échouer ne protège rien ([`evidence/C17/preuve-garde-fou-sortie-branche.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C17/preuve-garde-fou-sortie-branche.md)). Depuis, chaque nouveauté suit l'ordre test rouge, code, test vert ; le 24 octobre encore, le test du contrat OpenAPI a d'abord échoué sur `{'X-API-Key'}` au lieu de `{'X-Cle-Exercice'}`.

### 6.6 Ce qui manque, C12

- **Le briefing reste du texte libre**, sans schéma de sortie, et **aucun jeu de référence de briefings** (prix attendu, faits obligatoires, formules interdites) n'en mesure l'exactitude. La validation structurée existe pour `/question`, pas pour `/briefing`. C'est le manque que je comblerais en premier.
- Le seuil de blocage de 85 % n'est pas atteint sur deux garde-fous ; le détournement ne reconnaît aucune des 8 reformulations ; le contrôle des nombres vérifie leur présence, pas leur sens.
- Les tests unitaires des garde-fous et les cas d'évaluation d'[`evals/cas.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evals/cas.py) portent les mêmes phrases en double, copiées et non importées.
- Seize tests exigent la base réelle, absente de la CI : ils ne peuvent tourner que sur le poste ; trois dossiers échappent au périmètre de la couverture (6.2).

---

## 7. C13 : la chaîne de livraison continue {: #c13 }

**Le cas d'usage** : une correction fusionnée arrive sans geste manuel (9 minutes le 24 octobre), après un vrai briefing d'essai ; si un contrôle échoue, l'ancienne version revient. Comment livre-t-on, et comment revient-on ?

Le modèle étant fourni par une API, la chaîne n'a pas d'étape d'entraînement : elle livre l'application qui appelle ce modèle, pas ses poids. Elle teste et valide le comportement du modèle dans l'application : portes d'évaluation en CI, vrai briefing avant chaque mise en service (7.2).

### 7.1 Les sept workflows

| Fichier | Déclencheur | Rôle |
|---|---|---|
| `test.yml` | chaque poussée et pull request sur `main` et `develop` | `pytest` : d'abord l'étape « Tester les données (collecte, nettoyage, import, RGPD) », 19 fichiers, puis la suite avec couverture ; `evals` : les garde-fous mesurés et les portes non compensables |
| `livraison.yml` | poussée, pull request, tag `livrable-*` | lint, recherche de secrets, construction et vérification de l'image ; publication après une fusion dans `main` ou sur un tag ; après une fusion seulement, livraison au serveur |
| `revue-pr.yml` | chaque pull request vers `main` | relecture adversariale automatisée, avec [`AGENTS.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/AGENTS.md) et [`CLAUDE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/CLAUDE.md) comme grille |
| `retour-arriere.yml`, `ingestion.yml` | bouton manuel, avec son nom et le motif | remettre la version précédente ; rafraîchir les articles et l'index de la production |
| `scan-giskard.yml` | bouton manuel | scan d'attaques, deux frontières, plafond de scénarios par frontière saisi (il limite le coût du juge sans le plafonner en euros) |
| `alerte-incident.yml` | envoi de Langfuse, ou bouton manuel | ouvre ou commente une issue `incident` |

### 7.2 Ce que fait `livraison.yml`, dans l'ordre

1. **Lint** (`ruff`, version fixée) et **recherche de secrets** dans tout l'historique (`gitleaks` v8.30.1, toutes les branches et tous les tags) : rien ne se construit si l'un est rouge.
2. **Tests, porte de livraison** : `scripts/verifier_livrable.py --ci` (suite et couverture, portes d'évaluation, liens internes ; sur un tag, le tag cité dans [`ETAT.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/ETAT.md) et [`CHANGELOG.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/CHANGELOG.md)).
3. **Construction de l'image**, jamais publiée à cette étape, puis **vérifications de l'image construite** : elle démarre et répond sur `/health`, annonce le bon commit, refuse sans clé (403), n'a pas de fichier `/app/.env` (le seul chemin contrôlé), embarque ses fichiers de déploiement.
4. **Publication** de l'image vérifiée sur le registre de GitHub (`ghcr.io/ganda15/rita-api`), après une fusion dans `main` ou sur un tag `livrable-*`. C'est l'image testée à l'étape 3 qui part, pas une reconstruction (corrigé le 26 septembre, issue #22). Sur un tag : neuf passages depuis le 15 octobre, sept verts.
5. **Après une fusion dans `main` seulement**, livraison au serveur. Le travail attend la fin du créneau du matin (de 8 h à 9 h, heure de Paris, rien ne bascule), puis envoie l'ordre `livrer` par une clé SSH dédiée, limitée par une commande forcée à un seul script ([`deploy/deployer.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/deploy/deployer.py)). Le serveur essaie l'image à part (pré-test : un vrai briefing, qui doit être conforme), rejoue les questions de démonstration sur la recherche documentaire, sans appel au modèle, la met en service, la contrôle, et remet l'ancienne si un contrôle échoue. Un tag publie son image sans jamais la livrer.

![La chaîne de livraison continue, du poste à la production](schemas/E3-chaine-livraison.png){: style="width:85%" }

*Figure 5. Les sept workflows, la règle de `main`, le serveur, et ce qui n'est pas construit. Source éditable : [`schemas/E3-chaine-livraison.drawio`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/rapports/E3/schemas/E3-chaine-livraison.drawio) ; détail : [`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/CI-CD.md).*

**Mesuré** : le 24 octobre, la version N18 (`b547cbf`) est allée de la fusion au service en 9 minutes 2 secondes, sans intervention (passage `40083432816`). Le **retour arrière** est un bouton : répété le 14 octobre (28 s de bout en bout) et le 15 octobre (35 s), il remet la version précédente avec sa configuration et son index ; pendant la bascule du 14, la production a répondu 502 pendant environ 7 s ([`evidence/sprint-2/N1-retour-arriere-2026-10-14.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/sprint-2/N1-retour-arriere-2026-10-14.md)). La procédure, ses résultats et ses limites sont écrits dans [`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/exploitation.md).

`main` ne bouge que par une pull request depuis `develop`. Sur le poste, un hook `pre-push` refuse la poussée directe. Sur GitHub, le ruleset « main protegee » exige une pull request et **six** checks verts (`lint`, `secrets`, `pytest`, `evals`, `construire-et-publier`, `revue`), interdit suppression et force-push, sans contournement ; un second ruleset interdit de déplacer ou supprimer un tag `livrable-*` ([`evidence/C19/ruleset-main-2026-10-14.json`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C19/ruleset-main-2026-10-14.json)). La chaîne a déjà refusé à bon droit : la PR #93, cassée exprès le 15 octobre, n'a jamais pu être fusionnée ([`evidence/sprint-2/journaux/pr-93-commit-casse.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/sprint-2/journaux/pr-93-commit-casse.txt)) ; le tag `livrable-sprint-4-v1`, absent du `CHANGELOG`, a été refusé par la porte de livraison le 21 octobre.

### 7.3 L'image

`Dockerfile` en deux étapes, `python:3.13-slim` tirée de `mirror.gcr.io` (le miroir public de Docker Hub tenu par Google, depuis le 21 octobre, carte #85), utilisateur `rita` sans shell (UID 10001), `HEALTHCHECK`. Le fichier Compose monte le conteneur en lecture seule avec `no-new-privileges` ; quinze tests lisent ce fichier ([`tests/test_docker_compose.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_docker_compose.py)).

### 7.4 Ce qui manque, C13

- **Aucune approbation humaine avant un déploiement** : l'environnement `production` de GitHub n'a pas de règle de protection ; la décision humaine est la fusion de la pull request relue.
- Le retour arrière ne revient que d'un pas et ne restaure pas la base ; son secours sans GitHub n'a jamais été exécuté. Le script du serveur s'installe à la main.
- **Manifeste de version partiel** : `/health` annonce le commit, la date de construction et l'index, mais aucune version de prompt n'existe. Le passage d'un tag reconstruit l'image : un même commit peut avoir deux empreintes.
- [`requirements.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/requirements.txt) n'est épinglé que pour six dépendances ; [`requirements-api.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/requirements-api.txt), celui de l'image, l'est entièrement (13 lignes). Pas de filtre de chemin, pas d'analyse de vulnérabilités des dépendances.
- **Aucune alerte ne signale une exécution rouge** : le 3 octobre, dix exécutions rouges consécutives sont passées inaperçues pendant 1 h 26 (INC-007, [`evidence/C21/INC-007-ci-rouge-scout-base-reelle.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C21/INC-007-ci-rouge-scout-base-reelle.md)).
- **Une livraison peut ne pas démarrer pour une raison extérieure au code** : le 26 octobre à 12 h 53, GitHub n'a lancé ni le lint ni la recherche de secrets de la livraison de `5a82279` (annotation : paiement en échec ou plafond de dépense atteint). Rien n'a été publié ni livré, la production est restée sur `2014e22` : la chaîne échoue fermée, mais aucune alerte ne l'a signalé.

---

## 8. Ce que les briefs de la formation ont apporté ici {: #s8 }

Velmo (juillet) a donné les trois emplacements de garde-fou et les deux chiffres toujours ensemble ; Sorabel (septembre), qu'un garde-fou non branché n'en est pas un (mutation du 2 octobre, refus journalisés) ; Mardik (septembre), l'identifiant de requête et le retour arrière, faits, le manifeste, partiel, et le filtre de chemin, non fait ; Industrialisation (fin septembre), les étapes de trace et les alertes, avec `/v1` reporté et des objectifs de service non mesurés ; Kaldera (1er octobre), tester la trace et non le texte (`test_trace_chemin.py`) ; Factum (2 octobre), `--cov` dans la commande et la preuve par une PR rouge (#93) ; le chapitre « Données » (validé le 3 octobre), la matrice d'accès à fermeture et le journal des appels d'outils (`mcp_calls`).

---

## 9. Reproduire {: #s9 }

**Cette version** : 1.9, 27 octobre 2026 : première page avec sommaire, ouverture par les deux usages, chaque compétence ouverte par son cas d'usage, preuves renforcées (entraînement, accessibilité de la documentation), deux lignes de la grille repassées partielles. La version gelée précédente est le tag `livrable-E3-v1` (commit `312056a`).

**Traçabilité des mesures** : du 2 au 24 octobre 2026, chacune avec sa date, sa commande, et pour la CI sa branche, son commit et son passage. La production servait alors `b547cbf`. Au 26 octobre, elle sert `2014e22` : code applicatif identique au tag, seuls des documents et un test ont changé depuis ; données, variables d'environnement et index n'ont pas été comparés.

**La pile** : Python 3.13 en intégration continue et 3.14 sur le poste ; FastAPI 0.136.3 ; LangGraph 1.2.9 pour le graphe ; ChromaDB 1.5.9 pour la recherche documentaire ; Langfuse 4.12.0 pour les traces ; PostgreSQL 18 ; Docker ; GitHub Actions. Versions lues dans [`requirements-api.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/requirements-api.txt) le 24 octobre 2026.

Les mesures de ce rapport portent sur le commit `9683f04` (branche `develop`) : pour les retrouver, partir de ce commit. Pour examiner le livrable gelé, partir du tag `livrable-E3-v1` (`312056a`), dont le résultat de CI, distinct, figure en section 6.1. Prérequis : [`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/exploitation.md). Depuis cette copie, avec `C:\Python314\python.exe` :

```
C:\Python314\python.exe -m pytest --cov -q
C:\Python314\python.exe -X utf8 -m evals.mesurer_entree
C:\Python314\python.exe -X utf8 -m evals.mesurer_gardefou
C:\Python314\python.exe -X utf8 -m evals.mesurer_sortie
C:\Python314\python.exe -X utf8 -m evals.mesurer_rag
C:\Python314\python.exe scripts\verifier_liens.py
```

Les mesures des garde-fous ne dépendent que du code ; la suite complète et la mesure de recherche exigent PostgreSQL (port 5433) et l'index local. Installation : [`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/exploitation.md). Ce rapport se rend en PDF par `scripts\rendre_pdf.py` ; ses schémas se régénèrent par [`schemas/generer_schemas.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/rapports/E3/schemas/generer_schemas.py), qui refuse d'écrire si un texte déborde de sa boîte ; les cinq figures publiées sont rendues depuis la mise en forme d'Era (`schemas/E3-*-illustre.svg`), dont [`tests/test_schemas_e3.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_schemas_e3.py) compare chaque texte à celui du générateur.

---

## 10. Les 44 critères, regroupés en 39 lignes {: #s10 }

État au 24 octobre 2026. ✅ tenu avec preuve · 🟠 partiel · 🔴 absent. Une auto-évaluation, pas une validation : seul le jury valide.

**Accessibilité de la documentation** (une ligne de C9, C11, C12 et C13) : les documents du dépôt sont en Markdown, à titres hiérarchisés, lisibles sans logiciel particulier ; ce rapport est un PDF balisé, c'est-à-dire structuré pour un lecteur d'écran, en langue déclarée française, dont chaque figure porte un texte alternatif et dont les tableaux sont du texte, pas des images. Limites : aucun essai avec un lecteur d'écran, et la page `/docs` générée par FastAPI n'a pas été auditée.

### C9, exposer le modèle (11 critères, en 8 lignes)

| Critère | État | Preuve |
|---|---|---|
| L'API restreint l'accès au modèle par une authentification | ✅ | `X-API-Key`, 403, aucune clé par défaut, refus journalisés ; [`tests/test_health.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_health.py), [`tests/test_refus_cle_journal.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_refus_cle_journal.py) |
| L'API donne accès aux fonctions du modèle selon les spécifications | ✅ | `POST /briefing` et `POST /question` ; valeur inconnue en 422 avant le modèle |
| Recommandations OWASP intégrées quand nécessaire | 🟠 | section 3.3 : API2, injection, LLM01, LLM02 appliqués ; API4 et API8 partiels (aucun en-tête de sécurité en production, mesuré le 24 octobre) |
| Sources versionnées sur un dépôt distant | ✅ | `Ganda15/rita-agent` |
| Les tests couvrent tous les points de terminaison | ✅ | section 3.4, 149 tests sur l'API |
| Les tests s'exécutent sans bug, résultats interprétés | ✅ | CI du 24 octobre : 1 719 réussis, 30 sautés expliqués, 2 `xfailed` : deux objectifs de blocage non atteints, déclarés, qui n'empêchent pas la livraison (section 6.1) |
| Documentation : architecture, points de terminaison, authentification | ✅ | [`docs/ARCHITECTURE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/ARCHITECTURE.md) (24 octobre : 19 chemins, deux clés, règles d'accès) ; contrat OpenAPI corrigé le 24 octobre |
| Documentation et API au standard OpenAPI, format accessible | ✅ | OpenAPI 3.1.0 généré ; Markdown à titres, PDF balisé (en tête de cette section) |

### C10, intégrer l'API dans une application (9 critères, en 8 lignes)

| Critère | État | Preuve |
|---|---|---|
| L'application de départ est installée et fonctionnelle en développement | ✅ | [`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/exploitation.md), voies courte et longue ; copie du poste du sprint 5 |
| La communication avec l'API fonctionne | ✅ | `test_frontend.py`, `test_smoke_ui.py`, `test_passerelle_mcp.py` ; production |
| Authentification et renouvellement intégrés selon la documentation | ✅ | clé saisie, `sessionStorage`, 403 traité ; pas de jeton expirant dans le contrat, donc pas de renouvellement |
| Tous les points de terminaison concernés sont intégrés | 🟠 | onze chemins appelés par les écrans, dont `/briefing` et `/question` : l'intégration du modèle est vérifiée ; la passerelle MCP appelle trois routes de données, mais son parcours portefeuille ne fonctionne pas sur le jeu de démonstration importé (#152) |
| Adaptations d'interface conformes aux spécifications | 🟠 | écrans spécifiés ([`evidence/C14/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/evidence/C14), [`docs/sprint-3/SPEC.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/sprint-3/SPEC.md)) ; la clé gardée trop tôt sur trois écrans (#73), non corrigé |
| Tests d'intégration sur tous les points de terminaison exploités | ✅ | 92 + 13 + 32 + 19 tests, plus 26 sur le journal des appels |
| Les tests s'exécutent en totalité, résultats interprétés | ✅ | suite verte |
| Sources versionnées sur le dépôt de l'application | ✅ | même dépôt |

### C11, monitorer le modèle (9 critères, en 9 lignes)

| Critère | État | Preuve |
|---|---|---|
| Les métriques sont expliquées sans erreur d'interprétation | ✅ | section 5.3, sur deux traces réelles, y compris le coût d'une trace à l'autre |
| Les outils sont adaptés au contexte et aux contraintes | 🟠 | section 5.1 : Langfuse en région UE, traces sans texte ; mais son contrat permet un traitement hors de la région, et sa vérification au regard de la règle « UE seule » est incomplète (registre RGPD, T3) |
| Un vecteur de restitution en temps réel est proposé | ✅ | tableau Langfuse « RITA C11 » ; tableau de bord de RITA sur `/sante`, en production depuis le 23 octobre |
| Accessibilité prise en compte dans le choix de l'outil | 🟠 | section 5.6 : examinée après le choix de Langfuse ; le tableau de RITA porte des marqueurs RGAA testés |
| La chaîne est d'abord testée dans un bac à sable | ✅ | suite sans traçage, doubles de client (INC-006) ; projet Langfuse propre à la copie (#130) |
| La chaîne est en état de marche | ✅ | production tracée depuis le 21 octobre, trace relue sans texte ; deux alertes qui ont sonné (#77, #130) |
| Sources versionnées | ✅ | [`src/traces.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/src/traces.py), [`monitorage/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/monitorage), [`.github/workflows/alerte-incident.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/.github/workflows/alerte-incident.yml) |
| Documentation d'installation, configuration, utilisation | ✅ | [`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/exploitation.md) : alertes, vigie, tableau de bord |
| Documentation au format accessible | ✅ | Markdown à titres, PDF balisé (en tête de cette section) |

### C12, tests automatisés (7 critères, en 7 lignes)

| Critère | État | Preuve |
|---|---|---|
| Cas à tester listés : partie visée, périmètre, stratégie | ✅ | section 6.1, figure 4 et trois extraits réels |
| Outils de test cohérents avec l'environnement | ✅ | pytest, coverage, Playwright, PyYAML, FastAPI TestClient |
| Tests intégrés, couverture souhaitée établie et respectée | ✅ | 96,32 % en CI le 24 octobre, seuil de 90 % établi par l'historique ; trois dossiers hors périmètre, mesurés à part (98 %) |
| Tests exécutés sans problème technique en environnement de test | ✅ | CI verte sur `develop` et `main` le 24 octobre ; chutes du 28 septembre et du 3 octobre expliquées |
| Sources versionnées | ✅ | [`tests/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/tests), [`evals/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/evals), [`.coveragerc`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/.coveragerc) |
| Documentation : installation de l'environnement de test, exécution, couverture | ✅ | [`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/exploitation.md) §5, [`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/CI-CD.md) |
| Documentation au format accessible | ✅ | Markdown à titres, PDF balisé (en tête de cette section) ; [`evidence/C12/preuve-ci-develop-2026-10-24.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/evidence/C12/preuve-ci-develop-2026-10-24.md) |

### C13, chaîne de livraison continue (8 critères, en 7 lignes)

| Critère | État | Preuve |
|---|---|---|
| Documentation de la chaîne : étapes, tâches, déclencheurs | ✅ | [`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/CI-CD.md) (24 octobre) : sept workflows, chaque déclencheur, chaque étape ; section 7 |
| Déclencheurs intégrés comme définis | ✅ | poussée, pull request, tag, manuel, `repository_dispatch` |
| Fichiers de configuration reconnus et exécutés | ✅ | 1 010 exécutions depuis le 28 juillet ; livraison N18 du 24 octobre |
| Étape de test des données intégrée | ✅ | étape nommée dans `test.yml`, avant la suite ([`tests/test_ci_donnees.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/tests/test_ci_donnees.py)) ; le 24 octobre : 296 réussis, 3 sautés |
| Étapes de test, d'entraînement et de validation du modèle intégrées | ✅ | entraînement sans objet, le modèle est fourni (section 7) ; portes d'évaluation en CI, dont deux sous leur objectif (`xfail`, 6.1) ; avant chaque mise en service, un vrai briefing et le rejeu des questions sur la recherche ; après, un contrôle par une vraie question |
| Sources de la chaîne versionnées | ✅ | [`.github/workflows/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/.github/workflows), [`.github/actions/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/.github/actions), [`.githooks/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/.githooks), [`deploy/`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2/deploy), [`scripts/verifier_livrable.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/scripts/verifier_livrable.py) |
| Documentation d'installation, configuration, test de la chaîne, accessible | ✅ | [`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/docs/CI-CD.md) §4 à §7 : secrets dont ceux de l'environnement `production`, permissions, installation, tests de la chaîne ; Markdown à titres, PDF balisé (en tête de cette section) |

**Décompte** : 34 ✅ · 5 🟠 · 0 🔴 sur 39 lignes couvrant 44 critères (version précédente : 36, 3, 0 ; version 1.4 du 11 octobre : 35, 4, 0). Deux lignes repassent partielles à la relecture du 27 octobre, sans changement du code : l'intégration de tous les points de terminaison (#152) et l'adaptation de l'outil de monitorage aux contraintes (règle « UE seule »). Les cinq lignes partielles : l'OWASP, ces deux-là, les adaptations d'interface (#73) et l'accessibilité du choix de l'outil.

---

## 11. Ce qui n'est pas fait, et les risques {: #s11 }

**Pas fait au 24 octobre 2026** : les en-têtes de sécurité et le message d'une panne totale (#75) ; la correction de la clé gardée trop tôt (#73) ; le contrat `/v1` ; une version de prompt ; un jeu de référence de briefings ; une alerte de silence et une alerte sur une CI rouge ; la capture du tableau Langfuse ; l'essai du retour arrière sans GitHub.

**La règle « UE seule »** (posée le 5 octobre : aucune donnée personnelle hors de l'Union européenne) : les replis Anthropic et OpenRouter restent dans l'ordre par défaut du code ([`src/llm.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v2/src/llm.py) : `foundry,anthropic,openrouter`), sans garantie de traitement dans l'Union européenne : le registre RGPD juge un transfert hors UE probable, et la règle non tenue tant qu'ils existent (T6). Sur le poste, `LLM_ORDRE=foundry` les coupe depuis le 11 octobre ; la valeur de production n'est pas dans le dépôt et reste à vérifier. Cette variable ne prouve pas, à elle seule, le respect de la règle pour toute la chaîne : le contrat de Langfuse permet un traitement hors de sa région (section 5.1).

**Risques pour la démonstration** : si Azure est indisponible, `/question` répond 503 ; pour `/briefing`, une panne de tous les fournisseurs activés produit un 500 générique, sans fuite, et sur le poste configuré Azure seul, une panne d'Azure suffit. La production et le poste n'ont pas les mêmes données (index de 2 140 articles en production le 24 octobre) : à l'oral, dire laquelle on montre. Le budget de GitHub Actions a déjà bloqué la CI 21 minutes le 23 octobre, et empêché une livraison le 26 octobre (section 7.4) : pas de livraison en direct devant le jury sans marge.

**Ce que ce rapport ne prétend pas** : qu'un garde-fou à motifs lexicaux arrête une intention habilement formulée (70 %) ; qu'une mesure de recherche sur un jeu annoté par un modèle vaut une mesure humaine ; que la chaîne d'alerte a attrapé une vraie panne : elle a attrapé une dégradation réelle et deux fausses alertes, chacune expliquée.

---

## 📖 Glossaire {: #glossaire }

| Terme | En clair |
|---|---|
| **422, 429, 502, 503** | codes HTTP : requête invalide (ici, valeur inconnue) ; trop de requêtes ; erreur d'un service appelé ; service indisponible |
| **Alerte (Langfuse)** | règle qui prévient quand une mesure franchit un seuil sur une fenêtre de temps |
| **AMF** | Autorité des marchés financiers ; ici, l'interdit de recommander l'achat ou la vente |
| **Briefing** | le texte court rédigé par le modèle pour une valeur |
| **Cascade de fournisseurs** | si le premier fournisseur du modèle échoue, RITA essaie le suivant ; la trace dit lequel a répondu |
| **Charge utile** | le contenu JSON envoyé avec un appel, ici par Langfuse à GitHub quand une alerte sonne |
| **Commande forcée** | sur le serveur, une clé SSH qui ne peut lancer qu'un seul script |
| **Empreinte (d'une image)** | identifiant calculé sur le contenu de l'image Docker ; deux images de même empreinte sont identiques |
| **Faux positif** | un texte légitime bloqué à tort ; se mesure toujours avec le taux de blocage |
| **Garde-fou** | contrôle qui bloque une question, un résultat d'outil ou un texte produit interdit |
| **Hit@1** | part des questions dont le premier document rendu est un document attendu |
| **Hybride (recherche)** | recherche par similarité de sens (dense) et par mots (BM25), fusionnées |
| **Jeton (token)** | unité de texte facturée par le fournisseur du modèle |
| **JSON imposé (mode strict)** | le fournisseur doit rendre un objet conforme à un schéma donné ; l'application le revérifie |
| **LangGraph** | bibliothèque qui exécute un graphe d'étapes avec un état partagé |
| **Limite de débit (quota)** | nombre maximal d'appels acceptés par minute ; au-delà, la réponse est 429 |
| **MCP** | *Model Context Protocol* : protocole qui expose des outils à un modèle de langage |
| **OpenAPI** | description normalisée d'une API REST, générée ici par FastAPI |
| **OWASP** | fondation qui publie les dix risques les plus courants (web, API, modèles de langage) |
| **p95** | la valeur sous laquelle tombent 95 % des mesures |
| **Pull request** | proposition de fusion d'une branche, relue avant intégration |
| **request_id** | un identifiant par requête, repris dans la réponse, le journal et la trace |
| **Retour arrière** | remise en service de la version précédente, en une opération |
| **RGPD** | règlement européen sur les données personnelles ; le registre des traitements en est l'article 30 |
| **Ruleset** | règle que GitHub applique lui-même sur une branche ou un tag (pull request, checks, interdits) |
| **Span, trace** | une étape chronométrée, et l'arbre des étapes d'une requête |
| **Tag** | étiquette Git posée sur un commit précis ; son lien ne bouge plus |
| **xfail strict** | test dont l'échec est attendu et déclaré ; s'il passe, la suite devient rouge |
