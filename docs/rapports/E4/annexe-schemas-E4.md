<style>
@page{ size:A4 landscape; margin:12mm; }
h2, .saut{ break-before:page; }
h2.sommaire{ break-before:auto; }
img{ display:block; margin:3mm auto; max-width:100%; max-height:126mm; width:auto; height:auto; }
img.grand{ max-height:158mm; }
.vue{ overflow:hidden; margin:2mm auto; }
.vue img{ max-width:none; max-height:none; height:auto; margin:0; }
.logo{ float:right; width:13mm; margin:4pt 0 2pt 12pt; }
.identite{ color:var(--ink-soft); font-size:9.4pt; }
.planche{ display:flex; gap:4mm; margin:3mm 0 0; }
.planche a{ flex:1; color:var(--ink); text-decoration:none; text-align:center; font-size:9pt; }
.planche img{ width:100%; height:30mm; max-height:none; object-fit:contain; margin:0 0 1.5mm; padding:1.5mm;
  box-sizing:border-box; border:.5pt solid var(--rule); border-radius:2pt; background:#fff; }
.planche span{ display:block; font-weight:600; color:var(--accent); }
</style>

<div><img class="logo" src="../E3/logo/rita-logo-marque.png" alt="Logo de RITA"></div>

# Annexe du rapport E4 : les schémas

Projet fil rouge **RITA** · **Eramalingam Gandakumar** · Développeur en intelligence artificielle, RNCP 37827 · Simplon × Wild Code School · compétences C14 à C19 · annexe du rapport E4, version 1.1, 2 novembre 2026
{: .identite }

> Cette annexe montre les schémas que le rapport cite, chacun sur sa page,
> suivi de sa légende : ce qu'il montre pour E4, la date de son contenu et sa limite, reprise du rapport. Version de référence de
> l'application : commit `174b0c1` (02/11/2026).

## Les schémas de cette annexe {: .sommaire }

| | Schéma | Critères | Contenu daté du | Version présentée | Page |
|---|---|---|---|---|---|
| A1 | Modèle conceptuel des données, formalisme Merise | C14 | 02/11/2026 (revu ; celui du 01/08 gardé) | original du dépôt | 2 |
| A2 | Wireframes d'état : Portefeuille, Indicateurs, Briefing | C14, C17 | 18/08 et 03/10/2026 | originaux du dépôt, agrandis | 3 à 5 |
| A3 | Architecture de l'application : deux chemins vers le modèle | C15 | 24/10/2026 | mise en forme du 31/10, texte inchangé | 6 |
| A4 | Flux de données, des sources à l'écran | C15 | 02/11/2026 (celui du 18/08 gardé) | original du dépôt | 7 |
| A5 | Chaîne d'intégration et de livraison | C18, C19 | 24/10/2026 | mise en forme du 31/10, texte inchangé | 8 |
| A6 | Parcours des écrans Question et Tableau de bord | C14 | 02/11/2026 | originaux du dépôt | 9 et 10 |

**Mise en forme du 31/10.** A3 et A5 ont reçu de nouvelles icônes et des flèches, avec l'aide d'une IA ; leur texte
est identique mot pour mot aux originaux du dépôt, cités dans chaque légende. Aucun contenu n'a été modifié ou mis à
jour pour cette annexe.

**Ce que l'annexe ne contient pas, et pourquoi.** Les écrans Question et Tableau de bord n'ont pas de maquette
préalable (rapport, critère C14.2) : leurs parcours (A6) et le diagramme de flux (A4) sont relevés sur l'existant le
02/11, et le disent. Ils décrivent l'application ; ils n'ont pas guidé sa construction.


### Les schémas en miniature

<div class="planche" role="navigation" aria-label="Les schémas en miniature, chacun relié à sa page">
<a href="#a1"><img src="../../../evidence/C4/MCD-MERISE-RITA-2026-11-02.png" alt="Miniature de A1, le modèle conceptuel des données"><span>A1 · modèle des données · p. 2</span></a>
<a href="#a2"><img src="../../../evidence/C14/WIREFRAMES-C14-ecran-portefeuille.svg" alt="Miniature de A2, le wireframe de l'écran Portefeuille"><span>A2 · wireframes · p. 3 à 5</span></a>
<a href="#a3"><img src="schemas/E4-architecture-mise-en-forme.svg" alt="Miniature de A3, l'architecture de l'application"><span>A3 · architecture · p. 6</span></a>
<a href="#a4"><img src="../../../evidence/C15/flux/FLUX-DONNEES-C15-application-RITA-2026-11-02.svg" alt="Miniature de A4, le diagramme de flux de données"><span>A4 · flux de données · p. 7</span></a>
<a href="#a5"><img src="schemas/E4-chaine-livraison-mise-en-forme.png" alt="Miniature de A5, la chaîne d'intégration et de livraison"><span>A5 · chaîne de livraison · p. 8</span></a>
<a href="#a6"><img src="../../../evidence/C14/parcours/PARCOURS-C14-ecran-question.svg" alt="Miniature de A6, le parcours de l'écran Question"><span>A6 · parcours · p. 9 et 10</span></a>
</div>

## A1. Le modèle conceptuel des données (C14) {: #a1 }

![Modèle conceptuel des données de RITA, au formalisme Merise, revu le 2 novembre 2026](../../../evidence/C4/MCD-MERISE-RITA-2026-11-02.png)

**MCD au formalisme Merise**, revu le 02/11/2026 (`evidence/C4/MCD-MERISE-RITA-2026-11-02.png`) : 6 entités et 6
associations, le même modèle que dans le livret E1 v5. Une valeur peut exister sans cotation (`VALEUR 0,n`), comme
dans la base ; un test le vérifie (`tests/test_mcd_c4.py`). Celui du 01/08 est gardé (`evidence/C4/MCD-MERISE-RITA.png`). **Limite** : la table `article`, qui porte les
données de l'écran Question, n'y figure pas (choix du 11/08 ; rapport, § 1.4 et critère C14.1).

## A2. Les wireframes d'état des trois premiers écrans (C14, C17) {: #a2 }

![Wireframe de l'écran Portefeuille](../../../evidence/C14/WIREFRAMES-C14-ecran-portefeuille.svg){: .grand }

**Écran Portefeuille, 18/08/2026** (`evidence/C14/WIREFRAMES-C14-ecran-portefeuille.svg`). Limites des trois
wireframes : sous le troisième, page 5.

<div class="saut"></div>

![Wireframe de l'écran Indicateurs](../../../evidence/C14/WIREFRAMES-C14-ecran-indicateurs.svg){: .grand }

**Écran Indicateurs, 03/10/2026** (`evidence/C14/WIREFRAMES-C14-ecran-indicateurs.svg`).

<div class="saut"></div>

![Wireframe de l'écran Briefing](../../../evidence/C14/WIREFRAMES-C14-ecran-briefing.svg){: .grand }

**Écran Briefing, 03/10/2026** (`evidence/C14/WIREFRAMES-C14-ecran-briefing.svg`). **Limites des trois
wireframes** : chacun a été dessiné après son écran ; il ne prouve ni qu'une maquette a guidé le développement, ni que
l'écran actuel lui est conforme. Les écrans Question et Tableau de bord n'ont pas de maquette (rapport, § 4.3 et
critère C14.2).

## A3. L'architecture de l'application (C15) {: #a3 }

![Architecture de RITA : le chemin d'un briefing et le chemin d'une question](schemas/E4-architecture-mise-en-forme.svg)

**Architecture de l'application, état du code au 24/10/2026** (commit `9683f04`), mise en forme du 31/10, texte inchangé
(original : `docs/rapports/E3/schemas/E3-architecture.svg`). **Ce qu'il montre pour E4** : les clients, dont les cinq
écrans de l'interface ; l'API et ses refus (403, 422, 429) ; les deux chemins vers le modèle, le briefing (scout,
recherche documentaire, rédacteur) et la question (recherche, puis réponse JSON stricte) ; les garde-fous avant et après
le modèle ; les données lues (PostgreSQL, index des articles) ; la surveillance (traces, alertes, `/sante`).
**Limites** : la vigie n'y figure pas (rapport, § 2.1 et critère C15.1) ; il montre l'état du 24/10, « briefing :
cascade, Azure d'abord » ; depuis le 31/10, après la version de référence, Azure est seul par défaut.

## A4. Le diagramme de flux de données (C15) {: #a4 }

![Diagramme de flux de données de RITA, relevé sur le code le 2 novembre 2026 : des sources aux cinq écrans, avec le chemin des questions, la passerelle MCP, les traces et la vigie](../../../evidence/C15/flux/FLUX-DONNEES-C15-application-RITA-2026-11-02.svg){: .grand }

**Diagramme de flux de données, relevé sur le code flux par flux le 02/11/2026** (`evidence/C15/flux/`, généré par
`generer_flux.py` ; preuve : `evidence/C15/preuve-flux-donnees-2026-11-02.md`). Il se lit dans le sens de la donnée ;
les flux de données personnelles sont marqués. Celui du 18/08 est gardé (`evidence/C15/FLUX-DONNEES-C15-application-RITA.png`).
**Limite** : relevé après le code, il décrit l'existant ; il n'a pas guidé la construction.

## A5. La chaîne d'intégration et de livraison (C18, C19) {: #a5 }

![Chaîne d'intégration et de livraison de RITA](schemas/E4-chaine-livraison-mise-en-forme.png)

**Chaîne d'intégration et de livraison, état au 24/10/2026** (commit `9683f04`), mise en forme du 31/10, texte inchangé
(original : `docs/rapports/E3/schemas/E3-chaine-livraison.svg` ; cette mise en forme n'existe qu'en image, pas en
vectoriel). **Ce qu'il montre pour E4** : du poste à la production, les contrôles de chaque étape, la protection de
`main`, la livraison au serveur avec pré-test et retour arrière (rapport, sections 5 et 6). **Limite** : l'installation
à la main d'un fichier Compose modifié, qui conditionne une livraison, n'y figure pas (§ 6.1). Le créneau « 8 h à 9 h » est celui où
le serveur refuse toute bascule ; GitHub commence à attendre 30 minutes plus tôt, pour qu'une livraison ne démarre pas
son pré-test juste avant 8 h, d'où les « 7 h 30 à 9 h » du rapport (`deploy/deployer.py`, `secondes_avant_livraison`).

## A6. Les parcours des écrans Question et Tableau de bord (C14) {: #a6 }

![Schéma du parcours de l'écran Question : entrer, demander, répondre ou refuser, remonter à la source](../../../evidence/C14/parcours/PARCOURS-C14-ecran-question.svg){: .grand }

**Écran Question, relevé le 02/11/2026** (`evidence/C14/parcours/PARCOURS-C14-ecran-question.svg`) : chaque étape,
chaque refus et chaque panne des scénarios de la spécification (`evidence/C14/preuve-specifications-ecrans-4-et-5.md`).

<div class="saut"></div>

![Schéma du parcours de l'écran Tableau de bord : entrer, lire, montrer, laisser lire, dont la suspension de l'actualisation](../../../evidence/C14/parcours/PARCOURS-C14-ecran-tableau-de-bord.svg){: .grand }

**Écran Tableau de bord, relevé le 02/11/2026** (`evidence/C14/parcours/PARCOURS-C14-ecran-tableau-de-bord.svg`).
**Limite des deux schémas** : relevés sur la version actuelle, ce ne sont pas des maquettes initiales.
