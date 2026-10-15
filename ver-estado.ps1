$Base = "C:\ACERVO"
Write-Host "=== ACERVO ===" -ForegroundColor Cyan
$storage = Get-ChildItem "$Base\storage" -Recurse -File -EA 0
$tamanho = ($storage | Measure-Object Length -Sum).Sum
Write-Host "Storage: $($storage.Count) ficheiros ($([math]::Round($tamanho / 1GB, 2)) GB)"
$db = "$Base\db\acervo.db"
$total = sqlite3 $db "SELECT COUNT(*) FROM ficheiros;" 2>$null
Write-Host "DB: $total registos"
$gw = Get-Process acervo-gateway -EA 0
Write-Host "Gateway: $(if ($gw) { "ON (PID $($gw.Id))" } else { "OFF" })"
Write-Host ""
Get-ChildItem "$Base\*.ps1" | Select-Object Name
