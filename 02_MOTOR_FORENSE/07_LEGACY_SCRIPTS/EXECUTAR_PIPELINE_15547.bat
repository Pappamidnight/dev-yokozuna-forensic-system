@echo off
REM ==============================================================================
REM EXECUTAR_PIPELINE_15547.bat - PIPELINE DO PROCESSO 15547/26.0T8LSB
REM Juizo Central Civel de Lisboa — Reivindicacao, Propriedade e Litisconsorcio
REM ==============================================================================
TITLE Pipeline Deterministico: Processo 15547/26.0T8LSB

set DEV_ROOT=C:\Users\Yokozuna\Dev
set SCRIPT=%DEV_ROOT%\AI\skills\mcp-fs-pydantic-org\scripts\pipeline_processo_15547.py

cd /d "%DEV_ROOT%"

cls
echo ==============================================================================
echo       PIPELINE DETERMINISTICO ESPECIALIZADO: PROCESSO 15547/26.0T8LSB
echo ==============================================================================
echo  Tribunal : Juizo Central Civel de Lisboa
echo  Materia  : Propriedade Plena, Direito Sucessorio e Litisconsorcio Necessario
echo  Titular  : Teresa de Jesus Martins
echo  Normas   : Art. 1311 e 892 CC c/c Art. 33 CPC e Art. 65 CRP
echo ==============================================================================
echo.

python "%SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Ocorreu um problema ao executar o pipeline do processo 15547.
    pause
    exit /b 1
)

echo.
echo [SUCESSO] Pipeline do Processo 15547/26.0T8LSB concluido com exito.
echo - Relatorio Markdown : %DEV_ROOT%\OUTPUT_CENTRALIZADO\01_INDEX_E_RELATORIOS\DOSSIER_15547_RELATORIO.md
echo - Painel Visual HTML : %DEV_ROOT%\OUTPUT_CENTRALIZADO\DOSSIER_PROCESSO_15547.html
echo - Dados JSONL        : %DEV_ROOT%\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\processo_15547_atos.jsonl
echo.
pause
