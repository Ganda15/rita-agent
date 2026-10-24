#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vérifie TOUS les liens des fichiers Markdown du dépôt — externes et internes.

Pourquoi ce script existe : un livrable de certification part au formateur et au jury.
Un lien mort dans un livrable, c'est un évaluateur qui clique et qui tombe sur une erreur.
Le contrôle ne peut pas dépendre de la mémoire de quelqu'un.

Deux familles de liens, deux pannes différentes :
  - EXTERNE  (http/https) : le site peut disparaître ou déplacer sa page
  - INTERNE  (chemin relatif) : le fichier peut être renommé ou jamais commité
                                -> c'est le piège du 11/08 : `evidence/C4/` était vide

Usage :
    C:\\Python314\\python.exe scripts/verifier_liens.py            # tout le dépôt
    C:\\Python314\\python.exe scripts/verifier_liens.py docs/      # un sous-dossier
    C:\\Python314\\python.exe scripts/verifier_liens.py --internes # sans réseau

Code de sortie : 0 si tout est bon, 1 s'il existe au moins un lien cassé.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# [texte](cible) — on ignore les images ![alt](...) traitées pareil, et les ancres pures (#x)
MOTIF_LIEN = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)>\s]+)>?[^)]*\)")
IGNORES = ("mailto:", "tel:", "#", "javascript:")
DELAI_S = 20
AGENT = "Mozilla/5.0 (verificateur-de-liens RITA)"


def fichiers_markdown(depart: Path) -> list[Path]:
    exclus = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache"}
    return sorted(
        c for c in depart.rglob("*.md")
        if not exclus & set(c.relative_to(RACINE).parts)
    )


def liens_du_fichier(chemin: Path) -> list[tuple[int, str]]:
    """Retourne [(numéro de ligne, cible)] — le numéro sert à retrouver le lien vite."""
    trouves = []
    for n, ligne in enumerate(chemin.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        for cible in MOTIF_LIEN.findall(ligne):
            if not cible.startswith(IGNORES):
                trouves.append((n, cible))
    return trouves


def verifier_interne(source: Path, cible: str) -> str | None:
    """None si le fichier visé existe, sinon le motif de l'échec."""
    chemin = (source.parent / cible.split("#")[0]).resolve()
    if not chemin.exists():
        return "fichier introuvable"
    if not str(chemin).startswith(str(RACINE)):
        # Règle établie le 11/08 : un livrable ne pointe jamais hors du dépôt.
        return "pointe HORS du depot"
    return None


# Chaque forme d'URL du dépôt, et la question qui la vérifie dans l'API de GitHub (24/10/2026). Avant, seule
# `/tree/<ref>` était connue : 116 liens (fichiers, PR, issues, passages de CI) restaient « non vérifiables ».
FORMES_GITHUB = (
    (re.compile(r"/blob/([^/]+)/(.+)"), lambda m: f"contents/{m[2]}?ref={m[1]}"),
    (re.compile(r"/tree/([^/]+)/(.+)"), lambda m: f"contents/{m[2]}?ref={m[1]}"),
    (re.compile(r"/tree/([^/]+)/?"), lambda m: f"contents/?ref={m[1]}"),
    (re.compile(r"/pull/(\d+)(?:/.*)?"), lambda m: f"pulls/{m[1]}"),
    (re.compile(r"/issues/(\d+)(?:/.*)?"), lambda m: f"issues/{m[1]}"),
    (re.compile(r"/actions/runs/(\d+)(?:/.*)?"), lambda m: f"actions/runs/{m[1]}"),
    (re.compile(r"/actions/workflows/([^/]+\.ya?ml)"), lambda m: f"actions/workflows/{m[1]}"),   # l'API accepte le nom du fichier
    (re.compile(r"/commit/([0-9a-f]{7,40})"), lambda m: f"commits/{m[1]}"),
)


def point_api_github(url: str) -> str | None:
    """La question à poser à l'API de GitHub pour vérifier ce lien, ou None si sa forme est inconnue.

    L'ancre (`#L12`) et la requête (`?plain=1`) sont retirées : elles ne changent pas l'existence de la cible.
    """
    m = re.match(r"https://github\.com/([^/]+)/([^/?#]+)(/[^?#]*)?", url)
    if not m:
        return None
    proprietaire, depot, chemin = m[1], m[2], m[3] or ""
    for motif, question in FORMES_GITHUB:
        trouve = motif.fullmatch(chemin)
        if trouve:
            return f"repos/{proprietaire}/{depot}/{question(trouve)}"
    return None


def verifier_github_prive(url: str) -> str | None:
    """Vérifie un lien vers le dépôt privé du projet, via `gh` (authentifié).

    ⚠️ Écrit le 18/08/2026 après un **faux positif de ce script**. Le dépôt est privé :
    une requête HTTP anonyme reçoit **404** sur un lien pourtant valide. Le script
    signalait donc comme cassé le lien du tag `livrable-E1-v1` — celui-là même qu'on
    envoie au formateur.

    *Un vérificateur qui crie au loup sur des liens corrects finit par être ignoré, et
    c'est alors le vrai lien cassé qui passe.*
    """
    import subprocess

    point = point_api_github(url)
    if point is None:
        return "HTTP 404 (dépôt privé, forme d'URL non vérifiable par gh)"

    try:
        r = subprocess.run(["gh", "api", point], capture_output=True, timeout=DELAI_S)
    except Exception as erreur:
        return f"HTTP 404 et gh injoignable ({type(erreur).__name__})"

    if r.returncode != 0:
        return f"introuvable meme via gh : {point}"
    return None      # la cible existe : le lien est bon pour qui a l'accès


def verifier_externe(url: str) -> str | None:
    import httpx
    try:
        r = httpx.get(url, follow_redirects=True, timeout=DELAI_S,
                      headers={"User-Agent": AGENT})
    except Exception as erreur:
        return f"injoignable ({type(erreur).__name__})"

    # Un 404 sur notre propre dépôt GitHub ne prouve rien : il est privé.
    # On retente avec `gh`, qui est authentifié.
    if r.status_code == 404 and "github.com/Ganda15/" in url:
        return verifier_github_prive(url)

    return None if r.status_code < 400 else f"HTTP {r.status_code}"


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sans_reseau = "--internes" in sys.argv
    depart = (RACINE / args[0]).resolve() if args else RACINE

    fichiers = fichiers_markdown(depart)
    casses: list[str] = []
    n_ext = n_int = 0

    print(f"Verification des liens — {len(fichiers)} fichiers Markdown sous {depart}\n")

    for fichier in fichiers:
        relatif = fichier.relative_to(RACINE)
        for ligne, cible in liens_du_fichier(fichier):
            if cible.startswith(("http://", "https://")):
                if sans_reseau:
                    continue
                n_ext += 1
                probleme = verifier_externe(cible)
            else:
                n_int += 1
                probleme = verifier_interne(fichier, cible)

            if probleme:
                casses.append(f"{relatif}:{ligne}  {probleme}\n      -> {cible}")
                print(f"  CASSE  {relatif}:{ligne}  {probleme}")

    print(f"\n{'-' * 60}")
    print(f"Liens internes verifies : {n_int}")
    print(f"Liens externes verifies : {n_ext}" + ("  (ignores : --internes)" if sans_reseau else ""))
    print(f"Liens casses            : {len(casses)}")

    if casses:
        print("\nDETAIL :")
        for c in casses:
            print(f"  - {c}")
        return 1

    print("\nAucun lien casse.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
