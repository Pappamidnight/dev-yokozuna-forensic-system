<#
.SYNOPSIS
    Consolidacao Total do Ecossistema Forense Deterministico (PowerShell).
.DESCRIPTION
    Integra fontes em nuvem (Google Drive G:\, OneDrive), pastas processuais,
    protege o sistema, executa memoria vetorial RAG, Frozen Judge 100/100
    e gera o Dossie Executivo Consolidado.
#>

[CmdletBinding()]
param(
    [string]$DevRoot = "C:\Users\Yokozuna\Dev"
)

$ErrorActionPreference = "Continue"
$SkillsDir = Join-Path $DevRoot "AI\skills\mcp-fs-pydantic-org\scripts"
$ScriptPath = Join-Path $SkillsDir "consolidate_total_system.py"
$CentralDir = Join-Path $DevRoot "OUTPUT_CENTRALIZADO"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " CONSOLIDACAO TOTAL DO ECOSSISTEMA FORENSE (POWERSHELL)" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Raiz Dev     : $DevRoot"
Write-Host " Script       : $ScriptPath"
Write-Host " Central      : $CentralDir"
Write-Host " Versao       : v2.5.0-PROD"
Write-Host "=================================================================="

if (Test-Path $ScriptPath) {
    & python $ScriptPath
} else {
    Write-Host "[ERRO] Script nao encontrado em: $ScriptPath" -ForegroundColor Red
}
