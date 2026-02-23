# MEMORY_ID: TASK_AUTOMATION_MONITORING
# TIMESTAMP: 09-11-2025 21:37 CET
# AUTHOR: Cursor_Omega

<#
.SYNOPSIS
    Executa o Core Prometheus em modo CLI.

.NOTES
    Pode ser agendado via Windows Task Scheduler.
#>

param(
    [string]$ProjectRoot = "$PSScriptRoot\.."
)

Set-Location $ProjectRoot

Write-Host "[Prometheus] Inicializando Core.Main..." -ForegroundColor Cyan
python -m Core.Main
Write-Host "[Prometheus] Execução concluída." -ForegroundColor Green

