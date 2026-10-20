"""Rejeu en production après la livraison N10 (sprint 4, tâche D2, étape 5 ; spec CA8.2, critère 1 du contrat).

Cinq appels à l'adresse de production, avec la clé de production lue dans la variable RITA_API_KEY de la session :

- POST /question, H1 (prompt hostile) : refus TENTATIVE_DETOURNEMENT attendu ;
- POST /question, Q4 : une réponse qui contient « 1 000 postes » (le cas de la mesure du 20/10) ;
- POST /question, H8 (hors périmètre) : un refus, abstention ou hors corpus ;
- POST /briefing, une valeur de 21 caractères : 422 ;
- POST /briefing?ticker=OR.PA : 200, un en-tête X-Request-ID, un texte (critère 1 du contrat).

Les textes des réponses et du briefing sont AFFICHÉS dans la console pour être lus, mais ne sont PAS conservés : D9
n'autorise pas à garder les briefings, et le rapport n'a besoin que des verdicts. Le rapport garde les codes HTTP, les
identifiants de requête, les statuts, les motifs, les identifiants d'articles cités, les longueurs et les verdicts ;
jamais la clé, ni un texte.

Bibliothèque standard seulement : aucun module du projet n'est importé, donc aucun .env local n'est chargé, et la clé
envoyée est celle de la session ou aucune (défaut relevé au sprint 3 sur l'outil d'évaluation).

Usage, depuis la racine du dépôt, la clé déjà dans la session : C:/Python314/python.exe evidence/sprint-4/rejeu_production.py
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ADRESSE = "https://178-104-184-125.sslip.io"
RACINE = Path(__file__).resolve().parents[2]
DOSSIER = RACINE / "evidence" / "sprint-4"
DELAI_S = 120
MOTS_FRANCAIS = ("le", "la", "les", "de", "des", "du", "une", "est", "et", "en", "sur", "pour")


def _normaliser(texte: str) -> str:
    """Espaces insécables et suites d'espaces ramenées à une espace simple."""
    return " ".join(texte.replace(chr(0xA0), " ").replace(chr(0x202F), " ").split())


def _appeler(cle: str | None, methode: str, chemin: str, corps: dict | None = None) -> dict:
    """Un appel HTTP ; rend le code, les en-têtes utiles et le corps JSON (ou None)."""
    donnees = json.dumps(corps).encode("utf-8") if corps is not None else None
    entetes = {"Content-Type": "application/json"} if corps is not None else {}
    if cle:
        entetes["X-API-Key"] = cle
    requete = urllib.request.Request(ADRESSE + chemin, data=donnees, headers=entetes, method=methode)
    try:
        with urllib.request.urlopen(requete, timeout=DELAI_S) as reponse:
            code, en_tetes, brut = reponse.status, reponse.headers, reponse.read()
    except urllib.error.HTTPError as erreur:
        code, en_tetes, brut = erreur.code, erreur.headers, erreur.read()
    try:
        contenu = json.loads(brut.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        contenu = None
    return {"code": code, "request_id": en_tetes.get("X-Request-ID"), "retry_after": en_tetes.get("Retry-After"),
            "corps": contenu}


def _question(jeu: dict, identifiant: str) -> str:
    return next(q["question"] for q in jeu["questions"] if q["id"] == identifiant)


def main() -> int:
    cle = os.environ.get("RITA_API_KEY", "").strip()
    if not cle:
        print("RITA_API_KEY absente de la session : aucun appel n'est fait.", file=sys.stderr)
        return 2

    jeu = json.loads((RACINE / "rag" / "questions_demo.json").read_text(encoding="utf-8"))
    sante = _appeler(None, "GET", "/health")["corps"] or {}
    rapport = {"date": datetime.now(timezone.utc).isoformat(timespec="seconds"), "adresse": ADRESSE,
               "commit_servi": sante.get("commit"), "index_servi": (sante.get("index") or {}).get("identifiant"),
               "appels": []}
    a_lire = []

    for identifiant, motifs_permis, statut_attendu in (("H1", {"TENTATIVE_DETOURNEMENT"}, "refus"),
                                                       ("Q4", {"OK"}, "reponse"),
                                                       ("H8", {"ABSTENTION", "OUT_OF_CORPUS"}, "refus")):
        r = _appeler(cle, "POST", "/question", {"question": _question(jeu, identifiant)})
        corps = r["corps"] or {}
        texte = str(corps.get("texte") or "")
        conforme = r["code"] == 200 and corps.get("statut") == statut_attendu and corps.get("motif") in motifs_permis
        if identifiant == "Q4":
            conforme = conforme and "1 000 postes" in _normaliser(texte)
        rapport["appels"].append({
            "cas": identifiant, "route": "POST /question", "code": r["code"], "request_id": r["request_id"],
            "statut": corps.get("statut"), "motif": corps.get("motif"),
            "articles_cites": [ref.get("id") for ref in corps.get("references") or []],
            "longueur_texte": len(texte), "conforme": conforme})
        a_lire.append((identifiant, texte))

    r = _appeler(cle, "POST", "/briefing?ticker=" + "X" * 21)
    rapport["appels"].append({"cas": "21 caractères", "route": "POST /briefing", "code": r["code"],
                              "request_id": r["request_id"], "conforme": r["code"] == 422})

    r = _appeler(cle, "POST", "/briefing?ticker=" + urllib.parse.quote("OR.PA"))
    corps = r["corps"] or {}
    texte = str(corps.get("briefing") or "")
    mots = _normaliser(texte).lower().split()
    reperes = sorted({mot for mot in MOTS_FRANCAIS if mot in mots})
    rapport["appels"].append({
        "cas": "OR.PA", "route": "POST /briefing", "code": r["code"], "request_id": r["request_id"],
        "conforme_amf": corps.get("conforme_amf"), "longueur_texte": len(texte),
        "mots_francais_reperes": reperes,
        "conforme": r["code"] == 200 and bool(r["request_id"]) and len(texte) > 0 and len(reperes) >= 3})
    a_lire.append(("OR.PA", texte))

    horodatage = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    sortie = DOSSIER / f"rejeu-production-{horodatage}.json"
    # Mode « x » : le fichier ne doit pas exister. Le 20/10/2026, deux lancements dans la même minute avaient
    # écrit le même nom (sans les secondes), et le second avait écrasé le rapport du premier.
    with open(sortie, "x", encoding="utf-8") as fichier:
        fichier.write(json.dumps(rapport, ensure_ascii=False, indent=1) + "\n")

    print(f"commit servi : {rapport['commit_servi']} | index : {rapport['index_servi']}")
    for appel in rapport["appels"]:
        print(f"{appel['cas']:>14} | {appel['route']:<15} | HTTP {appel['code']} | statut {appel.get('statut')} "
              f"| motif {appel.get('motif')} | conforme {appel['conforme']}")
    print("--- textes à lire (affichés ici, jamais conservés) ---")
    for identifiant, texte in a_lire:
        print(f"[{identifiant}] {texte}")
    print("rapport :", sortie)
    return 0 if all(appel["conforme"] for appel in rapport["appels"]) else 1


if __name__ == "__main__":
    sys.exit(main())
