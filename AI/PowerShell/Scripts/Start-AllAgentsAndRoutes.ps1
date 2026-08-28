<#
.SYNOPSIS
    Executor Mestre Nativo PowerShell: Todos os Agentes e Rotas Canonicas.
.DESCRIPTION
    Executa a cadeia deterministica completa dos 14 estagios:
    Higienizacao, Scanner dos 6 Agentes Canonicos, Loops A-D, Factualidade,
    Remediacao, Eval Pipeline, Vetores, Frozen Judge 100/100, Controlador de Workflow,
    Sincronizacao de Outputs e Geracao do Dossier Executivo e Forense.
#>

[CmdletBinding()]
param(
    [string]$DevRoot = "C:\Users\Yokozuna\Dev"
)

$ErrorActionPreference = "Continue"
$StartTime = Get-Date

$SkillsDir = Join-Path $DevRoot "AI\skills\mcp-fs-pydantic-org\scripts"
$CanonicalRoot = Join-Path $DevRoot "Projects\Ficheiros Escritos Canónicos"
$IndexDir = Join-Path $CanonicalRoot "_index"
$CentralDir = Join-Path $DevRoot "OUTPUT_CENTRALIZADO"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " EXECUTOR MESTRE DETERMINISTICO: TODOS OS AGENTES E ROTAS (PS)" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Raiz Dev     : $DevRoot"
Write-Host " Acervo       : $CanonicalRoot"
Write-Host " Indice       : $IndexDir"
Write-Host " Central      : $CentralDir"
Write-Host " Versao       : v2.5.0-PROD"
Write-Host "=================================================================="

$Stages = @(
    @{ Name = "01/14 - Higienizacao e Simplificacao"; Script = "sanitize_and_simplify.py"; Args = @() },
    @{ Name = "02/14 - Mapa Estrutural tree_dirs.md"; Script = "generate_tree.py"; Args = @() },
    @{ Name = "03/14 - Scanner dos 6 Agentes Canonicos"; Script = "run_act_agents.py"; Args = @("--root", $CanonicalRoot, "--hash", "--out", $IndexDir) },
    @{ Name = "04/14 - Loop de Validacao Pydantic (A-D)"; Script = "optimize_and_validate_loop.py"; Args = @("--index-dir", $IndexDir) },
    @{ Name = "05/14 - Loop Factual e Matriz de Relevancia"; Script = "factual_relevance_loop.py"; Args = @() },
    @{ Name = "06/14 - Auto-Correcao de Erros e Sanidade"; Script = "error_remediation_handler.py"; Args = @() },
    @{ Name = "07/14 - Agente de Qualidade e Factualidade"; Script = "agent_quality_factuality.py"; Args = @() },
    @{ Name = "08/14 - Eval Pipeline (Golden Dataset)"; Script = "eval_pipeline.py"; Args = @() },
    @{ Name = "09/14 - Indexador Vetorial RAG"; Script = "vector_index.py"; Args = @() },
    @{ Name = "10/14 - Frozen Judge (100/100) & Cronologia"; Script = "frozen_judge.py"; Args = @() },
    @{ Name = "11/14 - Controlador de Workflow"; Script = "workflow_controller.py"; Args = @() },
    @{ Name = "12/14 - Sincronizacao de Outputs"; Script = "centralize_outputs.py"; Args = @() },
    @{ Name = "13/14 - Compilacao do Dossier Forense"; Script = "generate_full_dossier.py"; Args = @() }
)

foreach ($stage in $Stages) {
    Write-Host "`n------------------------------------------------------------------" -ForegroundColor Yellow
    Write-Host " Executando: $($stage.Name)" -ForegroundColor Yellow
    Write-Host " Script    : $($stage.Script)" -ForegroundColor DarkGray
    Write-Host "------------------------------------------------------------------"
    
    $scriptPath = Join-Path $SkillsDir $stage.Script
    if (Test-Path $scriptPath) {
        & python $scriptPath $stage.Args
    } else {
        Write-Host "[AVISO] Script nao encontrado: $scriptPath" -ForegroundColor Red
    }
}

$EndTime = Get-Date
$Duration = $EndTime - $StartTime

Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host " [SUCESSO] EXECUCAO COMPLETA DE TODOS OS AGENTES E ROTAS!" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host " Duracao Total : $($Duration.Minutes)m $($Duration.Seconds)s"
Write-Host " Dossie HTML   : $CentralDir\DOSSIER_EXECUTIVO_FORENSE.html"
Write-Host " Dossie MD     : $CentralDir\DOSSIER_EXECUTIVO_FORENSE_CONSOLIDADO.md"
Write-Host " Dossie JSON   : $CentralDir\02_DADOS_ESTRUTURADOS\dossier_consolidado.json"
Write-Host "=================================================================="
