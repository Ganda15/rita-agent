"""Extraction par scraping HTML d'une page de cotation (C1 — page web).

Cinquième source de RITA, et la seule qui couvre le type **« page web (scraping) »** exigé
par C1. Cible : les pages `/cours/<symbole>/` de Boursorama, rendues côté serveur.

Trois choses distinguent cette source des quatre autres :

1. **On n'a aucun contrat.** Une API publie un schéma et le fait vivre. Une page HTML peut
   changer de structure du jour au lendemain, sans préavis. Le code doit donc échouer
   *bruyamment* quand un sélecteur ne répond plus — un scraper qui retourne silencieusement
   `None` pollue la base sans qu'on le voie.

2. **On doit demander la permission.** `robots.txt` est vérifié **avant** toute requête.
   C'est l'« identification des contraintes techniques propres aux sources de données, dont
   les règles de confidentialité » que demande C1, et c'est aussi la seule attitude
   défendable.

3. **Le contenu est hostile par défaut.** Toute chaîne extraite d'une page tierce passe par
   `guardrails/injection.py` avant de pouvoir approcher un LLM.

Contraintes constatées le 31/07/2026 en testant les cibles possibles :
    - AMF (actualites)          -> HTTP 200 mais liste **rendue en JavaScript**, absente de
                                   l'HTML : inexploitable sans navigateur headless
    - Wikipédia FR              -> HTTP 403 sur requête programmatique simple
    - Zonebourse / Boursier     -> HTTP 403 (anti-bot)
    - Boursorama /cours/        -> HTTP 200, HTML statique, robots.txt autorise  ✅

Usage :
    python -m sources.scraper
"""
from __future__ import annotations

import logging
import re
import urllib.robotparser as robotparser
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from guardrails.injection import neutraliser

logger = logging.getLogger(__name__)

BASE = "https://www.boursorama.com/cours/{symbole}/"
DELAI_S = 20.0

# Symbole Boursorama -> ticker Yahoo. Les deux sources n'emploient pas les mêmes
# identifiants : `1rPMC` chez Boursorama, `MC.PA` chez Yahoo. Cette table est la clé de
# rapprochement — sans elle, les cours scrapés ne peuvent rejoindre l'historique en base.
SYMBOLES = {
    "1rPMC": "MC.PA",     # LVMH
    "1rPOR": "OR.PA",     # L'Oreal
    "1rPAI": "AI.PA",     # Air Liquide
}

# Sélecteurs CSS -> champ. En configuration : quand Boursorama change son HTML,
# on corrige ici, pas dans la logique (standard Velmo 2.0, point 7).
SELECTEURS = {
    "dernier": ".c-instrument--last",
    "variation": ".c-instrument--variation",
    "ouverture": ".c-instrument--open",
    "haut": ".c-instrument--high",
    "bas": ".c-instrument--low",
    "cloture_veille": ".c-instrument--previousclose",
    "volume": ".c-instrument--totalvolume",
}

CHAMPS_OBLIGATOIRES = ("dernier", "ouverture", "haut", "bas")


class StructurePageModifiee(RuntimeError):
    """La page ne contient plus les éléments attendus — le scraper doit être corrigé.

    Levée volontairement plutôt que de retourner des `None` : une panne de scraper doit
    être visible immédiatement, pas se diluer dans les données.
    """


@dataclass
class Cotation:
    """Une cotation extraite par scraping."""
    symbole: str
    nom: str
    isin: str
    place: str
    dernier: float | None
    variation_pct: float | None
    ouverture: float | None
    haut: float | None
    bas: float | None
    cloture_veille: float | None
    volume: int | None
    collecte_le: str
    champs_absents: list[str] = field(default_factory=list)
    motifs_injection: list[str] = field(default_factory=list)


@lru_cache(maxsize=16)
def _lecteur_robots(racine: str) -> robotparser.RobotFileParser | None:
    """Télécharge et met en cache le robots.txt d'un domaine.

    Le cache évite de retélécharger robots.txt à chaque page scrapée : sans lui, scraper
    50 valeurs déclenche 50 requêtes inutiles sur le même fichier. C'est autant une
    question de politesse envers le site que de latence.
    """
    try:
        reponse = httpx.get(f"{racine}/robots.txt", timeout=10.0, follow_redirects=True)
        lecteur = robotparser.RobotFileParser()
        lecteur.parse(reponse.text.splitlines())
        return lecteur
    except Exception as erreur:                              # noqa: BLE001
        logger.warning("robots.txt illisible sur %s (%s)", racine, erreur)
        return None


def scraping_autorise(url: str, agent: str = "*") -> bool:
    """Vérifie robots.txt AVANT la requête. En cas de doute, on s'abstient."""
    partie = urlparse(url)
    lecteur = _lecteur_robots(f"{partie.scheme}://{partie.netloc}")
    if lecteur is None:
        return False                                          # abstention par défaut
    return lecteur.can_fetch(agent, url)


def _nombre(texte: str | None) -> float | None:
    """Convertit un nombre au format français en float.

    « 475,15 » -> 475.15   ·   « 429 187 » -> 429187.0   ·   « +0,39% » -> 0.39
    Les espaces insécables (\\xa0) des milliers sont fréquents dans l'HTML français.
    """
    if not texte:
        return None
    propre = (texte.replace("\xa0", "").replace(" ", "")
              .replace(" ", "").replace("%", "").replace(",", "."))
    trouve = re.search(r"[-+]?\d*\.?\d+", propre)
    return float(trouve.group()) if trouve else None


def extraire(html: bytes, symbole: str) -> Cotation:
    """Parse l'HTML d'une page de cotation.

    Raises:
        StructurePageModifiee: si aucun champ obligatoire n'est trouvé.
    """
    soupe = BeautifulSoup(html, "lxml")

    valeurs, absents = {}, []
    for champ, selecteur in SELECTEURS.items():
        element = soupe.select_one(selecteur)
        if element is None:
            absents.append(champ)
            valeurs[champ] = None
        else:
            valeurs[champ] = _nombre(element.get_text(strip=True))

    if all(champ in absents for champ in CHAMPS_OBLIGATOIRES):
        raise StructurePageModifiee(
            f"Aucun champ obligatoire trouve pour {symbole}. "
            f"Selecteurs a revoir : {list(SELECTEURS.values())}"
        )

    titre_el = soupe.select_one("a.c-faceplate__company-link, h1")
    isin_el = soupe.select_one(".c-faceplate__isin")
    place_el = soupe.select_one(".c-faceplate__real-time")

    nom = titre_el.get_text(" ", strip=True) if titre_el else ""
    isin_brut = isin_el.get_text(" ", strip=True) if isin_el else ""
    place = place_el.get_text(" ", strip=True) if place_el else ""

    # Garde-fou OUTILS : ces trois chaînes viennent d'une page tierce et finiront
    # dans le contexte du Rédacteur. Elles sont contrôlées avant tout usage.
    verdict = neutraliser(f"{nom}\n{isin_brut}\n{place}", source=f"scraping:{symbole}")

    isin = isin_brut.split()[0] if isin_brut else ""

    return Cotation(
        symbole=symbole,
        nom=nom,
        isin=isin,
        place=place,
        dernier=valeurs["dernier"],
        variation_pct=valeurs["variation"],
        ouverture=valeurs["ouverture"],
        haut=valeurs["haut"],
        bas=valeurs["bas"],
        cloture_veille=valeurs["cloture_veille"],
        volume=int(valeurs["volume"]) if valeurs["volume"] is not None else None,
        collecte_le=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        champs_absents=absents,
        motifs_injection=verdict["motifs_detectes"],
    )


def recuperer(symbole: str) -> Cotation:
    """Scrape une page de cotation, robots.txt vérifié au préalable."""
    url = BASE.format(symbole=symbole)

    if not scraping_autorise(url):
        raise PermissionError(f"robots.txt interdit le scraping de {url}")

    reponse = httpx.get(url, timeout=DELAI_S, follow_redirects=True)
    reponse.raise_for_status()
    return extraire(reponse.content, symbole)


def collecter() -> dict:
    """Scrape tous les symboles configurés, sans qu'un échec emporte les autres."""
    cotations, echecs = [], []
    for symbole, nom in SYMBOLES.items():
        try:
            cotations.append(recuperer(symbole))
        except Exception as erreur:                          # noqa: BLE001
            logger.warning("Scraping %s (%s) echoue — %s", symbole, nom, erreur)
            echecs.append((symbole, nom, f"{type(erreur).__name__}: {erreur}"[:80]))
    return {"cotations": cotations, "echecs": echecs}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    r = collecter()

    print("\n=== SCRAPING HTML — pages de cotation ===")
    print(f"Recuperees : {len(r['cotations'])}/{len(SYMBOLES)}")

    for c in r["cotations"]:
        print(f"\n  {c.nom}  ({c.isin})")
        print(f"    place       : {c.place}")
        print(f"    dernier     : {c.dernier}   variation : {c.variation_pct} %")
        print(f"    O/H/L       : {c.ouverture} / {c.haut} / {c.bas}")
        print(f"    veille      : {c.cloture_veille}   volume : {c.volume:,}"
              if c.volume else f"    veille      : {c.cloture_veille}")
        print(f"    collecte le : {c.collecte_le}")
        if c.champs_absents:
            print(f"    !! champs absents : {c.champs_absents}")
        if c.motifs_injection:
            print(f"    !! INJECTION detectee : {c.motifs_injection}")

    for symbole, nom, cause in r["echecs"]:
        print(f"\n  !! ECHEC {symbole} ({nom}) : {cause}")
