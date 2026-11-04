"""Refonte 001, R2, critères 5 et 6 (04/11/2026 au soir) : chaque chiffre sous son titre, la volatilité nommée comme
elle est calculée, et une colonne sur deux teintée pour suivre les chiffres d'une ligne à l'autre (demande d'Era).

Pourquoi le premier test : une relecture a vu, sur un serveur local démarré avant la tâche 5 (donc sans
`Cache-Control: no-cache`), 11 titres et 15 cases par ligne : l'ancien script avec la nouvelle page, la moyenne mobile
20 séances sous « Volatilité ». Le code du dépôt fait 11 cases ; ce test l'impose titre par titre.
"""
from pathlib import Path

import pytest

from tests.test_entete_commun import contraste
from tests.test_indicateurs_ui import ecran, navigateur, ouvrir  # noqa: F401  (fixtures et ouverture de l'écran)
from tests.test_smoke_ui import serveur  # noqa: F401

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
VOLATILITE = "Volatilité annualisée (20 séances)"


def _titres_et_cases(page, ticker):
    return page.evaluate("""(t) => {
        const titres = [...document.querySelectorAll('#tableau-indicateurs thead th')].map(th => th.textContent.trim());
        const tr = document.querySelector(`#lignes tr[data-ticker="${t}"]`);
        return [titres, [...tr.children].map(c => c.textContent.trim())];
    }""", ticker)


def test_chaque_chiffre_est_sous_son_titre(ecran):  # noqa: F811
    titres, cases = _titres_et_cases(ecran, "MC.PA")
    assert len(cases) == len(titres) == 11
    ligne = dict(zip(titres, cases))
    assert ligne["Valeur"] == "MC.PA" and ligne["Nom"] == "LVMH MOET VUITTON"
    assert ligne["Cours"] == "401,50 EUR"
    assert ligne["1 jour"] == "▼ -0,25 %" and ligne["1 mois"] == "▼ -3,86 %" and ligne["1 an"] == "▲ +5,40 %"
    assert ligne[VOLATILITE] == "24,70 %"
    assert ligne["Pire baisse (1 an)"] == "-30,20 %"
    assert ligne["RSI 14"] == "44,1"


def test_la_volatilite_dit_sa_fenetre_de_20_seances(ecran):  # noqa: F811
    titres, _ = _titres_et_cases(ecran, "MC.PA")
    assert VOLATILITE in titres
    ecran.locator('#lignes tr[data-ticker="MC.PA"] button.choisir-valeur').click()
    ecran.wait_for_selector("#detail:not([hidden])")
    assert "volatilité annualisée (20 séances) : 24,70 %" in ecran.locator("#detail").inner_text()
    for fichier in ("indicateurs.html", "indicateurs.js"):
        assert "volatilité (1 an)" not in (FRONTEND / fichier).read_text(encoding="utf-8").lower(), fichier


def test_la_zone_de_recherche_liste_toutes_les_valeurs(navigateur, serveur):  # noqa: F811
    """R2, critère 7 : parcourir tous les codes en faisant défiler la liste de la zone de recherche. La liste vient des
    données (quatre valeurs ici, pas un nombre écrit dans le code), même celles qu'un filtre cache dans le tableau."""
    from tests.test_indicateurs_ui import INDICATEURS, valeur
    quatre = dict(INDICATEURS, nb=4, indicateurs=INDICATEURS["indicateurs"] + [valeur("AAPL", "APPLE", 2.0, devise="USD")])
    contexte, page = ouvrir(navigateur, serveur, indicateurs=quatre)
    champ = page.locator("#recherche")
    assert champ.get_attribute("list") == "valeurs-suivies", "la zone de recherche est reliée à sa liste"
    options = page.evaluate("[...document.querySelectorAll('#valeurs-suivies option')].map(o => [o.value, o.label])")
    assert options == [["MC.PA", "LVMH MOET VUITTON"], ["AI.PA", "AIR LIQUIDE"],
                       ["VK.PA", "VALLOUREC ANCIEN (cotation périmée)"], ["AAPL", "APPLE"]]
    page.locator("#masquer-perimees").check()
    assert page.locator("#lignes tr").count() == 3, "le filtre cache une ligne du tableau"
    assert page.locator("#valeurs-suivies option").count() == 4, "mais la liste garde toutes les valeurs"
    # Choisir un code dans la liste filtre le tableau comme une saisie.
    champ.fill("AAPL")
    assert page.locator("#lignes tr").count() == 1
    contexte.close()


def test_le_titre_long_de_la_volatilite_passe_sur_deux_lignes(ecran):  # noqa: F811
    """« Volatilité annualisée (20 séances) » est le titre exact, mais écrit sur une ligne il fait une colonne de 267 px
    (mesuré le 04/11) : le chiffre flotte loin de son titre. Le titre passe à la ligne, la colonne reste étroite."""
    largeur = ecran.evaluate("document.querySelectorAll('#tableau-indicateurs thead th')[8].getBoundingClientRect().width")
    assert largeur <= 200, f"colonne de la volatilité : {largeur:.0f} px"


def test_le_cours_et_les_capitaux_portent_leur_devise(navigateur, serveur):  # noqa: F811
    """Des marchés différents dans un même tableau : chaque montant dit sa devise, lue dans les données, jamais « EUR »
    partout."""
    from tests.test_indicateurs_ui import INDICATEURS, valeur
    avec_dollar = dict(INDICATEURS, nb=4, indicateurs=INDICATEURS["indicateurs"] + [
        valeur("AAPL", "APPLE", 2.0, devise="USD", cours=270.1)])
    contexte, page = ouvrir(navigateur, serveur, indicateurs=avec_dollar)
    assert dict(zip(*_titres_et_cases(page, "AAPL")))["Cours"] == "270,10 USD"
    assert dict(zip(*_titres_et_cases(page, "MC.PA")))["Cours"] == "401,50 EUR"
    page.locator('#lignes tr[data-ticker="AAPL"] button.choisir-valeur').click()
    page.wait_for_selector("#detail:not([hidden])")
    # Intl écrit « 250 M » avec une espace insécable (U+00A0) : on la lit comme une espace.
    assert "échangé par jour (20 séances) : 250 M USD" in page.locator("#detail").inner_text().replace("\xa0", " ")
    contexte.close()


def test_une_cotation_ancienne_n_est_pas_dite_radiee():
    """Une cotation ancienne peut venir d'une collecte interrompue, d'une suspension ou d'une radiation : l'écran ne
    choisit pas la cause."""
    html = (FRONTEND / "indicateurs.html").read_text(encoding="utf-8")
    assert "probablement" not in html
    assert "La dernière cotation disponible est ancienne" in html
    assert "collecte interrompue, suspension ou radiation" in html


def test_le_pied_de_page_dit_qui_calcule():
    """Le RSI est calculé en Python (`indicateurs/risque.py`), pas par la base : le pied de page ne dit plus « la base »."""
    html = (FRONTEND / "indicateurs.html").read_text(encoding="utf-8")
    assert "calculés par la base" not in html
    assert "indicateurs calculés par RITA à partir des cotations collectées" in html


# Le fond réel de chaque case : les couches de fond, du premier ancêtre opaque jusqu'à la case, teinte comprise.
FONDS = """() => {
    const lire = (s) => { const m = /rgba?\\(([^)]+)\\)/.exec(s || ''); if (!m) return null;
        const p = m[1].split(',').map(Number); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; };
    const poser = (dessous, c) => ({r: c.r * c.a + dessous.r * (1 - c.a), g: c.g * c.a + dessous.g * (1 - c.a),
                                    b: c.b * c.a + dessous.b * (1 - c.a), a: 1});
    const fond = (el) => {
        const chaine = [];
        for (let e = el; e; e = e.parentElement) {
            chaine.unshift(e);
            const c = lire(getComputedStyle(e).backgroundColor);
            if (c && c.a === 1) break;
        }
        let couleur = {r: 255, g: 255, b: 255, a: 1};
        for (const e of chaine) {
            const s = getComputedStyle(e);
            const c = lire(s.backgroundColor);
            if (c && c.a > 0) couleur = poser(couleur, c);
            const teinte = s.backgroundImage.startsWith('linear-gradient') ? lire(s.backgroundImage) : null;
            if (teinte && teinte.a > 0) couleur = poser(couleur, teinte);
        }
        return [couleur.r, couleur.g, couleur.b];
    };
    const rvb = (s) => { const c = lire(s); return [c.r, c.g, c.b]; };
    return [...document.querySelectorAll('#tableau-indicateurs tr')].map(tr => [...tr.children].map(c => ({
        fond: fond(c), texte: rvb(getComputedStyle(c).color), bouton: !!c.querySelector('button')})));
}"""


def _hex(rvb):
    return "#%02x%02x%02x" % tuple(round(c) for c in rvb)


@pytest.mark.parametrize("theme", ["sombre", "clair"])
def test_une_colonne_sur_deux_est_teintee_et_reste_lisible(navigateur, serveur, theme):  # noqa: F811
    contexte, page = ouvrir(navigateur, serveur)
    page.locator("#masquer-perimees").uncheck()   # la ligne périmée, au fond différent, est contrôlée aussi
    if theme == "clair":
        page.locator("#bascule-theme").click()
    lignes = page.evaluate(FONDS)
    assert len(lignes) == 4, "la ligne des titres et les trois valeurs"
    for ligne in lignes:
        fonds = [_hex(c["fond"]) for c in ligne]
        assert all(a != b for a, b in zip(fonds, fonds[1:])), f"{theme} : deux colonnes voisines du même fond {fonds}"
        for case in ligne:
            if case["bouton"]:
                continue   # le texte est celui du bouton, qui a son propre fond
            assert contraste(_hex(case["texte"]), _hex(case["fond"])) >= 4.5, (theme, case)
    contexte.close()


# --- relecture extérieure du 04/11 au soir (R2, critères 8 à 10) -----------------------------------------------------------

def _tickers(page):
    return page.evaluate("[...document.querySelectorAll('#lignes tr')].map(tr => tr.dataset.ticker)")


def test_apres_une_recherche_sans_resultat_le_detail_se_ferme_et_un_message_le_dit(navigateur, serveur):  # noqa: F811
    """Ouvrir LVMH, chercher « viridien » : zéro résultat, mais le détail de LVMH restait dessous et pouvait faire croire
    qu'il répondait à la nouvelle recherche."""
    contexte, page = ouvrir(navigateur, serveur)
    page.locator('#lignes tr[data-ticker="MC.PA"] button.choisir-valeur').click()
    page.wait_for_selector("#detail:not([hidden])")
    page.locator("#recherche").fill("viridien")
    assert _tickers(page) == []
    assert page.locator("#detail").is_hidden(), "le détail d'une valeur absente des résultats se ferme"
    assert "Aucune valeur trouvée pour cette recherche" in page.locator("#statut").inner_text()
    # Effacer la recherche rend le tableau et efface le message, sans rouvrir un détail que personne n'a demandé.
    page.locator("#recherche").fill("")
    assert _tickers(page) == ["MC.PA", "AI.PA"]
    assert page.locator("#detail").is_hidden()
    assert page.locator("#statut").inner_text() == ""
    contexte.close()


def test_le_detail_reste_tant_que_la_valeur_est_dans_les_resultats(navigateur, serveur):  # noqa: F811
    contexte, page = ouvrir(navigateur, serveur)
    page.locator('#lignes tr[data-ticker="MC.PA"] button.choisir-valeur').click()
    page.wait_for_selector("#detail:not([hidden])")
    page.locator("#recherche").fill("lvmh")
    assert _tickers(page) == ["MC.PA"] and page.locator("#detail").is_visible()
    contexte.close()


def test_une_valeur_existante_dont_la_cotation_perimee_est_masquee_est_dite(navigateur, serveur):  # noqa: F811
    """Chercher VK.PA (cotation périmée, masquée par défaut) : « aucune valeur » serait faux, elle existe."""
    contexte, page = ouvrir(navigateur, serveur)
    page.locator("#recherche").fill("VK.PA")
    assert _tickers(page) == []
    message = page.locator("#statut").inner_text()
    assert "Aucune valeur trouvée pour cette recherche" in message
    assert "1 correspond à une cotation périmée masquée" in message and "Masquer les cotations périmées" in message
    page.locator("#masquer-perimees").uncheck()
    assert _tickers(page) == ["VK.PA"] and page.locator("#statut").inner_text() == ""
    contexte.close()


def test_les_cotations_perimees_sont_masquees_par_defaut(ecran):  # noqa: F811
    assert ecran.locator("#masquer-perimees").is_checked()
    assert _tickers(ecran) == ["MC.PA", "AI.PA"]
    assert "1 cotation périmée masquée" in ecran.locator("#mention-perimees").inner_text()
    ecran.locator("#masquer-perimees").uncheck()
    assert _tickers(ecran) == ["MC.PA", "AI.PA", "VK.PA"]
    assert "1 cotation périmée dans l'univers suivi" in ecran.locator("#mention-perimees").inner_text()


def test_le_tableau_defile_dans_sa_zone_avec_ses_en_tetes_fixes(navigateur, serveur):  # noqa: F811
    """Cent onze lignes : la barre de défilement horizontale était tout en bas de la page, les trois dernières colonnes
    cachées à droite. Le tableau défile dans sa zone, qui tient dans la fenêtre, et ses titres restent visibles."""
    from tests.test_indicateurs_ui import INDICATEURS, valeur
    beaucoup = dict(INDICATEURS, nb=111, indicateurs=[valeur(f"T{i:03d}.PA", f"VALEUR {i:03d}", float(i % 7)) for i in range(111)])
    contexte, page = ouvrir(navigateur, serveur, indicateurs=beaucoup)
    mesure = page.evaluate("""() => {
        const zone = document.querySelector('.tableau-large');
        return {sticky: getComputedStyle(document.querySelector('#tableau-indicateurs thead th')).position,
                defile: zone.scrollHeight > zone.clientHeight, haut: zone.getBoundingClientRect().height,
                fenetre: window.innerHeight, largeur: zone.scrollWidth > zone.clientWidth};
    }""")
    assert mesure["sticky"] == "sticky", "les titres restent visibles pendant le défilement"
    assert mesure["defile"], "la zone défile : 111 lignes ne la rendent pas haute comme la page"
    assert mesure["haut"] <= mesure["fenetre"], f"la zone ({mesure['haut']:.0f} px) tient dans la fenêtre ({mesure['fenetre']} px)"
    contexte.close()


def test_l_aide_dit_ce_que_fait_l_ecran():
    """L'aide disait « RITA ne classe pas les valeurs et ne signale aucun seuil » alors que l'écran trie et dessine les
    repères 30 et 70 du RSI ; elle décrivait aussi la volatilité et la pire baisse comme un « détail »."""
    html = " ".join((FRONTEND / "indicateurs.html").read_text(encoding="utf-8").split())
    assert "ne classe pas les valeurs" not in html and "ne signale aucun seuil" not in html
    assert ("RITA permet de comparer les indicateurs. Le tri et les repères du RSI ne donnent pas de consigne d'achat ou de vente."
            in html)
    assert "Volatilité et pire baisse (détail)" not in html
    assert "<dt>Volatilité annualisée et pire baisse</dt>" in html


