# ============================================================================
# SCRIPT DE INÍCIO DO SERVIDOR PRINCIPAL (ARQUITETURA BIG TECH)
# PROJETO: Prometheus v3.0.0
# PROTOCOLO: Omega TIER-0
# ============================================================================

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "SAMSUNG GLOBAL MARKET - SERVIDOR PRINCIPAL" -ForegroundColor Cyan
Write-Host "Arquitetura: Big Tech - Modelo de Serviços Desacoplados" -ForegroundColor Yellow
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

# Verificar se o servidor principal existe
if (-not (Test-Path "Server\main_server.py")) {
    Write-Host "[ERRO] Arquivo Server\main_server.py não encontrado!" -ForegroundColor Red
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
Write-Host "INICIANDO SERVIDOR PRINCIPAL..." -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""
Write-Host "[INFO] Serviços que serão iniciados:" -ForegroundColor Yellow
Write-Host "  1. TradingEngine (Cérebro do Sistema)" -ForegroundColor White
Write-Host "  2. MT5SocketService (Comunicação com EA)" -ForegroundColor White
Write-Host ""
Write-Host "[INFO] Logs serão salvos em: logs\main_server.log" -ForegroundColor Yellow
Write-Host "[INFO] Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host ""
Write-Host "==========================================================================="
Write-Host ""

# Iniciar servidor principal
python Server/main_server.py

Write-Host ""
Write-Host "[INFO] Servidor principal encerrado" -ForegroundColor Yellow

