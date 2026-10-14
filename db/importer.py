"""Import des données préparées vers PostgreSQL (C4 — script d'import).

Critère C4 : « Le script d'import fourni est fonctionnel : il permet l'insertion des
données dans le système mis en place. »

Le script applique **au moment de l'import** les règles de nettoyage établies par
l'analyse exploratoire (`bigdata/explorer.py`, 31/07/2026) :

  - dédoublonnage sur (ticker, date_seance) — 2 560 lignes redondantes mesurées
  - marquage des valeurs incohérentes plutôt que suppression (STLAP.PA, ALJXR.PA)
  - résolution des alias de portefeuille vers un ticker unique (cas CGG -> VIRI.PA)

Connexion : variable `DATABASE_URL`, ou `--dsn` en ligne de commande.

    postgresql://rita:rita_dev_local@localhost:5432/rita     (docker compose)

Usage :
    python -m db.importer                      # tout
    python -m db.importer --dsn "postgresql://..." --limite-annees 3
"""
from __future__ import annotations

import argparse
import csv
import logging
import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.extras import execute_values

from sources.marches import date_de_seance, devise_de_cotation, facteur_prix

# Sans cette ligne, le script ne lit PAS le .env et retombe sur DSN_DEFAUT, qui
# pointe le port 5432 du docker-compose — alors que le PostgreSQL réel écoute sur
# 5433. Constaté le 16/08/2026 : l'import échouait avec « Connection refused » sur
# un port que personne n'écoutait. Seul api/main.py chargeait le .env.
load_dotenv()

logger = logging.getLogger(__name__)

RACINE = Path(__file__).resolve().parent.parent
PARQUET = RACINE / "data" / "bigdata" / "ohlcv"
UNIVERS = RACINE / "data" / "univers-155.csv"

DSN_DEFAUT = "postgresql://rita:rita_dev_local@localhost:5432/rita"

# Valeurs écartées du calcul mais CONSERVÉES en base, avec leur cause.
# Constats mesurés, pas suppositions — voir evidence/C1/preuve-09-analyse-exploratoire.md
QUALITE = {
    "STLAP.PA": ("INCOHERENT",
                 "1142 clotures hors bornes + 1143 volumes nuls (explorer.py 31/07/2026)"),
    "ALJXR.PA": ("INCOHERENT",
                 "prix max 7 156 748 EUR - echelle aberrante (ligne de droits non ajustee)"),
    # 27/09/2026 (#48) : classées OK_PARTIEL dans l'univers (« série partielle »), elles
    # devenaient OK en base et étaient redemandées à Yahoo chaque soir, en échec.
    # Leur historique reste : il sert à mesurer le biais du survivant.
    "ZC.PA": ("DELISTEE", "radiee : derniere seance le 2018-03-22 (Zodiac Aerospace)"),
    "ELE.PA": ("DELISTEE", "radiee : derniere seance le 2018-04-26 (Euler Hermes)"),
    "GTO.PA": ("DELISTEE", "radiee : derniere seance le 2019-05-28 (Gemalto)"),
}


def charger_univers() -> tuple[dict[str, dict], list[tuple[str, str]]]:
    """Lit l'univers et sépare les valeurs de leurs alias de portefeuille.

    Retourne (valeurs par ticker, liste d'alias). C'est ici que le cas CGG se résout :
    deux libellés (« CGG BS », « CGG RGPT ») produisent UNE valeur et DEUX alias.
    """
    valeurs: dict[str, dict] = {}
    alias: list[tuple[str, str]] = []

    with open(UNIVERS, encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            if not ligne["statut"].startswith("OK"):
                continue
            ticker, nom = ligne["ticker"], ligne["nom"]
            alias.append((nom, ticker))
            if ticker not in valeurs:
                statut, note = QUALITE.get(ticker, ("OK", None))
                valeurs[ticker] = {"ticker": ticker, "nom": nom,
                                   "statut": statut, "note": note}

    return valeurs, alias


def importer_valeurs(cur, valeurs: dict[str, dict], alias: list[tuple[str, str]]) -> None:
    # 27/09/2026 (#47) : la devise n'était jamais renseignée, donc EUR par défaut pour
    # tout le monde, y compris FTI et SLB (dollars) et HSBA.L (livres).
    execute_values(cur, """
        INSERT INTO valeur (ticker, nom_officiel, statut_qualite, note_qualite, devise)
        VALUES %s
        ON CONFLICT (ticker) DO UPDATE
          SET nom_officiel   = EXCLUDED.nom_officiel,
              statut_qualite = EXCLUDED.statut_qualite,
              note_qualite   = EXCLUDED.note_qualite,
              devise         = EXCLUDED.devise
    """, [(v["ticker"], v["nom"], v["statut"], v["note"], devise_de_cotation(v["ticker"]))
          for v in valeurs.values()])

    execute_values(cur, """
        INSERT INTO alias_valeur (alias, ticker) VALUES %s
        ON CONFLICT (alias) DO NOTHING
    """, alias)


def importer_cotations(cur, limite_annees: int | None = None) -> dict:
    """Charge le Parquet, dédoublonne, insère en lot."""
    if not PARQUET.exists():
        raise FileNotFoundError(
            f"Jeu Parquet absent : {PARQUET}\n"
            "Le construire avec : python -m bigdata.build_parquet"
        )

    df = pd.read_parquet(PARQUET)
    lues = len(df)

    if limite_annees:
        seuil = int(df["annee"].max()) - limite_annees + 1
        df = df[df["annee"] >= seuil]

    # --- Dédoublonnage C3 : la règle établie dans evidence/C3/ ---
    avant = len(df)
    df = df.drop_duplicates(subset=["ticker", "date"], keep="first")
    retirees = avant - len(df)

    # Les tickers absents de `valeur` ne peuvent pas entrer (clé étrangère).
    cur.execute("SELECT ticker FROM valeur")
    connus = {r[0] for r in cur.fetchall()}
    orphelins = set(df["ticker"].unique()) - connus
    if orphelins:
        logger.warning("%d ticker(s) hors univers ignore(s) : %s",
                       len(orphelins), sorted(orphelins)[:5])
        df = df[df["ticker"].isin(connus)]

    # 27/09/2026 (#53) : `r.date.date()` prenait la date UTC. Le Parquet stocke minuit
    # heure de la place converti en UTC, soit 22h00 ou 23h00 LA VEILLE à Paris : dix ans
    # d'archive étaient décalés d'un jour (52 426 cotations rangées un dimanche). Le fait
    # était pourtant écrit dans `sources/cotations.py` depuis le 03/08 (§2).
    # Et Londres cote en pence : on ramène en livres (#47).
    lignes = []
    for r in df.itertuples():
        f = facteur_prix(r.ticker)
        lignes.append((r.ticker, date_de_seance(r.date, r.ticker),
                       float(r.ouverture) * f, float(r.haut) * f,
                       float(r.bas) * f, float(r.cloture) * f, int(r.volume)))

    execute_values(cur, """
        INSERT INTO cotation
              (ticker, date_seance, ouverture, haut, bas, cloture, volume)
        VALUES %s
        ON CONFLICT (ticker, date_seance) DO NOTHING
    """, lignes, page_size=5000)

    # Bornes de cotation : servent la détection du biais de survie (requête « perf 10 ans »)
    cur.execute("""
        UPDATE valeur v SET premiere_cotation = b.mini, derniere_cotation = b.maxi
        FROM (SELECT ticker, min(date_seance) mini, max(date_seance) maxi
              FROM cotation GROUP BY ticker) b
        WHERE b.ticker = v.ticker
    """)

    return {"lues": lues, "dedoublonnees": retirees, "inserees": len(lignes)}


CLE_DATE_PAR_DEFAUT = "1900-01-01"   # ce que l'index unique met a la place d'une date d'achat absente
CLE_LIGNE = "(ticker, pru, COALESCE(date_achat, DATE '1900-01-01'))"


def importer_positions(cur) -> dict:
    """Réconcilie la table `position` avec le CSV : le CSV dit ce qui est détenu (plan 66, D1 à D4 = A).

    1. Les lignes présentes sont **upsertées** sur la clé (ticker, PRU, date d'achat) : une quantité
       modifiée se met à jour, une ligne revenue se rouvre (`date_cloture = NULL`), rien ne se duplique.
       Avant : un `INSERT` sans clé, qui dupliquait tout le portefeuille à la seconde exécution.
    2. Les lignes absentes du CSV sont **closes**, datées du jour : la vente est datée du jour où on la
       constate, le CSV n'a pas de date de vente. Jamais supprimées : P2 les purge trois ans après.
    3. Garde-fou (D4) : un CSV sans aucune ligne valide ne clôt rien et le dit ; moins de la moitié des
       positions actives : on clôt quand même mais on avertit (vente massive ou fichier partiel ?).
    4. Cas D07 (#69) : une position dont la devise du PRU diffère de celle de la valeur cotée est
       importée mais signalée en WARNING et comptée ; la comparaison PRU / cours se lit alors dans la
       devise de la position, pas en euros.
    """
    from sources.positions import lire

    portefeuille = lire()
    lignes, ignorees, devises_differentes = [], [], 0

    for p in portefeuille.positions:
        cur.execute("SELECT ticker, devise FROM valeur WHERE ticker = %s", (p.ticker,))
        trouve = cur.fetchone()
        if not trouve:
            cur.execute("SELECT v.ticker, v.devise FROM alias_valeur a JOIN valeur v ON v.ticker = a.ticker "
                        "WHERE a.alias = %s", (p.nom,))
            trouve = cur.fetchone()
            if not trouve:
                ignorees.append(p.ticker)
                continue
        cible, devise_valeur = trouve[0], trouve[1]
        if devise_valeur and p.devise and p.devise != devise_valeur:
            devises_differentes += 1
            logger.warning("position %s : PRU en %s, valeur cotee en %s (cas D07) : la performance se lit "
                           "dans la devise de la position", cible, p.devise, devise_valeur)
        lignes.append((cible, p.quantite, p.pru, p.devise, p.date_achat or None))

    bilan = {"lignes": len(lignes), "inserees": 0, "mises_a_jour": 0, "rouvertes": 0, "closes": 0,
             "ignorees": len(ignorees), "devises_differentes": devises_differentes, "avertissement": None}
    if ignorees:
        logger.warning("%d position(s) sans valeur correspondante : %s", len(ignorees), ignorees)
    if not lignes:
        bilan["avertissement"] = ("aucune ligne valide dans le CSV : aucune position close (un fichier "
                                  "deplace ou corrompu ne vend pas un portefeuille)")
        logger.warning(bilan["avertissement"])
        return bilan

    cles = tuple((l[0], l[2], l[4] or CLE_DATE_PAR_DEFAUT) for l in lignes)

    cur.execute("SELECT count(*) FROM position WHERE date_cloture IS NULL")
    actives_avant = int(cur.fetchone()[0])
    cur.execute(f"SELECT count(*) FROM position WHERE date_cloture IS NOT NULL AND {CLE_LIGNE} IN %s", (cles,))
    bilan["rouvertes"] = int(cur.fetchone()[0])

    resultats = execute_values(cur, f"""
        INSERT INTO position (ticker, quantite, pru, devise, date_achat)
        VALUES %s
        ON CONFLICT {CLE_LIGNE} DO UPDATE
            SET quantite = EXCLUDED.quantite, devise = EXCLUDED.devise,
                date_cloture = NULL, importe_le = now()
        RETURNING (xmax = 0) AS inseree
    """, lignes, fetch=True)
    inserees = sum(1 for r in (resultats or []) if r and r[0])
    bilan["inserees"], bilan["mises_a_jour"] = inserees, len(lignes) - inserees

    cur.execute(f"UPDATE position SET date_cloture = CURRENT_DATE "
                f"WHERE date_cloture IS NULL AND {CLE_LIGNE} NOT IN %s", (cles,))
    bilan["closes"] = cur.rowcount if isinstance(cur.rowcount, int) and cur.rowcount >= 0 else 0

    if actives_avant and len(lignes) < actives_avant / 2:
        bilan["avertissement"] = (f"le CSV porte {len(lignes)} ligne(s) pour {actives_avant} position(s) active(s) : "
                                  f"{bilan['closes']} close(s). Vente massive ou fichier partiel ? Verifier le CSV.")
        logger.warning(bilan["avertissement"])
    return bilan


def importer(dsn: str, limite_annees: int | None = None) -> dict:
    valeurs, alias = charger_univers()

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            importer_valeurs(cur, valeurs, alias)
            stats = importer_cotations(cur, limite_annees)
            stats["valeurs"] = len(valeurs)
            stats["alias"] = len(alias)
            positions = importer_positions(cur)
            stats["positions"] = positions["lignes"]
            stats["positions_detail"] = positions
        conn.commit()

    return stats


# --- Le mode « démonstration » (sprint 2, tâche 5) -------------------------------------------------------------------
# Remplit une base NEUVE avec le jeu versionné `data/demo/`, pour reconstruire RITA depuis le dépôt. La base de
# démonstration porte une marque : le commentaire de la base. Toute base qui contient déjà des données sans cette marque
# est refusée, avant la moindre insertion : les tickers seuls ne disent pas si la destination est une vraie base.

MARQUE_DEMO = "rita-demonstration"
TABLES_DE_REFERENCE = {"devise"}   # les seules tables que db/schema.sql remplit lui-même


class BaseNonDemo(Exception):
    """La base contient déjà des données et ne porte pas la marque de démonstration : import refusé."""


def lire_marque(cur) -> str | None:
    """Le commentaire de la base courante (la marque de démonstration, ou autre chose, ou rien)."""
    cur.execute("SELECT shobj_description(oid, 'pg_database') FROM pg_database WHERE datname = current_database()")
    return cur.fetchone()[0]


def base_vide(cur) -> bool:
    """Toutes les tables du schéma `public` sont vides, sauf les tables de référence. Une table ajoutée plus tard au
    schéma est couverte sans changer ce code : la liste vient de `information_schema`."""
    cur.execute("SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")
    tables = [ligne[0] for ligne in cur.fetchall() if ligne[0] not in TABLES_DE_REFERENCE]
    for table in tables:
        cur.execute(sql.SQL("SELECT EXISTS (SELECT 1 FROM {})").format(sql.Identifier(table)))
        if cur.fetchone()[0]:
            return False
    return True


def preparer_base_demo(cur) -> None:
    """Accepte une base déjà marquée ; marque une base entièrement vide ; refuse tout le reste, avant toute insertion."""
    if lire_marque(cur) == MARQUE_DEMO:
        return
    if not base_vide(cur):
        raise BaseNonDemo("la base contient deja des donnees et ne porte pas la marque de demonstration : "
                          "import de demonstration refuse (rien n'a ete ecrit)")
    cur.execute("SELECT current_database()")
    nom = cur.fetchone()[0]
    cur.execute(sql.SQL("COMMENT ON DATABASE {} IS {}").format(sql.Identifier(nom), sql.Literal(MARQUE_DEMO)))


def _lire_csv(chemin: Path) -> list[dict[str, str]]:
    with open(chemin, encoding="utf-8", newline="") as fichier:
        return list(csv.DictReader(fichier, delimiter=";"))


def _inserer(cur, requete: str, lignes: list[tuple]) -> int:
    """Insère ligne par ligne et rend le nombre de lignes réellement insérées (`rowcount`)."""
    total = 0
    for ligne in lignes:
        cur.execute(requete, ligne)
        total += max(cur.rowcount, 0)
    return total


def importer_demo(cur, dossier: Path) -> dict[str, int]:
    """Importe les quatre fichiers du jeu ; une deuxième exécution n'insère rien (ON CONFLICT DO NOTHING)."""
    vide = lambda v: v or None  # noqa: E731 - une chaîne vide du CSV devient NULL
    valeurs = [(l["ticker"], l["nom_officiel"], vide(l["isin"]), l["devise"], vide(l["place_cotation"]))
               for l in _lire_csv(dossier / "valeurs.csv")]
    cotations = [(l["ticker"], l["date_seance"], l["ouverture"], l["haut"], l["bas"], l["cloture"], l["volume"])
                 for l in _lire_csv(dossier / "cotations.csv")]
    articles = [(l["source"], l["titre"], l["lien"], l["publie_le"], l["resume"])
                for l in _lire_csv(dossier / "articles.csv")]
    positions = [(l["ticker"], l["quantite"], l["pru"], l["devise"], l["date_achat"], l["ticker"])
                 for l in _lire_csv(dossier / "positions.csv")]
    return {
        "valeurs": _inserer(cur, "INSERT INTO valeur (ticker, nom_officiel, isin, devise, place_cotation) "
                                 "VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", valeurs),
        "cotations": _inserer(cur, "INSERT INTO cotation (ticker, date_seance, ouverture, haut, bas, cloture, volume) "
                                   "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", cotations),
        "articles": _inserer(cur, "INSERT INTO article (source, titre, lien, publie_le, resume) "
                                  "VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", articles),
        # Pas de clé naturelle sur `position` : aucune insertion si le ticker a déjà une position.
        "positions": _inserer(cur, "INSERT INTO position (ticker, quantite, pru, devise, date_achat) "
                                   "SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS "
                                   "(SELECT 1 FROM position WHERE ticker = %s)", positions),
    }


def importer_demo_complet(dsn: str, dossier: Path) -> dict[str, int]:
    """La marque puis l'import, dans une seule transaction : un refus ou une erreur n'écrit rien."""
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            preparer_base_demo(cur)
            bilan = importer_demo(cur, dossier)
        conn.commit()
    return bilan


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parseur = argparse.ArgumentParser(description="Import RITA -> PostgreSQL")
    parseur.add_argument("--dsn", default=os.getenv("DATABASE_URL", DSN_DEFAUT))
    exclusifs = parseur.add_mutually_exclusive_group()
    exclusifs.add_argument("--limite-annees", type=int, default=None,
                           help="n'importer que les N dernieres annees")
    exclusifs.add_argument("--demo", type=Path, default=None, metavar="DOSSIER",
                           help="remplir une base neuve avec le jeu de demonstration (data/demo)")
    args = parseur.parse_args()

    if args.demo:
        print(importer_demo_complet(args.dsn, args.demo))
        raise SystemExit(0)

    r = importer(args.dsn, args.limite_annees)

    print("\n=== IMPORT POSTGRESQL ===")
    print(f"Valeurs            : {r['valeurs']}")
    print(f"Alias portefeuille : {r['alias']}   (> valeurs = cas CGG resolu)")
    print(f"Cotations lues     : {r['lues']:,}")
    print(f"  dedoublonnees    : {r['dedoublonnees']:,}")
    print(f"  inserees         : {r['inserees']:,}")
    d = r["positions_detail"]
    print(f"Positions          : {r['positions']}  (inserees {d['inserees']}, mises a jour {d['mises_a_jour']}, "
          f"rouvertes {d['rouvertes']}, closes {d['closes']}, devises differentes {d['devises_differentes']})")
    if d["avertissement"]:
        print(f"  !! {d['avertissement']}")
