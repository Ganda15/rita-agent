"""Prépare la notation du français à l'aveugle (07/11/2026) : les 30 briefings d'Azure et les 30 de Mistral Large 3,
mélangés dans un seul fichier, sans le nom du fournisseur. La clé (numéro vers fournisseur) est à part.

Pourquoi un fichier commun : les deux passages ont été lancés séparément (Mistral a dû être réglé entre les deux), et
le banc ne mélange que les fournisseurs d'un même passage. Pourquoi retirer `**` : les 30 textes de Mistral en
contiennent, aucun d'Azure ; les laisser montrerait qui a écrit quoi. Le Markdown est compté à part, comme une mesure.

Usage, depuis la racine : C:\\Python314\\python.exe -X utf8 evidence/C7/banc-2026-11-07-comparaison/preparer_notation_aveugle.py
"""
import csv
import json
import random
from pathlib import Path

ICI = Path(__file__).resolve().parent
SOURCES = {"azure": ICI.parent / "banc-2026-11-07" / "resultats-2026-11-07.jsonl",
           "mistral-large-3": ICI.parent / "banc-2026-11-07-mistral-large-3" / "resultats-2026-11-07.jsonl"}

lignes = []
for fournisseur, chemin in SOURCES.items():
    for brut in chemin.read_text(encoding="utf-8").splitlines():
        l = json.loads(brut)
        lignes.append((fournisseur, l["ticker"], l["repetition"], (l["texte"] or "").replace("**", "")))

random.Random(20261107).shuffle(lignes)   # graine fixée : le mélange se refait à l'identique
with open(ICI / "notes-francais-2026-11-07.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["id", "ticker", "texte", "note_francais_0_1_2", "remarque"])
    for i, (_, ticker, _, texte) in enumerate(lignes, 1):
        w.writerow([i, ticker, texte, "", ""])
with open(ICI / "notes-francais-2026-11-07-cle.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["id", "fournisseur", "ticker", "repetition"])
    for i, (fournisseur, ticker, rep, _) in enumerate(lignes, 1):
        w.writerow([i, fournisseur, ticker, rep])
print(len(lignes), "textes ;", sum(1 for x in lignes if x[0] == "azure"), "Azure,", sum(1 for x in lignes if x[0] != "azure"), "Mistral")
