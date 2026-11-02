"""Les schémas de parcours des écrans 4 et 5 (C14.2) sont ceux que le générateur écrit, et aucun texte ne déborde.

Relevés le 02/11/2026 sur la version actuelle (`evidence/C14/parcours/generer_parcours.py`). Un `.svg` ou un `.drawio`
retouché à la main divergerait du générateur sans que rien ne le dise ; une ligne trop longue sortirait de sa boîte.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).parent.parent
DOSSIER = RACINE / "evidence/C14/parcours"
NOMS = ("PARCOURS-C14-ecran-question", "PARCOURS-C14-ecran-tableau-de-bord")


@pytest.fixture(scope="module")
def gen():
    spec = importlib.util.spec_from_file_location("parcours_c14_test", DOSSIER / "generer_parcours.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["parcours_c14_test"] = module   # dataclass relit son module dans sys.modules
    spec.loader.exec_module(module)
    return module


def test_les_deux_parcours_sont_decrits(gen):
    assert tuple(s.nom for s in gen.SCHEMAS) == NOMS


def test_aucun_texte_ne_deborde_de_sa_boite(gen):
    assert [d for s in gen.SCHEMAS for d in gen.moteur.debordements(s)] == []


def test_chaque_schema_dit_qu_il_est_un_releve_et_pas_une_maquette(gen):
    for schema in gen.SCHEMAS:
        assert any(b.titre == "Relevé du jour, pas une maquette initiale" for b in schema.boites), schema.nom


@pytest.mark.parametrize("nom", NOMS)
def test_les_fichiers_publies_sont_ceux_du_generateur(gen, nom):
    schema = next(s for s in gen.SCHEMAS if s.nom == nom)
    assert (DOSSIER / f"{nom}.svg").read_text(encoding="utf-8") == gen.moteur.svg(schema)
    assert (DOSSIER / f"{nom}.drawio").read_text(encoding="utf-8") == gen.moteur.drawio(schema)
    assert (DOSSIER / f"{nom}.png").stat().st_size > 0


def test_la_preuve_c14_montre_les_deux_parcours():
    preuve = (RACINE / "evidence/C14/preuve-specifications-ecrans-4-et-5.md").read_text(encoding="utf-8")
    for nom in NOMS:
        assert f"](parcours/{nom}.png)" in preuve, f"{nom} absent de la preuve"
