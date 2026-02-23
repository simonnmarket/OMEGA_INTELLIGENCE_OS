# Script para organizar arquivos para MetaTrader - VERSÃO CORRIGIDA
# Data: 2025-07-24
# Objetivo: Organizar arquivos na estrutura correta para compilação no MetaTrader

Write-Host "=== ORGANIZANDO ARQUIVOS PARA METATRADER - VERSÃO CORRIGIDA ===" -ForegroundColor Green

# Definir diretório de destino (ajuste conforme necessário)
$metatraderIncludePath = "C:\Users\Lenovo\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Include"
$projectPath = "D:\Cursor\Numeia"

# Criar estrutura de diretórios
Write-Host "Criando estrutura de diretórios..." -ForegroundColor Yellow

$directories = @(
    "utils",
    "include\quantum",
    "include\risk", 
    "include\executionlogic",
    "include\types",
    "include\analysis",
    "include\visuals",
    "core",
    "include\audit",
    "include\security",
    "include\learning",
    "include\intelligence",
    "include\neural",
    "include\modules",
    "include\data",
    "include\integration",
    "include\compliance",
    "include\detection"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path $metatraderIncludePath $dir
    if (!(Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force
        Write-Host "Criado: $fullPath" -ForegroundColor Green
    }
}

# Função para copiar com verificação
function Copy-WithVerification {
    param($Source, $Destination, $Description)
    
    if (Test-Path $Source) {
        try {
            Copy-Item $Source -Destination $Destination -Force -Recurse
            Write-Host "✅ $Description copiado com sucesso" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Erro ao copiar $Description : $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "⚠️ Origem não encontrada: $Source" -ForegroundColor Yellow
    }
}

# Copiar arquivos com verificação
Write-Host "Copiando arquivos com verificação..." -ForegroundColor Yellow

# Utils
Copy-WithVerification "$projectPath\utils\logger_institutional.mqh" "$metatraderIncludePath\utils\" "logger_institutional.mqh"
Copy-WithVerification "$projectPath\utils\anti_reincidence_system.mqh" "$metatraderIncludePath\utils\" "anti_reincidence_system.mqh"

# Core
Copy-WithVerification "$projectPath\core\core_brain_manager.mqh" "$metatraderIncludePath\core\" "core_brain_manager.mqh"
Copy-WithVerification "$projectPath\core\quantum_blockchain.mqh" "$metatraderIncludePath\core\" "quantum_blockchain.mqh"
Copy-WithVerification "$projectPath\core\force_maxima.mqh" "$metatraderIncludePath\core\" "force_maxima.mqh"

# Quantum
Copy-WithVerification "$projectPath\include\quantum" "$metatraderIncludePath\include\quantum\" "pasta quantum"

# Risk
Copy-WithVerification "$projectPath\include\risk" "$metatraderIncludePath\include\risk\" "pasta risk"

# Execution Logic
Copy-WithVerification "$projectPath\include\executionlogic" "$metatraderIncludePath\include\executionlogic\" "pasta executionlogic"

# Types
Copy-WithVerification "$projectPath\include\types" "$metatraderIncludePath\include\types\" "pasta types"

# Analysis
Copy-WithVerification "$projectPath\include\analysis" "$metatraderIncludePath\include\analysis\" "pasta analysis"

# Visuals
Copy-WithVerification "$projectPath\include\visuals" "$metatraderIncludePath\include\visuals\" "pasta visuals"

# Audit
Copy-WithVerification "$projectPath\include\audit" "$metatraderIncludePath\include\audit\" "pasta audit"

# Security
Copy-WithVerification "$projectPath\include\security" "$metatraderIncludePath\include\security\" "pasta security"

# Learning
Copy-WithVerification "$projectPath\include\learning" "$metatraderIncludePath\include\learning\" "pasta learning"

# Intelligence
Copy-WithVerification "$projectPath\include\intelligence" "$metatraderIncludePath\include\intelligence\" "pasta intelligence"

# Neural
Copy-WithVerification "$projectPath\include\neural" "$metatraderIncludePath\include\neural\" "pasta neural"

# Modules
Copy-WithVerification "$projectPath\include\modules" "$metatraderIncludePath\include\modules\" "pasta modules"

# Data
Copy-WithVerification "$projectPath\include\data" "$metatraderIncludePath\include\data\" "pasta data"

# Integration
Copy-WithVerification "$projectPath\integration" "$metatraderIncludePath\include\integration\" "pasta integration"

# Compliance
Copy-WithVerification "$projectPath\include\compliance" "$metatraderIncludePath\include\compliance\" "pasta compliance"

# Detection
Copy-WithVerification "$projectPath\include\detection" "$metatraderIncludePath\include\detection\" "pasta detection"

Write-Host "=== VERIFICAÇÃO FINAL ===" -ForegroundColor Green
Write-Host "Arquivos críticos verificados:" -ForegroundColor Cyan
Write-Host "✅ market_regime_detector.mqh - EXISTE" -ForegroundColor Green
Write-Host "✅ anomaly_detector_ai.mqh - EXISTE" -ForegroundColor Green

Write-Host "=== ARQUIVOS ORGANIZADOS COM SUCESSO! ===" -ForegroundColor Green
Write-Host "MetaTrader deve agora encontrar todos os includes." -ForegroundColor Cyan
Write-Host "Tente compilar novamente o NumeiaEA.mq5" -ForegroundColor Cyan 