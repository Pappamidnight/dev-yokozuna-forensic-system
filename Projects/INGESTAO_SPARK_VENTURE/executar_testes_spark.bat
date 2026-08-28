@echo off
REM ==============================================================================
REM executar_testes_spark.bat - Testes Unitarios e Validacao de INGESTAO_SPARK_VENTURE
REM ==============================================================================
TITLE Testes - INGESTAO_SPARK_VENTURE

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

cls
echo ==============================================================================
echo       TESTES AUTOMATIZADOS E VALIDACAO: INGESTAO_SPARK_VENTURE
echo ==============================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_EXE=python
) else (
    set PY_EXE="C:\Users\Yokozuna\AppData\Local\Programs\Python\Python312\python.exe"
)

echo [1/1] Executando testes unitarios do classificador heuristico e Pydantic v2...
%PY_EXE% -m unittest discover -s "%PROJECT_DIR%tests" -p "test_*.py"

echo.
pause
