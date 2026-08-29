@echo off
chcp 65001 > nul
title INGESTAO FORENSE MULTI-PC (PCS 2018, 2019 E 2022)
cls
echo ===============================================================================
echo   SISTEMA DETERMINISTICO - INGESTAO E SINCRONIZACAO MULTI-PC
echo   (Computadores de 2018, 2019 e 2022)
echo ===============================================================================
echo.
echo Pode ligar qualquer disco externo, Pen USB ou pasta de rede dos outros PCs.
echo.
set /p target_drive="Introduza a letra da unidade ou caminho do disco (Ex: E:\, F:\, D:\): "

if not exist "%target_drive%" (
    echo [-] Unidade ou caminho nao encontrado: %target_drive%
    pause
    exit /b 1
)

echo.
echo [1/2] A iniciar varredura e calculo paralelo de SHA-256 em: %target_drive%...
python "C:\Users\Yokozuna\Dev\AI\skills\mcp-fs-pydantic-org\scripts\fast_parallel_hasher.py"

echo.
echo [2/2] A correlacionar por epocas historicas (2018, 2019 e 2022)...
python "C:\Users\Yokozuna\Dev\AI\skills\mcp-fs-pydantic-org\scripts\ingest_multi_pc_forensics.py"

echo.
echo ===============================================================================
echo   SINCRONIZACAO E INGESTAO MULTI-PC CONCLUIDA!
echo ===============================================================================
pause
