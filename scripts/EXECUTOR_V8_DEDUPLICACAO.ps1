<#
.SYNOPSIS
    EXECUTOR_V8_DEDUPLICACAO.ps1
    Orquestrador Sequencial Atomico V8 com Bloqueio Automatico e Resumo Global.
    Regra: 1 CSV = 1 Tipo = 1 Relatorio JSON = 1 Validacao = 1 Decisao.
    SE FALHA -> STOP IMEDIATO.
#>

$ErrorActionPreference = "Stop"

$BaseDir       = "C:\ACERVO"
$ScriptsDir    = "$BaseDir\scripts"
$LogsDedupe    = "$BaseDir\logs\deduplicado"
$PythonScript  = "$ScriptsDir\separar_tipo.py"
$GlobalSummary = "$LogsDedupe\resumo_global.json"

# Garantir diretorio de saida
if (-not (Test-Path $LogsDedupe)) {
    New-Item -ItemType Directory -Force -Path $LogsDedupe | Out-Null
}

# Sequencia estrita aprovada (12 tipos por ordem crescente de risco/volume)
$Sequencia = @(
    "database",
    "video",
    "excel",
    "audio",
    "word",
    "pdf",
    "imagem",
    "json",
    "texto",
    "yaml",
    "csv",
    "markdown"
)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  ACERVO V8 - ORQUESTRADOR ATOMICO SEQUENCIAL COM BLOQUEIO RIGIDO     " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$processados = [System.Collections.Generic.List[string]]::new()
$inicioGlobal = Get-Date

foreach ($tipo in $Sequencia) {
    Write-Host "[INICIANDO FASE ATOMICA] Tipo: $tipo" -ForegroundColor Yellow
    
    # 1. Executar o script Python para o tipo exato
    $pythonCmd = "python `"$PythonScript`" $tipo"
    $exitCode = 0
    try {
        & python "$PythonScript" $tipo
        $exitCode = $LASTEXITCODE
    } catch {
        $exitCode = 1
    }

    # 2. Localizar o resumo JSON do tipo gerado
    $resumoTipoPath = "$LogsDedupe\$tipo\resumo_$tipo.json"
    
    if (-not (Test-Path $resumoTipoPath)) {
        Write-Host ""
        Write-Host "[ERRO CRITICO] O ficheiro de resumo nao foi gerado: $resumoTipoPath" -ForegroundColor Red
        
        $estadoGlobal = [ordered]@{
            "timestamp"      = (Get-Date).ToString("o")
            "processados"    = $processados
            "bloqueado_em"   = $tipo
            "motivo"         = "Ficheiro resumo_$tipo.json inexistente"
            "estado_global"  = "FALHA"
        }
        $estadoGlobal | ConvertTo-Json -Depth 5 | Set-Content -Path $GlobalSummary -Encoding UTF8
        Write-Host "[BLOQUEADO] Execucao abortada. Resumo global atualizado." -ForegroundColor Red
        exit 1
    }

    # 3. Ler e auditar o resumo do tipo
    $resumoConteudo = Get-Content -Path $resumoTipoPath -Raw -Encoding UTF8 | ConvertFrom-Json

    # 4. Verificar se passou ou se falhou
    if ($exitCode -ne 0 -or $resumoConteudo.estado -ne "OK") {
        Write-Host ""
        Write-Host "======================================================================" -ForegroundColor Red
        Write-Host "  [BLOQUEIO V8 ATIVADO] Tipo '$tipo' FALHOU na validacao!" -ForegroundColor Red
        Write-Host "  Diferenca: $($resumoConteudo.diferenca)" -ForegroundColor Red
        Write-Host "  Originais: $($resumoConteudo.originais_eleitos)" -ForegroundColor Red
        Write-Host "  Duplicados: $($resumoConteudo.duplicados_marcados)" -ForegroundColor Red
        Write-Host "  Ficheiros Processados: $($resumoConteudo.ficheiros_processados)" -ForegroundColor Red
        Write-Host "======================================================================" -ForegroundColor Red
        
        $motivoFalha = "estado == $($resumoConteudo.estado)"
        if ($resumoConteudo.diferenca -ne 0) { $motivoFalha = "diferenca != 0 ($($resumoConteudo.diferenca))" }
        elseif ($resumoConteudo.originais_eleitos -le 0) { $motivoFalha = "originais_eleitos == 0" }
        elseif ($resumoConteudo.duplicados_marcados -le 0) { $motivoFalha = "duplicados_marcados == 0" }
        elseif (-not $resumoConteudo.validacao_grupos) { $motivoFalha = "validacao_grupos == false" }

        $estadoGlobal = [ordered]@{
            "timestamp"      = (Get-Date).ToString("o")
            "processados"    = $processados
            "bloqueado_em"   = $tipo
            "motivo"         = $motivoFalha
            "detalhes_falha" = $resumoConteudo
            "estado_global"  = "FALHA"
        }
        $estadoGlobal | ConvertTo-Json -Depth 5 | Set-Content -Path $GlobalSummary -Encoding UTF8
        Write-Host ""
        Write-Host "[STOP] O resumo global foi atualizado em: $GlobalSummary" -ForegroundColor Red
        Write-Host "[STOP] Nenhum tipo subsequente sera executado." -ForegroundColor Red
        exit 1
    }

    # 5. Adicionar a lista de processados com sucesso
    $processados.Add($tipo)
    Write-Host "  [OK] $tipo validado com sucesso! Duracao: $($resumoConteudo.duracao_segundos)s" -ForegroundColor Green

    # 6. Atualizar resumo global incremental a cada tipo
    $estadoGlobal = [ordered]@{
        "timestamp"      = (Get-Date).ToString("o")
        "processados"    = $processados
        "bloqueado_em"   = $null
        "motivo"         = $null
        "ultimo_tipo_ok" = $tipo
        "estado_global"  = if ($processados.Count -eq $Sequencia.Count) { "CONCLUIDO" } else { "EM_PROGRESSO" }
    }
    $estadoGlobal | ConvertTo-Json -Depth 5 | Set-Content -Path $GlobalSummary -Encoding UTF8
    Write-Host "  [GLOBAL] resumo_global.json atualizado ($($processados.Count)/$($Sequencia.Count))." -ForegroundColor DarkGray
    Write-Host ""
}

$fimGlobal = Get-Date
$duracaoTotal = [math]::Round(($fimGlobal - $inicioGlobal).TotalSeconds, 2)

Write-Host "======================================================================" -ForegroundColor Green
Write-Host "  ACERVO V8 - TODOS OS 12 TIPOS PROCESSADOS E AUDITADOS COM SUCESSO!  " -ForegroundColor Green
Write-Host "  Duracao Total: ${duracaoTotal}s                                      " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
