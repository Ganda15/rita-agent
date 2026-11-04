# C3 · Preuve : Viridien en production (commencée le 04/11/2026, écrite au fil de l'opération)

Plan suivi : [`docs/PLAN-VIRIDIEN-PRODUCTION.md`](../../docs/PLAN-VIRIDIEN-PRODUCTION.md). Correction locale :
[`preuve-correction-viridien-2026-11-04.md`](preuve-correction-viridien-2026-11-04.md).

| Statut | État au 04/11/2026, 18 h 40 |
|---|---|
| Testé en local | **oui** : base locale corrigée et vérifiée cellule par cellule et sur l'écran ; mode `--corrections-seulement` et ses portes testés sur des copies (id 8 à 14) ; suite complète 2 180 réussis, 60 sautés, 2 xfailed, deux fois (la seconde avec Azure injoignable) |
| Déployé | **non** : la production sert le commit `2310f87` ; le code de la correction n'est pas encore commité |
| Vérifié en production | **non** : aucune écriture faite ni autorisée |

## 1. Avant (lecture seule et écran public)

**Diagnostic en lecture seule, 04/11/2026 vers 17 h UTC** (une session SSH, `SELECT` en session lecture seule) : la ligne
`VIRI.PA` a l'id 14, 120 × 1,85, achat du 14/10/2021, ouverte, `importe_le` du 20/08/2026 11 h 03 UTC ; la valeur s'appelle
`CGG BS` ; la vue rend Viridien à 96,15 € (27/10/2026), +5 097,30 %, 11 538,00 €, total 32 277,05 € sur 7 lignes.

**Écran public, capture d'Era du 04/11/2026 au soir** (`https://178-104-184-125.sslip.io/index.html`, ancienne interface, avec sa
clé) : « Total du portefeuille : 32 277,05 € · 7 lignes » ; « Portefeuille valorisé, cours du 2026-10-27 » ; ligne VIRI.PA « CGG BS »,
120, 1,85, cours 96,15, investi 222,00 €, valorisation 11 538,00 €, **+5 097,30 %**, poids **35,75 %** ; bandeau rouge « 6 jours
ouvrés de retard, dernière séance du 27/10/2026. La collecte ne tourne plus. » Les sept lignes égalent celles du diagnostic.
Fichier de la capture : à déposer par Era dans `captures-viridien-production/1-avant-production-2026-11-04.png` (l'agent n'y a pas
accès ; une première copie faite par erreur depuis une autre capture, celle du port 8000 local, a été supprimée aussitôt).

Le retard des cours et l'archive décalée d'un jour (plan § 7) sont hors de cette correction.

## 2. À venir, dans l'ordre du plan

Lecture complémentaire approuvée ; copie représentative et répétition ; sauvegarde sur le poste et restauration testée ;
déploiement du code (accord A) ; passage à blanc puis vrai passage avec compteurs attendus (accords B) ; vérifications base, API,
écran ; captures après.
