@echo off
REM ==============================================================================
REM START_15MIN_GATHERING_SESSION.bat - SESSÃO DE REUNIÃO DE INFORMAÇÃO DE 15 MINUTOS
REM Ecossistema Dev Yokozuna - Versão 2.1.0
REM ==============================================================================
TITLE Sessao de Reuniao e Consolidacao de Informacao de 15 Minutos

set DEV_ROOT=C:\Users\Yokozuna\Dev
set SCRIPT=%DEV_ROOT%\AI\skills\mcp-fs-pydantic-org\scripts\session_15min_gatherer.py
set LOG_FILE=%DEV_ROOT%\Projects\Ficheiros Escritos Canónicos\_index\session_15min.log

cd /d "%DEV_ROOT%"

echo ==============================================================================
echo       INICIANDO SESSAO DE REUNIAO E CONSOLIDACAO DE INFORMACAO (15 MIN)
echo ==============================================================================
echo  Raiz   : %DEV_ROOT%
echo  Script : %SCRIPT%
echo  Log    : %LOG_FILE%
echo ==============================================================================
echo  - Monitorizacao e Ingestao em tempo real durante 15 minutos (900s)
echo  - Extracao Factual e Separacao FACTO vs ALEGACAO
echo  - Ordenacao Cronologica Mestre (ISO-8601)
echo  - Avaliacao continua com Frozen Judge (Meta: 100/100)
echo  - Auditoria com Agente de Qualidade e Factualidade
echo  - Verificacao Final com o Controlador Deterministico de Resultados
echo ==============================================================================
echo.

python "%SCRIPT%" --minutes 15 --interval 45

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Ocorreu um problema durante a execucao da sessao.
    pause
) else (
    echo.
    echo [SUCESSO] Sessao de 15 minutos concluida.
    pause
)
