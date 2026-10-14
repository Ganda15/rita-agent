"""Sprint 2, tâche 4 : le jeu de démonstration versionné (`data/demo/`), qui permet de reconstruire RITA depuis le dépôt.

Trois valeurs (OR.PA, MC.PA, AIR.PA), leurs cours réels du 01/07/2026 au 14/10/2026 extraits de la base du poste, six
articles synthétiques clairement marqués et trois positions inventées. Les règles vérifiées ici sont celles de la base
(`CHECK` de la table `cotation`) : un fichier qui les violerait ferait échouer la reconstruction.
"""
import csv
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts import extraire_jeu_demo as e

DOSSIER = Path(__file__).resolve().parent.parent / "data" / "demo"
EN_TETES = {
    "valeurs.csv": ["ticker", "nom_officiel", "isin", "devise", "place_cotation"],
    "cotations.csv": ["ticker", "date_seance", "ouverture", "haut", "bas", "cloture", "volume"],
    "articles.csv": ["source", "titre", "lien", "publie_le", "resume"],
    "positions.csv": ["ticker", "quantite", "pru", "devise", "date_achat"],
}
MENTION = "Démonstration, contenu synthétique :"


def _lignes(nom):
    with open(DOSSIER / nom, encoding="utf-8", newline="") as fichier:
        return list(csv.DictReader(fichier, delimiter=";"))


@pytest.mark.parametrize("nom", sorted(EN_TETES))
def test_chaque_fichier_existe_avec_son_en_tete(nom):
    with open(DOSSIER / nom, encoding="utf-8", newline="") as fichier:
        assert next(csv.reader(fichier, delimiter=";")) == EN_TETES[nom]


def test_les_tickers_des_cours_et_des_positions_sont_des_valeurs_du_jeu():
    valeurs = {l["ticker"] for l in _lignes("valeurs.csv")}
    assert valeurs == {"OR.PA", "MC.PA", "AIR.PA"}
    assert {l["ticker"] for l in _lignes("cotations.csv")} <= valeurs
    assert {l["ticker"] for l in _lignes("positions.csv")} <= valeurs


def test_or_pa_a_au_moins_50_seances():
    assert sum(1 for l in _lignes("cotations.csv") if l["ticker"] == "OR.PA") >= 50


def test_chaque_cotation_respecte_les_regles_de_la_base():
    for l in _lignes("cotations.csv"):
        assert float(l["haut"]) >= float(l["bas"]), l
        assert float(l["cloture"]) > 0 and float(l["ouverture"]) > 0, l
        assert int(l["volume"]) >= 0, l
        assert date(2026, 7, 1) <= date.fromisoformat(l["date_seance"]) <= date(2026, 10, 14), l


def test_les_articles_sont_marques_comme_synthetiques():
    articles = _lignes("articles.csv")
    assert len(articles) == 6
    for a in articles:
        assert a["source"] == "demonstration"
        assert a["lien"].startswith("https://demo.rita.invalid/")
        assert a["resume"].startswith(MENTION)


def test_les_positions_sont_valides():
    positions = _lignes("positions.csv")
    assert len(positions) == 3
    for p in positions:
        assert float(p["quantite"]) > 0 and float(p["pru"]) > 0 and p["devise"] == "EUR"
        date.fromisoformat(p["date_achat"])


def test_extraction_refuse_sans_dsn_de_lecture(monkeypatch, tmp_path, capsys):
    # Pas de repli vers DATABASE_URL : sans compte de lecture, arrêt, aucune connexion tentée.
    monkeypatch.delenv("RITA_DSN_LECTURE", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://ne-doit-pas-servir")
    with patch.object(e.psycopg2, "connect") as connexion:
        assert e.main(["--dossier", str(tmp_path)]) == 2
    connexion.assert_not_called()
    assert "RITA_DSN_LECTURE" in capsys.readouterr().err


def test_extraction_lit_en_session_seule_et_ecrit_les_deux_fichiers(tmp_path):
    curseur = MagicMock()
    curseur.fetchall.side_effect = [
        [("OR.PA", "OREAL(L')", "FR0000120321", "EUR", None)],
        [("OR.PA", date(2026, 7, 1), 380.5, 384.0, 379.1, 383.2, 120000)],
    ]
    cnx = MagicMock()
    cnx.cursor.return_value.__enter__.return_value = curseur
    with patch.object(e.psycopg2, "connect", return_value=cnx):
        compte = e.extraire("postgresql://lecture", ["OR.PA"], date(2026, 7, 1), date(2026, 10, 14), tmp_path)
    cnx.set_session.assert_called_once_with(readonly=True)     # la base refuse toute écriture dans cette session
    assert compte == {"valeurs": 1, "cotations": 1}
    assert (tmp_path / "cotations.csv").read_text(encoding="utf-8").splitlines() == [
        "ticker;date_seance;ouverture;haut;bas;cloture;volume", "OR.PA;2026-07-01;380.5;384.0;379.1;383.2;120000"]
    assert (tmp_path / "valeurs.csv").read_text(encoding="utf-8").splitlines()[1] == "OR.PA;OREAL(L');FR0000120321;EUR;"
