#!/usr/bin/env bash
# Vérifications en lecture après la livraison du 07/11 (aucune clé réelle, aucune écriture).
# Usage : verifier_production.sh            -> en-têtes, compression, port, contrat
#         verifier_production.sh frein      -> le frein des essais de clé (BLOQUE l'adresse du poste 15 minutes)
set -u
SITE="https://178-104-184-125.sslip.io"
date -u +"mesure du %Y-%m-%dT%H:%M:%SZ"

if [ "${1:-}" != "frein" ]; then
  echo "== /health =="
  curl -sS -m 15 "$SITE/health"; echo
  echo "== en-têtes des cinq écrans et de la documentation =="
  for p in / /indicateurs.html /briefing.html /question.html /tableau-de-bord.html /docs; do
    echo "--- $p"
    curl -sS -m 15 -o /dev/null -D - -H "Accept-Encoding: gzip" "$SITE$p" \
      | grep -iE "^HTTP/|^content-security-policy|^strict-transport|^x-content-type|^x-frame|^referrer-policy|^server|^via|^content-encoding" \
      | tr -d '\r'
  done
  echo "== port 8001 de l'extérieur (attendu : 000) =="
  curl -sS -m 10 -o /dev/null -w "%{http_code}\n" http://178.104.184.125:8001/health 2>/dev/null || true
  echo "== version du contrat (attendu : 1.2.0) =="
  curl -sS -m 15 "$SITE/openapi.json" | python -c "import json,sys; print(json.load(sys.stdin)['info']['version'])"
  echo "== consigne de l'écran Question =="
  curl -sS -m 15 "$SITE/question.html" | grep -c 'id="consigne-donnees"'
  exit 0
fi

echo "== frein : 11 fausses clés (attendu : dix 403 puis 429) =="
for i in $(seq -w 1 11); do
  curl -sS -m 15 -o /dev/null -w "%{http_code} " -H "X-API-Key: fausse-cle-de-verification-$i-xxxxxxxx" "$SITE/donnees/valeurs"
done; echo
echo "== même chose avec un X-Forwarded-For inventé à chaque appel (attendu : 429, Caddy remplace l'en-tête) =="
for i in $(seq 1 3); do
  curl -sS -m 15 -o /dev/null -w "%{http_code} " -H "X-Forwarded-For: 203.0.113.$i" \
    -H "X-API-Key: fausse-cle-de-verification-x$i-xxxxxxxx" "$SITE/donnees/valeurs"
done; echo
