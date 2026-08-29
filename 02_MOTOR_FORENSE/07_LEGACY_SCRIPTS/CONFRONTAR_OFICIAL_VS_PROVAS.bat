@echo off
chcp 65001 > nul
title CONFRONTO LADO A LADO: DOCUMENTOS OFICIAIS vs PROVAS FORENSES
cls
echo ===============================================================================
echo   MOTOR DE CONFRONTO FORENSE LADO A LADO - DEV YOKOZUNA
echo   Coluna A: Documentos Oficiais Citius  vs  Coluna B: Provas Materiais Reais
echo ===============================================================================
echo.
python "C:\Users\Yokozuna\Dev\Backend\motor_confronto_lado_a_lado.py"
echo.
echo A abrir Dashboard Interativo Lado a Lado...
start "" "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\01_INDEX_E_RELATORIOS\CONFRONTO_LADO_A_LADO_INTERATIVO.html"
echo.
pause
