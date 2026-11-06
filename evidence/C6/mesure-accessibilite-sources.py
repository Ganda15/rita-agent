r"""Mesure simple de l'accessibilité des pages sources de la veille (C6.8), relevée le 06/11/2026.

Pourquoi : le référentiel demande de privilégier les sources « respectant les normes d'accessibilité ». Ce script relève,
page par page, ce qu'un programme peut constater sans navigateur : la page est servie sans connexion, la langue est
déclarée, les titres existent et ne sautent pas de niveau, les images ont un texte alternatif, les liens ont un texte
explicite, le texte est du HTML (donc lisible et sélectionnable). Ce n'est pas un audit RGAA ni WCAG : le contraste, la
navigation au clavier et la lecture par un lecteur d'écran ne sont pas mesurés, et les documents PDF ne sont pas lus.

Lancement : C:\Python314\python.exe -X utf8 evidence/C6/mesure-accessibilite-sources.py
"""
from html.parser import HTMLParser
from urllib.request import Request, urlopen

SOURCES = [
    ("OWASP GenAI (S34)", "https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/"),
    ("ANSSI (S33)", "https://messervices.cyber.gouv.fr/guides/recommandations-de-securite-pour-un-systeme-dia-generative"),
    ("CNIL (S34)", "https://www.cnil.fr/fr/ia-agentique-cnil-cianum-note"),
    ("NIST AI RMF (S34)", "https://www.nist.gov/itl/ai-risk-management-framework"),
    ("Simon Willison (S36)", "https://simonwillison.net/2026/Aug/27/breaking-claude-code-opus-5-auto-mode/"),
    ("Johann Rehberger (S36)", "https://embracethered.com/blog/posts/2026/breaking-claude-code-opus-5-and-automode/"),
    ("The Register (S36)", "https://www.theregister.com/research/2026/08/28/researcher-shows-how-claude-code-can-be-tricked-simply-by-asking-it-to-summarize-a-website/5293372"),
    ("arXiv, préprint (S41)", "https://arxiv.org/abs/2610.03448"),
    ("NeurIPS, AgentDojo (S41)", "https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html"),
]
LIENS_VAGUES = {"ici", "cliquez ici", "click here", "here", "lire la suite", "read more", "en savoir plus", "lien",
                "more", "plus", "learn more"}


class Releve(HTMLParser):
    def __init__(self):
        super().__init__()
        self.langue, self.titres, self.images, self.sans_alt = None, [], 0, 0
        self.liens, self.liens_vagues, self._lien, self._texte_lien = 0, 0, False, ""
        self._ignore, self.texte = 0, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.langue = a.get("lang")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.titres.append(int(tag[1]))
        elif tag == "img":
            self.images += 1
            self.sans_alt += "alt" not in a
        elif tag == "a" and a.get("href"):
            self.liens, self._lien, self._texte_lien = self.liens + 1, True, ""
        elif tag in ("script", "style"):
            self._ignore += 1

    def handle_endtag(self, tag):
        if tag == "a" and self._lien:
            self.liens_vagues += self._texte_lien.strip().lower() in LIENS_VAGUES
            self._lien = False
        elif tag in ("script", "style") and self._ignore:
            self._ignore -= 1

    def handle_data(self, data):
        if not self._ignore:
            self.texte += len(data.strip())
            if self._lien:
                self._texte_lien += data


def sauts(niveaux):
    return sum(1 for avant, apres in zip(niveaux, niveaux[1:]) if apres > avant + 1)


print("| Source | Accès sans compte | Langue | Titres (h1 / total) | Sauts de niveau | Images sans alt | Liens vagues | Texte HTML |")
print("|---|---|---|---|---|---|---|---|")
for nom, url in SOURCES:
    try:
        with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
            code, html = r.status, r.read().decode("utf-8", "replace")
    except Exception as e:  # une source injoignable est notée, pas cachée
        print(f"| {nom} | erreur : {type(e).__name__} | | | | | | |")
        continue
    p = Releve()
    p.feed(html)
    print(f"| [{nom}]({url}) | oui ({code}) | {p.langue or 'non déclarée'} | {p.titres.count(1)} / {len(p.titres)} | "
          f"{sauts(p.titres)} | {p.sans_alt} sur {p.images} | {p.liens_vagues} sur {p.liens} | "
          f"{'oui' if p.texte > 500 else 'non'} ({p.texte} car.) |")
