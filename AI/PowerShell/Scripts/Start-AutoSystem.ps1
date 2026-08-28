<#
.SYNOPSIS
    Inicia o Sistema Automatico Continuo (Daemon Watchdog + Fatos + Otimizacao) no PowerShell.
#>

$DevRoot = "C:\Users\Yokozuna\Dev"
$ScriptPath = "$DevRoot\AI\skills\mcp-fs-pydantic-org\scripts\auto_system_daemon.py"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "INICIANDO SISTEMA AUTOMATICO CONTINUO (POWERSHELL DAEMON)" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Cyan

Set-Location $DevRoot
python $ScriptPath --poll 3 --optimize-interval 60
