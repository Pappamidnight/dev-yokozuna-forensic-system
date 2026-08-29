@echo off
chcp 65001 > nul
title PIPELINE DE TESTE E CONFRONTO FORENSE ISOLADO
cls
echo ===============================================================================
echo   PIPELINE DE TESTE FORENSE ISOLADO POR TERMO - DEV YOKOZUNA
echo   Validação de Provas, RAG 4 Camadas, Tom Neutro e Score 100/100
echo ===============================================================================
echo.
set /p termo="Introduza o termo ou referência a testar (ex: 15547, tinta azul, 419855940, UNICRE): "

if "%termo%"=="" (
    set termo=15547
)

echo.
echo A executar pipeline completo para o termo "%termo%"...
echo.
python "C:\Users\Yokozuna\Dev\Backend\pipeline_teste_confronto_isolado.py" "%termo%"
echo.
pause
