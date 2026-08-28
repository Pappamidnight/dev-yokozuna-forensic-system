@echo off
REM ==============================================================================
REM executar_ingestao_google.bat - Sincronizacao de Gmail e Google Drive
REM ==============================================================================
TITLE Ingestao Google Cloud (Gmail & Drive) - YKF

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

cls
echo ==============================================================================
echo            INGESTAO GOOGLE CLOUD: GMAIL (LABELS) & GOOGLE DRIVE
echo ==============================================================================
echo  Labels Gmail : 3719/25.0T8LSB, ANALISTA, CENTENARIO, Finpartner
echo  Pastas Drive : 1 TRIBUNAL, MAPA PROVAS, SPARK 2926, 02 Assuntos Juridicos...
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
echo Sincronizacao concluida. Ficheiros e manifestos gravados em data/raw/
echo ==============================================================================
pause
