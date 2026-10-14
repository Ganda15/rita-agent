"""Tests des règles du script du serveur (sprint 2, tâche 7) : `deploy/deployer.py`, sans Docker ni réseau.

Deux familles :
- les calculs purs (analyse des ordres, créneau du matin, transitions d'état) ;
- les opérations sur fichiers (état, journal, marque d'opération, verrou), testées dans des dossiers temporaires.
Le verrou repose sur `fcntl`, qui n'existe que sous Linux : ses tests tournent dans la chaîne, pas sous Windows.
"""
import json
import os
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from deploy import deployer as d

PARIS = ZoneInfo("Europe/Paris")
EMPREINTE = "ghcr.io/ganda15/rita-api@sha256:" + "a" * 64


# --- Les ordres ----------------------------------------------------------------------------------------------------

def test_ordre_livrer_valide():
    assert d.analyser_ordre("livrer " + EMPREINTE) == d.Ordre("livrer", EMPREINTE)


def test_ordre_revenir_valide():
    assert d.analyser_ordre("revenir 12345") == d.Ordre("revenir", "12345")


def test_ordre_version_valide():
    assert d.analyser_ordre("version") == d.Ordre("version", None)


@pytest.mark.parametrize("texte", [
    "livrer sha256:abc",
    "livrer " + EMPREINTE + "; rm -rf /",
    "livrer ghcr.io/autre/image@sha256:" + "a" * 64,
    "livrer " + EMPREINTE.upper(),
    "revenir 12a",
    "revenir",
    "revenir " + "1" * 21,
    "",
    "VERSION",
    "version\n",
    "version ",
    " version",
    "livrer " + EMPREINTE + "\n",
])
def test_ordres_refuses(texte):
    with pytest.raises(d.OrdreRefuse):
        d.analyser_ordre(texte)


# --- Le créneau du matin -------------------------------------------------------------------------------------------

@pytest.mark.parametrize("jour", [14, 25])
@pytest.mark.parametrize("heure, minute, seconde, attendu", [
    (7, 59, 59, 0), (8, 0, 0, 3600), (8, 59, 59, 1), (9, 0, 0, 0),
])
def test_creneau_heure_de_paris(jour, heure, minute, seconde, attendu):
    maintenant = datetime(2026, 10, jour, heure, minute, seconde, tzinfo=PARIS)
    assert d.secondes_avant_ouverture(maintenant) == attendu


@pytest.mark.parametrize("jour, heure_utc, attendu", [
    (14, 6, 3600),   # 06:00 UTC = 08:00 à Paris en heure d'été (UTC+2)
    (25, 7, 3600),   # 07:00 UTC = 08:00 à Paris le jour du passage à l'heure d'hiver (UTC+1)
    (25, 6, 0),      # 06:00 UTC = 07:00 à Paris le 25/10 : hors créneau
])
def test_creneau_depuis_une_heure_utc(jour, heure_utc, attendu):
    maintenant = datetime(2026, 10, jour, heure_utc, 0, 0, tzinfo=timezone.utc)
    assert d.secondes_avant_ouverture(maintenant) == attendu


def test_creneau_refuse_une_heure_sans_fuseau():
    with pytest.raises(ValueError):
        d.secondes_avant_ouverture(datetime(2026, 10, 14, 8, 30))


def test_une_fraction_de_seconde_avant_9h_reste_dans_le_creneau():
    maintenant = datetime(2026, 10, 14, 8, 59, 59, 500000, tzinfo=PARIS)
    assert d.secondes_avant_ouverture(maintenant) == 1


@pytest.mark.parametrize("heure, minute, seconde, attendu", [
    (7, 29, 59, 0), (7, 30, 0, 5400), (8, 59, 59, 1), (9, 0, 0, 0),
])
def test_creneau_elargi_pour_github(heure, minute, seconde, attendu):
    maintenant = datetime(2026, 10, 14, heure, minute, seconde, tzinfo=PARIS)
    assert d.secondes_avant_livraison(maintenant) == attendu


# --- Les ports du serveur ------------------------------------------------------------------------------------------

# Relevé du serveur du 14/10 (tâche 10, `docker ps`) : les ports déjà publiés par d'autres conteneurs.
PORTS_PRIS_SUR_LE_SERVEUR = {8001: "rita-api-preprod (production RITA)", 8002: "glossary", 8100: "kaldera-partenaire"}


def test_le_pretest_vise_un_port_libre_du_serveur():
    # Un pré-test sur un port déjà pris échouerait au démarrage, à chaque livraison.
    assert d.PORT_PRETEST not in PORTS_PRIS_SUR_LE_SERVEUR, PORTS_PRIS_SUR_LE_SERVEUR.get(d.PORT_PRETEST)
    assert d.URL_PRETEST == f"http://127.0.0.1:{d.PORT_PRETEST}"
    assert d.PORT_PRODUCTION == 8001


# --- Les transitions d'état (calculs purs) -------------------------------------------------------------------------

A = d.Version("ghcr.io/ganda15/rita-api@sha256:" + "a" * 64, "/root/rita-deploy/configs/a", "complet")
B = d.Version("ghcr.io/ganda15/rita-api@sha256:" + "b" * 64, "/root/rita-deploy/configs/b", "complet")
C = d.Version("ghcr.io/ganda15/rita-api@sha256:" + "c" * 64, "/root/rita-deploy/configs/c", "complet")


def test_apres_livraison():
    assert d.apres_livraison(d.Etat(active=A, precedente=B), C) == d.Etat(active=C, precedente=A)


def test_premiere_livraison_sans_precedente():
    assert d.apres_livraison(d.Etat(), A) == d.Etat(active=A, precedente=None)


def test_apres_retour():
    assert d.apres_retour(d.Etat(active=C, precedente=A)) == d.Etat(active=A, precedente=None)


def test_retour_sans_precedente_leve():
    with pytest.raises(d.AucunePrecedente):
        d.apres_retour(d.Etat(active=A))


# --- L'état sur le disque ------------------------------------------------------------------------------------------

def test_etat_absent_rend_un_etat_vide(tmp_path):
    assert d.lire_etat(tmp_path / "etat.json") == d.Etat()


def test_etat_garde_image_config_et_profil(tmp_path):
    chemin = tmp_path / "etat.json"
    etat = d.Etat(active=C, precedente=A, observee=C.image, sante="sain")
    d.ecrire_etat(chemin, etat)
    assert d.lire_etat(chemin) == etat


def test_etat_sans_precedente_se_relit(tmp_path):
    # L'état d'après la première livraison : une active, pas de précédente (« null » dans le fichier).
    chemin = tmp_path / "etat.json"
    d.ecrire_etat(chemin, d.Etat(active=A))
    assert d.lire_etat(chemin) == d.Etat(active=A, precedente=None)


@pytest.mark.parametrize("contenu", [
    '{"active": {"image": "x", "config": "y"',          # JSON tronqué
    "",                                                  # fichier vide
    '["pas", "un", "objet"]',                            # mauvaise forme
    '{"active": {"image": "x"}}',                        # version incomplète
    '{"active": {"image": 1, "config": "y", "profil": "complet"}}',  # champs complets, mauvais type
    "{}",                                                            # objet vide : pas une première livraison
    '{"activee": null}',                                             # nom de champ faux
    '{"active": null, "precedente": null, "observee": 3, "sante": null}',        # observee pas du texte
    '{"active": null, "precedente": null, "observee": null, "sante": {"x": 1}}', # sante pas une valeur permise
    '{"active": null, "precedente": null, "observee": null, "sante": "bof"}',    # sante inconnue
    '{"active": null, "precedente": null, "observee": null, "sante": null, "x": 1}',  # champ en trop
    '{"active": {"image": "x"}, "precedente": null, "observee": null, "sante": null}',  # version incomplète
    '{"active": {"image": 1, "config": "y", "profil": "c"}, "precedente": null, "observee": null, "sante": null}',
])
def test_etat_illisible_leve_et_ne_passe_jamais_pour_une_premiere_livraison(tmp_path, contenu):
    chemin = tmp_path / "etat.json"
    chemin.write_text(contenu, encoding="utf-8")
    with pytest.raises(d.EtatIllisible):
        d.lire_etat(chemin)


def test_ecriture_atomique_ne_laisse_pas_de_fichier_temporaire(tmp_path):
    chemin = tmp_path / "etat.json"
    d.ecrire_etat(chemin, d.Etat(active=A))
    assert sorted(p.name for p in tmp_path.iterdir()) == ["etat.json"]


def test_un_remplacement_rate_laisse_l_ancien_etat_intact(tmp_path, monkeypatch):
    chemin = tmp_path / "etat.json"
    d.ecrire_etat(chemin, d.Etat(active=A, precedente=B))

    def remplacement_rate(source, cible):
        raise OSError("disque plein")

    monkeypatch.setattr(d.os, "replace", remplacement_rate)
    with pytest.raises(OSError):
        d.ecrire_etat(chemin, d.Etat(active=C, precedente=A))
    monkeypatch.undo()
    assert d.lire_etat(chemin) == d.Etat(active=A, precedente=B)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["etat.json"]


# --- La marque d'opération et le journal ---------------------------------------------------------------------------

def test_operation_deja_ouverte_leve(tmp_path):
    d.ouvrir_operation(tmp_path, d.Ordre("livrer", EMPREINTE))
    with pytest.raises(d.OperationInachevee):
        d.ouvrir_operation(tmp_path, d.Ordre("revenir", "1"))


def test_fermer_operation_efface_la_marque(tmp_path):
    d.ouvrir_operation(tmp_path, d.Ordre("livrer", EMPREINTE))
    d.fermer_operation(tmp_path)
    d.ouvrir_operation(tmp_path, d.Ordre("revenir", "1"))


def test_journal_ajoute_une_ligne_json(tmp_path):
    quand = datetime(2026, 10, 14, 10, 0, tzinfo=PARIS)
    d.journaliser(tmp_path, maintenant=quand, operation="livrer", resultat="livree")
    d.journaliser(tmp_path, maintenant=quand, operation="revenir", resultat="refuse")
    lignes = (tmp_path / "journal.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(l)["operation"] for l in lignes] == ["livrer", "revenir"]
    assert json.loads(lignes[0])["date"] == "2026-10-14T10:00:00+02:00"


def test_empreinte_du_script():
    attendu = __import__("hashlib").sha256(Path(d.__file__).read_bytes()).hexdigest()
    assert d.empreinte_du_script() == attendu


# --- Le verrou (Linux seulement) -----------------------------------------------------------------------------------

LINUX_SEULEMENT = pytest.mark.skipif(sys.platform == "win32", reason="fcntl n'existe que sous Linux : tourne dans la chaîne")

TENIR_LE_VERROU = textwrap.dedent("""
    import sys, time
    from pathlib import Path
    from deploy import deployer as d
    with d.prendre_verrou(Path(sys.argv[1]), attente_max=0):
        print("pris", flush=True)
        time.sleep(float(sys.argv[2]))
""")


@LINUX_SEULEMENT
def test_verrou_tenu_par_un_autre_processus_leve_apres_l_attente(tmp_path):
    verrou = tmp_path / "verrou"
    autre = subprocess.Popen([sys.executable, "-c", TENIR_LE_VERROU, str(verrou), "4"], stdout=subprocess.PIPE,
                             text=True, cwd=Path(d.__file__).resolve().parent.parent)
    try:
        assert autre.stdout.readline().strip() == "pris"
        with pytest.raises(d.VerrouOccupe):
            with d.prendre_verrou(verrou, attente_max=1):
                pass
    finally:
        autre.wait(timeout=10)
    with d.prendre_verrou(verrou, attente_max=1):
        pass


@LINUX_SEULEMENT
def test_le_verrou_est_libere_apres_une_exception(tmp_path):
    verrou = tmp_path / "verrou"
    with pytest.raises(RuntimeError):
        with d.prendre_verrou(verrou, attente_max=0):
            raise RuntimeError("panne au milieu d'une opération")
    resultat = subprocess.run([sys.executable, "-c", TENIR_LE_VERROU, str(verrou), "0"], capture_output=True,
                              text=True, cwd=Path(d.__file__).resolve().parent.parent, env=dict(os.environ))
    assert resultat.returncode == 0 and resultat.stdout.strip() == "pris", resultat.stderr
