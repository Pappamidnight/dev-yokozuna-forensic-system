<#
.SYNOPSIS
    V8_Processar_Tipo.ps1 (Versao Final com Validacao Cruzada e Modo DRY-RUN)
    Garante que ACERVO_MODE=DRYRUN e o padrao.
    NUNCA apaga qualquer ficheiro. Acao executada em DRYRUN: NENHUMA.
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$CsvFile,

    [Parameter(Mandatory = $false)]
    [string]$Tipo,

    [switch]$ValidacaoCruzadaLinux
)

$ErrorActionPreference = "Stop"

# 1. Definir obrigatoriamente ACERVO_MODE=DRYRUN se nao definido
if (-not $env:ACERVO_MODE) {
    $env:ACERVO_MODE = "DRYRUN"
}

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
$LogsCsvDir    = "$BaseDir\logs\csv"
$LogsDedupe    = "$BaseDir\logs\deduplicado"
$GlobalJson    = "$LogsDedupe\resumo_global.json"
$PythonScript  = "$ScriptsDir\separar_tipo.py"
$PythonCruzado = "$ScriptsDir\validacao_cruzada_tripla.py"

# Localizar CSV se apenas -Tipo foi passado
if (-not $CsvFile -and $Tipo) {
    $tLower = $Tipo.ToLower()
    $candidatos = Get-ChildItem -Path $LogsCsvDir -Filter "duplicados_${tLower}_*.csv" -EA 0
    if (-not $candidatos) {
        $candidatos = Get-ChildItem -Path $LogsCsvDir -Filter "duplicados_${tLower}.csv" -EA 0
    }
    if ($candidatos) {
        $CsvFile = ($candidatos | Sort-Object Name -Descending | Select-Object -First 1).FullName
    } else {
        Write-Host "[ERRO] Nenhum CSV encontrado para o tipo: $Tipo em $LogsCsvDir" -ForegroundColor Red
        exit 1
    }
}

if (-not $CsvFile) {
    Write-Host "[ERRO] E necessario especificar -CsvFile ou -Tipo." -ForegroundColor Red
    exit 1
}

$nomeCsv = [System.IO.Path]::GetFileNameWithoutExtension($CsvFile)
$tipoDetetado = $null
foreach ($t in $TiposPermitidos) {
    if ($nomeCsv -match "_$t(_|$)") {
        $tipoDetetado = $t
        break
    }
}

if (-not $tipoDetetado) {
    Write-Host "[ERRO] Tipo nao suportado para o ficheiro: $CsvFile" -ForegroundColor Red
    exit 1
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  ACERVO V8 - PROCESSAMENTO ATOMICO (1 CSV DE CADA VEZ)               " -ForegroundColor Cyan
Write-Host "  Tipo:            $tipoDetetado" -ForegroundColor Cyan
Write-Host "  CSV:             $CsvFile" -ForegroundColor Cyan
Write-Host "  MODO GLOBAL:     $($env:ACERVO_MODE) (READ-ONLY / ZERO ELIMINACAO)" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

# 2. Executar Separador Python Atómico
$exitCode = 0
try {
    & python "$PythonScript" $tipoDetetado
    $exitCode = $LASTEXITCODE
} catch {
    $exitCode = 1
}

$resumoTipoPath = "$LogsDedupe\$tipoDetetado\resumo_$tipoDetetado.json"
if (-not (Test-Path $resumoTipoPath)) {
    Write-Host "[ERRO CRITICO] O relatorio $resumoTipoPath nao foi gerado!" -ForegroundColor Red
    exit 1
}

$resumoTipo = Get-Content -Path $resumoTipoPath -Raw -Encoding UTF8 | ConvertFrom-Json

# Validacoes rigorosas
$total            = $resumoTipo.total_candidatos
$gruposTotais     = $resumoTipo.grupos_totais
$originaisCount   = $resumoTipo.originais_eleitos
$duplicadosCount  = $resumoTipo.duplicados_marcados
$erros            = $resumoTipo.erros_resiliencia
$diferenca        = $resumoTipo.diferenca
$validacao_grupos = ($gruposTotais -eq $originaisCount)
$validacao_csv    = $resumoTipo.validacao_csv

$estado = if ($diferenca -eq 0 -and $originaisCount -gt 0 -and $duplicadosCount -gt 0 -and $validacao_csv -and $validacao_grupos -and $exitCode -eq 0) { "OK" } else { "FALHA" }

# 3. Opcional: Validacao Cruzada Forense Tripla (rmlint + fdupes + rdfind)
if ($ValidacaoCruzadaLinux -and $estado -eq "OK") {
    Write-Host ""
    Write-Host "[VALIDACAO CRUZADA] A disparar rmlint + fdupes + rdfind via WSL..." -ForegroundColor Yellow
    try {
        & python "$PythonCruzado" $tipoDetetado "$BaseDir\storage"
        if ($LASTEXITCODE -ne 0) {
            $estado = "FALHA"
        }
    } catch {
        $estado = "FALHA"
    }
}

# 4. Atualizar resumo_global.json com campos oficiais DRYRUN
$globalObj = $null
if (Test-Path $GlobalJson) {
    try { $globalObj = Get-Content -Path $GlobalJson -Raw -Encoding UTF8 | ConvertFrom-Json } catch { $globalObj = $null }
}

if (-not $globalObj -or -not $globalObj.tipos) {
    $tiposInit = [ordered]@{}
    foreach ($t in $TiposPermitidos) {
        $tiposInit[$t] = [ordered]@{ "estado" = "PENDENTE"; "concluido" = $false }
    }
    $globalObj = [ordered]@{
        "modo"                 = $env:ACERVO_MODE
        "estado_global"        = "OK"
        "ultimo_tipo"          = $null
        "ultima_execucao"      = (Get-Date).ToString("s")
        "acoes_executadas"     = 0
        "ficheiros_movidos"    = 0
        "ficheiros_apagados"   = 0
        "tipos"                = $tiposInit
    }
}

$tiposMap = [ordered]@{}
foreach ($prop in $globalObj.tipos.PSObject.Properties) {
    $tiposMap[$prop.Name] = $prop.Value
}
foreach ($t in $TiposPermitidos) {
    if (-not $tiposMap.Contains($t)) {
        $tiposMap[$t] = [ordered]@{ "estado" = "PENDENTE"; "concluido" = $false }
    }
}

$tiposMap[$tipoDetetado] = [ordered]@{
    "modo"                 = $env:ACERVO_MODE
    "estado"               = $estado
    "concluido"            = ($estado -eq "OK")
    "data"                 = (Get-Date).ToString("s")
    "total_candidatos"     = $total
    "originais"            = $originaisCount
    "duplicados"           = $duplicadosCount
    "erros"                = $erros
    "diferenca"            = $diferenca
    "acao_executada"       = "NENHUMA"
}

$globalObj.modo                = $env:ACERVO_MODE
$globalObj.estado_global       = $estado
$globalObj.ultimo_tipo         = $tipoDetetado
$globalObj.ultima_execucao     = (Get-Date).ToString("s")
$globalObj.acoes_executadas    = 0
$globalObj.ficheiros_movidos   = 0
$globalObj.ficheiros_apagados  = 0
$globalObj.tipos               = $tiposMap

# Bloqueio Imediato se FALHA
if ($estado -eq "FALHA") {
    $globalObj.estado_global = "FALHA"
    $globalObj | Add-Member -NotePropertyName "bloqueado_em" -NotePropertyValue $tipoDetetado -Force
    $globalObj | Add-Member -NotePropertyName "motivo" -NotePropertyValue "VALIDACAO" -Force
    $globalObj | ConvertTo-Json -Depth 20 | Set-Content -Path $GlobalJson -Encoding UTF8

    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Red
    Write-Host "[BLOQUEADO] Falha na validacao do tipo: $tipoDetetado" -ForegroundColor Red
    Write-Host "Diferenca: $diferenca | Grupos: $gruposTotais | Originais: $originaisCount" -ForegroundColor Red
    Write-Host "======================================================================" -ForegroundColor Red
    exit 1
}

# Sucesso
$globalObj | ConvertTo-Json -Depth 20 | Set-Content -Path $GlobalJson -Encoding UTF8

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "  [OK] Tipo '$tipoDetetado' processado com SUCESSO!" -ForegroundColor Green
Write-Host "  Total: $total | Originais: $originaisCount | Duplicados: $duplicadosCount | Erros: $erros" -ForegroundColor Green
Write-Host "  Modo: $($env:ACERVO_MODE) | Acoes: NENHUMA | Apagados: 0 | Movidos: 0" -ForegroundColor Green
Write-Host "  resumo_global.json sincronizado com estado OK." -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
