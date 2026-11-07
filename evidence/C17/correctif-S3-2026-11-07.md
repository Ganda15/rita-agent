# Constat S3 : le frein des essais de clé (07/11/2026)

Compétence : C17 (sécurité, OWASP API4:2023). Constat S3 de la revue du 03/10
(`evidence/C17/revue-owasp-top10-2025-2026-10-03.md`), carte #75, point 4. Plan : `docs/PLAN-S3-essais-de-cle.md`,
validé par Era le 07/11 (« ok plan S3 », option A, par adresse).

## Avant

Une mauvaise clé recevait 403 et laissait une ligne de journal ; rien ne freinait les essais suivants. La moitié
« appels du modèle » de S3 était faite depuis le 20/10 (`api/limiteur.py`, 10 appels par minute) ; restait la moitié
« essais de clé ».

## Le correctif

- `api/limiteur.py`, `FreinDesEssais` : au-delà de 10 mauvaises clés en 15 minutes depuis une adresse, 429 avec
  `Retry-After` et le motif `TROP_D_ESSAIS`, avant toute comparaison de clé. Une clé absente ou juste ne compte pas.
  Au plus 10 000 adresses suivies. Une seule ligne de journal par blocage, sans adresse ni clé.
- `docker-compose.yml` : `FORWARDED_ALLOW_IPS` pour que `uvicorn` lise l'adresse écrite par Caddy, et le seuil
  `RITA_ESSAIS_DE_CLE_MAX` (10 par défaut). La confiance tient parce que le port n'écoute que la machine
  (`evidence/C17/correctif-port-8001-2026-11-07.md`).
- Registre RGPD : traitement **T9**, inscrit avant sa mise en service (adresse en mémoire, 15 minutes au plus).
- `docs/exploitation.md` : « Une adresse bloquée par le frein des essais de clé ».
- La clé d'exercice (`X-Cle-Exercice`, routes `/exercice/*`) : même frein, même compteur, ajouté le 07/11 après la revue
  de sécurité automatique (2 tests dans `tests/test_essais_de_cle.py`, rouge avant, vert après).

## Tests, écrits avant le code

- `tests/test_essais_de_cle.py` (11 tests) : rouge avant (`ImportError`, la classe n'existait pas), vert après.
- `tests/test_docker_compose.py` (2 tests de plus) : rouges avant (2 échecs), verts après.
- Le schéma de collecte du rapport E1 lit le registre : régénéré (« T1 à T9 »), illustration reportée, PNG rendu et
  regardé le 07/11.

## Ce qui reste

- **Pas encore en production.** La preuve viendra après la livraison, depuis le poste :
  - 11 appels avec une fausse clé : 10 fois 403, puis 429 ;
  - les mêmes appels avec un `X-Forwarded-For` inventé, différent à chaque fois : la 11e reçoit quand même 429 (Caddy
    remplace l'en-tête envoyé par le visiteur) ; sinon, l'option A ne tient pas ;
  - la vraie clé depuis une autre connexion répond 200.
