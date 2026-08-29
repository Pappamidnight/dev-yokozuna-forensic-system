@echo off
chcp 65001 > nul
title SENTINELA-5 - PDFiD (Didier Stevens)
cls
echo ===============================================================================
echo   SENTINELA-5 FORENSIC SUITE - PDFiD (Triage e Estrutura de PDF)
echo ===============================================================================
echo.

if "%~1"=="" (
    set /p pdf_path="Introduza o caminho do PDF ou arraste o ficheiro para aqui: "
) else (
    set "pdf_path=%~1"
)

if "%pdf_path%"=="" (
    echo [!] Nenhum caminho indicado. A fazer scan geral aos PDFs gerados...
    python "C:\Users\Yokozuna\Dev\02_MOTOR_FORENSE\03_HASHING_CUSTODIA\tools\pdfid.py" --scan "C:\Users\Yokozuna\Dev\03_RESULTADOS\05_PDFS_FINAIS"
) else (
    python "C:\Users\Yokozuna\Dev\02_MOTOR_FORENSE\03_HASHING_CUSTODIA\tools\pdfid.py" -e "%pdf_path%"
)

echo.
pause
