$Base = "C:\ACERVO"
Set-Location $Base
Write-Host "ACERVO Gateway" -ForegroundColor Cyan
Write-Host "URL: http://localhost:8080" -ForegroundColor White
Write-Host "Ctrl+C para parar" -ForegroundColor Gray
Write-Host ""
& "$Base\target\release\acervo-gateway.exe"
