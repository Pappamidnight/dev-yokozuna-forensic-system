@echo off
chcp 65001 > nul
title HERMES AGENT - NOUSRESEARCH
cls
echo ===============================================================================
echo   HERMES AGENT (NousResearch) - AGENTE AUTONOMO DE IA
echo ===============================================================================
echo.
cd /d "C:\Users\Yokozuna\Dev\hermes-agent"
python -m hermes_cli.main --help
echo.
echo ===============================================================================
echo Para iniciar o Hermes Agent com dashboard web:
echo   python -m hermes_cli.main dashboard
echo Para iniciar em modo interativo CLI:
echo   python -m hermes_cli.main
echo ===============================================================================
pause
