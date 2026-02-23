# Iniciar servidor file-based automaticamente

$projectPath = Split-Path -Parent $PSScriptRoot
$serverPath = Join-Path $projectPath "Server\server_file_based_v2.0.0.py"
$mt5Path = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "INICIANDO SERVIDOR FILE-BASED v2.0.0 (AUTOMATICO)" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""
Write-Host "Caminho MT5: $mt5Path" -ForegroundColor Cyan
Write-Host ""

Set-Location $projectPath

# Ativar venv se existir
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
}

# Iniciar servidor
python $serverPath $mt5Path

