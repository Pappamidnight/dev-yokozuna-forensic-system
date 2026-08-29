@echo off
REM ==============================================================================
REM INICIAR_HIGIENIZACAO_DESKTOP.bat - Launcher Centralizado do Agente de Higienizacao
REM ==============================================================================
TITLE Higienizacao Deterministica do Desktop - Dev Yokozuna

set DEV_ROOT=C:\Users\Yokozuna\Dev
set PROJ_DIR=%DEV_ROOT%\Projects\AGENTE_HIGIENIZACAO_DESKTOP

cd /d "%DEV_ROOT%"

:MENU
cls
echo ==============================================================================
echo       AGENTE DETERMINISTICO DE HIGIENIZACAO E AUDITORIA DO DESKTOP
echo ==============================================================================
echo  Desktop Alvo : C:\Users\Yokozuna\Desktop
echo  Modo Padrao  : READ-ONLY / AUDITORIA CRIPTOGRAFICA COM SHA-256
echo ==============================================================================
echo.
echo  1. Executar Auditoria do Desktop (Inventario e Detecao de Duplicados)
echo  2. Abrir Plano Formal de Higienizacao (Markdown)
echo  3. Sair
echo.
echo ==============================================================================
set /p OPTION="Selecione uma opcao (1-3): "

if "%OPTION%"=="1" goto RUN_AUDIT
if "%OPTION%"=="2" goto OPEN_REPORT
if "%OPTION%"=="3" goto END

echo Opcao invalida.
pause
goto MENU

:RUN_AUDIT
cls
call "%PROJ_DIR%\auditar_desktop.bat"
goto MENU

:OPEN_REPORT
start notepad "%PROJ_DIR%\outputs\markdown\PLANO_HIGIENIZACAO_DESKTOP.md"
goto MENU

:END
echo [INFO] Launcher encerrado.
exit /b 0
