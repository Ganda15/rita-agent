# Aucune marque Markdown visible sur les 2 briefings contrôlés en production (14/11/2026)

## Le défaut

Depuis le 14/11, Mistral rédige les briefings quand Azure refuse sa clé (`evidence/C21/INC-010-azure-repond-401.md`).
L'écran affiche le texte tel quel (`textContent`). Deux cas vus en production sur MC.PA, version `9d48870` :

- « Selon \*BFM Bourse\* (13/10/2026) » (une source en italique) ;
- « \*Source : Données de marché au 13/11/2026 (BFM Bourse, 13/10/2026, sur la persistance des pressions chinoises).\* »
  (toute une ligne en italique).

Au banc C7 du 07/11, 30 briefings de Mistral sur 30 contenaient `**` (`evidence/C7/banc-2026-11-07-comparaison/`).

## La correction

PR #263, tests d'abord (`tests/test_mise_en_forme.py`, les deux cas ci-dessus compris) : `agents/mise_en_forme.py`
retire les seules marques d'emphase appariées et un `#` de titre en début de ligne, avant le garde-fou de sortie.
Livrée par #264 : exécution « Livraison » 43629837361, bascule terminée le 14/11 à 19 h 15 UTC ; à 19 h 21 UTC,
`/health` annonce `"commit":"dc9e072"`, construit à 19 h 08 UTC.

## La vérification en production

Briefings demandés à l'écran entre 19 h 21 UTC (vérification de `/health` sur `dc9e072`) et 19 h 25 UTC (envoi des
captures), donc sur `dc9e072` ; références de requête à retrouver dans Langfuse :

| Valeur | Référence de la requête | Marques Markdown | Chiffres du texte et des cartes | Modèle |
|---|---|---|---|---|
| OR.PA | `cc49ef6fc80f4a0d9504a666c4efe5c0` | aucune | identiques (451,20 € ; +0,97 % ; +16,54 %) | Mistral, `mistral-large-2512`, après un échec d'Azure |
| AIR.PA | `8123f1a8fa9b4d349345d4336c2a8546` | aucune | identiques (206,65 € ; −0,77 % ; +10,80 %) | Mistral, `mistral-large-2512`, après un échec d'Azure |

Le texte d'AIR.PA finit par « Source : données de séance collectées le 13/11/2026. », sans astérisque : la même forme de
ligne qui sortait en italique avant la correction.

## Limites

- Un troisième briefing, MC.PA (`a11ae2ccc3e34a29b6cabff5da924188`), ne compte pas : il a été demandé au plus tard à
  19 h 14 UTC (heure de sa capture), avant la bascule, donc sur `9d48870`. Il ne montrait pas d'astérisque, par hasard.
- Mistral n'écrit pas des marques à chaque fois : deux briefings sans astérisque sur la nouvelle version ne prouvent pas,
  seuls, que la correction retire une marque écrite. Ce qui le prouve, ce sont les tests (les deux phrases vues en
  production y sont), joués à chaque PR.
- Les captures d'écran de ces deux briefings ont été regardées le 14/11 ; elles ne sont pas encore dans ce dossier.
  Tant qu'elles n'y sont pas, la preuve visible tient aux références de requête, dont la consultation dans Langfuse
  demande un accès privé.
- Des chiffres conformes aux cartes ne prouvent pas l'exactitude de tout le texte : ce contrôle porte sur l'affichage,
  pas sur la qualité de la rédaction (mesurée ailleurs : banc C7 du 07/11, `evidence/C7/banc-2026-11-07-comparaison/`).
- L'écran Question n'est pas concerné par cette correction (aucune marque observée le 14/11).
