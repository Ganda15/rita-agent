"""Refonte 001, tâche 6 (R1, R2, R3) : `graphiques.js`, des fonctions pures qui dessinent en SVG.

Chaque fonction reçoit des données et rend `{svg, alternative}` : le dessin (ou `null` s'il n'y a rien à dessiner) et une
alternative en texte qui porte les mêmes chiffres (WCAG, images complexes). Aucun appel réseau, aucun HTML inséré.

Le seul calcul fait par l'écran (spécification § 5) : les séries des moyennes mobiles 20 et 50 séances, pour tracer
leurs courbes. Même règle que la base (`db/indicateurs.sql:95-107`) : la fenêtre inclut la séance du jour, et la moyenne
n'existe qu'avec exactement 20 (ou 50) séances. Le dernier point doit égaler `ma20` et `ma50` du serveur, arrondis à
4 décimales (`ROUND(f.ma20, 4)`, `db/indicateurs.sql:151`).
"""
import os
import random
import re
import statistics
from datetime import date, timedelta
from pathlib import Path

import pytest

from tests.test_frontend import code_sans_commentaires
from tests.test_smoke_ui import serveur  # noqa: F401  (fixture : l'API servie en local)

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
CLE_SERVEUR = "cle-de-test-smoke-ui-32-caracteres-x"   # tests/test_smoke_ui.py, fixture `serveur`


@pytest.fixture(scope="module")
def page(serveur):  # noqa: F811
    with sync_playwright() as p:
        canal = {} if os.environ.get("CI") else {"channel": "chrome"}
        nav = p.chromium.launch(headless=True, **canal)
        pg = nav.new_page()
        pg.goto(serveur + "/index.html")
        pg.add_script_tag(url=serveur + "/graphiques.js")
        yield pg
        nav.close()


def seances(clotures, debut=date(2026, 1, 5)):
    """Une séance par jour ouvré, rendue comme l'API : de la plus récente à la plus ancienne."""
    lignes, jour = [], debut
    for cloture in clotures:
        while jour.weekday() >= 5:
            jour += timedelta(days=1)
        lignes.append({"date_seance": jour.isoformat(), "cloture": cloture})
        jour += timedelta(days=1)
    return list(reversed(lignes))


def serie(n):
    return [round(100 + 10 * ((i * 37) % 17) / 17 + i * 0.05, 4) for i in range(n)]


def dessiner(page, fonction, donnees):
    """Appelle GRAPHIQUES.<fonction> et rend ce qu'un lecteur voit : le SVG en texte, l'alternative, les traces."""
    return page.evaluate("""([fonction, donnees]) => {
        const r = GRAPHIQUES[fonction](donnees);
        const svg = r.svg;
        return {
            svg: svg ? svg.outerHTML : null,
            alternative: r.alternative.textContent,
            series: svg ? [...svg.querySelectorAll('[data-serie]')].map(e => e.getAttribute('data-serie')) : [],
            points_cours: svg && svg.querySelector('polyline[data-serie="cours"]')
                ? svg.querySelector('polyline[data-serie="cours"]').getAttribute('points').trim().split(/\\s+/) : [],
            textes: svg ? [...svg.querySelectorAll('text')].map(t => t.textContent) : [],
            balises: svg ? [...svg.querySelectorAll('*')].map(e => e.tagName.toLowerCase()) : [],
        };
    }""", [fonction, donnees])


# --- la règle des moyennes, celle de la base ----------------------------------------------------------------------------

def test_moyenne_mobile_regle_de_la_base(page):
    valeurs = list(range(1, 26))
    resultat = page.evaluate("v => GRAPHIQUES.moyenneMobile(v, 20)", valeurs)
    assert resultat[:19] == [None] * 19, "moins de 20 séances : pas de moyenne"
    assert resultat[19] == 10.5 and resultat[24] == 15.5, "la fenêtre inclut la séance du jour"


def test_moyennes_egales_a_un_calcul_independant(page):
    tirage = random.Random(20261104)
    valeurs = [round(tirage.uniform(50, 500), 4) for _ in range(179)]
    for n in (20, 50):
        js = page.evaluate("([v, n]) => GRAPHIQUES.moyenneMobile(v, n)", [valeurs, n])
        attendu = [None if i < n - 1 else statistics.fmean(valeurs[i - n + 1:i + 1]) for i in range(len(valeurs))]
        assert [x is None for x in js] == [x is None for x in attendu]
        assert all(abs(a - b) < 1e-9 for a, b in zip(js, attendu) if a is not None)


# --- la courbe du cours -------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("n, series, message", [
    (0, [], "Aucun historique de cotation disponible"),
    (1, ["cours"], "moyennes indisponibles (moins de 20 séances)"),
    (19, ["cours"], "moyennes indisponibles (moins de 20 séances)"),
    (20, ["cours", "mm20"], "moyenne 50 indisponible (moins de 50 séances)"),
    (49, ["cours", "mm20"], "moyenne 50 indisponible (moins de 50 séances)"),
    (50, ["cours", "mm20", "mm50"], None),
    (179, ["cours", "mm20", "mm50"], None),
])
def test_courbe_selon_l_historique(page, n, series, message):
    """Les messages de la conception (§ 5) ; 130 séances affichées au plus, les moyennes calculées sur tout l'historique."""
    rendu = dessiner(page, "courbe", seances(serie(n)))
    assert rendu["series"] == series
    if message:
        assert message in rendu["alternative"]
    else:
        assert "indisponible" not in rendu["alternative"]
    if n == 0:
        assert rendu["svg"] is None
    if n >= 2:
        assert len(rendu["points_cours"]) == min(n, 130)


def test_courbe_trie_les_dates(page):
    """L'API rend la séance la plus récente d'abord : la courbe doit la remettre à droite."""
    croissante = [100 + i for i in range(31)]               # le cours monte avec le temps
    rendu = dessiner(page, "courbe", seances(croissante))   # rendu de la plus récente à la plus ancienne
    xs = [float(p.split(",")[0]) for p in rendu["points_cours"]]
    ys = [float(p.split(",")[1]) for p in rendu["points_cours"]]
    assert xs == sorted(xs) and len(set(xs)) == len(xs), "les dates vont de gauche à droite"
    assert ys[0] > ys[-1], "le cours le plus ancien (le plus bas) est à gauche, en bas"
    premiere, derniere = seances(croissante)[-1]["date_seance"], seances(croissante)[0]["date_seance"]
    jjmmaaaa = lambda iso: f"{iso[8:10]}/{iso[5:7]}/{iso[:4]}"
    assert f"Du {jjmmaaaa(premiere)} au {jjmmaaaa(derniere)}" in rendu["alternative"], "la période, dans l'ordre des dates"


def test_valeurs_manquantes(page):
    """Un cours absent ou illisible n'est jamais dessiné comme « NaN » : la séance est écartée et l'alternative le dit."""
    lignes = seances(serie(25))
    lignes[3]["cloture"] = None
    lignes[7]["cloture"] = "illisible"
    rendu = dessiner(page, "courbe", lignes)
    assert "NaN" not in rendu["svg"] and "Infinity" not in rendu["svg"]
    assert len(rendu["points_cours"]) == 23
    assert "2 séances écartées (cours absent ou illisible)" in rendu["alternative"]
    assert rendu["series"] == ["cours", "mm20"]


def test_courbe_accepte_les_decimaux_de_l_api(page):
    """Mesuré le 04/11 : `/donnees/cotations` rend `cloture` en texte ("401.5000", le NUMERIC de PostgreSQL). La courbe
    doit le lire comme un nombre ; un texte qui n'est pas un décimal reste écarté."""
    lignes = seances([f"{v:.4f}" for v in serie(60)])
    rendu = dessiner(page, "courbe", lignes)
    assert rendu["series"] == ["cours", "mm20", "mm50"] and len(rendu["points_cours"]) == 60
    assert "écartée" not in rendu["alternative"]
    assert page.evaluate("[GRAPHIQUES.lireNombre('401.5000'), GRAPHIQUES.lireNombre('4e2'), GRAPHIQUES.lireNombre(' 12 ')]") ==         [401.5, None, None]


def test_cours_constants(page):
    rendu = dessiner(page, "courbe", seances([50.0] * 30))
    assert "NaN" not in rendu["svg"] and "Infinity" not in rendu["svg"]
    ys = {p.split(",")[1] for p in rendu["points_cours"]}
    assert len(ys) == 1, "un cours constant est une ligne plate"


# --- l'anneau, les barres, la jauge -------------------------------------------------------------------------------------------

def test_anneau_non_dessine_si_poids_nuls(page):
    rendu = dessiner(page, "anneau", [{"nom": "A", "poids_pct": None}, {"nom": "B", "poids_pct": 0}])
    assert rendu["svg"] is None
    assert "Répartition non calculable" in rendu["alternative"]


def test_anneau_une_part_par_ligne(page):
    rendu = dessiner(page, "anneau", [{"nom": "LVMH", "poids_pct": 60}, {"nom": "TotalEnergies", "poids_pct": 40}])
    assert rendu["series"] == ["part", "part"]
    assert "LVMH : 60,0 %" in rendu["alternative"] and "TotalEnergies : 40,0 %" in rendu["alternative"]


def test_barres_signees_et_non_disponibles(page):
    rendu = dessiner(page, "barres", [{"nom": "A", "performance_pct": 12.5}, {"nom": "B", "performance_pct": -3.2},
                                      {"nom": "C", "performance_pct": None}])
    assert rendu["series"] == ["hausse", "baisse"], "pas de barre pour une performance absente"
    for attendu in ("A : ▲ +12,50 %", "B : ▼ -3,20 %", "C : non disponible"):
        assert attendu in rendu["alternative"], attendu


def test_barres_une_valeur_extreme_garde_l_echelle_commune_un_zero_visible_et_tous_ses_chiffres(page):
    """Viridien à +4 856,76 % écrasait les autres barres (04/11/2026). Le dessin ne triche pas : une échelle commune, la
    valeur extrême n'est ni plafonnée ni cachée, le zéro a son axe, et chaque ligne garde son pourcentage exact écrit.
    Rendre le graphique plus lisible se fait en corrigeant la donnée ou par un zoom annoncé, jamais en plafonnant en
    silence."""
    rendu = dessiner(page, "barres", [{"nom": "A", "performance_pct": 4856.76}, {"nom": "B", "performance_pct": 53.3},
                                      {"nom": "C", "performance_pct": 0}, {"nom": "D", "performance_pct": -36.51}])
    assert rendu["series"] == ["hausse", "hausse", "nulle", "baisse"]
    texte = rendu["alternative"].replace(" ", " ").replace(" ", " ")
    for attendu in ("A : ▲ +4 856,76 %", "B : ▲ +53,30 %", "C : 0,00 %", "D : ▼ -36,51 %"):
        assert attendu in texte, attendu
    dessin = page.evaluate("""(donnees) => {
        const svg = GRAPHIQUES.barres(donnees).svg;
        return {largeurs: [...svg.querySelectorAll('rect')].map(r => Number(r.getAttribute('width'))),
                axe: svg.querySelectorAll('line.axe').length};
    }""", [{"nom": "A", "performance_pct": 4856.76}, {"nom": "B", "performance_pct": 53.3},
           {"nom": "C", "performance_pct": 0}, {"nom": "D", "performance_pct": -36.51}])
    a, b, c, d = dessin["largeurs"]
    assert dessin["axe"] == 1, "le zéro a son axe"
    assert a == 160, "la valeur extrême prend toute la demi-zone : ni plafonnée ni réduite"
    assert abs(b / a - 53.3 / 4856.76) < 0.001 and abs(d / a - 36.51 / 4856.76) < 0.001, "échelle commune, proportions exactes"
    assert c == 1, "une valeur nulle garde un trait d'un pixel, jamais une barre vide qui disparaît"


@pytest.mark.parametrize("rsi, texte, dessinee", [
    (41.2, "RSI 14 : 41,2. Repères : 30 et 70.", True),
    (None, "RSI 14 : non disponible", False),
    (150, "RSI 14 : non disponible", False),
])
def test_jauge_du_rsi(page, rsi, texte, dessinee):
    """Le RSI est un fait, jamais un signal (contrainte AMF) : la jauge est neutre, la phrase est celle de la conception."""
    rendu = dessiner(page, "jauge", rsi)
    assert rendu["alternative"] == texte
    assert (rendu["svg"] is not None) is dessinee


# --- l'alternative, la sécurité ---------------------------------------------------------------------------------------------

def _nombres(texte):
    """Les nombres écrits : chiffres, groupes de milliers (espace fine insécable, comme fr-FR), décimales. Jamais l'espace
    ordinaire qui suit un nombre : « 2026 » dans le dessin et « 2026 : » dans le texte sont le même nombre."""
    return set(re.findall(r"-?\d+(?:[\u202f\u00a0]\d{3})*(?:,\d+)?", texte))


@pytest.mark.parametrize("fonction, donnees", [
    ("courbe", seances(serie(179))),
    ("anneau", [{"nom": "LVMH", "poids_pct": 62.5}, {"nom": "Air Liquide", "poids_pct": 37.5}]),
    ("barres", [{"nom": "LVMH", "performance_pct": 4.21}, {"nom": "Kering", "performance_pct": -12.08}]),
    ("jauge", 63.4),
])
def test_alternative_contient_les_memes_chiffres(page, fonction, donnees):
    """Chaque nombre écrit dans le dessin se retrouve dans l'alternative : personne n'est privé d'un chiffre."""
    rendu = dessiner(page, fonction, donnees)
    manquants = {n for t in rendu["textes"] for n in _nombres(t)} - _nombres(rendu["alternative"])
    assert manquants == set(), manquants


def test_aucun_texte_insere_comme_html(page):
    piege = '<img src=x onerror="window.piege=1">'
    for fonction, donnees in (("anneau", [{"nom": piege, "poids_pct": 100}]),
                              ("barres", [{"nom": piege, "performance_pct": 1.5}])):
        rendu = dessiner(page, fonction, donnees)
        assert "img" not in rendu["balises"], fonction
        assert piege in rendu["alternative"], "le nom reste un texte, lisible tel quel"
    assert page.evaluate("window.piege") is None
    code = code_sans_commentaires("graphiques.js")
    for interdit in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "fetch(", "XMLHttpRequest"):
        assert interdit not in code, interdit
    assert "createElementNS" in code


# --- contre le serveur, sur les vraies données ------------------------------------------------------------------------------

def test_dernier_point_egal_a_la_valeur_du_serveur(page, serveur):  # noqa: F811
    """Mêmes cotations, même date que `/donnees/indicateurs` : le dernier point de chaque moyenne égale `ma20` et `ma50`
    du serveur, à l'arrondi de l'API près (4 décimales). Sans base joignable (la CI), le test est sauté, et le dit."""
    lu = page.evaluate("""async (cle) => {
        const lire = (u) => fetch(u, {headers: {'X-API-Key': cle}}).then(async r => ({statut: r.status, corps: r.ok ? await r.json() : null}));
        return {cotations: await lire('/donnees/cotations?ticker=MC.PA&limite=179'),
                indicateurs: await lire('/donnees/indicateurs?ticker=MC.PA')};
    }""", CLE_SERVEUR)
    if lu["cotations"]["statut"] != 200 or lu["indicateurs"]["statut"] != 200:
        pytest.skip(f"base locale absente : cotations {lu['cotations']['statut']}, indicateurs {lu['indicateurs']['statut']}")
    cotations = lu["cotations"]["corps"]["cotations"]
    serveur_mc = lu["indicateurs"]["corps"]["indicateurs"][0]
    assert serveur_mc["date_cours"] == cotations[0]["date_seance"], "la même dernière séance des deux côtés"
    clotures = [c["cloture"] for c in sorted(cotations, key=lambda c: c["date_seance"])]
    for n, champ in ((20, "ma20"), (50, "ma50")):
        dernier = page.evaluate("([v, n]) => GRAPHIQUES.moyenneMobile(v.map(GRAPHIQUES.lireNombre), n).at(-1)", [clotures, n])
        assert abs(dernier - serveur_mc[champ]) <= 0.00005, (champ, dernier, serveur_mc[champ])
