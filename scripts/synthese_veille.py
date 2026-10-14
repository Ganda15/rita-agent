"""Assemble la synthèse mensuelle de la veille C6 : une page de garde, puis les notes hebdomadaires, telles quelles.

Pourquoi ce script (03/10/2026). La première synthèse (08/09/2026) avait été assemblée sans source versionnée :
quand une note change, le PDF ne peut pas se corriger à la main sans diverger. Ici la synthèse est un fichier
Markdown produit depuis les notes, et le PDF se rend ensuite par `scripts/rendre_pdf.py`. Rien n'est reformulé,
rien n'est résumé : chaque note est reproduite telle qu'elle figure dans le dépôt.

Usage, depuis la racine :

    C:\\Python314\\python.exe -X utf8 scripts\\synthese_veille.py 33 36
    C:\\Python314\\python.exe -X utf8 scripts\\rendre_pdf.py docs\\veille\\Veille-C6-synthese-S33-a-S36.md
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
VEILLE = RACINE / "docs" / "veille"
ANNEE = 2026


def notes_entre(debut: int, fin: int) -> list[tuple[int, Path]]:
    notes = []
    for s in range(debut, fin + 1):
        trouvees = sorted(VEILLE.glob(f"{ANNEE}-S{s:02d}-*.md"))
        if trouvees:
            notes.append((s, trouvees[0]))
    return notes


def titre_de(chemin: Path) -> str:
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        if ligne.startswith("# "):
            return ligne[2:].strip()
    return chemin.stem


def entete_sur_lignes_separees(texte: str) -> str:
    """Les lignes d'en-tête d'une note (`**Auteur** : …`, `**Semaine** : …`) se suivent sans ligne vide ;
    Markdown les fusionnerait en un seul paragraphe. Deux espaces en fin de ligne forcent le retour,
    seulement avant le premier titre de section, et le fichier d'origine n'est pas touché."""
    sortie, avant_section = [], True
    for ligne in texte.split("\n"):
        if ligne.startswith("## "):
            avant_section = False
        if avant_section and ligne.startswith("**") and not ligne.endswith("  "):
            ligne += "  "
        sortie.append(ligne)
    return "\n".join(sortie)


def assembler(debut: int, fin: int, aujourdhui: dt.date) -> Path:
    notes = notes_entre(debut, fin)
    if not notes:
        raise SystemExit(f"aucune note entre S{debut} et S{fin} dans {VEILLE}")
    lundi = dt.date.fromisocalendar(ANNEE, debut, 1)
    dimanche = dt.date.fromisocalendar(ANNEE, fin, 7)
    manquantes = [f"S{s}" for s in range(debut, fin + 1) if s not in {n for n, _ in notes}]
    lignes = [
        "# Veille technique : synthèse mensuelle",
        "",
        "**Thématique** : sécurité des agents LLM, l'injection de prompt  ",
        "**Projet** : RITA, Retrieval Intelligence pour le Tracking et l'Analyse  ",
        "**Auteur des notes** : Eramalingam GANDAKUMAR  ",
        f"**Période couverte** : semaines ISO {debut} à {fin} ({lundi:%d/%m/%Y} au {dimanche:%d/%m/%Y})  ",
        "**Créneau de veille** : lundi 09h00 à 10h00, une note par semaine  ",
        f"**Assemblée le** : {aujourdhui:%d/%m/%Y} par `scripts/synthese_veille.py` depuis les notes du dépôt",
        "",
        "## Ce que contient ce document",
        "",
        "| Semaine | Note | Fichier dans le dépôt |",
        "|---|---|---|",
    ]
    for s, chemin in notes:
        lignes.append(f"| S{s} | {titre_de(chemin)} | `{chemin.name}` |")
    if manquantes:
        lignes += ["", f"Semaines sans note dans cette période : {', '.join(manquantes)} (dit tel quel, pas antidaté)."]
    lignes += [
        "",
        "Protocole de veille : sources retenues, critères de fiabilité, méthode de relevé et règles d'accessibilité sont",
        "décrits dans `docs/veille/README.md` du dépôt `Ganda15/rita-agent`.",
        "",
        "Note sur ce document : il s'agit d'une compilation des notes hebdomadaires, sans reformulation ni résumé ajouté.",
        "Chaque note est reproduite telle qu'elle figure dans le dépôt, dans l'ordre chronologique. Deux notes (S35, S36)",
        "ont été rédigées en rattrapage le 08/09/2026 et le disent dans leur en-tête ; leurs étiquettes de semaine ont été",
        "corrigées le 03/10/2026 pour suivre le calendrier ISO, la période réellement balayée restant indiquée.",
        "",
    ]
    for s, chemin in notes:
        texte = chemin.read_text(encoding="utf-8").strip("\n")
        lignes += ['<div style="break-before:page"></div>', "", entete_sur_lignes_separees(texte), ""]
    sortie = VEILLE / f"Veille-C6-synthese-S{debut}-a-S{fin}.md"
    sortie.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return sortie


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    sortie = assembler(int(argv[1]), int(argv[2]), dt.date.today())
    print(f"synthese : {sortie} ({len(sortie.read_text(encoding='utf-8').split())} mots)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
