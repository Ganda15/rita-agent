@echo off
REM ===========================================================================
REM  RITA — collecte quotidienne (C1 : "perenniser la collecte")
REM
REM  Lance par le Planificateur de taches Windows, chaque soir a 19h00.
REM  Voir scripts/README-planification.md pour la commande d'installation.
REM
REM  Pourquoi un .cmd et pas un .ps1 : PowerShell refuse d'executer un script
REM  non signe tant que la strategie d'execution n'a pas ete modifiee. Un .cmd
REM  ne demande aucun changement de configuration systeme.
REM ===========================================================================

setlocal

set RACINE=D:\KandaWork\RITA_PROJECT\rita-agent
set PYTHON=C:\Python314\python.exe

cd /d "%RACINE%" || exit /b 1
if not exist "logs" mkdir "logs"

REM Horodatage ISO, independant du format regional de Windows.
for /f %%d in ('%PYTHON% -c "import datetime;print(datetime.date.today().isoformat())"') do set JOUR=%%d

echo. >> "logs\collecte-%JOUR%.log"
echo ==================== %DATE% %TIME% ==================== >> "logs\collecte-%JOUR%.log"

REM Les 5 etapes. Une etape en echec n'interrompt pas les suivantes : c'est le
REM comportement voulu du pipeline (un COMMIT par etape).
REM
REM  "indexation" ajoutee le 02/09/2026. Le defaut qu'elle corrige, mesure ce
REM  jour-la : 309 documents indexes pour 439 articles en base. On collectait
REM  chaque soir et on ne reindexait JAMAIS — le RAG cherchait donc dans un
REM  corpus perime d'un peu plus chaque jour, en silence.
REM
REM  Elle vient EN DERNIER : elle doit indexer ce que rss et scraping viennent
REM  d'ecrire, pas l'etat d'avant.
REM
REM  Historique du runtime (a lire comme des FAITS DATES, pas une conclusion) :
REM   - 02/09/2026 : sur ce poste, Smart App Control refusait de charger cygrpc
REM     (roue cp314 sans reputation) -> chromadb ne s'importait pas -> l'etape
REM     etait ATTENDUE EN ECHEC chaque soir, visiblement, par choix : une erreur
REM     au journal vaut mieux qu'une peremption silencieuse.
REM   - 04, 05 et 06/09/2026 : MESURE OK. "Etapes reussies : 5/5", code 0,
REM     indexation 502, 538 puis 566 documents ; base = index verifie le 06/09.
REM     La roue a manifestement acquis sa reputation dans le cloud Microsoft.
REM  Une reputation SAC peut redescendre : le plan de repli (Python 3.13 a cote,
REM  ou lancer cette etape dans Docker) est CONSERVE, pas supprime. Si une ligne
REM  "!! indexation ECHEC : ImportError: DLL load failed..." reapparait au
REM  journal, c'est ce signal-la, et c'est le repli qui s'applique.
"%PYTHON%" -X utf8 -m pipelines.ingest --etapes ecb,cotations,rss,scraping,indexation >> "logs\collecte-%JOUR%.log" 2>&1
set CODE=%ERRORLEVEL%

echo Code de sortie : %CODE% >> "logs\collecte-%JOUR%.log"
endlocal & exit /b %CODE%
