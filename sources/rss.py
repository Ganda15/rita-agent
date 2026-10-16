"""Collecte des actualités financières par flux RSS (C1 — service web).

Quatrième source de RITA. Deux différences majeures avec yfinance et la BCE :

1. **Le contenu est du texte libre écrit par des tiers.** yfinance renvoie des nombres,
   la BCE renvoie un taux. Un flux RSS renvoie des phrases rédigées par quelqu'un qu'on ne
   contrôle pas. Ce texte finit dans le prompt du Rédacteur — donc il passe
   obligatoirement par le filtre d'injection (`guardrails/injection.py`).

2. **Aucune garantie de disponibilité.** Un flux peut disparaître, changer d'URL ou
   renvoyer du HTML d'erreur. La collecte doit donc être *tolérante aux pannes* : un flux
   mort ne doit jamais faire tomber les autres.

Usage :
    python -m sources.rss
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

import feedparser
import httpx

from guardrails.injection import neutraliser

logger = logging.getLogger(__name__)

# Flux francophones d'actualité économique et financière.
# En configuration, pas en dur dans la logique (standard Velmo 2.0, point 7).
#
# Chaque flux a été testé en direct le 31/07/2026 avant d'entrer ici.
# Écartés à cette occasion, avec leur cause — c'est l'« identification des contraintes
# techniques propres aux sources de données » demandée par C1 :
#   - Boursorama  https://www.boursorama.com/rss/actualites          -> HTTP 404 (URL morte)
#   - Les Échos   https://services.lesechos.fr/rss/...xml            -> HTTP 403 (anti-bot)
#   - Zonebourse / Boursier / ABC Bourse                             -> HTTP 403 (anti-bot)
# Un User-Agent de navigateur ne change rien sur les 403 : le blocage est délibéré.
FLUX = {
    "bfm_eco": "https://www.bfmtv.com/rss/economie/",
    "latribune": "https://www.latribune.fr/feed.xml",
    "lemonde_eco": "https://www.lemonde.fr/economie/rss_full.xml",
}

DELAI_S = 20.0

# Les flux Google News par entreprise (ajoutés le 28/08/2026, un par valeur détenue) ont
# été retirés au sprint 3 (décision D3, tâche B1, 16/10/2026) : la requête envoyait à
# Google le nom des entreprises du portefeuille. Les articles déjà collectés par ce biais
# (source `ent_...`) restent en base et dans l'index ; aucun nouveau n'est demandé. Le
# manque mesuré le 28/08 (13 % des articles citaient une valeur suivie) redevient donc
# une limite connue du corpus (`evidence/C17/preuve-rag-indexation.md`).


@dataclass
class Article:
    """Un article de presse, déjà passé au filtre d'injection."""
    source: str
    titre: str
    lien: str
    publie_le: str
    resume: str
    motifs_injection: list[str] = field(default_factory=list)
    bloque: bool = False


def _horodatage(entree) -> str:
    """Normalise la date de publication en ISO 8601 UTC (C3).

    Les flux RSS publient des dates dans des formats et fuseaux variés. On homogénéise
    ici, à la source, pour ne pas propager l'hétérogénéité dans le reste du pipeline.
    """
    parsee = entree.get("published_parsed") or entree.get("updated_parsed")
    if not parsee:
        return ""
    return datetime(*parsee[:6], tzinfo=timezone.utc).isoformat()


def _nettoyer_html(texte: str) -> str:
    """Retire les balises HTML des résumés RSS, qui en contiennent souvent."""
    from bs4 import BeautifulSoup
    return BeautifulSoup(texte or "", "lxml").get_text(" ", strip=True)


def lire_flux(nom: str, url: str, limite: int = 10) -> list[Article]:
    """Lit un flux et retourne ses articles, filtrés contre l'injection.

    Ne lève jamais : un flux indisponible retourne une liste vide et journalise.
    C'est volontaire — la panne d'une source ne doit pas interrompre la collecte.

    Note d'implémentation : on récupère le flux avec httpx **avant** de le donner à
    feedparser. `feedparser.parse(url)` accepte une URL, mais avale silencieusement les
    erreurs HTTP : un 403 ressort en flux « malformé et vide », sans jamais dire qu'on a
    été bloqué. Séparer les deux étapes rend la cause visible dans les logs.
    """
    try:
        reponse = httpx.get(url, timeout=DELAI_S, follow_redirects=True)
        reponse.raise_for_status()
    except httpx.HTTPStatusError as erreur:
        logger.warning("Flux %s — HTTP %s (source bloquante ou URL morte)",
                       nom, erreur.response.status_code)
        return []
    except Exception as erreur:                              # noqa: BLE001
        logger.warning("Flux %s injoignable — %s", nom, erreur)
        return []

    flux = feedparser.parse(reponse.content)
    if not flux.entries:
        logger.warning("Flux %s lu mais sans entrée — ignoré", nom)
        return []

    articles: list[Article] = []
    for entree in flux.entries[:limite]:
        titre = entree.get("title", "").strip()
        resume = _nettoyer_html(entree.get("summary", ""))

        # Garde-fou OUTILS : le texte vient d'un tiers, il est traité comme hostile
        # jusqu'à preuve du contraire. Titre ET résumé sont contrôlés.
        verdict = neutraliser(f"{titre}\n{resume}", source=f"rss:{nom}")

        articles.append(Article(
            source=nom,
            titre=titre,
            lien=entree.get("link", ""),
            publie_le=_horodatage(entree),
            resume=resume,
            motifs_injection=verdict["motifs_detectes"],
            bloque=verdict["bloque"],
        ))

    return articles


def collecter(limite_par_flux: int = 10) -> dict:
    """Collecte les flux configurés dans `FLUX`, et eux seuls.

    Un flux en échec n'interrompt pas les autres : `flux_echec` le signale, et la
    collecte continue.

    Returns:
        {articles, articles_bloques, flux_ok, flux_echec, total}
    """
    tous, bloques, ok, echec = [], [], [], []

    for nom, url in FLUX.items():
        articles = lire_flux(nom, url, limite_par_flux)
        if not articles:
            echec.append(nom)
            continue
        ok.append(nom)
        for a in articles:
            (bloques if a.bloque else tous).append(a)

    if bloques:
        logger.warning("%d article(s) bloqué(s) par le filtre d'injection", len(bloques))

    return {
        "articles": tous,
        "articles_bloques": bloques,
        "flux_ok": ok,
        "flux_echec": echec,
        "total": len(tous) + len(bloques),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    r = collecter()

    print("\n=== COLLECTE RSS ===")
    print(f"Flux OK      : {len(r['flux_ok'])}/{len(FLUX)}  {r['flux_ok']}")
    if r["flux_echec"]:
        print(f"Flux en echec: {r['flux_echec']}")
    print(f"Articles     : {len(r['articles'])} retenus, "
          f"{len(r['articles_bloques'])} bloques")

    for a in r["articles"][:6]:
        print(f"\n  [{a.source}] {a.publie_le[:10]}")
        print(f"  {a.titre[:95]}")

    for a in r["articles_bloques"]:
        print(f"\n  !! BLOQUE [{a.source}] motifs={a.motifs_injection}")
        print(f"     {a.titre[:95]}")
