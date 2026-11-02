"""Le diagramme de flux de données à jour (C15.3) est celui que le générateur écrit ; l'ancien du 18/08 est gardé.

Relevé le 02/11/2026 sur le code (`evidence/C15/flux/generer_flux.py`). Un `.svg` ou un `.drawio` retouché à la main
divergerait du générateur sans que rien ne le dise ; une ligne trop longue sortirait de sa boîte ; et une nouvelle
version ne remplace pas l'ancienne, elle s'y ajoute.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).parent.parent
DOSSIER = RACINE / "evidence/C15/flux"
NOM = "FLUX-DONNEES-C15-application-RITA-2026-11-02"
PREUVE = RACINE / "evidence/C15/preuve-flux-donnees-2026-11-02.md"


@pytest.fixture(scope="module")
def gen():
    spec = importlib.util.spec_from_file_location("flux_c15_test", DOSSIER / "generer_flux.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["flux_c15_test"] = module   # dataclass relit son module dans sys.modules
    spec.loader.exec_module(module)
    return module


def test_aucun_texte_ne_deborde_de_sa_boite(gen):
    assert gen.moteur.debordements(gen.FLUX) == []


def test_le_diagramme_dit_qu_il_est_une_nouvelle_version_et_le_sens_des_fleches(gen):
    textes = " ".join(b.titre + " " + " ".join(b.lignes) for b in gen.FLUX.boites)
    assert "18/08" in textes and "sens de la donnée" in textes


def test_les_flux_de_donnees_personnelles_sont_marques(gen):
    assert any(f.sens == "perso" for f in gen.FLUX.fleches)


def test_les_fichiers_publies_sont_ceux_du_generateur(gen):
    assert (DOSSIER / f"{NOM}.svg").read_text(encoding="utf-8") == gen.moteur.svg(gen.FLUX)
    assert (DOSSIER / f"{NOM}.drawio").read_text(encoding="utf-8") == gen.moteur.drawio(gen.FLUX)
    assert (DOSSIER / f"{NOM}.png").stat().st_size > 0


def test_l_ancien_diagramme_du_18_08_est_garde():
    for extension in ("png", "svg"):
        assert (RACINE / f"evidence/C15/FLUX-DONNEES-C15-application-RITA.{extension}").stat().st_size > 0


def test_la_preuve_montre_le_nouveau_diagramme():
    assert f"](flux/{NOM}.png)" in PREUVE.read_text(encoding="utf-8")
