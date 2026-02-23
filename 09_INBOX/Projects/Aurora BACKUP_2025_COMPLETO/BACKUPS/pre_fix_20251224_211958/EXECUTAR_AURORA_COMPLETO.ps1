#!/usr/bin/env pwsh
# ============================================================================
# AURORA v5.1 - EXECUÇÃO EXTERNA COMPLETA COM MONITORAMENTO MT5
# ============================================================================
# Executa o sistema completo Aurora com todas as estratégias e MT5 ativo
# Permite acompanhar ordens em tempo real no terminal
# ============================================================================

$ErrorActionPreference = "Continue"

# Cores para output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Banner
Clear-Host
Write-ColorOutput "=================================================================================" "Cyan"
Write-ColorOutput "           AURORA v5.1 - SISTEMA COMPLETO COM MT5 INTEGRADO" "Cyan"
Write-ColorOutput "=================================================================================" "Cyan"
Write-Host ""
Write-ColorOutput "📊 Sistema: Aurora Trading System v5.1" "Yellow"
Write-ColorOutput "🎯 Fase: BETA (Validação 24h)" "Yellow"
Write-ColorOutput "🔌 MT5: Integrado e Ativo" "Yellow"
Write-ColorOutput "📈 Estratégias: Alpha Momentum, Mean Reversion, Breakout Detection" "Yellow"
Write-Host ""

# Verificar se Python está instalado
Write-ColorOutput "🔍 Verificando Python..." "Cyan"
try {
    $pythonVersion = python --version 2>&1
    Write-ColorOutput "✅ Python encontrado: $pythonVersion" "Green"
} catch {
    Write-ColorOutput "❌ Python não encontrado! Instale Python 3.8+ primeiro." "Red"
    exit 1
}

# Verificar se está no diretório correto
$currentDir = Get-Location
Write-ColorOutput "📁 Diretório atual: $currentDir" "Cyan"

if (-not (Test-Path "AURORA_FINAL_EXECUCAO_AIC_V5.1.py")) {
    Write-ColorOutput "❌ Arquivo AURORA_FINAL_EXECUCAO_AIC_V5.1.py não encontrado!" "Red"
    Write-ColorOutput "   Certifique-se de estar no diretório do projeto Aurora" "Yellow"
    exit 1
}

# Verificar dependências
Write-ColorOutput "🔍 Verificando dependências..." "Cyan"
try {
    python -c "import MetaTrader5; print('✅ MetaTrader5 instalado')" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ MetaTrader5: OK" "Green"
    } else {
        Write-ColorOutput "⚠️  MetaTrader5 não instalado. Instalando..." "Yellow"
        pip install MetaTrader5
    }
} catch {
    Write-ColorOutput "⚠️  Verificando MetaTrader5..." "Yellow"
}

try {
    python -c "import yfinance; print('✅ yfinance instalado')" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ yfinance: OK" "Green"
    }
} catch {
    Write-ColorOutput "⚠️  yfinance não encontrado" "Yellow"
}

Write-Host ""

# Verificar se MT5 está rodando
Write-ColorOutput "🔍 Verificando MetaTrader 5..." "Cyan"
$mt5Process = Get-Process -Name "terminal64" -ErrorAction SilentlyContinue
if ($mt5Process) {
    Write-ColorOutput "✅ MetaTrader 5 está rodando (PID: $($mt5Process.Id))" "Green"
} else {
    Write-ColorOutput "⚠️  MetaTrader 5 não está rodando!" "Yellow"
    Write-ColorOutput "   O sistema tentará conectar automaticamente" "Yellow"
    Write-ColorOutput "   Recomendado: Abra o MetaTrader 5 antes de continuar" "Yellow"
    Write-Host ""
    $continue = Read-Host "▶️  Continuar mesmo assim? (s/N)"
    if ($continue -ne "s" -and $continue -ne "S") {
        Write-ColorOutput "⏹️  Execução cancelada" "Yellow"
        exit 0
    }
}

Write-Host ""
Write-ColorOutput "=================================================================================" "Cyan"
Write-ColorOutput "🚀 INICIANDO SISTEMA AURORA COMPLETO" "Cyan"
Write-ColorOutput "=================================================================================" "Cyan"
Write-Host ""
Write-ColorOutput "📋 O sistema irá:" "Yellow"
Write-ColorOutput "   1. Conectar ao MetaTrader 5" "White"
Write-ColorOutput "   2. Inicializar as 3 estratégias de trading" "White"
Write-ColorOutput "   3. Coletar dados de mercado (crypto)" "White"
Write-ColorOutput "   4. Gerar sinais de trading" "White"
Write-ColorOutput "   5. Enviar ordens automaticamente ao MT5" "White"
Write-ColorOutput "   6. Monitorar posições em tempo real" "White"
Write-Host ""
Write-ColorOutput "⏱️  Duração: 24 horas (FASE β)" "Yellow"
Write-ColorOutput "📊 Logs: Serão exibidos em tempo real neste terminal" "Yellow"
Write-ColorOutput "📈 Ordens: Aparecerão no MetaTrader 5 automaticamente" "Yellow"
Write-Host ""

# Confirmar execução
$confirm = Read-Host "▶️  Executar sistema completo agora? (s/N)"
if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-ColorOutput "⏹️  Execução cancelada pelo usuário" "Yellow"
    exit 0
}

Write-Host ""
Write-ColorOutput "=================================================================================" "Cyan"
Write-ColorOutput "▶️  EXECUTANDO SISTEMA..." "Cyan"
Write-ColorOutput "=================================================================================" "Cyan"
Write-Host ""

# Criar arquivo de log com timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "aurora_execucao_completa_$timestamp.log"

Write-ColorOutput "📝 Log sendo salvo em: $logFile" "Cyan"
$monitorCmd = "Get-Content $logFile -Tail 50 -Wait"
Write-ColorOutput "💡 Dica: Abra outro terminal para monitorar: $monitorCmd" "Yellow"
Write-Host ""

# Executar sistema Python
Write-ColorOutput "🚀 Iniciando Aurora v5.1..." "Green"
Write-Host ""

# Executar e mostrar output em tempo real
python AURORA_FINAL_EXECUCAO_AIC_V5.1.py beta 2>&1 | Tee-Object -FilePath $logFile

# Verificar resultado
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-ColorOutput "=================================================================================" "Green"
    Write-ColorOutput "✅ SISTEMA EXECUTADO COM SUCESSO" "Green"
    Write-ColorOutput "=================================================================================" "Green"
} else {
    Write-Host ""
    Write-ColorOutput "=================================================================================" "Red"
    Write-ColorOutput "❌ SISTEMA FINALIZOU COM ERROS" "Red"
    Write-ColorOutput "=================================================================================" "Red"
    Write-ColorOutput "📝 Verifique o log: $logFile" "Yellow"
}

Write-Host ""
Write-ColorOutput "📊 PRÓXIMOS PASSOS:" "Cyan"
Write-ColorOutput "   1. Verificar ordens no MetaTrader 5 (aba Trade)" "White"
Write-ColorOutput "   2. Revisar log completo: $logFile" "White"
Write-ColorOutput "   3. Verificar relatórios gerados" "White"
Write-Host ""

# Perguntar se quer abrir MT5
$openMT5 = Read-Host "▶️  Abrir MetaTrader 5 agora? (s/N)"
if ($openMT5 -eq "s" -or $openMT5 -eq "S") {
    $mt5Path = "C:\Program Files\MetaTrader 5\terminal64.exe"
    if (Test-Path $mt5Path) {
        Start-Process $mt5Path
        Write-ColorOutput "✅ MetaTrader 5 aberto" "Green"
    } else {
        Write-ColorOutput "⚠️  MetaTrader 5 não encontrado no caminho padrão" "Yellow"
        Write-ColorOutput "   Abra manualmente o MetaTrader 5" "Yellow"
    }
}

Write-Host ""
Write-ColorOutput "=================================================================================" "Cyan"
Write-ColorOutput "🏁 EXECUÇÃO FINALIZADA" "Cyan"
Write-ColorOutput "=================================================================================" "Cyan"
Write-Host ""

