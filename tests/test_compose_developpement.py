"""Constat S8 de la revue OWASP du 03/10, partie poste (06/11/2026) : la base de développement n'écoute que la machine.

Pourquoi : `db/docker-compose.yml` publiait PostgreSQL sur toutes les interfaces (`5432:5432`), avec un mot de passe
écrit dans le fichier : sur un réseau partagé (Wi-Fi d'un lieu de formation), n'importe quelle machine voisine pouvait
s'y connecter. Liée à `127.0.0.1`, la base n'est joignable que depuis le poste ; le mot de passe de développement reste
un mot de passe local, sans portée au-delà de la machine. Même règle que la base jetable du 02/11 (mémoire du projet).
"""
import re
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parent.parent


def test_la_base_de_developpement_n_est_publiee_que_sur_la_machine():
    compose = yaml.safe_load((RACINE / "db" / "docker-compose.yml").read_text(encoding="utf-8"))
    ports = compose["services"]["postgres"]["ports"]
    assert ports and all(str(p).startswith("127.0.0.1:") for p in ports), ports


# Constat S8, partie serveur (06/11/2026) : plus de valeur de secours publique pour le mot de passe du propriétaire.
# Le serveur a sa propre ligne `POSTGRES_PASSWORD` (vérifié par Era le 06/11, `grep -c`, sans afficher la valeur) ; sans
# elle, Compose doit refuser de démarrer plutôt que de prendre `rita_preprod_local`, écrite dans le dépôt public de tous.
@pytest.mark.parametrize("fichier", ["docker-compose.yml", "docker-compose.sprint5.yml"])
def test_le_mot_de_passe_du_proprietaire_n_a_plus_de_valeur_de_secours(fichier):
    texte = (RACINE / fichier).read_text(encoding="utf-8")
    assert "rita_preprod_local" not in texte
    usages = re.findall(r"\$\{POSTGRES_PASSWORD(?![A-Z_])([^}]*)\}", texte)   # pas POSTGRES_PASSWORD_API
    assert usages and all(u.startswith(":?") for u in usages), usages
