Get-Process acervo-gateway, python -EA 0 | Stop-Process -Force -EA 0
foreach ($porta in @(5173, 5174, 8080)) {
    $conn = Get-NetTCPConnection -LocalPort $porta -State Listen -EA 0
    if ($conn) {
        foreach ($pid in ($conn.OwningProcess | Select-Object -Unique)) {
            Stop-Process -Id $pid -Force -EA 0
        }
    }
}
Write-Host "Todos os servidores parados" -ForegroundColor Green
