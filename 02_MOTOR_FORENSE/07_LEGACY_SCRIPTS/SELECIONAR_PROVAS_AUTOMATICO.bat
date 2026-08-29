@echo off
chcp 65001 > nul
title SELETOR AUTOMÁTICO DE PROVAS FORENSES - DEV YOKOZUNA
cls
echo ===============================================================================
echo   SELEÇÃO E AGRUPAMENTO AUTOMÁTICO DE PROVAS POR PROCESSO JUDICIAL
echo ===============================================================================
echo.
python "C:\Users\Yokozuna\Dev\Backend\selecionador_automatico_provas.py"
echo.
echo A abrir pasta com as provas organizadas por processo...
explorer "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\03_PROVAS_SELECIONADAS_POR_PROCESSO"
echo.
pause
