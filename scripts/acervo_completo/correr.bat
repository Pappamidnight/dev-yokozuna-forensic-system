@echo off
chcp 65001 >nul
echo ============================================================
echo   ACERVO - MENU
echo ============================================================
echo.
echo   1. Diagnostico es.exe
echo   2. Analise 5 locais
echo   3. Analise so Perfil
echo   4. Analise so Dev
echo   5. Analise so G:\
echo   0. Sair
echo.
set /p op="Escolhe: "

if "%op%"=="1" python C:\ACERVO\scripts\acervo_completo\diagnostico\es_diag.py
if "%op%"=="2" python C:\ACERVO\scripts\acervo_completo\analise\analise_5locais.py
if "%op%"=="3" python C:\ACERVO\scripts\acervo_completo\analise\analise_5locais.py --local 1
if "%op%"=="4" python C:\ACERVO\scripts\acervo_completo\analise\analise_5locais.py --local 2
if "%op%"=="5" python C:\ACERVO\scripts\acervo_completo\analise\analise_5locais.py --local 5
if "%op%"=="0" exit

pause
