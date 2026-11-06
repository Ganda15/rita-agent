"""Les titres des rapports : le style « bandeaux bleus » de la copie E2 v1.1, sans ses bordures (Era, 06/11/2026).

Pourquoi : Era a choisi ce style pour tous les rapports. Mesuré dans sa copie
(`rapport-E2-2026-11-05-v1.1-bandeaux-bleus-corrige.pdf`) : les titres (h1, h2) en texte noir sur un bandeau bleu
#BFD7F2, les sous-titres (h3) en texte bleu sur un bandeau plus clair #D6E6F7, chaque bandeau avec une bande bleu marine
#12395E à gauche (5 pt pour un titre, 4 pt pour un sous-titre), en Georgia gras. Les deux filets de l'ancienne feuille
(au-dessus du h1, sous le h2) sont retirés : « sans bordure ». Le PDF sort de la source avec ce style, sans retouche.
"""
import re

import pytest

from scripts import rendre_pdf


def _regle(selecteur: str) -> str:
    """Déclarations de la règle propre au sélecteur dans la feuille des rapports (h1{...}, pas h1,h2{...})."""
    regles = re.findall(rf"(?:^|\}}|\n)\s*{re.escape(selecteur)}\s*\{{([^}}]*)\}}", rendre_pdf.STYLE)
    assert regles, f"aucune règle pour {selecteur}"
    return regles[-1]


def test_les_couleurs_sont_celles_de_la_copie_choisie():
    assert "--marine:#12395E" in rendre_pdf.STYLE
    assert "--bandeau-titre:#BFD7F2" in rendre_pdf.STYLE
    assert "--bandeau-sous-titre:#D6E6F7" in rendre_pdf.STYLE


@pytest.mark.parametrize("titre", ["h1", "h2"])
def test_le_titre_est_noir_sur_le_bandeau_bleu_avec_sa_bande_marine(titre):
    regle = _regle(titre)
    assert "background:linear-gradient(to right, var(--marine) 5pt, var(--bandeau-titre) 5pt)" in regle
    assert "color:var(--ink)" in regle


def test_le_sous_titre_est_bleu_sur_le_bandeau_plus_clair_avec_sa_bande_marine():
    regle = _regle("h3")
    assert "background:linear-gradient(to right, var(--marine) 4pt, var(--bandeau-sous-titre) 4pt)" in regle
    assert "color:var(--accent)" in regle


@pytest.mark.parametrize("titre", ["h1", "h2", "h3"])
def test_le_titre_n_a_aucune_bordure(titre):
    assert "border" not in _regle(titre)


def test_les_titres_restent_en_georgia():
    regle = re.search(r"h1,h2,h3,h4\{([^}]*)\}", rendre_pdf.STYLE).group(1)
    assert regle.split("font-family:")[1].startswith("Georgia")
