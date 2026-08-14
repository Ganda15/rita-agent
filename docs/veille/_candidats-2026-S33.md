# Candidats — semaine S33 (du 10 au 16 août 2026)

> ⚠️ **Ce fichier n'est PAS la note de veille.** C'est la matière première : ce qui a été
> repéré, avec de quoi le vérifier. **La sélection, le jugement de fiabilité et la conclusion
> « ce que ça change dans RITA » restent à écrire** dans
> `2026-S33-injection-de-prompt.md`, à partir du gabarit.
>
> Relevé le **2026-08-14** · à vérifier à la source avant citation.

---

## 🔴 Candidat 1 — OWASP Top 10 for LLM Applications, **édition 2026**

| | |
|---|---|
| **Source** | OWASP GenAI Security Project |
| **Auteur** | fondation OWASP — à but non lucratif, contributeurs nommés |
| **Date annoncée** | **6 août 2026** — donc **cette semaine ou la précédente** |
| **Lien** | [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) |

**Ce qui est rapporté** :

- **L'injection de prompt reste n°1**, pour la **troisième année consécutive**.
- La catégorie **absorbe désormais les attaques inter-modales** — instructions cachées dans une
  **image** ou un **son**, plus seulement dans du texte.
- **Changement de méthode** : le classement est pour la première fois adossé à des incidents
  réels — **75 % vote d'experts, 25 % données issues de 6 639 incidents** recensés.
- **« Excessive Agency » passe de la 6ᵉ à la 3ᵉ place.**
- **« System Prompt Leakage » devient « Hidden Context Exposure »**.

> ⚠️ **À vérifier avant de citer** : le 14/08, la page officielle `genai.owasp.org/llm-top-10/`
> affichait encore l'**édition 2025**. L'édition 2026 n'est pour l'instant attestée que par la
> **presse spécialisée**. **Va voir la source primaire toi-même** — si elle n'est pas encore
> publiée, c'est **cela** qu'il faut écrire dans la note. *Une information reprise par cinq
> sites reste une information non vérifiée si aucun n'est la source.*

**Lien possible avec RITA** : ton garde-fou `guardrails/injection.py` ne filtre que du **texte**.
RITA lit-il des images ? (Réponse à chercher dans `sources/scraper.py`.)

---

## 🔴 Candidat 2 — « The lethal trifecta for AI agents » (Simon Willison)

| | |
|---|---|
| **Auteur** | **Simon Willison** — co-créateur de Django, a **inventé le terme *prompt injection* en 2022** |
| **Date** | 16 juin 2025 — **plus ancien**, mais devenu le cadre de référence en 2026 |
| **Intérêts** | blog personnel, ne vend aucune solution de sécurité |
| **Lien** | [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) |

**L'idée** : trois capacités qui, **réunies**, rendent l'exploitation quasi certaine —

1. **accès à des données privées**,
2. **exposition à du contenu non fiable**,
3. **moyen de communiquer vers l'extérieur**.

> *« L'attaque n'a pas besoin que le modèle se rebelle. Il lui suffit qu'il suive les
> instructions — ce qui est sa fonction même. »*

**Lien possible avec RITA — la question à te poser** : RITA réunit-il les trois ?
Données privées (`position`, le portefeuille) · contenu non fiable (`sources/scraper.py`,
`sources/rss.py`) · communication externe (**le traçage LangSmith vers les États-Unis**, que
**ton propre registre RGPD classe déjà en risque 🔴 haute, traitement T3**).
**Si les trois sont réunis, c'est le point le plus important de ta veille cette année.**

---

## 🟠 Candidat 3 — ANSSI / CERT-FR : agents IA autonomes sur postes de travail

| | |
|---|---|
| **Source** | ANSSI — agence nationale, **aucun intérêt commercial**, site public soumis au RGAA |
| **Référence** | bulletin **CERTFR-2026-ACT-016** |
| **Date rapportée** | 13 avril 2026 |
| **Lien** | [CERT-FR — bulletins d'actualité](https://www.cert.ssi.gouv.fr/) |

**Ce qui est rapporté** : alerte sur les **agents IA autonomes installés sur des postes de
travail**, avec **recommandation de les proscrire en production**. À lire à la source : la
formulation exacte compte, et la presse la résume mal.

**Lien possible avec RITA** : RITA n'est pas un agent de poste de travail — mais l'argumentaire
de l'ANSSI sur *pourquoi* un agent autonome est risqué est **directement transposable** à ton
chapitre garde-fous, et c'est une **source française et officielle** (précieux devant un jury).

---

## 🟠 Candidat 4 — ANSSI : « Recommandations de sécurité pour un système d'IA générative »

| | |
|---|---|
| **Date** | 29 avril 2024 — **le socle**, pas une nouveauté |
| **Contenu** | **35 recommandations** : sécurité sur tout le cycle de vie, analyse de risque, DevSecOps, confidentialité des données, contrôle du code source |
| **Limite** | ⚠️ **ne traite pas l'agentique** — mise à jour annoncée tous les 12 mois |
| **Lien** | [MesServicesCyber — recommandations de sécurité pour un système d'IA générative](https://messervices.cyber.gouv.fr/guides/recommandations-de-securite-pour-un-systeme-dia-generative) |

**Lien possible avec RITA** : c'est le document à citer si le jury demande *« sur quel
référentiel français vous appuyez-vous ? »*.

---

## ⚪ Candidat 5 — CERT-FR : menaces liées à l'IA générative

| | |
|---|---|
| **Référence** | **CERTFR-2026-CTI-001** — 12 pages, daté du 4 février 2026 |
| **Lien** | [CERTFR-2026-CTI-001 (PDF)](https://www.cert.ssi.gouv.fr/uploads/CERTFR-2026-CTI-001.pdf) |

Panorama de menaces. Plus contextuel que technique — utile en introduction de note.

---

## ❌ Écartés cette semaine — et c'est un acte de veille

La recherche a massivement remonté des **blogs d'éditeurs de sécurité** commentant le Top 10
OWASP : Mend, ReversingLabs, Repello AI, HiddenLayer, Sophos, Airia, Webnestify.

**Tous écartés**, en application du protocole (`README.md`, §3) : ils décrivent le problème
qu'ils vendent — **conflit d'intérêts direct**. Également écarté un article **Medium** signé
d'un pseudonyme : **auteur non identifiable**, donc critère de fiabilité non satisfait.

> 💡 Ces sources ne sont pas fausses. Elles sont **non indépendantes** — et le critère C6
> demande *« absence d'intérêts personnels »*, pas « absence d'erreurs ».

---

## ▶️ Ta séance d'une heure — proposition de déroulé

| Temps | Quoi |
|---|---|
| **0–10 min** | Ouvrir la page OWASP officielle. **L'édition 2026 est-elle vraiment publiée ?** Noter ce que tu constates, pas ce que la presse annonce. |
| **10–25 min** | Lire « the lethal trifecta » en entier. |
| **25–40 min** | Répondre par écrit : **RITA réunit-il les 3 conditions ?** Ouvrir `db/RGPD-registre-des-traitements.md` §T3. |
| **40–55 min** | Remplir la note depuis le gabarit — surtout **« Ce que ça change dans RITA »**. |
| **55–60 min** | Passer la liste de contrôle d'accessibilité. Enregistrer, commiter. |
