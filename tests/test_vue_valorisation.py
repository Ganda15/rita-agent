"""La vue de valorisation ne remplace plus un taux de change manquant par 1 (issue #65, cas D06
du chapitre « Données », plan `docs/PLAN-65-valorisation-taux-manquant.md`, validé par Era le 03/10/2026).

Avant : `COALESCE(t.valeur_pour_eur, 1)` dans trois copies du même SQL (la vue, la requête R1 du
rapport E1, l'extraction lue par l'API). Une devise sans taux divisait par 1 : un montant en dollars
s'affichait en euros. Après : l'euro se convertit par 1 sans lire `taux_change` ; une devise étrangère
sans taux rend `NULL` et la colonne `taux_manquant` vaut vrai ; la ligne reste visible.

Deux familles de tests ici : des tests de contrat sur le texte des trois copies (ils figent la
règle et tiennent les copies alignées), et des tests sur la base réelle, dans une transaction
annulée (règle INC-006 : un test n'écrit jamais en production), sautés sans `DATABASE_URL`.
"""
import re
from pathlib import Path

import pytest

from sources import database

RACINE = Path(__file__).resolve().parent.parent
SCHEMA = (RACINE / "db" / "schema.sql").read_text(encoding="utf-8")
REQUETES = (RACINE / "db" / "requetes.sql").read_text(encoding="utf-8")
INDICATEURS_PORTEFEUILLE = (RACINE / "db" / "indicateurs_portefeuille.sql").read_text(encoding="utf-8")


def _bloc(texte: str, debut: str, fin: str) -> str:
    i = texte.index(debut)
    return texte[i:texte.index(fin, i)]


COPIES = {
    "vue": _bloc(SCHEMA, "CREATE VIEW v_portefeuille_valorise", "COMMENT ON VIEW v_portefeuille_valorise"),
    "R1": _bloc(REQUETES, "-- R1 ", "-- R1 bis "),   # R1 bis (positions closes) est une autre requête
    "SQL_PORTEFEUILLE": database.SQL_PORTEFEUILLE,
}
CONVERSION = "CASE WHEN p.devise = 'EUR' THEN 1 ELSE t.valeur_pour_eur END"


# --- 1. les trois copies disent la même règle ---------------------------------------------------

@pytest.mark.parametrize("nom", COPIES)
def test_aucune_copie_ne_remplace_un_taux_manquant_par_1(nom):
    assert "COALESCE(t.valeur_pour_eur, 1)" not in COPIES[nom]


@pytest.mark.parametrize("nom", COPIES)
def test_l_euro_se_convertit_par_1_sans_lire_taux_change(nom):
    """Une position en EUR ne doit plus dépendre de la ligne « EUR = 1 » que l'étape ecb insère."""
    assert CONVERSION in COPIES[nom]


@pytest.mark.parametrize("nom", COPIES)
def test_chaque_copie_expose_taux_manquant(nom):
    assert "AS taux_manquant" in COPIES[nom]
    assert "LEFT JOIN   taux_du_jour t" in COPIES[nom] or "LEFT JOIN taux_du_jour t" in COPIES[nom], \
        "la ligne doit rester visible sans taux : LEFT JOIN, jamais INNER"


def _expressions(sql: str) -> list[str]:
    """Les expressions de calcul des montants, blancs normalisés : ce qui doit être identique."""
    return [re.sub(r"\s+", " ", m).strip()
            for m in re.findall(r"ROUND\(p\.quantite \* (?:p\.pru|d\.cloture)[^\n]*?\)\s*AS \w+", sql)]


def test_les_trois_copies_calculent_exactement_la_meme_chose():
    """Trois copies, un seul calcul : c'est ce test qui les tient alignées, pas la discipline."""
    reference = _expressions(COPIES["vue"])
    assert len(reference) == 2, reference
    for nom, sql in COPIES.items():
        assert _expressions(sql) == reference, nom


# --- 2. poids et exposition ne prétendent plus être complets --------------------------------------

def _requete(nom: str) -> str:
    i = INDICATEURS_PORTEFEUILLE.index(f"-- @@REQUETE {nom}")
    j = INDICATEURS_PORTEFEUILLE.find("-- @@REQUETE", i + 1)
    bloc = INDICATEURS_PORTEFEUILLE[i:j if j > 0 else None]
    return "\n".join(l.split("--", 1)[0] for l in bloc.splitlines())


@pytest.mark.parametrize("nom", ["poids", "exposition"])
def test_un_taux_manquant_rend_les_parts_indisponibles_et_le_dit(nom):
    """Un poids calculé sur un total partiel est faux pour chaque ligne, pas seulement pour celle
    qui manque : si une valorisation est nulle, toutes les parts sont NULL et `complet` est faux."""
    sql = _requete(nom)
    assert "BOOL_OR(taux_manquant)" in sql
    assert "AS complet" in sql


# --- 3. sur la base réelle, dans une transaction annulée ------------------------------------------

psycopg2 = pytest.importorskip("psycopg2")


@pytest.fixture
def curseur():
    from tests.test_role_lecture import dsn_proprietaire
    try:
        con = psycopg2.connect(dsn_proprietaire(), connect_timeout=3)
    except psycopg2.OperationalError as e:
        pytest.skip(f"PostgreSQL injoignable : {e}")
    con.autocommit = False
    cur = con.cursor()
    yield cur
    con.rollback()      # tout ce qui suit est annulé : la base de production ne bouge jamais
    con.close()


def _une_valeur(cur) -> str:
    cur.execute("SELECT ticker FROM valeur ORDER BY ticker LIMIT 1")
    return cur.fetchone()[0]


def test_en_base_une_devise_sans_taux_rend_indisponible_et_la_ligne_reste_visible(curseur):
    """Cas D06 : taux absent, montant indisponible, pas 200 pour 10 titres à 20 USD."""
    ticker = _une_valeur(curseur)
    curseur.execute("DELETE FROM taux_change WHERE devise = 'USD'")
    curseur.execute("INSERT INTO position (ticker, quantite, pru, devise) VALUES (%s, 10, 20, 'USD')", (ticker,))
    curseur.execute("SELECT devise, investi_eur, valorisation_eur, taux_manquant FROM v_portefeuille_valorise "
                    "WHERE ticker = %s AND devise = 'USD'", (ticker,))
    lignes = curseur.fetchall()
    assert len(lignes) == 1, "la ligne doit rester visible (LEFT JOIN), pas disparaître"
    devise, investi, valorisation, taux_manquant = lignes[0]
    assert investi is None and valorisation is None
    assert taux_manquant is True


def test_en_base_une_position_en_euros_se_valorise_meme_sans_aucun_taux(curseur):
    """L'euro se convertit par 1 par construction, plus par la ligne « EUR = 1 » de l'étape ecb."""
    ticker = _une_valeur(curseur)
    curseur.execute("DELETE FROM taux_change")
    curseur.execute("INSERT INTO position (ticker, quantite, pru, devise) VALUES (%s, 10, 20, 'EUR')", (ticker,))
    curseur.execute("SELECT investi_eur, taux_manquant FROM v_portefeuille_valorise WHERE ticker = %s AND pru = 20",
                    (ticker,))
    investi, taux_manquant = curseur.fetchone()
    assert investi == 200 and taux_manquant is False


def test_en_base_avec_un_taux_present_la_conversion_est_juste(curseur):
    """10 titres à 20 USD, taux 1,25 USD pour 1 EUR : 160 EUR, l'exemple du chapitre."""
    ticker = _une_valeur(curseur)
    curseur.execute("DELETE FROM taux_change WHERE devise = 'USD'")
    curseur.execute("INSERT INTO taux_change (devise, date_taux, valeur_pour_eur) VALUES ('USD', CURRENT_DATE, 1.25)")
    curseur.execute("INSERT INTO position (ticker, quantite, pru, devise) VALUES (%s, 10, 20, 'USD')", (ticker,))
    curseur.execute("SELECT investi_eur, taux_manquant FROM v_portefeuille_valorise WHERE ticker = %s AND devise = 'USD'",
                    (ticker,))
    investi, taux_manquant = curseur.fetchone()
    assert float(investi) == 160.0 and taux_manquant is False


# --- plan 66 (03/10/2026) : une position close ne se valorise plus ---------------------------------

FRAICHEUR = (RACINE / "db" / "fraicheur.sql").read_text(encoding="utf-8")


@pytest.mark.parametrize("nom", COPIES)
def test_chaque_copie_ne_valorise_que_les_positions_detenues(nom):
    assert "p.date_cloture IS NULL" in COPIES[nom], nom


def test_la_fraicheur_ne_compte_que_les_positions_detenues():
    assert re.search(r"FROM position\s+WHERE date_cloture IS NULL\)\s+AS nb_positions", FRAICHEUR)


def test_une_requete_r1_bis_sert_les_positions_closes_au_proprietaire_seul():
    """D3 : les closes ne sortent ni par l'API ni par MCP ; une requete dans db/requetes.sql suffit."""
    bloc = _bloc(REQUETES, "-- R1 bis ", "-- R2 ")
    assert "date_cloture IS NOT NULL" in bloc
    assert "COALESCE(t.valeur_pour_eur, 1)" not in bloc
