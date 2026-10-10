# Erratum C20 : le refus du verrou de démonstration du 3 octobre (mesuré le 10/10/2026)

Ce fichier corrige une interprétation de `preuve-journal-mcp.md` (3 octobre), qui n'est **pas** réécrite. Constitué le
jour de la découverte.

## Ce que disait la preuve du 3 octobre

Ligne 58 et section 4 : l'appel « déclaré démo, base réelle » a été refusé (`NOT_AUTHORIZED`) parce que « les sept
positions réelles ne sont pas le jeu de démonstration ». Le rapport E3 v1.2 (section 4.1) en tirait que le journal
montrait le verrou à l'endroit exact où il agit.

## Ce qui a été mesuré le 10 octobre

Le code réel du verrou (`passerelle_mcp/serveur.py:93-106`, `_est_le_jeu_de_demonstration`) a été exécuté sur la
réponse de l'API archivée le 3 octobre (`evidence/C17/mesures-2026-10-03/entrees/donnees_portefeuille.json`) :

| Mesure | Résultat |
|---|---|
| Lignes du fichier d'exemple (`data/positions-exemple.csv`) | 12 |
| Lignes gardées par le lecteur CSV (2 lignes de test rejetées exprès) | 10 |
| Positions servies par l'API, donc présentes en base | 7 |
| Positions servies présentes dans le fichier d'exemple | 7 |
| Positions servies absentes du fichier d'exemple | 0 |
| Lignes du fichier d'exemple absentes de la base | 3 |
| Le verrou accepte-t-il cette base ? | **non** (`False`) |

**Cause** : l'import des positions (`db/importer.py:191-200`, `importer_positions`) écarte une ligne dont le ticker
n'est ni dans la table `valeur` ni retrouvé par un alias, et trois lignes du fichier d'exemple sont dans ce cas. Le verrou, lui, compare dans les deux sens à toutes les
lignes gardées par le lecteur (10). Les deux ne filtrent pas les positions de la même façon.

**Conséquence** : en démonstration, `rita_portefeuille` refuse aussi le jeu de démonstration importé dans l'environnement
actuel. Le refus du 3 octobre ne
venait pas d'un portefeuille réel : les 7 positions servies provenaient toutes du fichier d'exemple, mais 3 des 10
positions valides n'avaient pas été importées. Le verrou échoue
fermé, sans rien laisser sortir ; la sécurité tient, la fonction de démonstration ne marche pas.

**Pourquoi les tests étaient verts** : `tests/test_passerelle_mcp.py:210-215` simule une réponse de l'API de
10 positions, alors que l'API de l'environnement de démonstration importé n'en rend actuellement que sept ; le test ne passe ni par l'import ni par la base.

## Correction (après le gel du 15/10, test d'abord)

Le verrou doit partager avec l'import la même normalisation, le même filtrage par l'univers et la même résolution des
alias, et comparer une liste normalisée et triée (un multiensemble : un simple ensemble fusionnerait deux lignes
identiques) d'au moins le ticker canonique, la quantité, le prix de revient et la devise. Le test doit traverser le
filtrage et les alias de l'import, puis la forme réelle de la réponse de l'API. Carte à créer.

## Ce que le jeu d'exemple contient

Des positions inventées sur des sociétés réellement cotées ; Era déclare le 10/10/2026 n'avoir jamais détenu ces titres.

## 📖 Glossaire

- **Verrou de démonstration** : contrôle de la passerelle MCP destiné à ne servir que le jeu d'exemple du dépôt ; son implémentation actuelle ne compare que les couples (ticker, quantité),
  sous forme d'ensemble.
- **Échouer fermé** : en cas de doute, refuser plutôt que laisser passer.
- **Univers** : les 111 valeurs suivies par RITA ; une position hors univers ne peut pas entrer en base.
- **Doublure** : fausse réponse utilisée par un test à la place du système réel.
