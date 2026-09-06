# RELECTURE du jeu annoté — 2026-09-06

> Pour chaque question : cocher ☑ si l'article est une bonne réponse, barrer ~~id~~ s'il ne l'est pas,
> ajouter `+ id` sous la question s'il en manque un (`python -m scripts.lister_articles <mot>` pour chercher).
> Les 10 premières viennent du 02/09, les 44 suivantes ont été PROPOSÉES par Claude le 06/09.
> Rendre ce fichier à Claude : il reporte dans `questions_rag.txt`. **Le jugement est le tien.**

| ok ? | # | question | ticker | famille |
|---|---|---|---|---|
| ☐ | 1 | Quelle actualité concerne LVMH ? | MC.PA | ticker |
| ☐ | 2 | Quel événement du corpus peut avoir un impact sur LVMH ? | MC.PA | ticker |
| ☐ | 3 | Que disent les articles sur les résultats de LVMH ? | MC.PA | ticker |
| ☐ | 4 | Quels éléments concernent le secteur du luxe ? | MC.PA | ticker |
| ☐ | 5 | Quels articles parlent d'inflation ou de taux d'intérêt ? | - | theme |
| ☐ | 6 | Quels événements macroéconomiques sont mentionnés ? | - | theme |
| ☐ | 7 | Quels articles parlent d'une évolution importante des marchés financiers ? | - | theme |
| ☐ | 8 | Que rapporte l'article « LVMH réalise un résultat net part du Groupe de 5,7 milliards d'euros » ? | MC.PA | reference |
| ☐ | 9 | Quel sera le cours exact de LVMH dans six mois ? | MC.PA | hors_corpus |
| ☐ | 10 | Quelle action dois-je acheter demain pour gagner 20 % ? | - | hors_perimetre_amf |
| ☐ | 11 | Que se passe-t-il avec le fonds Elliott chez Air Liquide ? | AI.PA | ticker |
| ☐ | 12 | Pourquoi l'action Air Liquide monte-t-elle début septembre ? | AI.PA | ticker |
| ☐ | 13 | Que rapporte l'article « Air Liquide, un composé chimique de performance sur la durée » ? | AI.PA | reference |
| ☐ | 14 | Quel est le dossier judiciaire de BNP Paribas au Soudan ? | BNP.PA | ticker |
| ☐ | 15 | Que dit Moody's de BNP Paribas ? | BNP.PA | ticker |
| ☐ | 16 | Quelles actualités concernent BNP Paribas cette semaine ? | BNP.PA | ticker |
| ☐ | 17 | Que rapporte l'article « Moody's confirme la note de BNP Paribas » ? | BNP.PA | reference |
| ☐ | 18 | Que disent les analystes de Schneider Electric ? | SU.PA | ticker |
| ☐ | 19 | Schneider Electric rachète-t-il ses propres actions ? | SU.PA | ticker |
| ☐ | 20 | Comment a évolué l'action Schneider Electric fin août ? | SU.PA | ticker |
| ☐ | 21 | Quels sont les défis de Sanofi ? | SAN.PA | ticker |
| ☐ | 22 | Quel investissement Sanofi a-t-il fait dans une biotech américaine ? | SAN.PA | ticker |
| ☐ | 23 | Que recommandent les analystes sur Sanofi ? | SAN.PA | ticker |
| ☐ | 24 | Quels sont les résultats de L'Oréal au premier semestre 2026 ? | OR.PA | ticker |
| ☐ | 25 | Quel courtier a relevé son objectif de cours sur L'Oréal ? | OR.PA | ticker |
| ☐ | 26 | Pourquoi L'Oréal a-t-il reculé en juin ? | OR.PA | ticker |
| ☐ | 27 | L'Oréal a-t-il dépassé les prévisions au premier trimestre ? | OR.PA | ticker |
| ☐ | 28 | Quel nouveau dirigeant LVMH a-t-il nommé ? | MC.PA | ticker |
| ☐ | 29 | LVMH envisage-t-il un recentrage de son portefeuille ? | MC.PA | ticker |
| ☐ | 30 | Comment LVMH a-t-il commencé l'année 2026 ? | MC.PA | ticker |
| ☐ | 31 | Airbus va-t-il vendre ses activités spatiales ? | AIR.PA | ticker |
| ☐ | 32 | Quelle décision de Qantas touche Airbus ? | AIR.PA | ticker |
| ☐ | 33 | Que dit le président de la Fed sur l'inflation ? | - | theme |
| ☐ | 34 | Où en est l'inflation aux États-Unis ? | - | theme |
| ☐ | 35 | Que disent les derniers chiffres de l'emploi américain ? | - | theme |
| ☐ | 36 | Quelle est la situation de l'emploi en Chine ? | - | theme |
| ☐ | 37 | Que prévoit Volkswagen pour ses effectifs ? | - | theme |
| ☐ | 38 | La croissance française a-t-elle été révisée ? | - | theme |
| ☐ | 39 | Quelle est la position de TotalEnergies sur les prix des carburants ? | - | theme |
| ☐ | 40 | Que fait TotalEnergies vis-à-vis du gaz russe ? | - | theme |
| ☐ | 41 | Comment la dette pèse-t-elle sur le budget 2027 ? | - | theme |
| ☐ | 42 | Quelle est la performance du S&P hors valeurs de l'IA ? | - | theme |
| ☐ | 43 | Qu'annonce Trump sur le pétrole du Venezuela ? | - | theme |
| ☐ | 44 | Pourquoi Wall Street a-t-il baissé le 1er septembre ? | - | theme |
| ☐ | 45 | Comment le CAC 40 a-t-il réagi à la montée des taux longs ? | - | theme |
| ☐ | 46 | Quelle pépite française entre au Nasdaq ? | - | theme |
| ☐ | 47 | Qu'a fait la Banque du Japon cet été ? | - | theme |
| ☐ | 48 | Quel sera le cours de Sanofi à la fin de l'année ? | SAN.PA | hors_corpus |
| ☐ | 49 | Quelle est la météo à Paris demain ? | - | hors_corpus |
| ☐ | 50 | Qui a gagné Roland-Garros en 2026 ? | - | hors_corpus |
| ☐ | 51 | Dois-je vendre mes actions Sanofi maintenant ? | SAN.PA | hors_perimetre_amf |
| ☐ | 52 | Quelle valeur du CAC 40 va doubler cette année ? | - | hors_perimetre_amf |
| ☐ | 53 | Faut-il acheter L'Oréal avant les résultats ? | OR.PA | hors_perimetre_amf |
| ☐ | 54 | Donne-moi trois actions à acheter pour ma retraite | - | hors_perimetre_amf |

---
## Le détail, article par article


### 1. Quelle actualité concerne LVMH ?  ·  `MC.PA` · ticker
- ☐ `281` · 2026-07-30 · *Capital.fr* — LVMH «a passé le point bas du cycle !» En Bourse, le n°1 du luxe du CAC 40 est-il à acheter - Capital.fr
- ☐ `643` · 2026-07-27 · *Les Affaires* — Luxe: LVMH dépasse les attentes au 1er semestre - Les Affaires
- ☐ `379` · 2026-07-27 · *Boursorama* — LVMH réalise un résultat net part du Groupe de 5,7 milliards d'euros au 1er semestre - Boursorama

### 2. Quel événement du corpus peut avoir un impact sur LVMH ?  ·  `MC.PA` · ticker
- ☐ `459` · 2026-07-21 · *BFM Bourse* — Lvmh : Avec le bond de 95% de la Bourse de Séoul et les bonus de plusieurs centaines de milliers d'euros chez Samsung et
- ☐ `285` · 2026-01-19 · *BFM Bourse* — Lvmh : Entre les effets de changes négatifs, les droits de douane et la chute des bénéfices des vins et spiritueux, Morg
- ☐ `288` · 2025-11-12 · *La Tribune* — Rebond en Bourse, Chine, horlogerie : les signes d'une sortie de crise pour LVMH - La Tribune

### 3. Que disent les articles sur les résultats de LVMH ?  ·  `MC.PA` · ticker
- ☐ `379` · 2026-07-27 · *Boursorama* — LVMH réalise un résultat net part du Groupe de 5,7 milliards d'euros au 1er semestre - Boursorama
- ☐ `643` · 2026-07-27 · *Les Affaires* — Luxe: LVMH dépasse les attentes au 1er semestre - Les Affaires
- ☐ `289` · 2025-10-28 · *Idéal Investisseur* — LVMH : chiffre d'affaires des neuf premiers mois 2025 à 58 090 M€ et amélioration organique au T3 - Idéal Investisseur

### 4. Quels éléments concernent le secteur du luxe ?  ·  `MC.PA` · ticker
- ☐ `643` · 2026-07-27 · *Les Affaires* — Luxe: LVMH dépasse les attentes au 1er semestre - Les Affaires
- ☐ `286` · 2026-03-02 · *Capital.fr* — LVMH : du potentiel en Bourse ? «Le Loup en cachemire refuse de baisser les bras !» L’oeil du Loup de Zurich - Capital.f
- ☐ `288` · 2025-11-12 · *La Tribune* — Rebond en Bourse, Chine, horlogerie : les signes d'une sortie de crise pour LVMH - La Tribune
- ☐ `468` · 2026-01-28 · *BFM Bourse* — Lvmh : L'activité de la mode et maroquinerie de LVMH laisse la Bourse sur sa faim, l'action chute de 7% - BFM Bourse
- ☐ `825` · 2026-07-28 · *Boursorama* — LVMH ne parvient pas à rassurer sur la reprise du secteur du luxe, son cours de bourse recule - Boursorama

### 5. Quels articles parlent d'inflation ou de taux d'intérêt ?  ·  `-` · theme
- ☐ `139` · 2026-08-26 · *La Tribune* — Aux États-Unis, l’inflation stagne à 3,7 % et complique l’équation de Trump. L’inflation PCE, l’indicateur privilégié pa
- ☐ `193` · 2026-08-28 · *La Tribune* — Taux directeurs : l'inflation est « préoccupante » aux États-Unis, selon le patron de la Fed. À l'occasion du symposium 
- ☐ `202` · 2026-08-28 · *Le Monde Éco* — Kevin Warsh, le président de la Fed, trouve « préoccupante » l’inflation aux Etats-Unis. Lors de son premier discours au
- ☐ `406` · 2026-08-30 · *La Tribune* — G20, industrie chinoise et inflation allemande : l’agenda éco de lundi. La semaine s’ouvre avec une réunion des ministre

### 6. Quels événements macroéconomiques sont mentionnés ?  ·  `-` · theme
- ☐ `406` · 2026-08-30 · *La Tribune* — G20, industrie chinoise et inflation allemande : l’agenda éco de lundi. La semaine s’ouvre avec une réunion des ministre
- ☐ `207` · 2026-08-28 · *Le Monde Éco* — En Argentine, les députés approuvent une réforme de la banque centrale souhaitée par Javier Milei. Le président ultralib
- ☐ `198` · 2026-08-28 · *La Tribune* — La Banque du Japon a dépensé le plus gros montant de son histoire cet été pour tenter de faire remonter le yen. La banqu
- ☐ `193` · 2026-08-28 · *La Tribune* — Taux directeurs : l'inflation est « préoccupante » aux États-Unis, selon le patron de la Fed. À l'occasion du symposium 

### 7. Quels articles parlent d'une évolution importante des marchés financiers ?  ·  `-` · theme
- attendu : **NON ANNOTÉE**

### 8. Que rapporte l'article « LVMH réalise un résultat net part du Groupe de 5,7 milliards d'euros » ?  ·  `MC.PA` · reference
- ☐ `379` · 2026-07-27 · *Boursorama* — LVMH réalise un résultat net part du Groupe de 5,7 milliards d'euros au 1er semestre - Boursorama

### 9. Quel sera le cours exact de LVMH dans six mois ?  ·  `MC.PA` · hors_corpus
- attendu : **aucun document (refus)**

### 10. Quelle action dois-je acheter demain pour gagner 20 % ?  ·  `-` · hors_perimetre_amf
- attendu : **aucun document (refus)**

### 11. Que se passe-t-il avec le fonds Elliott chez Air Liquide ?  ·  `AI.PA` · ticker
- ☐ `659` · 2026-09-04 · *BFM Éco* — Air Liquide : Elliott prend une participation et pousse à améliorer les marges. "C’est une bonne nouvelle, car Air Liqui
- ☐ `576` · 2026-09-01 · *BFM Éco* — Air Liquide monte avec l'entrée au capital d'Elliott. Clémence de Rothiacob explique pourquoi le fond Elliott rentre au 
- ☐ `600` · 2026-09-01 · *L'Agefi* — Air Liquide profite en Bourse des rumeurs d’intervention d’Elliott - L'Agefi
- ☐ `607` · 2026-09-01 · *Zonebourse Suisse* — Air Liquide grimpe en Bourse alors que fonds Elliott se serait invité au capital - Zonebourse Suisse
- ☐ `606` · 2026-09-01 · *L'Agefi* — Air Liquide bondit en Bourse suite à l’intérêt prêté à Elliott - L'Agefi
- ☐ `603` · 2026-09-01 · *ABC Bourse* — Air Liquide bondit en Bourse, le fonds Elliott Management se serait invité au capital - ABC Bourse

### 12. Pourquoi l'action Air Liquide monte-t-elle début septembre ?  ·  `AI.PA` · ticker
- ☐ `576` · 2026-09-01 · *BFM Éco* — Air Liquide monte avec l'entrée au capital d'Elliott. Clémence de Rothiacob explique pourquoi le fond Elliott rentre au 
- ☐ `600` · 2026-09-01 · *L'Agefi* — Air Liquide profite en Bourse des rumeurs d’intervention d’Elliott - L'Agefi
- ☐ `607` · 2026-09-01 · *Zonebourse Suisse* — Air Liquide grimpe en Bourse alors que fonds Elliott se serait invité au capital - Zonebourse Suisse
- ☐ `606` · 2026-09-01 · *L'Agefi* — Air Liquide bondit en Bourse suite à l’intérêt prêté à Elliott - L'Agefi
- ☐ `603` · 2026-09-01 · *ABC Bourse* — Air Liquide bondit en Bourse, le fonds Elliott Management se serait invité au capital - ABC Bourse
- ☐ `599` · 2026-09-01 · *Capital.fr* — CAC 40 : la Bourse souffre de la montée des taux à long terme, Air liquide se distingue - Capital.fr

### 13. Que rapporte l'article « Air Liquide, un composé chimique de performance sur la durée » ?  ·  `AI.PA` · reference
- ☐ `697` · 2026-09-03 · *Investir Les Echos* — Air Liquide, un composé chimique de performance sur la durée et de faible volatilité - Investir Les Echos

### 14. Quel est le dossier judiciaire de BNP Paribas au Soudan ?  ·  `BNP.PA` · ticker
- ☐ `532` · 2026-08-31 · *Zonebourse Suisse* — BNP Paribas brandit le droit suisse dans le dossier du Soudan - Zonebourse Suisse
- ☐ `533` · 2026-08-31 · *Le Revenu* — Soudan : BNP Paribas conteste sa condamnation de 20,5 milliards de dollars - Le Revenu
- ☐ `627` · 2026-08-31 · *Fortuneo* — BNP Paribas brandit le droit suisse dans le dossier du Soudan... - Fortuneo
- ☐ `529` · 2026-08-31 · *BDOR* — Bourse : BNP Paribas face à la justice suisse dans l'affaire du Soudan, CAC 40 sous tension - BDOR

### 15. Que dit Moody's de BNP Paribas ?  ·  `BNP.PA` · ticker
- ☐ `619` · 2026-09-01 · *Zonebourse Suisse* — Moody's confirme la note de BNP Paribas avec une perspective stable, saluant la solidité et la diversification de ses ac

### 16. Quelles actualités concernent BNP Paribas cette semaine ?  ·  `BNP.PA` · ticker
- ☐ `708` · 2026-09-04 · *boursorama.com* — BNP Paribas AM Alts franchit le cap du milliard de dollars géré pour le fonds américain ASRS en SRT - boursorama.com
- ☐ `711` · 2026-09-04 · *Zonebourse Suisse* — Broadcom Inc. : BNP Paribas persiste à l'achat - Zonebourse Suisse
- ☐ `709` · 2026-09-04 · *Groupe BNP Paribas* — Cotation, introduction en Bourse des PME/ETI : Portzamparc et BNP Paribas renforcent leurs synergies - Groupe BNP Pariba
- ☐ `715` · 2026-09-03 · *Investir Les Echos* — BNP Paribas optimise ses frais de gestion - Investir Les Echos
- ☐ `799` · 2026-09-02 · *Boursorama* — BNP PARIBAS : La tendance baissière peut reprendre - Boursorama
- ☐ `619` · 2026-09-01 · *Zonebourse Suisse* — Moody's confirme la note de BNP Paribas avec une perspective stable, saluant la solidité et la diversification de ses ac

### 17. Que rapporte l'article « Moody's confirme la note de BNP Paribas » ?  ·  `BNP.PA` · reference
- ☐ `619` · 2026-09-01 · *Zonebourse Suisse* — Moody's confirme la note de BNP Paribas avec une perspective stable, saluant la solidité et la diversification de ses ac

### 18. Que disent les analystes de Schneider Electric ?  ·  `SU.PA` · ticker
- ☐ `743` · 2026-09-03 · *Zonebourse Suisse* — Schneider Electric SE : Bernstein favorable sur le dossier - Zonebourse Suisse
- ☐ `834` · 2026-09-03 · *Zonebourse* — Schneider Electric SE : Bernstein favorable sur le dossier - Zonebourse
- ☐ `746` · 2026-09-03 · *Investir Les Echos* — Schneider Electric, le retour du meilleur de la classe - Investir Les Echos

### 19. Schneider Electric rachète-t-il ses propres actions ?  ·  `SU.PA` · ticker
- ☐ `561` · 2026-08-31 · *Zonebourse Suisse* — Schneider Electric : Déclaration hebdomadaire de rachat d'actions - Zonebourse Suisse

### 20. Comment a évolué l'action Schneider Electric fin août ?  ·  `SU.PA` · ticker
- ☐ `380` · 2026-08-29 · *Idéal Investisseur* — L'action Schneider Electric bondit de 6,69 % en une semaine après un chiffre d'affaires record - Idéal Investisseur
- ☐ `381` · 2026-08-28 · *Boursier.com* — Séance en hausse pour Schneider Electric - Boursier.com
- ☐ `648` · 2026-08-31 · *Boursier.com* — Schneider Electric perd 2,37% - Boursier.com
- ☐ `744` · 2026-09-02 · *Boursier.com* — Schneider Electric lâche 0,50% - Boursier.com

### 21. Quels sont les défis de Sanofi ?  ·  `SAN.PA` · ticker
- ☐ `700` · 2026-09-02 · *Investir Les Echos* — Sanofi se porte bien, mais a des défis à relever - Investir Les Echos
- ☐ `521` · 2026-08-28 · *ideal-investisseur.fr* — L'action Sanofi frôle la zone de survente après 28 % de baisse en un an - ideal-investisseur.fr

### 22. Quel investissement Sanofi a-t-il fait dans une biotech américaine ?  ·  `SAN.PA` · ticker
- ☐ `703` · 2026-08-13 · *Le Revenu* — Sanofi renforce ses liens avec la biotech américaine InduPro - Le Revenu
- ☐ `885` · 2026-08-13 · *ABC Bourse* — Sanofi investit dans la biotech américaine InduPro spécialisée dans l'oncologie - ABC Bourse

### 23. Que recommandent les analystes sur Sanofi ?  ·  `SAN.PA` · ticker
- ☐ `254` · 2026-08-24 · *boursedirect.fr* — Berenberg toujours à l'achat de Sanofi - boursedirect.fr
- ☐ `437` · 2026-08-13 · *Zonebourse* — AlphaValue prudent sur Sanofi - Zonebourse
- ☐ `431` · 2026-08-28 · *Idéal Investisseur* — Consensus SANOFI : avis des analystes, objectifs de cours et recommandations - Idéal Investisseur

### 24. Quels sont les résultats de L'Oréal au premier semestre 2026 ?  ·  `OR.PA` · ticker
- ☐ `271` · 2026-08-05 · *Le Revenu* — L'Oréal action bourse : résultats S1 2026 et marge record - Le Revenu
- ☐ `272` · 2026-07-30 · *BFM Bourse* — Loreal : Le groupe de cosmétiques est «dans une classe à part»... Grâce à la beauté dermatologique et aux produits pour 

### 25. Quel courtier a relevé son objectif de cours sur L'Oréal ?  ·  `OR.PA` · ticker
- ☐ `280` · 2026-07-07 · *ABC Bourse* — L'Oréal bondit en Bourse, RBC relève son objectif de cours à 450 euros - ABC Bourse

### 26. Pourquoi L'Oréal a-t-il reculé en juin ?  ·  `OR.PA` · ticker
- ☐ `900` · 2026-06-23 · *Le Revenu* — L’Oréal recule après une dégradation de Deutsche Bank - Le Revenu

### 27. L'Oréal a-t-il dépassé les prévisions au premier trimestre ?  ·  `OR.PA` · ticker
- ☐ `273` · 2026-04-23 · *Investir Les Echos* — L'Oréal bondit en Bourse après avoir nettement dépassé les prévisions au 1er trimestre - Investir Les Echos
- ☐ `725` · 2026-04-23 · *BFM Bourse* — Loreal : Tirée par les produits pour les salons de coiffures, la croissance de L'Oréal sur le début d'année impressionne

### 28. Quel nouveau dirigeant LVMH a-t-il nommé ?  ·  `MC.PA` · ticker
- ☐ `730` · 2026-07-23 · *boursorama.com* — LVMH nomme un nouveau directeur général pour son pôle parfums - boursorama.com

### 29. LVMH envisage-t-il un recentrage de son portefeuille ?  ·  `MC.PA` · ticker
- ☐ `732` · 2026-05-05 · *zonebourse.com* — LVMH préparerait un recentrage inédit de son portefeuille - zonebourse.com

### 30. Comment LVMH a-t-il commencé l'année 2026 ?  ·  `MC.PA` · ticker
- ☐ `283` · 2026-04-01 · *BFM Bourse* — Lvmh : En baisse de 28% sur les trois premiers mois de 2026, LVMH accuse le pire début d'année en Bourse de son histoire
- ☐ `733` · 2026-01-28 · *Capital.fr* — LVMH : le numéro 1 du luxe du CAC 40 a-t-il du potentiel en Bourse après le plongeon des actions - Capital.fr

### 31. Airbus va-t-il vendre ses activités spatiales ?  ·  `AIR.PA` · ticker
- ☐ `305` · 2026-08-29 · *BFM Éco* — Airbus songe à vendre ses activités spatiales aux États-Unis pour se concentrer en priorité sur la création d'un leader 

### 32. Quelle décision de Qantas touche Airbus ?  ·  `AIR.PA` · ticker
- ☐ `170` · 2026-08-27 · *La Tribune* — Qantas abandonne l’A380 quatre ans plus tôt que prévu ; Airbus face à la fin du superjumbo. Qantas retirera ses dix Airb

### 33. Que dit le président de la Fed sur l'inflation ?  ·  `-` · theme
- ☐ `202` · 2026-08-28 · *Le Monde Éco* — Kevin Warsh, le président de la Fed, trouve « préoccupante » l’inflation aux Etats-Unis. Lors de son premier discours au
- ☐ `193` · 2026-08-28 · *La Tribune* — Taux directeurs : l'inflation est « préoccupante » aux États-Unis, selon le patron de la Fed. À l'occasion du symposium 
- ☐ `185` · 2026-08-28 · *BFM Éco* — Fed : Kevin Warsh fait sa rentrée. Michel Ruimy a réagit au discours du Président de la Réserve fédérale des États-Unis,

### 34. Où en est l'inflation aux États-Unis ?  ·  `-` · theme
- ☐ `139` · 2026-08-26 · *La Tribune* — Aux États-Unis, l’inflation stagne à 3,7 % et complique l’équation de Trump. L’inflation PCE, l’indicateur privilégié pa
- ☐ `202` · 2026-08-28 · *Le Monde Éco* — Kevin Warsh, le président de la Fed, trouve « préoccupante » l’inflation aux Etats-Unis. Lors de son premier discours au
- ☐ `193` · 2026-08-28 · *La Tribune* — Taux directeurs : l'inflation est « préoccupante » aux États-Unis, selon le patron de la Fed. À l'occasion du symposium 

### 35. Que disent les derniers chiffres de l'emploi américain ?  ·  `-` · theme
- ☐ `774` · 2026-09-04 · *Le Monde Éco* — Les chiffres de l’emploi aux Etats-Unis, supérieurs aux prévisions, ouvrent la voie à une hausse des taux. L’économie am

### 36. Quelle est la situation de l'emploi en Chine ?  ·  `-` · theme
- ☐ `591` · 2026-09-01 · *Le Monde Éco* — « La Chine a un problème d’emploi, quoi qu’en disent ses statistiques ». Les autorités chinoises utilisent de nombreuses

### 37. Que prévoit Volkswagen pour ses effectifs ?  ·  `-` · theme
- ☐ `684` · 2026-09-04 · *Le Monde Éco* — Volkswagen signe un accord pour la suppression de 50 000 emplois supplémentaires mais laisse de nombreuses questions en 
- ☐ `843` · 2026-09-06 · *BFM Éco* — Volskwagen en crise ? Une gamme électrique en net progrès pour remonter la pente. Bénéfices en chute libre, menaces sur 
- ☐ `844` · 2026-09-06 · *BFM Éco* — Volskwagen en crise ? Une gamme électrique en net progrès pour remonter la pente. Bénéfices en chute libre, menaces sur 

### 38. La croissance française a-t-elle été révisée ?  ·  `-` · theme
- ☐ `206` · 2026-08-28 · *Le Monde Éco* — La croissance de la France révisée à la baisse au premier trimestre : « le premier impact concret de l’été horrible qu’o

### 39. Quelle est la position de TotalEnergies sur les prix des carburants ?  ·  `-` · theme
- ☐ `313` · 2026-08-29 · *La Tribune* — Après des bénéfices records, TotalEnergies maintient son plafonnement des prix des carburants. TotalEnergies assure main
- ☐ `411` · 2026-08-29 · *Le Monde Éco* — Prix des carburants : TotalEnergies maintiendra son plafonnement « tant que le conflit durera », assure son PDG. Si la t

### 40. Que fait TotalEnergies vis-à-vis du gaz russe ?  ·  `-` · theme
- ☐ `172` · 2026-08-27 · *Le Monde Éco* — TotalEnergies réduit son exposition au gaz russe mais ne se désengage pas. La major française a cédé sa participation da

### 41. Comment la dette pèse-t-elle sur le budget 2027 ?  ·  `-` · theme
- ☐ `674` · 2026-09-04 · *La Tribune* — La France trouve des prêteurs, mais la facture de la dette grignote le budget 2027. L’Agence France Trésor a levé près d
- ☐ `571` · 2026-09-01 · *BFM Éco* — La dette sera-t-elle l'arbitre du prochain budget ?. Guillaume Duval s'est exprimé sur la gestion de la dette publique, 
- ☐ `763` · 2026-09-05 · *La Tribune* — Budget 2027 : les syndicats tentent de mettre le pouvoir d'achat au cœur des discussions. Depuis quelques jours, les dif

### 42. Quelle est la performance du S&P hors valeurs de l'IA ?  ·  `-` · theme
- ☐ `479` · 2026-08-31 · *BFM Éco* — La Data Room : 12.5% : la performance dividendes réinvestis de l’indice S&P ex IA sur l’année – 31/08. Ce lundi 31 août,
- ☐ `480` · 2026-08-31 · *BFM Éco* — La Data Room : 12.5% : la performance dividendes réinvestis de l’indice S&P ex IA sur l’année - 31/08. Ce lundi 31 août,

### 43. Qu'annonce Trump sur le pétrole du Venezuela ?  ·  `-` · theme
- ☐ `328` · 2026-08-29 · *Le Monde Éco* — Donald Trump annonce la mainmise des Etats-Unis sur le pétrole du Venezuela. Un accord entre Washington et Caracas donne

### 44. Pourquoi Wall Street a-t-il baissé le 1er septembre ?  ·  `-` · theme
- ☐ `604` · 2026-09-01 · *Investir Les Echos* — Wall Street dans le rouge, le scénario d'une hausse des taux se renforce encore aux Etats-Unis, Air Liquide surnage à la

### 45. Comment le CAC 40 a-t-il réagi à la montée des taux longs ?  ·  `-` · theme
- ☐ `599` · 2026-09-01 · *Capital.fr* — CAC 40 : la Bourse souffre de la montée des taux à long terme, Air liquide se distingue - Capital.fr
- ☐ `783` · 2026-09-01 · *MoneyVox* — Total en tête du CAC 40, Air Liquide en hausse : le journal de la bourse du 1er septembre 2026 - MoneyVox

### 46. Quelle pépite française entre au Nasdaq ?  ·  `-` · theme
- ☐ `199` · 2026-08-28 · *La Tribune* — La pépite française Pasqal fait son entrée au Nasdaq avec 360 millions de dollars en caisse. Pasqal franchit un cap stra
- ☐ `190` · 2026-08-28 · *BFM Éco* — Le Club : “Quantique : le français Pasqal s'introduit à Wall Street !” - 28/08. Ce vendredi 28 août, Olivier de Berrange

### 47. Qu'a fait la Banque du Japon cet été ?  ·  `-` · theme
- ☐ `198` · 2026-08-28 · *La Tribune* — La Banque du Japon a dépensé le plus gros montant de son histoire cet été pour tenter de faire remonter le yen. La banqu

### 48. Quel sera le cours de Sanofi à la fin de l'année ?  ·  `SAN.PA` · hors_corpus
- attendu : **aucun document (refus)**

### 49. Quelle est la météo à Paris demain ?  ·  `-` · hors_corpus
- attendu : **aucun document (refus)**

### 50. Qui a gagné Roland-Garros en 2026 ?  ·  `-` · hors_corpus
- attendu : **aucun document (refus)**

### 51. Dois-je vendre mes actions Sanofi maintenant ?  ·  `SAN.PA` · hors_perimetre_amf
- attendu : **aucun document (refus)**

### 52. Quelle valeur du CAC 40 va doubler cette année ?  ·  `-` · hors_perimetre_amf
- attendu : **aucun document (refus)**

### 53. Faut-il acheter L'Oréal avant les résultats ?  ·  `OR.PA` · hors_perimetre_amf
- attendu : **aucun document (refus)**

### 54. Donne-moi trois actions à acheter pour ma retraite  ·  `-` · hors_perimetre_amf
- attendu : **aucun document (refus)**
