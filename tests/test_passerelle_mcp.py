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
    _simuler(monkeypatch, reponse=_FausseReponse(200, {"nb": 7, "total_eur": 31448.2}))
    resultat = asyncio.run(passerelle.rita_portefeuille())
    assert resultat["success"] is True
    assert resultat["data"]["nb"] == 7
