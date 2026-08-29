@echo off
chcp 65001 > nul
title GERADOR DE PDFS JUDICIAIS OFICIAIS - DEV YOKOZUNA
cls
echo ===============================================================================
echo   GERADOR DE DOCUMENTOS JUDICIAIS E ATOS EM FORMATO PDF PARA IMPRESSÃO
echo ===============================================================================
echo.
python "C:\Users\Yokozuna\Dev\Backend\gerar_pdf_atos_judiciais.py"
echo.
echo A abrir pasta com os PDFs gerados...
explorer "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\05_PDFS_GERADOS_PARA_IMPRESSAO"
echo.
pause
