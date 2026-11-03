# Budget de RITA : dépenses, valeur du travail et coût de fonctionnement

> **Version du 03/11/2026.** Montants relevés sur les justificatifs reçus par courriel, ou déclarés par Era quand la
> pièce n'a pas été retrouvée (c'est dit ligne par ligne). Aucun montant n'est inventé : une case « à lire » attend
> sa pièce. Les factures ne vont jamais dans Git ; ce fichier dit seulement de
> quelle pièce vient chaque montant.
>
> **Décision d'Era du 03/11**, après le retour écrit du formateur du même jour : le budget se présente en **trois
> montants séparés, jamais additionnés**. Les dépenses ([le tableau](#le-tableau)), la valeur du travail au taux
> journalier ([deuxième montant](#deuxième-montant--la-valeur-du-travail-au-tjm)) et le fonctionnement par mois
> ([troisième montant](#troisième-montant--le-fonctionnement-par-mois)). Elle remplace la décision du 28/10 (pas de
> taux journalier, développement compté en argent réellement dépensé). Le livret E1 v6 porte une ligne « Budget » avec
> les trois montants ; le détail est ici.

## Les règles de comptage

1. **Facturé, payé et consommé par RITA sont trois colonnes distinctes.** Une facture émise n'est pas un paiement
   confirmé ; un achat de crédits n'est pas une consommation de RITA.
2. **Payé et estimé ne se mélangent pas.** Un calcul au prix public est une estimation, dite comme telle.
3. **Une pièce ne se compte qu'une fois**, dans une seule catégorie. Un rappel de paiement n'est pas une dépense de plus.
4. **Une période d'abonnement est la période facturée**, lue sur la pièce, pas une date de commit.
5. **OpenRouter se dit en trois chiffres, jamais additionnés** : les recharges payées, le crédit restant, et la
   consommation des clés de RITA.
6. **Un plafond n'est pas une dépense** : le budget GitHub Actions porté à 5 $ le 23/10 est une limite.
7. **Une alerte de coût prévient, elle ne coupe pas** : les seuils de 1 € et 5 € de la vigie ne plafonnent aucune facture.
8. **Les devises d'origine sont gardées** (€ ou $), sans conversion.
9. **Un abonnement qui sert aussi à autre chose que RITA est compté en entier** : convention choisie par Era le
   31/10, déclarée comme telle, pas une mesure d'usage. Elle ne vaut pas pour les recharges OpenRouter, qui couvrent
   le compte entier : pour elles, seule la consommation des clés de RITA compte.
10. **Les dépenses de RITA commencent en mai 2026** (décision d'Era du 31/10) : un reçu OpenRouter du 26/04 (6,96 $)
   est exclu.

## Le tableau

| Poste | Catégorie | Période | Facturé | Payé | Consommé par RITA | Affectation à RITA | Pièce |
|---|---|---|---|---|---|---|---|
| Hetzner CPX32 (`ubuntu-8gb-nbg1-1`), jamais utilisé, supprimé le 19/08 | infrastructure inutilisée | mai, juin, juillet, août (partiel) | **64,76 €** (17,39 + 17,39 + 17,39 + 12,59) | à vérifier pour août (prélèvement d'août en échec, puis rappels) | sans objet | achat pour RITA (Era, 28/10) | factures Hetzner du 02/06, 02/07, 02/08 et 02/09 |
| Hetzner CX23, production depuis le 19/08 | exploitation | août (partiel), septembre | **10,59 €** (3,40 + 7,19) | à vérifier | entièrement | RITA | factures Hetzner du 02/09 et du 19/10 ; octobre pas encore facturé |
| OpenRouter, recharges payées | développement | 01/05 au 04/10 | | **425,04 $** (11 reçus) | voir ligne suivante | compte partagé possible | reçus OpenRouter du 01/05 au 04/10 ; celui du 26/04 (6,96 $) est exclu, avant le début de RITA |
| OpenRouter, crédit restant | (information) | au jour du relevé | | | non relevé | | page des crédits OpenRouter |
| OpenRouter, consommation des clés de RITA | développement | 01/05 au 31/10 | | | **0,97 $** (0,718 « project rita » + 0,253 « RITA » + 0,000132 « RITA APP ») | RITA, d'après le nom des trois clés | relevé d'Era du 03/11 dans l'activité OpenRouter (mesure « Total Usage », regroupée par clé, cumul sur la période) ; d'abord un usage gratuit, puis ces appels payants ; un appel de RITA passé sous une clé partagée resterait à identifier |
| Mistral, abonnement Pro | développement | 10/10 au 09/11 | 17,99 € | **17,99 €** (10 € prépayés, puis 7,99 €) | consommation API des essais non isolée | comptée en entier (convention) | reçu Mistral de 10 €, facture Mistral du 10/10 de 7,99 € |
| GitHub Pro | développement | 03/10 au 02/11 | | **4,00 $** | sans objet | RITA : activé le 03/10 pour protéger `main` côté serveur (`CHANGELOG.md`, entrée du 03/10 ; `evidence/C19/preuve-protection-main-2026-10-03.md`) | reçu GitHub du 03/10 |
| GitHub Copilot Pro | développement | 14/10 au 02/11 | | **6,45 $** | sans objet | compté en entier (convention) | reçu GitHub du 14/10 |
| GitHub Actions, minutes au-delà du quota gratuit | développement (part de la CI) | octobre | à lire | aucune pièce trouvée | | RITA | facturation GitHub ; le plafond de 5 $ n'est pas une dépense |
| Abonnement Claude (code, revue des pull requests) | développement | mai à octobre (6 mois) | 20 € par mois | **120 €** déclarés | sans objet | compté en entier (convention) | déclaration d'Era du 31/10 ; pièce non retrouvée dans cette messagerie |
| Abonnement OpenAI utilisé pour Codex (relecture des pull requests depuis le 19/09) | développement | septembre et octobre (2 mois) | 23 € par mois | **46 €** déclarés | sans objet | compté en entier (convention) | déclaration d'Era du 31/10 ; pièce non retrouvée dans cette messagerie |
| Azure AI Foundry, `gpt-5.4` | exploitation | depuis le 03/10 | 0 € déclaré | 0 € déclaré | | RITA | déclaration d'Era du 31/10, non vérifiée sur le portail (gestion des coûts) |
| Langfuse, palier gratuit ; sources de données ; HTTPS, `sslip.io` | exploitation | | 0 € | 0 € | | RITA | gratuité documentée dans le projet ; facturation des comptes non contrôlée |

**Estimé, pour mémoire (pas une pièce)** : le banc C7 du 03/10, au prix public d'OpenRouter, revient à environ
0,68 $ sur ses cinq passages (`evidence/C7/preuve-benchmark-2026-10-03.md`). Ces appels ont été payés par les crédits
OpenRouter : ils ne s'ajoutent pas.

## Ce qui n'est pas chiffré

- **Le matériel** (le poste de développement) et les **frais indirects** (électricité, connexion) : hors chiffrage.
- **La durée réelle du travail** : elle n'est pas mesurée. Le deuxième montant repose sur une estimation, dite comme
  telle.

## Les sous-totaux, et le total provisoire

Recensés au 31/10 : montants facturés, payés, relevés ou déclarés selon le poste (voir le tableau), pas encore « consommés par RITA » :

| Catégorie | Postes | Montant |
|---|---|---|
| Développement | Claude 120 € (déclarés), OpenAI 46 € (déclarés), Mistral Pro 17,99 € (payés) | **183,99 €** |
| Développement | GitHub Pro 4,00 $ et Copilot Pro 6,45 $ (payés) | **10,45 $** |
| Développement | consommation OpenRouter des trois clés de RITA (relevé du 03/11) | **0,97 $** |
| Infrastructure inutilisée | Hetzner CPX32, mai à août (facturés) | **64,76 €** |
| Exploitation | Hetzner CX23, août et septembre (facturés) ; Azure 0 € déclaré | **10,59 €** |
| **Total recensé au 31/10, provisoire** | | **259,34 € et 11,42 $** (10,45 $ + 0,97 $), frais à confirmer |

Ce total mêle des montants facturés (Hetzner), payés (Mistral, GitHub), relevés (OpenRouter) et déclarés par Era
sans pièce retrouvée (Claude et OpenAI, 166 €) : il n'est pas entièrement justifié. Pour information, hors total :
les recharges OpenRouter du compte entier, 425,04 $ de mai à octobre, ne s'ajoutent pas ; seule la consommation des
clés de RITA compte.

**Le total reste provisoire** : le paiement de la facture Hetzner d'août (prélèvement d'abord en échec) est à
confirmer, la facture d'octobre du CX23 n'est pas encore émise, et les minutes GitHub Actions au-delà du quota n'ont
pas de pièce. Ce premier montant ne s'additionne pas avec les deux suivants.

## Deuxième montant : la valeur du travail au TJM

Ce montant n'est pas une dépense : personne ne l'a payé. Il dit ce que le travail aurait coûté s'il avait été
facturé, pour donner l'ordre de grandeur du projet. Il ne s'ajoute pas aux 259,34 € et 11,42 $.

| Élément | Valeur | D'où il vient |
|---|---|---|
| Journées de travail | **63** | estimation d'Era du 03/11, pas une mesure. Pour repère, Git compte 60 jours distincts avec au moins un commit du 14/05 au 31/10, toutes branches (`git log --all --format=%ad --date=short`, dates uniques) : il date l'activité, il ne compte ni les heures ni le travail sans commit (lecture, conception, oraux) |
| Taux journalier (TJM) | **400 € HT** | bas de la fourchette « TJM Ingénieur IA / Prompt Engineer Junior (0-2 ans) 2026 : 400-550€/jour », hors taxes (« par jour (HT) » sur la même page), du [simulateur de travail-industrie.com](https://travail-industrie.com/simulateur-tjm/data-ia/ingenieur-ia/junior), consulté le 03/11 ; profil junior, en reconversion. C'est la seule hypothèse ajustable de ce fichier |
| **Valeur du travail** | **25 200 € HT** | 63 × 400 € HT ; environ 491 h à 39 h par semaine de cinq jours (63 × 7,8 h) |

## Troisième montant : le fonctionnement par mois

Un **scénario**, pas une mesure : ce que coûterait un mois d'exploitation à un volume fixé, pour 30 jours.

| Poste | Hypothèse | Par mois | Source |
|---|---|---|---|
| Serveur Hetzner CX23 | une machine porte l'API et PostgreSQL (`docker-compose.yml:15`, « comme en production ») | **7,19 €** TTC | facture Hetzner du 19/10 (septembre) |
| Briefings | 10 par jour, soit 300 × 0,0047 $ | **1,41 $** | prix public Azure de `gpt-5.4` relevé le 03/10 : `docs/rapports/E2/rapport-E2.md:232`, `evidence/C7/preuve-benchmark-2026-10-03.md:128` |
| Questions | 5 par jour, soit 150 × 0,006 $ | **0,90 $** | hypothèse : le coût d'une génération de production lue dans Langfuse le 21/10, environ 1 000 jetons (`docs/rapports/E3/rapport-E3.md:233`) ; une question n'a pas été mesurée à part |
| Langfuse, sources de données, HTTPS | palier gratuit | 0 | voir le tableau |
| **Total** | | **7,19 € et environ 2,31 $** | |

Sur la ressource Azure du projet, le modèle est déclaré à 0 € (ligne Azure du tableau) : les 2,31 $ disent ce que
coûteraient les appels au prix public, pas une facture.

## L'évolution prévue avant le jury : une clé par client (C5)

**Au 03/11/2026** : une seule clé d'API partagée (`X-API-Key`, variable `RITA_API_KEY`), 403 sans elle (`api/main.py:208`).
Révoquer la clé coupe tout le monde.

**Prévu avant le jury** : une clé par client, révocable seule. Test d'acceptation : après la révocation de la clé du
client A, A reçoit **403** et le client B garde son accès (**200**). Estimation : **1 à 2 journées**, soit **400 à
800 € HT** au TJM de 400 € HT. Ce coût n'entre dans aucun des trois montants : c'est un travail à venir.

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **TTC** | toutes taxes comprises : le montant réellement payé, TVA incluse |
| **HT** | hors taxes : un montant avant TVA ; un TJM se donne d'habitude hors taxes |
| **TJM** | taux journalier moyen : prix d'une journée de travail facturée ; ici 400 € HT, pour le deuxième montant |
| **Scénario** | calcul à partir d'un volume choisi d'avance (ici 10 briefings et 5 questions par jour) ; ce n'est pas une mesure |
| **Révocation** | retrait d'une clé d'accès : elle cesse d'ouvrir l'API, sans toucher aux autres clés |
| **Recharge** | crédit acheté d'avance chez un fournisseur, consommé ensuite par les appels |
| **Quota gratuit** | part d'un service offerte chaque mois ; au-delà, l'usage est facturé |
| **Plafond de dépense** | limite fixée par l'utilisateur ; ce n'est pas une somme payée |
| **Prix public** | tarif affiché par le fournisseur ; sert à estimer, pas à prouver une dépense |
| **Affectation** | part d'une dépense attribuée à RITA, selon une règle déclarée |
