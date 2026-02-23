# scripts/init_pms.ps1
# Project Memory System - Inicializacao
# Versao: 1.0
# Data: 17-01-2026
# Projeto: AURORA v6.0 MVP

<#
.SYNOPSIS
    Inicializa o Project Memory System (PMS) para AURORA

.DESCRIPTION
    Cria estrutura completa de pastas e arquivos necessarios
    para sistema de gestao de conhecimento enterprise

.EXAMPLE
    .\init_pms.ps1
#>

param(
    [string]$ProjectRoot = $PSScriptRoot + "\..",
    [switch]$Force
)

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  PROJECT MEMORY SYSTEM (PMS) v1.0 - Inicializacao" -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# Estrutura de diretorios
$directories = @(
    ".pms",
    ".pms/auto_backup",
    "docs",
    "memory",
    "memory/decisions",
    "memory/tasks",
    "memory/tasks/requested",
    "memory/tasks/approved",
    "memory/tasks/in_progress",
    "memory/tasks/completed",
    "memory/tasks/blocked",
    "memory/changes",
    "memory/notes",
    "memory/notes/technical",
    "memory/notes/meetings",
    "memory/notes/ideas",
    ".context"
)

Write-Host "Criando estrutura de diretorios..." -ForegroundColor Yellow

foreach ($dir in $directories) {
    $fullPath = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  [OK] Criado: $dir" -ForegroundColor Green
    } else {
        Write-Host "  [INFO] Existe: $dir" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Criando arquivos de configuracao..." -ForegroundColor Yellow

# Config PMS
$configPath = Join-Path $ProjectRoot ".pms/config.json"
$timestamp = Get-Date -Format "dd-MM-yyyy HH:mm:ss"
$config = @{
    version = "1.0"
    project = "AURORA v6.0 MVP"
    created = $timestamp
    timezone = "Europe/Berlin"
    date_format = "DD-MM-YYYY"
    auto_backup = $true
    backup_interval_minutes = 30
    protocol_level = "RED"
} | ConvertTo-Json -Depth 10

Set-Content -Path $configPath -Value $config -Encoding UTF8
Write-Host "  [OK] Criado: .pms/config.json" -ForegroundColor Green

# Session history
$sessionHistoryPath = Join-Path $ProjectRoot ".pms/session_history.json"
$sessionHistory = @{
    sessions = @()
    last_session = $null
    total_sessions = 0
} | ConvertTo-Json -Depth 10

Set-Content -Path $sessionHistoryPath -Value $sessionHistory -Encoding UTF8
Write-Host "  [OK] Criado: .pms/session_history.json" -ForegroundColor Green

# Indice de decisoes
$decisionsIndexPath = Join-Path $ProjectRoot "memory/decisions/index.json"
$decisionsIndex = @{
    decisions = @()
    last_updated = $timestamp
    total_decisions = 0
} | ConvertTo-Json -Depth 10

Set-Content -Path $decisionsIndexPath -Value $decisionsIndex -Encoding UTF8
Write-Host "  [OK] Criado: memory/decisions/index.json" -ForegroundColor Green

# Indice de mudancas
$changesIndexPath = Join-Path $ProjectRoot "memory/changes/index.json"
$changesIndex = @{
    changes = @()
    last_updated = $timestamp
    total_changes = 0
} | ConvertTo-Json -Depth 10

Set-Content -Path $changesIndexPath -Value $changesIndex -Encoding UTF8
Write-Host "  [OK] Criado: memory/changes/index.json" -ForegroundColor Green

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  [OK] PMS INICIALIZADO COM SUCESSO" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host "  1. Execute: .\scripts\update_context.ps1 -Summary [resumo]" -ForegroundColor White
Write-Host "  2. Edite: docs/00_PROJECT_SCRIPT.md" -ForegroundColor White
Write-Host "  3. Configure: docs/01_GOVERNANCE.md" -ForegroundColor White
Write-Host ""

