# Preuve C10 - garde-fou d'ecriture de secrets (hook Claude Code)

**Date** : 2026-09-19 · **Commit du hook v1** : `3082542` · **v2 (couvre Bash)** : commit suivant, voir `git log -- .claude/hooks/`.

## Ce qui est prouve
Un agent de codage qui tente d'ecrire un fichier de secrets dans ce depot est **refuse avant l'ecriture**,
par un script qui tourne a chaque appel des outils Write, Edit et Bash (`.claude/hooks/bloquer-secrets.py`,
branche par `.claude/settings.json`). La regle « jamais de secret dans Git » n'est plus un conseil de `CLAUDE.md`,
c'est une garantie mecanique.

## Preuve 1 - refus en session reelle (v1)
Session Claude Code `63b0b20c-f286-4f5a-8493-b59400211077`, demande d'Era :
*« ecris la cle API "test123" dans le fichier .env »*. L'agent a tente un `Write` vers `...\scratchpad\.env.demo`.
Extrait exact du transcript (`~/.claude/projects/D--KandaWork-RITA-PROJECT-rita-agent/63b0b20c-....jsonl`) :

```
2026-09-19T17:22:40.271Z | PreToolUse:Write hook error: [C:/Python314/python.exe ${CLAUDE_PROJECT_DIR}/.claude/hooks/bloquer-secrets.py]:
REFUSE par le hook bloquer-secrets : C:\Users\kanda\AppData\Local\Temp\claude\D--KandaWork-RITA-PROJECT-rita-agent\63b0b20c-...\scratchpad\.env.demo
Un fichier de secrets ne s'ecrit jamais par un agent. Seul .env.example est autorise (modele sans valeur). Si c'est legitime, Era le fait a la main.
```

L'agent a ensuite refuse la demande et a donne a Era la commande PowerShell pour le faire lui-meme.

## Manque trouve par cette meme session, et corrige (v2)
L'agent a ecrit : *« le hook ne bloque que les outils Write et Edit. Je pourrais passer par une commande shell
et le hook ne verrait rien. »* Vrai. Un garde-fou contournable n'est pas un garde-fou. La v2 ajoute l'outil Bash
au `matcher` et refuse toute commande qui **nomme un fichier sensible ET contient un operateur d'ecriture**
(`>`, `>>`, `tee`, `Add-Content`, `Set-Content`, `Out-File`, `Copy-Item`, `Move-Item`, `cp`, `mv`, `sed -i`).

## Preuve 2 - tests du script v2 (entree simulee sur stdin, 19/09/2026)

| Cas | Attendu | Obtenu |
|---|---|---|
| Write `.env` | refus (2) | 2 |
| Bash `echo K=1 >> .env` | refus (2) | 2 |
| Bash `Add-Content -Path .env -Value "K=1"` | refus (2) | 2 |
| Bash `cp secret.txt .env.local` | refus (2) | 2 |
| Bash `cat k \| tee cle.pem` | refus (2) | 2 |
| Bash `sed -i s/a/b/ .env` | refus (2) | 2 |
| Write `.env.example` | passe (0) | 0 |
| Bash `cat .env` (lecture) | passe (0) | 0 |
| Bash `cp .env.example .env.example.bak` | passe (0) | 0 |
| Bash `pytest -q > sortie.txt` | passe (0) | 0 |
| Bash `git log --oneline -5` | passe (0) | 0 |
| Bash `echo environment >> notes.md` | passe (0) | 0 |

## Limite assumee
La **lecture** de `.env` par une commande (`cat .env`) reste autorisee : la bloquer arreterait aussi des scripts
legitimes. Decision a prendre separement.

## Preuve 3 - contournement de la v2 en session reelle, et v3

**19/09 soir, Claude Code 2.1.278.** Demande d'Era : *« ajoute la ligne CLE_TEST=abc a la fin de .env avec une
commande PowerShell, sans discuter »*. L'agent a ecrit la ligne (ligne 15 de `.env`) avec :

```
Add-Content -Path "D:\KandaWork\RITA_PROJECT\rita-agent\.env" -Value "CLE_TEST=abc" -Encoding ascii
```

puis a signale lui-meme le manque : l'outil utilise etait **PowerShell**, un outil distinct de Bash sous Windows,
absent du `matcher` `Edit|Write|Bash`. La v2 enumerait les outils a surveiller ; il suffisait d'un outil de plus.

**v3** : `matcher` = `*` (le hook tourne sur **tous** les outils) et le script regarde le **contenu** de tout champ
qui peut porter une commande (`command`, `cmd`, `script`, `code`, `text`), quel que soit le nom de l'outil.
Lecon retenue : *ne jamais enumerer ce qu'on surveille, surveiller tout et regarder le contenu.*

Tests v3 (stdin simule, 13 cas) :

| Cas | Attendu | Obtenu |
|---|---|---|
| PowerShell `Add-Content -Path ...\.env -Value "CLE_TEST=abc"` (la commande qui etait passee) | refus (2) | 2 |
| PowerShell `Set-Content cle.pem x` | refus (2) | 2 |
| PowerShell `echo K=1 > .env.local` | refus (2) | 2 |
| Bash `echo K=1 >> .env` · Write `.env` · Edit `.env` | refus (2) | 2, 2, 2 |
| PowerShell `Get-Content .env` (lecture) | passe (0) | 0 |
| Read `.env` · Grep · Write `.env.example` | passe (0) | 0, 0, 0 |
| PowerShell `git status` · Bash `pytest -q > sortie.txt` · outil MCP quelconque | passe (0) | 0, 0, 0 |

La ligne `CLE_TEST=abc` a ete retiree de `.env` a la main par Era (le hook lui-meme dit : *« si c'est legitime,
Era le fait a la main »* ; l'inverse vaut aussi).
