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
    tete = (RACINE / "docs" / "sprint-5" / "livrable" / "livrable-sprint-5.md").read_text(encoding="utf-8")[:1200]
    assert "Version 2" in tete
    assert "page 11" in tete
