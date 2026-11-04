"""Le mode le plus étroit de l'importateur : --corrections-seulement (04/11/2026 au soir).

Pourquoi : `--positions-seulement` n'est pas « seulement Viridien » (relecture extérieure du 04/11). Il réécrit les 111 valeurs
(nom, statut, note, devise d'après l'univers), insère les alias manquants, rafraîchit `importe_le` sur toutes les positions du
CSV et CLÔT les positions absentes du CSV. Sans effet visible sur la base locale, mais rien ne le garantit sur une autre base.
Ce mode n'applique que les corrections connues, écrites dans le code (`REGROUPEMENTS`, `NOMS_OFFICIELS`), sur les seules lignes
qu'elles visent : aucun CSV lu, aucun univers lu, aucune réconciliation, aucun fichier de données nécessaire dans l'image.
"""
from unittest.mock import MagicMock, patch

import pytest

from db import importer


def test_les_noms_officiels_ne_visent_que_leur_valeur_et_seulement_si_le_nom_differe(monkeypatch):
    monkeypatch.setattr(importer, "NOMS_OFFICIELS", {"VIRI.PA": "VIRIDIEN"})
    cur = MagicMock()
    cur.fetchall.return_value = [("VIRI.PA",)]
    assert importer.corriger_noms_officiels(cur) == 1
    sql, params = cur.execute.call_args.args
    assert sql.upper().startswith("UPDATE VALEUR SET NOM_OFFICIEL")
    assert "WHERE TICKER = %S" in sql.upper() and "IS DISTINCT FROM" in sql.upper()
    assert params == ("VIRIDIEN", "VIRI.PA", "VIRIDIEN")


def test_appliquer_les_corrections_ne_lit_ni_csv_ni_univers_et_ne_reconcilie_rien(monkeypatch):
    lire, univers, valeurs, positions = MagicMock(), MagicMock(), MagicMock(), MagicMock()
    monkeypatch.setattr("sources.positions.lire", lire)
    monkeypatch.setattr(importer, "charger_univers", univers)
    monkeypatch.setattr(importer, "importer_valeurs", valeurs)
    monkeypatch.setattr(importer, "importer_positions", positions)
    monkeypatch.setattr(importer, "corriger_regroupements", MagicMock(return_value=1))
    monkeypatch.setattr(importer, "corriger_noms_officiels", MagicMock(return_value=1))
    monkeypatch.setattr(importer, "controler_prix_de_revient", MagicMock(return_value={"hors_echelle": [], "non_controlees": []}))
    bilan = importer.appliquer_corrections(MagicMock())
    for jamais in (lire, univers, valeurs, positions):
        jamais.assert_not_called()
    assert (bilan["corrigees"], bilan["noms_corriges"]) == (1, 1)


def test_importer_corrections_valide_une_seule_fois(monkeypatch):
    monkeypatch.setattr(importer, "appliquer_corrections", MagicMock(return_value={"corrigees": 0, "noms_corriges": 0}))
    with patch("db.importer.psycopg2.connect") as connect:
        importer.importer_corrections("postgresql://test")
    connect.assert_called_once_with("postgresql://test")
    connect.return_value.__enter__.return_value.commit.assert_called_once()


@pytest.mark.parametrize("autre", ["--positions-seulement", "--limite-annees"])
def test_corrections_seulement_s_exclut_avec_les_autres_modes(monkeypatch, autre):
    # D'abord l'option seule : sinon l'exclusion « passerait » parce que l'option n'existe pas (argparse sort aussi).
    assert importer.lire_arguments(["--corrections-seulement"]).corrections_seulement is True
    argv = ["importer", "--corrections-seulement", autre] + (["1"] if autre == "--limite-annees" else [])
    monkeypatch.setattr("sys.argv", argv)
    with pytest.raises(SystemExit):
        importer.lire_arguments()


# --- les portes avant l'écriture (relecture du 04/11) : un passage à blanc, et des compteurs attendus ------------------------

def _connexion_simulee(monkeypatch, corrigees, noms):
    monkeypatch.setattr(importer, "appliquer_corrections",
                        MagicMock(return_value={"corrigees": corrigees, "noms_corriges": noms, "controle_prix_de_revient": {}}))
    return patch("db.importer.psycopg2.connect")


def test_a_blanc_applique_puis_annule_sans_valider(monkeypatch):
    with _connexion_simulee(monkeypatch, 1, 1) as connect:
        bilan = importer.importer_corrections("postgresql://test", a_blanc=True)
    conn = connect.return_value.__enter__.return_value
    conn.commit.assert_not_called()
    conn.rollback.assert_called_once()
    assert bilan["a_blanc"] is True


def test_des_compteurs_differents_de_l_attendu_annulent_tout(monkeypatch):
    with _connexion_simulee(monkeypatch, 0, 1) as connect:
        with pytest.raises(importer.CorrectionsInattendues, match="attendu"):
            importer.importer_corrections("postgresql://test", attendu=(1, 1))
    connect.return_value.__enter__.return_value.commit.assert_not_called()


def test_des_compteurs_egaux_a_l_attendu_valident(monkeypatch):
    with _connexion_simulee(monkeypatch, 1, 1) as connect:
        importer.importer_corrections("postgresql://test", attendu=(1, 1))
    connect.return_value.__enter__.return_value.commit.assert_called_once()


def test_les_portes_se_lisent_en_ligne_de_commande():
    args = importer.lire_arguments(["--corrections-seulement", "--a-blanc", "--attendu-corrigees", "1", "--attendu-noms", "1"])
    assert (args.a_blanc, args.attendu_corrigees, args.attendu_noms) == (True, 1, 1)


@pytest.mark.parametrize("argv", [["--a-blanc"], ["--attendu-corrigees", "1", "--attendu-noms", "1"],
                                  ["--corrections-seulement", "--attendu-corrigees", "1"]])
def test_les_portes_n_existent_qu_avec_le_mode_cible_et_par_paire(argv):
    with pytest.raises(SystemExit):
        importer.lire_arguments(argv)
