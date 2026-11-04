"""Les places de cotation : fuseau, devise, unité de prix, jours fériés (issues #47, #49, #51, #53).

Chaque règle vient d'une mesure du 27/09/2026 : trois valeurs étrangères étiquetées EUR,
HSBA.L cotée en pence, dix ans d'archive datés en UTC (un jour trop tôt), un cours de
vendredi rangé sous un samedi, et un calcul de fraîcheur qui ignorait les fériés Euronext.
Source des fériés : https://live.euronext.com/en/resources/trading-hours-holidays
"""
from datetime import date

import pandas as pd
import pytest

from sources.marches import (
    date_de_seance,
    derniere_seance,
    devise_de_cotation,
    est_jour_de_bourse,
    facteur_prix,
    jours_feries_euronext,
    paques,
)


# --- devise et unité de prix, par place --------------------------------------

@pytest.mark.parametrize("ticker, devise", [
    ("MC.PA", "EUR"), ("MT.AS", "EUR"), ("SOLB.BR", "EUR"),
    ("HSBA.L", "GBP"), ("FTI", "USD"), ("SLB", "USD"),
])
def test_la_devise_de_cotation_suit_la_place(ticker, devise):
    assert devise_de_cotation(ticker) == devise


def test_une_place_inconnue_echoue_bruyamment():
    """Deviner « EUR » par défaut est exactement ce qui a produit #47."""
    with pytest.raises(ValueError):
        devise_de_cotation("SAP.DE")


def test_londres_cote_en_pence_les_autres_places_en_unites():
    assert facteur_prix("HSBA.L") == 0.01
    assert facteur_prix("MC.PA") == 1
    assert facteur_prix("FTI") == 1


# --- date de séance : la date LOCALE de la place, pas la date UTC ------------

def test_minuit_a_paris_en_ete_reste_le_meme_jour():
    """Minuit à Paris en été = 22h00 UTC la veille : c'est le décalage de #53."""
    assert date_de_seance(pd.Timestamp("2016-07-31 22:00", tz="UTC"), "MC.PA") == date(2016, 8, 1)


def test_minuit_a_paris_en_hiver_reste_le_meme_jour():
    assert date_de_seance(pd.Timestamp("2026-01-04 23:00", tz="UTC"), "MC.PA") == date(2026, 1, 5)


def test_londres_en_ete_et_en_hiver():
    assert date_de_seance(pd.Timestamp("2026-06-01 23:00", tz="UTC"), "HSBA.L") == date(2026, 6, 2)
    assert date_de_seance(pd.Timestamp("2026-01-05 00:00", tz="UTC"), "HSBA.L") == date(2026, 1, 5)


def test_new_york_n_est_pas_decale():
    assert date_de_seance(pd.Timestamp("2026-09-25 04:00", tz="UTC"), "FTI") == date(2026, 9, 25)


def test_un_horodatage_sans_fuseau_est_lu_comme_utc():
    assert date_de_seance(pd.Timestamp("2026-07-30"), "MC.PA") == date(2026, 7, 30)


# --- jours fériés Euronext ----------------------------------------------------

def test_paques():
    assert paques(2025) == date(2025, 4, 20)
    assert paques(2026) == date(2026, 4, 5)


def test_feries_euronext_2026_selon_la_page_officielle():
    feries = jours_feries_euronext(2026)
    for jour in (date(2026, 1, 1), date(2026, 4, 3), date(2026, 4, 6),
                 date(2026, 5, 1), date(2026, 12, 25)):
        assert jour in feries


def test_le_26_decembre_est_ferie_quand_il_tombe_en_semaine():
    assert date(2025, 12, 26) in jours_feries_euronext(2025)


@pytest.mark.parametrize("jour", [
    date(2026, 7, 14),   # fête nationale : Euronext Paris cote
    date(2026, 5, 14),   # Ascension : cote
    date(2026, 5, 25),   # lundi de Pentecôte : cote
    date(2026, 8, 15),   # Assomption : samedi en 2026, donc pas une séance, mais pas un férié Euronext
])
def test_les_feries_francais_ne_sont_pas_des_feries_euronext(jour):
    assert jour not in jours_feries_euronext(jour.year)


def test_est_jour_de_bourse():
    assert est_jour_de_bourse(date(2026, 7, 14)) is True
    assert est_jour_de_bourse(date(2026, 4, 3)) is False       # Vendredi saint
    assert est_jour_de_bourse(date(2026, 9, 26)) is False      # samedi


def test_derniere_seance():
    assert derniere_seance(date(2026, 9, 25)) == date(2026, 9, 25)   # vendredi
    assert derniere_seance(date(2026, 9, 26)) == date(2026, 9, 25)   # samedi -> vendredi
    assert derniere_seance(date(2026, 9, 27)) == date(2026, 9, 25)   # dimanche -> vendredi
    assert derniere_seance(date(2026, 4, 6)) == date(2026, 4, 2)     # lundi de Pâques -> jeudi


def test_place_de_cotation_nomme_euronext_et_les_autres_places():
    """Refonte 001, tâche 3 : le diagnostic du briefing compte les séances avec le calendrier Euronext, et seulement
    pour une valeur cotée sur Euronext (Paris, Amsterdam, Bruxelles). Une place inconnue échoue bruyamment."""
    import pytest
    from sources.marches import place_de_cotation
    places = [place_de_cotation(t) for t in ("MC.PA", "ASML.AS", "UCB.BR", "HSBA.L", "SLB")]
    assert places == ["Euronext", "Euronext", "Euronext", "Londres", "New York"]
    with pytest.raises(ValueError):
        place_de_cotation("BMW.DE")
