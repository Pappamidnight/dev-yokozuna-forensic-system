@echo off
REM ==============================================================================
REM INICIAR AGENTES E WORKFLOWS DETERMINISTICOS - ECOSSISTEMA DEV YOKOZUNA
REM Versao: 3.0.0 Enterprise Master
REM ==============================================================================
TITLE Painel de Controlo Master - Agentes e Workflows Dev

set DEV_ROOT=C:\Users\Yokozuna\Dev
set SKILLS_DIR=%DEV_ROOT%\AI\skills\mcp-fs-pydantic-org\scripts
set CANONICAL_ROOT=%DEV_ROOT%\Projects\Ficheiros Escritos Canónicos
set INDEX_DIR=%CANONICAL_ROOT%\_index

cd /d "%DEV_ROOT%"

:MENU
cls
echo ==============================================================================
echo        PAINEL DE CONTROLO MASTER: ECOSSISTEMA FORENSE & MULTIAGENTE
echo ==============================================================================
echo  Raiz: %DEV_ROOT%
echo  Acervo: %CANONICAL_ROOT%
echo  Index: %INDEX_DIR%
echo ==============================================================================
echo  0. [MESTRE] Executar TODOS os Agentes, Loops, Rotas e Dossie Forense
echo  1. Executar Pipeline Deterministico Completo (6 Agentes Canonicos)
echo  2. Iniciar Watchdog Auto-Indexer (Tempo Real / Monitorizacao Continua)
echo  3. Executar Watchdog em Modo Unico (Scan e Atualizacao Imediata)
echo  4. Executar Loop de Validacao e Otimizacao de Dados (Loops A-D)
echo  5. Regenerar Mapa Estrutural de Pastas e Ficheiros (tree_dirs.md)
echo  6. Abrir Relatorio de Auditoria e Qualidade (_index)
echo  7. Executar Pipeline sobre Processo Especifico (SFF Mode)
echo  8. Executar Eval Pipeline (Avaliacao contra Golden Dataset)
echo  9. Abrir YKF Suite Forense (YKF Launcher)
echo  10. Executar Loop Factual e Matriz de Relevancia (FACTO vs ALEGACAO)
echo  11. Iniciar Sessao de 15 Minutos de Reuniao de Informacao
echo  12. Executar Frozen Judge (Score 100/100) e Cronologia Mestre
echo  13. Executar Controlador de Workflow (Verificar Entregaveis Obrigatorios)
echo  14. Executar Auto-Correcao de Erros e Sanidade do Acervo
echo  15. Executar Higienizacao e Simplificacao da Estrutura
echo  16. Sincronizar Pasta de Output Centralizado
echo  17. Gerar Dossie Executivo e Forense Consolidado (Layout Completo)
echo  18. Organizar e Ingerir Acervo Global de Pastas (com Protecao de Sistema)
echo  19. Agentes Estrategicos de Defesa de Nuno Duarte (Pecas Citius)
echo  20. Executar Pipeline Especializado do Processo 15547/26.0T8LSB
echo  21. Atualizar Memoria Persistente e Base de Dados SQLite Forense
echo  22. Executar Pipeline Societario SPARK / Venture Partners / CMVM
echo  23. Iniciar Motor RAG Forense e Societario (Busca Semantica 175k Chunks)
echo  24. Abrir LLM Knowledge Wiki (Site HTML e Doutrina)
echo  25. Executar Agente de Higienizacao e Consolidacao do Desktop
echo  26. Configurar WSL2 (Ubuntu / Kali Linux)
echo  27. Sincronizar com o GitHub
echo  28. Sair
echo ==============================================================================
set /p OPTION="Selecione uma opcao (0-28): "

if "%OPTION%"=="0" goto RUN_ALL_AGENTS_ROUTES
if "%OPTION%"=="1" goto RUN_PIPELINE
if "%OPTION%"=="2" goto RUN_WATCHDOG_CONTINUOUS
if "%OPTION%"=="3" goto RUN_WATCHDOG_ONCE
if "%OPTION%"=="4" goto RUN_OPTIMIZE_LOOP
if "%OPTION%"=="5" goto RUN_GENERATE_TREE
if "%OPTION%"=="6" goto OPEN_REPORTS
if "%OPTION%"=="7" goto RUN_SFF_PROCESS
if "%OPTION%"=="8" goto RUN_EVAL_PIPELINE
if "%OPTION%"=="9" goto RUN_YKF_LAUNCHER
if "%OPTION%"=="10" goto RUN_FACTUAL_LOOP
if "%OPTION%"=="11" goto RUN_15MIN_SESSION
if "%OPTION%"=="12" goto RUN_FROZEN_JUDGE
if "%OPTION%"=="13" goto RUN_WORKFLOW_CONTROLLER
if "%OPTION%"=="14" goto RUN_ERROR_REMEDIATION
if "%OPTION%"=="15" goto RUN_SANITIZATION
if "%OPTION%"=="16" goto RUN_CENTRALIZE_OUTPUTS
if "%OPTION%"=="17" goto RUN_GENERATE_DOSSIER
if "%OPTION%"=="18" goto RUN_ORGANIZE_GLOBAL
if "%OPTION%"=="19" goto RUN_DEFESA_NUNO_DUARTE
if "%OPTION%"=="20" goto RUN_PIPELINE_15547
if "%OPTION%"=="21" goto RUN_PERSISTENT_MEMORY
if "%OPTION%"=="22" goto RUN_SPARK_VENTURE
if "%OPTION%"=="23" goto RUN_RAG
if "%OPTION%"=="24" goto RUN_WIKI
if "%OPTION%"=="25" goto RUN_DESKTOP_HYGIENE
if "%OPTION%"=="26" goto RUN_WSL2_SETUP
if "%OPTION%"=="27" goto RUN_GITHUB_SYNC
if "%OPTION%"=="28" goto END

echo Opcao invalida. Tente novamente.
pause
goto MENU

:RUN_PIPELINE
cls
echo [INFO] A executar Pipeline Deterministico dos 6 Agentes Canonicos...
python "%SKILLS_DIR%\run_act_agents.py" --root "%CANONICAL_ROOT%" --hash --out "%INDEX_DIR%"
pause
goto MENU

:RUN_WATCHDOG_CONTINUOUS
cls
echo [INFO] A iniciar Watchdog Auto-Indexer em tempo real (Polling 3s)...
echo Pressione Ctrl+C para interromper.
python "%SKILLS_DIR%\watchdog_indexer.py" --poll 3
pause
goto MENU

:RUN_WATCHDOG_ONCE
cls
echo [INFO] A executar checagem unica do Watchdog...
python "%SKILLS_DIR%\watchdog_indexer.py" --once
pause
goto MENU

:RUN_OPTIMIZE_LOOP
cls
echo [INFO] A executar Loop de Validacao e Otimizacao de Dados...
python "%SKILLS_DIR%\optimize_and_validate_loop.py" --index-dir "%INDEX_DIR%"
pause
goto MENU

:RUN_GENERATE_TREE
cls
echo [INFO] A regenerar mapa estrutural tree_dirs.md...
python "%SKILLS_DIR%\generate_tree.py"
pause
goto MENU

:OPEN_REPORTS
cls
echo [INFO] A exibir resumo de pipeline_report.json:
if exist "%INDEX_DIR%\pipeline_report.json" (
    type "%INDEX_DIR%\pipeline_report.json"
) else (
    echo [AVISO] pipeline_report.json nao encontrado em %INDEX_DIR%.
)
echo.
pause
goto MENU

:RUN_SFF_PROCESS
cls
set /p PROC="Digite o ID do processo (ex: 15547, 3719, 10153, 23142): "
python "%SKILLS_DIR%\run_process_pipeline.py" --process-id "%PROC%" --hash --out "%INDEX_DIR%"
pause
goto MENU

:RUN_EVAL_PIPELINE
cls
echo [INFO] A executar Evaluation Pipeline contra Golden Dataset...
python "%SKILLS_DIR%\run_evals.py" --golden "%SKILLS_DIR%\..\assets\eval\goldenset.json" --data "%INDEX_DIR%"
pause
goto MENU

:RUN_YKF_LAUNCHER
cls
echo [INFO] A abrir YKF Launcher...
if exist "%DEV_ROOT%\Projects\Ficheiros Escritos Canónicos\YKF\ykf_deep_scanner.bat" (
    call "%DEV_ROOT%\Projects\Ficheiros Escritos Canónicos\YKF\ykf_deep_scanner.bat"
) else (
    echo [AVISO] Launcher YKF nao encontrado.
    pause
)
goto MENU

:RUN_FACTUAL_LOOP
cls
echo [INFO] A executar Loop Factual e Matriz de Relevancia...
python "%SKILLS_DIR%\run_factual_loop.py" --index-dir "%INDEX_DIR%"
pause
goto MENU

:RUN_15MIN_SESSION
cls
echo [INFO] A iniciar Sessao Deterministica de 15 Minutos...
call "%DEV_ROOT%\START_15MIN_GATHERING_SESSION.bat"
goto MENU

:RUN_FROZEN_JUDGE
cls
echo [INFO] A executar Frozen Judge v2.5.0 e Validador de Score 100/100...
python "%SKILLS_DIR%\frozen_judge.py" --index-dir "%INDEX_DIR%"
pause
goto MENU

:RUN_WORKFLOW_CONTROLLER
cls
echo [INFO] A executar Controlador Deterministico de Workflow...
python "%SKILLS_DIR%\workflow_controller.py" --index-dir "%INDEX_DIR%"
pause
goto MENU

:RUN_ERROR_REMEDIATION
cls
echo [INFO] A executar Auto-Correcao de Erros e Sanidade do Acervo...
python "%SKILLS_DIR%\error_remediation_handler.py"
pause
goto MENU

:RUN_SANITIZATION
cls
echo [INFO] A executar Higienizacao e Simplificacao da Estrutura Dev...
python "%SKILLS_DIR%\sanitize_and_simplify.py"
pause
goto MENU

:RUN_CENTRALIZE_OUTPUTS
cls
echo [INFO] A sincronizar e centralizar todos os outputs em C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO...
python "%SKILLS_DIR%\centralize_outputs.py"
pause
goto MENU

:RUN_ALL_AGENTS_ROUTES
cls
echo [INFO] A iniciar Executor Mestre (Todos os Agentes e Rotas)...
call "%DEV_ROOT%\EXECUTAR_TODOS_AGENTES_E_ROTAS.bat"
goto MENU

:RUN_GENERATE_DOSSIER
cls
echo [INFO] A gerar Dossie Executivo e Forense Consolidado...
call "%DEV_ROOT%\GERAR_DOSSIER_COMPLETO.bat"
goto MENU

:RUN_ORGANIZE_GLOBAL
cls
echo [INFO] A abrir Organizador Global de Pastas e Protecao de Sistema...
call "%DEV_ROOT%\ORGANIZAR_ACERVO_GLOBAL.bat"
goto MENU

:RUN_DEFESA_NUNO_DUARTE
cls
echo [INFO] A abrir Agentes Estrategicos de Defesa de Nuno Duarte...
call "%DEV_ROOT%\GERAR_AGENTES_DEFESA_NUNO_DUARTE.bat"
goto MENU

:RUN_PIPELINE_15547
cls
echo [INFO] A executar Pipeline Deterministico do Processo 15547/26.0T8LSB...
call "%DEV_ROOT%\EXECUTAR_PIPELINE_15547.bat"
goto MENU

:RUN_PERSISTENT_MEMORY
cls
echo [INFO] A atualizar Memoria Persistente e Base de Dados SQLite Forense...
call "%DEV_ROOT%\EXECUTAR_MEMORIA_PERSISTENTE.bat"
goto MENU

:RUN_SPARK_VENTURE
cls
echo [INFO] A executar Pipeline Societario SPARK / Venture Partners / CMVM...
call "%DEV_ROOT%\INICIAR_PROJETO_SPARK.bat"
goto MENU

:RUN_RAG
cls
echo [INFO] A abrir Motor RAG Forense e Societario...
call "%DEV_ROOT%\INICIAR_PROJETO_RAG.bat"
goto MENU

:RUN_WIKI
cls
echo [INFO] A abrir LLM Knowledge Wiki...
call "%DEV_ROOT%\INICIAR_PROJETO_WIKI.bat"
goto MENU

:RUN_DESKTOP_HYGIENE
cls
echo [INFO] A executar Agente de Higienizacao e Consolidacao do Desktop...
call "%DEV_ROOT%\INICIAR_HIGIENIZACAO_DESKTOP.bat"
goto MENU

:RUN_WSL2_SETUP
cls
echo [INFO] A abrir Gestor de Instalacao WSL2 (Ubuntu / Kali)...
call "%DEV_ROOT%\INSTALAR_WSL2_UBUNTU_KALI.bat"
goto MENU

:RUN_GITHUB_SYNC
cls
echo [INFO] A abrir Sincronizador GitHub...
call "%DEV_ROOT%\SINCRONIZAR_GITHUB.bat"
goto MENU

:END
echo [INFO] Painel encerrado.
exit /b 0
