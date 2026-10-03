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


def test_p2_ne_vise_que_les_positions_closes():
    """Plan 66 : une position soldee est une ligne dont `date_cloture` est posee par l'import le jour ou
    elle quitte le CSV. `quantite = 0` etait interdit par le schema : la procedure ne trouvait jamais rien."""
    cur = _curseur(0)
    rgpd_purge.p2_purger_positions_soldees(cur, appliquer=True)
    requete = _requetes(cur)[0]
    assert "DATE_CLOTURE IS NOT NULL" in requete
    assert "DATE_CLOTURE <" in requete
    assert "QUANTITE" not in requete, "la quantite d'une position close est celle qu'on detenait, pas zero"


def test_p2_respecte_la_duree_du_registre():
    cur = _curseur(1)
    rgpd_purge.p2_purger_positions_soldees(cur, appliquer=False)
    assert f"{rgpd_purge.RETENTION_POSITION_ANS} YEARS" in _requetes(cur)[0]


# --- P3 retiree (plan 66) : la base refuse les doublons, plus besoin de les detecter ----------------

def test_p3_n_existe_plus_la_base_refuse_les_doublons():
    assert not hasattr(rgpd_purge, "p3_detecter_doublons")


def test_l_orchestration_sans_p3_rend_les_trois_purges():
    import inspect
    source = inspect.getsource(rgpd_purge.executer)
    assert "p3_detecter_doublons" not in source and "doublons" not in source
    assert "p2_purger_positions_soldees" in source


# --- garde-fou global ---------------------------------------------------------

def test_le_defaut_est_la_simulation():
    """Signature : appliquer=False par défaut. Le défaut doit être inoffensif."""
    import inspect
    params = inspect.signature(rgpd_purge.executer).parameters
    assert params["appliquer"].default is False


# --- P6 : purge du journal des appels MCP (plan 62, T5 du registre) ---------------------------

def test_p6_simulation_ne_lance_aucun_delete():
    cur = _curseur(4)
    r = rgpd_purge.p6_purger_mcp_calls(cur, appliquer=False)
    assert r["procedure"] == "P6" and r["concernees"] == 4 and r["supprimees"] == 0
    assert not any("DELETE" in q for q in _requetes(cur))


def test_p6_application_lance_le_delete_sur_mcp_calls():
    cur = _curseur(4)
    r = rgpd_purge.p6_purger_mcp_calls(cur, appliquer=True)
    assert r["supprimees"] == 4
    assert any("DELETE FROM MCP_CALLS" in q for q in _requetes(cur))


def test_p6_respecte_la_duree_du_registre():
    cur = _curseur(1)
    rgpd_purge.p6_purger_mcp_calls(cur, appliquer=False)
    assert f"{rgpd_purge.RETENTION_MCP_CALLS_JOURS} DAYS" in _requetes(cur)[0]
    assert rgpd_purge.RETENTION_MCP_CALLS_JOURS == 90


def test_p6_fait_partie_de_l_orchestration():
    import inspect
    assert "p6_purger_mcp_calls" in inspect.getsource(rgpd_purge.executer)
