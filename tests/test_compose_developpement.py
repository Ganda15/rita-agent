"""Constat S8 de la revue OWASP du 03/10, partie poste (06/11/2026) : la base de développement n'écoute que la machine.

Pourquoi : `db/docker-compose.yml` publiait PostgreSQL sur toutes les interfaces (`5432:5432`), avec un mot de passe
écrit dans le fichier : sur un réseau partagé (Wi-Fi d'un lieu de formation), n'importe quelle machine voisine pouvait
s'y connecter. Liée à `127.0.0.1`, la base n'est joignable que depuis le poste ; le mot de passe de développement reste
un mot de passe local, sans portée au-delà de la machine. Même règle que la base jetable du 02/11 (mémoire du projet).
"""
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent


def test_la_base_de_developpement_n_est_publiee_que_sur_la_machine():
    compose = yaml.safe_load((RACINE / "db" / "docker-compose.yml").read_text(encoding="utf-8"))
    ports = compose["services"]["postgres"]["ports"]
    assert ports and all(str(p).startswith("127.0.0.1:") for p in ports), ports
