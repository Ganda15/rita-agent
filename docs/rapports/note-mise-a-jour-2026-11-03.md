<style>
.logo{ float:right; width:12mm; margin:2pt 0 2pt 10pt; }
.identite{ color:var(--ink-soft); font-size:8.8pt; }
body{ font-size:9.2pt; line-height:1.36; }
h1{ font-size:15pt; margin-bottom:5pt; }
h2{ font-size:11pt; margin:9pt 0 3pt; }
table{ font-size:8.5pt; margin:3pt 0 5pt; }
th{ font-size:7.4pt; }
p{ margin:0 0 4pt; }
p, li{ orphans:3; widows:3; }
h2#glossaire + ul{ columns:2; column-gap:16pt; font-size:8.3pt; }
h2#glossaire + ul li{ margin-bottom:1pt; }
@page{ margin:12mm 13mm 12mm 13mm; }
h2#criteres + p + table td:first-child{ width:11%; }
h2#criteres + p + table td:nth-child(2){ width:33%; }
</style>

<div><img class="logo" src="E3/logo/rita-logo-marque.png" alt="Logo de RITA"></div>

# Note de mise à jour des rapports E2 à E5

Projet fil rouge **RITA** · **Eramalingam Gandakumar** · Développeur en intelligence artificielle, RNCP 37827 · Simplon × Wild Code School · 3 novembre 2026 · à lire avec les rapports [E2](https://github.com/Ganda15/rita-agent/tree/livrable-E2-v1), [E3](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v3), [E4](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v1) et [E5](https://github.com/Ganda15/rita-agent/tree/livrable-E5-v1) remis le 5 novembre · dépôt GitHub privé `Ganda15/rita-agent`
{: .identite }

Chaque rapport est figé par son **tag** (une étiquette Git posée sur une version du dépôt, qui ne bouge plus), et je ne
le réécris pas. Depuis la pose des tags, des preuves datées ont changé huit lignes de mon auto-évaluation, et une
relecture a trouvé deux erreurs dans E3 et une phrase imprécise dans E4. Cette note les corrige, chacune avec sa
preuve. Le reste des rapports ne change pas.

## 1. Huit critères passent à ✅ {: #criteres }

Le 3 novembre à 14 h 42, j'ai envoyé au formateur le guide d'exploitation et la synthèse de veille en PDF, avec les
liens vers la documentation technique ([preuve d'envoi](https://github.com/Ganda15/rita-agent/blob/livrable-E1-v6/evidence/C8/envoi-documents-formateur-2026-11-03.md)).
Les critères qui demandent une documentation « communiquée » ont maintenant leur preuve. C6.2 demande que la veille soit
planifiée : elle l'est depuis le 14/08, et le rapport garde le bilan des semaines manquées
([registre des partiels](https://github.com/Ganda15/rita-agent/blob/livrable-E1-v6/docs/recette/registre-des-partiels.md)).

| Rapport, page | Critère | Au tag | Au 3/11 | Preuve |
|---|---|---|---|---|
| E2, p. 14 | C6.2 temps de veille planifiés | ⚠️ | ✅ | créneau du lundi, de 9 h à 10 h ([`docs/veille/README.md`, ligne 35](https://github.com/Ganda15/rita-agent/blob/livrable-E2-v1/docs/veille/README.md#L35)) |
| E2, p. 4 et 14 | C6.4 synthèses communiquées | ⚠️ | ✅ | synthèse S33 à S36 envoyée en PDF |
| E2, p. 15 et 16 | C8.5 documentation communiquée | ❌ | ✅ | guide d'exploitation envoyé en PDF |
| E4, p. 17 | C16.3 rituels partagés | ⚠️ | ✅ | lien vers `docs/PILOTAGE-AGILE.md` envoyé |
| E4, p. 18 | C17.11 documentation technique | ⚠️ | ✅ | `README.md` corrigé le 02/11 ; liens vers lui et vers `docs/ARCHITECTURE.md` envoyés |
| E4, p. 19 | C18.6 et C19.7 documentation de la chaîne | ⚠️ | ✅ | lien vers `docs/CI-CD.md` envoyé |
| E5, p. 5 | C20.7 documentation communiquée | ⚠️ | ✅ | guide d'exploitation envoyé en PDF |

E2 passe de 13 ✅, 6 ⚠️ et 1 ❌ à 16 ✅ et 4 ⚠️ ; E4, de 27 ✅ et 11 ⚠️ à 31 ✅ et 7 ⚠️ ; E5, de 10 ✅ et 2 ⚠️ à
11 ✅ et 1 ⚠️. Les passages d'E2 qui disent l'envoi non fait (p. 4, § 2.5 ; p. 16, § 6) se lisent avec cette date. E1 et E3 ne changent pas. Au total : 120 ✅, 17 ⚠️ et aucun ❌ sur 137 critères. Les ⚠️ restent à
consolider, par exemple C20.5 : les alertes de Langfuse sont automatiques, mais la vigie se lance à la main.

## 2. Deux erreurs dans E3 {: #e3 }

| Où | Le rapport dit | Ce qui est exact |
|---|---|---|
| p. 1, en-tête | « formateur et jury invités » | Le formateur a accès au dépôt ([preuve](https://github.com/Ganda15/rita-agent/blob/livrable-E1-v6/evidence/C16/preuve-acces-kanban-formateur-2026-11-03.md)). Les examinateurs ne sont pas encore invités : la date et la façon de leur ouvrir l'accès sont demandées au formateur depuis le 03/11 ([message](https://github.com/Ganda15/rita-agent/blob/livrable-E1-v6/evidence/C8/envoi-documents-formateur-2026-11-03.md)). |
| p. 3, § 3.2, et p. 4, § 3.3, ligne API5 | sans la clé d'exercice, « ces routes répondent 503 » | Sans cette clé, ou avec une mauvaise clé, la route répond **403**. Elle répond **503** seulement quand le serveur n'a pas de clé d'exercice (absente ou de moins de 16 caractères) : les exercices sont alors désactivés ([`api/exercice.py`, lignes 36 à 45](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v3/api/exercice.py#L36-L45) ; [les deux tests](https://github.com/Ganda15/rita-agent/blob/livrable-E3-v3/tests/test_exercice.py#L83-L95)). |

## 3. Une phrase imprécise dans E4 {: #e4 }

Page 4, § 1.7, et page 16, § 7.3 : « spécifications des écrans 4 et 5 rétrospectives ». C'est vrai pour l'écran 5
(Tableau de bord). Pour l'écran 4 (Question), la première spécification a précédé l'écran : elle est versionnée le 15/10
([commit `e16ec77`](https://github.com/Ganda15/rita-agent/commit/e16ec77)), l'écran le 16/10
([commit `98177c2`](https://github.com/Ganda15/rita-agent/commit/98177c2)). Seuls les scénarios et l'accessibilité
ajoutés le 02/11 sont rétrospectifs. Le tableau du § 1.3 (page 2) et le premier point du § 1.7 le disent déjà.

## 📖 Glossaire {: #glossaire }

- **Tag** : étiquette Git posée sur une version du dépôt ; son lien montre toujours cette version.
- **Commit** : une version enregistrée du dépôt, désignée par un identifiant court.
- **Auto-évaluation** : mon statut pour chaque critère du référentiel : ✅ prouvé, ⚠️ à consolider, ❌ non fait.
- **403** : code HTTP « accès refusé » : la clé manque ou elle est fausse.
- **503** : code HTTP « service indisponible » : ici, la fonction n'est pas configurée.
- **Vigie** : script hors de l'API qui sonde le service et ouvre un ticket pour chaque signal en problème.
