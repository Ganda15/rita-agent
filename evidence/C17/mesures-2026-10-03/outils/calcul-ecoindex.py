"""EcoIndex des trois ecrans de RITA, avant et apres compression, depuis les mesures Lighthouse du 03/10/2026.
Formule et tables : depot officiel cnumr/ecoindex_python (components/ecoindex/compute/ecoindex.py, data/quantiles.py, data/grades.py),
recopiees telles quelles. Entrees : noeuds du DOM, taille en Ko, nombre de requetes."""
import gzip, json, sys, pathlib

QD = [0, 47, 75, 159, 233, 298, 358, 417, 476, 537, 603, 674, 753, 843, 949, 1076, 1237, 1459, 1801, 2479, 594601]
QR = [0, 2, 15, 25, 34, 42, 49, 56, 63, 70, 78, 86, 95, 105, 117, 130, 147, 170, 205, 281, 3920]
QS = [0, 1.37, 144.7, 319.53, 479.46, 631.97, 783.38, 937.91, 1098.62, 1265.47, 1448.32, 1648.27, 1876.08, 2142.06, 2465.37, 2866.31, 3401.59, 4155.73, 5400.08, 8037.54, 223212.26]
GRADES = [("A", 80), ("B", 70), ("C", 55), ("D", 40), ("E", 25), ("F", 10)]


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


def ges(s):   # gCO2e par page, formule officielle
    return round(100 * (2 + 2 * (50 - s) / 100)) / 100


def eau(s):   # centilitres par page
    return round(100 * (3 + 3 * (50 - s) / 100)) / 100


POIDS = pathlib.Path(sys.argv[1])
LH = pathlib.Path(sys.argv[2])
gz = lambda octets: len(gzip.compress(octets, compresslevel=9))
lire = lambda nom: (POIDS / nom).read_bytes()

ECRANS = {
    "portefeuille": {"statique": ["index.html", "style.css", "app.js"],
                     "api": ["donnees_portefeuille.json", "donnees_indicateurs-portefeuille.json", "donnees_fraicheur.json"]},
    "indicateurs": {"statique": ["indicateurs.html", "style.css", "indicateurs.js"],
                    "api": ["donnees_indicateurs.json", "donnees_indicateurs-risque.json"]},
    "briefing": {"statique": ["briefing.html", "style.css", "briefing.js"],
                 "api": ["donnees_valeurs_limite_200.json"]},
}

sortie = {}
print(f"{'ecran':13} {'etat':28} {'DOM':>5} {'req':>4} {'Ko':>7}  {'EcoIndex':>8} {'note':>4} {'gCO2e':>6} {'cl eau':>6}")
for nom, d in ECRANS.items():
    # DOM de l'etat "donnees affichees" : dernier instantane du flux de bureau
    resume = json.load(open(LH / "resume-bureau.json", encoding="utf-8"))
    navs = [e for e in resume if e["ecran"] == nom and e["mode_lighthouse"] == "navigation"]
    # les instantanes n'ont pas cet audit : etat 1 = premiere navigation ; donnees = derniere navigation
    # (pour le briefing : donnees chargees, avant l'arrivee du texte)
    dom_vide, dom_final = navs[0]["noeuds_dom"], navs[-1]["noeuds_dom"]
    stat = sum(len(lire(f)) for f in d["statique"])
    stat_gz = sum(gz(lire(f)) for f in d["statique"])
    api = sum(len(lire(f)) for f in d["api"])
    api_gz = sum(gz(lire(f)) for f in d["api"])
    n_req_vide = len(d["statique"]) + (1 if nom == "portefeuille" else 0)       # + favicon.ico (404) a la premiere visite
    n_req_donnees = len(d["statique"]) + len(d["api"]) + (1 if nom == "portefeuille" else 0)
    cas = [
        ("etat 1, sans cle, actuel", dom_vide, n_req_vide, stat),
        ("etat 1, sans cle, gzip", dom_vide, n_req_vide, stat_gz),
        ("donnees affichees, actuel", dom_final, n_req_donnees, stat + api),
        ("donnees affichees, gzip", dom_final, n_req_donnees, stat_gz + api_gz),
    ]
    sortie[nom] = {"statique_octets": stat, "statique_gzip_octets": stat_gz, "api_octets": api, "api_gzip_octets": api_gz,
                   "dom_etat1": dom_vide, "dom_donnees": dom_final, "requetes_etat1": n_req_vide, "requetes_donnees": n_req_donnees, "cas": []}
    for etat, dom, req, octets in cas:
        ko = octets / 1024
        s = score(dom, ko, req)
        print(f"{nom:13} {etat:28} {dom:5d} {req:4d} {ko:7.1f}  {s:8d} {grade(s):>4} {ges(s):6.2f} {eau(s):6.2f}")
        sortie[nom]["cas"].append({"etat": etat, "dom": dom, "requetes": req, "ko": round(ko, 1), "ecoindex": s, "note": grade(s), "gco2e": ges(s), "cl_eau": eau(s)})
    print(f"   statique {stat} o -> gzip {stat_gz} o ({100*(1-stat_gz/stat):.0f} % en moins) ; API {api} o -> gzip {api_gz} o ({100*(1-api_gz/api):.0f} % en moins)")
json.dump(sortie, open(LH / "ecoindex-resume.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
