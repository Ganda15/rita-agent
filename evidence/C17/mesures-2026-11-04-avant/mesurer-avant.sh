#!/usr/bin/env bash
# Tache 0 de specs/001-refonte-interface/plan.md : la mesure "avant", rejouee avec les outils et reglages du 03/10.
# La cle jetable ne vit que dans ce processus : jamais affichee, jamais ecrite dans un fichier.
set -uo pipefail
LH="C:/Users/kanda/AppData/Local/Temp/claude/89f877c678431dc8/4019b285-c6bd-42b0-b70b-39a1ab706cd9/scratchpad/lh"
DEPOT="D:/KandaWork/RITA_PROJECT/rita-agent"
OUTILS_0310="$DEPOT/evidence/C17/mesures-2026-10-03/outils"
SORTIE="$DEPOT/evidence/C17/mesures-2026-11-04-avant"
PY="C:/Python314/python.exe"
BASE="http://127.0.0.1:8001"

mkdir -p "$SORTIE/entrees" "$SORTIE/outils" "$LH/brut"
cp "$OUTILS_0310"/* "$LH/"            # les scripts a cote de node_modules (resolution des modules)
cp "$OUTILS_0310"/* "$SORTIE/outils/" # le dossier de preuve garde les outils exacts

export LH_CLE="$("$PY" -c "import secrets; print(secrets.token_hex(16))")"
export RITA_API_KEY="$LH_CLE"
export LANGFUSE_TRACING_ENABLED=false
export RESULTATS="$DEPOT/evidence/C7/resultats-2026-10-03.jsonl"

cd "$DEPOT"
date -u +"debut %Y-%m-%dT%H:%M:%SZ"
echo "commit mesure : $(git rev-parse --short HEAD) ; frontend modifie depuis : $(git --no-pager log -1 --format=%h -- frontend)"
"$PY" -m uvicorn api.main:app --host 127.0.0.1 --port 8001 > "$LH/serveur.log" 2>&1 &
PID=$!
trap 'kill $PID 2>/dev/null' EXIT
for i in $(seq 1 60); do
  [ "$(curl -s -o /dev/null -w '%{http_code}' "$BASE/health")" = "200" ] && break
  sleep 1
done
echo "serveur : $(curl -s -o /dev/null -w '%{http_code}' "$BASE/health") apres ${i} s"

# Les pages et les reponses de l'API telles que mesurees (entrees du calcul EcoIndex)
for f in index.html style.css app.js indicateurs.html indicateurs.js briefing.html briefing.js; do cp "frontend/$f" "$SORTIE/entrees/"; done
for r in portefeuille indicateurs-portefeuille fraicheur indicateurs indicateurs-risque; do
  echo "  /donnees/$r : $(curl -s -H "X-API-Key: $LH_CLE" -o "$SORTIE/entrees/donnees_$r.json" -w '%{http_code}' "$BASE/donnees/$r")"
done
echo "  /donnees/valeurs?limite=200 : $(curl -s -H "X-API-Key: $LH_CLE" -o "$SORTIE/entrees/donnees_valeurs_limite_200.json" -w '%{http_code}' "$BASE/donnees/valeurs?limite=200")"

cd "$LH"
echo "=== audit bureau";  node audit-rita.mjs "$SORTIE" bureau  2>&1 | tail -3
echo "=== audit mobile";  node audit-rita.mjs "$SORTIE" mobile  2>&1 | tail -3
echo "=== clavier";       node clavier.mjs "$SORTIE/clavier.json" > "$LH/clavier-sortie.txt" 2>&1; echo "code $?"
echo "=== analyse";       "$PY" -X utf8 analyse-audits.py "$SORTIE" > "$LH/analyse-avant.txt" 2>&1; echo "code $?"
echo "=== ecoindex";      "$PY" -X utf8 calcul-ecoindex.py "$SORTIE/entrees" "$SORTIE" 2>&1
echo "=== environnement"
node -e "const f=require('$SORTIE/flux-briefing-bureau.json'); const e=f.steps[0].lhr.environment; console.log('agent', e.hostUserAgent); console.log('lighthouse', f.steps[0].lhr.lighthouseVersion, '| fetchTime', f.steps[0].lhr.fetchTime)"
echo "node $(node --version)"
# Meme jeu de fichiers que le 03/10 : rapports de bureau gardes, flux JSON et rapports mobiles a cote, hors depot
mv "$SORTIE"/flux-*.json "$SORTIE"/flux-*-mobile.html "$LH/brut/"
date -u +"fin %Y-%m-%dT%H:%M:%SZ"
