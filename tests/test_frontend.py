"""Tests de l'interface — le premier écran, le portefeuille (C10, C17).

Trois choses sont vérifiées ici, et aucune n'est décorative :

1. **L'interface est servie sans casser l'API.** `app.mount("/")` capture toutes les
   adresses restantes : mal placé, il masquerait `/donnees` et `/briefing`. Le test
   de non-régression est la seule façon de s'en assurer durablement.
2. **Aucun secret dans le code du front.** La clé d'API est saisie par l'utilisateur,
   jamais écrite dans les sources — donc jamais dans Git. OWASP.
3. **Les marqueurs d'accessibilité sont présents.** Ils se suppriment par accident à
   la première refonte du CSS ; un test les rend impossibles à perdre en silence.

C17 exige *« des tests d'intégration ou unitaires couvrent au moins les composants
métier et la gestion des accès »*.
"""
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app

FRONTEND = Path(__file__).parent.parent / "frontend"


def code_sans_commentaires(nom: str) -> str:
    """Retourne le JavaScript débarrassé de ses commentaires.

    ⚠️ Écrit après un échec réel, le 16/08/2026. La première version cherchait
    `innerHTML` dans le fichier entier — et le trouvait dans le commentaire
    *« vide le tableau sans passer par innerHTML »*. Le test échouait sur la phrase
    qui explique la bonne pratique.

    Réécrire le commentaire aurait fait passer le test sans rien corriger : c'est le
    test qui cherchait au mauvais endroit. **Un test doit porter sur le code exécuté.**
    """
    source = (FRONTEND / nom).read_text(encoding="utf-8")
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)   # blocs /* … */
    source = re.sub(r"//.*", "", source)                          # lignes //
    return source


@pytest.fixture
def client():
    return TestClient(app)


# --- 1. L'interface est servie ------------------------------------------------

def test_la_racine_sert_la_page(client):
    reponse = client.get("/")
    assert reponse.status_code == 200
    assert "text/html" in reponse.headers["content-type"]
    assert "RITA — Mon portefeuille" in reponse.text


@pytest.mark.parametrize("fichier", ["style.css", "app.js"])
def test_les_ressources_statiques_sont_servies(client, fichier):
    assert client.get(f"/{fichier}").status_code == 200


# --- 2. NON-RÉGRESSION : le montage ne masque pas l'API -----------------------
# Sans ces deux tests, déplacer `app.mount` d'une ligne casserait toute l'API
# sans qu'aucun test ne le voie.

def test_le_montage_ne_masque_pas_l_api(client):
    """403 (et non 404) prouve que la route existe encore et reste protégée."""
    assert client.get("/donnees/portefeuille").status_code == 403


def test_le_montage_ne_masque_pas_la_documentation(client):
    assert client.get("/openapi.json").status_code == 200


# --- 3. Aucun secret dans le front -------------------------------------------

def test_aucune_cle_d_api_dans_le_code_du_front():
    """La clé est saisie par l'utilisateur, jamais écrite dans les sources.

    Le test cherche la valeur par défaut de `RITA_API_KEY` : si elle apparaît un jour
    dans le front, c'est qu'on l'y a codée en dur.
    """
    for fichier in ("app.js", "index.html"):
        contenu = (FRONTEND / fichier).read_text(encoding="utf-8")
        assert "dev-key" not in contenu, f"clé d'API codée en dur dans {fichier}"


def test_la_cle_n_est_pas_stockee_durablement():
    """`sessionStorage` s'efface à la fermeture de l'onglet, `localStorage` non."""
    code = code_sans_commentaires("app.js")
    assert "sessionStorage" in code
    assert "localStorage" not in code


def test_le_rendu_n_utilise_jamais_innerhtml():
    """OWASP A03 — injection. `textContent` insère du texte, `innerHTML` du code."""
    code = code_sans_commentaires("app.js")
    assert "innerHTML" not in code
    assert "textContent" in code


# --- 4. Les marqueurs d'accessibilité (RGAA) ---------------------------------

@pytest.mark.parametrize("marqueur, regle", [
    ('lang="fr"', "RGAA 8.3 — langue de la page"),
    ("<caption", "RGAA 5.4 — titre du tableau"),
    ('scope="col"', "RGAA 5.7 — en-têtes de colonnes"),
    ('aria-live="polite"', "RGAA 4.x — annonce des changements d'état"),
    ('role="status"', "zone de statut identifiée"),
])
def test_les_marqueurs_d_accessibilite_sont_presents(marqueur, regle):
    page = (FRONTEND / "index.html").read_text(encoding="utf-8")
    assert marqueur in page, f"marqueur absent : {regle}"


def test_le_signe_est_toujours_affiche_sur_les_performances():
    """RGAA 3.1 — l'information ne doit pas être portée par la seule couleur.

    `signDisplay: "always"` force le `+` sur les hausses : un daltonien lit
    « +33,30 % » aussi bien que n'importe qui.
    """
    code = (FRONTEND / "app.js").read_text(encoding="utf-8")
    assert 'signDisplay: "always"' in code


# --- 5. La contrainte AMF est visible à l'écran ------------------------------

def test_l_avertissement_amf_est_affiche(client):
    """La contrainte n'est pas seulement dans le prompt : l'utilisateur la lit."""
    page = client.get("/").text
    assert "Aucune recommandation d'achat ou de vente" in page


# --- Écran 2 : les indicateurs (lot 1) ----------------------------------------

@pytest.mark.parametrize("fichier", ["indicateurs.html", "indicateurs.js"])
def test_l_ecran_indicateurs_est_servi(client, fichier):
    assert client.get(f"/{fichier}").status_code == 200


def test_aucune_cle_d_api_dans_le_code_de_l_ecran_indicateurs():
    """Même exigence que pour le premier écran : la clé est saisie, jamais écrite."""
    code = code_sans_commentaires("indicateurs.js")
    assert "dev-key" not in code
    assert not re.search(r"X-API-Key\"\s*:\s*\"[^\"]+\"", code), \
        "une clé littérale est écrite dans l'en-tête"


def test_l_ecran_indicateurs_n_utilise_jamais_innerhtml():
    """Un nom d'instrument contenant du HTML serait exécuté — OWASP A03."""
    assert "innerHTML" not in code_sans_commentaires("indicateurs.js")


@pytest.mark.parametrize("marqueur, regle", [
    ('lang="fr"', "RGAA 8.3 — langue de la page"),
    ('scope="col"', "RGAA 5.7 — en-têtes de colonne"),
    ("<caption", "RGAA 5.4 — titre du tableau"),
    ('aria-live="polite"', "RGAA 12.x — annonce des changements de statut"),
    ('role="status"', "zone de statut identifiée"),
    ('aria-current="page"', "page courante signalée dans la navigation"),
    ('aria-controls="tableau-indicateurs"', "le filtre est relié au tableau qu'il modifie"),
])
def test_les_marqueurs_d_accessibilite_de_l_ecran_2(marqueur, regle):
    html = (FRONTEND / "indicateurs.html").read_text(encoding="utf-8")
    assert marqueur in html, f"marqueur absent — {regle}"


def test_les_en_tetes_de_ligne_sont_poses_par_le_rendu():
    """`scope="row"` ne peut PAS être dans le HTML : les lignes du tableau sont
    créées à l'exécution, une fois les données reçues. Le chercher dans la page
    aurait fait échouer le test sur un code pourtant correct — c'est ce qui est
    arrivé le 18/08. **Un test doit chercher là où la chose est réellement écrite.**"""
    assert 'setAttribute("scope", "row")' in code_sans_commentaires("indicateurs.js")


def test_la_zone_qui_defile_est_atteignable_au_clavier():
    """⚠️ Écrit après un défaut réel, le 18/08/2026.

    Le commentaire du CSS annonçait que `tabindex` et `role="region"` rendaient la
    zone défilable atteignable au clavier — **ils n'étaient nulle part dans le HTML**.
    Douze colonnes ne tenant pas à l'écran, une personne naviguant au clavier
    n'aurait jamais pu voir les colonnes de droite.

    Même famille de défaut que le garde-fou de sortie du 17/08 : **un contrôle
    documenté mais absent est pire qu'un contrôle absent** — tant qu'il est écrit,
    personne ne le cherche.
    """
    html = (FRONTEND / "indicateurs.html").read_text(encoding="utf-8")
    zone = re.search(r'<div class="tableau-large"[^>]*>', html)
    assert zone, "la zone de défilement a disparu"
    assert 'tabindex="0"' in zone.group(0)
    assert 'role="region"' in zone.group(0)
    assert "aria-label" in zone.group(0), "une région doit porter un nom accessible"


def test_le_signe_est_toujours_affiche_sur_les_indicateurs():
    """RGAA 3.1 : l'information n'est jamais portée par la seule couleur.
    Une performance négative doit se lire au signe, pas à la teinte."""
    assert 'signDisplay: "always"' in code_sans_commentaires("indicateurs.js")


def test_une_valeur_absente_devient_un_tiret_et_non_un_zero():
    """`null` signifie « pas calculable » ; `0` signifierait « aucune variation ».
    Afficher 0 à la place d'un tiret ferait lire une performance nulle inexistante."""
    code = code_sans_commentaires("indicateurs.js")
    assert 'return n === null ? "—"' in code or "n === null ? \"—\"" in code


def test_la_peremption_est_signalee_en_texte_pas_seulement_en_couleur():
    """La classe CSS `perimee` n'est qu'un renfort visuel. L'information doit
    exister dans le TEXTE de la cellule, sinon elle n'existe pas pour un lecteur
    d'écran ni pour une personne qui ne perçoit pas les couleurs."""
    code = code_sans_commentaires("indicateurs.js")
    assert "cotation périmée" in code, "la mention textuelle a disparu"


def test_les_deux_ecrans_se_relient(client):
    """Un écran isolé n'est pas une application. La navigation doit exister des
    deux côtés, sinon on entre dans l'écran 2 sans pouvoir en sortir."""
    for page, cible in [("index.html", "indicateurs.html"), ("indicateurs.html", "index.html")]:
        html = (FRONTEND / page).read_text(encoding="utf-8")
        assert f'href="{cible}"' in html, f"{page} ne renvoie pas vers {cible}"


# --- Écran 1 : le lot 2 des indicateurs (poids et exposition) ------------------

def test_la_colonne_poids_existe_dans_l_ecran_portefeuille():
    html = (FRONTEND / "index.html").read_text(encoding="utf-8")
    assert "<th scope=\"col\">Poids</th>" in html


def test_les_deux_points_de_terminaison_sont_appeles_en_parallele():
    """`Promise.all` et non deux `await` enchaînés : l'attente doit être celle du
    plus lent, pas la somme des deux. Enchaîner doublerait le temps perçu pour rien."""
    code = code_sans_commentaires("app.js")
    assert "Promise.all" in code
    assert "/donnees/indicateurs-portefeuille" in code


def test_le_poids_est_apparie_par_ticker_et_non_par_position():
    """⚠️ Vérifié dans le navigateur le 19/08 : les deux points de terminaison
    renvoient leurs lignes dans des ordres DIFFÉRENTS. Se fier à l'ordre serait un
    défaut invisible tant que les deux ordres coïncident par hasard."""
    code = code_sans_commentaires("app.js")
    assert "new Map(" in code
    assert "poidsParTicker.get(p.ticker)" in code


def test_une_panne_des_indicateurs_ne_fait_pas_tomber_le_portefeuille():
    """Les poids sont un COMPLÉMENT. Perdre la répartition ne doit pas priver
    l'utilisateur de ses positions et de leur valorisation — une dépendance
    secondaire qui fait tomber l'écran principal est une erreur de conception."""
    code = code_sans_commentaires("app.js")
    assert "reponseIndicateurs.ok" in code
    assert "? await reponseIndicateurs.json()" in code


def test_le_poids_s_affiche_sans_signe():
    """Un poids est toujours positif. « +34,83 % » suggérerait une variation,
    alors que c'est une part. Le format sans signe est donc distinct de celui
    des performances."""
    code = code_sans_commentaires("app.js")
    assert "pourcentSansSigne" in code


def test_la_distinction_cotation_vs_economique_est_affichee():
    """Sans cette mention, le chiffre d'exposition se lit de travers. Elle doit
    être dans la PAGE, pas seulement dans le code — un utilisateur ne lit pas le
    JavaScript."""
    html = (FRONTEND / "index.html").read_text(encoding="utf-8")
    assert "cotation" in html and "économique" in html


def test_aucun_seuil_de_concentration_n_est_affiche():
    """⚠️ Garde-fou AMF. Un poids de 34,83 % est un fait. « Concentration
    excessive », « à alléger » ou un code couleur d'alerte seraient des conseils."""
    html = (FRONTEND / "index.html").read_text(encoding="utf-8")
    code = code_sans_commentaires("app.js")
    for mot in ("excessive", "trop concentré", "alléger", "surpondér", "risqué"):
        assert mot not in html.lower(), f"conseil dans la page : {mot}"
        assert mot not in code.lower(), f"conseil dans le code : {mot}"


# --- Écran 2 : le lot 3 (volatilité, drawdown, RSI) ----------------------------

def test_les_3_colonnes_du_lot_3_existent():
    html = (FRONTEND / "indicateurs.html").read_text(encoding="utf-8")
    for colonne in ("Volatilité (1 an)", "Pire baisse (1 an)", "RSI 14"):
        assert f'<th scope="col">{colonne}</th>' in html


def test_les_deux_points_de_terminaison_du_lot_3_sont_appeles_en_parallele():
    code = code_sans_commentaires("indicateurs.js")
    assert "Promise.all" in code
    assert "/donnees/indicateurs-risque" in code


def test_le_lot_3_est_apparie_par_ticker():
    """Même défaut potentiel que sur l'écran portefeuille : les deux points de
    terminaison n'ont aucune raison de renvoyer leurs lignes dans le même
    ordre — vérifié dans le navigateur le 19/08 avec un ordre volontairement
    inversé."""
    code = code_sans_commentaires("indicateurs.js")
    assert "risqueParTicker" in code
    assert "new Map(" in code


def test_une_panne_du_lot_3_ne_fait_pas_tomber_le_lot_1():
    code = code_sans_commentaires("indicateurs.js")
    assert "reponseRisque.ok" in code
    assert "? await reponseRisque.json()" in code


def test_la_volatilite_s_affiche_sans_signe():
    """Une volatilité est une amplitude, toujours ≥ 0 — jamais « +22,14 % »,
    qui suggérerait une variation."""
    code = code_sans_commentaires("indicateurs.js")
    assert "formatPourcentSansSigne" in code


def test_le_rsi_n_est_pas_affiche_pour_une_valeur_perimee():
    """La règle est écrite dans la page, pas seulement dans le code : un
    utilisateur ne lit pas le JavaScript."""
    html = (FRONTEND / "indicateurs.html").read_text(encoding="utf-8")
    assert "RSI" in html and "n'est pas affiché" in html


def test_aucun_conseil_sur_le_rsi_dans_la_page_ou_le_code():
    """Garde-fou AMF : « RSI > 70 → vendre » est l'exemple même que la
    spécification donne d'un conseil interdit.

    ⚠️ **Deux versions précédentes cassées par le même piège**, chacune plus
    subtile que la précédente :
    - la 1ʳᵉ bannissait le mot « acheter » à l'état brut — trouvé dans la
      phrase qui EXPLIQUE l'interdit ;
    - la 2ᵉ bannissait « il faut acheter » — encore trouvé, en SOUS-CHAÎNE de
      « …qu'il faut acheter ou vendre », toujours la même phrase de négation.

    Une négation à l'infinitif contient forcément les mots qu'elle nie. Ce
    test cherche des formes IMPÉRATIVES (« achetez », « vendez »), qui
    n'apparaissent dans aucune tournure de négation en français correct —
    contrairement à l'infinitif, qui s'y niche naturellement."""
    html = (FRONTEND / "indicateurs.html").read_text(encoding="utf-8").lower()
    code = code_sans_commentaires("indicateurs.js").lower()
    formes_imperatives = (
        "achetez", "vendez", "achète maintenant", "vends maintenant",
        "signal d'achat", "signal de vente", "survendu", "suracheté",
    )
    for forme in formes_imperatives:
        assert forme not in html, f"conseil dans la page : {forme}"
        assert forme not in code, f"conseil dans le code : {forme}"

    # Contrôle inverse : le disclaimer qui NIE le conseil doit, lui, être présent.
    assert "n'indique jamais" in html
