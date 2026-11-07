# C15 · Réévaluation des prestataires au regard de leur démarche éco-responsable, 6 novembre 2026

**Le critère** (règlement, page 30) : « Les éventuels services (PaaS, SaaS, etc) et prestataires ayant une démarche
éco-responsable sont favorisés lors des choix techniques. »

**Pourquoi cette preuve.** L'hébergeur de RITA, Hetzner, a été choisi le 19/08 pour une raison de continuité : un serveur
payé ne s'éteint pas avant le jury, contrairement aux offres gratuites de Render et de Railway, qui expiraient avant le 05/11 (`CONTINUITE.md`,
décisions ; rapport E4 v1.6, § 2.5). Son impact environnemental n'était pas un critère de ce choix, et cette note ne
le réécrit pas. Le 06/11, après le retour du formateur, le choix des prestataires est **réévalué avec ce critère**, et
la règle est écrite pour les choix suivants.

## Ce que publient les prestataires, relevé du 06/11/2026

| Prestataire et usage | Ce qu'il publie sur son énergie et son efficacité | Source | Ce qui reste incertain |
|---|---|---|---|
| **Hetzner**, serveur CX23 à Falkenstein (Allemagne), qui héberge l'API et l'interface | « 100 percent of our electricity from renewable energy sources » en Allemagne ; PUE moyen de 1,13 ; Hetzner écrit lui-même ne pas être encore « completely climate neutral » | <https://docs.hetzner.com/general/company-and-policy/sustainability-at-hetzner/> (modifiée le 03/09/2026) | chiffres déclarés par l'hébergeur, non audités ici ; aucun chiffre pour le seul serveur de RITA |
| **Microsoft Azure**, service de modèle | chiffres d'entreprise de l'exercice 2025 : électricité renouvelable directe à 100 %, PUE moyen de 1,17 ; aucun chiffre par modèle | relevé du 03/10, `evidence/C7/prix-et-environnement-2026-10-03.md` (rapport E2, § 3.5) | l'empreinte d'un briefing n'est pas connue |
| **Langfuse Cloud**, traçage, région UE | non relevé | | à relever avant la prochaine décision sur Langfuse (registre RGPD, § 5) |

## La décision du 06/11

- **Hetzner est gardé.** Il publie une électricité renouvelable en Allemagne et une efficacité énergétique mesurée (PUE de
  1,13) ; il répond aussi aux autres contraintes du projet : serveur dans l'Union européenne, coût connu (7,19 € par
  mois), continuité jusqu'au jury.
- **La règle pour les choix suivants** : à coût et à continuité comparables, le prestataire qui publie son énergie et
  son efficacité, vérifiables, est préféré ; un prestataire qui ne publie rien est noté « non relevé » et ne peut pas
  être retenu sur ce critère.

## Ce que cette réévaluation ne prouve pas

- Le choix du 19/08 n'a pas été fait sur ce critère : la réévaluation est datée du 06/11, elle ne remonte pas le temps.
- Aucune comparaison chiffrée avec un autre hébergeur n'est faite ici.
- Les chiffres sont ceux que publient les prestataires ; aucun n'est audité dans ce projet.
- Langfuse n'est pas encore relevé.

## 📖 Glossaire

- **PUE** (Power Usage Effectiveness) : énergie totale du centre de données divisée par l'énergie des seuls serveurs ;
  1 serait parfait.
- **Neutralité carbone** : compenser ou éviter autant d'émissions qu'on en produit ; Hetzner dit ne pas l'avoir atteinte.
- **Prestataire** : entreprise qui fournit un service au projet (hébergement, modèle, traçage).
