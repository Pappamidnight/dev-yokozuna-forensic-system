@echo off
chcp 65001 > nul
title OPENCODE COM MCP FORENSE & RAG - DEV YOKOZUNA
cls
echo ===============================================================================
echo   OPENCODE COM SERVIDOR MCP FORENSE INTEGRADO
echo   (Acesso automatico a +133k evidencias, SQLite e RAG dos 4 Processos)
echo ===============================================================================
echo.
cd /d "C:\Users\Yokozuna\Dev\opencode"
"C:\Users\Yokozuna\.bun\bin\bun.exe" run dev
echo.
pause
