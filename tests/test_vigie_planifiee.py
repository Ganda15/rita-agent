"""La vigie tourne seule, à heure fixe, contre la production (E5, C20.5 ; 06/11/2026).

Pourquoi : `monitorage/vigie.py` sonde `/health`, lit `/sante` et ouvre une issue `incident` par signal en problème, mais
elle était lancée à la main (rapport E5, § 6 : « vigie lancée à la main »). Une alerte qui dépend de quelqu'un qui pense à
la lancer n'est pas une alerte en état de marche. Ce workflow la lance toutes les trois heures, et à la demande.

Le fichier de workflow est un contrat : on le teste comme du code, comme `alerte-incident.yml`.
"""
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).parent.parent
CHEMIN = RACINE / ".github/workflows/vigie.yml"
PRODUCTION = "https://178-104-184-125.sslip.io"


@pytest.fixture(scope="module")
def flux():
    assert CHEMIN.exists(), "workflow .github/workflows/vigie.yml absent"
    return yaml.safe_load(CHEMIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def job(flux):
    (seul,) = flux["jobs"].values()
    return seul


def test_la_vigie_tourne_a_heure_fixe_et_a_la_demande(flux):
    declencheurs = flux.get("on") if "on" in flux else flux.get(True)   # PyYAML lit `on` comme True
    assert set(declencheurs) == {"schedule", "workflow_dispatch"}
    assert declencheurs["schedule"] == [{"cron": "17 */3 * * *"}]


def test_le_jeton_ne_peut_qu_ecrire_des_issues(flux):
    assert flux["permissions"] == {"issues": "write", "contents": "read"}


def test_deux_passages_ne_se_chevauchent_pas_et_le_job_est_borne(job):
    assert job["concurrency"] == {"group": "vigie", "cancel-in-progress": False}
    assert job["timeout-minutes"] <= 10


def test_la_vigie_vise_la_production_et_agit_pour_de_vrai(job):
    lancement = [e for e in job["steps"] if "monitorage.vigie" in e.get("run", "")]
    assert len(lancement) == 1
    assert f"--adresse {PRODUCTION}" in lancement[0]["run"]
    assert "--github" in lancement[0]["run"]


def test_la_cle_vient_d_un_secret_et_n_est_jamais_affichee(job):
    lancement = next(e for e in job["steps"] if "monitorage.vigie" in e.get("run", ""))
    assert lancement["env"]["RITA_API_KEY"] == "${{ secrets.RITA_API_KEY_VIGIE }}"
    assert lancement["env"]["GH_TOKEN"] == "${{ github.token }}"
    texte = CHEMIN.read_text(encoding="utf-8")
    assert "echo $RITA_API_KEY" not in texte and 'echo "$RITA_API_KEY"' not in texte
    assert "set -x" not in texte


def test_sans_secret_le_passage_s_arrete_en_le_disant(job):
    garde = [e for e in job["steps"] if "RITA_API_KEY_VIGIE" in e.get("name", "")]
    assert len(garde) == 1
    assert "::error::" in garde[0]["run"]


def test_le_guide_d_exploitation_dit_que_la_vigie_tourne_seule_et_ce_qu_il_faut_pour_cela():
    guide = (RACINE / "docs/exploitation.md").read_text(encoding="utf-8")
    section = guide.split('<a id="vigie-et-exercices"></a>')[1].split("### La panne simulée")[0]
    assert ".github/workflows/vigie.yml" in section and "RITA_API_KEY_VIGIE" in section
    assert "sans lancement, la vigie ne tourne pas" not in section
