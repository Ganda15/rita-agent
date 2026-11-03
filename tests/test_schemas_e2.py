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


def test_les_schemas_disent_l_envoi_du_03_11(gen):
    # Le 03/11, la synthèse de veille et le guide sont envoyés au formateur (evidence/C8/) : plus de « non effectué ».
    textes = {s.nom: gen.moteur.svg(s) for s in gen.SCHEMAS}
    assert "envoi au formateur non effectué" not in textes["E2-veille"]
    assert "envoi au formateur le 03/11, sans réponse" in textes["E2-veille"]
    assert "remise prévue le 05/11" not in textes["E2-service-aujourdhui"]
    assert "envoyé au formateur le 03/11" in textes["E2-service-aujourdhui"]


def test_mistral_est_dit_teste_et_non_active(gen):
    # Décision d'Era du 03/11 : Mistral Large 4 a servi un vrai briefing le 10/10 (branche mistral-ue), il n'est pas
    # activé en production ; le secours attend un banc sur 10 cas contre Azure UE et la lecture du contrat.
    textes = {s.nom: gen.moteur.svg(s) for s in gen.SCHEMAS}
    assert "futur second, sous" not in textes["E2-banc-decision"]
    assert "briefing LVMH" in textes["E2-banc-decision"] and "non activé en production" in textes["E2-banc-decision"]
    assert "pas encore lu" not in textes["E2-service-aujourdhui"]
    assert "secours envisagé" in textes["E2-service-aujourdhui"]
    assert "contrat à vérifier" in textes["E2-service-aujourdhui"]


def test_l_annexe_montre_les_trois_schemas():
    # Depuis le 03/11, l'annexe peut montrer une mise en forme (`<nom>-illustre.png`) ; elle cite alors l'original du
    # générateur, seul à faire foi pour le texte.
    annexe = (RACINE / "docs/rapports/E2/annexe-schemas-E2.md").read_text(encoding="utf-8")
    for nom in NOMS:
        illustre = f"](schemas/{nom}-illustre.png)" in annexe
        assert illustre or f"](schemas/{nom}.png)" in annexe, f"{nom} absent de l'annexe"
        if illustre:
            assert (DOSSIER / f"{nom}-illustre.png").stat().st_size > 0
            assert f"schemas/{nom}.svg" in annexe, f"{nom} : la mise en forme doit citer l'original du générateur"
