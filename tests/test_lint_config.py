"""Sprint 2, tâche 2 : le lint de la chaîne.

La configuration ne sélectionne que les vraies erreurs (syntaxe, comparaisons invalides, instructions mal
placées, noms non définis) : on n'impose pas de style à un code existant de plus de 800 tests. La version de
ruff est la même dans `requirements.txt` et dans la chaîne, et le lint passe avant la construction, dans
l'ordre du brief : lint, tests, construction, déploiement.
"""
import re
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
LIVRAISON = RACINE / ".github" / "workflows" / "livraison.yml"


def test_ruff_ne_selectionne_que_les_vraies_erreurs():
    config = tomllib.loads((RACINE / "ruff.toml").read_text(encoding="utf-8"))
    assert config["target-version"] == "py313"
    assert config["lint"]["select"] == ["E9", "F63", "F7", "F82"]


def test_la_version_de_ruff_est_la_meme_dans_requirements_et_dans_la_chaine():
    exigee = re.search(r"^ruff==([0-9.]+)$", (RACINE / "requirements.txt").read_text(encoding="utf-8"), re.M)
    assert exigee, "ruff doit être fixé à une version exacte dans requirements.txt"
    installee = re.search(r'pip install "ruff==([0-9.]+)"', LIVRAISON.read_text(encoding="utf-8"))
    assert installee, "le travail lint doit installer ruff à une version fixée"
    assert exigee.group(1) == installee.group(1)


def test_le_lint_passe_avant_la_construction():
    texte = LIVRAISON.read_text(encoding="utf-8")
    assert re.search(r"^  lint:$", texte, re.M), "le travail lint doit exister dans livraison.yml"
    entete = texte.split("\n  construire-et-publier:\n", 1)[1].split("steps:", 1)[0]
    assert re.search(r"^    needs: lint$", entete, re.M), "construire-et-publier doit attendre lint"
