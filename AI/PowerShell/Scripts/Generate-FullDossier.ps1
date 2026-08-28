<#
.SYNOPSIS
    Gera o Dossier Executivo e Forense Consolidado com todos os outputs, relatorios e comparativo esperado vs. real.
.DESCRIPTION
    Script nativo PowerShell para orquestrar a geracao do Dossier nos formatos Markdown, HTML e JSON,
    sincronizando os outputs em C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO.
#>

[CmdletBinding()]
param(
    [string]$DevRoot = "C:\Users\Yokozuna\Dev"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Join-Path $DevRoot "AI\skills\mcp-fs-pydantic-org\scripts"
$DossierScript = Join-Path $ScriptDir "generate_full_dossier.py"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " GERANDO DOSSIER EXECUTIVO E FORENSE CONSOLIDADO (POWERSHELL)" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Raiz Dev : $DevRoot"
Write-Host " Gerador  : $DossierScript"
Write-Host "=================================================================="

if (Test-Path $DossierScript) {
    python $DossierScript
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[SUCESSO] Dossier Executivo gerado em OUTPUT_CENTRALIZADO!" -ForegroundColor Green
        Write-Host " - Markdown : C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\DOSSIER_EXECUTIVO_FORENSE_CONSOLIDADO.md"
        Write-Host " - HTML     : C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\DOSSIER_EXECUTIVO_FORENSE.html"
        Write-Host " - JSON     : C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\02_DADOS_ESTRUTURADOS\dossier_consolidado.json"
    } else {
        Write-Host "`n[ERRO] Falha ao executar gerador de dossier." -ForegroundColor Red
    }
} else {
    Write-Host "`n[ERRO] Script gerador nao encontrado em: $DossierScript" -ForegroundColor Red
}
