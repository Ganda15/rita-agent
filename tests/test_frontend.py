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
