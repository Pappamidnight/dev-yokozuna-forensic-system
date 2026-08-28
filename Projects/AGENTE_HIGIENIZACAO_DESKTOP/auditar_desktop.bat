@echo off
REM ==============================================================================
REM auditar_desktop.bat - Auditoria e Higienizacao Deterministica do Desktop
REM ==============================================================================
TITLE Auditoria do Desktop - Dev Yokozuna

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

cls
echo ==============================================================================
echo       AGENTE DE AUDITORIA E HIGIENIZACAO DO DESKTOP (READ-ONLY)
echo ==============================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_EXE=python
) else (
    set PY_EXE="C:\Users\Yokozuna\AppData\Local\Programs\Python\Python312\python.exe"
)

%PY_EXE% "%PROJECT_DIR%auditar_desktop.py"

echo.
pause
