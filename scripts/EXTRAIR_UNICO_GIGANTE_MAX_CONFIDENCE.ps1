<#
.SYNOPSIS
    EXTRAIR_UNICO_GIGANTE_MAX_CONFIDENCE.ps1
    Extrai um unico CSV global contendo todos os duplicados de Maximo Sinal:
    dupe:name;size + !attrib:H + !attrib:S + !empty: + Exclusoes de Ruido.
    Exporta diretamente para C:\ACERVO\logs\csv_max_confidence\duplicados_max_confidence.csv
#>

[CmdletBinding()]
param (
    [string]$BaseUrl = "http://localhost:8080/",
    [string]$OutDir  = "C:\ACERVO\logs\csv_max_confidence"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $OutDir)) {
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
}

# Filtro Unico Gigante de Maximo Sinal
$FiltroGigante = 'dupe:name;size !attrib:H !attrib:S !empty: !path:"$Recycle.Bin" !path:"System Volume Information" !path:node_modules !path:.git !path:__pycache__ !path:venv !path:site-packages !path:AppData !path:ProgramData'

$DestinoCsv = "$OutDir\duplicados_max_confidence.csv"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  ACERVO V8 - EXTRACAO UNICA GIGANTE (MAXIMA CONFIANCA)               " -ForegroundColor Cyan
Write-Host "  Query:    $FiltroGigante" -ForegroundColor Cyan
Write-Host "  Destino:  $DestinoCsv" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$encoded = [System.Uri]::EscapeDataString($FiltroGigante)
$url = "$($BaseUrl)?search=$encoded&json=1&path_column=1&size_column=1&date_modified_column=1&attributes_column=1&extension_column=1&count=9999999"

$t0 = Get-Date
Write-Host "[INFO] A consultar Everything HTTP API (porta 8080)..." -ForegroundColor Yellow

try {
    $json = curl.exe -s $url | ConvertFrom-Json
    $items = $json.results
    $t1 = Get-Date
    $duracaoExtracao = [math]::Round(($t1 - $t0).TotalSeconds, 2)

    if ($items -and $items.Count -gt 0) {
        Write-Host "  [OK] Everything devolveu $($items.Count) registos em ${duracaoExtracao}s." -ForegroundColor Green
        Write-Host "  [INFO] A converter e a gravar CSV com cabecalhos canónicos..." -ForegroundColor DarkGray

        $csvRows = foreach ($it in $items) {
            [PSCustomObject]@{
                Nome       = $it.name
                Caminho    = $it.path
                Tamanho    = $it.size
                DataMod    = $it.date_modified
                Extensao   = $it.extension
                Atributos  = $it.attributes
            }
        }
        $csvRows | Export-Csv -Path $DestinoCsv -NoTypeInformation -Encoding utf8BOM

        $t2 = Get-Date
        $duracaoTotal = [math]::Round(($t2 - $t0).TotalSeconds, 2)
        $tamanhoMB = [math]::Round((Get-Item $DestinoCsv).Length / 1MB, 2)

        Write-Host ""
        Write-Host "======================================================================" -ForegroundColor Green
        Write-Host "  [SUCESSO] CSV de Maxima Confianca Gerado com Sucesso!" -ForegroundColor Green
        Write-Host "  Total Registos: $($items.Count)" -ForegroundColor Green
        Write-Host "  Tamanho Ficheiro: ${tamanhoMB} MB" -ForegroundColor Green
        Write-Host "  Tempo Total: ${duracaoTotal}s" -ForegroundColor Green
        Write-Host "  Ficheiro: $DestinoCsv" -ForegroundColor Green
        Write-Host "======================================================================" -ForegroundColor Green
    } else {
        Write-Host "  [AVISO] 0 registos devolvidos pelo Everything." -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [ERRO] Falha durante a consulta ou gravacao: $_" -ForegroundColor Red
    exit 1
}
