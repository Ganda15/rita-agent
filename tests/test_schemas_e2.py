"""Les schémas de l'annexe du rapport E2 sont ceux que le générateur écrit, et aucun texte ne déborde (01/11/2026).

Pourquoi : les trois schémas sont dessinés depuis une seule description (`docs/rapports/E2/schemas/generer_schemas.py`).
Un `.svg` ou un `.drawio` retouché à la main divergerait du générateur sans que rien ne le dise ; une ligne trop longue
sortirait de sa boîte une fois imprimée.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).parent.parent
DOSSIER = RACINE / "docs/rapports/E2/schemas"
NOMS = ("E2-veille", "E2-banc-decision", "E2-service-aujourdhui")


@pytest.fixture(scope="module")
def gen():
    chemin = DOSSIER / "generer_schemas.py"
    spec = importlib.util.spec_from_file_location("schemas_e2_test", chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules["schemas_e2_test"] = module   # dataclass relit son module dans sys.modules
    spec.loader.exec_module(module)
    return module


def test_les_trois_schemas_sont_decrits(gen):
    assert tuple(s.nom for s in gen.SCHEMAS) == NOMS


def test_aucun_texte_ne_deborde_de_sa_boite(gen):
    assert [d for s in gen.SCHEMAS for d in gen.moteur.debordements(s)] == []


@pytest.mark.parametrize("nom", NOMS)
def test_les_fichiers_publies_sont_ceux_du_generateur(gen, nom):
    schema = next(s for s in gen.SCHEMAS if s.nom == nom)
    assert (DOSSIER / f"{nom}.svg").read_text(encoding="utf-8") == gen.moteur.svg(schema)
    assert (DOSSIER / f"{nom}.drawio").read_text(encoding="utf-8") == gen.moteur.drawio(schema)
    assert (DOSSIER / f"{nom}.png").stat().st_size > 0


def test_l_annexe_montre_les_trois_schemas():
    annexe = (RACINE / "docs/rapports/E2/annexe-schemas-E2.md").read_text(encoding="utf-8")
    for nom in NOMS:
        assert f"](schemas/{nom}.png)" in annexe, f"{nom} absent de l'annexe"
