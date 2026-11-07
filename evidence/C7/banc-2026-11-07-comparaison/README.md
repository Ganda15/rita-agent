# Banc C7 du 07/11/2026 : Azure contre Mistral, même jeu, même budget

Compétences : C7 (choix du service), C8 (contrainte UE). Demande d'Era du 07/11 (« A + B »). Le banc du 03/10 comparait
Azure (*Global Standard*, ancien prompt) à Claude par OpenRouter ; Mistral n'avait servi qu'un briefing par modèle, le
10/10, sur la branche `mistral-ue` (PR #88, non fusionnée).

## Les deux passages

Le même jeu figé (`evidence/C7/jeu-d-essai-2026-10-03.json`, 10 cas, 3 répétitions), le même prompt que le rédacteur
(celui du 06/11), le même budget de 500 jetons, le même plafond de 5 USD :

| | Azure | Mistral |
|---|---|---|
| Commande | `--fournisseurs foundry --sortie evidence/C7/banc-2026-11-07` | `MISTRAL_MODEL=mistral-large-2512`, `--fournisseurs mistral --sortie evidence/C7/banc-2026-11-07-mistral-large-3` |
| Lancé le 07/11 (UTC) | 09:24:46 à 09:25:58 | 09:32:35 à 09:34:04 |
| Modèle rendu, origine | `gpt-5.4-2026-03-05`, Sweden Central (déploiement `gpt-5.4-dzs-eu`, zone UE) | `mistral-large-2512` (Large 3), `api.eu.mistral.ai` |

Aucune donnée personnelle dans le jeu : des cours et des passages d'articles publics. Mistral n'est pas dans la cascade
de l'application : la fonction d'appel ajoutée le 07/11 (`src/llm.py`, `_appel_mistral`) ne sert qu'au banc ; la
production reste sur Azure seul tant que le contrat de Mistral n'est pas lu (règle UE, registre § 0).

## Pourquoi Large 3 et pas Large 4

Mesuré le 07/11 sur un cas réel du jeu (MC.PA), avant le passage :

| Réglage | Résultat |
|---|---|
| Large 4, `reasoning_effort: "none"` (le réglage du 10/10) | **400** : « reasoning_effort none is not supported for this model », valeurs acceptées low, medium, high ; Mistral a changé son API depuis le 10/10. Passage refusé dès la sonde : `../banc-2026-11-07-mistral-large-4-refuse/` |
| Large 4, `low`, 500 jetons | 200, mais 499 jetons de réflexion sur 500 : **aucun texte** |
| Large 4, `low`, 2 000 jetons | texte rendu, 10,0 s, 1 249 jetons dont 1 150 de réflexion |
| Large 3 (`mistral-large-2512`), sans réflexion, 500 jetons | texte rendu, 3,8 s, 283 jetons |

Choix d'Era du 07/11 : Large 3, au même budget qu'Azure.

## Les résultats

Résumés : [`../banc-2026-11-07/resume-2026-11-07.json`](../banc-2026-11-07/resume-2026-11-07.json),
[`../banc-2026-11-07-mistral-large-3/resume-2026-11-07.json`](../banc-2026-11-07-mistral-large-3/resume-2026-11-07.json).

| Mesure | Azure `gpt-5.4`, zone UE | Mistral Large 3, UE |
|---|---|---|
| Disponibilité | 30 sur 30 | 30 sur 30 |
| Acceptés par le garde-fou de sortie (AMF) | 30 sur 30 | 30 sur 30 |
| Fidèles aux faits fournis (contrôle minimal du script) | 30 sur 30 | 30 sur 30 |
| Latence, médiane et 95e centile | **2,19 s et 2,55 s** | 2,80 s et 3,68 s |
| Longueur moyenne | 569 caractères | 685 caractères |
| Textes contenant du Markdown (`**`) | 0 sur 30 | **30 sur 30** |
| Jetons pour 30 briefings, entrée et sortie | 21 534 et 5 243 | 23 334 et 6 579 |
| Coût d'un briefing au prix public | 0,0044 USD (2,50 et 15,00 USD par million, prix du 03/10) | **0,00072 USD** (0,5 et 1,5 USD par million, prix Mistral lu le 10/10) |
| Français, noté par Era à l'aveugle (0, 1 ou 2) | à compléter | à compléter |

Le Markdown compte : l'interface affiche le texte tel quel (`textContent`), donc des astérisques visibles, le défaut
déjà relevé sur l'écran Briefing (rapport E4, annexe A7). Avec Mistral en production, il faudrait le retirer ou le
demander autrement.

## La notation du français

[`notes-francais-2026-11-07.csv`](notes-francais-2026-11-07.csv) : les 60 textes mélangés (graine fixée), sans le nom du
fournisseur, `**` retirés pour ne pas désigner Mistral. La clé est à part :
[`notes-francais-2026-11-07-cle.csv`](notes-francais-2026-11-07-cle.csv). Script :
[`preparer_notation_aveugle.py`](preparer_notation_aveugle.py).

**Limite écrite** : la forme trahit en partie l'auteur (Mistral ouvre par une ligne de titre, Azure par la date).

## Ce que ce banc ne prouve pas

- Un passage chacun, un samedi matin : la latence d'un autre jour peut être différente.
- Le prix de la zone de données UE d'Azure n'est pas relevé ; celui de Mistral date du 10/10.
- La route `/question` n'est pas comparée entre fournisseurs (limite gardée, choix d'Era du 07/11).
