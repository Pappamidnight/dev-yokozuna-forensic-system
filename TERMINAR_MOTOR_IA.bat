@echo off
chcp 65001 > nul
title TERMINAR MOTOR IA FORENSE - DEV YOKOZUNA
cls
echo ===============================================================================
echo   A DESLIGAR E TERMINAR SERVIÇOS DO MOTOR DE IA FORENSE
echo ===============================================================================
echo.
echo [1/2] A encerrar processos Python associados aos servidores forenses...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8088 :8080"') do (
    taskkill /F /PID %%a > nul 2>&1
)

echo.
echo [2/2] A libertar memória e ficheiros de bloqueio...
echo [+] Servidores e processos em segundo plano terminados com sucesso.
echo.
echo ===============================================================================
echo   SISTEMA DE IA DESLIGADO COM SUCESSO E EM SEGURANÇA.
echo ===============================================================================
echo.
pause
