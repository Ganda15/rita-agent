# Plan : le journal d'audit des appels MCP, table `mcp_calls` (issue #62, C20, chapitre « Données » §3.7)

> **Établi le 03/10/2026**, après #65. **Zone sous garde** (`db/schema.sql`) et **nouveau traitement RGPD** : ce plan est
> relu et validé par Era **avant** toute ligne de code. Rien de ce qui suit n'est fait. Trois décisions en section 7.

## 1. Le besoin, et ce qui existe déjà

Le chapitre (§3.6, règle 7) demande de « tracer les événements nécessaires et les refus avec une collecte minimale ;
une défaillance de journalisation doit être détectable ». Il propose (§3.7) une table `mcp_calls`, absente du schéma,
écrite **par l'API ou un collecteur d'audit, jamais par la passerelle** (qui ne touche pas la base), et qui couvre
aussi **les refus survenus avant l'appel métier**.

| Ce qui existe au 03/10 | Ce qu'il en manque |
|---|---|
| `request_id` sur chaque réponse de l'API, dans le journal et la trace Langfuse (02/10) | la passerelle ne le transmet pas et ne l'enregistre nulle part |
| Traces Langfuse par briefing (C11) | elles couvrent `/briefing`, pas les lectures de données ni les appels MCP ; et Langfuse est un tiers, pas notre base |
| La passerelle refuse localement (#60 : portefeuille hors démonstration ; clé absente) | ces refus ne laissent **aucune trace** nulle part |
| `memory_audit` : table d'audit déjà dans le schéma, purge P1 à 90 jours, traitement T2 du registre | c'est le modèle à suivre (forme, purge, registre), pas la table à réutiliser : autre finalité |

Ce que ça apporte aux épreuves : E5 / C20 (« les règles de journalisation sont intégrées aux sources de l'application »,
« les métriques et seuils d'alerte ») et E3 / C10 (l'intégration MCP devient observable). Et au chapitre : la matrice
d'accès a une règle de fermeture ; sans journal des refus, personne ne saura jamais si elle a servi.

## 2. La table

```sql
CREATE TABLE mcp_calls (
    id                BIGSERIAL    PRIMARY KEY,
    request_id        VARCHAR(64)  NOT NULL,            -- celui de l'API (ou genere par la passerelle pour un refus local)
    client_id         VARCHAR(40)  NOT NULL,            -- identite TECHNIQUE posee par le systeme : 'passerelle-mcp'
    outil             VARCHAR(60)  NOT NULL,            -- nom demande, meme inconnu
    statut            VARCHAR(10)  NOT NULL CHECK (statut IN ('succes', 'refuse', 'erreur')),
    code_erreur       VARCHAR(40),                      -- NOT_AUTHORIZED, NOT_FOUND, DELAI_DEPASSE... jamais un message libre
    duree_ms          INTEGER      CHECK (duree_ms IS NULL OR duree_ms >= 0),
    version_politique VARCHAR(40)  NOT NULL,            -- 'matrice-acces-2026-09-07' : les regles appliquees
    horodatage        TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE INDEX idx_mcp_calls_horodatage ON mcp_calls (horodatage DESC);
COMMENT ON TABLE mcp_calls IS 'Journal des appels MCP (C20, chapitre Donnees 3.7). Aucun parametre brut, aucun prompt, aucune cle, aucun chiffre de portefeuille. Retention 90 jours (P4). Ecrit par l API seule.';
```

Écarts volontaires avec le chapitre : `id` en `BIGSERIAL` et non UUID (même forme que `memory_audit`, et un identifiant
d'événement n'a pas besoin d'être devinable ou non : il ne sort jamais) ; `request_id` en `VARCHAR(64)` parce que l'API
accepte un identifiant client de 8 à 64 caractères, pas seulement un UUID. Tout le reste suit le chapitre mot pour mot.
**Ce qui n'y entre jamais** : les paramètres de l'appel (un ticker est un intérêt personnel), les prompts, les clés, les
positions ou totaux rendus, le message d'erreur libre (le code typé suffit, le message est dans le journal texte).

## 3. Qui écrit, et comment

Deux chemins, un seul écrivain.

| Chemin | Quand | Comment |
|---|---|---|
| **A. L'appel arrive à l'API** | la passerelle appelle `GET /donnees/...` | la passerelle ajoute deux en-têtes : `X-Client-Id: passerelle-mcp` et `X-Outil: rita_indicateurs`. Le middleware de `api/main.py`, qui pose déjà `X-Request-ID`, écrit une ligne **après** la réponse quand `X-Client-Id` est présent : statut `succes` (2xx), `refuse` (401, 403, 404, 422), `erreur` (5xx) ; `code_erreur` déduit du code HTTP ; `duree_ms` mesurée |
| **B. La passerelle refuse avant d'appeler** | clé absente, portefeuille hors démonstration (#60), jeu de données non conforme | la passerelle appelle `POST /audit/mcp` (clé d'API obligatoire, corps : `outil`, `statut`, `code_erreur`, `request_id` qu'elle génère) ; l'API écrit. Pas de SQL depuis la passerelle, conformément au chapitre |

L'écrivain : `db/audit_mcp.py::enregistrer(evenement)`, requête paramétrée, une connexion courte. **Fail-safe dans un seul
sens** : une panne d'écriture ne fait jamais échouer l'appel métier, mais elle est **détectable** : une ligne WARNING
`audit mcp non ecrit` et un compteur `audit_mcp_echecs` lisible par `GET /donnees/fraicheur` (déjà le vecteur de C20).
C'est la règle 7 du chapitre, et la même règle que le traçage Langfuse depuis la revue automatisée du 03/10.

Le middleware écrit hors du chemin de la réponse (`BackgroundTask` de Starlette) : l'appelant ne paie pas l'écriture.
`version_politique` est une constante de l'API, `matrice-acces-2026-09-07` (la date de la matrice du chapitre) ; elle
change quand la matrice change, pas à chaque déploiement.

Le rôle `rita_lecture` lit la table par les privilèges par défaut déjà posés (`db/roles.sql`) et ne peut pas y écrire ;
l'API écrit avec le rôle `rita`, comme pour tout le reste.

## 4. RGPD : un traitement nouveau, T5

Un journal technique peut rester une donnée personnelle (le chapitre le dit) : `request_id` et `horodatage` relient un
appel à un moment, et le propriétaire est la seule personne qui appelle. Donc : **traitement T5** dans
`db/RGPD-registre-des-traitements.md`, sur le modèle de T2 : finalité (sécurité et surveillance des accès, C20), base
légale (intérêt légitime du responsable, sécurité du service), données (les huit colonnes, aucune donnée de contenu),
durée **90 jours** (même durée que T2, justifiée : au-delà, un refus ancien n'aide plus un diagnostic), accès (propriétaire
et outils en lecture seule), purge **P4** dans `db/rgpd_purge.py` (même forme que P1, hebdomadaire), droits (effacement
sur demande : suppression par `request_id`).

## 5. Les tests, écrits avant le code

| # | Test | Fichier | Rouge d'abord ? |
|---|---|---|---|
| 1 | contrat sur `db/schema.sql` : la table, ses huit colonnes, le `CHECK` du statut, l'index, le commentaire sans contenu brut | `tests/test_schema.py` (nouveau, lecture du texte) | oui |
| 2 | `enregistrer()` : requête paramétrée, aucun champ hors des huit, `None` accepté pour `code_erreur` et `duree_ms` ; une panne de connexion donne une ligne WARNING et incrémente `audit_mcp_echecs`, sans lever | `tests/test_audit_mcp.py` (nouveau, connexion simulée) | oui |
| 3 | middleware : une requête avec `X-Client-Id` et `X-Outil` écrit une ligne `succes` sur 200, `refuse` sur 403 et 404, `erreur` sur 500, avec le `request_id` de la réponse ; **sans** `X-Client-Id`, rien n'est écrit (un navigateur n'est pas un client MCP) ; aucun paramètre de requête dans la ligne | `tests/test_audit_mcp.py` | oui |
| 4 | `POST /audit/mcp` : refuse sans clé ; accepte seulement `statut` et `code_erreur` dans les listes ; écrit la ligne ; n'accepte aucun champ libre | `tests/test_audit_mcp.py` | oui |
| 5 | passerelle : chaque appel porte `X-Client-Id` et `X-Outil` ; un refus local (#60, clé absente) déclenche le `POST /audit/mcp` avec le bon code ; une panne du `POST` ne change pas la réponse à l'utilisateur | `tests/test_passerelle_mcp.py` | oui |
| 6 | purge P4 : compte et supprime au-delà de 90 jours, à blanc sans `appliquer` | `tests/test_rgpd_purge.py` | oui |
| 7 | base réelle, transaction annulée (sauté sans `DATABASE_URL`) : insertion, lecture par `SET ROLE rita_lecture`, refus d'écriture par ce rôle, purge P4 à blanc | `tests/test_audit_mcp_base.py` (nouveau) | oui |
| 8 | registre : le texte contient `T5`, `mcp_calls`, `90 jours`, `P4` | `tests/test_rgpd_registre.py` (nouveau ou existant) | oui |

## 6. L'ordre des opérations

1. Era valide ce plan et tranche la section 7.
2. Tests 1 à 8 écrits, lancés, vus rouges.
3. `db/schema.sql` (table, index, commentaire) ; migration rejouable `db/migration-2026-10-XX-mcp-calls.sql`
   (`CREATE TABLE IF NOT EXISTS`, même forme que le 27/09 et le 03/10) ; `db/roles.sql` inchangé (privilèges par défaut).
4. `db/audit_mcp.py` ; middleware et route `POST /audit/mcp` dans `api/main.py` ; compteur exposé par `/donnees/fraicheur`.
5. Passerelle : deux en-têtes, `request_id` local pour les refus, `POST` des refus, fail-safe.
6. Registre T5, purge P4, `docs/EXPLOITATION.md` (migration, lecture du journal : une requête `SELECT statut, COUNT(*)` par jour).
7. Migration jouée sur le poste, puis Compose, puis Hetzner ; sortie collée dans `evidence/C20/preuve-journal-mcp.md`
   avec un premier appel réel par la passerelle (succès) et un refus réel (#60 sans déclaration).
8. Ledger : décision D « la passerelle n'écrit jamais, l'API écrit l'audit » ; `CHANGELOG` ; `docs/conception/donnees/README.md`.
9. Commit `Closes #62`, PR relue.

Estimation : 3 h, une vingtaine de tests. Touche `db/schema.sql` (zone sous garde) et le registre RGPD ; ne touche ni
`guardrails/` ni `evals/`.

## 7. Trois décisions pour Era

| # | Question | Option A (recommandée) | Option B |
|---|---|---|---|
| D1 | Qui est journalisé | **seuls les appels qui portent `X-Client-Id`** (la passerelle MCP aujourd'hui, d'autres clients automatiques demain) : le navigateur d'Era n'est pas un client MCP et sa navigation n'a pas à être tracée en base | tous les appels à `/donnees/*`, quel que soit le client |
| D2 | Les refus locaux de la passerelle | **remontés à l'API par `POST /audit/mcp`** : le journal couvre les refus avant appel, comme le chapitre le demande | non journalisés (plus simple ; mais la règle de fermeture devient invisible) |
| D3 | Le vecteur de « défaillance détectable » | **compteur `audit_mcp_echecs` dans `/donnees/fraicheur`** + ligne WARNING : un seul vecteur C20 déjà lu par l'écran et l'outil MCP | ligne WARNING seule |

## 8. Risques, dits franchement

- Une écriture en base par appel de lecture : négligeable pour une passerelle qui fait quelques appels par jour ; à
  revoir si un client automatique en faisait des milliers (un lot par minute serait alors la réponse, pas l'abandon).
- `request_id` généré côté passerelle pour un refus local n'est pas celui de l'API : les deux restent distinguables
  par `statut` et par l'absence de ligne API correspondante ; c'est dit dans le registre.
- Le journal ne prouve rien tant qu'il n'est pas lu : la requête de lecture dans `docs/EXPLOITATION.md` et le compteur
  dans `/donnees/fraicheur` sont ce qui le fait vivre ; sans eux, c'est une table de plus.
- Un journal technique **reste** une donnée personnelle ici (un seul utilisateur) : d'où T5 et P4 dès le premier jour,
  pas « plus tard ».

## 📖 Glossaire

- **Journal d'audit** : table qui enregistre qui a demandé quoi, quand, avec quel résultat ; jamais le contenu.
- **Middleware** : code qui voit chaque requête HTTP avant et après la route ; c'est là que vit déjà `X-Request-ID`.
- **`BackgroundTask`** : travail exécuté après l'envoi de la réponse ; l'appelant n'attend pas.
- **Fail-safe** : une panne du journal ne casse pas l'appel ; mais elle se voit (compteur, WARNING).
- **`version_politique`** : étiquette des règles d'accès en vigueur au moment de l'appel ; permet de relire un vieux refus avec les bonnes règles.
