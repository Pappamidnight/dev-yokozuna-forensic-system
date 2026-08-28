@echo off
REM ==============================================================================
REM start_fabrica_15min.bat - Fabrica Multiagente INGESTAO_15547_PRO
REM Sessao de 15 Minutos com Watchdog, Frozen Judge e Auditoria de Evals
REM ==============================================================================
TITLE Fabrica Multiagente INGESTAO_15547_PRO (15 Minutos)

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

cls
echo ==============================================================================
echo       FABRICA MULTIAGENTE DETERMINISTICA: INGESTAO_15547_PRO
echo ==============================================================================
echo  Processo   : 15547/26.0T8LSB (Juizo Central Civel de Lisboa)
echo  Diretorio  : %PROJECT_DIR%
echo  Duracao    : 15 Minutos (900s)
echo ==============================================================================
echo.

REM Deteccao automatica do executavel Python
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_EXE=python
) else if exist "C:\Users\Yokozuna\AppData\Local\Programs\Python\Python312\python.exe" (
    set PY_EXE="C:\Users\Yokozuna\AppData\Local\Programs\Python\Python312\python.exe"
) else (
    echo [ERRO] Executavel Python nao encontrado no PATH ou diretorio padrao.
    pause
    exit /b 1
)

%PY_EXE% "%PROJECT_DIR%backend\watchdog_runner.py" --root "%PROJECT_DIR%." --seconds 900 --interval 30

echo.
echo [INFO] A sincronizar outputs para OUTPUT_CENTRALIZADO...
%PY_EXE% -c "import shutil, os; central='C:\\Users\\Yokozuna\\Dev\\OUTPUT_CENTRALIZADO'; [shutil.copy2(os.path.join(r, f), os.path.join(central, '02_DADOS_ESTRUTURADOS', f)) for r, d, files in os.walk(r'%PROJECT_DIR%outputs\jsonl') for f in files if f.endswith('.jsonl')]"

echo.
pause
