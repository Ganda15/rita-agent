"""Assemblage d'un rapport et de son annexe en un seul PDF (05/11/2026, relecture d'E4 v1.3).

Pourquoi ce test existe. Le 04/11, une première renumérotation des pieds de page a reconstruit le PDF complet avec
PyMuPDF seul : les pieds étaient justes, mais les 16 liens internes (sommaire, index des annexes) et les 68 signets du
volet latéral avaient disparu. Une relecture extérieure l'a vu. Ces tests fixent les trois choses qu'un assemblage doit
garder : une seule numérotation, les liens internes et leur destination, les signets des deux documents.

Les PDF de test sont fabriqués ici avec PyMuPDF (deux pages chacun, un pied « n / 2 », un lien interne, deux signets).
La CI n'installe ni PyMuPDF ni pypdf : ces tests s'y sautent, comme les autres tests de rendu des rapports. Le saut
se fait dans une fixture, jamais au chargement du module : le job `base` charge tous les fichiers avant de choisir les
tests marqués `postgresql`, et un fichier sauté au chargement le ferait échouer (`tests/test_ci_base.py`).
"""
from __future__ import annotations

import pytest

from scripts import assembler_pdf_avec_annexe as assemblage


@pytest.fixture
def fitz():
    module = pytest.importorskip("fitz", reason="PyMuPDF absent : les PDF se relisent sur le poste, la CI ne rend pas de PDF")
    pytest.importorskip("pypdf", reason="pypdf absent : l'assemblage garde les liens et les signets avec pypdf")
    return module


def _document(fitz, chemin, titre: str) -> None:
    """Deux pages : un titre, un pied « n / 2 » en bas à droite, un lien de la page 1 vers la page 2, deux signets."""
    doc = fitz.open()
    for n in (1, 2):
        page = doc.new_page(width=595, height=842)
        page.insert_text((72, 100), f"{titre}, page {n}", fontsize=14)
        page.insert_text((520, 820), f"{n} / 2", fontsize=8)
    doc[0].insert_link({"kind": fitz.LINK_GOTO, "from": fitz.Rect(72, 120, 300, 140), "page": 1, "to": fitz.Point(72, 72)})
    doc.set_toc([[1, titre, 1], [2, f"{titre}, deuxième page", 2]])
    doc.save(chemin)


@pytest.fixture
def complet(fitz, tmp_path):
    rapport, annexe, sortie = tmp_path / "rapport.pdf", tmp_path / "annexe.pdf", tmp_path / "complet.pdf"
    _document(fitz, rapport, "Rapport")
    _document(fitz, annexe, "Annexe")
    assert assemblage.assembler(rapport, annexe, sortie) == 4
    return fitz.open(sortie)


def _pieds(page) -> list[str]:
    return [ligne.strip() for ligne in page.get_text().split("\n") if assemblage.PIED.match(ligne.strip())]


def test_les_pieds_de_page_suivent_la_numerotation_du_pdf_complet(complet):
    assert [_pieds(page) for page in complet] == [["1 / 4"], ["2 / 4"], ["3 / 4"], ["4 / 4"]]


def test_les_liens_internes_gardent_leur_destination(fitz, complet):
    internes = [(i + 1, lien["page"] + 1) for i, page in enumerate(complet) for lien in page.get_links()
                if lien["kind"] == fitz.LINK_GOTO]
    assert internes == [(1, 2), (3, 4)]


def test_les_signets_des_deux_documents_sont_gardes_et_pointent_sur_la_bonne_page(complet):
    assert [(niveau, titre, page) for niveau, titre, page in complet.get_toc()] == [
        (1, "Rapport", 1), (2, "Rapport, deuxième page", 2), (1, "Annexe", 3), (2, "Annexe, deuxième page", 4)]


def test_une_page_sans_pied_fait_echouer_l_assemblage(fitz, tmp_path):
    rapport, annexe = tmp_path / "rapport.pdf", tmp_path / "annexe.pdf"
    _document(fitz, rapport, "Rapport")
    sans_pied = fitz.open()
    sans_pied.new_page().insert_text((72, 100), "aucun pied de page")
    sans_pied.save(annexe)
    with pytest.raises(ValueError, match="page 3"):
        assemblage.assembler(rapport, annexe, tmp_path / "complet.pdf")
