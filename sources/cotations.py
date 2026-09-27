"""Source cotations — rafraîchissement quotidien des cours (C1 : service web).

Type de source C1 : **service web**. Complète `bigdata/build_parquet.py`, qui construit
l'archive de 10 ans une fois pour toutes ; ce module-ci maintient la base **à jour**.

C1 demande de « **pérenniser** la collecte ». Un script lancé une fois ne pérennise rien :
il faut un rafraîchissement incrémental, rejouable sans dégât.

## Trois faits vérifiés le 2026-08-03, et non supposés

1. **L'archive est en cours AJUSTÉS.** Mesuré sur MC.PA au 2016-08-01 : archive 125,10 ·
   yfinance brut 152,90 · yfinance ajusté 127,94. Insérer des cours bruts créerait une
   cassure de 22 % dans la série. On utilise donc `history()`, comme `build_parquet.py`.

2. **Les dates de l'archive sont en UTC à 22:00** — soit minuit à Paris. `2026-07-28
   22:00+00:00` désigne la séance du **29 juillet**. Sans conversion vers Europe/Paris,
   on décale tout d'un jour et on compare des séances différentes.

3. **La dernière séance de l'archive peut être incomplète.** Au 2026-07-29, l'archive dit
   466,80 et yfinance 467,95 (+0,25 %) : la ligne a été capturée **avant la clôture**.
   D'où `DEPUIS_INCLUSIF` — on re-télécharge la dernière séance connue pour l'écraser,
   au lieu de repartir du lendemain.
"""
from __future__ import annotations

from datetime import date, timedelta

# La dernière séance connue est re-téléchargée, pas seulement les suivantes : voir §3.
DEPUIS_INCLUSIF = True

# Les bornes que la base refusera de toute façon (contraintes CHECK de `cotation`).
# Filtrer ici évite de faire échouer un lot entier pour une ligne aberrante.
def _ligne_valide(o: float, h: float, b: float, c: float, v: float) -> bool:
    # ⚠️ Deux formes d'absence, pas une seule.
    #
    #   NaN  -> `x == x` est FAUX. C'est ce que rend yfinance pour un jour non coté.
    #   None -> `x == x` est VRAI. C'est ce qu'il rend pour une valeur RADIÉE.
    #
    # Le test `x == x` seul laissait donc passer les None, et la comparaison
    # `c > 0` levait ensuite `TypeError: '>' not supported between instances of
    # 'NoneType' and 'int'`. Mesuré le 18/08/2026 sur ZC.PA (Zodiac Aerospace,
    # radiée en 2018) : l'exception remontait jusqu'à `etape_cotations`, où le
    # `except Exception` faisait perdre **tout le groupe** de tickers partageant
    # cette date de dernière séance — pas seulement le ticker fautif.
    if any(x is None for x in (o, h, b, c, v)):
        return False
    return (
        all(x == x for x in (o, h, b, c, v))   # x != x est vrai pour NaN
        and c > 0 and o > 0
        and h >= b
        and v >= 0
    )


def fetch_cotations(tickers: list[str], depuis: date) -> list[dict]:
    """Télécharge les séances de `tickers` à partir de `depuis` incluse.

    Args:
        tickers: codes Yahoo, ex. ['MC.PA', 'SLB'].
        depuis: première séance voulue. Les jours non ouvrés sont simplement absents.

    Returns:
        Liste de `{ticker, date_seance, ouverture, haut, bas, cloture, volume}`,
        `date_seance` étant un `datetime.date` **en heure de Paris**.

    Raises:
        ValueError: si `tickers` est vide.
    """
    if not tickers:
        raise ValueError("Aucun ticker demandé.")

    import yfinance as yf

    # yfinance exclut la borne de fin : +1 jour pour inclure aujourd'hui.
    donnees = yf.download(
        tickers,
        start=depuis.isoformat(),
        end=(date.today() + timedelta(days=1)).isoformat(),
        interval="1d",
        auto_adjust=True,        # cours ajustés — cohérent avec l'archive (§1)
        group_by="ticker",
        progress=False,
        threads=True,
    )
    if donnees is None or donnees.empty:
        return []

    import pandas as pd

    from sources.marches import facteur_prix

    # 27/09/2026 (#50) : yfinance imbrique les colonnes (ticker, champ) MÊME pour un seul
    # ticker. L'ancien code lisait « à plat » dès qu'il n'y avait qu'un ticker : chaque
    # ligne était écartée, sans erreur. HSBA.L, seule dans son groupe après un férié à
    # Londres (31/08), n'a plus été alimentée pendant un mois. On décide donc sur la FORME
    # des colonnes, pas sur le nombre de tickers.
    imbrique = isinstance(donnees.columns, pd.MultiIndex)

    lignes: list[dict] = []
    for ticker in tickers:
        try:
            sous = donnees[ticker] if imbrique else donnees
        except KeyError:
            continue
        # Londres cote en pence : 1 512,2 GBp = 15,122 GBP (#47). Le volume ne change pas.
        facteur = facteur_prix(ticker)

        for horodatage, r in sous.iterrows():
            o, h, b, c, v = (r.get("Open"), r.get("High"),
                             r.get("Low"), r.get("Close"), r.get("Volume"))
            if not _ligne_valide(o, h, b, c, v):
                continue
            # L'index yfinance est déjà localisé sur la place de cotation.
            lignes.append({
                "ticker": ticker,
                "date_seance": horodatage.date(),
                "ouverture": round(float(o) * facteur, 4),
                "haut": round(float(h) * facteur, 4),
                "bas": round(float(b) * facteur, 4),
                "cloture": round(float(c) * facteur, 4),
                "volume": int(v),
            })
    return lignes
