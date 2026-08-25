# Preuve C20 — fraîcheur du jeu de données

**Date : 25/08/2026** · Compétences visées : **C20** (surveiller une application) et
**C1** (pérenniser la collecte — la rendre *démontrable*).

---

## 1. Le manque comblé

`/health` répondait `{"status":"ok"}` : il disait que le **service** tournait, pas que ses
**données** valaient quelque chose. Un service parfaitement en ligne servant des cours vieux
de trois mois est un service en panne — silencieuse, donc pire.

Le besoin était écrit **depuis le 11/08**, dans `scripts/README-planification.md` §7 :

> « Une tâche planifiée s'exécute — elle ne garantit pas que **les données arrivent**.
> C'est pourquoi la vraie sécurité n'est pas la planification mais une **requête de
> fraîcheur** — savoir dire "ma donnée la plus récente a N jours". C'est le chantier C,
> pas encore fait. »

Il l'est.

## 2. Ce qui a été construit

| Fichier | Rôle |
|---|---|
| `db/fraicheur.sql` | les **faits** : dates les plus récentes, comptages. Aucune décision |
| `monitorage/fraicheur.py` | la **décision** : retard en jours ouvrés, statut vert/orange/rouge |
| `api/donnees.py` → `GET /donnees/fraicheur` | **10ᵉ** point de terminaison, authentifié |
| `frontend/index.html` + `app.js` + `style.css` | le **bandeau** en haut de l'écran 1 |
| `tests/test_fraicheur.py` (14) · `test_frontend.py` (+7) · `test_api_donnees.py` (+2) | **23 tests** |

**Séparation faits / décision, et pourquoi** : `evaluer()` est une fonction pure — mêmes
entrées, même sortie, aucune base, aucune horloge implicite (la date du jour est un
**paramètre**). Elle se teste donc entièrement sans PostgreSQL, et changer un seuil
n'oblige pas à toucher au SQL.

## 3. La décision de conception qui compte : les jours **ouvrés**

La Bourse de Paris ne cote ni le samedi ni le dimanche. Compter en jours **calendaires**
ferait passer la jauge à l'orange **chaque week-end** — et *une alerte qui crie tous les
samedis est une alerte qu'on cesse de regarder*.

| Statut | Seuil | Justification |
|---|---|---|
| 🟢 vert | ≤ 1 jour ouvré | la séance du jour n'entre en base qu'après la collecte de **19h00** — la Bourse clôture à 17h35 |
| 🟠 orange | ≤ 3 jours ouvrés | une collecte manquée, à vérifier |
| 🔴 rouge | > 3 jours ouvrés | la collecte ne tourne plus |

⚠️ **Limite assumée** : les **jours fériés boursiers** ne sont pas connus du module. Un
14 juillet ajoute 1 jour ouvré apparent. Le seuil vert (1 jour) absorbe un férié isolé sans
le masquer indéfiniment. Écrit ici plutôt que découvert au jury.

## 4. Accessibilité — le statut n'est pas porté par la couleur

**RGAA 3.1 / WCAG 1.4.1** : *« l'information ne doit pas être véhiculée uniquement par la
couleur ».*

- la pastille colorée porte `aria-hidden="true"` — elle est **décorative** ;
- l'information est dans le **texte** : « Données à jour — dernière séance du 24/08/2026 » ;
- une personne daltonienne, ou un navigateur sans CSS, lit **exactement la même chose** ;
- teintes sombres, ratios calculés sur blanc : vert `#145a32` **8,3:1**, orange `#7a4f00`
  **7,1:1**, rouge `#8a1f11` **8,2:1** — tous au-delà des 4,5:1 exigés ;
- pas de `role="status"` sur le bandeau : `#statut` en porte déjà un. **Deux régions live
  qui parlent en même temps se coupent la parole** chez un lecteur d'écran.

## 5. Robustesse — la jauge ne casse pas ce qu'elle surveille

Les **trois** appels de l'écran partent en parallèle (`Promise.all`). Si celui de la
fraîcheur échoue, le bandeau ne s'affiche pas — **le portefeuille, si**. *Une jauge de santé
qui casse l'écran qu'elle surveille serait un comble.* Même principe que pour les
indicateurs (19/08), et il compte double ici.

`statut` vient du réseau : il est filtré par **liste blanche** avant d'entrer dans un nom de
classe. Le front n'utilise que `textContent` / `createTextNode`, jamais `innerHTML` —
mesure prise contre **A03 (injection)** de l'OWASP Top 10.

## 6. Vérification réelle — 25/08/2026

**Ce ne sont pas les tests qui prouvent, ce sont les exécutions.** Les 23 tests simulent
`_executer` : ils ne touchent ni la base ni la configuration.

### Le défaut que seule l'exécution réelle a trouvé

Les 14 premiers tests étaient **verts** alors que le module était **inutilisable** :

```
psycopg2.OperationalError: connection to server at "localhost", port 5432 failed
```

Port **5432** au lieu de **5433** : le module ne chargeait pas le `.env`, donc
`DATABASE_URL` était absente et `sources.database` retombait sur son DSN par défaut. Il
fonctionnait derrière `api/main.py` (qui appelle `load_dotenv()`) et **nulle part ailleurs**.

**Troisième occurrence de ce défaut dans le dépôt** : `db/importer.py` le 17/08
(commit `a7a3dba`), `indicateurs/socle.py` ensuite, celui-ci le 25/08.
👉 ***Un test vert ne prouve pas qu'on sait se connecter.***

### Après correction — HTTP réel, base réelle

```
1. sans clé                → 403                      (le garde-fou OWASP survit)
2. avec la clé             → 200
   {"aujourdhui":"2026-08-25","derniere_seance":"2026-08-24",
    "retard_jours_ouvres":1,"statut":"vert",
    "message":"Données à jour — dernière séance du 24/08/2026.",
    "nb_cotations":275554,"nb_valeurs":111,"nb_positions":7,
    "nb_articles":73,"nb_taux":10}
3. contrat OpenAPI         → /donnees/fraicheur présent, résumé documenté
```

Suite complète : **344 passed, 2 xfailed** · couverture **92,25 %** (seuil CI 90 %).

## 7. Ce que ça change pour la soutenance

Sans ce bandeau, répondre à *« vos données sont-elles à jour ? »* obligeait à **lancer une
collecte devant le jury** — réseau de la salle, Bourse fermée un dimanche, API muette :
trop de façons d'échouer, et une collecte réussie ne prouve qu'une minute, pas douze
semaines.

Avec lui, la réponse tient en **5 secondes, hors ligne**, et elle est datée.

**⬜ Reste à faire** : `logs/` est exclu de Git (`.gitignore` → `*.log`), à raison — un
journal peut contenir des valeurs détenues. La preuve de pérennisation s'accumule donc **en
local uniquement**. Un **extrait anonymisé mensuel** doit être déposé dans `evidence/C1/`.
