# Preuve C10 — passerelle MCP : l'API de RITA exposée à un client LLM

**Date : 28/08/2026** · Compétences visées : **C10** (intégrer l'API dans une application),
**C15** (cadre technique), **C17** (composants).
Consigne formateur du 28/08 : le **MCP est obligatoire**. Plan : `docs/PLAN-RAG-MCP.md`, étape E1.

---

## 1. Ce qui a été construit

| Fichier | Rôle |
|---|---|
| `passerelle_mcp/serveur.py` | Serveur MCP, transport **stdio**, 3 outils de lecture |
| `tests/test_passerelle_mcp.py` | **11 tests**, dont 2 centraux sur l'authentification |
| `requirements.txt` | dépendance `mcp>=2.1.1` ajoutée |
| `.env.example` | `RITA_API_URL` documentée |

**MCP** (*Model Context Protocol*) : protocole standard qui décrit des **outils** à un modèle
de langage — nom, entrées, sorties, erreurs. Le modèle décide **quand** appeler ; le code
décide **comment**.

## 2. La décision d'architecture, et pourquoi elle vaut le détour

**La passerelle appelle l'API REST en HTTP. Elle n'appelle pas les modules Python en direct.**

C'était le choix le plus court : `from indicateurs import socle` et on lit la base. Il a été
écarté pour trois raisons :

1. **C10 demande d'intégrer l'API dans une application**, pas de la contourner. Le critère
   parle de *« la communication avec l'API depuis l'application »* et des *« étapes
   d'authentification intégrées correctement »*. Un appel direct aux modules ne prouverait
   ni l'une ni l'autre — la passerelle est un **client** de RITA, comme `frontend/app.js`.
2. **Le garde-fou 403 reste en vigueur.** Une passerelle qui court-circuiterait
   l'authentification annulerait la correction OWASP API2 du 18/08
   (`evidence/C21/INC-001`) — sans qu'aucun autre test ne le signale.
3. **Un seul chemin d'accès à tester.** Deux chemins, ce sont deux comportements qui
   divergent le jour où l'un des deux change.

**Le coût** : un aller-retour HTTP local, quelques millisecondes. *C'est le prix de la preuve.*

## 3. Les trois outils

| Outil | Point de terminaison appelé | Entrées |
|---|---|---|
| `rita_fraicheur` | `GET /donnees/fraicheur` | aucune |
| `rita_portefeuille` | `GET /donnees/portefeuille` | aucune |
| `rita_indicateurs` | `GET /donnees/indicateurs` | `ticker` (optionnel) |

Les trois sont annotés **`read_only_hint=True`**, `destructive_hint=False`,
`idempotent_hint=True` : un client peut les appeler sans demander confirmation à
l'utilisateur, parce qu'ils ne modifient rien.

**Les descriptions portent les garde-fous métier**, pas seulement la technique :
- `rita_fraicheur` : *« à appeler EN PREMIER avant de commenter un chiffre »* ;
- `rita_indicateurs` : *« RITA rend des FAITS, jamais un conseil d'achat ou de vente »* —
  la contrainte AMF est ainsi transmise au modèle client, pas seulement appliquée en sortie.

## 4. Le contrat d'erreur — codes typés, jamais de texte libre

Repris du brief Sorabel. Un modèle qui lit `NOT_AUTHORIZED` sait quoi faire ; un modèle qui
lit « quelque chose s'est mal passé » réessaie au hasard.

```
NOT_AUTHORIZED · SERVICE_INDISPONIBLE · DELAI_DEPASSE · NOT_FOUND · ERREUR_API
```

Et chaque message dit **quoi faire** : *« Vérifier qu'elle est démarrée (uvicorn api.main:app)
ou ajuster RITA_API_URL »*. Un garde-fou qui bloque sans expliquer finit contourné par celui
qu'il protège.

## 5. Vérification réelle — 28/08/2026

**Contre l'API réelle et la base réelle**, pas en test simulé.

```
rita_fraicheur      → {"success": true, "data": {"statut": "vert",
                        "derniere_seance": "2026-08-27", "retard_jours_ouvres": 1,
                        "nb_cotations": 275878, "nb_articles": 163}}

rita_portefeuille   → {"success": true, "data": {"nb": 7, "total_eur": 31448.2,
                        "positions": [{"ticker": "VIRI.PA", ...}]}}

rita_indicateurs    → {"success": true, "data": {"nb": 1, "indicateurs":
   (ticker=MC.PA)       [{"ticker": "MC.PA", "nom_officiel": "LVMH MOET VUITTON",
                          "cours": 447.4, "perf_1j_pct": -1.41}]}}
```

### Les deux chemins d'erreur, vérifiés eux aussi

```
mauvaise clé        → 403 côté API → {"code": "NOT_AUTHORIZED"}
                      ✅ LE GARDE-FOU SURVIT À LA PASSERELLE
API éteinte         → {"code": "SERVICE_INDISPONIBLE",
                       "message": "...Verifier qu'elle est demarree (uvicorn...)"}
```

**Suite complète** : `355 passed, 2 xfailed` · couverture **92,25 %** (seuil CI 90 %).

## 6. Comment un client LLM s'y connecte

Le transport est **stdio** : le client lance ce programme comme sous-processus et lui parle
par ses tubes d'entrée/sortie. **Rien n'est exposé sur le réseau**, aucun port ouvert — c'est
le transport le plus sûr pour un serveur local.

Configuration côté client (l'API RITA doit tourner) :

```json
{
  "mcpServers": {
    "rita": {
      "command": "C:\\Python314\\python.exe",
      "args": ["-m", "passerelle_mcp.serveur"],
      "cwd": "D:\\KandaWork\\RITA_PROJECT\\rita-agent"
    }
  }
}
```

La clé et l'adresse sont lues dans le `.env` du projet — **aucun secret dans ce fichier de
configuration**.

## 7. Ce que ça prouve, et ce que ça ne prouve pas

**Prouvé** : l'API de RITA est intégrée dans une application tierce (un client LLM),
l'authentification est transmise et vérifiée, les erreurs sont typées et actionnables, et
11 tests verrouillent le tout.

⚠️ **Non confirmé — à poser au formateur** : *un client MCP compte-t-il comme « une
application » au sens de C10 ?* Écrit dans `docs/PLAN-RAG-MCP.md` §8 comme hypothèse assumée.
Si la réponse est non, la passerelle reste obligatoire par consigne mais ne coche pas ce
critère — et c'est **C15/C17** qui la portent.

⬜ **Reste à faire** : l'**audit** des appels (journal : identité, outil, décision, durée),
prévu au design Sorabel et pas encore implémenté ici. Et le **4ᵉ outil**, `search_articles`,
qui viendra avec le RAG — étapes E2 à E4 du plan.
