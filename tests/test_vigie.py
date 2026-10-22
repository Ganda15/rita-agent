"""Sprint 5, étape 4 : la vigie (plan du sprint 5, § 2 « Vigie » et « Alerte », étapes 4, 6 et 7).

La vigie regarde l'API de dehors : une API arrêtée ne peut pas annoncer sa propre panne. Elle sonde `/health` (deux
essais à 10 secondes d'écart), puis lit `/sante` et ses verdicts. Un signal en « problème » ouvre UNE issue, au titre
stable : jamais de doublon. Un signal résolu ferme son issue avec un commentaire. Après une panne, « service rétabli »
et « alerte résolue » sont deux constats distincts. Aucun test ne parle à GitHub ni au réseau : tout est remplacé.
"""
import json
from datetime import date

import pytest

from api.sante import construire
from monitorage import seuils, vigie
from monitorage.compteurs import Compteurs
from tests.conftest import CLE_DE_TEST

ADRESSE = "http://localhost:8011"
MAINTENANT = 1_000_000.0


class _Reponse:
    def __init__(self, code, corps=None):
        self.status_code, self._corps = code, corps

    def json(self):
        return self._corps


class _Http:
    """`http_get` remplacé : une file de réponses par adresse ; une exception dans la file est levée."""

    def __init__(self, sante=None, health=(200,)):
        self.files = {f"{ADRESSE}/health": [_Reponse(c) if isinstance(c, int) else c for c in health],
                      f"{ADRESSE}/sante": [sante] if sante is not None else []}
        self.appels = []

    def __call__(self, url, entetes):
        self.appels.append((url, entetes))
        suivant = self.files[url].pop(0) if len(self.files[url]) > 1 else self.files[url][0]
        if isinstance(suivant, Exception):
            raise suivant
        return suivant


class _GitHub:
    def __init__(self, ouvertes=None, commentaires=None):
        self.ouvertes = dict(ouvertes or {})
        self._commentaires = {n: list(c) for n, c in (commentaires or {}).items()}
        self.ouvertures, self.fermetures = [], []

    def issues_ouvertes(self):
        return dict(self.ouvertes)

    def ouvrir(self, titre, corps):
        self.ouvertures.append((titre, corps))

    def commenter(self, numero, corps):
        self._commentaires.setdefault(numero, []).append(corps)

    def fermer(self, numero, commentaire):
        self.fermetures.append((numero, commentaire))

    def commentaires(self, numero):
        return list(self._commentaires.get(numero, []))


def _sante(*appels):
    """Ce que `/sante` rendrait : chaque appel est (secondes avant maintenant, code, statut, motif)."""
    horloge = [MAINTENANT]
    mesures = Compteurs(horloge=lambda: horloge[0])
    for avant, code, statut, motif in appels:
        horloge[0] = MAINTENANT - avant
        mesures.noter("/question", code, statut, motif, 900, (2000, 300))
    horloge[0] = MAINTENANT
    lignes = [{"ticker": "MC.PA", "derniere_seance": date(2026, 10, 21), "aujourdhui": date(2026, 10, 22)}]
    return _Reponse(200, construire(mesures, lignes, MAINTENANT, date(2026, 10, 22)))


def _passage(http, github, attentes=None):
    attentes = [] if attentes is None else attentes
    return vigie.passage(ADRESSE, CLE_DE_TEST, http, github, attentes.append, lambda: MAINTENANT, seuils.charger())


SAIN = [(60, 200, "reponse", "OK")] * 12
ATTAQUE = [(60, 200, "reponse", "OK")] * 2 + [(30, 200, "refus", "TENTATIVE_DETOURNEMENT")] * 12


# --- la sonde du service ---------------------------------------------------------------------------------------------------

def test_une_sonde_qui_echoue_une_fois_puis_repond_n_ouvre_rien():
    attentes, github = [], _GitHub()
    actions, code = _passage(_Http(_sante(*SAIN), health=[ConnectionError("refus"), 200]), github, attentes)
    assert (actions, code, github.ouvertures) == ([], 0, [])
    assert attentes == [10]


def test_deux_sondes_en_echec_ouvrent_l_alerte_service_sans_lire_sante():
    http, github = _Http(_sante(*SAIN), health=[500, 500]), _GitHub()
    actions, code = _passage(http, github)
    assert code == 1
    [(titre, corps)] = github.ouvertures
    assert titre == vigie.titre("service") and "2 sondes" in corps and "docs/exploitation.md#" in corps
    assert all(not url.endswith("/sante") for url, _ in http.appels)


def test_le_service_retabli_ferme_l_alerte_service():
    github = _GitHub(ouvertes={vigie.titre("service"): 3})
    _passage(_Http(_sante(*SAIN)), github)
    [(numero, commentaire)] = github.fermetures
    assert numero == 3 and "Retour à la normale" in commentaire


# --- un problème, une issue, jamais de doublon ---------------------------------------------------------------------------

def test_un_probleme_ouvre_une_issue_qui_dit_tout_sauf_la_cle():
    github = _GitHub()
    actions, code = _passage(_Http(_sante(*ATTAQUE)), github)
    assert code == 1
    [(titre, corps)] = github.ouvertures
    assert titre == vigie.titre("refus_securite")
    for attendu in ("85,7 %", "12 sur 14", "30,0 %", "au moins 10 requêtes", ADRESSE,
                    "docs/exploitation.md#alerte-refus-de-securite"):
        assert attendu in corps, attendu
    assert CLE_DE_TEST not in corps
    assert actions == [f"ouverte : {titre}"]


def test_un_second_passage_n_ouvre_pas_de_doublon():
    github = _GitHub(ouvertes={vigie.titre("refus_securite"): 7})
    actions, code = _passage(_Http(_sante(*ATTAQUE)), github)
    assert (github.ouvertures, github.fermetures, code) == ([], [], 1)


def test_un_signal_resolu_ferme_son_issue_avec_un_commentaire():
    github = _GitHub(ouvertes={vigie.titre("refus_securite"): 7})
    actions, code = _passage(_Http(_sante(*SAIN)), github)
    [(numero, commentaire)] = github.fermetures
    assert numero == 7 and "Retour à la normale" in commentaire and code == 0


def test_des_refus_sous_le_minimum_gardent_l_issue_ouverte():
    github = _GitHub(ouvertes={vigie.titre("refus_securite"): 7})
    _passage(_Http(_sante(*[(30, 200, "refus", "TENTATIVE_DETOURNEMENT")] * 3)), github)
    assert github.fermetures == []


# --- après une panne : service rétabli, puis alerte résolue ----------------------------------------------------------------

PANNE_FINIE = [(120, 503, "erreur", "FOURNISSEUR_INDISPONIBLE")] * 5 + [(10, 200, "reponse", "OK")]


def test_la_panne_finie_donne_service_retabli_une_seule_fois_sans_fermer():
    titre = vigie.titre("erreurs_techniques")
    github = _GitHub(ouvertes={titre: 9})
    _passage(_Http(_sante(*PANNE_FINIE)), github)
    [commentaire] = github.commentaires(9)
    assert commentaire.startswith("Service rétabli")
    fin_attendue = vigie._hh_mm(MAINTENANT - 120 + 15 * 60)
    assert f"jusqu'à {fin_attendue} environ" in commentaire
    assert github.fermetures == []
    _passage(_Http(_sante(*PANNE_FINIE)), github)
    assert len(github.commentaires(9)) == 1


def test_une_panne_en_cours_ne_dit_pas_service_retabli():
    github = _GitHub(ouvertes={vigie.titre("erreurs_techniques"): 9})
    _passage(_Http(_sante(*[(60, 503, "erreur", "FOURNISSEUR_INDISPONIBLE")] * 5)), github)
    assert github.commentaires(9) == [] and github.fermetures == []


# --- quand la vigie ne peut pas lire /sante --------------------------------------------------------------------------------

def test_sante_illisible_donne_le_code_2_sans_issue_et_sans_la_cle():
    github = _GitHub()
    actions, code = _passage(_Http(_Reponse(403, {"detail": "Cle d'API invalide ou absente"})), github)
    assert code == 2 and github.ouvertures == []
    assert any("HTTP 403" in a for a in actions) and not any(CLE_DE_TEST in a for a in actions)


# --- la commande, et GitHub par gh ----------------------------------------------------------------------------------------

def test_sans_l_option_github_rien_n_est_envoye_a_github(monkeypatch, capsys):
    def interdit(*args, **kwargs):
        raise AssertionError("GitHub ne doit pas être appelé sans --github")

    monkeypatch.setattr(vigie, "GitHubCli", interdit)
    monkeypatch.setattr(vigie, "_http_get", _Http(_sante(*ATTAQUE)))
    monkeypatch.setenv("RITA_API_KEY", CLE_DE_TEST)
    assert vigie.main(["--adresse", ADRESSE]) == 1
    sortie = capsys.readouterr().out
    assert "à blanc" in sortie and vigie.titre("refus_securite") in sortie and CLE_DE_TEST not in sortie


def test_sans_cle_la_commande_s_arrete_avec_le_code_2(monkeypatch, capsys):
    monkeypatch.setenv("RITA_API_KEY", "")
    assert vigie.main(["--adresse", ADRESSE]) == 2
    assert "RITA_API_KEY" in capsys.readouterr().out


class _Executeur:
    def __init__(self, sortie=""):
        self.sortie, self.appels = sortie, []

    def __call__(self, arguments, **options):
        self.appels.append((arguments, options))

        class _Resultat:
            stdout = self.sortie
        return _Resultat()


def test_gh_est_appele_par_une_liste_d_arguments_sans_shell():
    executeur = _Executeur()
    vigie.GitHubCli(executer=executeur).ouvrir("Incident : vigie (prototype local) « x »", "corps")
    [(arguments, options)] = executeur.appels
    assert arguments == ["gh", "issue", "create", "--title", "Incident : vigie (prototype local) « x »",
                         "--body-file", "-", "--label", "incident", "--label", "E5", "-R", "Ganda15/rita-agent"]
    assert options["input"] == "corps" and not options.get("shell", False) and options["check"] is True


def test_les_issues_ouvertes_sont_celles_de_la_vigie_seulement():
    sortie = json.dumps([{"number": 4, "title": vigie.titre("fraicheur")},
                         {"number": 5, "title": "Incident : alerte Langfuse « latence »"}])
    executeur = _Executeur(sortie)
    assert vigie.GitHubCli(executer=executeur).issues_ouvertes() == {vigie.titre("fraicheur"): 4}


@pytest.mark.parametrize("methode, arguments, attendu", [
    ("commenter", (9, "texte"), ["gh", "issue", "comment", "9", "--body-file", "-", "-R", "Ganda15/rita-agent"]),
    ("fermer", (9, "fin"), ["gh", "issue", "close", "9", "--comment", "fin", "-R", "Ganda15/rita-agent"]),
])
def test_commenter_et_fermer(methode, arguments, attendu):
    executeur = _Executeur()
    getattr(vigie.GitHubCli(executer=executeur), methode)(*arguments)
    assert executeur.appels[0][0] == attendu


def test_les_commentaires_d_une_issue():
    executeur = _Executeur(json.dumps({"comments": [{"body": "Service rétabli à 16:05"}]}))
    assert vigie.GitHubCli(executer=executeur).commentaires(9) == ["Service rétabli à 16:05"]


# --- chaque signal se lit comme une phrase, dans l'issue -----------------------------------------------------------------

def _verdict(signal, **surcharges):
    from tests.test_seuils import _etat
    return seuils.evaluer(_etat(**surcharges), seuils.charger())[signal]


@pytest.mark.parametrize("signal, surcharges, valeur_attendue, seuil_attendu", [
    ("latence_p95_ms", {"latence_p95_ms": {"valeur": 25_000, "effectif": 20}},
     "25,0 s (p95 de 20 résultats, 15 dernières minutes)", "problème à partir de 20 s, attention à partir de 10 s"),
    ("latence_p95_ms", {"latence_p95_ms": {"valeur": None, "effectif": 0}}, "aucune requête", "au moins 5 requêtes"),
    ("refus_securite", {"refus_securite": {"valeur": None, "numerateur": 0, "effectif": 0}}, "aucune requête",
     "au moins 10 requêtes"),
    ("cout_24h", {"cout_24h": {"valeur": 6.0, "devise": "EUR"}}, "6,00 € sur les 24 dernières heures",
     "problème à partir de 5,00 €"),
    ("cout_24h", {"cout_24h": {"valeur": None, "devise": "EUR"}}, "inconnu", "attention à partir de 1,00 €"),
    ("rejets_15_min", {"rejets_15_min": 150}, "150 sur les 15 dernières minutes", "problème à partir de 100"),
    ("fraicheur", {"fraicheur": {"pire": "rouge", "nb_valeurs": 3, "message": "", "en_retard": [
        {"ticker": "AIR.PA", "derniere_seance": None, "retard_jours_ouvres": None, "statut": "rouge"},
        {"ticker": "OR.PA", "derniere_seance": "2026-10-14", "retard_jours_ouvres": 6, "statut": "rouge"}]}},
     "AIR.PA (aucune cotation), OR.PA (6 jours ouvrés)", "problème à partir de 4 jours ouvrés de retard"),
    ("fraicheur", {}, "aucune valeur en retard", "attention à partir de 2"),
])
def test_chaque_signal_a_une_valeur_et_un_seuil_lisibles(signal, surcharges, valeur_attendue, seuil_attendu):
    verdict = _verdict(signal, **surcharges)
    assert valeur_attendue in vigie._valeur_lisible(signal, verdict)
    assert seuil_attendu in vigie._seuil_lisible(signal, verdict)


def test_le_mode_a_blanc_annonce_sans_agir(capsys):
    a_blanc = vigie.GitHubABlanc()
    a_blanc.commenter(9, "texte")
    a_blanc.fermer(9, "fin")
    assert a_blanc.commentaires(9) == [] and a_blanc.issues_ouvertes() == {}
    sortie = capsys.readouterr().out
    assert "[à blanc] commenterait l'issue 9" in sortie and "[à blanc] fermerait l'issue 9" in sortie


def test_l_appel_http_passe_les_entetes_et_un_delai(monkeypatch):
    appels = []
    monkeypatch.setattr(vigie.httpx, "get", lambda url, **options: appels.append((url, options)) or "réponse")
    assert vigie._http_get(f"{ADRESSE}/sante", {"X-API-Key": "k"}) == "réponse"
    vigie._http_get(f"{ADRESSE}/health", None)
    assert appels == [(f"{ADRESSE}/sante", {"headers": {"X-API-Key": "k"}, "timeout": 10.0}),
                      (f"{ADRESSE}/health", {"headers": {}, "timeout": 10.0})]
