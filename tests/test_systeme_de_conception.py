"""Le système de conception de RITA est écrit, et les écrans le respectent (E4, C17.2 ; 06/11/2026).

Pourquoi : Question et Tableau de bord n'ont pas de maquette (rapport E4, § 4.3). Le formateur l'a dit le 03/11 : pour
C17.2, un système de conception suffit comme référence, à montrer à côté de l'interface réelle. Le système existait dans
le code (`frontend/style.css` : deux thèmes, une couleur par écran, des composants partagés) sans être écrit. Il l'est
dans `docs/conception/frontend/systeme-de-conception.md`, et ces tests tiennent l'écrit et le code ensemble :
- aucune couleur n'est écrite en dur hors des jetons (sauf une exception nommée) ;
- les deux écrans sans maquette n'utilisent que des composants du système ;
- chaque jeton du code est décrit dans le document.
"""
import re
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
CSS = (RACINE / "frontend/style.css").read_text(encoding="utf-8")
DOC = RACINE / "docs/conception/frontend/systeme-de-conception.md"
COULEUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")
# La seule couleur hors jetons : l'assombrissement d'un bouton survolé, un voile noir à 12 % posé sur la couleur du bouton.
EXCEPTIONS = {"button:hover { box-shadow: inset 0 0 0 999px rgba(0, 0, 0, .12); }"}


def _sans_commentaires(texte: str) -> str:
    return re.sub(r"/\*.*?\*/", "", texte, flags=re.S)


def _blocs_de_jetons(css: str) -> list[str]:
    return re.findall(r"^:root(?:\[data-theme=\"clair\"\])?\s*\{.*?^\}", css, flags=re.S | re.M)


def test_aucune_couleur_n_est_ecrite_en_dur_hors_des_jetons():
    reste = _sans_commentaires(CSS)
    for bloc in _blocs_de_jetons(reste):
        reste = reste.replace(bloc, "")
    fautives = [ligne.strip() for ligne in reste.splitlines() if COULEUR.search(ligne) and ligne.strip() not in EXCEPTIONS]
    assert fautives == []


@pytest.mark.parametrize("fichier", sorted(p.name for p in (RACINE / "frontend").glob("*.js")))
def test_aucun_script_de_l_interface_n_ecrit_de_couleur(fichier):
    texte = (RACINE / "frontend" / fichier).read_text(encoding="utf-8")
    code = "\n".join(l for l in texte.splitlines() if not l.strip().startswith("//"))
    assert not re.search(r"#[0-9a-fA-F]{6}\b|rgba?\(", code)


@pytest.mark.parametrize("page", ["question.html", "tableau-de-bord.html"])
def test_les_ecrans_sans_maquette_n_utilisent_que_des_composants_du_systeme(page):
    definies = set(re.findall(r"\.([a-zA-Z][\w-]*)", _sans_commentaires(CSS)))
    html = (RACINE / "frontend" / page).read_text(encoding="utf-8")
    script = (RACINE / "frontend" / page.replace(".html", ".js")).read_text(encoding="utf-8")
    utilisees = {c for attr in re.findall(r'class="([^"]*)"', html) for c in attr.split()}
    utilisees |= set(re.findall(r'className\s*=\s*"([\w-]+)"', script))
    utilisees |= set(re.findall(r'classList\.(?:add|toggle)\("([\w-]+)"', script))
    assert utilisees and utilisees <= definies, sorted(utilisees - definies)


def test_chaque_jeton_du_code_est_decrit_dans_le_document():
    assert DOC.exists(), "docs/conception/frontend/systeme-de-conception.md absent"
    doc = DOC.read_text(encoding="utf-8")
    jetons = set(re.findall(r"(--[a-z][a-z0-9-]*)\s*:", "\n".join(_blocs_de_jetons(_sans_commentaires(CSS)))))
    assert jetons and {j for j in jetons if f"`{j}`" not in doc} == set()


def test_le_document_dit_quand_il_a_ete_ecrit_et_ce_qu_il_ne_precede_pas():
    doc = DOC.read_text(encoding="utf-8")
    assert "06/11/2026" in doc
    assert "écrit après le code" in doc
