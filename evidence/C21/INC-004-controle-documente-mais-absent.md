# INC-004 — Des contrôles décrits dans la documentation n'existaient pas dans le code

> ⚠️ **Ce n'est pas un bug, c'est un mode de défaillance du projet.** Cinq occurrences en neuf
> jours, sur cinq fichiers différents, sans lien technique entre elles. Devant un jury, c'est
> la fiche la plus utile des quatre : elle montre un défaut **systémique identifié par le
> projet lui-même**, avec sa contre-mesure.

| | |
|---|---|
| **Détecté le** | **17/08/2026** (1ʳᵉ occurrence), puis 4 autres jusqu'au **25/08** |
| **Sévérité** | **P1 pour deux d'entre elles** — un garde-fou de sécurité absent, un contrôle d'accessibilité absent |
| **Impact réel** | variable, détaillé ci-dessous. Le point commun : **aucune n'était visible**, ni en test, ni à l'exécution |
| **Commits** | `c7c8811`, `a7a3dba`, `52ad1ae` (correctif `tabindex`), et le 25/08 pour la 5ᵉ |
| **Issue / demande de fusion** | **aucune — commits directs sur `develop`** |

## 1. Ce qu'on a vu — cinq fois

| # | Date | Ce que la documentation affirmait | Ce que le code faisait |
|---|---|---|---|
| 1 | 17/08 | `guardrails/injection.py:9` **invoquait** un garde-fou de sortie (interdit AMF) | **le fichier n'existait pas** ; `api/main.py` diffusait le texte du modèle **sans aucun contrôle** |
| 2 | 17/08 | `db/importer.py` lisait sa configuration | **il ne chargeait pas le `.env`** — inutilisable hors du serveur d'API (`a7a3dba`) |
| 3 | 18/08 | un commentaire CSS annonçait `tabindex` + `role="region"` sur la zone défilable | **absents du HTML** — une personne au clavier ne voyait jamais la moitié droite du tableau |
| 4 | 24/08 | `ETAT.md` : *« Récurrence **en place** : tâche `veille-hebdo-securite-llm`, tous les lundis 09h00 »* | **aucune tâche de ce nom sur la machine** |
| 5 | 24/08 | `scripts/README-planification.md` décrivait sur **138 lignes** une collecte quotidienne à 19h00, journaux à l'appui | **tâche jamais installée, dossier `logs/` inexistant** — elle n'avait **jamais** tourné |

*(Une 6ᵉ occurrence a eu lieu le 25/08 sur `monitorage/fraicheur.py` — même cause que le n°2,
le `.env` non chargé. Elle est documentée dans `evidence/C20/preuve-fraicheur.md`.)*

## 2. Cause racine

**Cause technique** : aucune. Les cinq n'ont pas de mécanisme commun — un import manquant, un
fichier absent, un attribut HTML oublié, deux tâches planifiées jamais créées.

**Cause de conception — la seule vraie** : la documentation est écrite **au moment où l'on
décide** de faire la chose, pas au moment où on l'a faite. Elle décrit une **intention**, et
rien ne vient plus tard confronter cette intention au réel.

> **Le document devient la preuve à la place de la chose.**

Trois circonstances aggravantes, propres à ce projet :
1. **La documentation y est de très bonne qualité** — précise, argumentée, avec des chiffres.
   Plus elle est crédible, moins on pense à la vérifier.
2. **Les tests ne l'attrapent pas.** Le n°5 est passé sous **319 tests** et une intégration
   continue : aucun test ne vérifie qu'une tâche Windows existe.
3. **Le n°1 était pire qu'une absence de contrôle** : le code *appelait* le garde-fou, donc
   toute relecture rapide concluait qu'il existait.

## 3. Reproduction en développement

Chaque occurrence se reproduit par une **commande unique** — c'est précisément ce qui rend le
défaut évitable :

```
n°1  python -c "import guardrails.sortie"     -> ModuleNotFoundError
n°2  python -m db.importer                    -> OperationalError, port 5432 au lieu de 5433
n°3  grep -n "tabindex" frontend/*.html       -> aucun résultat
n°4  schtasks /query /tn "veille-hebdo-..."   -> aucune tâche de ce nom
n°5  ls logs/                                 -> le dossier n'existe pas
```

**Aucune de ces commandes ne prend plus de deux secondes.** Le coût de la vérification n'a
jamais été le problème.

## 4. Procédure de débogage

Il n'y a pas eu de débogage : **il n'y avait pas de symptôme.** Les cinq ont été trouvées en
**relisant la documentation avec l'intention de la vérifier** — trois lors d'une revue
dirigée, deux lors d'une reprise de session le 24/08.

| # | Hypothèse | Comment elle a été testée | Résultat |
|---|---|---|---|
| 1 | Ce que ce document affirme est vrai | exécuter la commande qui le prouverait | ❌ **cinq fois sur cinq** |
| 2 | Les tests auraient dû l'attraper | relecture de la couverture | ❌ aucun test ne franchit la frontière du code (tâches système, fichiers absents) |

## 5. Correction, étape par étape

Chaque occurrence a été corrigée **et** rendue vérifiable :

| # | Correction | Ce qui la rend vérifiable ensuite |
|---|---|---|
| 1 | `guardrails/sortie.py` écrit, câblé sur `/briefing` | `evals/mesurer_sortie.py` **mesure** le taux de blocage |
| 2 | `load_dotenv()` ajouté | l'exécution réelle échoue bruyamment si absent |
| 3 | `tabindex` + `role="region"` ajoutés au HTML | **test statique** dans `tests/test_frontend.py` qui lit le HTML |
| 4 | ⬜ **non corrigé** — la tâche n'a pas de script derrière elle. `ETAT.md` a été **corrigé pour cesser d'affirmer du faux** | — |
| 5 | tâche installée, **lancée immédiatement** | `logs/collecte-2026-08-24.log`, `Code de sortie : 0` |

⚠️ **Le n°4 est laissé ouvert délibérément** : plutôt que de fabriquer une tâche vide pour faire
disparaître la ligne rouge, le document dit maintenant la vérité et pose l'alternative
(automatiser, ou assumer une préparation manuelle). *Une contradiction visible vaut mieux
qu'une contradiction résolue en apparence.*

## 6. Vérification et non-régression

- **n°3** est le seul dont la non-régression soit **automatisable**, et elle l'est : le test
  lit le HTML et échoue si l'attribut disparaît. Le même principe a été réappliqué le 25/08 au
  bandeau de fraîcheur — 7 tests statiques vérifient que le front **fait** ce que ses
  commentaires **disent**.
- **n°1** est verrouillé par une mesure chiffrée, pas par une affirmation.
- **n°4 et n°5** relèvent de l'environnement d'exécution : aucun test ne peut les couvrir.
  Leur contre-mesure est procédurale (§7).

## 7. Ce que ça change pour la suite

**La règle adoptée, et elle a déjà servi cinq fois :**

> ***Rien n'est marqué ✅ dans `ETAT.md` sans qu'une commande de vérification ait été lancée et
> sa sortie collée.***

Appliquée les 24 et 25/08 : `pg_restore --list` pour la sauvegarde (8 tables), `Code de
sortie : 0` pour la collecte, `403 / 200` en HTTP réel pour la fraîcheur. Trois affirmations,
trois sorties de commande — **aucune formulation au futur**.

**Deux formulations à bannir des documents du projet**, parce que ce sont les marqueurs du
défaut :
- *« est en place »* → remplacer par la commande qui le prouve ;
- *« il suffit de »* → si c'était fait, on citerait le résultat.

**Pourquoi cette fiche a de la valeur devant un jury** : un projet qui ne signale aucune
faiblesse n'est pas crédible. Un projet qui identifie son propre mode de défaillance, le compte
(5 occurrences), en explique la cause de conception et pose une contre-mesure **vérifiable**
démontre exactement la compétence que C21 évalue — *résoudre*, pas *ne jamais casser*.
