"""Le sommaire du rapport E4 dit vrai : chaque numéro imprimé est la page où commence sa section (E4 v0.8, 31/10/2026).

Pourquoi : même règle que pour E3 (`tests/test_rapport_e3_sommaire.py`). Les numéros sont lus dans le PDF et écrits dans
la source par `scripts/rendre_pdf.py` ; ces tests gardent la source et le PDF d'accord.
"""
import re
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
RAPPORT = RACINE / "docs/rapports/E4/rapport-E4.md"
ENTREE = re.compile(r'<a href="#([\w-]+)">[^<]*</a><span>p\. (\d+)</span>')
SECTIONS = 9   # huit sections et le glossaire


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


ANNEXE = RAPPORT.with_name("annexe-schemas-E4.md")
COMPLET = RAPPORT.with_name("rapport-E4-avec-annexe.pdf")
LIGNE = re.compile(r"^\| (A\d) \|.*\| (\d+)(?: (?:à|et) (\d+))? \|\s*$", re.M)
MINIATURE = re.compile(r'<a href="#a(\d)">.*?<span>A\d · [^<]* · p\. (\d+)</span>')
DEBUT_ANNEXE = re.compile(r"<li>Annexes A1 à A7[^<]*<span>p\. (\d+)</span></li>")


def test_les_pages_de_l_annexe_annoncees_sont_celles_du_pdf_complet():
    # E4 v1.5 (05/11/2026) : l'annexe annonce ses pages dans le PDF complet (tableau et miniatures), le sommaire du
    # rapport annonce son début. Ces numéros ne sont pas calculés par `scripts/rendre_pdf.py` : ce test les tient, en les
    # comparant aux signets que Chrome tire des titres.
    fitz = pytest.importorskip("fitz", reason="PyMuPDF absent : le PDF se relit sur le poste, la CI ne rend pas de PDF")
    annexe = ANNEXE.read_text(encoding="utf-8")
    tableau = {schema: (int(debut), int(fin or debut)) for schema, debut, fin in LIGNE.findall(annexe)}
    miniatures = {f"A{n}": int(page) for n, page in MINIATURE.findall(annexe)}
    assert sorted(tableau) == sorted(miniatures) == [f"A{n}" for n in range(1, 8)]
    with fitz.open(COMPLET) as pdf:
        total = len(pdf)
        signets = {titre.split(".")[0]: page for _, titre, page in pdf.get_toc() if re.match(r"A\d\. ", titre)}
        annexe_debut = next(page for _, titre, page in pdf.get_toc() if titre.startswith("Annexe du rapport E4"))
    assert int(DEBUT_ANNEXE.search(RAPPORT.read_text(encoding="utf-8")).group(1)) == annexe_debut
    for schema, (debut, fin) in tableau.items():
        assert signets[schema] == debut == miniatures[schema], f"{schema} : annoncé p. {debut}, commence p. {signets[schema]}"
        suivant = signets.get(f"A{int(schema[1]) + 1}", total + 1)
        assert fin == suivant - 1, f"{schema} : annoncé jusqu'à la p. {fin}, finit p. {suivant - 1}"
