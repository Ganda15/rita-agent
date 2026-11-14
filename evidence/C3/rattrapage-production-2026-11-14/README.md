# Rattrapage des cours de production au 13/11/2026 (samedi 14/11)

**Pourquoi** : la production n'avait les cours que jusqu'au 12/11 (rattrapage du jeudi soir) ; aucune collecte des cours
n'est planifiée sur le serveur (`docs/exploitation.md`, « Rattraper les cours et les taux en production, à la main »).
Le samedi, toutes les places sont fermées : la séance du vendredi 13/11 est définitive, la règle « après 22 h 05 » est
tenue.

**Comment** : par Era, dans la session du serveur, avec le guide corrigé le 13/11 (#245). Sortie complète :
[`sortie-serveur-2026-11-14.txt`](sortie-serveur-2026-11-14.txt), sans bannière de connexion ni adresse IP.

| Contrôle | Résultat |
|---|---|
| Étape 4 (ce qui est gardé) | `reseau=rita-agent_default`, `mot_de_passe=present` : la garde du 13/11 n'avait rien à arrêter |
| Passage à blanc | 217 cotations lues, 0 écrite ; 2 étapes sur 2 |
| Passage réel | 217 cotations écrites, 0 rejetée (séances du 11/11 au 13/11) ; 10 lignes de taux écrites |
| Dernière séance en base | **13/11/2026**, 281 923 cotations |
| Statistiques du planificateur | `ANALYZE cotation; ANALYZE taux_change;` |

**Image utilisée** : celle de l'API en service, livrée le 14/11 (`main` à `2dd385f`, empreinte `sha256:23a187a2…`).

**Limite** : les taux écrits (10) dépassent les taux lus (8) ; le comportement de l'étape `ecb` n'a pas été relu ce
jour-là pour l'expliquer. Les cours, eux, sont exacts : lus = écrits, aucun rejet.
