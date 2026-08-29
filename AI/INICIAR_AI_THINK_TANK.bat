@echo off
chcp 65001 > nul
title AI THINK TANK & ORQUESTRADOR FORENSE - DEV YOKOZUNA
cls
echo ===============================================================================
echo   AI THINK TANK FORENSE (6 AGENTES CANÓNICOS) - DEV YOKOZUNA
echo   Ingestor Universal, Tabela Mestra CSV, Confrontos e Refinamento
echo ===============================================================================
echo.
python "C:\Users\Yokozuna\Dev\AI\ai_master_orchestrator.py"
echo.
echo A abrir a Síntese Refinada e Dashboard...
start "" "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\01_INDEX_E_RELATORIOS\SINTESE_REFINADA_THINK_TANK.md"
start "" "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\01_INDEX_E_RELATORIOS\CONFRONTO_LADO_A_LADO_INTERATIVO.html"
echo.
pause
