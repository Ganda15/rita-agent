"""EcoIndex des cinq écrans de RITA, avant et après la pagination du tableau Indicateurs (C17.7), depuis les mesures Lighthouse du 07/11/2026.

Formule et tables : celles du script du 03/10 (evidence/C17/mesures-2026-10-03/outils/calcul-ecoindex.py), recopiées du
dépôt officiel cnumr/ecoindex_python, sans modification. Pour chaque écran, avec ses données :
- poids = octets réellement transférés pour les fichiers de l'interface au premier chargement (cache vide, étape 1)
  + octets transférés pour les réponses de l'API de l'écran chargé (étape 2) ;
- requêtes = LE MÊME PÉRIMÈTRE que le poids : fichiers de l'interface de l'étape 1 + réponses de l'API de l'étape 2 ;
- éléments du DOM = ceux de l'étape 2 (écran avec ses données), mesurés par Lighthouse.

Version corrigée le 07/11 au soir, après la relecture d'un autre agent du commit 1479ffe (la première version, commit
795e571, reprenait celle du 06/11) :
1. une route de l'API se reconnaît à son chemin exact (« /briefing », « /question ») ou à son répertoire
   (« /donnees/... ») : le simple préfixe classait « /briefing.html », « /briefing.js », « /question.html » et
   « /question.js » comme des routes de l'API ;
2. le poids est en ko décimaux (octets / 1000), comme le collecteur officiel
   (cnumr/EcoIndex_python, components/ecoindex/scraper/scrap.py : « size=self.all_requests.total_size / 1000 ») ;
3. les requêtes suivent le périmètre du poids (le collecteur officiel compte toutes les requêtes du chargement).

Usage : python calcul-ecoindex-2026-11-07.py <dossier avant> <dossier apres> [<fichier de sortie>]
(par défaut : ecoindex-2026-11-07-corrige.json, à côté du dossier « apres »)
"""
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

QD = [0, 47, 75, 159, 233, 298, 358, 417, 476, 537, 603, 674, 753, 843, 949, 1076, 1237, 1459, 1801, 2479, 594601]
QR = [0, 2, 15, 25, 34, 42, 49, 56, 63, 70, 78, 86, 95, 105, 117, 130, 147, 170, 205, 281, 3920]
QS = [0, 1.37, 144.7, 319.53, 479.46, 631.97, 783.38, 937.91, 1098.62, 1265.47, 1448.32, 1648.27, 1876.08, 2142.06,
      2465.37, 2866.31, 3401.59, 4155.73, 5400.08, 8037.54, 223212.26]
GRADES = [("A", 80), ("B", 70), ("C", 55), ("D", 40), ("E", 25), ("F", 10)]
ROUTES_EXACTES = {"/briefing", "/question", "/health", "/sante", "/audit"}
REPERTOIRES_API = ("/donnees/", "/sante/", "/audit/")


def est_route_api(url: str) -> bool:
    chemin = urlsplit(url).path
    return chemin in ROUTES_EXACTES or chemin.startswith(REPERTOIRES_API)


# Vérification à chaque exécution (relecture du 07/11) : les fichiers de l'interface ne sont jamais des routes.
for _fichier in ("/briefing.html", "/briefing.js", "/question.html", "/question.js", "/indicateurs.js", "/style.css?v=1"):
    assert not est_route_api(_fichier), _fichier
for _route in ("/briefing", "/question", "/donnees/indicateurs", "/donnees/cotations?ticker=MC.PA", "/health",
               "http://127.0.0.1:8001/donnees/portefeuille"):
    assert est_route_api(_route), _route


def quantile(q, v):
    for i in range(1, len(q)):
        if v < q[i]:
            return i - 1 + (v - q[i - 1]) / (q[i] - q[i - 1])
    return len(q) - 1


def score(dom, ko, req):
    return round(100 - 5 * (3 * quantile(QD, dom) + 2 * quantile(QR, req) + quantile(QS, ko)) / 6)


def grade(s):
    for g, seuil in GRADES:
        if s > seuil:
            return g
    return "G"


def ges(s):
    return round(100 * (2 + 2 * (50 - s) / 100)) / 100


def eau(s):
    return round(100 * (3 + 3 * (50 - s) / 100)) / 100


def mesurer(dossier):
    resume = json.load(open(Path(dossier) / "resume-bureau.json", encoding="utf-8"))
    sortie = {}
    for ecran in ("portefeuille", "indicateurs", "briefing", "question", "tableau-de-bord"):
        navs = [e for e in resume if e["ecran"] == ecran and e["mode_lighthouse"] == "navigation"]
        froid, donnees = navs[0], navs[-1]
        fichiers = [r for r in froid["requetes_detail"] if not est_route_api(r["url"])]
        reponses_api = [r for r in donnees["requetes_detail"] if est_route_api(r["url"])]
        statique = sum(r["octets"] or 0 for r in fichiers)
        api = sum(r["octets"] or 0 for r in reponses_api)
        ko = (statique + api) / 1000
        requetes = len(fichiers) + len(reponses_api)
        s = score(donnees["noeuds_dom"], ko, requetes)
        sortie[ecran] = {"dom": donnees["noeuds_dom"], "requetes": requetes, "ko": round(ko, 1),
                         "statique_ko": round(statique / 1000, 1), "api_ko": round(api / 1000, 1),
                         "ecoindex": s, "note": grade(s), "gco2e": ges(s), "eau_cl": eau(s),
                         "bonnes_pratiques": donnees["scores"]["bonnes_pratiques"]}
    return sortie


if __name__ == "__main__":
    sans, avec = mesurer(sys.argv[1]), mesurer(sys.argv[2])
    destination = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(sys.argv[2]).parent / "ecoindex-2026-11-07-corrige.json"
    print("| Écran | DOM avant | DOM après | Requêtes avant, après | Poids avant | Poids après | EcoIndex avant | EcoIndex après |")
    print("|---|---:|---:|---:|---:|---:|---|---|")
    for ecran in sans:
        a, b = sans[ecran], avec[ecran]
        print(f"| {ecran} | {a['dom']} | {b['dom']} | {a['requetes']} ; {b['requetes']} | {a['ko']} ko | {b['ko']} ko | "
              f"{a['note']} ({a['ecoindex']}) | {b['note']} ({b['ecoindex']}) |")
    json.dump({"avant": sans, "apres": avec, "calcul": "script corrigé du 07/11 au soir (routes, ko décimaux, périmètre des requêtes)"},
              open(destination, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("écrit :", destination)
