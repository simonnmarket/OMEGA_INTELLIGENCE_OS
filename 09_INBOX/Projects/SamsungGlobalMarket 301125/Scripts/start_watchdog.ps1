# ============================================================================
# SCRIPT DE INÍCIO DO WATCHDOG - WINDOWS
# PROJETO: Samsung Global Market
# PROTOCOLO: Omega TIER-0
# ============================================================================

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "WATCHDOG DO SERVIDOR MT5 - SISTEMA 24/7" -ForegroundColor Cyan
Write-Host "==========================================================================="
Write-Host ""

# Verificar se o ambiente virtual existe
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[ERRO] Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host "[INFO] Execute: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Ativar ambiente virtual
Write-Host "[INFO] Ativando ambiente virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Verificar se o script do watchdog existe
if (-not (Test-Path "server_watchdog.py")) {
    Write-Host "[ERRO] Arquivo server_watchdog.py não encontrado!" -ForegroundColor Red
    exit 1
}

# Verificar se o servidor existe
if (-not (Test-Path "simple_mt5_server.py")) {
    Write-Host "[ERRO] Arquivo simple_mt5_server.py não encontrado!" -ForegroundColor Red
    exit 1
}

# Parar processos Python antigos (se houver)
Write-Host "[INFO] Verificando processos Python anteriores..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "[INFO] Encontrados $($pythonProcesses.Count) processo(s) Python" -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "[OK] Processos anteriores parados" -ForegroundColor Green
}

# Criar diretório de logs
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "[OK] Diretório de logs criado" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================================================="
Write-Host "INICIANDO WATCHDOG..." -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""
Write-Host "[INFO] O watchdog irá:" -ForegroundColor Yellow
Write-Host "  - Monitorar o servidor 24/7" -ForegroundColor White
Write-Host "  - Reiniciar automaticamente em caso de falha" -ForegroundColor White
Write-Host "  - Preservar estado e progresso" -ForegroundColor White
Write-Host "  - Salvar logs em logs/watchdog.log" -ForegroundColor White
Write-Host ""
Write-Host "[INFO] Pressione Ctrl+C para parar o watchdog" -ForegroundColor Yellow
Write-Host ""
Write-Host "==========================================================================="
Write-Host ""

# Iniciar watchdog
python server_watchdog.py

Write-Host ""
Write-Host "[INFO] Watchdog encerrado" -ForegroundColor Yellow

