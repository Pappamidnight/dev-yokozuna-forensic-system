@echo off
REM ==============================================================================
REM executar_ingestao_google.bat - EXTRACAO TOTAL (Google Drive + Gmail)
REM ==============================================================================
TITLE Ingestao Total Google Cloud (Drive Completo & Gmail Completo) - YKF

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

cls
echo ==============================================================================
echo        EXTRACAO E SINCRONIZACAO TOTAL: GOOGLE DRIVE E GMAIL
echo ==============================================================================
echo  Google Drive : Todas as pastas da raiz recursivamente (Processos, Provas, etc.)
echo  Gmail        : Todas as labels, mensagens e anexos (PDFs, Chats WhatsApp, etc.)
echo  Destino      : %SCRIPT_DIR%data\raw
echo ==============================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_EXE=python
) else (
    set PY_EXE="C:\Users\Yokozuna\AppData\Local\Programs\Python\Python312\python.exe"
)

%PY_EXE% "%SCRIPT_DIR%google_ingest.py"

echo.
echo ==============================================================================
echo Sincronizacao concluida!
echo Manifesto gerado em: data\raw\_index\FULL_GOOGLE_INGEST_MANIFEST.json
echo ==============================================================================
pause
