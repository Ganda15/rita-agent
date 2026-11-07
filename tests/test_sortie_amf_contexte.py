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


# --- Revue de sécurité automatique du commit 4b11a4e : la contextualisation ne doit pas ouvrir de contournement ------
# Exiger « le titre » laissait passer un conseil sur une société nommée (« C'est le moment de renforcer LVMH ») :
# 12 conseils sur 13 passaient. Un nom propre ou un code de valeur compte comme un titre ; les exemptions restent
# étroites (une entreprise sujet, un verbe d'entreprise : « pour s'implanter », jamais « pour s'exposer »).
CONSEILS_SUR_UNE_SOCIETE = [
    "C'est le moment de renforcer LVMH.",
    "Est venu le moment de vendre Sanofi.",
    "Mieux vaut vendre Kering avant les résultats.",
    "Mieux vaut éviter Atos pour le moment.",
    "Il est temps de sortir de Casino.",
    "Air Liquide : à accumuler.",
    "LVMH reste à renforcer.",
    "Le titre mérite de figurer dans votre portefeuille.",
    "Une occasion à saisir pour s'exposer au titre.",
    "Une occasion à saisir pour se positionner sur LVMH.",
    "Le titre est à ne pas manquer avant la publication.",
    "C'est le moment de vendre MC.PA.",
    "Il est temps d'alléger votre position sur TotalEnergies.",
]

FAITS_SUR_UNE_SOCIETE = [
    "LVMH cherche à renforcer sa position en Asie.",
    "Sanofi a décidé de vendre sa filiale de santé grand public.",
    "Kering veut sortir de sa dépendance au marché chinois.",
    "Pour Air Liquide, c'est le moment de renforcer la coopération avec ses fournisseurs.",
    "Selon TotalEnergies, il est temps d'alléger sa dette.",
    "Renault reste à la recherche d'un partenaire.",
]


@pytest.mark.parametrize("texte", CONSEILS_SUR_UNE_SOCIETE)
def test_un_conseil_sur_une_societe_nommee_est_refuse(texte):
    assert not verifier_sortie(texte)["conforme"]


@pytest.mark.parametrize("texte", FAITS_SUR_UNE_SOCIETE)
def test_un_fait_sur_une_societe_nommee_n_est_pas_refuse(texte):
    verdict = verifier_sortie(texte)
    assert verdict["conforme"], verdict["motifs_detectes"]


# --- Revue de sécurité automatique du commit a3ac7f4 : bloquer par défaut dans les tournures de conseil ---------------
# Exiger une majuscule laissait passer « lvmh » et « Éramet », et la grammaire oubliait « d'acheter » et « le moment
# est venu de ». Les tournures de conseil (« c'est le moment de vendre X », « mieux vaut vendre X », « il est temps de
# sortir de X ») sont bloquées par défaut ; elles passent seulement si l'objet est un nom commun introduit par un
# déterminant, hors vocabulaire d'investissement (« la coopération », « sa dette », « de la dépendance »).
CONSEILS_SANS_MAJUSCULE_OU_AUTREMENT_DITS = [
    "C'est le moment d'acheter Kering.",
    "Le moment est venu de vendre LVMH.",
    "C'est le moment de renforcer lvmh.",
    "Mieux vaut vendre Éramet.",
    "Éramet reste à renforcer.",
    "Il est temps de vendre la ligne.",
    "Il est temps de sortir du dossier.",
    "Il est temps de sortir de l'action.",
    "C'est le moment de renforcer franchement les positions sur LVMH.",
    "Mieux vaut vendre maintenant.",
    "Il est temps d'acheter des actions.",
]

FAITS_DANS_UNE_TOURNURE_DE_CONSEIL = [
    "Le groupe estime que le moment est venu de vendre sa filiale américaine.",
    "La BCE juge qu'il est temps d'alléger sa politique monétaire.",
    "Selon l'économiste, il est temps de sortir du nucléaire.",
    "Pour l'État actionnaire, c'est le moment de renforcer la gouvernance.",
    "Le temps de vendre un bien immobilier s'allonge, selon les notaires.",
]


@pytest.mark.parametrize("texte", CONSEILS_SANS_MAJUSCULE_OU_AUTREMENT_DITS)
def test_un_conseil_sans_majuscule_ou_autrement_dit_est_refuse(texte):
    assert not verifier_sortie(texte)["conforme"]


@pytest.mark.parametrize("texte", FAITS_DANS_UNE_TOURNURE_DE_CONSEIL)
def test_un_fait_dans_une_tournure_de_conseil_n_est_pas_refuse(texte):
    verdict = verifier_sortie(texte)
    assert verdict["conforme"], verdict["motifs_detectes"]


# --- Revue de sécurité automatique du commit 757c3bb : décision d'Era, LISTE FERMÉE (07/11) ----------------------------
# Après trois réécritures, chaque revue trouvait de nouvelles tournures qui passaient (« le meilleur moment de vendre
# LVMH », « renforcer un peu LVMH », « acheter de l'or ») : une liste ouverte d'objets de fait a toujours des trous.
# Décision d'Era : dans une tournure de conseil, TOUJOURS refuser, sauf une liste fermée d'objets de fait, tirée des
# faits de ces tests. C'est le choix « fail-closed » déjà écrit dans guardrails/sortie.py.
CONSEILS_TOURNURES_OUVERTES = [
    "C'est le meilleur moment de vendre LVMH.",
    "Le moment de céder Kering approche.",
    "C'est le bon moment d'acheter Kering.",
    "C'est le moment de renforcer un peu LVMH.",
    "Il est temps de vendre une partie de vos LVMH.",
    "Mieux vaut éviter le secteur du luxe.",
    "C'est le moment d'acheter de l'or.",
    "Il est temps d'alléger davantage le groupe.",
    "C'est le moment de renforcer la coopération, puis d'acheter LVMH.",
]

# Le coût du choix, écrit en test pour rester visible : un fait dont l'objet n'est pas dans la liste est refusé.
FAITS_HORS_LISTE_REFUSES_PAR_CHOIX = [
    "Au moment de céder ses parts, le fonds a publié un communiqué.",
    "Pour la direction, c'est le moment de renforcer la sécurité informatique.",
]


@pytest.mark.parametrize("texte", CONSEILS_TOURNURES_OUVERTES)
def test_une_tournure_de_conseil_hors_liste_fermee_est_refusee(texte):
    assert not verifier_sortie(texte)["conforme"]


@pytest.mark.parametrize("texte", FAITS_HORS_LISTE_REFUSES_PAR_CHOIX)
def test_un_fait_hors_liste_fermee_est_refuse_par_choix(texte):
    assert not verifier_sortie(texte)["conforme"]
