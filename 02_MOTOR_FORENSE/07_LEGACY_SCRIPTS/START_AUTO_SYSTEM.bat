@echo off
REM ==============================================================================
REM START_AUTO_SYSTEM.bat - INICIAR SISTEMA AUTOMATICO E OTIMIZADOR CONTÍNUO
REM Ecossistema Dev Yokozuna - Versão 2.1.0
REM ==============================================================================
TITLE Sistema Automatico de Indexacao, Watchdog e Otimizacao Contínua

set DEV_ROOT=C:\Users\Yokozuna\Dev
set SCRIPT=%DEV_ROOT%\AI\skills\mcp-fs-pydantic-org\scripts\auto_system_daemon.py
set LOG_FILE=%DEV_ROOT%\Projects\Ficheiros Escritos Canónicos\_index\auto_system.log

cd /d "%DEV_ROOT%"

echo ==============================================================================
echo       INICIANDO SISTEMA AUTOMATICO DE INDEXACAO E OTIMIZACAO CONTINUA
echo ==============================================================================
echo  Raiz: %DEV_ROOT%
echo  Script: %SCRIPT%
echo  Log: %LOG_FILE%
echo ==============================================================================
echo  - Watchdog em tempo real (Polling: 3s)
echo  - Calculo automatico de SHA-256
echo  - Classificacao de atos processuais CPC
echo  - Atualizacao continua de _index/atos_processuais.jsonl
echo  - Regeneracao automatica de tree_dirs.md
echo  - Otimizacao e deteccao de lacunas (Loops A-D) a cada 60s ou por evento
echo ==============================================================================
echo.

python "%SCRIPT%" --poll 3 --optimize-interval 60

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Ocorreu um problema na execucao do sistema automatico.
    pause
)
