# File de validation — ce qui attend le formateur

> **Créée le 2026-08-16**, parce que le formateur est en congé et que le travail ne peut pas
> attendre son retour. Règle appliquée : `docs/PLAN-12-SEMAINES.md` §3 —
> **on produit → on gèle → on met en file → on continue.**

## Pourquoi ce fichier existe

L'ordre imposé par le formateur — *une compétence prouvée → envoyée en revue → puis la
suivante* — sert à empêcher d'empiler du travail non relu. **Il ne dit pas d'attendre un
absent.**

Ce registre est ce qui rend la démarche défendable devant un jury : il montre une recherche
de validation **systématique et datée**. Ce qui se reproche, c'est de n'avoir jamais cherché
la validation — pas d'avoir continué à produire pendant l'absence du relecteur.

## Comment on s'en sert

1. Dès qu'un livrable est **gelé** (commité, tests verts, liens vérifiés), on ajoute une ligne.
2. **Rien n'attend dans la file pour démarrer la suite.** La file est une boîte d'envoi, pas
   une salle d'attente.
3. Au retour du formateur : envoi **un par un, dans l'ordre de la file** — pas tout d'un bloc.
   Trois livrables envoyés le même jour reçoivent un seul retour, superficiel.
4. Un retour reçu se note **le jour où il arrive**, avec ce qu'il change.

⚠️ **Ce fichier ne remplace pas `docs/veille/_JOURNAL-DES-ENVOIS.md`** : celui-là trace le
partage **de la veille** (critère C6). Celui-ci trace la **validation des livrables**. Deux
besoins, deux registres.

---

## La file

| # | Gelé le | Livrable | Compétences | Tag / commit | Envoyé le | Retour reçu | Ce que le retour change |
|---|---|---|---|---|---|---|---|
| 1 | 2026-08-13 | **E1 — Données** | C1–C5 | `livrable-E1-v1` | ⬜ | ⬜ | — |
| 2 | 2026-08-15 | Protocole de veille C6 (complet) | C6 | `27ff359` | ⬜ | ⬜ | — |
| 3 | 2026-08-15 | Conception des indicateurs (E4) | — *(conception)* | `81780cb` | ⬜ | ⬜ | — |

**Légende** : ⬜ = pas encore fait · ✅ = fait, avec la date.

> **État au 2026-08-16 : 3 éléments en file, 0 envoyé.** Le formateur est en congé.
> La note de veille S33 a été envoyée séparément — voir `docs/veille/_JOURNAL-DES-ENVOIS.md`.

---

## Ce qui reste à mettre en file, dans l'ordre du plan

| Attendu en | Livrable | Compétences |
|---|---|---|
| S39 | **E4 — Application** | C10, C14–C19 |
| S41 | **C7 — Benchmark de services IA** | C7 |
| S42 | **E3 — API modèle & MLOps** | C9, C11, C12, C13 |
| S43 | **E5 — Monitorage** | C20, C21 |

---

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Geler** (*freeze*) | Arrêter de modifier : commiter, taguer, tests verts, liens vérifiés |
| **Tag Git** | Étiquette posée sur un commit précis, qui permet de retrouver exactement l'état envoyé — même si le code a changé depuis |
| **Mettre en file** | Inscrire ici un livrable prêt, pour ne pas dépendre de la disponibilité du relecteur |
