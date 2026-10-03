"""Procédures de tri RGPD — mise en conformité de la base (C4).

Critère C4 : « Les procédures de tri détaillent les traitements de conformité (automatisés
ou non) à appliquer ainsi que leur fréquence d'exécution. »

Ce script **exécute** les procédures automatisables décrites dans
`db/RGPD-registre-des-traitements.md`. Un registre sans script est une déclaration
d'intention ; un script sans registre est une suppression non justifiée. Il faut les deux.

    P1  Purger memory_audit au-delà de 90 jours          hebdomadaire   automatisé
    P2  Supprimer les positions soldées depuis 3 ans     mensuelle      automatisé
    P3  Détecter les doublons de positions               mensuelle      détection seule

⚠️ **Mode simulation par défaut.** Sans `--appliquer`, le script montre ce qu'il
supprimerait et ne supprime rien. Une purge déclenchée par accident est une perte de
données irréversible : le défaut doit être le comportement inoffensif.

P3 ne supprime jamais : deux achats identiques le même jour au même prix sont possibles.
Seul un humain peut trancher — c'est la limite honnête de l'automatisation.

Usage :
    python -m db.rgpd_purge                    # simulation (par defaut)
    python -m db.rgpd_purge --appliquer        # execute reellement
    python -m db.rgpd_purge --dsn "postgresql://..." --appliquer
"""
from __future__ import annotations

import argparse
import logging
import os

import psycopg2

logger = logging.getLogger(__name__)

DSN_DEFAUT = "postgresql://rita:rita_dev_local@localhost:5432/rita"

RETENTION_AUDIT_JOURS = 90      # T2 du registre
RETENTION_MCP_CALLS_JOURS = 90  # T5 du registre (plan 62)
RETENTION_POSITION_ANS = 3      # T1 du registre


# --- P1 -----------------------------------------------------------------------

def p1_purger_audit(cur, appliquer: bool) -> dict:
    """Purge le journal de mémoire des agents au-delà de la durée de conservation.

    Pourquoi 90 jours : au-delà, un log de débogage n'a plus d'utilité, et le champ
    `resume` peut contenir des éléments du portefeuille (ticker détenu, montant).
    """
    cur.execute("""
        SELECT count(*) FROM memory_audit
        WHERE horodatage < now() - INTERVAL '%s days'
    """ % RETENTION_AUDIT_JOURS)
    concernees = cur.fetchone()[0]

    if appliquer and concernees:
        cur.execute("""
            DELETE FROM memory_audit
            WHERE horodatage < now() - INTERVAL '%s days'
        """ % RETENTION_AUDIT_JOURS)

    return {"procedure": "P1", "libelle": f"memory_audit > {RETENTION_AUDIT_JOURS} jours",
            "concernees": concernees, "supprimees": concernees if appliquer else 0}


# --- P6 -----------------------------------------------------------------------

def p6_purger_mcp_calls(cur, appliquer: bool) -> dict:
    """Purge le journal des appels MCP au-delà de la durée de conservation (T5, plan 62).

    Pourquoi 90 jours, les mêmes que T2 : au-delà, un refus ancien n'aide plus un diagnostic ; et
    un journal technique reste une donnée personnelle quand il n'y a qu'un utilisateur.
    """
    cur.execute("""
        SELECT count(*) FROM mcp_calls
        WHERE horodatage < now() - INTERVAL '%s days'
    """ % RETENTION_MCP_CALLS_JOURS)
    concernees = cur.fetchone()[0]

    if appliquer and concernees:
        cur.execute("""
            DELETE FROM mcp_calls
            WHERE horodatage < now() - INTERVAL '%s days'
        """ % RETENTION_MCP_CALLS_JOURS)

    return {"procedure": "P6", "libelle": f"mcp_calls > {RETENTION_MCP_CALLS_JOURS} jours",
            "concernees": concernees, "supprimees": concernees if appliquer else 0}


# --- P2 -----------------------------------------------------------------------

def p2_purger_positions_soldees(cur, appliquer: bool) -> dict:
    """Supprime les positions closes depuis plus de 3 ans (T1 du registre, plan 66).

    Une position close est une ligne dont `date_cloture` a été posée par l'import le jour où elle a
    quitté le CSV. Avant le 03/10/2026, la procédure cherchait `quantite = 0`, que le schéma interdit :
    elle ne trouvait jamais rien. La date de référence est la clôture, pas l'achat.
    """
    cur.execute("""
        SELECT count(*) FROM position
        WHERE date_cloture IS NOT NULL
          AND date_cloture < CURRENT_DATE - INTERVAL '%s years'
    """ % RETENTION_POSITION_ANS)
    concernees = cur.fetchone()[0]

    if appliquer and concernees:
        cur.execute("""
            DELETE FROM position
            WHERE date_cloture IS NOT NULL
              AND date_cloture < CURRENT_DATE - INTERVAL '%s years'
        """ % RETENTION_POSITION_ANS)

    return {"procedure": "P2",
            "libelle": f"positions closes depuis plus de {RETENTION_POSITION_ANS} ans",
            "concernees": concernees, "supprimees": concernees if appliquer else 0}


# P3 (détection des doublons de positions) retirée le 03/10/2026 : l'index unique `uq_position_ligne`
# les refuse à l'écriture (plan 66, D1). Une procédure qui signalait ce que la base interdit n'a plus d'objet.


# --- orchestration ------------------------------------------------------------

def executer(dsn: str, appliquer: bool = False) -> dict:
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            resultats = [p1_purger_audit(cur, appliquer),
                         p2_purger_positions_soldees(cur, appliquer),
                         p6_purger_mcp_calls(cur, appliquer)]
        if appliquer:
            conn.commit()
        else:
            conn.rollback()          # ceinture et bretelles : rien ne persiste

    return {"appliquer": appliquer, "purges": resultats}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parseur = argparse.ArgumentParser(description="Procedures de tri RGPD - RITA")
    parseur.add_argument("--dsn", default=os.getenv("DATABASE_URL", DSN_DEFAUT))
    parseur.add_argument("--appliquer", action="store_true",
                         help="execute reellement les suppressions (defaut : simulation)")
    args = parseur.parse_args()

    r = executer(args.dsn, args.appliquer)

    mode = "EXECUTION REELLE" if r["appliquer"] else "SIMULATION (rien n'est supprime)"
    print("\n" + "=" * 62)
    print(f"PROCEDURES DE TRI RGPD  --  {mode}")
    print("=" * 62)

    for p in r["purges"]:
        verbe = "supprimees" if r["appliquer"] else "seraient supprimees"
        print(f"\n  {p['procedure']} - {p['libelle']}")
        print(f"      {p['concernees']} ligne(s) {verbe}")

    print("\n  P3 retiree le 03/10/2026 : l index unique uq_position_ligne refuse les doublons a l ecriture")

    if not r["appliquer"]:
        print("\n  Pour executer reellement :  python -m db.rgpd_purge --appliquer")
    print()
