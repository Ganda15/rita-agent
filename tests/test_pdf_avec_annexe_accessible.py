"""Le PDF avec annexe d'E2 et d'E4 est balisé comme le rapport seul (05/11/2026).

Pourquoi : jusqu'au 05/11, le PDF avec annexe était une fusion après coup (pypdf) ; mesure du 05/11, ni arbre de
structure ni (pour E2) langue déclarée, alors que le rapport seul a les deux. Depuis E2 v1.1 et E4 v1.5,
`scripts/rendre_pdf.py --annexe` rend le rapport et l'annexe dans un seul document Chrome. Ces tests relisent les fichiers
livrés : ils tournent sur le poste, la CI ne rend pas de PDF. Le balisage ne vaut pas un audit d'accessibilité complet.
"""
import re
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
RAPPORTS = {"E2": 13, "E4": 14}   # pages d'annexe, en paysage ; E2 v1.3 (06/11) : A4 veille, A5 banc, A6 service


def _chemins(epreuve: str) -> tuple[Path, Path]:
    dossier = RACINE / "docs/rapports" / epreuve
    return dossier / f"rapport-{epreuve}-avec-annexe.pdf", dossier / f"rapport-{epreuve}.pdf"


@pytest.fixture
def lecteurs():
    fitz = pytest.importorskip("fitz", reason="PyMuPDF absent : le PDF se relit sur le poste, la CI ne rend pas de PDF")
    pypdf = pytest.importorskip("pypdf", reason="pypdf absent : le PDF se relit sur le poste")
    return fitz, pypdf


@pytest.mark.parametrize("epreuve", RAPPORTS)
def test_le_pdf_complet_declare_le_francais_et_porte_un_arbre_de_structure(lecteurs, epreuve):
    _, pypdf = lecteurs
    catalogue = pypdf.PdfReader(str(_chemins(epreuve)[0])).trailer["/Root"]
    assert catalogue.get("/Lang") == "fr"
    assert "/StructTreeRoot" in catalogue, "pas d'arbre de structure : un lecteur d'écran ne voit que du texte à plat"
    assert bool(catalogue["/MarkInfo"].get_object().get("/Marked")), "le PDF ne se déclare pas balisé"


@pytest.mark.parametrize("epreuve", RAPPORTS)
def test_le_rapport_en_portrait_puis_l_annexe_en_paysage(lecteurs, epreuve):
    fitz, _ = lecteurs
    complet, seul = _chemins(epreuve)
    with fitz.open(complet) as pdf_complet, fitz.open(seul) as pdf_seul:
        pages_du_rapport = len(pdf_seul)
        formats = ["paysage" if page.rect.width > page.rect.height else "portrait" for page in pdf_complet]
    assert formats == ["portrait"] * pages_du_rapport + ["paysage"] * RAPPORTS[epreuve]


@pytest.mark.parametrize("epreuve", RAPPORTS)
def test_les_pieds_sont_numerotes_de_bout_en_bout(lecteurs, epreuve):
    fitz, _ = lecteurs
    with fitz.open(_chemins(epreuve)[0]) as pdf:
        total = len(pdf)
        for numero, page in enumerate(pdf, start=1):
            assert f"{numero} / {total}" in page.get_text(), f"page {numero} : pied absent ou mal numéroté"


@pytest.mark.parametrize("epreuve", RAPPORTS)
def test_le_sommaire_mene_aux_memes_pages_que_dans_le_rapport_seul(lecteurs, epreuve):
    fitz, _ = lecteurs

    def cibles(chemin):
        with fitz.open(chemin) as pdf:
            # une fusion pypdf écrit « /lire », Chrome « lire » : on compare les pages, pas l'écriture du nom
            return {lien["nameddest"].lstrip("/"): lien["page"] for lien in pdf[0].get_links() if lien.get("nameddest")}

    complet, seul = _chemins(epreuve)
    tout, rapport = cibles(complet), cibles(seul)
    # E2 v1.3 (06/11) : les entrées d'annexe du sommaire sont cliquables ; leurs ancres (a1, a2...) n'existent que dans le
    # PDF complet. Les liens du rapport doivent mener aux mêmes pages ; ceux des annexes, au-delà du rapport.
    annexes = {nom for nom in tout if re.fullmatch(r"a\d+", nom)}
    assert {nom: page for nom, page in tout.items() if nom not in annexes} == rapport and rapport,         "le rapport ne se met pas en page de la même façon"
    with fitz.open(seul) as pdf_seul:
        assert all(tout[nom] >= len(pdf_seul) for nom in annexes), "une entrée d'annexe mène dans le rapport"
