# Planifier la collecte quotidienne

> **Pourquoi ce fichier existe** — C1 demande de « **pérenniser** la collecte des données ».
> Un script qu'on lance à la main ne pérennise rien. Cette page décrit comment RITA se
> collecte tout seul, et comment vérifier qu'il l'a fait.

---

## 1. Ce que fait la tâche

Chaque soir à **19h00**, Windows lance `scripts/collecte-quotidienne.cmd`, qui exécute les
cinq étapes du pipeline :

| Étape | Source | Ce qu'elle met à jour |
|---|---|---|
| `ecb` | Banque centrale européenne | taux de change du jour |
| `cotations` | yfinance | les séances manquantes des **111 valeurs** |
| `rss` | 3 flux d'actualité + Google News par entreprise | articles du jour |
| `scraping` | Boursorama | cours de séance de 3 valeurs |
| `indexation` | ChromaDB (ajoutée le 02/09) | ré-indexe le corpus d'articles pour le RAG — **en dernier**, pour indexer ce que `rss` vient d'écrire |

**19h00 et pas plus tôt** : la Bourse de Paris clôture à 17h35, et les cours définitifs ne
sont disponibles qu'ensuite. Lancer à 17h donnerait des clôtures provisoires — exactement
le défaut mesuré sur la séance du 29/07, où la base disait 466,80 contre 467,95 réels.

---

## 2. Installer la tâche

⚠️ **Cette commande crée une tâche planifiée sur ta machine.** À lancer **toi-même**, dans
un terminal, après l'avoir lue.

```powershell
schtasks /create /tn "RITA - collecte quotidienne" /tr "D:\KandaWork\RITA_PROJECT\rita-agent\scripts\collecte-quotidienne.cmd" /sc daily /st 19:00 /f
```

| Morceau | Ce qu'il veut dire |
|---|---|
| `/create` | créer une tâche |
| `/tn "..."` | son nom, tel qu'il apparaîtra dans le Planificateur |
| `/tr "..."` | le programme à lancer |
| `/sc daily` | fréquence : tous les jours |
| `/st 19:00` | heure de lancement |
| `/f` | remplacer une tâche du même nom si elle existe |

**Aucun droit administrateur n'est requis** : la tâche s'exécute sous ton compte utilisateur.

---

## 2 bis. Sans fenêtre — la parade posée le 18/09/2026

**Ce qui s'est passé.** Du 13 au 17/09, quatre collectes sur sept se sont arrêtées dans les
dix premières secondes, le journal se terminant par `^C`. Diagnostic (mesuré, pas supposé) :
poste fixe sans batterie, aucun arrêt ni veille dans le journal Système à 19 h, et une tâche
**interactive, non cachée** — donc, chaque soir, une **console noire s'affichait à l'écran
pendant une minute**. `^C` est la trace qu'une console laisse quand on la ferme ou qu'on y
presse Ctrl+C. La cause la plus probable est une main sur la fenêtre. Non prouvable :
l'historique du Planificateur était désactivé.

**La parade.** La tâche ne lance plus le `.cmd` directement, mais un PowerShell caché qui
le démarre **sans fenêtre** et **remonte son code de sortie**. Le `.cmd` n'est pas modifié.

```powershell
$a = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -WindowStyle Hidden -Command "$p = Start-Process -FilePath ''D:\KandaWork\RITA_PROJECT\rita-agent\scripts\collecte-quotidienne.cmd'' -WindowStyle Hidden -PassThru -Wait; exit $p.ExitCode"'
```

```powershell
Set-ScheduledTask -TaskName "RITA - collecte quotidienne" -Action $a
```

| Morceau | Ce qu'il veut dire |
|---|---|
| `-WindowStyle Hidden` (deux fois) | la fenêtre de PowerShell, puis celle du `.cmd`, restent invisibles |
| `-PassThru -Wait` | attendre la fin de la collecte et garder la main sur le processus |
| `exit $p.ExitCode` | rendre au Planificateur le code du `.cmd`, pour que « Dernier résultat » reste vrai |
| `''…''` | un guillemet simple à l'intérieur d'une chaîne à guillemets simples |

**Vérifié le 18/09 à 21:11** : `schtasks /run` → aucune fenêtre, `Etapes reussies : 5/5`,
`Code de sortie : 0`, `LastTaskResult 0`. Au plus, un cadre PowerShell clignote une fraction
de seconde au démarrage.

**Ce qui a été écarté, et pourquoi.** Le mode « exécuter même si l'utilisateur n'est pas
connecté » sans mot de passe (S4U) supprimerait aussi la fenêtre, mais Windows le **refuse
aux comptes Microsoft** (`Accès refusé`, même en administrateur) — et `kanda` en est un.
Le mode avec mot de passe stockerait le mot de passe Microsoft dans la tâche : écarté.

**Reste à faire** — activer l'historique du Planificateur, pour que la prochaine coupure
laisse une trace. Dans un PowerShell **administrateur** :

```powershell
wevtutil set-log Microsoft-Windows-TaskScheduler/Operational /enabled:true
```

---

## 3. Vérifier qu'elle est bien installée

```powershell
schtasks /query /tn "RITA - collecte quotidienne" /v /fo LIST
```

Regarde trois lignes : **Prochaine exécution**, **Dernier résultat** (`0` = succès) et
**État** (`Prêt`).

## 4. La lancer tout de suite, sans attendre 19h

```powershell
schtasks /run /tn "RITA - collecte quotidienne"
```

## 5. La supprimer

```powershell
schtasks /delete /tn "RITA - collecte quotidienne" /f
```

---

## 6. Lire ce qui s'est passé

Un fichier par jour, dans `logs/` (dossier **exclu de Git** — il peut contenir des noms de
valeurs détenues) :

```powershell
Get-Content "D:\KandaWork\RITA_PROJECT\rita-agent\logs\collecte-2026-08-03.log" -Tail 30
```

Sortie attendue :

```
  taux_change (BCE)            lues    5 | ecrites    5 | rejetees   0
  cotations (yfinance)         lues  333 | ecrites  333 | rejetees   0
      - seances du 2026-07-29 au 2026-07-31
  article (RSS)                lues   28 | ecrites   12 | rejetees   0
  cours scrapes (Boursorama)   lues    3 | ecrites    3 | rejetees   0

  Etapes reussies : 4/4   Duree : 41.2 s
```

---

## 7. ⚠️ Ce que la planification ne garantit PAS

Une tâche planifiée s'exécute — elle ne garantit pas que **les données arrivent**.

| Cas | Ce qui se passe | Ce que tu vois |
|---|---|---|
| L'ordinateur est éteint à 19h | la tâche est **sautée** (et **pas rattrapée** au réveil : `StartWhenAvailable` vaut `False`) | rien dans les journaux ce jour-là |
| Quelqu'un ferme la console de la collecte | les étapes restantes **n'ont pas lieu** — cas des 13, 14, 16, 17/09 | le journal du jour se termine par `^C`, sans `Etapes reussies` — plus possible depuis le 18/09 (§2 bis) |
| yfinance ne répond pas | l'étape échoue, **les autres continuent** | `!! cotations ECHEC` |
| Jour férié boursier | 0 séance récupérée | `lues 0` — **normal**, pas une panne |

C'est pourquoi la vraie sécurité n'est pas la planification mais une **requête de
fraîcheur** — savoir dire « ma donnée la plus récente a N jours ». C'est le chantier **C**,
pas encore fait.

---

## 7 bis. Rattraper une période manquée (ajouté le 18/09/2026)

Quand des soirs ont sauté, le pipeline sait remonter dans le temps pour **deux** de ses
sources — pas pour les autres :

| Étape | Rattrapable ? | Comment |
|---|---|---|
| `ecb` | oui | l'API BCE accepte une plage de dates (`startPeriod`/`endPeriod`) |
| `rss` | **entreprises seulement** | Google News accepte `after:`/`before:` dans la requête ; les trois flux généraux n'ont que 20–30 items du jour |
| `cotations` | inutile | déjà incrémentale : elle comble seule l'écart depuis la dernière séance |
| `scraping` | non, et sans intérêt | cours intraday éphémères |

D'abord en simulation (rien n'est écrit), une fenêtre **un jour plus large** de chaque côté
que le trou (les bornes de Google News sont floues d'un jour ; le dédoublonnage absorbe) :

```powershell
cd D:\KandaWork\RITA_PROJECT\rita-agent
```

```powershell
C:\Python314\python.exe -X utf8 -m pipelines.ingest --etapes ecb,rss --du 2026-09-12 --au 2026-09-18 --simulation
```

Puis pour de vrai, avec l'indexation en dernier pour que le RAG voie les nouveaux articles :

```powershell
C:\Python314\python.exe -X utf8 -m pipelines.ingest --etapes ecb,rss,indexation --du 2026-09-12 --au 2026-09-18
```

Rejouable sans risque : taux et cotations en `ON CONFLICT DO UPDATE`, articles dédoublonnés
par lien **et** par (titre, jour). Exécuté le 18/09/2026 : 25 taux, 156 articles, index 1 038.

---

## 8. Tester avant d'installer

Lance-le une fois en **simulation** — rien n'est écrit en base :

```powershell
cd D:\KandaWork\RITA_PROJECT\rita-agent
C:\Python314\python.exe -X utf8 -m pipelines.ingest --etapes cotations --simulation
```

Puis une fois pour de vrai, sur la seule étape des cotations :

```powershell
C:\Python314\python.exe -X utf8 -m pipelines.ingest --etapes cotations
```

---

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Tâche planifiée** | Un programme lancé automatiquement par Windows à heure fixe |
| **`schtasks`** | La commande Windows qui crée et gère ces tâches |
| **Code de sortie** | Nombre renvoyé par un programme ; `0` = tout s'est bien passé |
| **Simulation** | Le pipeline calcule tout mais n'écrit rien en base |
| **Incrémental** | Ne récupérer que ce qui manque, pas tout retélécharger |
| **Fraîcheur** | L'âge de la donnée la plus récente |
