# Veille S36 — L'incident Claude Code, et LongGuard qui confirme le choix des expressions régulières

**Semaine** : 2026-S36, du 31 août au 6 septembre 2026 · **Période réellement balayée** : du 24 au 31 août (relevé du 31/08, voir `_candidats-2026-S36.md` ; l'étiquette portait cette fenêtre jusqu'au 03/10/2026, corrigée sans changer le contenu) · **Créneau tenu** : rédigée en rattrapage le 08/09/2026
**Thématique** : sécurité des agents LLM — injection de prompt

## Résumé en clair

Un chercheur a montré fin août qu'on peut faire exécuter du code caché à Claude Code en lui
demandant simplement de résumer un site web — et le garde-fou de l'outil a ensuite empêché
de nettoyer l'infection détectée. RITA n'exécute aucun code et n'a aucun outil : ce risque
précis ne la concerne pas directement. La leçon compte quand même pour son propre garde-fou
de sortie : un contrôle mal placé peut empêcher une réaction, pas seulement échouer à
protéger. Un préprint publié la même semaine confirme par ailleurs un choix déjà fait par
RITA : un garde-fou fondé sur un modèle perd plus de la moitié de sa détection sur un texte
long, ce que des expressions régulières évitent.

## Ce que j'ai lu cette semaine

| Source | Titre (texte de lien explicite) | Date de publication | Auteur |
|---|---|---|---|
| embracethered.com | [Breaking Claude Code Opus 5 Auto Mode with Indirect Prompt Injection](https://embracethered.com/blog/posts/2026/breaking-claude-code-opus-5-and-automode/) | 27 août 2026 | Johann Rehberger |
| simonwillison.net | [Breaking Claude Code Opus 5 Auto Mode](https://simonwillison.net/2026/Aug/27/breaking-claude-code-opus-5-auto-mode/) | 27 août 2026, mise à jour 30 août | Simon Willison |
| The Register | [Researcher shows how Claude Code can be tricked simply by asking it to summarize a website](https://www.theregister.com/research/2026/08/28/researcher-shows-how-claude-code-can-be-tricked-simply-by-asking-it-to-summarize-a-website/5293372) | 28 août 2026 | rédaction The Register |
| arXiv `cs.CR` (préprint) | [LongGuard: Mechanistic Analysis and Training-Free Mitigation of Long-Context Failure in Safety Guardrails](https://arxiv.org/abs/2608.27580) | 27 août 2026 | Ziyang Chen, Xing Wu, Songlin Hu |

## Analyse de fiabilité

| Source | Auteur identifié ? | Intérêt commercial ? | Confirmée ailleurs ? | Retenue ? |
|---|---|---|---|---|
| Johann Rehberger | Oui — chercheur connu pour ses travaux sur l'injection indirecte | Non, blog personnel | Oui — reprise par Willison et The Register | Oui |
| Simon Willison | Oui — a créé le terme *prompt injection* en 2022 | Non, blog personnel | Source de synthèse indépendante | Oui |
| The Register | Oui — rédaction identifiée | Non — presse, aucun produit de sécurité à vendre | Confirme Rehberger et Willison | Oui |
| LongGuard | Oui — 3 auteurs nommés | Non, mais **préprint non relu par les pairs** | Non, isolé | Oui — comme signal cohérent avec un choix déjà pris, pas comme preuve |

**Mentionnés brièvement, sans approfondir cette semaine** :
- **DreamGuard** (arXiv, garde-fou d'exécution à « modèle de monde ») — vise des agents qui
  enchaînent des actions avec des outils ; RITA n'en est pas là.
- **CNIL** — mise à jour de son outil de traçabilité des modèles open source (26 août) —
  hors sujet injection de prompt, lien indirect seulement avec la chaîne de dépendances.

## Ce que j'en retiens

1. RITA n'exécute aucun code et n'a aucun outil (fait établi en S33/S34) : le vecteur précis
   de l'incident Claude Code (archive décompressée, script masquant un module) ne s'applique
   pas directement.
2. La leçon qui reste utile : un garde-fou peut lui-même produire un effet nuisible en
   bloquant la réaction plutôt que l'attaque — pertinent pour `guardrails/sortie.py`.
3. LongGuard confirme le choix déjà fait par RITA : un garde-fou par expressions régulières
   ne perd pas en performance sur un texte long, contrairement à un garde-fou fondé sur un
   modèle (perte mesurée de plus de 50 % dans ce préprint) — un argument de plus contre un
   passage à un classifieur.

## ⭐ Ce que ça change dans RITA

| Constat | Action pour RITA | Fichier concerné | Fait ? |
|---|---|---|---|
| Un garde-fou mal placé peut bloquer la réaction à une compromission, pas seulement échouer à la prévenir | Vérifier que la logique *fail-closed* de `guardrails/sortie.py` ne pourrait jamais empêcher une action corrective | `guardrails/sortie.py` | ⬜ |
| LongGuard confirme que les expressions régulières restent le bon choix face à un texte long (page scrapée en entier) | Documenter ce choix comme argumenté, avec la référence LongGuard | `guardrails/injection.py`, `ETAT.md` | ⬜ |

## Question ouverte pour la semaine prochaine

LongGuard propose un correctif sans réentraînement (détection par tronçons, +22 % annoncé) —
vaut-il la peine de l'évaluer sur `guardrails/injection.py`, ou les 9 motifs regex
suffisent-ils tant qu'aucune régression n'est mesurée sur les 18 cas de `evals/cas.py` ?

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Injection indirecte** | Instruction hostile cachée dans une page web ou un flux que l'agent lit tout seul |
| **Adjoint égaré** (*confused deputy*) | Un composant de confiance est manipulé pour agir avec ses propres privilèges, sans instruction explicite |
| **Mode « auto »** | Réglage où un agent exécute des actions sans confirmation à chaque étape |
| **Fail-closed** | En cas de doute, le garde-fou refuse de laisser passer, plutôt que de laisser passer par défaut |
| **Dilution de l'attention** | Dans un texte long, le passage dangereux « pèse » moins dans le calcul du modèle, qui finit par ne plus le voir |
| **Détection par tronçons** | Découper un texte long en morceaux analysés séparément, pour contrer la dilution de l'attention |
| **Garde-fou par expression régulière** | Garde-fou qui compare le texte à des formes connues, comme `guardrails/injection.py` — par opposition à un garde-fou **par modèle** |
| **Préprint** | Article de recherche publié avant relecture par les pairs — une piste, pas une preuve |

---

### ✅ Contrôle d'accessibilité avant publication

- [x] un seul `#`, puis `##` sans niveau sauté
- [x] aucun lien nommé « ici » ou « cliquez ici », aucune URL nue
- [x] pas d'image dans cette note
- [x] tableaux avec ligne d'en-tête, aucune cellule fusionnée
- [x] aucune information portée par la seule couleur
- [x] résumé en langage clair présent, 5 lignes
- [x] chaque terme technique défini + glossaire rempli
