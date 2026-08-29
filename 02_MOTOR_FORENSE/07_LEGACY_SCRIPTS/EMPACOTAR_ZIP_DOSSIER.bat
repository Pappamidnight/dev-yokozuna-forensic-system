@echo off
chcp 65001 > nul
title EMPACOTADOR DE DOSSIER FORENSE ZIP - DEV YOKOZUNA
cls
echo ===============================================================================
echo   A GERAR ARQUIVO ZIP COM TODAS AS FOLHAS E PEÇAS ORGANIZADAS POR PROCESSO
echo ===============================================================================
echo.
python "C:\Users\Yokozuna\Dev\Backend\empacotar_dossier_forense_zip.py"
echo.
echo A abrir a pasta de destino...
explorer /select,"C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\DOSSIER_FORENSE_COMPLETO_DEV_YOKOZUNA.zip"
echo.
pause
