# Plan du constat S3 : freiner les essais de clé (carte #75, point 4)

> Écrit le 07/11/2026, **validé par Era le 07/11 (« ok plan S3 », option A)**.
> Source : `evidence/C17/revue-owasp-top10-2025-2026-10-03.md` (S3) ; carte #75, point 4 : « limite par adresse et par
> clé, 429 ». La moitié « appels du modèle » est faite depuis le 20/10 (`api/limiteur.py`) ; reste la moitié « essais de clé ».

## 1. Ce qui est vrai aujourd'hui (relevé le 07/11)

| Fait | Où |
|---|---|
| Une mauvaise clé reçoit 403 et laisse une ligne de journal (identifiant de requête, route, motif), jamais la clé | `api/main.py`, `verify_api_key` |
| Rien ne freine les essais : on peut tenter autant de clés qu'on veut | même fonction |
| La clé de production est longue (32 octets tirés au hasard) : la deviner par essais n'est pas réaliste. Le risque réel est ailleurs : un flot d'essais remplit le journal et occupe le service | `cle_attendue`, longueur minimale 16 |
| Derrière Caddy, l'API ne voit pas l'adresse du visiteur : toutes les requêtes arrivent de la passerelle du réseau Docker. Caddy transmet la vraie adresse dans `X-Forwarded-For`, mais `uvicorn` ne la lit que si l'appelant est dans `--forwarded-allow-ips` (par défaut `127.0.0.1`) | `Dockerfile`, ligne 116 ; `uvicorn` 0.40.0 |
| Depuis le correctif du port (07/11), seul ce qui tourne sur le serveur peut joindre l'API : faire confiance à l'en-tête de Caddy devient sûr | `docker-compose.yml`, `127.0.0.1:8001:8000` |

## 2. Le choix à faire (décision d'Era)

| Option | Ce qu'elle fait | Défaut |
|---|---|---|
| **A, recommandée** : par adresse | `uvicorn` lit `X-Forwarded-For` posé par Caddy ; au-delà de 10 mauvaises clés en 15 minutes depuis une même adresse, 429 avec `Retry-After`, sans même comparer la clé | l'adresse IP est une donnée personnelle : gardée en mémoire 15 minutes au plus, jamais écrite dans le journal ; ajout daté au registre RGPD |
| B : un compteur pour tous | au-delà de N mauvaises clés en tout, 429 pour tout le monde | n'importe qui bloque Era (et le jury) en envoyant de fausses clés : un déni de service offert |
| C : ne rien faire et l'écrire | la clé longue suffit contre la devinette ; S3 reste « en partie » avec sa raison | C17.8 et la ligne OWASP de E3 restent à consolider |

## 3. Les tâches de l'option A, test d'abord

| # | Test écrit avant, qui doit échouer | Code |
|---|---|---|
| T1 | `tests/test_essais_de_cle.py` : 10 mauvaises clés depuis une adresse, puis la 11e reçoit 429 et `Retry-After` ; une autre adresse passe encore ; une bonne clé ne compte pas ; après 15 minutes (horloge simulée), l'adresse repasse ; au plus 10 000 adresses suivies (les plus anciennes oubliées) | `api/limiteur.py` : une classe `FreinDesEssais`, même fenêtre glissante et même verrou que `Limiteur` |
| T2 | même fichier : la ligne de journal du blocage n'écrit ni la clé ni l'adresse ; une seule ligne par blocage, pas une par essai | `verify_api_key` appelle le frein avant la comparaison |
| T3 | `tests/test_docker_compose.py` : le service `api` reçoit `FORWARDED_ALLOW_IPS` ; `tests/test_port_api_local.py` reste vert (la confiance ne vaut que parce que le port est local) | `docker-compose.yml` |
| T4 | registre : ajout daté au traitement de l'API (adresse IP en mémoire, 15 minutes, finalité sécurité, intérêt légitime) ; aucune ligne passée effacée | `db/RGPD-registre-des-traitements.md` |

## 4. Après la livraison : ce qui prouve que c'est fait

- 💻 Depuis le poste, 11 appels avec une fausse clé : 10 fois 403, puis 429. Un appel avec la vraie clé, depuis un
  autre réseau (téléphone en partage de connexion), répond toujours 200.
- Les mêmes 11 appels avec un `X-Forwarded-For` inventé, différent à chaque fois : la 11e reçoit quand même 429. C'est
  la preuve que Caddy remplace l'en-tête envoyé par le visiteur au lieu de le recopier ; sinon, l'option A ne tient pas
  et on revient à C.
- Le journal de l'API montre une ligne de blocage, sans clé ni adresse.

## 5. Ce que ce plan ne fait pas

- Pas de stockage partagé : un seul processus `uvicorn` (vérifié le 20/10), le compteur repart à zéro au redémarrage,
  comme celui du quota.
- Pas de blocage durable ni de liste noire.

## 6. Écarts au plan pendant l'exécution (07/11)

- **T4** : le registre n'avait pas de traitement « API » où ajouter une ligne ; l'adresse IP en mémoire est inscrite
  comme un traitement à part, **T9**, avant sa mise en service.
- **Seuil réglable** : `RITA_ESSAIS_DE_CLE_MAX` (10 par défaut), transmise par `docker-compose.yml`. Raison mesurée dans
  le code : l'écran Portefeuille envoie trois appels à la fois (`frontend/app.js`, `Promise.all`), une clé mal tapée
  compte donc trois fois ; 10 échecs, c'est trois ou quatre fautes de frappe en 15 minutes.
- **Une clé absente ne compte pas** : ce n'est pas un essai, et l'interface n'envoie jamais de clé vide
  (`frontend/commun.js`, `frontend/tableau-de-bord.js`).
- Hors du plan, non traité : la clé d'exercice (`X-Cle-Exercice`, routes `/exercice/*`) n'a pas de frein.
