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

def _jeu_demo_tel_que_l_api_le_rend():
    from sources.positions import EXEMPLE, lire
    positions = [{"ticker": p.ticker, "quantite": p.quantite, "pru": p.pru, "devise": p.devise}
                 for p in lire(EXEMPLE).positions]
    return {"nb": len(positions), "total_eur": 0.0, "positions": positions}


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
    _simuler(monkeypatch, reponse=_FausseReponse(200, _jeu_demo_tel_que_l_api_le_rend()))
    monkeypatch.setenv("RITA_MCP_PORTEFEUILLE", "demo")
    r = asyncio.run(passerelle.rita_portefeuille())
    assert r["success"] is True
    assert len(r["data"]["positions"]) == 10


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
