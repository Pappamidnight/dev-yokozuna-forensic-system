<#
.SYNOPSIS
    V8_Orquestrador.ps1
    Orquestrador Supervisor V8 (Interativo e Auditor).
    Mostra o estado atual dos 12 tipos (OK / PENDENTE / FALHA),
    identifica o PROXIMO TIPO pendente e lanca APENAS ESSE TIPO.
    NUNCA PROCESSA TODOS AO MESMO TEMPO.
#>

[CmdletBinding()]
param (
    [switch]$StatusOnly,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$TiposPermitidos = @(
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

$BaseDir       = "C:\ACERVO"
$ScriptsDir    = "$BaseDir\scripts"
$LogsDedupe    = "$BaseDir\logs\deduplicado"
$GlobalJson    = "$LogsDedupe\resumo_global.json"
$ProcessorPs1  = "$ScriptsDir\V8_Processar_Tipo.ps1"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  ACERVO V8 - ORQUESTRADOR SUPERVISOR (1 TIPO DE CADA VEZ)             " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Carregar resumo_global.json
$globalObj = $null
if (Test-Path $GlobalJson) {
    try {
        $globalObj = Get-Content -Path $GlobalJson -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        $globalObj = $null
    }
}

# 2. Exibir Painel de Estado dos 12 Tipos
Write-Host "ESTADO DO ACERVO:" -ForegroundColor Yellow
$proximoTipo = $null

foreach ($t in $TiposPermitidos) {
    $info = $null
    if ($globalObj -and $globalObj.tipos -and $globalObj.tipos.$t) {
        $info = $globalObj.tipos.$t
    }

    $st = if ($info -and $info.estado) { $info.estado } else { "PENDENTE" }
    
    $color = "Yellow"
    if ($st -eq "OK") { $color = "Green" }
    elseif ($st -eq "FALHA") { $color = "Red" }

    $detalhe = ""
    if ($info -and $info.total) {
        $detalhe = "(Total: $($info.total) | Originais: $($info.originais) | Duplicados: $($info.duplicados))"
    }

    $padding = " " * (12 - $t.Length)
    Write-Host ("  {0}{1} {2,-10} {3}" -f $t.ToUpper(), $padding, $st, $detalhe) -ForegroundColor $color

    # Identificar o primeiro pendente
    if (-not $proximoTipo -and $st -ne "OK") {
        $proximoTipo = $t
    }
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan

# 3. Verificar Bloqueio Ativo
if ($globalObj -and $globalObj.estado_global -eq "FALHA") {
    Write-Host "[SISTEMA BLOQUEADO] O sistema encontra-se bloqueado em: $($globalObj.bloqueado_em)" -ForegroundColor Red
    Write-Host "Motivo: $($globalObj.motivo)" -ForegroundColor Red
    Write-Host "Resolva a inconsistencia antes de avancar." -ForegroundColor Red
    exit 1
}

# 4. Modo Apenas Estado
if ($StatusOnly) {
    exit 0
}

# 5. Execucao de APENAS UM tipo
if (-not $proximoTipo) {
    Write-Host "[CONCLUIDO] Todos os 12 tipos ja foram processados e validados com SUCESSO!" -ForegroundColor Green
    exit 0
}

Write-Host "[PROXIMO PASSO] Lancando EXCLUSIVAMENTE o tipo: $proximoTipo" -ForegroundColor Green
Write-Host "Comando: & `"$ProcessorPs1`" -Tipo $proximoTipo" -ForegroundColor DarkGray
Write-Host ""

$dryParam = if ($DryRun) { "-DryRun" } else { "" }

if ($DryRun) {
    & powershell -ExecutionPolicy Bypass -File "$ProcessorPs1" -Tipo $proximoTipo -DryRun
} else {
    & powershell -ExecutionPolicy Bypass -File "$ProcessorPs1" -Tipo $proximoTipo
}
