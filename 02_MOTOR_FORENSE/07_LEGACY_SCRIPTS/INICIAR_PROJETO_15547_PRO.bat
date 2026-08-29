@echo off
REM ==============================================================================
REM INICIAR_PROJETO_15547_PRO.bat - Launcher Centralizado do Projeto INGESTAO_15547_PRO
REM Valida Python, Ambiente, PATH, e disponibiliza menu completo
REM ==============================================================================
TITLE Fabrica Multiagente INGESTAO_15547_PRO - Dev Yokozuna

set DEV_ROOT=C:\Users\Yokozuna\Dev
set PROJ_DIR=%DEV_ROOT%\Projects\INGESTAO_15547_PRO

cd /d "%DEV_ROOT%"

:MENU
cls
echo ==============================================================================
echo       FABRICA MULTIAGENTE DETERMINISTICA: INGESTAO_15547_PRO (DEV)
echo ==============================================================================
echo  Processo   : 15547/26.0T8LSB (Juizo Central Civel de Lisboa)
echo  Diretorio  : %PROJ_DIR%
echo  Status     : 100%% Validado com Frozen Judge, Judge Auditor e Graphify
echo ==============================================================================
echo.
echo  1. Iniciar Sessao de 15 Minutos com Watchdog (Automacao Completa)
echo  2. Executar Ciclo de Ingestao Direto (One-Shot)
echo  3. Executar Testes Unitarios e Avaliacao contra Golden Dataset
echo  4. Abrir Painel Visual Interativo (HTML)
echo  5. Abrir Relatorio Forense Completo (Markdown)
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
call "%PROJ_DIR%\start_fabrica_15min.bat"
goto MENU

:RUN_INGESTAO
cls
call "%PROJ_DIR%\executar_ingestao.bat"
goto MENU

:RUN_TESTS
cls
call "%PROJ_DIR%\executar_testes.bat"
goto MENU

:OPEN_HTML
start "" "%PROJ_DIR%\outputs\html\PAINEL_15547_PRO.html"
goto MENU

:OPEN_MD
start notepad "%PROJ_DIR%\outputs\markdown\RELATORIO_15547_PRO.md"
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
