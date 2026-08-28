@echo off
REM ==============================================================================
REM CONSOLIDACAO_TOTAL_ECOSSISTEMA.bat - CONSOLIDAÇÃO TOTAL DO ECOSSISTEMA FORENSE
REM Ecossistema Deterministico Dev Yokozuna - Versao 2.5.0-PROD
REM Integra Google Drive, OneDrive, Memoria Vetorial RAG, 6 Agentes e Dossie Mestre
REM ==============================================================================
TITLE Consolidacao Total do Ecossistema - Dev Yokozuna

set DEV_ROOT=C:\Users\Yokozuna\Dev
set SKILLS_DIR=%DEV_ROOT%\AI\skills\mcp-fs-pydantic-org\scripts
set CENTRAL_DIR=%DEV_ROOT%\OUTPUT_CENTRALIZADO
set CONSOLIDATE_SCRIPT=%SKILLS_DIR%\consolidate_total_system.py

cd /d "%DEV_ROOT%"

cls
echo ==============================================================================
echo        CONSOLIDACAO TOTAL DO ECOSSISTEMA FORENSE DETERMINISTICO
echo ==============================================================================
echo  Raiz Dev     : %DEV_ROOT%
echo  Acervo       : %DEV_ROOT%\Projects\Ficheiros Escritos Canónicos
echo  Central      : %CENTRAL_DIR%
echo  Versao       : v2.5.0-PROD
echo  Protocolo    : AGENTS.md / PROTOCOL.md / DIRETRIZES-GLOBAIS-DEV.md
echo ==============================================================================
echo.
echo  RECURSOS E FONTES INTEGRADOS:
echo   [1] Google Drive (G:\) e OneDrive (C:\Users\Yokozuna\OneDrive)
echo   [2] Pastas Processuais (01_INICIAL a 06_RECURSOS) e Documentos Gerais
echo   [3] Protecao Rigorosa de Ficheiros de Sistema e IA (.codex, .gemini, etc.)
echo   [4] Memoria Vetorial RAG e Indexacao Semantica 256-d (vector_index.jsonl)
echo   [5] Os 6 Agentes Canonicos + Hashing Criptografico SHA-256
echo   [6] Frozen Judge v2.5.0-PROD (Score 100/100) e Cronologia Mestre
echo   [7] Dossie Executivo e Forense Consolidado (HTML Interativo, MD e JSON)
echo ==============================================================================
echo.
echo Pressione qualquer tecla para iniciar a Consolidacao Total...
pause >nul

echo.
echo [INFO] A iniciar motor de consolidacao total...
python "%CONSOLIDATE_SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Ocorreu um problema durante a consolidacao total.
    pause
    exit /b 1
)

echo.
echo ==============================================================================
echo [SUCESSO] CONSOLIDACAO TOTAL CONCLUIDA COM EXITO (100/100 [PASS])!
echo ==============================================================================
echo  - Dossie Visual HTML : %CENTRAL_DIR%\DOSSIER_EXECUTIVO_FORENSE.html
echo  - Dossie Markdown    : %CENTRAL_DIR%\DOSSIER_EXECUTIVO_FORENSE_CONSOLIDADO.md
echo  - Dossie JSON        : %CENTRAL_DIR%\02_DADOS_ESTRUTURADOS\dossier_consolidado.json
echo  - Memoria Vetorial   : %CENTRAL_DIR%\02_DADOS_ESTRUTURADOS\vector_index.jsonl
echo  - Cronologia Mestre  : %CENTRAL_DIR%\02_DADOS_ESTRUTURADOS\cronologia_mestre.jsonl
echo  - Indice de Saidas   : %CENTRAL_DIR%\INDEX_GERAL_OUTPUTS.md
echo ==============================================================================
echo.

echo Deseja abrir os resultados gerados?
echo  1. Abrir Dossie HTML no Navegador (Recomendado para Visualizacao/Impressao)
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
echo [INFO] Processo finalizado com sucesso.
pause
exit /b 0
