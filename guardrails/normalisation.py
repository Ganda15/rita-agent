"""Normalisation commune aux garde-fous : ce que les règles lisent, et ce que le modèle reçoit (constat S9, 07/11/2026).

Pourquoi : une expression régulière ne lit pas « ign<espace de largeur nulle>ore » comme « ignore », ni « Ｉｇｎｏｒｅ »
(pleine chasse) ; un modèle de langage, si. Revue de sécurité automatique du 07/11, go d'Era (« Injection + sortie »),
périmètre fixé par la relecture d'un autre agent.

Deux usages, jamais mélangés :

- `textes_de_controle` : des COPIES pour la détection seule (injection, sortie AMF, fuite). La forme NFKC y ramène la
  pleine chasse et les ligatures à leurs lettres ordinaires. Elle change aussi le sens de certains caractères (« 10⁶ »
  devient « 106 », recommandation d'Unicode, UAX #15) : c'est pourquoi elle ne s'applique jamais au texte conservé, ni
  au texte envoyé au modèle, ni au texte montré au lecteur.
- `sans_invisibles` : le texte envoyé au modèle. On retire seulement les caractères de la catégorie Unicode Cf
  (« format ») : ils ne s'affichent pas et n'ont aucun rôle dans un article de presse financière ou une question de
  lecteur. Les principaux : U+00AD trait d'union conditionnel (« &shy; » du HTML), U+200B espace de largeur nulle,
  U+200C et U+200D antiliant et liant sans chasse, U+200E et U+200F marques de sens, U+202A à U+202E et U+2066 à U+2069
  contrôles bidirectionnels, U+2060 gluon de mots, U+FEFF indicateur d'ordre des octets, U+E0001 à U+E007F caractères
  d'étiquette (une phrase entière peut y être écrite, invisible à l'écran). Tout le reste du texte est inchangé.
"""
import re
import unicodedata

_ESPACES = re.compile(r"\s+")


def _est_invisible(caractere: str) -> bool:
    return unicodedata.category(caractere) == "Cf"


def sans_invisibles(texte: str) -> str:
    """Le texte sans ses caractères de la catégorie Unicode Cf, le reste à l'identique."""
    return "".join(c for c in texte if not _est_invisible(c))


def textes_de_controle(texte: str) -> tuple[str, ...]:
    """Les versions du texte que les règles lisent, sans doublon : l'original (les règles qui dépendent des sauts de
    ligne le lisent tel quel), puis deux copies normalisées (NFKC, espaces ramenés à un seul).

    Deux copies parce qu'un caractère invisible sert à deux choses : couper un mot (« ign·ore », il faut le retirer)
    ou séparer deux mots (« ignore·previous », il faut une espace à sa place).
    """
    retire = "".join(c for c in texte if not _est_invisible(c))
    espace = "".join(" " if _est_invisible(c) else c for c in texte)
    copies = (texte,) + tuple(_ESPACES.sub(" ", unicodedata.normalize("NFKC", t)) for t in (retire, espace))
    return tuple(dict.fromkeys(copies))
