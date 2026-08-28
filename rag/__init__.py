"""RAG — *Retrieval-Augmented Generation*, génération augmentée par récupération.

Aller **chercher** des passages pertinents dans les actualités collectées avant de
**générer** un briefing, pour que le texte s'appuie sur des sources datées et citables
plutôt que sur la seule mémoire du modèle.

Consigne formateur du 28/08/2026 : le RAG est **obligatoire**, et il doit être avancé.
Plan : `docs/PLAN-RAG-MCP.md`, étapes E2 à E5.

| Module | Étape | Rôle |
|---|---|---|
| `indexation.py` | E2 | construire l'index à partir de la table `article` |
| `recherche.py` | E3 | recherche hybride (dense + lexicale) et refus sans preuve |
"""
