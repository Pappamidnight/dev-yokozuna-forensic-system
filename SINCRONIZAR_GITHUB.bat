@echo off
REM ==============================================================================
REM SINCRONIZAR_GITHUB.bat - Sincronizacao de Versoes e Tags com o GitHub
REM Repositorio: @Pappamidnight / dev-yokozuna-forensic-system
REM ==============================================================================
TITLE Sincronizacao GitHub - Dev Yokozuna

set DEV_ROOT=%~dp0
cd /d "%DEV_ROOT%"

cls
echo ==============================================================================
echo       SINCRONIZADOR DE VERSOES E TAGS GITHUB (DEV YOKOZUNA)
echo ==============================================================================
echo  Conta GitHub : @Pappamidnight
echo  Tags Locais  : v1.0.0, v2.0.0, v2.5.0, v3.0.0
echo ==============================================================================
echo.
echo  1. Efetuar Push de Main e Todas as Tags para o GitHub
echo  2. Verificar Estado do Repositorio Git Local (git status / log)
echo  3. Listar Versoes e Tags (git tag -n)
echo  4. Reconfigurar URL do Remote Origin
echo  5. Sair
echo.
echo ==============================================================================
set /p OPTION="Selecione uma opcao (1-5): "

if "%OPTION%"=="1" goto PUSH_ALL
if "%OPTION%"=="2" goto GIT_STATUS
if "%OPTION%"=="3" goto LIST_TAGS
if "%OPTION%"=="4" goto CONFIG_REMOTE
if "%OPTION%"=="5" goto END

echo Opcao invalida.
pause
exit /b 1

:PUSH_ALL
cls
echo [INFO] A efetuar push da branch main para o GitHub...
git push -u origin main
echo.
echo [INFO] A efetuar push das tags de versao (v1.0.0, v2.0.0, v2.5.0, v3.0.0)...
git push origin --tags
echo.
pause
exit /b 0

:GIT_STATUS
cls
echo [INFO] Estado do Repositorio Git:
git status
echo.
echo [INFO] Ultimos Commits:
git log -n 5 --oneline --decorate
echo.
pause
exit /b 0

:LIST_TAGS
cls
echo [INFO] Versoes e Tags Registadas:
git tag -n
echo.
pause
exit /b 0

:CONFIG_REMOTE
cls
set /p REPO_NAME="Digite o nome do repositorio (ex: dev-yokozuna-forensic-system ou courses): "
git remote remove origin
git remote add origin https://github.com/Pappamidnight/%REPO_NAME%.git
echo [SUCESSO] Remote origin atualizado para: https://github.com/Pappamidnight/%REPO_NAME%
pause
exit /b 0

:END
exit /b 0
