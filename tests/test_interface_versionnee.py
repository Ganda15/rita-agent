"""Refonte 001 (R5, R6), 04/11/2026 : chaque script et chaque feuille de style de l'interface porte sa version dans son
adresse (`indicateurs.js?v=3fa9c1d07b`), calculée sur le contenu du fichier.

Pourquoi : le 04/11, un navigateur affichait la page neuve avec l'ancien script gardé en cache : 11 titres, 15 cases, les
chiffres décalés d'une colonne, sur Indicateurs puis sur Portefeuille. Le serveur local qui servait ces pages tournait
depuis avant l'ajout du `Cache-Control: no-cache` et n'en envoyait aucun : Chrome gardait le script des jours. Une adresse
qui change avec le contenu rend ce mélange impossible, quel que soit le cache. Le test échoue si on modifie un fichier
sans relancer `scripts/versionner_interface.py`, et le dit.
"""
from pathlib import Path

import pytest

from scripts import versionner_interface as v

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
PAGES = sorted(FRONTEND.glob("*.html"))
COMMANDE = r"C:\Python314\python.exe scripts\versionner_interface.py"


def test_les_cinq_pages_sont_trouvees():
    assert [p.name for p in PAGES] == ["briefing.html", "index.html", "indicateurs.html", "question.html",
                                       "tableau-de-bord.html"]


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_chaque_script_et_chaque_feuille_porte_sa_version(page):
    liens = v.references(page.read_bytes())
    assert liens, f"{page.name} : aucun script ni feuille de style trouvé, le test ne vérifie rien"
    for nom, version in liens:
        assert version, f"{page.name} : {nom} sans version. Lancer : {COMMANDE}"
        attendue = v.empreinte(FRONTEND / nom)
        assert version == attendue, f"{page.name} : {nom} est en version {version}, son contenu dit {attendue}. Lancer : {COMMANDE}"


def test_une_page_ne_charge_pas_deux_versions_du_meme_fichier():
    versions: dict[str, set[str]] = {}
    for page in PAGES:
        for nom, version in v.references(page.read_bytes()):
            versions.setdefault(nom, set()).add(version)
    assert {nom: vs for nom, vs in versions.items() if len(vs) > 1} == {}


def test_la_version_suit_le_contenu_et_pas_les_fins_de_ligne(tmp_path):
    # Windows écrit des fins de ligne CRLF, Linux (la CI, l'image Docker) LF : la version ne doit pas en dépendre.
    a, b, c = tmp_path / "a.js", tmp_path / "b.js", tmp_path / "c.js"
    a.write_bytes(b"let x = 1;\r\nlet y = 2;\r\n")
    b.write_bytes(b"let x = 1;\nlet y = 2;\n")
    c.write_bytes(b"let x = 1;\nlet y = 3;\n")
    assert v.empreinte(a) == v.empreinte(b)
    assert v.empreinte(b) != v.empreinte(c)


def test_versionner_est_idempotent_et_ne_touche_que_les_scripts_et_les_styles(tmp_path):
    (tmp_path / "p.js").write_bytes(b"1")
    (tmp_path / "s.css").write_bytes(b"2")
    html = (b'<link rel="stylesheet" href="s.css">\r\n<link rel="icon" href="logo.png">\r\n'
            b'<script src="p.js?v=ancienne"></script>\r\n<script src="https://exemple.org/x.js"></script>\r\n')
    une_fois = v.versionner(html, tmp_path)
    assert b'href="s.css?v=' in une_fois and b'src="p.js?v=' in une_fois and b"ancienne" not in une_fois
    assert b'href="logo.png"' in une_fois, "une image n'est pas versionnée"
    assert b'src="https://exemple.org/x.js"' in une_fois, "un script d'un autre site n'est pas touché"
    assert b"\r\n" in une_fois and une_fois.count(b"\r\n") == html.count(b"\r\n"), "les fins de ligne sont gardées"
    assert v.versionner(une_fois, tmp_path) == une_fois
