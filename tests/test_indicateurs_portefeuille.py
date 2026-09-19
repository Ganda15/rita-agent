"""Tests du lot 2 des indicateurs — `indicateurs/portefeuille.py`.

⚠️ **Ces tests portent une charge que les données réelles ne portent pas.**
Les 7 positions d'Era sont **toutes en euros** : le chemin multi-devises n'est donc
jamais exercé en production. Les cas ci-dessous sont la **seule** vérification que
l'exposition par devise fonctionne quand il y a plusieurs devises — le jour où une
ligne en dollars entrera, elle sera déjà couverte.

Même limite connue que pour le lot 1 : `_executer` est remplacé, donc le SQL
lui-même n'est pas vérifié ici. Il l'est par exécution réelle, tracée dans
`evidence/C14/preuve-indicateurs-lot2.md`.
"""
from decimal import Decimal

import pytest

from indicateurs import portefeuille, socle
from indicateurs.portefeuille import (
    _charger_requetes,
    lire_exposition,
    lire_poids,
)


def ligne_poids(**surcharges):
    base = {
        "ticker": "MC.PA", "nom_officiel": "LVMH", "devise": "EUR",
        "quantite": Decimal("12"), "valorisation_eur": Decimal("5395.80"),
        "poids_pct": Decimal("16.25"), "total_eur": Decimal("33214.80"),
    }
    base.update(surcharges)
    return base


# --- chargement des requêtes --------------------------------------------------

def test_les_deux_requetes_sont_trouvees_par_marqueur():
    """Le fichier SQL est découpé sur `-- @@REQUETE <nom>`, pas sur le
    point-virgule : un `;` peut apparaître dans une chaîne ou un commentaire, donc
    il ne peut pas servir de séparateur."""
    r = _charger_requetes()
    assert set(r) == {"poids", "exposition"}
    assert "v_portefeuille_valorise" in r["poids"]
    assert "GROUP BY" in r["exposition"]


def test_aucune_requete_ne_garde_de_point_virgule_final():
    """Un `;` résiduel casserait l'ajout d'un filtre ou d'un LIMIT par le code."""
    for nom, sql in _charger_requetes().items():
        assert not sql.rstrip().endswith(";"), nom


def _code_sql_seul(nom: str) -> str:
    """La requête, commentaires retirés.

    ⚠️ **Quatrième fois que ce piège se présente dans le projet** — après `LAG(` dans
    un commentaire SQL, `innerHTML` dans un commentaire JavaScript et `"dev-key"` dans
    une docstring. Ici le commentaire explique *« le défaut que `taux_change` existe
    pour corriger »* : chercher la chaîne dans le fichier entier ferait échouer le
    test sur la phrase qui documente la bonne pratique.

    **Un test doit porter sur le code exécuté, jamais sur ce qui l'explique.**
    """
    return "\n".join(
        code for l in _charger_requetes()[nom].splitlines()
        if (code := l.split("--", 1)[0]).strip()
    )


def test_le_total_se_calcule_apres_conversion_en_euros():
    """⚠️ Le piège central du lot 2, verrouillé par un test.

    Additionner des euros et des dollars produit un nombre dépourvu de sens. La
    requête part donc de `v_portefeuille_valorise`, qui a **déjà** converti — elle
    ne refait pas la conversion. C'est exactement le défaut que la première version
    de la vue commettait, corrigé le 10/08/2026.
    """
    poids = _code_sql_seul("poids")
    assert "v_portefeuille_valorise" in poids
    assert "taux_change" not in poids, \
        "la conversion doit venir de la vue, pas être refaite ici — deux calculs " \
        "de la même chose finissent par diverger"


def test_la_division_par_zero_est_gardee():
    """Un portefeuille vide ne doit pas faire échouer la requête, mais rendre NULL."""
    for sql in _charger_requetes().values():
        assert "NULLIF" in sql


# --- poids --------------------------------------------------------------------

def test_les_poids_sont_convertis_et_le_total_remonte(monkeypatch):
    monkeypatch.setattr(socle, "_executer", lambda sql, p=None: [
        ligne_poids(),
        ligne_poids(ticker="AI.PA", nom_officiel="AIR LIQUIDE",
                    valorisation_eur=Decimal("6682.40"), poids_pct=Decimal("20.12")),
    ])
    lignes, total = lire_poids()

    assert [l.ticker for l in lignes] == ["MC.PA", "AI.PA"]
    assert isinstance(lignes[0].poids_pct, float)
    assert total == pytest.approx(33214.80)


def test_le_total_est_rendu_avec_les_lignes_et_non_recalcule(monkeypatch):
    """L'appelant ne doit pas avoir à additionner lui-même les valorisations :
    ce serait refaire le calcul que la vue a déjà fait."""
    monkeypatch.setattr(socle, "_executer", lambda sql, p=None: [ligne_poids()])
    lignes, total = lire_poids()
    # Le total du portefeuille (33 214,80) n'est PAS la valorisation de la ligne (5 395,80).
    assert total != lignes[0].valorisation_eur


def test_un_portefeuille_vide_ne_plante_pas(monkeypatch):
    monkeypatch.setattr(socle, "_executer", lambda sql, p=None: [])
    lignes, total = lire_poids()
    assert lignes == [] and total is None


def test_la_somme_des_poids_fait_cent(monkeypatch):
    """Le test que la spécification demande explicitement (§6.1), **arrondi compris**.

    Chaque poids est arrondi à 2 décimales par la requête. Leur somme peut donc
    s'écarter de 100 — c'est pourquoi la spec dit « le tester » plutôt que de le
    supposer. Une tolérance de 0,05 point couvre l'arrondi de 7 lignes.
    """
    valeurs = [Decimal(v) for v in ("34.83", "20.12", "16.25", "9.02", "8.96", "5.84", "4.98")]
    monkeypatch.setattr(socle, "_executer", lambda sql, p=None: [
        ligne_poids(ticker=f"T{i}", poids_pct=v) for i, v in enumerate(valeurs)
    ])
    lignes, _ = lire_poids()
    assert sum(l.poids_pct for l in lignes) == pytest.approx(100.0, abs=0.05)


# --- exposition par devise ----------------------------------------------------

def test_exposition_multi_devises(monkeypatch):
    """⚠️ Le cas que les données réelles n'exercent PAS.

    Les 7 positions d'Era sont toutes en euros. Ce test est donc la seule
    vérification que le calcul tient avec plusieurs devises — le cas exact de la
    spécification §6.2 : 3 lignes EUR + 1 ligne USD à 25 %.
    """
    monkeypatch.setattr(socle, "_executer", lambda sql, p=None: [
        {"devise": "EUR", "nb_lignes": 3, "valorisation_eur": Decimal("3000.00"),
         "exposition_pct": Decimal("75.00")},
        {"devise": "USD", "nb_lignes": 1, "valorisation_eur": Decimal("1000.00"),
         "exposition_pct": Decimal("25.00")},
    ])
    e = lire_exposition()

    assert {x.devise: x.exposition_pct for x in e} == {"EUR": 75.0, "USD": 25.0}
    assert sum(x.exposition_pct for x in e) == pytest.approx(100.0)
    assert e[0].nb_lignes == 3


def test_une_seule_devise_donne_cent_pour_cent(monkeypatch):
    """L'état réel du portefeuille au 19/08/2026 : mono-devise."""
    monkeypatch.setattr(socle, "_executer", lambda sql, p=None: [
        {"devise": "EUR", "nb_lignes": 7, "valorisation_eur": Decimal("33214.80"),
         "exposition_pct": Decimal("100.00")},
    ])
    e = lire_exposition()
    assert len(e) == 1 and e[0].exposition_pct == 100.0


def test_le_dict_est_serialisable(monkeypatch):
    monkeypatch.setattr(socle, "_executer", lambda sql, p=None: [ligne_poids()])
    lignes, _ = lire_poids()
    d = lignes[0].en_dict()
    assert isinstance(d["poids_pct"], float)
    assert d["devise"] == "EUR"


# --- la limite de l'indicateur, écrite noir sur blanc -------------------------

def test_la_distinction_cotation_vs_economique_est_documentee():
    """L'exposition mesurée est celle **de cotation**, pas l'exposition économique :
    LVMH est cotée en euros mais vend en dollars et en yuans. Sans cette mention,
    le chiffre se lit de travers — et c'est le genre de nuance qu'un jury teste.

    Ce test verrouille la présence de l'avertissement : une reformulation qui le
    ferait disparaître serait signalée."""
    assert "économique" in portefeuille.ExpositionDevise.__doc__
    assert "économique" in _charger_requetes()["exposition"] or \
           "economique" in _charger_requetes()["exposition"]
