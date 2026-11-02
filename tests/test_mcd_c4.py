"""C4 : le MCD dit ce que la base accepte, une valeur peut n'avoir aucune cotation (décision d'Era, 02/11/2026).

Retour écrit du formateur sur l'oral blanc du 30/10 : « écart entre le MCD et la base (une valeur sans cotation est
acceptée) ». Le MCD du 01/08 disait `VALEUR 1,n ── est cotée lors ── 1,1 COTATION`. Rien ne l'impose : la clé
étrangère va de `cotation` vers `valeur`, et `db/importer.py` enregistre tout l'univers avant les cotations. Era a
choisi d'aligner le modèle sur la règle réelle, `0,n` côté VALEUR, plutôt que d'ajouter un contrôle à l'import.
Le MCD du 01/08 est une preuve : il est gardé tel quel, la version du 02/11 s'y ajoute.
"""
import re
from pathlib import Path

import psycopg2
import pytest

RACINE = Path(__file__).resolve().parent.parent
ANCIEN = RACINE / "evidence/C4/MCD-MERISE-RITA.drawio"
NOUVEAU = RACINE / "evidence/C4/MCD-MERISE-RITA-2026-11-02.drawio"


def _cellules(chemin: Path) -> dict[str, dict[str, str | None]]:
    # Les attributs des balises `mxCell`, lus sans analyseur XML : ces fichiers sont ceux du dépôt.
    cellules = {}
    for balise in re.findall(r"<mxCell\b([^>]*)>", chemin.read_text(encoding="utf-8")):
        attributs = dict(re.findall(r'(\w+)="([^"]*)"', balise))
        cellules[attributs.get("id")] = {k: attributs.get(k) for k in ("value", "source", "target")}
    return cellules


def _cardinalite(chemin: Path, source: str, cible: str) -> str | None:
    liens = [c["value"] for c in _cellules(chemin).values() if c["source"] == source and c["target"] == cible]
    assert len(liens) == 1, f"{chemin.name} : {len(liens)} lien(s) {source} -> {cible}"
    return liens[0]


def test_le_mcd_du_02_11_dit_qu_une_valeur_peut_n_avoir_aucune_cotation():
    assert _cardinalite(NOUVEAU, "a_cotee_lors", "e_valeur") == "0,n"
    assert _cardinalite(NOUVEAU, "e_cotation", "a_cotee_lors") == "1,1", "une cotation reste celle d'une seule valeur"


def test_le_mcd_du_01_08_est_garde_tel_quel():
    assert _cardinalite(ANCIEN, "a_cotee_lors", "e_valeur") == "1,n"


def test_seuls_la_cardinalite_et_le_titre_changent():
    ancien, nouveau = _cellules(ANCIEN), _cellules(NOUVEAU)
    differences = {i for i in ancien.keys() | nouveau.keys() if ancien.get(i) != nouveau.get(i)}
    assert differences == {"l2b", "titre"}, differences
    assert "revu le 2026-11-02" in nouveau["titre"]["value"], "le titre doit dire que le modèle a été revu, et quand"


@pytest.fixture
def curseur():
    from tests.garde_base import dsn_de_test
    try:
        con = psycopg2.connect(dsn_de_test(), connect_timeout=3)
    except psycopg2.OperationalError as e:
        pytest.skip(f"PostgreSQL injoignable : {e}")
    con.autocommit = False
    cur = con.cursor()
    yield cur
    con.rollback()      # tout ce qui suit est annulé
    con.close()


@pytest.mark.postgresql
def test_en_base_une_valeur_sans_aucune_cotation_est_acceptee(curseur):
    curseur.execute("INSERT INTO valeur (ticker, nom_officiel) VALUES ('ESSAI.C4', 'Valeur sans cotation')")
    curseur.execute("SELECT COUNT(*) FROM cotation WHERE ticker = 'ESSAI.C4'")
    assert curseur.fetchone()[0] == 0
    curseur.execute("SELECT nom_officiel FROM valeur WHERE ticker = 'ESSAI.C4'")
    assert curseur.fetchone()[0] == "Valeur sans cotation"
