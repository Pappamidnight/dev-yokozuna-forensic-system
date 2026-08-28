@echo off
REM ==============================================================================
REM INICIAR_PROJETO_SPARK.bat - Launcher Centralizado do Projeto INGESTAO_SPARK_VENTURE
REM Ingestao de Entidades Societarias, SCR, Fundos CMVM e Holdings
REM ==============================================================================
TITLE Fabrica Multiagente INGESTAO_SPARK_VENTURE - Dev Yokozuna

set DEV_ROOT=C:\Users\Yokozuna\Dev
set PROJ_DIR=%DEV_ROOT%\Projects\INGESTAO_SPARK_VENTURE

cd /d "%DEV_ROOT%"

:MENU
cls
echo ==============================================================================
echo       FABRICA MULTIAGENTE DETERMINISTICA: GRUPO SPARK / VENTURE PARTNERS
echo ==============================================================================
echo  Dominio    : Sociedades de Capital de Risco (SCR), Fundos CMVM e Holdings
echo  Diretorio  : %PROJ_DIR%
echo  Status     : Classificador Heuristico + Pydantic v2 + Frozen Judge Societario
echo ==============================================================================
echo.
echo  1. Iniciar Sessao de 15 Minutos com Watchdog (Automacao Completa)
echo  2. Executar Ciclo de Ingestao e Classificacao Societaria (One-Shot)
echo  3. Executar Testes Unitarios do Classificador e Schemas Pydantic
echo  4. Abrir Painel Visual Interativo (HTML)
echo  5. Abrir Relatorio Forense Societario (Markdown)
echo  6. Sincronizar Outputs com OUTPUT_CENTRALIZADO
echo  7. Sair
echo.
echo ==============================================================================
set /p OPTION="Selecione uma opcao (1-7): "

if "%OPTION%"=="1" goto RUN_WATCHDOG_15MIN
if "%OPTION%"=="2" goto RUN_INGESTAO
if "%OPTION%"=="3" goto RUN_TESTS
if "%OPTION%"=="4" goto OPEN_HTML
if "%OPTION%"=="5" goto OPEN_MD
if "%OPTION%"=="6" goto RUN_SYNC
if "%OPTION%"=="7" goto END

echo Opcao invalida. Tente novamente.
pause
goto MENU

:RUN_WATCHDOG_15MIN
cls
call "%PROJ_DIR%\start_fabrica_spark_15min.bat"
goto MENU

:RUN_INGESTAO
cls
call "%PROJ_DIR%\executar_ingestao_spark.bat"
goto MENU

:RUN_TESTS
cls
call "%PROJ_DIR%\executar_testes_spark.bat"
goto MENU

:OPEN_HTML
start "" "%PROJ_DIR%\outputs\html\PAINEL_SPARK_VENTURE.html"
goto MENU

:OPEN_MD
start notepad "%PROJ_DIR%\outputs\markdown\RELATORIO_SPARK_VENTURE.md"
goto MENU

:RUN_SYNC
cls
echo [INFO] Sincronizando outputs para OUTPUT_CENTRALIZADO...
python -c "import shutil, os; central='C:\\Users\\Yokozuna\\Dev\\OUTPUT_CENTRALIZADO'; [shutil.copy2(os.path.join(r, f), os.path.join(central, '02_DADOS_ESTRUTURADOS', f)) for r, d, files in os.walk(r'%PROJ_DIR%\\outputs\\jsonl') for f in files if f.endswith('.jsonl')]; [shutil.copy2(os.path.join(r, f), os.path.join(central, '02_DADOS_ESTRUTURADOS', f)) for r, d, files in os.walk(r'%PROJ_DIR%\\outputs\\graph') for f in files if f.endswith('.jsonl')]"
echo [SUCESSO] Sincronizacao concluida.
pause
goto MENU

:END
echo [INFO] Launcher encerrado.
exit /b 0
