"""Le guide d'exploitation se rend dans un PDF lisible (C8.5, 31/10/2026).

Pourquoi : le critère C8.5 demande une documentation « communiquée aux parties prenantes dans un format qui respecte les
recommandations d'accessibilité ». Le rendu des rapports met le texte courant à 10 pt, le code et les tableaux sous 9,5 pt,
et ne distingue les liens que par leur couleur ; le PDF n'a pas de signets. Les pratiques couramment citées demandent au
moins 12 pt pour un document texte, et les guides AcceDe des signets tirés des titres. L'option `--lisible` applique ces
règles sans changer la mise en page des rapports, dont le nombre de pages est limité.
"""
import re

from scripts import rendre_pdf


def _taille(css: str, selecteur: str) -> float:
    """Taille de police, en points, que la feuille de style donne au sélecteur (la dernière règle gagne)."""
    tailles = re.findall(rf"(?:^|\}}|\n)\s*{re.escape(selecteur)}\s*\{{[^}}]*?font-size:\s*([\d.]+)pt", css)
    assert tailles, f"aucune taille pour {selecteur}"
    return float(tailles[-1])


def test_chrome_produit_des_signets_tires_des_titres(tmp_path):
    commande = rendre_pdf.commande_chrome(tmp_path / "a.html", tmp_path / "a.pdf", tmp_path / "profil")
    assert "--generate-pdf-document-outline" in commande


def test_le_rendu_des_rapports_ne_change_pas_sans_l_option():
    assert rendre_pdf.feuille_de_style(lisible=False) == rendre_pdf.STYLE


def test_texte_courant_et_tableaux_au_moins_12_points_en_mode_lisible():
    css = rendre_pdf.feuille_de_style(lisible=True)
    assert _taille(css, "body") >= 12
    assert _taille(css, "table") >= 12


def test_code_au_moins_11_points_en_mode_lisible():
    css = rendre_pdf.feuille_de_style(lisible=True)
    assert _taille(css, "pre") >= 11
    assert _taille(css, "code") >= 11


def test_les_liens_sont_soulignes_pas_seulement_colores_en_mode_lisible():
    css = rendre_pdf.feuille_de_style(lisible=True)
    regles_a = re.findall(r"(?:^|\}|\n)\s*a\s*\{([^}]*)\}", css)
    assert "text-decoration:underline" in regles_a[-1].replace(" ", "")


def test_l_option_lisible_se_lit_sur_la_ligne_de_commande():
    assert rendre_pdf.lire_arguments(["rendre_pdf.py", "docs/exploitation.md", "--lisible"]) == ("docs/exploitation.md", True)
    assert rendre_pdf.lire_arguments(["rendre_pdf.py", "docs/rapports/E4/rapport-E4.md"]) == ("docs/rapports/E4/rapport-E4.md", False)
    assert rendre_pdf.lire_arguments(["rendre_pdf.py"]) is None


def test_un_lien_relatif_vers_un_fichier_du_depot_devient_du_texte():
    # Imprimé, un lien relatif devient une adresse de fichier du poste (`/C:/Users/...`) : morte pour le lecteur du PDF,
    # et elle expose un chemin local. Le texte du lien reste, le chemin aussi quand il en est le texte.
    texte = "le registre ([`../db/RGPD.md`](../db/RGPD.md), § 0) et [le seuil](../.coveragerc)"
    assert rendre_pdf.delier_les_liens_relatifs(texte) == "le registre (`../db/RGPD.md`, § 0) et le seuil"


def test_ancres_liens_web_et_images_restent_intacts():
    texte = "[annexes](#annexes) · [doc](https://www.postgresql.org/docs/) · ![schéma](schemas/a.png) · [m](mailto:x@y.z)"
    assert rendre_pdf.delier_les_liens_relatifs(texte) == texte
