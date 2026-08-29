@echo off
chcp 65001 > nul
title SENTINELA-5 - pdf-parser (Didier Stevens)
cls
echo ===============================================================================
echo   SENTINELA-5 FORENSIC SUITE - pdf-parser (Analise Estrutural de Objetos PDF)
echo ===============================================================================
echo.

if "%~1"=="" (
    set /p pdf_path="Introduza o caminho do PDF ou arraste o ficheiro para aqui: "
) else (
    set "pdf_path=%~1"
)

if "%pdf_path%"=="" (
    echo [!] Nenhum ficheiro indicado.
) else (
    python "C:\Users\Yokozuna\Dev\02_MOTOR_FORENSE\03_HASHING_CUSTODIA\tools\pdf-parser.py" -a "%pdf_path%"
)

echo.
pause
