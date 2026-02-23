# ============================================================================
# INICIAR SERVIDOR FILE-BASED v2.0.0
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "INICIANDO SERVIDOR FILE-BASED v2.0.0" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""

# Verificar se já está rodando
$existingProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $procInfo = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" | Select-Object CommandLine
    $procInfo.CommandLine -like "*server_file_based*"
}

if ($existingProcess) {
    Write-Host "[INFO] Servidor já está rodando (PID: $($existingProcess.Id))" -ForegroundColor Yellow
    Write-Host "[INFO] Parando processo anterior..." -ForegroundColor Yellow
    $existingProcess | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Caminho do diretório do projeto
$projectPath = Split-Path -Parent $PSScriptRoot

# Caminho do servidor
$serverPath = Join-Path $projectPath "Server\server_file_based_v2.0.0.py"

if (-not (Test-Path $serverPath)) {
    Write-Host "[ERRO] Arquivo do servidor não encontrado: $serverPath" -ForegroundColor Red
    exit 1
}

# Caminho do diretório MT5 Common/Files
$mt5Path = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"

Write-Host "[INFO] Caminho do servidor: $serverPath" -ForegroundColor Cyan
Write-Host "[INFO] Diretório MT5 Files: $mt5Path" -ForegroundColor Cyan
Write-Host ""

# Verificar se diretório existe
if (-not (Test-Path $mt5Path)) {
    Write-Host "[AVISO] Diretório MT5 não encontrado. Criando..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $mt5Path -Force | Out-Null
    Write-Host "[OK] Diretório criado" -ForegroundColor Green
}

# Mudar para diretório do projeto
Set-Location $projectPath

# Iniciar servidor em nova janela
$scriptBlock = {
    param($serverPath, $mt5Path)
    Set-Location (Split-Path $serverPath)
    python $serverPath $mt5Path
}

# Criar arquivo temporário com caminho para passar como argumento
$tempScript = Join-Path $env:TEMP "start_server_file_based.ps1"
@"
# Iniciar servidor com caminho do MT5
`$serverPath = '$serverPath'
`$mt5Path = '$mt5Path'

Write-Host '===========================================================================' -ForegroundColor Cyan
Write-Host 'SAMSUNG GLOBAL MARKET - SERVIDOR FILE-BASED v2.0.0' -ForegroundColor Green
Write-Host '===========================================================================' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Diretório MT5: ' -NoNewline
Write-Host `$mt5Path -ForegroundColor Cyan
Write-Host ''
Write-Host 'Pressione Ctrl+C para parar' -ForegroundColor Yellow
Write-Host ''

# Iniciar servidor com caminho hardcoded (modificar server para aceitar como argumento)
Set-Location (Split-Path `$serverPath)

# Modificar temporariamente o server para aceitar caminho como argumento
python `$serverPath
"@ | Out-File -FilePath $tempScript -Encoding UTF8

# Iniciar em nova janela
Start-Process powershell.exe -ArgumentList "-NoExit", "-File", $tempScript

Write-Host "[OK] Servidor iniciado em nova janela" -ForegroundColor Green
Write-Host "[INFO] Verifique a janela do servidor para logs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para verificar status, execute: .\Scripts\auditoria_tempo_real.ps1" -ForegroundColor Yellow

