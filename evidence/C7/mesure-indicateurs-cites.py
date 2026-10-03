"""Combien des 13 indicateurs du prompt se retrouvent, chiffres compris, dans les textes du 4e passage du banc ?
Heuristique, pas une preuve de fidelite : un chiffre present dans le texte = l'indicateur est cite.
Lancer depuis la racine du depot, avec python -X utf8, sur ce fichier."""
import json, re, sys, collections
from pathlib import Path
RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE))
R = str(RACINE / "evidence" / "C7") + "/"
from agents.analyst import construire_prompt, INDICATEURS_DU_PROMPT

jeu = {c["ticker"]: c for c in json.load(open(R + "jeu-d-essai-2026-10-03.json", encoding="utf-8"))["cas"]}

# les 13 : 3 lignes dediees du prompt + 10 du bloc
TREIZE = [("cours", "Cours de cloture"), ("variation_jour", "Variation sur 1 jour"), ("adtv20", "Capitaux moyens sur 20 seances")] \
         + [(k, l) for k, l, _ in INDICATEURS_DU_PROMPT]

def valeur(cas, cle):
    ind = cas["indicateurs"]
    return {"cours": cas["price"], "variation_jour": cas["change_pct"], "adtv20": cas["adtv20"]}.get(cle, ind.get(cle))

def fr(v, d):
    return f"{abs(v):.{d}f}".replace(".", ",")

def cite(texte, cle, v):
    t = texte.replace("\u202f", " ").replace("\u00a0", " ").replace("\u2212", "-")
    if v is None:
        return None
    if cle == "adtv20":
        m = v / 1e6
        motifs = [rf"(?<![\d,.]){fr(m, 2)} ?(millions|M|Md)", rf"(?<![\d,.]){fr(m, 1)} ?(millions|M|Md)",
                  rf"(?<![\d,.]){round(m)}(,\d+)? ?(millions|M|Md)", rf"(?<![\d,.]){round(m, 1)}".replace(".", ",") + r" ?(millions|M)",
                  f"{v:,.0f}".replace(",", r"[ ,.]?")]
        return any(re.search(p, t) for p in motifs)
    if cle == "cours" and re.search(rf"(?<![\d,.]){re.escape(str(abs(v)).replace(chr(46), chr(44)))}(?!\d)", t):
        return True
    d = 1 if cle == "rsi_14" else 2
    strict = rf"(?<![\d,.]){fr(v, d)}(?!\d)"
    if re.search(strict, t):
        return True
    if d == 2:       # arrondi a une decimale ("1,6 %" pour 1,59), explicitement une lecture plus souple
        return bool(re.search(rf"(?<![\d,.]){fr(v, 1)}(?!\d)", t)) and "souple"
    return bool(re.search(rf"(?<![\d,.]){round(abs(v))}(?![\d,])", t)) and "souple"

lignes = [json.loads(l) for l in open(R + "resultats-2026-10-03.jsonl", encoding="utf-8")]
res = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))   # [exact, souple, n]
dans_le_prompt = collections.Counter()
for l in lignes:
    if l["erreur"] or not l["texte"]:
        continue
    cas = jeu[l["ticker"]]
    prompt = construire_prompt(cas["ticker"], cas["price"], cas["change_pct"], cas["adtv20"], cas["currency"],
                               cas["fraicheur_jours"], cas["cotation_perimee"], cas["passages"] or None, cas["indicateurs"])
    for cle, lib in TREIZE:
        v = valeur(cas, cle)
        r = res[l["fournisseur"]][cle]; r[2] += 1
        c = cite(l["texte"], cle, v)
        if c is True: r[0] += 1
        elif c == "souple": r[1] += 1
for l in lignes[:1]:
    pass
# presence dans le prompt : chaque libelle des 13 est-il une ligne du prompt ? (un cas, en entier)
cas = jeu["AI.PA"]
prompt = construire_prompt(cas["ticker"], cas["price"], cas["change_pct"], cas["adtv20"], cas["currency"],
                           cas["fraicheur_jours"], cas["cotation_perimee"], cas["passages"] or None, cas["indicateurs"])
presents = {
    "cours": "Cours de clôture : 170.16" in prompt, "variation_jour": "Variation sur 1 jour : 2.24%" in prompt,
    "adtv20": "Capitaux échangés en moyenne par séance sur 20 séances : 131,989,980 EUR" in prompt,
}
for k, lib, _ in INDICATEURS_DU_PROMPT:
    presents[k] = f"- {lib} : " in prompt and "non disponible" not in [x for x in prompt.splitlines() if x.startswith(f"- {lib} :")][0]
print("Dans le prompt (AI.PA) :", sum(presents.values()), "sur 13")
for k, v in presents.items():
    print("  ", "oui" if v else "NON", k)
print()
for f in sorted(res):
    print(f)
    tot_ex = tot_so = 0
    for cle, lib in TREIZE:
        ex, so, n = res[f][cle]
        print(f"  {cle:28} exact {ex:2}/{n}   avec arrondi {ex + so:2}/{n}")
    moy_ex = sum(res[f][c][0] for c, _ in TREIZE) / res[f]["cours"][2]
    moy_so = sum(res[f][c][0] + res[f][c][1] for c, _ in TREIZE) / res[f]["cours"][2]
    print(f"  => indicateurs cites par texte, en moyenne : {moy_ex:.1f} sur 13 (exact), {moy_so:.1f} (avec arrondi)")
