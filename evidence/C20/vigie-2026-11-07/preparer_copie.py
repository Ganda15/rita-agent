"""Prepare une copie independante, de la version constatee en production."""
import io
import json
import os
import secrets
import subprocess
import tempfile
import zipfile
from pathlib import Path

OUT = Path(__file__).parent
REPO = Path(r"D:\KandaWork\RITA_PROJECT\rita-agent")
COMMIT = "6f428d61511019d7b6013fb007e290c133d48c2e"
IMAGE = "rita-api:c20-6f428d615110"
PROJECT = "rita-c20-20261107"


def main():
    runtime = Path(tempfile.mkdtemp(prefix="rita-c20-20261107-"))
    parts = ["docker-compose.yml", "db", "data/demo", "monitorage", "rag"]
    archive = subprocess.run(["git", "archive", "--format=zip", COMMIT, *parts],
                             cwd=REPO, capture_output=True, check=True).stdout
    with zipfile.ZipFile(io.BytesIO(archive)) as package:
        package.extractall(runtime)
    # L'essai de disponibilite ne fait aucun appel modele et n'utilise aucun secret cloud.
    values = {"AZURE_FOUNDRY_API_KEY": "", "AZURE_FOUNDRY_ENDPOINT": "",
              "AZURE_FOUNDRY_DEPLOYMENT": "", "ANTHROPIC_API_KEY": "", "OPENROUTER_API_KEY": "",
              "RITA_API_KEY": secrets.token_urlsafe(32),
              "RITA_CLE_EXERCICE": secrets.token_urlsafe(32),
              "POSTGRES_PASSWORD": secrets.token_hex(24),
              "POSTGRES_PASSWORD_API": secrets.token_hex(24),
              "LLM_ORDRE": "foundry", "LANGFUSE_TRACING_ENABLED": "false",
              "LANGFUSE_PUBLIC_KEY": "", "LANGFUSE_SECRET_KEY": ""}
    # La configuration privee reste dans Temp, separee du dossier de preuves partageable.
    for value in values.values():
        if "\n" in value or "\r" in value or "'" in value:
            raise RuntimeError("Format de configuration inattendu")
    (runtime / ".env").write_text("".join(f"{k}='{v}'\n" for k, v in values.items()), encoding="utf-8")
    values = None
    override = f"""services:
  postgres:
    container_name: rita-postgres-c20-20261107
  api:
    image: {IMAGE}
    container_name: rita-api-c20-20261107
    environment:
      RITA_CLE_EXERCICE: ${{RITA_CLE_EXERCICE}}
      LANGFUSE_TRACING_ENABLED: "false"
      LANGFUSE_PUBLIC_KEY: ""
      LANGFUSE_SECRET_KEY: ""
    ports: !override
      - "127.0.0.1:8011:8000"
  initialisation:
    image: {IMAGE}
  indexation:
    image: {IMAGE}
  collecte:
    image: {IMAGE}
    profiles: ["outils"]
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://rita:${{POSTGRES_PASSWORD}}@postgres:5432/rita
    command: ["python", "-m", "pipelines.ingest", "--etapes", "cotations", "--strict"]
    read_only: true
    tmpfs: ["/tmp"]
    security_opt: ["no-new-privileges:true"]
"""
    (runtime / "compose.c20.yml").write_text(override, encoding="utf-8")
    state = {"runtime": str(runtime), "project": PROJECT, "commit": COMMIT,
             "image": IMAGE, "url": "http://localhost:8011",
             "api_container": "rita-api-c20-20261107", "langfuse_enabled": False,
             "separate_database": True, "separate_keys": True, "cloud_credentials_copied": False,
             "scenario": "service_unavailable_then_recovered"}
    (OUT / "copie-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"setup_failed": True, "error_type": type(exc).__name__}))
        raise SystemExit(1)
