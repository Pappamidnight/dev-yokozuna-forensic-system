<#
.SYNOPSIS
    V8_Verificar_Ferramentas_Linux.ps1
    Verifica a disponibilidade das ferramentas forenses Linux via WSL:
    fdupes, rdfind, rmlint
#>

$distro = "Ubuntu-26.04"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  ACERVO V8 - AUDITORIA DE FERRAMENTAS FORENSES WSL ($distro)         " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$ferramentas = @("fdupes", "rdfind", "rmlint")

foreach ($tool in $ferramentas) {
    try {
        $check = wsl -d $distro -- which $tool 2>$null
        if ($check) {
            $ver = wsl -d $distro -- $tool --version 2>&1 | Select-Object -First 1
            Write-Host "  [OK] $tool : Disponivel ($ver)" -ForegroundColor Green
        } else {
            Write-Host "  [AVISO] $tool : Nao instalado. Para instalar: wsl -d $distro -- sudo apt update && sudo apt install -y $tool" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  [ERRO] Falha ao testar $tool via WSL: $_" -ForegroundColor Red
    }
}
Write-Host "======================================================================" -ForegroundColor Cyan
