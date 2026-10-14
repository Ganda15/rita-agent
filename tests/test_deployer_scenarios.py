"""Tests des scénarios du script du serveur (sprint 2, tâche 8) : livrer et revenir, sans Docker ni réseau réels.

Docker et HTTP sont remplacés par des doublures : `FauxDocker` retient quelle image tourne en production et en
préproduction, `faux_http` répond selon le comportement prévu pour chaque image. Un test par ligne du tableau de la
spec (`docs/CHAINE-V1.md` § 5.3), plus les cas du périmètre de l'atelier (§ 11) : la première livraison n'a pas de
précédente, et son échec demande la restauration manuelle d'août.
"""
import http.server
import json
import os
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
ENV = {"RITA_API_KEY": "cle-de-test-smoke-ui-32-caracteres-x", "RITA_DSN_LECTURE": "postgresql://lecture@base/rita"}
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

    def demarrer_pretest(self, ref, config, dsn_lecture):
        self.pretest = ref
        self.appels.append(("pretest", ref, dsn_lecture))

    def arreter_pretest(self):
        self.pretest = None
        self.appels.append(("arret_pretest",))

    def remplacer_production(self, version):
        self.production = version.image
        self.appels.append(("remplacer", version))

    def journal_du_conteneur(self, nom):
        image = self.pretest if nom == d.CONTENEUR_PRETEST else self.production
        if self.images.get(image, {}).get("journal"):
            return f"INFO briefing servi : request_id=rid-{image[-6:]} ticker='OR.PA' conforme_amf=True\n"
        return ""

    def remplacements(self):
        return [a[1] for a in self.appels if a[0] == "remplacer"]


def faux_http(docker):
    def requete(methode, url, entetes=None):
        image = docker.pretest if url.startswith(d.URL_PRETEST) else docker.production
        c = docker.images.get(image, {})
        chemin = url.split("127.0.0.1:")[1].split("/", 1)[1]
        if not c.get("health"):
            raise OSError("connexion refusée")
        if chemin == "health":
            return d.Reponse(200, {}, json.dumps({"status": "ok", "commit": c["commit"]}).encode())
        if chemin == "donnees/valeurs":
            return d.Reponse(403, {}, b"{}")
        if chemin == "briefing.html":
            return d.Reponse(200 if c.get("ecran") else 404, {}, b"")
        if chemin.startswith("briefing?"):
            corps = {"ok": {"briefing": "Texte du briefing.", "conforme_amf": True},
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
    # Les fichiers Compose installés par Era à côté du script (tâche 10) : ceux de l'image doivent leur être identiques.
    (tmp_path / "bin").mkdir()
    for nom in ("docker-compose.yml", "compose.prod.yml"):
        (tmp_path / "bin" / nom).write_text("services: {}\n", encoding="utf-8")
    env = tmp_path / "env-serveur"
    env.write_text("RITA_API_KEY=cle-de-test-smoke-ui-32-caracteres-x\nRITA_DSN_LECTURE=postgresql://lecture@base/rita\n",
                   encoding="utf-8")
    return tmp_path, env


def _version(ref, dossier, nom):
    chemin = dossier / "configs" / nom
    chemin.mkdir(parents=True, exist_ok=True)
    return d.Version(ref, str(chemin), "complet")


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

    def __call__(self, chemin, attente_max):
        self.pris.append(attente_max)
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
    assert code == 0 and verrou.pris == [900]


def test_main_livraison_prend_le_verrou_puis_livre(serveur):
    docker = FauxDocker({REF_C: _comportement(commit="ccc")}, production="rita-api:local")
    code, verrou = _main(serveur, "livrer " + REF_C, docker)
    assert code == 0 and verrou.pris == [600]


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

class Enregistreur:
    def __init__(self, sorties=None, echec=None):
        self.commandes = []
        self.sorties = sorties or {}
        self.echec = echec

    def __call__(self, args, check=False, capture_output=False, text=False, env=None):
        self.commandes.append((list(args), env))
        cle = " ".join(map(str, args[:3]))
        if self.echec and self.echec in " ".join(map(str, args)) and check:
            raise subprocess.CalledProcessError(1, args)
        return subprocess.CompletedProcess(args, 0, stdout=self.sorties.get(cle, ""), stderr="")


def test_bascule_ne_remplace_que_l_api(tmp_path):
    enregistreur = Enregistreur()
    version = d.Version(REF_C, str(tmp_path), "complet")
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
    d.Docker(executer=enregistreur).demarrer_pretest(REF_C, tmp_path, DSN_SECRET)
    lancements = [(args, env) for args, env in enregistreur.commandes if args[:2] == ["docker", "run"]]
    indexation = next(c for c in lancements if "pipelines.ingest" in c[0])
    api = next(c for c in lancements if "-d" in c[0])
    for args, env in (indexation, api):
        # Le mot de passe ne passe jamais dans les arguments : ils se lisent dans `ps` et une erreur les recopie.
        assert not any("MOTDEPASSE-FICTIF" in a for a in args)
        assert args[args.index("-e") + 1] == "DATABASE_URL" and env["DATABASE_URL"] == DSN_SECRET
        assert f"{d.VOLUME_INDEX_PRETEST}:/app/data/chroma" in args
    assert f"127.0.0.1:{d.PORT_PRETEST}:8000" in api[0] and d.CONTENEUR_PRETEST in api[0]


# --- Les chemins d'erreur (ajoutés après le code, pour les lignes que la couverture montrait non exercées) ---------

def test_controler_health_en_erreur_donne_indisponible():
    def http(methode, url, entetes=None):
        return d.Reponse(500, {}, b"")
    assert d.controler(d.URL_PRODUCTION, "k", "complet", None, lambda: "", http).sante == "indisponible"


def test_controler_sans_403_et_connexion_perdue():
    appels = []

    def http(methode, url, entetes=None):
        appels.append(url)
        if url.endswith("/health"):
            return d.Reponse(200, {}, b"pas du json")
        if url.endswith("/donnees/valeurs"):
            return d.Reponse(200, {}, b"[]")      # devrait être 403
        raise OSError("connexion perdue")
    controle = d.controler(d.URL_PRODUCTION, "k", "complet", "abc", lambda: "", http)
    assert controle.sante == "degrade"
    assert set(controle.echecs) == {"version", "403", "connexion"}


def test_attendre_disponible_abandonne_apres_les_essais():
    pauses = []

    def http(methode, url, entetes=None):
        raise OSError("pas encore")
    assert d.attendre_disponible(d.URL_PRODUCTION, http, pauses.append, essais=3, pause=2) is False
    assert pauses == [2, 2, 2]


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
    assert "deploy/* text eol=lf" in (RACINE / ".gitattributes").read_text(encoding="utf-8")
    for nom in ("deployer.py", "deployer.sh", "compose.prod.yml"):
        assert b"\r" not in (RACINE / "deploy" / nom).read_bytes(), f"deploy/{nom} contient des CR"


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


def test_main_une_commande_docker_ratee_n_affiche_jamais_ses_arguments(serveur, capsys):
    # Constat 2 : le message d'une CalledProcessError recopie toute la commande ; il remonterait par SSH jusqu'au
    # journal de GitHub. `main` n'affiche que le nom de la commande et son code.
    dossier, _ = serveur
    docker = DockerEnPanne({REF_C: _comportement(commit="ccc")}, production="rita-api:local")
    code, _ = _main(serveur, "livrer " + REF_C, docker)
    sortie = capsys.readouterr()
    assert code == 1
    assert "MOTDEPASSE-FICTIF" not in sortie.out + sortie.err
    assert "MOTDEPASSE-FICTIF" not in (dossier / "journal.jsonl").read_text(encoding="utf-8")
    assert "docker run" in sortie.err and "code 1" in sortie.err
    assert (dossier / "operation-en-cours.json").exists()   # interrompue : l'opération suivante vérifiera l'état réel


def test_le_pretest_ne_recoit_pas_les_acces_en_ecriture_a_la_base(tmp_path):
    # Constat 3 : le pré-test ne reçoit pas tout le `.env` de production, seulement ce qui ne permet pas d'écrire
    # dans la base ; sa base, il la reçoit par `-e DATABASE_URL` (le compte rita_lecture).
    (tmp_path / ".env").write_text(
        "# production\nRITA_API_KEY=k\nDATABASE_URL=postgresql://rita:ADMIN-FICTIF@postgres/rita\n"
        "POSTGRES_PASSWORD=ADMIN-FICTIF\nMISTRAL_API_KEY=m\n", encoding="utf-8")
    enregistreur = Enregistreur()
    d.Docker(executer=enregistreur).demarrer_pretest(REF_C, tmp_path, DSN_SECRET)
    lancements = [args for args, _ in enregistreur.commandes if args[:2] == ["docker", "run"]]
    assert len(lancements) == 2
    for args in lancements:
        fichier = Path(args[args.index("--env-file") + 1])
        assert fichier != tmp_path / ".env"
        contenu = fichier.read_text(encoding="utf-8")
        assert "ADMIN-FICTIF" not in contenu
        assert "RITA_API_KEY=k" in contenu and "MISTRAL_API_KEY=m" in contenu


def test_env_du_pretest_retire_toute_variable_d_ecriture():
    texte = "A=1\nDATABASE_URL=x\n  POSTGRES_DB=rita\n# commentaire\nB=2\r\n"
    assert d.env_du_pretest(texte) == "A=1\nB=2\n"


# Seconde revue automatique (commit 6b5eb53) : le filtre doit lire le .env comme `docker run --env-file` le lit,
# sinon une variable qu'il croit retirée arrive quand même au pré-test.

def test_env_du_pretest_retire_le_bom_comme_docker():
    # Docker retire un BOM UTF-8 en tête de fichier ; sans le retirer aussi, « ﻿POSTGRES_PASSWORD » passait.
    assert d.env_du_pretest("﻿POSTGRES_PASSWORD=ADMIN-FICTIF\nA=1\n") == "A=1\n"


def test_env_du_pretest_ne_coupe_les_lignes_que_sur_le_saut_de_ligne():
    # Docker ne coupe que sur « \n » : un « \r » isolé reste dans la valeur.
    assert d.env_du_pretest("A=x\ry\nB=1\n") == "A=x\ry\nB=1\n"


@pytest.mark.parametrize("ligne", ["export POSTGRES_USER=rita", " DATABASE_URL =x", "A B=1", "=valeur"])
def test_env_du_pretest_refuse_une_ligne_au_nom_illisible(ligne):
    # Ne pas deviner ce que Docker ferait d'un nom inhabituel : le pré-test est refusé, sans recopier la ligne.
    with pytest.raises(d.EnvIllisible) as erreur:
        d.env_du_pretest("A=1\n" + ligne + "\n")
    assert "ligne 2" in str(erreur.value) and "rita" not in str(erreur.value) and "valeur" not in str(erreur.value)


def test_le_pretest_lit_le_env_sans_transformer_les_fins_de_ligne(tmp_path):
    (tmp_path / ".env").write_bytes(b"A=x\ry\nB=1\n")
    d.Docker(executer=Enregistreur()).demarrer_pretest(REF_C, tmp_path, DSN_SECRET)
    assert (tmp_path / "pretest.env").read_bytes() == b"A=x\ry\nB=1\n"


def test_livrer_refuse_un_env_illisible_avant_toute_operation(serveur):
    dossier, env = serveur
    env.write_text(env.read_text(encoding="utf-8") + "export POSTGRES_USER=rita\n", encoding="utf-8")
    docker = FauxDocker({REF_C: _comportement(commit="ccc")}, production="rita-api:local")
    assert _livrer(REF_C, docker, dossier, env) == 1
    assert docker.appels == []
    assert _journal(dossier)[-1]["resultat"] == "refusee"
    assert not (dossier / "operation-en-cours.json").exists()


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
