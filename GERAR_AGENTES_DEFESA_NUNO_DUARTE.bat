@echo off
REM ==============================================================================
REM GERAR_AGENTES_DEFESA_NUNO_DUARTE.bat - AGENTES ESSENCIAIS DA DEFESA DE NUNO DUARTE
REM Ecossistema Forense Deterministico Dev Yokozuna - Versao 2.5.0-PROD
REM ==============================================================================
TITLE Agentes Estrategicos de Defesa de Nuno Duarte - Dev Yokozuna

set DEV_ROOT=C:\Users\Yokozuna\Dev
set SKILLS_DIR=%DEV_ROOT%\AI\skills\mcp-fs-pydantic-org\scripts
set CENTRAL_DIR=%DEV_ROOT%\OUTPUT_CENTRALIZADO
set CITIUS_DIR=%CENTRAL_DIR%\04_DOCUMENTOS_CITIUS_E_PECAS
set DEFESA_SCRIPT=%SKILLS_DIR%\defesa_nuno_duarte_agents.py

cd /d "%DEV_ROOT%"

:MENU
cls
echo ==============================================================================
echo       AGENTES ESSENCIAIS PARA A DEFESA JURIDICA DE NUNO DUARTE
echo ==============================================================================
echo  Raiz Dev     : %DEV_ROOT%
echo  Pecas Citius : %CITIUS_DIR%
echo  Versao       : v2.5.0-PROD
echo  Protocolo    : AGENTS.md / PROTOCOL.md / CONTRATO_FROZEN_JUDGE_GATEWAY.md
echo ==============================================================================
echo.
echo  OS 6 AGENTES ESPECIALISTAS DA DEFESA:
echo   [1] agente-defesa-10153 (Inexigibilidade Titulo / Retencao Unicre TPA)
echo   [2] agente-defesa-23142 (Nulidade Absoluta Citacao / Domicilio Fiscal Ativo)
echo   [3] agente-defesa-15547 (Propriedade Plena / Litisconsorcio Teresa Martins)
echo   [4] agente-defesa-3719  (Providencia Cautelar Urgente / Tutela da Habitacao)
echo   [5] agente-defesa-penal (Responsabilidade Penal / Falsidade / Deontologia)
echo   [6] agente-sintese      (Consolidacao Forense e Pecas Citius Prontas)
echo ==============================================================================
echo.
echo  1. Executar os 6 Agentes e Gerar Todas as Pecas Citius da Defesa
echo  2. Abrir Painel Visual da Defesa no Navegador (DEFESA_NUNO_DUARTE_PAINEL.html)
echo  3. Abrir Estrategia Consolidada de Defesa (Markdown)
echo  4. Abrir Pasta de Pecas e Articulados Citius no Explorer
echo  5. Executar Cadeia Completa (Defesa + Frozen Judge 100/100 + Sincronizacao)
echo  6. Sair
echo ==============================================================================
set /p OPTION="Selecione uma opcao (1-6): "

if "%OPTION%"=="1" goto RUN_GENERATE_DEFENSE
if "%OPTION%"=="2" goto OPEN_HTML_PANEL
if "%OPTION%"=="3" goto OPEN_STRATEGY_MD
if "%OPTION%"=="4" goto OPEN_CITIUS_FOLDER
if "%OPTION%"=="5" goto RUN_FULL_DEFENSE_PIPELINE
if "%OPTION%"=="6" goto END

echo Opcao invalida.
pause
goto MENU

:RUN_GENERATE_DEFENSE
cls
echo [INFO] A executar os 6 Agentes e a compilar articulados de defesa...
python "%DEFESA_SCRIPT%"
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao executar agentes de defesa.
    pause
    goto MENU
)
echo.
echo [SUCESSO] Pecas e articulados da defesa de Nuno Duarte gerados em:
echo %CITIUS_DIR%
echo.
pause
goto MENU

:OPEN_HTML_PANEL
cls
if exist "%CENTRAL_DIR%\DEFESA_NUNO_DUARTE_PAINEL.html" (
    start "" "%CENTRAL_DIR%\DEFESA_NUNO_DUARTE_PAINEL.html"
) else (
    echo [INFO] A gerar painel HTML primeiro...
    python "%DEFESA_SCRIPT%"
    start "" "%CENTRAL_DIR%\DEFESA_NUNO_DUARTE_PAINEL.html"
)
goto MENU

:OPEN_STRATEGY_MD
cls
if exist "%CITIUS_DIR%\ESTRATEGIA_DEFESA_NUNO_DUARTE_CONSOLIDADA.md" (
    start notepad "%CITIUS_DIR%\ESTRATEGIA_DEFESA_NUNO_DUARTE_CONSOLIDADA.md"
) else (
    echo [INFO] A gerar pecas primeiro...
    python "%DEFESA_SCRIPT%"
    start notepad "%CITIUS_DIR%\ESTRATEGIA_DEFESA_NUNO_DUARTE_CONSOLIDADA.md"
)
goto MENU

:OPEN_CITIUS_FOLDER
cls
if not exist "%CITIUS_DIR%" (
    python "%DEFESA_SCRIPT%"
)
start explorer "%CITIUS_DIR%"
goto MENU

:RUN_FULL_DEFENSE_PIPELINE
cls
echo [INFO] [1/3] A executar os 6 Agentes Especialistas da Defesa...
python "%DEFESA_SCRIPT%"

echo.
echo [INFO] [2/3] A auditar com Frozen Judge v2.5.0-PROD...
python "%SKILLS_DIR%\frozen_judge.py"

echo.
echo [INFO] [3/3] A sincronizar com OUTPUT_CENTRALIZADO...
python "%SKILLS_DIR%\centralize_outputs.py"
python "%SKILLS_DIR%\generate_full_dossier.py"

echo.
echo ==============================================================================
echo [CONCLUIDO] CADEIA DE DEFESA E AUDITORIA CONCLUIDA COM SUCESSO!
echo ==============================================================================
echo.
pause
goto MENU

:END
echo [INFO] Painel de Defesa encerrado.
exit /b 0
