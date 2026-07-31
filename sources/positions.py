"""Lecture du portefeuille depuis un fichier CSV (C1 — fichier de données · C3 — nettoyage).

Sixième et dernière source du pipeline principal. Elle couvre le type **« fichier de
données »** exigé par C1, et c'est aussi celle qui donne son sens au produit : sans les
positions, RITA commente le marché ; avec elles, il commente **le** portefeuille.

## ⚠️ Données personnelles

Le fichier réel contient les quantités et les prix de revient d'Era — une information
financière personnelle. Il n'est **jamais** versionné (`.gitignore`). Le dépôt ne contient
que `data/positions-exemple.csv`, anonymisé, qui sert aux tests et aux démonstrations.

Le chemin du fichier réel se donne par variable d'environnement :

    POSITIONS_CSV=D:\\chemin\\vers\\mon-portefeuille.csv

C'est aussi ce qui rend le script reproductible par le jury : il tourne sur l'exemple,
sans jamais exposer de données personnelles.

## Pourquoi ce lecteur est plus qu'un `pd.read_csv`

Un export de courtier français cumule quatre pièges, et chacun casse un `read_csv` naïf :

1. **Séparateur `;`** — Excel FR l'utilise, parce que la virgule est déjà la décimale
2. **Encodage `cp1252`** — pas UTF-8 : les accents sortent en `Ã©` si on ne détecte pas
3. **Nombres à la française** — `632,40` et `1 250` (espace insécable pour les milliers)
4. **En-têtes instables** — « Quantité », « Qté », « Nombre de titres » selon le courtier

Usage :
    python -m sources.positions
"""
from __future__ import annotations

import csv
import logging
import os
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

RACINE = Path(__file__).resolve().parent.parent
EXEMPLE = RACINE / "data" / "positions-exemple.csv"

# Synonymes d'en-têtes rencontrés selon les courtiers (Boursorama, Bourse Direct,
# Saxo, exports Excel manuels). En configuration : un nouvel export = une ligne ici,
# pas une modification de la logique.
SYNONYMES = {
    "ticker": ["ticker", "symbole", "code valeur", "mnemo", "mnemonique", "symbol"],
    "nom": ["libelle", "nom", "valeur", "designation", "intitule", "name", "description"],
    "isin": ["code isin", "isin", "code"],
    "quantite": ["quantite", "qte", "nombre de titres", "nb titres", "nombre",
                 "quantity", "shares", "qty"],
    "pru": ["prix de revient", "pru", "prix d'achat", "prix de revient unitaire",
            "cours d'achat", "prix unitaire", "average cost", "cost basis", "avg price"],
    "devise": ["devise", "monnaie", "currency"],
    "date_achat": ["date d'achat", "date achat", "date", "date d'operation",
                   "purchase date", "trade date"],
}

ENCODAGES = ("utf-8-sig", "utf-8", "cp1252", "latin-1")


@dataclass
class Position:
    """Une ligne de portefeuille, validée."""
    ticker: str
    nom: str
    isin: str
    quantite: float
    pru: float
    devise: str
    date_achat: str

    @property
    def montant_investi(self) -> float:
        """Ce que la position a coûté. La valorisation exige un cours — ce n'est pas
        le rôle de cette source (séparation des responsabilités)."""
        return round(self.quantite * self.pru, 2)


@dataclass
class Rejet:
    """Une ligne écartée, avec sa cause. Traçabilité C3 : on n'efface pas en silence."""
    ligne: int
    contenu: dict
    cause: str


@dataclass
class Portefeuille:
    positions: list[Position] = field(default_factory=list)
    rejets: list[Rejet] = field(default_factory=list)
    devises: set[str] = field(default_factory=set)

    @property
    def montant_total(self) -> float:
        """⚠️ Somme brute, toutes devises confondues — n'a de sens qu'en mono-devise.
        La conversion passe par `sources/ecb.py` (taux du jour), en aval."""
        return round(sum(p.montant_investi for p in self.positions), 2)


def _normaliser(entete: str) -> str:
    """« Prix de Revient » -> « prix de revient » ; « Quantité » -> « quantite »."""
    sans_accent = "".join(
        c for c in unicodedata.normalize("NFD", entete)
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"\s+", " ", sans_accent).strip().lower()


def _detecter_encodage(chemin: Path) -> str:
    """Renvoie le premier encodage qui lit le fichier sans erreur."""
    for encodage in ENCODAGES:
        try:
            chemin.read_text(encoding=encodage)
            return encodage
        except (UnicodeDecodeError, LookupError):
            continue
    raise UnicodeDecodeError(
        "positions", b"", 0, 1, f"aucun encodage connu ne lit {chemin.name}"
    )


def _detecter_separateur(echantillon: str) -> str:
    """`;` pour Excel FR, `,` pour un export anglo-saxon, `\\t` pour un copier-coller."""
    try:
        return csv.Sniffer().sniff(echantillon, delimiters=";,\t").delimiter
    except csv.Error:
        # Repli : on compte. Le séparateur le plus fréquent sur la 1re ligne gagne.
        premiere = echantillon.splitlines()[0] if echantillon else ""
        return max(";,\t", key=premiere.count)


def _associer_colonnes(entetes: list[str]) -> dict[str, str]:
    """Associe les en-têtes réels aux champs canoniques, via les synonymes."""
    normalises = {_normaliser(e): e for e in entetes}
    correspondance = {}
    for champ, variantes in SYNONYMES.items():
        for variante in variantes:
            if variante in normalises:
                correspondance[champ] = normalises[variante]
                break
    return correspondance


def _nombre_fr(texte: str | None) -> float | None:
    """« 632,40 » -> 632.4  ·  « 1 250 » -> 1250.0  ·  « » -> None."""
    if texte is None:
        return None
    propre = (texte.replace("\xa0", "").replace(" ", "")
              .replace(" ", "").replace("€", "").replace(",", ".").strip())
    if not propre:
        return None
    try:
        return float(propre)
    except ValueError:
        return None


def lire(chemin: Path | str | None = None) -> Portefeuille:
    """Lit un CSV de positions, valide chaque ligne, trace les rejets.

    Args:
        chemin: fichier à lire. Par défaut $POSITIONS_CSV, sinon l'exemple anonymisé.
    """
    if chemin is None:
        chemin = os.getenv("POSITIONS_CSV") or EXEMPLE
    chemin = Path(chemin)

    if not chemin.exists():
        raise FileNotFoundError(f"Fichier de positions introuvable : {chemin}")

    encodage = _detecter_encodage(chemin)
    contenu = chemin.read_text(encoding=encodage)
    separateur = _detecter_separateur(contenu[:2048])
    logger.info("Lecture %s (encodage=%s, separateur=%r)",
                chemin.name, encodage, separateur)

    lecteur = csv.DictReader(contenu.splitlines(), delimiter=separateur)
    entetes = lecteur.fieldnames or []
    colonnes = _associer_colonnes(entetes)

    manquants = [c for c in ("ticker", "quantite", "pru") if c not in colonnes]
    if manquants:
        raise ValueError(
            f"Colonnes obligatoires introuvables : {manquants}. "
            f"En-tetes du fichier : {entetes}"
        )

    portefeuille = Portefeuille()

    for numero, ligne in enumerate(lecteur, start=2):     # ligne 1 = en-têtes
        def champ(nom: str, defaut: str = "") -> str:
            colonne = colonnes.get(nom)
            return (ligne.get(colonne) or defaut).strip() if colonne else defaut

        ticker = champ("ticker")
        quantite = _nombre_fr(champ("quantite"))
        pru = _nombre_fr(champ("pru"))

        # --- Validation C3 : identification des entrées corrompues ---
        if not ticker:
            portefeuille.rejets.append(Rejet(numero, dict(ligne), "ticker absent"))
            continue
        if quantite is None:
            portefeuille.rejets.append(Rejet(numero, dict(ligne), "quantite illisible"))
            continue
        if quantite <= 0:
            portefeuille.rejets.append(
                Rejet(numero, dict(ligne), f"quantite nulle ou negative ({quantite})"))
            continue
        if pru is None:
            portefeuille.rejets.append(Rejet(numero, dict(ligne), "prix de revient absent"))
            continue
        if pru <= 0:
            portefeuille.rejets.append(
                Rejet(numero, dict(ligne), f"prix de revient invalide ({pru})"))
            continue

        devise = champ("devise", "EUR").upper() or "EUR"
        portefeuille.devises.add(devise)
        portefeuille.positions.append(Position(
            ticker=ticker,
            nom=champ("nom"),
            isin=champ("isin"),
            quantite=quantite,
            pru=pru,
            devise=devise,
            date_achat=champ("date_achat"),
        ))

    if portefeuille.rejets:
        logger.warning("%d ligne(s) rejetee(s) sur %d",
                       len(portefeuille.rejets),
                       len(portefeuille.positions) + len(portefeuille.rejets))

    return portefeuille


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = lire()

    print("\n=== PORTEFEUILLE ===")
    print(f"Positions retenues : {len(p.positions)}")
    print(f"Lignes rejetees    : {len(p.rejets)}")
    print(f"Devises            : {sorted(p.devises)}")

    print(f"\n{'Ticker':<10} {'Nom':<22} {'Qte':>7} {'PRU':>10} {'Investi':>12}  Dev")
    print("-" * 70)
    for pos in p.positions:
        print(f"{pos.ticker:<10} {pos.nom[:22]:<22} {pos.quantite:>7.0f} "
              f"{pos.pru:>10.2f} {pos.montant_investi:>12,.2f}  {pos.devise}")

    print("-" * 70)
    print(f"{'TOTAL (brut, multi-devises)':<41} {p.montant_total:>16,.2f}")
    if len(p.devises) > 1:
        print("  !! Plusieurs devises : ce total n'a pas de sens tel quel.")
        print("     Conversion via sources/ecb.py (taux du jour) avant tout usage.")

    if p.rejets:
        print("\n=== LIGNES REJETEES (tracabilite C3) ===")
        for r in p.rejets:
            print(f"  ligne {r.ligne} : {r.cause}")
