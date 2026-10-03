# Rapport E2 : veille, choix d'un service de modèle, et son paramétrage

**Bloc de compétences BC02, compétences C6 à C8** · Projet fil rouge **RITA** · RNCP 37827, Développeur en intelligence artificielle

| | |
|---|---|
| **Candidat** | Eramalingam Gandakumar |
| **Formation** | Simplon × Wild Code School, promotion Développeur IA et IA agentique |
| **Dépôt** | `Ganda15/rita-agent` (privé ; accès du jury par invitation de collaborateur) |
| **Version** | 0.1, squelette du 3 octobre 2026 ; format attendu 15 à 20 pages, oral 15 minutes, sans démonstration ; dû le 5 novembre 2026 |
| **État** | C6 et C8 rédigés depuis les faits du dépôt ; **C7 : le banc a tourné une fois sur le seul fournisseur disponible** (OpenRouter), aucune comparaison tant que les deux autres clés manquent ; plan validé D1 à D3 = A |

## Lire ce rapport

Trois compétences, trois questions. C6 : comment je me tiens informé, comment je juge une source, comment je partage,
et ce que ça change dans RITA. C7 : pourquoi ce service de modèle plutôt qu'un autre. C8 : comment on y accède, comment
il est configuré, surveillé, documenté et remis à quelqu'un d'autre. Un chiffre se cite mesuré, avec sa date et sa
commande ; ce qui n'existe pas est écrit comme tel, « Information missing, to complete later ». Un brouillon de ce
rapport existait en juillet 2026 dans le coffre de notes du candidat ; ses tableaux comparatifs portaient des scores
d'exemple d'un gabarit de formation, jamais mesurés. **Rien n'en est repris** ; ce rapport repart des faits.

---

## 1. Le contexte, une seule fois

RITA rédige en français un briefing court par valeur d'un portefeuille, à partir de données collectées (cours, taux,
séries macro, articles) et d'un modèle de langage fourni par un service extérieur. Deux contraintes tiennent tout :
jamais de recommandation d'achat ou de vente (AMF), et aucune donnée personnelle (positions, prix de revient) envoyée
au modèle. Le rapport E1 décrit les données, le rapport E3 l'API, les tests, le monitorage et la livraison. Celui-ci
décrit **ce qui vient de l'extérieur** : l'état de l'art que je suis, le service que je choisis, et la façon dont je le
paramètre.

---

## 2. C6 : la veille technique et réglementaire

### 2.1 Le sujet, et pourquoi lui

La sécurité des agents qui lisent du texte venu de l'extérieur, et d'abord l'**injection de prompt** : glisser une
instruction dans une donnée que le programme va lire. RITA lit chaque soir des articles de presse et les donne au
modèle ; c'est exactement la surface d'attaque. Le sujet est donc mobilisé dans le code, pas choisi pour la mode :
trois garde-fous (`guardrails/`), un scan d'attaques, deux incidents de sécurité documentés en découlent.

### 2.2 La méthode, telle qu'elle est pratiquée

Protocole dans `docs/veille/README.md` : un créneau le lundi de 9 h à 10 h ; des sources pesées une par une (auteur
identifié, notoriété, intérêts, accessibilité) : OWASP GenAI, ANSSI, CNIL, NIST, le blog de Simon Willison, arXiv
`cs.CR` en second rang ; une note par semaine depuis un gabarit (résumé en clair, ce que j'ai lu, analyse de
fiabilité, ce que ça change dans RITA, accessibilité). Le relevé des nouveautés est fait à la main, consigné chaque
semaine dans un fichier de candidats avec sa date ; **la note est écrite par le candidat**, une note produite par un
modèle ne prouverait rien. Le protocole a été corrigé le 03/10/2026 sur deux points qu'il affirmait à tort : une tâche
planifiée qui n'a jamais existé, et un module de collecte du projet (`sources/rss.py`, flux financiers) présenté comme
l'outil de veille. Les deux corrections sont datées dans le fichier.

### 2.3 Ce qui a été produit, semaine par semaine

| Semaine ISO | Note | Ce qu'elle a changé dans RITA |
|---|---|---|
| S33 (10 au 16/08), tenue le 14/08 | OWASP Top 10 2026 et la « lethal trifecta » | deux points de vigilance confirmés, un troisième sans objet ; le garde-fou de sortie, documenté mais absent, découvert et construit (INC-004) |
| S34 (17 au 23/08), tenue le 17/08 | le Top 10 agentique, et ce que mon 100 % ne mesurait pas | le 100 % du garde-fou était circulaire (cas écrits à partir des motifs) ; cas adverses ajoutés, taux réel 70 %, seuil 85 % déclaré non atteint |
| S35 (24 au 30/08), rédigée le 08/09 | le seuil de 85 % face à la littérature | le choix de garder le seuil et de déclarer l'écart (`xfail` strict) |
| S36 (31/08 au 06/09), rédigée le 08/09 | l'incident Claude Code, et LongGuard qui confirme le choix des expressions régulières | la limite structurelle des motifs lexicaux, écrite dans le code et dans E3 |
| S37 à S39 | aucune note | deux semaines sans séance et une avec relevé seul ; dit tel quel, pas antidaté (carte #31) |
| S40 | candidats relevés le 28/09, note à écrire | carte #30 |

Les quatre notes sont réunies dans `docs/veille/Veille-C6-synthese-S33-a-S36.pdf`, assemblée par un script depuis
les notes, sans reformulation. Deux notes ont été rédigées en rattrapage et le disent dans leur en-tête ; leurs
étiquettes de semaine, décalées d'une semaine, ont été corrigées le 03/10 en gardant la période réellement balayée.

### 2.4 Le partage, et ce qui manque

Un partage : la note S33 postée dans le canal Discord de la promotion le 16/08, terminée par une question ouverte.
**Aucune capture des réponses n'existe au 03/10**, et aucun envoi au formateur n'a été fait. Le critère « en animant
le travail collectif » est donc lancé, pas prouvé. La preuve attendue est écrite dans `evidence/C6/README.md` : le
fil avec ses réponses, l'envoi daté au formateur et son retour. Information missing, to complete later.

### 2.5 Accessibilité

Notes en Markdown dans le dépôt (titres hiérarchisés, tableaux avec en-têtes, liens explicites, aucune information
portée par la seule couleur), synthèse en PDF balisé par le navigateur. Les sources institutionnelles retenues sont
soumises au RGAA. Ce qui n'est pas fait : aucun audit outillé du PDF.

---

## 3. C7 : le choix du service de modèle

**État au 3 octobre 2026 au soir : le banc existe et a tourné une fois, mais un seul fournisseur a pu être mesuré,
donc aucune comparaison n'existe encore.** Ce que le projet possède : une cascade de trois fournisseurs branchée
(`src/llm.py`), un seul opérationnel sur le poste de démonstration, un **plan de banc** validé (D1 à D3 = A),
`docs/PLAN-C7-benchmark.md`, qui fixe avant toute dépense : le besoin reformulé (§1 du plan), le
périmètre et les exclusions (§2), un jeu d'essai figé de dix prompts construits par le code réel (§3), les mesures et
leur lecture, intervalles de Wilson pour les proportions (§4), l'information environnementale datée ou marquée
inconnue (§5), les fichiers de preuve (§6), le coût et le calendrier (§7), et trois décisions attendues (§8).

Une question est posée au formateur avant d'exécuter : un banc sur trois fournisseurs d'une même famille de modèles
répond-il au critère, ou faut-il au moins un modèle d'un autre éditeur ? La réponse change le périmètre, pas la
méthode.

Les sections suivantes seront remplies **après** la mesure, depuis `evidence/C7/` :

- 3.1 Le besoin et les contraintes : Information missing, to complete later (le plan en donne la version du 03/10).
- 3.2 Services inclus, exclus, et pourquoi : Information missing, to complete later.
- 3.3 Résultats mesurés : **première mesure le 03/10** (`evidence/C7/preuve-benchmark-2026-10-03.md`) sur dix cas figés, trois répétitions : OpenRouter servant `anthropic/claude-sonnet-4.5`, 30 appels sur 30 réussis, 30 textes conformes AMF et 30 fidèles aux faits fournis (Wilson 95 % [0,89 ; 1,00] pour chaque taux), latence médiane 6,3 s et p95 7,3 s, 797 jetons en entrée et 242 en sortie en moyenne, 0,0060 USD par briefing au prix public du jour ; troisième passage du 03/10, sur le prompt qui porte les 13 indicateurs du scout (le deuxième passage, prompt à quatre nombres corrigé de la carte #57, donnait 5,6 s et 0,0045 USD ; le premier, avant #57, voyait 5 textes sur 30 appeler des capitaux des « titres échangés »). Avec les indicateurs, 30 textes sur 30 citent le RSI, 25 la volatilité, aucun mot de signal n'apparaît. Azure AI Foundry et Anthropic en direct : **indisponibles pour la mesure** (clés absentes du poste), pas notés. Qualité du français : à noter par Era à l'aveugle, fichier préparé. Comparaison : Information missing, to complete later.
- 3.4 Environnement et prérequis techniques : Information missing, to complete later.
- 3.5 Recommandation argumentée : Information missing, to complete later.

Ce que ce rapport refuse de faire : présenter des scores non mesurés, ou transformer une vérification de
disponibilité (un fournisseur répond, deux échouent) en comparaison de qualité.

---

## 4. C8 : le service retenu, paramétré, surveillé, documenté

### 4.1 L'accès et la configuration

Trois fournisseurs en cascade, dans l'ordre `foundry,anthropic,openrouter`, configurable par la variable
`LLM_ORDRE` ; depuis le 3 octobre au soir, Foundry est appelé par son point compatible OpenAI (déploiement `gpt-5.4`,
ressource du candidat, gratuite), ce qui met un modèle d'un autre éditeur que Claude dans la cascade et dans le banc ; un modèle par fournisseur, configurable (`AZURE_FOUNDRY_DEPLOYMENT`, `ANTHROPIC_MODEL`,
`OPENROUTER_MODEL`) ; les clés lues dans l'environnement, jamais dans le code, un hook refusant toute écriture d'un
agent dans le fichier de secrets. Si le premier fournisseur échoue, le suivant est essayé, et chaque tentative est
tracée.

**Ce qui est démontré, et ce qui ne l'est pas.** Le 03/10/2026, un briefing réel a été servi : Azure AI Foundry
a échoué en 1 ms (clé absente du poste), l'API Anthropic en 0,18 s (authentification impossible), OpenRouter a
répondu en 5,6 s avec `anthropic/claude-sonnet-4.5`, 616 jetons en entrée et 210 en sortie. Le service **retenu et
démontré** est donc OpenRouter ; les deux autres sont branchés, pas opérationnels sur ce poste. Dire « trois
fournisseurs opérationnels » serait faux.

### 4.2 Ce qui est envoyé au service

Le prompt contient le ticker, le cours, la variation, le volume moyen et des passages d'articles ; **aucune position,
aucun prix de revient**. L'inventaire champ par champ (source, destinataire, conservation, finalité) est en cours au
registre RGPD (carte #68) : Information missing, to complete later.

### 4.3 Le monitorage disponible

Langfuse Cloud, région Union européenne. Chaque briefing donne une trace : une racine, une étape par nœud et par
garde-fou, une génération par fournisseur essayé avec modèle, jetons et erreur ; le verdict AMF est une note sur la
trace ; le même identifiant de requête est dans la réponse, le journal et la trace. Un tableau de bord à trois tuiles
existe ; une chaîne d'alerte vers une issue GitHub a été exécutée une fois à la main. Limites, dites telles quelles :
le coût affiché vaut zéro pour le modèle servi par OpenRouter (nom absent de la grille de prix), quinze traces
factices polluent les agrégats jusqu'à leur suppression, les deux alertes ne sont pas réglées. Détail : rapport E3 §5,
`evidence/C11/`.

### 4.4 La documentation, et sa remise

`docs/EXPLOITATION.md` : clés, installation avec et sans Docker, vérification, services externes, données, dépannage,
monitorage. Corrigé le 03/10 : la table des clés plaçait OpenRouter en deuxième, le code le place troisième ; le
fournisseur Foundry y manquait. **La remise aux parties prenantes n'est pas prouvée** : le guide n'a été envoyé à
personne (carte #43). La preuve attendue : un envoi daté au formateur et sa réponse, rangés dans `evidence/C8/`.
Information missing, to complete later.

---

## 5. Les 20 critères, un par un

État au 3 octobre 2026. ✅ tenu avec preuve · 🟠 partiel · 🔴 absent.

| Critère | État | Preuve ou manque |
|---|---|---|
| C6.1 thématique liée au projet | ✅ | injection de prompt, mobilisée dans `guardrails/` |
| C6.2 récurrence planifiée, une heure par semaine | 🟠 | créneau écrit ; quatre notes dont deux en rattrapage ; S37 à S40 sans note |
| C6.3 outils d'agrégation cohérents, budget | 🟠 | relevé manuel documenté le 03/10 ; budget 0 € ; aucun outil à montrer |
| C6.4 synthèses communiquées, format accessible | 🟠 | notes et synthèse PDF ; un partage Discord sans capture |
| C6.5 informations partagées sur la thématique | ✅ | les quatre notes |
| C6.6 fiabilité des sources, intérêts | ✅ | tableau par source dans chaque note et dans le protocole |
| C6.7 analyse récente, sourcée, structurée | 🟠 | notes datées et sourcées ; trou S37 à S39 |
| C6.8 sources accessibles, recoupement | 🟠 | listes et grilles ; pas d'audit outillé |
| C7.1 besoin reformulé | 🟠 | plan §1, à confirmer par la mesure |
| C7.2 services inclus et exclus | 🟠 | plan §2 ; question au formateur ouverte |
| C7.3 raisons d'exclusion | 🟠 | plan §2 |
| C7.4 adéquation fonctionnelle mesurée | 🟠 | un fournisseur mesuré sur dix cas figés (conformité, fidélité, latence, coût) ; les deux autres indisponibles ; français à noter |
| C7.5 approche environnementale | 🔴 | aucune donnée vérifiée |
| C7.6 prérequis et contraintes techniques | 🟠 | relevés dans le code (`src/llm.py`) et dans la sonde du banc (clé, authentification), à compléter par fournisseur |
| C7.7 recommandation argumentée | 🔴 | après la mesure |
| C8.1 service accessible, authentification | ✅ | briefing réel du 03/10, clé en environnement |
| C8.2 configuration conforme aux besoins | 🟠 | un fournisseur opérationnel sur trois |
| C8.3 monitorage opérationnel | 🟠 | trace complète et tableau ; coût faux, traces factices, alertes non réglées |
| C8.4 documentation d'accès, installation, tests, dépendances, flux | ✅ | `docs/EXPLOITATION.md`, corrigé le 03/10 |
| C8.5 documentation communiquée, accessible | 🔴 | aucune remise prouvée (#43) |

**Décompte** : 5 ✅ · 12 🟠 · 3 🔴 sur 20 (le matin : 5, 11, 4).

---

## 6. Ce qui n'est pas fait, et dans quel ordre le faire

1. Captures du fil Discord du 16/08 et envoi daté au formateur (Era) : la seule preuve de partage possible.
2. Note S40 écrite par Era depuis les candidats ; les semaines S37 à S39 restent déclarées sans séance.
3. Question au formateur sur le périmètre (D1) ; poser les clés Foundry et Anthropic sur le poste ; relancer le banc (une commande) pour avoir la comparaison ; noter le français à l'aveugle.
4. Envoi du guide d'exploitation au formateur, preuve rangée (#43).
5. Rédaction des sections C7 depuis `evidence/C7/`, relecture, PDF (`scripts/rendre_pdf.py`), tag `livrable-E2-v1`.

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Injection de prompt** | glisser une instruction dans une donnée que le programme va lire, pour détourner le modèle |
| **Veille** | lecture régulière et sourcée de ce qui change dans un domaine, avec une conclusion pour le projet |
| **Banc de comparaison** | la même épreuve donnée à plusieurs services dans les mêmes conditions |
| **Cascade de fournisseurs** | si un service échoue, le suivant est essayé ; la trace dit lequel a répondu |
| **Intervalle de Wilson** | fourchette d'un taux mesuré sur peu d'essais |
| **Trace** | l'arbre chronométré des étapes d'une requête, dans l'outil de monitorage |
| **Remise (handover)** | donner la documentation à quelqu'un qui peut faire tourner le service sans vous, et en garder la preuve |
