@echo off
chcp 65001 > nul
title EXTRACAO FORENSE DE TELEMOVEL (ECRA PARTIDO / ADB)
cls
echo ===============================================================================
echo   EXTRATOR FORENSE DE DADOS DE TELEMOVEL VIA CABO USB (ADB)
echo   (WhatsApp, Fotos DCIM, Documentos e Base de Dados)
echo ===============================================================================
echo.
echo [1/4] A verificar conexao com o telemovel por USB...
adb devices
if %errorlevel% neq 0 (
    echo.
    echo [-] ADB nao encontrado ou telemovel nao detetado.
    echo Certifique-se de que o cabo USB esta ligado e os drivers instalados.
    pause
    exit /b 1
)

echo.
echo [2/4] A criar pastas de saida em OUTPUT_CENTRALIZADO...
if not exist "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_whatsapp" (
    mkdir "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_whatsapp"
)
if not exist "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_fotos" (
    mkdir "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_fotos"
)

echo.
echo [3/4] A extrair WhatsApp do dispositivo...
adb pull /sdcard/Android/media/com.whatsapp/WhatsApp/ "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_whatsapp\"
adb pull /sdcard/WhatsApp/ "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_whatsapp\"

echo.
echo [4/4] A extrair Fotografias e Videos (DCIM)...
adb pull /sdcard/DCIM/ "C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_fotos\"

echo.
echo ===============================================================================
echo   EXTRACAO CONCLUIDA COM SUCESSO!
echo   Ficheiros guardados em:
echo   - WhatsApp: OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_whatsapp
echo   - Fotos   : OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\telemovel_fotos
echo ===============================================================================
pause
