<#
.SYNOPSIS
    EXTRAIR_MAX_CONFIDENCE_EVERYTHING.ps1
    Extrai candidatos a duplicados utilizando o FILTRO DE MAXIMO SINAL do Everything:
    dupe:name;size + !attrib:H + !attrib:S + !empty: + Exclusoes de Ruido.
    Exporta CSVs atomicos de alta confianca para C:\ACERVO\logs\csv_max_confidence\
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

# Modificadores de Maximo Sinal (sem ficheiros ocultos, de sistema ou vazios)
$SinaisFiltro = "!attrib:H !attrib:S !empty: !path:`"`$Recycle.Bin`" !path:`"System Volume Information`" !path:node_modules !path:.git !path:__pycache__ !path:venv !path:site-packages !path:AppData !path:ProgramData"

# 12 Tipologias Forenses
$Tipologias = [ordered]@{
    "database" = "ext:db;sqlite;mdb;accdb"
    "video"    = "ext:mp4;mkv;avi;mov;wmv"
    "excel"    = "ext:xls;xlsx;xlsm"
    "audio"    = "ext:mp3;wav;flac;m4a;aac"
    "word"     = "ext:doc;docx"
    "pdf"      = "ext:pdf"
    "imagem"   = "ext:jpg;jpeg;png;gif;bmp;webp;tiff"
    "json"     = "ext:json"
    "texto"    = "ext:txt"
    "yaml"     = "ext:yml;yaml"
    "csv"      = "ext:csv"
    "markdown" = "ext:md"
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  ACERVO V8 - EXTRACAO FORENSE COM FILTRO DE MAXIMO SINAL             " -ForegroundColor Cyan
Write-Host "  Condicao: dupe:name;size + !attrib:H + !attrib:S + !empty: + Exclusoes" -ForegroundColor Cyan
Write-Host "  Destino:  $OutDir" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

foreach ($tipo in $Tipologias.Keys) {
    $filtroCompleto = "dupe:name;size $($Tipologias[$tipo]) $SinaisFiltro"
    $encoded = [System.Uri]::EscapeDataString($filtroCompleto)
    $url = "$($BaseUrl)?search=$encoded&json=1&path_column=1&size_column=1&date_modified_column=1&attributes_column=1&count=9999999"
    $destinoCsv = "$OutDir\duplicados_${tipo}_max_confidence.csv"

    Write-Host "[EXTRAINDO] Tipo: $tipo..." -ForegroundColor Yellow
    
    try {
        $json = curl.exe -s $url | ConvertFrom-Json
        $items = $json.results
        
        if ($items -and $items.Count -gt 0) {
            $csvRows = foreach ($it in $items) {
                [PSCustomObject]@{
                    Nome        = $it.name
                    Caminho     = $it.path
                    Tamanho     = $it.size
                    DataMod     = $it.date_modified
                    Atributos   = $it.attributes
                }
            }
            $csvRows | Export-Csv -Path $destinoCsv -NoTypeInformation -Encoding utf8BOM
            Write-Host "  [OK] $tipo : $($items.Count) registos gravados em: $destinoCsv" -ForegroundColor Green
        } else {
            Write-Host "  [INFO] $tipo : 0 registos encontrados." -ForegroundColor DarkGray
        }
    } catch {
        Write-Host "  [ERRO] Falha ao extrair $tipo : $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "  Extracao de Maximo Sinal Concluida com Sucesso!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
