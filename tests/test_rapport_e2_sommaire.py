"""Le sommaire du rapport E2 dit vrai, et le rapport tient dans le format attendu (E2 v0.7, 01/11/2026).

Pourquoi : même règle que pour E3, E4 et E5 (`tests/test_rapport_e3_sommaire.py`). Les numéros sont lus dans le PDF et
écrits dans la source par `scripts/rendre_pdf.py`. Le format d'E2 est de 15 à 20 pages (support de certification) :
la version 0.6 en faisait 11.
"""
import re
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
RAPPORT = RACINE / "docs/rapports/E2/rapport-E2.md"
ENTREE = re.compile(r'<a href="#([\w-]+)">[^<]*</a><span>p\. (\d+)</span>')
SECTIONS = 8   # « Lire ce rapport », six sections et le glossaire


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


def test_le_rapport_tient_entre_quinze_et_vingt_pages():
    """Rapport pro 2 : de 15 à 20 pages (support de certification, détail des livrables, E2)."""
    pypdf = pytest.importorskip("pypdf", reason="pypdf absent : le PDF se relit sur le poste")
    assert 15 <= len(pypdf.PdfReader(str(RAPPORT.with_suffix(".pdf"))).pages) <= 20
