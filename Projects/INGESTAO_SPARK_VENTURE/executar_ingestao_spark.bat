@echo off
REM ==============================================================================
REM executar_ingestao_spark.bat - Execucao Direta do Pipeline INGESTAO_SPARK_VENTURE
REM ==============================================================================
TITLE Ingestao Deterministica - INGESTAO_SPARK_VENTURE

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

cls
echo ==============================================================================
echo       EXECUCAO DIRETA DO PIPELINE: INGESTAO_SPARK_VENTURE
echo ==============================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_EXE=python
) else (
    set PY_EXE="C:\Users\Yokozuna\AppData\Local\Programs\Python\Python312\python.exe"
)

%PY_EXE% "%PROJECT_DIR%ingestao_spark.py" --root "%PROJECT_DIR%."

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha na execucao do pipeline Spark.
    pause
    exit /b 1
)

echo.
echo [SUCESSO] Pipeline Spark concluido com exito.
echo - Relatorio Markdown : %PROJECT_DIR%outputs\markdown\RELATORIO_SPARK_VENTURE.md
echo - Painel HTML        : %PROJECT_DIR%outputs\html\PAINEL_SPARK_VENTURE.html
echo - Dados JSONL        : %PROJECT_DIR%outputs\jsonl\
echo - Grafo Societario   : %PROJECT_DIR%outputs\graph\
echo.
pause
