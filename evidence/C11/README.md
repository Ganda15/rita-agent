# C11 : Monitorer un modèle d'intelligence artificielle

**Créé le 02/10/2026.** Livrable **E3**. Outil : **Langfuse Cloud, région UE** (Irlande), projet `rita`,
palier gratuit (50 000 unités par mois, 30 jours de conservation, 2 alertes). Décision du 28/09
(`CONTINUITE.md` D, registre RGPD §T3), première trace réelle le 02/10 à 18:39.

---

## Les 9 critères officiels, et où RITA en est au 02/10/2026 au soir

| # | Critère (texte officiel) | État | Preuve ou manque |
|---|---|---|---|
| 1 | Les **métriques** du monitorage sont expliquées sans erreur d'interprétation | ✅ écrit | `docs/EXPLOITATION.md`, section « Monitorage Langfuse et alertes » : latence par étape, erreurs de repli, verdict AMF (note `conforme_amf`), jetons. À reprendre dans le rapport E3 |
| 2 | Le ou les **outils** sont adaptés au contexte et aux contraintes | ✅ décidé et mesuré | Langfuse retenu contre LangSmith et l'auto-hébergement : aucune donnée personnelle dans le prompt, région UE, pas de gRPC (bloqué sur le poste), 4 Go sur le serveur ; `CONTINUITE.md` D et E, registre §T3 |
| 3 | Au moins un **vecteur de restitution en temps réel** (tableau de bord) | 🟠 à faire | Les traces existent ; le tableau « RITA C11 » (3 widgets) se construit dans l'interface Langfuse, par Era. Aucune capture au 02/10 |
| 4 | Les enjeux d'**accessibilité** sont pris en compte dans le choix de l'outil | 🟠 à écrire | Interface web standard, texte et tableaux ; à argumenter dans le rapport E3, rien d'écrit ici |
| 5 | La chaîne est d'abord testée dans un **bac à sable** | ✅ mesuré | Toute la suite de tests tourne avec le traçage coupé (`tests/conftest.py`) et des doubles de client ; l'incident [INC-006](../C21/INC-006-tests-ecrivaient-en-production.md) a précisément établi cette séparation |
| 6 | La chaîne est **en état de marche** : les métriques sont évaluées et restituées | ✅ partiel | Traces réelles depuis le 02/10 18:39 (captures d'Era) ; en conteneur depuis la transmission des variables par `docker-compose.yml` (02/10, non encore déployé sur le serveur) |
| 7 | Les **sources** sont versionnées sur un dépôt distant | ✅ | `src/traces.py`, `api/main.py`, `graph/workflow.py`, `.github/workflows/alerte-incident.yml`, dépôt `Ganda15/rita-agent` |
| 8 | La **documentation technique** couvre l'installation, la configuration et l'utilisation | ✅ partiel | `docs/EXPLOITATION.md`, section « Monitorage Langfuse et alertes » (variables, tableau, alertes, test de la chaîne) |
| 9 | La documentation est communiquée dans un format **accessible** | 🟠 à faire | Markdown dans le dépôt ; le rapport E3 en PDF reste à produire |

**Bilan honnête : 5 critères tenus, 1 partiel, 3 à faire.** Les trois manquants sont du côté de
l'interface Langfuse (tableau, alertes réglées) et du rapport E3, pas du code.

## Ce qu'une trace montre (depuis le 02/10 au soir)

```
briefing                      racine : request_id, verdict AMF, note conforme_amf (1 ou 0)
├── scout                     ticker, fraîcheur en jours, cotation périmée, erreur éventuelle
├── rag        (retriever)    motif (OK, OUT_OF_CORPUS, NON_APPELE), nombre de passages, sources
│   └── garde-fou-entree      bloqué ou non, motifs ; niveau WARNING si bloqué
├── redacteur                 longueur du texte
│   └── briefing-llm          l'appel au modèle
│       └── llm-<fournisseur> une génération par fournisseur essayé, usage en jetons, erreur du repli
└── garde-fou-sortie          bloqué ou non, motifs ; niveau WARNING si bloqué
```

Le même `request_id` est dans l'en-tête `X-Request-ID` de la réponse, dans les lignes de journal de
l'API et comme identifiant de la trace. La sortie d'une étape est un résumé, jamais le contenu.

## Les pièces, et la commande qui les prouve

| Pièce | Où | Preuve (02/10/2026) |
|---|---|---|
| Module de traçage, no-op sans clés | `src/traces.py` | `tests/test_traces.py` (7 tests) |
| Racine par briefing, verdict AMF sur la trace | `src/traces.py` (`briefing`, `noter_verdict_amf`), `api/main.py` | `tests/test_trace_verdict_amf.py` (6 tests) |
| Un span par étape, test de trace à la Kaldera | `graph/workflow.py`, `rag/recherche.py`, `api/main.py` | `tests/test_trace_chemin.py` (8 tests) |
| `request_id` dans la réponse, le journal et la trace | `api/main.py` (middleware), `src/traces.py` | `tests/test_request_id.py` (11 tests) |
| Lignes de journal : servi, refusé, erreur 502 | `api/main.py` | `tests/test_journal_refus_amf.py` (2), `tests/test_request_id.py` |
| Variables transmises au conteneur | `docker-compose.yml` | `tests/test_docker_compose.py` (3 tests ajoutés) |
| Alerte Langfuse vers une issue `incident` | `.github/workflows/alerte-incident.yml` | `tests/test_alerte_incident.py` (7 tests) |
| La suite de tests ne trace jamais | `tests/conftest.py` | `tests/test_llm.py::test_la_suite_de_tests_n_envoie_jamais_de_trace` |

Suite complète le 02/10 au soir : `C:\Python314\python.exe -m pytest -q` : **626 passed, 2 xfailed** ;
couverture 93,66 % (seuil 90 %), `api/main.py` et `graph/workflow.py` à 100 %.

## Ce qui manque, et qui le fait

| Manque | Qui | Preuve attendue ici |
|---|---|---|
| Capture de la première trace réelle (02/10 18:39) et de la hiérarchie complète après le 02/10 au soir | Era, interface Langfuse | `capture-2026-10-02-premiere-trace.png`, `capture-trace-complete.png` |
| Capture des 12 lignes factices avant leur suppression (INC-006) | Era | `capture-2026-10-02-inc-006-avant-suppression.png` |
| Tableau « RITA C11 » : générations par fournisseur, p95 de `briefing-llm` par jour, observations en ERROR ou WARNING | Era, Dashboards | capture datée |
| Les 2 alertes (ERROR sur 1 jour ; aucune trace en 24 h), canal GitHub Actions | Era, Alerts ; seuils fixés après une semaine de traces | capture datée + lien de l'issue ouverte par le test manuel |
| Test manuel de la chaîne (bouton Run workflow) | Era, onglet Actions | numéro de l'issue `incident` |
| Variables Langfuse sur le serveur Hetzner | Era, serveur | une trace dont les métadonnées viennent du serveur |

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Trace** | L'arbre des étapes d'une requête, avec leur durée |
| **Span, observation** | Une étape chronométrée dans une trace ; une génération est le span d'un appel au modèle |
| **p95** | La valeur sous laquelle tombent 95 % des mesures : « 95 % des briefings répondent en moins de X secondes » |
| **Unité (Langfuse)** | Ce que le palier compte : une trace, une observation ou une note ; un briefing en coûte environ neuf |
| **Note (score)** | Une valeur attachée à une trace, ici `conforme_amf` à 1 ou 0, qu'un tableau peut compter |
| **Bac à sable** | Un environnement où l'on peut tout casser sans toucher la production ; ici la suite de tests, traçage coupé |
| **request_id** | Un identifiant par requête, repris dans la réponse, le journal et la trace pour les relier |
