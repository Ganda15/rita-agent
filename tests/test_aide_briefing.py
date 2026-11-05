"""Revue du 05/11/2026 (E4, avant le tournage) : l'aide de l'écran Briefing ne promet pas plus que le garde-fou.

Le garde-fou de sortie retient un texte où il DÉTECTE une recommandation d'achat ou de vente ; il ne peut pas garantir
qu'aucune ne passera jamais. Le rapport E4 v1.5 (annexe A7, page 34) relève « une aide qui promet trop ».
"""
import re
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "frontend" / "briefing.html"


def _aide() -> str:
    m = re.search(r'<p class="precision">(.*?)</p>', PAGE.read_text(encoding="utf-8"), re.S)
    assert m, "paragraphe d'aide de l'écran Briefing introuvable"
    return re.sub(r"\s+", " ", m.group(1).replace("&nbsp;", " ")).strip()


def test_l_aide_ne_promet_pas_qu_aucune_recommandation_ne_passera():
    assert "jamais diffusée" not in _aide()


def test_l_aide_dit_ce_que_fait_le_garde_fou():
    aide = _aide()
    assert "garde-fou" in aide and "détecte" in aide, aide
