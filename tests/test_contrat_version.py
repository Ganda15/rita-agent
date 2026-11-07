"""La version déclarée du contrat suit les routes (OWASP API9:2023, inventaire ; rapport E3, § 3.5).

Le contrat disait `1.1.0` depuis le 1er août 2026, alors que `/question`, `/sante`, `/exercice/*` et `/audit/mcp` ont
été ajoutées depuis. Une version qui ne bouge pas quand les routes changent ne renseigne plus un client sur ce qu'il
peut appeler. Règle suivie, celle de la gestion sémantique des versions : une route ajoutée sans rien retirer fait
monter le chiffre du milieu. Le test de l'inventaire échoue si une route apparaît sans être décrite dans le contrat.
"""
from api.main import DESCRIPTION, app


def test_la_version_declaree_compte_les_routes_ajoutees_depuis_le_1er_aout():
    assert app.openapi()["info"]["version"] == "1.2.0"


def test_le_contrat_dit_ce_que_chaque_version_a_ajoute():
    assert "### Versions du contrat" in DESCRIPTION
    section = DESCRIPTION.split("### Versions du contrat", 1)[1]
    for marque in ("1.1.0", "1.2.0", "`/question`", "`/sante`", "`/exercice/*`", "`/audit/mcp`"):
        assert marque in section, marque


def test_chaque_route_du_contrat_a_sa_famille_decrite():
    """Inventaire : chaque chemin servi appartient à une famille du tableau « Les familles de routes »."""
    familles = DESCRIPTION.split("### Les familles de routes", 1)[1].split("###", 1)[0]
    for chemin in app.openapi()["paths"]:
        famille = "/donnees/*" if chemin.startswith("/donnees/") else (
            "/exercice/*" if chemin.startswith("/exercice/") else chemin)
        assert f"`{famille}`" in familles, chemin
