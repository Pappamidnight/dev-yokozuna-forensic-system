@echo off
REM ==============================================================================
REM INSTALAR_WSL2_UBUNTU_KALI.bat - Gestor de Instalacao WSL2 (Ubuntu / Kali Linux)
REM Configura o ambiente Linux integrado com o workspace C:\Users\Yokozuna\Dev
REM ==============================================================================
TITLE Configurador WSL2 - Ubuntu & Kali Linux - Dev Yokozuna

cls
echo ==============================================================================
echo       CONFIGURADOR E INSTALADOR WSL2 (UBUNTU / KALI LINUX)
echo ==============================================================================
echo  Workspace Local : C:\Users\Yokozuna\Dev
echo  Ponto de Montagem Linux : /mnt/c/Users/Yokozuna/Dev
echo ==============================================================================
echo.
echo  1. Instalar Ubuntu (WSL2 Recomendado)
echo  2. Instalar Kali Linux (WSL2 Forense)
echo  3. Listar Distros Instaladas no Sistema
echo  4. Atualizar Kernel WSL2 (wsl --update)
echo  5. Sair
echo.
echo ==============================================================================
set /p OPTION="Selecione uma opcao (1-5): "

if "%OPTION%"=="1" goto INSTALL_UBUNTU
if "%OPTION%"=="2" goto INSTALL_KALI
if "%OPTION%"=="3" goto LIST_DISTROS
if "%OPTION%"=="4" goto UPDATE_WSL
if "%OPTION%"=="5" goto END

echo Opcao invalida.
pause
exit /b 1

:INSTALL_UBUNTU
cls
echo [INFO] Iniciando instalacao do Ubuntu no WSL2...
wsl.exe --install Ubuntu
echo.
echo [SUCESSO] Se a instalacao requerer reinicio, reinicie o computador e abra o terminal Ubuntu.
pause
exit /b 0

:INSTALL_KALI
cls
echo [INFO] Iniciando instalacao do Kali Linux no WSL2...
wsl.exe --install kali-linux
echo.
echo [SUCESSO] Se a instalacao requerer reinicio, reinicie o computador e abra o terminal Kali.
pause
exit /b 0

:LIST_DISTROS
cls
echo [INFO] Distros disponiveis e instaladas:
wsl.exe --list --verbose
echo.
pause
exit /b 0

:UPDATE_WSL
cls
echo [INFO] Atualizando subsistema WSL2 para a versao mais recente...
wsl.exe --update
echo.
pause
exit /b 0

:END
exit /b 0
