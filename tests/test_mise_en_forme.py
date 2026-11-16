"""Le texte d'un briefing s'affiche sans marques de mise en forme Markdown (14/11/2026).

Depuis le 14/11, Mistral rédige les briefings quand Azure refuse sa clé. Le banc C7 du 07/11 comptait des `**` dans
30 briefings de Mistral sur 30 ; l'écran affiche le texte tel quel (`textContent`). Observé en production le 14/11 sur
MC.PA : « Selon *BFM Bourse* (13/10/2026) ». La correction est limitée : seules les marques appariées (`*x*`, `**x**`,
`__x__`) et un `#` de titre en début de ligne sont retirées ; les nombres, les citations `[n]`, les paragraphes, les
tirets et un astérisque isolé restent.
"""
import pytest

from agents.mise_en_forme import sans_marques_markdown
from src.llm import ResultatTexte


@pytest.mark.parametrize("brut, attendu", [
    # Le cas observé en production le 14/11 (briefing MC.PA rédigé par Mistral).
    ("Selon *BFM Bourse* (13/10/2026), la résilience boursière du groupe s'explique en partie.",
     "Selon BFM Bourse (13/10/2026), la résilience boursière du groupe s'explique en partie."),
    ("L'action **LVMH** a clôturé à 403,45 €.", "L'action LVMH a clôturé à 403,45 €."),
    ("Une variation __modérée__ sur la séance.", "Une variation modérée sur la séance."),
    ("# Briefing sur LVMH (MC.PA)\nL'action a clôturé en repli.", "Briefing sur LVMH (MC.PA)\nL'action a clôturé en repli."),
    ("## Séance du 13/11/2026", "Séance du 13/11/2026"),
    ("*Les Échos* et **BFM Bourse** citent la demande chinoise.", "Les Échos et BFM Bourse citent la demande chinoise."),
    # Second cas vu en production le 14/11 (MC.PA, avant la livraison du correctif) : toute une ligne en italique.
    ("Volatilité annualisée élevée (22,12 %).\n*Source : Données de marché au 13/11/2026 (BFM Bourse, 13/10/2026, sur la "
     "persistance des pressions chinoises).*",
     "Volatilité annualisée élevée (22,12 %).\nSource : Données de marché au 13/11/2026 (BFM Bourse, 13/10/2026, sur la "
     "persistance des pressions chinoises)."),
])
def test_les_marques_appariees_et_les_titres_sont_retires(brut, attendu):
    assert sans_marques_markdown(brut) == attendu


@pytest.mark.parametrize("texte", [
    "L'action a reculé de 0,31 % ; sur un mois, +5,05 %.",          # nombres et signes
    "La société annonce une réorganisation [1] et un plan [2].",      # citations numérotées
    "Premier paragraphe.\n\nSecond paragraphe.",                      # paragraphes
    "- un point\n- un autre point",                                   # tirets de liste
    "Un calcul : 5 * 3 = 15.",                                        # astérisque entouré d'espaces
    "Une note de bas de page*",                                       # astérisque isolé
    "Le rôle rita_lecture lit la base.",                              # tiret bas dans un mot
    "Le titre # 3 du classement.",                                    # dièse hors début de ligne
    "",
])
def test_un_texte_sans_marques_reste_identique(texte):
    assert sans_marques_markdown(texte) == texte


def test_le_briefing_rendu_est_debarrasse_des_marques_et_garde_son_auteur(monkeypatch):
    """Le rédacteur nettoie le texte avant qu'il parte au garde-fou de sortie (api/main.py) et à l'écran ; le
    fournisseur, le modèle et les tentatives ne changent pas."""
    from agents import analyst

    brut = ResultatTexte(texte="Selon *BFM Bourse* (13/10/2026), le titre recule de **0,31 %**.",
                         fournisseur="mistral", modele="mistral-large-2512",
                         tentatives=[{"fournisseur": "foundry", "reussi": False},
                                     {"fournisseur": "mistral", "reussi": True}])
    monkeypatch.setattr(analyst, "generer_texte_detaille", lambda prompt, max_tokens: brut)

    rendu = analyst.generate_briefing_detaille("MC.PA", 403.45, -0.31, None, "EUR")

    assert rendu.texte == "Selon BFM Bourse (13/10/2026), le titre recule de 0,31 %."
    assert (rendu.fournisseur, rendu.modele, rendu.tentatives) == (brut.fournisseur, brut.modele, brut.tentatives)
