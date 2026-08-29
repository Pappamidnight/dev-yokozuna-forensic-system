@echo off
REM ==============================================================================
REM INICIAR_PROJETO_WIKI.bat - Launcher Centralizado da LLM Knowledge Wiki
REM ==============================================================================
TITLE LLM Knowledge Wiki - Dev Yokozuna

set DEV_ROOT=C:\Users\Yokozuna\Dev
set PROJ_DIR=%DEV_ROOT%\Projects\LLM_WIKI_VAULT

cd /d "%DEV_ROOT%"

:MENU
cls
echo ==============================================================================
echo       LLM KNOWLEDGE WIKI FORENSE E SOCIETARIA (VAULT ESTRUTURADO)
echo ==============================================================================
echo  Vault     : %PROJ_DIR%\vault\
echo  Site HTML : %PROJ_DIR%\site\index.html
echo ==============================================================================
echo.
echo  1. Compilar Artigos e Gerar Portal Wiki HTML
echo  2. Abrir Portal Wiki no Navegador
echo  3. Abrir Diretorio do Vault (Markdown)
echo  4. Sair
echo.
echo ==============================================================================
set /p OPTION="Selecione uma opcao (1-4): "

if "%OPTION%"=="1" goto RUN_COMPILE
if "%OPTION%"=="2" goto OPEN_SITE
if "%OPTION%"=="3" goto OPEN_VAULT
if "%OPTION%"=="4" goto END

echo Opcao invalida.
pause
goto MENU

:RUN_COMPILE
cls
call "%PROJ_DIR%\compilar_wiki.bat"
goto MENU

:OPEN_SITE
start "" "%PROJ_DIR%\site\index.html"
goto MENU

:OPEN_VAULT
start explorer "%PROJ_DIR%\vault"
goto MENU

:END
echo [INFO] Launcher encerrado.
exit /b 0
