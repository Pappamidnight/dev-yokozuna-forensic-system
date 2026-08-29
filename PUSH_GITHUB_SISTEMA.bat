@echo off
chcp 65001 > nul
title PUSH PARA O GITHUB - SISTEMA SENTINELA-5
cls
echo ===============================================================================
echo   ENVIO (PUSH) DO SISTEMA SENTINELA-5 FORENSE PARA O GITHUB
echo   Repositório: https://github.com/Pappamidnight/dev-yokozuna-forensic-system.git
echo ===============================================================================
echo.
echo [1/2] A configurar buffer HTTP de 500MB...
git config http.postBuffer 524288000
git config http.version HTTP/1.1

echo.
echo [2/2] A enviar branch main para o GitHub...
git push origin main
echo.
echo ===============================================================================
echo   SINCRONIZAÇÃO CONCLUÍDA!
echo ===============================================================================
echo.
pause
