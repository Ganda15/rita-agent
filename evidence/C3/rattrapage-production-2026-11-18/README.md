# Rattrapage des cours de production au 18/11/2026 (mercredi 18/11, 22 h 14 à Paris)

**Pourquoi** : la production avait les cours jusqu'au 17/11 (rattrapage du mardi 17/11). Aucune collecte des cours
n'est planifiée sur le serveur ; depuis la décision du 17/11, ils sont rattrapés à la main jusqu'au jury
(`docs/exploitation.md`, « Rattraper les cours et les taux en production, à la main »). Passage à blanc à 21 h 14 UTC,
soit 22 h 14 à Paris : New York est fermé depuis 22 h, la règle « après 22 h 05 » est tenue.

**Comment** : à la main, dans la session du serveur, en suivant le guide étape par étape ; l'étape 4 et le passage à
blanc ont été relus avant le passage réel. Sortie complète :
[`sortie-serveur-2026-11-18.txt`](sortie-serveur-2026-11-18.txt), remise bout à bout depuis les copies successives,
sans bannière de connexion ni adresse IP de connexion.

| Contrôle | Résultat |
|---|---|
| Étape 4 (ce qui est gardé) | `reseau=rita-agent_default`, adresse au nom de `rita`, `mot_de_passe=present` |
| Étape 5, avant | dernière séance **17/11/2026**, 282 138 cotations |
| Passage à blanc (étape 6) | 216 cotations lues, 0 écrite ; 8 taux lus, 0 écrit ; 2 étapes sur 2 ; `manifeste-2026-11-18-211443.json` |
| Passage réel (étape 7) | 216 cotations écrites, 0 rejetée (séances du 16/11 au 18/11) ; 8 taux lus, 10 écrits ; 2 étapes sur 2 ; `manifeste-2026-11-18-211550.json` |
| Étape 8, après | dernière séance **18/11/2026**, 282 246 cotations (**+108**) ; CHF, EUR, GBP, JPY et USD au 18/11 |
| Séances, une par une | 16/11 : 108 valeurs ; 17/11 : 108 ; 18/11 : 107 |
| Statistiques du planificateur | `ANALYZE cotation; ANALYZE taux_change;` |
| Variables de la session | effacées (`unset`), mot de passe compris |

**Le compte, mesuré** : 107 valeurs repartent de leur séance du 17/11 (17 et 18/11, soit 214 lignes) et CRI.PA de la
sienne, le 16/11 (16 et 17/11, soit 2 lignes) : 216, exactement les cotations écrites. Les lignes du 17/11 des 107
valeurs et celle du 16/11 de CRI.PA existaient déjà et ont été réécrites sur place (clé `ticker, date_seance`) ; les
nouvelles sont les 107 du 18/11 et celle du 17/11 de CRI.PA, 107 + 1 = 108, exactement l'écart du total. Aucun
doublon. Taux : 4 devises × 2 jours publiés par la BCE (17 et 18/11) = 8 lus, plus une ligne EUR = 1 par jour, soit
10 écrits (guide, « Compter les taux »).

**Image utilisée** : celle de l'API en service, `ghcr.io/ganda15/rita-api@sha256:761e9532…` (étape 4). `/health`, lu à
21 h 21 UTC : `main` à `16567ec`, construit le 18/11 à 10 h 33 UTC.

## CRI.PA : son 17/11 rattrapé, sans son 18/11

Le 17/11, CRI.PA était la seule valeur sans sa séance du jour. Elle l'a maintenant (clôture 7,37, requête dans la
sortie). Ce soir, c'est encore la seule valeur absente du 18/11 (requête `EXCEPT` entre le 17/11 et le 18/11) : même
retard du fournisseur qu'au 03/11, au 11/11 et au 17/11. Rien n'est perdu : le prochain rattrapage reprendra CRI.PA au
17/11 et écrira le 18/11 s'il existe.

## Une erreur de manipulation, sans effet

Après le passage réel, la sortie de l'étape 7 a été recollée par erreur dans le terminal. Le shell a lu ces lignes
comme des commandes : la première commençait par le texte de l'invite (`root@…#`), donc `docker run` n'a pas été
relancé (« No such file or directory ») ; l'apostrophe de « D'AGREGATION » a ouvert une chaîne jamais fermée, et la
commande tapée ensuite est restée dans cette chaîne sans s'exécuter. Ctrl+C a rendu l'invite ; l'étape 8 a été faite
ensuite. Le total de l'étape 8 (+108, exactement le compte attendu) confirme qu'aucune écriture de plus n'a eu lieu.
Les lignes sont gardées telles qu'affichées dans la sortie, avec une note entre crochets.

## Limites

- Tant que CRI.PA n'a pas son 18/11, la carte « Fraîcheur des cours » du tableau de bord, qui prend la pire valeur,
  passera à l'orange le 19/11 au matin ; la date la plus récente affichée reste le 18/11.
- Pas de capture de l'écran Indicateurs de la production ce soir, contrairement au 17/11 : la preuve tient aux
  requêtes de la sortie.
- La ligne `INFO Failed to create TzCache` de yfinance : le cache des fuseaux horaires n'est pas créé dans le
  conteneur jetable. Sans effet sur les données ; elle figurait déjà les 04, 08, 11, 14 et 17/11.
- Les volumes de FTI et SLB lus peu après 22 h ne sont pas toujours définitifs ; le rattrapage suivant les réécrit sur
  la même ligne.
- Aucune collecte des cours n'est planifiée sur le serveur : le prochain rattrapage est encore à la main.
