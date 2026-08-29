@echo off
chcp 65001 > nul
title PowerShell com Suite de Comandos Linux / Unix Integrada
cls
echo ===============================================================================
echo   POWERSHELL COM SUITE DE COMANDOS LINUX/UNIX
echo   (touch, which, file, locate, diff, cmp, cksum, zip, unzip, tar, gzip, scp)
echo ===============================================================================
echo.
powershell.exe -NoExit -ExecutionPolicy Bypass -Command ". 'C:\Users\Yokozuna\Dev\tools\linux_commands_setup.ps1'"
