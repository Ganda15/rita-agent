# Le marqueur `postgresql` remplace la recherche du mot `dsn_de_test` (02/11/2026, 00 h 25 à 00 h 30)

Constitué dans la foulée, à partir des sorties réelles, sur le poste (local, non commité au moment de l'écriture).
Le job `base` choisissait ses fichiers par `grep -l dsn_de_test tests/*.py` : fragile, `tests/test_ci_base.py` y entrait
parce qu'il cite le mot. Il choisit désormais `pytest -m postgresql tests`. Un garde-fou dans `tests/garde_base.py` fait
échouer tout test qui demande la base sans le marqueur : sans lui, un test oublié serait sauté dans le job `pytest` et
jamais choisi par le job `base`.

## 1. Tests écrits avant (rouge, puis vert)

Commande : `PYTHON_DOTENV_DISABLED=1 C:\Python314\python.exe -m pytest -q -p no:cacheprovider --no-cov
tests/test_garde_base.py tests/test_ci_base.py`

```
AVANT (00 h 25, code inchange) :
FAILED tests/test_garde_base.py::test_la_base_declaree_rend_l_adresse
FAILED tests/test_garde_base.py::test_une_base_non_declaree_est_sautee_sans_montrer_l_url
FAILED tests/test_garde_base.py::test_sans_base_declaree_tout_est_saute
FAILED tests/test_garde_base.py::test_sans_database_url_tout_est_saute
FAILED tests/test_garde_base.py::test_un_test_qui_demande_la_base_sans_le_marqueur_echoue
FAILED tests/test_garde_base.py::test_un_test_marque_passe_le_controle
FAILED tests/test_garde_base.py::test_hors_d_un_test_le_controle_echoue_aussi
FAILED tests/test_garde_base.py::test_dsn_de_test_applique_le_controle
FAILED tests/test_garde_base.py::test_le_registre_des_tests_marques_suit_la_collecte
FAILED tests/test_ci_base.py::test_le_job_choisit_les_tests_par_le_marqueur_postgresql
FAILED tests/test_ci_base.py::test_le_marqueur_postgresql_est_declare
11 failed, 6 passed, 1 warning in 3.38s
APRES :
17 passed, 1 warning in 3.34s
```

Les quatre premiers échecs viennent des tests existants, qui appellent désormais `adresse_de_la_base_de_test()` (la
logique de l'adresse, séparée du contrôle du marqueur) ; leur comportement attendu n'a pas changé.

## 2. Les mêmes tests, nom par nom

Référence : `evidence/C18/tests-postgresql-avant-marqueur-2026-11-02.txt` (les 24 tests sautés sans base dans la
sélection par le mot). Après : `pytest --collect-only -q -m postgresql tests`.

```
24/1926 tests collected (1902 deselected) in 6.95s
reference : 24 tests | marqueur : 24 tests
diff des deux listes triees : aucune difference
```

## 3. La commande du job, rejouée sur une base jetable

`postgres:18-alpine`, `127.0.0.1:55432`, compte `rita` en mode `trust` (aucun mot de passe), schéma puis rôles du
dépôt ; conteneur détruit ensuite. Commande : `pytest -q -rs --no-cov -m postgresql tests | tee sortie-base.txt`, puis
le contrôle des sauts du job.

```
avec la base : 24 passed, 1902 deselected, 1 warning in 6.05s -> aucun 'skipped' : code 0
sans base    : 24 skipped, 1902 deselected, 1 warning in 5.37s -> 'skipped' present : code 1
aucun test choisi (pytest -m marqueur_inexistant) : code de sortie 5, le job echoue aussi
```

## 4. Le garde-fou mis à l'épreuve (mutation)

Le décorateur `@pytest.mark.postgresql` est retiré de
`tests/test_vue_valorisation.py::test_en_base_avec_un_taux_present_la_conversion_est_juste` le temps d'un passage, puis
le fichier est restauré à l'octet près.

```
== sans base, le test non marque
tests/test_vue_valorisation.py::test_en_base_avec_un_taux_present_la_conversion_est_juste demande PostgreSQL sans le marqueur « postgresql » : ajouter @pytest.mark.postgresql (ou pytestmark dans le fichier), sinon le job base de l
1 warning, 1 error in 3.10s
== avec la base, le meme test
tests/test_vue_valorisation.py::test_en_base_avec_un_taux_present_la_conversion_est_juste demande PostgreSQL sans le marqueur « postgresql » : ajouter @pytest.mark.postgresql (ou pytestmark dans le fichier), sinon le job base de l
1 warning, 1 error in 3.15s
== selection du job
23/1926 tests collected (1903 deselected) in 5.27s
```

Sans le marqueur, le test n'est plus sauté en silence : il échoue, avec ou sans base, et le message nomme le test et
dit quoi ajouter ; la sélection du job tombe à 23, ce qui se voit.

## Ce qui reste

- Exécution sur GitHub : le job `base` doit montrer 24 réussis, 0 sauté, sur le commit qui porte ce changement.
