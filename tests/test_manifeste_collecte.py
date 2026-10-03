"""Le manifeste de collecte : un fichier JSON par exécution du pipeline (chapitre « Données » §1.3,
issue #64, C1 et C20).

Pourquoi : le journal raconte une exécution ligne par ligne ; le manifeste en fixe les faits en un
seul endroit, lisibles par un programme : par étape, lues / écrites / rejetées, durée, erreur ;
pour l'exécution, le mode, la période, le commit. Trois usages : la preuve C1 (« toutes les données
visées sont récupérées » devient un nombre par soir), la surveillance C20 (zéro article nouveau
trois soirs de suite est une alerte), et l'honnêteté du chapitre (« compter reçus / nouveaux /
rejetés séparément »).

Règles testées : seulement des nombres et des codes, jamais un texte d'article ni une clé d'API ;
deux exécutions le même jour ne s'écrasent pas ; une panne d'écriture n'échoue jamais la collecte.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from pipelines import ingest


def _resultat(**extra):
    base = {"bilans": [ingest.Bilan("articles (RSS)", lues=90, ecrites=51, rejetees=39,
                                    details=["flux OK 9/10 (dont 7 par entreprise)"]),
                       ingest.Bilan("macro (FRED)", erreur="HTTPStatusError: 403 sur ...?api_key=abcdef0123456789&file_type=json")],
            "simulation": False, "duree_s": 1545.0, "etapes_ok": 1}
    base.update(extra)
    return base


MOMENT = datetime(2026, 10, 3, 19, 0, 12)


def test_le_manifeste_porte_les_comptages_de_chaque_etape_et_le_bilan_de_l_execution(tmp_path):
    chemin = ingest.ecrire_manifeste(_resultat(), tmp_path, maintenant=MOMENT)
    m = json.loads(Path(chemin).read_text(encoding="utf-8"))
    assert m["version_manifeste"] == 1
    assert m["mode"] == "execution" and m["duree_s"] == 1545.0
    assert m["etapes_ok"] == 1 and m["etapes_total"] == 2
    rss = next(e for e in m["etapes"] if e["nom"] == "articles (RSS)")
    assert (rss["lues"], rss["ecrites"], rss["rejetees"], rss["ok"]) == (90, 51, 39, True)
    assert rss["details"] == ["flux OK 9/10 (dont 7 par entreprise)"]
    fred = next(e for e in m["etapes"] if e["nom"] == "macro (FRED)")
    assert fred["ok"] is False and fred["erreur"].startswith("HTTPStatusError")


def test_le_nom_du_fichier_porte_la_date_et_l_heure_du_lancement(tmp_path):
    chemin = ingest.ecrire_manifeste(_resultat(), tmp_path, maintenant=MOMENT)
    assert Path(chemin).name == "manifeste-2026-10-03-190012.json"


def test_deux_executions_le_meme_jour_ne_s_ecrasent_pas(tmp_path):
    a = ingest.ecrire_manifeste(_resultat(), tmp_path, maintenant=MOMENT)
    b = ingest.ecrire_manifeste(_resultat(), tmp_path, maintenant=datetime(2026, 10, 3, 21, 30, 0))
    assert a != b and Path(a).exists() and Path(b).exists()


def test_une_erreur_d_etape_est_recopiee_sans_la_cle_d_api(tmp_path):
    """Mesuré le 02/10 : 6 journaux sur 40 contenaient la clé FRED, écrite par httpx dans l'URL
    d'une erreur. Le manifeste recopie l'erreur, donc il doit la nettoyer."""
    chemin = ingest.ecrire_manifeste(_resultat(), tmp_path, maintenant=MOMENT)
    texte = Path(chemin).read_text(encoding="utf-8")
    assert "abcdef0123456789" not in texte
    assert "api_key=***" in texte


def test_le_mode_simulation_et_la_periode_de_rattrapage_sont_dits(tmp_path):
    chemin = ingest.ecrire_manifeste(_resultat(simulation=True), tmp_path, maintenant=MOMENT,
                                     periode=("2026-09-28", "2026-09-30"), etapes_demandees=["rss"])
    m = json.loads(Path(chemin).read_text(encoding="utf-8"))
    assert m["mode"] == "simulation"
    assert m["periode"] == ["2026-09-28", "2026-09-30"]
    assert m["etapes_demandees"] == ["rss"]


def test_le_commit_et_la_version_de_python_sont_notes_et_git_absent_ne_casse_rien(tmp_path):
    with patch("pipelines.ingest.subprocess.run", side_effect=FileNotFoundError("git absent")):
        chemin = ingest.ecrire_manifeste(_resultat(), tmp_path, maintenant=MOMENT)
    m = json.loads(Path(chemin).read_text(encoding="utf-8"))
    assert m["code"]["commit"] is None
    assert m["code"]["python"].startswith("3.")


def test_lire_dernier_manifeste_rend_le_plus_recent_ou_rien(tmp_path):
    assert ingest.lire_dernier_manifeste(tmp_path) is None
    ingest.ecrire_manifeste(_resultat(etapes_ok=1), tmp_path, maintenant=datetime(2026, 10, 2, 19, 0, 0))
    ingest.ecrire_manifeste(_resultat(etapes_ok=2), tmp_path, maintenant=MOMENT)
    dernier = ingest.lire_dernier_manifeste(tmp_path)
    assert dernier["etapes_ok"] == 2 and dernier["debut"].startswith("2026-10-03T19:00:12")


def test_une_panne_d_ecriture_du_manifeste_ne_fait_pas_echouer_la_collecte(tmp_path, caplog):
    """La collecte a réussi ; le manifeste est un bonus. Un disque plein ou un dossier illisible
    donne une ligne WARNING, pas une exception après 25 minutes de collecte."""
    pas_un_dossier = tmp_path / "fichier.txt"
    pas_un_dossier.write_text("x", encoding="utf-8")
    with caplog.at_level(logging.WARNING, logger="pipelines.ingest"):
        chemin = ingest.ecrire_manifeste_sans_casser(_resultat(), pas_un_dossier, maintenant=MOMENT)
    assert chemin is None
    assert any("manifeste" in r.getMessage() for r in caplog.records)


def test_le_point_de_lancement_ecrit_le_manifeste_dans_logs():
    """Le contrat du `__main__` : après `executer`, le manifeste part dans `logs/` (ignoré par Git)."""
    source = Path(ingest.__file__).read_text(encoding="utf-8")
    bloc_main = source[source.index('if __name__ == "__main__"'):]
    assert "ecrire_manifeste_sans_casser(" in bloc_main
    assert '"logs"' in bloc_main
