"""Banc de comparaison des fournisseurs de modèle (C7), selon `docs/PLAN-C7-benchmark.md`.

Ce que ce script fait, et dans cet ordre : il relit un jeu d'essai figé (ou le construit depuis la base et
l'index, une fois, avec `--construire`), sonde chaque fournisseur une fois (un refus d'authentification ou une
clé absente = **indisponible pour la mesure**, pas un zéro de qualité), puis envoie à chaque fournisseur
disponible le **même prompt que le rédacteur** (`agents.analyst.construire_prompt`), autant de fois que demandé,
sous un plafond de dépense. Chaque appel donne une ligne brute (fournisseur, modèle rendu, durée, jetons, coût,
texte, erreur, conformité AMF par `guardrails.sortie`, fidélité aux faits fournis). Le résumé sépare ce que le
plan sépare : conformité, fidélité, latence, coût, disponibilité ; les proportions portent un intervalle de Wilson.

Ce qu'il ne fait pas : noter le français (c'est Era, à l'aveugle, depuis le fichier `notes-francais-*.csv`
que ce script prépare), ni décider.

Usage, depuis la racine (clés lues dans l'environnement par `api.main`, jamais affichées) :

    python -X utf8 -m evals.benchmark_fournisseurs --construire MC.PA OR.PA ... --sortie evidence/C7
    python -X utf8 -m evals.benchmark_fournisseurs --jeu evidence/C7/jeu-d-essai-2026-10-03.json --repetitions 3 --plafond 5
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import os
import random
import re
import statistics
import time
from pathlib import Path
from typing import Callable

from agents.analyst import construire_prompt
from guardrails.sortie import verifier_sortie

CHAMPS_CAS = ("ticker", "price", "change_pct", "adtv20", "currency", "fraicheur_jours", "cotation_perimee", "passages")
MAX_TOKENS = 500          # celui du rédacteur
FOURNISSEURS = ("foundry", "anthropic", "openrouter")
MOTS_HAUSSE = ("hausse", "progress", "gagn", "mont", "avanc", "grimp", "bondi", "rebond")
MOTS_BAISSE = ("baisse", "recul", "perd", "cèd", "ced", "repli", "chut", "décroch", "decroch", "fléch", "flech")


# ----------------------------------------------------------------------------- statistiques

def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Intervalle de Wilson à 95 % d'une proportion k/n. None sans essai : pas de chiffre inventé."""
    if n <= 0:
        return None
    p = k / n
    denominateur = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denominateur
    marge = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominateur
    return (max(0.0, centre - marge), min(1.0, centre + marge))


# ----------------------------------------------------------------------------- le jeu d'essai

def charger_jeu(chemin: Path | str) -> dict:
    jeu = json.loads(Path(chemin).read_text(encoding="utf-8"))
    for i, cas in enumerate(jeu.get("cas", [])):
        manquants = [c for c in CHAMPS_CAS if c not in cas]
        if manquants:
            raise ValueError(f"cas {i} ({cas.get('ticker', '?')}) : champs manquants {manquants}")
    if not jeu.get("cas"):
        raise ValueError("jeu d'essai vide")
    return jeu


def construire_jeu(tickers: list[str], collecter=None, rechercher=None) -> dict:
    """Fige les faits du jour pour chaque ticker : ce que le scout lit, ce que la recherche retrouve."""
    if collecter is None:
        from agents.scout import collect as collecter
    if rechercher is None:
        from rag.recherche import rechercher
    cas = []
    for t in tickers:
        etat = collecter(t)
        # La même question que le nœud `rag` du graphe (graph/workflow.py), pour figer les mêmes passages.
        nom = (etat.get("indicateurs") or {}).get("nom_officiel") or t
        resultat = rechercher(f"actualite {nom.split()[0]}", ticker=t)
        passages = [p.en_dict() for p in getattr(resultat, "passages", [])] if resultat is not None else []
        cas.append({c: etat.get(c) for c in CHAMPS_CAS if c != "passages"}
                   | {"passages": passages, "indicateurs": etat.get("indicateurs") or {}})
    return {"fige_le": dt.date.today().isoformat(), "cas": cas}


def prompt_du_cas(cas: dict) -> str:
    # `indicateurs` est facultatif : un jeu figé avant le 03/10 n'en a pas, et son prompt reste celui d'alors.
    return construire_prompt(**{c: cas[c] for c in CHAMPS_CAS}, indicateurs=cas.get("indicateurs") or None)


# ----------------------------------------------------------------------------- fidélité aux faits

def _formes_du_cours(price: float) -> list[str]:
    formes = {f"{price:.2f}", f"{price:.2f}".replace(".", ","), f"{price:g}", f"{price:g}".replace(".", ",")}
    return sorted(formes)


def fidele(texte: str, cas: dict) -> bool:
    """Le cours fourni est dans le texte, et le sens de la variation n'est pas inversé.

    Heuristique, déclarée comme telle : elle attrape un cours absent ou un sens inversé, pas un chiffre
    inventé ailleurs dans le texte (relecture humaine des cas limites, plan §4)."""
    t = texte.lower()
    if not any(f in texte for f in _formes_du_cours(float(cas["price"]))):
        return False
    hausse = any(m in t for m in MOTS_HAUSSE)
    baisse = any(m in t for m in MOTS_BAISSE)
    if cas["change_pct"] >= 0:
        return not (baisse and not hausse)
    return not (hausse and not baisse)


# ----------------------------------------------------------------------------- l'exécution

def appel_reel(nom: str, prompt: str, max_tokens: int):
    """Appelle UN fournisseur de `src.llm`, sans cascade et sans trace : on mesure le fournisseur, pas RITA."""
    from src import llm
    return getattr(llm, f"_appel_{nom}")(prompt, max_tokens)


def _cout(usage: dict | None, prix: tuple[float, float] | None) -> float:
    if not usage or not prix:
        return 0.0
    entree, sortie = prix
    return usage.get("input", 0) / 1e6 * entree + usage.get("output", 0) / 1e6 * sortie


def executer(jeu: dict, fournisseurs: list[str], repetitions: int, plafond_usd: float,
             prix: dict[str, tuple[float, float]], appel: Callable | None = None,
             journal: Callable[[dict], None] | None = None) -> tuple[list[dict], dict]:
    """Une sonde par fournisseur, puis cas × répétitions ; s'arrête quand le plafond est franchi."""
    if appel is None:
        appel = appel_reel
    lignes: list[dict] = []
    etat: dict[str, dict] = {}
    depense = 0.0
    cas_liste = jeu["cas"]
    for nom in fournisseurs:
        prompt_sonde = prompt_du_cas(cas_liste[0])
        try:
            appel(nom, prompt_sonde, 16)
        except Exception as erreur:  # noqa: BLE001 : la sonde dit « indisponible », elle ne juge pas
            etat[nom] = {"statut": "indisponible", "motif": f"{type(erreur).__name__}: {erreur}"[:200]}
            continue
        etat[nom] = {"statut": "mesure", "motif": ""}
        for repetition in range(1, repetitions + 1):
            for cas in cas_liste:
                if depense > plafond_usd:
                    etat[nom] = {"statut": "plafond atteint", "motif": f"{depense:.4f} USD > {plafond_usd} USD"}
                    break
                prompt = prompt_du_cas(cas)
                debut = time.perf_counter()
                ligne = {"fournisseur": nom, "modele": None, "ticker": cas["ticker"], "repetition": repetition,
                         "horodatage": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                         "duree_s": None, "jetons_entree": 0, "jetons_sortie": 0, "cout_usd": 0.0,
                         "texte": None, "erreur": None, "conforme_amf": None, "fidele": None}
                try:
                    reponse = appel(nom, prompt, MAX_TOKENS)
                    texte = reponse if isinstance(reponse, str) else reponse.texte
                    usage = None if isinstance(reponse, str) else getattr(reponse, "usage", None)
                    ligne.update({
                        "modele": None if isinstance(reponse, str) else getattr(reponse, "modele", None),
                        "jetons_entree": (usage or {}).get("input", 0), "jetons_sortie": (usage or {}).get("output", 0),
                        "cout_usd": _cout(usage, prix.get(nom)), "texte": texte,
                        "conforme_amf": bool(verifier_sortie(texte)["conforme"]), "fidele": fidele(texte, cas),
                    })
                except Exception as erreur:  # noqa: BLE001 : une erreur est une ligne, pas un arrêt
                    ligne["erreur"] = f"{type(erreur).__name__}: {erreur}"[:200]
                ligne["duree_s"] = round(time.perf_counter() - debut, 3)
                depense += ligne["cout_usd"]
                lignes.append(ligne)
                if journal:
                    journal(ligne)
            if etat[nom]["statut"] == "plafond atteint":
                break
    return lignes, etat


# ----------------------------------------------------------------------------- le résumé

def _percentile(valeurs: list[float], p: float) -> float | None:
    """Rang le plus proche : la valeur sous laquelle tombent au moins p des mesures (lisible sur 30 appels)."""
    if not valeurs:
        return None
    v = sorted(valeurs)
    return v[max(0, math.ceil(p * len(v)) - 1)]


def resumer(lignes: list[dict]) -> dict[str, dict]:
    resume: dict[str, dict] = {}
    for nom in sorted({l["fournisseur"] for l in lignes}):
        mes = [l for l in lignes if l["fournisseur"] == nom]
        ok = [l for l in mes if l["erreur"] is None]
        conformes = sum(1 for l in ok if l["conforme_amf"])
        fideles = sum(1 for l in ok if l["fidele"])
        durees = [l["duree_s"] for l in ok if l["duree_s"] is not None]
        resume[nom] = {
            "appels": len(mes), "reussis": len(ok),
            "intervalle_disponibilite": wilson(len(ok), len(mes)),
            "conformes_amf": conformes, "intervalle_conformes": wilson(conformes, len(ok)),
            "fideles": fideles, "intervalle_fideles": wilson(fideles, len(ok)),
            "latence_p50_s": statistics.median(durees) if durees else None, "latence_p95_s": _percentile(durees, 0.95),
            "jetons_entree_moyen": statistics.mean([l["jetons_entree"] for l in ok]) if ok else None,
            "jetons_sortie_moyen": statistics.mean([l["jetons_sortie"] for l in ok]) if ok else None,
            "cout_total_usd": sum(l["cout_usd"] for l in mes),
            "cout_moyen_usd": (sum(l["cout_usd"] for l in ok) / len(ok)) if ok else None,
        }
    return resume


def ecrire_notation_a_l_aveugle(lignes: list[dict], dossier: Path, date: str, graine: int = 2026) -> None:
    """Deux fichiers : les textes mélangés sans fournisseur (à noter), et la clé de correspondance (à ouvrir après)."""
    ok = [l for l in lignes if l["erreur"] is None and l["texte"]]
    ordre = list(range(len(ok)))
    random.Random(graine).shuffle(ordre)
    with open(dossier / f"notes-francais-{date}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "ticker", "texte", "note_francais_0_1_2", "remarque"])
        for i, k in enumerate(ordre, 1):
            w.writerow([i, ok[k]["ticker"], ok[k]["texte"].replace("\n", " "), "", ""])
    with open(dossier / f"notes-francais-{date}-cle.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "fournisseur", "modele", "repetition", "horodatage"])
        for i, k in enumerate(ordre, 1):
            w.writerow([i, ok[k]["fournisseur"], ok[k]["modele"], ok[k]["repetition"], ok[k]["horodatage"]])


def prix_openrouter(modele: str) -> tuple[tuple[float, float] | None, str]:
    """Prix public d'OpenRouter pour un modèle, en EUR approchés par USD (lu le jour du banc, lien cité)."""
    import httpx
    url = "https://openrouter.ai/api/v1/models"
    try:
        corps = httpx.get(url, timeout=20).json()
    except Exception as erreur:  # noqa: BLE001
        return None, f"prix inconnu ({type(erreur).__name__})"
    for m in corps.get("data", []):
        if m.get("id") == modele:
            p = m.get("pricing", {})
            return (float(p.get("prompt", 0)) * 1e6, float(p.get("completion", 0)) * 1e6), url
    return None, f"modèle {modele} absent de {url}"


def _afficher(resume: dict, etat: dict) -> None:
    print("=== BANC DES FOURNISSEURS (plan C7) ===")
    for nom, e in etat.items():
        print(f"{nom:12} {e['statut']:18} {e['motif']}")
    for nom, r in resume.items():
        iv = lambda x: "n/a" if x is None else f"[{x[0]:.2f} ; {x[1]:.2f}]"
        print(f"\n{nom} : {r['reussis']}/{r['appels']} réussis {iv(r['intervalle_disponibilite'])}")
        print(f"  conformes AMF : {r['conformes_amf']}/{r['reussis']} {iv(r['intervalle_conformes'])}")
        print(f"  fidèles       : {r['fideles']}/{r['reussis']} {iv(r['intervalle_fideles'])}")
        print(f"  latence p50 / p95 : {r['latence_p50_s']} s / {r['latence_p95_s']} s")
        print(f"  jetons entrée / sortie (moyenne) : {r['jetons_entree_moyen']} / {r['jetons_sortie_moyen']}")
        print(f"  coût total : {r['cout_total_usd']:.4f} USD, moyen par briefing : {r['cout_moyen_usd']}")


def main(argv: list[str] | None = None) -> int:
    # INC-006 bis (03/10/2026) : construire le jeu appelle `rag.recherche`, qui ouvre une trace Langfuse ;
    # sans ce verrou, le banc a écrit 22 traces `rag` dans le projet de production. Le traçage est coupé
    # AVANT tout import du code de RITA : on mesure les fournisseurs, on ne trace pas RITA.
    os.environ["LANGFUSE_TRACING_ENABLED"] = "false"
    import api.main  # noqa: F401 : charge l'environnement (clés), jamais affichées

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--construire", nargs="*", metavar="TICKER", help="fige le jeu d'essai depuis la base et l'index")
    p.add_argument("--jeu", help="jeu d'essai figé (JSON)")
    p.add_argument("--sortie", default="evidence/C7")
    p.add_argument("--repetitions", type=int, default=3)
    p.add_argument("--plafond", type=float, default=5.0, help="plafond de dépense en USD (prix publics des fournisseurs, en dollars)")
    p.add_argument("--fournisseurs", default=",".join(FOURNISSEURS))
    a = p.parse_args(argv)
    dossier = Path(a.sortie); dossier.mkdir(parents=True, exist_ok=True)
    date = dt.date.today().isoformat()

    if a.construire:
        jeu = construire_jeu(a.construire)
        chemin = dossier / f"jeu-d-essai-{date}.json"
        chemin.write_text(json.dumps(jeu, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"jeu figé : {chemin} ({len(jeu['cas'])} cas, sans article : "
              f"{[c['ticker'] for c in jeu['cas'] if not c['passages']]})")
        return 0

    if not a.jeu:
        p.error("--jeu ou --construire")
    jeu = charger_jeu(a.jeu)
    from src.llm import _modele_prevu
    prix: dict[str, tuple[float, float]] = {}
    sources_prix: dict[str, str] = {}
    po, source = prix_openrouter(_modele_prevu("openrouter"))
    if po:
        prix["openrouter"] = po
    sources_prix["openrouter"] = source
    fournisseurs = [f.strip() for f in a.fournisseurs.split(",") if f.strip()]
    chemin_brut = dossier / f"resultats-{date}.jsonl"
    with open(chemin_brut, "a", encoding="utf-8") as f:
        def journal(ligne: dict) -> None:
            f.write(json.dumps(ligne, ensure_ascii=False) + "\n"); f.flush()
            print(f"  {ligne['fournisseur']:11} {ligne['ticker']:8} rép {ligne['repetition']} "
                  f"{ligne['duree_s']}s {ligne['erreur'] or 'ok'}")
        lignes, etat = executer(jeu, fournisseurs, a.repetitions, a.plafond, prix, journal=journal)
    resume = resumer(lignes)
    (dossier / f"resume-{date}.json").write_text(
        json.dumps({"fige_le": jeu.get("fige_le"), "prix_par_million_usd": prix, "sources_prix": sources_prix,
                    "etat": etat, "resume": resume}, ensure_ascii=False, indent=1), encoding="utf-8")
    ecrire_notation_a_l_aveugle(lignes, dossier, date)
    _afficher(resume, etat)
    print(f"\nbrut : {chemin_brut} ; prix : {sources_prix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
