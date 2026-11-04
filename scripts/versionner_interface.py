"""Écrit la version de chaque script et de chaque feuille de style dans les pages de `frontend/` (refonte 001, 04/11/2026).

Pourquoi : un navigateur qui a gardé l'ancien `indicateurs.js` l'a affiché avec la page neuve (11 titres, 15 cases, les
chiffres décalés d'une colonne). Si l'adresse change avec le contenu (`indicateurs.js?v=3fa9c1d07b`), le navigateur ne
peut plus réutiliser l'ancien fichier : c'est une adresse qu'il n'a jamais vue. La version est l'empreinte du contenu, pas
une date : un fichier inchangé garde son adresse, donc son cache, et l'éco-conception n'y perd rien.

À relancer après toute modification d'un fichier `.js` ou `.css` de `frontend/` ; `tests/test_interface_versionnee.py`
échoue sinon et donne la commande :

    C:\\Python314\\python.exe scripts\\versionner_interface.py

Les images (logos) ne sont pas versionnées : elles changent rarement. Aucun script d'un autre site n'est touché.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

# <script src="x.js"> et <link ... href="x.css"> : un nom de fichier local, sans adresse complète ni dossier.
LIEN = re.compile(rb'(<(?:script|link)\b[^>]*?\b(?:src|href)=")([A-Za-z0-9_.-]+\.(?:js|css))(?:\?v=([0-9A-Za-z]*))?(")')


def empreinte(chemin: Path) -> str:
    """10 caractères de l'empreinte SHA-256 du contenu, fins de ligne ramenées à LF.

    Windows écrit CRLF, Linux (la CI, l'image Docker) LF : le même fichier doit donner la même version partout.
    """
    contenu = chemin.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(contenu).hexdigest()[:10]


def references(html: bytes) -> list[tuple[str, str | None]]:
    """Les (fichier, version) de chaque script et feuille de style locaux d'une page ; version None si absente."""
    return [(m.group(2).decode(), m.group(3).decode() if m.group(3) is not None else None) for m in LIEN.finditer(html)]


def versionner(html: bytes, dossier: Path = FRONTEND) -> bytes:
    """La page avec la bonne version dans chaque lien ; idempotent, fins de ligne gardées."""
    def remplacer(m: re.Match) -> bytes:
        nom = m.group(2).decode()
        return m.group(1) + nom.encode() + b"?v=" + empreinte(dossier / nom).encode() + m.group(4)
    return LIEN.sub(remplacer, html)


def main() -> int:
    modifiees = 0
    for page in sorted(FRONTEND.glob("*.html")):
        avant = page.read_bytes()
        apres = versionner(avant)
        if apres != avant:
            page.write_bytes(apres)
            modifiees += 1
            print(f"mise à jour : {page.name}")
    print(f"{modifiees} page(s) modifiée(s)" if modifiees else "toutes les versions sont à jour")
    return 0


if __name__ == "__main__":
    sys.exit(main())
