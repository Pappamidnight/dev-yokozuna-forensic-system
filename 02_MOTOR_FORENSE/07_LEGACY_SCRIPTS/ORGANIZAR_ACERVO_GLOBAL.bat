@echo off
REM ==============================================================================
REM ORGANIZAR_ACERVO_GLOBAL.bat - ORGANIZADOR GLOBAL E PROTEÇÃO DE SISTEMA
REM Ecossistema Deterministico Dev Yokozuna - Versao 2.5.0-PROD
REM ==============================================================================
TITLE Organizador Global de Pastas e Protecao de Sistema - Dev Yokozuna

set DEV_ROOT=C:\Users\Yokozuna\Dev
set SKILLS_DIR=%DEV_ROOT%\AI\skills\mcp-fs-pydantic-org\scripts
set CENTRAL_DIR=%DEV_ROOT%\OUTPUT_CENTRALIZADO
set SCRIPT=%SKILLS_DIR%\organize_user_workspace.py

cd /d "%DEV_ROOT%"

:MENU
cls
echo ==============================================================================
echo       ORGANIZADOR GLOBAL DE PASTAS E PROTECAO RIGOROSA DO SISTEMA
echo ==============================================================================
echo  Raiz Dev     : %DEV_ROOT%
echo  Destino      : %DEV_ROOT%\Projects\Ficheiros Escritos Canónicos
echo  Versao       : v2.5.0-PROD
echo  Protocolo    : AGENTS.md / PROTOCOL.md / DIRETRIZES-GLOBAIS-DEV.md
echo ==============================================================================
echo.
echo  PASTAS DO SISTEMA E IA PROTEGIDAS (TOTALMENTE IMUTAVEIS):
echo   - .codex, .gemini, .antigravity-ide, .kimi-work, .kimi-webbridge, .cache
echo   - Searches, Favorites, Links, Saved Games, Music, Videos, Pictures
echo   - Extensoes de sistema (.exe, .dll, .sys, .dat, .ini, .bin, etc.)
echo.
echo  FONTES DE DOCUMENTOS JURIDICOS PARA INGESTAO:
echo   - 01_INICIAL, 02_CONTESTACAO, 03_PROVAS, 04_ALEGACOES, 05_SENTENCA, 06_RECURSOS
echo   - Desktop, Documents, Downloads, OneDrive (Filtro documental + SHA-256)
echo ==============================================================================
echo.
echo  1. [SIMULACAO / AUDITORIA] Varredura Segura sem Escrita (Dry-Run)
echo  2. [INGESTAO REAL] Organizar e Copiar Documentos para os 6 Agentes Canonicos
echo  3. [PIPELINE COMPLETO] Ingestao Real + 14 Estagios + Frozen Judge + Dossie
echo  4. [VER PROTECAO] Abrir Mapa de Pastas Protegidas do Sistema
echo  5. Sair
echo ==============================================================================
set /p OPTION="Selecione uma opcao (1-5): "

if "%OPTION%"=="1" goto RUN_DRY_RUN
if "%OPTION%"=="2" goto RUN_APPLY
if "%OPTION%"=="3" goto RUN_FULL_PIPELINE
if "%OPTION%"=="4" goto VIEW_PROTECTION
if "%OPTION%"=="5" goto END

echo Opcao invalida.
pause
goto MENU

:RUN_DRY_RUN
cls
echo [INFO] A executar simulacao (Dry-Run)... Nenhum ficheiro sera alterado.
python "%SCRIPT%" --dry-run
echo.
echo [INFO] Relatorio de simulacao gerado em OUTPUT_CENTRALIZADO\01_INDEX_E_RELATORIOS\
pause
goto MENU

:RUN_APPLY
cls
echo ==============================================================================
echo                     CONFIRMACAO DE INGESTAO REAL
echo ==============================================================================
echo  Esta acao ira copiar com seguranca os novos documentos identificados
echo  para as pastas canonicas dos 6 Agentes em:
echo  %DEV_ROOT%\Projects\Ficheiros Escritos Canónicos
echo.
echo  Ficheiros de sistema e configuracoes de IA permanecerao 100%% INTATOS.
echo ==============================================================================
set /p CONFIRM="Deseja prosseguir com a organizacao real? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo [INFO] Operacao cancelada pelo utilizador.
    pause
    goto MENU
)

echo [INFO] A executar ingestao e organizacao segura...
python "%SCRIPT%" --apply
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Ocorreu um erro durante a ingestao.
    pause
    goto MENU
)

echo.
echo [SUCESSO] Ingestao concluida com sucesso!
pause
goto MENU

:RUN_FULL_PIPELINE
cls
echo [INFO] A executar Ingestao Real de Documentos...
python "%SCRIPT%" --apply

echo.
echo [INFO] A iniciar Pipeline Mestre dos 14 Estagios Deterministicos...
call "%DEV_ROOT%\EXECUTAR_TODOS_AGENTES_E_ROTAS.bat"
goto MENU

:VIEW_PROTECTION
cls
if exist "%CENTRAL_DIR%\01_INDEX_E_RELATORIOS\mapa_pastas_protegidas.md" (
    type "%CENTRAL_DIR%\01_INDEX_E_RELATORIOS\mapa_pastas_protegidas.md"
) else (
    echo [INFO] A gerar mapa de protecao...
    python "%SCRIPT%" --dry-run
    if exist "%CENTRAL_DIR%\01_INDEX_E_RELATORIOS\mapa_pastas_protegidas.md" (
        type "%CENTRAL_DIR%\01_INDEX_E_RELATORIOS\mapa_pastas_protegidas.md"
    )
)
echo.
pause
goto MENU

:END
echo [INFO] Painel encerrado.
exit /b 0
