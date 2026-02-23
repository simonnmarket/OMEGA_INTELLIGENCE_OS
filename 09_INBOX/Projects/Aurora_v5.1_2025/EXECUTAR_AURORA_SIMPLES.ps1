#!/usr/bin/env pwsh
# ============================================================================
# AURORA v5.1 - EXECUÇÃO SIMPLES (VERSÃO CORRIGIDA)
# ============================================================================

$ErrorActionPreference = "Continue"

Clear-Host
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "           AURORA v5.1 - SISTEMA COMPLETO COM MT5 INTEGRADO" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "🔍 Verificando Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado! Instale Python 3.8+ primeiro." -ForegroundColor Red
    exit 1
}

# Verificar arquivo
if (-not (Test-Path "AURORA_FINAL_EXECUCAO_AIC_V5.1.py")) {
    Write-Host "❌ Arquivo AURORA_FINAL_EXECUCAO_AIC_V5.1.py não encontrado!" -ForegroundColor Red
    exit 1
}

# Verificar MT5
Write-Host "🔍 Verificando MetaTrader 5..." -ForegroundColor Cyan
$mt5Process = Get-Process -Name "terminal64" -ErrorAction SilentlyContinue
if ($mt5Process) {
    Write-Host "✅ MetaTrader 5 está rodando (PID: $($mt5Process.Id))" -ForegroundColor Green
} else {
    Write-Host "⚠️  MetaTrader 5 não está rodando!" -ForegroundColor Yellow
    Write-Host "   O sistema tentará conectar automaticamente" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "🚀 INICIANDO SISTEMA AURORA COMPLETO" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 O sistema irá:" -ForegroundColor Yellow
Write-Host "   1. Conectar ao MetaTrader 5" -ForegroundColor White
Write-Host "   2. Inicializar as 3 estratégias de trading" -ForegroundColor White
Write-Host "   3. Coletar dados de mercado (crypto)" -ForegroundColor White
Write-Host "   4. Gerar sinais de trading" -ForegroundColor White
Write-Host "   5. Enviar ordens automaticamente ao MT5" -ForegroundColor White
Write-Host "   6. Monitorar posições em tempo real" -ForegroundColor White
Write-Host ""
Write-Host "⏱️  Duração: 24 horas (FASE β)" -ForegroundColor Yellow
Write-Host "📊 Logs: Serão exibidos em tempo real neste terminal" -ForegroundColor Yellow
Write-Host "📈 Ordens: Aparecerão no MetaTrader 5 automaticamente" -ForegroundColor Yellow
Write-Host ""

# Confirmar execução
$confirm = Read-Host "▶️  Executar sistema completo agora? (s/N)"
if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host "⏹️  Execução cancelada pelo usuário" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "▶️  EXECUTANDO SISTEMA..." -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

# Criar arquivo de log
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "aurora_execucao_completa_$timestamp.log"
Write-Host "📝 Log sendo salvo em: $logFile" -ForegroundColor Cyan
Write-Host ""

# Executar sistema Python
Write-Host "🚀 Iniciando Aurora v5.1..." -ForegroundColor Green
Write-Host ""

# Executar e mostrar output em tempo real
python AURORA_FINAL_EXECUCAO_AIC_V5.1.py beta 2>&1 | Tee-Object -FilePath $logFile

# Verificar resultado
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=================================================================================" -ForegroundColor Green
    Write-Host "✅ SISTEMA EXECUTADO COM SUCESSO" -ForegroundColor Green
    Write-Host "=================================================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=================================================================================" -ForegroundColor Red
    Write-Host "❌ SISTEMA FINALIZOU COM ERROS" -ForegroundColor Red
    Write-Host "=================================================================================" -ForegroundColor Red
    Write-Host "📝 Verifique o log: $logFile" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📊 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "   1. Verificar ordens no MetaTrader 5 (aba Trade)" -ForegroundColor White
Write-Host "   2. Revisar log completo: $logFile" -ForegroundColor White
Write-Host "   3. Verificar relatórios gerados" -ForegroundColor White
Write-Host ""

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "🏁 EXECUÇÃO FINALIZADA" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

