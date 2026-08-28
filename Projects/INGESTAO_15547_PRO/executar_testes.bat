@echo off
REM ==============================================================================
REM executar_testes.bat - Testes Unitarios e Evals de INGESTAO_15547_PRO
REM ==============================================================================
TITLE Testes e Avaliacao - INGESTAO_15547_PRO

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

cls
echo ==============================================================================
echo       TESTES AUTOMATIZADOS E EVALUATIONS: INGESTAO_15547_PRO
echo ==============================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_EXE=python
) else (
    set PY_EXE="C:\Users\Yokozuna\AppData\Local\Programs\Python\Python312\python.exe"
)

echo [1/2] Executando testes unitarios...
%PY_EXE% -m unittest discover -s "%PROJECT_DIR%tests" -p "test_*.py"

echo.
echo [2/2] Executando pipeline de avaliacao contra Golden Dataset...
%PY_EXE% "%PROJECT_DIR%evals\run_evals.py" --root "%PROJECT_DIR%."

echo.
pause
