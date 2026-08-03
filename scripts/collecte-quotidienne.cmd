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

REM Les 4 etapes. Une etape en echec n'interrompt pas les suivantes : c'est le
REM comportement voulu du pipeline (un COMMIT par etape).
"%PYTHON%" -X utf8 -m pipelines.ingest --etapes ecb,cotations,rss,scraping >> "logs\collecte-%JOUR%.log" 2>&1
set CODE=%ERRORLEVEL%

echo Code de sortie : %CODE% >> "logs\collecte-%JOUR%.log"
endlocal & exit /b %CODE%
