@echo off
chcp 65001 > nul
title PDF-ID LOCATOR - BUSCA INSTANTÂNEA DE TEXTO EM PDFs
cls
echo ===============================================================================
echo   PDF-ID LOCATOR FORENSE - DEV YOKOZUNA
echo   Localizador Instantâneo de Palavras e Referências Citius dentro dos PDFs
echo ===============================================================================
echo.
set /p termo="Introduza a palavra, referência Citius ou NIF a pesquisar: "

if "%termo%"=="" (
    set termo=419855940
)

echo.
echo A pesquisar por "%termo%" em todos os PDFs do acervo...
echo.
python "C:\Users\Yokozuna\Dev\Backend\pdf_identifier_tool.py" "%termo%"
echo.
pause
