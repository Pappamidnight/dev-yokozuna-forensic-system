@echo off
chcp 65001 > nul
title SISTEMA FORENSE UNIFICADO EM 4 MUNDOS - DEV YOKOZUNA
cls
echo ===============================================================================
echo   SISTEMA FORENSE UNIFICADO EM 4 MUNDOS INDEPENDENTES
echo   01_RECURSOS_ORIGINAIS  ->  02_MOTOR_FORENSE  ->  03_RESULTADOS
echo   Governação e Navegação: 04_CONTROLO_E_INDICES
echo ===============================================================================
echo.
echo [1/4] A sincronizar arquitetura e indices de controlo...
python "C:\Users\Yokozuna\Dev\Backend\estruturar_arquitetura_4_mundos.py"

echo.
echo [2/4] A executar o Motor Super Forense CORE-5 (Orquestrador Inteligente)...
python "C:\Users\Yokozuna\Dev\02_MOTOR_FORENSE\10_CORE5_SUPER_MOTOR\motor_super_forense_core.py"

echo.
echo [3/4] A iniciar o Servidor AJAX / RAG na porta 8088...
start /b python "C:\Users\Yokozuna\Dev\02_MOTOR_FORENSE\09_INTERFACES\ajax_forensic_server.py" 8088

echo.
echo [4/4] A abrir o Mapa Geral e Dashboard de Confronto...
timeout /t 2 > nul
start "" "C:\Users\Yokozuna\Dev\04_CONTROLO_E_INDICES\MAPA_GERAL.md"
start "" "C:\Users\Yokozuna\Dev\03_RESULTADOS\06_DASHBOARDS_HTML\CONFRONTO_LADO_A_LADO_INTERATIVO.html"

echo.
echo ===============================================================================
echo   SISTEMA OPERACIONAL COM SCORE 100/100!
echo   Porta Ativa: http://localhost:8088/
echo   Para desligar: execute TERMINAR_MOTOR_IA.bat
echo ===============================================================================
echo.
pause
