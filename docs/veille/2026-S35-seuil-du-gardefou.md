# Veille S35 — Le seuil de 85 % du garde-fou RITA face à la littérature

**Semaine** : 2026-S35, du 24 au 30 août 2026 · **Période réellement balayée** : du 17 au 25 août (relevé du 25/08, voir `_candidats-2026-S35.md` ; l'étiquette portait cette fenêtre jusqu'au 03/10/2026, corrigée sans changer le contenu) · **Créneau tenu** : rédigée en rattrapage le 08/09/2026
**Thématique** : sécurité des agents LLM — injection de prompt

## Résumé en clair

Le garde-fou anti-injection de RITA bloque 70 % des tentatives d'attaque, sans jamais
bloquer une requête légitime (0 % de fausses alertes) — alors que l'objectif affiché est
85 %. Cette semaine, deux travaux de recherche montrent que 85 % n'est pas une norme
universelle : un outil utilisé en production (par Meta) obtient un résultat comparable.
Décision : RITA garde 85 % comme objectif, et assume 70 %/0 % comme un choix délibéré,
pas comme un échec. Limite reconnue : ce chiffre repose sur seulement 18 cas de test.

## Ce que j'ai lu cette semaine

| Source | Titre (texte de lien explicite) | Date de publication | Auteur |
|---|---|---|---|
| arXiv `cs.CR` (préprint) | [Confidently Wrong: Severity-Aware Calibration of Prompt-Injection Detectors under Attack Shift](https://arxiv.org/abs/2606.22659) | 21 juin 2026 | Md Anas Biswas |
| arXiv `cs.CR` (préprint) | [Evaluating Prompt Injection Defenses for Educational LLM Tutors: Security-Usability-Latency Trade-offs](https://arxiv.org/abs/2605.06669) | 29 mars 2026 | Alexandre Cristovão Maiorano |

## Analyse de fiabilité

| Source | Auteur identifié ? | Intérêt commercial ? | Confirmée ailleurs ? | Retenue ? |
|---|---|---|---|---|
| Confidently Wrong | Oui — Md Anas Biswas | Non, mais **préprint non relu par les pairs, auteur unique** | Non, isolée | Oui — comme signal, pas comme preuve |
| Educational LLM Tutors | Oui — Alexandre Cristovão Maiorano | Non, mais **préprint non relu par les pairs, auteur unique** | Non, isolée | Oui — les chiffres NeMo/Prompt Guard cités viennent de produits publics vérifiables |

**Information écartée cette semaine, et pourquoi** :
- **CASCADE** (arXiv, architecture à 3 étages, 61 % de rappel) — écartée : un troisième
  préprint proche des deux premiers n'ajoute pas d'argument nouveau, il dilue la note.
- **Simon Willison** (2 billets d'août sur un incident AISI et le vol de traces de
  raisonnement) — écartés : hors sujet de la question posée cette semaine (le seuil).
- **OWASP GenAI, NIST, CNIL, CERT-FR/ANSSI** — rien de neuf trouvé sur le seuil de
  détection cette semaine (sources vérifiées, aucune publication nouvelle sur le sujet).

## Ce que j'en retiens

1. Un chiffre de blocage seul ne veut rien dire sans son taux de fausses alertes associé —
   on atteint 100 % de blocage en refusant tout.
2. **Prompt Guard**, un outil publié par Meta et utilisé en production, atteint ~61,5 % de
   blocage avec 3,60 % de fausses alertes sur son propre jeu de test — un résultat proche
   ou inférieur à celui de RITA. Comparaison à prendre avec prudence : les jeux de test ne
   sont pas les mêmes, ce n'est pas un match direct.
3. Le seuil de RITA est calibré sur **18 cas fixes** (`evals/cas.py`) et verrouillé en
   intégration continue — solide pour repérer une régression, mais ne garantit rien face à
   des attaques qui ne ressemblent pas à ces 18 cas.

## ⭐ Ce que ça change dans RITA

| Constat | Action pour RITA | Fichier concerné | Fait ? |
|---|---|---|---|
| 85 % n'est pas une norme externe : c'est un objectif choisi par RITA, et 70 %/0 % est un point de fonctionnement défendable | Documenter ce choix comme décision assumée, pas comme échec à corriger | `ETAT.md`, `tests/test_evals.py` | ⬜ |
| Le seuil ne repose que sur 18 cas fixes, sans garantie hors de ce banc d'essai | Ajouter une note de limite connue, à surveiller pour une future itération du jeu de cas | `evals/cas.py` (docstring) | ⬜ |

## Question ouverte pour la semaine prochaine

Les PDF NIST AI 700-1 et AI 700-2 répondent en HTTP 200 mais leur contenu n'a pas pu être
lu par mes outils automatiques cette semaine. Ils décriraient une convention de mesure
« taux de blocage à taux de fausses alertes fixé » — à ouvrir et lire moi-même pour
vérifier si elle s'applique au garde-fou de RITA.

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Taux de faux positifs** | Part des requêtes légitimes bloquées à tort par le garde-fou |
| **Taux de blocage** (*rappel*) | Part des attaques effectivement détectées et bloquées |
| **Point de fonctionnement** | Le couple (taux de blocage, taux de fausses alertes) choisi délibérément — un chiffre seul ne veut rien dire |
| **Calibration** | Régler le seuil à partir duquel un score devient « bloqué », sur un jeu de cas donné |
| **Décalage de distribution** | Les attaques réelles ne ressemblent pas toujours à celles du jeu de test — le seuil calibré peut alors devenir faux sans prévenir |
| **`xfail` strict** | Test déclaré « attendu en échec » : il ne casse pas la suite, mais la casse s'il se met à réussir — on est prévenu du jour où le taux repasse au-dessus |
| **Préprint** | Article de recherche publié avant relecture par les pairs — une piste, pas une preuve |

---

### ✅ Contrôle d'accessibilité avant publication

- [x] un seul `#`, puis `##` sans niveau sauté
- [x] aucun lien nommé « ici » ou « cliquez ici », aucune URL nue
- [x] pas d'image dans cette note (règle du texte alternatif non applicable)
- [x] tableaux avec ligne d'en-tête, aucune cellule fusionnée
- [x] aucune information portée par la seule couleur
- [x] résumé en langage clair présent, 5 lignes
- [x] chaque terme technique défini + glossaire rempli
