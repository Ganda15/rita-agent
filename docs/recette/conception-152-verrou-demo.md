# #152 : verrou de démonstration de la passerelle MCP (01/11/2026)

> **État.** Orientation validée par la revue du 01/11 au soir, complétée par une seconde revue (contenu des champs,
> fichier fictif imposé au test) ; correctif écrit et testé **en local, non commité**. Rien n'est en production.
> Preuves avant et après : `evidence/C17/correctifs-2026-11-01/`, fichiers `152-verrou-demo-*` puis
> `152-contenu-des-champs-*`.

## Le problème

En démonstration, `rita_portefeuille` doit servir le jeu d'exemple du dépôt et rien d'autre. Le verrou d'avant
(`passerelle_mcp/serveur.py`) comparait des **ensembles** de couples (ticker, quantité) aux dix lignes de
`data/positions-exemple.csv`. Trois défauts :

1. il refusait le jeu d'exemple **importé** : l'import en garde sept lignes, pas dix ;
2. il acceptait les mêmes tickers et quantités avec **d'autres prix de revient** (test rouge du 01/11, dans le dossier
   de preuves) ;
3. un ensemble absorbe une **ligne en double**.

Le test rouge montre qu'un jeu synthétique non conforme passait le verrou. Il ne montre pas qu'un portefeuille personnel
réel a été divulgué.

Les défauts 1 et 3 étaient déjà décrits le 10/10 dans `evidence/C20/erratum-verrou-demonstration-2026-10-10.md`, qui
proposait de faire refaire à la passerelle le filtrage par l'univers et la résolution des alias de l'import. La solution
retenue le 01/11 diffère sur ce point : la passerelle ne lit ni l'univers ni les alias (elle passe par HTTP) ; elle
compare à un jeu versionné, et c'est un test du vrai import qui garantit que ce jeu est bien le résultat de l'import.

## Ce que fait l'import, vérifié sur le dépôt

`db/importer.py`, `importer_positions` : le ticker du fichier est cherché dans `valeur` ; sinon le libellé est cherché
dans `alias_valeur` ; sinon la ligne est ignorée. Sur le fichier d'exemple et l'univers versionné
(`data/univers-155.csv`, 111 valeurs, 112 alias), vérifié le 01/11 :

| Lignes du fichier | Résultat de l'import |
|---|---|
| MC.PA, OR.PA, AI.PA, SAN.PA, BNP.PA, SU.PA, VIRI.PA | importées, **reconnues par leur ticker** |
| TTE.PA, AAPL, MSFT | ignorées : hors univers, aucun alias ne les rattrape |
| deux lignes corrompues (quantité nulle, prix absent) | écartées dès la lecture (`sources/positions.py`) |

Aucune des sept positions ne passe par un alias.

## La solution retenue

1. **Le jeu attendu est versionné** : `passerelle_mcp/jeu_demo_attendu.csv`, les sept positions écrites à l'échelle des
   colonnes SQL (`quantite NUMERIC(16,4)`, `pru NUMERIC(14,4)`). La correspondance avec l'import est **testée sur le vrai
   import** : `tests/test_jeu_demo_mcp_base.py` charge l'univers puis le fichier d'exemple par les fonctions de
   `db/importer.py`, sur la base de test, et compare les `NUMERIC` lus en base au fichier. Un test sans base
   (`tests/test_passerelle_mcp.py`) refait la même règle en miroir, pour que le contrôle tourne aussi dans le job
   `pytest`.
2. **La comparaison** porte sur quatre champs (ticker, quantité, prix de revient, devise) et compte les doublons
   (`collections.Counter`). Elle est décimale et sans arrondi : un nombre reçu est relu par `Decimal(str(x))`, la
   représentation la plus courte du flottant, celle-là même que le JSON a transportée. Une valeur de 15 chiffres
   significatifs au plus se relit exactement (tout prix de revient, toute quantité sous cent milliards) ; au-delà, la
   lecture peut s'écarter de la base, ce qui ne peut que faire refuser, les valeurs attendues étant petites. Une
   différence d'un cent-millième fait refuser (testé).
3. **La réponse transmise par MCP est reconstruite**, jamais la réponse brute de l'API :
   - enveloppe : `nb`, `total_eur`, `positions_sans_taux`, `positions` ;
   - par position, les treize champs de la requête R1, nommés un par un : `ticker`, `nom_officiel`, `statut_qualite`,
     `quantite`, `pru`, `devise`, `date_cours`, `cours`, `investi_eur`, `valorisation_eur`, `performance_pct`,
     `taux_pour_eur`, `taux_manquant`. Un champ ajouté demain à l'API ne sort pas par la passerelle sans être ajouté ici ;
   - `total_eur` est recalculé sur les positions vérifiées ; il vaut `null` dès qu'une ligne n'a pas de valorisation
     (même règle que l'API, plan 65 : un total partiel n'est pas un total) ;
   - `positions_sans_taux` est recompté sur les mêmes positions.
4. **Le contenu des champs est vérifié** (seconde revue du 01/11 au soir) : la première version contrôlait la présence
   des treize champs, pas leur contenu. Un objet à la place du cours ou du texte à la place de la valorisation sortaient
   tels quels, et une ligne pouvait annoncer un taux manquant avec une valorisation chiffrée. Désormais :
   - types : les quatre textes non vides, `quantite` et `pru` nombres, `taux_manquant` booléen, `date_cours` date
     `AAAA-MM-JJ` ou `null`, les cinq autres montants nombres ou `null` ;
   - cohérence, d'après la requête R1 : le cours et sa date vont ensemble ; sans cours, ni valorisation ni
     performance ; l'euro se convertit par 1 et n'a jamais de taux manquant ; un taux manquant rend les montants en
     euros `null`, et seulement lui.

   Une valeur légitimement indisponible reste `null` et la ligne est servie.
5. **Le doute vaut refus** (`NOT_AUTHORIZED`, aucune donnée dans le message) : jeu attendu absent, vide ou illisible ;
   réponse sans `positions`, sans `nb` ou sans `positions_closes` ; `nb` différent du nombre de lignes rendues ; un des
   treize champs absent, mal formé ou contradictoire ; une position en plus, en moins ou en double ; un champ comparé
   différent.
6. **`positions_closes` différent de 0 : refus**, en mode de démonstration strict. Une position close n'est pas
   forcément personnelle (elle peut être fictive), mais elle n'appartient pas au jeu attendu, et la passerelle ne peut
   pas savoir d'où elle vient.

## Ce qui a été écarté, et pourquoi

- **Une route d'API pour les alias** (proposée le 01/11 après-midi) : inutile pour le jeu actuel, aucune des sept
  positions n'en a besoin. Elle aurait changé le contrat de l'API et les nombres de routes cités dans les rapports. Si
  un jour le jeu d'exemple contient une ligne reconnue par alias, le test du vrai import échouera et la question se
  reposera.
- **Recalculer le jeu attendu à chaque appel** depuis le fichier d'exemple : il faudrait l'univers complet et les alias,
  que la passerelle ne lit pas (elle passe par HTTP, voir la docstring du module).

## Les tests

| Cas | Fichier | Attendu |
|---|---|---|
| le jeu importé, tel que l'API le rend | `tests/test_passerelle_mcp.py` | servi, 7 positions |
| le jeu attendu est le fichier d'exemple passé par les règles de l'import (sans base) | idem | égalité |
| prix de revient (dont un écart d'un cent-millième), quantité, devise modifiés | idem | refusé |
| une position en plus, en moins, en double | idem | refusé |
| `positions_closes` à 1, ou absent ; `nb` faux ; un champ indispensable absent | idem | refusé |
| jeu attendu absent ou vide | idem | refusé |
| champs en trop dans la réponse de l'API | idem | servi sans eux |
| total de l'API faux ; une ligne sans cotation (cours, date, valorisation, performance à `null`) | idem | total recalculé ; servi avec un total `null` |
| un objet à la place du cours ; du texte à la place de la valorisation ; un taux manquant avec une valorisation chiffrée | idem | refusé, rien du contenu ne sort |
| vrai import du fichier d'exemple sur la base de test, une ligne avec cours et six sans ; `POSITIONS_CSV` imposé sur le fichier fictif | `tests/test_jeu_demo_mcp_base.py` | égalité exacte en base, puis servi |
| position personnelle ou position close ajoutée après l'import | idem | servi avant l'ajout, refusé après |

Les trois tests du vrai import demandent PostgreSQL : en CI, ils tournent dans le job `base`, qui échoue si un test est
sauté. Le test qui attendait dix positions servies (`test_en_demonstration_le_jeu_d_exemple_est_servi`) validait le
défaut ; il attend maintenant sept positions, et sa docstring le dit.

## Limite connue

Le jeu de la démonstration Docker (`data/demo/positions.csv`, trois positions OR.PA, MC.PA, AIR.PA) n'est pas le jeu
attendu : avec ce jeu en base, `rita_portefeuille` refuse. C'était déjà le cas avant #152. Le servir demanderait une
deuxième référence versionnée : décision à prendre à part.
