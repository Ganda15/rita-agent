"""Contrôle des NOMBRES d'une réponse : chacun doit figurer dans un des articles cités (sprint 4, après le rejeu en
production du 20/10/2026).

**Pourquoi.** Q4 a été servie en production avec « 1 0 postes » pour un passage qui dit « 1 000 postes ». La cause
exacte n'est pas établie : le passage stocké en production est le même qu'en local, et 22 essais locaux sur 22 étaient
justes ; le chiffre s'abîme dans la réponse du modèle, rarement. Un chiffre faux sous une source juste est le pire cas
pour un lecteur : il croit vérifiée une information qui ne l'est pas. Le contrôle ne cherche pas la cause, il vérifie
le résultat avant qu'il soit servi.

**Comment.** Toutes les espaces Unicode (catégorie Zs : ordinaire, insécable, fine...) sont ramenées à une espace
simple, dans la réponse comme dans les sources ; les numéros de citation « [1] » sont retirés. Un nombre est une suite
de chiffres, avec ses groupes séparés par une espace et sa partie décimale après une virgule (« 1 000 », « 0,5 »,
« 2027 »). Il doit apparaître ENTIER dans les sources : « 1 00 » ne vaut pas « 1 000 », ni « 0,55 » « 0,5 ».

**Limite connue et acceptée.** Une réponse qui reformule un chiffre (« mille » pour « 1 000 ») ou qui en calcule un est
refusée, même juste ; une réponse qui écrit un chiffre en lettres n'est pas contrôlée.
"""
import re
import unicodedata

MESSAGE_REFUS_NOMBRE = ("La réponse produite contenait un chiffre absent des articles cités : elle n'est pas "
                        "affichée.")

_CITATION = re.compile(r"\[\d+\]")
_NOMBRE = re.compile(r"\d+(?: \d+)*(?:,\d+)?")


def espaces_simples(texte: str) -> str:
    """Toutes les espaces Unicode deviennent une espace simple, et chaque suite d'espaces une seule."""
    return " ".join("".join(" " if unicodedata.category(c) == "Zs" else c for c in texte).split())


def nombres_absents(texte: str, sources: list[str]) -> list[str]:
    """Les nombres de `texte` qui ne figurent dans aucune des `sources`, dans leur ordre d'apparition, sans doublon."""
    reference = " ".join(espaces_simples(source) for source in sources)
    absents: list[str] = []
    for nombre in _NOMBRE.findall(_CITATION.sub(" ", espaces_simples(texte))):
        # Le nombre entier : ni chiffre ni virgule devant ; ni chiffre, ni décimale, ni groupe de chiffres derrière.
        entier = r"(?<![\d,])" + re.escape(nombre) + r"(?!\d|,\d| \d)"
        if not re.search(entier, reference) and nombre not in absents:
            absents.append(nombre)
    return absents
