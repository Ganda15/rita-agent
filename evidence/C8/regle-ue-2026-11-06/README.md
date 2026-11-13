# La règle « UE seule » précisée, puis vérifiée pour Azure et pour Langfuse, 6 novembre 2026

## 1. Ma décision, datée du 06/11/2026

L'ancienne règle (registre RGPD, § 0, posée le 05/10) : « aucune donnée personnelle ne quitte l'Union européenne ».
Le registre précise que c'est un choix du projet, pas une exigence du référentiel (C4 demande une base « dans le
respect du RGPD »), plus strict que le RGPD, qui autorise les transferts encadrés (articles 45 et 46).

Pourquoi la préciser. Aucun des deux sous-traitants qui reçoivent des données de RITA ne garantit la lettre de
l'ancienne règle : chacun prévoit dans son contrat des sorties de la région. Microsoft qualifie lui-même l'accès à
distance de son personnel de transfert, comme le CEPD (lignes directrices 05/2021, § 9, cité au registre). Garder une
promesse que le contrat dément ne protège personne.

La règle précisée : RITA utilise des services configurés dans leurs régions de l'Union européenne. Elle ne promet
plus l'absence absolue de transfert hors de l'Union : pour chaque sous-traitant, les exceptions prévues par son contrat
sont identifiées, leurs garanties vérifiées, et les données envoyées limitées au nécessaire.

Ce que la décision ne fait pas : elle ne rend aucun critère vert. Le statut de C8.2 (E2) et de la ligne C11 sur
l'outil de monitorage (E3) dépend des vérifications ci-dessous, service par service.

## 2. Azure (Microsoft), le service de modèle (registre T6 et T8)

| Question | Constat | Source |
|---|---|---|
| Configuration | déploiement `gpt-5.4-dzs-eu` en Data Zone Standard EU, ressource en `swedencentral` ; trois appels du 09/10 servis en Sweden Central | portail Azure (capture du 06/11, `evidence/C8/captures-2026-11-06/`) ; `evidence/C8/preuve-deploiement-zone-eu-2026-10-09.md` |
| Données envoyées | briefing : valeur, cours, variation, capitaux moyens, devise, fraîcheur, 13 indicateurs, passages de presse ; aucune position, aucun prix de revient, aucune quantité. Question : le texte libre de la question, qui peut contenir une donnée personnelle, et des passages d'articles | registre T6 et T8 ; `agents/analyst.py` |
| Contrat applicable | « Microsoft Products and Services Data Protection Addendum », version « Last updated November 1, 2026 », engageante depuis le 01/11/2026 | <https://www.microsoft.com/licensing/docs/view/Microsoft-Products-and-Services-Data-Protection-Addendum-DPA>, document anglais téléchargé et lu le 06/11 |
| Transferts | section « Data Transfers » : tout transfert hors de l'UE, de l'EEE, du Royaume-Uni et de la Suisse est soumis aux clauses contractuelles types de 2021 (module de sous-traitant à sous-traitant, Microsoft Ireland Operations Limited vers Microsoft Corporation) ; « In addition, Microsoft is certified to the EU-U.S. […] Data Privacy Frameworks » | DPA, sections « Definitions » et « Data Transfers » |
| Certification, vérifiée sur la liste officielle | Microsoft Corporation : Active Participant ; EU-U.S. Data Privacy Framework Active, certification d'origine du 12/08/2016, prochaine échéance le 31/08/2027 ; données RH et hors RH | <https://www.dataprivacyframework.gov/list>, consultée le 06/11 ; capture `dpf-microsoft-liste-officielle-2026-11-06.jpg` |
| Localisation | section « Location of Customer Data » : pour les services de l'EU Data Boundary, stockage et traitement dans l'UE et l'AELE, « as set forth in the Product Terms » | DPA |
| Exceptions documentées | accès à distance du personnel depuis l'extérieur, opérations de sécurité, acheminement réseau | `evidence/C8/verification-conditions-microsoft-2026-11-06.md` (pages de Microsoft du 21/07 et du 04/11/2026) |
| Usage des données | seulement pour fournir le service et les opérations qui en découlent ; jamais pour du profilage, de la publicité ou des études de marché | DPA, « Nature of Data Processing; Ownership » |
| Sous-traitants ultérieurs | autorisés, liste publiée par Microsoft ; préavis de 6 mois, 30 jours pour un sous-traitant d'intelligence artificielle | DPA, « Notice and Controls on use of Subprocessors » |
| Conservation | données du client : 90 jours après la fin de l'abonnement, puis suppression sous 90 jours ; l'échantillon de la surveillance des abus : durée non indiquée | DPA, « Data Retention and Deletion » ; pages de surveillance des abus |

### Bilan Azure

- Vérifié : configuration en zone UE ; contrat applicable identifié et lu sur les transferts, la localisation,
  l'usage, les sous-traitants et la conservation ; garanties des transferts : clauses types de 2021 et certification
  au Data Privacy Framework, vérifiée sur la liste officielle, ce qui place un transfert vers Microsoft Corporation sous
  la décision d'adéquation (article 45, registre § 5).
- Preuve : ce tableau, le DPA du 01/11/2026, la capture de la liste officielle, la note du 06/11 sur les pages de
  Microsoft.
- Points restants : (1) l'écran Question n'invite pas à taire les données personnelles : le texte libre part tel
  quel vers Azure ; les données envoyées ne sont donc pas « limitées au nécessaire » pour ce parcours ; (2) la durée de
  conservation de l'échantillon de la surveillance des abus n'est pas connue ; (3) la présence du service de modèle
  d'Azure dans la liste des services de l'EU Data Boundary (Product Terms) n'est pas vérifiée ici.

## 3. Langfuse (ClickHouse), l'outil de monitorage (registre T3)

| Question | Constat | Source |
|---|---|---|
| Configuration | Langfuse Cloud, région UE, `https://cloud.langfuse.com` (AWS `eu-west-1`, Irlande) ; 30 jours de conservation (palier gratuit) | `src/traces.py`, ligne 40 ; registre T3 |
| Données envoyées | métadonnées seules depuis le 20/10 (décision D9) : identifiant de requête, valeur demandée pour un briefing, verdict des garde-fous, noms et durées des étapes, fournisseur, modèle, tentative, jetons, type d'une erreur ; pour une question : statut, motif, longueur et identifiants des articles cités ; attributs techniques du SDK (nom du service, identifiant d'instance). Jamais le prompt ni le texte produit | `src/traces.py`, en-tête et lignes 155 à 360 |
| Ces métadonnées sont-elles anonymes ? | Non : la valeur demandée et l'heure disent ce qui intéresse l'utilisateur ; l'identifiant de requête relie la trace aux journaux du serveur | registre T3, mise à jour du 21/10 |
| Contrat applicable | « ClickHouse Customer Data Processing Addendum », en vigueur le 10/04/2026 ; Langfuse GmbH (Allemagne) au sein du groupe ClickHouse | <https://clickhouse.com/legal/agreements/data-processing-addendum>, relu le 06/11 |
| Localisation et exceptions | § 6.1 : hébergement dans la région choisie ; pas de transfert hors de cette région « except as reasonably necessary to provide the Services or as necessary to comply with the law or binding order » ; aucune clause sur l'accès à distance du personnel | DPA, § 6.1 |
| Garanties des transferts | § 6.2 : hors de l'EEE, clauses contractuelles types ; § 6.5 : dans la mesure où ClickHouse est certifiée au Data Privacy Framework, un transfert vers les États-Unis n'est pas un transfert restreint | DPA, § 6.2 et § 6.5 |
| Certification, vérifiée sur la liste officielle | ClickHouse, Inc. : Active Participant ; EU-U.S. Data Privacy Framework Active, certification d'origine du 09/05/2024, prochaine échéance le 11/04/2027 ; données hors RH ; ClickHouse s'y déclare sous-traitant des données de ses clients ; aucune autre entité couverte | <https://www.dataprivacyframework.gov/list>, consultée le 06/11 ; capture `dpf-clickhouse-liste-officielle-2026-11-06.jpg` |

### Bilan Langfuse

- Vérifié : région UE ; données envoyées limitées à des métadonnées, non anonymes, sans prompt ni texte ; contrat
  applicable identifié et relu (§ 6.1, 6.2, 6.5) ; certification de ClickHouse, Inc. au Data Privacy Framework vérifiée
  sur la liste officielle, ce qui place un transfert vers elle sous la décision d'adéquation (article 45).
- Preuve : ce tableau, le DPA du 10/04/2026, la capture de la liste officielle, `src/traces.py`.
- Points restants : l'exception du § 6.1 n'est ni chiffrée ni décrite par l'éditeur, on ne peut pas la dire
  « rare » ; aucune clause sur l'accès à distance du personnel ; la certification couvre ClickHouse, Inc., pas les
  entités européennes du groupe, qui n'en ont pas besoin.

## 4. Réévaluation des critères, sans passage automatique au vert

| Critère | Lecture au 06/11 | Proposition |
|---|---|---|
| E2, C8.2 « configuré selon les besoins et les contraintes » | configuration UE vérifiée et garanties vérifiées ; mais le parcours Question envoie un texte libre sans consigne de minimisation | reste à consolider tant que l'écran Question ne dit pas de ne pas y écrire de donnée personnelle ; à réévaluer après ce correctif |
| E3, C11 « outils adaptés au contexte et aux contraintes » (règle UE) | règle précisée ; région UE ; métadonnées seules ; contrat relu ; certification vérifiée sur la liste officielle | tenu, sous réserve du double contrôle ; limites écrites : exception du § 6.1 non chiffrée, aucune clause sur l'accès à distance |

## Glossaire

- **Transfert** (RGPD, chapitre V) : toute mise à disposition de données personnelles à un destinataire hors de l'EEE,
  y compris un accès à distance depuis un pays tiers.
- **Décision d'adéquation** (article 45) : décision de la Commission européenne qui reconnaît une protection suffisante ;
  celle du 10/07/2023 couvre les entreprises américaines certifiées au Data Privacy Framework.
- **Clauses contractuelles types** (article 46) : contrat type de la Commission qui encadre un transfert ; la CNIL demande
  alors une analyse d'impact du transfert.
- **Data Privacy Framework** : programme américain d'autocertification ; la liste officielle est tenue par le
  Département du Commerce des États-Unis.
- **DPA** (*Data Processing Addendum*) : avenant au contrat qui fixe les obligations du sous-traitant.
- **Métadonnées** : données sur un traitement (durée, modèle, identifiant), pas son contenu ; elles peuvent rester
  personnelles.
