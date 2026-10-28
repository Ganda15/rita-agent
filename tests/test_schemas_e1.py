"""Les schémas du rapport E1 disent ce que dit le code, et restent à jour (C1, C2, C3, C5).

Pourquoi ce test (04/10/2026) : le schéma de collecte du 11/08 (`evidence/C1/SCHEMA-C1-...`)
affichait « 9 motifs, 100 % blocage » pour le garde-fou d'injection, et « 8 tables ». Au 04/10,
le code compte 12 motifs, la mesure donne 70 % et la base 10 tables. Un schéma dessiné à la main
vieillit sans bruit, et un jury qui lit 100 % ici et 70 % dans le rapport E3 voit une contradiction.

Ici les chiffres viennent du code au moment de la génération (`faits()`), et deux contrôles
empêchent la dérive : chaque chiffre affiché est celui du code, et le fichier rangé est
exactement ce que le générateur produit aujourd'hui.
"""
import importlib.util
import re
from pathlib import Path

import pytest

RACINE = Path(__file__).parent.parent
DOSSIER = RACINE / "docs/rapports/E1/schemas"
NOMS = ("E1-collecte", "E1-nettoyage", "E1-requetes", "E1-api")
# 27/10/2026 : C2 (requêtes) et C5 (API) ont leur schéma, et C3 passe à la mise en forme de C1, à la demande d'Era.
# L'illustration de ces trois-là est produite par le générateur ; celle de la collecte reste celle fournie par Era.
ILLUSTRES_GENERES = ("E1-nettoyage", "E1-requetes", "E1-api")


@pytest.fixture(scope="module")
def gen():
    chemin = DOSSIER / "generer_schemas.py"
    assert chemin.exists(), "générateur docs/rapports/E1/schemas/generer_schemas.py absent"
    spec = importlib.util.spec_from_file_location("schemas_e1", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def faits(gen):
    return gen.faits()


@pytest.mark.parametrize("nom", NOMS)
@pytest.mark.parametrize("ext", ("drawio", "svg", "png"))
def test_chaque_schema_existe_en_drawio_svg_et_png(nom, ext):
    """Règle du dépôt : un .drawio pour corriger, une image pour voir."""
    assert (DOSSIER / f"{nom}.{ext}").exists(), f"{nom}.{ext} absent"


def test_les_faits_sont_lus_dans_le_code_pas_recopies(faits):
    import guardrails.injection as inj
    import sources.rss as rss
    schema = (RACINE / "db/schema.sql").read_text(encoding="utf-8")
    assert faits["tables"] == len(re.findall(r"CREATE TABLE", schema, re.I))
    assert faits["check"] == len(re.findall(r"\bCHECK\s*\(", schema))
    assert faits["motifs_injection"] == len(inj.MOTIFS)
    assert faits["flux_generaux"] == len(rss.FLUX)


def test_le_taux_de_blocage_affiche_est_celui_mesure(faits):
    from evals.mesurer_gardefou import mesurer
    assert faits["blocage_injection"] == round(mesurer()["taux_blocage"])


@pytest.mark.parametrize("nom", NOMS)
def test_le_fichier_range_est_celui_que_produit_le_generateur(gen, nom):
    """Si le code change (une table, un motif, une mesure) sans que le schéma soit régénéré,
    ce test tombe : c'est lui qui empêche le schéma de vieillir en silence."""
    schema = gen.SCHEMAS[nom]()
    assert (DOSSIER / f"{nom}.svg").read_text(encoding="utf-8") == gen.svg(schema), \
        f"{nom}.svg n'est plus à jour : relancer generer_schemas.py, puis le rendu PNG"
    assert (DOSSIER / f"{nom}.drawio").read_text(encoding="utf-8") == gen.drawio(schema)


def test_le_schema_de_collecte_affiche_les_chiffres_du_code(gen, faits):
    texte = gen.svg(gen.SCHEMAS["E1-collecte"]())
    assert f"{faits['tables']} tables" in texte
    assert f"{faits['motifs_injection']} motifs" in texte
    assert f"{faits['blocage_injection']} % de blocage" in texte
    assert "100 % blocage" not in texte and "100 % de blocage" not in texte
    t, p = faits["traitements_rgpd"], faits["procedures_rgpd"]
    assert f"traitements {t[0]} à {t[-1]}" in texte, "les traitements du registre RGPD ne sont pas ceux du schéma"
    assert f"procédures de tri {p[0]} à {p[-1]}" in texte, "les procédures du registre RGPD ne sont pas celles du schéma"


def test_le_schema_de_nettoyage_relie_chaque_regle_a_son_fichier(gen):
    """C3 : une règle de nettoyage sans son fichier n'est pas vérifiable par le jury."""
    texte = gen.svg(gen.SCHEMAS["E1-nettoyage"]())
    for fichier in ("db/importer.py", "db/schema.sql", "sources/marches.py", "sources/positions.py"):
        assert fichier in texte, f"{fichier} n'est cité nulle part dans le schéma de nettoyage"
        assert (RACINE / fichier).exists(), f"{fichier} cité mais absent du dépôt"


# --- 24/10/2026 : la mise en forme illustrée du schéma de collecte (modèle fourni par Era) ---------------------------
# Le PNG remis au jury est rendu depuis E1-collecte-illustre.html, mis en forme hors du générateur (icônes, formes).
# Sans ce test, ses textes vieilliraient en silence, exactement le défaut que ce fichier existe pour empêcher.

def _textes(morceaux: list[str]) -> list[str]:
    import html
    return [" ".join(html.unescape(m).split()) for m in morceaux if m.strip()]


@pytest.mark.parametrize("nom", NOMS)
def test_le_schema_illustre_dit_exactement_ce_que_dit_le_schema_genere(gen, nom):
    source = (DOSSIER / f"{nom}-illustre.html").read_text(encoding="utf-8")
    corps = re.sub(r"<(style|title)[^>]*>.*?</\1>", "", source, flags=re.S)
    illustre = _textes(re.split(r"<[^>]+>", corps))
    genere = _textes([re.sub(r"<[^>]+>", "", t) for t in re.findall(r"<text[^>]*>(.*?)</text>",
                                                                     gen.svg(gen.SCHEMAS[nom]()), re.S)])
    tout_illustre, tout_genere = " ".join(illustre), " ".join(genere)
    pied = [t for t in illustre if t.startswith("Mise en forme illustrée")]
    assert len(pied) == 1, "le pied de l'illustration doit dire qu'elle est une mise en forme, pas une génération"
    assert [t for t in illustre if t not in tout_genere and t not in pied] == [], "texte de l'illustration absent du schéma généré"
    assert [t for t in genere if t not in tout_illustre and not t.startswith("Génération :")] == [], \
        "texte du schéma généré absent de l'illustration"


# --- 27/10/2026 : C2 et C5 ont leur schéma, C3 passe à la mise en forme de C1 (demande d'Era) -------------------------

@pytest.mark.parametrize("nom", ILLUSTRES_GENERES)
def test_l_illustration_rangee_est_celle_que_produit_le_generateur(gen, nom):
    """Ces trois illustrations sortent du générateur : un chiffre qui change sans régénération fait tomber ce test."""
    assert (DOSSIER / f"{nom}-illustre.html").read_text(encoding="utf-8") == gen.illustre(gen.SCHEMAS[nom]()), \
        f"{nom}-illustre.html n'est plus à jour : relancer generer_schemas.py, puis le rendu PNG"


@pytest.mark.parametrize("nom", NOMS)
def test_aucun_texte_ne_deborde_de_sa_boite(gen, nom):
    """Estimation du générateur (la vraie mesure se fait au rendu) : la dernière ligne tient au-dessus du bord bas."""
    s = gen.SCHEMAS[nom]()
    for b in s.boites:
        if b.genre == "zone":
            continue
        titres, lignes = gen._textes(b)
        derniere = 26 + 19 * len(titres) + 3 + 17 * (len(lignes) - 1) if lignes else 26 + 19 * (len(titres) - 1)
        assert derniere + 8 <= b.h, f"{nom}, boîte {b.id} : le texte descend à {derniere + 8}, la boîte mesure {b.h}"


def test_le_schema_des_requetes_lit_ses_filtres_dans_le_code(gen):
    """C2 : les partitions lues par S2 et S3 se déduisent du filtre écrit dans bigdata/query_spark.py."""
    import bigdata.query_spark as q
    f = gen.faits_requetes()
    assert f"annee >= {f['annee_s2']}" in q.S2_AMPLITUDE and f"annee >= {f['annee_s3']}" in q.S3_EXTREMES
    comptes = gen.PARQUET_27_10
    lues_s2 = sum(n for a, n in comptes.items() if a >= f["annee_s2"])
    texte = gen.svg(gen.SCHEMAS["E1-requetes"]())
    assert f"{len(comptes)} partitions" in texte
    assert f"{sum(comptes.values()):,}".replace(",", " ") + " lignes" in texte
    assert f"{lues_s2:,}".replace(",", " ") + " lignes" in texte


def test_les_mesures_postgresql_du_schema_sont_celles_de_db_requetes_sql(gen):
    """Une durée affichée sans sa source est une durée inventée : chacune doit être écrite dans db/requetes.sql."""
    requetes = (RACINE / "db/requetes.sql").read_text(encoding="utf-8")
    texte = gen.svg(gen.SCHEMAS["E1-requetes"]())
    mesures = re.findall(r"\d+,\d+ ms", texte)
    assert len(mesures) >= 4
    for m in mesures:
        assert m.replace(" ms", "") in requetes, f"{m} affiché mais absent de db/requetes.sql"


def test_les_partitions_affichees_sont_celles_du_parquet():
    """Comptage daté (27/10) : vérifié contre l'archive quand elle est là. Elle n'est pas dans le dépôt, donc pas en CI."""
    pq = pytest.importorskip("pyarrow.parquet")
    dossier = RACINE / "data/bigdata/ohlcv"
    if not dossier.exists():
        pytest.skip("archive Parquet absente de cette machine : contrôle local seulement")
    spec = importlib.util.spec_from_file_location("schemas_e1_pq", DOSSIER / "generer_schemas.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    comptes = {int(d.name.split("=")[1]): sum(pq.ParquetFile(f).metadata.num_rows for f in d.glob("*.parquet"))
               for d in dossier.glob("annee=*")}
    assert comptes == module.PARQUET_27_10


def test_le_schema_de_l_api_affiche_chaque_route_et_le_contrat_du_code(gen):
    """C5 : chaque point de terminaison de api/donnees.py est sur le schéma, et le contrat est celui de l'application."""
    from api.main import LONGUEUR_MINIMALE_CLE, app
    donnees = (RACINE / "api/donnees.py").read_text(encoding="utf-8")
    routes = re.findall(r'@routeur\.get\(\s*"([^"]+)"', donnees)
    contrat = app.openapi()
    texte = gen.svg(gen.SCHEMAS["E1-api"]())
    assert len(routes) == 12
    for r in routes:
        assert r in texte, f"route /donnees{r} absente du schéma de l'API"
    assert f"{len(routes)} points de terminaison" in texte
    assert f"OpenAPI {contrat['openapi']}" in texte
    assert f"{len(contrat['paths'])} chemins" in texte
    assert f"au moins {LONGUEUR_MINIMALE_CLE} caractères" in texte
    assert "403" in texte


# --- 28/10/2026 : relecture croisée (un second agent, vérifiée contre le code) : ce que les schémas disaient de trop ---

def test_le_nettoyage_ne_dit_pas_que_toutes_les_requetes_ecartent_les_valeurs_douteuses(gen):
    """R1 (le portefeuille) ne filtre pas statut_qualite (db/requetes.sql, « Aucun filtre ») : seules R2 et R3 le font."""
    requetes = (RACINE / "db/requetes.sql").read_text(encoding="utf-8")
    assert "Aucun filtre sur `statut_qualite`" in requetes
    texte = gen.svg(gen.SCHEMAS["E1-nettoyage"]())
    assert "exclue des requêtes" not in texte and "les requêtes ne lisent que" not in texte
    assert "R1" in texte


def test_le_nettoyage_affiche_la_cle_de_dedoublonnage_du_code(gen):
    """db/importer.py dédoublonne sur (ticker, date), la date de l'archive, avant le calcul de date_seance."""
    importer = (RACINE / "db/importer.py").read_text(encoding="utf-8")
    cle = re.search(r'drop_duplicates\(subset=\["(\w+)", "(\w+)"\]', importer).groups()
    texte = gen.svg(gen.SCHEMAS["E1-nettoyage"]())
    assert f"({cle[0]}, {cle[1]})" in texte
    assert "(ticker, date_seance) avant insertion" not in texte


def test_le_nettoyage_dit_la_limite_des_libelles_cgg(gen):
    """Addendum C3 du 26/10 : deux libellés sur un ticker ne prouvent pas un même instrument."""
    assert "ne démontre pas : que les deux libellés désignent le même instrument" in \
        (RACINE / "evidence/C3/preuve-dedoublonnage-cgg.md").read_text(encoding="utf-8")
    assert "même instrument" in gen.svg(gen.SCHEMAS["E1-nettoyage"]())


def test_l_api_ne_se_dit_pas_en_lecture_seule_tant_que_l_audit_mcp_ecrit(gen):
    """Un appel qui porte X-Client-Id (la passerelle MCP) laisse une ligne dans mcp_calls, /donnees compris."""
    main = (RACINE / "api/main.py").read_text(encoding="utf-8")
    assert 'request.headers.get("X-Client-Id"' in main and "audit_mcp.enregistrer" in main
    texte = gen.svg(gen.SCHEMAS["E1-api"]())
    assert "n'écrit en base" not in texte and "en lecture seule" not in texte
    assert "mcp_calls" in texte


def test_l_api_ne_promet_pas_le_jeu_complet(gen):
    """Aucune route de api/donnees.py ne sert taux_change : la bande de couverture le dit, sans « jeu complet »."""
    assert "taux_change" not in (RACINE / "api/donnees.py").read_text(encoding="utf-8")
    texte = gen.svg(gen.SCHEMAS["E1-api"]())
    assert "jeu complet" not in texte and "taux de change" in texte
