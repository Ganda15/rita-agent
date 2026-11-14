"""Essai local : comment Mistral répond-il au vrai prompt des questions de RITA ? (14/11, diagnostic de
CITATIONS_INVALIDES et des réponses tronquées). Trois extraits inventés, la question de contrôle du pré-test.
Appel direct (même corps que `src/llm.py`, `_requete_json`) pour voir la sortie brute et `finish_reason`, à la
température par défaut puis à 0,2. Rien n'est écrit dans le dépôt ; la clé est lue dans l'environnement local,
jamais affichée."""
import json
import os
import re
import sys

import httpx

sys.path.insert(0, r"D:\KandaWork\RITA_PROJECT\rita-agent")
os.chdir(r"D:\KandaWork\RITA_PROJECT\rita-agent")
from dotenv import load_dotenv  # noqa: E402

load_dotenv()
from agents.question import SCHEMA_SORTIE, SortieModele, citations_valides, construire_prompt, _NUMERO_CITE  # noqa: E402
from rag.recherche import Passage  # noqa: E402
from src.llm import MISTRAL_URL, _texte_mistral  # noqa: E402

print("cle Mistral presente :", bool(os.environ.get("MISTRAL_API_KEY")))
print("MISTRAL_MODEL local :", os.environ.get("MISTRAL_MODEL") or "(absent : defaut du code, mistral-large-2512)")


def passage(i, texte):
    return Passage(article_id=i, texte=texte, titre=f"titre {i}", source="Reuters", lien="https://example.org",
                   publie_le="2026-11-03", tickers=["NFLX"], rang_dense=i, rang_lexical=i, distance_dense=0.1,
                   score_lexical=1.0)


passages = [
    passage(1, "Netflix va supprimer environ 1 000 postes, soit près de 6 % de ses effectifs, selon un mémo interne."),
    passage(2, "La plateforme veut réduire ses coûts après un trimestre décevant ; les suppressions toucheront le marketing."),
    passage(3, "Les marchés ont salué l'annonce : l'action Netflix gagnait 2 % à l'ouverture."),
]
prompt = construire_prompt("Combien de postes Netflix va-t-il supprimer ?", passages)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 6


def appel(temperature, modele):
    corps = {"model": modele, "max_tokens": 800,
             "messages": [{"role": "user", "content": prompt}],
             "response_format": {"type": "json_schema",
                                 "json_schema": {"name": "reponse_rita", "strict": True, "schema": SCHEMA_SORTIE}}}
    if temperature is not None:
        corps["temperature"] = temperature
    r = httpx.post(MISTRAL_URL, headers={"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"}, json=corps,
                   timeout=90.0)
    r.raise_for_status()
    choix = r.json()["choices"][0]
    return choix.get("finish_reason"), choix["message"]["content"], r.json().get("usage", {}), r.json().get("model")


MODELES = ([sys.argv[2]] if len(sys.argv) > 2
           else list(dict.fromkeys([os.environ.get("MISTRAL_MODEL") or "mistral-large-2512", "mistral-large-2512"])))
for modele in MODELES:
    temperature = None
    print(f"\n=== modele demande : {modele} ===")
    valides = 0
    for k in range(N):
        try:
            fin, contenu, usage, servi = appel(temperature, modele)
        except Exception as erreur:  # noqa: BLE001
            print(f"{k + 1}. ERREUR {type(erreur).__name__}")
            continue
        reflexion = isinstance(contenu, list) and any(isinstance(b, dict) and b.get("type") == "thinking" for b in contenu)
        brut = contenu if isinstance(contenu, str) else json.dumps(contenu, ensure_ascii=False)
        if fin in ("length", "model_length"):
            print(f"{k + 1}. TRONQUEE ({fin}, {usage.get('completion_tokens')} jetons, servi={servi}, reflexion={reflexion}) fin={brut[-80:]!r}")
            continue
        try:
            texte = _texte_mistral(contenu)
            sortie = SortieModele.model_validate_json(texte)
        except Exception as erreur:  # noqa: BLE001
            print(f"{k + 1}. JSON INVALIDE {type(erreur).__name__} servi={servi} reflexion={reflexion} debut={brut[-160:]!r}")
            continue
        ok = citations_valides(sortie, len(passages))
        valides += ok
        print(f"{k + 1}. valide={ok} servi={servi} reflexion={reflexion} jetons={usage.get('completion_tokens')} statut={sortie.statut} declarees={sorted(sortie.citations)} "
              f"dans_le_texte={sorted(int(n) for n in _NUMERO_CITE.findall(sortie.texte))} "
              f"crochets={re.findall(r'[\[][^\]]{0,20}[\]]', sortie.texte)}")
        if not ok:
            print("   texte :", sortie.texte[:300])
    print(f"--> {valides}/{N} valides")
