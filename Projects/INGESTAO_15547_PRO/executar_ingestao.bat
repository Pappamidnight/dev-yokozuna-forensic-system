@echo off
REM ==============================================================================
REM executar_ingestao.bat - Execucao Direta do Pipeline INGESTAO_15547_PRO
REM ==============================================================================
TITLE Ingestao Deterministica - INGESTAO_15547_PRO

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

cls
echo ==============================================================================
echo       EXECUCAO DIRETA DO PIPELINE: INGESTAO_15547_PRO
echo ==============================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_EXE=python
) else (
    set PY_EXE="C:\Users\Yokozuna\AppData\Local\Programs\Python\Python312\python.exe"
)

%PY_EXE% "%PROJECT_DIR%ingestao.py" --root "%PROJECT_DIR%."

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha na execucao do pipeline de ingestao.
    pause
    exit /b 1
)

echo.
echo [SUCESSO] Pipeline concluido com exito.
echo - Relatorio Markdown : %PROJECT_DIR%outputs\markdown\RELATORIO_15547_PRO.md
echo - Painel HTML        : %PROJECT_DIR%outputs\html\PAINEL_15547_PRO.html
echo - Dados JSONL        : %PROJECT_DIR%outputs\jsonl\
echo - Grafo de Nós/Edges : %PROJECT_DIR%outputs\graph\
echo.
pause
