@echo off
chcp 65001 > nul
title EXTRATOR DE DOCUMENTOS OFICIAIS DO TRIBUNAL - CITIUS
cls
echo ===============================================================================
echo   SISTEMA DETERMINISTICO - EXTRATOR DE DOCUMENTOS DO TRIBUNAL (CITIUS)
echo   (Processos 23142, 3719, 10153, 20203 e 15547)
echo ===============================================================================
echo.
python "C:\Users\Yokozuna\Dev\AI\skills\mcp-fs-pydantic-org\scripts\extrair_documentos_tribunal.py"
echo.
echo ===============================================================================
pause
