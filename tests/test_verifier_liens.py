"""Le vérificateur de liens, sur les liens du dépôt privé (24/10/2026).

Le dépôt est privé : une requête anonyme reçoit 404 même sur un lien valide. Le script retente avec `gh`, qui est
authentifié, mais ne savait le faire que pour `/tree/<ref>`. 116 liens (fichiers, PR, issues, passages de CI) restaient
« non vérifiables », et la règle « zéro lien cassé avant un tag » bloquait les tags E1 et E3. Ici, chaque forme d'URL
du dépôt correspond à une question précise posée à l'API de GitHub. Aucun appel réseau dans ces tests.
"""
import subprocess
from unittest.mock import patch

import pytest

from scripts import verifier_liens as v

DEPOT = "https://github.com/Ganda15/rita-agent"
API = "repos/Ganda15/rita-agent"


@pytest.mark.parametrize("url, attendu", [
    (f"{DEPOT}/blob/main/docs/exploitation.md#L12", f"{API}/contents/docs/exploitation.md?ref=main"),
    (f"{DEPOT}/blob/livrable-sprint-4-v2/evidence/sprint-4/README.md?plain=1",
     f"{API}/contents/evidence/sprint-4/README.md?ref=livrable-sprint-4-v2"),
    (f"{DEPOT}/tree/livrable-E1-v1", f"{API}/contents/?ref=livrable-E1-v1"),
    (f"{DEPOT}/tree/main/docs/rapports", f"{API}/contents/docs/rapports?ref=main"),
    (f"{DEPOT}/pull/133", f"{API}/pulls/133"),
    (f"{DEPOT}/pull/93/files", f"{API}/pulls/93"),
    (f"{DEPOT}/issues/128", f"{API}/issues/128"),
    (f"{DEPOT}/actions/runs/39995996403", f"{API}/actions/runs/39995996403"),
    (f"{DEPOT}/actions/runs/39995996403/job/120861234", f"{API}/actions/runs/39995996403"),
    (f"{DEPOT}/actions/workflows/livraison.yml", f"{API}/actions/workflows/livraison.yml"),
    (f"{DEPOT}/commit/d215617f7cffa7a9817da28f2b2684dc7c63f7cd", f"{API}/commits/d215617f7cffa7a9817da28f2b2684dc7c63f7cd"),
])
def test_chaque_forme_de_lien_du_depot_a_sa_question_a_l_api(url, attendu):
    assert v.point_api_github(url) == attendu


def test_une_forme_inconnue_reste_non_verifiable_et_le_dit():
    """Mieux vaut un « je ne sais pas vérifier » écrit qu'un faux « bon »."""
    with patch("subprocess.run") as gh:
        verdict = v.verifier_github_prive(f"{DEPOT}/settings")
    assert verdict and "non vérifiable" in verdict
    gh.assert_not_called()


def test_un_lien_que_gh_trouve_est_bon():
    with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0)) as gh:
        assert v.verifier_github_prive(f"{DEPOT}/pull/133") is None
    assert gh.call_args.args[0] == ["gh", "api", f"{API}/pulls/133"]


def test_un_lien_que_gh_ne_trouve_pas_est_casse_et_le_dit():
    """Le cas qui compte : un fichier renommé (EXPLOITATION.md devenu exploitation.md le 22/10)."""
    with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 1)):
        verdict = v.verifier_github_prive(f"{DEPOT}/blob/main/docs/EXPLOITATION.md")
    assert verdict and "introuvable" in verdict
