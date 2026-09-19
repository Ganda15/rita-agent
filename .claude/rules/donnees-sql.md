---
paths:
  - "db/**"
  - "api/**"
  - "pipelines/**"
  - "indicateurs/**"
---

# Données et SQL — règles quand on lit ou écrit du code qui touche la base

- **Lire `db/schema.sql` avant d'écrire une requête.** Ne jamais inventer une colonne, une table ou une vue.
  Si un nom manque, le dire, ne pas deviner.
- **Requêtes paramétrées**, jamais de SQL construit par concaténation de chaînes (OWASP A03).
- **Écriture en base** : uniquement par `db/importer.py` et `pipelines/ingest.py`. Un script neuf qui écrit
  en base est une décision, pas un raccourci.
- **PostgreSQL local sur le port 5433** ; la chaîne de connexion vient de `.env`, jamais du code.
- **Données personnelles** : vérifier `db/RGPD-registre-des-traitements.md` avant d'ajouter une colonne
  qui décrit une personne ; la purge est `db/rgpd_purge.py`.
- **Les vues d'indicateurs** (`db/indicateurs*.sql`) suivent la spec `docs/indicateurs/CONCEPTION.md` :
  111 valeurs, pas 135 ; Sharpe écarté. Un indicateur nouveau = spec d'abord.
