@echo off
REM ==============================================================================
REM GERAR_DOSSIER_COMPLETO.bat - GERADOR DE DOSSIÊ EXECUTIVO E FORENSE CONSOLIDADO
REM Ecossistema Deterministico Dev Yokozuna - Versao 2.5.0-PROD
REM ==============================================================================
TITLE Gerador de Dossier Executivo e Forense - Dev Yokozuna

set DEV_ROOT=C:\Users\Yokozuna\Dev
set SKILLS_DIR=%DEV_ROOT%\AI\skills\mcp-fs-pydantic-org\scripts
set CENTRAL_DIR=%DEV_ROOT%\OUTPUT_CENTRALIZADO
set DOSSIER_SCRIPT=%SKILLS_DIR%\generate_full_dossier.py
set SYNC_SCRIPT=%SKILLS_DIR%\centralize_outputs.py

cd /d "%DEV_ROOT%"

cls
echo ==============================================================================
echo        GERADOR DE DOSSIE EXECUTIVO E FORENSE CONSOLIDADO
echo ==============================================================================
echo  Raiz Dev     : %DEV_ROOT%
echo  Destino      : %CENTRAL_DIR%
echo  Versao       : v2.5.0-PROD
echo  Protocolo    : AGENTS.md / PROTOCOL.md / DIRETRIZES-GLOBAIS-DEV.md
echo ==============================================================================
echo.
echo  Etapas de Execucao:
echo   [1/2] Sincronizacao e Centralizacao de Outputs
echo   [2/2] Compilacao do Dossier Forense (Markdown, HTML e JSON)
echo ==============================================================================
echo.

echo [INFO] [1/2] A sincronizar pasta de output centralizado...
python "%SYNC_SCRIPT%"

echo.
echo [INFO] [2/2] A compilar Dossie Executivo e Forense Consolidado...
python "%DOSSIER_SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Ocorreu um problema durante a geracao do dossier.
    pause
    exit /b 1
)

echo.
echo ==============================================================================
echo [SUCESSO] DOSSIE EXECUTIVO E FORENSE GERADO COM EXITO!
echo ==============================================================================
echo  - Ficheiro Markdown : %CENTRAL_DIR%\DOSSIER_EXECUTIVO_FORENSE_CONSOLIDADO.md
echo  - Ficheiro HTML     : %CENTRAL_DIR%\DOSSIER_EXECUTIVO_FORENSE.html
echo  - Ficheiro JSON     : %CENTRAL_DIR%\02_DADOS_ESTRUTURADOS\dossier_consolidado.json
echo ==============================================================================
echo.

echo Deseja abrir o Dossie no navegador ou editor?
echo  1. Abrir Dossie HTML no Navegador
echo  2. Abrir Dossie Markdown no Bloco de Notas / Editor
echo  3. Abrir Pasta OUTPUT_CENTRALIZADO no Explorador do Windows
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
