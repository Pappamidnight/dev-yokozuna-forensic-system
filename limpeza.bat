@echo off
chcp 65001 >nul
echo === ACERVO - Limpeza (baixo risco) ===
echo.
echo [1] Desativar hibernacao...
powercfg /h off
echo [2] Reduzir pontos de restauro...
vssadmin resize shadowstorage /for=C: /on=C: /maxsize=5GB
echo [3] Limpar temporarios...
del /f /s /q "%TEMP%\*" 2>nul
del /f /s /q "C:\Windows\Temp\*" 2>nul
echo.
echo Concluido.
pause
