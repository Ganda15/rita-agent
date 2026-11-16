# Aucune marque Markdown visible sur les 3 briefings contrôlés en production (14/11/2026)

## Le défaut

Depuis le 14/11, Mistral rédige les briefings quand Azure refuse sa clé (`evidence/C21/INC-010-azure-repond-401.md`).
L'écran affiche le texte tel quel (`textContent`). Deux cas vus en production sur MC.PA, version `9d48870` ; sur les deux
captures, les astérisques se voient à l'écran :

| Cas | Capture (heure UTC) | Référence de la requête |
|---|---|---|
| « Selon \*BFM Bourse\* (13/10/2026) » (une source en italique) | [`briefing-MC.PA-avant-1-2026-11-14.png`](briefing-MC.PA-avant-1-2026-11-14.png), 17 h 59 | `2e1360c682734b40977541cbe0e1bf9e` |
| « \*Source : Données de marché au 13/11/2026 (BFM Bourse, 13/10/2026, sur la persistance des pressions chinoises).\* » (toute une ligne en italique) | [`briefing-MC.PA-avant-2-2026-11-14.png`](briefing-MC.PA-avant-2-2026-11-14.png), 18 h 53 | `4beb33056f514c48b8befc5077fe8514` |

Au banc C7 du 07/11, 30 briefings de Mistral sur 30 contenaient `**` (`evidence/C7/banc-2026-11-07-comparaison/`).

## La correction

PR #263, tests d'abord (`tests/test_mise_en_forme.py`, les deux cas ci-dessus compris) : `agents/mise_en_forme.py`
retire les seules marques d'emphase appariées et un `#` de titre en début de ligne, avant le garde-fou de sortie.
Livrée par #264 : exécution « Livraison » 43629837361, bascule terminée le 14/11 à 19 h 15 UTC ; à 19 h 21 UTC,
`/health` annonce `"commit":"dc9e072"`, construit à 19 h 08 UTC.

## La vérification en production

Après l'annonce de `dc9e072` par `/health` à 19 h 21 UTC, trois briefings sont demandés à l'écran, dans cet ordre :
MC.PA, OR.PA, AIR.PA. Leurs captures sont prises à 19 h 22, 19 h 23 et 19 h 24 UTC, donc sur `dc9e072`. Références de
requête à retrouver dans Langfuse :

| Valeur | Capture (heure UTC) | Référence de la requête | Marques Markdown | Chiffres du texte et des cartes | Modèle |
|---|---|---|---|---|---|
| MC.PA | [`briefing-MC.PA-2026-11-14.png`](briefing-MC.PA-2026-11-14.png), 19 h 22 | `a50b630d08e341e6bbf76b721cfabe07` | aucune | identiques (403,45 € ; −0,31 % ; +5,05 %) | Mistral, `mistral-large-2512`, après un échec d'Azure |
| OR.PA | [`briefing-OR.PA-2026-11-14.png`](briefing-OR.PA-2026-11-14.png), 19 h 23 | `cc49ef6fc80f4a0d9504a666c4efe5c0` | aucune | identiques (451,20 € ; +0,97 % ; +16,54 %) | Mistral, `mistral-large-2512`, après un échec d'Azure |
| AIR.PA | [`briefing-AIR.PA-2026-11-14.png`](briefing-AIR.PA-2026-11-14.png), 19 h 24 | `8123f1a8fa9b4d349345d4336c2a8546` | aucune | identiques (206,65 € ; −0,77 % ; +10,80 %) | Mistral, `mistral-large-2512`, après un échec d'Azure |

Le texte de MC.PA contient « Selon BFM Bourse (13/10/2026) », sans astérisque : la phrase du premier cas. Celui d'AIR.PA
finit par « Source : données de séance collectées le 13/11/2026. », sans astérisque : la même forme de ligne que le
second cas.

### D'où viennent les captures

Captures d'écran prises sur le poste le 14/11, versées ici le 15/11 sans retouche : leurs empreintes SHA-256 sont celles
des fichiers d'origine. L'heure UTC est celle du fichier d'origine, nommé à l'heure de Paris (UTC+1) :
`Capture d'écran 2026-11-14 185930.png` (avant 1), `195303` (avant 2), `202233` (MC.PA), `202322` (OR.PA), `202408`
(AIR.PA).

Le 14/11, la capture de MC.PA transmise pour le contrôle était, par erreur, celle de 19 h 09 (`a11ae2cc…`, ancienne
version) : ce dossier ne comptait alors que deux briefings. La capture de 19 h 22 (`a50b630d…`) a été retrouvée le 15/11
parmi les captures du poste.

## Limites

- Un autre briefing, MC.PA (`a11ae2ccc3e34a29b6cabff5da924188`), ne compte pas : capturé à 19 h 09 UTC, il a été demandé
  avant la bascule de 19 h 15, donc sur `9d48870`. Il ne montrait pas d'astérisque, par hasard. (Le 14/11, cette ligne
  donnait 19 h 14 : l'heure à laquelle la capture a été transmise, pas celle de la capture.)
- L'heure d'une requête n'est pas écrite sur sa capture. Que les trois briefings aient été demandés après 19 h 21 repose
  sur l'ordre des faits : annonce de `dc9e072` par `/health`, demande des trois briefings, captures entre 19 h 22 et
  19 h 24. Langfuse date chaque requête et peut le confirmer, mais sa consultation demande un accès privé.
- Mistral n'écrit pas des marques à chaque fois : trois briefings sans astérisque sur la nouvelle version ne prouvent pas,
  seuls, que la correction retire une marque écrite. Le texte brut du modèle ne peut pas être relu dans Langfuse, qui ne
  garde aucun texte (décision D9, `src/traces.py`). Ce qui le prouve, ce sont les tests (les deux phrases vues en
  production y sont), joués à chaque PR.
- Des chiffres conformes aux cartes ne prouvent pas l'exactitude de tout le texte : ce contrôle porte sur l'affichage,
  pas sur la qualité de la rédaction (mesurée ailleurs : banc C7 du 07/11, `evidence/C7/banc-2026-11-07-comparaison/`).
- L'écran Question n'est pas concerné par cette correction (aucune marque observée le 14/11).
