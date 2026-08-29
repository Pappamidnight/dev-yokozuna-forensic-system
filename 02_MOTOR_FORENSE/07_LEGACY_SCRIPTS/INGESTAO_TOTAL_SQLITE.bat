@echo off
REM ==============================================================================
REM INGESTAO TOTAL FORENSE PARA BASE DE DADOS SQLITE UNIFICADA
REM ==============================================================================
TITLE Ingestao Total Forense SQLite - Dev Yokozuna

set DEV_ROOT=C:\Users\Yokozuna\Dev
set PYTHON_SCRIPT=%DEV_ROOT%\AI\skills\mcp-fs-pydantic-org\scripts\ingest_all_to_sqlite.py

echo ==============================================================================
echo  INICIANDO INGESTAO COMPLETA DE EVIDENCIAS NA BASE SQLITE UNIFICADA
echo ==============================================================================
python "%PYTHON_SCRIPT%"

echo.
echo Processamento concluido.
pause
