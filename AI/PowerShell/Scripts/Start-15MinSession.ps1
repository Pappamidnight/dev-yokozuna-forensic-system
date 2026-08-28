<#
.SYNOPSIS
    Sessao de 15 Minutos de Reuniao de Informacao, Ordenacao Cronologica e Frozen Judge (PowerShell).
.DESCRIPTION
    Executa o script session_15min_gatherer.py com contagem regressiva de 15 minutos e validacao Frozen Judge 100/100.
#>

[CmdletBinding()]
param (
    [int]$Minutes = 15,
    [int]$Interval = 45
)

$DevRoot = "C:\Users\Yokozuna\Dev"
$ScriptPath = "$DevRoot\AI\skills\mcp-fs-pydantic-org\scripts\session_15min_gatherer.py"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "INICIANDO SESSAO DE 15 MINUTOS NO POWERSHELL (FROZEN JUDGE 100/100)" -ForegroundColor Green
Write-Host "Raiz Dev   : $DevRoot" -ForegroundColor Gray
Write-Host "Script     : $ScriptPath" -ForegroundColor Gray
Write-Host "Duracao    : $Minutes minutos ($($Minutes * 60) segundos)" -ForegroundColor Gray
Write-Host "==================================================================" -ForegroundColor Cyan

Set-Location $DevRoot
python $ScriptPath --minutes $Minutes --interval $Interval
