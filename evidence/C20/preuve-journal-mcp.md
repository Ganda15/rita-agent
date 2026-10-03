# Preuve C20 : le journal des appels MCP, table `mcp_calls` (03/10/2026)

> Issue #62, chapitre « Données » §3.6 règle 7 et §3.7. Plan validé par Era le 03/10 (D1 D2 D3 = A) :
> `docs/PLAN-62-journal-mcp-calls.md`. Zone sous garde (`db/schema.sql`) et nouveau traitement RGPD (T5) :
> rien n'a été écrit avant la validation.

## 1. Ce qui manquait

La passerelle MCP appelait l'API avec une clé et rien d'autre : aucun moyen de distinguer ses appels de ceux du
navigateur, et ses refus locaux (clé absente, portefeuille hors démonstration, #60) ne laissaient **aucune trace
nulle part**. Le chapitre demande de « tracer les événements nécessaires et les refus avec une collecte minimale »
et qu'« une défaillance de journalisation soit détectable ». Sans journal des refus, la règle de fermeture de la
matrice d'accès est invérifiable.

## 2. Ce qui a été construit

| Pièce | Fichier | Règle |
|---|---|---|
| Table `mcp_calls`, huit colonnes du chapitre | `db/schema.sql`, migration `db/migration-2026-10-03-mcp-calls.sql` | jamais un paramètre, un prompt, une clé, un chiffre ; `CHECK` sur le statut ; index sur l'horodatage |
| L'écrivain | `db/audit_mcp.py` | requête paramétrée ; identifiants douteux neutralisés (« invalide ») ; une panne compte un échec et laisse une ligne WARNING, **ne lève jamais** |
| Chemin A : l'appel arrive à l'API | middleware de `api/main.py` | un appel qui porte `X-Client-Id` laisse une ligne **après** la réponse (`BackgroundTask`), statut déduit du code HTTP ; sans l'en-tête, rien (D1) |
| Chemin B : la passerelle refuse avant d'appeler | `POST /audit/mcp` (`api/main.py`), `_signaler_refus` (`passerelle_mcp/serveur.py`) | contrat fermé (`extra="forbid"`, codes en majuscules, pas de champ libre) ; la passerelle ne fait jamais de SQL (D2) |
| La défaillance se voit | `GET /donnees/fraicheur` : `audit_mcp_echecs` | zéro en temps normal ; le vecteur C20 que l'écran et l'outil MCP lisent déjà (D3) |
| RGPD | registre T5, purge P6 (`db/rgpd_purge.py`, 90 jours) | un journal technique reste personnel quand il n'y a qu'un utilisateur |
| Lecture seule pour les outils | privilèges par défaut de `db/roles.sql` | `rita_lecture` lit, n'écrit pas (mesuré ci-dessous) |

Écart au plan, dit : la purge s'appelle **P6**, pas P4, parce que le registre numérotait déjà P4 (hook Git) et P5.

## 3. Les tests, écrits avant le code

17 tests rouges et un fichier qui ne se collectait même pas (le module n'existait pas) ; 145 passed sur les neuf
fichiers touchés après ; suite complète **719 passed, 2 xfailed, 93,83 %**.

| Fichier | Ce qu'il prouve |
|---|---|
| `tests/test_schema.py` | contrat : huit colonnes, `CHECK`, index, commentaire qui dit ce qui n'entre jamais, migration rejouable |
| `tests/test_audit_mcp.py` | l'écrivain (paramètres liés, statut contrôlé, identifiants neutralisés, panne comptée sans lever, statut par code HTTP) ; le middleware (succès, 403, 500 journalisés avec le `request_id` de la réponse ; rien sans `X-Client-Id` ; jamais un ticker) ; `POST /audit/mcp` (clé exigée, une seule ligne, tout champ hors contrat refusé) ; le compteur dans `/donnees/fraicheur` |
| `tests/test_audit_mcp_base.py` | **base réelle, transaction annulée** : une ligne conforme entre et se relit ; un statut hors liste est refusé par la base ; `rita_lecture` lit mais n'écrit pas ; P6 compte sans supprimer en simulation |
| `tests/test_passerelle_mcp.py` | chaque appel porte `X-Client-Id` et `X-Outil` ; un refus local part vers `POST /audit/mcp` sans appel métier et sans aucune donnée ; une panne du signalement ne change pas la réponse |
| `tests/test_rgpd_purge.py` | P6 : simulation sans `DELETE`, application avec, 90 jours depuis la constante, présente dans l'orchestration |
| `tests/test_rgpd_registre.py` | la fiche T5 existe avec ses rubriques ; P6 est une procédure automatisée |

## 4. Mesuré sur le poste le 03/10

Migration jouée (sortie réelle) :

```
colonnes : ['id', 'request_id', 'client_id', 'outil', 'statut', 'code_erreur', 'duree_ms', 'version_politique', 'horodatage']
lignes : 0
rita_lecture SELECT, INSERT : (True, False)
```

Puis l'API réelle démarrée sur un port libre et **quatre appels réels par la passerelle** (sortie réelle, 13 h 10) :

```
1. rita_fraicheur       : True | retard : 0
2. rita_portefeuille sans declaration : False NOT_AUTHORIZED
3. rita_portefeuille declare demo, base reelle : False NOT_AUTHORIZED (les 7 positions reelles ne sont pas le jeu d'exemple)
4. rita_indicateurs MC.PA : True
==== mcp_calls (base du poste) :
   ('passerelle-mcp', 'rita_fraicheur',    'succes', None,             120, 'matrice-acces-2026-09-07', '13:10:02')
   ('passerelle-mcp', 'rita_portefeuille', 'refuse', 'NOT_AUTHORIZED', None, 'matrice-acces-2026-09-07', '13:10:02')
   ('passerelle-mcp', 'rita_portefeuille', 'succes', None,             138, 'matrice-acces-2026-09-07', '13:10:03')
   ('passerelle-mcp', 'rita_portefeuille', 'refuse', 'NOT_AUTHORIZED', None, 'matrice-acces-2026-09-07', '13:10:03')
   ('passerelle-mcp', 'rita_indicateurs',  'succes', None,             370, 'matrice-acces-2026-09-07', '13:10:03')
lignes contenant MC.PA : 0
```

Cinq lignes pour quatre appels, et c'est juste : l'appel 3 en fait deux. L'API a **servi** le portefeuille (ligne
`succes`, chemin A : la clé était bonne), puis la passerelle l'a **refusé** après comparaison au jeu d'exemple (ligne
`refuse`, chemin B) : les sept positions réelles ne sont pas le jeu de démonstration. Le journal montre exactement ce
que le verrou de #60 fait, et à quel endroit. Le ticker de l'appel 4 n'apparaît nulle part.

## 5. Reste, dit franchement

- ~~La migration sur la base Compose et sur Hetzner~~ **faite le 03/10 après-midi** : table `mcp_calls`, index et droits
  présents sur les deux (`rita_lecture` lit, n'écrit pas). Le code du serveur (20/08) n'écrit pas encore dedans :
  déploiement à faire après le gel du 15/10.
- Aucune alerte ne lit encore ce journal : la requête de lecture est dans `docs/EXPLOITATION.md` ; brancher une
  règle (« plus de N refus par jour ») viendra avec les seuils C20, après une semaine de données.
- Les refus pris par le cadre `mcp` lui-même (outil inconnu) ne passent pas par notre code : ils ne sont pas journalisés.
- Un seul client aujourd'hui ; `client_id` prendra son sens quand un second client automatique existera.

## 📖 Glossaire

- **Middleware** : code qui voit chaque requête avant et après la route ; c'est là que vit `X-Request-ID`.
- **`BackgroundTask`** : travail exécuté après l'envoi de la réponse ; l'appelant n'attend pas.
- **Contrat fermé (`extra="forbid"`)** : tout champ non prévu est refusé avec 422.
- **Transaction annulée** : `BEGIN` puis `ROLLBACK` ; les tests sur la base réelle n'y laissent rien.
