"""Refonte 001, exigence R2, critère 11 (décision d'Era du 07/11/2026, éco-conception C17.7) : 20 valeurs à la fois.

L'écran Indicateurs était le seul en D (EcoIndex 52, 1 625 éléments de page : les 111 lignes du tableau, mesure du
06/11, `evidence/C17/mesures-2026-11-06/`). Le tableau montre 20 valeurs à la fois ; la recherche, le tri et la case des
cotations périmées portent sur toutes les valeurs avant le découpage. Tests écrits AVANT le code, dans un vrai
navigateur, API interceptée.
"""
from tests.test_indicateurs_ui import RISQUE, navigateur, ouvrir, valeur  # noqa: F401  (fixtures et ouverture)
from tests.test_smoke_ui import serveur  # noqa: F401


def _univers(n: int) -> dict:
    """`n` valeurs fictives : V01.PA à Vnn.PA, une performance à 1 mois égale à leur rang (V45 a la plus forte)."""
    lignes = [valeur(f"V{k:02d}.PA", f"VALEUR {k:02d}", float(k)) for k in range(1, n + 1)]
    return {"nb": n, "seuil_perime_jours": 40, "nb_perimees": 0, "indicateurs": lignes}


def _risque(n: int) -> dict:
    return {"nb": n, "indicateurs": [{"ticker": f"V{k:02d}.PA", "volatilite_annualisee_pct": 20.0,
                                      "drawdown_max_1a_pct": -10.0, "rsi_14": 50.0} for k in range(1, n + 1)]}


def _tickers(page) -> list[str]:
    return page.evaluate("[...document.querySelectorAll('#lignes tr')].map(tr => tr.dataset.ticker)")


def _ouvrir(navigateur, serveur, n):  # noqa: F811
    return ouvrir(navigateur, serveur, indicateurs=_univers(n), risque=(200, _risque(n)))


def test_le_tableau_montre_vingt_valeurs_a_la_fois(navigateur, serveur):  # noqa: F811
    contexte, page = _ouvrir(navigateur, serveur, 45)
    assert len(_tickers(page)) == 20
    assert _tickers(page)[0] == "V01.PA"
    assert page.locator("#position-pages").inner_text() == "Valeurs 1 à 20 sur 45"
    assert page.locator("#nb-valeurs").inner_text() == "45 valeurs"
    assert page.locator("#pages-precedentes").is_disabled()
    assert page.locator("#pages-suivantes").is_enabled()
    assert page.erreurs_js == []
    contexte.close()


def test_valeurs_suivantes_puis_precedentes(navigateur, serveur):  # noqa: F811
    contexte, page = _ouvrir(navigateur, serveur, 45)
    page.locator("#pages-suivantes").click()
    assert _tickers(page)[0] == "V21.PA" and len(_tickers(page)) == 20
    assert page.locator("#position-pages").inner_text() == "Valeurs 21 à 40 sur 45"
    page.locator("#pages-suivantes").click()
    assert _tickers(page) == [f"V{k}.PA" for k in range(41, 46)]
    assert page.locator("#position-pages").inner_text() == "Valeurs 41 à 45 sur 45"
    assert page.locator("#pages-suivantes").is_disabled()
    page.locator("#pages-precedentes").click()
    assert _tickers(page)[0] == "V21.PA"
    contexte.close()


def test_tri_et_recherche_portent_sur_toutes_les_valeurs_et_ramenent_a_la_premiere_page(navigateur, serveur):  # noqa: F811
    contexte, page = _ouvrir(navigateur, serveur, 45)
    page.locator("#pages-suivantes").click()
    page.select_option("#tri", "perf_1m_pct")
    assert _tickers(page)[0] == "V45.PA", "le tri range toutes les valeurs, pas seulement la page affichée"
    assert page.locator("#position-pages").inner_text() == "Valeurs 1 à 20 sur 45"
    page.fill("#recherche", "VALEUR 44")
    assert _tickers(page) == ["V44.PA"]
    assert page.locator("#nb-valeurs").inner_text() == "1 valeur"
    assert page.locator("#pagination").is_hidden()
    contexte.close()


def test_sous_vingt_et_une_valeurs_pas_de_boutons(navigateur, serveur):  # noqa: F811
    contexte, page = _ouvrir(navigateur, serveur, 20)
    assert len(_tickers(page)) == 20
    assert page.locator("#pagination").is_hidden()
    contexte.close()


def test_cent_onze_valeurs_jamais_plus_de_vingt_lignes(navigateur, serveur):  # noqa: F811
    """Le cas réel de l'univers suivi : 111 valeurs, 20 lignes dans la page."""
    contexte, page = _ouvrir(navigateur, serveur, 111)
    assert len(_tickers(page)) == 20
    assert page.locator("#position-pages").inner_text() == "Valeurs 1 à 20 sur 111"
    contexte.close()


def test_changer_de_page_ne_ferme_pas_le_detail(navigateur, serveur):  # noqa: F811
    contexte, page = _ouvrir(navigateur, serveur, 45)
    page.locator("#lignes tr[data-ticker='V02.PA'] button.choisir-valeur").click()
    page.wait_for_selector("#detail:not([hidden])")
    page.locator("#pages-suivantes").click()
    assert page.locator("#detail").is_visible(), "la valeur choisie reste dans les résultats : son détail reste ouvert"
    contexte.close()


def test_les_boutons_de_page_sont_des_boutons_qui_pilotent_le_tableau(navigateur, serveur):  # noqa: F811
    contexte, page = _ouvrir(navigateur, serveur, 45)
    for bouton in ("#pages-precedentes", "#pages-suivantes"):
        assert page.locator(bouton).evaluate("b => b.tagName === 'BUTTON' && b.type === 'button'")
        assert page.locator(bouton).get_attribute("aria-controls") == "tableau-indicateurs"
    assert page.locator("#position-pages").get_attribute("aria-live") == "polite"
    contexte.close()
