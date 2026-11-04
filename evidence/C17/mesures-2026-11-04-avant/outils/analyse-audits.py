import json, sys, glob, os
D = sys.argv[1]
for mode in ("bureau", "mobile"):
    for ecran in ("portefeuille", "indicateurs", "briefing"):
        fl = json.load(open(f"{D}/flux-{ecran}-{mode}.json", encoding="utf-8"))
        for st in fl["steps"]:
            lhr = st["lhr"]
            nav = lhr["gatherMode"] == "navigation"
            echecs = []
            for cid, cat in lhr["categories"].items():
                for ref in cat["auditRefs"]:
                    a = lhr["audits"][ref["id"]]
                    if a["score"] is not None and a["score"] < 1 and a["scoreDisplayMode"] in ("binary", "numeric", "metricSavings"):
                        echecs.append((cid, a["id"], a["title"][:70], a.get("displayValue", ""), round(a["score"], 2)))
            if mode == "bureau" or "etat 1" in st["name"]:
                print(f"\n[{mode}] {ecran} | {st['name'][:60]} | {lhr['gatherMode']}")
                for e in echecs:
                    print("   NON REUSSI", e)
            if mode == "bureau" and nav:
                for iid in ("dom-size-insight", "cache-insight", "document-latency-insight", "modern-http-insight", "third-parties-insight", "render-blocking-insight"):
                    a = lhr["audits"].get(iid)
                    if a:
                        det = a.get("details", {})
                        print(f"   {iid}: score {a['score']} | {a.get('displayValue','')} | {str(det.get('items') or det.get('metadata') or det.get('value') or '')[:230]}")
        # liste des controles manuels d'accessibilite (une fois)
        if mode == "bureau" and ecran == "indicateurs":
            lhr = fl["steps"][-1]["lhr"]
            man = [lhr["audits"][r["id"]]["title"] for r in lhr["categories"]["accessibility"]["auditRefs"] if lhr["audits"][r["id"]]["scoreDisplayMode"] == "manual"]
            print("\nCONTROLES D'ACCESSIBILITE A FAIRE A LA MAIN :", *man, sep="\n  - ")
