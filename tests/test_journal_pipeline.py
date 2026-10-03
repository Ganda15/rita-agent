"""Le journal de la collecte ne contient jamais la clé d'API FRED (C20, règle de journalisation).

Mesuré le 02/10/2026 : 6 des 40 journaux `logs/collecte-*.log` contenaient la clé FRED en
clair, dans des lignes `INFO HTTP Request: GET https://api.stlouisfed.org/...&api_key=...`.
Ce n'est pas notre code qui l'écrit : c'est la bibliothèque `httpx`, qui journalise chaque
requête avec son URL complète au niveau INFO, et la clé FRED se passe dans l'URL (c'est l'API
qui l'impose). Le pipeline règle la racine à INFO, donc `httpx` parle.

Le correctif : la configuration du journal du pipeline passe `httpx` à WARNING. Une requête
réussie ne s'écrit plus ; une requête en échec, si. Les journaux déjà écrits restent sur le
disque d'Era (ils ne sont pas versionnés) : la clé est à faire tourner chez FRED, décision d'Era.
"""
import logging
import subprocess
import sys

from pipelines.ingest import configurer_journal


def test_httpx_ne_parle_plus_au_niveau_info_apres_configuration():
    configurer_journal()
    assert logging.getLogger("httpx").isEnabledFor(logging.INFO) is False
    assert logging.getLogger("httpx").isEnabledFor(logging.WARNING) is True


def test_le_pipeline_lui_meme_reste_au_niveau_info_dans_un_processus_propre():
    """Sous pytest, la racine a déjà le capteur de pytest et `basicConfig` ne fait rien, par
    conception. La preuve utile se mesure comme en production : dans un processus neuf."""
    code = ("import logging; from pipelines.ingest import configurer_journal; configurer_journal(); "
            "print(logging.getLogger('pipelines.ingest').isEnabledFor(logging.INFO), "
            "logging.getLogger('httpx').isEnabledFor(logging.INFO))")
    sortie = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    assert sortie.stdout.strip().splitlines()[-1] == "True False", sortie.stderr[-400:]
