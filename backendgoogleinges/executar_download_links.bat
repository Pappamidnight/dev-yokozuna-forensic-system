@echo off
REM ==============================================================================
REM executar_download_links.bat - Descarregar ficheiros a partir de links.txt
REM ==============================================================================
TITLE Download Google Docs / Drive por Links - YKF

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

cls
echo ==============================================================================
echo        DESCARREGAMENTO DIRETO A PARTIR DE LINKS.TXT (200+ RECURSOS)
echo ==============================================================================
echo  Ficheiro de Links : %SCRIPT_DIR%links.txt
echo  Destino           : %SCRIPT_DIR%data\raw\google_links
echo ==============================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_EXE=python
) else (
    set PY_EXE="C:\Users\Yokozuna\AppData\Local\Programs\Python\Python312\python.exe"
)

%PY_EXE% "%SCRIPT_DIR%download_from_links.py"

echo.
echo ==============================================================================
echo A processar e organizar cronologicamente...
echo ==============================================================================
%PY_EXE% "%SCRIPT_DIR%processar_dados.py"

echo.
pause
