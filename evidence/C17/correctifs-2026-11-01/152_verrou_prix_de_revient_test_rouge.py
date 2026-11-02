"""#152 (recette du 01/11/2026) : le verrou de démonstration de la passerelle MCP reconnaît le jeu d'exemple
précisément, et rien d'autre. Ce test vaut quel que soit le correctif retenu pour le jeu importé.

Aujourd'hui le verrou ne compare que les couples (ticker, quantité) : un portefeuille qui reprend les tickers et les
quantités du fichier d'exemple, mais avec d'autres prix de revient (des données personnelles), passe le verrou.
L'issue demande une comparaison sur au moins le ticker, la quantité, le prix de revient et la devise.
"""
import asyncio

from tests.test_passerelle_mcp import _FausseReponse, _jeu_demo_tel_que_l_api_le_rend, _simuler, passerelle


def test_des_prix_de_revient_differents_ne_sont_pas_le_jeu_d_exemple(monkeypatch):
    deguise = _jeu_demo_tel_que_l_api_le_rend()
    for p in deguise["positions"]:
        p["pru"] = round(p["pru"] * 1.37, 2)   # mêmes tickers, mêmes quantités, autres prix de revient
    _simuler(monkeypatch, reponse=_FausseReponse(200, deguise))
    monkeypatch.setenv("RITA_MCP_PORTEFEUILLE", "demo")
    r = asyncio.run(passerelle.rita_portefeuille())
    assert r["success"] is False and r["error"]["code"] == "NOT_AUTHORIZED"
    assert "data" not in r
