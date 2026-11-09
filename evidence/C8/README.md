# C8 : paramétrer le service de modèle retenu, et le remettre à quelqu'un d'autre

> C8 : *« Paramétrer un service d'intelligence artificielle pour l'intégrer dans un projet applicatif, en
> documentant son accès, sa configuration, son monitorage et sa remise aux parties prenantes. »*
>
> Dossier créé le 03/10/2026. Il ne contient aucune preuve nouvelle : il indexe celles qui existent ailleurs
> dans le dépôt, critère par critère, et dit ce qui manque. Livrable E2.

## Ce qui existe, et ce que ça prouve

| Pièce | Où | Ce que ça prouve pour C8 |
|---|---|---|
| Cascade de trois fournisseurs, clés lues dans l'environnement, modèle configurable par variable ; depuis le 03/10 au soir, Foundry par son point compatible OpenAI (`gpt-5.4`, gratuit pour le projet, 1ᵉʳ de la cascade) | `src/llm.py` (`LLM_ORDRE`, `AZURE_FOUNDRY_DEPLOYMENT`, `ANTHROPIC_MODEL`, `OPENROUTER_MODEL`), `.env.example` | l'accès et la configuration (C8.1, C8.2) |
| Un briefing réel servi le 03/10 : OpenRouter répond en 5,6 s après deux fournisseurs en échec, 616 jetons entrée, 210 sortie | `../C9/preuve-api-modele-2026-10-03.md`, `../C11/preuve-langfuse-2026-10-03.md` §5 | le service est accessible et configuré ; le monitorage le montre (C8.1, C8.3) |
| Chaque tentative tracée (fournisseur, modèle, jetons, erreur), tableau « RITA C11 », chaîne d'alerte exécutée une fois | `../C11/` | le monitorage disponible du service est en marche (C8.3), avec ses limites |
| Guide d'exploitation : clés, installation avec et sans Docker, vérification, services externes, données, dépannage, monitorage | `../../docs/EXPLOITATION.md` | la documentation d'accès, d'installation, de tests, de dépendances, de flux de données (C8.4) |
| Tests de la cascade et du traçage | `tests/test_llm.py` (5), `tests/test_traces.py` (7), `tests/test_traces_robustesse.py` (8) | la configuration est testée, une panne du traçage ne casse pas le service |

## Ce qu'il faut dire tel quel

- Deux fournisseurs répondent sur le poste de démonstration depuis le 03/10 au soir : Azure AI Foundry
  (`gpt-5.4`, point compatible OpenAI, premier de la cascade, gratuit pour le projet) et OpenRouter
  (`anthropic/claude-sonnet-4.5`, secours). L'API Anthropic directe n'a pas de clé. Le service retenu et démontré
  est Foundry (briefing réel SAN.PA en 5,6 s, trace à une seule génération) ; « trois fournisseurs opérationnels »
  serait faux. Comparaison mesurée : `../C7/preuve-benchmark-2026-10-03.md` §9.
- Le coût affiché par Langfuse vaut 0 pour ce modèle (nom au format OpenRouter absent de la grille de prix) :
  la métrique existe, elle est fausse ; correction dans l'interface ou dans le code, pas faite au 03/10.
- Quinze traces factices (suite de tests, incident INC-006) polluent encore les métriques agrégées jusqu'à leur
  suppression, à faire par moi en tant que propriétaire du compte.
- Le guide d'exploitation a été corrigé le 03/10 : sa table des clés disait d'OpenRouter « 2ᵉ fournisseur » alors
  que le code le place troisième ; les trois fournisseurs y sont maintenant dans l'ordre réel de `LLM_ORDRE`.
- La remise aux parties prenantes n'est pas prouvée (C8.5, carte #43) : le guide existe, il n'a été envoyé à
  personne. La preuve attendue est un envoi daté au formateur (message ou mail) et sa réponse, rangés ici sous
  `envoi-<date>-formateur.*`. Un fichier dans le dépôt n'est pas une remise.

## Les 5 critères, et où ils en sont au 03/10/2026

| Critère | État | Preuve ou manque |
|---|---|---|
| C8.1 Service accessible, authentification en place | ✅ | appel réel du 03/10, clé en variable d'environnement, 403 sans clé côté RITA |
| C8.2 Configuration conforme aux besoins | 🟠 | briefings servis par Foundry et par OpenRouter ; un fournisseur sur trois sans clé, à dire ; `memory_audit` et inventaire #68 en cours côté RGPD |
| C8.3 Monitorage disponible opérationnel | 🟠 | trace complète et tableau ; coût faux, traces factices, alertes non réglées |
| C8.4 Documentation d'accès, d'installation, de tests, de dépendances, de flux | ✅ | `docs/EXPLOITATION.md`, ordre des fournisseurs corrigé le 03/10 |
| C8.5 Documentation communiquée, format accessible | 🔴 | aucune remise prouvée (#43) ; Markdown lisible, PDF du rapport E2 à produire |

## Ce que ce dossier n'est pas

Le brouillon de rapport E2 de juillet 2026 (dans le coffre Obsidian, hors dépôt) décrivait un autre montage
(Anthropic plus un modèle local sur Mac, LangSmith, journaux JSON, alerte de coût par courriel). Rien de cela n'est
dans le code d'aujourd'hui ; ce dossier décrit le montage réel, et le rapport E2 partira de lui.

## Glossaire

| Terme | En clair |
|---|---|
| **Cascade de fournisseurs** | si le premier service échoue, le suivant est essayé ; la trace dit lequel a répondu |
| **Remise (handover)** | donner la documentation à quelqu'un qui peut faire tourner le service sans vous, et en garder la preuve |
| **Monitorage du service** | voir chaque appel : durée, jetons, fournisseur, erreur ; ici Langfuse Cloud, région UE |
