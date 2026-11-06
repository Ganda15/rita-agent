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
    assert "RITA : Mon portefeuille" in reponse.text   # refonte 001 : titre sans tiret long


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
    ('aria-live="polite"', "RGAA 7.5 — messages de statut annoncés"),
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
    ('aria-live="polite"', "RGAA 7.5 — messages de statut annoncés"),
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
    # Refonte 001 (tâche 8) : le signe est écrit avec la flèche (« ▲ + », « ▼ - ») ; le rendu est vérifié dans un vrai
    # navigateur (tests/test_indicateurs_ui.py::test_carte_des_performances_lisible_sans_couleur).
    code = code_sans_commentaires("indicateurs.js")
    assert '"▲ +"' in code and '"▼ -"' in code


def test_une_valeur_absente_devient_un_tiret_et_non_un_zero():
    """`null` signifie « pas calculable » ; `0` signifierait « aucune variation ».
    Afficher 0 à la place d'un tiret ferait lire une performance nulle inexistante."""
    code = code_sans_commentaires("indicateurs.js")
    # Refonte 001 (tâche 8) : le tiret est « – » (tiret simple ; le tiret long est banni des textes du projet).
    assert 'n === null ? "–"' in code


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
    # 04/11/2026 : « annualisée (20 séances) », la fenêtre réelle de db/indicateurs_risque.sql, et non plus « (1 an) ».
    for colonne in ("Volatilité annualisée (20 séances)", "Pire baisse (1 an)", "RSI 14"):
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
    assert "function pourcentSansSigne" in code   # refonte 001 (tâche 8) : renommée, même règle


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


# --- Le bandeau de fraîcheur des données (C20) -------------------------------

def test_le_bandeau_de_fraicheur_existe_dans_la_page():
    """Le bandeau doit être dans le HTML, pas seulement dans le JavaScript :
    un utilisateur ne lit pas le code, et un évaluateur regarde l'écran."""
    html = (FRONTEND / "index.html").read_text(encoding="utf-8")
    assert 'id="fraicheur"' in html


def test_le_point_de_terminaison_de_fraicheur_est_appele():
    code = code_sans_commentaires("app.js")
    assert "/donnees/fraicheur" in code


def test_les_trois_appels_partent_en_parallele():
    """Trois appels enchaînés tripleraient le temps perçu. Promise.all les
    lance ensemble : l'attente est celle du plus lent."""
    code = code_sans_commentaires("app.js")
    assert "reponseFraicheur" in code
    assert "Promise.all" in code


def test_une_panne_de_la_fraicheur_ne_fait_pas_tomber_le_portefeuille():
    """Une jauge de santé qui casse l'écran qu'elle surveille serait un comble.
    Même principe que pour les indicateurs, et il compte double ici."""
    code = code_sans_commentaires("app.js")
    assert "reponseFraicheur.ok" in code
    assert "? await reponseFraicheur.json()" in code


def test_le_statut_n_est_pas_porte_par_la_seule_couleur():
    """RGAA 3.1 / WCAG 1.4.1. La pastille est décorative (aria-hidden) et c'est
    le TEXTE du message qui porte l'information. Une personne daltonienne, ou un
    navigateur sans CSS, doit lire exactement la même chose."""
    code = code_sans_commentaires("app.js")
    assert 'setAttribute("aria-hidden", "true")' in code
    assert "createTextNode(fraicheur.message)" in code


def test_le_statut_venu_de_l_api_est_filtre_par_liste_blanche():
    """`statut` vient du réseau : on ne le concatène pas tel quel dans un nom de
    classe sans le vérifier."""
    code = code_sans_commentaires("app.js")
    assert "STATUTS_FRAICHEUR" in code
    assert "STATUTS_FRAICHEUR.includes(fraicheur.statut)" in code


def test_le_bandeau_n_utilise_pas_innerHTML():
    """Le front entier s'interdit innerHTML — mesure prise contre A03 (injection)
    de l'OWASP Top 10. Le bandeau ne fait pas exception."""
    code = code_sans_commentaires("app.js")
    assert "innerHTML" not in code


# --- plan 65 (cas D06, 03/10/2026) : « indisponible », jamais 0,00 EUR ---------------------------

def test_un_montant_sans_taux_s_affiche_indisponible_jamais_zero():
    """`euro.format(null)` écrit « 0,00 € » : un montant inconnu passerait pour un montant nul.
    Le code doit traiter `taux_manquant` et écrire « indisponible »."""
    code = code_sans_commentaires("app.js")
    assert "taux_manquant" in code
    assert "indisponible" in code


def test_le_total_dit_combien_de_positions_sont_sans_taux():
    code = code_sans_commentaires("app.js")
    assert "positions_sans_taux" in code


# --- Écran 3 : le briefing (C10, 03/10/2026) -------------------------------------------------------
#
# Jusqu'ici l'interface servait les deux écrans de données ; `/briefing`, le seul point de terminaison
# qui expose le modèle, ne se demandait que par curl, la passerelle MCP ou la documentation interactive.
# Le rapport E3 le déclarait comme premier manque de C10. Même dispositif que les deux autres écrans :
# clé en sessionStorage, 4 états, textContent seulement, aucune information portée par la seule couleur.

BRIEFING_HTML = (FRONTEND / "briefing.html").read_text(encoding="utf-8")
BRIEFING_JS = (FRONTEND / "briefing.js").read_text(encoding="utf-8")


@pytest.mark.parametrize("fichier", ["briefing.html", "briefing.js"])
def test_l_ecran_briefing_est_servi(client, fichier):
    assert client.get(f"/{fichier}").status_code == 200


def test_les_trois_ecrans_se_relient(client):
    for page in ("index.html", "indicateurs.html", "briefing.html"):
        html = client.get(f"/{page}").text
        for cible in ("index.html", "indicateurs.html", "briefing.html"):
            if cible != page:
                assert f'href="{cible}"' in html, f"{page} ne mène pas à {cible}"
        assert 'aria-current="page"' in html


def test_l_ecran_briefing_appelle_le_point_de_terminaison_du_modele_en_post_avec_la_cle():
    # Refonte 001 (tâche 7) : l'appel passe par RITA.appeler (commun.js, tâche 5), qui pose l'en-tête de la clé.
    assert '"/briefing"' in BRIEFING_JS
    assert "RITA.appeler" in BRIEFING_JS and 'methode: "POST"' in BRIEFING_JS
    assert '"X-API-Key"' in code_sans_commentaires("commun.js")


def test_aucune_cle_d_api_dans_le_code_de_l_ecran_briefing():
    code = code_sans_commentaires("briefing.js") + BRIEFING_HTML
    assert "RITA_API_KEY" not in code
    assert not re.search(r"['\"][A-Za-z0-9_-]{32,}['\"]", code), "une clé en dur ?"


def test_l_ecran_briefing_n_utilise_jamais_innerhtml():
    assert "innerHTML" not in code_sans_commentaires("briefing.js")


@pytest.mark.parametrize("marqueur, regle", [
    ('<label for="cle">', "RGAA 11.1 : le champ de clé a une étiquette"),
    ('<label for="ticker">', "RGAA 11.1 : le champ de ticker a une étiquette"),
    ('aria-live="polite"', "RGAA 7.5 : le statut est annoncé aux lecteurs d'écran"),
    ('<nav aria-label=', "RGAA 12.6 : la navigation est une zone nommée"),
    ('aria-current="page"', "bonne pratique : la page courante est marquée"),
])
def test_les_marqueurs_d_accessibilite_de_l_ecran_3(marqueur, regle):
    assert marqueur in BRIEFING_HTML, regle


def test_l_avertissement_amf_est_sur_l_ecran_briefing():
    assert "Aucune recommandation d'achat ou de vente" in BRIEFING_HTML


def test_le_verdict_du_garde_fou_est_dit_en_texte_pas_seulement_en_couleur():
    code = code_sans_commentaires("briefing.js")
    assert "conforme_amf" in code
    assert "retenu par le garde-fou" in code, "un texte refusé est dit avec des mots"
    assert "motifs_amf" in code, "les motifs du refus sont montrés"


def test_un_ticker_inconnu_est_dit_en_clair_et_une_cle_refusee_est_oubliee():
    code = code_sans_commentaires("briefing.js")
    assert "502" in code and "introuvable" in code
    # Refonte 001 (tâche 7) : sur 401 ou 403, RITA.appeler oublie la clé (commun.js) ; l'écran la redemande.
    assert "403" in code and "demanderCle" in code
    commun = code_sans_commentaires("commun.js")
    assert "reponse.status === 403" in commun and "oublierCle()" in commun
    # Le 502 ne veut plus dire « aucun fournisseur » : c'est le 503 (tâche 3).
    assert "503" in code and "Aucun fournisseur de modèle n'a répondu" in code


def test_le_texte_du_modele_est_rendu_en_paragraphes_sans_html():
    code = code_sans_commentaires("briefing.js")
    assert 'createElement("p")' in code and "textContent" in code


def test_l_ecran_briefing_dit_que_la_redaction_prend_du_temps():
    code = code_sans_commentaires("briefing.js")
    assert "secondes" in code, "un appel au modèle dure 5 à 15 s : le dire, sinon l'écran paraît figé"


def test_l_identifiant_de_requete_est_montre_pour_le_support():
    assert "X-Request-ID" in code_sans_commentaires("briefing.js")


# --- Écran 4 : la question libre (sprint 3, tâche A6 ; spec CA1.1, CA1.2, CA1.5, CA2.1, CA2.4) ---------------------
#
# Même dispositif que l'écran du briefing : clé en sessionStorage, oubliée sur un 403, rendu par textContent seulement.
# Le texte d'une réponse vient d'un modèle ; les titres, sources et liens viennent de flux RSS. Tout est une donnée,
# jamais du code. Les fichiers sont lus dans chaque test, pas au chargement du module : tant que l'écran n'existe pas,
# seuls ces tests échouent, et les autres tests de ce fichier continuent de tourner.

def _question_html() -> str:
    return (FRONTEND / "question.html").read_text(encoding="utf-8")


@pytest.mark.parametrize("fichier", ["question.html", "question.js"])
def test_l_ecran_question_est_servi(client, fichier):
    assert client.get(f"/{fichier}").status_code == 200


def test_l_ecran_question_est_relie_au_portefeuille():
    assert 'href="question.html"' in (FRONTEND / "index.html").read_text(encoding="utf-8")
    html = _question_html()
    assert 'href="index.html"' in html
    assert 'aria-current="page"' in html


def test_l_ecran_question_appelle_la_route_en_post_avec_la_cle():
    code = code_sans_commentaires("question.js")
    assert '"/question"' in code
    assert 'method: "POST"' in code
    assert '"X-API-Key"' in code


def test_l_ecran_question_appelle_la_fiche_avec_la_cle():
    # CA1.5 : la fiche s'ouvre depuis l'écran, sans autre outil. Elle est protégée par la clé comme le reste.
    code = code_sans_commentaires("question.js")
    assert '"/donnees/articles/"' in code
    assert '"X-API-Key"' in code


def test_aucune_cle_d_api_dans_le_code_de_l_ecran_question():
    code = code_sans_commentaires("question.js") + _question_html()
    assert "RITA_API_KEY" not in code and "dev-key" not in code
    assert not re.search(r"['\"][A-Za-z0-9_-]{32,}['\"]", code), "une clé en dur ?"


def test_l_ecran_question_garde_la_cle_le_temps_de_l_onglet_et_l_oublie_sur_un_403():
    code = code_sans_commentaires("question.js")
    assert "sessionStorage" in code and "localStorage" not in code
    assert "403" in code and "sessionStorage.removeItem" in code


def test_l_ecran_question_n_insere_jamais_de_html():
    # Une réponse ou un titre qui contient « <script> » reste du texte affiché, jamais du code exécuté (OWASP A03).
    code = code_sans_commentaires("question.js")
    for interdit in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write"):
        assert interdit not in code, f"{interdit} dans question.js"
    assert "textContent" in code


def test_un_lien_n_est_rendu_que_s_il_est_http_ou_https():
    # Seconde barrière, après le filtre de l'API (revue de sécurité du commit A4, 16/10/2026) : l'écran vérifie lui
    # aussi le protocole avant de créer un lien, et ouvre l'article d'origine sans lui donner la main sur la page.
    code = code_sans_commentaires("question.js")
    assert "new URL(" in code
    assert '"http:"' in code and '"https:"' in code
    assert '"noopener noreferrer"' in code


def test_chaque_reference_montre_titre_source_table_identifiant_date_et_lien():
    # CA1.2 : les informations d'une référence viennent de l'API, donc des données stockées, jamais du texte du modèle.
    code = code_sans_commentaires("question.js")
    for champ in ("n", "titre", "source", "table", "id", "date", "lien"):
        assert f"reference.{champ}" in code, f"la référence ne montre pas « {champ} »"


def test_la_fiche_montre_la_ligne_stockee_et_son_extrait():
    # CA1.5 et CA1.8 : la fiche montre la ligne telle qu'elle est en base, et le passage transmis au modèle.
    code = code_sans_commentaires("question.js")
    for champ in ("table", "id", "titre", "source", "publie_le", "collecte_le", "extrait"):
        assert f"fiche.{champ}" in code, f"la fiche ne montre pas « {champ} »"


def test_un_refus_et_une_erreur_s_affichent_dans_deux_encarts_distincts():
    # CA2.1 et CA2.4 : un refus (200, statut « refus ») montre son motif ; une panne (503) est une erreur, présentée
    # ailleurs. Les confondre ferait passer une panne pour un refus propre, ou l'inverse.
    html = _question_html()
    assert 'id="refus"' in html and 'id="erreur"' in html
    code = code_sans_commentaires("question.js")
    assert '"refus"' in code and "503" in code
    assert ".motif" in code


def test_la_taille_de_la_question_est_bornee_comme_dans_l_api():
    # Mêmes bornes que `DemandeQuestion` (api/question.py). Le navigateur arrête la saisie avant l'appel ; l'API reste
    # la vraie barrière (422).
    html = _question_html()
    assert 'minlength="3"' in html and 'maxlength="500"' in html


@pytest.mark.parametrize("marqueur, regle", [
    ('lang="fr"', "RGAA 8.3 : langue de la page"),
    ('<label for="cle">', "RGAA 11.1 : le champ de clé a une étiquette"),
    ('<label for="question">', "RGAA 11.1 : le champ de question a une étiquette"),
    ('aria-live="polite"', "RGAA 7.5 : le résultat est annoncé aux lecteurs d'écran"),
    ('<nav aria-label=', "RGAA 12.6 : la navigation est une zone nommée"),
    ('aria-current="page"', "la page courante est marquée"),
])
def test_les_marqueurs_d_accessibilite_de_l_ecran_question(marqueur, regle):
    assert marqueur in _question_html(), regle


def test_l_avertissement_amf_est_sur_l_ecran_question():
    assert "Aucune recommandation d'achat ou de vente" in _question_html()


# --- Règle UE précisée du 06/11/2026 (registre RGPD, § 5, point 13) -------------------------------------------------------
# Le texte d'une question part tel quel vers Azure (T8). La règle demande de limiter les données envoyées au nécessaire :
# l'écran dit, sous le champ, de ne pas y écrire de donnée personnelle. Le texte est relié au champ (aria-describedby), pour
# qu'un lecteur d'écran le lise en même temps que l'étiquette.
def test_l_ecran_question_demande_de_ne_pas_ecrire_de_donnee_personnelle():
    html = _question_html()
    champ = re.search(r"<textarea\b[^>]*\bid=\"question\"[^>]*>", html)
    assert champ and 'aria-describedby="consigne-donnees"' in champ.group(0)
    consigne = re.search(r'<p\b[^>]*\bid="consigne-donnees"[^>]*>(.*?)</p>', html, flags=re.S)
    assert consigne
    texte = " ".join(consigne.group(1).split())
    assert "donnée personnelle" in texte and "Azure" in texte
