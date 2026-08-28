@echo off
REM ==============================================================================
REM executar_rag.bat - Indexacao e Consulta RAG Forense e Societario
REM ==============================================================================
TITLE Motor RAG Forense e Societario - Dev Yokozuna

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

cls
echo ==============================================================================
echo       MOTOR RAG FORENSE E SOCIETARIO (INDEXACAO E RETRIEVAL)
echo ==============================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_EXE=python
) else (
    set PY_EXE="C:\Users\Yokozuna\AppData\Local\Programs\Python\Python312\python.exe"
)

%PY_EXE% "%PROJECT_DIR%rag_cli.py" --index

echo.
echo [SUCESSO] Indexacao RAG concluida.
echo Relatorio : %PROJECT_DIR%outputs\markdown\RELATORIO_RAG_INDEX.md
echo Base BD   : %PROJECT_DIR%state\rag_index.db
echo.
pause
