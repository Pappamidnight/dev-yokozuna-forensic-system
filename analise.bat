@echo off
chcp 65001 >nul
echo === ACERVO - Analise rapida ===
echo.
echo TOP 20 maiores ficheiros:
echo.
C:\ACERVO\bin\es.exe -instance 1.5a -n 20 -size -dm -sort size-descending "size:>1gb"
echo.
echo TOP 20 videos duplicados:
echo.
C:\ACERVO\bin\es.exe -instance 1.5a -n 20 -size -sort size-descending "video: dupe:size"
echo.
pause
