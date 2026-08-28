@echo off
REM ==============================================================================
REM compilar_wiki.bat - Compilador da LLM Knowledge Wiki
REM ==============================================================================
TITLE Compilador Wiki - LLM_WIKI_VAULT

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

cls
echo ==============================================================================
echo       COMPILADOR DA LLM KNOWLEDGE WIKI FORENSE E SOCIETARIA
echo ==============================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_EXE=python
) else (
    set PY_EXE="C:\Users\Yokozuna\AppData\Local\Programs\Python\Python312\python.exe"
)

%PY_EXE% "%PROJECT_DIR%wiki_generator.py"

echo.
pause
