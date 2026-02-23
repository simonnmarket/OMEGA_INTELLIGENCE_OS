# scripts/load_context.ps1
# Project Memory System - Carregar Contexto
# Versao: 1.0
# Uso: Executar no inicio de cada nova sessao

<#
.SYNOPSIS
    Carrega contexto do projeto para TECH LEAD

.DESCRIPTION
    Exibe resumo completo do estado atual do projeto.
    TECH LEAD deve ler este output no inicio da sessao.

.PARAMETER Detailed
    Mostra informacoes adicionais (tarefas, decisoes, bloqueadores)

.EXAMPLE
    .\load_context.ps1
    .\load_context.ps1 -Detailed
#>

param(
    [string]$ProjectRoot = $PSScriptRoot + "\..",
    [switch]$Detailed
)

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  CARREGANDO CONTEXTO DO PROJETO" -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# Ler status atual
$currentStatusPath = Join-Path $ProjectRoot ".context/CURRENT_STATUS.md"
if (Test-Path $currentStatusPath) {
    Write-Host "STATUS ATUAL:" -ForegroundColor Green
    Write-Host ""
    Get-Content $currentStatusPath
    Write-Host ""
} else {
    Write-Host "[AVISO] .context/CURRENT_STATUS.md nao encontrado!" -ForegroundColor Yellow
    Write-Host "   Execute: .\scripts\init_pms.ps1" -ForegroundColor White
    Write-Host ""
}

# Se detailed, mostrar mais informacoes
if ($Detailed) {
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host "  INFORMACOES ADICIONAIS" -ForegroundColor White
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Tarefas em progresso
    $inProgressPath = Join-Path $ProjectRoot "memory/tasks/in_progress"
    if (Test-Path $inProgressPath) {
        $tasks = Get-ChildItem $inProgressPath -Filter "*.md" -ErrorAction SilentlyContinue
        if ($tasks.Count -gt 0) {
            Write-Host "TAREFAS EM PROGRESSO:" -ForegroundColor Yellow
            foreach ($task in $tasks) {
                Write-Host "  - $($task.BaseName)" -ForegroundColor White
            }
            Write-Host ""
        } else {
            Write-Host "TAREFAS EM PROGRESSO: Nenhuma" -ForegroundColor Gray
            Write-Host ""
        }
    }
    
    # Ultimas decisoes
    $decisionsIndexPath = Join-Path $ProjectRoot "memory/decisions/index.json"
    if (Test-Path $decisionsIndexPath) {
        $decisionsIndex = Get-Content $decisionsIndexPath -Raw | ConvertFrom-Json
        if ($decisionsIndex.decisions.Count -gt 0) {
            $lastDecisions = $decisionsIndex.decisions | Select-Object -Last 3
            Write-Host "ULTIMAS DECISOES DO CONSELHO:" -ForegroundColor Yellow
            foreach ($decision in $lastDecisions) {
                Write-Host "  - [$($decision.date)] $($decision.summary)" -ForegroundColor White
            }
            Write-Host ""
        } else {
            Write-Host "DECISOES DO CONSELHO: Nenhuma registrada" -ForegroundColor Gray
            Write-Host ""
        }
    }
    
    # Historico de sessoes
    $sessionHistoryPath = Join-Path $ProjectRoot ".pms/session_history.json"
    if (Test-Path $sessionHistoryPath) {
        $sessionHistory = Get-Content $sessionHistoryPath -Raw | ConvertFrom-Json
        Write-Host "HISTORICO DE SESSOES:" -ForegroundColor Yellow
        Write-Host "  Total de sessoes: $($sessionHistory.total_sessions)" -ForegroundColor White
        Write-Host "  Ultima sessao: $($sessionHistory.last_session)" -ForegroundColor White
        Write-Host ""
    }
    
    # Bloqueadores
    $nextStepsPath = Join-Path $ProjectRoot ".context/NEXT_STEPS.md"
    if (Test-Path $nextStepsPath) {
        Write-Host "BLOQUEADORES E PROXIMOS PASSOS:" -ForegroundColor Red
        Write-Host ""
        Get-Content $nextStepsPath
        Write-Host ""
    }
}

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  [OK] CONTEXTO CARREGADO" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dica: Use -Detailed para mais informacoes" -ForegroundColor Gray
Write-Host ""

