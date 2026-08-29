@echo off
chcp 65001 > nul
title SENTINELA-5 FORENSIC CORE - DEV YOKOZUNA
cls
echo ===============================================================================
echo   SISTEMA SENTINELA-5 FORENSIC CORE (ORQUESTRADOR MESTRE)
echo   Certificação de Qualidade 100/100 nos 7 Subsistemas Integrados
echo ===============================================================================
echo.
python "C:\Users\Yokozuna\Dev\02_MOTOR_FORENSE\08_VALIDADORES\sentinela5_dryrun_master.py"
echo.
echo A abrir o Certificado Mestre e o Dashboard de Confronto...
start "" "C:\Users\Yokozuna\Dev\03_RESULTADOS\01_INDICES_E_RELATORIOS\CERTIFICADO_CONFORMIDADE_SENTINELA5.md"
start "" "C:\Users\Yokozuna\Dev\03_RESULTADOS\06_DASHBOARDS_HTML\CONFRONTO_LADO_A_LADO_INTERATIVO.html"
echo.
pause
