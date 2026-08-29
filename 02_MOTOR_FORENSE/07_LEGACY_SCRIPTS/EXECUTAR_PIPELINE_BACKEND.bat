@echo off
chcp 65001 > nul
title PIPELINE MASTER BACKEND FORENSE - DEV YOKOZUNA
cls
echo ===============================================================================
echo   SISTEMA DETERMINISTICO - PIPELINE BACKEND FORENSE MASTER
echo   (Orquestracao dos 4 Processos Judiciais, SQLite e Modelos Pydantic v2)
echo ===============================================================================
echo.
python "C:\Users\Yokozuna\Dev\Backend\master_forensic_backend.py" --run
echo.
echo ===============================================================================
pause
