# Preuve C8 et C4 : le premier fournisseur du modèle traite en zone UE (9 octobre 2026)

## Pourquoi

Règle du projet posée par Era le 05/10/2026 : aucune donnée personnelle hors de l'Union européenne (registre RGPD, § 0).
Le prompt d'un briefing ne contient ni position ni prix de revient, mais la valeur demandée et l'heure de la demande disent
ce qui intéresse l'unique utilisateur (registre, T6). Jusqu'au 09/10, le déploiement Azure était en **Global Standard**,
qui peut traiter un appel dans n'importe quelle région (`evidence/C7/prix-et-environnement-2026-10-03.md`).

## Ce qu'Era a fait dans le portail Microsoft Foundry (09/10/2026)

Relevé par Era dans le portail :

| Élément | Valeur |
|---|---|
| Nom du déploiement | `gpt-5.4-dzs-eu` |
| Type | `DataZoneStandard`, zone `EUR` |
| Modèle | `gpt-5.4` (le même qu'avant) |
| Capacité | 150 000 jetons par minute |
| État | `Succeeded`, en service ; test du portail : HTTP 200, réponse `RITA_EU_OK`, région Sweden Central |

Azure ne convertit pas un déploiement Global Standard en Data Zone Standard : l'ancien (`gpt-5.4-2`) est gardé pour le
retour arrière, le temps de la vérification. Un déploiement `gpt-5.4-3`, Global Standard, a été créé par erreur par une
action rapide du portail et n'est pas utilisé.

Puis, dans le fichier d'environnement du poste, Era a changé la ligne `AZURE_FOUNDRY_DEPLOYMENT` pour
`gpt-5.4-dzs-eu` (l'assistant ne touche jamais ce fichier). Aucun code de RITA n'a changé : `src/llm.py` lit le nom du
déploiement dans cette variable (ligne 39) et appelle `<adresse>/chat/completions` (lignes 58 à 60).

## La vérification, par le code de RITA lui-même

Le 09/10/2026 à 22:54, trois appels réels par `src/llm._appel_foundry`, avec un prompt de quelques mots ; la configuration
est chargée comme au démarrage de l'API, aucune clé n'est affichée.

```
deploiement configure : gpt-5.4-dzs-eu
ordre des fournisseurs : ['foundry', 'anthropic', 'openrouter']
appel 1 : HTTP 200 | modele=gpt-5.4-2026-03-05 | x-ms-region=Sweden Central | texte='RITA_EU_OK'
appel 2 : HTTP 200 | modele=gpt-5.4-2026-03-05 | x-ms-region=Sweden Central | texte='RITA_EU_OK'
appel 3 : HTTP 200 | modele=gpt-5.4-2026-03-05 | x-ms-region=Sweden Central | texte='RITA_EU_OK'
```

L'en-tête `x-ms-region` est celui qu'Azure renvoie à chaque réponse ; RITA l'enregistre dans chaque trace
(`src/llm.py:81`). Trois appels ne prouvent pas tous les appels à venir : c'est le type de déploiement (Data Zone EU) qui
le garantit, et la région enregistrée dans les traces permet de le contrôler dans la durée.

## Ce qui reste, dit franchement

- **T6 n'est pas encore conforme à la règle UE seule** : si Azure échoue, la cascade bascule vers Anthropic, puis
  OpenRouter, sans garantie de région (`LLM_ORDRE=foundry,anthropic,openrouter`). Les retirer change la chaîne que
  décrivent E1 et E3 : après le gel, carte #82. C8.2 reste donc partiel.
- Microsoft reste une société américaine ; son contrat de traitement n'est pas relu en détail (registre, § 5, point 6).
- Après le gel : la valeur par défaut `gpt-5.4` de `src/llm.py:39` et le commentaire « Global Standard » de la ligne 79.
- Dans le portail, par Era : supprimer `gpt-5.4-3`, puis `gpt-5.4-2` une fois ce changement poussé, pour qu'aucun
  déploiement capable de traiter hors de l'UE ne reste appelable avec la clé.
