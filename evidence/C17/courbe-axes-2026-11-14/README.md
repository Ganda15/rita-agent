# Courbe du cours avec ses axes, en production (14/11/2026)

Ma capture de l'écran Briefing de production pour MC.PA, fichier du 14/11/2026, séance du 13/11. Elle montre la
correction d'un manque relevé à l'oral blanc du 13/11 : la courbe du cours n'avait ni axe ni échelle. Corrigé dans la
PR #244, tests d'abord (`tests/test_graphiques_ui.py`), livré en production le 14/11.

**Ce que la capture montre** : les dates en abscisse (17/05/2026 au 13/11/2026) ; l'échelle des prix en ordonnée, de
350 à 550, à pas régulier ; la légende Cours, MM20 et MM50 ; le résumé écrit sous la courbe. La devise, EUR, est écrite
dans la carte « Cours », pas sur l'axe.

**Limites** : la capture précède le retrait des marques Markdown du même jour (#263) : les astérisques autour de
« BFM Bourse » sont encore visibles dans le texte. Le modèle indiqué est Mistral (Azure : échec), l'état du 14/11
(`evidence/C21/INC-010-azure-repond-401.md`). L'image contient un identifiant de requête, aucune clé ni adresse de
courriel.

**Fichiers** : `briefing-MC-axes-2026-11-14.png`, la capture d'origine (SHA-256 `a57abef839eb7e310985ad8e8a4b4b6dd2a5d9e60fca99bda3b41640d00d5ad5`) ; la figure recadrée de
l'annexe A7 du rapport E4, `docs/rapports/E4/schemas/E4-A7-axes-2026-11-14-recadree.png`.
