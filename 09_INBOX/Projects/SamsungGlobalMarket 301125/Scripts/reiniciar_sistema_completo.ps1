# Script para reiniciar todo o sistema após falha
param(
    [switch]$AutoStart = $false
)

$ErrorActionPreference = "Continue"
$projectPath = Split-Path -Parent $PSScriptRoot

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "REINICIANDO SISTEMA COMPLETO" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""

# 1. Limpar processos antigos
Write-Host "[1] Limpando processos antigos..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "  Processos Python encerrados" -ForegroundColor Green
Start-Sleep -Seconds 2
Write-Host ""

# 2. Limpar arquivos antigos
Write-Host "[2] Limpando arquivos MT5 antigos..." -ForegroundColor Yellow
$mt5Path = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"
if (Test-Path $mt5Path) {
    Remove-Item (Join-Path $mt5Path "AIRequest.*.json") -Force -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $mt5Path "AIResponse.*.json") -Force -ErrorAction SilentlyContinue
    Write-Host "  Arquivos antigos removidos" -ForegroundColor Green
} else {
    Write-Host "  Diretorio MT5 nao encontrado - sera criado pelo EA" -ForegroundColor Yellow
}
Write-Host ""

# 3. Iniciar servidor
Write-Host "[3] Iniciando servidor Python..." -ForegroundColor Yellow
Set-Location $projectPath
$serverPath = Join-Path $projectPath "Server\server_file_based_v2.0.0.py"

if (-not (Test-Path $serverPath)) {
    Write-Host "  ERRO: Servidor nao encontrado em $serverPath" -ForegroundColor Red
    exit 1
}

# Ativar venv se existir
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
    Write-Host "  Virtual environment ativado" -ForegroundColor Green
}

# Iniciar servidor
Start-Process python -ArgumentList $serverPath, $mt5Path -WindowStyle Minimized
Start-Sleep -Seconds 3

$proc = Get-Process python -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "  Servidor iniciado (PID: $($proc.Id))" -ForegroundColor Green
} else {
    Write-Host "  ERRO: Servidor nao iniciou!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 4. Verificar MetaTrader
Write-Host "[4] Verificando MetaTrader 5..." -ForegroundColor Yellow
$mt5Process = Get-Process terminal64 -ErrorAction SilentlyContinue
if ($mt5Process) {
    Write-Host "  MetaTrader ja esta rodando" -ForegroundColor Green
} else {
    Write-Host "  MetaTrader NAO esta rodando" -ForegroundColor Red
    Write-Host ""
    Write-Host "  ACAO NECESSARIA:" -ForegroundColor Yellow
    Write-Host "    1. Abra o MetaTrader 5 manualmente" -ForegroundColor Cyan
    Write-Host "    2. Faca login na conta demo/real" -ForegroundColor Cyan
    Write-Host "    3. Anexe o EA ao grafico:" -ForegroundColor Cyan
    Write-Host "       - Abra grafico BTCUSD M5" -ForegroundColor Cyan
    Write-Host "       - Arraste 'SamsungGlobalMarket_EA_v2.0.0_FILE_BASED' ao grafico" -ForegroundColor Cyan
    Write-Host "       - Confirme os parametros" -ForegroundColor Cyan
    Write-Host ""
    
    if ($AutoStart) {
        Write-Host "  Tentando iniciar MetaTrader automaticamente..." -ForegroundColor Yellow
        # Tentar encontrar o executavel do MT5
        $mt5Paths = @(
            "C:\Program Files\MetaTrader 5\terminal64.exe",
            "C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
            "$env:ProgramFiles\MetaTrader 5\terminal64.exe",
            "${env:ProgramFiles(x86)}\MetaTrader 5\terminal64.exe"
        )
        
        $mt5Exe = $null
        foreach ($path in $mt5Paths) {
            if (Test-Path $path) {
                $mt5Exe = $path
                break
            }
        }
        
        if ($mt5Exe) {
            Start-Process $mt5Exe
            Write-Host "  MetaTrader iniciado. Aguarde carregar..." -ForegroundColor Green
            Write-Host "  Depois anexe o EA manualmente ao grafico" -ForegroundColor Yellow
        } else {
            Write-Host "  Executavel do MT5 nao encontrado automaticamente" -ForegroundColor Red
            Write-Host "  Por favor, inicie manualmente" -ForegroundColor Yellow
        }
    }
}
Write-Host ""

# 5. Iniciar monitoramento
Write-Host "[5] Iniciando sistema de monitoramento..." -ForegroundColor Yellow

$monitorScript = Join-Path $projectPath "Scripts\monitor_realtime_background.ps1"
if (Test-Path $monitorScript) {
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $monitorScript -WindowStyle Normal
    Write-Host "  Monitor em tempo real iniciado" -ForegroundColor Green
} else {
    Write-Host "  AVISO: Script de monitoramento nao encontrado" -ForegroundColor Yellow
}

$alertaScript = Join-Path $projectPath "Scripts\alerta_10_minutos_sem_trades.ps1"
if (Test-Path $alertaScript) {
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $alertaScript -WindowStyle Normal
    Write-Host "  Alerta de 10 minutos iniciado" -ForegroundColor Green
} else {
    Write-Host "  AVISO: Script de alerta nao encontrado" -ForegroundColor Yellow
}
Write-Host ""

# 6. Status final
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "SISTEMA REINICIADO" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""
Write-Host "[STATUS]:" -ForegroundColor Yellow
Write-Host "  Servidor Python: " -NoNewline
$proc = Get-Process python -ErrorAction SilentlyContinue
if ($proc) { Write-Host "RODANDO (PID: $($proc.Id))" -ForegroundColor Green } else { Write-Host "PARADO" -ForegroundColor Red }

Write-Host "  MetaTrader 5: " -NoNewline
$mt5 = Get-Process terminal64 -ErrorAction SilentlyContinue
if ($mt5) { Write-Host "RODANDO" -ForegroundColor Green } else { Write-Host "PARADO - ABRIR MANUALMENTE" -ForegroundColor Red }

Write-Host "  Monitoramento: " -NoNewline
Write-Host "ATIVO EM JANELAS SEPARADAS" -ForegroundColor Green
Write-Host ""

if (-not $mt5) {
    Write-Host "PROXIMOS PASSOS:" -ForegroundColor Yellow
    Write-Host "  1. Abrir MetaTrader 5" -ForegroundColor Cyan
    Write-Host "  2. Login na conta" -ForegroundColor Cyan
    Write-Host "  3. Anexar EA ao grafico BTCUSD M5" -ForegroundColor Cyan
    Write-Host "  4. Verificar logs do EA no Terminal" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "Sistema pronto para operar!" -ForegroundColor Green
Write-Host ""

