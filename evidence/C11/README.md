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
| 3 | Au moins un **vecteur de restitution en temps réel** (tableau de bord) | ✅ construit le 03/10 | Tableau « RITA C11 », trois tuiles (générations par fournisseur, p95 de `briefing-llm`, observations ERROR ou WARNING), créé par l'API publique : `dashboard-rita-c11-2026-10-03.json`, `preuve-langfuse-2026-10-03.md`. Capture d'écran encore à faire par Era |
| 4 | Les enjeux d'**accessibilité** sont pris en compte dans le choix de l'outil | 🟠 argumenté le 04/10 | Rapport E3 v1.1, § 5.6 : texte et tableaux, clavier, rien par la seule couleur, export CSV de chaque tuile, alerte en texte ; reste partiel : examinée après le choix de l'outil, sans déclaration de l'éditeur ni test au lecteur d'écran |
| 5 | La chaîne est d'abord testée dans un **bac à sable** | ✅ mesuré | Toute la suite de tests tourne avec le traçage coupé (`tests/conftest.py`) et des doubles de client ; l'incident [INC-006](../C21/INC-006-tests-ecrivaient-en-production.md) a précisément établi cette séparation |
| 6 | La chaîne est **en état de marche** : les métriques sont évaluées et restituées | ✅ partiel | Traces réelles depuis le 02/10 18:39 (captures d'Era) ; les deux alertes ont sonné pour de vrai le 04/10 et ouvert l'issue #77 (`preuve-alertes-2026-10-04.md`) ; reste partiel parce que le serveur Hetzner n'envoie encore aucune trace |
| 7 | Les **sources** sont versionnées sur un dépôt distant | ✅ | `src/traces.py`, `api/main.py`, `graph/workflow.py`, `.github/workflows/alerte-incident.yml`, dépôt `Ganda15/rita-agent` |
| 8 | La **documentation technique** couvre l'installation, la configuration et l'utilisation | ✅ partiel | `docs/EXPLOITATION.md`, section « Monitorage Langfuse et alertes » (variables, tableau, alertes, test de la chaîne) |
| 9 | La documentation est communiquée dans un format **accessible** | ✅ 04/10 | Markdown dans le dépôt ; rapport E3 v1.1 en PDF de 20 pages (`docs/rapports/E3/rapport-E3.pdf`), relu page par page |

**Bilan honnête au 03/10 : 6 critères tenus, 1 partiel, 2 à faire** (le 02/10 : 5, 1, 3). Les deux manquants sont
l'accessibilité à argumenter et le PDF du rapport E3 ; les alertes (critère 6) restent à régler dans l'interface, voir
`preuve-langfuse-2026-10-03.md`.

**Mise à jour du 04/10 :** les alertes sont réglées et ont sonné (`preuve-alertes-2026-10-04.md`), les 15 traces
factices sont supprimées. Le décompte ne change pas : le critère 6 reste partiel tant que le serveur ne trace pas, et
les critères 4 et 9 attendent le rapport E3.

**État au 04/10 au soir : 7 critères tenus, 2 partiels, 0 à faire.** Le critère 9 est tenu (rapport E3 v1.1 en PDF) ;
le critère 4 est argumenté mais reste partiel ; le critère 6 reste partiel (serveur non tracé). Les deux alertes sont
revenues à l'état normal (constaté dans l'interface le 04/10 au soir lors d'une relecture ; capture d'Era à ranger).
**Défaut trouvé dans le tableau de bord** : la tuile « Générations par fournisseur » (filtre `type = GENERATION`,
regroupée par nom) compte aussi `briefing-llm`, qui n'est pas un fournisseur : le 02/10, la première instrumentation
l'enregistrait comme génération (6 observations, lues par l'API) ; depuis le 03/10 (commit `334a934`) c'est une étape.
**Corrigé le 04/10 au soir** (décision d'Era) par l'API : `PATCH /api/public/unstable/dashboard-widgets/{id}` (format lu
dans l'OpenAPI de Langfuse), réponse 200 ; seul le champ `filters` change : `type = GENERATION` **et** `name` parmi
`llm-foundry`, `llm-anthropic`, `llm-openrouter` ; type de graphique, regroupement et mesures relus inchangés. Avant et
après : `tuile-generations-par-fournisseur-2026-10-04.json`.
**Renommée le même soir** après une relecture : les barres comptent des **tentatives** d'appel, réussies et en échec,
pas des briefings servis. Mesure par l'API sur 7 jours : Foundry 5 (2 réussies, 3 en échec), Anthropic 3 (0 réussie,
3 en échec, clés absentes le 02 et le 03/10), OpenRouter 3 (3 réussies). La tuile s'appelle désormais « Tentatives par
fournisseur (échecs compris) », avec une description qui renvoie à la tuile des erreurs (PATCH 200, relu ; filtres,
regroupement et mesures inchangés). **Non obtenu** : les étiquettes de valeur sur les barres (`show_value_labels`)
ont été envoyées, l'API a répondu 200 mais ne les a pas gardées ; l'axe commence toujours à 3 et l'API publique n'a
aucun réglage d'axe (schéma OpenAPI lu) : l'éditeur de la tuile dans l'interface reste à regarder pour un axe à zéro.
Avant et après : `tuile-renommage-2026-10-04.json`.

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
| Alerte Langfuse vers une issue `incident` | `.github/workflows/alerte-incident.yml` | `tests/test_alerte_incident.py` (10 tests depuis le 04/10, dont 2 qui jouent le vrai script sur la charge utile de Langfuse) |
| La suite de tests ne trace jamais | `tests/conftest.py` | `tests/test_llm.py::test_la_suite_de_tests_n_envoie_jamais_de_trace` |

Suite complète le 02/10 au soir : `C:\Python314\python.exe -m pytest -q` : **626 passed, 2 xfailed** ;
couverture 93,66 % (seuil 90 %), `api/main.py` et `graph/workflow.py` à 100 %.

## Ce qui manque, et qui le fait

| Manque | Qui | Preuve attendue ici |
|---|---|---|
| Capture de la première trace réelle (02/10 18:39) et de la hiérarchie complète après le 02/10 au soir | Era, interface Langfuse | `capture-2026-10-02-premiere-trace.png`, `capture-trace-complete.png` |
| Suppression des **15** lignes factices (INC-006) : **faite par Era le 04/10**, constatée par l'API à 11:44:47 (7 traces, 0 « prompt test ») | fait | `preuve-alertes-2026-10-04.md`, section 1 ; export d'avant : `inc-006-traces-factices-avant-suppression-2026-10-03.json` |
| Tableau « RITA C11 » : **construit par l'API le 03/10** (`dashboard-rita-c11-2026-10-03.json`) ; reste la capture | Era, Dashboards | `capture-2026-10-03-dashboard-rita-c11.png` |
| Les 2 alertes, canal GitHub Actions : **faites le 04/10** (ERROR sur 1 jour ; p95 de `briefing-llm` au-dessus de 15 000 ms sur 1 jour). L'alerte « aucune trace en 24 h » prévue au départ a été remplacée par la latence : deux alertes seulement au palier gratuit | fait ; seuil de latence à revoir après une semaine | `preuve-alertes-2026-10-04.md`, `capture-2026-10-04-alerte-latence-seuil-15000.webp`, issue #77 |
| Retour à OK des deux alertes | constaté le 04/10 au soir dans l'interface ; capture encore à ranger | capture de la liste des alertes |
| Test manuel de la chaîne (bouton Run workflow) : **fait le 03/10 à 13 h 50**, juste après la fusion de la PR #58 (le bouton n'existait pas avant : `workflow_dispatch` ne vaut que sur la branche par défaut). Run `37120911852` en succès, issue **#71** créée avec le label `incident`, puis fermée comme issue de démonstration | fait | https://github.com/Ganda15/rita-agent/issues/71 |
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
