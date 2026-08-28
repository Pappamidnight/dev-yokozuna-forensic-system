<#
.SYNOPSIS
    Inicia o Pipeline de Ingestao Societaria SPARK / Venture Partners (PowerShell).
#>

$DevRoot = "C:\Users\Yokozuna\Dev"
$ProjDir = "$DevRoot\Projects\INGESTAO_SPARK_VENTURE"
$ScriptPath = "$ProjDir\ingestao_spark.py"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "INICIANDO INGESTAO SOCIETARIA: GRUPO SPARK / VENTURE PARTNERS" -ForegroundColor Green
Write-Host "Raiz: $ProjDir" -ForegroundColor Gray
Write-Host "==================================================================" -ForegroundColor Cyan

Set-Location $DevRoot
python $ScriptPath --root $ProjDir
