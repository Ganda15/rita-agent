# Planifier la collecte quotidienne

> **Pourquoi ce fichier existe** — C1 demande de « **pérenniser** la collecte des données ».
> Un script qu'on lance à la main ne pérennise rien. Cette page décrit comment RITA se
> collecte tout seul, et comment vérifier qu'il l'a fait.

---

## 1. Ce que fait la tâche

Chaque soir à **19h00**, Windows lance `scripts/collecte-quotidienne.cmd`, qui exécute les
quatre étapes du pipeline :

| Étape | Source | Ce qu'elle met à jour |
|---|---|---|
| `ecb` | Banque centrale européenne | taux de change du jour |
| `cotations` | yfinance | les séances manquantes des **111 valeurs** |
| `rss` | 3 flux d'actualité | articles du jour |
| `scraping` | Boursorama | cours de séance de 3 valeurs |

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
| L'ordinateur est éteint à 19h | la tâche est **sautée** | rien dans les journaux ce jour-là |
| yfinance ne répond pas | l'étape échoue, **les autres continuent** | `!! cotations ECHEC` |
| Jour férié boursier | 0 séance récupérée | `lues 0` — **normal**, pas une panne |

C'est pourquoi la vraie sécurité n'est pas la planification mais une **requête de
fraîcheur** — savoir dire « ma donnée la plus récente a N jours ». C'est le chantier **C**,
pas encore fait.

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
