"""L'outil de calcul EcoIndex de la mesure du 07/11 n'écrit jamais là où on ne le lui a pas demandé (revue Claude Code
de #226). Sans fichier de sortie, il écrivait à côté du second dossier : lancé sur les relevés du 06/11, il aurait
ajouté un fichier dans une preuve d'une autre date, que le projet interdit de modifier après coup.
"""
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
MESURE = RACINE / "evidence/C17/mesures-2026-11-07-pagination"
SCRIPT = MESURE / "outils/calcul-ecoindex-2026-11-07.py"


def _copier_les_releves(dossier: Path) -> tuple[Path, Path]:
    for etat in ("avant", "apres"):
        (dossier / etat).mkdir()
        shutil.copy(MESURE / etat / "resume-bureau.json", dossier / etat / "resume-bureau.json")
    return dossier / "avant", dossier / "apres"


def test_sans_fichier_de_sortie_le_script_refuse_et_n_ecrit_rien(tmp_path):
    avant, apres = _copier_les_releves(tmp_path)
    fini = subprocess.run([sys.executable, str(SCRIPT), str(avant), str(apres)], capture_output=True, text=True)
    assert fini.returncode != 0
    assert sorted(p.name for p in tmp_path.iterdir()) == ["apres", "avant"], "aucun fichier écrit"


def test_avec_fichier_de_sortie_le_calcul_est_ecrit_la_ou_on_le_demande(tmp_path):
    avant, apres = _copier_les_releves(tmp_path)
    sortie = tmp_path / "resultat.json"
    fini = subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT), str(avant), str(apres), str(sortie)],
                          capture_output=True, text=True, encoding="utf-8")
    assert fini.returncode == 0, fini.stderr
    import json
    resultat = json.loads(sortie.read_text(encoding="utf-8"))
    assert (resultat["avant"]["indicateurs"]["note"], resultat["apres"]["indicateurs"]["note"]) == ("D", "B")
