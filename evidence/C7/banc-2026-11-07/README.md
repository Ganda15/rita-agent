# Banc C7 du 07/11/2026 : Azure tel qu'il tourne aujourd'hui (zone UE, prompt corrigé)

Compétence : C7 (choix du service de modèle). Demande d'Era du 07/11, pendant le double contrôle : le banc du 03/10
mesurait Azure en déploiement *Global Standard* avec l'ancien prompt ; ni le déploiement en zone de données UE, ni le
prompt corrigé le 06/11 (`548f1f5`) n'avaient été mesurés (rapport E2, 3.3).

## La commande

```
C:\Python314\python.exe -X utf8 -m evals.benchmark_fournisseurs --jeu evidence/C7/jeu-d-essai-2026-10-03.json --repetitions 3 --plafond 5 --fournisseurs foundry --sortie evidence/C7/banc-2026-11-07
```

- Le même jeu figé que le 03/10 : 10 cas, 3 répétitions, 30 appels. Le même prompt que le rédacteur
  (`agents.analyst.construire_prompt`, celui du 06/11).
- Déploiement appelé : `gpt-5.4-dzs-eu`, lu dans la configuration du poste, le même que la production. Modèle rendu :
  `gpt-5.4-2026-03-05`. Origine déclarée par la réponse, pour les 30 appels : *Sweden Central*.
- Lancé le 07/11/2026 de 09:24:46 à 09:25:58 UTC. Aucune donnée personnelle dans le jeu : des cours et des passages
  d'articles publics.

## Les résultats ([`resume-2026-11-07.json`](resume-2026-11-07.json), lignes brutes : [`resultats-2026-11-07.jsonl`](resultats-2026-11-07.jsonl))

| Mesure | 03/10 (Global Standard, ancien prompt) | 07/11 (zone UE, prompt corrigé) |
|---|---|---|
| Disponibilité | 30 sur 30 | 30 sur 30, intervalle de Wilson [0,89 ; 1,00] |
| Textes acceptés par le garde-fou de sortie (AMF) | 30 sur 30 | 30 sur 30 |
| Fidélité aux faits fournis (contrôle minimal du script) | voir `preuve-benchmark-2026-10-03.md` | 30 sur 30 |
| Latence, médiane | 3,21 s | **2,19 s** |
| Latence, 95e centile | 10,69 s (2 appels sur 30 au-dessus de 10 s) | **2,55 s** |
| Jetons par briefing, entrée et sortie (moyenne) | 644 et 204 | 718 et 175 |
| Coût d'un briefing au prix public *Global Standard* (2,50 et 15,00 USD par million) | 0,0047 USD | 0,0044 USD (calcul : 21 534 jetons d'entrée et 5 243 de sortie pour 30 appels) |

Le script affiche un coût de 0 USD : il ne connaît que le prix d'OpenRouter ; son plafond (`--plafond 5`) n'a donc
pas pu jouer pour Azure. Le coût ci-dessus est calculé à la main,
au prix public du 03/10 (`prix-et-environnement-2026-10-03.md`). Le prix de la zone de données UE n'est pas relevé dans
les preuves : le chiffre exact pour ce déploiement n'est pas établi.

## Ce que ce banc ne mesure pas

- Seul, ce passage dit comment Azure se comporte aujourd'hui ; la comparaison avec Mistral Large 3, même jeu et même
  budget, est dans `../banc-2026-11-07-comparaison/`.
- Le français : noté par Era à l'aveugle, avec les 30 textes de Mistral Large 3 (`../banc-2026-11-07-comparaison/`).
- Un seul passage, un samedi matin : la latence d'un autre jour ou d'une démonstration chargée peut être différente.
