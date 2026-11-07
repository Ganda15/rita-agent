# Constat S9 : les garde-fous sous le seuil de 85 %, corrigés et mesurés (07/11/2026)

Compétence : C17 (OWASP Top 10, A05 et LLM01). Constat S9 de la revue du 03/10
(`evidence/C17/revue-owasp-top10-2025-2026-10-03.md`) : « garde-fous d'injection et de sortie à 70 %, sous le seuil de
85 % ». Plan : `docs/PLAN-S9-garde-fous.md`, validé par Era le 07/11 (« ok plan S9 »), complété le même jour pour le
garde-fou de sortie AMF, que le plan du 06/11 avait oublié (« Yes, extend (go) »). Les seuils ne changent pas : 85 % de
blocage, 15 % de faux positifs au plus.

## La méthode

1. Un jeu tenu à l'écart, organisé par famille d'attaque, écrit et commité **avant** toute modification de
   `guardrails/` :
   - injection et fuite, commit `ee64757` (`evals/cas_s9_reserves.py`) ;
   - sortie AMF, commit `f01d407` (`evals/cas_s9_reserves_sortie.py`), mesuré avant correction sur les nombres seuls,
     sans lire quels textes passaient (méthode demandée par la relecture d'un autre agent).
2. Des tests rouges avant le code (`tests/test_evals.py`), dont deux empreintes qui figent les jeux après leur commit.
3. Une correction par famille, jamais par phrase, en expressions régulières (latence en millisecondes).
4. La mesure, sur l'ancien jeu et sur le jeu tenu à l'écart, puis sur des textes réels.

## Les résultats

| Garde-fou | Avant (jeu tenu à l'écart) | Après : ancien jeu | Après : jeu tenu à l'écart | Faux positifs après |
|---|---|---|---|---|
| Injection indirecte (`guardrails/injection.py`) | 0 sur 12 | 10 sur 10 (70 % avant) | **12 sur 12** | 0 sur 8 et 0 sur 12 |
| Contrôle de fuite (`verifier_fuite`) | 0 sur 12 | 7 sur 7 (71,4 % avant) | **12 sur 12** | 0 sur 11 et 0 sur 12 |
| Sortie AMF (`verifier_sortie`) | 0 sur 12 | 10 sur 10 (70 % avant) | **12 sur 12** | 0 sur 6 et 0 sur 12 |

Sorties brutes : [`mesure-avant-correction.txt`](mesure-avant-correction.txt),
[`mesure-avant-correction-sortie-amf.txt`](mesure-avant-correction-sortie-amf.txt),
[`mesure-apres-correction-injection-fuite.txt`](mesure-apres-correction-injection-fuite.txt),
[`mesure-apres-correction-sortie-amf.txt`](mesure-apres-correction-sortie-amf.txt).

**Sur des textes réels, sans aucun refus** :
- 38 passages d'articles du jeu figé du banc (`evidence/C7/jeu-d-essai-2026-10-03*.json`) : 0 bloqué par l'injection ;
- 230 briefings écrits par les modèles lors des bancs (`evidence/C7/**/resultats-*.jsonl`) : 0 refusé par la sortie
  AMF, 0 par le contrôle de fuite.

Les deux marqueurs `xfail` stricts des tests (injection et sortie AMF), posés le 17/08 parce que le seuil n'était pas
atteint, sont retirés : `pytest` les signalait comme réussis par surprise, ce qu'ils exigeaient le jour de la levée.

## Un défaut trouvé en cours de route

La revue de sécurité automatique du 07/11 a relevé un retour arrière catastrophique (ReDoS) dans la première règle
« secret dit en clair » : sur « password » suivi de 5 000 espaces, le contrôle ne finissait pas en 120 s. Corrigé avant
tout envoi (suites d'espaces bornées) ; six entrées hostiles passent désormais les trois garde-fous en moins de 10 ms,
avec un test qui fixe un budget d'une seconde.

## Les limites, écrites

- **Ce n'est pas une validation indépendante** : le même agent a écrit les cas et les règles. Pour l'injection et la
  fuite, les textes qui passaient ont été lus avant la correction ; pour la sortie AMF, seulement leur nombre. Une
  évaluation indépendante demanderait des cas écrits par quelqu'un qui n'a pas vu les règles.
- 100 % sur ces jeux ne veut pas dire une protection parfaite : quelques dizaines de cas mesurent des familles connues,
  pas un attaquant qui s'adapte.
- Un seul passage réel d'article figure parmi les cas légitimes : la base n'est pas lisible sur le poste avec le rôle
  de lecture `rita_lecture`.
