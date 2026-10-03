# INC-006 : douze générations de test sont apparues dans le projet Langfuse de production

> Trouvé le 02/10/2026 vers 19 h **en lisant l'interface Langfuse**, pas en lisant le code : Era
> voulait voir sa première trace réelle et a trouvé, au-dessus, douze lignes « prompt test »
> suivies de « ok anthropic ». Aucune n'était un vrai briefing.

| | |
|---|---|
| **Détecté le** | 02/10/2026, vers 19 h, par lecture de l'interface Langfuse (capture d'Era) |
| **Sévérité** | **P3** : aucune donnée personnelle, aucun effet sur le service ; mais douze fausses mesures dans le projet de production, donc un tableau de bord et une alerte faussés avant d'exister |
| **Durée** | de 18:25 (première ligne) à 19:14 (commit du correctif) : moins d'une heure |
| **Impact réel** | 12 générations factices dans le projet `rita` (région UE), à supprimer à la main dans l'interface : **pas encore fait au 02/10 au soir** |
| **Commit du correctif** | `7cf3ffd` (02/10/2026 19:14), dans le même commit que le traçage lui-même |
| **Issue / demande de fusion** | **aucune, commit direct sur `develop`**. La chaîne du `README.md` (issue, branche, PR) n'a pas été suivie : trouvé et corrigé dans la même heure, pendant le travail sur le traçage. La règle reste la règle ; ce manquement est dit ici, pas maquillé |

## 1. Ce qu'on a vu *(critère 1 : le symptôme, avant la cause)*

Dans Langfuse, onglet Tracing, projet `rita`, le 02/10 entre 18:25 et 18:38 : douze observations de
type génération, nom `llm-anthropic`, entrée « prompt test », sortie « ok anthropic ». La première
vraie trace (entrée : le prompt d'un briefing, sortie « Bonjour ») n'arrive qu'à 18:39.

« prompt test » et « ok anthropic » ne sont écrits nulle part dans le code de production.

## 2. Cause racine *(critère 1)*

**Cause technique.** `api/main.py` appelle `load_dotenv()` à l'import : dès qu'un test d'API importe
l'application, les vraies clés Langfuse du fichier d'environnement entrent dans le processus de
test. Les tests de `tests/test_llm.py` simulent les fournisseurs (`patch("src.llm._appel_anthropic",
return_value="ok anthropic")`) mais pas le traçage : `src/traces.py` voyait des clés, construisait un
vrai client, et envoyait chaque appel simulé à la production. Douze tests de cascade, douze lignes.

**Cause de conception.** Le module de traçage décidait « actif ou non » sur un seul critère, la
présence des clés. Rien ne distinguait un processus de test d'un processus de production, et rien ne
le testait. Le défaut était invisible depuis le code : la suite était verte, et elle le serait restée.
Il n'était visible que depuis l'extérieur, dans l'outil de surveillance. C'est la leçon du brief
Sorabel reprise dans `CONTINUITE.md` : confronter ce que le code déclare à ce qu'un client tiers voit.

## 3. Reproduction en développement *(critère 2)*

Le mécanisme se reproduit sans réseau, avec des clés factices dans le processus (02/10/2026) :

```
C:\Python314\python.exe -c "import os; os.environ['LANGFUSE_PUBLIC_KEY']='pk-test-reproduction'; os.environ['LANGFUSE_SECRET_KEY']='sk-test-reproduction'; os.environ.pop('LANGFUSE_TRACING_ENABLED', None); from src import traces; traces.reinitialiser(); print(type(traces.client_traces()).__name__)"
1. clés présentes, drapeau absent (état d'AVANT le correctif) : client = Langfuse
2. clés présentes, LANGFUSE_TRACING_ENABLED=false (ce que conftest.py pose) : client = None
```

Avant le correctif, la ligne 1 est l'état de tout processus de test après le premier import de
l'API : un client réel. La ligne 2 est l'état que `tests/conftest.py` impose maintenant.

## 4. Procédure de débogage *(critère 3)*

| # | Hypothèse | Comment elle a été testée | Résultat |
|---|---|---|---|
| 1 | Les douze lignes viennent d'appels réels ratés pendant la mise au point | lecture des entrées : « prompt test », jamais un vrai prompt | écartée |
| 2 | La chaîne « prompt test » vient du code de production | `grep -rn "prompt test"` : seulement `tests/test_llm.py` | la source est la suite de tests |
| 3 | Les tests n'ont pas de clés, ils ne peuvent pas tracer | lecture de `api/main.py` : `load_dotenv()` à l'import, et `tests/test_health.py` importe l'application | les clés entrent dès le premier test d'API |
| 4 | Retirer `load_dotenv()` de l'API | le serveur et le conteneur lisent leurs variables par ce chemin | écartée : casserait la production pour un défaut de test |
| 5 | Couper le traçage pour toute la suite par une fixture automatique | `LANGFUSE_TRACING_ENABLED=false` est déjà lu par `src/traces.py` avant toute autre chose | retenue |

Débogage fait dans le chat de la session du 02/10, pas dans une issue : critère 3 non suivi pour
cet incident (voir l'en-tête).

## 5. Correction, étape par étape *(critère 4)*

1. **Test d'abord** : `tests/test_llm.py::test_la_suite_de_tests_n_envoie_jamais_de_trace` pose
   des clés factices et exige `client_traces() is None`. Rouge avant le correctif.
2. **Fixture automatique** `couper_le_tracage` dans `tests/conftest.py` : pose
   `LANGFUSE_TRACING_ENABLED=false` et appelle `traces.reinitialiser()` avant et après chaque
   test, pour oublier un client qu'un test précédent aurait résolu. Les tests qui veulent un client
   posent eux-mêmes un double (`tests/test_traces.py`).
3. Pourquoi ce choix : il ne touche pas au code de production, il protège toute la suite d'un
   coup, et il s'appuie sur un interrupteur qui existait déjà pour l'exploitation.

## 6. Vérification et non-régression *(critères 2 et 5)*

```
C:\Python314\python.exe -m pytest "tests/test_llm.py::test_la_suite_de_tests_n_envoie_jamais_de_trace" -q
1 passed in 2.58s
```

Suite complète après le correctif, le 02/10 : 586 passed, 2 xfailed. Au soir du 02/10, après les
étapes suivantes du traçage : 626 passed, 2 xfailed. Aucune nouvelle ligne factice n'est apparue
dans Langfuse pendant ces exécutions (à confirmer par Era dans l'interface : seules les traces
« briefing » réelles doivent figurer après 19:14).

**Test de non-régression** : `tests/test_llm.py::test_la_suite_de_tests_n_envoie_jamais_de_trace`

## 7. Ce que ça change pour la suite

- **Fait** : la suite de tests ne peut plus tracer, quelles que soient les variables du poste.
- **À faire par Era** : supprimer les lignes factices dans l'interface Langfuse (projet `rita`), et
  garder une capture avant suppression dans `evidence/C11/`.
  **Complément du 03/10** : relues par l'API, elles sont **quinze**, pas douze : une troisième série de trois
  à 18 h 42 (heure de Paris) manquait au décompte du 02/10 au soir. Export d'avant suppression :
  `evidence/C11/inc-006-traces-factices-avant-suppression-2026-10-03.json`. La suppression par l'agent a été
  refusée par l'outil de développement (suppression de masse chez un tiers) ; les clics sont dans
  `evidence/C11/preuve-langfuse-2026-10-03.md`, section 3.1.
- **À décider** : un second projet Langfuse `rita-dev` pour le poste de développement, afin que
  même un appel réel fait à la main pendant le travail n'entre pas dans les mesures de production.
  Coût : zéro (le palier gratuit accepte plusieurs projets). Non fait au 02/10.
- **Règle de processus** : le prochain incident suit la chaîne issue, branche, PR, même s'il est
  corrigé en dix minutes. Cet incident montre pourquoi la règle existe : sans issue, le débogage
  n'est écrit que dans un chat.
