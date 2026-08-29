@echo off
chcp 65001 > nul
title INICIAR MOTOR IA FORENSE - DEV YOKOZUNA
cls
echo ===============================================================================
echo   INICIALIZAÇÃO DO MOTOR DETERMINÍSTICO DE IA FORENSE
echo   Diretrizes: PROTOCOL.md e AI/INSTRUCOES_DETERMINISTICAS_MOTOR_IA.md
echo ===============================================================================
echo.
echo [1/4] A verificar integridade da base SQLite e FTS5...
python "C:\Users\Yokozuna\Dev\Backend\otimizar_memoria_sqlite_fts5.py"

echo.
echo [2/4] A sincronizar Tabela Mestra de Referência Forense em CSV (Conflito Zero)...
python "C:\Users\Yokozuna\Dev\Backend\exportar_tabela_mestra_csv.py"

echo.
echo [3/4] A iniciar Servidor AJAX / RAG Forense na porta 8088...
start /b python "C:\Users\Yokozuna\Dev\Backend\ajax_forensic_server.py" 8088

echo.
echo [4/4] A abrir Portal de Consulta RAG e Dashboard no Browser...
timeout /t 2 > nul
start http://localhost:8088/
start "" "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\01_INDEX_E_RELATORIOS\CONFRONTO_LADO_A_LADO_INTERATIVO.html"

echo.
echo ===============================================================================
echo   MOTOR DE IA INICIADO COM SUCESSO!
echo   Tabela Mestra CSV: OUTPUT_CENTRALIZADO/02_DADOS_ESTRUTURADOS/TABELA_MESTRA_REFERENCIA_FORENSE.csv
echo   Porta Ativa: http://localhost:8088/
echo   Para desligar o motor a qualquer momento, execute TERMINAR_MOTOR_IA.bat
echo ===============================================================================
echo.
pause
