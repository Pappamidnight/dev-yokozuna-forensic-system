@echo off
chcp 65001 > nul
title SERVIDOR BACKEND FORENSE & RAG JURIDICO - DEV YOKOZUNA
cls
echo ===============================================================================
echo   SISTEMA DETERMINISTICO - SERVIDOR BACKEND AJAX & RAG JURIDICO
echo ===============================================================================
echo.
echo A iniciar servidor local HTTP com RAG Juridico na porta 8088...
echo Pode aceder no navegador a: http://localhost:8088/
echo.
python "C:\Users\Yokozuna\Dev\Backend\ajax_forensic_server.py" 8088
echo.
pause
