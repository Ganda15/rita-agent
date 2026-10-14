"""Rend un rapport Markdown du dépôt en HTML puis en PDF A4, avec la feuille de style des rapports RITA.

Pourquoi ce script existe (03/10/2026). Les rapports E3, E4, E5 s'écrivent en Markdown dans `docs/rapports/`
(lisible dans GitHub, relu par diff). Le jury reçoit un PDF. Plutôt qu'une mise en page à la main à chaque
version, la conversion est une commande, reproductible, et le PDF regardé page par page avant l'envoi.

Usage, depuis la racine :

    C:\\Python314\\python.exe -X utf8 scripts\\rendre_pdf.py docs\\rapports\\E3\\rapport-E3.md

Produit `rapport-E3.html` et `rapport-E3.pdf` à côté du `.md`, et affiche le nombre de pages.
Dépendances : `markdown` (pip), Chrome installé (impression sans fenêtre), `pypdf` pour compter les pages.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

STYLE = """
:root{ --ink:#16202B; --ink-soft:#4A5766; --rule:#D5DCE4; --rule-strong:#9DAAB8; --accent:#14607F; --wash:#ECF3F7; --flag:#9E4318; }
@page{ size:A4; margin:14mm 14mm 14mm 14mm; }
*{ box-sizing:border-box; }
body{ margin:0; color:var(--ink); font-family:"Segoe UI","Calibri",system-ui,sans-serif; font-size:10pt; line-height:1.4;
      font-variant-numeric:tabular-nums; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
h1,h2,h3,h4{ font-family:Georgia,"Times New Roman",serif; font-weight:600; margin:0; color:var(--ink); break-after:avoid; }
h1{ font-size:20pt; line-height:1.2; border-top:2.5pt solid var(--accent); padding-top:8pt; margin-bottom:8pt; }
h2{ font-size:14pt; margin:18pt 0 6pt; padding-bottom:3pt; border-bottom:.75pt solid var(--rule-strong); }
h3{ font-size:11.5pt; margin:12pt 0 4pt; color:var(--accent); }
h4{ font-size:10.5pt; margin:10pt 0 3pt; color:var(--accent); font-family:"Segoe UI",sans-serif; }
p{ margin:0 0 6pt; }
ul,ol{ margin:0 0 6pt; padding-left:16pt; }
li{ margin-bottom:2pt; }
strong{ font-weight:600; }
em{ font-style:italic; }
code{ font-family:Consolas,"Courier New",monospace; font-size:9pt; background:var(--wash); padding:0 2pt; border-radius:2pt; }
pre{ font-family:Consolas,monospace; font-size:8.6pt; line-height:1.38; background:#F7F9FB; border:.4pt solid var(--rule);
     border-left:2pt solid var(--rule-strong); padding:6pt 8pt; margin:5pt 0 8pt; white-space:pre-wrap; overflow-wrap:anywhere; break-inside:avoid; }
pre code{ background:none; padding:0; font-size:inherit; }
table{ width:100%; border-collapse:collapse; margin:5pt 0 9pt; font-size:9.2pt; break-inside:auto; }
th{ text-align:left; font-weight:700; font-size:8pt; letter-spacing:.06em; text-transform:uppercase; color:var(--ink-soft);
    border-bottom:.75pt solid var(--rule-strong); padding:3pt 6pt 3pt 0; vertical-align:bottom; }
td{ padding:3pt 6pt 3pt 0; border-bottom:.4pt solid var(--rule); vertical-align:top; }
tr{ break-inside:avoid; }
blockquote{ border-left:2.2pt solid var(--accent); background:var(--wash); padding:5pt 9pt; margin:6pt 0; color:var(--ink); }
hr{ border:0; border-top:.5pt solid var(--rule); margin:12pt 0; }
img{ max-width:100%; height:auto; display:block; margin:6pt auto; }
a{ color:var(--accent); text-decoration:none; }
h2 + table, h3 + table{ margin-top:4pt; }
"""


def rendre(chemin_md: Path) -> tuple[Path, Path, int]:
    texte = chemin_md.read_text(encoding="utf-8")
    corps = markdown.markdown(texte, extensions=["tables", "fenced_code", "sane_lists", "attr_list"], output_format="html5")
    titre = next((l.lstrip("# ").strip() for l in texte.splitlines() if l.startswith("# ")), chemin_md.stem)
    html = ("<!DOCTYPE html>\n<html lang=\"fr\">\n<head>\n<meta charset=\"utf-8\">\n"
            f"<title>{titre}</title>\n<style>{STYLE}</style>\n</head>\n<body>\n{corps}\n</body>\n</html>\n")
    chemin_html = chemin_md.with_suffix(".html")
    chemin_html.write_text(html, encoding="utf-8")
    chemin_pdf = chemin_md.with_suffix(".pdf")
    profil = Path(tempfile.gettempdir()) / "chrome-rendu-rita"   # Chrome exige un profil, sinon échec silencieux
    subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--user-data-dir={profil}", f"--print-to-pdf={chemin_pdf.resolve()}",
                    chemin_html.resolve().as_uri()], check=True, capture_output=True)
    try:
        import pypdf
        pages = len(pypdf.PdfReader(str(chemin_pdf)).pages)
    except Exception:  # noqa: BLE001
        pages = -1
    return chemin_html, chemin_pdf, pages


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    chemin_md = Path(argv[1])
    if not chemin_md.exists():
        print(f"introuvable : {chemin_md}")
        return 1
    html, pdf, pages = rendre(chemin_md)
    print(f"html : {html}\npdf  : {pdf}\npages : {pages}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
