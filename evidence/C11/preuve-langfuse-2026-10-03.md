# Preuve C11 : ce qui a été fait dans Langfuse par l'API le 03/10/2026, et ce qui reste à cliquer

> Contexte : après le push du 03/10, Era a demandé « Langfuse clicks next ». Tout ce qui pouvait se faire
> par l'API publique depuis le poste, avec les clés déjà chargées par l'application (jamais affichées), a été
> fait et est prouvé ci-dessous. Ce que l'API ne permet pas, ou ce que la session a refusé, est listé avec
> les clics exacts, à faire par Era dans le navigateur.

## 1. Fait par l'API, avec preuve

| Action | Résultat mesuré | Preuve |
|---|---|---|
| Lecture des traces du 02/10 (15 h 30 à 17 h 30 UTC) | 22 traces dans le projet ; 15 ont pour entrée `prompt test` (générations de la suite de tests, INC-006), 7 sont réelles | `inc-006-traces-factices-avant-suppression-2026-10-03.json` (identifiants, heures, entrées, sorties) |
| Correction du décompte d'INC-006 | la fiche disait douze lignes (18 h 25 à 18 h 38, heure de Paris) ; une troisième série de trois à 18 h 42 porte le total à **quinze** | même fichier, champ `note` ; complément daté dans la fiche INC-006 |
| Validation des champs de métriques (API `v2/metrics`, lecture seule) | générations par nom : `briefing-llm` 21, `llm-foundry` 1, `llm-anthropic` 1, `llm-openrouter` 1 · p95 de `briefing-llm` : 1 671,8 ms · observations ERROR : 17, WARNING : 0 | sortie du script, reprise ici |
| Création de trois widgets | `Générations par fournisseur` (barres, par nom d'étape) · `Latence p95 de briefing-llm` (courbe) · `Observations en ERROR ou WARNING` (barres par niveau) | `dashboard-rita-c11-2026-10-03.json`, clé `widgets` |
| Création du tableau de bord **RITA C11** | trois tuiles sur la grille de 12 colonnes (deux en haut, une pleine largeur dessous) | même fichier, clé `dashboard` ; adresse : `https://cloud.langfuse.com/project/cmr25olp200v5ad0d1jrrmtui/dashboards/cmurnbyvy0a9oad0hauajc8t4` |

Ce que ces chiffres disent : le p95 de 1 671,8 ms porte sur 21 appels, dont 15 factices (la suite de tests a
un double qui répond vite), donc **il bougera après la suppression** ; c'est la mesure d'avant nettoyage.
Les 17 observations ERROR sont des échecs de fournisseurs (clés absentes du poste), pas des briefings non
servis : voir le rapport E3, section 5.3.

L'API utilisée porte le préfixe `unstable` (`/api/public/unstable/dashboards`, `/dashboard-widgets`) : Langfuse
peut en changer la forme. Le SDK installé (4.12.0) ne l'expose pas encore, l'appel a été fait en HTTP direct.

## 2. Non fait, et pourquoi

| Action | Pourquoi | Qui, quand |
|---|---|---|
| Suppression des 15 traces factices | l'appel `DELETE /api/public/traces` était prêt ; l'outil de développement l'a **refusé** (règle : pas de suppression de masse sur un service distant par l'agent). L'export d'avant suppression est fait | **Era**, clics en 3.1 |
| Les 2 alertes (ERROR sur 24 h ; aucune trace en 24 h) vers GitHub Actions | aucune route d'API pour les alertes dans la spécification OpenAPI du 03/10 | **Era**, clics en 3.2 |
| Déclenchement manuel du workflow `alerte-incident.yml` (bouton *Run workflow*) | **fait le 03/10 à 13 h 50** après la fusion de la PR #58 : run `37120911852` en succès, issue #71 créée avec le label `incident` (fermée ensuite : c'était un test) | fait |
| Captures d'écran | pas de session navigateur sur le compte Langfuse d'Era | **Era**, après 3.1 et 3.2 |

## 3. Les clics, dans l'ordre

Tout se passe sur 🌐 **SITE LANGFUSE** (`https://cloud.langfuse.com`, projet « My Project », région UE),
dans le navigateur. Aucune commande à taper.

### 3.1 Supprimer les 15 traces factices (INC-006)

1. Menu de gauche, **Tracing**, puis **Traces**.
2. Régler la période sur le **2 octobre 2026**.
3. Dans la barre de filtre, ajouter **Input** · *contains* · `prompt test`. Il doit rester **15 lignes**, toutes
   nommées `briefing-llm`, entre 18 h 25 et 18 h 42.
4. **Capture d'écran** de cette liste : `evidence/C11/capture-2026-10-03-inc-006-avant-suppression.png`.
5. Cocher la case d'en-tête (toutes les lignes), bouton **Delete**, confirmer.
6. Retirer le filtre : il doit rester **7 traces** le 2 octobre (six `Reponds par un seul mot : bonjour.`,
   une `Reponds par un seul mot : merci.`). Capture : `capture-2026-10-03-traces-reelles-apres-suppression.png`.

### 3.2 Les deux alertes vers GitHub Actions (palier Hobby : deux au maximum)

1. Menu de gauche, **Alerts** (ou **Settings**, puis **Alerts**).
2. **New alert** n° 1 : métrique **Observations**, filtre **Level = ERROR**, condition **count > 0 sur 24 heures**,
   nom `RITA : fournisseur en erreur`. Canal **GitHub Actions** : dépôt `Ganda15/rita-agent`, type d'événement
   `alerte-langfuse`, jeton GitHub avec la portée `repo` (à créer dans GitHub, **Settings → Developer settings →
   Personal access tokens**, jamais collé dans le chat ni dans un fichier du dépôt).
3. **New alert** n° 2 : métrique **Traces**, condition **count = 0 sur 24 heures**, nom
   `RITA : aucune trace depuis 24 h`, même canal.
4. Capture de la liste des deux alertes : `capture-2026-10-03-alertes.png`.

⚠️ Tant que `alerte-incident.yml` n'est pas sur `main`, l'événement `alerte-langfuse` envoyé par Langfuse
**n'ouvrira aucune issue** : GitHub l'ignore. Les alertes peuvent être créées dès maintenant, elles
prendront effet à la fusion.

### 3.3 Vérifier le tableau de bord

1. Menu de gauche, **Dashboards**, ouvrir **RITA C11**.
2. Période : **7 derniers jours**. Les trois tuiles doivent afficher des données du 2 octobre.
3. Capture : `capture-2026-10-03-dashboard-rita-c11.png`.

## 4. Ce qui change dans les critères C11

| Critère | Avant le 03/10 | Après |
|---|---|---|
| 3. Vecteur de restitution en temps réel | 🟠 conçu, non construit | ✅ construit par l'API, trois tuiles ; capture à faire |
| 6. Chaîne en état de marche | 🟠 traces réelles sur le poste | 🟠 inchangé : alertes non réglées, conteneur et serveur pas encore |
| 4. Accessibilité du vecteur | 🟠 | 🟠 inchangé : argument à écrire dans le rapport E3 (interface web standard, données exportables par l'API) |

## 📖 Glossaire

- **API publique** : les adresses `https://cloud.langfuse.com/api/public/...`, appelées avec la paire de clés du projet ; tout ce que l'interface fait n'y est pas exposé (les alertes, par exemple).
- **Préfixe `unstable`** : partie de l'API que Langfuse déclare susceptible de changer sans préavis.
- **Widget** : une tuile d'un tableau de bord ; elle a une vue (observations), des dimensions (par quoi grouper), une métrique (quoi compter) et des filtres.
- **p95** : la valeur sous laquelle se trouvent 95 % des mesures ; ici la durée de l'appel au modèle.
- **`workflow_dispatch`** : le bouton *Run workflow* de GitHub Actions ; il n'existe que pour un workflow présent sur la branche par défaut.
