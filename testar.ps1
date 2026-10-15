Write-Host "=== TESTAR GATEWAY ===" -ForegroundColor Cyan
$ok = 0; $fail = 0
foreach ($ep in @("/api/health", "/api/status", "/api/files/1")) {
    try {
        $r = Invoke-RestMethod "http://localhost:8080$ep" -TimeoutSec 3
        Write-Host "OK $ep" -ForegroundColor Green
        $ok++
    } catch {
        Write-Host "FAIL $ep" -ForegroundColor Red
        $fail++
    }
}
Write-Host ""
Write-Host "OK: $ok | FAIL: $fail" -ForegroundColor $(if ($fail -eq 0) { "Green" } else { "Yellow" })
