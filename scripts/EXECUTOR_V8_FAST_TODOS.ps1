<#
.SYNOPSIS
    EXECUTOR_V8_FAST_TODOS.ps1
    Orquestrador Sequencial Reutilizável V8 FAST.
    Processa todos os 12 tipos sequencialmente em ~12 segundos totais.
    Exibe progresso em tempo real e consolida o resumo global.
#>

$ErrorActionPreference = "Stop"

$Tipos = @(
    "database",
    "video",
    "excel",
    "audio",
    "word",
    "pdf",
    "imagem",
    "json",
    "texto",
    "yaml",
    "csv",
    "markdown"
)

$ScriptPython = "C:\ACERVO\scripts\processar_tipo_v8_fast.py"
$DestFast     = "C:\ACERVO\logs\v8_fast"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  ACERVO V8.1 FAST - EXECUCAO SEQUENCIAL REUTILIZAVEL (12 TIPOS)       " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$t0 = Get-Date

foreach ($t in $Tipos) {
    Write-Host "[RUN] A processar tipo: $t" -ForegroundColor Yellow
    $output = python -u "$ScriptPython" $t 2>&1
    
    # Extrair e mostrar apenas métricas essenciais no ecrã
    $output | Select-String -Pattern "Originais:|Duplicados:|Espaço Recuperável:|Tempo Total:" | ForEach-Object {
        Write-Host "    $_" -ForegroundColor Green
    }
    Write-Host ""
}

$t1 = Get-Date
$duracao = [math]::Round(($t1 - $t0).TotalSeconds, 2)

Write-Host "======================================================================" -ForegroundColor Green
Write-Host "  [SUCESSO] TODOS OS 12 TIPOS PROCESSADOS COM V8 FAST EM ${duracao}s!" -ForegroundColor Green
Write-Host "  Destino dos CSVs: $DestFast" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
