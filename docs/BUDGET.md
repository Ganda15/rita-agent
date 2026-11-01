# Budget de RITA : dépenses financières, hors valorisation du travail personnel

> **Version du 31/10/2026.** Montants relevés sur les justificatifs reçus par courriel, ou déclarés par Era quand la
> pièce n'a pas été retrouvée (c'est dit ligne par ligne). Aucun montant n'est inventé : une case « à lire » attend
> sa pièce. Les factures ne vont jamais dans Git ; ce fichier dit seulement de
> quelle pièce vient chaque montant. Décisions d'Era du 28/10 : pas de taux journalier (TJM), le développement se
> compte en argent réellement dépensé ; le livret E1 ne porte que trois lignes (« Budget financier »,
> « Fonctionnement », « Contraintes »), le détail est ici.

## Les règles de comptage

1. **Facturé, payé et consommé par RITA sont trois colonnes distinctes.** Une facture émise n'est pas un paiement
   confirmé ; un achat de crédits n'est pas une consommation de RITA.
2. **Payé et estimé ne se mélangent pas.** Un calcul au prix public est une estimation, dite comme telle.
3. **Une pièce ne se compte qu'une fois**, dans une seule catégorie. Un rappel de paiement n'est pas une dépense de plus.
4. **Une période d'abonnement est la période facturée**, lue sur la pièce, pas une date de commit.
5. **OpenRouter se dit en trois chiffres, jamais additionnés** : les recharges payées, le crédit restant, et la
   consommation de la clé de RITA.
6. **Un plafond n'est pas une dépense** : le budget GitHub Actions porté à 5 $ le 23/10 est une limite.
7. **Une alerte de coût prévient, elle ne coupe pas** : les seuils de 1 € et 5 € de la vigie ne plafonnent aucune facture.
8. **Les devises d'origine sont gardées** (€ ou $), sans conversion.
9. **Un abonnement qui sert aussi à autre chose que RITA est compté en entier** : convention choisie par Era le
   31/10, déclarée comme telle, pas une mesure d'usage. Elle ne vaut pas pour les recharges OpenRouter, qui couvrent
   le compte entier : pour elles, seule la consommation de la clé de RITA compte.
10. **Les dépenses de RITA commencent en mai 2026** (décision d'Era du 31/10) : un reçu OpenRouter du 26/04 (6,96 $)
   est exclu.

## Le tableau

| Poste | Catégorie | Période | Facturé | Payé | Consommé par RITA | Affectation à RITA | Pièce |
|---|---|---|---|---|---|---|---|
| Hetzner CPX32 (`ubuntu-8gb-nbg1-1`), jamais utilisé, supprimé le 19/08 | infrastructure inutilisée | mai, juin, juillet, août (partiel) | **64,76 €** (17,39 + 17,39 + 17,39 + 12,59) | à vérifier pour août (prélèvement d'août en échec, puis rappels) | sans objet | achat pour RITA (Era, 28/10) | factures Hetzner du 02/06, 02/07, 02/08 et 02/09 |
| Hetzner CX23, production depuis le 19/08 | exploitation | août (partiel), septembre | **10,59 €** (3,40 + 7,19) | à vérifier | entièrement | RITA | factures Hetzner du 02/09 et du 19/10 ; octobre pas encore facturé |
| OpenRouter, recharges payées | développement | 01/05 au 04/10 | | **425,04 $** (11 reçus) | voir ligne suivante | compte partagé possible | reçus OpenRouter du 01/05 au 04/10 ; celui du 26/04 (6,96 $) est exclu, avant le début de RITA |
| OpenRouter, crédit restant | (information) | au jour du relevé | | | à lire | | page des crédits OpenRouter |
| OpenRouter, consommation de la clé de RITA | développement | à lire | | | à lire | RITA | activité OpenRouter filtrée sur la clé de RITA |
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

- **Le travail personnel** : non valorisé financièrement ; sa durée totale n'est pas mesurée.
- **Le matériel** (le poste de développement) et les **frais indirects** (électricité, connexion) : hors chiffrage.

## Les sous-totaux vérifiés, et le total

Vérifiés sur pièces au 31/10 (montants facturés ou payés, pas encore « consommés par RITA ») :

| Catégorie | Postes | Montant |
|---|---|---|
| Développement | Claude 120 € (déclarés), OpenAI 46 € (déclarés), Mistral Pro 17,99 € (payés) | **183,99 €** |
| Développement | GitHub Pro 4,00 $ et Copilot Pro 6,45 $ (payés) | **10,45 $** |
| Développement | consommation OpenRouter de la clé de RITA | **à lire** |
| Infrastructure inutilisée | Hetzner CPX32, mai à août (facturés) | **64,76 €** |
| Exploitation | Hetzner CX23, août et septembre (facturés) ; Azure 0 € déclaré | **10,59 €** |
| **Total recensé au 31/10, provisoire** | | **259,34 € et 10,45 $**, hors consommation OpenRouter de RITA et frais à confirmer |

Ce total mêle des montants facturés (Hetzner), payés (Mistral, GitHub) et déclarés par Era sans pièce retrouvée
(Claude et OpenAI, 166 €) : il n'est pas entièrement justifié. Pour information, hors total : les recharges OpenRouter du compte entier, 425,04 $ de mai à octobre, ne s'ajoutent
pas ; seule la consommation de la clé de RITA compte.

**Le total reste incomplet** tant que la consommation OpenRouter de RITA n'est pas lue. Le paiement de la facture
Hetzner d'août (prélèvement d'abord en échec) est à confirmer, et la facture d'octobre du CX23 n'est pas encore émise. Les sous-totaux ci-dessus ne s'additionnent pas en un « budget de RITA » :
les recharges OpenRouter couvrent le compte entier.

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **TTC** | toutes taxes comprises : le montant réellement payé, TVA incluse |
| **TJM** | taux journalier moyen : prix d'une journée de travail ; ici, non utilisé |
| **Recharge** | crédit acheté d'avance chez un fournisseur, consommé ensuite par les appels |
| **Quota gratuit** | part d'un service offerte chaque mois ; au-delà, l'usage est facturé |
| **Plafond de dépense** | limite fixée par l'utilisateur ; ce n'est pas une somme payée |
| **Prix public** | tarif affiché par le fournisseur ; sert à estimer, pas à prouver une dépense |
| **Affectation** | part d'une dépense attribuée à RITA, selon une règle déclarée |
