# Sprint 5 : le scénario de la démo (10 minutes)

**Prototype local du sprint 5** : la démonstration se fait sur la copie de RITA lancée sur le poste
(`http://localhost:8011`, voir [docs/exploitation.md](../exploitation.md)). Elle couvre les trois exigences du
critère 6 de la grille de l'atelier 5 : le parcours principal, une livraison, une alerte déclenchée. Les questions
ci-dessous ont été vérifiées sur la copie le 22/10/2026 ; le résultat attendu est écrit sous chaque geste.

## Avant la démo (10 minutes avant)

| À vérifier | Commande ou geste | Attendu |
|---|---|---|
| Docker Desktop est lancé | `docker version` | une ligne `Server` |
| La démonstration de l'atelier 2 est arrêtée (port 8011) | `docker stop rita-api-demo-20261015-atelier rita-postgres-demo-20261015-atelier` | les deux noms, ou « No such container » s'ils sont déjà arrêtés |
| La dernière version est construite | `C:\Python314\python.exe scripts\copie_sprint5.py deployer` | `déployée, /health annonce <commit courant>` |
| La copie tourne sur la version précédente (pour montrer une vraie livraison pendant la démo) | `C:\Python314\python.exe scripts\copie_sprint5.py revenir` | `revenue à <version précédente>` |
| Aucune issue de la vigie n'est ouverte | `gh issue list -R Ganda15/rita-agent --state open --label incident` | aucune ligne « Incident : vigie (prototype local) » |
| Aucun exercice de panne | le tableau de bord, sans bandeau | |
| Les onglets du navigateur, dans l'ordre | 1. tableau de bord (connecté avec la clé) ; 2. écran des questions `http://localhost:8011/question.html` (connecté) ; 3. les issues du dépôt ; 4. `docs/exploitation.md` (copie de lecture) ; 5. l'exécution N15 de la livraison de production (connecté à GitHub) | |
| PowerShell | dans `D:\KandaWork\RITA_PROJECT\rita-agent-sprint-5`, police agrandie | l'invite se termine par `rita-agent-sprint-5>` |

La copie redémarre à l'étape `revenir` : les mesures du tableau de bord repartent de zéro (« mesures depuis HH:MM »).

## Le déroulé

| Début | Durée | Segment | Ce qui est montré |
|---|---|---|---|
| 0:00 | 20 s | Introduction | la vigie du prototype local, en une phrase |
| 0:20 | 110 s | Parcours principal | une question couverte, une question hors corpus, le tableau de bord |
| 2:10 | 90 s | Livraison | la livraison de la version courante sur la copie, `/health` avant et après |
| 3:40 | 210 s | Alerte déclenchée | la dérive simulée, l'issue ouverte par la vigie, le tableau de bord, l'action |
| 7:10 | 80 s | Documentation | `docs/exploitation.md` : la table des alertes, le diagnostic, le retour arrière |
| 8:30 | 60 s | Conclusion | ce qui est prouvé, et les limites |

Total : 570 secondes, soit 9 min 30 ; 30 secondes de marge.

### 0:00 · Introduction (20 s)

**À dire** : « Sprint 5 : la vigie. RITA est surveillée de l'extérieur : sept signaux, des seuils argumentés, une alerte
par signal liée à une action, et une documentation qu'un tiers suit seul. C'est un prototype local : la production n'est
pas touchée. »

### 0:20 · Parcours principal (110 s)

| Geste | Résultat attendu |
|---|---|
| Écran des questions : « Comment L'Oréal organise-t-elle sa division des produits professionnels ? » | « Réponse », environ 2 s ; « Sources citées » : [1] « L'Oréal présente l'organisation de sa division des produits professionnels », source `demonstration`, 16/09/2026 |
| Même écran : « Quelle est la recette de la tarte Tatin ? » | « Pas de réponse » ; motif : aucun article collecté ne traite de cette question (`OUT_OF_CORPUS`), sans appel au modèle |
| Onglet du tableau de bord, Actualiser | « Refus de sécurité » INCONNU : « Pas assez de questions pour juger (2 sur 10 nécessaires) » |

**À dire** : « Une réponse cite toujours sa source ; hors du corpus, RITA refuse au lieu d'inventer. Le tableau de
bord compte chaque appel, et quand il n'a pas assez de données, il dit INCONNU, jamais SAIN. »

Question de secours, si la première tarde : « Comment Airbus répartit-il ses chaînes d'assemblage entre ses sites ? »
(source attendue : « Airbus décrit l'organisation de ses chaînes d'assemblage », 10/09/2026).

### 2:10 · Livraison (90 s)

| Geste | Résultat attendu |
|---|---|
| `git log --oneline -1` | le commit à livrer |
| `C:\Python314\python.exe scripts\copie_sprint5.py deployer` | une quinzaine de secondes (image en cache) ; `déployée, /health annonce <ce commit> ; version précédente gardée : <l'ancienne>` |
| `C:\Python314\python.exe scripts\copie_sprint5.py etat` | `version courante : <ce commit>` ; `version precedente : <l'ancienne>` |
| Onglet du tableau de bord, Actualiser | « mesures depuis HH:MM » : la nouvelle version vient de démarrer |

**À dire, pendant `deployer`** : « La livraison construit l'image du commit, relance la copie, et vérifie que
`/health` annonce bien ce commit ; sinon, elle échoue sans rien changer. La version d'avant est gardée pour un retour
arrière. »

**À dire, juste après `etat`, en montrant l'onglet 5** : « En production, la livraison est automatique : chaque fusion
dans main déploie toute seule, comme la livraison N15 du 21/10. Je ne la rejoue pas ici, pour ne pas toucher la
production. »

L'exécution N15 (commit `3c35398`, conclusion `success`, avec son job `deployer`), citée et pas rejouée, se montre dans
l'onglet 5 : `github.com/Ganda15/rita-agent/actions/runs/39671479884`. Le dépôt est privé : la page ne s'ouvre qu'une
fois connecté avec un compte qui a accès au dépôt.

Si le temps le permet : `C:\Python314\python.exe scripts\copie_sprint5.py revenir` (environ 6 s), qui relance l'image
précédente sans la reconstruire et vérifie le commit et l'image ; puis `deployer` de nouveau.

### 3:40 · Alerte déclenchée (210 s)

| Geste | Résultat attendu |
|---|---|
| `C:\Python314\python.exe -m monitorage.exercer derive` | 12 lignes `HTTP 200 refus TENTATIVE_DETOURNEMENT`, environ 90 s ; `jetons ajoutés : 0` |
| `C:\Python314\python.exe -m monitorage.vigie --adresse http://localhost:8011 --github` | `ouverte : Incident : vigie (prototype local) « refus_securite »` ; `code 1` |
| Onglet du tableau de bord, Actualiser | « Refus de sécurité » PROBLÈME, 12 sur 12 (100 %), avec « Que faire » |
| Onglet des issues : l'issue ouverte | l'heure, le signal, le verdict, la valeur, le seuil, le pourquoi, le lien vers l'action, la résolution |
| L'action écrite dans la doc (« Alerte : refus de sécurité », rubrique « Vérifier ») : la commande ci-dessous | au moins 12 lignes `statut=refus motif=TENTATIVE_DETOURNEMENT`, chacune avec son `request_id`, jamais le texte de la question |

```powershell
cmd /c "docker logs --since 15m rita-api-s5 2>&1" | Select-String "statut=refus motif=TENTATIVE_DETOURNEMENT|motif=INTENTION_INTERDITE|motif=FUITE_BLOQUEE"
```

**À dire, pendant les 90 s de la dérive** : « J'envoie les six prompts hostiles du jeu de test, deux fois, à 8 par
minute pour laisser de la place aux autres appels. Le seuil : 30 % de refus de sécurité sur 15 minutes, avec au moins
10 requêtes, parce qu'une hausse de refus signale une attaque, ou un garde-fou qui bloque de vraies questions. Ces
refus arrivent avant le modèle : zéro jeton consommé. »

**À dire, devant l'issue** : « La vigie tourne hors de l'API : une API arrêtée ne peut pas annoncer sa propre panne.
Une issue par signal, jamais de doublon ; elle se fermera seule, avec un commentaire, quand les refus sortiront de la
fenêtre de 15 minutes. Ici, la lecture des refus montre des prompts hostiles connus : les garde-fous ont fait leur
travail. »

### 7:10 · Documentation (80 s)

| Geste | Ce qui est montré |
|---|---|
| Onglet de `docs/exploitation.md`, section « Les alertes : que faire » | la table : chaque signal, ses seuils, son action |
| Section « Diagnostiquer une panne » | les six étapes ; « Service rétabli » et « Alerte résolue », deux constats distincts |
| Section « Revenir à la version précédente » | la commande et ses limites : la base n'est pas restaurée, un second retour est refusé |

**À dire** : « La documentation se suit seule : une commande par bloc, le résultat attendu écrit dessous. Je l'ai
jouée sur la copie : une panne simulée, diagnostiquée avec la doc ; le service rétabli ; puis l'alerte résolue quinze
minutes plus tard. Les preuves sont dans le dépôt. »

### 8:30 · Conclusion (60 s)

**À dire** : « Ce qui est prouvé : les mesures, le tableau de bord, des seuils argumentés, la vigie et ses issues,
une panne diagnostiquée avec la doc, une livraison et un retour arrière vérifiés. Les limites, dites franchement : c'est
un prototype local, la production n'a pas de vigie ; les seuils sont provisoires, écrits avant toute mesure de trafic
réel ; la livraison de la copie est lancée par une commande. »

## Plan B

| Ce qui arrive | Ce que je fais |
|---|---|
| Azure ne répond pas pendant le parcours principal | c'est une vraie panne : la montrer avec « Diagnostiquer une panne », étapes 1, 2 et 4 (motif `FOURNISSEUR_INDISPONIBLE`, puis le type d'erreur, dans le journal) ; la démonstration du critère 4 remplace le parcours |
| La construction de l'image tarde | lancer `deployer` avant le chronomètre et l'annoncer ; montrer `etat` et `/health` pendant le segment |
| GitHub ne répond pas | lancer la vigie sans `--github` : elle dit « ouvrirait l'issue » ; montrer l'issue #128 du 22/10 comme preuve |
| Docker Desktop ou la copie ne démarre pas | montrer les captures `evidence/sprint-5/captures/copie-1` à `copie-3` et le fichier de preuves `evidence/sprint-5/preuves-copie-2026-10-22.md` |
| « Trop de demandes » (429) | la limite est de 10 appels par minute, partagée : attendre une minute avant la question suivante |

## Après la démo

L'issue « refus_securite » se ferme au plus tôt 15 minutes après le dernier refus. Attendre ce délai, plus une minute,
puis :

```powershell
C:\Python314\python.exe -m monitorage.vigie --adresse http://localhost:8011 --github
```

Attendu : `fermée : Incident : vigie (prototype local) « refus_securite »`, puis `passage terminé, code 0`.
