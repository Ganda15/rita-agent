"""Les schémas du rapport E3 disent ce que dit le générateur, et la mise en forme d'Era aussi (E3 v1.5, 24/10/2026).

Pourquoi ce test : le 24/10, la première mise en forme des cinq schémas, faite à partir d'un rendu intermédiaire,
disait « 6 h à 9 h » pour le créneau du matin (8 h à 9 h dans le code), et deux autres textes que le générateur avait
déjà corrigés. Une image dessinée à la main ne se relit pas seule : ce test compare chaque texte de la mise en forme
(`E3-<nom>-illustre.svg`) aux textes du générateur, qui sont ceux vérifiés contre le code.

Le générateur reste la source des textes ; le `.drawio` et le `.svg` générés restent les fichiers à corriger ; la
mise en forme d'Era est l'image publiée, rendue en PNG depuis son SVG.
"""
import html
import importlib.util
import re
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).parent.parent
DOSSIER = RACINE / "docs/rapports/E3/schemas"
NOMS = ("E3-architecture", "E3-integration-briefing", "E3-monitorage", "E3-strategie-tests", "E3-chaine-livraison")
# Étiquettes de flèche que la mise en forme peut ajouter : vraies, retirées du générateur seulement parce qu'elles
# chevauchaient une boîte dans SA disposition (24/10).
ETIQUETTES_PERMISES = {"lit", "fusion relue", "livrer <empreinte>", "Légende"}


@pytest.fixture(scope="module")
def gen():
    chemin = DOSSIER / "generer_schemas.py"
    spec = importlib.util.spec_from_file_location("schemas_e3_test", chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules["schemas_e3_test"] = module   # dataclass relit son module dans sys.modules
    spec.loader.exec_module(module)
    return module


def _norme(texte: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(texte).replace("’", "'").replace(" ", " ")).strip()


def _textes_attendus(schema) -> list[str]:
    textes = [schema.titre, schema.sous_titre, schema.legende]
    for b in schema.boites:
        textes += [b.titre, *b.lignes]
    textes += [f.etiquette for f in schema.fleches if f.etiquette]
    textes += [*schema.cles_boites.values(), *schema.cles_fleches.values()]
    return [_norme(t) for t in textes]


def _textes_et_tailles(svg: str) -> list[tuple[str, float | None]]:
    """(texte, taille) de chaque <text>, ou de chaque <tspan> quand le texte en a."""
    sortie = []
    for attributs, contenu in re.findall(r"<text\b([^>]*)>(.*?)</text>", svg, re.S):
        taille = re.search(r'font-size="([\d.]+)', attributs)
        taille = float(taille.group(1)) if taille else None
        morceaux = re.findall(r"<tspan\b([^>]*)>(.*?)</tspan>", contenu, re.S) or [("", contenu)]
        for a, c in morceaux:
            t = re.search(r'font-size="([\d.]+)', a)
            sortie.append((_norme(re.sub(r"<[^>]+>", "", c)), float(t.group(1)) if t else taille))
    return [(t, s) for t, s in sortie if t]


def _illustre(nom: str) -> str:
    chemin = DOSSIER / f"{nom}-illustre.svg"
    assert chemin.exists(), f"{chemin.name} absent : la mise en forme publiée n'a pas sa source"
    return chemin.read_text(encoding="utf-8")


@pytest.mark.parametrize("nom", NOMS)
@pytest.mark.parametrize("fichier", ("{}.drawio", "{}.svg", "{}.png", "{}-illustre.svg"))
def test_chaque_schema_a_sa_source_et_son_image(nom, fichier):
    """Règle du dépôt : un .drawio pour corriger, une image pour voir ; et la source de l'image publiée."""
    assert (DOSSIER / fichier.format(nom)).exists(), fichier.format(nom)


@pytest.mark.parametrize("nom", NOMS)
def test_le_fichier_genere_range_est_celui_que_produit_le_generateur(gen, nom):
    schema = {s.nom: s for s in gen.SCHEMAS}[nom]
    assert (DOSSIER / f"{nom}.svg").read_text(encoding="utf-8") == gen.svg(schema), \
        f"{nom}.svg n'est plus à jour : relancer generer_schemas.py"
    assert (DOSSIER / f"{nom}.drawio").read_text(encoding="utf-8") == gen.drawio(schema)


def test_aucun_texte_genere_ne_deborde_de_sa_boite(gen):
    assert [d for s in gen.SCHEMAS for d in gen.debordements(s)] == []


@pytest.mark.parametrize("nom", NOMS)
def test_la_mise_en_forme_dit_exactement_les_textes_du_generateur(gen, nom):
    schema = {s.nom: s for s in gen.SCHEMAS}[nom]
    attendus = _textes_attendus(schema)
    presents = [t for t, _ in _textes_et_tailles(_illustre(nom))]
    assert [a for a in attendus if a not in presents] == [], "texte du générateur absent de la mise en forme"
    assert [t for t in presents if t not in attendus and t not in ETIQUETTES_PERMISES] == [], \
        "texte de la mise en forme que le générateur ne dit pas"


@pytest.mark.parametrize("nom", NOMS)
def test_la_mise_en_forme_ne_charge_rien_et_n_execute_rien(nom):
    svg = _illustre(nom)
    interdits = re.findall(r"<script|\bon[a-z]+\s*=|javascript:|<foreignObject|<iframe|<!ENTITY|"
                           r"(?:href|src)\s*=\s*[\"']https?:", svg, re.I)
    assert interdits == []


@pytest.mark.parametrize("nom", NOMS)
def test_la_mise_en_forme_reste_lisible_une_fois_imprimee(nom):
    """Dans le rapport, une figure fait 516 points de large : sur 1440 de large, 14 px donnent 5 points imprimés."""
    svg = _illustre(nom)
    largeur, hauteur = (float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
    tailles = [s for _, s in _textes_et_tailles(svg) if s]
    assert min(tailles) >= 14 * largeur / 1440, f"texte trop petit : {min(tailles)} px sur {largeur:.0f}"
    assert hauteur / largeur <= 0.71, "plus haute qu'un A4 paysage : le rapport dépasserait 20 pages"
