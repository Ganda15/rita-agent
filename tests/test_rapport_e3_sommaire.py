"""Le sommaire du rapport E3 dit vrai : chaque numéro imprimé est la page où commence sa section (E3 v1.9, 27/10/2026).

Pourquoi : un sommaire tapé à la main se périme à la première retouche, et un jury qui suit « C11, p. 7 » et tombe sur
C10 ne croit plus le reste. Les numéros sont lus dans le PDF (chaque entrée est un lien vers son titre, que Chrome
résout en page), puis écrits dans la source par `scripts/rendre_pdf.py` ; ces tests gardent la source et le PDF d'accord.
"""
import re
from pathlib import Path

import pytest

from scripts import rendre_pdf

RACINE = Path(__file__).resolve().parent.parent
RAPPORT = RACINE / "docs/rapports/E3/rapport-E3.md"
ENTREE = re.compile(r'<a href="#([\w-]+)">[^<]*</a><span>p\. (\d+)</span>')


def test_numeroter_sommaire_ecrit_la_page_de_chaque_ancre():
    texte = ('<li><a href="#c9">3. C9</a><span>p. 00</span></li>\n'
             '<li><a href="#c10">4. C10</a><span>p. 7</span></li>')
    resultat = rendre_pdf.numeroter_sommaire(texte, {"c9": 3, "c10": 5})
    assert ENTREE.findall(resultat) == [("c9", "3"), ("c10", "5")]


def test_numeroter_sommaire_refuse_une_ancre_sans_page():
    with pytest.raises(KeyError):
        rendre_pdf.numeroter_sommaire('<a href="#c11">5. C11</a><span>p. 00</span>', {"c9": 3})


def test_un_texte_sans_sommaire_ne_change_pas():
    assert rendre_pdf.numeroter_sommaire("# Titre\n\nTexte.", {}) == "# Titre\n\nTexte."


def test_chaque_entree_du_sommaire_vise_un_titre_du_rapport():
    texte = RAPPORT.read_text(encoding="utf-8")
    entrees = ENTREE.findall(texte)
    assert len(entrees) == 13
    for ancre, _ in entrees:
        assert re.search(r"^#+ .*\{: #" + re.escape(ancre) + r" \}$", texte, re.M), f"aucun titre pour #{ancre}"


def test_les_numeros_du_sommaire_sont_ceux_du_pdf_livre():
    fitz = pytest.importorskip("fitz", reason="PyMuPDF absent : le PDF se relit sur le poste, la CI ne rend pas de PDF")
    with fitz.open(RAPPORT.with_suffix(".pdf")) as pdf:
        pages = {lien["nameddest"]: lien["page"] + 1 for lien in pdf[0].get_links() if lien.get("nameddest")}
    imprimes = {ancre: int(n) for ancre, n in ENTREE.findall(RAPPORT.read_text(encoding="utf-8"))}
    assert len(imprimes) == 13, "pas de sommaire : le test ne prouverait rien"
    assert imprimes == pages
