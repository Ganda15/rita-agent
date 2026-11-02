"""Tests de la passerelle MCP — `passerelle_mcp/serveur.py` (C10, C15, C17).

## Ce que ces tests protègent

Le risque principal d'une passerelle n'est pas qu'elle tombe en panne : c'est qu'elle
**contourne** silencieusement les protections du service qu'elle expose. Un outil MCP
qui répondrait sans clé d'API annulerait la correction OWASP API2 du 18/08
(`evidence/C21/INC-001`) sans qu'aucun autre test ne s'en aperçoive.

`test_la_cle_est_bien_transmise_a_l_api` et `test_un_403_devient_NOT_AUTHORIZED` sont
donc les deux tests centraux de ce fichier. Les autres vérifient que les pannes
produisent un message **actionnable** plutôt qu'une trace d'exception.

## Pourquoi `asyncio.run()` et pas `pytest-asyncio`

Les outils MCP sont asynchrones, mais le dépôt n'utilise `pytest-asyncio` nulle part.
Ajouter une dépendance de test pour huit cas serait disproportionné : `asyncio.run()`
dans un test synchrone fait exactement le même travail, sans rien installer.

**Aucun test ici ne touche l'API réelle** — `httpx.AsyncClient` est simulé. La preuve
d'exécution réelle est dans `evidence/C10/preuve-passerelle-mcp.md`.
"""
import asyncio
import csv
from collections import Counter
from decimal import Decimal
from pathlib import Path

import httpx
import pytest

from passerelle_mcp import serveur as passerelle


# --- outillage de simulation --------------------------------------------------

class _FausseReponse:
    def __init__(self, code=200, corps=None):
        self.status_code = code
        self._corps = corps if corps is not None else {"ok": True}

    def json(self):
        return self._corps


class _FauxClient:
    """Remplace `httpx.AsyncClient` : enregistre l'appel, rend une réponse figée."""

    dernier_appel: dict = {}

    def __init__(self, reponse=None, exception=None, **_):
        self._reponse = reponse or _FausseReponse()
        self._exception = exception

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return False

    async def get(self, url, headers=None, params=None):
        _FauxClient.dernier_appel = {"url": url, "headers": headers, "params": params}
        if self._exception:
            raise self._exception
        return self._reponse

    dernier_post: dict = {}

    async def post(self, url, headers=None, json=None):
        _FauxClient.dernier_post = {"url": url, "headers": headers, "json": json}
        if self._exception:
            raise self._exception
        return _FausseReponse(200, {"enregistre": True})


def _simuler(monkeypatch, reponse=None, exception=None):
    monkeypatch.setenv("RITA_API_KEY", "cle-de-test-suffisamment-longue")
    monkeypatch.setattr(
        passerelle.httpx, "AsyncClient",
        lambda **kw: _FauxClient(reponse=reponse, exception=exception, **kw),
    )


# --- les outils déclarés ------------------------------------------------------

def test_les_trois_outils_sont_declares():
    outils = asyncio.run(passerelle.serveur.list_tools())
    assert {o.name for o in outils} == {
        "rita_fraicheur", "rita_portefeuille", "rita_indicateurs",
    }


def test_tous_les_outils_sont_declares_en_lecture_seule():
    """`read_only_hint` autorise un client à appeler l'outil sans demander de
    confirmation. Un outil qui écrirait en base et se déclarerait en lecture seule
    serait un piège pour l'utilisateur — d'où ce test sur les trois."""
    outils = asyncio.run(passerelle.serveur.list_tools())
    for o in outils:
        assert o.annotations.read_only_hint is True, o.name
        assert o.annotations.destructive_hint is False, o.name


def test_seul_indicateurs_prend_un_parametre():
    outils = {o.name: o for o in asyncio.run(passerelle.serveur.list_tools())}
    assert list(outils["rita_indicateurs"].input_schema["properties"]) == ["ticker"]
    assert outils["rita_fraicheur"].input_schema.get("properties", {}) == {}


# --- l'authentification : les deux tests centraux -----------------------------

def test_la_cle_est_bien_transmise_a_l_api(monkeypatch):
    """LE test du fichier. La passerelle **transmet** l'identité, elle ne la
    remplace pas. Si cet en-tête disparaissait, la passerelle deviendrait une porte
    dérobée contournant le 403 — et rien d'autre ne le signalerait."""
    _simuler(monkeypatch)
    asyncio.run(passerelle.rita_fraicheur())
    assert _FauxClient.dernier_appel["headers"]["X-API-Key"] == "cle-de-test-suffisamment-longue"


def test_un_403_devient_NOT_AUTHORIZED(monkeypatch):
    _simuler(monkeypatch, reponse=_FausseReponse(403))
    resultat = asyncio.run(passerelle.rita_portefeuille())
    assert resultat["success"] is False
    assert resultat["error"]["code"] == "NOT_AUTHORIZED"


def test_sans_cle_la_passerelle_refuse_de_servir(monkeypatch):
    """Même règle que `api/main.py` : pas de valeur par défaut, panne explicite.
    Une clé par défaut n'est pas une clé, c'est une porte ouverte documentée."""
    monkeypatch.delenv("RITA_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="RITA_API_KEY"):
        passerelle._cle_api()


# --- les pannes produisent un message actionnable -----------------------------

def test_api_injoignable_donne_SERVICE_INDISPONIBLE(monkeypatch):
    _simuler(monkeypatch, exception=httpx.ConnectError("refused"))
    resultat = asyncio.run(passerelle.rita_fraicheur())
    assert resultat["error"]["code"] == "SERVICE_INDISPONIBLE"
    # Le message doit dire QUOI FAIRE : un garde-fou qui bloque sans expliquer
    # se contourne par celui qu'il protège.
    assert "uvicorn" in resultat["error"]["message"]


def test_delai_depasse_est_distingue_d_une_panne(monkeypatch):
    """Une API lente et une API éteinte ne se corrigent pas de la même façon :
    deux codes distincts, pas un `ERREUR` générique."""
    _simuler(monkeypatch, exception=httpx.TimeoutException("trop long"))
    resultat = asyncio.run(passerelle.rita_indicateurs())
    assert resultat["error"]["code"] == "DELAI_DEPASSE"


# --- le passage des paramètres ------------------------------------------------

def test_le_ticker_est_transmis_en_parametre(monkeypatch):
    _simuler(monkeypatch)
    asyncio.run(passerelle.rita_indicateurs(ticker="MC.PA"))
    assert _FauxClient.dernier_appel["params"] == {"ticker": "MC.PA"}


def test_sans_ticker_aucun_parametre_n_est_envoye(monkeypatch):
    """`params=None` et non `{'ticker': None}` : le second enverrait `ticker=`
    dans l'URL, que FastAPI refuserait ou interpréterait de travers."""
    _simuler(monkeypatch)
    asyncio.run(passerelle.rita_indicateurs())
    assert _FauxClient.dernier_appel["params"] is None


def test_une_reponse_valide_est_enveloppee_avec_success(monkeypatch):
    # Sur `rita_fraicheur` : depuis le 03/10 (cas A04), `rita_portefeuille` a sa propre politique
    # d'accès, testée plus bas ; ce test ne porte que sur l'enveloppe `success` / `data`.
    _simuler(monkeypatch, reponse=_FausseReponse(200, {"nb": 7, "derniere_seance": "2026-10-02"}))
    resultat = asyncio.run(passerelle.rita_fraicheur())
    assert resultat["success"] is True
    assert resultat["data"]["nb"] == 7


# --- chapitre « Données » (validé le 03/10/2026), cas A04 : le portefeuille n'est servi qu'en
# démonstration déclarée ET vérifiée (issue #60) --------------------------------------------
#
# Avant : `rita_portefeuille` rendait ce que l'API rendait, et sa description promettait un « jeu
# de démonstration anonymisé » sans rien vérifier. Or la table `position` contient ce qu'on y a
# importé : le jeu d'exemple, ou le portefeuille réel d'Era (données personnelles financières).
# Règle de la matrice d'accès (§3.3) : application hôte MCP → portefeuille réel REFUS par défaut,
# portefeuille fictif seulement « si connecté au jeu fictif vérifié ».

JEU_ATTENDU = Path(passerelle.__file__).resolve().parent / "jeu_demo_attendu.csv"

# Les treize champs de la requête R1 (`sources/database.py`, SQL_PORTEFEUILLE), les seuls qui sortent par MCP (#152).
CHAMPS_SERVIS = {"ticker", "nom_officiel", "statut_qualite", "quantite", "pru", "devise", "date_cours", "cours",
                 "investi_eur", "valorisation_eur", "performance_pct", "taux_pour_eur", "taux_manquant"}


def _jeu_demo_tel_que_l_api_le_rend():
    """La réponse de `GET /donnees/portefeuille` quand la base porte le jeu d'exemple importé (#152, 01/11/2026).

    Sept positions, pas dix : l'import écarte TTE.PA, AAPL et MSFT, hors univers. Les treize champs de la requête R1,
    l'enveloppe complète de la route, et les nombres en flottants, comme FastAPI sérialise les `NUMERIC` de PostgreSQL.
    """
    with JEU_ATTENDU.open(encoding="utf-8", newline="") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    positions = []
    for l in lignes:
        quantite, pru = float(l["quantite"]), float(l["pru"])
        cours = round(pru * 1.1, 2)
        positions.append({
            "ticker": l["ticker"], "nom_officiel": f"Societe {l['ticker']}", "statut_qualite": "OK",
            "quantite": quantite, "pru": pru, "devise": l["devise"], "date_cours": "2026-10-30", "cours": cours,
            "investi_eur": round(quantite * pru, 2), "valorisation_eur": round(quantite * cours, 2),
            "performance_pct": 10.0, "taux_pour_eur": 1, "taux_manquant": False,
        })
    return {"nb": len(positions), "total_eur": round(sum(p["valorisation_eur"] for p in positions), 2),
            "positions_sans_taux": 0, "positions_closes": 0, "positions": positions}


def test_sans_declaration_d_environnement_le_portefeuille_est_refuse_sans_appeler_l_api(monkeypatch):
    _simuler(monkeypatch, reponse=_FausseReponse(200, _jeu_demo_tel_que_l_api_le_rend()))
    monkeypatch.delenv("RITA_MCP_PORTEFEUILLE", raising=False)
    _FauxClient.dernier_appel = {}
    r = asyncio.run(passerelle.rita_portefeuille())
    assert r["success"] is False and r["error"]["code"] == "NOT_AUTHORIZED"
    assert "RITA_MCP_PORTEFEUILLE" in r["error"]["message"], "le message dit quoi declarer"
    assert _FauxClient.dernier_appel == {}, "refus par defaut : l'API n'est meme pas appelee"


def test_un_environnement_declare_reel_est_refuse_aussi(monkeypatch):
    _simuler(monkeypatch, reponse=_FausseReponse(200, _jeu_demo_tel_que_l_api_le_rend()))
    monkeypatch.setenv("RITA_MCP_PORTEFEUILLE", "reel")
    _FauxClient.dernier_appel = {}
    r = asyncio.run(passerelle.rita_portefeuille())
    assert r["success"] is False and r["error"]["code"] == "NOT_AUTHORIZED"
    assert _FauxClient.dernier_appel == {}


def test_en_demonstration_le_jeu_d_exemple_est_servi(monkeypatch):
    """#152 : jusqu'au 01/11/2026, ce test attendait les dix lignes du fichier d'exemple, que l'API ne rend jamais
    (l'import en garde sept) ; il validait donc le défaut au lieu de l'attraper."""
    _simuler(monkeypatch, reponse=_FausseReponse(200, _jeu_demo_tel_que_l_api_le_rend()))
    monkeypatch.setenv("RITA_MCP_PORTEFEUILLE", "demo")
    r = asyncio.run(passerelle.rita_portefeuille())
    assert r["success"] is True
    assert len(r["data"]["positions"]) == 7


def test_en_demonstration_des_positions_qui_ne_sont_pas_le_jeu_d_exemple_sont_refusees(monkeypatch):
    """Le cas A04 : la déclaration dit « démo » mais l'API sert autre chose (un portefeuille réel).
    La passerelle le détecte en comparant aux positions du fichier d'exemple, et ne rend RIEN."""
    reel = {"nb": 2, "total_eur": 12345.0,
            "positions": [{"ticker": "MC.PA", "quantite": 3, "pru": 710.0, "devise": "EUR"},
                          {"ticker": "TTE.PA", "quantite": 50, "pru": 52.1, "devise": "EUR"}]}
    _simuler(monkeypatch, reponse=_FausseReponse(200, reel))
    monkeypatch.setenv("RITA_MCP_PORTEFEUILLE", "demo")
    r = asyncio.run(passerelle.rita_portefeuille())
    assert r["success"] is False and r["error"]["code"] == "NOT_AUTHORIZED"
    assert "data" not in r
    assert "12345" not in str(r) and "710" not in str(r), "aucun chiffre du portefeuille ne fuit dans l'erreur"


def test_les_autres_outils_ne_dependent_pas_de_la_declaration(monkeypatch):
    _simuler(monkeypatch, reponse=_FausseReponse(200, {"derniere_seance": "2026-10-02"}))
    monkeypatch.delenv("RITA_MCP_PORTEFEUILLE", raising=False)
    assert asyncio.run(passerelle.rita_fraicheur())["success"] is True
    assert asyncio.run(passerelle.rita_indicateurs("MC.PA"))["success"] is True


# --- plan 62 (03/10/2026) : chaque appel est identifiable, chaque refus local remonte ------------

def test_chaque_appel_porte_l_identite_technique_et_le_nom_de_l_outil(monkeypatch):
    """D1 : l'API ne journalise que les appels qui se declarent ; la passerelle se declare toujours."""
    _simuler(monkeypatch, reponse=_FausseReponse(200, {"ok": True}))
    asyncio.run(passerelle.rita_indicateurs("MC.PA"))
    entetes = _FauxClient.dernier_appel["headers"]
    assert entetes["X-Client-Id"] == "passerelle-mcp"
    assert entetes["X-Outil"] == "rita_indicateurs"


def test_un_refus_local_du_portefeuille_est_signale_a_l_api(monkeypatch):
    """D2 : le refus par defaut (#60) ne laissait aucune trace ; il part maintenant vers POST /audit/mcp,
    sans jamais lire la base ni appeler la route de donnees."""
    _simuler(monkeypatch)
    monkeypatch.delenv("RITA_MCP_PORTEFEUILLE", raising=False)
    _FauxClient.dernier_appel = {}
    _FauxClient.dernier_post = {}
    r = asyncio.run(passerelle.rita_portefeuille())
    assert r["success"] is False
    assert _FauxClient.dernier_appel == {}, "aucun appel metier"
    post = _FauxClient.dernier_post
    assert post["url"].endswith("/audit/mcp")
    assert post["json"]["outil"] == "rita_portefeuille" and post["json"]["statut"] == "refuse"
    assert post["json"]["code_erreur"] == "NOT_AUTHORIZED"
    assert post["headers"]["X-Client-Id"] == "passerelle-mcp"
    assert "positions" not in post["json"] and "ticker" not in str(post["json"])


def test_une_panne_du_signalement_ne_change_pas_la_reponse_a_l_utilisateur(monkeypatch):
    _simuler(monkeypatch, exception=httpx.ConnectError("refused"))
    monkeypatch.delenv("RITA_MCP_PORTEFEUILLE", raising=False)
    r = asyncio.run(passerelle.rita_portefeuille())
    assert r["success"] is False and r["error"]["code"] == "NOT_AUTHORIZED"


# --- #152 (recette du 01/11/2026) : le verrou reconnaît le jeu importé, et rien d'autre ----------------------------
#
# Avant : le verrou comparait des ENSEMBLES de couples (ticker, quantité) aux dix lignes du fichier d'exemple. Il
# refusait le jeu réellement importé (sept lignes) et acceptait les mêmes tickers et quantités avec d'autres prix de
# revient, ou une ligne en double. Référence désormais : `passerelle_mcp/jeu_demo_attendu.csv`, versionné, relié au
# vrai import par `tests/test_jeu_demo_mcp_base.py`. Comparaison de quatre champs, doublons comptés, sans arrondi ;
# réponse reconstruite ; refus au moindre doute.

def _servir(monkeypatch, corps):
    _simuler(monkeypatch, reponse=_FausseReponse(200, corps))
    monkeypatch.setenv("RITA_MCP_PORTEFEUILLE", "demo")
    return asyncio.run(passerelle.rita_portefeuille())


def _refuse_sans_donnee(r):
    return r["success"] is False and r["error"]["code"] == "NOT_AUTHORIZED" and "data" not in r


def test_le_jeu_attendu_est_le_fichier_d_exemple_passe_par_les_regles_de_l_import():
    """Miroir sans base des règles de `db/importer.py` (ticker dans l'univers, sinon alias du libellé, sinon ignoré).
    La preuve qui fait foi est le vrai import, sur la base de test ; celle-ci tourne aussi dans le job `pytest`."""
    from db.importer import charger_univers
    from sources.positions import EXEMPLE, lire
    valeurs, alias = charger_univers()
    par_alias = dict(alias)
    attendu = Counter()
    for p in lire(EXEMPLE).positions:
        cible = p.ticker if p.ticker in valeurs else par_alias.get(p.nom)
        if cible:
            attendu[(cible, Decimal(str(p.quantite)), Decimal(str(p.pru)), p.devise)] += 1
    assert sum(attendu.values()) == 7
    assert passerelle._jeu_attendu() == attendu


def test_des_prix_de_revient_differents_ne_sont_pas_le_jeu_d_exemple(monkeypatch):
    """Le test rouge du 01/11 (`evidence/C17/correctifs-2026-11-01/`) : mêmes tickers, mêmes quantités, autres prix."""
    deguise = _jeu_demo_tel_que_l_api_le_rend()
    for p in deguise["positions"]:
        p["pru"] = round(p["pru"] * 1.37, 2)
    assert _refuse_sans_donnee(_servir(monkeypatch, deguise))


@pytest.mark.parametrize("champ, valeur", [
    ("pru", 866.39),
    ("pru", 632.40001),       # au-delà de l'échelle de la colonne : aucun arrondi ne masque l'écart
    ("quantite", 13.0),
    ("quantite", 12.00001),
    ("devise", "USD"),
])
def test_un_seul_champ_compare_qui_differe_fait_refuser(monkeypatch, champ, valeur):
    corps = _jeu_demo_tel_que_l_api_le_rend()
    next(p for p in corps["positions"] if p["ticker"] == "MC.PA")[champ] = valeur
    assert _refuse_sans_donnee(_servir(monkeypatch, corps))


@pytest.mark.parametrize("cas", ["une_en_plus", "une_en_moins", "une_ligne_en_double"])
def test_une_position_en_plus_en_moins_ou_en_double_fait_refuser(monkeypatch, cas):
    corps = _jeu_demo_tel_que_l_api_le_rend()
    positions = corps["positions"]
    if cas == "une_en_plus":
        positions.append({**positions[0], "ticker": "ORA.PA", "nom_officiel": "Orange"})
    elif cas == "une_en_moins":
        positions.pop()
    else:
        positions.append(dict(positions[0]))   # un ensemble l'aurait absorbée
    corps["nb"] = len(positions)
    assert _refuse_sans_donnee(_servir(monkeypatch, corps))


@pytest.mark.parametrize("closes", [1, None])
def test_des_positions_closes_ou_un_compte_absent_font_refuser(monkeypatch, closes):
    """Mode strict : une position close n'est pas forcément personnelle (elle peut être fictive), mais elle n'appartient
    pas au jeu attendu ; et une réponse qui ne dit pas combien il y en a ne permet pas de le savoir."""
    corps = _jeu_demo_tel_que_l_api_le_rend()
    if closes is None:
        del corps["positions_closes"]
    else:
        corps["positions_closes"] = closes
    assert _refuse_sans_donnee(_servir(monkeypatch, corps))


def test_un_compte_de_positions_qui_ne_correspond_pas_fait_refuser(monkeypatch):
    corps = _jeu_demo_tel_que_l_api_le_rend()
    corps["nb"] = 8
    assert _refuse_sans_donnee(_servir(monkeypatch, corps))


@pytest.mark.parametrize("champ", ["pru", "devise", "cours", "taux_manquant"])
def test_un_champ_indispensable_absent_fait_refuser(monkeypatch, champ):
    corps = _jeu_demo_tel_que_l_api_le_rend()
    del corps["positions"][0][champ]
    assert _refuse_sans_donnee(_servir(monkeypatch, corps))


@pytest.mark.parametrize("contenu", [None, "ticker;quantite;pru;devise\n"])
def test_un_jeu_attendu_absent_ou_vide_fait_refuser(monkeypatch, tmp_path, contenu):
    fichier = tmp_path / "jeu_demo_attendu.csv"
    if contenu is not None:
        fichier.write_text(contenu, encoding="utf-8")
    monkeypatch.setattr(passerelle, "JEU_DEMO_ATTENDU", fichier)
    assert _refuse_sans_donnee(_servir(monkeypatch, _jeu_demo_tel_que_l_api_le_rend()))


def test_la_reponse_servie_ne_porte_que_les_champs_de_la_liste(monkeypatch):
    corps = _jeu_demo_tel_que_l_api_le_rend()
    corps["titulaire"] = "a ne pas diffuser"
    for p in corps["positions"]:
        p["note_personnelle"] = "a ne pas diffuser"
    r = _servir(monkeypatch, corps)
    assert r["success"] is True
    assert set(r["data"]) == {"nb", "total_eur", "positions_sans_taux", "positions"}
    assert all(set(p) == CHAMPS_SERVIS for p in r["data"]["positions"])
    assert "a ne pas diffuser" not in str(r)


def test_le_total_est_recalcule_sur_les_positions_verifiees(monkeypatch):
    corps = _jeu_demo_tel_que_l_api_le_rend()
    corps["total_eur"] = 999999.99      # le total de l'API n'est pas repris
    r = _servir(monkeypatch, corps)
    attendu = sum(Decimal(str(p["valorisation_eur"])) for p in corps["positions"])
    assert r["data"]["nb"] == 7
    assert Decimal(str(r["data"]["total_eur"])) == attendu


def test_sans_valorisation_pour_une_ligne_le_total_est_indisponible(monkeypatch):
    """Un total partiel présenté comme total serait faux (même règle que l'API, plan 65) : `null`, jamais une somme.

    La ligne est celle que la requête R1 rend pour une valeur sans cotation : cours, date, valorisation et performance
    à `null` ensemble. Une valeur légitimement indisponible reste `null` et la ligne est servie."""
    corps = _jeu_demo_tel_que_l_api_le_rend()
    corps["positions"][0].update(cours=None, date_cours=None, valorisation_eur=None, performance_pct=None)
    r = _servir(monkeypatch, corps)
    assert r["success"] is True and r["data"]["total_eur"] is None


# --- #152, seconde revue du 01/11 au soir : le contenu des champs, pas seulement leur nom --------------------------
#
# La première version vérifiait que les treize champs étaient présents, pas ce qu'ils contenaient : un objet à la place
# d'un cours, ou du texte à la place d'une valorisation, sortaient tels quels ; une ligne annonçait un taux manquant et
# une valorisation chiffrée. Aucune donnée personnelle n'a été montrée sortie, mais la promesse « au moindre doute, rien
# ne sort » n'était pas tenue. Les règles de cohérence sont celles de la requête R1 (`sources/database.py`).

def test_un_objet_a_la_place_du_cours_fait_refuser(monkeypatch):
    corps = _jeu_demo_tel_que_l_api_le_rend()
    corps["positions"][0]["cours"] = {"valeur": 695.64, "note": "a ne pas diffuser"}
    r = _servir(monkeypatch, corps)
    assert _refuse_sans_donnee(r) and "a ne pas diffuser" not in str(r)


def test_du_texte_a_la_place_de_la_valorisation_fait_refuser(monkeypatch):
    corps = _jeu_demo_tel_que_l_api_le_rend()
    corps["positions"][0]["valorisation_eur"] = "a ne pas diffuser"
    r = _servir(monkeypatch, corps)
    assert _refuse_sans_donnee(r) and "a ne pas diffuser" not in str(r)


def test_un_taux_manquant_avec_une_valorisation_chiffree_fait_refuser(monkeypatch):
    """La requête R1 rend les montants en euros à `null` quand le taux manque : un taux manquant avec une valorisation
    chiffrée est une réponse contradictoire (elle annonçait un taux manquant et un total chiffré), refusée."""
    corps = _jeu_demo_tel_que_l_api_le_rend()
    corps["positions"][0]["taux_manquant"] = True
    assert _refuse_sans_donnee(_servir(monkeypatch, corps))
