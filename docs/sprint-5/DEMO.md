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
| Les onglets du navigateur, dans l'ordre | 1. tableau de bord (connecté avec la clé) ; 2. écran des questions `http://localhost:8011/question.html` (connecté) ; 3. les issues du dépôt ; 4. `docs/exploitation.md` (copie de lecture) ; 5. l'exécution N16 de la livraison de production (connecté à GitHub) | |
| PowerShell | dans `D:\KandaWork\RITA_PROJECT\rita-agent-sprint-5`, police agrandie | l'invite se termine par `rita-agent-sprint-5>` |

La copie redémarre à l'étape `revenir` : les mesures du tableau de bord repartent de zéro (« mesures depuis HH:MM »).

## Le déroulé

| Début | Durée | Segment | Ce qui est montré |
|---|---|---|---|
| 0:00 | 30 s | Introduction | ce qu'est RITA, pourquoi la surveiller, ce que le sprint 5 apporte |
| 0:30 | 110 s | Parcours principal | une question couverte, une question hors corpus, le tableau de bord |
| 2:20 | 90 s | Livraison | la livraison de la version courante sur la copie, `/health` avant et après |
| 3:50 | 210 s | Alerte déclenchée | la dérive simulée, l'issue ouverte par la vigie, le tableau de bord, l'action |
| 7:20 | 80 s | Documentation | `docs/exploitation.md` : la table des alertes, le diagnostic, le retour arrière |
| 8:40 | 60 s | Conclusion | ce qui est prouvé, et les limites |

Total : 580 secondes, soit 9 min 40 ; 20 secondes de marge. Si le temps manque, la trace Langfuse du parcours (15 s) saute la première.

### 0:00 · Introduction (30 s)

D'abord le concept, puis le cas d'usage, puis ce que le sprint apporte ; la technique vient ensuite, dans la démonstration.

**À dire** : « RITA aide un investisseur particulier à suivre ses valeurs cotées. Elle rassemble cinq sources : les cours
de bourse, les taux de change, des indicateurs économiques, et les articles de trois journaux économiques. Elle répond
toujours en citant ses sources, et refuse plutôt que d'inventer. »

**À dire** : « Le cas d'usage de ce sprint : une fois RITA en service, il faut savoir si elle va bien. Si le fournisseur
du modèle tombe, si quelqu'un l'attaque, ou si elle coûte trop cher, il faut le voir tout de suite et savoir quoi faire,
sans être développeur. »

**À dire** : « Ce que le sprint 5 apporte : un tableau de bord lisible par tous, une alerte qui dit quoi faire, et une
documentation qu'une autre personne peut suivre seule. Je le montre sur une copie de RITA, sur mon poste, pour pouvoir
provoquer des pannes sans toucher la production. »

### 0:30 · Parcours principal (110 s)

| Geste | Résultat attendu |
|---|---|
| Écran des questions : « Comment L'Oréal organise-t-elle sa division des produits professionnels ? » | « Réponse », environ 2 s ; « Sources citées » : [1] « L'Oréal présente l'organisation de sa division des produits professionnels », source `demonstration`, 16/09/2026 |
| Même écran : « Quelle est la recette de la tarte Tatin ? » | « Pas de réponse » ; motif : aucun article collecté ne traite de cette question (`OUT_OF_CORPUS`), sans appel au modèle |
| Onglet du tableau de bord, Actualiser | « Refus de sécurité » INCONNU : « Pas assez de questions pour juger (2 sur 10 nécessaires) » |

**À dire** : « Une réponse cite toujours sa source ; hors du corpus, RITA refuse au lieu d'inventer. Le tableau de
bord compte chaque appel, et quand il n'a pas assez de données, il dit INCONNU, jamais SAIN. »

**À dire, facultatif (15 s), en montrant la trace dans Langfuse** : « Chaque question laisse aussi une trace dans
Langfuse, sans son texte : son parcours, sa durée, son statut. Avant ce sprint, une seule alerte regardait ces traces,
sur les erreurs du fournisseur ; le sprint 5 ajoute les mesures, les seuils et le tableau de bord. »

Question de secours, si la première tarde : « Comment Airbus répartit-il ses chaînes d'assemblage entre ses sites ? »
(source attendue : « Airbus décrit l'organisation de ses chaînes d'assemblage », 10/09/2026).

### 2:20 · Livraison (90 s)

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
dans main déploie toute seule : c'est la livraison N16 qui a mis ce sprint en production, le 23/10. Je ne la rejoue
pas ici, pour ne pas toucher la production. »

L'exécution N16 (commit `845e3b3`, conclusion `success`, avec son job `deployer`), citée et pas rejouée, se montre dans
l'onglet 5 : `github.com/Ganda15/rita-agent/actions/runs/39983152061`. Le dépôt était privé lors de la démo : la page ne
s'ouvrait qu'une fois connecté avec un compte qui avait accès au dépôt. Depuis le 23/11/2026, il est public, et elle
s'ouvre sans connexion.

Le segment s'arrête là : un seul `deployer`. Le retour arrière se montre dans la documentation (segment 7:20), pas ici :
un `revenir` remettrait la copie sur l'ancienne version et fausserait la suite de la démonstration.

### 3:50 · Alerte déclenchée (210 s)

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

### 7:20 · Documentation (80 s)

| Geste | Ce qui est montré |
|---|---|
| Onglet de `docs/exploitation.md`, section « Les alertes : que faire » | la table : chaque signal, ses seuils, son action |
| Section « Diagnostiquer une panne » | les six étapes ; « Service rétabli » et « Alerte résolue », deux constats distincts |
| Section « Revenir à la version précédente » | la commande et ses limites : la base n'est pas restaurée, un second retour est refusé |

**À dire** : « La documentation se suit seule : une commande par bloc, le résultat attendu écrit dessous. Je l'ai
jouée sur la copie : une panne simulée, diagnostiquée avec la doc ; le service rétabli ; puis l'alerte résolue quinze
minutes plus tard. Les preuves sont dans le dépôt. »

### 8:40 · Conclusion (60 s)

**À dire** : « Ce qui est prouvé : les mesures, le tableau de bord, des seuils argumentés, la vigie et ses issues,
une panne diagnostiquée avec la doc, une livraison et un retour arrière vérifiés. Les limites, dites franchement : la
vigie de production se lance à la main, pas encore toutes les 15 minutes ; les seuils sont provisoires, écrits avant toute mesure de trafic
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
