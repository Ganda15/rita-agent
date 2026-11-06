# Accessibilité des pages sources de la veille (C6.8), relevé du 6 novembre 2026

Commande : `C:\Python314\python.exe -X utf8 evidence/C6/mesure-accessibilite-sources.py` (script à côté de ce fichier).
Ce que le script constate et ce qu'il ne mesure pas : voir sa description. Pas un audit RGAA ni WCAG ; les PDF (OWASP, ANSSI) ne sont pas lus.

| Source | Accès sans compte | Langue | Titres (h1 / total) | Sauts de niveau | Images sans alt | Liens vagues | Texte HTML |
|---|---|---|---|---|---|---|---|
| [OWASP GenAI (S34)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | oui (200) | en-US | 1 / 9 | 0 | 0 sur 6 | 0 sur 95 | oui (2420 car.) |
| [ANSSI (S33)](https://messervices.cyber.gouv.fr/guides/recommandations-de-securite-pour-un-systeme-dia-generative) | oui (200) | fr | 1 / 4 | 0 | 0 sur 3 | 1 sur 11 | oui (2285 car.) |
| [CNIL (S34)](https://www.cnil.fr/fr/ia-agentique-cnil-cianum-note) | oui (200) | fr | 1 / 5 | 1 | 0 sur 9 | 0 sur 139 | oui (6868 car.) |
| [NIST AI RMF (S34)](https://www.nist.gov/itl/ai-risk-management-framework) | oui (200) | en | 1 / 12 | 0 | 0 sur 11 | 1 sur 164 | oui (6924 car.) |
| [Simon Willison (S36)](https://simonwillison.net/2026/Aug/27/breaking-claude-code-opus-5-auto-mode/) | oui (200) | en-gb | 1 / 3 | 0 | 0 sur 0 | 0 sur 50 | oui (2990 car.) |
| [Johann Rehberger (S36)](https://embracethered.com/blog/posts/2026/breaking-claude-code-opus-5-and-automode/) | oui (200) | en-us | 2 / 25 | 0 | 0 sur 9 | 0 sur 47 | oui (14974 car.) |
| [The Register (S36)](https://www.theregister.com/research/2026/08/28/researcher-shows-how-claude-code-can-be-tricked-simply-by-asking-it-to-summarize-a-website/5293372) | oui (200) | en-US | 1 / 43 | 1 | 0 sur 13 | 0 sur 162 | oui (9925 car.) |
| [arXiv, préprint (S41)](https://arxiv.org/abs/2610.03448) | oui (200) | en | 7 / 14 | 0 | 0 sur 4 | 0 sur 62 | oui (4692 car.) |
| [NeurIPS, AgentDojo (S41)](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html) | oui (200) | en | 1 / 3 | 1 | 0 sur 0 | 0 sur 10 | oui (2175 car.) |

Constat lu à la main le 06/11 sur la page de Johann Rehberger : une image de l'étape 7 reprend le texte alternatif de l'étape 4, qui ne la décrit pas.
