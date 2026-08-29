@echo off
chcp 65001 > nul
title CONTROLO DE QUALIDADE E HIGIENIZAÇÃO FORENSE - DEV YOKOZUNA
cls
echo ===============================================================================
echo   CONTROLO DE QUALIDADE, LEDGER DE VALIDAÇÃO E HIGIENIZAÇÃO FORENSE
echo   Máquina de Estados: Ingestão -> Validação -> Quarentena/Aprovação -> Resultados
echo ===============================================================================
echo.
python "C:\Users\Yokozuna\Dev\02_MOTOR_FORENSE\08_VALIDADORES\controlo_qualidade_higienizacao.py"
echo.
echo A abrir Relatório de Higienização...
start "" "C:\Users\Yokozuna\Dev\04_CONTROLO_E_QUALIDADE\hygiene_report.md"
echo.
pause
