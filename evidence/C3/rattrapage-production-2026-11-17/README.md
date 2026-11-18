# Rattrapage des cours de production au 17/11/2026 (mardi 17/11, 22 h 12 à Paris)

**Pourquoi** : la production n'avait les cours que jusqu'au 13/11 (rattrapage du samedi 14/11). Aucune collecte des
cours n'est planifiée sur le serveur ; depuis la décision du 17/11, ils sont rattrapés à la main jusqu'au jury
(`docs/exploitation.md`, « Rattraper les cours et les taux en production, à la main »). Lancé à 22 h 12, heure de
Paris : New York est fermé depuis 22 h, la règle « après 22 h 05 » est tenue.

**Comment** : à la main, dans la session du serveur, en suivant le guide étape par étape ; le passage à blanc et
l'étape 4 ont été relus avant le passage réel. Sortie complète :
[`sortie-serveur-2026-11-17.txt`](sortie-serveur-2026-11-17.txt), sans bannière de connexion ni adresse IP de connexion.

| Contrôle | Résultat |
|---|---|
| Étape 4 (ce qui est gardé) | `reseau=rita-agent_default`, adresse au nom de `rita`, `mot_de_passe=present` |
| Étape 5, avant | dernière séance **13/11/2026**, 281 923 cotations |
| Passage à blanc (étape 6) | 323 cotations lues, 0 écrite ; 12 taux lus, 0 écrit ; 2 étapes sur 2 ; `manifeste-2026-11-17-211252.json` |
| Passage réel (étape 7) | 323 cotations écrites, 0 rejetée (séances du 13/11 au 17/11) ; 12 taux lus, 15 écrits ; 2 étapes sur 2 ; `manifeste-2026-11-17-211347.json` |
| Étape 8, après | dernière séance **17/11/2026**, 282 138 cotations (**+215**) ; CHF, EUR, GBP, JPY et USD au 17/11 |
| Séances, une par une | 13/11 : 108 valeurs ; 16/11 : 108 ; 17/11 : 107 |
| Statistiques du planificateur | `ANALYZE cotation; ANALYZE taux_change;` |
| Variables de la session | effacées (`unset`), mot de passe compris |
| Écran Indicateurs de la production | « Carte des performances : cours du 17/11/2026 » ; 108 valeurs, 3 cotations périmées masquées (les trois valeurs radiées en 2018 et 2019) ; capture `capture-indicateurs-2026-11-17.webp` |

**Le compte, mesuré** : 108 + 108 + 107 = 323, exactement les cotations écrites. Les lignes du 13/11 existaient déjà et
ont été réécrites sur place (clé `ticker, date_seance`) ; les nouvelles sont celles du 16/11 et du 17/11,
108 + 107 = 215, exactement l'écart du total. Aucun doublon. Taux : 4 devises × 3 jours publiés par la BCE (13, 16 et
17/11) = 12 lus, plus une ligne EUR = 1 par jour, soit 15 écrits (guide, « Compter les taux »).

**Image utilisée** : celle de l'API en service, livrée le 17/11 (`main` à `ceab6f3`, lu sur `/health` à 21 h 17 UTC ;
empreinte `sha256:62c42606…`).

## CRI.PA, sans cotation du 17/11

La seule valeur absente du 17/11 est CRI.PA (requête `EXCEPT` entre le 16/11 et le 17/11, dans la sortie). C'est le
même retard du fournisseur qu'au 03/11 et au 11/11 : sa séance du jour n'arrive pas le soir même. Rien n'est perdu :
chaque valeur repart de sa dernière séance en base, donc le prochain rattrapage reprendra CRI.PA au 16/11 et écrira
le 17/11 s'il existe.

## Limites

- Tant que CRI.PA n'a pas son 17/11, la carte « Fraîcheur des cours » du tableau de bord, qui prend la pire valeur,
  passera à l'orange le 18/11 au matin ; la date la plus récente affichée reste le 17/11.
- La ligne `INFO Failed to create TzCache` de yfinance au passage réel : le cache des fuseaux horaires n'est pas créé
  dans le conteneur jetable. Sans effet sur les données ; elle figurait déjà les 04, 08, 11 et 14/11.
- Les volumes de FTI et SLB lus peu après 22 h ne sont pas toujours définitifs ; le rattrapage suivant les réécrit sur
  la même ligne.
- Aucune collecte des cours n'est planifiée sur le serveur : le prochain rattrapage est encore à la main.
