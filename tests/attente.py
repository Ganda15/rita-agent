"""Attendre qu'une condition soit vraie dans la page, sans `wait_for_function` (06/11/2026, carte #75, constat S1).

Pourquoi : depuis la politique de contenu `default-src 'self'` (sans `'unsafe-eval'`), Playwright ne peut plus évaluer
le texte d'une condition passé à `wait_for_function` : il le compile avec `eval` dans la page, et le navigateur le refuse
(« Evaluating a string as JavaScript violates the following Content Security Policy directive »). La politique fait son
travail ; c'est l'outil de test qui doit s'adapter, sans la contourner. `page.evaluate` passe par le protocole du
navigateur et n'est pas soumis à la politique : on interroge la même condition, à intervalle court, avec le même délai.
"""
import time


def attendre_que(page, expression: str, timeout: float = 30_000, pas: float = 50) -> None:
    """Interroge `expression` jusqu'à ce qu'elle soit vraie ; même délai par défaut que `wait_for_function` (30 s)."""
    fin = time.monotonic() + timeout / 1000
    while True:
        try:
            if page.evaluate(expression):
                return
        except Exception as erreur:  # noqa: BLE001  (pas d'import de Playwright ici : le job `base` ne l'a pas)
            # Une page qui se recharge détruit son contexte d'exécution : on réessaie, comme `wait_for_function`.
            if "context was destroyed" not in str(erreur) and "navigat" not in str(erreur):
                raise
        if time.monotonic() > fin:
            raise TimeoutError(f"condition non atteinte en {timeout:.0f} ms : {expression}")
        page.wait_for_timeout(pas)
