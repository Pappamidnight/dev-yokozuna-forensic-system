<#
.SYNOPSIS
    Inicia o servico de Watchdog Auto-Indexer em segundo plano para o diretorio Dev.

.DESCRIPTION
    Monitoriza alteracoes em ficheiros, calcula SHA-256, atualiza _index/ e regenera tree_dirs.md automaticamente.

.EXAMPLE
    .\Start-WatchdogIndexer.ps1 -PollInterval 3
#>

param(
    [int]$PollInterval = 3,
    [switch]$Once
)

$ScriptPath = "C:\Users\Yokozuna\Dev\AI\skills\mcp-fs-pydantic-org\scripts\watchdog_indexer.py"

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Script watchdog_indexer.py nao encontrado em $ScriptPath"
    exit 1
}

Write-Host "[INFO] A iniciar Watchdog Auto-Indexer no diretorio C:\Users\Yokozuna\Dev..." -ForegroundColor Cyan

if ($Once) {
    python $ScriptPath --once
} else {
    python $ScriptPath --poll $PollInterval
}
