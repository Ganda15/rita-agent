#!/bin/sh
# Point d'entrée de la clé SSH dédiée (sprint 2, tâche 8). La ligne de authorized_keys du serveur commence par
# command="/root/rita-deploy/bin/deployer.sh" : quoi que demande l'appelant, seul ce script tourne, et la commande
# demandée n'arrive que dans SSH_ORIGINAL_COMMAND, que deployer.py lit et valide (trois ordres permis).
exec /usr/bin/python3 /root/rita-deploy/bin/deployer.py
