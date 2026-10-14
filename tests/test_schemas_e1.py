"""Les schémas du rapport E1 disent ce que dit le code, et restent à jour (C1, C3).

Pourquoi ce test (04/10/2026) : le schéma de collecte du 11/08 (`evidence/C1/SCHEMA-C1-...`)
affichait « 9 motifs, 100 % blocage » pour le garde-fou d'injection, et « 8 tables ». Au 04/10,
le code compte 12 motifs, la mesure donne 70 % et la base 10 tables. Un schéma dessiné à la main
vieillit sans bruit, et un jury qui lit 100 % ici et 70 % dans le rapport E3 voit une contradiction.

Ici les chiffres viennent du code au moment de la génération (`faits()`), et deux contrôles
empêchent la dérive : chaque chiffre affiché est celui du code, et le fichier rangé est
exactement ce que le générateur produit aujourd'hui.
"""
import importlib.util
import re
from pathlib import Path

import pytest

RACINE = Path(__file__).parent.parent
DOSSIER = RACINE / "docs/rapports/E1/schemas"
NOMS = ("E1-collecte", "E1-nettoyage")


@pytest.fixture(scope="module")
def gen():
    chemin = DOSSIER / "generer_schemas.py"
    assert chemin.exists(), "générateur docs/rapports/E1/schemas/generer_schemas.py absent"
    spec = importlib.util.spec_from_file_location("schemas_e1", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def faits(gen):
    return gen.faits()


@pytest.mark.parametrize("nom", NOMS)
@pytest.mark.parametrize("ext", ("drawio", "svg", "png"))
def test_chaque_schema_existe_en_drawio_svg_et_png(nom, ext):
    """Règle du dépôt : un .drawio pour corriger, une image pour voir."""
    assert (DOSSIER / f"{nom}.{ext}").exists(), f"{nom}.{ext} absent"


def test_les_faits_sont_lus_dans_le_code_pas_recopies(faits):
    import guardrails.injection as inj
    import sources.rss as rss
    schema = (RACINE / "db/schema.sql").read_text(encoding="utf-8")
    assert faits["tables"] == len(re.findall(r"CREATE TABLE", schema, re.I))
    assert faits["check"] == len(re.findall(r"\bCHECK\s*\(", schema))
    assert faits["motifs_injection"] == len(inj.MOTIFS)
    assert faits["flux_generaux"] == len(rss.FLUX)


def test_le_taux_de_blocage_affiche_est_celui_mesure(faits):
    from evals.mesurer_gardefou import mesurer
    assert faits["blocage_injection"] == round(mesurer()["taux_blocage"])


@pytest.mark.parametrize("nom", NOMS)
def test_le_fichier_range_est_celui_que_produit_le_generateur(gen, nom):
    """Si le code change (une table, un motif, une mesure) sans que le schéma soit régénéré,
    ce test tombe : c'est lui qui empêche le schéma de vieillir en silence."""
    schema = gen.SCHEMAS[nom]()
    assert (DOSSIER / f"{nom}.svg").read_text(encoding="utf-8") == gen.svg(schema), \
        f"{nom}.svg n'est plus à jour : relancer generer_schemas.py, puis le rendu PNG"
    assert (DOSSIER / f"{nom}.drawio").read_text(encoding="utf-8") == gen.drawio(schema)


def test_le_schema_de_collecte_affiche_les_chiffres_du_code(gen, faits):
    texte = gen.svg(gen.SCHEMAS["E1-collecte"]())
    assert f"{faits['tables']} tables" in texte
    assert f"{faits['motifs_injection']} motifs" in texte
    assert f"{faits['blocage_injection']} % de blocage" in texte
    assert "100 % blocage" not in texte and "100 % de blocage" not in texte
    t, p = faits["traitements_rgpd"], faits["procedures_rgpd"]
    assert f"traitements {t[0]} à {t[-1]}" in texte, "les traitements du registre RGPD ne sont pas ceux du schéma"
    assert f"procédures de tri {p[0]} à {p[-1]}" in texte, "les procédures du registre RGPD ne sont pas celles du schéma"


def test_le_schema_de_nettoyage_relie_chaque_regle_a_son_fichier(gen):
    """C3 : une règle de nettoyage sans son fichier n'est pas vérifiable par le jury."""
    texte = gen.svg(gen.SCHEMAS["E1-nettoyage"]())
    for fichier in ("db/importer.py", "db/schema.sql", "sources/marches.py", "sources/positions.py"):
        assert fichier in texte, f"{fichier} n'est cité nulle part dans le schéma de nettoyage"
        assert (RACINE / fichier).exists(), f"{fichier} cité mais absent du dépôt"
