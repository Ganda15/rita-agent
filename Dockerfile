# =============================================================================
# RITA — image de l'API
#
# Livrables : C13 (chaîne de livraison continue) · C15 (preuve de concept en
#             environnement de pré-production)
#
# Construire :  docker build -t rita-api .
# Lancer seule : docker run --rm -p 8000:8000 --env-file .env rita-api
# Pile complète : docker compose up -d      (voir docker-compose.yml)
# =============================================================================

# --- Étape 1 : construction --------------------------------------------------
# Deux étapes plutôt qu'une : les outils de compilation (gcc, en-têtes) sont
# nécessaires pour bâtir psycopg2, mais **inutiles pour l'exécuter**. Les laisser
# dans l'image finale, ce serait des centaines de mégaoctets transportés à chaque
# déploiement et une surface d'attaque de plus. Ils restent ici.
# Image de base tirée de la galerie publique d'Amazon, où Docker publie ses images officielles : même image que
# `python:3.13-slim` de Docker Hub (même empreinte le 09/10/2026), sans la limite des téléchargements anonymes
# qui a fait échouer trois constructions de suite ce soir-là (carte #85).
FROM public.ecr.aws/docker/library/python:3.13-slim AS constructeur

# Compilateur requis par psycopg2-binary sur certaines plateformes, et libpq pour
# les en-têtes PostgreSQL.
RUN apt-get update \
 && apt-get install --no-install-recommends -y gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Les dépendances sont copiées SEULES, avant le code. Docker met en cache chaque
# étape : tant que ce fichier ne change pas, la réinstallation est sautée. Copier
# le code d'abord annulerait le cache à la moindre modification d'une ligne Python.
COPY requirements-api.txt .

# `--prefix` installe dans un dossier isolé, recopié tel quel dans l'image finale.
RUN pip install --no-cache-dir --prefix=/installation -r requirements-api.txt


# --- Étape 2 : exécution -----------------------------------------------------
FROM public.ecr.aws/docker/library/python:3.13-slim AS execution

# `libpq5` seule — la bibliothèque cliente PostgreSQL à l'exécution, sans les
# en-têtes ni le compilateur de l'étape précédente.
RUN apt-get update \
 && apt-get install --no-install-recommends -y libpq5 \
 && rm -rf /var/lib/apt/lists/*

# ⚠️ Utilisateur NON privilégié. Par défaut un conteneur s'exécute en root : une
# faille dans l'application donnerait alors les pleins pouvoirs dans le conteneur.
# Créé avant la copie du code pour que les fichiers lui appartiennent directement.
RUN useradd --create-home --shell /usr/sbin/nologin --uid 10001 rita

COPY --from=constructeur /installation /usr/local

WORKDIR /app

# Le code applicatif. `.dockerignore` écarte .env, .git, les tests et les caches :
# ce qui n'entre pas dans l'image ne peut pas en fuir.
COPY --chown=rita:rita api/     ./api/
COPY --chown=rita:rita agents/  ./agents/
COPY --chown=rita:rita db/      ./db/
COPY --chown=rita:rita graph/   ./graph/
COPY --chown=rita:rita guardrails/ ./guardrails/
COPY --chown=rita:rita indicateurs/ ./indicateurs/
# 🔴 Oublié depuis le 25/08, jour de sa création : `api/donnees.py` importe
# `monitorage.fraicheur` en haut de fichier pour le bandeau de fraîcheur (C20).
COPY --chown=rita:rita monitorage/ ./monitorage/
COPY --chown=rita:rita pipelines/ ./pipelines/
# 🔴 Oublié jusqu'au 02/09/2026, alors que `graph/workflow.py` importe
# `rag.recherche` en haut de fichier depuis le 30/08 : l'image se construisait
# sans erreur puis s'arrêtait à l'import au démarrage. Un `COPY` manquant ne se
# voit pas à la construction — seulement à l'exécution.
COPY --chown=rita:rita rag/     ./rag/
COPY --chown=rita:rita sources/ ./sources/
COPY --chown=rita:rita src/     ./src/
COPY --chown=rita:rita frontend/ ./frontend/

# Revue Codex, PR #12 : un volume nommé hérite du propriétaire du dossier de l'image à sa
# première création. Sans ce `chown` AVANT `USER rita`, le point de montage `/app/data/chroma`
# appartient à root et ChromaDB (UID 10001) ne peut rien y écrire. Testé par
# tests/test_docker_compose.py.
RUN mkdir -p /app/data/chroma /home/rita/.cache && chown -R rita:rita /app/data /home/rita/.cache
USER rita

# Python n'écrit pas de .pyc et ne tamponne pas sa sortie : sans cela, les journaux
# d'un conteneur qui s'arrête brutalement seraient perdus dans le tampon.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

EXPOSE 8000

# `/health` est le seul point de terminaison non protégé — c'est précisément son
# rôle : vérifier que le service répond sans exposer la moindre donnée.
# `start-period` laisse le temps du démarrage sans compter d'échec.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import httpx,sys; sys.exit(0 if httpx.get('http://127.0.0.1:8000/health',timeout=4).status_code==200 else 1)"

# Pas de `--reload` : c'est un outil de développement. Il surveille le système de
# fichiers en permanence et redémarre le serveur — dans une image livrée, c'est du
# gaspillage et un risque.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
