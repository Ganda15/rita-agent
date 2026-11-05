"""Le PDF d'E2 avec annexe est balisé comme le rapport seul (05/11/2026).

Pourquoi : la version 1.0 du PDF avec annexe était une fusion après coup ; mesure du 05/11, ni langue déclarée ni arbre
de structure, alors que `rapport-E2.pdf` a les deux. Depuis la version 1.1, `scripts/rendre_pdf.py --annexe` rend le
rapport et l'annexe dans un seul document Chrome. Ce test relit le fichier livré : il tourne sur le poste, la CI ne
rend pas de PDF.
"""
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
COMPLET = RACINE / "docs/rapports/E2/rapport-E2-avec-annexe.pdf"
SEUL = RACINE / "docs/rapports/E2/rapport-E2.pdf"
PAGES_ANNEXE = 3


@pytest.fixture
def lecteurs():
    fitz = pytest.importorskip("fitz", reason="PyMuPDF absent : le PDF se relit sur le poste, la CI ne rend pas de PDF")
    pypdf = pytest.importorskip("pypdf", reason="pypdf absent : le PDF se relit sur le poste")
    return fitz, pypdf


def test_le_pdf_complet_declare_le_francais_et_porte_un_arbre_de_structure(lecteurs):
    _, pypdf = lecteurs
    catalogue = pypdf.PdfReader(str(COMPLET)).trailer["/Root"]
    assert catalogue.get("/Lang") == "fr"
    assert "/StructTreeRoot" in catalogue, "pas d'arbre de structure : un lecteur d'écran ne voit que du texte à plat"
    assert bool(catalogue["/MarkInfo"].get_object().get("/Marked")), "le PDF ne se déclare pas balisé"


def test_le_rapport_en_portrait_puis_l_annexe_en_paysage(lecteurs):
    fitz, _ = lecteurs
    with fitz.open(COMPLET) as complet, fitz.open(SEUL) as seul:
        pages_du_rapport = len(seul)
        formats = ["paysage" if page.rect.width > page.rect.height else "portrait" for page in complet]
    assert formats == ["portrait"] * pages_du_rapport + ["paysage"] * PAGES_ANNEXE


def test_les_pieds_sont_numerotes_de_bout_en_bout(lecteurs):
    fitz, _ = lecteurs
    with fitz.open(COMPLET) as pdf:
        total = len(pdf)
        for numero, page in enumerate(pdf, start=1):
            assert f"{numero} / {total}" in page.get_text(), f"page {numero} : pied absent ou mal numéroté"


def test_le_sommaire_mene_aux_memes_pages_que_dans_le_rapport_seul(lecteurs):
    fitz, _ = lecteurs

    def cibles(chemin):
        with fitz.open(chemin) as pdf:
            # une fusion pypdf écrit « /lire », Chrome « lire » : on compare les pages, pas l'écriture du nom
            return {lien["nameddest"].lstrip("/"): lien["page"] for lien in pdf[0].get_links() if lien.get("nameddest")}

    assert cibles(COMPLET) == cibles(SEUL) and cibles(SEUL), "le rapport ne se met pas en page de la même façon"
