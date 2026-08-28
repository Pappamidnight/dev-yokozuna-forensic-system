<#
.SYNOPSIS
    Atualiza a Memoria Persistente e Base de Dados SQLite Forense (PowerShell).
#>

$DevRoot = "C:\Users\Yokozuna\Dev"
$ScriptPath = "$DevRoot\AI\skills\mcp-fs-pydantic-org\scripts\persistent_memory_manager.py"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "ATUALIZANDO MEMORIA PERSISTENTE E BASE DE DADOS SQLITE" -ForegroundColor Green
Write-Host "BD: $DevRoot\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\memoria_forense_unificada.db" -ForegroundColor Gray
Write-Host "==================================================================" -ForegroundColor Cyan

Set-Location $DevRoot
python $ScriptPath
