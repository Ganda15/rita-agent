"""EcoIndex des cinq écrans de RITA, sans et avec la carte #74, depuis les mesures Lighthouse du 06/11/2026.

Formule et tables : celles du script du 03/10 (evidence/C17/mesures-2026-10-03/outils/calcul-ecoindex.py), recopiées du
dépôt officiel cnumr/ecoindex_python, sans modification. Différence avec le 03/10 : la compression n'est plus simulée,
elle est mesurée. Pour chaque écran, avec ses données :
- poids = octets réellement transférés pour les fichiers de l'interface au premier chargement (cache vide, étape 1)
  + octets transférés pour les réponses de l'API de l'écran chargé (étape 2) ;
- requêtes et éléments du DOM = ceux de l'étape 2 (écran avec ses données), mesurés par Lighthouse.

Usage : python calcul-ecoindex-2026-11-06.py <dossier sans-74> <dossier avec-74>
"""
import json
import sys
from pathlib import Path

QD = [0, 47, 75, 159, 233, 298, 358, 417, 476, 537, 603, 674, 753, 843, 949, 1076, 1237, 1459, 1801, 2479, 594601]
QR = [0, 2, 15, 25, 34, 42, 49, 56, 63, 70, 78, 86, 95, 105, 117, 130, 147, 170, 205, 281, 3920]
QS = [0, 1.37, 144.7, 319.53, 479.46, 631.97, 783.38, 937.91, 1098.62, 1265.47, 1448.32, 1648.27, 1876.08, 2142.06,
      2465.37, 2866.31, 3401.59, 4155.73, 5400.08, 8037.54, 223212.26]
GRADES = [("A", 80), ("B", 70), ("C", 55), ("D", 40), ("E", 25), ("F", 10)]
ROUTES_API = ("/donnees", "/sante", "/briefing", "/question", "/health", "/audit")


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
        statique = sum(r["octets"] or 0 for r in froid["requetes_detail"] if not r["url"].startswith(ROUTES_API))
        api = sum(r["octets"] or 0 for r in donnees["requetes_detail"] if r["url"].startswith(ROUTES_API))
        ko = (statique + api) / 1024
        s = score(donnees["noeuds_dom"], ko, donnees["requetes"])
        sortie[ecran] = {"dom": donnees["noeuds_dom"], "requetes": donnees["requetes"], "ko": round(ko, 1),
                         "statique_ko": round(statique / 1024, 1), "api_ko": round(api / 1024, 1),
                         "ecoindex": s, "note": grade(s), "gco2e": ges(s), "eau_cl": eau(s),
                         "bonnes_pratiques": donnees["scores"]["bonnes_pratiques"]}
    return sortie


sans, avec = mesurer(sys.argv[1]), mesurer(sys.argv[2])
print("| Écran | Éléments du DOM | Requêtes | Poids sans #74 | Poids avec #74 | EcoIndex sans #74 | EcoIndex avec #74 | gCO2e par page, avec | Bonnes pratiques sans, avec |")
print("|---|---:|---:|---:|---:|---|---|---:|---|")
for ecran in sans:
    a, b = sans[ecran], avec[ecran]
    print(f"| {ecran} | {b['dom']} | {b['requetes']} | {a['ko']} Ko | {b['ko']} Ko | {a['note']} ({a['ecoindex']}) | "
          f"{b['note']} ({b['ecoindex']}) | {b['gco2e']} | {a['bonnes_pratiques']} ; {b['bonnes_pratiques']} |")
json.dump({"sans_74": sans, "avec_74": avec}, open(Path(sys.argv[2]).parent / "ecoindex-2026-11-06.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
