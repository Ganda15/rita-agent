"""Sprint 2, tâche 3 : le contrôle des secrets dans la chaîne.

Trois garanties, testées sans lancer gitleaks :
- les règles par défaut de gitleaks sont gardées, et les seules exceptions visent les cinq fausses clés de test du
  dépôt, chacune écrite en entier (aucun motif large qui laisserait passer une vraie clé) ;
- `.gitleaksignore` ne contient que les deux secrets historiques RÉVOQUÉS de l'incident INC-008, jamais un faux
  positif ;
- le travail `secrets` lit tout l'historique, à une version fixée, valeurs masquées, et l'image est contrôlée.
"""
import re
import secrets
import string
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
LIVRAISON = (RACINE / ".github" / "workflows" / "livraison.yml")

FAUSSES_CLES = {
    "cle-de-test-integration-continue-32c",
    "cle-de-verification-au-demarrage-32c",
    "cle-de-test-smoke-ui-32-caracteres-x",
    "cle-de-reconstruction-ci-32-caracteres",
    "remplacer-par-une-cle-generee-de-32-octets",
}


def _exceptions() -> list[str]:
    config = tomllib.loads((RACINE / ".gitleaks.toml").read_text(encoding="utf-8"))
    assert config["extend"]["useDefault"] is True, "les règles par défaut de gitleaks doivent être gardées"
    return [motif for liste in config["allowlists"] for motif in liste["regexes"]]


def test_les_exceptions_ne_visent_que_les_cinq_fausses_cles():
    motifs = _exceptions()
    assert len(motifs) == len(FAUSSES_CLES)
    for motif in motifs:
        assert motif.startswith("^") and motif.endswith("$"), f"motif non ancré : {motif}"
        assert ".*" not in motif and ".+" not in motif, f"motif trop large : {motif}"
    for cle in FAUSSES_CLES:
        assert sum(bool(re.search(m, cle)) for m in motifs) == 1, f"{cle} doit être couverte par une seule exception"


def test_une_vraie_cle_ne_ressemble_a_aucune_exception():
    motifs = _exceptions()
    alphabet = string.ascii_letters + string.digits
    for _ in range(50):
        cle = "".join(secrets.choice(alphabet) for _ in range(32))
        assert not any(re.search(m, cle) for m in motifs)


def test_gitleaksignore_ne_contient_que_les_deux_secrets_revoques():
    lignes = (RACINE / ".gitleaksignore").read_text(encoding="utf-8").splitlines()
    commentaires = " ".join(l for l in lignes if l.startswith("#"))
    empreintes = [l for l in lignes if l.strip() and not l.startswith("#")]
    assert "INC-008" in commentaires and "révoqu" in commentaires.lower()
    assert len(empreintes) == 2
    for empreinte in empreintes:
        assert re.fullmatch(r"[0-9a-f]{40}:\.env\.example:generic-api-key:\d+", empreinte), empreinte


def test_le_travail_secrets_lit_tout_l_historique_a_une_version_fixee():
    texte = LIVRAISON.read_text(encoding="utf-8")
    assert re.search(r"^  secrets:$", texte, re.M), "le travail secrets doit exister dans livraison.yml"
    bloc = texte.split("\n  secrets:\n", 1)[1].split("\n  construire-et-publier:\n", 1)[0]
    assert "fetch-depth: 0" in bloc
    assert "zricethezav/gitleaks:v8.30.1" in bloc
    assert "--redact" in bloc and "--gitleaks-ignore-path" in bloc and "--config" in bloc
    assert "--branches --remotes --tags" in bloc
    assert "scripts/verifier_dockerfile.py Dockerfile" in bloc


def test_l_image_est_controlee_pour_le_fichier_env():
    assert "test -e /app/.env" in LIVRAISON.read_text(encoding="utf-8")
