"""Sprint 5, étapes 6 et 7 : les commandes des exercices (plan du sprint 5, § 3, étapes 6 et 7).

`python -m monitorage.exercer panne|fin|appels|derive` : la panne se pose et se retire avec le nom et le motif ; les
appels de test envoient cinq questions du corpus de démonstration ; la dérive envoie H1 à H6 du jeu v3 deux fois, à
8 par minute, et vérifie qu'aucun jeton n'a été consommé (aucun appel au modèle attendu). Aucun test ne parle au
réseau ; aucune clé n'est jamais affichée.
"""
import pytest

from monitorage import exercer
from rag.controle_questions import charger_jeu
from tests.conftest import CLE_DE_TEST

ADRESSE = "http://localhost:8011"
CLE_EXERCICE = "cle-d-exercice-de-test-32-caracteres"


class _Reponse:
    def __init__(self, code, corps):
        self.status_code, self._corps = code, corps

    def json(self):
        return self._corps


class _Reseau:
    """`post` et `get` remplacés : chaque appel est gardé ; les réponses viennent d'une fonction."""

    def __init__(self, repondre_post=None, jetons=(0, 0)):
        self.posts, self.gets = [], []
        self._repondre_post = repondre_post or (lambda url, corps: _Reponse(200, {}))
        self._jetons = list(jetons)

    def post(self, url, entetes, corps):
        self.posts.append((url, entetes, corps))
        return self._repondre_post(url, corps)

    def get(self, url, entetes):
        self.gets.append((url, entetes))
        valeur = self._jetons.pop(0) if len(self._jetons) > 1 else self._jetons[0]
        return _Reponse(200, {"jetons_24h": {"entree": valeur, "sortie": 0}})


def test_panne_envoie_la_cle_d_exercice_le_nom_et_le_motif(capsys):
    reseau = _Reseau(lambda url, corps: _Reponse(200, {"nom": "Era", "fin_au_plus_tard": "2026-10-22T16:25:00+02:00"}))
    assert exercer.panne(ADRESSE, CLE_EXERCICE, "Era", "répétition atelier 5", 20, reseau.post) == 0
    [(url, entetes, corps)] = reseau.posts
    assert url == f"{ADRESSE}/exercice/panne" and entetes == {"X-Cle-Exercice": CLE_EXERCICE}
    assert corps == {"nom": "Era", "motif": "répétition atelier 5", "duree_min": 20}
    sortie = capsys.readouterr().out
    assert "16:25" in sortie and CLE_EXERCICE not in sortie


def test_une_panne_refusee_le_dit_avec_son_code(capsys):
    reseau = _Reseau(lambda url, corps: _Reponse(403, {"detail": "Clé d'exercice invalide ou absente"}))
    assert exercer.panne(ADRESSE, "mauvaise", "Era", "répétition", 20, reseau.post) == 1
    assert "HTTP 403" in capsys.readouterr().out


def test_fin_envoie_le_nom_et_le_motif():
    reseau = _Reseau(lambda url, corps: _Reponse(200, {"statut": "exercice terminé"}))
    assert exercer.fin(ADRESSE, CLE_EXERCICE, "Era", "fin de la répétition", reseau.post) == 0
    assert reseau.posts == [(f"{ADRESSE}/exercice/fin", {"X-Cle-Exercice": CLE_EXERCICE},
                             {"nom": "Era", "motif": "fin de la répétition"})]


def test_les_appels_de_test_envoient_cinq_questions_avec_la_cle_des_questions(capsys):
    reseau = _Reseau(lambda url, corps: _Reponse(503, {"statut": "erreur", "motif": "FOURNISSEUR_INDISPONIBLE"}))
    assert exercer.appels(ADRESSE, CLE_DE_TEST, reseau.post) == 0
    assert len(reseau.posts) == 5
    assert all(url == f"{ADRESSE}/question" and entetes == {"X-API-Key": CLE_DE_TEST}
               for url, entetes, _ in reseau.posts)
    assert [c["question"] for _, _, c in reseau.posts] == list(exercer.QUESTIONS_DE_TEST)
    sortie = capsys.readouterr().out
    assert "5/5 : HTTP 503" in sortie and CLE_DE_TEST not in sortie


def test_les_textes_de_la_derive_sont_h1_a_h6_du_jeu_v3():
    jeu = {q["id"]: q["question"] for q in charger_jeu()["questions"]}
    assert exercer.textes_derive() == [jeu[f"H{n}"] for n in range(1, 7)]


def test_la_derive_envoie_douze_appels_a_huit_par_minute_et_compte_les_jetons(capsys):
    refus = _Reponse(200, {"statut": "refus", "motif": "TENTATIVE_DETOURNEMENT"})
    reseau, attentes = _Reseau(lambda url, corps: refus, jetons=(1200, 1200)), []
    assert exercer.derive(ADRESSE, CLE_DE_TEST, reseau.post, reseau.get, attentes.append) == 0
    assert len(reseau.posts) == 12 and attentes == [7.5] * 11
    assert [c["question"] for _, _, c in reseau.posts] == exercer.textes_derive() * 2
    sortie = capsys.readouterr().out
    assert "12/12 : HTTP 200 refus TENTATIVE_DETOURNEMENT" in sortie
    assert "jetons ajoutés : 0" in sortie and CLE_DE_TEST not in sortie


def test_une_derive_qui_consomme_des_jetons_ou_n_est_pas_refusee_le_signale(capsys):
    reponse = _Reponse(200, {"statut": "reponse", "motif": "OK"})
    reseau = _Reseau(lambda url, corps: reponse, jetons=(1000, 4000))
    assert exercer.derive(ADRESSE, CLE_DE_TEST, reseau.post, reseau.get, lambda s: None) == 1
    sortie = capsys.readouterr().out
    assert "jetons ajoutés : 3000" in sortie and "attention" in sortie


@pytest.mark.parametrize("arguments, variable", [(["panne", "--nom", "Era", "--motif", "répétition"], "RITA_CLE_EXERCICE"),
                                                 (["derive"], "RITA_API_KEY")])
def test_sans_cle_la_commande_s_arrete_avec_le_code_2(monkeypatch, capsys, arguments, variable):
    monkeypatch.setenv(variable, "")
    assert exercer.main(arguments) == 2
    assert variable in capsys.readouterr().out


def test_la_commande_panne_lit_la_cle_et_appelle_le_reseau(monkeypatch):
    reseau = _Reseau(lambda url, corps: _Reponse(200, {"nom": "Era", "fin_au_plus_tard": "2026-10-22T16:25:00+02:00"}))
    monkeypatch.setattr(exercer, "_post", reseau.post)
    monkeypatch.setenv("RITA_CLE_EXERCICE", CLE_EXERCICE)
    assert exercer.main(["panne", "--nom", "Era", "--motif", "répétition", "--adresse", ADRESSE]) == 0
    assert reseau.posts[0][1] == {"X-Cle-Exercice": CLE_EXERCICE}


@pytest.mark.parametrize("sous_commande, attendu", [("appels", 5), ("derive", 12)])
def test_les_commandes_appels_et_derive_partent_de_main(monkeypatch, sous_commande, attendu):
    refus = _Reponse(200, {"statut": "refus", "motif": "TENTATIVE_DETOURNEMENT"})
    reseau = _Reseau(lambda url, corps: refus)
    monkeypatch.setattr(exercer, "_post", reseau.post)
    monkeypatch.setattr(exercer, "_get", reseau.get)
    monkeypatch.setattr(exercer.time, "sleep", lambda s: None)
    monkeypatch.setenv("RITA_API_KEY", CLE_DE_TEST)
    exercer.main([sous_commande, "--adresse", ADRESSE])
    assert len(reseau.posts) == attendu


def test_la_commande_fin_part_de_main(monkeypatch):
    reseau = _Reseau(lambda url, corps: _Reponse(200, {"statut": "exercice terminé"}))
    monkeypatch.setattr(exercer, "_post", reseau.post)
    monkeypatch.setenv("RITA_CLE_EXERCICE", CLE_EXERCICE)
    assert exercer.main(["fin", "--nom", "Era", "--motif", "fin", "--adresse", ADRESSE]) == 0


def test_les_appels_reseau_passent_les_entetes_et_un_delai(monkeypatch):
    appels = []
    monkeypatch.setattr(exercer.httpx, "post", lambda url, **o: appels.append(("post", url, o)) or "r")
    monkeypatch.setattr(exercer.httpx, "get", lambda url, **o: appels.append(("get", url, o)) or "r")
    exercer._post(f"{ADRESSE}/question", {"X-API-Key": "k"}, {"question": "q"})
    exercer._get(f"{ADRESSE}/sante", {"X-API-Key": "k"})
    assert appels == [("post", f"{ADRESSE}/question", {"headers": {"X-API-Key": "k"}, "json": {"question": "q"},
                                                       "timeout": 10.0}),
                      ("get", f"{ADRESSE}/sante", {"headers": {"X-API-Key": "k"}, "timeout": 10.0})]


class _Illisible:
    status_code = 502

    def json(self):
        raise ValueError("pas du JSON")


def test_une_fin_refusee_le_dit_avec_son_code(capsys):
    reseau = _Reseau(lambda url, corps: _Illisible())
    assert exercer.fin(ADRESSE, CLE_EXERCICE, "Era", "fin", reseau.post) == 1
    assert "HTTP 502" in capsys.readouterr().out


def test_une_reponse_illisible_ne_fait_pas_planter_les_appels(capsys):
    assert exercer.appels(ADRESSE, CLE_DE_TEST, _Reseau(lambda url, corps: _Illisible()).post) == 0
    assert "5/5 : HTTP 502" in capsys.readouterr().out


def test_sans_sante_lisible_la_derive_ne_peut_pas_conclure(capsys):
    # Les jetons ne peuvent pas être vérifiés : ce n'est pas une réussite (« inconnu » n'est jamais vert).
    refus = _Reponse(200, {"statut": "refus", "motif": "TENTATIVE_DETOURNEMENT"})

    def get_en_panne(url, entetes):
        raise ConnectionError("API arrêtée")

    assert exercer.derive(ADRESSE, CLE_DE_TEST, lambda u, e, c: refus, get_en_panne, lambda s: None) == 1
    sortie = capsys.readouterr().out
    assert "jetons ajoutés : inconnu" in sortie and "non vérifié" in sortie
