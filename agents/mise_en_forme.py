"""Retire les marques de mise en forme Markdown d'un texte rédigé par le modèle (14/11/2026).

Pourquoi : l'écran du briefing affiche le texte tel quel (`textContent`, aucune interprétation du Markdown, pour qu'un
texte venu du modèle ne puisse jamais devenir du HTML). Mistral, en secours d'Azure depuis le 14/11, écrit des
marques que le lecteur voit telles quelles : `**` dans 30 briefings sur 30 au banc C7 du 07/11, et « *BFM Bourse* »
observé en production le 14/11.

Ce qui est retiré, et seulement cela : une marque d'emphase **appariée sur la même ligne** (`**x**`, `__x__`, `*x*`)
et un `#` de titre en début de ligne. Une marque appariée colle au mot qu'elle entoure ; un astérisque entouré
d'espaces (« 5 * 3 ») ou isolé reste, comme un tiret bas dans un mot (`rita_lecture`). Les nombres, les citations
`[n]`, les paragraphes et les tirets de liste ne sont pas touchés.
"""
import re

# `**x**` et `__x__` : le contenu ne commence ni ne finit par une espace et ne traverse pas une ligne.
_GRAS = re.compile(r"(\*\*|__)(?=\S)([^\n]*?\S)\1")
# `*x*` : un seul astérisque de chaque côté (pas un morceau de `**`), collé au mot qu'il entoure.
_ITALIQUE = re.compile(r"(?<![*\w])\*(?=[^\s*])([^*\n]*?[^\s*])\*(?![*\w])")
# `#` à `######` suivis d'une espace, en début de ligne.
_TITRE = re.compile(r"^#{1,6}[ \t]+", flags=re.MULTILINE)


def sans_marques_markdown(texte: str) -> str:
    """Le même texte, sans les marques d'emphase appariées ni les `#` de titre en début de ligne."""
    texte = _GRAS.sub(r"\2", texte)
    texte = _ITALIQUE.sub(r"\1", texte)
    return _TITRE.sub("", texte)
