# =====================================================================
# POWERSHELL OFFICIAL PROFILE - C:\Users\Yokozuna\Dev\AI\PowerShell
# =====================================================================

# 1. INICIALIZAÇÃO AUTOMÁTICA EM DEV
Set-Location 'C:\Users\Yokozuna\Dev'

# 2. VARIÁVEIS DE AMBIENTE PADRÃO
$env:DEV_ROOT = "C:\Users\Yokozuna\Dev"
$env:REPORTS_DIR = "C:\Users\Yokozuna\Dev\Projects"

# 3. ATALHOS E ATRIBUIÇÕES DE DADOS
$global:atalhos = @{
    dev   = "C:\Users\Yokozuna\Dev"
    proj  = "C:\Users\Yokozuna\Dev\Projects"
    back  = "C:\Users\Yokozuna\Dev\Backend"
    ai    = "C:\Users\Yokozuna\Dev\AI"
    labs  = "C:\Users\Yokozuna\Dev\Labs"
    docs  = [Environment]::GetFolderPath('MyDocuments')
    down  = (Join-Path $env:USERPROFILE 'Downloads')
    desk  = [Environment]::GetFolderPath('Desktop')
}

# 4. FUNÇÕES DE NAVEGAÇÃO E NAVEGAÇÃO RÁPIDA
function go {
    param($destino)
    if ($global:atalhos.ContainsKey($destino)) {
        Set-Location $global:atalhos[$destino]
    } elseif (Test-Path $destino) {
        Set-Location $destino
    } else {
        Write-Host "Caminho não encontrado: $destino" -ForegroundColor Red
    }
}

function dev { Set-Location 'C:\Users\Yokozuna\Dev' }
function projects { Set-Location 'C:\Users\Yokozuna\Dev\Projects' }
function backend { Set-Location 'C:\Users\Yokozuna\Dev\Backend' }
function labs { Set-Location 'C:\Users\Yokozuna\Dev\Labs' }
function ai { Set-Location 'C:\Users\Yokozuna\Dev\AI' }

# 5. FUNÇÕES DE SISTEMA E MANIPULAÇÃO DE FICHEIROS
function touch {
    param([string]$path)
    if (Test-Path $path) {
        (Get-Item $path).LastWriteTime = Get-Date
    } else {
        New-Item -Path $path -ItemType File -Force
    }
}

function size {
    param($Path = ".")
    $sizeBytes = (Get-ChildItem $Path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    [PSCustomObject]@{
        Caminho   = (Resolve-Path $Path).Path
        TamanhoGB = if ($sizeBytes) { [math]::Round($sizeBytes / 1GB, 2) } else { 0 }
        TamanhoMB = if ($sizeBytes) { [math]::Round($sizeBytes / 1MB, 2) } else { 0 }
    }
}

function findbig {
    param($Path = ".", $Size = "100MB")
    $sizeBytes = switch -Wildcard ($Size) {
        "*KB" { [int]($Size -replace 'KB','') * 1KB }
        "*MB" { [int]($Size -replace 'MB','') * 1MB }
        "*GB" { [int]($Size -replace 'GB','') * 1GB }
        default { [int]$Size }
    }
    Get-ChildItem $Path -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt $sizeBytes } | Sort-Object Length -Descending
}

function recent {
    param($Path = ".", $Days = 7)
    Get-ChildItem $Path -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-$Days) } | Sort-Object LastWriteTime -Descending
}

function cleantemp {
    Remove-Item -Recurse -Force $env:TEMP\* -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force C:\Windows\Temp\* -ErrorAction SilentlyContinue
    Write-Host "Ficheiros temporários removidos com sucesso." -ForegroundColor Green
}

function pathinfo {
    $path = Get-Location
    Write-Host "Path: $path" -ForegroundColor Cyan
    Write-Host "Pastas: $( (Get-ChildItem -Directory).Count )" -ForegroundColor Green
    Write-Host "Ficheiros: $( (Get-ChildItem -File).Count )" -ForegroundColor Green
    $sizeBytes = (Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if ($sizeBytes) {
        Write-Host "Tamanho: $([math]::Round($sizeBytes/1MB,2)) MB" -ForegroundColor Yellow
    }
}

function mkpath {
    param($path)
    if (-not (Test-Path $path)) {
        New-Item -Path $path -ItemType Directory -Force
        Write-Host "Pasta criada: $path" -ForegroundColor Green
    } else {
        Write-Host "Pasta já existe: $path" -ForegroundColor Yellow
    }
}

function whereis {
    param($comando)
    Get-Command $comando -ErrorAction SilentlyContinue | Select-Object Name, Source
}

function countext {
    param($Path = ".")
    Get-ChildItem $Path -Recurse -File -ErrorAction SilentlyContinue | Group-Object Extension | Select-Object Name, Count | Sort-Object Count -Descending
}

# 6. FUNÇÕES DE ESTRUTURA E ÁRVORE (TREE)
function npp-tree-dir {
    Clear-Host
    Write-Host "Gerando estrutura de PASTAS..." -ForegroundColor Cyan
    tree /A | Out-File -Encoding utf8 tree_dirs.md
    Write-Host "Ficheiro 'tree_dirs.md' criado." -ForegroundColor Green
}

function npp-tree-file {
    Clear-Host
    Write-Host "Gerando estrutura de PASTAS e FICHEIROS..." -ForegroundColor Cyan
    tree /F /A | Out-File -Encoding utf8 tree_full.md
    Write-Host "Ficheiro 'tree_full.md' criado." -ForegroundColor Green
}

function npp-tree-depth {
    param([int]$Depth = 2)
    Clear-Host
    Write-Host "Gerando estrutura com profundidade $Depth..." -ForegroundColor Cyan
    tree /A /F | Select-Object -First (30 + ($Depth * 10)) | Out-File -Encoding utf8 tree_depth.md
    Write-Host "Ficheiro 'tree_depth.md' criado." -ForegroundColor Green
}

function npp-tree-ignore {
    param([string]$Ignore = "node_modules,.git,__pycache__,venv")
    Clear-Host
    Write-Host "Gerando estrutura ignorando: $Ignore" -ForegroundColor Cyan
    $pattern = $Ignore -split ',' | ForEach-Object { "*/$_/*" }
    tree /A /F | Select-String -NotMatch $pattern | Out-File -Encoding utf8 tree_ignore.md
    Write-Host "Ficheiro 'tree_ignore.md' criado." -ForegroundColor Green
}

function npp-tree-custom {
    param(
        [string]$FileName = "estrutura.md",
        [switch]$ShowFiles,
        [int]$Depth = 0
    )
    Clear-Host
    Write-Host "Gerando estrutura personalizada..." -ForegroundColor Cyan
    $params = "/A"
    if ($ShowFiles) { $params += " /F" }
    $output = tree $params
    if ($Depth -gt 0) {
        $output = $output | Select-Object -First (30 + ($Depth * 10))
    }
    $output | Out-File -Encoding utf8 $FileName
    Write-Host "Ficheiro '$FileName' criado." -ForegroundColor Green
}
