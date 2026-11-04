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
    python -m db.importer --positions-seulement      (valeurs et positions : ni cotations ni bornes de cotation)
    python -m db.importer --corrections-seulement    (les seules corrections connues, sur les seules lignes visees)
"""
from __future__ import annotations

import argparse
import csv
import logging
import os
from decimal import Decimal
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

# 04/11/2026 : le nom affiché d'une valeur renommée. L'univers garde les libellés du courtier (« CGG BS »,
# « CGG RGPT »), qui restent des alias du portefeuille ; le nom officiel est celui de la société aujourd'hui.
# CGG s'appelle Viridien depuis 2024 (ses communiqués de juin et juillet 2024 disent « Viridien (ex-CGG) »).
NOMS_OFFICIELS = {"VIRI.PA": "VIRIDIEN"}

# 04/11/2026 (constat d'Era sur l'écran Indicateurs : VIRI.PA en tête à +4 856 %) : une position déjà en base,
# ramenée à l'échelle d'un regroupement d'actions. Les cours de la base sont rétro-ajustés ; un prix de revient
# resté à l'ancienne échelle multiplie le gain par la parité.
# Pourquoi corriger sur place : la réconciliation identifie une ligne par (ticker, PRU, date d'achat). Changer le PRU
# dans le CSV ferait lire la correction comme une vente (l'ancienne ligne close) suivie d'un achat (une ligne neuve).
# Corriger une donnée n'est pas constater une vente. La mise à jour vise la seule ligne exacte d'avant, ouverte, et
# ne joue qu'une fois : rejouée, elle ne trouve plus rien.
# Viridien : 100 actions anciennes pour 1 nouvelle, effectif le 31/07/2024. La position d'exemple est simulée ; les
# rompus (20 anciennes, indemnisées par l'intermédiaire) ne sont pas reconstitués : la position garde la seule action
# entière, au coût des 100 anciennes qu'elle remplace.
REGROUPEMENTS = (
    {"ticker": "VIRI.PA", "date_achat": "2021-10-14", "quantite": Decimal("120"), "pru": Decimal("1.85"),
     "parite": 100, "source": "communiqué Viridien du 31/07/2024, finalisation du regroupement (100 pour 1)"},
)


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
                valeurs[ticker] = {"ticker": ticker, "nom": NOMS_OFFICIELS.get(ticker, nom),
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
        # 04/11/2026 : pandas lit la colonne de partition `annee` comme une catégorie sans ordre : `.max()` levait
        # « Categorical is not ordered » et l'option plantait (les tests simulaient un entier).
        annees = df["annee"].astype(int)
        df = df[annees >= int(annees.max()) - limite_annees + 1]

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


def position_regroupee(quantite: Decimal, pru: Decimal, parite: int) -> tuple[Decimal, Decimal, Decimal]:
    """Une position après un regroupement de `parite` actions anciennes pour 1 nouvelle.

    Rend (actions entières, PRU de l'action nouvelle, rompus en actions anciennes). Le PRU nouveau est le coût des
    `parite` anciennes que l'action remplace. Les rompus sont rendus à part par l'intermédiaire : ils sortent du
    portefeuille, et leur indemnisation n'est pas connue ici.
    """
    entieres = quantite // parite
    if entieres < 1:
        raise ValueError(f"{quantite} actions anciennes pour une parité de {parite} : aucune action nouvelle, tout part "
                         "en rompus (une vraie sortie du portefeuille, que la correction n'invente pas)")
    return entieres, pru * parite, quantite - entieres * parite


def convertir_lignes_d_avant_regroupement(lignes: list[tuple]) -> tuple[list[tuple], int]:
    """Les lignes du CSV qui portent EXACTEMENT la ligne d'avant d'un regroupement connu sont converties, avec un avertissement.

    Pourquoi : la base est corrigée (1 × 185) ; si quelqu'un réimporte l'ancien fichier (120 × 1,85), l'ancienne ligne
    reviendrait et la ligne corrigée, absente du fichier, serait close : une vente inventée. Constaté sur la base de test
    le 04/11/2026. Le périmètre est celui du jeu simulé : la ligne est reconnue par ses quatre champs (ticker, date d'achat,
    quantité, prix de revient) ; une ligne qui s'en approche n'est pas touchée. Une ligne déjà corrigée ne l'est pas deux fois.
    Rend (les lignes, le nombre de lignes converties).
    """
    sorties, converties = [], 0
    for ligne in lignes:
        ticker, quantite, pru, devise, date_achat = ligne
        for r in REGROUPEMENTS:
            if (ticker, str(date_achat), Decimal(str(quantite)), Decimal(str(pru))) == (
                    r["ticker"], r["date_achat"], r["quantite"], r["pru"]):
                nouvelle_quantite, nouveau_pru, _ = position_regroupee(r["quantite"], r["pru"], r["parite"])
                ligne = (ticker, nouvelle_quantite, nouveau_pru, devise, date_achat)
                converties += 1
                logger.warning("ligne du CSV d'avant le regroupement (%s, %s a %s, achat du %s) convertie en %s a %s : "
                               "mettre le CSV a jour", ticker, r["quantite"], r["pru"], date_achat, nouvelle_quantite, nouveau_pru)
                break
        sorties.append(ligne)
    return sorties, converties


def corriger_regroupements(cur) -> int:
    """Applique `REGROUPEMENTS` sur place, avant la réconciliation ; rend le nombre de lignes corrigées.

    Seule la ligne exacte d'avant (ticker, date d'achat, quantité, PRU), encore ouverte, est visée ; si la ligne
    corrigée existe déjà, rien n'est touché (l'index unique la refuserait). Rejouée, la correction ne trouve plus rien.
    """
    corrigees = 0
    for r in REGROUPEMENTS:
        quantite, pru, rompus = position_regroupee(r["quantite"], r["pru"], r["parite"])
        cur.execute(
            "UPDATE position SET quantite = %s, pru = %s, importe_le = now() "
            "WHERE ticker = %s AND date_achat = %s AND quantite = %s AND pru = %s AND date_cloture IS NULL "
            "AND NOT EXISTS (SELECT 1 FROM position p WHERE p.ticker = %s AND p.pru = %s AND p.date_achat = %s) "
            "RETURNING ticker",
            (quantite, pru, r["ticker"], r["date_achat"], r["quantite"], r["pru"], r["ticker"], pru, r["date_achat"]))
        n = len(cur.fetchall() or [])
        if n:
            corrigees += n
            logger.info("position %s du %s : regroupement %s pour 1 applique sur place, %s a %s devient %s a %s "
                        "(%s rompus hors portefeuille ; %s)", r["ticker"], r["date_achat"], r["parite"],
                        r["quantite"], r["pru"], quantite, pru, rompus, r["source"])
    return corrigees


def corriger_noms_officiels(cur) -> int:
    """Applique `NOMS_OFFICIELS` sur place : la seule valeur listée, et seulement si son nom diffère. Rend le nombre de
    valeurs renommées. Ne touche à aucune autre valeur, ni à leurs statuts, notes ou devises."""
    renommees = 0
    for ticker, nom in NOMS_OFFICIELS.items():
        cur.execute("UPDATE valeur SET nom_officiel = %s WHERE ticker = %s AND nom_officiel IS DISTINCT FROM %s RETURNING ticker",
                    (nom, ticker, nom))
        renommees += len(cur.fetchall() or [])
    return renommees


# 04/11/2026 : le garde qui aurait vu Viridien. Une position dont le prix de revient est très loin du cours du jour de
# l'achat est probablement à une autre échelle que les cours (regroupement ou division d'actions non répercuté) : Viridien
# est resté trois mois en tête d'un écran à +4 856 % sans que personne ne le voie. Mesuré le 04/11 : 0,78 à 1,51 pour six
# lignes, 0,029 pour Viridien. Une alerte, pas une preuve : un prix de revient peut cumuler plusieurs achats et des frais.
# Bornes comprises, convention déclarée : un regroupement de 10 pour 1 donne 0,1, de 100 pour 1 donne 0,01.
BORNES_PRU_SUR_COURS = (Decimal("0.2"), Decimal("5"))


def rapport_hors_echelle(pru: Decimal, cloture: Decimal) -> Decimal | None:
    """Le rapport PRU / cours, arrondi à quatre décimales, s'il sort des bornes ; sinon None (aussi sans cours)."""
    if cloture <= 0:
        return None
    rapport = pru / cloture
    bas, haut = BORNES_PRU_SUR_COURS
    return None if bas <= rapport <= haut else rapport.quantize(Decimal("0.0001"))


def controler_prix_de_revient(cur) -> dict:
    """Compare le prix de revient des positions ouvertes au dernier cours à ou avant la date d'achat. Lecture seule.

    Rend {"hors_echelle": [...], "non_controlees": [...]}. Chaque ligne donne la date du cours réellement lu
    (`date_cours`), qui n'est pas forcément la date d'achat (un week-end, un jour férié).
    - Si la devise du prix de revient diffère de celle du cours, le rapport n'est PAS calculé : des bornes larges ne
      rendent pas correcte la comparaison de deux monnaies. La ligne va dans `non_controlees`, avec les deux devises.
    - Une position sans date d'achat, ou achetée avant le premier cours connu, n'est pas jugée.
    """
    cur.execute("""
        SELECT p.ticker, p.date_achat, p.pru, p.devise, v.devise, c.date_seance, c.cloture
        FROM   position p
        JOIN   valeur v ON v.ticker = p.ticker
        JOIN LATERAL (SELECT date_seance, cloture FROM cotation
                      WHERE  ticker = p.ticker AND date_seance <= p.date_achat
                      ORDER  BY date_seance DESC LIMIT 1) c ON TRUE
        WHERE  p.date_cloture IS NULL AND p.date_achat IS NOT NULL
        ORDER  BY p.ticker, p.date_achat
    """)
    controle = {"hors_echelle": [], "non_controlees": []}
    for ticker, date_achat, pru, devise_pru, devise_cours, date_cours, cloture in cur.fetchall():
        ligne = {"ticker": ticker, "date_achat": date_achat, "pru": pru, "date_cours": date_cours, "cloture": cloture}
        if devise_pru != devise_cours:
            controle["non_controlees"].append(dict(ligne, devise_pru=devise_pru, devise_cours=devise_cours))
            continue
        rapport = rapport_hors_echelle(pru, cloture)
        if rapport is not None:
            controle["hors_echelle"].append(dict(ligne, rapport=rapport))
    return controle


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

    bilan = {"lignes": len(lignes), "inserees": 0, "mises_a_jour": 0, "rouvertes": 0, "closes": 0, "corrigees": 0,
             "converties": 0,
             "ignorees": len(ignorees), "devises_differentes": devises_differentes, "avertissement": None}
    if ignorees:
        logger.warning("%d position(s) sans valeur correspondante : %s", len(ignorees), ignorees)
    if not lignes:
        bilan["avertissement"] = ("aucune ligne valide dans le CSV : aucune position close (un fichier "
                                  "deplace ou corrompu ne vend pas un portefeuille)")
        logger.warning(bilan["avertissement"])
        return bilan

    # 04/11/2026 : l'ancien CSV est converti, puis les corrections de regroupement passent AVANT la réconciliation, pour
    # qu'une ligne corrigée ne soit pas lue comme vendue, quel que soit le fichier lu.
    lignes, bilan["converties"] = convertir_lignes_d_avant_regroupement(lignes)
    bilan["corrigees"] = corriger_regroupements(cur)

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


def importer(dsn: str, limite_annees: int | None = None, positions_seulement: bool = False) -> dict:
    """L'import complet : valeurs, cotations, positions, contrôle du prix de revient.

    `positions_seulement` (04/11/2026) : les valeurs et les positions, sans relire le Parquet ni recalculer les dates de
    première et de dernière cotation de toutes les valeurs. Pour corriger une position sans autre effet : l'import
    complet changeait aussi ces dates sur 108 valeurs de la base locale (mesuré), dont l'API lit deux colonnes.
    """
    valeurs, alias = charger_univers()

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            importer_valeurs(cur, valeurs, alias)
            stats = {} if positions_seulement else importer_cotations(cur, limite_annees)
            stats["valeurs"] = len(valeurs)
            stats["alias"] = len(alias)
            positions = importer_positions(cur)
            stats["positions"] = positions["lignes"]
            stats["positions_detail"] = positions
            stats["controle_prix_de_revient"] = controler_prix_de_revient(cur)
            for l in stats["controle_prix_de_revient"]["hors_echelle"]:
                logger.warning("position %s : prix de revient %s, dernier cours a ou avant l'achat du %s (cours du %s) %s, "
                               "rapport %s hors de %s a %s : verifier un regroupement ou une division d'actions non repercute",
                               l["ticker"], l["pru"], l["date_achat"], l["date_cours"], l["cloture"], l["rapport"],
                               *BORNES_PRU_SUR_COURS)
            for l in stats["controle_prix_de_revient"]["non_controlees"]:
                logger.warning("position %s : controle du prix de revient non effectue, devises differentes (PRU en %s, cours en %s)",
                               l["ticker"], l["devise_pru"], l["devise_cours"])
        conn.commit()

    return stats


# --- Le mode le plus étroit : --corrections-seulement (04/11/2026 au soir) -----------------------------------------------
# `--positions-seulement` n'est pas « seulement Viridien » (relecture extérieure du 04/11) : il réécrit les 111 valeurs
# d'après l'univers, insère les alias manquants, rafraîchit `importe_le` de toutes les positions du CSV et clôt celles qui en
# sont absentes. Ce mode n'applique que les corrections connues, écrites ci-dessus (`REGROUPEMENTS`, `NOMS_OFFICIELS`), sur les
# seules lignes qu'elles visent. Aucun CSV ni univers lu, aucune réconciliation : il ne demande aucun fichier de données, et
# peut donc tourner tel quel dans l'image de l'API, où le dossier data/ n'existe pas.
def appliquer_corrections(cur) -> dict:
    """Les corrections connues, puis le contrôle du prix de revient (lecture). Rend le bilan."""
    bilan = {"corrigees": corriger_regroupements(cur), "noms_corriges": corriger_noms_officiels(cur)}
    bilan["controle_prix_de_revient"] = controler_prix_de_revient(cur)
    return bilan


class CorrectionsInattendues(Exception):
    """Le nombre de lignes corrigées n'est pas celui qu'on attendait : tout est annulé, rien n'est validé."""


def importer_corrections(dsn: str, a_blanc: bool = False, attendu: tuple[int, int] | None = None) -> dict:
    """`appliquer_corrections` dans une seule transaction, avec deux portes (relecture du 04/11) :

    - `a_blanc` : la transaction est annulée après le bilan, rien n'est validé (on voit l'effet exact sur la vraie base) ;
    - `attendu` = (positions regroupées, noms corrigés) : si le bilan diffère, tout est annulé et l'erreur le dit. Sans cette
      porte, un importateur valide sans regarder son propre bilan.
    """
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            bilan = appliquer_corrections(cur)
        obtenu = (bilan["corrigees"], bilan["noms_corriges"])
        if attendu is not None and obtenu != tuple(attendu):
            conn.rollback()
            raise CorrectionsInattendues(f"attendu {tuple(attendu)} (positions regroupees, noms corriges), obtenu {obtenu} : "
                                         "tout est annule, rien n'est valide")
        if a_blanc:
            conn.rollback()
            bilan["a_blanc"] = True
        else:
            conn.commit()
    return bilan


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


def lire_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parseur = argparse.ArgumentParser(description="Import RITA -> PostgreSQL")
    parseur.add_argument("--dsn", default=os.getenv("DATABASE_URL", DSN_DEFAUT))
    exclusifs = parseur.add_mutually_exclusive_group()
    exclusifs.add_argument("--limite-annees", type=int, default=None,
                           help="n'importer que les N dernieres annees")
    exclusifs.add_argument("--positions-seulement", action="store_true",
                           help="valeurs et positions seulement : ni cotations ni bornes de cotation")
    exclusifs.add_argument("--corrections-seulement", action="store_true",
                           help="les seules corrections connues (REGROUPEMENTS, NOMS_OFFICIELS) : aucun CSV, aucune reconciliation")
    exclusifs.add_argument("--demo", type=Path, default=None, metavar="DOSSIER",
                           help="remplir une base neuve avec le jeu de demonstration (data/demo)")
    parseur.add_argument("--a-blanc", action="store_true",
                         help="avec --corrections-seulement : appliquer, afficher le bilan, puis tout annuler")
    parseur.add_argument("--attendu-corrigees", type=int, default=None,
                         help="avec --corrections-seulement : nombre de positions regroupees attendu, sinon tout est annule")
    parseur.add_argument("--attendu-noms", type=int, default=None,
                         help="avec --corrections-seulement : nombre de noms officiels corriges attendu, sinon tout est annule")
    args = parseur.parse_args(argv)
    portes = args.a_blanc or args.attendu_corrigees is not None or args.attendu_noms is not None
    if portes and not args.corrections_seulement:
        parseur.error("--a-blanc et --attendu-* ne servent qu'avec --corrections-seulement")
    if (args.attendu_corrigees is None) != (args.attendu_noms is None):
        parseur.error("--attendu-corrigees et --attendu-noms vont ensemble")
    return args


def imprimer_controle(controle: dict) -> None:
    for l in controle["hors_echelle"]:
        print(f"  !! {l['ticker']} : prix de revient {l['pru']} contre un cours de {l['cloture']} (cours du {l['date_cours']}, "
              f"achat du {l['date_achat']}), rapport {l['rapport']} : a verifier, regroupement ou division d'actions non repercute ?")
    for l in controle["non_controlees"]:
        print(f"  .. {l['ticker']} : controle du prix de revient non effectue, devises differentes "
              f"(PRU en {l['devise_pru']}, cours en {l['devise_cours']})")
    if not controle["hors_echelle"]:
        print("Prix de revient    : aucun hors de l'echelle des cours (lignes en devises differentes non comparees)")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = lire_arguments()

    if args.demo:
        print(importer_demo_complet(args.dsn, args.demo))
        raise SystemExit(0)

    if args.corrections_seulement:
        attendu = None if args.attendu_corrigees is None else (args.attendu_corrigees, args.attendu_noms)
        try:
            c = importer_corrections(args.dsn, a_blanc=args.a_blanc, attendu=attendu)
        except CorrectionsInattendues as erreur:
            print(f"\n!! {erreur}")
            raise SystemExit(1)
        print("\n=== CORRECTIONS CIBLEES (--corrections-seulement)"
              + (" : A BLANC, TOUT EST ANNULE, RIEN N'EST VALIDE" if args.a_blanc else "") + " ===")
        print(f"Positions regroupees : {c['corrigees']}   (corrigees sur place ; aucun CSV lu, aucune reconciliation)")
        print(f"Noms officiels       : {c['noms_corriges']}")
        imprimer_controle(c["controle_prix_de_revient"])
        raise SystemExit(0)

    r = importer(args.dsn, args.limite_annees, args.positions_seulement)

    print("\n=== IMPORT POSTGRESQL ===")
    print(f"Valeurs            : {r['valeurs']}")
    print(f"Alias portefeuille : {r['alias']}   (> valeurs = cas CGG resolu)")
    if "lues" in r:
        print(f"Cotations lues     : {r['lues']:,}")
        print(f"  dedoublonnees    : {r['dedoublonnees']:,}")
        print(f"  tentees          : {r['inserees']:,}   (deja presentes ignorees : ON CONFLICT DO NOTHING)")
    else:
        print("Cotations          : non touchees (--positions-seulement)")
    d = r["positions_detail"]
    print(f"Positions          : {r['positions']}  (inserees {d['inserees']}, mises a jour {d['mises_a_jour']}, "
          f"rouvertes {d['rouvertes']}, closes {d['closes']}, corrigees {d['corrigees']}, converties {d['converties']}, "
          f"devises differentes {d['devises_differentes']})")
    if d["avertissement"]:
        print(f"  !! {d['avertissement']}")
    imprimer_controle(r["controle_prix_de_revient"])
