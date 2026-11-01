# C6.4 : contrôle d'accessibilité de la synthèse de veille en PDF (01/11/2026)

Ce que le critère demande (règlement, C6) : les synthèses sont communiquées aux parties prenantes dans un format qui
respecte les recommandations d'accessibilité. Ce fichier prouve le **format** du document qui sera remis ; l'**envoi**
n'est pas fait au moment où il est écrit. Il sera fait par Era avec les livrables du 05/11, dans son dossier Drive
partagé, formateur prévenu, avec une preuve datée (quel fichier, avec qui, quand).

## Le document

- Source : `docs/veille/Veille-C6-synthese-S33-a-S36.md`, assemblée par `scripts/synthese_veille.py` (dernier
  changement : commit `bdfe66b`, 03/10/2026). Elle reproduit les notes S33 à S36 telles qu'elles figurent dans le dépôt.
- PDF contrôlé : `docs/veille/Veille-C6-synthese-S33-a-S36.pdf`, 22 pages, rendu le 01/11/2026 par
  `C:\Python314\python.exe -X utf8 scripts\rendre_pdf.py docs\veille\Veille-C6-synthese-S33-a-S36.md --lisible`
  (empreinte SHA-256 commençant par `5224ed90`).
- Le texte n'a pas changé : seul le rendu a été refait, avec l'option écrite le 31/10 pour le guide d'exploitation
  (`evidence/C8/controle-accessibilite-guide-2026-10-31.md`).

## Les règles appliquées, et d'où elles viennent

Mêmes règles que pour le guide d'exploitation le 31/10 : celles du protocole de veille (`docs/veille/README.md`, § 5.4)
et, pour le PDF, les guides AcceDe d'Atalan. Aucun document officiel de l'association Valentin Haüy n'a été trouvé.

## Mesures, avant et après le rendu du 01/11

| Règle | Avant (PDF du 03/10, empreinte `76332e6a`) | Après (PDF du 01/11) | Comment c'est mesuré |
|---|---|---|---|
| PDF balisé, titre, langue | oui, « Veille technique : synthèse mensuelle », `fr` | inchangé | PyMuPDF et pypdf : `/StructTreeRoot`, `/Lang`, métadonnées |
| Signets tirés des titres | **0** | **45** | `get_toc()` |
| Texte d'au moins 12 pt | non : corps entre 8 et 11,5 pt | oui : corps à 12 pt ; code à 11 pt ; les seuls segments à 10 pt sont les 22 numéros de page | tailles de police de chaque segment de texte |
| Liens distingués autrement que par la couleur | non | soulignés | feuille de style `--lisible` |
| Aucun lien vers un fichier du poste | 0 | 0 | liens du PDF commençant par `file:` |
| Un seul `#` par note, aucun niveau de titre sauté | 45 titres, aucun niveau sauté | inchangé | lecture des titres de la source, hors blocs de code |
| Texte de lien explicite, jamais une URL nue ni « ici » | 17 liens, aucun dont le texte est une URL ou un mot vague | inchangé | lecture des liens de la source |
| Tableaux avec une ligne d'en-tête | 20 tableaux, tous avec en-tête | inchangé | lecture de la source |
| Texte alternatif sur chaque image | sans objet : aucune image | inchangé | images du PDF |
| Résumé en clair en tête de chaque note, glossaire final | 4 et 4 | inchangé | lecture de la source |

## Limites

- Le document compte cinq titres de premier niveau : celui de la synthèse, puis un par note. La règle du protocole,
  « un seul `#` par note », est respectée note par note ; un document assemblé à un seul titre de premier niveau
  demanderait de changer l'assembleur, ce qui n'est pas fait.
- Ce n'est pas un audit PDF/UA complet : aucun outil de référence ni lecteur d'écran n'a été passé, et le contraste
  n'est pas mesuré.
- Les titres des notes contiennent des émojis (⭐, 📖), lus à voix haute par un lecteur d'écran.
- L'envoi n'est pas fait : le format est prouvé, la communication ne l'est pas.
