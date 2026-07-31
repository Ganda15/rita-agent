"""Tests du lecteur de positions — aucun accès aux données personnelles d'Era.

Tous les cas utilisent des fichiers temporaires fabriqués dans le test. Le fichier réel
n'est jamais lu, jamais versionné, jamais nécessaire pour faire tourner la suite.
"""
from pathlib import Path

import pytest

from sources import positions

CSV_FR = (
    "Libellé;Code ISIN;Ticker;Quantité;Prix de revient;Devise\n"
    "LVMH;FR0000121014;MC.PA;12;632,40;EUR\n"
    "Air Liquide;FR0000120073;AI.PA;40;158,25;EUR\n"
)


def _ecrire(tmp_path: Path, contenu: str, nom: str = "p.csv",
            encodage: str = "utf-8") -> Path:
    chemin = tmp_path / nom
    chemin.write_text(contenu, encoding=encodage)
    return chemin


# --- lecture nominale ---------------------------------------------------------

def test_lit_un_export_francais(tmp_path):
    p = positions.lire(_ecrire(tmp_path, CSV_FR))

    assert len(p.positions) == 2
    assert p.rejets == []
    lvmh = p.positions[0]
    assert lvmh.ticker == "MC.PA"
    assert lvmh.nom == "LVMH"
    assert lvmh.isin == "FR0000121014"
    assert lvmh.quantite == 12
    assert lvmh.pru == 632.40                     # virgule décimale FR
    assert lvmh.montant_investi == 7588.80


def test_devise_par_defaut_si_colonne_absente(tmp_path):
    csv = "Ticker;Quantité;Prix de revient\nMC.PA;10;100,00\n"
    p = positions.lire(_ecrire(tmp_path, csv))
    assert p.positions[0].devise == "EUR"


# --- les quatre pièges de l'export courtier -----------------------------------

def test_encodage_cp1252(tmp_path):
    """Excel FR exporte souvent en cp1252 : sans détection, « L'Oréal » devient « LÃ©al »."""
    chemin = _ecrire(tmp_path, CSV_FR.replace("LVMH", "L'Oréal"),
                     encodage="cp1252")
    p = positions.lire(chemin)
    assert p.positions[0].nom == "L'Oréal"


def test_separateur_virgule_export_anglo_saxon(tmp_path):
    csv = "Ticker,Quantity,Prix de revient\nAAPL,6,178.45\n"
    p = positions.lire(_ecrire(tmp_path, csv))
    assert p.positions[0].ticker == "AAPL"
    assert p.positions[0].pru == 178.45


def test_separateur_tabulation(tmp_path):
    csv = "Ticker\tQuantité\tPRU\nMC.PA\t12\t632,40\n"
    p = positions.lire(_ecrire(tmp_path, csv))
    assert p.positions[0].quantite == 12


@pytest.mark.parametrize("entete_qte", ["Quantité", "Qté", "Nombre de titres", "NOMBRE"])
def test_synonymes_d_entetes(tmp_path, entete_qte):
    """Chaque courtier nomme ses colonnes autrement."""
    csv = f"Ticker;{entete_qte};PRU\nMC.PA;12;632,40\n"
    p = positions.lire(_ecrire(tmp_path, csv))
    assert p.positions[0].quantite == 12


@pytest.mark.parametrize("brut, attendu", [
    ("632,40", 632.40),
    ("1 250", 1250.0),
    ("1\xa0250,50", 1250.50),      # espace insécable des milliers
    ("178.45", 178.45),
    ("12 €", 12.0),
    ("", None),
    ("n/a", None),
    (None, None),
])
def test_nombres_au_format_francais(brut, attendu):
    assert positions._nombre_fr(brut) == attendu


# --- validation C3 ------------------------------------------------------------

@pytest.mark.parametrize("ligne, cause_attendue", [
    (";12;632,40", "ticker absent"),
    ("MC.PA;0;632,40", "quantite nulle"),
    ("MC.PA;-5;632,40", "quantite nulle"),
    ("MC.PA;abc;632,40", "quantite illisible"),
    ("MC.PA;12;", "prix de revient absent"),
    ("MC.PA;12;0", "prix de revient invalide"),
])
def test_lignes_corrompues_rejetees_avec_leur_cause(tmp_path, ligne, cause_attendue):
    csv = f"Ticker;Quantité;Prix de revient\n{ligne}\n"
    p = positions.lire(_ecrire(tmp_path, csv))

    assert p.positions == []
    assert len(p.rejets) == 1
    assert cause_attendue in p.rejets[0].cause


def test_un_rejet_n_empeche_pas_les_lignes_valides(tmp_path):
    """Une ligne corrompue ne doit pas faire perdre tout le fichier."""
    csv = ("Ticker;Quantité;Prix de revient\n"
           "MC.PA;12;632,40\n"
           "XXX.PA;0;100,00\n"
           "AI.PA;40;158,25\n")
    p = positions.lire(_ecrire(tmp_path, csv))

    assert len(p.positions) == 2
    assert len(p.rejets) == 1
    # Ligne 1 = en-têtes, 2 = MC.PA, 3 = XXX.PA (rejetée), 4 = AI.PA
    assert p.rejets[0].ligne == 3                 # numéro de ligne du fichier conservé


def test_le_rejet_conserve_la_ligne_source(tmp_path):
    """Traçabilité C3 : on doit pouvoir montrer la ligne exacte qui a été écartée."""
    csv = "Ticker;Quantité;Prix de revient\nXXX.PA;0;100,00\n"
    p = positions.lire(_ecrire(tmp_path, csv))
    assert p.rejets[0].contenu["Ticker"] == "XXX.PA"


# --- erreurs franches ---------------------------------------------------------

def test_colonnes_obligatoires_absentes_leve(tmp_path):
    csv = "Libellé;Code ISIN\nLVMH;FR0000121014\n"
    with pytest.raises(ValueError, match="Colonnes obligatoires introuvables"):
        positions.lire(_ecrire(tmp_path, csv))


def test_fichier_absent_leve(tmp_path):
    with pytest.raises(FileNotFoundError):
        positions.lire(tmp_path / "inexistant.csv")


# --- multi-devises ------------------------------------------------------------

def test_devises_multiples_recensees(tmp_path):
    csv = ("Ticker;Quantité;Prix de revient;Devise\n"
           "MC.PA;12;632,40;EUR\n"
           "AAPL;6;178,45;USD\n")
    p = positions.lire(_ecrire(tmp_path, csv))
    assert p.devises == {"EUR", "USD"}


# --- confidentialité ----------------------------------------------------------

def test_chemin_pilote_par_variable_d_environnement(tmp_path, monkeypatch):
    """Le fichier réel se donne par $POSITIONS_CSV — jamais en dur dans le code."""
    chemin = _ecrire(tmp_path, CSV_FR)
    monkeypatch.setenv("POSITIONS_CSV", str(chemin))
    assert len(positions.lire().positions) == 2


def test_exemple_anonymise_par_defaut(monkeypatch):
    """Sans variable d'environnement, on lit l'exemple — jamais de données perso."""
    monkeypatch.delenv("POSITIONS_CSV", raising=False)
    p = positions.lire()
    assert len(p.positions) == 10
    assert len(p.rejets) == 2                     # les 2 lignes corrompues volontaires
