"""Sprint 5, livrable en version 2 : la mise en page du PDF ne doit pas transformer une phrase en titre.

Le 25/10, la page 11 du PDF du livrable affichait « #130). L'API de Langfuse l'a confirmé… » en très gros titre : la
ligne 305 du `.md` commençait par `#130)`, et Markdown lit un `#` en début de ligne comme un titre. Ces tests gardent
les documents du sprint 5 qui partent en PDF à l'abri de ce piège, et vérifient que le livrable annonce sa version 2.
"""
import re
from pathlib import Path

import pytest

RACINE = Path(__file__).parent.parent
EN_PDF = [
    RACINE / "docs" / "sprint-5" / "livrable" / "livrable-sprint-5.md",
    RACINE / "docs" / "sprint-5" / "livrable" / "synthese-sprint-5.md",
    RACINE / "docs" / "sprint-5" / "DEMO.md",
    RACINE / "docs" / "exploitation.md",
]


@pytest.mark.parametrize("document", EN_PDF, ids=lambda p: p.name)
def test_aucune_ligne_ne_commence_par_un_diese_suivi_d_un_chiffre(document):
    hors_code, dans_bloc = [], False
    for numero, ligne in enumerate(document.read_text(encoding="utf-8").splitlines(), start=1):
        if ligne.startswith("```"):
            dans_bloc = not dans_bloc
            continue
        if not dans_bloc and re.match(r"#\d", ligne):
            hors_code.append(f"ligne {numero} : {ligne[:60]}")
    assert not hors_code, f"{document.name} : une ligne qui commence par « #<chiffre> » devient un titre : {hors_code}"


def test_le_livrable_annonce_sa_version_2_et_ce_qui_change():
    tete = (RACINE / "docs" / "sprint-5" / "livrable" / "livrable-sprint-5.md").read_text(encoding="utf-8")[:1500]
    assert "Version 2" in tete
    assert "page 11" in tete


LIVRABLE = RACINE / "docs" / "sprint-5" / "livrable" / "livrable-sprint-5.md"


def _section(texte: str, debut: str, fin: str) -> str:
    return texte[texte.index(debut):texte.index(fin, texte.index(debut))]


def test_le_livrable_v3_donne_la_chronologie_d_abord_en_local_puis_en_production():
    """Version 3 (26/10) : le déroulé « d'abord la copie locale, puis la production » se lit d'un coup d'œil (§ 1.2)."""
    texte = LIVRABLE.read_text(encoding="utf-8")
    assert "Version 3" in texte[:1500]
    s12 = _section(texte, "### 1.2", "### 1.3")
    lignes = [l for l in s12.splitlines() if l.startswith("| ") and not l.startswith("| Quand")]
    lieux = [l.split("|")[2].strip() for l in lignes if not set(l.replace("|", "").strip()) <= set("-")]
    assert lieux[0].startswith("copie locale") and lieux[-1].startswith("production"), lieux
    assert any("copie locale" in l for l in lieux[:3]) and "N16" in s12


def test_la_discussion_avec_le_formateur_est_consignee_dans_le_journal_des_retours():
    s6 = _section(LIVRABLE.read_text(encoding="utf-8"), "## 6. Journal des retours", "## 7.")
    assert "formateur" in s6 and "copie locale" in s6 and "production" in s6
