#!/bin/sh
# Carte #76 (06/11/2026) : sur une base NEUVE seulement (démonstration, copie du poste), pose le mot de passe du rôle
# rita_api créé par 02-roles.sql. Le mot de passe vient de POSTGRES_PASSWORD_API (fichier d'environnement de la machine)
# et passe par une variable psql : il n'est jamais collé dans le texte SQL. En production, la base existe déjà : cette
# étape se fait à la main (docs/PLAN-76-role-api.md, § 4).
set -eu
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -v mdp="$POSTGRES_PASSWORD_API" <<SQL
ALTER ROLE rita_api PASSWORD :'mdp';
SQL
