"""Le sommaire du rapport E5 dit vrai : chaque numéro imprimé est la page où commence sa section (E5 v0.2, 31/10/2026).

Pourquoi : même règle que pour E3 et E4 (`tests/test_rapport_e3_sommaire.py`). Les numéros sont lus dans le PDF et écrits
dans la source par `scripts/rendre_pdf.py` ; ces tests gardent la source et le PDF d'accord.
"""
import re
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
RAPPORT = RACINE / "docs/rapports/E5/rapport-E5.md"
ENTREE = re.compile(r'<a href="#([\w-]+)">[^<]*</a><span>p\. (\d+)</span>')
SECTIONS = 10   # neuf sections et le glossaire


def test_chaque_entree_du_sommaire_vise_un_titre_du_rapport():
    texte = RAPPORT.read_text(encoding="utf-8")
    entrees = ENTREE.findall(texte)
    assert len(entrees) == SECTIONS
    for ancre, _ in entrees:
        assert re.search(r"^#+ .*\{: #" + re.escape(ancre) + r" \}$", texte, re.M), f"aucun titre pour #{ancre}"


def test_les_numeros_du_sommaire_sont_ceux_du_pdf_livre():
    fitz = pytest.importorskip("fitz", reason="PyMuPDF absent : le PDF se relit sur le poste, la CI ne rend pas de PDF")
    with fitz.open(RAPPORT.with_suffix(".pdf")) as pdf:
        pages = {lien["nameddest"]: lien["page"] + 1 for lien in pdf[0].get_links() if lien.get("nameddest")}
    imprimes = {ancre: int(n) for ancre, n in ENTREE.findall(RAPPORT.read_text(encoding="utf-8"))}
    assert len(imprimes) == SECTIONS, "pas de sommaire : le test ne prouverait rien"
    assert imprimes == pages


def test_le_rapport_tient_en_cinq_pages_au_plus():
    """Rapport pro 5 : de 2 à 5 pages (référentiel, détail des livrables, E5)."""
    pypdf = pytest.importorskip("pypdf", reason="pypdf absent : le PDF se relit sur le poste")
    assert 2 <= len(pypdf.PdfReader(str(RAPPORT.with_suffix(".pdf"))).pages) <= 5
