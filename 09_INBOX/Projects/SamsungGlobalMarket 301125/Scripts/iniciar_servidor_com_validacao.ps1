# Iniciar servidor com validacao completa
$ErrorActionPreference = "Stop"

$projectPath = Split-Path -Parent $PSScriptRoot
$serverPath = Join-Path $projectPath "Server\server_file_based_v2.0.0.py"
$mt5Path = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "INICIALIZACAO COMPLETA DO SERVIDOR FILE-BASED" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""

# 1. Parar processos anteriores
Write-Host "[1] Parando processos Python anteriores..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "  OK" -ForegroundColor Green
Write-Host ""

# 2. Verificar diretorio
Write-Host "[2] Verificando diretorio MT5..." -ForegroundColor Yellow
if (-not (Test-Path $mt5Path)) {
    Write-Host "  Criando diretorio..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $mt5Path -Force | Out-Null
}
Write-Host "  Diretorio: $mt5Path" -ForegroundColor Cyan
Write-Host "  OK" -ForegroundColor Green
Write-Host ""

# 3. Ativar venv se existir
Set-Location $projectPath
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[3] Ativando ambiente virtual..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
    Write-Host "  OK" -ForegroundColor Green
    Write-Host ""
}

# 4. Iniciar servidor em background
Write-Host "[4] Iniciando servidor..." -ForegroundColor Yellow
$process = Start-Process python -ArgumentList $serverPath, $mt5Path -PassThru -NoNewWindow -RedirectStandardOutput "$projectPath\logs\server_output.txt" -RedirectStandardError "$projectPath\logs\server_error.txt"
Write-Host "  PID: $($process.Id)" -ForegroundColor Cyan
Write-Host "  OK - Aguardando inicializacao..." -ForegroundColor Green
Start-Sleep -Seconds 3
Write-Host ""

# 5. Validar que processo esta rodando
Write-Host "[5] Validando processo..." -ForegroundColor Yellow
$stillRunning = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
if ($stillRunning) {
    Write-Host "  OK - Servidor rodando (PID: $($process.Id))" -ForegroundColor Green
} else {
    Write-Host "  ERRO - Servidor nao esta rodando!" -ForegroundColor Red
    Write-Host "  Verifique logs:" -ForegroundColor Yellow
    Write-Host "    logs\server_error.txt" -ForegroundColor Cyan
    Write-Host "    logs\server_output.txt" -ForegroundColor Cyan
    exit 1
}
Write-Host ""

# 6. Aguardar processamento de requests existentes
Write-Host "[6] Aguardando processamento de requests..." -ForegroundColor Yellow
$reqs = Get-ChildItem -Path $mt5Path -Filter "AIRequest.*.json" -ErrorAction SilentlyContinue
if ($reqs) {
    Write-Host "  Encontrados $($reqs.Count) request(s) - aguardando processamento..." -ForegroundColor Cyan
    $timeout = 15
    $countdown = $timeout
    $processed = $false
    
    while ($countdown -gt 0 -and -not $processed) {
        Start-Sleep -Seconds 1
        $countdown--
        $remainingReqs = (Get-ChildItem -Path $mt5Path -Filter "AIRequest.*.json" -ErrorAction SilentlyContinue).Count
        $newResps = (Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue).Count
        
        if ($remainingReqs -eq 0 -or $newResps -gt 0) {
            $processed = $true
            Write-Host "  OK - Requests processados!" -ForegroundColor Green
            Write-Host "    Responses criados: $newResps" -ForegroundColor Cyan
        } else {
            Write-Host "  Aguardando... ($countdown s restantes)" -ForegroundColor Gray
        }
    }
    
    if (-not $processed) {
        Write-Host "  AVISO - Requests ainda nao processados apos $timeout segundos" -ForegroundColor Yellow
        Write-Host "    Verifique logs do servidor" -ForegroundColor Cyan
    }
} else {
    Write-Host "  Nenhum request encontrado - OK" -ForegroundColor Green
}
Write-Host ""

# 7. Resumo final
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "SERVIDOR INICIADO E VALIDADO" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host "PID: $($process.Id)" -ForegroundColor Cyan
Write-Host "Diretorio: $mt5Path" -ForegroundColor Cyan
Write-Host ""
Write-Host "Monitorar status:" -ForegroundColor Yellow
Write-Host "  .\Scripts\verificar_estado_completo.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ver logs em tempo real:" -ForegroundColor Yellow
Write-Host "  Get-Content logs\server_output.txt -Wait" -ForegroundColor Cyan
Write-Host ""

