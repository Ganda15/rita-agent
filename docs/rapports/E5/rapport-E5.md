<style>
.logo{ float:right; width:15mm; margin:7pt 0 2pt 12pt; }
.identite{ color:var(--ink-soft); font-size:9.4pt; }
.sommaire{ margin:9pt 0 2pt; padding:6pt 10pt 5pt; border:.5pt solid var(--rule); border-radius:2pt; }
.sommaire-titre{ font-family:Georgia,"Times New Roman",serif; font-weight:600; font-size:11pt; margin:0 0 4pt; }
.sommaire ol{ list-style:none; padding:0; margin:0; columns:2; column-gap:22pt; }
.sommaire li{ display:flex; justify-content:space-between; gap:8pt; margin:0 0 2pt; break-inside:avoid; font-size:9.4pt; }
.sommaire li a{ color:var(--ink); }
.sommaire li span{ color:var(--accent); font-weight:600; }
p, li{ orphans:3; widows:3; }
h2#glossaire + ul{ columns:2; column-gap:18pt; }
h2#criteres + p + table td:first-child{ width:53%; }
h2#preuves + table th:nth-child(1){ width:15%; } h2#preuves + table th:nth-child(2){ width:10%; }
h2#preuves + table th:nth-child(3){ width:25%; }
/* 07/11 : les couleurs du rapport E2 (choix du 06/11 sur le nuancier) : tableaux d'information en
   style A (en-tête marine, lignes zébrées, première colonne marine), titres en dégradé marine vers sarcelle, code
   coloré. L'espacement d'E2 n'est pas repris, pour garder le nombre de pages. */
:root{ --zebre:#F2F6FA; }
table thead th{ background:var(--marine); color:#fff; padding:2.5pt 5pt; }
table tbody tr:nth-child(even) td{ background:var(--zebre); }
table tbody td:first-child{ font-weight:600; color:var(--marine); }
td{ padding-top:2.5pt; padding-bottom:2.5pt; padding-left:5pt; }
table thead th code{ color:#fff; background:rgba(255,255,255,.16); border:none; }
body h1, body h2{ background:linear-gradient(90deg, #12395E, #14607F); color:#fff; }
body h1{ padding:2pt 10pt; }
body h2{ padding:1pt 10pt; }
body h3{ background:linear-gradient(90deg, #D6E6F7, #EEF5FC); color:#12395E; padding:1pt 9pt; }
pre{ background:#0F2A44; color:#E8EEF5; border:none; border-radius:4pt; padding:6pt 9pt; }
pre code{ color:inherit; background:none; }
code{ background:#E3F0F3; color:#0D4C5E; border-radius:2pt; }
/* 08/11 : mise en forme « luxe fintech » de la maquette E2 du 08/11 (formes seules, texte inchangé) : en-tête de
   tableau en bleus par colonne, cellules sur fond pâle sans zébrage, filets fins, sous-titres en bandeau uni avec barre
   marine, filets marine et sarcelle en bord de page (boîtes de marge de @page ; page 1 : sous le titre, sans filet haut). */
/* 08/11, après la maquette : bleus clairs des en-têtes assombris, texte blanc à 5:1 au moins (WCAG AA). */
table{ --rule:#C5D0DA; --rule-strong:#C5D0DA; }
table thead th:nth-child(1), table thead th.azure:nth-child(1), table thead th.claude:nth-child(1){ background:#0A2550; }
table thead th:nth-child(2), table thead th.azure:nth-child(2), table thead th.claude:nth-child(2){ background:#0066A3; }
table thead th:nth-child(3), table thead th.azure:nth-child(3), table thead th.claude:nth-child(3){ background:#007494; }
table thead th:nth-child(4), table thead th.azure:nth-child(4), table thead th.claude:nth-child(4){ background:#007B86; }
table thead th:nth-child(n+5), table thead th.azure:nth-child(n+5), table thead th.claude:nth-child(n+5){ background:#00798F; }
table thead th:nth-child(2):last-child{ background:#007494; }
table tbody tr td:not(.ok):not(.alerte){ background:#EEF2F6; }
table tbody tr td:first-child:not(.ok):not(.alerte){ background:#E6EEF5; }
body h3{ background:#D6E6F7; border-left:4px solid #12395E; padding-left:calc(9pt - 4px); }
@page{
  @top-left-corner{ content:""; border-left:3px solid #0B1F3A; border-top:2px solid #0B1F3A; background:linear-gradient(#1A7A8C, #1A7A8C) 0 0 / 100% 1px no-repeat, linear-gradient(#1A7A8C, #1A7A8C) 0 0 / 1px 100% no-repeat; }
  @top-center{ content:""; width:100%; height:1px; margin-bottom:auto; background:#1A7A8C; border-top:2px solid #0B1F3A; }
  @top-right-corner{ content:""; height:1px; margin-bottom:auto; background:#1A7A8C; border-top:2px solid #0B1F3A; }
  @left-top{ content:""; width:1px; margin-right:auto; background:#1A7A8C; border-left:3px solid #0B1F3A; }
  @left-middle{ content:""; width:1px; margin-right:auto; background:#1A7A8C; border-left:3px solid #0B1F3A; }
  @left-bottom{ content:""; width:1px; margin-right:auto; background:#1A7A8C; border-left:3px solid #0B1F3A; }
  @bottom-left-corner{ content:""; width:1px; margin-right:auto; background:#1A7A8C; border-left:3px solid #0B1F3A; }
}
@page :first{
  @top-left-corner{ content:none; } @top-center{ content:none; } @top-right-corner{ content:none; }
  @left-top{ border-left:0; width:4px; background:linear-gradient(#0B1F3A, #0B1F3A) 0 51.81pt / 3px 100% no-repeat, linear-gradient(#1A7A8C, #1A7A8C) 3px 51.81pt / 1px 100% no-repeat; }
}
</style>

<div><img class="logo" src="../E3/logo/rita-logo-marque.png" alt="Logo de RITA"></div>

# Rapport E5 : surveiller l'application et résoudre un incident (C20 et C21)

Projet fil rouge **RITA** · **Eramalingam Gandakumar** · Développeur en intelligence artificielle, RNCP 37827 · Simplon × Wild Code School · bloc de compétences 3, compétences C20 et C21 · version 1.1, 8 novembre 2026 · application de référence : commit `6f428d6` de `main`, en production le 07/11/2026 ; correctif de l'incident : PR #171 du 31/10/2026 · code et preuves versionnés : `Ganda15/rita-agent`, version figée au tag `livrable-E5-v6`
{: .identite }

> **En une minute.** Ce document est la documentation technique du monitorage de RITA, écrite pour la personne qui
> reprendrait son exploitation. Il dit ce qui est surveillé, à partir de quand on alerte et avec quels outils (C20),
> puis il déroule un incident réel, trouvé dans la chaîne d'alerte elle-même, de sa détection à sa correction
> versionnée (C21). Le contexte de RITA est présenté dans le rapport E1, le traçage des appels au modèle dans le
> rapport E3 (C11) : ce document décrit ce qui s'y ajoute pour surveiller l'application entière.

<div class="sommaire" role="navigation" aria-label="Sommaire">
<p class="sommaire-titre">Sommaire</p>
<ol>
<li><a href="#dispositif">1. Le dispositif en une vue</a><span>p. 1</span></li>
<li><a href="#signaux">2. Les signaux et leurs seuils</a><span>p. 1</span></li>
<li><a href="#outils">3. Pourquoi ces outils</a><span>p. 2</span></li>
<li><a href="#journaux">4. La journalisation et les données personnelles</a><span>p. 2</span></li>
<li><a href="#installer">5. Installer, configurer, lancer</a><span>p. 3</span></li>
<li><a href="#preuves">6. Les alertes ont fonctionné</a><span>p. 3</span></li>
<li><a href="#incident">7. L'incident INC-009</a><span>p. 4</span></li>
<li><a href="#limites">8. Les limites</a><span>p. 5</span></li>
<li><a href="#criteres">9. Les douze critères</a><span>p. 5</span></li>
<li><a href="#glossaire">Glossaire</a><span>p. 5</span></li>
</ol>
</div>

## 1. Le dispositif en une vue {: #dispositif }

Le monitorage, c'est la surveillance continue d'une application en service : on mesure, on compare à des seuils
écrits à l'avance, et on prévient quelqu'un quand un seuil est franchi. Celui de RITA a cinq parties, toutes dans la
version de production `6f428d6`.

| Partie | Où | Ce qu'elle fait |
|---|---|---|
| Les **compteurs** | dans l'API, [`monitorage/compteurs.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/monitorage/compteurs.py) | une observation par appel à `/briefing` et `/question` : route, résultat, motif, durée, jetons ; jamais de texte |
| Les **verdicts** | `GET /sante` ([`api/sante.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/api/sante.py), [`monitorage/signaux.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/monitorage/signaux.py), [`monitorage/seuils.json`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/monitorage/seuils.json)) | calcule chaque signal sur sa fenêtre et le classe : sain, attention, problème ou inconnu |
| Le **tableau de bord** | [`frontend/tableau-de-bord.html`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/frontend/tableau-de-bord.html) | affiche les verdicts de `/sante`, avec la clé de l'API ; s'actualise toutes les 30 s, suspendable depuis le 02/11 |
| La **vigie** | hors de l'API, [`monitorage/vigie.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/monitorage/vigie.py) | sonde `/health`, lit `/sante`, ouvre une issue `incident` par signal en problème et la ferme à la résolution écrite |
| Les **alertes Langfuse** | Langfuse Cloud, puis [`.github/workflows/alerte-incident.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/.github/workflows/alerte-incident.yml) | deux alertes sur les traces du modèle ; chacune ouvre ou commente une issue `incident` |

## 2. Les signaux et leurs seuils {: #signaux }

Les seuils sont écrits dans [`monitorage/seuils.json`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/monitorage/seuils.json) (version du 22/10/2026), chacun avec sa raison, l'action à mener
et la condition de résolution. Ils sont **provisoires** : écrits avant toute mesure du trafic réel, à relire sur des
données réelles. Pour les taux et le temps de réponse, sous le minimum de requêtes ou sans donnée, le verdict est « inconnu », jamais
« sain » ; la fraîcheur est « inconnue » quand la base ne répond pas.

| Signal | Mesure, fenêtre | Attention | Problème | Minimum |
|---|---|---|---|---|
| Le service répond | sonde de `/health` par la vigie | | 2 échecs à 10 s d'écart | |
| Réponses en erreur | part des résultats, 15 min | 10 % | 20 % | 5 requêtes |
| Refus de sécurité | part des résultats, 15 min | 15 % | 30 % | 10 requêtes |
| Temps de réponse | p95, 15 min | 10 s | 20 s | 5 requêtes |
| Coût estimé | 24 h disponibles | 1 € | 5 € | |
| Fraîcheur des cours | par valeur, en jours ouvrés | 2 ou 3 jours | plus de 3 jours | |
| Appels rejetés (403, 422, 429) | file à part, 15 min | 20 | 100 | |
| Langfuse : fournisseur en erreur | observations `ERROR`, 1 jour | | plus de 0 | |
| Langfuse : appel au modèle lent | p95 de `briefing-llm`, 1 jour | | plus de 15 000 ms | |

Le **p95** est la durée sous laquelle se trouvent 95 % des réponses. Le seuil de 20 % d'erreurs demande au moins
5 requêtes parce que le trafic de RITA est faible : une erreur sur cinq vaut déjà 20 %. Le seuil Langfuse de latence
a d'abord été écrit `15` en pensant à des secondes, alors que la mesure est en millisecondes : il a sonné à tort le
04/10 et a été corrigé à `15000` le jour même, sans changer la cible de quinze secondes
([`evidence/C11/preuve-alertes-2026-10-04.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/evidence/C11/preuve-alertes-2026-10-04.md)). Pour chaque signal, le guide d'exploitation dit quoi vérifier, quoi
faire et quand l'alerte est résolue ([`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/docs/exploitation.md), « Les alertes : que faire »).

## 3. Pourquoi ces outils {: #outils }

- **Une vigie hors de l'API** : une API arrêtée ne peut pas annoncer sa propre panne. Deux sondes à 10 secondes
  d'écart évitent une alerte sur un seul paquet perdu.
- **Une seule source de verdicts** : le tableau de bord et la vigie utilisent les verdicts calculés par `/sante`, ce
  qui évite de dupliquer les règles. La vigie contrôle aussi la disponibilité de l'API (`/health`).
- **Des compteurs en mémoire** : la production sert l'API avec un seul processus, donc un seul jeu de compteurs, sans
  base ni service de plus. Un verrou protège les appels simultanés, et les rejets ont leur propre file : 20 000 appels
  sans clé ne peuvent pas effacer les refus de sécurité déjà comptés (revue de sécurité du 22/10, commit `d8232b4`).
- **Langfuse Cloud, région UE, palier gratuit**, pour les traces du modèle (rapport E3) : Langfuse est configuré en
  région UE, conformément au choix d'hébergement des traces de RITA (registre RGPD, T3). Les conditions et garanties ont
  été examinées le 06/11 ; les exceptions contractuelles et les limites restantes sont documentées dans le registre.
  L'auto-hébergement a été écarté par la mesure (six composants, dont ClickHouse, sur un serveur
  de 4 Go déjà occupé). Le palier gratuit offre deux alertes, et ses canaux sont Slack, un webhook signé ou GitHub
  Actions, sans courriel.
- **Les issues GitHub comme outil de suivi** : les incidents vivent déjà dans le dépôt (fiches, PR, tests) ; une
  alerte y ouvre une fiche datée, et la boucle de C21 (issue, diagnostic, PR, post-mortem) commence d'elle-même.

## 4. La journalisation et les données personnelles {: #journaux }

Chaque requête reçoit un identifiant (`request_id`), renvoyé dans l'en-tête `X-Request-ID` de chaque réponse, erreurs
comprises, et repris dans les lignes du journal de l'API. Lorsqu'une trace Langfuse est produite, cet identifiant est
ajouté à ses métadonnées pour retrouver l'exécution correspondante. Format d'une ligne du journal ([`api/main.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/api/main.py)) :
`briefing servi : request_id=… ticker=… conforme_amf=… duree_ms=…` ; les refus portent leur motif
(`TENTATIVE_DETOURNEMENT`, `FUITE_BLOQUEE`, etc.). Chaque résultat est classé dans une catégorie métier (réponse, refus
de sécurité, refus de corpus, refus de qualité, erreur technique, rejet d'accès) : un motif inconnu compte comme
erreur technique, avec une ligne de journal, parce qu'une mesure inconnue n'est jamais verte.

**Ce qui n'est jamais enregistré** : les journaux applicatifs et les traces Langfuse de RITA n'enregistrent ni le
contenu des questions et réponses, ni les consignes envoyées au modèle (prompts), ni la clé API. Depuis le 20/10, les
traces conservent des métadonnées techniques : identifiant de requête, ticker, verdicts du garde-fou, modèle,
fournisseur, consommation et durées. Ces traitements sont
inscrits au registre RGPD ([`db/RGPD-registre-des-traitements.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/db/RGPD-registre-des-traitements.md)) : T3 pour les traces (Langfuse, région UE, actives
en production depuis le 21/10), T5 pour le journal des appels MCP (huit colonnes, purge à 90 jours), T8 pour les
questions (texte jamais conservé, vérifié par des tests).

## 5. Installer, configurer, lancer {: #installer }

La procédure complète est dans [`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/docs/exploitation.md) : installation avec ou sans Docker, clés, et les sections
« Les alertes : que faire » et « La vigie et les exercices ». L'essentiel :

| Outil | Dépendances et réglages | Lancer |
|---|---|---|
| Compteurs, `/sante`, tableau de bord | livrés avec l'API, rien à installer ; la clé `RITA_API_KEY` | ouvrir `/tableau-de-bord.html` et saisir la clé |
| Vigie | Python ; la clé `RITA_API_KEY` (environnement ou `.env` du dépôt) ; GitHub CLI, ci-dessous | `python -m monitorage.vigie --adresse <url>` (à blanc), puis `--github` |
| Traces | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` dans `.env` | actives dès que les clés sont présentes |
| Alertes Langfuse | dans l'interface Langfuse : adresse de déclenchement du dépôt, type `alerte-langfuse`, jeton gardé dans Langfuse | automatique ; essai par « Run workflow » |

**GitHub CLI pour la vigie** (le guide d'exploitation ne le décrit pas encore) : 1. installer, `winget install --id
GitHub.cli` ; 2. s'authentifier avec un compte collaborateur du dépôt, qui a le droit d'écrire des issues :
`gh auth login`, puis `gh auth status` ; 3. vérifier l'accès sans rien créer : `gh issue list -R Ganda15/rita-agent
--label incident --limit 1` ; 4. lancer la vigie à blanc. Les étiquettes `incident` et `E5`, posées par la vigie sur
chaque issue, doivent exister dans le dépôt.

Sans `--github`, la vigie affiche ce qu'elle ferait et n'envoie rien. Ses codes de sortie : 0 aucun signal en
problème, 1 au moins un problème, 2 `/sante` illisible. En production, la vigie est également programmée toutes les
trois heures par GitHub Actions. Le secret `RITA_API_KEY_VIGIE` fournit la clé au workflow. Premier passage planifié réussi le 07/11 à 21 h 52 UTC
([42417908976](https://github.com/Ganda15/rita-agent/actions/runs/42417908976)), code 0. Le tableau de bord de production répond à l'adresse
`https://178-104-184-125.sslip.io/tableau-de-bord.html` (vérifiée le 05/11 : HTTP 200).

## 6. Les alertes ont fonctionné {: #preuves }

| Issue | Date | Origine | Ce que cela prouve |
|---|---|---|---|
| [#71](https://github.com/Ganda15/rita-agent/issues/71) | 03/10 | essai manuel de la chaîne Langfuse vers GitHub | la chaîne ouvre une issue |
| [#77](https://github.com/Ganda15/rita-agent/issues/77) | 04/10 au 11/10 | deux alertes Langfuse, quatre déclenchements et quatre retours à OK | de vraies alertes, nées sur le poste : le 03/10, deux fournisseurs sans clé et un repli réussi ; le 10/10, une réponse de Mistral en blocs a fait échouer le garde-fou de sortie (corrigé le jour même, commit `2a7f18c`, sur une branche non fusionnée) |
| [#127](https://github.com/Ganda15/rita-agent/issues/127), [#128](https://github.com/Ganda15/rita-agent/issues/128), [#129](https://github.com/Ganda15/rita-agent/issues/129), [#131](https://github.com/Ganda15/rita-agent/issues/131) | 22 et 23/10 | vigie, copie locale, exercices | ouverture, commentaire « Service rétabli », fermeture à la résolution en 16 à 17 minutes |
| [#130](https://github.com/Ganda15/rita-agent/issues/130) | 23/10 | alerte Langfuse en production | vraie alerte, fausse alerte qualifiée : les erreurs venaient de l'exercice de la copie locale, qui envoyait ses traces au projet de la production |
| [#137](https://github.com/Ganda15/rita-agent/issues/137) | 24/10 | retour à OK de l'alerte de #130 | un défaut de la chaîne elle-même : l'incident INC-009 |
| [#230](https://github.com/Ganda15/rita-agent/issues/230) | 07/11 | vigie, copie de l'image de production (`6f428d6`), signal `service` | ouverture après deux sondes en échec, fermeture au retour de `/health` à 200 ; aucune panne en production ([preuve](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/evidence/C20/vigie-2026-11-07/README.md)) |

Un retour à OK ne prouve pas, à lui seul, une correction ; le 04/10, celui de la latence vient aussi du seuil corrigé.

## 7. L'incident INC-009 {: #incident }

**Déclenchement.** Le 23/10 à 08:30 UTC, l'alerte « fournisseur en erreur » ouvre #130 ; elle est fermée à la main à
09:48, fausse alerte qualifiée. Le 24/10 à 08:30, Langfuse envoie le retour à la normale de la même alerte, de gravité
`OK`. Le workflow ne trouve aucune issue ouverte sous ce titre et en crée une nouvelle, #137.

**Périmètre.** La chaîne d'alerte seulement : ni le service, ni les données, ni une alerte réelle ne sont touchés.
Mais un faux incident, resté sept jours sans traitement, pouvait faire croire à une nouvelle panne de fournisseur.

**Diagnostic.** Trouvé le 31/10 en relisant les issues `incident` ouvertes. Deux pistes écartées : une nouvelle
panne (le message dit « recovered ») et un doublon de Langfuse (identifiant et gravité différents). Cause : la gravité
était lue mais seulement affichée, et sans issue ouverte une issue était créée quelle que soit la gravité ; la chaîne
supposait qu'un incident reste ouvert jusqu'à son retour à OK.

**Reproduction en environnement de développement.** Les deux étapes du workflow, rejouées telles qu'elles sont
écrites, avec le message réel de #137 et un faux `gh` qui note les appels, dans un conteneur jetable (le poste n'a pas
`jq`), sans secret ni ticket créé : le message OK sans issue ouverte demande `issue create`. Réécrire la logique en
Python aurait testé un autre code que celui qui tourne : l'idée a été abandonnée.

**Résolution.** Le titre d'origine envoyé par Langfuse est conservé pour reconnaître le retour à la normale (gravité
`OK` ou titre « [OK] », ligne 78). La décision devient ([`.github/workflows/alerte-incident.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/.github/workflows/alerte-incident.yml), lignes 140 à 148,
commit `a57dccb`) :

```bash
if [ -n "$existante" ]; then
  echo "Issue #$existante déjà ouverte pour cette alerte : on commente."
  gh issue comment "$existante" --body-file corps.md
elif [ "$RETABLIE" = "oui" ]; then
  # INC-009 : un retour à la normale sans issue ouverte n'ouvre rien ; on le note dans le journal de l'exécution.
  echo "Retour à la normale sans issue ouverte pour cette alerte : aucune issue créée."
else
  gh issue create --title "$TITRE" --label incident --body-file corps.md
fi
```

Une issue ouverte est commentée, comme avant ; sans issue ouverte, un retour à OK ne crée plus rien et l'écrit dans le
journal de l'exécution ; une alerte crée l'issue, comme avant. Dans cette chaîne d'alerte Langfuse, la fermeture reste
manuelle : une décision humaine, justifiée.

**Tests en succès.** Le test qui empêche le défaut de revenir ([`tests/test_alerte_incident.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/tests/test_alerte_incident.py), lignes 225 à 228) :

```python
def test_un_retour_a_la_normale_sans_issue_ouverte_ne_cree_aucune_issue(etapes, tmp_path):
    """Le cas de #137 : l'incident a été fermé, puis le retour à la normale arrive. Rien à ouvrir."""
    appels = _rejouer(etapes, tmp_path, CHARGE_LANGFUSE_24_10_OK, issues_ouvertes=[])
    assert not any(a.startswith("issue create") for a in appels), f"un retour à OK a créé une issue : {appels}"
```

Il échouait avant le correctif (13 tests passent, 1 échoue) ; après, même conteneur et même fichier : **14 tests
passent**. Sur la PR #171, [l'intégration continue passe](https://github.com/Ganda15/rita-agent/actions/runs/41246397659) :
1 821 tests réussis, dont les quatre nouveaux.

**Versionnement et documentation.** Branche `fix/137-retour-a-la-normale`, commits `a57dccb` et `78957e0`,
[PR #171](https://github.com/Ganda15/rita-agent/pull/171) vers `develop`, puis
[PR #172](https://github.com/Ganda15/rita-agent/pull/172) vers `main`, en production le 01/11. Le débogage est écrit
[dans l'issue #137](https://github.com/Ganda15/rita-agent/issues/137#issuecomment-6549650079), le post-mortem dans
[`evidence/C21/INC-009-retour-a-la-normale-ouvre-un-incident.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/evidence/C21/INC-009-retour-a-la-normale-ouvre-un-incident.md), les journaux avant et après dans
[`evidence/C21/INC-009-reproduction/`](https://github.com/Ganda15/rita-agent/tree/livrable-E5-v4/evidence/C21/INC-009-reproduction).

Huit autres incidents ont leur fiche dans [`evidence/C21/`](https://github.com/Ganda15/rita-agent/tree/livrable-E5-v4/evidence/C21) ; seuls INC-005 et INC-009 ont suivi la chaîne complète
(issue, PR, post-mortem), les autres sont passés le plus souvent par un commit direct, chaque fiche le dit.

## 8. Les limites {: #limites }

- **Seuils provisoires**, jamais relus sur du trafic réel ; **compteurs remis à zéro** à chaque redémarrage de l'API.
- **La vigie planifiée dépend de GitHub** : le 07/11, trois déclenchements du workflow ont été observés pour sept
  créneaux prévus : deux arrêtés faute de secret, puis un passage planifié réussi à 21 h 52 UTC, 35 minutes après le
  créneau prévu ; la vigie de production n'a encore émis aucune alerte.
- **Deux règles de fermeture coexistent** : la vigie ferme son issue quand la résolution écrite est atteinte (#131 l'a
  été faute de requêtes), la chaîne Langfuse ne ferme jamais. L'écart est à trancher.
- **Exercice et production** ont partagé le même projet Langfuse (INC-006, #130) ; le 23/10, la copie testée est isolée
  sur `rita-copie-sprint5`, vérifié par l'API ([preuve](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/evidence/sprint-5/test-doc-et-repetitions-2026-10-23.md), l. 48). Vaut pour cette copie, pas pour tous les postes.
- **Aucune routine ne relit les issues `incident`** : le 07/11, #77 (depuis le 04/10) et #132 (vigie, copie locale,
  depuis le 23/10) sont encore ouvertes ; #137 l'est restée sept jours.
- **Le correctif d'INC-009 est sur `main` depuis le 01/11** (`922349d`), tests de non-régression verts. Au 07/11, le
  workflow GitHub d'alerte n'a pas tourné depuis le 24/10 : aucun retour à la normale réel observé depuis.

## 9. Les douze critères {: #criteres }

Mon auto-évaluation au 07/11/2026 ; les limites sont dites dans les lignes et au § 8.

| Critère | Statut | Preuve |
|---|---|---|
| C20.1 Métriques, seuils et valeurs d'alerte | ✅ | § 2 ; seuils provisoires, dits |
| C20.2 Arguments des choix d'outillage | ✅ | § 3 : un argument écrit pour chaque outil |
| C20.3 Outils installés, opérationnels en local a minima | ✅ | § 5 et 6 ; exercices locaux, production |
| C20.4 Journalisation intégrée aux sources | ✅ | § 4 ; `compteurs.py`, [`api/main.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E5-v4/api/main.py) |
| C20.5 Alertes configurées et en état de marche | ✅ | § 5 et 6 : vigie planifiée, #230 ; limites § 8 |
| C20.6 Installation et configuration documentées | ✅ | § 5, dont GitHub CLI |
| C20.7 Documentation communiquée dans un format accessible | ✅ | guide d'exploitation, format contrôlé le 31/10, envoyé le 03/11, réception confirmée le 04/11 ([`evidence/C8/`](https://github.com/Ganda15/rita-agent/tree/livrable-E5-v4/evidence/C8)) |
| C21.1 Causes identifiées | ✅ | § 7, post-mortem INC-009 |
| C21.2 Reproduit en environnement de développement | ✅ | § 7 ; `pytest-avant.txt` |
| C21.3 Débogage documenté dans l'outil de suivi | ✅ | issue #137, commentaire du 31/10 |
| C21.4 Chaque étape de la solution explicitée | ✅ | § 7, extraits ; post-mortem |
| C21.5 Solution versionnée par une demande de fusion | ✅ | [PR #171](https://github.com/Ganda15/rita-agent/pull/171), sur `main` depuis le 01/11 |

## 📖 Glossaire {: #glossaire }

- **Monitorage** : surveillance continue d'une application en service, avec des seuils écrits à l'avance.
- **Signal** : grandeur surveillée (taux d'erreurs, temps de réponse…), calculée sur une fenêtre de temps.
- **Seuil** : valeur à partir de laquelle un signal passe en attention ou en problème.
- **p95** : durée sous laquelle se trouvent 95 % des réponses.
- **Vigie** : programme qui surveille l'API de l'extérieur et ouvre ou ferme les issues d'incident.
- **Trace** : enregistrement d'un appel au modèle (durée, jetons, fournisseur, erreur), lu dans Langfuse.
- **Issue** : fiche de suivi dans GitHub ; l'étiquette `incident` marque celles des alertes.
- **Demande de fusion (PR)** : proposition de modification relue et testée avant d'entrer dans une branche.
- **Post-mortem** : fiche écrite après un incident : ce qui s'est passé, pourquoi, comment c'est corrigé, la suite.
- **Retour à la normale (OK)** : message qui dit que la condition d'une alerte n'est plus remplie au moment du calcul.
- **Conteneur jetable** : environnement isolé, créé pour une exécution puis supprimé.
- **`jq`** : outil en ligne de commande qui filtre du JSON.
