@echo off
REM ==============================================================================
REM INICIAR_PROJETO_RAG.bat - Launcher Centralizado do Motor RAG Forense
REM ==============================================================================
TITLE Motor RAG Forense e Societario - Dev Yokozuna

set DEV_ROOT=C:\Users\Yokozuna\Dev
set PROJ_DIR=%DEV_ROOT%\Projects\RAG_FORENSE_SOCIETARIO

cd /d "%DEV_ROOT%"

:MENU
cls
echo ==============================================================================
echo       MOTOR RAG FORENSE E SOCIETARIO (SEMANTIC RETRIEVAL)
echo ==============================================================================
echo  Base de Dados  : %PROJ_DIR%\state\rag_index.db
echo  Metadados      : Chunks, SHA-256, Processos Citius, Entidades CMVM
echo ==============================================================================
echo.
echo  1. Executar Reindexacao Completa do Acervo Forense e Societario
echo  2. Consultar RAG (Pesquisa Interativa)
echo  3. Ver Relatorio de Indexacao
echo  4. Sair
echo.
echo ==============================================================================
set /p OPTION="Selecione uma opcao (1-4): "

if "%OPTION%"=="1" goto RUN_INDEX
if "%OPTION%"=="2" goto RUN_QUERY
if "%OPTION%"=="3" goto OPEN_REPORT
if "%OPTION%"=="4" goto END

echo Opcao invalida.
pause
goto MENU

:RUN_INDEX
cls
call "%PROJ_DIR%\executar_rag.bat"
goto MENU

:RUN_QUERY
cls
set /p QUERY_TEXT="Digite o termo ou pergunta jurídica/societária: "
python "%PROJ_DIR%\rag_cli.py" --query "%QUERY_TEXT%" --top_k 5
pause
goto MENU

:OPEN_REPORT
start notepad "%PROJ_DIR%\outputs\markdown\RELATORIO_RAG_INDEX.md"
goto MENU

:END
echo [INFO] Launcher encerrado.
exit /b 0
