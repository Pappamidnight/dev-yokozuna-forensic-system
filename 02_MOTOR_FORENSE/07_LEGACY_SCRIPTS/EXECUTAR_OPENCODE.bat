@echo off
chcp 65001 > nul
title OPENCODE - ANOMALYCO AI CODING ASSISTANT
cls
echo ===============================================================================
echo   OPENCODE (AnomalyCo) - ASSISTENTE DE CODIFICACAO E AGENTES
echo ===============================================================================
echo.
cd /d "C:\Users\Yokozuna\Dev\opencode"
"C:\Users\Yokozuna\.bun\bin\bun.exe" run dev
echo.
pause
