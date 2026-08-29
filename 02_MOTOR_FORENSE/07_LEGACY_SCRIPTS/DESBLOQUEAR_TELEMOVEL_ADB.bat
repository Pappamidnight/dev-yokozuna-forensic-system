@echo off
chcp 65001 > nul
title DESBLOQUEIO DE TELEMOVEL VIA PC (ECRA PARTIDO / ADB)
cls
echo ===============================================================================
echo   DESBLOQUEADOR DE TELEMOVEL COM ECRA PARTIDO VIA TECLADO DO PC
echo ===============================================================================
echo.
echo [1/3] A verificar ligacao com o telemovel...
adb devices
echo.

set /p user_pass="Digite a sua PASSWORD ou CODIGO PIN e prima ENTER: "

echo.
echo [2/3] A acordar o telemovel e a abrir o teclado de desbloqueio...
adb shell input keyevent 26
timeout /t 1 > nul
adb shell input keyevent 82
timeout /t 1 > nul

echo [3/3] A enviar a password para o dispositivo...
adb shell input text "%user_pass%"
timeout /t 1 > nul
adb shell input keyevent 66

echo.
echo ===============================================================================
echo   COMANDO DE DESBLOQUEIO ENVIADO!
echo   Se o codigo estiver correto, o telemovel esta agora desbloqueado.
echo   Pode agora executar: EXTRAIR_DADOS_TELEMOVEL_ADB.bat
echo ===============================================================================
pause
