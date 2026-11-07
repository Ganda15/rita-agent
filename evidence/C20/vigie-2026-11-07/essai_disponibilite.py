"""Essai reel du signal service sur copie, avec issues GitHub limitees a ce seul signal."""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import dotenv_values

OUT = Path(__file__).parent
STATE = json.loads((OUT / "copie-state.json").read_text())
RUNTIME = Path(STATE["runtime"])
sys.path.insert(0, str(RUNTIME))
from monitorage import vigie, seuils

BASE = STATE["url"]
CONTAINER = STATE["api_container"]
KEY = dotenv_values(RUNTIME / ".env")["RITA_API_KEY"]
TITLE = vigie.titre("service", BASE)
REPORT = {"scenario": "service_unavailable_then_recovered", "commit": STATE["commit"],
          "image": STATE["image"], "address": BASE, "events": [],
          "scope": "Signal service uniquement ; protection des autres incidents par adaptateur GitHub",
          "cloud_model_calls": 0, "production_mutated": False}


def record(event, **data):
    item = {"at_utc": datetime.now(timezone.utc).isoformat(), "event": event, **data}
    REPORT["events"].append(item)
    (OUT / "essai-service.json").write_text(json.dumps(REPORT, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(item, ensure_ascii=False), flush=True)


class GithubServiceOnly(vigie.GitHubCli):
    """Restriction du banc : aucune modification possible des autres incidents, dont #132."""
    def issues_ouvertes(self):
        return {title: number for title, number in super().issues_ouvertes().items() if title == TITLE}

    def ouvrir(self, title, body):
        assert title == TITLE, "Un autre signal est sorti du perimetre"
        body = ("**ESSAI C20.5 DU 07/11/2026 SUR COPIE LOCALE** : arret volontaire du conteneur local, "
                "aucune panne de production. Meme image que la production, commit `" + STATE["commit"] + "`.\n\n" + body)
        return super().ouvrir(title, body)

    def fermer(self, number, comment):
        assert self.issues_ouvertes().get(TITLE) == number, "Cloture hors perimetre refusee"
        return super().fermer(number, comment)

    def commenter(self, number, comment):
        assert self.issues_ouvertes().get(TITLE) == number, "Commentaire hors perimetre refuse"
        return super().commenter(number, comment)


def docker(action):
    assert CONTAINER == "rita-api-c20-20261107"
    r = subprocess.run(["docker", action, CONTAINER], capture_output=True, text=True, timeout=40)
    assert r.returncode == 0, "Operation sur la copie refusee"


def get(url, headers):
    assert url.startswith(BASE + "/"), "Adresse hors de la copie"
    started = time.monotonic()
    try:
        response = httpx.get(url, headers=headers or {}, timeout=10)
        record("http", path=url.removeprefix(BASE), status=response.status_code,
               duration_s=round(time.monotonic()-started, 3))
        return response
    except Exception as exc:
        record("http", path=url.removeprefix(BASE), status=None, error_type=type(exc).__name__,
               duration_s=round(time.monotonic()-started, 3))
        raise


def wait_health():
    for _ in range(30):
        try:
            r = httpx.get(BASE + "/health", timeout=3)
            if r.status_code == 200:
                assert r.json().get("commit") == STATE["commit"]
                return r.json()
        except (httpx.HTTPError, OSError):
            pass
        time.sleep(2)
    raise RuntimeError("La copie ne repond pas")


def main():
    assert BASE == "http://localhost:8011"
    github = GithubServiceOnly()
    assert not github.issues_ouvertes(), "Un incident service local existe deja"
    before = wait_health()
    sante = httpx.get(BASE + "/sante", headers={"X-API-Key": KEY}, timeout=10)
    assert sante.status_code == 200
    body = sante.json()
    assert not body.get("exercice")
    assert not any(v["etat"] == "probleme" for v in body["verdicts"].values())
    config = seuils.charger()
    assert config["signaux"]["service"]["essais"] == 2
    assert config["signaux"]["service"]["intervalle_s"] == 10
    record("baseline", health=before, service_threshold=config["signaux"]["service"])
    stopped = False
    try:
        docker("stop")
        stopped = True
        record("copy_stopped", container=CONTAINER)
        actions, code = vigie.passage(BASE, KEY, get, github, time.sleep, time.time, config)
        record("monitor_during_outage", actions=actions, exit_code=code)
        assert code == 1
        issues = github.issues_ouvertes()
        assert TITLE in issues
        number = issues[TITLE]
        REPORT["issue_number"] = number
        REPORT["issue_url"] = f"https://github.com/Ganda15/rita-agent/issues/{number}"
        record("alert_verified", issue_number=number, url=REPORT["issue_url"])
        docker("start")
        stopped = False
        health = wait_health()
        record("copy_recovered", health=health)
        actions, code = vigie.passage(BASE, KEY, get, github, time.sleep, time.time, config)
        record("monitor_after_recovery", actions=actions, exit_code=code)
        assert code == 0
        result = subprocess.run(["gh", "issue", "view", str(number), "--repo", "Ganda15/rita-agent",
                                 "--json", "number,title,state,createdAt,closedAt,url,comments"],
                                capture_output=True, text=True, encoding="utf-8", check=True)
        issue = json.loads(result.stdout)
        assert issue["state"] == "CLOSED"
        assert any(c["body"].startswith("Retour à la normale") for c in issue["comments"])
        (OUT / "issue-essai-service.json").write_text(json.dumps(issue, indent=2, ensure_ascii=False), encoding="utf-8")
        record("trial_complete", issue_state=issue["state"], issue_url=issue["url"])
    finally:
        if stopped:
            docker("start")
            record("copy_restarted_in_cleanup")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        record("trial_failed", error_type=type(exc).__name__)
        raise SystemExit(1)
