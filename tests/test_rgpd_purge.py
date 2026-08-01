"""Tests des procédures de tri RGPD — curseur simulé, aucune base requise.

La propriété la plus importante à tester n'est pas « la purge supprime bien », c'est
**« la simulation ne supprime rien »**. Un mode simulation qui supprimerait par erreur
provoquerait exactement la perte de données qu'il est censé empêcher.
"""
from unittest.mock import MagicMock

from db import rgpd_purge


def _curseur(nb_lignes: int = 3, doublons=None) -> MagicMock:
    """Curseur simulé : fetchone -> compteur, fetchall -> doublons."""
    cur = MagicMock()
    cur.fetchone.return_value = (nb_lignes,)
    cur.fetchall.return_value = doublons or []
    return cur


def _requetes(cur) -> list[str]:
    return [appel.args[0].upper() for appel in cur.execute.call_args_list]


# --- P1 : purge du journal de mémoire ----------------------------------------

def test_p1_simulation_ne_lance_aucun_delete():
    cur = _curseur(3)
    r = rgpd_purge.p1_purger_audit(cur, appliquer=False)

    assert r["concernees"] == 3
    assert r["supprimees"] == 0
    assert not any("DELETE" in q for q in _requetes(cur))


def test_p1_application_lance_le_delete():
    cur = _curseur(3)
    r = rgpd_purge.p1_purger_audit(cur, appliquer=True)

    assert r["supprimees"] == 3
    assert any("DELETE FROM MEMORY_AUDIT" in q for q in _requetes(cur))


def test_p1_ne_supprime_pas_quand_rien_a_purger():
    """Zéro ligne concernée : pas de DELETE inutile."""
    cur = _curseur(0)
    r = rgpd_purge.p1_purger_audit(cur, appliquer=True)

    assert r["concernees"] == 0
    assert not any("DELETE" in q for q in _requetes(cur))


def test_p1_respecte_la_duree_du_registre():
    """90 jours : la valeur doit venir de la constante, pas d'un nombre en dur."""
    cur = _curseur(1)
    rgpd_purge.p1_purger_audit(cur, appliquer=False)
    assert f"{rgpd_purge.RETENTION_AUDIT_JOURS} DAYS" in _requetes(cur)[0]


# --- P2 : positions soldées ---------------------------------------------------

def test_p2_simulation_ne_lance_aucun_delete():
    cur = _curseur(2)
    r = rgpd_purge.p2_purger_positions_soldees(cur, appliquer=False)

    assert r["concernees"] == 2
    assert r["supprimees"] == 0
    assert not any("DELETE" in q for q in _requetes(cur))


def test_p2_ne_vise_que_les_positions_soldees():
    """Filtre quantite = 0 obligatoire — sinon on efface un portefeuille vivant."""
    cur = _curseur(0)
    rgpd_purge.p2_purger_positions_soldees(cur, appliquer=True)
    assert "QUANTITE = 0" in _requetes(cur)[0]


def test_p2_respecte_la_duree_du_registre():
    cur = _curseur(1)
    rgpd_purge.p2_purger_positions_soldees(cur, appliquer=False)
    assert f"{rgpd_purge.RETENTION_POSITION_ANS} YEARS" in _requetes(cur)[0]


# --- P3 : détection seule -----------------------------------------------------

def test_p3_ne_supprime_jamais_rien():
    """Même en mode application : deux achats identiques le même jour sont possibles."""
    cur = _curseur(doublons=[("MC.PA", "2023-04-18", 632.40, 2, [1, 8])])
    doublons = rgpd_purge.p3_detecter_doublons(cur)

    assert len(doublons) == 1
    assert doublons[0][0] == "MC.PA"
    assert not any("DELETE" in q for q in _requetes(cur))


def test_p3_groupe_sur_ticker_date_et_pru():
    cur = _curseur()
    rgpd_purge.p3_detecter_doublons(cur)
    requete = _requetes(cur)[0]
    assert "GROUP  BY TICKER, DATE_ACHAT, PRU" in requete
    assert "HAVING COUNT(*) > 1" in requete


def test_p3_sans_doublon_retourne_liste_vide():
    assert rgpd_purge.p3_detecter_doublons(_curseur(doublons=[])) == []


# --- garde-fou global ---------------------------------------------------------

def test_le_defaut_est_la_simulation():
    """Signature : appliquer=False par défaut. Le défaut doit être inoffensif."""
    import inspect
    params = inspect.signature(rgpd_purge.executer).parameters
    assert params["appliquer"].default is False
