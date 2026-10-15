<#
.SYNOPSIS
    V8_Rmlint_Auditor.ps1
    Auditoria de Conteudo Real via 'rmlint' (WSL Ubuntu/Kali).
    Opera em modo 100% DRY-RUN (NAO APAGA QUALQUER FICHEIRO).
    Cumpre os Contratos de Runtime de Agentes (Tool, Observability e Reversibility Contracts).
.PARAMETER Tipo
    Tipo obrigatorio a auditar: database, video, excel, audio, word, pdf, imagem, json, texto, yaml, csv, markdown.
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("database", "video", "excel", "audio", "word", "pdf", "imagem", "json", "texto", "yaml", "csv", "markdown")]
    [string]$Tipo,

    [string]$Distro = "Ubuntu-26.04",

    [string]$AlvoWindows = "C:\ACERVO\storage"
)

$ErrorActionPreference = "Stop"

$MapeamentoExtensoes = @{
    "database" = "db,sqlite,mdb,accdb"
    "video"    = "mp4,mkv,avi,mov,wmv"
    "excel"    = "xls,xlsx,xlsm"
    "audio"    = "mp3,wav,flac,m4a,aac"
    "word"     = "doc,docx"
    "pdf"      = "pdf"
    "imagem"   = "jpg,jpeg,png,gif,webp,bmp,tiff"
    "json"     = "json"
    "texto"    = "txt"
    "yaml"     = "yml,yaml"
    "csv"      = "csv"
    "markdown" = "md"
}

$BaseDir     = "C:\ACERVO"
$LogsDedupe  = "$BaseDir\logs\deduplicado\$Tipo"
if (-not (Test-Path $LogsDedupe)) {
    New-Item -ItemType Directory -Force -Path $LogsDedupe | Out-Null
}

$OutJsonWin  = "$LogsDedupe\rmlint_$Tipo.json"
$OutShWin    = "$LogsDedupe\rmlint_${Tipo}_dryrun.sh"

# Converter caminhos para WSL
function To-WslPath($winPath) {
    $p = $winPath -replace "\\", "/"
    if ($p -match "^([A-Za-z]):(.*)$") {
        $drive = $matches[1].ToLower()
        $rest = $matches[2]
        return "/mnt/$drive$rest"
    }
    return $p
}

$wslAlvo = To-WslPath $AlvoWindows
$wslOutJson = To-WslPath $OutJsonWin
$wslOutSh   = To-WslPath $OutShWin
$extensoes  = $MapeamentoExtensoes[$Tipo]

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  ACERVO V8 - AUDITOR RMLINT (WSL $Distro)                            " -ForegroundColor Cyan
Write-Host "  Tipo:        $Tipo" -ForegroundColor Cyan
Write-Host "  Extensoes:   $extensoes" -ForegroundColor Cyan
Write-Host "  Alvo:        $wslAlvo" -ForegroundColor Cyan
Write-Host "  MODO:        100% DRY-RUN (AUDITORIA E CUSTODIA READ-ONLY)         " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

# Verificar se rmlint existe no WSL
$checkRmlint = wsl -d $Distro -- which rmlint 2>$null
if (-not $checkRmlint) {
    Write-Host "[ERRO] 'rmlint' nao encontrado no WSL ($Distro)." -ForegroundColor Red
    Write-Host "Instale executando: wsl -d $Distro -- sudo apt update && sudo apt install -y rmlint" -ForegroundColor Yellow
    exit 1
}

# Construir comando rmlint com protecao total e dryrun
# Nota: rmlint gera relatorio json e um script shell que NAO e executado (permanece auditavel)
$cmdWsl = "rmlint '$wslAlvo' --types=$extensoes -o json:'$wslOutJson' -o sh:'$wslOutSh'"

Write-Host "[INFO] A executar rmlint no WSL..." -ForegroundColor DarkGray
Write-Host "Comando: wsl -d $Distro -- $cmdWsl" -ForegroundColor DarkGray

$t0 = Get-Date
try {
    $output = wsl -d $Distro -- bash -c "$cmdWsl" 2>&1
    $exitCode = $LASTEXITCODE
} catch {
    $exitCode = 1
    $output = $_.Exception.Message
}
$t1 = Get-Date
$duracao = [math]::Round(($t1 - $t0).TotalSeconds, 2)

if ($exitCode -ne 0) {
    Write-Host "[ERRO] rmlint falhou com codigo $exitCode" -ForegroundColor Red
    Write-Host $output -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "  [OK] Auditoria rmlint concluida com sucesso em ${duracao}s!" -ForegroundColor Green
Write-Host "  Relatorio JSON: $OutJsonWin" -ForegroundColor Green
Write-Host "  Relatorio Script (Auditavel - Nao Executado): $OutShWin" -ForegroundColor Green
Write-Host "  Nenhum ficheiro foi apagado ou modificado no sistema." -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
