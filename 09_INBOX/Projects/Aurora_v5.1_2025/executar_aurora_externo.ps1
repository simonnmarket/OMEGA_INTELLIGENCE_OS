# ============================================================================
# AURORA v5.1 - SCRIPT DE EXECUÇÃO EXTERNA (POWERSHELL)
# ============================================================================
# Este script executa o sistema Aurora de forma independente
# Compatível com execução em background e monitoramento via MT5
# ============================================================================

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "AURORA v5.1 - EXECUCAO EXTERNA" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[INFO] Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Python nao encontrado. Instale Python 3.8+ primeiro." -ForegroundColor Red
    exit 1
}

# Mudar para diretório do script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Verificar dependências
Write-Host "[INFO] Verificando dependencias..." -ForegroundColor Yellow
try {
    python -c "import yfinance, pandas, numpy, aiohttp" 2>&1 | Out-Null
    Write-Host "[OK] Dependencias instaladas" -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Instalando dependencias necessarias..." -ForegroundColor Yellow
    pip install yfinance pandas numpy aiohttp --quiet
}

# Verificar argumentos
$phase = "alpha"
if ($args.Count -gt 0) {
    $phase = $args[0]
}

Write-Host "[INFO] Iniciando execucao na FASE: $phase" -ForegroundColor Cyan
Write-Host "[INFO] Sistema rodando externamente - ordens aparecerao no MT5" -ForegroundColor Cyan
Write-Host ""

# Executar script principal
$exitCode = 0
try {
    python AURORA_FINAL_EXECUCAO_AIC_V5.1.py $phase
    $exitCode = $LASTEXITCODE
} catch {
    Write-Host "[ERRO] Falha na execucao: $_" -ForegroundColor Red
    $exitCode = 1
}

# Resultado
if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "[SUCESSO] Execucao concluida com sucesso." -ForegroundColor Green
    Write-Host "[INFO] Verifique os relatorios gerados no diretorio atual." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "[ERRO] Execucao falhou. Verifique os logs acima." -ForegroundColor Red
}

Write-Host ""
Read-Host "Pressione Enter para sair"

exit $exitCode

