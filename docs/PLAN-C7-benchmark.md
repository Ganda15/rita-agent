# Plan C7 : le banc de comparaison des services de modèle, avant toute mesure

> Écrit le 03/10/2026 pour les cartes #32 (protocole) et #33 (conclusion). Rien n'a été mesuré : ce document fixe
> **ce qu'on mesure, comment, et ce qu'on refuse de conclure**, avant de dépenser un centime. Trois décisions sont
> attendues d'Era (§8), et une question est à poser au formateur (§2). Même méthode que les plans 62, 65 et 66.

## 1. Le besoin, reformulé au 03/10/2026 (critère C7.1)

RITA a besoin d'un service de modèle de langage pour **une seule tâche** : rédiger en français un briefing court
(600 à 900 caractères) sur une valeur, à partir de faits fournis dans le prompt (cours, variation, volume moyen) et
de passages d'articles retrouvés par la recherche documentaire. Les contraintes, toutes vérifiables dans le code :

| Contrainte | D'où elle vient | Comment on la mesure |
|---|---|---|
| **Jamais de recommandation d'achat ou de vente** (AMF) | prompt du rédacteur, `guardrails/sortie.py` | taux de textes retenus par le garde-fou de sortie, et relecture humaine des textes passés |
| **Fidélité aux faits fournis** : le cours et la variation du prompt doivent se retrouver dans le texte, rien d'inventé | `agents/analyst.py` | contrôle automatique : le cours et le signe de la variation sont dans le texte ; relecture humaine des chiffres non fournis |
| **Français lisible par un particulier** | utilisateur unique, non professionnel | grille à trois niveaux, notée à l'aveugle par Era (fournisseur masqué) |
| **Latence acceptable** pour un briefing du matin | rien d'imposé par une spécification acceptée ; on mesure, on ne fixe pas de seuil a priori | p50 et p95 sur l'échantillon, par fournisseur |
| **Coût par briefing** | budget 0 € sauf le modèle ; sept positions, un briefing par valeur et par jour | jetons entrée et sortie rapportés par le fournisseur, prix public daté |
| **Données personnelles** : aucune position, aucun prix de revient dans le prompt | registre RGPD T3, inventaire #68 | contrôle automatique du prompt envoyé |
| **Clé en variable d'environnement, jamais dans le code** | `AGENTS.md` | lecture du code |

Ce que le besoin n'exige pas, et qu'on ne mesurera donc pas : du code, de l'image, de la conversation, un contexte
long (le prompt tient en moins de 1 000 jetons).

## 2. Le périmètre : qui est comparé, qui ne l'est pas (critères C7.2, C7.3)

**Inclus, parce que déjà branchés dans `src/llm.py`** (ordre de la cascade : `foundry`, `anthropic`, `openrouter`) :

| Service (fournisseur) | Modèle réellement appelé (configuration du 03/10) | État sur le poste de démonstration |
|---|---|---|
| Azure AI Foundry | `claude-opus-4-8` (déploiement Azure) | clé absente : **indisponible pour la mesure** tant qu'elle manque |
| Anthropic, API directe | `claude-sonnet-5` | authentification en échec le 03/10 : **indisponible pour la mesure** tant que ce n'est pas réglé |
| OpenRouter | `anthropic/claude-sonnet-4.5` | opérationnel, un briefing réel servi le 03/10 |

Deux choses à dire franchement. D'abord, les trois services servent **la même famille de modèles** : comparer
trois fournisseurs d'un même modèle mesure le fournisseur (latence, coût, disponibilité, conditions), pas le
modèle. Ensuite, une version différente du modèle chez deux fournisseurs ferait passer une différence de modèle
pour une différence de fournisseur : le banc note donc **le fournisseur et l'identifiant exact du modèle** à chaque
appel, et ne compare que ce qui est comparable.

**Question à poser au formateur avant de mesurer** : « Pour C7, un banc sur trois fournisseurs du même modèle
répond-il au critère "services d'intelligence artificielle", ou attendez-vous au moins un modèle d'un autre
éditeur ? » Si la réponse est la seconde, l'ajout le moins coûteux est **un second modèle par OpenRouter** (même
clé, même code, par exemple un modèle Mistral ou OpenAI), déclaré comme quatrième ligne du banc. Décision D1 (§8).

**Exclus, et pourquoi** : les services qui exigent une carte bancaire ou un abonnement nouveau (budget 0 € hors
modèle) ; un modèle local (aucune machine du projet n'a la mémoire pour un modèle de qualité suffisante, et « local »
ne veut dire ni gratuit ni plus sobre sans mesure) ; les services sans conditions de traitement des données lisibles.
Les services nommés dans le brouillon de juillet 2026 (Gemini, Llama local sur Mac, Mistral) y figuraient avec des
**scores d'exemple d'un gabarit, jamais mesurés** ; ils ne sont ni repris ni exclus par ce plan, ils reviennent si D1
l'exige, avec une mesure.

## 3. Le jeu d'essai, figé avant la première mesure (critère C7.4)

- **Dix prompts**, construits par la fonction réelle du projet (`agents/analyst.py`), pas à la main : les neuf
  valeurs valides du portefeuille d'exemple (`data/positions-exemple.csv`, la dixième ligne y est volontairement
  corrompue) plus une valeur de l'univers sans article retrouvé, pour voir ce que chaque service fait du vide.
- **Les faits sont figés** : un instantané des cours, variations et volumes du jour J, et les passages retrouvés ce
  jour-là, enregistrés dans `evidence/C7/jeu-d-essai-<date>.json`. Le même instantané sert à tous les fournisseurs.
- **Mêmes réglages** : `max_tokens` du projet, aucune température modifiée, même prompt système.
- **Trois répétitions** par prompt et par fournisseur, pour voir la variance ; soit 30 appels par fournisseur.
- **Horodatage** de chaque appel, identifiant du modèle rendu par le fournisseur, jetons entrée et sortie, durée
  mesurée autour de l'appel, erreur éventuelle avec son type.

Ce qui est compté : un refus d'authentification est **une indisponibilité**, pas une note ; une réponse vide ou
tronquée est **un échec**, compté comme tel ; un délai supérieur à 60 s est un échec de latence.

## 4. Les mesures, et comment chacune se lit

| Mesure | Nature | Lecture |
|---|---|---|
| Taux de textes **conformes AMF** (non retenus par `guardrails/sortie.py`) | proportion sur 30 | **intervalle de Wilson à 95 %** ; sur 30 appels, un taux de 29/30 donne environ [0,83 ; 0,99] : on le dit, on ne conclut pas sur un écart de un |
| Taux de textes **fidèles** (cours et sens de la variation présents, aucun chiffre étranger au prompt) | proportion sur 30 | intervalle de Wilson, contrôle automatique puis relecture humaine des cas limites |
| **Qualité du français** | note 0, 1, 2 par texte, à l'aveugle | moyenne et répartition ; Era note, fournisseur masqué, ordre mélangé |
| **Latence** | p50, p95 en secondes | descriptive ; pas d'intervalle de Wilson, ce n'est pas une proportion |
| **Jetons et coût** | somme entrée et sortie, prix public du fournisseur à la date du banc | coût moyen par briefing ; le prix est cité avec sa date et son lien |
| **Disponibilité** | appels réussis sur appels tentés | proportion, Wilson |

**Ce qui est séparé à dessein** : la fidélité aux faits (vrai ou faux), le style (jugement humain), et l'interdit
AMF (garde-fou), parce qu'un service peut être excellent sur l'un et mauvais sur l'autre.

## 5. Environnement et conditions (critère C7.5, C7.6)

Pour chaque service : la région d'hébergement et les conditions de traitement des données, lues sur la page du
fournisseur **à la date du banc**, lien et date cités ; l'empreinte énergétique ou carbone **si le fournisseur
publie un chiffre daté, sinon « inconnu »**. Aucune note d'« éco-responsabilité » n'est inventée : le brouillon de
juillet en donnait, sans source, et elles ne sont pas reprises. Prérequis techniques relevés dans le code :
authentification (clé en variable d'environnement), bibliothèque (`anthropic`, `httpx`), limites de débit publiées,
format d'erreur, disponibilité d'un contrat de traitement des données.

## 6. Ce qui sera écrit, et où (critère C7.7)

- `evidence/C7/jeu-d-essai-<date>.json` : les dix prompts, l'instantané des faits.
- `evidence/C7/resultats-<date>.jsonl` : une ligne par appel, brute (fournisseur, modèle rendu, texte, erreur,
  durée, jetons, horodatage).
- `evidence/C7/notes-francais-<date>.csv` : les notes à l'aveugle, avec la clé de correspondance révélée après.
- `evidence/C7/preuve-benchmark-<date>.md` : le tableau des mesures avec intervalles, le coût réel dépensé, et la
  **recommandation argumentée** : le service retenu, ce qu'il fait mieux, ce qu'un autre fait mieux, et ce qui
  ferait changer la décision (par exemple une clé Foundry qui marche, ou un prix qui bouge).
- Le script `evals/benchmark_fournisseurs.py`, écrit **test d'abord** (jeu figé relu, Wilson juste, une
  indisponibilité comptée comme telle et jamais comme un zéro de qualité).

## 7. Coût et calendrier

30 appels par fournisseur, 3 fournisseurs (4 avec D1), environ 900 jetons par appel : de l'ordre de 100 000 jetons
au total, soit **quelques dizaines de centimes à quelques euros** selon le modèle, à plafonner par un paramètre du
script. Une matinée pour écrire le script test d'abord, une demi-heure d'appels, une heure de notation à l'aveugle,
une heure de rédaction. Après le gel du 15/10, avant le 25/10 si E4 le permet, sinon la semaine du 26/10.

## 8. Décisions attendues d'Era

| # | Question | Option A (recommandée) | Option B |
|---|---|---|---|
| D1 | Périmètre | trois fournisseurs de `src/llm.py`, et la question posée au formateur ; un quatrième modèle par OpenRouter seulement si le formateur l'attend | ajouter d'emblée un modèle d'un autre éditeur par OpenRouter |
| D2 | Plafond de dépense | 5 € pour tout le banc, paramètre du script, arrêt au-delà | sans plafond |
| D3 | Qui note le français | Era seul, à l'aveugle, grille à trois niveaux écrite avant | un modèle juge (refusé par ce plan : un modèle qui note un modèle de la même famille ne prouve rien au jury) |

Tant que D1 à D3 ne sont pas tranchées, aucun appel payant n'est lancé.

**Décision du 03/10/2026** : D1, D2, D3 = A (Era, « ok do it »). Première mesure le jour même, `evidence/C7/preuve-benchmark-2026-10-03.md` : un seul fournisseur mesurable (OpenRouter, 30 appels, 0,14 USD), les deux autres indisponibles faute de clés sur le poste ; la question du formateur reste à poser.

## 📖 Glossaire

- **Banc (benchmark)** : la même épreuve donnée à plusieurs services, dans les mêmes conditions, pour les comparer.
- **Intervalle de Wilson** : fourchette dans laquelle se trouve vraisemblablement un taux mesuré sur peu d'essais ; sur 30 essais, elle est large, et il faut le dire.
- **Fournisseur, modèle** : le fournisseur sert l'accès (OpenRouter, Anthropic, Azure) ; le modèle est ce qui rédige (par exemple `claude-sonnet-5`). Un banc compare l'un ou l'autre, jamais les deux à la fois sans le dire.
- **Notation à l'aveugle** : noter des textes sans savoir quel service les a produits, pour que la préférence ne guide pas la note.
- **p50, p95** : la durée sous laquelle tombent la moitié, puis 95 %, des appels.
