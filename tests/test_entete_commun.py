"""Refonte 001, tâche 4 (exigence R5) : un en-tête identique dans les cinq pages, et le style A.

L'en-tête reste du HTML écrit dans chaque page (il marche sans JavaScript) : la marque, l'avertissement AMF et la
navigation vers les cinq écrans, dans le même ordre ; seule l'entrée de la page courante diffère (`aria-current`).
Le titre propre à chaque page (`<h1>`) est dans `<main>`. Deux thèmes : sombre par défaut, clair au choix (décision d'Era du 04/11, spécification § 4 et § 7).
Couleurs : `specs/001-refonte-interface/plan.md`, contraintes globales ; un contraste d'au moins 4,5:1 (WCAG 1.4.3)
est calculé ici dans les deux thèmes, pas supposé.
"""
import re
from pathlib import Path

import pytest

from tests.test_frontend import code_sans_commentaires

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
# (fichier, écran, libellé dans la navigation), dans l'ordre de la navigation
ECRANS = [("index.html", "portefeuille", "Mon portefeuille"), ("indicateurs.html", "indicateurs", "Indicateurs"),
          ("briefing.html", "briefing", "Briefing"), ("question.html", "question", "Question"),
          ("tableau-de-bord.html", "tableau-de-bord", "Tableau de bord")]
# Les couleurs des écrans, dans les deux thèmes (plan, contraintes globales ; décision d'Era du 04/11 après-midi).
# Question et Tableau de bord partagent la palette « service ».
PALETTE = {"portefeuille": "portefeuille", "indicateurs": "indicateurs", "briefing": "briefing",
           "question": "service", "tableau-de-bord": "service"}
COULEURS = {"clair": {"portefeuille": "#1e7b45", "indicateurs": "#3f3fa8", "briefing": "#a35a00", "service": "#12507a"},
            "sombre": {"portefeuille": "#4ccb8a", "indicateurs": "#a5a8ff", "briefing": "#f2a93b", "service": "#6cb8ea"}}
AVERTISSEMENT = "Aide à la lecture. Aucune recommandation d'achat ou de vente."


def html(fichier: str) -> str:
    return (FRONTEND / fichier).read_text(encoding="utf-8")


def entete(fichier: str) -> str:
    trouve = re.search(r"<header\b.*?</header>", html(fichier), re.S)
    assert trouve, f"{fichier} : pas d'en-tête"
    return trouve.group(0)


def entrees_de_navigation(fichier: str) -> list[tuple[str, str | None, str]]:
    """(balise, href ou None, libellé) de chaque entrée de la navigation principale, dans l'ordre."""
    nav = re.search(r'<nav aria-label="Navigation principale">(.*?)</nav>', entete(fichier), re.S)
    assert nav, f"{fichier} : pas de navigation principale dans l'en-tête"
    return [(balise, (re.search(r'href="([^"]+)"', attributs) or [None, None])[1], libelle.strip())
            for balise, attributs, libelle in re.findall(r"<(a|span)\b([^>]*)>(.*?)</\1>", nav.group(1), re.S)]


# --- l'en-tête ------------------------------------------------------------------------------------------------------------

def test_les_cinq_entetes_sont_identiques_hors_page_courante():
    """Une fois l'entrée courante remise sous forme de lien, les cinq en-têtes sont le même texte."""
    normalises = {}
    for fichier, _ecran, libelle in ECRANS:
        texte = entete(fichier)
        assert texte.count('aria-current="page"') == 1, f"{fichier} : une seule page courante"
        courante = f'<span aria-current="page">{libelle}</span>'
        assert courante in texte, f"{fichier} : la page courante doit être « {libelle} »"
        texte = texte.replace(courante, f'<a href="{fichier}">{libelle}</a>')
        normalises[fichier] = re.sub(r"\s+", " ", texte).strip()
    assert len(set(normalises.values())) == 1, normalises


@pytest.mark.parametrize("fichier, ecran, libelle", ECRANS)
def test_chaque_page_a_les_cinq_liens(fichier, ecran, libelle):
    attendu = [("span", None, lib) if fic == fichier else ("a", fic, lib) for fic, _e, lib in ECRANS]
    assert entrees_de_navigation(fichier) == attendu


@pytest.mark.parametrize("fichier", [e[0] for e in ECRANS])
def test_chaque_page_a_l_avertissement_amf(fichier):
    assert AVERTISSEMENT in entete(fichier)


@pytest.mark.parametrize("fichier", [e[0] for e in ECRANS])
def test_un_seul_titre_de_page_dans_main(fichier):
    """Le titre propre à la page vit dans `<main>` : l'en-tête commun n'en contient aucun."""
    page = html(fichier)
    assert page.count("<h1") == 1, f"{fichier} : un seul titre de niveau 1"
    assert "<h1" not in entete(fichier)
    assert "<h1" in re.search(r"<main\b.*?</main>", page, re.S).group(0)


# --- le style A -------------------------------------------------------------------------------------------------------------

def _luminance(couleur: str) -> float:
    rvb = [int(couleur[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rvb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contraste(a: str, b: str) -> float:
    clair, sombre = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (clair + 0.05) / (sombre + 0.05)


def _bloc_css(selecteur: str) -> dict[str, str]:
    css = (FRONTEND / "style.css").read_text(encoding="utf-8")
    trouve = re.search(re.escape(selecteur) + r"\s*\{([^}]*)\}", css)
    assert trouve, f"style.css : aucun bloc {selecteur}"
    return {nom: valeur.strip().lower() for nom, valeur in re.findall(r"(--[a-z-]+)\s*:\s*([^;]+);", trouve.group(1))}


def themes() -> dict[str, dict[str, str]]:
    """Les variables de chaque thème : `:root` porte le sombre (par défaut), `:root[data-theme="clair"]` le clair."""
    sombre = _bloc_css(":root")
    return {"sombre": sombre, "clair": {**sombre, **_bloc_css(':root[data-theme="clair"]')}}


def test_une_couleur_par_ecran_refait():
    css = (FRONTEND / "style.css").read_text(encoding="utf-8")
    for fichier, ecran, _libelle in ECRANS:
        assert f'<body data-ecran="{ecran}"' in html(fichier), f"{fichier} : body sans data-ecran"
        regle = re.search(r'body\[data-ecran="' + re.escape(ecran) + r'"\]\s*\{([^}]*)\}', css)
        assert regle, f"style.css : aucune règle pour l'écran {ecran}"
        palette = PALETTE[ecran]
        assert re.search(r"--couleur-ecran\s*:\s*var\(--couleur-" + palette + r"\)", regle.group(1)), ecran
        assert re.search(r"--teinte-ecran\s*:\s*var\(--teinte-" + palette + r"\)", regle.group(1)), ecran
    for theme, variables in themes().items():
        for palette, attendue in COULEURS[theme].items():
            assert variables[f"--couleur-{palette}"] == attendue, (theme, palette)


PAIRES = [("--texte", "--surface"), ("--texte", "--fond"), ("--texte", "--fond-alt"), ("--texte-doux", "--surface"),
          ("--texte-doux", "--fond"), ("--texte-doux", "--fond-alt"), ("--alerte", "--surface"), ("--alerte", "--fond-alt"),
          ("--frais-ok", "--surface"), ("--frais-attention", "--surface"), ("--texte", "--perimee"),
          ("--texte", "--perimee-survol"), ("--couleur-marque", "--surface"),
          # La carte des performances (tâche 8) : le chiffre reste lisible sur la teinte qui le répète.
          ("--texte", "--fond-hausse"), ("--texte", "--fond-baisse")]
# Le pied de page est posé sur le dégradé, sans carte : son texte doit tenir sur chacun des trois arrêts.
PAIRES += [(texte, f"--degrade-{arret}") for texte in ("--texte", "--texte-doux") for arret in ("debut", "milieu", "fin")]
PAIRES += [paire for p in ("portefeuille", "indicateurs", "briefing", "service")
           for paire in ((f"--couleur-{p}", "--surface"), (f"--couleur-{p}", "--fond"),
                         (f"--couleur-{p}", f"--teinte-{p}"), ("--texte-sur-couleur", f"--couleur-{p}"))]


@pytest.mark.parametrize("theme", ["sombre", "clair"])
def test_contrastes_des_deux_themes(theme):
    """Chaque texte et son fond, dans chaque thème : au moins 4,5:1 (WCAG 1.4.3). Calculé, jamais supposé."""
    variables = themes()[theme]
    faibles = {f"{texte} sur {fond}": round(contraste(variables[texte], variables[fond]), 2)
               for texte, fond in PAIRES if contraste(variables[texte], variables[fond]) < 4.5}
    assert faibles == {}


def test_style_focus_visible_et_mouvement_reduit():
    css = (FRONTEND / "style.css").read_text(encoding="utf-8")
    focus = re.search(r":focus-visible\s*\{([^}]*)\}", css).group(1)
    assert "var(--couleur-ecran)" in focus and "solid" in focus
    assert "@media (prefers-reduced-motion: reduce)" in css


# --- le thème : sombre par défaut, clair au choix --------------------------------------------------------------------------

@pytest.mark.parametrize("fichier", [e[0] for e in ECRANS])
def test_theme_sombre_par_defaut_et_bouton_cache_sans_javascript(fichier):
    """Sans JavaScript, la page s'affiche en sombre et le bouton, qui ne servirait à rien, reste caché. Le script du thème
    est lu dans `<head>`, avant l'affichage : la page ne clignote pas d'un thème à l'autre."""
    page = html(fichier)
    assert '<html lang="fr">' in page, "aucun thème écrit dans la page : le sombre est celui par défaut"
    tete = re.search(r"<head>.*?</head>", page, re.S).group(0)
    assert '<script src="theme.js"></script>' in tete
    bouton = re.search(r'<button\b[^>]*\bid="bascule-theme"[^>]*>', entete(fichier))
    assert bouton, f"{fichier} : pas de bouton de thème dans l'en-tête"
    assert 'type="button"' in bouton.group(0) and " hidden" in bouton.group(0)
    assert 'aria-pressed="false"' in bouton.group(0)


def test_le_theme_n_utilise_jamais_localstorage():
    """Le choix du thème vit dans l'onglet (`sessionStorage`), comme la clé : RITA n'écrit rien qui survive à l'onglet."""
    code = code_sans_commentaires("theme.js")
    assert "sessionStorage" in code and '"rita_theme"' in code
    assert "localStorage" not in code


# --- aucun chargement depuis un autre site -------------------------------------------------------------------------------

_TIERS = "(?:https?:)?//"
MOTIFS_HTML = [r"<script\b[^>]*\bsrc\s*=\s*[\"']?" + _TIERS, r"<link\b[^>]*\bhref\s*=\s*[\"']?" + _TIERS,
               r"<(?:img|source|video|audio|embed|track|input)\b[^>]*\b(?:src|srcset|data|poster)\s*=\s*[\"']?" + _TIERS,
               r"<object\b[^>]*\bdata\s*=\s*[\"']?" + _TIERS, r"<iframe\b", r"<frame\b",
               r"@import\b", r"url\(\s*[\"']?" + _TIERS]
MOTIFS_CSS = [r"@import\b", r"url\(\s*[\"']?" + _TIERS]
MOTIFS_JS = [r"[\"'`]" + _TIERS, r"\bimport\s*\(", r"\bimportScripts\s*\(", r"\bnew\s+WebSocket\s*\(",
             r"\bnavigator\.sendBeacon\s*\("]


def chargements_tiers(texte: str, motifs: list[str]) -> list[str]:
    return [m.group(0) for motif in motifs for m in re.finditer(motif, texte, re.I)]


@pytest.mark.parametrize("exemple, motifs", [
    ('<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>', MOTIFS_HTML),
    ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter">', MOTIFS_HTML),
    ('<img src="//exemple.test/logo.png" alt="">', MOTIFS_HTML),
    ('<iframe title="x" src="page.html"></iframe>', MOTIFS_HTML),
    ('body { background: url("https://exemple.test/fond.png"); }', MOTIFS_CSS),
    ('@import "theme.css";', MOTIFS_CSS),
    ('fetch("https://api.exemple.test/donnees")', MOTIFS_JS),
])
def test_le_detecteur_voit_un_chargement_tiers(exemple, motifs):
    """Le garde est lui-même testé : sans ces exemples, un détecteur qui ne voit rien passerait pour un frontend propre."""
    assert chargements_tiers(exemple, motifs)


def test_le_detecteur_laisse_passer_un_lien_vers_une_source():
    assert chargements_tiers('<a href="https://www.boursorama.com/article">Source</a>', MOTIFS_HTML) == []


def test_aucun_chargement_tiers():
    """Ni script, ni feuille de style, ni police, ni image, ni cadre, ni `@import`, ni `url()` d'un autre site ; les liens
    `<a href>` vers les sources restent permis (ils ne chargent rien tant qu'on ne clique pas)."""
    trouves = {}
    for chemin in sorted(FRONTEND.iterdir()):
        if chemin.suffix == ".html":
            trouves[chemin.name] = chargements_tiers(chemin.read_text(encoding="utf-8"), MOTIFS_HTML)
        elif chemin.suffix == ".css":
            trouves[chemin.name] = chargements_tiers(chemin.read_text(encoding="utf-8"), MOTIFS_CSS)
        elif chemin.suffix == ".js":
            trouves[chemin.name] = chargements_tiers(code_sans_commentaires(chemin.name), MOTIFS_JS)
    assert {nom: liste for nom, liste in trouves.items() if liste} == {}
    assert {"index.html", "style.css", "app.js"} <= set(trouves), "le garde doit avoir lu les fichiers"


def test_polices_modernes_sans_telechargement():
    """Demande d'Era du 04/11 : des polices modernes. Éco-conception (C17) : aucune police téléchargée. Donc des polices
    déjà installées : Segoe UI Variable (Windows 11), SF Pro (macOS) ; Cascadia Mono pour les chiffres (style B)."""
    css = (FRONTEND / "style.css").read_text(encoding="utf-8")
    variables = _bloc_css(":root")
    assert variables["--police-texte"].startswith('"segoe ui variable text"')
    assert variables["--police-titres"].startswith('"segoe ui variable display"')
    assert variables["--police-chiffres"].startswith('"cascadia mono"')
    for pile in ("--police-texte", "--police-titres", "--police-chiffres"):
        assert variables[pile].rstrip().endswith(("sans-serif", "monospace")), "une famille générique en dernier recours"
    assert "@font-face" not in css, "aucune police téléchargée"
    assert re.search(r"body\s*\{[^}]*font-family:\s*var\(--police-texte\)", css)


# --- le logo et le dégradé (demandes d'Era du 04/11 au soir) --------------------------------------------------------------

def test_logo_dans_l_en_tete_selon_le_theme():
    """La marque officielle de RITA, réduite à 64 px (environ 3 Ko) : carré blanc sur le thème sombre, carré bleu nuit
    sur le clair. Décorative à côté du mot « RITA » (aria-hidden) ; elle sert aussi d'icône d'onglet, ce qui supprime la
    demande de `favicon.ico` qui répondait 404 depuis le 03/10 (constat F3)."""
    for fichier, _ecran, _libelle in ECRANS:
        assert '<span class="logo" aria-hidden="true"></span> RITA' in entete(fichier), fichier
        tete = re.search(r"<head>.*?</head>", html(fichier), re.S).group(0)
        assert '<link rel="icon" type="image/png" href="logo-rita-clair.png">' in tete, fichier
    theme = themes()
    assert theme["sombre"]["--logo"] == 'url("logo-rita-sombre.png")'
    assert theme["clair"]["--logo"] == 'url("logo-rita-clair.png")'
    for nom in ("logo-rita-sombre.png", "logo-rita-clair.png"):
        assert (FRONTEND / nom).stat().st_size < 5000, f"{nom} : trop lourd pour un logo de 28 px"


def test_degrade_de_fond_sans_image():
    """Du bleu nuit au bleu, comme la couverture du livret E1, mais en CSS : aucune image téléchargée (éco-conception)."""
    css = (FRONTEND / "style.css").read_text(encoding="utf-8")
    for theme, variables in themes().items():
        assert "linear-gradient" in variables["--degrade"] and "url(" not in variables["--degrade"], theme
    assert re.search(r"html\s*\{[^}]*background-image:\s*var\(--degrade\)", css)
