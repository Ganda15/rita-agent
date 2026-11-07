"""Transfere la cle RITA active au secret de vigie, sans jamais l'afficher."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

REPO = "Ganda15/rita-agent"
BASE = "https://178-104-184-125.sslip.io"
SECRET = "RITA_API_KEY_VIGIE"
DEST = Path(__file__).with_name("verification-secret.json")


def metadata():
    result = subprocess.run(
        ["gh", "api", f"repos/{REPO}/actions/secrets/{SECRET}"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode:
        raise RuntimeError("Lecture des metadonnees GitHub impossible")
    value = json.loads(result.stdout)
    return {k: value.get(k) for k in ("name", "created_at", "updated_at")}


def main():
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "secret": SECRET, "repository": REPO,
              "secret_value_recorded": False,
              "before": metadata()}
    # Uniquement la cle de l'API RITA du conteneur de production documente.
    result = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=12",
         "-o", "StrictHostKeyChecking=yes", "root@178.104.184.125",
         "docker exec rita-api-preprod printenv RITA_API_KEY"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode:
        raise RuntimeError("Lecture ciblee de la cle active impossible")
    key = result.stdout.rstrip("\r\n")
    if not key or "\n" in key or "\r" in key:
        raise RuntimeError("Format de cle inattendu")
    result = None
    request = Request(BASE + "/sante", headers={"X-API-Key": key})
    try:
        with urlopen(request, timeout=30) as response:
            report["sante_http_status"] = response.status
            response.read()
    except HTTPError as exc:
        report["sante_http_status"] = exc.code
        DEST.write_text(json.dumps(report, indent=2), encoding="utf-8")
        raise RuntimeError("Cle active refusee : aucun secret modifie") from None
    if report["sante_http_status"] != 200:
        raise RuntimeError("Etat inattendu : aucun secret modifie")
    with urlopen(BASE + "/health", timeout=20) as response:
        health = json.load(response)
        report["health_http_status"] = response.status
        report["production_commit"] = health.get("commit")
    # Valeur transmise par stdin, jamais dans les arguments, un fichier ou les logs.
    update = subprocess.run(
        ["gh", "secret", "set", SECRET, "--repo", REPO],
        input=key, capture_output=True, text=True, timeout=45,
    )
    key = None
    if update.returncode:
        raise RuntimeError("Mise a jour GitHub refusee")
    report["after"] = metadata()
    report["updated"] = report["after"]["updated_at"] != report["before"]["updated_at"]
    report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    DEST.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))
    if not report["updated"]:
        raise RuntimeError("Horodatage non actualise : verification necessaire")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Aucun message generique d'une bibliotheque ne doit reveler les en-tetes.
        print(json.dumps({"operation_failed": True, "error_type": type(exc).__name__}))
        raise SystemExit(1)
