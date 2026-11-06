"""Rend un rapport Markdown du dépôt en HTML puis en PDF A4, avec la feuille de style des rapports RITA.

Pourquoi ce script existe (03/10/2026). Les rapports E3, E4, E5 s'écrivent en Markdown dans `docs/rapports/`
(lisible dans GitHub, relu par diff). Le jury reçoit un PDF. Plutôt qu'une mise en page à la main à chaque
version, la conversion est une commande, reproductible, et le PDF regardé page par page avant l'envoi.

Usage, depuis la racine :

    C:\\Python314\\python.exe -X utf8 scripts\\rendre_pdf.py docs\\rapports\\E3\\rapport-E3.md

Produit `rapport-E3.html` et `rapport-E3.pdf` à côté du `.md`, et affiche le nombre de pages. Avec `--lisible`
(guide d'exploitation, C8.5) : texte à 12 pt, liens soulignés, titres sans empattement. Les signets du PDF sont toujours
tirés des titres. Avec `--annexe <annexe.md>` (05/11/2026) : rapport et annexe rendus dans un seul document,
`<rapport>-avec-annexe.pdf`, en français et balisé pour les lecteurs d'écran, comme le rapport seul :

    C:\\Python314\\python.exe -X utf8 scripts\\rendre_pdf.py docs\\rapports\\E2\\rapport-E2.md --annexe docs\\rapports\\E2\\annexe-schemas-E2.md
Dépendances : `markdown` (pip), Chrome installé (impression sans fenêtre), `pypdf` pour compter les pages.

Sommaire (27/10/2026, rapport E3 v1.9). Si le `.md` contient un sommaire (`<a href="#ancre">…</a><span>p. N</span>`),
aucun numéro n'est tapé à la main : chaque entrée est un lien vers son titre, Chrome résout ce lien en page dans le
PDF, le script lit ces pages (PyMuPDF), les écrit dans le `.md` et rend de nouveau, jusqu'à ce qu'aucun numéro ne
change. Un sommaire tapé à la main se périme à la première retouche ; `tests/test_rapport_e3_sommaire.py` garde la
source et le PDF d'accord.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

SOMMAIRE = re.compile(r'(<a href="#([\w-]+)">[^<]*</a><span>)p\. \d+(</span>)')

CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

STYLE = """
:root{ --ink:#16202B; --ink-soft:#4A5766; --rule:#D5DCE4; --rule-strong:#9DAAB8; --accent:#14607F; --wash:#ECF3F7; --flag:#9E4318;
       --marine:#12395E; --bandeau-titre:#BFD7F2; --bandeau-sous-titre:#D6E6F7; }
@page{ size:A4; margin:14mm 14mm 14mm 14mm;
  @bottom-right{ content:counter(page) " / " counter(pages); font-family:"Segoe UI",sans-serif; font-size:8pt; color:#5b6472; } }
*{ box-sizing:border-box; }
body{ margin:0; color:var(--ink); font-family:"Segoe UI","Calibri",system-ui,sans-serif; font-size:10pt; line-height:1.4;
      font-variant-numeric:tabular-nums; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
h1,h2,h3,h4{ font-family:Georgia,"Times New Roman",serif; font-weight:600; margin:0; color:var(--ink); break-after:avoid; }
/* Titres (06/11/2026, décision d'Era) : le style « bandeaux bleus » de sa copie E2 v1.1, sans ses deux filets.
   Titres (h1, h2) en noir sur #BFD7F2, sous-titres (h3) en bleu sur #D6E6F7, une bande bleu marine à gauche ;
   la bande est dans le fond (dégradé net), pas une bordure ; marges intérieures du modèle (1 à 2 pt), pour ne pas
   allonger les rapports ; h1 évite le logo flottant. */
h1{ font-size:20pt; line-height:1.2; background:linear-gradient(to right, var(--marine) 5pt, var(--bandeau-titre) 5pt); color:var(--ink); padding:2pt 8pt 2pt 12pt; margin-bottom:8pt; display:flow-root; }
h2{ font-size:14pt; margin:16pt 0 5pt; padding:1pt 8pt 1pt 12pt; background:linear-gradient(to right, var(--marine) 5pt, var(--bandeau-titre) 5pt); color:var(--ink); }
h3{ font-size:11.5pt; margin:10pt 0 3pt; padding:1pt 8pt 1pt 11pt; background:linear-gradient(to right, var(--marine) 4pt, var(--bandeau-sous-titre) 4pt); color:var(--accent); }
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

# Option `--lisible` (31/10/2026, C8.5) : le guide d'exploitation se remet aux parties prenantes « dans un format qui
# respecte les recommandations d'accessibilité ». Ajoutée APRÈS la feuille des rapports, elle l'emporte sur elle : texte
# et tableaux à 12 pt (minimum couramment cité pour un document texte), code à 11 pt, titres sans empattement, liens
# soulignés (la couleur seule ne suffit pas). Les rapports gardent leur mise en page : leur nombre de pages est limité.
STYLE_LISIBLE = """
@page{ @bottom-right{ font-size:10pt; } }
body{ font-size:12pt; line-height:1.5; }
h1,h2,h3,h4{ font-family:"Segoe UI","Calibri",system-ui,sans-serif; }
h1{ font-size:22pt; }
h2{ font-size:16pt; }
h3{ font-size:13.5pt; }
h4{ font-size:12.5pt; }
code{ font-size:11pt; }
pre{ font-size:11pt; line-height:1.4; }
table{ font-size:12pt; }
th{ font-size:12pt; letter-spacing:0; text-transform:none; color:var(--ink); }
a{ text-decoration:underline; }
"""


# Un lien Markdown relatif (`../db/registre.md`) devient, une fois imprimé, une adresse de fichier du poste
# (`/C:/Users/...`) : mort pour qui lit le PDF, et il expose un chemin local (relevé le 31/10 dans le guide). On garde
# son texte. Restent des liens : les ancres (#), le web, les adresses de courriel, et les images (`![...]`).
LIEN_RELATIF = re.compile(r"(?<!!)\[([^\]]+)\]\((?!https?://|#|mailto:)[^)\s]+\)")


def delier_les_liens_relatifs(texte: str) -> str:
    """Remplace chaque lien relatif vers un fichier du dépôt par son seul texte."""
    return LIEN_RELATIF.sub(r"\1", texte)


def feuille_de_style(lisible: bool) -> str:
    """La feuille des rapports, suivie des règles de lecture facilitée si `lisible`."""
    return STYLE + STYLE_LISIBLE if lisible else STYLE


def commande_chrome(chemin_html: Path, chemin_pdf: Path, profil: Path) -> list[str]:
    """Impression sans fenêtre ; les signets du PDF sont tirés des titres (navigation au clavier et au lecteur d'écran)."""
    return [str(CHROME), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--generate-pdf-document-outline",
            f"--user-data-dir={profil}", f"--print-to-pdf={chemin_pdf.resolve()}", chemin_html.resolve().as_uri()]


def numeroter_sommaire(texte: str, pages: dict[str, int]) -> str:
    """Écrit dans chaque entrée du sommaire la page où commence sa section ; une ancre sans page lève KeyError."""
    return SOMMAIRE.sub(lambda m: f"{m.group(1)}p. {pages[m.group(2)]}{m.group(3)}", texte)


def _pages_des_ancres(chemin_pdf: Path) -> dict[str, int]:
    """Page visée (comptée à partir de 1) par chaque lien de la première page, telle que Chrome l'a résolue."""
    import fitz  # PyMuPDF, sur le poste seulement : la CI ne rend pas de PDF

    with fitz.open(chemin_pdf) as pdf:
        return {lien["nameddest"]: lien["page"] + 1 for lien in pdf[0].get_links() if lien.get("nameddest")}


def rendre(chemin_md: Path, lisible: bool = False) -> tuple[Path, Path, int]:
    for _ in range(4):
        texte = chemin_md.read_bytes().decode("utf-8")   # en octets : les fins de ligne ne changent pas
        chemin_html, chemin_pdf = _imprimer(chemin_md, texte, lisible)
        if not SOMMAIRE.search(texte):
            break
        nouveau = numeroter_sommaire(texte, _pages_des_ancres(chemin_pdf))
        if nouveau == texte:
            break
        chemin_md.write_bytes(nouveau.encode("utf-8"))   # la source garde les numéros du PDF rendu
    else:
        raise RuntimeError("les numéros du sommaire ne se stabilisent pas après quatre rendus")
    try:
        import pypdf
        pages = len(pypdf.PdfReader(str(chemin_pdf)).pages)
    except Exception:  # noqa: BLE001
        pages = -1
    return chemin_html, chemin_pdf, pages


def _corps(texte: str) -> str:
    import markdown  # ici et pas en tête : les tests du sommaire importent ce module sans `markdown`

    return markdown.markdown(delier_les_liens_relatifs(texte), extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
                             output_format="html5")


def _titre(texte: str, defaut: str) -> str:
    return next((l.lstrip("# ").strip() for l in texte.splitlines() if l.startswith("# ")), defaut)


def _page_html(titre: str, style: str, corps: str) -> str:
    return ("<!DOCTYPE html>\n<html lang=\"fr\">\n<head>\n<meta charset=\"utf-8\">\n"
            f"<title>{titre}</title>\n<style>{style}</style>\n</head>\n<body>\n{corps}\n</body>\n</html>\n")


def _chrome(chemin_html: Path, chemin_pdf: Path) -> None:
    profil = Path(tempfile.gettempdir()) / "chrome-rendu-rita"   # Chrome exige un profil, sinon échec silencieux
    subprocess.run(commande_chrome(chemin_html, chemin_pdf, profil), check=True, capture_output=True)


def _imprimer(chemin_md: Path, texte: str, lisible: bool = False) -> tuple[Path, Path]:
    html = _page_html(_titre(texte, chemin_md.stem), feuille_de_style(lisible), _corps(texte))
    chemin_html = chemin_md.with_suffix(".html")
    chemin_html.write_text(html, encoding="utf-8")
    chemin_pdf = chemin_md.with_suffix(".pdf")
    _chrome(chemin_html, chemin_pdf)
    return chemin_html, chemin_pdf


# Rapport et annexe dans un seul document (05/11/2026). Le PDF « avec annexe » était fusionné après coup : la fusion garde
# pages, liens et signets, mais perd la langue déclarée et l'arbre de structure que Chrome écrit (mesure du 05/11 sur E1,
# E2 et E4). Rendus ensemble, ils les gardent, et les pieds se numérotent de bout en bout. L'annexe porte sa propre
# feuille (`<style>` en tête du `.md`) : sa règle `@page` devient la page nommée « annexe » (paysage), et ses autres
# règles sont imbriquées dans `.annexe{ }` (imbrication CSS, Chrome 120 et plus) pour ne pas toucher au rapport.
BLOC_STYLE = re.compile(r"<style>(.*?)</style>", re.S)
IDENTIFIANT = re.compile(r'\bid="([^"]+)"')


def _fin_du_bloc(css: str, ouvrante: int) -> int:
    """Position juste après l'accolade qui ferme celle de `ouvrante`."""
    profondeur = 0
    for i in range(ouvrante, len(css)):
        profondeur += {"{": 1, "}": -1}.get(css[i], 0)
        if profondeur == 0:
            return i + 1
    raise ValueError("feuille de l'annexe : accolade non fermée")


def feuille_annexe(style: str) -> str:
    """La feuille de l'annexe pour le document complet : `@page` nommée « annexe », autres règles limitées à sa section."""
    pages, reste = [], style
    while (debut := reste.find("@page")) != -1:
        ouvrante = reste.index("{", debut)
        if reste[debut + len("@page"):ouvrante].strip():
            raise ValueError(f"feuille de l'annexe : règle {reste[debut:ouvrante].strip()!r} déjà nommée, à renommer à la main")
        fin = _fin_du_bloc(reste, ouvrante)
        pages.append("@page annexe" + reste[ouvrante:fin])
        reste = reste[:debut] + reste[fin:]
    return "\n".join(pages) + "\n.annexe{ page:annexe; break-before:page;\n" + reste.strip() + "\n}\n"


def document_avec_annexe(titre: str, style: str, corps_rapport: str, style_annexe: str, corps_annexe: str) -> str:
    """Un seul document HTML : le rapport, puis l'annexe dans `<section class="annexe">`."""
    doubles = sorted(set(IDENTIFIANT.findall(corps_rapport)) & set(IDENTIFIANT.findall(corps_annexe)))
    if doubles:
        raise ValueError(f"identifiant(s) présents dans le rapport et dans l'annexe : {', '.join(doubles)}")
    corps = f'{corps_rapport}\n<section class="annexe">\n{corps_annexe}\n</section>'
    return _page_html(titre, style + "\n" + feuille_annexe(style_annexe), corps)


def rendre_avec_annexe(chemin_md: Path, chemin_annexe: Path) -> tuple[Path, Path, int]:
    """Produit `<rapport>-avec-annexe.html` et `.pdf` ; ne réécrit pas la source (le sommaire est celui du rapport seul)."""
    texte = chemin_md.read_bytes().decode("utf-8")
    texte_annexe = chemin_annexe.read_bytes().decode("utf-8")
    style_annexe = "\n".join(BLOC_STYLE.findall(texte_annexe))
    html = document_avec_annexe(_titre(texte, chemin_md.stem), feuille_de_style(False), _corps(texte),
                                style_annexe, _corps(BLOC_STYLE.sub("", texte_annexe)))
    chemin_html = chemin_md.with_name(f"{chemin_md.stem}-avec-annexe.html")
    chemin_html.write_text(html, encoding="utf-8")
    chemin_pdf = chemin_html.with_suffix(".pdf")
    _chrome(chemin_html, chemin_pdf)
    import pypdf
    return chemin_html, chemin_pdf, len(pypdf.PdfReader(str(chemin_pdf)).pages)


def lire_arguments(argv: list[str]) -> tuple[str, bool] | None:
    """Le chemin du `.md` et l'option `--lisible`, ou None si la ligne de commande ne nomme pas un seul fichier."""
    args = argv[1:]
    if "--annexe" in args:
        i = args.index("--annexe")
        if i + 1 >= len(args):
            return None
        args = args[:i] + args[i + 2:]
    lisible = "--lisible" in args
    chemins = [a for a in args if a != "--lisible"]
    return (chemins[0], lisible) if len(chemins) == 1 else None


def lire_annexe(argv: list[str]) -> str | None:
    """Le chemin donné après `--annexe`, ou None."""
    args = argv[1:]
    return args[args.index("--annexe") + 1] if "--annexe" in args[:-1] else None


def main(argv: list[str]) -> int:
    arguments = lire_arguments(argv)
    if arguments is None:
        print(__doc__)
        return 2
    chemin_md, lisible = Path(arguments[0]), arguments[1]
    annexe = lire_annexe(argv)
    for chemin in (chemin_md, Path(annexe) if annexe else None):
        if chemin is not None and not chemin.exists():
            print(f"introuvable : {chemin}")
            return 1
    if annexe:
        html, pdf, pages = rendre_avec_annexe(chemin_md, Path(annexe))
    else:
        html, pdf, pages = rendre(chemin_md, lisible)
    print(f"html : {html}\npdf  : {pdf}\npages : {pages}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
