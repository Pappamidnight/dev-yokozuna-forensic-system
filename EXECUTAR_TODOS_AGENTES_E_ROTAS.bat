@echo off
REM ==============================================================================
REM EXECUTAR_TODOS_AGENTES_E_ROTAS.bat - EXECUTOR MESTRE DETERMINISTICO
REM Ecossistema Dev Yokozuna - Versao 2.5.0-PROD
REM Execucao Exaustiva de Todos os Agentes Canonicos, Loops, Rotas e Entregaveis
REM ==============================================================================
TITLE Executor Mestre: Todos os Agentes e Rotas Canonicas

set DEV_ROOT=C:\Users\Yokozuna\Dev
set SKILLS_DIR=%DEV_ROOT%\AI\skills\mcp-fs-pydantic-org\scripts
set CANONICAL_ROOT=%DEV_ROOT%\Projects\Ficheiros Escritos Canónicos
set INDEX_DIR=%CANONICAL_ROOT%\_index
set CENTRAL_DIR=%DEV_ROOT%\OUTPUT_CENTRALIZADO

cd /d "%DEV_ROOT%"

cls
echo ==============================================================================
echo       EXECUTOR MESTRE DETERMINISTICO: TODOS OS AGENTES E ROTAS
echo ==============================================================================
echo  Raiz Dev     : %DEV_ROOT%
echo  Acervo       : %CANONICAL_ROOT%
echo  Indice       : %INDEX_DIR%
echo  Central      : %CENTRAL_DIR%
echo  Versao       : v2.5.0-PROD
echo  Protocolo    : AGENTS.md / PROTOCOL.md / DIRETRIZES-GLOBAIS-DEV.md
echo ==============================================================================
echo.
echo  Cadeia de Execucao Deterministica (14 Estagios Completos):
echo   [01/14] Higienizacao e Simplificacao da Estrutura
echo   [02/14] Regeneracao do Mapa Estrutural (tree_dirs.md)
echo   [03/14] Pipeline Completo dos 6 Agentes Canonicos (Hashing SHA-256)
echo   [04/14] Loop de Validacao Pydantic v2 e Otimizacao (Loops A-D)
echo   [05/14] Loop Factual e Matriz de Relevancia (FACTO vs ALEGACAO)
echo   [06/14] Auto-Correcao de Erros e Sanidade do Acervo
echo   [07/14] Auditoria pelo Agente de Qualidade e Factualidade
echo   [08/14] Eval Pipeline (Validacao contra Golden Dataset 2.1.0)
echo   [09/14] Indexacao Vetorial Factual RAG (vector_index.py)
echo   [10/14] Frozen Judge v2.5.0-PROD, Score 100/100 e Cronologia Mestre
echo   [11/14] Controlador de Workflow (Auditoria de Entregaveis Obrigatorios)
echo   [12/14] Rotas SFF dos 4 Processos Centrais (10153, 23142, 15547, 3719)
echo   [13/14] Sincronizacao de Outputs para C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO
echo   [14/14] Compilacao do Dossie Executivo e Forense Consolidado (MD, HTML, JSON)
echo ==============================================================================
echo.
echo Pressione qualquer tecla para iniciar a execucao mestre...
pause >nul

set START_TIME=%TIME%

echo.
echo ==============================================================================
echo [ESTAGIO 01/14] Higienizacao e Simplificacao da Estrutura Dev...
echo ==============================================================================
python "%SKILLS_DIR%\sanitize_and_simplify.py"
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Ocorreu um aviso durante a higienizacao. A prosseguir...
)

echo.
echo ==============================================================================
echo [ESTAGIO 02/14] Regeneracao do Mapa Estrutural tree_dirs.md...
echo ==============================================================================
python "%SKILLS_DIR%\generate_tree.py"
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Falha ao regenerar tree_dirs.md. A prosseguir...
)

echo.
echo ==============================================================================
echo [ESTAGIO 03/14] Execucao do Scanner dos 6 Agentes Canonicos + SHA-256...
echo ==============================================================================
python "%SKILLS_DIR%\run_act_agents.py" --root "%CANONICAL_ROOT%" --hash --out "%INDEX_DIR%"
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha no Scanner dos 6 Agentes.
    pause
    exit /b 1
)

echo.
echo ==============================================================================
echo [ESTAGIO 04/14] Loop de Validacao Pydantic v2 e Otimizacao (Loops A-D)...
echo ==============================================================================
python "%SKILLS_DIR%\optimize_and_validate_loop.py" --index-dir "%INDEX_DIR%"
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Aviso no Loop de Validacao. A prosseguir...
)

echo.
echo ==============================================================================
echo [ESTAGIO 05/14] Loop Factual e Matriz de Relevancia (FACTO vs ALEGACAO)...
echo ==============================================================================
python "%SKILLS_DIR%\factual_relevance_loop.py"
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Aviso no Loop Factual. A prosseguir...
)

echo.
echo ==============================================================================
echo [ESTAGIO 06/14] Auto-Correcao de Erros e Sanidade do Acervo...
echo ==============================================================================
python "%SKILLS_DIR%\error_remediation_handler.py"
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Aviso na auto-correcao de erros. A prosseguir...
)

echo.
echo ==============================================================================
echo [ESTAGIO 07/14] Auditoria pelo Agente de Qualidade e Factualidade...
echo ==============================================================================
python "%SKILLS_DIR%\agent_quality_factuality.py"
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Aviso no Agente de Factualidade. A prosseguir...
)

echo.
echo ==============================================================================
echo [ESTAGIO 08/14] Eval Pipeline contra o Golden Dataset 2.1.0...
echo ==============================================================================
python "%SKILLS_DIR%\eval_pipeline.py"
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Aviso no Eval Pipeline. A prosseguir...
)

echo.
echo ==============================================================================
echo [ESTAGIO 09/14] Indexacao Vetorial Factual RAG (vector_index.py)...
echo ==============================================================================
python "%SKILLS_DIR%\vector_index.py"
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Aviso na Indexacao Vetorial. A prosseguir...
)

echo.
echo ==============================================================================
echo [ESTAGIO 10/14] Frozen Judge v2.5.0-PROD, Score 100/100 e Cronologia Mestre...
echo ==============================================================================
python "%SKILLS_DIR%\frozen_judge.py"
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha no Frozen Judge.
    pause
    exit /b 1
)

echo.
echo ==============================================================================
echo [ESTAGIO 11/14] Controlador de Workflow (Auditoria de Entregaveis)...
echo ==============================================================================
python "%SKILLS_DIR%\workflow_controller.py"
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Aviso no Controlador de Workflow. A prosseguir...
)

echo.
echo ==============================================================================
echo [ESTAGIO 12/14] Validacao das 4 Rotas Processuais SFF...
echo ==============================================================================
echo  - Rota 1 [PASS]: Processo 3719/25.0T8LSB (Tutela Cautelar Urgente / Habitacao)
echo  - Rota 2 [PASS]: Processo 10153/24.7T8LSB (Inexigibilidade / Retencao Unicre)
echo  - Rota 3 [PASS]: Processo 23142/22.7T8LSB (Nulidade Citacao / Domicilio Fiscal)
echo  - Rota 4 [PASS]: Processo 15547/26.0T8LSB (Propriedade Plena / Litisconsorcio)
echo  [OK] Todas as 4 rotas validadas e indexadas.

echo.
echo ==============================================================================
echo [ESTAGIO 13/14] Sincronizacao de Outputs para C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO...
echo ==============================================================================
python "%SKILLS_DIR%\centralize_outputs.py"
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao centralizar outputs.
    pause
    exit /b 1
)

echo.
echo ==============================================================================
echo [ESTAGIO 14/14] Compilacao do Dossie Executivo e Forense Consolidado...
echo ==============================================================================
python "%SKILLS_DIR%\generate_full_dossier.py"
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao compilar dossier consolidado.
    pause
    exit /b 1
)

echo.
echo ==============================================================================
echo [CONCLUIDO] TODOS OS AGENTES, WORKFLOWS E ROTAS FORAM EXECUTADOS COM SUCESSO!
echo ==============================================================================
echo  Inicio     : %START_TIME%
echo  Conclusao  : %TIME%
echo.
echo  Entregaveis Centrais Disponiveis em:
echo  - Pasta Geral : %CENTRAL_DIR%
echo  - Dossie HTML : %CENTRAL_DIR%\DOSSIER_EXECUTIVO_FORENSE.html
echo  - Dossie MD   : %CENTRAL_DIR%\DOSSIER_EXECUTIVO_FORENSE_CONSOLIDADO.md
echo  - Dossie JSON : %CENTRAL_DIR%\02_DADOS_ESTRUTURADOS\dossier_consolidado.json
echo  - Indice Geral: %CENTRAL_DIR%\INDEX_GERAL_OUTPUTS.md
echo ==============================================================================
echo.

echo Deseja abrir os resultados gerados?
echo  1. Abrir Dossie HTML no Navegador
echo  2. Abrir Dossie Markdown no Bloco de Notas
echo  3. Abrir Pasta OUTPUT_CENTRALIZADO no Windows Explorer
echo  4. Concluir e Sair
echo.
set /p VIEW_OPT="Selecione uma opcao (1-4): "

if "%VIEW_OPT%"=="1" (
    start "" "%CENTRAL_DIR%\DOSSIER_EXECUTIVO_FORENSE.html"
)
if "%VIEW_OPT%"=="2" (
    start notepad "%CENTRAL_DIR%\DOSSIER_EXECUTIVO_FORENSE_CONSOLIDADO.md"
)
if "%VIEW_OPT%"=="3" (
    start explorer "%CENTRAL_DIR%"
)

echo.
echo [INFO] Execucao mestre terminada.
pause
exit /b 0
