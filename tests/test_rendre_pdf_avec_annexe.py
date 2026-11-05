"""Le rapport et son annexe se rendent dans un seul document Chrome (05/11/2026).

Pourquoi : jusqu'au 05/11, le PDF « avec annexe » d'E1, E2 et E4 était fusionné après coup (pypdf). La fusion garde
les pages, les liens et les signets, mais perd la langue déclarée et l'arbre de structure que Chrome écrit dans chaque
PDF : un lecteur d'écran ne sait plus ce qui est un titre ou un tableau. Mesure du 05/11 sur les fichiers remis : les
rapports seuls sont balisés et en français, les trois PDF fusionnés ne le sont pas. Rendus ensemble, rapport et annexe
gardent ce balisage. L'annexe est en paysage : sa règle `@page` devient une page nommée, et ses autres règles ne valent
que dans sa section (imbrication CSS), pour que `h2{ break-before:page }` n'ouvre pas une page à chaque titre du rapport.
"""
import pytest

from scripts import rendre_pdf

STYLE_ANNEXE = """
@page{ size:A4 landscape; margin:12mm;
  @bottom-right{ content:"Annexe · " counter(page) " / " counter(pages); } }
h2{ break-before:page; }
#a1{ break-before:auto; }
"""


def _bloc(css: str, debut: str) -> str:
    """Le bloc entre accolades qui suit `debut`, accolades imbriquées comprises."""
    i = css.index(debut) + len(debut) - 1
    assert css[i] == "{"
    profondeur = 0
    for j in range(i, len(css)):
        profondeur += {"{": 1, "}": -1}.get(css[j], 0)
        if profondeur == 0:
            return css[i:j + 1]
    raise AssertionError("bloc non fermé")


def test_la_page_de_l_annexe_devient_une_page_nommee_en_paysage():
    css = rendre_pdf.feuille_annexe(STYLE_ANNEXE)
    page = _bloc(css, "@page annexe{")
    assert "size:A4 landscape" in page
    assert '"Annexe · " counter(page) " / " counter(pages)' in page, "le pied de l'annexe est gardé"
    assert "@page{" not in css, "aucune règle de page ne doit rester sans nom : elle toucherait le rapport"


def test_les_regles_de_l_annexe_ne_valent_que_dans_sa_section():
    css = rendre_pdf.feuille_annexe(STYLE_ANNEXE)
    section = _bloc(css, ".annexe{")
    assert "page:annexe" in section
    assert "h2{ break-before:page; }" in section and "#a1{ break-before:auto; }" in section
    hors_section = css.replace(section, "").replace(_bloc(css, "@page annexe{"), "")
    assert "h2" not in hors_section, "une règle de l'annexe s'appliquerait aux titres du rapport"


def test_une_regle_de_page_deja_nommee_est_refusee():
    # Une page nommée ou `:first` ne se renomme pas sans risque : mieux vaut s'arrêter que rendre une mise en page fausse.
    with pytest.raises(ValueError, match="@page"):
        rendre_pdf.feuille_annexe("@page :first{ margin:0; }")


def test_le_document_complet_a_une_seule_racine_en_francais_et_l_annexe_apres_le_rapport():
    html = rendre_pdf.document_avec_annexe("Rapport E2", "body{}", '<h2 id="c6">C6</h2>', STYLE_ANNEXE, '<h2 id="a1">A1</h2>')
    assert html.count('<html lang="fr">') == 1 and html.count("<body>") == 1
    assert html.index('id="c6"') < html.index('<section class="annexe">') < html.index('id="a1"')
    assert "<title>Rapport E2</title>" in html
    assert "@page annexe{" in html


def test_un_identifiant_present_dans_le_rapport_et_dans_l_annexe_est_refuse():
    # Deux titres de même identifiant : un lien du sommaire mènerait au mauvais endroit, sans que rien ne le signale.
    with pytest.raises(ValueError, match="a1"):
        rendre_pdf.document_avec_annexe("R", "", '<h2 id="a1">x</h2>', "", '<h2 id="a1">y</h2>')


def test_l_option_annexe_se_lit_sur_la_ligne_de_commande():
    argv = ["rendre_pdf.py", "docs/rapports/E2/rapport-E2.md", "--annexe", "docs/rapports/E2/annexe-schemas-E2.md"]
    assert rendre_pdf.lire_annexe(argv) == "docs/rapports/E2/annexe-schemas-E2.md"
    assert rendre_pdf.lire_arguments(argv) == ("docs/rapports/E2/rapport-E2.md", False)
    assert rendre_pdf.lire_annexe(["rendre_pdf.py", "docs/rapports/E2/rapport-E2.md"]) is None
    assert rendre_pdf.lire_arguments(["rendre_pdf.py", "r.md", "--annexe"]) is None, "--annexe sans fichier"
