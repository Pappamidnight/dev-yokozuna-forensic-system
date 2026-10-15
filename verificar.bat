@echo off
chcp 65001 >nul
echo === ACERVO - Estado ===
echo.
echo es.exe:
C:\ACERVO\bin\es.exe -version
echo.
echo PDFs no indice:
C:\ACERVO\bin\es.exe -instance 1.5a -get-result-count "ext:pdf"
echo.
echo Videos no indice:
C:\ACERVO\bin\es.exe -instance 1.5a -get-result-count "video:"
echo.
echo Total:
C:\ACERVO\bin\es.exe -instance 1.5a -get-result-count ""
echo.
echo Config:
dir C:\ACERVO\config\*.json /b
echo.
pause
