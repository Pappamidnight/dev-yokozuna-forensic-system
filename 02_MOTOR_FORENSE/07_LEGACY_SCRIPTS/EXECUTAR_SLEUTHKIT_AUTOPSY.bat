@echo off
chcp 65001 > nul
title INTEGRADOR THE SLEUTH KIT E AUTOPSY FORENSICS
cls
echo ===============================================================================
echo   SISTEMA DETERMINISTICO - INTEGRADOR THE SLEUTH KIT (TSK) E AUTOPSY
echo ===============================================================================
echo.
echo [1/2] A preparar estrutura de caso e manifestos para o Autopsy...
python "C:\Users\Yokozuna\Dev\AI\skills\mcp-fs-pydantic-org\scripts\sleuthkit_forensic_carver.py"

echo.
echo [2/2] Estrutura pronta!
echo Pode agora abrir o Autopsy e selecionar o caso em:
echo   C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\03_AUTOPSY_CASES
echo.
echo ===============================================================================
pause
