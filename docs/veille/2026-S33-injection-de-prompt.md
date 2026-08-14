# Veille S33 — OWASP Top 10 2026 et la « lethal trifecta »

**Auteur** : Eramalingam GANDAKUMAR
**Semaine** : 2026-S33, du 10 au 16 août 2026 · **Créneau tenu** : vendredi 14 août 2026
**Thématique** : sécurité des agents LLM — injection de prompt

> **Méthode.** Chaque affirmation de cette note repose sur une vérification faite dans le code
> du projet ou à la source primaire, et la commande de vérification est citée à côté du
> constat. Rien n'est repris d'un résumé de seconde main.

## Résumé en clair

Cette semaine, l'OWASP a publié la version 2026 de sa liste des dix risques les plus
importants pour les applications qui utilisent un modèle de langage. L'injection de prompt —
glisser une fausse instruction dans une donnée que le programme va lire — reste au premier
rang pour la troisième année de suite. Nouveauté : ce risque couvre maintenant aussi les
instructions cachées dans une **image** ou un **son**, et le classement s'appuie pour la
première fois sur des incidents réellement survenus. J'ai comparé ces risques à RITA :
**deux points de vigilance sont confirmés, un troisième ne s'applique pas**, et RITA se révèle
mieux protégé que prévu sur le risque qui progresse le plus.

## Ce que j'ai lu cette semaine

| Source | Titre (texte de lien explicite) | Date de publication | Auteur |
|---|---|---|---|
| OWASP GenAI Security Project | [OWASP GenAI LLM Top 10 — édition 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) | 3 août 2026 | fondation OWASP, contributeurs nommés |
| OWASP GenAI Security Project | [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resources/) | 2026 | fondation OWASP |
| simonwillison.net | [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) | 16 juin 2025 | Simon Willison — a créé le terme *prompt injection* en 2022 |
| ANSSI / CERT-FR | [Recommandations de sécurité pour un système d'IA générative](https://messervices.cyber.gouv.fr/guides/recommandations-de-securite-pour-un-systeme-dia-generative) | 29 avril 2024 | agence nationale française |

## Analyse de fiabilité

| Source | Auteur identifié ? | Intérêt commercial ? | Confirmée ailleurs ? | Retenue ? |
|---|---|---|---|---|
| OWASP | oui — fondation, contributeurs nommés | **non** — à but non lucratif | oui — reprise par plusieurs médias spécialisés | ✅ |
| Simon Willison | oui — nommé, notoriété établie | **non** — blog personnel, ne vend rien | oui — concept repris par l'ensemble du secteur | ✅ |
| ANSSI | oui — agence d'État | **non** | — source primaire officielle | ✅ |
| Éditeurs de modèles (Anthropic, OpenAI) | oui | ⚠️ **oui, direct** | — | ⚠️ jamais source unique |
| arXiv | oui | non | ⚠️ **non relu par les pairs** | ⚠️ à signaler comme préprint |

**Information écartée cette semaine, et pourquoi** :
sept blogs d'éditeurs de sécurité commentant le Top 10 (Mend, ReversingLabs, Repello,
HiddenLayer, Sophos, Airia, Webnestify) — **conflit d'intérêts direct** : ils décrivent le
problème qu'ils vendent. Plus un article Medium signé d'un pseudonyme : **auteur non
identifiable**, donc critère de fiabilité non satisfait.

**Vérification faite à la source, et elle comptait** : la page `genai.owasp.org/llm-top-10/`
affichait encore l'édition **2025**. C'est une page d'archive. L'édition **2026** est bien
publiée, sur une autre adresse, **le 3 août 2026** — alors que la presse annonçait le 6 août.
*Une information reprise par cinq sites reste non vérifiée si aucun n'est la source.*

## Ce que j'en retiens

1. **L'injection de prompt reste le risque n°1, pour la troisième année consécutive.** Ce
   n'est donc pas une mode : c'est un problème structurel, non résolu. Le garde-fou que j'ai
   écrit dans `guardrails/injection.py` traite le bon sujet.

2. **Le risque s'élargit au-delà du texte** : l'édition 2026 range désormais dans la même
   catégorie les instructions cachées dans une image ou un son. Mon filtre est en expression
   régulière sur du texte — il serait aveugle à ce type d'attaque.

3. **Ce n'est pas le modèle qui se rebelle, c'est le modèle qui obéit.** La « lethal
   trifecta » de Simon Willison le formule ainsi : trois capacités réunies — données privées,
   contenu non fiable, moyen de communiquer vers l'extérieur — suffisent, sans aucune faille
   dans le code classique. C'est une grille de lecture **d'architecture**, pas de programmation.

## ⭐ Ce que ça change dans RITA

### La « lethal trifecta » appliquée à RITA — 2 conditions sur 3

| Condition | RITA | Vérification |
|---|---|---|
| **Données privées** | ✅ **OUI** — table `position` : quantités, prix de revient, plus-values. Exposée par `GET /donnees/portefeuille` | `db/schema.sql` · `api/donnees.py` |
| **Contenu non fiable** | ✅ **OUI** — pages Boursorama et flux RSS écrits par des tiers | `sources/scraper.py` · `sources/rss.py` |
| **Communication externe choisie par le modèle** | ❌ **NON** | voir ci-dessous |

**Pourquoi la troisième condition n'est pas remplie — et c'est un choix d'architecture, pas
une chance :**

- Le graphe LangGraph compte **deux nœuds fixes** — `scout` puis `redacteur` — et se termine.
  Aucun `tools=` n'est déclaré : **le modèle ne peut appeler aucun outil.**
  *(`grep -rn "tools=" graph/ agents/` → aucun résultat.)*
- Le seul appel sortant du code de l'agent est `httpx.post` vers le fournisseur du modèle
  (`src/llm.py:43`). **Son adresse est fixée dans le code** : le modèle ne peut pas la choisir.
- Le traçage LangSmith, seul autre canal sortant envisagé, **n'est pas activé** — vérifié le
  14/08 (ni `LANGCHAIN_TRACING_V2` ni `LANGCHAIN_API_KEY` dans le `.env`).

> Autrement dit : une page hostile peut faire **dire** n'importe quoi à RITA, mais **ne peut
> pas lui faire envoyer quoi que ce soit** à un tiers. Le seul dégât possible est un texte
> faux affiché à l'utilisateur — ce que le garde-fou de sortie et l'interdit AMF traitent déjà.

### « Excessive Agency » — le risque qui progresse le plus, et RITA y est peu exposé

L'entrée passe de la 6ᵉ à la 3ᵉ place. RITA est **structurellement à faible pouvoir d'agir** :

| Ce que RITA fait tout seul | Où | Le modèle peut-il le déclencher ? |
|---|---|---|
| Écrire en base (cotations, articles, taux) | `pipelines/ingest.py` | **Non** — c'est le pipeline d'ingestion, lancé par une tâche planifiée, hors du graphe de l'agent |
| Produire un texte | `agents/analyst.py` | Oui, mais c'est sa seule sortie |
| Appeler un outil externe | — | **Aucun outil déclaré** |

**À dire à l'oral** : la séparation entre le pipeline d'ingestion et le graphe de l'agent
n'était pas motivée par la sécurité au départ — mais elle produit exactement l'effet
recommandé : **l'agent ne peut rien écrire**.

### Actions retenues

| Constat | Action pour RITA | Fichier concerné | Fait ? |
|---|---|---|---|
| OWASP 2026 étend l'injection aux images et aux sons ; le filtre est en regex sur du texte | **Aucune action immédiate** : `grep -rniE "image\|base64\|vision\|audio\|ocr"` sur `sources/ agents/ graph/ pipelines/` → **0 résultat**. RITA ne lit ni image ni son. **Écrire cette limite** en tête de `guardrails/injection.py` pour que l'angle mort soit connu le jour où une source visuelle sera ajoutée | `guardrails/injection.py` | ⬜ |
| La 3ᵉ condition de la trifecta est absente **par construction** | **Documenter cette propriété** dans le dossier E3 : c'est un argument de conception, pas un hasard. Elle disparaîtrait si on ajoutait un appel d'outil au modèle | `docs/rapports/` | ⬜ |
| Le registre RGPD décrivait T3 (LangSmith) comme actif alors qu'il ne l'est pas | ✅ **corrigé le 14/08** — T3 passé en « envisagé, non activé » | `db/RGPD-registre-des-traitements.md` | ✅ |
| Activer un jour le traçage rétablirait un canal sortant | **Avant d'activer**, choisir l'outil : auto-hébergé = pas de sortie ; hébergé = la 3ᵉ condition revient | `db/RGPD-registre-des-traitements.md` | ⬜ |

## Question ouverte pour la semaine prochaine

L'OWASP publie un **second** document, distinct : **« Top 10 for Agentic Applications 2026 »**.
RITA *est* une application agentique — graphe LangGraph, deux agents. Je ne l'ai pas lu cette
semaine.

**Question S34** : les risques propres aux applications agentiques recoupent-ils ceux des
applications LLM, ou en ajoutent-ils que RITA ne traite pas du tout ?

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Injection de prompt** | Texte glissé dans une donnée pour que le modèle le prenne pour une instruction |
| **Injection indirecte** | La même chose, cachée dans une page web ou un flux que l'agent lit tout seul |
| **Attaque inter-modale** | Instruction cachée dans une image ou un son au lieu du texte |
| **Excessive Agency** | Un agent qui a plus de pouvoir d'agir que nécessaire — il peut faire des dégâts en suivant une instruction hostile |
| **Lethal trifecta** | Les 3 conditions qui, réunies, rendent l'exploitation quasi certaine |
| **Préprint** | Article de recherche publié **avant** relecture par les pairs |
| **Garde-fou** (*guardrail*) | Contrôle qui filtre ce qui entre ou sort d'un modèle |

---

### ✅ Contrôle d'accessibilité avant publication

- [x] un seul `#`, puis `##` / `###` sans niveau sauté
- [x] aucun lien nommé « ici » ou « cliquez ici », aucune URL nue
- [x] pas d'image dans cette note (donc pas de texte alternatif requis)
- [x] tableaux avec ligne d'en-tête, aucune cellule fusionnée
- [x] aucune information portée par la seule couleur
- [x] résumé en langage clair présent
- [x] chaque terme technique défini + glossaire rempli
