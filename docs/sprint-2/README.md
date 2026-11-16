# Sprint 2 : le socle et la chaîne

Document d'entrée du sprint 2 du fil rouge RITA. Il dit où voir chaque élément demandé par le brief, et ce qui n'est
pas fait.

**À lire en premier** : le livrable du sprint, `docs/sprint-2/livrable/livrable-sprint-2.pdf` (13 pages : livrables
demandés, exigence par exigence, preuves, ce qui n'est pas fait). Index des preuves : `evidence/sprint-2/README.md`.

- **Production** : <https://178-104-184-125.sslip.io> (serveur Hetzner, `178.104.184.125`). `/health` annonce le
  commit et la date de construction de la version servie.
- **Conception** : `docs/CHAINE-V1.md` (la spec) ; plan de travail : `docs/sprint-2/PLAN-TRAVAIL.md`.
- **Exploitation** : `docs/exploitation.md` (installation, reconstruction depuis le dépôt au § 3 ter, secrets).

## Ce que le brief demande, et où le voir

| Demande du brief | Où le voir |
|---|---|
| Un dépôt propre, des environnements reproductibles, des secrets hors du dépôt | `Dockerfile`, `docker-compose.yml` ; reconstruction depuis le dépôt : `docker-compose.demo.yml`, `data/demo/`, `docs/exploitation.md` § 3 ter ; secrets : travail `secrets` (gitleaks sur tout l'historique), `scripts/verifier_dockerfile.py`, `evidence/C21/INC-008-cles-mistral-dans-l-historique.md` |
| Un squelette : une route API, une interface minimale, un appel au modèle qui répond | `POST /briefing`, `GET /health` (`api/main.py`), `frontend/briefing.html`, `src/llm.py` |
| Une chaîne lint, tests, construction, déploiement automatique, à travers les environnements | `.github/workflows/livraison.yml` : `lint`, `secrets`, `construire-et-publier`, `attendre-creneau`, `deployer` ; le serveur essaie chaque image en préproduction (port 8003, compte en lecture seule) avant de la mettre en service (`deploy/deployer.py`) ; première livraison : `evidence/sprint-2/N0-premiere-livraison-2026-10-14.md` |
| Des tests bloquants, prouvés par un commit cassé | règle de protection de `main` : six contrôles exigés (`evidence/C19/ruleset-main-2026-10-14.json`) ; la PR cassée #93, ouverte pendant l'atelier du 15/10, bloquée et jamais fusionnée : `evidence/sprint-2/journaux/pr-93-commit-casse.txt` |
| Un retour arrière en une opération, répété | `.github/workflows/retour-arriere.yml` (*Run workflow*), ordre `revenir` du script du serveur ; répété le 14/10 : `evidence/sprint-2/N1-retour-arriere-2026-10-14.md` |

## Mes décisions avant la première livraison (14/10/2026)

1. **Tâches 4 à 6 faites avant N0.** Le jeu de démonstration, le mode `--demo` de l'importateur et le service
   `initialisation` sont livrés avec N0. Seul le travail `reconstruction` de la chaîne (automatisation dans la CI)
   reste reporté après l'atelier.
2. **Première bascule acceptée avec un secours dégradé.** La version en service avant la chaîne a été sauvegardée le
   14/10 (image `sha256:2a5004248ff8…aa6f`, configuration, environnement effectif, base), et les archives se
   relisent. L'essai de redémarrage de cette version (port 8003) démarre et répond, mais ne produit plus de briefing :
   ses variables de clé de modèle sont vides. Si la première livraison échoue après la bascule, le secours est donc
   cette version dégradée, restaurée à la main. J'accepte de faire la première bascule dans ces conditions.

## Préparation du serveur (tâche 10, 14/10/2026)

Je l'ai faite moi-même, chaque point vérifié par une commande :
- `.env` du serveur lisible par root seul (600) ; clés du modèle Azure ajoutées sans être affichées (l'adresse,
  collée deux fois, a été corrigée le soir même ; un appel réel au modèle depuis le serveur répond 200) ;
- compte PostgreSQL `rita_lecture` avec un mot de passe aléatoire jamais affiché ; lecture vérifiée, écriture refusée ;
- SSH par clé seulement : mot de passe refusé, clé acceptée ;
- jeton GHCR en lecture seule ; clé SSH dédiée à GitHub, limitée par une commande forcée à `deployer.sh` ;
  environnement GitHub `production` et ses trois secrets ; empreinte du serveur vérifiée. Le secret
  `DEPLOY_KNOWN_HOSTS` se pose par `gh secret set --body` avec la ligne vérifiée, jamais par `ssh-keyscan | gh` : sur
  mon poste, le `ssh-keyscan` de Windows échoue face à ce serveur et le secret part vide ;
- articles de la base de production remplacés une fois par ceux du poste (2 052 articles, dont 54 sur L'Oréal) : le
  contrôle de livraison exige au moins un article pour `OR.PA`.

## Première livraison N0 (14/10/2026, mesurée)

La fusion de la PR #91 (commit `4819627`) est arrivée en production au troisième essai du travail `deployer`. Les
deux premiers ont été refusés sans toucher à la production : empreinte du serveur enregistrée vide (SSH refuse la
connexion), puis adresse du modèle collée deux fois dans le `.env` du serveur (le pré-test refuse la version, faute de
briefing). Le troisième a livré en 221 s côté serveur ; `/health` annonce le commit `48196272…`. Détail et sorties :
`evidence/sprint-2/N0-premiere-livraison-2026-10-14.md`.

## N1 et la répétition du retour arrière (14/10/2026, mesurés)

- **N1** (PR #92, commit `e06cd17`) : livrée au premier essai, 9 min 24 s de la fusion à la production.
- **Retour arrière N1 vers N0** en une opération (`gh workflow run retour-arriere.yml`, avec acteur et motif) :
  28 s de bout en bout, 16 s côté serveur ; N0 servie 19 s après le lancement.
- **N1 relivrée** par la relance du travail `deployer` : la production correspond de nouveau à `main`.

Détail, journal du serveur et mesure de `/health` : `evidence/sprint-2/N1-retour-arriere-2026-10-14.md`.

## Ce qui n'est pas fait

- Le travail `reconstruction` de la chaîne (reconstruction automatique à chaque PR) : reporté après l'atelier ; la
  reconstruction est montrée en direct.
- Le nettoyage automatique des anciennes images et des anciens index : à la main (un index ne sert déjà plus,
  celui de la première livraison de N1).
- Une bascule sans coupure : pendant le retour arrière, la production a répondu 502 pendant environ 7 s, le temps de
  remplacer le conteneur de l'API ; les livraisons basculent de la même façon.
- Le retour automatique vers la version d'avant la chaîne : la première livraison n'a pas de version précédente
  connue du script ; en cas d'échec, restauration manuelle.
- Les durées maximales du script du serveur sont calculées ; une seule est mesurée : 221 s pour la première
  livraison, pour un maximum calculé de 4 161 s.
- Le journal du serveur nomme le contrôle en échec sans son code HTTP, et le conteneur du pré-test part avec ses
  journaux : un refus demande une enquête. À ajouter après l'atelier (le script du serveur devra être réinstallé).
- Le retour arrière sans GitHub : prévu dans `docs/CHAINE-V1.md` § 5.2, qui le dit « écrit dans
  `docs/exploitation.md` » ; la procédure n'y est pas encore, et elle n'a jamais été exercée.
- Pas de traçage Langfuse en production : aucune clé Langfuse sur le serveur.
- La fraîcheur des données de production n'entre pas dans ce sprint : les articles ont été copiés une fois, le 14/10.
