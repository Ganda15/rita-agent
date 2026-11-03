# Preuve d'envoi : documents du projet communiqués au formateur (03/11/2026)

> Critères concernés. Six du type « la documentation est communiquée aux parties prenantes dans un format qui
> respecte les recommandations d'accessibilité » : **C6.4** (synthèses de veille), **C8.5** (documentation du service),
> **C17.11** (documentation technique), **C18.6** (documentation de la chaîne d'intégration), **C19.7** (documentation
> de la livraison), **C20.7** (documentation du monitorage). Un sans exigence de format : **C16.3**, « les objectifs et
> les modalités des rituels sont partagés à toutes les parties prenantes ».
> Le **format** de chaque document est prouvé à part (§ 3) ; ce fichier prouve sa **communication**.

## 1. L'envoi, daté

| Champ | Valeur relevée |
|---|---|
| Date | 03/11/2026, 14 h 42 (heure de Paris), 13:42:34 UTC |
| De | Era |
| À | Elbby, formateur (compte GitHub `bybysker`) |
| Objet | « Objet : RITA : parcours Question, documents du projet et deux questions sur la remise » |
| Pièces jointes | `RITA-E4-parcours-et-comparaison-pour-Elbby-2026-11-03.pdf` ; `Veille-C6-synthese-S33-a-S36.pdf` ; `EXPLOITATION.pdf` |
| Demande | confirmation par retour de mail de la réception des trois PDF et de l'ouverture des documents |

**Source** : le message envoyé, lu le 03/11 dans la messagerie d'Era par le connecteur Gmail de la session de travail
(dossier « Envoyés »). Les adresses électroniques ne sont pas recopiées ici (données personnelles). Les pièces jointes
portent les noms des fichiers du dépôt ; Era les a jointes depuis `docs/veille/` et `docs/`, dont les empreintes SHA-256
sont égales, le 03/11, à celles des tags `livrable-E2-v1` et `livrable-E4-v1`. Le contenu des pièces reçues n'a pas été
recomparé octet par octet après l'envoi.

## 2. Ce qui a été communiqué, critère par critère

| Critère | Document | Comment il a été transmis |
|---|---|---|
| C6.4 | synthèse de veille S33 à S36 | PDF en pièce jointe ; source en ligne, `docs/veille/Veille-C6-synthese-S33-a-S36.md` au tag `livrable-E2-v1` |
| C8.5, C20.7 | guide d'exploitation | PDF en pièce jointe ; source en ligne, `docs/exploitation.md` au tag `livrable-E4-v1` |
| C16.3 | méthode Kanban et rituels | lien, `docs/PILOTAGE-AGILE.md` au tag `livrable-E4-v1` |
| C17.11 | installation et architecture | liens, `README.md` et `docs/ARCHITECTURE.md` au tag `livrable-E4-v1` |
| C18.6, C19.7 | tests et livraison continue | lien, `docs/CI-CD.md` au tag `livrable-E4-v1` |

Les six liens du message ont été vérifiés le 03/11 avant l'envoi (`gh api repos/Ganda15/rita-agent/contents/<chemin>?ref=<tag>` :
chaque fichier présent). Les PDF sont joints plutôt que liés : le lecteur de PDF de GitHub ne les affichait pas, alors
que les fichiers sont valides (22 et 35 pages).

## 3. Le format, prouvé avant l'envoi

| Document | Contrôle | Version contrôlée = version envoyée ? |
|---|---|---|
| synthèse de veille (PDF) | [`../C6/controle-accessibilite-synthese-2026-11-01.md`](../C6/controle-accessibilite-synthese-2026-11-01.md) | oui : dernier changement au tag, `5d13cd7` (01/11) |
| guide d'exploitation (PDF) | [`controle-accessibilite-guide-2026-10-31.md`](controle-accessibilite-guide-2026-10-31.md) | oui : `9b8bd62` (31/10) |
| `README.md`, `docs/ARCHITECTURE.md`, `docs/CI-CD.md` (lus sur GitHub) | [`../C17/controle-accessibilite-readme-2026-11-02.md`](../C17/controle-accessibilite-readme-2026-11-02.md) | oui pour `ARCHITECTURE.md` (`afa741d`) et `CI-CD.md` (`8ff64bf`) ; `README.md` a changé ensuite, `113b279` (02/11), deux lignes du tableau d'état seulement, sans toucher titres, liens ni tableaux |
| `docs/PILOTAGE-AGILE.md` | aucun contrôle de format daté | dernier changement `477b018` (03/10) |

## 4. Ce qui n'est pas encore là

- **L'accusé de réception du formateur**, demandé dans le message ; il sera ajouté ici à sa réception.
- **Le jury** n'a rien reçu : la procédure d'accès est demandée au formateur dans le même message.
- Le statut de chaque critère se décide par Era, critère par critère. **Décision d'Era du 03/11** : les sept passent à OK
  dans les classeurs des compétences, sur la base de cet envoi daté.
