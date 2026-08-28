@echo off
REM ==============================================================================
REM start_fabrica_spark_15min.bat - Fabrica Multiagente INGESTAO_SPARK_VENTURE
REM Sessao de 15 Minutos com Classificador Heuristico, Frozen Judge e Grafo
REM ==============================================================================
TITLE Fabrica Multiagente INGESTAO_SPARK_VENTURE (15 Minutos)

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

cls
echo ==============================================================================
echo       FABRICA MULTIAGENTE DETERMINISTICA: INGESTAO_SPARK_VENTURE
echo ==============================================================================
echo  Dominio    : Entidades Societarias, SCR, Fundos CMVM e Holdings
echo  Diretorio  : %PROJECT_DIR%
echo  Duracao    : 15 Minutos (900s)
echo ==============================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_EXE=python
) else (
    set PY_EXE="C:\Users\Yokozuna\AppData\Local\Programs\Python\Python312\python.exe"
)

%PY_EXE% "%PROJECT_DIR%ingestao_spark.py" --root "%PROJECT_DIR%."

echo.
echo [INFO] A sincronizar outputs para OUTPUT_CENTRALIZADO...
%PY_EXE% -c "import shutil, os; central='C:\\Users\\Yokozuna\\Dev\\OUTPUT_CENTRALIZADO'; [shutil.copy2(os.path.join(r, f), os.path.join(central, '02_DADOS_ESTRUTURADOS', f)) for r, d, files in os.walk(r'%PROJECT_DIR%outputs\jsonl') for f in files if f.endswith('.jsonl')]"

echo.
pause
