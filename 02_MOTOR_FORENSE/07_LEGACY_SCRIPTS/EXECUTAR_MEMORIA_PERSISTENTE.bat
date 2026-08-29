@echo off
REM ==============================================================================
REM EXECUTAR_MEMORIA_PERSISTENTE.bat - BASE DE DADOS SQLITE E MEMORIA PERSISTENTE
REM Consolida dados PRE-INGESTAO e POS-INGESTAO na BD memoria_forense_unificada.db
REM ==============================================================================
TITLE Memoria Persistente Forense - Dev Yokozuna

set DEV_ROOT=C:\Users\Yokozuna\Dev
set SCRIPT=%DEV_ROOT%\AI\skills\mcp-fs-pydantic-org\scripts\persistent_memory_manager.py

cd /d "%DEV_ROOT%"

cls
echo ==============================================================================
echo       GESTOR DE MEMORIA PERSISTENTE E BASE DE DADOS FORENSE (SQLITE)
echo ==============================================================================
echo  Destino da BD : %DEV_ROOT%\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\memoria_forense_unificada.db
echo  Metodologia   : %DEV_ROOT%\OUTPUT_CENTRALIZADO\01_INDEX_E_RELATORIOS\METODOLOGIA_MEMORIA_PERSISTENTE.md
echo ==============================================================================
echo.

python "%SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao atualizar a memoria persistente.
    pause
    exit /b 1
)

echo.
echo [SUCESSO] Memoria Persistente atualizada com exito na Base de Dados SQLite.
echo.
pause
