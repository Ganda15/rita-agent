"""Tests du laboratoire big data.

Deux familles, volontairement séparées :

* **rapides** — vérifient la configuration et les requêtes SANS lancer Spark. Ils tournent
  en CI, où il n'y a ni JDK ni jeu Parquet.
* **d'intégration** — lancent une vraie session Spark. Ignorés automatiquement si `JAVA_HOME`
  ou le jeu Parquet manquent : un test qui échoue faute d'environnement n'apprend rien.
"""
import os
import re
import shutil

import pytest

from bigdata import query_spark, session_spark

JAVA_DISPO = bool(os.environ.get("JAVA_HOME") or session_spark.JAVA_HOME_DEFAUT.exists()
                  or shutil.which("java"))
PARQUET_DISPO = session_spark.PARQUET.exists()

integration = pytest.mark.skipif(
    not (JAVA_DISPO and PARQUET_DISPO),
    reason="JAVA_HOME ou jeu Parquet absent — test d'integration ignore",
)


# --- rapides : configuration --------------------------------------------------

def test_prepare_environnement_renseigne_pyspark_python():
    """Sans PYSPARK_PYTHON, Spark lance `python` — absent du PATH sur cette machine."""
    session_spark.preparer_environnement()
    assert os.environ["PYSPARK_PYTHON"].endswith("python.exe")


def test_les_fichiers_sont_des_uri_file():
    """Spark attend des URI, pas des chemins Windows : `file:///D:/...`, jamais `D:\\...`."""
    for uri in session_spark.fichiers_parquet():
        assert uri.startswith("file:///")
        assert "\\" not in uri


@pytest.mark.skipif(not PARQUET_DISPO, reason="jeu Parquet absent")
def test_un_fichier_par_partition_annee():
    fichiers = session_spark.fichiers_parquet()
    assert len(fichiers) >= 10
    assert all("annee%3D" in f or "annee=" in f for f in fichiers)


# --- rapides : les requêtes SQL -----------------------------------------------

def test_les_trois_requetes_sont_declarees():
    assert set(query_spark.REQUETES) == {"volumetrie", "amplitude", "extremes"}


@pytest.mark.parametrize("cle", ["volumetrie", "amplitude", "extremes"])
def test_chaque_requete_lit_la_vue_cotation(cle):
    _, sql = query_spark.REQUETES[cle]
    assert "FROM   cotation" in sql or "FROM cotation" in sql


@pytest.mark.parametrize("cle", ["amplitude", "extremes"])
def test_les_requetes_filtrent_sur_la_colonne_de_partition(cle):
    """`annee` est la colonne de partitionnement : filtrer dessus déclenche le pruning.
    C'est l'optimisation majeure du monde big data — sans elle, Spark lit tout."""
    _, sql = query_spark.REQUETES[cle]
    assert re.search(r"annee\s*>=", sql)


def test_amplitude_evite_la_division_par_zero():
    """L'analyse exploratoire a mesuré des cours à 0,01 et 2 802 volumes nuls."""
    _, sql = query_spark.REQUETES["amplitude"]
    assert "bas > 0" in sql


def test_extremes_ecarte_la_premiere_seance():
    """LAG() renvoie NULL sur la première séance — la variation n'existe pas."""
    _, sql = query_spark.REQUETES["extremes"]
    assert "veille IS NOT NULL" in sql


def test_requete_inconnue_leve_avant_de_lancer_spark():
    """Démarrer une JVM pour découvrir un nom de requête invalide serait absurde."""
    with pytest.raises(ValueError, match="Requete\\(s\\) inconnue"):
        query_spark.executer("nexiste_pas")


# --- intégration : vraie session Spark ----------------------------------------

@integration
def test_spark_lit_le_parquet_nativement():
    """Contournement Windows : en passant les fichiers explicitement, on n'appelle jamais
    le code natif Hadoop (`NativeIO$Windows.access0`) qui exige winutils.exe."""
    spark = session_spark.creer_session("test-lecture")
    try:
        df = session_spark.charger_cotations(spark)
        assert df.count() > 250_000
        assert "annee" in df.columns          # `basePath` a bien restitué la partition
    finally:
        spark.stop()


@integration
def test_le_partition_pruning_apparait_dans_le_plan():
    """La preuve que Spark ne lit qu'une partition sur onze."""
    spark = session_spark.creer_session("test-pruning")
    try:
        df = session_spark.charger_cotations(spark).filter("annee = 2024")
        plan = df._jdf.queryExecution().simpleString()
        assert "PartitionFilters" in plan
        assert "annee" in plan.split("PartitionFilters")[1][:80]
    finally:
        spark.stop()


@integration
def test_les_trois_requetes_sql_retournent_des_lignes():
    r = query_spark.executer()
    assert len(r["resultats"]) == 3
    for res in r["resultats"]:
        assert res["lignes"], f"{res['cle']} n'a retourne aucune ligne"


@integration
def test_les_requetes_filtrees_declenchent_bien_le_pruning():
    """Vérifie le pruning sur le plan RÉEL, pas seulement dans le texte SQL."""
    for cle in ("amplitude", "extremes"):
        res = query_spark.executer(cle)["resultats"][0]
        assert res["pruning"], f"{cle} : aucun PartitionFilters dans le plan"
