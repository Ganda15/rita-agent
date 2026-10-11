# Veille S41 : les détecteurs d'injection réussissent le test sur lequel ils sont entraînés

**Semaine** : 2026-S41, du 05/10 au 11/10 · **Créneau** : lundi 05/10 non tenu ; relevé le 11/10, note rédigée en rattrapage le 11/10
**Thématique** : sécurité des agents LLM, injection de prompt

## Résumé en clair

Un filtre anti-injection peut être très bien noté sur un banc d'essai et rater
presque tout sur un autre. Un article d'octobre a retesté 15 filtres publiés sur
trois jeux d'essai : le classement ne se retrouve pas d'un jeu à l'autre. La cause
n'est pas le hasard : pour les deux filtres dont les données d'entraînement sont
publiques, les bons scores viennent d'un entraînement qui ressemble au test. RITA est
directement concernée : son filtre
et ses premiers cas de test ont été écrits le même jour, et les trois cas écrits
après coup contre le filtre sont exactement ceux qu'il rate.

## Ce que j'ai lu cette semaine

| Source | Titre (texte de lien explicite) | Date de publication | Auteur |
|---|---|---|---|
| arXiv | [Passing the Test You Trained On: Re-evaluating Prompt-Injection Detectors for LLM Agents](https://arxiv.org/abs/2610.03448) | 2 octobre 2026 (v1) | Zhuowen Liu (JAIST) |

## Analyse de fiabilité

| Source | Auteur identifié ? | Intérêt commercial ? | Confirmée ailleurs ? | Retenue ? |
|---|---|---|---|---|
| arXiv 2610.03448 (candidat 4) | Oui : Zhuowen Liu, JAIST | Rien repéré | Partiellement : conclusions convergentes avec un autre préprint du relevé S41, RAG-PIBench ([arXiv 2610.08571](https://arxiv.org/abs/2610.08571)) | Oui |

Réserve : auteur unique, notoriété non établie (pas de page institutionnelle
trouvée). Les chiffres sont cités tels que l'auteur les rapporte ; rien n'est
répliqué indépendamment.

**Information écartée cette semaine, et pourquoi** : le relevé S41 proposait six
candidats ; je n'en retiens qu'un ici. Le relevé écarte aussi deux préprints pour
intérêt commercial (BRANCH et CounterSteer, voir `_candidats-2026-S41.md`).
Une précision sur mon propre dépôt : la mesure du 29/07 (100 % sur 7 cas) a sa
preuve dédiée (`evidence/C5/`) ; le 70 % sur 10 cas figure dans `evidence/C10/`
(scan du 20/09) et `evidence/C17/` (revue du 03/10), mais la mesure du 17/08
elle-même n'a pas de fiche datée.

## Ce que j'en retiens

1. Même filtre, même point de fonctionnement (1 % de faux positifs) : PIGuard
   détecte 95,1 % des injections de la moitié test de BIPIA, mais 2,1 % de celles
   d'AgentDojo (AD-Matched). La corrélation de classement entre les deux jeux est
   quasi nulle (τ de Kendall = 0,01). Au seuil par défaut (0,5), le même filtre
   signale 29,5 % des sorties d'outils saines d'AgentDojo, et 59,8 % des tâches
   auraient au moins une sortie saine signalée.
2. Une cause et un biais de méthode, documentés par l'auteur : PIGuard a été entraîné
   sur 1 116 entrées complètes de BIPIA, le test ressemble donc à l'entraînement ; et
   le seuil à 1 % est réglé sur le jeu bénin qui sert aussi à l'évaluation, ce qui
   rend tous les chiffres optimistes (« which favors the detectors », § 4.3).
3. Limites déclarées : environnements simulés (YAML/JSON synthétiques) et attaques
   figées, non adaptatives : les taux de détection sont des bornes supérieures
   (§ 6). À mon avis, l'étude mesure la détection par le filtre, pas le
   comportement de l'agent face à une injection passée.

## ⭐ Ce que ça change dans RITA

| Constat | Action pour RITA | Fichier concerné | Fait ? |
|---|---|---|---|
| Le filtre d'injection (9 motifs) et ses 7 premiers cas de test sont nés dans le même commit (29/07, c1ee404) : les cas calquent les motifs un à un. La preuve C5 le disait déjà : « 100 % / 0 % sur ce jeu de cas n'est pas un exploit : le jeu est circulaire. » | Re-mesurer sur la branche develop et consigner le résultat dans une fiche datée (la mesure du 17/08 n'en a pas ; le 70 % figure dans evidence/C10 et evidence/C17) | evals/cas.py, evidence/C5/mesure-garde-fou-injection.md | ⬜ |
| Les 3 cas adverses écrits le 17/08 contre les motifs (c7c8811, branche develop) sont exactement les 3 ratés : 7 attaques sur 10 bloquées, 0 faux positif sur 8, sur 18 cas. Le commentaire ajouté ce jour-là dans evals/cas.py l'avait formulé avant l'article : « le 100 % mesurait la couverture des motifs, pas la sécurité. » | Garder un lot de test disjoint des motifs, renouvelé à chaque incident, jamais utilisé pour les régler ; publier les deux chiffres toujours ensemble, avec la taille de l'échantillon (7/10, intervalle ≈ 35–93 %) | evals/cas.py, guardrails/injection.py | ⬜ |

## Question ouverte pour la semaine prochaine

Quel lot de contenus bénins représentatifs de nos vraies sources (articles RSS,
champs extraits des pages par scraping) pour mesurer le taux de faux positifs là où le filtre sera réellement
branché (première règle pratique de l'auteur) ?

## 📖 Glossaire

| Terme | En clair |
|---|---|
| Faux positif | Un contenu normal signalé comme attaque ; à l'échelle d'une tâche, cela peut la bloquer. |
| Point de fonctionnement | Le seuil choisi pour le filtre. Ici 1 % de faux positifs, sauf mention contraire : les 29,5 % et 59,8 % sont au seuil par défaut (0,5). |
| Jeu de test disjoint | Des cas de test jamais utilisés pour écrire ou régler le filtre ; le contraire du « jeu circulaire » mesuré le 29/07. |
| Bornes supérieures | Des chiffres qui ne peuvent qu'être revus à la baisse en conditions réelles, ici parce que les attaques sont figées et les environnements simulés. |

### ✅ Contrôle d'accessibilité avant publication

- [ ] un seul `#`, puis `##` / `###` sans niveau sauté
- [ ] aucun lien nommé « ici » ou « cliquez ici », aucune URL nue
- [ ] texte alternatif sur chaque image
- [ ] tableaux avec ligne d'en-tête, aucune cellule fusionnée
- [ ] aucune information portée par la seule couleur
- [ ] résumé en langage clair présent, 5 lignes maximum
- [ ] chaque terme technique défini + glossaire rempli