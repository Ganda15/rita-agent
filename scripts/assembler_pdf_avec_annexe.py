"""Assemble un rapport et son annexe en un seul PDF, numéroté de 1 à N en pied de page, liens et signets gardés.

Pourquoi ce script existe (05/11/2026, rapport E4 v1.3). `scripts/rendre_pdf.py` rend le rapport et l'annexe chacun avec
son pied « n / total ». Le jury reçoit un seul PDF : une seule numérotation doit valoir, celle que montre la visionneuse,
et les renvois de l'annexe (« A7, p. 31 ») s'y lisent. Le 04/11, une première version reconstruisait le PDF avec PyMuPDF
seul : pieds justes, mais 16 liens internes et 68 signets perdus. Ici, pypdf fusionne les deux documents (il garde les
liens internes, leurs destinations et les signets des deux), puis PyMuPDF ne touche qu'au pied de chaque page : il
l'efface et écrit « n / N » à sa place, même taille et même couleur. Le rapport seul garde son « n / 20 ».

Usage, depuis la racine :

    C:\\Python314\\python.exe -X utf8 scripts\\assembler_pdf_avec_annexe.py docs\\rapports\\E4\\rapport-E4.pdf docs\\rapports\\E4\\annexe-schemas-E4.pdf docs\\rapports\\E4\\rapport-E4-avec-annexe.pdf

Dépendances : `pypdf` et `pymupdf` (pip). Test : `tests/test_assembler_pdf_avec_annexe.py`.
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

PIED = re.compile(r"^\d+ / \d+$")
POLICE_WINDOWS = Path(r"C:\Windows\Fonts\segoeui.ttf")   # la police des pieds rendus par Chrome sur ce poste


def _pied(page):
    """Le seul span « n / total » du bas de la page ; ValueError s'il n'y en a pas exactement un."""
    trouves = [s for bloc in page.get_text("dict")["blocks"] for ligne in bloc.get("lines", []) for s in ligne["spans"]
               if PIED.match(s["text"].strip()) and s["bbox"][1] > page.rect.height - 60]
    if len(trouves) != 1:
        raise ValueError(f"page {page.number + 1} : {len(trouves)} pied(s) de page « n / total » trouvé(s), 1 attendu")
    return trouves[0]


def _renumeroter(page, numero: int, total: int) -> None:
    import fitz
    span = _pied(page)
    x0, y0, x1, y1 = span["bbox"]
    page.add_redact_annot(fitz.Rect(x0 - 40, y0 - 1, x1 + 1, y1 + 1), fill=(1, 1, 1))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    texte = f"{numero} / {total}"
    couleur = tuple(((span["color"] >> k) & 255) / 255 for k in (16, 8, 0))
    if POLICE_WINDOWS.exists():
        police = {"fontname": "segoe", "fontfile": str(POLICE_WINDOWS)}
        largeur = fitz.Font(fontfile=str(POLICE_WINDOWS)).text_length(texte, fontsize=span["size"])
    else:
        police = {"fontname": "helv"}
        largeur = fitz.get_text_length(texte, fontname="helv", fontsize=span["size"])
    page.insert_text((x1 - largeur, span["origin"][1]), texte, fontsize=span["size"], color=couleur, **police)


def assembler(rapport: Path, annexe: Path, sortie: Path) -> int:
    """Écrit `sortie` (rapport puis annexe), pieds « n / N », liens internes et signets gardés ; rend N."""
    import fitz
    from pypdf import PdfWriter

    fusion = PdfWriter()
    for chemin in (rapport, annexe):
        fusion.append(str(chemin))
    tampon = io.BytesIO()
    fusion.write(tampon)
    document = fitz.open("pdf", tampon.getvalue())
    total = len(document)
    for page in document:
        _renumeroter(page, page.number + 1, total)
    # 05/11 : la fusion perd la langue déclarée par Chrome ; on la remet. Limite connue : l'arbre de structure (balisage
    # d'accessibilité) des deux documents n'est pas fusionné ; le rapport seul, rendu par Chrome, reste balisé.
    document.set_language("fr")
    document.save(str(sortie), deflate=True)
    return total


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage : assembler_pdf_avec_annexe.py <rapport.pdf> <annexe.pdf> <sortie.pdf>")
    n = assembler(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
    print(f"{sys.argv[3]} : {n} pages, pieds de 1 à {n}")
