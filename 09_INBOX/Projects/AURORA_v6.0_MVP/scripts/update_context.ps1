# scripts/update_context.ps1
# Project Memory System - Atualizacao de Contexto
# Versao: 1.0
# Protocolo: VERMELHO (Obrigatorio antes de encerrar sessao)

<#
.SYNOPSIS
    Atualiza contexto do projeto (PROTOCOLO VERMELHO)

.DESCRIPTION
    Script obrigatorio para executar ao fim de cada sessao.
    Atualiza CURRENT_STATUS.md, LAST_SESSION.md e cria backup.

.PARAMETER Summary
    Resumo das atividades da sessao

.PARAMETER NextSteps
    Proximos passos definidos

.EXAMPLE
    .\update_context.ps1 -Summary "Implementado PMS" -NextSteps "Testar sistema amanha"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Summary,
    
    [Parameter(Mandatory=$false)]
    [string]$NextSteps = "Definir na proxima sessao",
    
    [string]$ProjectRoot = $PSScriptRoot + "\.."
)

$timestamp = Get-Date -Format "dd-MM-yyyy HH:mm:ss"
$date = Get-Date -Format "dd-MM-yyyy"
$dateFile = Get-Date -Format "yyyy-MM-dd"

Write-Host ""
Write-Host "PROTOCOLO VERMELHO - Atualizacao Obrigatoria" -ForegroundColor Red
Write-Host "=======================================================" -ForegroundColor Red
Write-Host ""

# 1. Atualizar CURRENT_STATUS.md
Write-Host "Atualizando CURRENT_STATUS.md..." -ForegroundColor Yellow

$currentStatusPath = Join-Path $ProjectRoot ".context/CURRENT_STATUS.md"
$currentStatus = @"
# STATUS ATUAL DO PROJETO

**Ultima atualizacao:** $timestamp (Berlin)
**Projeto:** AURORA v6.0 MVP
**Protocolo:** PMS v1.0

---

## RESUMO EXECUTIVO

$Summary

---

## ESTRUTURA ORGANIZACIONAL

- **CEO:** Responsavel por decisoes estrategicas e validacao
- **CQO:** Responsavel por qualidade e padroes
- **CTO:** Responsavel por arquitetura e tecnologia
- **TECH LEAD:** Responsavel por implementacao

---

## PROXIMOS PASSOS

$NextSteps

---

## BLOQUEADORES CONHECIDOS

[Atualizar manualmente conforme necessario]

---

## LOCALIZACAO NO ROADMAP

[Atualizar manualmente: Fase X, Tarefa Y]

---

## REFERENCIAS RAPIDAS

- **Inventario:** docs/02_INVENTORY.md
- **Decisoes:** memory/decisions/index.json
- **Tarefas Ativas:** memory/tasks/in_progress/
- **Ultima Sessao:** .context/LAST_SESSION.md

---

**IMPORTANTE:** Este arquivo e atualizado automaticamente pelo PROTOCOLO VERMELHO.
Para contexto historico, consulte .context/LAST_SESSION.md ou memory/changes/
"@

Set-Content -Path $currentStatusPath -Value $currentStatus -Encoding UTF8
Write-Host "  [OK] Atualizado: .context/CURRENT_STATUS.md" -ForegroundColor Green

# 2. Salvar sessao anterior
Write-Host ""
Write-Host "Salvando sessao anterior..." -ForegroundColor Yellow

$lastSessionPath = Join-Path $ProjectRoot ".context/LAST_SESSION.md"
if (Test-Path $currentStatusPath) {
    $lastSessionBackup = Join-Path $ProjectRoot ".pms/auto_backup/session_${dateFile}.md"
    Copy-Item -Path $currentStatusPath -Destination $lastSessionBackup -Force
    Copy-Item -Path $currentStatusPath -Destination $lastSessionPath -Force
    Write-Host "  [OK] Backup: .pms/auto_backup/session_${dateFile}.md" -ForegroundColor Green
}

# 3. Atualizar historico de sessoes
Write-Host ""
Write-Host "Atualizando historico..." -ForegroundColor Yellow

$sessionHistoryPath = Join-Path $ProjectRoot ".pms/session_history.json"
if (Test-Path $sessionHistoryPath) {
    $sessionHistory = Get-Content $sessionHistoryPath -Raw | ConvertFrom-Json
    
    $newSession = @{
        timestamp = $timestamp
        date = $date
        summary = $Summary
        next_steps = $NextSteps
    }
    
    # Adicionar nova sessao ao array
    $sessions = @($sessionHistory.sessions)
    $sessions += $newSession
    $sessionHistory.sessions = $sessions
    $sessionHistory.last_session = $timestamp
    $sessionHistory.total_sessions = $sessions.Count
    
    $sessionHistory | ConvertTo-Json -Depth 10 | Set-Content $sessionHistoryPath -Encoding UTF8
    Write-Host "  [OK] Historico atualizado" -ForegroundColor Green
}

# 4. Criar log de mudancas do dia
Write-Host ""
Write-Host "Criando log de mudancas..." -ForegroundColor Yellow

$changesPath = Join-Path $ProjectRoot "memory/changes/${dateFile}_changes.md"
$changesContent = @"

---

# Mudancas - $date

**Timestamp:** $timestamp

## Resumo

$Summary

## Proximos Passos

$NextSteps

## Detalhes Tecnicos

[Adicionar manualmente conforme necessario]

---
*Gerado automaticamente pelo PROTOCOLO VERMELHO*
"@

Add-Content -Path $changesPath -Value $changesContent -Encoding UTF8
Write-Host "  [OK] Log: memory/changes/${dateFile}_changes.md" -ForegroundColor Green

# 5. Atualizar indice de mudancas
$changesIndexPath = Join-Path $ProjectRoot "memory/changes/index.json"
if (Test-Path $changesIndexPath) {
    $changesIndex = Get-Content $changesIndexPath -Raw | ConvertFrom-Json
    
    $newChange = @{
        date = $date
        timestamp = $timestamp
        summary = $Summary
        file = "${dateFile}_changes.md"
    }
    
    $changes = @($changesIndex.changes)
    $changes += $newChange
    $changesIndex.changes = $changes
    $changesIndex.last_updated = $timestamp
    $changesIndex.total_changes = $changes.Count
    
    $changesIndex | ConvertTo-Json -Depth 10 | Set-Content $changesIndexPath -Encoding UTF8
}

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Red
Write-Host "  [OK] PROTOCOLO VERMELHO EXECUTADO COM SUCESSO" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Red
Write-Host ""
Write-Host "Contexto atualizado em:" -ForegroundColor White
Write-Host "  - .context/CURRENT_STATUS.md" -ForegroundColor Cyan
Write-Host "  - .context/LAST_SESSION.md" -ForegroundColor Cyan
Write-Host "  - .pms/auto_backup/session_${dateFile}.md" -ForegroundColor Cyan
Write-Host "  - memory/changes/${dateFile}_changes.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "Sessao encerrada com seguranca." -ForegroundColor Red
Write-Host ""

