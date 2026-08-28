<#
.SYNOPSIS
    Organizador Global do Workspace com Protecao Rigorosa de Ficheiros de Sistema (PowerShell).
.DESCRIPTION
    Executa a varredura e ingestao segura das pastas processuais (01_INICIAL a 06_RECURSOS)
    e pastas gerais (Desktop, Documents, Downloads, OneDrive), protegendo pastas de sistema
    e IA (.codex, .gemini, .antigravity-ide, .kimi-work, AppData, etc.).
#>

[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$DryRun,
    [string]$DevRoot = "C:\Users\Yokozuna\Dev"
)

$ErrorActionPreference = "Continue"
$SkillsDir = Join-Path $DevRoot "AI\skills\mcp-fs-pydantic-org\scripts"
$ScriptPath = Join-Path $SkillsDir "organize_user_workspace.py"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " ORGANIZADOR GLOBAL E PROTECAO DE SISTEMA (POWERSHELL)" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Raiz Dev : $DevRoot"
Write-Host " Script   : $ScriptPath"
Write-Host " Modo     : $(if ($Apply) { 'EXECUCAO REAL' } else { 'SIMULACAO (DRY-RUN)' })"
Write-Host "=================================================================="

$argsList = @()
if ($Apply) {
    $argsList += "--apply"
} else {
    $argsList += "--dry-run"
}

if (Test-Path $ScriptPath) {
    & python $ScriptPath $argsList
} else {
    Write-Host "[ERRO] Script nao encontrado em: $ScriptPath" -ForegroundColor Red
}
