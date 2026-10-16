"""Tests des scénarios du script du serveur (sprint 2, tâche 8) : livrer et revenir, sans Docker ni réseau réels.

Docker et HTTP sont remplacés par des doublures : `FauxDocker` retient quelle image tourne en production et en
préproduction, `faux_http` répond selon le comportement prévu pour chaque image. Un test par ligne du tableau de la
spec (`docs/CHAINE-V1.md` § 5.3), plus les cas du périmètre de l'atelier (§ 11) : la première livraison n'a pas de
précédente, et son échec demande la restauration manuelle d'août.
"""
import http.server
import json
import os
import re
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from deploy import deployer as d

PARIS = ZoneInfo("Europe/Paris")
RACINE = Path(__file__).resolve().parent.parent
REF_A = "ghcr.io/ganda15/rita-api@sha256:" + "a" * 64
REF_B = "ghcr.io/ganda15/rita-api@sha256:" + "b" * 64
REF_C = "ghcr.io/ganda15/rita-api@sha256:" + "c" * 64
ENV = {"RITA_API_KEY": "cle-de-test-smoke-ui-32-caracteres-x", "RITA_DSN_LECTURE": "postgresql://lecture@base/rita",
       # Revue de la PR #100 : les questions n'appellent qu'Azure (D5) ; ses variables sont exigées par le script.
       "AZURE_FOUNDRY_ENDPOINT": "https://azure.exemple.test", "AZURE_FOUNDRY_API_KEY": "cle-azure-fictive"}
SAIN = {"health": True, "ecran": True, "briefing": "ok", "journal": True}


def _comportement(**ecarts):
    return {**SAIN, **ecarts}


class FauxDocker:
    def __init__(self, images, production=None, aout=True):
        self.images = images          # empreinte -> {"commit": ..., "health": ..., "ecran": ..., ...}
        self.production = production  # empreinte de l'image qui sert en production
        self.pretest = None
        self.aout = aout
        self.appels = []
        self.fichiers_compose = {"docker-compose.yml": "services: {}\n", "compose.prod.yml": "services: {}\n"}
        self.index_absents = set()    # volumes d'index qui n'existent pas (ou plus)
        self.index_supprimes = []
        # Sprint 3, tâche B3 : la collecte, le rejeu des questions et l'identité des index.
        self.index_production = None  # le volume d'index que l'API de production sert
        self.index_pretest = None
        self.collecte = "ok"          # « ok », « echec », ou « sans_manifeste » (code 0 sans rien écrire)
        self.rejeu = "ok"             # « ok », « echec » (rapport écrit puis code 1), ou « sans_rapport »
        self.alterer_identite = None  # fonction appliquée à l'identité que /health annonce en production

    @staticmethod
    def identite(nom):
        """L'identité d'un index, comme `identite.json` la donne : chaque construction a son identifiant."""
        return {"nb_articles": 40, "empreinte": f"emp-{nom}", "identifiant": f"id-{nom}"}

    def identite_annoncee(self):
        identite = self.identite(self.index_production)
        return self.alterer_identite(identite) if self.alterer_identite else identite

    def collecter(self, version, dsn_ingestion, dossier_rapports):
        self.appels.append(("collecter", version.image, dsn_ingestion))
        if self.collecte == "echec":
            raise subprocess.CalledProcessError(1, ["docker", "run"])
        if self.collecte == "ok":
            numero = sum(1 for appel in self.appels if appel[0] == "collecter")
            (dossier_rapports / f"manifeste-2026-10-16-1000{numero:02d}.json").write_text('{"etapes_ok": 1}',
                                                                                          encoding="utf-8")

    def rejouer_questions(self, version, dsn_lecture, dossier_rapports):
        self.appels.append(("rejeu", version.index, dsn_lecture))
        rapport = d.chemin_rapport_rejeu(dossier_rapports, version)
        if self.rejeu != "sans_rapport":
            rapport.write_text(json.dumps({"index": self.identite(version.index), "ecarts": []}), encoding="utf-8")
        if self.rejeu == "echec":
            raise subprocess.CalledProcessError(1, ["docker", "run"])
        return rapport

    def tirer(self, ref):
        self.appels.append(("tirer", ref))

    def image_existe(self, ref):
        return self.aout if ref == d.IMAGE_AOUT else True

    def commit_de_l_image(self, ref):
        return self.images.get(ref, {}).get("commit")

    def image_du_conteneur(self, nom):
        return self.production

    def extraire_config(self, ref, dossier):
        for nom, contenu in self.fichiers_compose.items():
            (dossier / nom).write_text(contenu, encoding="utf-8")
        self.appels.append(("extraire", ref))

    def index_existe(self, nom):
        return nom not in self.index_absents

    def supprimer_index(self, nom):
        self.index_supprimes.append(nom)
        self.index_absents.add(nom)

    def demarrer_pretest(self, version, dsn_lecture):
        self.pretest = version.image
        self.index_pretest = version.index
        self.appels.append(("pretest", version.image, dsn_lecture, version.index))

    def arreter_pretest(self):
        self.pretest = None
        self.appels.append(("arret_pretest",))

    def remplacer_production(self, version):
        self.appels.append(("remplacer", version))
        if version.index in self.index_absents:   # Compose refuse un volume externe absent, sans le créer
            raise subprocess.CalledProcessError(1, ["docker", "compose", "up"])
        self.production = version.image
        self.index_production = version.index

    def journal_du_conteneur(self, nom):
        image = self.pretest if nom == d.CONTENEUR_PRETEST else self.production
        if self.images.get(image, {}).get("journal"):
            return f"INFO briefing servi : request_id=rid-{image[-6:]} ticker='OR.PA' conforme_amf=True\n"
        return ""

    def remplacements(self):
        return [a[1] for a in self.appels if a[0] == "remplacer"]


def faux_http(docker):
    def requete(methode, url, entetes=None, delai=None, corps=None):
        image = docker.pretest if url.startswith(d.URL_PRETEST) else docker.production
        c = docker.images.get(image, {})
        chemin = url.split("127.0.0.1:")[1].split("/", 1)[1]
        if not c.get("health"):
            raise OSError("connexion refusée")
        if chemin == "health":
            # Sprint 3, tâche A1 : /health annonce l'identité de l'index servi. Une version d'avant le sprint 3
            # (comportement `index=False`) ne l'annonce pas, et n'a pas de route /question.
            sante = {"status": "ok", "commit": c["commit"]}
            if c.get("index", True):
                sante["index"] = (docker.identite(docker.index_pretest) if url.startswith(d.URL_PRETEST)
                                  else docker.identite_annoncee())
            return d.Reponse(200, {}, json.dumps(sante).encode())
        if chemin == "question":
            # Revue de la PR #100 : la question de contrôle. « ok » : réponse citée ; « panne » : Azure indisponible ;
            # « refus » et « sans_reference » : pas de réponse citée ; « absente » : la route n'existe pas.
            docker.appels.append(("question", image))
            if c.get("cle") and (entetes or {}).get("X-API-Key") != c["cle"]:
                return d.Reponse(403, {}, b"{}")
            corps = {"ok": (200, {"statut": "reponse", "motif": "OK", "references": [{"id": 2788}]}),
                     "panne": (503, {"statut": "erreur", "motif": "FOURNISSEUR_INDISPONIBLE"}),
                     "refus": (200, {"statut": "refus", "motif": "OUT_OF_CORPUS", "references": []}),
                     "sans_reference": (200, {"statut": "reponse", "motif": "OK", "references": []}),
                     "absente": (404, {"detail": "Not Found"})}[c.get("question", "ok")]
            return d.Reponse(corps[0], {}, json.dumps(corps[1]).encode())
        if chemin == "donnees/valeurs":
            return d.Reponse(403, {}, b"{}")
        if chemin == "briefing.html":
            return d.Reponse(200 if c.get("ecran") else 404, {}, b"")
        if chemin.startswith("briefing?") and c.get("cle") and (entetes or {}).get("X-API-Key") != c["cle"]:
            return d.Reponse(403, {}, b"{}")      # chaque version n'accepte que SA clé
        if chemin.startswith("briefing?"):
            corps = {"ok": {"briefing": "Texte du briefing.", "conforme_amf": True,
                            "articles_transmis": c.get("articles", 1)},
                     "vide": {"briefing": " ", "conforme_amf": True},
                     "refus": {"briefing": "Briefing retenu par le garde-fou.", "conforme_amf": False}}[c["briefing"]]
            return d.Reponse(200, {"x-request-id": f"rid-{image[-6:]}"}, json.dumps(corps).encode())
        return d.Reponse(404, {}, b"")
    return requete


def _horloge(*instants):
    suite = iter(instants)
    dernier = [instants[-1]]

    def maintenant():
        try:
            dernier[0] = next(suite)
        except StopIteration:
            pass
        return dernier[0]
    return maintenant


DIX_HEURES = _horloge(datetime(2026, 10, 14, 10, 0, tzinfo=PARIS))


@pytest.fixture
def serveur(tmp_path):
    (tmp_path / "sauvegardes" / "avant-chaine").mkdir(parents=True)
    # Sprint 3, tâche B3 : le dossier des manifestes et des rapports de rejeu, créé par Era (tâche B5), jamais par le
    # script (créé par root, il ne serait pas inscriptible par l'utilisateur de l'image).
    (tmp_path / "rapports").mkdir()
    # Les fichiers Compose installés par Era à côté du script (tâche 10) : ceux de l'image doivent leur être identiques.
    (tmp_path / "bin").mkdir()
    for nom in ("docker-compose.yml", "compose.prod.yml"):
        (tmp_path / "bin" / nom).write_text("services: {}\n", encoding="utf-8")
    env = tmp_path / "env-serveur"
    env.write_text("RITA_API_KEY=cle-de-test-smoke-ui-32-caracteres-x\nRITA_DSN_LECTURE=postgresql://lecture@base/rita\n"
                   "AZURE_FOUNDRY_ENDPOINT=https://azure.exemple.test\nAZURE_FOUNDRY_API_KEY=cle-azure-fictive\n",
                   encoding="utf-8")
    return tmp_path, env


def _version(ref, dossier, nom, cle=ENV["RITA_API_KEY"]):
    chemin = dossier / "configs" / nom
    chemin.mkdir(parents=True, exist_ok=True)
    (chemin / ".env").write_text(f"RITA_API_KEY={cle}\n", encoding="utf-8")   # le .env sauvegardé de la version
    return d.Version(ref, str(chemin), "complet", f"rita-index-{nom}")


def _livrer(ref, docker, dossier, env_source, maintenant=DIX_HEURES):
    return d.livrer(ref, docker, dossier, ENV, maintenant, http=faux_http(docker), dormir=lambda s: None,
                    source_env=env_source)


def _journal(dossier):
    return [json.loads(l) for l in (dossier / "journal.jsonl").read_text(encoding="utf-8").splitlines()]


# --- Les lignes du tableau § 5.3 -----------------------------------------------------------------------------------

def test_livraison_reussie_met_a_jour_active_et_precedente(serveur):
    dossier, env = serveur
    a, b = _version(REF_A, dossier, "a"), _version(REF_B, dossier, "b")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a, precedente=b))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")}, production=REF_A)
    assert _livrer(REF_C, docker, dossier, env) == 0
    etat = d.lire_etat(dossier / "etat.json")
    assert etat.active.image == REF_C and etat.precedente == a
    assert etat.observee == REF_C and etat.sante == "sain"
    assert Path(etat.active.config, ".env").read_text(encoding="utf-8") == env.read_text(encoding="utf-8")
    assert _journal(dossier)[-1]["resultat"] == "livree"
    assert not (dossier / "operation-en-cours.json").exists()


def test_pretest_rate_ne_touche_pas_la_production(serveur):
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc", briefing="vide")},
                        production=REF_A)
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert docker.remplacements() == [] and docker.production == REF_A
    assert ("arret_pretest",) in docker.appels
    assert d.lire_etat(dossier / "etat.json") == d.Etat(active=a)
    assert _journal(dossier)[-1]["resultat"] == "refusee au pre-test"


def test_bascule_ratee_restaure_l_active_du_debut(serveur):
    dossier, env = serveur
    a, b = _version(REF_A, dossier, "a"), _version(REF_B, dossier, "b")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a, precedente=b))
    # C passe le pré-test (qui ne demande pas l'écran) et échoue en production (écran absent).
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_B: _comportement(commit="bbb"),
                         REF_C: _comportement(commit="ccc", ecran=False)}, production=REF_A)
    assert _livrer(REF_C, docker, dossier, env) == 1
    remplacees = docker.remplacements()
    assert [v.image for v in remplacees] == [REF_C, REF_A]       # A revient, jamais B
    assert remplacees[1] == a                                    # avec sa configuration
    etat = d.lire_etat(dossier / "etat.json")
    assert (etat.active, etat.precedente, etat.observee, etat.sante) == (a, b, REF_A, "sain")
    assert "livraison refusee" in _journal(dossier)[-1]["resultat"]


def test_bascule_ratee_et_restauration_ratee(serveur):
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa", ecran=False),
                         REF_C: _comportement(commit="ccc", ecran=False)}, production=REF_A)
    assert _livrer(REF_C, docker, dossier, env) == 1
    etat = d.lire_etat(dossier / "etat.json")
    assert etat.active == a and etat.sante == "degrade"
    dernier = _journal(dossier)[-1]
    assert "restauration en echec" in dernier["resultat"]
    assert "cause externe possible (modele, base) ou configuration commune incorrecte" in dernier["message"]


def test_retour_manuel_reussi_vide_la_precedente(serveur):
    dossier, env = serveur
    a, c = _version(REF_A, dossier, "a"), _version(REF_C, dossier, "c")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=c, precedente=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")}, production=REF_C)
    assert d.revenir("4242", docker, dossier, ENV, DIX_HEURES, http=faux_http(docker), dormir=lambda s: None) == 0
    etat = d.lire_etat(dossier / "etat.json")
    assert (etat.active, etat.precedente, etat.observee) == (a, None, REF_A)
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "retour arriere" and dernier["passage"] == "4242"


def test_retour_manuel_rate_remet_l_active(serveur):
    dossier, env = serveur
    a, c = _version(REF_A, dossier, "a"), _version(REF_C, dossier, "c")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=c, precedente=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa", health=False), REF_C: _comportement(commit="ccc")},
                        production=REF_C)
    assert d.revenir("4243", docker, dossier, ENV, DIX_HEURES, http=faux_http(docker), dormir=lambda s: None) == 1
    assert [v.image for v in docker.remplacements()] == [REF_A, REF_C]
    etat = d.lire_etat(dossier / "etat.json")
    assert (etat.active, etat.precedente, etat.observee) == (c, a, REF_C)
    assert _journal(dossier)[-1]["resultat"] == "retour refuse"


def test_retour_sans_precedente_refuse(serveur):
    dossier, env = serveur
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=_version(REF_A, dossier, "a")))
    docker = FauxDocker({REF_A: _comportement(commit="aaa")}, production=REF_A)
    assert d.revenir("1", docker, dossier, ENV, DIX_HEURES, http=faux_http(docker), dormir=lambda s: None) == 1
    assert docker.remplacements() == []
    assert "aucune version precedente" in _journal(dossier)[-1]["resultat"]


# --- Le périmètre de l'atelier : la première livraison -------------------------------------------------------------

def test_premiere_livraison_reussie_n_a_pas_de_precedente(serveur):
    dossier, env = serveur
    docker = FauxDocker({REF_C: _comportement(commit="ccc")}, production="rita-api:local")
    assert _livrer(REF_C, docker, dossier, env) == 0
    etat = d.lire_etat(dossier / "etat.json")
    assert etat.active.image == REF_C and etat.precedente is None


def test_premiere_livraison_ratee_demande_la_restauration_manuelle_d_aout(serveur):
    dossier, env = serveur
    docker = FauxDocker({REF_C: _comportement(commit="ccc", ecran=False)}, production="rita-api:local")
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert [v.image for v in docker.remplacements()] == [REF_C]   # aucune tentative de restauration
    assert d.lire_etat(dossier / "etat.json").active is None
    assert "restauration manuelle d'aout requise" in _journal(dossier)[-1]["message"]


def test_premiere_livraison_exige_la_sauvegarde_d_aout(serveur):
    dossier, env = serveur
    (dossier / "sauvegardes" / "avant-chaine").rmdir()
    docker = FauxDocker({REF_C: _comportement(commit="ccc")})
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert docker.appels == []
    assert "sauvegarde d'aout absente" in _journal(dossier)[-1]["message"]


def test_premiere_livraison_exige_aussi_l_image_d_aout(serveur):
    dossier, env = serveur
    docker = FauxDocker({REF_C: _comportement(commit="ccc")}, aout=False)
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert docker.appels == []


# --- Les points de vigilance ---------------------------------------------------------------------------------------

def test_etat_illisible_arrete_sans_livrer(serveur):
    dossier, env = serveur
    (dossier / "etat.json").write_text("{}", encoding="utf-8")
    docker = FauxDocker({REF_C: _comportement(commit="ccc")})
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert docker.appels == []


def test_variable_manquante_refuse_sans_livrer(serveur):
    dossier, env = serveur
    docker = FauxDocker({REF_C: _comportement(commit="ccc")})
    code = d.livrer(REF_C, docker, dossier, {"RITA_API_KEY": "x" * 32}, DIX_HEURES, http=faux_http(docker),
                    dormir=lambda s: None, source_env=env)
    assert code == 1 and docker.appels == []
    assert "RITA_DSN_LECTURE" in _journal(dossier)[-1]["message"]


def test_creneau_atteint_pendant_le_pretest_annule_proprement(serveur):
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")}, production=REF_A)
    horloge = _horloge(datetime(2026, 10, 14, 7, 58, tzinfo=PARIS), datetime(2026, 10, 14, 7, 58, tzinfo=PARIS),
                       datetime(2026, 10, 14, 8, 1, tzinfo=PARIS))
    assert _livrer(REF_C, docker, dossier, env, maintenant=horloge) == d.CODE_CRENEAU
    assert docker.remplacements() == [] and docker.pretest is None
    assert not (dossier / "operation-en-cours.json").exists()
    assert d.lire_etat(dossier / "etat.json") == d.Etat(active=a)


def test_meme_image_config_changee_livraison_ratee_restaure_l_ancienne_config(serveur):
    dossier, env = serveur
    ancienne = _version(REF_C, dossier, "ancienne")
    (Path(ancienne.config) / ".env").write_text("ANCIENNE=1\n", encoding="utf-8")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=ancienne))
    env.write_text(env.read_text(encoding="utf-8") + "NOUVELLE=1\n", encoding="utf-8")
    comportements = {REF_C: _comportement(commit="ccc")}
    docker = FauxDocker(comportements, production=REF_C)
    # La nouvelle configuration casse l'écran en production : simulé en changeant le comportement à la bascule.
    remplacer = docker.remplacer_production

    def remplacer_et_casser(version):
        remplacer(version)
        comportements[REF_C] = _comportement(commit="ccc", ecran=version.config == ancienne.config)
    docker.remplacer_production = remplacer_et_casser
    assert _livrer(REF_C, docker, dossier, env) == 1
    remplacees = docker.remplacements()
    assert remplacees[0].config != ancienne.config and remplacees[1] == ancienne
    assert (Path(ancienne.config) / ".env").read_text(encoding="utf-8") == "ANCIENNE=1\n"


def test_preparer_version_ne_reecrit_jamais_un_dossier(serveur):
    dossier, env = serveur
    docker = FauxDocker({})
    instant = datetime(2026, 10, 14, 10, 0, tzinfo=PARIS)
    d.preparer_version(docker, REF_C, dossier, env, instant)
    with pytest.raises(FileExistsError):
        d.preparer_version(docker, REF_C, dossier, env, instant)


# --- Les contrôles -------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("ecarts, sante, echec", [
    ({}, "sain", None),
    ({"briefing": "vide"}, "degrade", "briefing"),
    ({"briefing": "refus"}, "degrade", "briefing"),
    ({"journal": False}, "degrade", "journal"),
    ({"articles": 0}, "degrade", "articles"),
    ({"articles": True}, "degrade", "articles"),      # en Python, True est un entier : il ne vaut pas « 1 article »
    ({"commit": "zzz"}, "degrade", "version"),
    ({"health": False}, "indisponible", "health"),
])
def test_controler_production(ecarts, sante, echec):
    comportement = {**_comportement(commit="ccc"), **ecarts}
    docker = FauxDocker({REF_C: comportement}, production=REF_C)
    controle = d.controler(d.URL_PRODUCTION, ENV["RITA_API_KEY"], "complet", "ccc",
                           lambda: docker.journal_du_conteneur(d.CONTENEUR), faux_http(docker))
    assert controle.sante == sante
    assert (echec in controle.echecs) if echec else controle.echecs == ()


def test_le_pretest_ne_demande_pas_l_ecran():
    docker = FauxDocker({REF_C: _comportement(commit="ccc", ecran=False)})
    docker.pretest = REF_C
    controle = d.controler(d.URL_PRETEST, ENV["RITA_API_KEY"], "pretest", "ccc",
                           lambda: docker.journal_du_conteneur(d.CONTENEUR_PRETEST), faux_http(docker))
    assert controle.sante == "sain"


# --- main : le parcours réellement utilisé par SSH -----------------------------------------------------------------

class FauxVerrou:
    def __init__(self):
        self.pris = []
        self.chemins = []

    def __call__(self, chemin, attente_max):
        self.pris.append(attente_max)
        self.chemins.append(chemin)
        return _ContexteVide()


class _ContexteVide:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _main(serveur, ordre, docker, maintenant=DIX_HEURES, verrou=None):
    dossier, env = serveur
    verrou = verrou or FauxVerrou()
    code = d.main(environ={"SSH_ORIGINAL_COMMAND": ordre}, docker=docker, dossier=dossier, maintenant=maintenant,
                  http=faux_http(docker), verrou=verrou, dormir=lambda s: None, source_env=env)
    return code, verrou


def test_main_creneau_refuse_avant_tout_verrou(serveur):
    docker = FauxDocker({REF_C: _comportement(commit="ccc")})
    code, verrou = _main(serveur, "livrer " + REF_C, docker,
                         maintenant=_horloge(datetime(2026, 10, 14, 8, 30, tzinfo=PARIS)))
    assert code == d.CODE_CRENEAU and verrou.pris == [] and docker.appels == []


def test_main_retour_manuel_ignore_le_creneau(serveur):
    dossier, _ = serveur
    a, c = _version(REF_A, dossier, "a"), _version(REF_C, dossier, "c")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=c, precedente=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")}, production=REF_C)
    code, verrou = _main(serveur, "revenir 77", docker, maintenant=_horloge(datetime(2026, 10, 14, 8, 30, tzinfo=PARIS)))
    assert code == 0 and verrou.pris == [d.ATTENTE_VERROU["revenir"]]


def test_main_livraison_prend_le_verrou_puis_livre(serveur):
    docker = FauxDocker({REF_C: _comportement(commit="ccc")}, production="rita-api:local")
    code, verrou = _main(serveur, "livrer " + REF_C, docker)
    assert code == 0 and verrou.pris == [d.ATTENTE_VERROU["livrer"]]


def test_main_operation_inachevee_bloque_la_livraison(serveur):
    dossier, _ = serveur
    d.ouvrir_operation(dossier, d.Ordre("livrer", REF_A))
    docker = FauxDocker({REF_C: _comportement(commit="ccc")}, production="rita-api:local")
    code, _ = _main(serveur, "livrer " + REF_C, docker)
    assert code == 1
    assert [a for a in docker.appels if a[0] != "image_du_conteneur"] == []
    assert "operation inachevee" in _journal(dossier)[-1]["resultat"]


def test_main_ordre_refuse_rend_2_sans_rien_lancer(serveur):
    docker = FauxDocker({})
    code, verrou = _main(serveur, "livrer " + REF_C + "; rm -rf /", docker)
    assert code == 2 and verrou.pris == [] and docker.appels == []


def test_main_version_affiche_l_empreinte(serveur, capsys):
    code, verrou = _main(serveur, "version", FauxDocker({}))
    assert code == 0 and verrou.pris == []
    assert capsys.readouterr().out.strip() == d.empreinte_du_script()


# --- La vraie classe Docker : les commandes construites ------------------------------------------------------------

# L'environnement que `docker compose config` donnerait au service api (forme vérifiée avec le vrai Compose le 14/10).
ENV_COMPOSE = {"RITA_API_KEY": "cle-compose-fictive", "LLM_ORDRE": "foundry,anthropic,openrouter",
               "AZURE_FOUNDRY_DEPLOYMENT": "gpt-5.4-dzs-eu", "ANTHROPIC_API_KEY": "",
               "DATABASE_URL": "postgresql://rita:ADMIN-FICTIF@postgres:5432/rita"}


# L'identité que le rejeu « réel » (sur l'Enregistreur) écrit dans son rapport, et que /health annonce dans `_pire_chemin`.
IDENTITE_ENREGISTREE = {"empreinte": "emp-reelle", "identifiant": "id-reel"}


class Enregistreur:
    """Remplace `subprocess.run` : note chaque commande, son environnement et son délai maximal."""

    def __init__(self, sorties=None, echec=None, environnement=None):
        self.commandes = []
        self.delais = []
        self.sorties = sorties or {}
        self.echec = echec
        self.environnement = ENV_COMPOSE if environnement is None else environnement

    def __call__(self, args, check=False, capture_output=False, text=False, env=None, timeout=None):
        self.commandes.append((list(args), env))
        self.delais.append((" ".join(map(str, args[:3])), timeout))
        if self.echec and self.echec in " ".join(map(str, args)) and check:
            raise subprocess.CalledProcessError(1, args)
        if args[:2] == ["docker", "cp"]:
            Path(args[-1]).write_text("services: {}\n", encoding="utf-8")
        # Sprint 3, tâche B3 : la collecte écrit son manifeste et le rejeu son rapport, dans le dossier monté sur
        # /app/logs (le chemin de l'hôte est tout ce qui précède « :/app/logs », lettre de lecteur Windows comprise).
        logs = next((str(a)[:-len(":/app/logs")] for a in args if str(a).endswith(":/app/logs")), None)
        if logs and "pipelines.ingest" in args:
            Path(logs, "manifeste-2026-10-16-100000.json").write_text("{}", encoding="utf-8")
        if logs and "rag.controle_questions" in args:
            Path(logs, Path(args[args.index("--sortie") + 1]).name).write_text(
                json.dumps({"index": IDENTITE_ENREGISTREE}), encoding="utf-8")
        if "config" in args and "--format" in args:
            sortie = json.dumps({"services": {"api": {"environment": self.environnement}}})
            return subprocess.CompletedProcess(args, 0, stdout=sortie, stderr="")
        cle = " ".join(map(str, args[:3]))
        return subprocess.CompletedProcess(args, 0, stdout=self.sorties.get(cle, ""), stderr="")


def test_bascule_ne_remplace_que_l_api(tmp_path):
    enregistreur = Enregistreur()
    version = d.Version(REF_C, str(tmp_path), "complet", "rita-index-essai")
    d.Docker(executer=enregistreur).remplacer_production(version)
    args, env = enregistreur.commandes[-1]
    assert isinstance(args, list) and args[:2] == ["docker", "compose"]
    assert "--no-deps" in args and "--no-build" in args and args[-1] == "api"
    assert args[args.index("--pull") + 1] == "never"
    assert args[args.index("-p") + 1] == d.PROJET_COMPOSE
    assert env["RITA_IMAGE"] == REF_C


def test_docker_lit_le_commit_de_l_image():
    enregistreur = Enregistreur({"docker image inspect": "PATH=/usr/bin\nRITA_GIT_SHA=abc1234\nX=1\n"})
    assert d.Docker(executer=enregistreur).commit_de_l_image(REF_C) == "abc1234"


def test_docker_image_absente():
    enregistreur = Enregistreur(echec="image inspect")
    assert d.Docker(executer=enregistreur).image_existe(d.IMAGE_AOUT) is False


def test_docker_extraire_config_supprime_le_conteneur_meme_en_cas_d_echec(tmp_path):
    enregistreur = Enregistreur(echec="compose.prod.yml")
    with pytest.raises(subprocess.CalledProcessError):
        d.Docker(executer=enregistreur).extraire_config(REF_C, tmp_path)
    assert enregistreur.commandes[-1][0][:3] == ["docker", "rm", "-f"]


DSN_SECRET = "postgresql://rita_lecture:MOTDEPASSE-FICTIF@postgres:5432/rita"


def test_docker_pretest_indexe_puis_demarre_en_lecture_seule(tmp_path):
    (tmp_path / ".env").write_text("RITA_API_KEY=k\n", encoding="utf-8")
    enregistreur = Enregistreur()
    d.Docker(executer=enregistreur).demarrer_pretest(
        d.Version(REF_C, str(tmp_path), "complet", "rita-index-essai"), DSN_SECRET)
    lancements = [(args, env) for args, env in enregistreur.commandes if args[:2] == ["docker", "run"]]
    indexation = next(c for c in lancements if "pipelines.ingest" in c[0])
    api = next(c for c in lancements if "-d" in c[0])
    for args, env in (indexation, api):
        # Le mot de passe ne passe jamais dans les arguments : ils se lisent dans `ps` et une erreur les recopie.
        assert not any("MOTDEPASSE-FICTIF" in a for a in args)
        assert args[args.index("-e") + 1] == "DATABASE_URL" and env["DATABASE_URL"] == DSN_SECRET
        assert "rita-index-essai:/app/data/chroma" in args     # l'index DE LA VERSION, gardé ensuite
    assert f"127.0.0.1:{d.PORT_PRETEST}:8000" in api[0] and d.CONTENEUR_PRETEST in api[0]


# --- Les chemins d'erreur (ajoutés après le code, pour les lignes que la couverture montrait non exercées) ---------

def test_controler_health_en_erreur_donne_indisponible():
    def http(methode, url, entetes=None, delai=None):
        return d.Reponse(500, {}, b"")
    assert d.controler(d.URL_PRODUCTION, "k", "complet", None, lambda: "", http).sante == "indisponible"


def test_controler_sans_403_et_connexion_perdue():
    appels = []

    def http(methode, url, entetes=None, delai=None):
        appels.append(url)
        if url.endswith("/health"):
            return d.Reponse(200, {}, b"pas du json")
        if url.endswith("/donnees/valeurs"):
            return d.Reponse(200, {}, b"[]")      # devrait être 403
        raise OSError("connexion perdue")
    controle = d.controler(d.URL_PRODUCTION, "k", "complet", "abc", lambda: "", http)
    assert controle.sante == "degrade"
    assert set(controle.echecs) == {"version", "403", "connexion"}


def test_revenir_refuse_sans_variable_ou_avec_un_etat_illisible(serveur):
    dossier, _ = serveur
    docker = FauxDocker({})
    assert d.revenir("1", docker, dossier, {"RITA_API_KEY": "x" * 32}, DIX_HEURES, http=faux_http(docker)) == 1
    (dossier / "etat.json").write_text("{}", encoding="utf-8")
    assert d.revenir("1", docker, dossier, ENV, DIX_HEURES, http=faux_http(docker)) == 1
    assert docker.appels == []


def test_main_verrou_occupe_rend_1(serveur):
    def verrou_occupe(chemin, attente_max):
        raise d.VerrouOccupe("tenu")
    docker = FauxDocker({})
    code, _ = _main(serveur, "revenir 1", docker, verrou=verrou_occupe)
    assert code == 1 and docker.appels == []


def test_docker_autres_commandes():
    enregistreur = Enregistreur({"docker inspect --format": "ghcr.io/ganda15/rita-api@sha256:abc\n",
                                 "docker image inspect": "PATH=/usr/bin\n"})
    docker = d.Docker(executer=enregistreur)
    docker.tirer(REF_C)
    assert docker.image_existe(REF_C) is True
    assert docker.commit_de_l_image(REF_C) is None             # image sans RITA_GIT_SHA
    assert docker.image_du_conteneur(d.CONTENEUR) == "ghcr.io/ganda15/rita-api@sha256:abc"
    docker.arreter_pretest()
    assert docker.journal_du_conteneur(d.CONTENEUR) == ""
    commandes = [args for args, _ in enregistreur.commandes]
    assert ["docker", "pull", REF_C] in commandes
    assert ["docker", "rm", "-f", d.CONTENEUR_PRETEST] in commandes
    assert ["docker", "logs", "--since", "15m", d.CONTENEUR] in commandes


def test_docker_conteneur_absent():
    docker = d.Docker(executer=Enregistreur(echec="docker inspect"))
    assert docker.image_du_conteneur(d.CONTENEUR) is None


# --- Les fichiers du serveur, la configuration embarquée, les vraies requêtes HTTP --------------------------------

def test_lire_env(tmp_path):
    chemin = tmp_path / ".env"
    chemin.write_text("# commentaire\n\nA=1\nB=\"deux\"\nC='trois'\nD=a=b\n", encoding="utf-8")
    assert d.lire_env(chemin) == {"A": "1", "B": "deux", "C": "trois", "D": "a=b"}


def test_l_image_embarque_ses_fichiers_compose():
    dockerfile = (RACINE / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY --chown=rita:rita docker-compose.yml deploy/compose.prod.yml ./deploy/" in dockerfile
    prod = (RACINE / "deploy" / "compose.prod.yml").read_text(encoding="utf-8")
    assert "${RITA_IMAGE:?" in prod and "pull_policy: never" in prod
    entree = (RACINE / "deploy" / "deployer.sh").read_text(encoding="utf-8")
    assert "exec /usr/bin/python3 /root/rita-deploy/bin/deployer.py" in entree
    livraison = (RACINE / ".github" / "workflows" / "livraison.yml").read_text(encoding="utf-8")
    assert "test -f /app/deploy/docker-compose.yml && test -f /app/deploy/compose.prod.yml" in livraison


def test_les_fichiers_du_serveur_sont_toujours_en_lf():
    # Sur le poste Windows (core.autocrlf=true), une copie en CRLF casserait `#!/bin/sh` et changerait l'empreinte
    # comparée par la chaîne (ordre `version`) : livraisons refusées. `.gitattributes` impose LF dans `deploy/`.
    # Relecture du 14/10 : docker-compose.yml aussi, car il est comparé octet par octet à la copie installée sur le
    # serveur ; une copie en CRLF depuis Windows différerait de celle de l'image (construite sous Linux, en LF).
    attributs = (RACINE / ".gitattributes").read_text(encoding="utf-8")
    assert "deploy/* text eol=lf" in attributs and "docker-compose.yml text eol=lf" in attributs
    for chemin in ("deploy/deployer.py", "deploy/deployer.sh", "deploy/compose.prod.yml", "docker-compose.yml"):
        assert b"\r" not in (RACINE / chemin).read_bytes(), f"{chemin} contient des CR"


def test_requete_reelle_sur_un_petit_serveur_local():
    class Gestionnaire(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200 if self.path == "/health" else 404)
            self.send_header("X-Request-ID", "rid-1")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')

        def do_POST(self):
            self.send_response(403)
            self.end_headers()

        def log_message(self, *args):
            pass

    serveur = http.server.HTTPServer(("127.0.0.1", 0), Gestionnaire)
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    base = f"http://127.0.0.1:{serveur.server_port}"
    try:
        ok = d.requete("GET", base + "/health")
        assert ok.statut == 200 and ok.entetes["x-request-id"] == "rid-1" and json.loads(ok.corps) == {"status": "ok"}
        assert d.requete("GET", base + "/absent").statut == 404
        assert d.requete("POST", base + "/briefing", {"X-API-Key": "x"}).statut == 403
    finally:
        serveur.shutdown()
    with pytest.raises(OSError):
        d.requete("GET", base + "/health", delai=2)


# --- Correctifs de sécurité (revue automatique du 14/10 sur le commit 6b473d0) -------------------------------------

@pytest.mark.parametrize("cas", ["different", "absent"])
def test_compose_de_l_image_different_de_celui_installe_refuse_la_livraison(serveur, cas):
    # Constat 1 : le serveur exécute les fichiers Compose en root. Une fusion dans `main` ne doit pas pouvoir changer,
    # seule, un réglage de la machine : seuls les fichiers installés par Era sont acceptés.
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")}, production=REF_A)
    if cas == "different":
        docker.fichiers_compose["compose.prod.yml"] = "services:\n  api:\n    privileged: true\n"
    else:
        (dossier / "bin" / "compose.prod.yml").unlink()
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert docker.remplacements() == [] and not any(appel[0] == "pretest" for appel in docker.appels)
    assert d.lire_etat(dossier / "etat.json") == d.Etat(active=a)
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "refusee" and "compose.prod.yml" in dernier["message"]
    assert not (dossier / "operation-en-cours.json").exists()


class DockerEnPanne(FauxDocker):
    def tirer(self, ref):
        raise subprocess.CalledProcessError(1, ["docker", "run", "-e", f"DATABASE_URL={DSN_SECRET}", ref],
                                            stderr=f"echec avec {DSN_SECRET}")


def test_une_commande_ratee_avant_la_bascule_refuse_sans_rien_afficher_de_secret(serveur, capsys):
    # Le message d'une CalledProcessError recopie toute la commande. Avant la bascule, la production n'a pas bougé :
    # la livraison est refusée proprement, l'état réel relu, l'opération fermée (relecture du 14/10).
    dossier, _ = serveur
    docker = DockerEnPanne({REF_C: _comportement(commit="ccc")}, production="rita-api:local")
    code, _ = _main(serveur, "livrer " + REF_C, docker)
    sortie = capsys.readouterr()
    assert code == 1
    assert "MOTDEPASSE-FICTIF" not in sortie.out + sortie.err + (dossier / "journal.jsonl").read_text(encoding="utf-8")
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "refusee" and dernier["message"] == "commande en echec : docker run (code 1)"
    assert dernier["observee"] == "rita-api:local"
    assert not (dossier / "operation-en-cours.json").exists()


class DockerTropLent(FauxDocker):
    def demarrer_pretest(self, version, dsn_lecture):
        self.appels.append(("pretest", version.image, dsn_lecture))
        raise subprocess.TimeoutExpired(["docker", "run", "-e", f"DATABASE_URL={DSN_SECRET}"], d.DELAI_INDEXATION)


def test_une_commande_trop_longue_avant_la_bascule_refuse_sans_toucher_la_production(serveur):
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = DockerTropLent({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")}, production=REF_A)
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert docker.remplacements() == [] and ("arret_pretest",) in docker.appels
    dernier = _journal(dossier)[-1]
    assert dernier["message"] == f"commande trop longue : docker run (plus de {d.DELAI_INDEXATION} s)"
    assert "MOTDEPASSE-FICTIF" not in json.dumps(dernier)
    assert d.lire_etat(dossier / "etat.json") == d.Etat(active=a)
    assert not (dossier / "operation-en-cours.json").exists()


class DockerEnPanneAuDepart(FauxDocker):
    def image_existe(self, ref):
        raise subprocess.TimeoutExpired(["docker", "image", "inspect", DSN_SECRET], d.DELAI_COURT)


def test_main_n_affiche_jamais_les_arguments_d_une_commande_en_dernier_recours(serveur, capsys):
    # Le dernier filet de `main` : une erreur Docker qui échapperait aux phases de `livrer` n'affiche que son nom.
    docker = DockerEnPanneAuDepart({REF_C: _comportement(commit="ccc")}, production="rita-api:local")
    code, _ = _main(serveur, "livrer " + REF_C, docker)
    sortie = capsys.readouterr()
    assert code == 1 and "MOTDEPASSE-FICTIF" not in sortie.out + sortie.err
    assert f"commande trop longue : docker image (plus de {d.DELAI_COURT} s)" in sortie.err


# --- Relecture du 14/10 : l'environnement du pré-test est celui de la production, calculé par Compose ---------------

def test_le_pretest_recoit_l_environnement_de_production_sans_la_base(tmp_path):
    # En production, l'API ne reçoit que le bloc `environment` de docker-compose.yml. Le pré-test reçoit le même,
    # calculé par Compose avec les mêmes fichiers, sauf DATABASE_URL (mot de passe administrateur) : une variable de
    # plus dans le .env n'arrive ni à la production, ni au pré-test.
    (tmp_path / ".env").write_text("RITA_API_KEY=k\nAUTRE_SECRET=ne-doit-pas-passer\n", encoding="utf-8")
    enregistreur = Enregistreur()
    d.Docker(executer=enregistreur).demarrer_pretest(
        d.Version(REF_C, str(tmp_path), "complet", "rita-index-essai"), DSN_SECRET)
    config, env_config = next((args, env) for args, env in enregistreur.commandes if "config" in args)
    assert config[:2] == ["docker", "compose"] and str(tmp_path / ".env") in config
    assert env_config["RITA_IMAGE"] == REF_C and env_config["RITA_INDEX"] == "rita-index-essai"
    assert (tmp_path / "pretest.env").read_text(encoding="utf-8") == (
        "ANTHROPIC_API_KEY=\nAZURE_FOUNDRY_DEPLOYMENT=gpt-5.4-dzs-eu\nLLM_ORDRE=foundry,anthropic,openrouter\n"
        "RITA_API_KEY=cle-compose-fictive\n")
    for args, _ in enregistreur.commandes:
        if args[:2] == ["docker", "run"]:
            assert args[args.index("--env-file") + 1] == str(tmp_path / "pretest.env")


def test_env_du_pretest_retire_la_base_et_garde_les_valeurs_vides():
    environnement = {"B": "2", "DATABASE_URL": "postgresql://rita:x@p/r", "POSTGRES_PASSWORD": "x", "A": "", "C": None}
    assert d.env_du_pretest(environnement) == "A=\nB=2\n"


@pytest.mark.parametrize("valeur", ["ligne-un\nligne-deux", "morceau-a\rmorceau-b"])
def test_env_du_pretest_refuse_une_valeur_sur_plusieurs_lignes(valeur):
    # `docker run --env-file` ne sait pas lire une valeur sur plusieurs lignes : refus, sans recopier la valeur.
    with pytest.raises(d.EnvIllisible) as erreur:
        d.env_du_pretest({"CLE_MULTI": valeur})
    assert "CLE_MULTI" in str(erreur.value) and "morceau" not in str(erreur.value) and "ligne-" not in str(erreur.value)


# --- Relecture du 14/10 : une bascule qui échoue ou dépasse son délai déclenche la récupération --------------------

class DockerBasculeRatee(FauxDocker):
    """`docker compose up` échoue (ou dépasse son délai) après avoir commencé le remplacement, pour certaines images."""

    def __init__(self, *args, rates, erreur, **kwargs):
        super().__init__(*args, **kwargs)
        self.rates, self.erreur = set(rates), erreur

    def remplacer_production(self, version):
        self.appels.append(("remplacer", version))
        if version.image in self.rates:
            self.production = None               # l'ancienne API est arrêtée, la nouvelle n'a pas démarré
            raise self.erreur
        self.production = version.image
        self.index_production = version.index


@pytest.mark.parametrize("erreur", [subprocess.CalledProcessError(1, ["docker", "compose", "up"]),
                                    subprocess.TimeoutExpired(["docker", "compose", "up"], 300)],
                         ids=["echec", "delai"])
def test_une_bascule_qui_echoue_remet_l_active_du_debut(serveur, erreur):
    dossier, env = serveur
    a, b = _version(REF_A, dossier, "a"), _version(REF_B, dossier, "b")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a, precedente=b))
    docker = DockerBasculeRatee({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")},
                                production=REF_A, rates=[REF_C], erreur=erreur)
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert [v.image for v in docker.remplacements()] == [REF_C, REF_A]
    etat = d.lire_etat(dossier / "etat.json")
    assert etat.active == a and etat.precedente == b and etat.observee == REF_A and etat.sante == "sain"
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "livraison refusee, version active du debut restauree"
    assert "bascule" in dernier["echecs"]
    assert not (dossier / "operation-en-cours.json").exists()


def test_une_bascule_qui_echoue_a_la_premiere_livraison_demande_la_restauration_manuelle(serveur):
    dossier, env = serveur
    docker = DockerBasculeRatee({REF_C: _comportement(commit="ccc")}, production="rita-api:avant-chaine",
                                rates=[REF_C], erreur=subprocess.CalledProcessError(1, ["docker", "compose", "up"]))
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert [v.image for v in docker.remplacements()] == [REF_C]
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "echec apres bascule" and "restauration manuelle" in dernier["message"]
    assert d.lire_etat(dossier / "etat.json").observee is None      # l'état réel relu : plus aucune API
    assert not (dossier / "operation-en-cours.json").exists()


def test_un_retour_dont_la_bascule_depasse_son_delai_remet_la_version_de_depart(serveur):
    dossier, _ = serveur
    a, c = _version(REF_A, dossier, "a"), _version(REF_C, dossier, "c")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=c, precedente=a))
    docker = DockerBasculeRatee({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")},
                                production=REF_C, rates=[REF_A],
                                erreur=subprocess.TimeoutExpired(["docker", "compose", "up"], 300))
    assert d.revenir("7", docker, dossier, ENV, DIX_HEURES, http=faux_http(docker), dormir=lambda s: None) == 1
    assert [v.image for v in docker.remplacements()] == [REF_A, REF_C]
    etat = d.lire_etat(dossier / "etat.json")
    assert etat.active == c and etat.observee == REF_C and etat.sante == "sain"
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "retour refuse" and "bascule" in dernier["echecs"]


def test_une_restauration_dont_la_bascule_echoue_aussi_est_journalisee(serveur):
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = DockerBasculeRatee({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")},
                                production=REF_A, rates=[REF_C, REF_A],
                                erreur=subprocess.CalledProcessError(1, ["docker", "compose", "up"]))
    assert _livrer(REF_C, docker, dossier, env) == 1
    etat = d.lire_etat(dossier / "etat.json")
    assert etat.active == a and etat.observee is None and etat.sante == "indisponible"
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "restauration en echec, intervention necessaire"
    assert dernier["echecs_restauration"] == ["bascule"]
    assert not (dossier / "operation-en-cours.json").exists()


# --- Relecture du 14/10 : chaque version est contrôlée avec SA clé sauvegardée --------------------------------------

CLE_A = "cle-fictive-de-l-ancienne-version-a-32"


def test_le_retour_controle_la_version_cible_avec_sa_propre_cle(serveur):
    # A, réinstallée avec son ancien .env, n'accepte que son ancienne clé. Contrôlée avec la clé actuelle, elle
    # répondait 403 et le retour était refusé à tort.
    dossier, _ = serveur
    a, c = _version(REF_A, dossier, "a", cle=CLE_A), _version(REF_C, dossier, "c")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=c, precedente=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa", cle=CLE_A),
                         REF_C: _comportement(commit="ccc", cle=ENV["RITA_API_KEY"])}, production=REF_C)
    assert d.revenir("7", docker, dossier, ENV, DIX_HEURES, http=faux_http(docker), dormir=lambda s: None) == 0
    assert d.lire_etat(dossier / "etat.json").active == a


def test_une_version_sans_env_sauvegarde_echoue_au_controle_au_lieu_de_planter(serveur):
    # Ajouté après le code (ligne que la couverture montrait non exercée) : sans .env sauvegardé, pas de clé ; le
    # contrôle du briefing échoue de façon visible et le retour est refusé, la version de départ remise.
    dossier, _ = serveur
    sans_env = dossier / "configs" / "a-sans-env"
    sans_env.mkdir(parents=True)
    a, c = d.Version(REF_A, str(sans_env), "complet", "rita-index-a"), _version(REF_C, dossier, "c")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=c, precedente=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa", cle=CLE_A), REF_C: _comportement(commit="ccc")},
                        production=REF_C)
    assert d.revenir("7", docker, dossier, ENV, DIX_HEURES, http=faux_http(docker), dormir=lambda s: None) == 1
    # Revue de la PR #100 : la version A de ce test annonce un index (comme toute version du sprint 3) ; sans clé, la
    # question de contrôle échoue aussi, après le briefing.
    assert _journal(dossier)[-1]["echecs"] == ["briefing", "question"]
    assert d.lire_etat(dossier / "etat.json").observee == REF_C


def test_le_retour_automatique_controle_l_active_avec_sa_propre_cle(serveur):
    dossier, env = serveur
    a = _version(REF_A, dossier, "a", cle=CLE_A)
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa", cle=CLE_A),
                         REF_C: _comportement(commit="ccc", ecran=False)}, production=REF_A)
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert _journal(dossier)[-1]["resultat"] == "livraison refusee, version active du debut restauree"


# --- Relecture du 14/10 : des délais partout, et une durée bornée tant que le verrou est tenu ----------------------

def test_toutes_les_commandes_docker_ont_un_delai_maximal(tmp_path):
    enregistreur = Enregistreur({"docker image inspect": "RITA_GIT_SHA=ccc\n"})
    docker = d.Docker(executer=enregistreur)
    (tmp_path / ".env").write_text("RITA_API_KEY=k\n", encoding="utf-8")
    docker.tirer(REF_C)
    docker.image_existe(REF_C)
    docker.commit_de_l_image(REF_C)
    docker.image_du_conteneur(d.CONTENEUR)
    docker.extraire_config(REF_C, tmp_path)
    version = d.Version(REF_C, str(tmp_path), "complet", "rita-index-essai")
    docker.demarrer_pretest(version, DSN_SECRET)
    docker.arreter_pretest()
    docker.remplacer_production(version)
    docker.index_existe(version.index)
    docker.supprimer_index(version.index)
    docker.journal_du_conteneur(d.CONTENEUR)
    docker.collecter(version, DSN_SECRET, tmp_path)               # sprint 3, tâche B3
    docker.rejouer_questions(version, DSN_SECRET, tmp_path)
    assert len(enregistreur.delais) >= 15
    permis = {d.DELAI_COURT, d.DELAI_TIRAGE, d.DELAI_INDEXATION, d.DELAI_BASCULE, d.DELAI_COLLECTE, d.DELAI_REJEU}
    assert all(delai in permis for _, delai in enregistreur.delais), enregistreur.delais
    assert ("docker pull " + REF_C, d.DELAI_TIRAGE) in enregistreur.delais
    assert ("docker run --rm", d.DELAI_INDEXATION) in enregistreur.delais
    assert ("docker compose -p", d.DELAI_BASCULE) in enregistreur.delais


def test_une_commande_de_nettoyage_trop_longue_n_interrompt_rien():
    def executer(args, check=False, capture_output=False, text=False, env=None, timeout=None):
        raise subprocess.TimeoutExpired(args, timeout)
    docker = d.Docker(executer=executer)
    docker.arreter_pretest()                                   # ne lève rien
    assert docker.image_du_conteneur(d.CONTENEUR) is None
    assert docker.image_existe(REF_C) is False
    assert docker.journal_du_conteneur(d.CONTENEUR) == ""


class FausseHorloge:
    def __init__(self):
        self.instant = 0.0

    def __call__(self):
        return self.instant

    def dormir(self, secondes):
        self.instant += secondes


def test_attendre_disponible_respecte_son_echeance():
    horloge = FausseHorloge()
    delais = []

    def http(methode, url, entetes=None, delai=None):
        delais.append(delai)
        horloge.instant += delai                 # chaque appel dure tout son délai, puis échoue
        raise OSError("pas encore")
    assert d.attendre_disponible(d.URL_PRODUCTION, http, horloge.dormir, horloge=horloge) is False
    assert horloge.instant <= d.DUREE_MAX_DISPONIBLE and set(delais) == {d.DELAI_SONDE}


def test_chaque_appel_d_un_controle_est_borne():
    delais = []

    def http(methode, url, entetes=None, delai=None):
        delais.append(delai)
        return d.Reponse(200, {}, b"{}")
    d.controler(d.URL_PRODUCTION, "k", "complet", None, lambda: "", http)
    assert len(delais) == 4 and None not in delais
    assert sum(delais) + d.DELAI_COURT <= d.DUREE_MAX_CONTROLE     # plus `docker logs`


def _pire_chemin(serveur, monkeypatch, briefing_rate):
    """La vraie classe Docker sur un Enregistreur : renvoie (enregistreur, délais HTTP, nombre d'attentes, http)."""
    dossier, _ = serveur
    enregistreur = Enregistreur({"docker image inspect": "RITA_GIT_SHA=ccc\n",
                                 "docker logs --since": "INFO request_id=rid\n"})
    attentes, delais_http, briefings = [], [], []
    monkeypatch.setattr(d, "attendre_disponible", lambda *args, **kwargs: attentes.append(1) or True)

    def http(methode, url, entetes=None, delai=None, corps=None):
        delais_http.append(delai)
        fin = url.rsplit("/", 1)[-1]
        if fin == "health":
            return d.Reponse(200, {}, json.dumps({"commit": "ccc", "index": IDENTITE_ENREGISTREE}).encode())
        if fin == "valeurs":
            return d.Reponse(403, {}, b"{}")
        if fin == "question":   # revue de la PR #100 : la question de contrôle, toujours citée ici
            return d.Reponse(200, {}, json.dumps({"statut": "reponse", "references": [{"id": 2788}]}).encode())
        if fin.startswith("briefing?"):
            briefings.append(url)
            statut = 500 if len(briefings) == briefing_rate else 200
            corps = json.dumps({"briefing": "Texte.", "conforme_amf": True, "articles_transmis": 2}).encode()
            return d.Reponse(statut, {"x-request-id": "rid"}, corps)
        return d.Reponse(200, {}, b"")
    return d.Docker(executer=enregistreur, depot=dossier), enregistreur, attentes, delais_http, http


def _duree(enregistreur, attentes, delais_http):
    return sum(delai for _, delai in enregistreur.delais) + sum(delais_http) + len(attentes) * d.DUREE_MAX_DISPONIBLE


def test_une_livraison_dure_toujours_moins_que_l_attente_du_retour_d_urgence(serveur, monkeypatch):
    # Sans délais, une livraison bloquée gardait le verrou et le retour d'urgence abandonnait au bout de 900 s.
    # Pire chemin : pré-test vert, nouvelle version en échec après la bascule (2e briefing), restauration de l'active.
    dossier, env = serveur
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=_version(REF_A, dossier, "a")))
    docker, enregistreur, attentes, delais_http, http = _pire_chemin(serveur, monkeypatch, briefing_rate=2)
    assert d.livrer(REF_C, docker, dossier, ENV, DIX_HEURES, http=http, dormir=lambda s: None, source_env=env) == 1
    assert _journal(dossier)[-1]["resultat"] == "livraison refusee, version active du debut restauree"
    assert _duree(enregistreur, attentes, delais_http) <= d.DUREE_MAX_LIVRER < d.ATTENTE_VERROU["revenir"]


def test_un_retour_dure_toujours_moins_que_l_attente_d_une_livraison(serveur, monkeypatch):
    # Pire chemin : la version cible échoue (1er briefing), la version de départ est remise et recontrôlée.
    dossier, _ = serveur
    a, c = _version(REF_A, dossier, "a"), _version(REF_C, dossier, "c")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=c, precedente=a))
    docker, enregistreur, attentes, delais_http, http = _pire_chemin(serveur, monkeypatch, briefing_rate=1)
    assert d.revenir("7", docker, dossier, ENV, DIX_HEURES, http=http, dormir=lambda s: None) == 1
    assert _duree(enregistreur, attentes, delais_http) <= d.DUREE_MAX_REVENIR < d.ATTENTE_VERROU["livrer"]


class DockerQuiCopieUnPiege(FauxDocker):
    """L'image contient, à la place de compose.prod.yml, un lien symbolique ou un dossier."""

    def __init__(self, *args, piege, **kwargs):
        super().__init__(*args, **kwargs)
        self.piege = piege

    def extraire_config(self, ref, dossier):
        (dossier / "docker-compose.yml").write_text("services: {}\n", encoding="utf-8")
        cible = dossier / "compose.prod.yml"
        if self.piege == "lien":
            # Le lien vise la copie installée : la comparaison passerait, puis la cible pourrait changer avant la bascule.
            os.symlink(dossier.parent.parent / "bin" / "compose.prod.yml", cible)
        else:
            cible.mkdir()
        self.appels.append(("extraire", ref))


@pytest.mark.parametrize("piege", ["lien", "dossier"])
def test_un_fichier_compose_qui_n_est_pas_un_fichier_ordinaire_est_refuse(serveur, piege):
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    if piege == "lien":
        try:
            os.symlink(dossier / "bin" / "compose.prod.yml", dossier / "essai-lien")
        except OSError:
            pytest.skip("liens symboliques non permis sur ce poste : le test tourne dans la chaîne (Linux)")
    docker = DockerQuiCopieUnPiege({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")},
                                   production=REF_A, piege=piege)
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert docker.remplacements() == [] and not any(appel[0] == "pretest" for appel in docker.appels)
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "refusee" and "compose.prod.yml" in dernier["message"]
    assert not (dossier / "operation-en-cours.json").exists()


# --- Choix A d'Era (14/10) : un index par livraison, vérifié avant la bascule, gardé pour le retour arrière ---------

def test_un_index_vide_est_refuse_au_pretest(serveur):
    # Un briefing est rédigé même sans article : seul le compte d'articles rend un index vide visible.
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc", articles=0)},
                        production=REF_A)
    assert _livrer(REF_C, docker, dossier, env) == 1
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "refusee au pre-test" and "articles" in dernier["echecs"]
    assert docker.remplacements() == []


def test_la_livraison_garde_l_index_verifie_pour_la_production(serveur):
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")}, production=REF_A)
    assert _livrer(REF_C, docker, dossier, env) == 0
    pretest = next(appel for appel in docker.appels if appel[0] == "pretest")
    active = d.lire_etat(dossier / "etat.json").active
    assert active.index == pretest[3] == docker.remplacements()[0].index     # testé, puis servi en production
    assert active.index.startswith("rita-index-") and docker.index_supprimes == []


def test_chaque_livraison_a_son_propre_index_meme_pour_la_meme_image(serveur):
    dossier, env = serveur
    docker = FauxDocker({})
    premiere = d.preparer_version(docker, REF_C, dossier, env, datetime(2026, 10, 14, 10, 0, tzinfo=PARIS))
    seconde = d.preparer_version(docker, REF_C, dossier, env, datetime(2026, 10, 14, 10, 0, 1, tzinfo=PARIS))
    assert premiere.index != seconde.index
    assert premiere.index == "rita-index-" + Path(premiere.config).name
    assert re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]+", premiere.index)     # un nom de volume Docker valide


def test_une_candidate_refusee_au_pretest_perd_son_index_et_l_active_garde_le_sien(serveur):
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc", briefing="vide")},
                        production=REF_A)
    assert _livrer(REF_C, docker, dossier, env) == 1
    candidate = next(appel for appel in docker.appels if appel[0] == "pretest")[3]
    assert docker.index_supprimes == [candidate] and a.index not in docker.index_supprimes
    assert d.lire_etat(dossier / "etat.json") == d.Etat(active=a)


def test_une_candidate_ratee_apres_bascule_perd_son_index_et_l_active_garde_le_sien(serveur):
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc", ecran=False)},
                        production=REF_A)
    assert _livrer(REF_C, docker, dossier, env) == 1
    remplacees = docker.remplacements()
    assert remplacees[1] == a                                   # l'active revient avec SON index
    assert docker.index_supprimes == [remplacees[0].index] and a.index not in docker.index_supprimes


def test_une_livraison_dont_l_active_n_a_plus_son_index_est_refusee(serveur):
    # Sans l'index de l'active, un retour automatique serait impossible : on ne bascule pas.
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")}, production=REF_A)
    docker.index_absents.add(a.index)
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert docker.appels == [] and _journal(dossier)[-1]["resultat"] == "refusee"
    assert a.index in _journal(dossier)[-1]["message"]
    assert not (dossier / "operation-en-cours.json").exists()


def test_le_retour_reprend_exactement_l_ancien_index(serveur):
    dossier, _ = serveur
    a, c = _version(REF_A, dossier, "a"), _version(REF_C, dossier, "c")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=c, precedente=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")}, production=REF_C)
    assert d.revenir("7", docker, dossier, ENV, DIX_HEURES, http=faux_http(docker), dormir=lambda s: None) == 0
    assert docker.remplacements() == [a] and docker.remplacements()[0].index == "rita-index-a"
    assert docker.index_supprimes == []


def test_un_retour_vers_une_version_sans_index_est_refuse_sans_rien_toucher(serveur):
    # Un volume manquant ne doit jamais être recréé vide : refus explicite, avant toute bascule.
    dossier, _ = serveur
    a, c = _version(REF_A, dossier, "a"), _version(REF_C, dossier, "c")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=c, precedente=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc")}, production=REF_C)
    docker.index_absents.add(a.index)
    assert d.revenir("7", docker, dossier, ENV, DIX_HEURES, http=faux_http(docker), dormir=lambda s: None) == 1
    assert docker.remplacements() == []
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "refuse" and a.index in dernier["message"]
    assert not (dossier / "operation-en-cours.json").exists()


def test_compose_prod_branche_l_api_sur_l_index_de_la_version_sans_jamais_le_creer():
    prod = (RACINE / "deploy" / "compose.prod.yml").read_text(encoding="utf-8")
    assert "rita_chroma_preprod:" in prod and "external: true" in prod
    assert "name: ${RITA_INDEX:?" in prod


def test_la_vraie_classe_docker_gere_les_index_par_leur_nom(tmp_path):
    enregistreur = Enregistreur(echec="volume inspect rita-index-absent")
    docker = d.Docker(executer=enregistreur)
    assert docker.index_existe("rita-index-present") is True
    assert docker.index_existe("rita-index-absent") is False
    docker.supprimer_index("rita-index-candidate")
    version = d.Version(REF_C, str(tmp_path), "complet", "rita-index-essai")
    docker.remplacer_production(version)
    docker.arreter_pretest()
    commandes = [args for args, _ in enregistreur.commandes]
    assert ["docker", "volume", "inspect", "rita-index-present"] in commandes
    assert ["docker", "volume", "rm", "rita-index-candidate"] in commandes
    assert enregistreur.commandes[-2][1]["RITA_INDEX"] == "rita-index-essai"      # la bascule
    assert commandes[-1] == ["docker", "rm", "-f", d.CONTENEUR_PRETEST]          # l'arrêt garde l'index


# === Sprint 3, tâche B3 : l'ordre `ingerer` et le rejeu des questions (décision D1, spec CA3.1 à CA3.6) =============
#
# Une ingestion garde l'image et la configuration de la version active. Elle collecte les articles, prépare un NOUVEL
# index à part (pré-test), rejoue les questions de démonstration sur cet index, puis seulement le met en service. Tout
# échec avant la bascule laisse l'index servi intact. Après la bascule, l'identité de l'index servi est vérifiée, et la
# version du début revient si elle ne correspond pas. La version précédente reste la cible d'un retour arrière.

ENV_INGESTION = {**ENV, "RITA_DSN_INGESTION": "postgresql://ingestion@base/rita"}


def _ingerer(docker, dossier, env=ENV_INGESTION, maintenant=DIX_HEURES):
    return d.ingerer("31", docker, dossier, env, maintenant, http=faux_http(docker), dormir=lambda s: None)


def _avec_active(dossier):
    """Une version active A (index « rita-index-a ») et une précédente P, comme après deux livraisons."""
    a, p = _version(REF_A, dossier, "a"), _version(REF_B, dossier, "p")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a, precedente=p))
    return a, p


def _docker_a():
    return FauxDocker({REF_A: _comportement(commit="aaa"), REF_B: _comportement(commit="bbb"),
                       REF_C: _comportement(commit="ccc")}, production=REF_A)


def _appel(docker, genre):
    return next(appel for appel in docker.appels if appel[0] == genre)


def test_ingestion_reussie_change_l_index_et_garde_le_retour_logiciel(serveur):
    dossier, _ = serveur
    a, p = _avec_active(dossier)
    docker = _docker_a()
    assert _ingerer(docker, dossier) == 0
    etat = d.lire_etat(dossier / "etat.json")
    nouvelle = etat.active
    assert (nouvelle.image, nouvelle.config, nouvelle.profil) == (a.image, a.config, a.profil)    # même logiciel
    assert nouvelle.index.startswith("rita-index-ing-") and nouvelle.index != a.index
    assert (etat.precedente, etat.observee, etat.sante) == (p, REF_A, "sain")
    # La collecte écrit avec le compte d'ingestion ; le pré-test et le rejeu portent sur l'index candidat.
    assert _appel(docker, "collecter") == ("collecter", REF_A, ENV_INGESTION["RITA_DSN_INGESTION"])
    assert _appel(docker, "pretest")[3] == nouvelle.index
    assert _appel(docker, "rejeu") == ("rejeu", nouvelle.index, ENV["RITA_DSN_LECTURE"])
    assert docker.remplacements() == [nouvelle]
    assert docker.index_supprimes == []                           # l'ancien index est gardé
    dernier = _journal(dossier)[-1]
    assert (dernier["resultat"], dernier["passage"]) == ("ingeree", "31")
    assert (dernier["ancien_index"], dernier["nouvel_index"]) == (a.index, nouvelle.index)
    assert dernier["empreinte"] == FauxDocker.identite(nouvelle.index)["empreinte"]
    assert Path(dernier["manifeste"]).is_file() and Path(dernier["rapport"]).is_file()
    assert not (dossier / "operation-en-cours.json").exists()


def test_echec_de_collecte_ne_touche_pas_l_index(serveur):
    dossier, _ = serveur
    a, p = _avec_active(dossier)
    docker = _docker_a()
    docker.collecte = "echec"
    assert _ingerer(docker, dossier) == 1
    assert docker.remplacements() == [] and not any(appel[0] == "pretest" for appel in docker.appels)
    assert d.lire_etat(dossier / "etat.json") == d.Etat(active=a, precedente=p)
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "echec collecte"
    assert "restent en base" in dernier["message"]        # CA3.3 : les écritures déjà validées ne sont pas cachées
    assert not (dossier / "operation-en-cours.json").exists()


def test_echec_du_rejeu_bloque_la_mise_en_service(serveur):
    dossier, _ = serveur
    a, p = _avec_active(dossier)
    docker = _docker_a()
    docker.rejeu = "echec"
    assert _ingerer(docker, dossier) == 1
    candidat = _appel(docker, "rejeu")[1]
    assert docker.remplacements() == [] and docker.index_supprimes == [candidat]
    assert d.lire_etat(dossier / "etat.json") == d.Etat(active=a, precedente=p)
    assert _journal(dossier)[-1]["resultat"] == "refusee au rejeu"
    assert not (dossier / "operation-en-cours.json").exists()


def test_pretest_rouge_bloque_l_ingestion(serveur):
    # Un index candidat vide : le briefing du pré-test ne reçoit aucun article.
    dossier, _ = serveur
    a, p = _avec_active(dossier)
    docker = FauxDocker({REF_A: _comportement(commit="aaa", articles=0)}, production=REF_A)
    assert _ingerer(docker, dossier) == 1
    candidat = _appel(docker, "pretest")[3]
    assert docker.remplacements() == [] and docker.index_supprimes == [candidat]
    assert not any(appel[0] == "rejeu" for appel in docker.appels)
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "refusee au pre-test" and "articles" in dernier["echecs"]
    assert d.lire_etat(dossier / "etat.json") == d.Etat(active=a, precedente=p)


@pytest.mark.parametrize("cas", ["sans_active", "etat_illisible", "index_actif_absent", "sans_dossier_des_rapports"])
def test_ingestion_sans_version_active_refusee(serveur, cas):
    # Les refus d'avant toute opération : rien n'est lancé, aucune marque n'est posée.
    dossier, _ = serveur
    docker = _docker_a()
    if cas == "sans_active":
        d.ecrire_etat(dossier / "etat.json", d.Etat())
    elif cas == "etat_illisible":
        (dossier / "etat.json").write_text("{}", encoding="utf-8")
    else:
        a, _ = _avec_active(dossier)
        if cas == "index_actif_absent":
            docker.index_absents.add(a.index)
        else:
            (dossier / "rapports").rmdir()
    assert _ingerer(docker, dossier) == 1
    assert docker.appels == []
    assert _journal(dossier)[-1]["resultat"] == "refusee"
    assert not (dossier / "operation-en-cours.json").exists()


def test_variable_d_ingestion_absente_refusee(serveur):
    dossier, _ = serveur
    _avec_active(dossier)
    docker = _docker_a()
    assert _ingerer(docker, dossier, env=ENV) == 1          # ENV n'a pas RITA_DSN_INGESTION
    assert docker.appels == []
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "refusee" and "RITA_DSN_INGESTION" in dernier["message"]


def test_ingestion_pendant_le_creneau_reportee(serveur):
    docker = _docker_a()
    code, verrou = _main(serveur, "ingerer 31", docker, maintenant=_horloge(datetime(2026, 10, 14, 8, 30, tzinfo=PARIS)))
    assert code == d.CODE_CRENEAU and verrou.pris == [] and docker.appels == []


def test_creneau_atteint_pendant_l_ingestion_annule_avant_la_bascule(serveur):
    # L'heure est relue juste avant la bascule : le créneau de 8 h, atteint pendant le rejeu, annule proprement.
    dossier, _ = serveur
    a, p = _avec_active(dossier)
    docker = _docker_a()

    def maintenant():
        rejoue = any(appel[0] == "rejeu" for appel in docker.appels)
        return datetime(2026, 10, 14, 8, 1, tzinfo=PARIS) if rejoue else datetime(2026, 10, 14, 7, 50, tzinfo=PARIS)
    assert _ingerer(docker, dossier, maintenant=maintenant) == d.CODE_CRENEAU
    assert docker.remplacements() == [] and docker.index_supprimes == [_appel(docker, "rejeu")[1]]
    assert d.lire_etat(dossier / "etat.json") == d.Etat(active=a, precedente=p)
    assert not (dossier / "operation-en-cours.json").exists()


def test_le_verrou_est_partage_avec_les_livraisons(serveur):
    dossier, env = serveur
    _avec_active(dossier)
    env.write_text(env.read_text(encoding="utf-8") + "RITA_DSN_INGESTION=postgresql://ingestion@base/rita\n",
                   encoding="utf-8")
    code, verrou_ingestion = _main(serveur, "ingerer 31", _docker_a())
    assert code == 0 and verrou_ingestion.pris == [d.ATTENTE_VERROU["ingerer"]]
    _, verrou_livraison = _main(serveur, "livrer " + REF_C, _docker_a())
    assert verrou_ingestion.chemins == verrou_livraison.chemins == [dossier / "verrou"]
    # Chaque opération attend plus longtemps que les deux autres ne peuvent durer : aucune n'abandonne en route.
    assert d.ATTENTE_VERROU["livrer"] > max(d.DUREE_MAX_REVENIR, d.DUREE_MAX_INGERER)
    assert d.ATTENTE_VERROU["revenir"] > max(d.DUREE_MAX_LIVRER, d.DUREE_MAX_INGERER)
    assert d.ATTENTE_VERROU["ingerer"] > max(d.DUREE_MAX_LIVRER, d.DUREE_MAX_REVENIR)


def test_un_retour_apres_ingestion_revient_a_la_version_precedente_avec_son_index(serveur):
    dossier, _ = serveur
    a, p = _avec_active(dossier)
    docker = _docker_a()
    assert _ingerer(docker, dossier) == 0
    reindexee = d.lire_etat(dossier / "etat.json").active
    assert d.revenir("32", docker, dossier, ENV, DIX_HEURES, http=faux_http(docker), dormir=lambda s: None) == 0
    assert docker.remplacements()[-1] == p                    # le logiciel précédent, avec SON index
    etat = d.lire_etat(dossier / "etat.json")
    assert (etat.active, etat.precedente) == (p, None)
    assert a.index not in docker.index_supprimes and reindexee.index not in docker.index_supprimes


def test_livraison_bloquee_si_le_rejeu_echoue(serveur):
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = _docker_a()
    docker.rejeu = "echec"
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert docker.remplacements() == [] and docker.index_supprimes == [_appel(docker, "rejeu")[1]]
    assert d.lire_etat(dossier / "etat.json") == d.Etat(active=a)
    assert _journal(dossier)[-1]["resultat"] == "refusee au rejeu"
    assert not (dossier / "operation-en-cours.json").exists()


def test_une_collecte_sans_manifeste_est_un_echec(serveur):
    # La commande rend 0, mais aucun manifeste n'a été écrit PENDANT l'opération : `ecrire_manifeste_sans_casser` ne
    # fait qu'avertir quand l'écriture échoue. Un manifeste plus ancien, déjà dans le dossier, ne compte pas.
    dossier, _ = serveur
    a, p = _avec_active(dossier)
    (dossier / "rapports" / "manifeste-2026-10-15-190000.json").write_text("{}", encoding="utf-8")
    docker = _docker_a()
    docker.collecte = "sans_manifeste"
    assert _ingerer(docker, dossier) == 1
    assert not any(appel[0] == "pretest" for appel in docker.appels)
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "echec collecte" and "preuve absente" in dernier["message"]
    assert d.lire_etat(dossier / "etat.json") == d.Etat(active=a, precedente=p)


@pytest.mark.parametrize("operation", ["ingerer", "livrer"])
def test_un_rejeu_sans_rapport_est_un_echec(serveur, operation):
    dossier, env = serveur
    _avec_active(dossier)
    docker = _docker_a()
    docker.rejeu = "sans_rapport"
    code = _ingerer(docker, dossier) if operation == "ingerer" else _livrer(REF_C, docker, dossier, env)
    assert code == 1 and docker.remplacements() == []
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "refusee au rejeu" and "preuve absente" in dernier["message"]


def test_le_rapport_d_un_rejeu_en_echec_est_garde(serveur):
    dossier, _ = serveur
    _avec_active(dossier)
    docker = _docker_a()
    docker.rejeu = "echec"
    assert _ingerer(docker, dossier) == 1
    rapport = Path(_journal(dossier)[-1]["rapport"])
    assert rapport.parent == dossier / "rapports" and rapport.is_file()
    assert json.loads(rapport.read_text(encoding="utf-8"))["index"]["identifiant"].startswith("id-rita-index-ing-")


@pytest.mark.parametrize("alteration", [
    lambda identite: {**identite, "empreinte": "emp-autre-corpus"},
    lambda identite: {**identite, "identifiant": "id-autre-construction"},   # même corpus, autre construction
    lambda identite: None,                                                   # /health sans identité d'index
], ids=["autre_empreinte", "meme_empreinte_autre_identifiant", "identite_absente"])
@pytest.mark.parametrize("operation", ["ingerer", "livrer"])
def test_la_bascule_verifie_l_identite_de_l_index(serveur, operation, alteration):
    # Pendant une ingestion, le commit ne change pas : il ne prouve pas que le nouvel index est servi. Deux index du
    # même corpus ont la même empreinte : elle seule ne suffit pas non plus. Il faut l'empreinte ET l'identifiant.
    dossier, env = serveur
    a, p = _avec_active(dossier)
    docker = _docker_a()
    docker.alterer_identite = alteration
    code = _ingerer(docker, dossier) if operation == "ingerer" else _livrer(REF_C, docker, dossier, env)
    assert code == 1
    remplacees = docker.remplacements()
    assert len(remplacees) == 2 and remplacees[1] == a              # la version du début revient, avec son index
    assert docker.index_supprimes == [remplacees[0].index]
    etat = d.lire_etat(dossier / "etat.json")
    assert (etat.active, etat.precedente, etat.sante) == (a, p, "sain")
    dernier = _journal(dossier)[-1]
    assert "index" in dernier["echecs"] and "restauree" in dernier["resultat"]
    assert not (dossier / "operation-en-cours.json").exists()


class DockerCollecteEnPanne(FauxDocker):
    def collecter(self, version, dsn_ingestion, dossier_rapports):
        self.appels.append(("collecter", version.image, dsn_ingestion))
        raise subprocess.CalledProcessError(1, ["docker", "run", "-e", f"DATABASE_URL={DSN_SECRET}"],
                                            stderr=f"echec avec {DSN_SECRET}")


def test_un_echec_de_collecte_n_ecrit_jamais_le_mot_de_passe(serveur, capsys):
    dossier, env = serveur
    _avec_active(dossier)
    env.write_text(env.read_text(encoding="utf-8") + f"RITA_DSN_INGESTION={DSN_SECRET}\n", encoding="utf-8")
    code, _ = _main(serveur, "ingerer 31", DockerCollecteEnPanne({REF_A: _comportement(commit="aaa")}, production=REF_A))
    sortie = capsys.readouterr()
    assert code == 1
    journal = (dossier / "journal.jsonl").read_text(encoding="utf-8")
    assert "MOTDEPASSE-FICTIF" not in sortie.out + sortie.err + journal
    assert _journal(dossier)[-1]["message"].startswith("commande en echec : docker run (code 1)")


# --- La vraie classe Docker : la collecte et le rejeu ---------------------------------------------------------------

def _seul_lancement(enregistreur):
    (lancement,) = [(args, env) for args, env in enregistreur.commandes if args[:2] == ["docker", "run"]]
    return lancement


def test_docker_collecte_avec_le_compte_d_ingestion_sans_mot_de_passe_dans_les_arguments(tmp_path):
    enregistreur = Enregistreur()
    version = d.Version(REF_C, str(tmp_path), "complet", "rita-index-essai")
    d.Docker(executer=enregistreur).collecter(version, DSN_SECRET, tmp_path)
    args, env = _seul_lancement(enregistreur)
    assert not any("MOTDEPASSE-FICTIF" in a for a in args)
    assert args[args.index("-e") + 1] == "DATABASE_URL" and env["DATABASE_URL"] == DSN_SECRET
    assert "--rm" in args and f"{tmp_path}:/app/logs" in args
    assert args[args.index("--network") + 1] == f"{d.PROJET_COMPOSE}_default"
    assert args[args.index(REF_C) + 1:] == ["python", "-m", "pipelines.ingest", "--etapes", "rss", "--strict"]
    assert not any(str(a).endswith(":/app/data/chroma") for a in args)      # la collecte ne touche aucun index
    assert enregistreur.delais[-1][1] == d.DELAI_COLLECTE


def test_docker_rejeu_lit_l_index_de_la_version_et_rend_le_chemin_du_rapport(tmp_path):
    enregistreur = Enregistreur()
    version = d.Version(REF_C, str(tmp_path), "complet", "rita-index-essai")
    rapport = d.Docker(executer=enregistreur).rejouer_questions(version, DSN_SECRET, tmp_path)
    args, env = _seul_lancement(enregistreur)
    assert rapport == tmp_path / "rejeu-rita-index-essai.json" == d.chemin_rapport_rejeu(tmp_path, version)
    assert "rita-index-essai:/app/data/chroma" in args and f"{tmp_path}:/app/logs" in args
    assert args[args.index("--sortie") + 1] == "/app/logs/rejeu-rita-index-essai.json"
    assert "rag.controle_questions" in args and "--rm" in args
    assert not any("MOTDEPASSE-FICTIF" in a for a in args) and env["DATABASE_URL"] == DSN_SECRET
    assert enregistreur.delais[-1][1] == d.DELAI_REJEU


def test_une_ingestion_dure_toujours_moins_que_l_attente_des_autres_operations(serveur, monkeypatch):
    # Pire chemin : collecte, pré-test et rejeu verts ; la version réindexée échoue après la bascule (2e briefing) ;
    # la version du début est remise et recontrôlée (3e briefing).
    dossier, _ = serveur
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=_version(REF_A, dossier, "a")))
    docker, enregistreur, attentes, delais_http, http = _pire_chemin(serveur, monkeypatch, briefing_rate=2)
    assert d.ingerer("9", docker, dossier, ENV_INGESTION, DIX_HEURES, http=http, dormir=lambda s: None) == 1
    assert _journal(dossier)[-1]["resultat"] == "ingestion refusee, version active du debut restauree"
    duree = _duree(enregistreur, attentes, delais_http)
    assert duree <= d.DUREE_MAX_INGERER < min(d.ATTENTE_VERROU["livrer"], d.ATTENTE_VERROU["revenir"])


# === Revue automatique de la PR #100 (16/10/2026) : contrôler /question à chaque livraison et ingestion ============
#
# Les questions n'appellent qu'Azure (décision D5), sans repli. `/briefing`, lui, se replie sur d'autres fournisseurs :
# ne contrôler que lui laissait passer une version dont chaque question rend 503 (clé Azure absente ou fausse). Les
# contrôles posent donc une vraie question couverte, et le script exige les variables d'Azure. Une version d'avant le
# sprint 3 (sans identité d'index, sans route /question) n'est pas soumise à ce contrôle : le retour arrière reste
# possible.

@pytest.mark.parametrize("question", ["panne", "refus", "sans_reference"])
def test_controler_exige_une_question_citee_quand_l_api_a_un_index(question):
    docker = FauxDocker({REF_C: _comportement(commit="ccc", question=question)}, production=REF_C)
    controle = d.controler(d.URL_PRODUCTION, ENV["RITA_API_KEY"], "complet", "ccc",
                           lambda: docker.journal_du_conteneur(d.CONTENEUR), faux_http(docker))
    assert controle.sante == "degrade" and "question" in controle.echecs


def test_controler_ne_pose_pas_la_question_a_une_version_sans_index():
    docker = FauxDocker({REF_A: _comportement(commit="aaa", index=False, question="absente")}, production=REF_A)
    controle = d.controler(d.URL_PRODUCTION, ENV["RITA_API_KEY"], "complet", "aaa",
                           lambda: docker.journal_du_conteneur(d.CONTENEUR), faux_http(docker))
    assert controle.sante == "sain" and not any(appel[0] == "question" for appel in docker.appels)


def test_une_livraison_dont_la_question_echoue_est_refusee_au_pretest(serveur):
    # Le cas de la revue : Azure mal configuré, briefing sauvé par un autre fournisseur. Rien ne bascule.
    dossier, env = serveur
    a = _version(REF_A, dossier, "a")
    d.ecrire_etat(dossier / "etat.json", d.Etat(active=a))
    docker = FauxDocker({REF_A: _comportement(commit="aaa"), REF_C: _comportement(commit="ccc", question="panne")},
                        production=REF_A)
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert docker.remplacements() == []
    dernier = _journal(dossier)[-1]
    assert dernier["resultat"] == "refusee au pre-test" and "question" in dernier["echecs"]


@pytest.mark.parametrize("operation", ["livrer", "ingerer"])
def test_les_variables_azure_sont_exigees(serveur, operation):
    dossier, env = serveur
    _avec_active(dossier)
    docker = _docker_a()
    sans_azure = {cle: valeur for cle, valeur in ENV_INGESTION.items() if cle != "AZURE_FOUNDRY_API_KEY"}
    if operation == "livrer":
        code = d.livrer(REF_C, docker, dossier, sans_azure, DIX_HEURES, http=faux_http(docker), dormir=lambda s: None,
                        source_env=env)
    else:
        code = d.ingerer("31", docker, dossier, sans_azure, DIX_HEURES, http=faux_http(docker), dormir=lambda s: None)
    assert code == 1 and docker.appels == []
    assert "AZURE_FOUNDRY_API_KEY" in _journal(dossier)[-1]["message"]


def test_la_question_de_controle_est_une_question_couverte_du_jeu():
    # La question posée à chaque contrôle est celle de Q4 dans le jeu validé par Era : son article (2788) est dans le
    # corpus de production, et un article n'en sort jamais.
    jeu = json.loads((RACINE / "rag" / "questions_demo.json").read_text(encoding="utf-8"))
    q4 = next(q for q in jeu["questions"] if q["id"] == "Q4")
    assert d.QUESTION_CONTROLE == q4["question"] and q4["attendu"] == "reponse"


def test_la_question_de_controle_est_bornee():
    delais, appels = [], []

    def http(methode, url, entetes=None, delai=None, corps=None):
        delais.append(delai)
        appels.append(url.rsplit("/", 1)[-1])
        if url.endswith("/question"):
            # La question envoyée est bien celle du jeu, en JSON.
            assert json.loads(corps) == {"question": d.QUESTION_CONTROLE}
        if url.endswith("/health"):
            return d.Reponse(200, {}, json.dumps({"commit": "c", "index": {"identifiant": "i"}}).encode())
        if url.endswith("/question"):
            return d.Reponse(200, {}, json.dumps({"statut": "reponse", "references": [{"id": 2788}]}).encode())
        return d.Reponse(200, {}, b"{}")
    d.controler(d.URL_PRODUCTION, "k", "complet", None, lambda: "", http)
    assert "question" in appels and None not in delais
    assert sum(delais) + d.DELAI_COURT <= d.DUREE_MAX_CONTROLE     # plus `docker logs`
