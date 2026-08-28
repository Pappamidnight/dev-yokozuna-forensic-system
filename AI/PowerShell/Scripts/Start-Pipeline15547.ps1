<#
.SYNOPSIS
    Executa o Pipeline Deterministico Especializado para o Processo 15547/26.0T8LSB (PowerShell).
#>

$DevRoot = "C:\Users\Yokozuna\Dev"
$ScriptPath = "$DevRoot\AI\skills\mcp-fs-pydantic-org\scripts\pipeline_processo_15547.py"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "INICIANDO PIPELINE PROCESSO 15547/26.0T8LSB (POWERSHELL)" -ForegroundColor Green
Write-Host "Materia: Propriedade Plena, Direito Sucessorio e Litisconsorcio" -ForegroundColor Gray
Write-Host "Titular: Teresa de Jesus Martins" -ForegroundColor Gray
Write-Host "==================================================================" -ForegroundColor Cyan

Set-Location $DevRoot
python $ScriptPath
