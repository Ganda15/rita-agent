"""Liste les articles du corpus pour annoter le jeu d'évaluation du RAG (C17).

## Pourquoi ce script existe

L'évaluation par ablation (D0 → D1 → H0 → H1) compare des modes de recherche entre
eux. Comparer suppose une **vérité terrain** : pour chaque question, la liste des
articles qui répondent réellement. Cette liste ne se devine pas depuis le code — elle
se lit dans le corpus, article par article.

Ce script ne juge rien : il **montre** les articles annotables, avec leur identifiant.
Le choix de ce qui répond à quoi reste un acte humain — c'est lui qui donne sa valeur
à la mesure. Un jeu de questions annoté par la machine qui sera ensuite évaluée par ce
même jeu mesurerait sa propre cohérence, pas sa pertinence. *(C'est exactement le
« 100 % circulaire » du garde-fou, trouvé en veille S34.)*

## Les articles bloqués ne sont jamais listés

`bloque_injection = TRUE` marque un article porteur d'une tentative d'injection de
prompt. `rag/indexation.py` l'exclut de l'index : il ne peut donc jamais être une
bonne réponse. Le lister ici laisserait annoter une réponse que le moteur ne pourra
jamais rendre.

Usage :
    python -m scripts.lister_articles                    # les 40 plus récents
    python -m scripts.lister_articles LVMH               # ceux qui citent LVMH
    python -m scripts.lister_articles inflation taux     # OU entre les motifs
"""
from __future__ import annotations

import argparse

from psycopg2.extras import RealDictCursor

from sources.database import _connexion

# Le filtre porte sur titre ET résumé : un article peut ne citer l'entreprise que dans
# son résumé. `bloque_injection = FALSE` reprend la règle de l'index — voir plus haut.
SQL_ARTICLES = """
SELECT   id, publie_le::date AS date_publication, source, titre
FROM     article
WHERE    bloque_injection = FALSE
  AND    ({filtre})
ORDER BY publie_le DESC NULLS LAST
LIMIT    %(limite)s
"""


def lister(motifs: list[str], limite: int) -> list[dict]:
    """Rend les articles dont le titre ou le résumé contient l'un des motifs.

    Sans motif, rend les plus récents. La casse est ignorée : les titres de presse
    écrivent « LVMH », « Lvmh » et « lvmh » selon la source.
    """
    if motifs:
        filtre = " OR ".join(
            f"LOWER(titre || ' ' || COALESCE(resume, '')) LIKE %(motif{i})s"
            for i in range(len(motifs))
        )
        params = {f"motif{i}": f"%{m.lower()}%" for i, m in enumerate(motifs)}
    else:
        filtre, params = "TRUE", {}

    params["limite"] = limite
    with _connexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(SQL_ARTICLES.format(filtre=filtre), params)
            return [dict(r) for r in cur.fetchall()]


if __name__ == "__main__":
    parseur = argparse.ArgumentParser(
        description="Liste les articles du corpus, pour annoter le jeu d'évaluation du RAG"
    )
    parseur.add_argument("motifs", nargs="*", help="mots à chercher dans le titre ou le résumé")
    parseur.add_argument("--limite", type=int, default=100)
    args = parseur.parse_args()

    lignes = lister(args.motifs, args.limite if args.motifs else min(args.limite, 40))

    if args.motifs:
        print(f"=== ARTICLES CITANT : {' OU '.join(args.motifs)} ===")
    else:
        print("=== LES ARTICLES LES PLUS RECENTS ===")
    print(f"{'id':>5} | {'date':<10} | {'source':<20} | titre")
    print("-" * 110)
    for l in lignes:
        titre = (l["titre"] or "")[:70]
        print(f"{l['id']:>5} | {l['date_publication']} | {(l['source'] or '')[:20]:<20} | {titre}")
    print("-" * 110)
    print(f"{len(lignes)} article(s). Recopier les id dans la colonne ids_attendus.")
