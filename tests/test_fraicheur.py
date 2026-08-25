"""Tests de la fraîcheur du jeu de données — `monitorage/fraicheur.py`.

⚠️ **Aucun test ici ne touche une base ni une horloge.** `evaluer()` est une
fonction pure et `aujourdhui` est un paramètre : sans ça, la suite virerait au
rouge toute seule un samedi, et on ne saurait pas si c'est le code ou le
calendrier qui a changé.

La limite connue et assumée, la même que pour les lots d'indicateurs : le SQL
lui-même n'est pas exercé ici (`_executer` est remplacé). Il l'est par exécution
réelle, tracée dans `evidence/C20/`.
"""
from datetime import date, datetime

from monitorage import fraicheur
from monitorage.fraicheur import evaluer, jours_ouvres_ecoules


# --- le comptage en jours ouvrés ------------------------------------------

def test_le_week_end_ne_compte_pas():
    """Vendredi 21/08 -> dimanche 23/08 : aucun jour ouvré écoulé.

    C'est LE cas qui justifie tout le module : compter en jours calendaires
    donnerait 2 et ferait passer la jauge à l'orange chaque dimanche.
    """
    assert jours_ouvres_ecoules(date(2026, 8, 21), date(2026, 8, 23)) == 0


def test_vendredi_vers_lundi_fait_un_jour_ouvre():
    assert jours_ouvres_ecoules(date(2026, 8, 21), date(2026, 8, 24)) == 1


def test_vendredi_vers_mercredi_fait_trois_jours_ouvres():
    assert jours_ouvres_ecoules(date(2026, 8, 21), date(2026, 8, 26)) == 3


def test_une_semaine_pleine_fait_cinq_jours_ouvres():
    assert jours_ouvres_ecoules(date(2026, 8, 17), date(2026, 8, 24)) == 5


def test_une_date_future_ne_donne_pas_un_retard_negatif():
    """Une donnée « du futur » vaut zéro retard, jamais un nombre négatif."""
    assert jours_ouvres_ecoules(date(2026, 8, 25), date(2026, 8, 20)) == 0


def test_le_meme_jour_ne_compte_pas():
    assert jours_ouvres_ecoules(date(2026, 8, 25), date(2026, 8, 25)) == 0


# --- les seuils -----------------------------------------------------------

def _faits(derniere=date(2026, 8, 24)):
    return {
        "derniere_seance": derniere,
        "nb_cotations": 275554,
        "nb_valeurs": 111,
        "nb_positions": 7,
        "nb_articles": 60,
        "nb_taux": 10,
        "derniere_collecte_article": datetime(2026, 8, 25, 19, 0),
        "dernier_taux": date(2026, 8, 25),
    }


def test_seance_de_la_veille_reste_verte():
    """Le seuil vert tolère 1 jour ouvré : la séance du jour n'entre en base
    qu'après la collecte de 19h00, la Bourse clôturant à 17h35."""
    f = evaluer(_faits(date(2026, 8, 24)), aujourdhui=date(2026, 8, 25))
    assert f.statut == "vert"
    assert f.retard_jours_ouvres == 1


def test_deux_jours_ouvres_passent_a_l_orange():
    f = evaluer(_faits(date(2026, 8, 21)), aujourdhui=date(2026, 8, 25))
    assert f.statut == "orange"
    assert f.retard_jours_ouvres == 2


def test_au_dela_de_trois_jours_ouvres_c_est_rouge():
    f = evaluer(_faits(date(2026, 8, 18)), aujourdhui=date(2026, 8, 25))
    assert f.statut == "rouge"
    assert f.retard_jours_ouvres == 5


def test_un_dimanche_avec_la_seance_de_vendredi_reste_vert():
    """Le cas qui ne doit JAMAIS alerter : dimanche, dernière séance vendredi."""
    f = evaluer(_faits(date(2026, 8, 21)), aujourdhui=date(2026, 8, 23))
    assert f.statut == "vert"
    assert f.retard_jours_ouvres == 0


# --- les cas dégradés -----------------------------------------------------

def test_base_sans_aucune_cotation_est_rouge_et_le_dit():
    """Le 16/08 la base avait disparu. Ce cas ne doit pas rendre « vert, 0 jour
    de retard » — l'absence de donnée n'est pas de la donnée fraîche."""
    faits = _faits(None)
    faits["derniere_seance"] = None
    faits["nb_cotations"] = 0
    f = evaluer(faits, aujourdhui=date(2026, 8, 25))
    assert f.statut == "rouge"
    assert f.retard_jours_ouvres is None
    assert "jamais abouti" in f.message


def test_les_comptages_sont_remontes_tels_quels():
    f = evaluer(_faits(), aujourdhui=date(2026, 8, 25))
    assert f.nb_cotations == 275554
    assert f.nb_valeurs == 111
    assert f.nb_positions == 7


def test_en_dict_est_serialisable_pour_l_api():
    d = evaluer(_faits(), aujourdhui=date(2026, 8, 25)).en_dict()
    assert d["statut"] == "vert"
    assert set(d) >= {"aujourdhui", "derniere_seance", "retard_jours_ouvres",
                      "statut", "message", "nb_cotations"}


# --- la lecture complète, base simulée ------------------------------------

def test_lire_prend_la_date_du_serveur_pas_celle_du_poste(monkeypatch):
    """`CURRENT_DATE` vient de PostgreSQL : c'est l'horloge de la base qui fait
    foi pour des données stockées en base. Ici le serveur dit le 26/08 alors
    que la dernière séance est le 21/08 — donc 3 jours ouvrés, orange."""
    class _Extraction:
        lignes = [{**_faits(date(2026, 8, 21)), "aujourdhui": date(2026, 8, 26)}]

    monkeypatch.setattr(fraicheur.database, "_executer",
                        lambda sql, nom, dsn=None, **kw: _Extraction())
    f = fraicheur.lire()
    assert f.aujourdhui == date(2026, 8, 26)
    assert f.retard_jours_ouvres == 3
    assert f.statut == "orange"
