# Preuve C9 : l'API expose le modèle, et un vrai briefing a été servi (03/10/2026)

> Livrable E3. La route `POST /briefing` est la seule qui expose le modèle de langage ; `/donnees/*` sert le jeu de
> données (C5). Cette fiche range un appel réel du 03/10/2026 et les contrôles qui l'entourent.

## 1. L'appel réel

API démarrée sur le poste (`uvicorn api.main:app`, port libre), clé lue par l'application depuis son environnement,
jamais affichée. Un seul appel, parce qu'il est payant (OpenRouter) :

```
POST /briefing?ticker=MC.PA        X-API-Key: <clé>
statut : 200 | duree : 13.85 s | X-Request-ID : 10db04cd0b4b4e1ba9c298d3736b87c7
cles reponse : ['briefing', 'change_pct', 'conforme_amf', 'currency', 'motifs_amf', 'price', 'ticker']
conforme_amf : True | ticker : MC.PA | price : 378.55 | change_pct : -0.25
briefing : 631 caracteres, commence par « **Briefing MC.PA (LVMH) - Séance du jour** L'action LVMH clôture à 378,55 EUR, en légère baisse de 0,25 % ... »
```

La ligne de journal de l'API, pour la même requête :

```
2026-10-03 14:48:28,287 INFO api.main briefing servi : request_id=10db04cd0b4b4e1ba9c298d3736b87c7 ticker='MC.PA' conforme_amf=True duree_ms=13829
```

Le même identifiant est dans l'en-tête de la réponse, dans le journal et dans la trace Langfuse
(`../C11/preuve-langfuse-2026-10-03.md`, §5) : c'est ce que le `request_id` promet.

## 2. Le contrat

- OpenAPI 3.1.0, **14 chemins** le 03/10/2026 (`app.openapi()`), dont `POST /briefing`, `GET /health`, `POST /audit/mcp`
  et onze routes `/donnees/*`. Documentation interactive sur `/docs`.
- Version déclarée de l'API : `1.1.0` (`api/main.py`).
- Authentification : en-tête `X-API-Key`, 16 caractères minimum, aucune valeur par défaut, comparaison à temps constant ;
  refus en 403 sur toutes les routes sauf `/health`. Origine : incident INC-001 (`../C21/INC-001-cle-par-defaut.md`).
- Un refus du garde-fou de sortie n'est pas une erreur : HTTP 200 avec `conforme_amf=false` et le texte remplacé.

## 3. Les tests qui tiennent le contrat

| Fichier | Tests | Ce qu'il prouve |
|---|---|---|
| `tests/test_health.py` | 10 | vivacité, 403 sans clé, briefing simulé, 502 quand le graphe échoue, refus de démarrer sans clé, substitution AMF (prouvée par mutation le 02/10) |
| `tests/test_request_id.py` | 12 | identifiant sur toute réponse, 403, 502 et 500 inattendu compris ; identifiant client repris seulement s'il est sain |
| `tests/test_traces_robustesse.py` | 8 | une panne du traçage ne fait jamais tomber un briefing (remarque P1 de la revue de la PR 58) |
| `tests/test_api_donnees.py` | 57 | les routes de données, hors périmètre C9 mais même routeur et même clé |

Suite complète le 03/10/2026 : `740 passed, 2 xfailed`, couverture 93,92 %.

## 4. Ce qui manque, dit tel quel

- Un ticker inconnu répond **502** au lieu de **422** ; un test fige encore ce comportement.
- Aucune limite de débit (OWASP API4) : celui qui tient la clé peut déclencher des appels payants sans borne.
- Pas de version dans l'adresse (`/v1`), pas de format d'erreur RFC 9457.
- Sur le poste de démonstration, un seul fournisseur de modèle répond (OpenRouter) ; les deux autres échouent faute de clé,
  et la trace le montre.
