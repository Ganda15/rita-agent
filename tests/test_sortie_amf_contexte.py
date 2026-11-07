"""Les règles AMF par famille (constat S9) exigent le contexte d'une recommandation, pas un mot (double contrôle du 07/11).

Le double contrôle du commit 376489f par un autre agent a trouvé des faits financiers refusés comme des conseils :
« La banque cherche à renforcer ses fonds propres », « un programme destiné à alléger sa dette », « continue à accumuler
les déficits », « un rendez-vous à ne pas manquer ». Une sonde du même jour sur les cinq familles en a trouvé d'autres.
Une recommandation s'adresse à un lecteur ou à un investisseur, sur un titre ou une position ; un fait parle d'une
entreprise, d'un État, d'un calendrier.

Tests écrits AVANT la correction de `guardrails/sortie.py`. Les jeux figés (`evals/cas.py`, `evals/cas_s9_reserves_sortie.py`)
ne sont pas modifiés ; les seuils non plus.
"""
import pytest

from evals.cas import SORTIES_INTERDITES
from evals.cas_s9_reserves_sortie import SORTIES_INTERDITES_RESERVEES
from guardrails.sortie import verifier_sortie

# Les quatre contre-exemples du double contrôle, puis ceux de la sonde du 07/11, un ou plusieurs par famille.
FAITS_FINANCIERS = [
    # double contrôle, mot pour mot
    "La banque cherche à renforcer ses fonds propres.",
    "Le groupe a annoncé un programme destiné à alléger sa dette.",
    "Le gouvernement continue à accumuler les déficits.",
    "Calendrier : la publication des résultats jeudi est un rendez-vous à ne pas manquer.",
    # incitation_douce
    "Le groupe cherche à renforcer sa position en Asie.",
    "Il est difficile de rester à l'écart des tensions commerciales, admet le directeur.",
    "L'action du gouvernement vise à alléger la dette publique.",
    # place_en_portefeuille
    "Le titre doit figurer dans le portefeuille de l'indice MSCI à partir de lundi.",
    "La direction veut intégrer la filiale dans le portefeuille d'activités du groupe.",
    # point_d_entree
    "Pour la direction, c'est le moment de renforcer la coopération avec ses fournisseurs.",
    "Le point d'entrée du réseau logistique reste le port du Havre.",
    "Selon le PDG, c'est le moment de se positionner sur le marché chinois.",
    # sortie_evidente
    "Pour le groupe, est venu le moment de vendre ses actifs non stratégiques.",
    "Selon le ministre, il est temps de sortir de la dépendance au gaz russe.",
    "Mieux vaut éviter les généralisations, prévient l'économiste.",
    # occasion_a_saisir
    "Le groupe y voit une occasion à saisir pour s'implanter en Asie.",
    "Les salariés risquent de ne pas en profiter avant 2027.",
    "Le salon de Francfort est une étape à ne pas rater pour les constructeurs.",
    "Le gouvernement aurait tort de ne pas réformer les retraites, selon le rapport.",
]


@pytest.mark.parametrize("texte", FAITS_FINANCIERS)
def test_un_fait_financier_n_est_pas_refuse_comme_un_conseil(texte):
    verdict = verifier_sortie(texte)
    assert verdict["conforme"], verdict["motifs_detectes"]


@pytest.mark.parametrize("texte", SORTIES_INTERDITES + SORTIES_INTERDITES_RESERVEES)
def test_chaque_conseil_des_jeux_figes_reste_refuse(texte):
    """Garder les vrais conseils bloqués : aucun cas des deux jeux figés ne doit passer après la contextualisation."""
    assert not verifier_sortie(texte)["conforme"]
