"""Chronomètre les trois garde-fous sur les entrées hostiles du test ReDoS (S9, 07/11/2026).

Pourquoi ce script : la relecture d'un autre agent (07/11) a demandé de conserver les chronométrages qui soutiennent
« moins de 10 ms », et de décrire exactement la preuve d'avant la correction. Chaque appel (une entrée, un garde-fou)
tourne dans son propre sous-processus, arrêté à l'échéance : une expression régulière qui bloque est notée
« interrompu », elle ne bloque pas la mesure.

Usage, depuis la racine du dépôt :
    C:\\Python314\\python.exe -X utf8 evidence/C17/s9-2026-11-07/chronometrer_entrees_hostiles.py [--racine DOSSIER]

--racine : dossier dont on importe `guardrails/` (par défaut ce dépôt). Pour mesurer une version passée, on extrait
cette version dans un arbre de travail Git séparé et on le donne ici.
"""
import argparse
import datetime
import platform
import subprocess
import sys
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(DEPOT))
from tests.test_evals import ENTREES_HOSTILES  # noqa: E402  (les entrées du test, sans les recopier)

NOMS = ["password + 5000 espaces", "mot de passe + 5000 espaces + x", "clé + 3000 « a »", "clé + 3000 « a , »",
        "note de la rédaction + 5000 espaces + achat", "consignes de rédaction + 3000 « x »"]
APPELS = {
    "verifier_fuite": "from guardrails.sortie import verifier_fuite as f\nappel = lambda t: f(t)",
    "verifier_sortie": "from guardrails.sortie import verifier_sortie as f\nappel = lambda t: f(t)",
    "neutraliser": "from guardrails.injection import neutraliser as f\nappel = lambda t: f(t, 'eval')",
}
ENFANT = (
    "import sys, time\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "{import_}\n"
    "texte = sys.stdin.buffer.read().decode('utf-8')\n"
    "debut = time.perf_counter()\n"
    "appel(texte)\n"
    "print(time.perf_counter() - debut)\n"
)


def version(racine: Path) -> str:
    """Le commit de l'arbre mesuré, et s'il porte des modifications non commitées dans guardrails/."""
    # safe.directory passé pour cette commande seule : un arbre de travail extrait sous le dossier temporaire est refusé
    # par Git (« dubious ownership ») ; on ne modifie pas la configuration globale.
    git = ["git", "-c", f"safe.directory={racine.as_posix()}", "-C", str(racine)]
    tete = subprocess.run(git + ["rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    sale = subprocess.run(git + ["status", "--porcelain", "--", "guardrails"], capture_output=True, text=True)
    if tete.returncode or sale.returncode:
        return "version inconnue (git : " + (tete.stderr or sale.stderr).strip().splitlines()[0] + ")"
    etat = "avec modifications non commitées de guardrails/" if sale.stdout.strip() else "guardrails/ identique au commit"
    return f"{tete.stdout.strip()} ({etat})"


def mesurer(racine: Path, nom_appel: str, texte: str, echeance: float) -> str:
    code = ENFANT.format(import_=APPELS[nom_appel])
    try:
        fini = subprocess.run([sys.executable, "-c", code, str(racine)], input=texte.encode("utf-8"),
                              capture_output=True, timeout=echeance)
    except subprocess.TimeoutExpired:
        return f"interrompu après {echeance:.0f} s"
    if fini.returncode != 0:
        return "erreur : " + fini.stderr.decode("utf-8", "replace").strip().splitlines()[-1]
    return f"{float(fini.stdout.decode('ascii')) * 1000:.2f} ms"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--racine", type=Path, default=DEPOT)
    parser.add_argument("--echeance", type=float, default=20.0)
    args = parser.parse_args()
    racine = args.racine.resolve()
    print(f"Chronométrage des entrées hostiles, {datetime.datetime.now():%d/%m/%Y %H:%M}")
    print(f"Code mesuré : {version(racine)}")
    print(f"Python {platform.python_version()} sur {platform.system()} ; un sous-processus par appel, "
          f"échéance {args.echeance:.0f} s ; temps mesuré dans l'enfant, sans le démarrage de Python")
    print()
    print(f"{'entrée':45} {'verifier_fuite':>22} {'verifier_sortie':>22} {'neutraliser':>22}")
    for nom, texte in zip(NOMS, ENTREES_HOSTILES, strict=True):
        cases = [mesurer(racine, appel, texte, args.echeance) for appel in APPELS]
        print(f"{nom:45} " + " ".join(f"{c:>22}" for c in cases))


if __name__ == "__main__":
    main()
