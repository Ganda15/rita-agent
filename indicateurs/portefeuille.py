"""Indicateurs de marché — lot 2 « portefeuille ».

Spécification : `docs/indicateurs/CONCEPTION.md` §6
Requêtes      : `db/indicateurs_portefeuille.sql`
Livrable      : E4 — alimente l'écran 2.

⚠️ **DONNÉES PERSONNELLES (RGPD).** `position` porte la situation financière de
l'utilisateur. Ces indicateurs héritent du traitement **T1** du registre
(`db/RGPD-registre-des-traitements.md`) : destinataire unique, purge déjà testée.
**Aucun nouveau traitement à déclarer** — vérifié, pas supposé.

⚠️ **Des indicateurs, jamais des stratégies.** Un poids de 34,83 % est un **fait**.
« Vous êtes trop concentré, allégez » serait un **conseil**, et l'interdit AMF le
proscrit. Aucun seuil d'alerte, aucun classement « à surveiller ».

**Pourquoi ce lot compte plus que le socle** : les indicateurs du lot 1 décrivent des
*instruments*, ce que fait n'importe quel site de cotations. Ceux-ci décrivent **le
portefeuille** — ses lignes, ses devises. C'est la réponse à « qu'est-ce qui est
spécifique à votre projet ? ».
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

# ⚠️ On importe le MODULE, pas les fonctions.
#
# `from indicateurs.socle import _executer` copierait la référence dans l'espace de
# noms de ce module au moment de l'import. Remplacer `socle._executer` dans un test
# n'aurait alors aucun effet ici : les deux noms pointeraient sur des objets
# différents. Constaté le 19/08/2026 — quatre tests recevaient les VRAIES données de
# la base au lieu du jeu simulé, et passaient donc à côté de leur sujet.
#
# Appeler `socle._executer(...)` résout le nom **à chaque appel**, donc après le
# remplacement.
from indicateurs import socle

_REQUETES = Path(__file__).parent.parent / "db" / "indicateurs_portefeuille.sql"

# Les requêtes du fichier SQL sont repérées par `-- @@REQUETE <nom>`, et non
# découpées sur le point-virgule : un `;` peut apparaître dans une chaîne ou un
# commentaire. Un séparateur qui peut apparaître dans le contenu n'en est pas un.
_MARQUEUR = re.compile(r"^--\s*@@REQUETE\s+(\w+)\s*$", re.MULTILINE)


def _charger_requetes() -> dict[str, str]:
    """Retourne {nom: sql} d'après les marqueurs du fichier."""
    texte = _REQUETES.read_text(encoding="utf-8")
    bornes = [(m.group(1), m.end()) for m in _MARQUEUR.finditer(texte)]
    if not bornes:
        raise RuntimeError(f"Aucun marqueur @@REQUETE dans {_REQUETES}")

    requetes: dict[str, str] = {}
    for i, (nom, debut) in enumerate(bornes):
        fin = bornes[i + 1][1] - len(f"-- @@REQUETE {bornes[i + 1][0]}") if i + 1 < len(bornes) else len(texte)
        requetes[nom] = texte[debut:fin].strip().rstrip(";")
    return requetes


@dataclass(frozen=True)
class LignePortefeuille:
    """Une ligne détenue, avec son poids dans le total."""

    ticker: str
    nom_officiel: str
    devise: str
    quantite: float | None
    valorisation_eur: float | None
    poids_pct: float | None

    def en_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExpositionDevise:
    """L'exposition du portefeuille à une devise.

    ⚠️ **Exposition de cotation, pas exposition économique.** Cet indicateur dit dans
    quelle monnaie les titres sont *cotés*. LVMH est cotée en euros mais réalise une
    part importante de son chiffre d'affaires en dollars : un portefeuille « 100 %
    EUR » selon cet indicateur peut être fortement exposé au dollar dans les faits.

    La distinction est écrite ici parce que, sans elle, le chiffre se lit de travers.
    """

    devise: str
    nb_lignes: int
    valorisation_eur: float | None
    exposition_pct: float | None

    def en_dict(self) -> dict[str, Any]:
        return asdict(self)


def lire_poids() -> tuple[list[LignePortefeuille], float | None]:
    """Le poids de chaque ligne, et le total du portefeuille en euros.

    Le total est rendu **avec** les lignes plutôt que recalculé par l'appelant :
    additionner soi-même des `valorisation_eur` reviendrait à refaire le calcul que
    la vue a déjà fait, et deux calculs de la même chose finissent par diverger.
    """
    lignes = socle._executer(_charger_requetes()["poids"])
    total = socle._nombre(lignes[0]["total_eur"]) if lignes else None
    return [
        LignePortefeuille(
            ticker=l["ticker"],
            nom_officiel=l["nom_officiel"],
            devise=l["devise"],
            quantite=socle._nombre(l["quantite"]),
            valorisation_eur=socle._nombre(l["valorisation_eur"]),
            poids_pct=socle._nombre(l["poids_pct"]),
        )
        for l in lignes
    ], total


def lire_exposition() -> list[ExpositionDevise]:
    """L'exposition par devise de cotation."""
    return [
        ExpositionDevise(
            devise=l["devise"],
            nb_lignes=int(l["nb_lignes"]),
            valorisation_eur=socle._nombre(l["valorisation_eur"]),
            exposition_pct=socle._nombre(l["exposition_pct"]),
        )
        for l in socle._executer(_charger_requetes()["exposition"])
    ]


if __name__ == "__main__":
    lignes, total = lire_poids()
    expositions = lire_exposition()

    print("=" * 74)
    print("INDICATEURS - LOT 2 (portefeuille)")
    print("=" * 74)
    print(f"  {len(lignes)} ligne(s) · total {total:,.2f} EUR".replace(",", " "))
    print()
    print(f"  {'ticker':<10} {'nom':<24} {'valorisation':>13} {'poids':>8}")
    print("  " + "-" * 58)
    for l in lignes:
        print(f"  {l.ticker:<10} {l.nom_officiel[:24]:<24} "
              f"{l.valorisation_eur:>13,.2f} {l.poids_pct:>7.2f} %".replace(",", " "))

    somme = sum(l.poids_pct or 0 for l in lignes)
    print("  " + "-" * 58)
    print(f"  {'':<10} {'SOMME DES POIDS':<24} {'':>13} {somme:>7.2f} %")

    print()
    print("  Exposition par devise DE COTATION (pas economique) :")
    for e in expositions:
        print(f"    {e.devise}  {e.nb_lignes} ligne(s)  "
              f"{e.valorisation_eur:>12,.2f} EUR  {e.exposition_pct:>6.2f} %".replace(",", " "))
