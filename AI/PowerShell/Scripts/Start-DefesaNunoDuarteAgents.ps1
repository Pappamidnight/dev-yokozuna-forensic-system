<#
.SYNOPSIS
    Agentes Estrategicos de Defesa de Nuno Duarte (PowerShell).
.DESCRIPTION
    Orquestra os 6 agentes especialistas, gera pecas para os 4 processos centrais
    (10153, 23142, 15547, 3719) e acao penal/disciplinar, e compila o painel visual.
#>

[CmdletBinding()]
param(
    [string]$DevRoot = "C:\Users\Yokozuna\Dev"
)

$ErrorActionPreference = "Continue"
$SkillsDir = Join-Path $DevRoot "AI\skills\mcp-fs-pydantic-org\scripts"
$ScriptPath = Join-Path $SkillsDir "defesa_nuno_duarte_agents.py"
$CitiusDir = Join-Path $DevRoot "OUTPUT_CENTRALIZADO\04_DOCUMENTOS_CITIUS_E_PECAS"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " AGENTES DE DEFESA DE NUNO DUARTE (POWERSHELL)" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Raiz Dev     : $DevRoot"
Write-Host " Script       : $ScriptPath"
Write-Host " Pecas Citius : $CitiusDir"
Write-Host " Versao       : v2.5.0-PROD"
Write-Host "=================================================================="

if (Test-Path $ScriptPath) {
    & python $ScriptPath
} else {
    Write-Host "[ERRO] Script nao encontrado em: $ScriptPath" -ForegroundColor Red
}
